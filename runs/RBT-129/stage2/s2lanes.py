#!/usr/bin/env python3
"""RBT-129 Stage 2a: emission and lane runner on the registered build (c) (STAGE2-PLAN.md §2, §11; COORD-RULING-523;
COORD-RULING-527).  Nothing here launches anything.

    /opt/rbt129-venvs/instr/bin/python runs/RBT-129/stage2/s2lanes.py emit [--hosts 10]   -> runs/RBT-129/lanes/S2A/
    /opt/rbt129-venvs/instr/bin/python runs/RBT-129/stage2/s2lanes.py run-lane runs/RBT-129/lanes/S2A/hostK-laneL.jsonl

**Why it lives outside the pinned trees** (COORD-RULING-527 T5, NOTE 17).  The SCAN and RB lanes pin
``runs/RBT-129/launch``, ``scripts`` and ``rabbitstew``; any change there would make their restarts refuse (exit 5).
This module changes none of them.  It **imports** ``stages`` and reuses its guards, its job runner and its emitter
unchanged, and adds only:

1. **The Stage-2a units** (plan §2.1-§2.3): 12 points x seeds 129001-129008, S60 → ckpt60 → S to 300 on the build, M and
   N at the gated points, each forked from ckpt60 only on seeds valid at the merge (``seed_rule``, as R-B).
2. **O-2's re-simulation and byte-equality adoption** (plan §2.1, A-12; owner-approved, OWNER-DECISIONS-2026-10-03b):
   129001's S 0-59 is re-simulated fresh on the build at salts (0, 0), then ``s60cmp`` compares it with the census's
   S 0-59 at the same point, file by file (logs, provenance and the EPA log excluded; config.json compared bar
   ``workers``).  **IDENTICAL**: the chain goes on from the re-simulated state, which *is* the census state, now
   scanned.  **DIFFER**: the lane stops (HELP, exit 4), and the DIFFER is saved to the unit's branch, so every later
   job of the unit refuses on every restart (``require_identical``; #533 adversary BLOCKING 1).
3. **K-SALT** (F7) at 129002 and 129003 against the census, with ``stages``' own ``ksalt`` job.
4. **The lane gates**: the build (``stages.check_host``); the code the lane executes outside the pinned trees, pinned
   by blob in launch.txt and committed (``check_code``: the lock and ruling files are not pinned, so opening a GO or
   ruling a quarantine leaves a lane runnable; MAJOR 2); the overflow rule (``stages.check_overflow_rule``); **the 2a
   GO**, read from the merged base after a narrow fetch that must succeed, with ``2B2A`` ruled in a strict ancestor of
   the commit that opened it (``check_go``; MINOR 5, 6); the lane file equal to its slice of the emission
   (``check_emission``; MINOR 7); and the quarantine lines of the base as well as HEAD's.
5. **One documented override**: ``stages.CONTINUATION_PREFIXES`` gains ``"S2A/"`` in this process only, so that
   ``stages.run_job`` runs Stage-2a jobs as continuations (through ``epa_ecology.py``, the build check, the EPA log,
   ``check_not_crashed``).  Nothing else of ``stages`` is replaced.
"""
from __future__ import annotations

import argparse
import fcntl
import importlib.util
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUNS))
LAUNCH = os.path.join(RUNS, "launch")
if LAUNCH not in sys.path:
    sys.path.insert(0, LAUNCH)
import blocks  # noqa: E402
import stages  # noqa: E402

_spec = importlib.util.spec_from_file_location("stage2_readout", os.path.join(RUNS, "stage2-plan", "stage2_readout.py"))
s2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s2)

NAME = "S2A"                       # lanes/S2A, and the job-name prefix
PREFIX = NAME + "/"
STAGE_DIR = "stage2a"              # runs/RBT-129/stage2a/<point>/<seed>/{S, s60cmp, ksalt, ckpt60, M, N}
#: the trees this module and the plan live in (outside stages.PINNED_TREES; NOTE 17)
OWN_TREES = ("runs/RBT-129/stage2", "runs/RBT-129/stage2-plan")
#: the code a Stage-2a lane executes outside stages.PINNED_TREES, pinned **by blob** in launch.txt (``code:<path>``;
#: #533 adversary MAJOR 2).  The lock and ruling files beside it (RULINGS-CITED-S2.md, continuations/QUARANTINE.md)
#: and the plan's prose are not pinned: opening a GO, a ruled QUARANTINE: line or a plan edit leaves a lane runnable,
#: and any change to executed code refuses it (exit 5).  ``check_code`` also refuses a process that loaded code from
#: under runs/ outside the pinned trees that is not one of these files.
CODE_FILES = ("runs/RBT-129/stage2/s2lanes.py", "runs/RBT-129/stage2-plan/stage2_readout.py",
              "runs/RBT-129/stage1-readout/stage1_readout.py")
UNPINNED = ("runs/RBT-129/stage2-plan/RULINGS-CITED-S2.md", "runs/RBT-129/continuations/QUARANTINE.md")
RULINGS_REL = os.path.join("runs", "RBT-129", "stage2-plan", "RULINGS-CITED-S2.md")
GO_TAG, GO_VALUE = "GO-ID-2A:", "RBT129-S2-2A-GO-1"
B2A_TAG = "2B2A:"
SEEDS = tuple(range(1, stages.STAGE1_N + 1))
#: F7 / T10: the census's seeds; 129001 is re-simulated and compared (O-2), 129002-129003 take K-SALT
CENSUS_SEEDS = (1, 2, 3)
S60CMP_FILE = "S60CMP.txt"
#: not compared by s60cmp: logs and provenance (the re-simulation records the build), every EPA log, done-markers, the
#: verdict itself; config.json is compared separately, bar ``workers`` (``stages._arm_config``), as adopt_census does
S60CMP_SKIP = ("config.json", "platform.json", "command.txt", "run.log", "durable.log", "run.lock", S60CMP_FILE)


def with_s2a_prefix() -> None:
    """The one override (module docstring, item 5): Stage-2a jobs are continuations in this process."""
    if PREFIX not in stages.CONTINUATION_PREFIXES:
        stages.CONTINUATION_PREFIXES = stages.CONTINUATION_PREFIXES + (PREFIX,)


# -- the units (plan §2.1-§2.3) ----------------------------------------------------------------------------------- #

def s2a_gate(census_path: str = None) -> list:
    """DESIGN 5.2 / T5 at the 12 Stage-2a points, from the committed census (``stages.committed_census``, the readout
    the Stage-1 and R-B gates read): M where g0 <= 1.0, designed not FOUNDING-FAIL and not an anchor, lowest g0 first, up
    to 4; N at the M points with g0 <= 0.8, up to 2.  The seed rule applies at run time (``seed_rule``).  Equals the
    plan's ``stage2_readout.mn_gate`` (a test holds them together)."""
    g0, ff = stages.committed_census(census_path)
    rows = []
    for pid in s2.STAGE2A_POINTS:
        m = pid not in blocks.ANCHORS and pid not in ff and g0.get(pid) is not None and g0[pid] <= stages.GATE_M_G0
        rows.append({"point": pid, "g0": g0.get(pid), "m": m, "n": m and g0[pid] <= stages.GATE_N_G0})
    rows.sort(key=lambda r: (r["g0"] is None, r["g0"] or 0.0, r["point"]))
    m_pts = [r["point"] for r in rows if r["m"]][:s2.M_CAP["2a"]]
    n_pts = [r["point"] for r in rows if r["n"] and r["point"] in m_pts][:s2.N_CAP["2a"]]
    for r in rows:
        r["m"], r["n"] = r["point"] in m_pts, r["point"] in n_pts
    return rows


def s2a_units(root: str, salts: dict, gate: list) -> list:
    """Per point and seed 1-8: S60 fresh on the build at the seed's screened salts; at 129001 the ``s60cmp`` against
    the census (O-2); at 129002-129003 K-SALT; ckpt60; S to 300; M and N where the gate admits the point, forked from
    ckpt60 only if the seed is valid at the merge.  Seed 129001 must have salts (0, 0) (T10), or emission refuses."""
    arms = {r["point"]: r for r in gate}
    units = []
    for pid in s2.STAGE2A_POINTS:
        for j in SEEDS:
            s, t = salts[stages.seed(j)]
            sd = stages.seed(j)
            d = os.path.join(root, STAGE_DIR, pid, str(sd))
            census = os.path.join(root, "stage0", pid, str(sd), "S")
            jobs = [{"job": "fresh", "name": f"{PREFIX}{pid}/{sd}/S60", "point": pid, "seed": sd, "dir": f"{d}/S",
                     "seasons": stages.MERGE, "extra": stages.salts_argv(s, t), "cost": stages.MERGE}]
            if j == stages.RESUME_SEED:
                if (s, t) != (0, 0):
                    stages._refuse(f"{sd}: salts {(s, t)}, not (0, 0): O-2's census comparison needs the census's own salts", 8)
                jobs.append({"job": "s60cmp", "name": f"{PREFIX}{pid}/{sd}/S60CMP", "point": pid, "seed": sd,
                             "src": f"{d}/S", "ref": census, "dir": f"{d}/s60cmp", "seasons": stages.MERGE, "cost": 0})
            elif j in CENSUS_SEEDS and s >= 1 and t == 0:
                jobs.append({"job": "ksalt", "name": f"{PREFIX}{pid}/{sd}/KSALT", "seed": sd, "src": f"{d}/S", "ref": census,
                             "dir": f"{d}/ksalt", "cost": 0})
            jobs += [{"job": "snapshot", "name": f"{PREFIX}{pid}/{sd}/ckpt60", "src": f"{d}/S", "dir": f"{d}/ckpt60", "seed": sd,
                      "cost": 0},
                     {"job": "resume", "name": f"{PREFIX}{pid}/{sd}/S", "dir": f"{d}/S", "seed": sd, "seasons": stages.SEASONS,
                      "cost": stages.SEASONS - stages.MERGE}]
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


def arm_seasons(units: list) -> dict:
    """Arm-seasons by arm (the plan's budget counts them the same way: plan §2.5, ``stage2_readout.budget``)."""
    out = {"S": 0, "M": 0, "N": 0}
    for u in units:
        for j in u["jobs"]:
            arm = j["name"].rsplit("/", 1)[1]
            key = "S" if arm in ("S60", "S") else arm if arm in ("M", "N") else None
            if key:
                out[key] += j["cost"]
    return out


def s2a_inputs(root: str) -> tuple:
    """(salts, launch): Stage 1's screened salts (lanes/1 = lanes/1-MN) and flags; the registered inputs check
    (``stage2_readout.check_inputs``: the accepted record and both lists); refused (exit 8) otherwise."""
    launch = stages.read_launch(os.path.join(root, "lanes", "1", "launch.txt"))
    mn = stages.read_launch(os.path.join(root, "lanes", stages.MN_LANES, "launch.txt"))
    if launch.get("salts") != mn.get("salts"):
        stages._refuse("lanes/1 and lanes/1-MN record different salts", 8)
    bad = s2.check_inputs()
    if bad:
        stages._refuse("the registered inputs do not check: " + "; ".join(bad), 8)
    return stages._salts_line(launch["salts"]), launch


def emit(root: str, hosts: int) -> list:
    """Write ``lanes/S2A/`` (not launched).  Refused (exit 9) unless this process runs the registered build (FC-3, as
    every emitter), and unless the trees this lane pins are committed."""
    import mjbuild

    stages.check_continuation_build()
    for t in CODE_FILES + stages.PINNED_TREES:
        if stages._git("status", "--porcelain", "--", t):
            stages._refuse(f"uncommitted changes under {t}: emit from a committed tree", 5)
    salts, launch = s2a_inputs(root)
    gate = s2a_gate()
    units = s2a_units(root, salts, gate)
    extra = {stages.BUILD_KEY: mjbuild.BUILD_LINE, "go": GO_VALUE, "salts": launch["salts"], "hosts": hosts,
             "s2a_points": " ".join(s2.STAGE2A_POINTS),
             "s2a_m": " ".join(r["point"] for r in gate if r["m"]), "s2a_n": " ".join(r["point"] for r in gate if r["n"]),
             **code_pins()}
    return stages.emit_lanes(NAME, units, hosts, root, launch["fair"].split(), launch["eat"].split(), extra)


def lane_jobs_emitted(path: str, launch: dict, root: str = RUNS) -> list:
    """The jobs ``emit`` writes to the lane file ``path`` (``hostK-laneL.jsonl``), rebuilt now from the committed
    inputs (``s2a_inputs``: the salts of lanes/1, the registered inputs check) and the committed census gate, at the
    launch's host count, as ``stages.emit_lanes`` lays them out (MINOR 7)."""
    import re

    m = re.fullmatch(r"host(\d+)-lane([01])\.jsonl", os.path.basename(path))
    if not m or "hosts" not in launch:
        stages._refuse(f"{path}: not a lane file of an S2A launch with a hosts line: re-emit", 4)
    salts, base = s2a_inputs(root)
    if base["salts"] != launch.get("salts"):
        stages._refuse("launch.txt's salts are not lanes/1's: re-emit", 4)
    lanes = stages.layout(s2a_units(root, salts, s2a_gate()), int(launch["hosts"]))
    k = 2 * int(m.group(1)) + int(m.group(2))
    if k >= len(lanes):
        stages._refuse(f"{path}: no such lane in the emission ({len(lanes)} lanes)", 4)
    worlds = os.path.join(root, "worlds")
    return [{kk: (stages.rel(v) if kk in stages.PATH_KEYS else v) for kk, v in {**j, "worlds": worlds}.items()}
            for u in lanes[k] for j in u["jobs"]]


def check_emission(path: str, launch: dict, raw: list) -> None:
    """MINOR 7: the lane file is exactly its slice of the emission, job for job and in order (exit 4)."""
    want = lane_jobs_emitted(path, launch)
    if raw != want:
        bad = next((i for i, (a, b) in enumerate(zip(raw, want)) if a != b), min(len(raw), len(want)))
        stages._refuse(f"{os.path.basename(path)}: not the emission's lane (first difference at job {bad + 1};"
                       f" {len(raw)} jobs, {len(want)} emitted): re-emit", 4)


# -- the lane gates ------------------------------------------------------------------------------------------------ #

def _git(root: str, *a) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True)


def committed(path_rel: str, rev: str = "HEAD", root: str = ROOT) -> str:
    return _git(root, "show", f"{rev}:{path_rel}").stdout


def ruled_text(text: str):
    """The plan's own parser (``stage2_readout.ruled_lines``) on a text; None when it is a HELP (a duplicated or empty
    ruled line)."""
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(text)
    try:
        return s2.ruled_lines(f.name)
    except s2.Stage2Help:
        return None
    finally:
        os.remove(f.name)


def go_open(text: str) -> bool:
    """Exactly one ``GO-ID-2A: RBT129-S2-2A-GO-1`` line and exactly one ``2B2A: COMMITTED|DECLINED`` line, through the
    plan's own parser (``stage2_readout.ruled_lines``: a duplicated or empty ruled line is a HELP)."""
    r = ruled_text(text)
    return r is not None and r.get(GO_TAG) == [GO_VALUE] and r.get(B2A_TAG, [None])[0] in s2.B2A_VALUES


def b2a(text: str):
    """The ruled ``2B2A:`` value of a text, or None (missing, duplicated or malformed)."""
    v = (ruled_text(text) or {}).get(B2A_TAG) or []
    return v[0] if len(v) == 1 and v[0] in s2.B2A_VALUES else None


def fetch_base(base: str = stages.RULE_BASE, root: str = ROOT) -> str:
    """A narrow fetch of the base; a failed fetch refuses (exit 10, MINOR 6): a GO is read from the merged base only,
    never from a stale tracking ref."""
    r = _git(root, "fetch", "-q", "origin", f"+refs/heads/{base}:refs/remotes/origin/{base}")
    if r.returncode != 0:
        stages._refuse(f"the narrow fetch of origin/{base} failed (exit {r.returncode}): the 2a GO is read from the"
                       " merged base only, so the lane does not run on a stale tracking ref", 10)
    return f"origin/{base}"


def check_go(base: str = stages.RULE_BASE, root: str = ROOT) -> None:
    """The 2a GO (plan §2.7, §11; COORD-RULING-523 P4), read from the **merged base** (a narrow fetch; a failed fetch
    refuses), so a lock opened only locally never runs a lane, and a lane at an older HEAD still runs once later locks
    land on the base (MAJOR 2).  Refused (exit 10) unless ``origin/<base>:RULINGS-CITED-S2.md`` opens it and FC-2
    holds: the commit that opened ``GO-ID-2A`` is a strict descendant of the one that ruled ``2B2A`` (its parent
    already carries the base's 2B2A value; MINOR 5)."""
    rev = fetch_base(base, root)
    if not go_open(committed(RULINGS_REL, rev, root)):
        stages._refuse(f"{rev}:{RULINGS_REL} does not open the 2a GO ({GO_TAG} {GO_VALUE}, with {B2A_TAG} set): Stage"
                       " 2a does not run (STAGE2-PLAN.md §2.7)", 10)
    log = _git(root, "log", "--format=%H", f"-S{GO_TAG} {GO_VALUE}", rev, "--", RULINGS_REL)
    opened = log.stdout.split()
    if log.returncode != 0 or not opened:
        stages._refuse(f"the commit that opened {GO_TAG} is not in this clone's history of {rev} (a shallow clone?):"
                       " FC-2 cannot be checked", 10)
    if _git(root, "cat-file", "-e", opened[0] + "^").returncode != 0:
        stages._refuse(f"the parent of {opened[0][:12]} (which opened {GO_TAG}) is not in this clone (shallow): FC-2"
                       f" cannot be checked; fetch more of origin/{base}'s history", 10)
    ruled = b2a(committed(RULINGS_REL, rev, root))
    before = b2a(committed(RULINGS_REL, opened[0] + "^", root))
    if before is None or before != ruled:
        stages._refuse(f"FC-2: {GO_TAG} was opened in {opened[0][:12]}, whose parent does not already rule {B2A_TAG}"
                       f" {ruled}: the 2B2A ruling must precede the GO in a strict ancestor commit", 10)


def base_quarantined_labels(base: str = stages.RULE_BASE, root: str = ROOT) -> list:
    """Every ``QUARANTINE:`` line of ``stages.QUARANTINE_FILES`` as merged on the base (fetched by ``check_go``), so a
    quarantine ruled after a lane's commit reaches it (MAJOR 2).  An empty line refuses (exit 4), as in ``stages``."""
    out = []
    for path in stages.QUARANTINE_FILES:
        for line in committed(path, f"origin/{base}", root).splitlines():
            if line.startswith("QUARANTINE:"):
                label = line.split(":", 1)[1].strip()
                if not label:
                    stages._refuse(f"an empty QUARANTINE: line in origin/{base}:{path}", 4)
                out.append(label)
    return out


def code_pins(root: str = ROOT) -> dict:
    """``{"code:<path>": blob}`` at HEAD for ``CODE_FILES``."""
    return {f"code:{p}": _git(root, "rev-parse", f"HEAD:{p}").stdout.strip() for p in CODE_FILES}


def loaded_code() -> set:
    """The repository paths of this process's code outside ``stages.PINNED_TREES``: this module, the plan's readout, the
    Stage-1 readout it imports, and any other module loaded from under runs/."""
    files = {__file__, s2.__file__, s2.sr.__file__}
    runs = os.path.join(ROOT, "runs") + os.sep
    files |= {m.__file__ for m in list(sys.modules.values())
              if isinstance(getattr(m, "__file__", None), str) and os.path.abspath(m.__file__).startswith(runs)}
    rels = {os.path.relpath(os.path.abspath(f), ROOT) for f in files}
    return {r for r in rels if not any(r == t or r.startswith(t + "/") for t in stages.PINNED_TREES)}


def check_code(launch: dict, root: str = ROOT, loaded=None) -> None:
    """MAJOR 2: the code a lane executes outside the pinned trees is the launch's, by blob, and committed (exit 5).  The
    lock and ruling files are not pinned (``UNPINNED``)."""
    pins = {k[len("code:"):]: v for k, v in launch.items() if k.startswith("code:")}
    if set(pins) != set(CODE_FILES):
        stages._refuse(f"launch.txt pins {sorted(pins)}, not {sorted(CODE_FILES)}: re-emit", 5)
    extra = (loaded_code() if loaded is None else set(loaded)) - set(CODE_FILES)
    if extra:
        stages._refuse(f"this process runs code outside the pinned trees that launch.txt does not pin: {sorted(extra)}", 5)
    for p, blob in sorted(pins.items()):
        now = _git(root, "rev-parse", f"HEAD:{p}").stdout.strip()
        if now != blob:
            stages._refuse(f"HEAD:{p} is {now or '(absent)'}, not the launch's {blob}: the lane runs the code it was"
                           " emitted with; check out the launch commit, or re-emit", 5)
    dirty = _git(root, "status", "--porcelain", "--", *CODE_FILES).stdout.strip()
    if dirty:
        stages._refuse("uncommitted changes to the lane's code:\n" + dirty, 5)


ALLOWED = {"S60": "fresh", "S60CMP": "s60cmp", "KSALT": "ksalt", "ckpt60": "snapshot", "S": "resume", "M": "fork", "N": "fork"}


def check_lane_s2a(jobs: list, launch: dict, quarantined=()) -> None:
    """Every job is a Stage-2a job emit wrote (exit 4): its point and seed, its kind for its tag, the census reference
    of its own point and seed, the fork source of its own unit with its arm's settings and the seed rule, M and N only
    at the gated points, and nothing that touches a quarantined label or the CRASHED Stage-1 unit."""
    pts, m_pts, n_pts = set(launch.get("s2a_points", "").split()), set(launch.get("s2a_m", "").split()), set(launch.get("s2a_n", "").split())
    if launch.get("go") != GO_VALUE or stages.BUILD_KEY not in launch or not pts:
        stages._refuse("not a Stage-2a launch.txt (go, mujoco_build and s2a_points lines): re-emit", 4)
    seeds = {stages.seed(j) for j in SEEDS}
    for j in jobs:
        parts = j["name"].split("/")
        if len(parts) != 4 or parts[0] != NAME or parts[1] not in pts or j["seed"] not in seeds or str(j["seed"]) != parts[2]:
            stages._refuse(f"{j['name']}: not a Stage-2a job (points {sorted(pts)}, seeds {min(seeds)}-{max(seeds)})", 4)
        pid, sd, tag = parts[1], parts[2], parts[3]
        unit = os.path.join(STAGE_DIR, pid, sd)
        if ALLOWED.get(tag) != j["job"]:
            stages._refuse(f"{j['name']}: job {j['job']!r} is not the one for {tag}", 4)
        for k in ("dir", "src", "ref"):
            if k in j and (stages.is_quarantined(stages._label(j[k]))
                           or any(q.lower() in stages._label(j[k]).lower() for q in quarantined)):
                stages._refuse(f"{j['name']}: touches a quarantined label (RULING.md item 3)", 4)
        if not os.path.normpath(j["dir"]).endswith(os.path.join(unit, {"S60": "S", "S60CMP": "s60cmp", "KSALT": "ksalt"}.get(tag, tag))):
            stages._refuse(f"{j['name']}: its directory is not its unit's", 4)
        if tag in ("S60CMP", "KSALT"):
            ok_seed = int(sd) == stages.seed(stages.RESUME_SEED) if tag == "S60CMP" else int(sd) in {stages.seed(x) for x in CENSUS_SEEDS[1:]}
            if not ok_seed or not os.path.normpath(j["ref"]).endswith(os.path.join("stage0", pid, sd, "S")):
                stages._refuse(f"{j['name']}: not its point's census reference at its seed", 4)
        if tag in ("M", "N"):
            want = {"merge_after": stages.MERGE, "pooled_capacity": stages.POOLED}
            if tag == "N":
                want["merge_null"] = stages.null_kind(int(sd) - blocks.SEED_BASE)
            if (pid not in (m_pts if tag == "M" else n_pts) or j.get("set") != want or not j.get("seed_rule")
                    or not os.path.normpath(j["src"]).endswith(os.path.join(unit, "ckpt60"))):
                stages._refuse(f"{j['name']}: not a fork the gate admitted, or not its arm's settings and seed rule", 4)


# -- O-2: the re-simulation against the census (plan §2.1, A-12) --------------------------------------------------- #

def s60_files(d: str) -> dict:
    out = {}
    for base, _, files in os.walk(d):
        for n in files:
            if n in S60CMP_SKIP or n.startswith(".rbt129-done-") or n.startswith("epa_overflow"):
                continue
            out[os.path.relpath(os.path.join(base, n), d)] = os.path.join(base, n)
    return out


def s60_verdict(resim: str, census: str) -> tuple:
    """(IDENTICAL | DIFFER, lines): config.json equal bar ``workers``, and every other output file byte for byte.
    The lines name files, never contents."""
    lines = []
    if stages._arm_config(resim) != stages._arm_config(census):
        lines.append("DIFFERS: config.json (bar workers)")
    a, b = s60_files(resim), s60_files(census)
    lines += [f"only in {'re-simulation' if n in a else 'census'}: {n}" for n in sorted(set(a) ^ set(b))]
    for n in sorted(set(a) & set(b)):
        if open(a[n], "rb").read() != open(b[n], "rb").read():
            lines.append(f"DIFFERS: {n}")
    return ("IDENTICAL" if not lines else "DIFFER"), [f"{len(set(a) & set(b))} files compared"] + lines


def s60_compare(job: dict, d: str) -> str:
    """The ``s60cmp`` job: the re-simulated S 0-59 against the census's (restored from its own branch), written to
    ``d/S60CMP.txt`` and printed as the verdict only.  The re-simulation must stand at season 60 (its S not yet resumed),
    else refused (exit 4).  DIFFER stops the lane (HELP): the chain is not adopted."""
    src, ref = job["src"], job["ref"]
    for x in (src, ref):
        if stages.is_quarantined(stages._label(x)):
            stages._refuse(f"{job['name']}: a quarantined run is never read (RULING.md item 3)", 4)
    stages._restore(ref)
    if not os.path.exists(os.path.join(ref, "state.json")):
        stages._refuse(f"{job['name']}: the census run {stages.rel_or_abs(ref)} is not here and has no snapshot", 4)
    at = json.load(open(os.path.join(src, "state.json")))["season"]
    if at != job.get("seasons", stages.MERGE):
        stages._refuse(f"{job['name']}: {stages.rel_or_abs(src)} is at season {at}, not {job.get('seasons', stages.MERGE)}:"
                       " the comparison runs before S resumes", 4)
    verdict, lines = s60_verdict(src, ref)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, S60CMP_FILE), "w") as f:
        f.write(f"S60CMP {verdict}: the re-simulation {stages.rel_or_abs(src)} (build (c)) against the census"
                f" {stages.rel_or_abs(ref)}, seasons 0-{job.get('seasons', stages.MERGE) - 1} (O-2)\n"
                + "".join(f"  {x}\n" for x in lines))
    print(f"{job['name']}: S60CMP {verdict}", flush=True)  # the comparison's verdict, not an outcome
    if verdict != "IDENTICAL":
        # durable before the refusal (BLOCKING 1): the DIFFER is saved to the unit's own ckpt branch in the foreground,
        # so every later job of the unit, on any restart in any container, finds it and refuses
        stages._mark(d, job["name"].rsplit("/", 1)[1], "S60CMP DIFFER")
        if not os.environ.get("NO_DURABLE"):
            stages.save_now(d)
        differ_refusal(job["name"])
    return verdict


def differ_refusal(name: str):
    stages._refuse(f"{name}: S60CMP DIFFER: the re-simulation is not the census run; the chain is not adopted"
                   " (STAGE2-PLAN.md §2.1, O-2): HELP, tell the coordinator.  Every later job of this unit refuses, on"
                   " every restart", 4)


def s60cmp_word(d: str):
    """The recorded verdict in ``d`` (the s60cmp directory): IDENTICAL only when both ``S60CMP.txt``'s first line and the
    done-marker's note say so; DIFFER when either says DIFFER; None when there is no complete record."""
    tag = "S60CMP"
    try:
        first = open(os.path.join(d, S60CMP_FILE)).readline().split()
    except OSError:
        first = []
    word = first[1].rstrip(":") if len(first) > 1 and first[0] == "S60CMP" else None
    note = (stages._marker_text(d, tag) or "").split(" ", 1)[-1].strip()
    if word == "DIFFER" or note == "S60CMP DIFFER":
        return "DIFFER"
    if word == "IDENTICAL" and note == "S60CMP IDENTICAL":
        return "IDENTICAL"
    return None


def require_identical(job: dict) -> None:
    """BLOCKING 1: every job of the 129001 unit after its S60 (ckpt60, S, M, N) runs only beside a saved
    ``S60CMP IDENTICAL``: the unit's s60cmp directory is restored from its branch, its marker must be on the branch
    (``stages._finished``), and the verdict must read IDENTICAL.  A DIFFER refuses (exit 4, HELP); no record refuses
    too (exit 4): O-2's comparison runs first."""
    d = os.path.join(os.path.dirname(os.path.normpath(job["dir"])), "s60cmp")
    stages._restore(d, S60CMP_FILE)
    word = s60cmp_word(d) if stages._finished(d, "S60CMP") else None
    if word == "DIFFER":
        differ_refusal(job["name"])
    if word != "IDENTICAL":
        stages._refuse(f"{job['name']}: no saved S60CMP IDENTICAL beside it ({stages.rel_or_abs(d)}): O-2's comparison"
                       " adopts the re-simulation first (STAGE2-PLAN.md §2.1)", 4)


# -- the runner ---------------------------------------------------------------------------------------------------- #

def run_job(job: dict) -> None:
    """``s60cmp`` here; every other job through ``stages.run_job`` unchanged (as a continuation, ``with_s2a_prefix``).
    A finished ``s60cmp`` is skipped only when its saved verdict is IDENTICAL (a DIFFER refuses again, exit 4), and every
    job of the 129001 unit after its S60 needs that IDENTICAL beside it (BLOCKING 1)."""
    tag = job["name"].rsplit("/", 1)[1]
    if job["job"] != "s60cmp":
        if job["seed"] == stages.seed(stages.RESUME_SEED) and tag != "S60":
            require_identical(job)
        stages.run_job(job)
        return
    d = job["dir"]
    stages._restore(d, S60CMP_FILE)
    if stages._finished(d, tag):
        if s60cmp_word(d) != "IDENTICAL":
            differ_refusal(job["name"])
        return
    s60_compare(job, d)
    stages._finish(d, tag, "S60CMP IDENTICAL")


def run_lane(path: str, base: str = stages.RULE_BASE) -> None:
    """``stages.run_lane``'s order, with Stage 2a's gates added: the host and build (``check_host``), this module's
    trees, the 2a GO, the overflow rule, the blocks and salts, the Stage-2a job check; then the jobs under the seed
    lock, each followed by its EPA overflow count (``stages.epa_note``)."""
    with_s2a_prefix()
    launch = stages.read_launch(os.path.join(os.path.dirname(os.path.abspath(path)), "launch.txt"))
    stages.check_host(launch)
    check_code(launch)
    check_go(base)
    print(f"overflow rule {os.path.relpath(stages.OVERFLOW_RULE, ROOT)} blob {stages.check_overflow_rule()}", flush=True)
    raw = [json.loads(line) for line in open(path) if line.strip()]
    check_emission(path, launch, raw)
    jobs = [{k: (stages.absolute(v) if k in stages.PATH_KEYS else v) for k, v in j.items()} for j in raw]
    stages.check_lane_blocks(jobs, launch)
    stages.check_lane_salts(jobs, launch)
    check_lane_s2a(jobs, launch, base_quarantined_labels(base))
    os.makedirs(stages.LOCKS, exist_ok=True)
    for job in jobs:
        with open(os.path.join(stages.LOCKS, f"seed-{job['seed']}.lock"), "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            t0 = time.time()
            print(f"{time.strftime('%H:%M:%S')} start {job['name']}", flush=True)
            run_job(job)
            print(f"{time.strftime('%H:%M:%S')} done  {job['name']} ({(time.time() - t0) / 60:.1f} min)", flush=True)
            if job["job"] in ("fresh", "resume", "fork"):
                stages.epa_note(job)
            fcntl.flock(lock, fcntl.LOCK_UN)
    print(f"lane {os.path.basename(path)} complete: {len(jobs)} jobs")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("emit", help="write lanes/S2A (not launched); needs the registered build")
    e.add_argument("--hosts", type=int, default=10)
    r = sub.add_parser("run-lane", help="run one Stage-2a lane file (refused until the 2a GO is open)")
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
