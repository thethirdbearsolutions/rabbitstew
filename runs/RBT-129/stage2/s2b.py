#!/usr/bin/env python3
"""RBT-129 Stage 2b for the Stage-2a points ("2b(2a)"): the mechanical emitter, its checker and its lane runner
(STAGE2-PLAN.md §2.4, §5.1; S2-R3; FC-4; the #535 adversary's R-4).  Nothing here launches anything.

    /opt/rbt129-venvs/instr/bin/python runs/RBT-129/stage2/s2b.py emit [--hosts 10]   -> runs/RBT-129/lanes/S2B/
    /opt/rbt129-venvs/instr/bin/python runs/RBT-129/stage2/s2b.py run-lane runs/RBT-129/lanes/S2B/hostK-laneL.jsonl

**Why this is fixed before GO-ID-2A.**  ``2B2A: COMMITTED`` (OWNER-DECISIONS-2026-10-03b) commits Stage 2b to whatever
the interim's R4 list names.  So the 2b(2a) design is a pure function, written now, of one input: the committed interim
output's R4 list (``runs/RBT-129/stage2/stage2a_interim.txt``, which ``s2readout.py interim`` writes).  Nothing about it is
chosen after the coordinator has seen that list:

- **Points**: the R4 list, in its order (at most 11; COORD-RULING-512 R4).
- **Seeds**: 129009-129016 at the screened salts of ``lanes/1/launch.txt`` (129010 and 129016 at (1, 0)); every S60 fresh
  on the build; no K-SALT (F7 reads "wherever the census also ran"; O-4).
- **The chain**: S60 → ckpt60 → S to 300 (as R-B's ``stages.rb_units``), then M and N where the gate admits the point,
  each forked from ckpt60 only on seeds valid at the merge (``seed_rule``, at run time).
- **The M/N gate** (``s2b_gate``): DESIGN §5.2 as at Stage 2a (census g0 <= 1.0, designed not FOUNDING-FAIL, not an
  anchor; N where also g0 <= 0.8, among the M points), **within the R-B caps shared with GO-1, Stage-1 points first**:
  M <= 6 less GO-1's M points, N <= 2 less GO-1's N points (``stages.rb_gate``).

**The checker** (``check_s2b``): ``lanes/S2B`` must be exactly ``emit``'s output for the committed interim file, lane by
lane (or that, less the base's ruled exclusions: ``s2lanes.droppable``), and its launch record must name that file's blob.
``s2readout.final`` runs it too, and refuses (HELP) any other set.

**The lane gates** (``run_lane``): the build and pinned trees, the modules, this module's code by blob, the 2a GO with
FC-2 (``s2lanes.check_go``), **and** on the merged base: ``2B2A: COMMITTED``, ``GO-ID-INTERIM`` open, the interim
file the lanes were emitted from, and **the 2b lanes' own lock** ``GO-ID-2B: RBT129-S2-2B-GO-1`` (the coordinator's, added
2026-10-10 so that merging ``lanes/S2B`` does not by itself launch them: every lock the plan registers for 2b(2a) is
already open; ``go2b_open``); then the overflow rule, the emission, the blocks and salts, and every job a 2b(2a) job.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s2lanes  # noqa: E402

stages, s2, blocks = s2lanes.stages, s2lanes.s2, s2lanes.blocks
RUNS, ROOT = s2lanes.RUNS, s2lanes.ROOT

NAME = "S2B"
PREFIX = NAME + "/"
STAGE_DIR = "stage2b"
INTERIM_REL = os.path.join("runs", "RBT-129", "stage2", "stage2a_interim.txt")
R4_HEAD = "## R4 list for 2b(2a)"
DECLINED_LINE = "  declined: the Stage-2a points stay at n = 8 in the final map"
INTERIM_TAG, INTERIM_VALUE = "GO-ID-INTERIM:", "RBT129-S2-INTERIM-GO-1"
#: the 2b lanes' own lock in RULINGS-CITED-S2.md, registered -PENDING and opened by the coordinator's rename (not one of
#: ``stage2_readout.RULED_TAGS``: the readout never reads it, so the pinned readout is unchanged)
GO2B_TAG, GO2B_VALUE = "GO-ID-2B:", "RBT129-S2-2B-GO-1"
SEEDS = s2.SEEDS_HALF2
#: the code a 2b(2a) lane executes outside stages.PINNED_TREES, pinned by blob (as ``s2lanes.CODE_FILES``)
CODE_FILES = s2lanes.CODE_FILES + ("runs/RBT-129/stage2/s2b.py",)


def with_s2b_prefix() -> None:
    """The same documented override as ``s2lanes.with_s2a_prefix``: 2b(2a) jobs are continuations in this process."""
    if PREFIX not in stages.CONTINUATION_PREFIXES:
        stages.CONTINUATION_PREFIXES = stages.CONTINUATION_PREFIXES + (PREFIX,)


# -- the one input: the interim's R4 list ------------------------------------------------------------------------- #

def parse_interim(text: str):
    """The R4 list the interim printed, in its order: a tuple of points; ``None`` when the interim says 2b(2a) is
    declined.  Refused (exit 8) when the text is not an interim output, or its list is malformed or longer than the
    cap."""
    lines = text.splitlines()
    if DECLINED_LINE in lines:
        return None
    heads = [i for i, x in enumerate(lines) if x.startswith(R4_HEAD)]
    if len(heads) != 1:
        stages._refuse("the interim output has no single R4 list (STAGE2-PLAN.md §5.1): 2b(2a) is not emitted", 8)
    m = re.search(r": (\d+) points;", lines[heads[0]])
    pts = []
    for x in lines[heads[0] + 1:]:
        if not x.startswith("  ") or ": CP " not in x:
            break
        pts.append(x.split(":")[0].strip())
    if not m or int(m.group(1)) != len(pts) or len(set(pts)) != len(pts):
        stages._refuse("the interim's R4 list does not match its own count, or repeats a point", 8)
    if not set(pts) <= set(s2.STAGE2A_POINTS) or len(pts) > s2.rb_stage2a_slots():
        stages._refuse(f"the interim's R4 list {pts} is not within the Stage-2a points and the cap"
                       f" {s2.rb_stage2a_slots()}", 8)
    return tuple(pts)


def interim_points(rev: str = "HEAD", root: str = ROOT, path: str = None):
    """The R4 list of the committed interim output at ``rev`` (or of the file ``path``, for a synthetic tree)."""
    text = open(path).read() if path else s2lanes.committed(INTERIM_REL, rev, root)
    if not text:
        stages._refuse(f"{rev}:{INTERIM_REL} is not committed: 2b(2a) is emitted from the committed interim only", 8)
    return parse_interim(text)


# -- the units ------------------------------------------------------------------------------------------------------- #

def go1_slots() -> tuple:
    """(M, N) slots GO-1 takes of the R-B caps (Stage-1 points first; plan §2.4)."""
    rows = stages.rb_gate()
    return sum(1 for r in rows if r["m"]), sum(1 for r in rows if r["n"])


def s2b_gate(points, census_path: str = None) -> list:
    """DESIGN 5.2 at the R4 points, as ``s2lanes.s2a_gate`` reads it, within M <= 6 and N <= 2 less GO-1's."""
    g0, ff = stages.committed_census(census_path)
    gm, gn = go1_slots()
    m_cap, n_cap = s2.M_CAP["2b"] - gm, s2.N_CAP["2b"] - gn
    rows = []
    for pid in points:
        m = pid not in blocks.ANCHORS and pid not in ff and g0.get(pid) is not None and g0[pid] <= stages.GATE_M_G0
        rows.append({"point": pid, "g0": g0.get(pid), "m": m, "n": m and g0[pid] <= stages.GATE_N_G0})
    rows.sort(key=lambda r: (r["g0"] is None, r["g0"] or 0.0, r["point"]))
    m_pts = [r["point"] for r in rows if r["m"]][:max(0, m_cap)]
    n_pts = [r["point"] for r in rows if r["n"] and r["point"] in m_pts][:max(0, n_cap)]
    for r in rows:
        r["m"], r["n"] = r["point"] in m_pts, r["point"] in n_pts
    return rows


def s2b_units(root: str, salts: dict, points, gate: list) -> list:
    """Per R4 point (in the list's order) and seed 9-16: S60 fresh at the seed's screened salts, ckpt60, S to 300, then M
    and N where the gate admits the point, forked from ckpt60 with the seed rule (``stages.rb_units``' chain)."""
    arms = {r["point"]: r for r in gate}
    units = []
    for pid in points:
        for j in SEEDS:
            sd = stages.seed(j)
            s, t = salts[sd]
            d = os.path.join(root, STAGE_DIR, pid, str(sd))
            jobs = [{"job": "fresh", "name": f"{PREFIX}{pid}/{sd}/S60", "point": pid, "seed": sd, "dir": f"{d}/S",
                     "seasons": stages.MERGE, "extra": stages.salts_argv(s, t), "cost": stages.MERGE},
                    {"job": "snapshot", "name": f"{PREFIX}{pid}/{sd}/ckpt60", "src": f"{d}/S", "dir": f"{d}/ckpt60",
                     "seed": sd, "cost": 0},
                    {"job": "resume", "name": f"{PREFIX}{pid}/{sd}/S", "dir": f"{d}/S", "seed": sd,
                     "seasons": stages.SEASONS, "cost": stages.SEASONS - stages.MERGE}]
            base = {"job": "fork", "src": f"{d}/ckpt60", "seed": sd, "seasons": stages.SEASONS, "salts": [s, t],
                    "seed_rule": True, "cost": stages.SEASONS - stages.MERGE}
            if arms[pid]["m"]:
                jobs.append({**base, "name": f"{PREFIX}{pid}/{sd}/M", "dir": f"{d}/M",
                             "set": {"merge_after": stages.MERGE, "pooled_capacity": stages.POOLED}})
            if arms[pid]["n"]:
                jobs.append({**base, "name": f"{PREFIX}{pid}/{sd}/N", "dir": f"{d}/N",
                             "set": {"merge_after": stages.MERGE, "pooled_capacity": stages.POOLED,
                                     "merge_null": stages.null_kind(j)}})
            units.append({"stage": NAME, "seed": sd, "jobs": jobs})
    return units


def emission(points, root: str = RUNS) -> tuple:
    """(units, gate, salts line) for an R4 list, from the committed inputs (``s2lanes.s2a_inputs``)."""
    salts, launch = s2lanes.s2a_inputs(root)
    gate = s2b_gate(points)
    return s2b_units(root, salts, points, gate), gate, launch


def code_pins(root: str = ROOT) -> dict:
    return {f"code:{p}": s2lanes._git(root, "rev-parse", f"HEAD:{p}").stdout.strip() for p in CODE_FILES}


def emit(root: str = RUNS, hosts: int = 10, rev: str = "HEAD") -> list:
    """Write ``lanes/S2B/`` (not launched) from the interim output committed at ``rev``.  Refused (exit 9) off the
    registered build (FC-3), (exit 5) with uncommitted code, (exit 8) when 2b(2a) is declined or the list is empty."""
    import mjbuild

    stages.check_continuation_build()
    for t in CODE_FILES + stages.PINNED_TREES:
        if stages._git("status", "--porcelain", "--", t):
            stages._refuse(f"uncommitted changes under {t}: emit from a committed tree", 5)
    points = interim_points(rev)
    if not points:
        stages._refuse("the interim declines 2b(2a), or its R4 list is empty: nothing to emit", 8)
    units, gate, launch = emission(points, root)
    blob = stages._git("rev-parse", f"{rev}:{INTERIM_REL}")
    extra = {stages.BUILD_KEY: mjbuild.BUILD_LINE, "go": s2lanes.GO_VALUE, "interim": f"{INTERIM_REL} {blob}",
             "salts": launch["salts"], "hosts": hosts, "s2b_points": " ".join(points),
             "s2b_m": " ".join(r["point"] for r in gate if r["m"]), "s2b_n": " ".join(r["point"] for r in gate if r["n"]),
             **code_pins()}
    return stages.emit_lanes(NAME, units, hosts, root, launch["fair"].split(), launch["eat"].split(), extra)


def lane_slices(points, hosts: int, root: str = RUNS) -> dict:
    """{lane file name: the jobs ``emit`` writes there}, as ``stages.emit_lanes`` lays them out (paths as written)."""
    units = emission(points, root)[0]
    worlds = os.path.join(root, "worlds")
    out = {}
    for k, lane in enumerate(stages.layout(units, hosts)):
        out[f"host{k // 2}-lane{k % 2}.jsonl"] = [
            {kk: (stages.rel(v) if kk in stages.PATH_KEYS else v) for kk, v in {**j, "worlds": worlds}.items()}
            for u in lane for j in u["jobs"]]
    return out


def check_s2b(lane_dir: str, points, rev: str = None, root: str = ROOT, interim_blob: str = None,
              runs: str = RUNS, excl: tuple = None) -> dict:
    """R-4: ``lane_dir`` is exactly the emission for ``points`` (the committed interim's R4 list): the same lane files,
    each its slice job for job (or that slice less the ruled exclusions: the base's at ``rev``, or ``excl`` =
    (quarantined, crashed) as given), and a launch record naming the points, the gate, the host count and, when given,
    the interim file's blob.  Refused (exit 4) otherwise.  Returns the launch record."""
    if excl is None:
        excl = s2lanes.ruled_exclusions(rev, root) if rev else ((), (), {})
    launch = stages.read_launch(os.path.join(lane_dir, "launch.txt"))
    gate = s2b_gate(points)
    want_launch = {"s2b_points": " ".join(points), "s2b_m": " ".join(r["point"] for r in gate if r["m"]),
                   "s2b_n": " ".join(r["point"] for r in gate if r["n"])}
    if any(launch.get(k) != v for k, v in want_launch.items()) or "hosts" not in launch:
        stages._refuse(f"{lane_dir}/launch.txt does not record the interim's R4 points and their gate: re-emit", 4)
    if interim_blob and launch.get("interim") != f"{INTERIM_REL} {interim_blob}":
        stages._refuse(f"{lane_dir} was not emitted from the committed interim output (blob {interim_blob})", 4)
    want = lane_slices(points, int(launch["hosts"]), runs)
    have = sorted(f for f in os.listdir(lane_dir) if f.endswith(".jsonl"))
    if have != sorted(want):
        stages._refuse(f"{lane_dir} holds lane files {have}, not the emission's {sorted(want)}", 4)
    for f in have:
        raw = [json.loads(x) for x in open(os.path.join(lane_dir, f)) if x.strip()]
        gone = s2lanes.droppable(want[f], *excl)
        if raw not in (want[f], [j for j in want[f] if j["name"] not in gone]):
            stages._refuse(f"{lane_dir}/{f}: not the emission's lane, nor that lane less its ruled exclusions: re-emit", 4)
    return launch


# -- the lane runner --------------------------------------------------------------------------------------------------- #

def check_code(launch: dict, root: str = ROOT, loaded=None) -> None:
    """``s2lanes.check_code`` for this lane's code (``CODE_FILES``): by blob, committed, nothing else from runs/ (exit 5)."""
    pins = {k[len("code:"):]: v for k, v in launch.items() if k.startswith("code:")}
    if set(pins) != set(CODE_FILES):
        stages._refuse(f"launch.txt pins {sorted(pins)}, not {sorted(CODE_FILES)}: re-emit", 5)
    extra = (s2lanes.loaded_code() | {os.path.relpath(__file__, ROOT)} if loaded is None else set(loaded)) - set(CODE_FILES)
    if extra:
        stages._refuse(f"this process runs code outside the pinned trees that launch.txt does not pin: {sorted(extra)}", 5)
    for p, blob in sorted(pins.items()):
        now = s2lanes._git(root, "rev-parse", f"HEAD:{p}").stdout.strip()
        if now != blob:
            stages._refuse(f"HEAD:{p} is {now or '(absent)'}, not the launch's {blob}: check out the launch commit", 5)
    dirty = s2lanes._git(root, "status", "--porcelain", "--", *CODE_FILES).stdout.strip()
    if dirty:
        stages._refuse("uncommitted changes to the lane's code:\n" + dirty, 5)


def go2b_open(text: str) -> bool:
    """Exactly one ``GO-ID-2B: RBT129-S2-2B-GO-1`` line (an empty, duplicated or other-valued one is not open)."""
    vals = [x.split(":", 1)[1].strip() for x in text.splitlines() if x.startswith(GO2B_TAG)]
    return vals == [GO2B_VALUE]


def check_go_2b(base: str = stages.RULE_BASE, root: str = ROOT) -> str:
    """The 2a GO and FC-2 (``s2lanes.check_go``), then on the merged base: ``2B2A: COMMITTED``, ``GO-ID-INTERIM`` open,
    the committed interim output, and the 2b lanes' own lock (``go2b_open``).  Refused (exit 10) otherwise.  Returns the
    interim file's blob on the base."""
    s2lanes.check_go(base, root)
    rev = f"origin/{base}"
    r = s2lanes.ruled_text(s2lanes.committed(s2lanes.RULINGS_REL, rev, root)) or {}
    if r.get(s2lanes.B2A_TAG) != ["COMMITTED"] or r.get(INTERIM_TAG) != [INTERIM_VALUE]:
        stages._refuse(f"{rev}: 2b(2a) runs only with 2B2A: COMMITTED and {INTERIM_TAG} {INTERIM_VALUE} open"
                       " (STAGE2-PLAN.md §5.1, §10)", 10)
    blob = s2lanes._git(root, "rev-parse", f"{rev}:{INTERIM_REL}").stdout.strip()
    if not blob or len(blob) != 40:
        stages._refuse(f"{rev}:{INTERIM_REL} is not merged: 2b(2a) follows the committed interim only", 10)
    if not go2b_open(s2lanes.committed(s2lanes.RULINGS_REL, rev, root)):
        stages._refuse(f"{rev}: the 2b(2a) lanes are not authorised: {s2lanes.RULINGS_REL} has no '{GO2B_TAG} {GO2B_VALUE}'"
                       " line (the coordinator opens it after the lanes' review)", 10)
    return blob


ALLOWED = {"S60": "fresh", "ckpt60": "snapshot", "S": "resume", "M": "fork", "N": "fork"}


def check_lane_s2b(jobs: list, launch: dict, quarantined=()) -> None:
    """Every job is a 2b(2a) job ``emit`` wrote (exit 4): an R4 point, a seed of 9-16, its kind for its tag, its own
    unit's directories and fork source, M and N only at the gated points with their arm's settings and the seed rule,
    and nothing that touches a quarantined label."""
    pts, m_pts, n_pts = (set(launch.get(k, "").split()) for k in ("s2b_points", "s2b_m", "s2b_n"))
    seeds = {stages.seed(j) for j in SEEDS}
    for j in jobs:
        parts = j["name"].split("/")
        if len(parts) != 4 or parts[0] != NAME or parts[1] not in pts or j["seed"] not in seeds or str(j["seed"]) != parts[2]:
            stages._refuse(f"{j['name']}: not a 2b(2a) job", 4)
        pid, sd, tag = parts[1:]
        unit = os.path.join(STAGE_DIR, pid, sd)
        if ALLOWED.get(tag) != j["job"]:
            stages._refuse(f"{j['name']}: job {j['job']!r} is not the one for {tag}", 4)
        for k in ("dir", "src"):
            if k in j and (stages.is_quarantined(stages._label(j[k]))
                           or any(q.lower() in stages._label(j[k]).lower() for q in quarantined)):
                stages._refuse(f"{j['name']}: touches a quarantined label", 4)
        if not os.path.normpath(j["dir"]).endswith(os.path.join(unit, "S" if tag == "S60" else tag)):
            stages._refuse(f"{j['name']}: its directory is not its unit's", 4)
        if tag in ("M", "N"):
            want = {"merge_after": stages.MERGE, "pooled_capacity": stages.POOLED}
            if tag == "N":
                want["merge_null"] = stages.null_kind(int(sd) - blocks.SEED_BASE)
            if (pid not in (m_pts if tag == "M" else n_pts) or j.get("set") != want or not j.get("seed_rule")
                    or not os.path.normpath(j["src"]).endswith(os.path.join(unit, "ckpt60"))):
                stages._refuse(f"{j['name']}: not a fork the gate admitted, or not its arm's settings and seed rule", 4)


def run_lane(path: str, base: str = stages.RULE_BASE) -> None:
    """``s2lanes.run_lane``'s order for a 2b(2a) lane."""
    with_s2b_prefix()
    lane_dir = os.path.dirname(os.path.abspath(path))
    launch = stages.read_launch(os.path.join(lane_dir, "launch.txt"))
    stages.check_host(launch)
    s2lanes.check_modules()
    check_code(launch)
    blob = check_go_2b(base)
    print(f"overflow rule {os.path.relpath(stages.OVERFLOW_RULE, ROOT)} blob {stages.check_overflow_rule()}", flush=True)
    rev = f"origin/{base}"
    check_s2b(lane_dir, interim_points(rev), rev, interim_blob=blob)
    raw = [json.loads(line) for line in open(path) if line.strip()]
    jobs = [{k: (stages.absolute(v) if k in stages.PATH_KEYS else v) for k, v in j.items()} for j in raw]
    stages.check_lane_blocks(jobs, launch)
    stages.check_lane_salts(jobs, launch)
    check_lane_s2b(jobs, launch, s2lanes.base_quarantined_labels(base))
    os.makedirs(stages.LOCKS, exist_ok=True)
    for job in jobs:
        with open(os.path.join(stages.LOCKS, f"seed-{job['seed']}.lock"), "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            t0 = time.time()
            print(f"{time.strftime('%H:%M:%S')} start {job['name']}", flush=True)
            stages.run_job(job)
            print(f"{time.strftime('%H:%M:%S')} done  {job['name']} ({(time.time() - t0) / 60:.1f} min)", flush=True)
            stages.epa_note(job)
            fcntl.flock(lock, fcntl.LOCK_UN)
    print(f"lane {os.path.basename(path)} complete: {len(jobs)} jobs")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("emit", help="write lanes/S2B from the committed interim output (not launched)")
    e.add_argument("--hosts", type=int, default=10)
    r = sub.add_parser("run-lane", help="run one 2b(2a) lane file (refused until its gates pass)")
    r.add_argument("lane")
    a = ap.parse_args(argv)
    if a.cmd == "emit":
        for p in emit(RUNS, a.hosts):
            print(os.path.relpath(p, ROOT))
        return 0
    run_lane(a.lane)
    return 0


if __name__ == "__main__":
    sys.exit(main())
