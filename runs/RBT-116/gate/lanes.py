"""RBT-116: emit W1's gate lanes (and print the gate's and the arms' cost).  Emits; never launches.

    python runs/RBT-116/gate/lanes.py emit [--dir runs/RBT-116/gate/lanes]   # writes the lane scripts and LANES.txt
    python runs/RBT-116/gate/lanes.py cost                                   # the cost tables (also in LANES.txt)

Every emitted script refuses to start unless ``RBT116_GATE_GO=1`` is set (the coordinator's GO, after the hooks PR
merges), on a clean, x86_64 checkout whose ``rabbitstew/`` tree is the one the lanes were emitted against.  Each lane
is one cloud session at ``WORKERS`` (default 4), launched as a harness background task (never ``nohup``), and each
snapshots its directory to its own ``ckpt/rbt-116-w1-*`` label with ``scripts/durable.sh``.  Re-running a lane resumes
it: an ``evolve`` run continues with ``--resume``; a gate cell skips every unit, host, shard or parent whose output is
already there.

The waves (a wave starts when every lane of the wave before it has saved):

    0  b-<ARM> x 8    the burn-in B of the arm's 3 units (RBT-113 arm ARM's seeds), at B_DRAWS_OPTION
    1  gate-a         config, hosts, screen, G1 + G2, G8's (d) and (e)
       g6-noise       sigma_P on every unit's burn-in finals
       g5             two generations of unit 1's U under each draws option (timing)
    2  g8-s<i> x 6, g4-s<i> x 4, g7, g9-s<i> x 2
    3  g6u-s<i> x 8   the children of every STEERS G8(a) and G8(c) plant
    4  g6-pilot       G6's choice, the pilot's 24 generations at it, the pilot's probe
    5  readout        GATE.txt: every row, power.py at the measured inputs, K, "the stronger no"
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R116 = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(R116))
sys.path.insert(0, R116)
import world as W  # noqa: E402

OUT = "runs/RBT-116/gate/W1"
BASE = "runs/RBT-116/W1"
ARMS = ("O1", "O2", "O3", "O4", "Z1", "Z2", "Z3", "Z4")
SHARDS = {"g8": 6, "g4": 4, "g9": 2, "g6-u": 8}
GATE_LABEL = "rbt-116-w1-gate"


def arm_units(arm: str) -> list:
    k = int(arm[1])
    return [3 * (k - 1) + i + (0 if arm[0] == "O" else 12) for i in (1, 2, 3)]


def unit_label(j: int, run: str) -> str:
    return f"rbt-116-w1-unit{j:02d}-{run.lower()}"


HEADER = """#!/bin/bash
# RBT-116 W1 gate lane {name} (wave {wave}): {desc}
# EMITTED by runs/RBT-116/gate/lanes.py; NOT LAUNCHED.  Launch only after the hooks PR has merged and the coordinator
# has given the GO: RBT116_GATE_GO=1 WORKERS=4 bash runs/RBT-116/gate/lanes/{name}.sh  (a harness background task)
# Re-running this script resumes the lane.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
[ "${{RBT116_GATE_GO:-}}" = 1 ] || {{ echo "REFUSED: no GO (set RBT116_GATE_GO=1 only on the coordinator's GO)" >&2; exit 4; }}
[ "$(uname -m)" = x86_64 ] || {{ echo "REFUSED: x86_64 only (RBT-96)" >&2; exit 3; }}
if [ -n "$(git status --porcelain -- rabbitstew scripts/durable.sh {pinned_paths})" ]; then
  echo "REFUSED: rabbitstew/ or a script the gate loads has uncommitted changes" >&2; exit 5
fi
[ "$(git rev-parse HEAD:rabbitstew)" = "{tree}" ] || {{ echo "REFUSED: rabbitstew/ is not the tree these lanes were emitted on ({tree})" >&2; exit 6; }}
# F7a: every script outside rabbitstew/ that gate.py loads, pinned by blob (re-emit with lanes.py on the final tree)
while read -r blob path; do
  [ "$(git rev-parse "HEAD:$path" 2>/dev/null)" = "$blob" ] || {{ echo "REFUSED: $path is not the blob these lanes were emitted on ($blob)" >&2; exit 6; }}
done <<'PINS'
{pins}
PINS
WORKERS=${{WORKERS:-4}}
OUT={out}
BASE={base}
mkdir -p "$OUT"
restore() {{  # restore DIR LABEL unless DIR is already there (durable.sh refuses a directory holding a state.json)
  if [ ! -e "$1/.restored" ] && [ ! -e "$1/state.json" ]; then scripts/durable.sh restore "$1" "$2" && touch "$1/.restored"; fi
}}
saver() {{  # snapshot DIR to LABEL every 20 minutes while PID runs (polling every 10 s), then once more
  local dir=$1 label=$2 pid=$3 t=0
  while kill -0 "$pid" 2>/dev/null; do
    sleep 10; t=$((t + 10))
    if [ "$t" -ge 1200 ]; then scripts/durable.sh save "$dir" "$label" || true; t=0; fi
  done
  scripts/durable.sh save "$dir" "$label"
}}
cell() {{  # run one gate.py cell in the background with its saver, and wait
  local label=$1; shift
  python runs/RBT-116/gate/gate.py "$@" --out "$OUT" --base "$BASE" --workers "$WORKERS" >> "$OUT/lane-{name}.log" 2>&1 &
  local pid=$!
  saver "$OUT" "$label" "$pid" &
  local sp=$!
  local rc=0; wait "$pid" || rc=$?
  wait "$sp" || true
  return $rc
}}
restore_units() {{ for j in $(seq 1 24); do restore "$BASE/unit$(printf %02d $j)/B" "rbt-116-w1-unit$(printf %02d $j)-b"; done; }}
restore_gate() {{ restore "$OUT" {gate}-a; }}
"""

EVOLVE_FN = """
evolve_run() {  # evolve_run DIR LABEL CMD...: launch, or resume, one evolve run with its durable loop (as RBT-113's run_arm.sh)
  local R=$1 L=$2; shift 2
  local G; G=$(python - "$@" <<'PY'
import sys
a = sys.argv[1:]
print(a[a.index("--generations") + 1])
PY
)
  if [ -f "$R/history.json" ] && [ -d "$R/holistic/final" ] && [ "$(python -c "import json,sys; print(sum(e['population']=='holistic' for e in json.load(open(sys.argv[1]))['history']))" "$R/history.json")" = "$G" ]; then
    echo "$R complete; skipped"; return 0
  fi
  local rr=0; restore "$R" "$L" || rr=$?  # F4: exit 3 is "no checkpoint yet" (a fresh run); anything else is a failure
  [ "$rr" = 0 ] || [ "$rr" = 3 ] || { echo "REFUSED: restoring $R from ckpt/$L failed (exit $rr)" >&2; exit 7; }
  if [ -f "$R/state.json" ]; then
    echo "resumed $(date -u +%FT%TZ)" >> "$R/resumes.txt"
    python -m rabbitstew.cli evolve --resume --out "$R" --workers "$WORKERS" >> "$R/run.log" 2>&1 &
  else
    [ -d "$R" ] && rm -rf "$R"
    mkdir -p "$R"; echo "$*" > "$R/command.txt"
    "$@" > "$R/run.log" 2>&1 &
  fi
  local pid=$!
  DURABLE_WATCH_PID=$pid scripts/durable.sh every 20 "$R" "$L" &
  local dp=$!
  local rc=0; wait "$pid" || rc=$?
  kill "$dp" 2>/dev/null || true; wait "$dp" 2>/dev/null || true  # its next check could be 20 minutes away
  scripts/durable.sh save "$R" "$L"
  if [ "$rc" != 0 ] && grep -q DecoyRefused "$R/run.log"; then  # H16 as ruled: the stop is reported for a ruling
    echo "STOPPED FOR A RULING (H16): $R: a decoy season found no clear theta (DecoyRefused); see $R/run.log" >&2; exit 8
  fi
  return $rc
}
"""


def sh_cmd(cmd: list) -> str:
    return " ".join(c if c.replace("/", "").replace("=", "").replace("-", "").replace(".", "").replace("_", "").isalnum() else f"'{c}'" for c in cmd)


def lanes(tree: str) -> list:
    """(wave, name, description, body) for every lane."""
    L = []
    for arm in ARMS:
        body = [f"restore runs/RBT-113/{arm} rbt-113-{arm}"]
        for j in arm_units(arm):
            r = os.path.join(BASE, f"unit{j:02d}", "B")
            body.append(f"evolve_run {r} {unit_label(j, 'B')} " + sh_cmd(W.command("B", j, r, W.B_DRAWS_OPTION, workers=4)).replace("--workers 4", '--workers "$WORKERS"'))
        L.append((0, f"b-{arm}", f"the burn-in B ({W.B_DRAWS_OPTION}, 13 generations) of units {arm_units(arm)}", body, True))
    L.append((1, "gate-a", "config, hosts, screen, G1 + G2, G8 (d) and (e)",
              ["restore_units", "for arm in " + " ".join(ARMS) + "; do restore runs/RBT-113/$arm rbt-113-$arm; done",
               f"cell {GATE_LABEL}-a config", f"cell {GATE_LABEL}-a fixture", f"cell {GATE_LABEL}-a hosts", f"cell {GATE_LABEL}-a screen",
               f"cell {GATE_LABEL}-a g1 || echo 'G1 FAILED: the gate has failed; later waves will refuse'",
               f"cell {GATE_LABEL}-a g8-controls"], False))
    L.append((1, "g6-noise", "G6's sigma_P on every unit's burn-in finals",
              ["restore_units", f"cell {GATE_LABEL}-noise config", f"cell {GATE_LABEL}-noise fixture", f"cell {GATE_LABEL}-noise g6-noise"], False))
    g5 = ["restore_units", f"cell {GATE_LABEL}-g5 config", f"cell {GATE_LABEL}-g5 fixture"]
    for opt in W.DRAWS_OPTIONS:
        r = f"$OUT/g5/{opt}"
        g5.append(f"evolve_run {r} {GATE_LABEL}-g5-{opt.lower()} " + sh_cmd(W.command("U", 1, "OUTDIR", opt, workers=4, generations=2)).replace("OUTDIR", r).replace("--workers 4", '--workers "$WORKERS"'))
    g5.append(f"cell {GATE_LABEL}-g5 g5")
    L.append((1, "g5", "G5: two generations of unit 1's U under each draws option", g5, True))
    w2 = ["restore_units", "restore_gate", "for arm in " + " ".join(ARMS) + "; do restore runs/RBT-113/$arm rbt-113-$arm; done"]
    for cellname, n in (("g8", SHARDS["g8"]), ("g4", SHARDS["g4"]), ("g9", SHARDS["g9"])):
        for i in range(n):
            L.append((2, f"{cellname}-s{i}", f"{cellname.upper()} shard {i}/{n}", w2 + [f"cell {GATE_LABEL}-{cellname}-s{i} {cellname} --shard {i}/{n}"], False))
    L.append((2, "g7", "G7: the Pioneer's valley", w2 + [f"cell {GATE_LABEL}-g7 g7"], False))
    g8r = [f"restore \"$OUT\" {GATE_LABEL}-g8-s{i}" for i in range(SHARDS["g8"])]
    merge = ["merge() { scripts/durable.sh restore \"$OUT\" \"$1\"; }"]
    for i in range(SHARDS["g6-u"]):
        body = ["restore_units", "restore_gate"] + [f"merge {GATE_LABEL}-g8-s{k}" for k in range(SHARDS["g8"])] + [f"cell {GATE_LABEL}-g6u-s{i} g6-u --shard {i}/{SHARDS['g6-u']}"]
        L.append((3, f"g6u-s{i}", f"G6's u_f shard {i}/{SHARDS['g6-u']}", merge + body, False))
    every = ([f"merge {GATE_LABEL}-{x}" for x in ("noise", "g5", "g7")]
             + [f"merge {GATE_LABEL}-{c}-s{i}" for c in ("g8", "g4", "g9") for i in range(SHARDS[c])]
             + [f"merge {GATE_LABEL}-g6u-s{i}" for i in range(SHARDS["g6-u"])])
    pilot = (merge + ["restore_units", "restore_gate"] + every
             + [f"cell {GATE_LABEL}-pilot g6-pick", f"cell {GATE_LABEL}-pilot pilot-prep",
                'OPT=$(python -c "import json; print(json.load(open(\'$OUT/g6.json\'))[\'chosen\'])")',
                "mapfile -t PCMD < <(python - \"$OPT\" <<'PY'\nimport sys; sys.path.insert(0, 'runs/RBT-116/gate'); import gate\nprint('\\n'.join(gate.pilot_command(gate.os.path.join('runs', 'RBT-116', 'gate', 'W1'), sys.argv[1])))\nPY\n)",
                f"evolve_run \"$OUT/pilot/run\" {GATE_LABEL}-pilot-run \"${{PCMD[@]}}\"",
                f"cell {GATE_LABEL}-pilot pilot-probe"])
    L.append((4, "g6-pilot", "G6's choice, the SHOULD 11 pilot (24 generations) and its probe", pilot, True))
    L.append((5, "readout", "GATE.txt", merge + ["restore_units", "restore_gate"] + every + [f"merge {GATE_LABEL}-pilot", f"cell {GATE_LABEL}-readout readout"], False))
    return L


# --------------------------------------------------------------------------- #
# Cost
# --------------------------------------------------------------------------- #

SEASON_S = 0.40  #: CPU-s per 15 s W1 season (measured 0.37 on run_solo here, +~10% for movers and the battery's recording)
CALL_PLANT = 8 + 64 + 0.6 * 32  #: seasons per call of a plant (all reach stage 2; ~60% confirm)
CALL_MEMBER = 8 + 0.75 * 64 + 0.10 * 32  #: seasons per call of an unplanted member (§9: 75% to stage 2, 10% confirm)
CALL_CHILD = 8 + 64 + 0.5 * 32  #: seasons per call of a STEERS plant's child


def gate_cost(steers_a: int = 48, steers_c: int = 19, d_pilot: str = "D16") -> list:
    """(cell, seasons) for every gate cell.  ``steers_a`` / ``steers_c``: STEERS G8(a) / G8(c) plants (G6's parents;
    priors: c_G1 ~ 0.5 of 96 designed, 0.2 of 96 holistic)."""
    per_gen = {"D16": 80 * 16, "D8": 80 * 8, "DF16": 80 * 4 + 22 * 16}
    return [
        ("hosts (direction probes, layouts, turning sense)", 24 * 4 * 32 * 1.25 + 24 * 4 * 5 * 2),
        ("screen (64 draws x 16 hosts; (c) tuning)", 16 * 64 + 8 * 6 * 8),
        ("G1 + G2 (16 hosts x 4 rungs; blind yields)", 16 * 4 * CALL_PLANT + 32 * 16),
        ("G8 (a)(b)(c)(f) on 192 hosts, tuning + calls; (d)(e)", 24 * (16 * CALL_PLANT + 4 * (8 + 6 + 8) * 8) + 6 * 8),
        ("G4 (400 members, all four conditions)", 400 * CALL_MEMBER),
        ("G6 sigma_P (24 units x 80 x 6 draws)", 24 * 80 * 6),
        (f"G6 u_f ({steers_a} + {steers_c} STEERS plants x 40 children)", (steers_a + steers_c) * 40 * CALL_CHILD),
        ("G5 (2 generations x 3 options)", 2 * sum(per_gen.values())),
        (f"G6 pilot (25 generations at {d_pilot}; probe 80; prep 28 plants)", 25 * per_gen[d_pilot] + 80 * CALL_MEMBER + 28 * 32),
        ("G7 (16 hosts x (1 + 8 x 4 rungs) x 16 draws; finding 8)", 16 * (1 + 8 * 4) * 16),
        ("G8(f) fixture check (F2, F3; in each wave-1 lane)", 3 * 2 * (5 + 8 * 4 * 2 + 104)),
        ("G9 (4 worlds x 216 members x 16 draws)", 4 * 216 * 16),
    ]


def arm_cost(option: str, b_option: str = W.B_DRAWS_OPTION) -> dict:
    """Per unit and for 24 units, CPU-h: B (13 generations at ``b_option``), U and N (49 each at ``option``), the
    probes (§9: 9 probe points x 2 faunas x 40 members) and the proposal assay (400 children + parent confirmation)."""
    per_gen = {"D16": 80 * 16, "D8": 80 * 8, "DF16": 80 * 4 + 22 * 16}
    evo = (W.GEN_B * per_gen[b_option] + 2 * W.GEN_UN * per_gen[option]) * SEASON_S / 3600
    probes = 9 * 2 * 40 * CALL_MEMBER * SEASON_S / 3600
    assay = (400 * CALL_MEMBER + 400 * 32) * SEASON_S / 3600
    unit = evo + probes + assay
    return {"evolution": evo, "probes": probes, "assay": assay, "unit": unit, "24 units": 24 * unit,
            "B share (24 units)": 24 * W.GEN_B * per_gen[b_option] * SEASON_S / 3600}


def cost_text() -> str:
    lines = [f"# RBT-116 W1: cost at {SEASON_S} CPU-s per 15 s season (measured 0.37 here; scale linearly)", "",
             "## The gate (after the 24 burn-ins; seasons and CPU-h)"]
    tot = 0.0
    for name, n in gate_cost():
        lines.append(f"  {name:62s} {n:9.0f}  {n * SEASON_S / 3600:6.1f}")
        tot += n
    lines.append(f"  {'TOTAL (priors: 48 STEERS (a), 19 STEERS (c); pilot at D16)':62s} {tot:9.0f}  {tot * SEASON_S / 3600:6.1f}")
    lo = sum(n for _, n in gate_cost(30, 10, "DF16"))
    hi = sum(n for _, n in gate_cost(96, 48, "D16"))
    lines.append(f"  range: {lo * SEASON_S / 3600:.0f} CPU-h (30 + 10 STEERS plants, pilot at DF16) to {hi * SEASON_S / 3600:.0f} (every (a), half the (c))")
    lines += ["", f"## The arms (24 units; B at {W.B_DRAWS_OPTION}, reading H2; U and N 49 generations each, reading H1)"]
    for opt in ("D16", "D8", "DF16"):
        c = arm_cost(opt)
        lines.append(f"  {opt:5s} per unit: evolution {c['evolution']:5.1f} + probes {c['probes']:4.1f} + assay {c['assay']:4.1f} = {c['unit']:5.1f}; "
                     f"24 units {c['24 units']:6.0f} CPU-h (of which B {c['B share (24 units)']:.0f})")
    for opt in ("D8", "DF16"):
        c = arm_cost(opt, b_option="DF16")
        lines.append(f"  {opt:5s} with B also at DF16: 24 units {c['24 units']:6.0f} CPU-h")
    return "\n".join(lines) + "\n"


def gate_sources() -> list:
    """Every file outside rabbitstew/ that importing gate.py loads (repository-relative), found by importing it in a
    fresh interpreter: what the lanes pin by blob (F7a)."""
    code = ("import os, sys; sys.path.insert(0, 'runs/RBT-116/gate'); import gate; r = os.path.realpath('.'); "
            "print('\\n'.join(sorted({os.path.relpath(os.path.realpath(m.__file__), r) for m in list(sys.modules.values()) "
            "if getattr(m, '__file__', None) and os.path.realpath(m.__file__).startswith(r + os.sep)})))")
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    lazy = ["runs/RBT-113/world.py", "runs/RBT-116/gate/lanes.py"]  # G9's census loads RBT-113's world.py on use
    return sorted(set(p for p in out if not p.startswith("rabbitstew" + os.sep)) | set(lazy))


def emit(d: str) -> int:
    tree = subprocess.run(["git", "rev-parse", "HEAD:rabbitstew"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    paths = gate_sources()
    blobs = [subprocess.run(["git", "rev-parse", f"HEAD:{p}"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip() for p in paths]
    pins = "\n".join(f"{b} {p}" for b, p in zip(blobs, paths))
    os.makedirs(d, exist_ok=True)
    plan = [f"# RBT-116 W1 gate lanes, emitted on rabbitstew/ tree {tree}.  NOT LAUNCHED: each refuses without RBT116_GATE_GO=1.",
            "# F7b: the last step before the GO is re-emitting these lanes (lanes.py emit) on the final merged tree, and committing them;",
            "# each lane refuses on any other rabbitstew/ tree or on any other blob of these scripts:"]
    plan += [f"#   {b} {p}" for b, p in zip(blobs, paths)] + [""]
    for wave, name, desc, body, evo in lanes(tree):
        txt = HEADER.format(name=name, wave=wave, desc=desc, tree=tree, out=OUT, base=BASE, gate=GATE_LABEL, pins=pins, pinned_paths=" ".join(paths))
        if evo:
            txt += EVOLVE_FN
        txt += "\n" + "\n".join(body) + f"\necho 'lane {name} done'\n"
        p = os.path.join(d, f"{name}.sh")
        with open(p, "w") as f:
            f.write(txt)
        os.chmod(p, 0o755)
        plan.append(f"wave {wave}  {name:10s}  {desc}")
    plan += ["", cost_text()]
    with open(os.path.join(d, "LANES.txt"), "w") as f:
        f.write("\n".join(plan))
    print("\n".join(plan))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("what", choices=("emit", "cost"))
    ap.add_argument("--dir", default=os.path.join(HERE, "lanes"))
    a = ap.parse_args(argv)
    if a.what == "cost":
        print(cost_text())
        return 0
    return emit(a.dir)


if __name__ == "__main__":
    sys.exit(main())
