"""RBT-134b registered-run lane: completeness checks, the control gate, the environment check and the RELAY block
(runs/RBT-134/REGISTRATION-134b.md).  The 134b counterpart of relay.py, whose helpers it reuses; relay.py and lanes
A and B are unchanged.

The RELAY block carries ONLY what the no-peek discipline allows (LAUNCH.md): the GO sha, each control's id with its
YES/NO tokens, the ids on the VOID list (never their text), whether the outputs were committed, the sha256 of every
output file, and per-stage wall / CPU time rounded to the hour.  No k, p, verdict, rate, count, bound, flag or table
figure ever reaches it: tokens are built from a fixed id pattern and the literal words YES / NO.

    relay134b.py complete-run  OUT/COND.json      HEAD N_PER_POOL N_BG_PER_POOL -> complete | incomplete | stale
    relay134b.py complete-swap OUT/COND-swap.json HEAD N_PER_POOL N_BG_PER_POOL -> likewise
    relay134b.py gate READOUT                     -> PASS iff its VOID list is "none", else STOP
    relay134b.py mujoco-ok                        -> ok iff this interpreter's mujoco is the lane's pin, else no
    relay134b.py relay OUT_DIR HEAD --committed yes|no --status S [NAME:WALL_S:CPU_S ...] -> the RELAY block
"""
import argparse
import importlib.util
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
MASTER_SEED = 20260912
MUJOCO_PIN = "3.14.0"  #: the lane's venv pin (REGISTRATION-134b.md); a repo-wide pin waits until SSCAN ends

#: the control lines readout134b prints at MASTER_SEED, and the safe id each maps to
CONTROL = re.compile(r"^(I2|I3|I5-S|I9) (B0|C\+L[1-3]|A0|P[1-5])\b")
B0_PREFIX = re.compile(r"^B0 r3 background, first 5,000 per pool, (all|unflagged):")
VOID_IDS = (  # (pattern on a VOID list entry, safe id); anything unmatched is relayed as "OTHER"
    (re.compile(r"^I2 (B0|C\+L[1-3]|A0|P[1-5])\b"), "I2 {0}"),
    (re.compile(r"^I3 (B0|C\+L[1-3]|A0|P[1-5])$"), "I3 {0}"),
    (re.compile(r"^I4 C\+$"), "I4 C+"),
    (re.compile(r"^I5-S (B0|A0|P[1-4])$"), "I5-S {0}"),
    (re.compile(r"^I9 (C\+L[1-3]|P5)$"), "I9 {0}"),
    (re.compile(r"^B0 background prefix (all|unflagged)$"), "B0-background-prefix {0}"),
    (re.compile(r"^B0's own k"), "B0-own-k"),
    (re.compile(r"^(B0|C\+L[1-3]|A0|P[1-5]): predicate mismatch"), "predicate-mismatch {0}"),
)


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, [path]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod


R3 = _module("relay134_r3", os.path.join(_HERE, "relay.py"))  # tokens, hashes and hours, reused unchanged
_ASSAY = []


def _conditions():
    """assay.CONDITIONS_134B, imported (not copied) so the check cannot drift from what `run134b` records."""
    if not _ASSAY:
        _ASSAY.append(_module("assay134b_relay", os.path.join(_ROOT, "runs", "RBT-134", "assay.py")))
    return _ASSAY[0].CONDITIONS_134B


def complete(path, head, n_per_pool, n_bg_per_pool, swap):
    """complete: parses, is the file's own condition (and swap or not, as named), at MASTER_SEED, covers both pools at
    n each with n_bg per pool and the condition's registered fields, and was written at HEAD.  stale: complete but
    written at another head, or recording no head (the lane refuses).  incomplete: anything else (the lane re-runs)."""
    name = os.path.basename(path)
    suffix = "-swap.json" if swap else ".json"
    if not name.endswith(suffix) or (not swap and name.endswith("-swap.json")):
        return "incomplete"
    cond = name[:-len(suffix)]
    try:
        r = json.load(open(path))
    except (OSError, ValueError):
        return "incomplete"
    if not isinstance(r, dict) or not isinstance(r.get("pools"), dict) or r.get("condition") != cond:
        return "incomplete"
    if r.get("swap") is not swap or r.get("master_seed") != MASTER_SEED:
        return "incomplete"
    if len(r["pools"]) != 2 or any(v != n_per_pool for v in r["pools"].values()) or r.get("n_per_pool") != n_per_pool:
        return "incomplete"
    fields = _conditions().get(cond)
    if fields is None or r.get("n_bg_per_pool") != n_bg_per_pool or r.get("fields") != json.loads(json.dumps(fields)):
        return "incomplete"
    if r.get("git") != head:
        return "stale"
    return "complete"


def mujoco_ok():
    try:
        import mujoco
    except ImportError:
        return "no"
    return "ok" if mujoco.__version__ == MUJOCO_PIN else "no"


def readout_tokens(readout):
    out, void, in_void = [], [], False
    for line in open(readout).read().splitlines():
        if line.startswith("## VOID"):
            in_void = True
            continue
        if in_void:
            if line.startswith("## "):
                in_void = False
            elif line.strip() == "none":
                void.append("none")
            elif line.startswith("- "):
                entry, safe = line[2:].strip(), "OTHER"
                for pat, fmt in VOID_IDS:
                    m = pat.match(entry)
                    if m:
                        safe = fmt.format(*m.groups())
                        break
                void.append(safe)
            continue
        m = CONTROL.match(line)
        if m:
            out.append(f"{m.group(1)} {m.group(2)}: {R3.tokens(line)}")
            continue
        m = B0_PREFIX.match(line)
        if m:
            out.append(f"B0-background-prefix {m.group(1)}: {R3.tokens(line)}")
    return out, void


def gate(readout):
    """DESIGN.md 13 step 3: PASS iff the controls readout's VOID list is exactly "none"."""
    try:
        _, void = readout_tokens(readout)
    except OSError:
        return "STOP"
    return "PASS" if void == ["none"] else "STOP"


def relay(out_dir, head, committed="no", status="done", stages=()):
    print("===== RELAY RBT-134b registered run =====")
    print(f"head {head} (the GO sha)")
    print(f"status {status}")
    print("COMMITTED yes" if committed == "yes" else
          "NOT COMMITTED (RBT134_NO_PUSH=1 or no push): outputs only under runs/RBT-134/out/134b-20260912/")
    readout = "readout.txt" if status == "done" else "readout-controls.txt"
    path = os.path.join(out_dir, readout)
    tok, void = readout_tokens(path) if os.path.exists(path) else ([], [])
    print(f"TOKENS ({readout})")
    for t in tok:
        print(f"  {t}")
    print("VOID " + (", ".join(void) if void else "MISSING"))
    names = [f for f in os.listdir(out_dir) if not f.endswith((".head", ".tmp"))]
    print("SHA256")
    for line in R3.hashes(out_dir, names):
        print("  " + line.replace("runs/RBT-134/out/", f"runs/RBT-134/out/{os.path.basename(out_dir)}/"))
    for st in stages:
        name, wall, cpu = st.rsplit(":", 2)
        print(f"TIME {name} wall_h={R3.hours(wall)} cpu_h={R3.hours(cpu)}")
    print("===== END RELAY =====")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd in ("complete-run", "complete-swap"):
        print(complete(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), cmd == "complete-swap"))
    elif cmd == "gate":
        print(gate(sys.argv[2]))
    elif cmd == "mujoco-ok":
        print(mujoco_ok())
    elif cmd == "relay":
        ap = argparse.ArgumentParser(prog="relay134b.py relay")
        ap.add_argument("out_dir")
        ap.add_argument("head")
        ap.add_argument("--committed", default="no")
        ap.add_argument("--status", default="done")
        ap.add_argument("stages", nargs="*")
        a = ap.parse_intermixed_args(sys.argv[2:])
        relay(a.out_dir, a.head, a.committed, a.status, a.stages)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
