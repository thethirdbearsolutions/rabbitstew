#!/usr/bin/env python3
"""RBT-129 Stage 1 readout (S arm, and the gated M and N forks): the script of ``READOUT-PLAN.md`` (pre-data).

    python3 runs/RBT-129/stage1-readout/stage1_readout.py integrity --go RULING_REF   -> stage1-readout/integrity.txt
    python3 runs/RBT-129/stage1-readout/stage1_readout.py readout   --go RULING_REF   -> stage1-readout/stage1_readout.txt

**It refuses to run without ``--go``**, the reference of the coordinator's ruling that lets the readout open Stage-1
outputs (plan section 1, step 0).  Its tests (``tests/test_rbt129_stage1_readout.py``) use synthetic fixtures only.

**The quarantine** (``mn-crash/RULING.md`` r3, item 3): every function here that fetches, restores, lists or reads a
branch or a run directory goes through :func:`refuse_quarantined`, which raises :class:`QuarantineRefusal` for the
label ``rbt-129-stage1-c2-p030-U-G-129001-M`` and for any path at or under ``runs/RBT-129/stage1/c2-p030-U-G/129001/M``,
before any reader is called.  ``lanes/1-MN/host1-lane0.jsonl``, the lane that schedules that unit, is never loaded as a
lane: :func:`crash_reconcile` reads only its job names.

Section numbers below are the plan's.  Every statistic is implemented as a pure function of per-seed values, so that
the tests can pin each registered rule on made-up numbers; the readers (``read_run``) are thin and guarded.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUNS))
sys.path.insert(0, os.path.join(RUNS, "launch"))

# -- registered constants ------------------------------------------------------------------------------------------ #

QUARANTINED_LABEL = "rbt-129-stage1-c2-p030-U-G-129001-M"
QUARANTINED_DIR = os.path.join("runs", "RBT-129", "stage1", "c2-p030-U-G", "129001", "M")
CRASHED_JOB = "1/c2-p030-U-G/129001/M"
CRASHED_POINT, CRASHED_SEED = "c2-p030-U-G", 129001
CRASHED_LINE = ("CRASHED: 1/c2-p030-U-G/129001/M (native SIGSEGV in libmujoco 3.14.0, projectOriginPlane under "
                "mjc_ccd), x4")
LANE0, LANE0B = "host1-lane0.jsonl", "host1-lane0b.jsonl"
MN_FORKS_REGISTERED = 38
MUJOCO = "3.14.0"

H, D, NB = "holistic", "conventional", "null_b"
FAUNAS = (H, D)
SEED_BASE = 129000
N_STAGE1 = 8
SEEDS = tuple(range(1, N_STAGE1 + 1))
SEASON_MERGE = 59          # validity for the share test: both alive at 59 (S)
SEASON_INCOME = 239        # validity for the income test: both alive through 239 (S)
SEASON_END = 299           # EXCLUDED: extinct by 299 (S)
WINDOW = (240, 299)        # every point outcome (5.2)
G0_WINDOW = (180, 299)     # M-arm g0 and VARIANCE-DRIVEN (6.1, 6.2)
G0_OFFSET = 0.35
POOLED = 120
DELTA_S, DELTA_I, EARNS_MIN = 0.10, 0.15, 0.10
Q_BH = 0.10
ALPHA_HOLM = 0.05
LIVING_COST = 0.25
K2_POOLED_BAR, K2_POINT_BAR = 0.05, 0.15
CONTINGENT_MIN_DF = 12
RA_CAP, RB_CAP = 16, 20
RB_N2 = 8
RB_ALPHA = 0.05
CLAIM = "among holistic and designed stream draws (founders and their early history) that establish at W118-b"
SHARE_QUAL = "under the committed rule"

PRICES = ("010", "030", "080")
PRICE_MID = {("010", "030"): "018", ("030", "080"): "053"}
CLUTTERS = ("0", "1", "2")
CLUTTER_MID = {("0", "1"): "05", ("1", "2"): "15"}
LAYOUTS = ("U", "HP", "PW")
STAGE1_POINTS = tuple([f"c{c}-p{p}-{L}-G" for c in CLUTTERS for p in PRICES for L in LAYOUTS]
                      + [f"c1-p{p}-{L}-L" for p in PRICES for L in LAYOUTS])
ANCHORS_STAGE1 = ("c1-p030-U-L", "c1-p030-PW-G")


# -- 2.5 the quarantine -------------------------------------------------------------------------------------------- #

class QuarantineRefusal(RuntimeError):
    """Raised before anything touches the quarantined unit (RULING.md item 3)."""


def label_of(path: str, root: str = ROOT) -> str:
    """``stages._label``: ``rbt-129-<path under runs/RBT-129>``, slashes to dashes."""
    rel = os.path.relpath(_abs(path, root), os.path.join(root, "runs", "RBT-129"))
    return "rbt-129-" + rel.replace(os.sep, "-")


def _abs(path: str, root: str) -> str:
    return os.path.abspath(path if os.path.isabs(path) else os.path.join(root, path))


def _is_quarantined_label(label: str) -> bool:
    lab = label.strip().lower()
    for prefix in ("refs/heads/", "refs/remotes/origin/", "origin/", "ckpt/"):
        if lab.startswith(prefix):
            lab = lab[len(prefix):]
    q = QUARANTINED_LABEL.lower()
    return lab == q or lab.startswith(q + "-") or lab.startswith(q + "/")


def _is_quarantined_path(path: str, root: str) -> bool:
    rel = os.path.relpath(_abs(path, root), root).lower()
    q = QUARANTINED_DIR.lower()
    return rel == q or rel.startswith(q + os.sep)


def refuse_quarantined(label: str = None, path: str = None, root: str = ROOT) -> None:
    """Raise :class:`QuarantineRefusal` if ``label`` or ``path`` names the quarantined unit (its branch, its run
    directory, or anything under it).  Called first by every reader."""
    if label is not None and _is_quarantined_label(label):
        raise QuarantineRefusal(f"refused: {label} is quarantined (mn-crash/RULING.md item 3); it is never restored, "
                                "checked out or read before the RBT-129 readout is complete")
    if path is not None and (_is_quarantined_path(path, root) or _is_quarantined_label(label_of(path, root))):
        raise QuarantineRefusal(f"refused: {path} is the quarantined unit's directory (mn-crash/RULING.md item 3)")


def guarded_reader(reader):
    """Wrap a ``reader(label, member) -> str | None`` (default ``stages.branch_file``) so that the quarantine is checked
    before it is ever called."""
    def read(label: str, member: str):
        refuse_quarantined(label=label)
        refuse_quarantined(label=f"{label}/{member}")
        return reader(label, member)
    return read


def default_reader():
    import stages
    return guarded_reader(stages.branch_file)


def guarded_restore(d: str, root: str = ROOT, restore=None) -> None:
    """Restore a run directory from its branch (``stages._restore``), after the quarantine check."""
    refuse_quarantined(path=d, root=root)
    refuse_quarantined(label=label_of(d, root))
    if restore is None:
        import stages
        restore = stages._restore
    restore(d)


# -- 2.1 lanes and expected branches ------------------------------------------------------------------------------- #

def lane_paths(root: str = ROOT) -> tuple:
    """(lanes/1's lane files, lanes/1-MN's with host1-lane0b in place of host1-lane0)."""
    one = sorted(glob.glob(os.path.join(root, "runs", "RBT-129", "lanes", "1", "*.jsonl")))
    mn_dir = os.path.join(root, "runs", "RBT-129", "lanes", "1-MN")
    mn = sorted(p for p in glob.glob(os.path.join(mn_dir, "*.jsonl")) if os.path.basename(p) != LANE0)
    if os.path.join(mn_dir, LANE0B) not in mn:
        raise SystemExit(f"integrity: {LANE0B} is missing from lanes/1-MN")
    return one, mn


def load_jobs(paths: list, root: str = ROOT) -> list:
    """Every job of these lane files, once each by name.  A lane file that schedules the quarantined directory is
    refused before any job is returned (``host1-lane0.jsonl``)."""
    jobs, seen = [], set()
    for path in paths:
        if os.path.basename(path) == LANE0 and os.path.basename(os.path.dirname(path)) == "1-MN":
            raise QuarantineRefusal(f"refused: {path} schedules the quarantined unit; the readout loads {LANE0B} instead")
        rows = [json.loads(line) for line in open(path) if line.strip()]
        for j in rows:
            refuse_quarantined(path=j["dir"], root=root)
        for j in rows:
            if j["name"] not in seen:
                seen.add(j["name"])
                jobs.append(j)
    return jobs


def unit_of(job: dict) -> str:
    """``stages._unit``: a chain's unit directory, from any of its jobs."""
    return os.path.dirname(job["src"] if job["job"] in ("snapshot", "fork") else job["dir"])


def expected_labels(jobs: list, root: str = ROOT) -> dict:
    """{label: run directory or unit record}, as ``stages.expected_branches``: every job's directory, and the record of
    every ``1/`` chain's unit.  Refused if the quarantined label is among them."""
    out = {}
    for j in jobs:
        out[label_of(j["dir"], root)] = j["dir"]
        if j["name"].startswith(("P/", "1/")):
            rec = os.path.join(unit_of(j), "record")
            out[label_of(rec, root)] = rec
    for lab in out:
        refuse_quarantined(label=lab)
    return out


def missing_branches(expected: dict, have: set) -> list:
    return sorted(k for k in expected if k not in have)


def remote_labels(root: str = ROOT) -> set:
    """Branch names only (``git ls-remote``); no branch is fetched."""
    import subprocess
    r = subprocess.run(["git", "ls-remote", "--heads", "origin", "refs/heads/ckpt/rbt-129-*"], cwd=root,
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"git ls-remote failed (exit {r.returncode})")
    return {line.split("refs/heads/ckpt/", 1)[1] for line in r.stdout.splitlines() if "refs/heads/ckpt/" in line}


# -- 2.2 done-markers ---------------------------------------------------------------------------------------------- #

def marker_jobs(jobs: list) -> list:
    """(label-bearing directory, tag, job) for every job: its ``.rbt129-done-<tag>``."""
    return [(j["dir"], j["name"].split("/")[-1], j) for j in jobs]


def check_markers(jobs: list, read, root: str = ROOT) -> dict:
    """{"done": n, "extinct": n, "missing_s": [...], "missing_fork": [...], "missing_other": [...]}.  A marker's
    extinction season is never returned (plan 2.2)."""
    out = {"done": 0, "extinct": 0, "missing_s": [], "missing_fork": [], "missing_other": []}
    for d, tag, j in marker_jobs(jobs):
        text = read(label_of(d, root), f".rbt129-done-{tag}")
        if text is None:
            key = "missing_fork" if j["job"] == "fork" else "missing_s" if j["job"] in ("fresh", "adopt", "resume", "snapshot") else "missing_other"
            out[key].append(j["name"])
        elif "skipped: extinct pre-merge" in text:
            out["extinct"] += 1
        else:
            out["done"] += 1
    return out


# -- 2.4 the CRASHED unit ------------------------------------------------------------------------------------------ #

def _job_names(path: str) -> list:
    """Job names only (registered input); used for host1-lane0.jsonl, which is never loaded as a lane."""
    return [json.loads(line)["name"] for line in open(path) if line.strip()]


def read_forks_line(launch_txt: str) -> list:
    for line in open(launch_txt):
        if line.startswith("forks "):
            return line.split()[1:]
    return []


def crash_reconcile(mn_dir: str) -> list:
    """Problems with the CRASHED unit's bookkeeping (empty list = PASS): lane0 minus lane0b is exactly the crashed
    fork; lane0b is a subset of lane0; launch.txt's forks line holds 38, the crashed one among them; the loaded lanes
    hold the other 37 and not it."""
    probs = []
    a, b = _job_names(os.path.join(mn_dir, LANE0)), _job_names(os.path.join(mn_dir, LANE0B))
    if set(a) - set(b) != {CRASHED_JOB}:
        probs.append(f"{LANE0} minus {LANE0B} is {sorted(set(a) - set(b))}, not [{CRASHED_JOB}]")
    if not set(b) <= set(a):
        probs.append(f"{LANE0B} holds jobs not in {LANE0}: {sorted(set(b) - set(a))}")
    forks = read_forks_line(os.path.join(mn_dir, "launch.txt"))
    if len(forks) != MN_FORKS_REGISTERED or len(set(forks)) != len(forks):
        probs.append(f"launch.txt's forks line holds {len(forks)} ({len(set(forks))} distinct), not {MN_FORKS_REGISTERED}")
    crashed = "/".join(CRASHED_JOB.split("/")[1:])
    if crashed not in forks:
        probs.append(f"{crashed} is not on launch.txt's forks line")
    loaded = set()
    for p in sorted(glob.glob(os.path.join(mn_dir, "*.jsonl"))):
        if os.path.basename(p) != LANE0:
            loaded |= set(_job_names(p))
    want = {f"1/{f}" for f in forks} - {CRASHED_JOB}
    if CRASHED_JOB in loaded:
        probs.append(f"{CRASHED_JOB} is in a loaded lane")
    if loaded != want:
        probs.append(f"the loaded lanes hold {len(loaded)} forks; the forks line less the crashed unit is {len(want)}"
                     f" (only in lanes: {sorted(loaded - want)}; only on the line: {sorted(want - loaded)})")
    return probs


# -- 2.6 MuJoCo provenance ----------------------------------------------------------------------------------------- #

def mujoco_versions(rec) -> list:
    """[(where, version)] from a ``platform.json`` record: the top level, then each ``resumes`` entry."""
    if not isinstance(rec, dict):
        return []
    out = [("top", rec.get("mujoco"))]
    for i, r in enumerate(rec.get("resumes") or []):
        out.append((f"resumes[{i}]", r.get("mujoco") if isinstance(r, dict) else None))
    return out


def check_platform(text) -> tuple:
    """(verdict, problems) for one ``platform.json`` text: PASS iff it parses and every MuJoCo version on it, top level
    and every resume, is 3.14.0 (RULING.md items 6, 7)."""
    if text is None:
        return "FAIL", ["no platform.json"]
    try:
        rec = json.loads(text)
    except ValueError:
        return "FAIL", ["platform.json does not parse"]
    vers = mujoco_versions(rec)
    if not vers:
        return "FAIL", ["platform.json is not a record"]
    bad = [f"{w}: {v!r}" for w, v in vers if v != MUJOCO]
    return ("PASS" if not bad else "FAIL"), bad


RUN_JOBS = ("fresh", "adopt", "resume", "snapshot", "fork")


def platform_dirs(jobs: list) -> list:
    """The directories that ran the ecology (S, ckpt60, M, N), once each; ksalt directories and records run nothing."""
    out = []
    for j in jobs:
        if j["job"] in RUN_JOBS and j["dir"] not in out:
            out.append(j["dir"])
    return out


def check_platforms(jobs: list, read, root: str = ROOT) -> dict:
    res = {"pass": 0, "fail": {}}
    for d in platform_dirs(jobs):
        verdict, probs = check_platform(read(label_of(d, root), "platform.json"))
        if verdict == "PASS":
            res["pass"] += 1
        else:
            res["fail"][d] = probs
    return res


# -- 2.7 K-SALT ---------------------------------------------------------------------------------------------------- #

def ksalt_word(text) -> str:
    if text is None:
        return "MISSING"
    first = text.splitlines()[0] if text.strip() else ""
    return "PASS" if first.startswith("KSALT PASS") else "VOID" if first.startswith("KSALT VOID") else "UNREADABLE"


def check_ksalt(jobs: list, read, root: str = ROOT) -> dict:
    """{job name: (record verdict, ksalt-dir verdict, marker note)}; the verdict that counts is the unit record's
    ``KSALT.txt`` (what ``s60_state`` and the M/N gate read)."""
    out = {}
    for j in jobs:
        if j["job"] != "ksalt":
            continue
        rec = read(label_of(os.path.join(unit_of(j), "record"), root), "KSALT.txt")
        own = read(label_of(j["dir"], root), "KSALT.txt")
        mark = read(label_of(j["dir"], root), f".rbt129-done-{j['name'].split('/')[-1]}")
        note = "VOID" if mark and "KSALT VOID" in mark else ("present" if mark else "missing")
        out[j["name"]] = (ksalt_word(rec), ksalt_word(own), note)
    return out


# -- 2.7 the gate's input, re-checked ------------------------------------------------------------------------------ #

def parse_gate_table(path: str) -> dict:
    """{point: (valid k or None, M seeds count, N seeds count)} from ``gate_table.txt``."""
    out = {}
    for line in open(path):
        m = re.match(r"\s+\d+\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\s+(\d+)\s+(\d+)\s", line)
        if m:
            v = m.group(2)
            out[m.group(1)] = (int(v.split("/")[0]) if "/" in v else None, int(m.group(3)), int(m.group(4)))
    return out


def gate_mismatches(table: dict, valid: dict) -> list:
    """``valid[point] = {j: bool}`` at the M-eligible points against the table's valid column."""
    probs = []
    for pid, (k, _, _) in table.items():
        if k is None:
            continue
        got = sum(1 for v in valid.get(pid, {}).values() if v)
        if pid not in valid or got != k:
            probs.append(f"{pid}: gate table valid {k}, recomputed {got if pid in valid else 'not read'}")
    return probs


# -- 2.3 the resume audit, for the forks ---------------------------------------------------------------------------- #

def fork_double_writes(jobs: list, written_twice, root: str = ROOT) -> dict:
    """{fork name: resumed.written_twice record} for every fork that shows a double write (repeated rows, steps back
    or torn lines).  ``resumed.py`` lists no ``fork`` job, so the 37 forks are checked here; each label passes the
    quarantine guard before ``written_twice`` (which fetches the branch) is called."""
    bad = {}
    for j in jobs:
        if j["job"] != "fork":
            continue
        lab = label_of(j["dir"], root)
        refuse_quarantined(label=lab)
        refuse_quarantined(path=j["dir"], root=root)
        rec = written_twice(lab)
        if any(v["repeated"] or v["steps_back"] or v["torn"] for v in rec.values()):
            bad[j["name"]] = rec
    return bad


def gate_valid_from_ckpt60(root: str, table: dict, restore=None) -> dict:
    """{point: {j: valid at the merge}} at the M-eligible points (the gate table's rows with a valid count), from each
    unit's restored ckpt60 history (``stages.valid_at_merge``'s rule; the gate's registered input, #500 item 7)."""
    out = {}
    for pid, (k, _, _) in table.items():
        if k is None:
            continue
        out[pid] = {}
        for j in SEEDS:
            ck = os.path.join(unit_dir(root, pid, j), "ckpt60")
            guarded_restore(ck, root, restore)
            hist = read_run(ck, root)["history"] if os.path.exists(os.path.join(ck, "history.json")) else []
            out[pid][j] = valid_share(hist)
    return out


# -- integrity driver ---------------------------------------------------------------------------------------------- #

def integrity(root: str, read, have: set, provenance: dict = None, written_twice=None, gate_valid: dict = None) -> tuple:
    """(ok, lines): plan section 2, in order.  ``read`` is a guarded reader; ``have`` the ``ls-remote`` labels;
    ``provenance`` the parallel session's per-directory verdicts (``stage1-provenance/``), if delivered;
    ``written_twice`` is ``resumed.written_twice`` (the forks' double-write check, 2.3); ``gate_valid`` the
    valid-at-merge table from the restored ckpt60s (2.7).  A check given None is printed as not run, and fails."""
    lines, ok = [], True
    one, mn = lane_paths(root)
    jobs = load_jobs(one, root) + load_jobs(mn, root)
    exp = expected_labels(jobs, root)
    miss = missing_branches(exp, have)
    lines.append(f"2.1 branches: {len(exp) - len(miss)} of {len(exp)} expected labels have a branch")
    lines += [f"  MISSING ckpt/{m}" for m in miss]
    ok &= not miss
    lines.append(f"2.1 the quarantined branch ckpt/{QUARANTINED_LABEL}: {'listed' if QUARANTINED_LABEL in have else 'not listed'}"
                 " by ls-remote (name only; never read)")
    mk = check_markers(jobs, read, root)
    lines.append(f"2.2 done-markers: {mk['done']} done, {mk['extinct']} done (extinct pre-merge), "
                 f"missing S-arm {len(mk['missing_s'])}, missing M/N {len(mk['missing_fork'])}, missing other {len(mk['missing_other'])}")
    for k, why in (("missing_s", "S-arm: the hive stops (ruling item 5): HELP"), ("missing_fork", "a candidate second crash (ruling item 5): HELP"),
                   ("missing_other", "HELP")):
        lines += [f"  MISSING {n}: {why}" for n in mk[k]]
        ok &= not mk[k]
    probs = crash_reconcile(os.path.join(root, "runs", "RBT-129", "lanes", "1-MN"))
    lines.append(f"2.4 {CRASHED_LINE}")
    lines.append(f"2.4 crash bookkeeping: {'PASS' if not probs else 'FAIL'}")
    lines += [f"  {p}" for p in probs]
    ok &= not probs
    if written_twice is None:
        lines.append("2.3 forks' double-write check: NOT RUN")
        ok = False
    else:
        dw = fork_double_writes(jobs, written_twice, root)
        n_forks = sum(1 for j in jobs if j["job"] == "fork")
        lines.append(f"2.3 forks' double-write check: {n_forks - len(dw)} of {n_forks} clean (resumed.py --check-runs covers"
                     " the S chains and the census sources: resumed-readout.txt)")
        lines += [f"  WRITTEN TWICE {n}: HELP" for n in sorted(dw)]
        ok &= not dw
    pl = check_platforms(jobs, read, root)
    lines.append(f"2.6 MuJoCo {MUJOCO}: {pl['pass']} of {pl['pass'] + len(pl['fail'])} run directories PASS (top level and every resume)")
    for d, p in sorted(pl["fail"].items()):
        lines.append(f"  FAIL {os.path.relpath(_abs(d, root), root)}: {'; '.join(p)}")
    ok &= not pl["fail"]
    if provenance is not None:
        ours = {os.path.relpath(_abs(d, root), root): ("FAIL" if d in pl["fail"] else "PASS") for d in platform_dirs(jobs)}
        diff = sorted(k for k in set(ours) | set(provenance) if ours.get(k) != provenance.get(k))
        lines.append(f"2.6 against stage1-provenance/: {'agrees' if not diff else f'{len(diff)} disagree: HELP'}")
        lines += [f"  {k}: readout {ours.get(k)}, stage1-provenance {provenance.get(k)}" for k in diff]
        ok &= not diff
    else:
        lines.append("2.6 stage1-provenance/: not delivered; the readout's own count stands alone until it is (HELP if it later disagrees)")
    ks = check_ksalt(jobs, read, root)
    void = sorted(n for n, (r, _, _) in ks.items() if r != "PASS")
    lines.append(f"2.7 K-SALT: {len(ks) - len(void)} of {len(ks)} PASS (unit record's KSALT.txt)")
    for n, (r, own, note) in sorted(ks.items()):
        if r != "PASS" or own != r or note != "present":
            lines.append(f"  {n}: record {r}, ksalt dir {own}, marker {note}"
                         + ("  (F7: the stream claim re-opens: HELP)" if r != "PASS" else ""))
    ok &= not void
    table = parse_gate_table(os.path.join(root, "runs", "RBT-129", "lanes", "1-MN", "gate_table.txt"))
    if gate_valid is None:
        lines.append("2.7 the gate's valid-at-merge counts: NOT RUN")
        ok = False
    else:
        gm = gate_mismatches(table, gate_valid)
        lines.append(f"2.7 the gate's valid-at-merge counts against gate_table.txt: {'PASS' if not gm else 'FAIL: HELP'}"
                     " (seen at emission; mn-emitter ruling item 7)")
        lines += [f"  {x}" for x in gm]
        ok &= not gm
    lines.append("2.7 K1: pilot PASS at c1-p030-U-L, c0-p030-U-L; UNTESTABLE at c1-p030-PW-G, c2-p030-PW-G; never tested on PW"
                 " terrain; no Stage-1 point is VOID by K1")
    return ok, lines, {"jobs": jobs, "ksalt": ks}


# -- 3 per-seed statistics (pure) ---------------------------------------------------------------------------------- #

def alive(history: list, kind: str, season: int) -> int:
    """``alive`` of ``kind`` at ``season``; a missing entry reads 0 (an empty cohort writes no row; plan 3.1)."""
    for e in history:
        if e["season"] == season and e["population"] == kind:
            return int(e["alive"])
    return 0


def valid_share(history: list) -> bool:
    return all(alive(history, k, SEASON_MERGE) > 0 for k in FAUNAS)


def valid_income(history: list) -> bool:
    return all(alive(history, k, SEASON_INCOME) > 0 for k in FAUNAS)


def extinct_by_end(history: list, kind: str) -> bool:
    return alive(history, kind, SEASON_END) == 0


def season_net(row: dict, price: float, variant: str = "net") -> float:
    if variant == "last_score":
        return float(row.get("last_score", 0.0))
    return float(row.get("food", 0.0)) - price * float(row.get("work", 0.0)) / 1000.0


def member_seasons(rows, kind: str, lo: int, hi: int, variant: str = "registered"):
    """The rows of plan 3.2: generation in [lo, hi], ``kind``, death absent or starved/aged, and a ``food`` field.
    Variants: ``survivors`` (death absent only), ``p0`` (the P+0 readout's: newborn rows kept, read as 0)."""
    for r in rows:
        if r.get("population") != kind or not lo <= r.get("generation", -1) <= hi:
            continue
        death = r.get("death")
        if death in ("cull", "merge-null"):
            continue
        if variant == "survivors" and death is not None:
            continue
        if variant != "p0" and "food" not in r:
            continue
        yield r


def flow(rows, kind: str, price: float, lo: int = WINDOW[0], hi: int = WINDOW[1], variant: str = "registered",
         net: str = "net"):
    """Mean season net over the fauna's member-seasons in [lo, hi] (member-season weighted), or None."""
    vals = [season_net(r, price, net) for r in member_seasons(rows, kind, lo, hi, variant)]
    return (sum(vals) / len(vals)) if vals else None


def share_window(history: list, kind: str, lo: int = WINDOW[0], hi: int = WINDOW[1]) -> list:
    """alive(kind, s) / 120 for s in [lo, hi]; the empty-world convention (plan 3.3): a missing entry is 0 of 120."""
    return [alive(history, kind, s) / POOLED for s in range(lo, hi + 1)]


def merge_share(s_history: list, kind: str = H, other: str = None) -> float:
    """n_kind / (n_kind + n_other) from S's season-59 counts; None if both are 0."""
    other = other or (D if kind == H else H)
    a, b = alive(s_history, kind, SEASON_MERGE), alive(s_history, other, SEASON_MERGE)
    return None if a + b == 0 else a / (a + b)


def yprime_m(m_history: list, s_history: list):
    s0 = merge_share(s_history, H)
    if s0 is None:
        return None
    w = share_window(m_history, H)
    return sum(w) / len(w) - s0


def yprime_n(n_history: list, s_history: list, k: str):
    """The null's y′: the merge-null kind K's share of 120 over the window, less n_K / (n_K + n_other) at 59."""
    s0 = merge_share(s_history, k)
    if s0 is None:
        return None
    w = share_window(n_history, k)
    return sum(w) / len(w) - s0


def living_share_window(history: list, kind: str = H, other: str = None):
    """The descriptive variant: alive(kind) / (alive(kind) + alive(other)), None if the world is empty in any window
    season (the seed is then listed)."""
    other = other or (D if kind == H else H)
    out = []
    for s in range(WINDOW[0], WINDOW[1] + 1):
        a, b = alive(history, kind, s), alive(history, other, s)
        if a + b == 0:
            return None
        out.append(a / (a + b))
    return sum(out) / len(out)


def missingness_bound(y_completed: list, s0: float, n: int = N_STAGE1) -> tuple:
    """Ruling item 4: the logical bounds of the n-seed mean y′ with the missing seed anywhere in [−s0, 1 − s0]
    (valid under plan 3.3's convention, which keeps every share in [0, 1])."""
    if not 0.0 <= s0 <= 1.0:
        raise ValueError("s0 outside [0, 1]: the bound is not printed (ruling item 4)")
    if len(y_completed) != n - 1:
        raise ValueError(f"the bound takes the {n - 1} completed seeds")
    t = sum(y_completed)
    return (t - s0) / n, (t + 1.0 - s0) / n


def m_row_label(point: str, m_seeds: list, crashed: dict) -> str:
    """'M k of n' with the CRASHED count (ruling item 1)."""
    c = len(crashed.get(point, []))
    return f"M {len(m_seeds) - c} of {len(m_seeds)}" + (f" ({c} CRASHED)" if c else "")


# -- statistics: distributions without scipy ----------------------------------------------------------------------- #

def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(c) > 1e-300 else 1e300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(c) > 1e-300 else 1e300
        de = d * c
        h *= de
        if abs(de - 1.0) < 3e-15:
            break
    return h


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_sf(t, df):
    """P(T > t), Student t with df degrees of freedom."""
    if math.isinf(t):
        return 0.0 if t > 0 else 1.0
    x = df / (df + t * t)
    tail = 0.5 * betainc(df / 2.0, 0.5, x)
    return tail if t > 0 else 1.0 - tail


def t_ppf(p, df):
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1 - t_sf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def f_sf(f, d1, d2):
    if f <= 0:
        return 1.0
    return betainc(d2 / 2.0, d1 / 2.0, d2 / (d2 + d1 * f))


def norm_cdf(z):
    return 0.5 * math.erfc(-z / math.sqrt(2))


def norm_ppf(p):
    if not 0 < p < 1:
        return math.copysign(math.inf, p - 0.5)
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def chi2_sf(x, k):
    """P(χ²_k > x): the regularized upper incomplete gamma Q(k/2, x/2)."""
    a, z = k / 2.0, x / 2.0
    if z <= 0:
        return 1.0
    if z < a + 1:
        term = s = 1.0 / a
        n = a
        for _ in range(1000):
            n += 1
            term *= z / n
            s += term
            if abs(term) < abs(s) * 1e-15:
                break
        return 1.0 - s * math.exp(-z + a * math.log(z) - math.lgamma(a))
    b, c, d = z + 1 - a, 1e300, 1.0 / (z + 1 - a)
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = b + an / c
        c = c if abs(c) > 1e-300 else 1e-300
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return math.exp(-z + a * math.log(z) - math.lgamma(a)) * h


# -- tests per point ----------------------------------------------------------------------------------------------- #

def mean_sd(xs: list) -> tuple:
    n = len(xs)
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n >= 2 else None
    return m, sd


def one_sample_t(xs: list, mu: float = 0.0) -> dict:
    """Two-sided one-sample t: {n, mean, sd, t, p}; t and p are None at n < 2; an SD of 0 gives t = ±inf (p 0) or nan
    (mean equal to mu; p 1)."""
    n = len(xs)
    if n == 0:
        return {"n": 0, "mean": None, "sd": None, "t": None, "p": None}
    m, sd = mean_sd(xs)
    if n < 2:
        return {"n": n, "mean": m, "sd": None, "t": None, "p": None}
    if sd == 0:
        t = math.copysign(math.inf, m - mu) if m != mu else math.nan
        return {"n": n, "mean": m, "sd": 0.0, "t": t, "p": 1.0 if math.isnan(t) else 0.0}
    t = (m - mu) / (sd / math.sqrt(n))
    return {"n": n, "mean": m, "sd": sd, "t": t, "p": min(1.0, 2 * t_sf(abs(t), n - 1))}


def tost_p(xs: list, margin: float):
    """TOST at ±margin: max of the one-sided p-values of H0: mu <= -margin and H0: mu >= +margin; None at n < 2."""
    if len(xs) < 2:
        return None
    m, sd = mean_sd(xs)
    n = len(xs)
    if sd == 0:
        return 0.0 if -margin < m < margin else 1.0
    se = sd / math.sqrt(n)
    p_lo = t_sf((m + margin) / se, n - 1)
    p_hi = 1 - t_sf((m - margin) / se, n - 1)
    return max(p_lo, p_hi)


def bh(pvals: dict, q: float = Q_BH) -> set:
    """Benjamini–Hochberg step-up over the keys with a p-value (None = not tested, not in K)."""
    items = sorted(((p, k) for k, p in pvals.items() if p is not None), key=lambda x: (x[0], str(x[1])))
    K = len(items)
    cut = 0
    for i, (p, _) in enumerate(items, 1):
        if p <= i * q / K:
            cut = i
    return {k for _, k in items[:cut]}


def by(pvals: dict, q: float = Q_BH) -> set:
    K = sum(1 for p in pvals.values() if p is not None)
    return bh(pvals, q / sum(1.0 / i for i in range(1, K + 1))) if K else set()


def holm(pvals: dict, alpha: float = ALPHA_HOLM) -> set:
    items = sorted(((p, k) for k, p in pvals.items()), key=lambda x: (x[0], str(x[1])))
    m, out = len(items), set()
    for i, (p, k) in enumerate(items):
        if p <= alpha / (m - i):
            out.add(k)
        else:
            break
    return out


def holm_provisional(t1_t3: dict, alpha: float = ALPHA_HOLM) -> set:
    """Holm over T1–T4 with T4 not measured, entered at p = 1 (plan 6): a lower bound on the final rejections."""
    return holm({**t1_t3, "T4": 1.0}, alpha) - {"T4"}


# -- 4 calls (pure) ------------------------------------------------------------------------------------------------ #

def thresholds(n: int) -> tuple:
    """(EXCLUDED at >= ceil(5n/8), PARTIAL at < ceil(3n/4)) (F's T6)."""
    return math.ceil(5 * n / 8), math.ceil(3 * n / 4)


def partial_label(seeds: dict) -> str:
    """``seeds[j] = (H alive at 59, D alive at 59)`` for the point's invalid seeds: the named survivor (plan 4.2, O-8)."""
    a_h = sum(1 for h, d in seeds.values() if h and not d)
    a_d = sum(1 for h, d in seeds.values() if d and not h)
    return "PARTIAL-H" if a_h > a_d else "PARTIAL-D" if a_d > a_h else "PARTIAL-TIED"


def body_call(p: dict) -> str:
    """The registered order (plan 4.2).  ``p`` holds: n (non-VOID seeds), extinct {H: k, D: k}, valid_share k,
    merge {j: (h alive, d alive)} over the non-VOID seeds, void (K1/K2), n_ran (N at the point), share {mean, rejected}
    (WIN family), contingent (bool), tie (TOST rejected), resolving, anchor."""
    n = p["n"]
    ex, part = thresholds(n)
    xh, xd = p["extinct"][H] >= ex, p["extinct"][D] >= ex
    if xh and xd:
        return "NEITHER"
    if xh:
        return "EXCLUDED-H"
    if xd:
        return "EXCLUDED-D"
    if p["valid_share"] < part:
        return partial_label({j: v for j, v in p["merge"].items() if not (v[0] and v[1])})
    if p.get("void"):
        return "VOID"
    if not p.get("n_ran"):
        return "RBT-118 (not available)" if p.get("anchor") else "NOT RUN"
    s = p.get("share") or {}
    if s.get("rejected") and s["mean"] > 0 and s["mean"] >= DELTA_S:
        return "H-WIN"
    if s.get("rejected") and s["mean"] < 0 and -s["mean"] >= DELTA_S:
        return "D-WIN"
    if p.get("contingent"):
        return "CONTINGENT"
    if p.get("tie") and p.get("resolving"):
        return "TIE"
    if not p.get("resolving"):
        return "SATURATED"
    return "UNDECIDED"


def income_call(mean, rejected_earns: bool, rejected_tie: bool) -> str:
    if mean is None:
        return "NOT TESTED"
    if rejected_earns and abs(mean) >= EARNS_MIN and mean != 0:
        return "EARNS-H" if mean > 0 else "EARNS-D"
    if rejected_tie:
        return "EARNS-TIE"
    return "UNDECIDED"


def per_birth_income(net_per_birth, living_cost: float = LIVING_COST):
    """Plan 3.5 (O-5): DESIGN's per-birth income is net of work, not of the living cost: regime's net_per_birth + cost."""
    return None if net_per_birth is None else net_per_birth + living_cost


def marginal(per_birth: dict, bar: float = LIVING_COST):
    """MARGINAL when either fauna's per-birth income is below the living cost; None if either is not measured."""
    if any(v is None for v in per_birth.values()):
        return None
    return any(v < bar for v in per_birth.values())


def contingent_callable(df_null: int) -> bool:
    return df_null >= CONTINGENT_MIN_DF


def pooled_null(runs: dict) -> tuple:
    """(σ̂², df) from ``runs[(point, kind)] = [y′, ...]``, each (point, kind) mean removed (O-9)."""
    ss, df = 0.0, 0
    for ys in runs.values():
        if len(ys) >= 2:
            m = sum(ys) / len(ys)
            ss += sum((y - m) ** 2 for y in ys)
            df += len(ys) - 1
    return (ss / df if df else None), df


def contingent_p(ys: list, var_null: float, df_null: int):
    if len(ys) < 2 or not var_null or df_null < 1:
        return None
    _, sd = mean_sd(ys)
    return f_sf(sd * sd / var_null, len(ys) - 1, df_null)


def k2_pooled(ys: list) -> tuple:
    """(PASS?, mean, t, p) over the stage's N runs (O-12): |mean| < 0.05 and the t test not rejected at 0.05."""
    r = one_sample_t(ys)
    if r["p"] is None:
        return False, r["mean"], r["t"], r["p"]
    return (abs(r["mean"]) < K2_POOLED_BAR and r["p"] > 0.05), r["mean"], r["t"], r["p"]


def k2_per_point(null: dict) -> dict:
    """{point: 'PASS' | 'FAIL' | 'UNTESTABLE (n = 1)'}; BH over the points with >= 2 runs, and the size bar."""
    ps = {pt: one_sample_t(ys)["p"] for pt, ys in null.items()}
    rej = bh(ps)
    out = {}
    for pt, ys in null.items():
        if ps[pt] is None:
            out[pt] = f"UNTESTABLE (n = {len(ys)})"
        else:
            out[pt] = "PASS" if pt not in rej and abs(sum(ys) / len(ys)) <= K2_POINT_BAR else "FAIL"
    return out


def g0_bounds(g0s: list):
    """The 90% bounds of g0 over seeds (plan 3.4), None at n < 2."""
    if len(g0s) < 2:
        return None
    m, sd = mean_sd(g0s)
    h = t_ppf(0.95, len(g0s) - 1) * sd / math.sqrt(len(g0s))
    return m - h, m + h


def resolving(m_ran: bool, n_ran: bool, g0s: list, n: int, resolvable=None) -> bool:
    """Ruling item 4(b): only where M and N both ran; both 90% bounds must pass ``power.resolvable``."""
    if not (m_ran and n_ran):
        return False
    b = g0_bounds(g0s)
    if b is None:
        return False
    if resolvable is None:
        sys.path.insert(0, RUNS)
        import power  # noqa: E402
        resolvable = power.resolvable
    return bool(resolvable(b[0], b[1], "lottery", n, reps=1500))


def variance_driven(y: list, dmean: list, dsd: list, win_sign: int):
    """Plan 4.4: OLS of y′ on standardised mean-income and income-SD differences (H − D).  True when the SD term's
    partial t, in the WIN's direction (the loser's SD larger), exceeds the mean term's and the mean term's is < 2;
    None when the fit has < 1 residual df or a predictor is constant."""
    import numpy as np
    n = len(y)
    if n - 3 < 1:
        return None
    def z(v):
        a = np.asarray(v, float)
        s = a.std(ddof=1)
        return None if s == 0 else (a - a.mean()) / s
    zm, zs = z(dmean), z(dsd)
    if zm is None or zs is None:
        return None
    X = np.column_stack([np.ones(n), zm, zs])
    yv = np.asarray(y, float)
    XtX = X.T @ X
    if abs(np.linalg.det(XtX)) < 1e-12:
        return None
    beta = np.linalg.solve(XtX, X.T @ yv)
    res = yv - X @ beta
    s2 = float(res @ res) / (n - 3)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(XtX)))
    t_mean, t_sd = beta[1] / se[1], beta[2] / se[2]
    # the WIN's direction for the SD term: H-WIN with D's SD larger means y′ falls as (sd_H − sd_D) rises
    t_sd_dir = -t_sd * win_sign
    t_mean_dir = t_mean * win_sign
    return bool(t_sd_dir > t_mean_dir and t_mean_dir < 2)


# -- 6 map-level --------------------------------------------------------------------------------------------------- #

def parse_point(pid: str) -> tuple:
    c, p, L, s = pid.split("-")
    cv = {"0": 0.0, "05": 0.5, "1": 1.0, "15": 1.5, "2": 2.0}[c[1:]]
    pv = int(p[1:]) / 1000.0
    return cv, pv, L, s


def design_row(pid: str) -> list:
    """Intercept, c − 1, log(p / 0.03), HP, PW, G, (c − 1) × log(p / 0.03) (O-21: centred at the committed world)."""
    c, p, L, s = parse_point(pid)
    cc, lp = c - 1.0, math.log(p / 0.03)
    return [1.0, cc, lp, float(L == "HP"), float(L == "PW"), float(s == "G"), cc * lp]


WORLD_TERMS = (1, 2, 3, 4, 5, 6)


def lmm_reml(y: list, X: list, groups: list) -> dict:
    """Random-intercept REML (profiling λ = σ²_u / σ²), GLS β and its covariance.  Plan section 6 (M2)."""
    import numpy as np
    y, X = np.asarray(y, float), np.asarray(X, float)
    g = np.asarray(groups)
    N, P = X.shape
    keys = sorted(set(groups))
    idx = [np.where(g == k)[0] for k in keys]

    def parts(lam):
        XtHX, XtHy, yHy, logdet = np.zeros((P, P)), np.zeros(P), 0.0, 0.0
        for ii in idx:
            Xi, yi, n = X[ii], y[ii], len(ii)
            w = lam / (1.0 + lam * n)
            sx, sy = Xi.sum(0), yi.sum()
            XtHX += Xi.T @ Xi - w * np.outer(sx, sx)
            XtHy += Xi.T @ yi - w * sx * sy
            yHy += yi @ yi - w * sy * sy
            logdet += math.log(1.0 + lam * n)
        beta = np.linalg.solve(XtHX, XtHy)
        rss = yHy - XtHy @ beta
        return beta, XtHX, rss, logdet

    def nll(lam):
        _, XtHX, rss, logdet = parts(lam)
        s2 = rss / (N - P)
        return 0.5 * ((N - P) * math.log(max(s2, 1e-300)) + logdet + np.linalg.slogdet(XtHX)[1])

    grid = [0.0] + [10 ** e for e in np.linspace(-4, 3, 57)]
    best = min(grid, key=nll)
    i = grid.index(best)
    lo, hi = grid[max(0, i - 1)], grid[min(len(grid) - 1, i + 1)]
    for _ in range(80):
        a, b = lo + 0.382 * (hi - lo), lo + 0.618 * (hi - lo)
        if nll(a) < nll(b):
            hi = b
        else:
            lo = a
    lam = (lo + hi) / 2 if nll((lo + hi) / 2) < nll(best) else best
    beta, XtHX, rss, _ = parts(lam)
    s2 = rss / (N - P)
    return {"beta": beta, "cov": s2 * np.linalg.inv(XtHX), "sigma2": s2, "lambda": lam, "n": N, "groups": len(keys)}


def wald(fit: dict, terms=WORLD_TERMS) -> tuple:
    """(χ², df, p) for the coefficients ``terms`` jointly zero (T1)."""
    import numpy as np
    b = fit["beta"][list(terms)]
    V = fit["cov"][np.ix_(list(terms), list(terms))]
    x2 = float(b @ np.linalg.solve(V, b))
    return x2, len(terms), chi2_sf(x2, len(terms))


def wald_one(fit: dict, term: int) -> tuple:
    """(z, p) for one coefficient (T2: c, term 1; T3: log p, term 2)."""
    b, se = float(fit["beta"][term]), math.sqrt(float(fit["cov"][term, term]))
    z = b / se
    return z, 2 * (1 - norm_cdf(abs(z)))


def fieller(xs: list, ys: list, level: float = 0.95) -> dict:
    """M3: OLS y = a + b x over seed-level points, p* = −a/b, and Fieller's interval for it (O-14)."""
    n = len(xs)
    if n < 3 or len(set(xs)) < 2:
        return {"p_star": None, "kind": "not estimable"}
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    s2 = sum((y - a - b * x) ** 2 for x, y in zip(xs, ys)) / (n - 2)
    va, vb, cab = s2 * (1 / n + mx * mx / sxx), s2 / sxx, -mx * s2 / sxx
    t = t_ppf(1 - (1 - level) / 2, n - 2)
    A, B, C = b * b - t * t * vb, 2 * (a * b - t * t * cab), a * a - t * t * va
    p_star = -a / b if b != 0 else None
    disc = B * B - 4 * A * C
    if A > 0 and disc >= 0:
        lo, hi = sorted(((-B - math.sqrt(disc)) / (2 * A), (-B + math.sqrt(disc)) / (2 * A)))
        return {"p_star": p_star, "kind": "bounded", "lo": lo, "hi": hi}
    return {"p_star": p_star, "kind": "unbounded" if disc >= 0 else "whole line"}


def m3_corroborates(fit: dict, lo: float = 0.01, hi: float = 0.08) -> bool:
    return fit.get("kind") == "bounded" and lo <= fit["lo"] and fit["hi"] <= hi


def cohen_kappa(a: list, b: list):
    n = len(a)
    if n == 0:
        return None
    cats = sorted(set(a) | set(b))
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return None if pe == 1 else (po - pe) / (1 - pe)


def cross_correlation(per_point: dict, min_common: int = 3) -> tuple:
    """(mean r, max r, pairs) over point pairs with >= 3 common valid seeds; ``per_point[pt] = {j: value}``."""
    pts, rs = sorted(per_point), []
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            js = sorted(set(per_point[a]) & set(per_point[b]))
            if len(js) < min_common:
                continue
            xa, xb = [per_point[a][j] for j in js], [per_point[b][j] for j in js]
            ma, mb = sum(xa) / len(xa), sum(xb) / len(xb)
            va, vb = sum((x - ma) ** 2 for x in xa), sum((x - mb) ** 2 for x in xb)
            if va > 0 and vb > 0:
                rs.append(sum((x - ma) * (y - mb) for x, y in zip(xa, xb)) / math.sqrt(va * vb))
    return ((sum(rs) / len(rs)) if rs else None), (max(rs) if rs else None), len(rs)


def sign_changes(values: list) -> int:
    s = [math.copysign(1, v) for v in values if v is not None and v != 0]
    return sum(1 for a, b in zip(s, s[1:]) if a != b)


# -- 7 refinement (mechanical) ------------------------------------------------------------------------------------- #

def ra_pairs(points=STAGE1_POINTS) -> list:
    """The 42 adjacent pairs and their midpoints: (a, b, midpoint id, axis)."""
    have, out = set(points), []
    for pid in points:
        c, p, L, s = pid.split("-")
        for (p1, p2), pm in PRICE_MID.items():
            if p == f"p{p1}" and f"{c}-p{p2}-{L}-{s}" in have:
                out.append((pid, f"{c}-p{p2}-{L}-{s}", f"{c}-p{pm}-{L}-{s}", "price"))
        for (c1, c2), cm in CLUTTER_MID.items():
            if c == f"c{c1}" and f"c{c2}-{p}-{L}-{s}" in have:
                out.append((pid, f"c{c2}-{p}-{L}-{s}", f"c{cm}-{p}-{L}-{s}", "clutter"))
    return out


SHARE_DECIDED = ("H-WIN", "D-WIN", "TIE")
INCOME_DECIDED = ("EARNS-H", "EARNS-D", "EARNS-TIE")


def _winner_absent(win: str, other_body: str) -> bool:
    """A WIN or EARNS for X beside a point where X is absent: EXCLUDED-X, NEITHER or PARTIAL-(other) (O-15)."""
    x = "H" if win in ("H-WIN", "EARNS-H") else "D" if win in ("D-WIN", "EARNS-D") else None
    if x is None:
        return False
    y = "D" if x == "H" else "H"
    return other_body in (f"EXCLUDED-{x}", "NEITHER", f"PARTIAL-{y}")


def ra_select(stats: dict, c1_candidates: list = (), cap: int = RA_CAP) -> tuple:
    """R-A (plan 7.1).  ``stats[pid]`` holds resolving, body, income {mean, t, call}, share {mean, t, call}.  Returns
    (selected midpoints, every pair's record)."""
    rows = []
    for a, b, mid, axis in ra_pairs():
        sa, sb = stats[a], stats[b]
        layer = "share" if sa.get("resolving") and sb.get("resolving") else "income"
        la, lb = sa.get(layer) or {}, sb.get(layer) or {}
        ma, mb = la.get("mean"), lb.get("mean")
        ok_a, ok_b = la.get("t") is not None, lb.get("t") is not None
        sign = ok_a and ok_b and ma is not None and mb is not None and ma * mb < 0
        decided = SHARE_DECIDED if layer == "share" else INCOME_DECIDED
        ca, cb = la.get("call"), lb.get("call")
        calls = (ca in decided and cb in decided and ca != cb) or _winner_absent(ca, sb["body"]) or _winner_absent(cb, sa["body"])
        if ok_a and ok_b:
            ta, tb = la["t"], lb["t"]
            dt = abs(ta - tb) if not (math.isnan(ta) or math.isnan(tb)) else None
            if dt is not None and math.isnan(dt):
                dt = None
        else:
            dt = None
        rows.append({"a": a, "b": b, "mid": mid, "axis": axis, "layer": layer, "sign": sign, "calls": calls,
                     "dt": dt, "smell": a.split("-")[3], "fires": sign or calls, "source": "R-A"})
    chosen = {r["mid"] for r in rows if r["fires"]}
    for mid in c1_candidates:
        if mid not in chosen:
            flank = next((r for r in rows if r["mid"] == mid), None)
            rows.append({**(flank or {"a": None, "b": None, "axis": None, "layer": "income", "sign": False, "calls": False,
                                      "dt": None, "smell": mid.split("-")[3]}), "mid": mid, "fires": True, "source": "C1",
                         "dt": flank["dt"] if flank else None, "no_stage1_pair": flank is None})
            chosen.add(mid)
    fired = [r for r in rows if r["fires"]]
    order = {mid: i for i, mid in enumerate(c1_candidates)}

    def key(r):
        """G block first (O-16); within it |Δt| descending (inf first), undefined |Δt| last; C1 candidates with no
        Stage-1 pair after every ranked pair, in the committed readout's order; ties by midpoint id."""
        dt = r["dt"]
        return (0 if r["smell"] == "G" else 1, r.get("no_stage1_pair", False), dt is None,
                -(dt if dt is not None else 0.0), order.get(r["mid"], 0) if r.get("no_stage1_pair") else 0, r["mid"])
    fired.sort(key=key)
    seen, out = set(), []
    for r in fired:
        if r["mid"] not in seen:
            seen.add(r["mid"])
            out.append(r["mid"])
    return out[:cap], rows


def c1_candidates(readout_txt: str) -> list:
    """Plan 7.1 (O-17): every sign change on a C1-listed row of the committed census readout names the refinement point
    between its two census levels."""
    out, on = [], False
    for line in open(readout_txt):
        if line.startswith("C1 monotonicity"):
            on = True
            continue
        if on and not line.startswith("  "):
            break
        if not on:
            continue
        axis = "price" if line.lstrip().startswith("price row") else "clutter"
        cells = re.findall(r"(c\d+-p\d+-\w+-[GL]) (\S+)", line)
        vals = [(pid, None if v == "--" else float(v)) for pid, v in cells]
        defined = [(pid, v) for pid, v in vals if v is not None and v != 0]
        for (p1, v1), (p2, v2) in zip(defined, defined[1:]):
            if (v1 > 0) != (v2 > 0):
                for pid in (p1, p2):  # the point at a refinement level of the row's own axis
                    c, p, _, _ = pid.split("-")
                    if (p[1:] in ("018", "053")) if axis == "price" else (c[1:] in ("05", "15")):
                        if pid not in out:
                            out.append(pid)
    return out


def conditional_power(t1: float, n1: int, n2: int = RB_N2, alpha: float = RB_ALPHA):
    """R-B's ranking (plan 7.2, O-19): the combined test Z = (Z1 + Z2)/√2 at the first-stage estimate."""
    if t1 is None or n1 < 2 or math.isnan(t1):
        return None
    p1 = 1.0 if t1 == 0 else min(1.0, 2 * t_sf(abs(t1), n1 - 1))
    z1 = math.copysign(norm_ppf(1 - p1 / 2), t1) if p1 > 0 else math.copysign(40.0, t1)
    theta = z1 * math.sqrt(n2 / n1)
    c = norm_ppf(1 - alpha / 2)
    return 1 - norm_cdf(math.sqrt(2) * c - z1 - theta) + norm_cdf(-math.sqrt(2) * c - z1 - theta)


RB_INELIGIBLE = ("EXCLUDED-H", "EXCLUDED-D", "NEITHER", "PARTIAL-H", "PARTIAL-D", "PARTIAL-TIED", "VOID")


def rb_select(stats: dict, literal: bool = False, cap: int = RB_CAP) -> list:
    """R-B (plan 7.2): eligible when the body call is UNDECIDED or CONTINGENT, or (the plan's registered reading, not
    ``literal``) NOT RUN with an UNDECIDED income call.  Ranked by conditional power, ties by point id."""
    cand = []
    for pid, s in stats.items():
        body, inc = s["body"], s.get("income") or {}
        ok = body in ("UNDECIDED", "CONTINGENT") or (not literal and body in ("NOT RUN", "RBT-118 (not available)")
                                                     and inc.get("call") == "UNDECIDED")
        if ok and body not in RB_INELIGIBLE:
            layer = s.get("share") if body in ("UNDECIDED", "CONTINGENT") else inc
            cp = conditional_power((layer or {}).get("t"), (layer or {}).get("n", 0))
            cand.append((-(cp if cp is not None else -1), pid, cp))
    cand.sort()
    return [(pid, cp) for _, pid, cp in cand[:cap]]


# -- 9 the verdict logic (provisional at Stage 1) ------------------------------------------------------------------ #

HABITABLE_OUT = RB_INELIGIBLE


def counting_set(calls: list, corroborated: list) -> bool:
    """>= 2 calls, or exactly 1 corroborated by M3 (``corroborated`` parallels ``calls``)."""
    return len(calls) >= 2 or (len(calls) == 1 and bool(corroborated[0]))


def verdicts(points: dict, t1_rejects: bool, corroborate) -> list:
    """The §8 verdicts that hold, in precedence order.  ``points[pid] = {"body", "income", "lever", "vd"}``;
    ``corroborate(pid) -> bool`` is the M3 test on the point's (c, L, s) row."""
    hab = [p for p, s in points.items() if s["body"] not in HABITABLE_OUT]

    def calls(kind_calls, fauna):
        """Calls of these kinds, LEVER and VARIANCE-DRIVEN removed; EARNS calls only at habitable points (plan 4.3)."""
        return [p for p, s in points.items() if s.get(kind_calls) in fauna and not s.get("lever")
                and not (kind_calls == "body" and s.get("vd")) and (kind_calls != "income" or p in hab)]

    def cset(pids):
        return counting_set(pids, [corroborate(p) for p in pids])

    eh, ed = calls("income", ("EARNS-H",)), calls("income", ("EARNS-D",))
    wh, wd = calls("body", ("H-WIN",)), calls("body", ("D-WIN",))
    surv_h = [p for p, s in points.items() if s["body"] in ("EXCLUDED-D", "PARTIAL-H")]
    surv_d = [p for p, s in points.items() if s["body"] in ("EXCLUDED-H", "PARTIAL-D")]
    m_points = [p for p, s in points.items() if s.get("m_arm")]
    resolving_pts = [p for p, s in points.items() if s.get("resolving")]
    out = []
    if t1_rejects and cset(eh) and cset(ed):
        out.append("EARNINGS DEPEND")
    if t1_rejects and cset(wh) and cset(wd):
        out.append("DEPENDS")
    for x, ex, oth in (("H", eh, ed + wd + surv_d), ("D", ed, eh + wh + surv_h)):
        if hab and len([p for p in ex if p in hab]) >= len(hab) / 3 and not cset(sorted(set(oth))):
            out.append(f"EARNINGS DOMINATED ({x})")
    for x, w, oth in (("H", wh, ed + wd + surv_d), ("D", wd, eh + wh + surv_h)):
        if m_points and len(w) >= len(m_points) / 3 and w and not cset(sorted(set(oth))):
            out.append(f"ONE BODY DOMINATES ({x})")
    for x, ex, eo, wo, wx, sy in (("H", eh, ed, wd, wh, surv_d), ("D", ed, eh, wh, wd, surv_h)):
        if ex and not cset(eo) and not wo and cset(sy):
            out.append(f"DEPENDS ONLY THROUGH HABITABILITY ({x})")
    ties = [p for p in hab if points[p].get("income") == "EARNS-TIE"]
    no_pairs = not ((cset(eh) and cset(ed)) or (cset(wh) and cset(wd)))
    share_route = len(resolving_pts) >= 6 and len([p for p in resolving_pts if points[p]["body"] == "TIE"]) >= len(resolving_pts) / 2
    if not t1_rejects and no_pairs and ((hab and len(ties) >= len(hab) / 2) or share_route):
        out.append("WORLD-INVARIANT")
    return out or ["NOT RESOLVED"]


# -- readers of restored run directories (guarded) ----------------------------------------------------------------- #

def read_run(d: str, root: str = ROOT) -> dict:
    """history, lineage rows (a list), price and living cost of one restored run directory, after the quarantine
    check.  Only called after integrity passes (plan section 1)."""
    refuse_quarantined(path=d, root=root)
    p = _abs(d, root)
    cfg = json.load(open(os.path.join(p, "config.json")))
    hist = json.load(open(os.path.join(p, "history.json")))["history"] if os.path.exists(os.path.join(p, "history.json")) else []
    rows = []
    path = os.path.join(p, "lineage.jsonl")
    if os.path.exists(path):
        rows = [json.loads(line) for line in open(path) if line.strip()]
    return {"history": hist, "rows": rows, "price": float(cfg["sim"]["food"]["work_cost"]),
            "living_cost": float(cfg["ecology"]["living_cost"])}


def unit_dir(root: str, pid: str, j: int) -> str:
    return os.path.join(root, "runs", "RBT-129", "stage1", pid, str(SEED_BASE + j))


def history_crosscheck(run: dict, kind: str, lo: int = WINDOW[0], hi: int = WINDOW[1]) -> int:
    """Plan 3.2's cross-check: the seasons in [lo, hi] where the member-season count differs from (alive − births) +
    deaths in history.json."""
    bad = 0
    for s in range(lo, hi + 1):
        e = next((x for x in run["history"] if x["season"] == s and x["population"] == kind), None)
        n_rows = sum(1 for _ in member_seasons(run["rows"], kind, s, s))
        want = 0 if e is None else e["alive"] - e["births"] + e["deaths"]
        bad += n_rows != want
    return bad


def null_kind(j: int) -> str:
    """The merge-null kind of seed j (``stages.null_kind``): holistic on odd seeds, designed on even."""
    return H if j % 2 else D


def assemble_point(root: str, pid: str, m_seeds: list = (), n_seeds: list = (), void_seeds: list = (),
                   crashed_seeds: list = ()) -> dict:
    """Per-seed values at one point (plan section 3), from its restored directories.  ``m_seeds`` and ``n_seeds`` are
    the gate's (``lanes/1-MN/launch.txt``); ``crashed_seeds`` are M seeds that are CRASHED, which are never read."""
    out = {"pid": pid, "n": 0, "extinct": {H: 0, D: 0}, "merge": {}, "valid_share": 0, "x": {}, "s0": {}, "y_m": {},
           "y_n": {}, "m_flow": {}, "s_flow": {}, "g0": {}, "void_seeds": list(void_seeds), "crashed": list(crashed_seeds),
           "m_seeds": list(m_seeds), "n_seeds": list(n_seeds), "crosscheck": 0}
    for j in SEEDS:
        if j in void_seeds:
            continue
        u = unit_dir(root, pid, j)
        s = read_run(os.path.join(u, "S"), root)
        ck = os.path.join(u, "ckpt60")
        merge_hist = read_run(ck, root)["history"] if os.path.exists(os.path.join(ck, "history.json")) else s["history"]
        out["n"] += 1
        for k in FAUNAS:
            out["extinct"][k] += extinct_by_end(s["history"], k)
        h59, d59 = alive(merge_hist, H, SEASON_MERGE) > 0, alive(merge_hist, D, SEASON_MERGE) > 0
        out["merge"][j] = (h59, d59)
        out["valid_share"] += h59 and d59
        if h59 and d59:
            out["s0"][j] = merge_share(merge_hist, H)
        if valid_income(s["history"]):
            fh, fd = flow(s["rows"], H, s["price"]), flow(s["rows"], D, s["price"])
            out["x"][j] = fh - fd
            out["s_flow"][j] = (fh, fd)
            out["crosscheck"] += sum(history_crosscheck(s, k) for k in FAUNAS)
        if j in m_seeds:
            if j in crashed_seeds:
                continue  # CRASHED (ruling item 1): never read, never imputed
            m = read_run(os.path.join(u, "M"), root)
            out["y_m"][j] = yprime_m(m["history"], merge_hist)
            out["m_flow"][j] = (flow(m["rows"], H, m["price"]), flow(m["rows"], D, m["price"]))
            pooled = [season_net(r, m["price"]) for k in FAUNAS for r in member_seasons(m["rows"], k, *G0_WINDOW)]
            out["g0"][j] = (sum(pooled) / len(pooled) + G0_OFFSET) if pooled else None
        if j in n_seeds:
            nrun = read_run(os.path.join(u, "N"), root)
            out["y_n"][j] = yprime_n(nrun["history"], merge_hist, null_kind(j))
    return out


def interference(pt: dict) -> dict:
    """M − S per fauna, S paired on the M arm's completed seeds (ruling item 4: at the CRASHED point, the 7)."""
    out = {}
    for k, i in ((H, 0), (D, 1)):
        diffs = [pt["m_flow"][j][i] - pt["s_flow"][j][i] for j in pt["m_flow"]
                 if j in pt["s_flow"] and pt["m_flow"][j][i] is not None]
        out[k] = (sum(diffs) / len(diffs), len(diffs)) if diffs else (None, 0)
    return out


def call_points(pts: dict, resolvable=None, var_null=None, df_null: int = 0, k2: dict = None, k2_pooled_pass: bool = True) -> dict:
    """The per-point calls (plan sections 4-5) over the assembled points: the income families over every tested point,
    the share families over the points where N ran only (ruling item 4(a))."""
    inc = {p: one_sample_t(list(v["x"].values())) for p, v in pts.items()}
    earns = bh({p: r["p"] for p, r in inc.items()})
    tie_p = {p: tost_p(list(v["x"].values()), DELTA_I) for p, v in pts.items()}
    ties = bh(tie_p)
    n_ran = {p for p, v in pts.items() if v["y_n"]}
    k2_fail = {p: (k2 or {}).get(p) == "FAIL" or (p in n_ran and not k2_pooled_pass) for p in pts}
    # O-22: a point whose body call is settled by items 1-3 (EXCLUDED, NEITHER, PARTIAL, VOID) enters no share family
    pre = {p for p in n_ran if body_call({"n": pts[p]["n"], "extinct": pts[p]["extinct"], "valid_share": pts[p]["valid_share"],
                                          "merge": pts[p]["merge"], "void": k2_fail[p], "n_ran": False}) != "NOT RUN"}
    tested = n_ran - pre
    share = {p: one_sample_t([pts[p]["y_m"][j] for j in pts[p]["y_m"] if j in pts[p]["s0"]]) for p in n_ran}
    wins = bh({p: share[p]["p"] for p in tested})
    stie = bh({p: tost_p([pts[p]["y_m"][j] for j in pts[p]["y_m"] if j in pts[p]["s0"]], DELTA_S) for p in tested})
    cont_p = {p: (contingent_p(list(pts[p]["y_m"].values()), var_null, df_null) if contingent_callable(df_null) else None)
              for p in tested}
    cont = bh(cont_p)
    out = {}
    for p, v in pts.items():
        res = (resolving(bool(v["m_seeds"]), True, [g for g in v["g0"].values() if g is not None], share[p]["n"], resolvable)
               if p in n_ran else False)
        s = share.get(p, {})
        f99 = cont_p.get(p) is not None and cont_p[p] < 0.01
        body = body_call({"n": v["n"], "extinct": v["extinct"], "valid_share": v["valid_share"], "merge": v["merge"],
                          "void": k2_fail[p], "n_ran": p in n_ran, "anchor": p in ANCHORS_STAGE1,
                          "share": {"mean": s.get("mean"), "rejected": p in wins},
                          "contingent": p in cont and f99, "tie": p in stie, "resolving": res})
        r = inc[p]
        # K1 and K2 VOID the share call only; the income layer loses only K-SALT-VOID seeds (plan 2.8, 4.3)
        call = income_call(r["mean"] if r["p"] is not None else None, p in earns, p in ties)
        out[p] = {"body": body, "income": {**r, "call": call, "tost_p": tie_p[p]}, "share": {**s, "call": body}
                  if p in n_ran else {}, "resolving": res, "share_family": p in tested}
    return out


def flow_from_history(history: list, kind: str, price: float, lo: int = WINDOW[0], hi: int = WINDOW[1]):
    """Plan 3.2's second cross-check: the member-season-weighted mean of the sweep log's ``food_mean − p ·
    work_mean / 1000`` (every member evaluated that season, the living and the dead), weights (alive − births) +
    deaths.  None where the log has no such field."""
    num = den = 0
    for e in history:
        if e["population"] != kind or not lo <= e["season"] <= hi:
            continue
        if e.get("food_mean") is None or e.get("work_mean") is None:
            return None
        n = e["alive"] - e["births"] + e["deaths"]
        num += n * (e["food_mean"] - price * e["work_mean"] / 1000.0)
        den += n
    return (num / den) if den else None


# -- main ---------------------------------------------------------------------------------------------------------- #

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("step", choices=("integrity", "readout"))
    ap.add_argument("--go", help="the coordinator's ruling that lets the readout open Stage-1 outputs (required)")
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args(argv)
    if not a.go:
        print("refused: the Stage-1 readout runs only after READOUT-PLAN.md is committed, reviewed and the coordinator"
              " rules (--go RULING_REF).  Nothing was read.", file=sys.stderr)
        return 9
    if a.step == "integrity":
        prov_path = os.path.join(a.root, "runs", "RBT-129", "stage1-provenance", "verdicts.json")
        prov = json.load(open(prov_path)) if os.path.exists(prov_path) else None
        import resumed
        table = parse_gate_table(os.path.join(a.root, "runs", "RBT-129", "lanes", "1-MN", "gate_table.txt"))
        ok, lines, _ = integrity(a.root, default_reader(), remote_labels(a.root), prov, resumed.written_twice,
                                 gate_valid_from_ckpt60(a.root, table))
        text = f"# RBT-129 Stage 1 integrity (READOUT-PLAN.md section 2); go: {a.go}\n" + "\n".join(lines) + \
               f"\nINTEGRITY {'PASS' if ok else 'FAIL: HELP; nothing further is read'}\n"
        with open(os.path.join(HERE, "integrity.txt"), "w") as f:
            f.write(text)
        print(text)
        return 0 if ok else 1
    # The readout (plan sections 3-10) assembles the functions above over the restored directories once integrity.txt
    # reads PASS; it is written and run in the readout session, not here (no Stage-1 output is opened before the go).
    raise SystemExit("readout: run `integrity` first; the assembly runs in the readout session after INTEGRITY PASS")


if __name__ == "__main__":
    sys.exit(main())
