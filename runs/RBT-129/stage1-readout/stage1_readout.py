#!/usr/bin/env python3
"""RBT-129 Stage 1 readout (S arm, and the gated M and N forks): the script of ``READOUT-PLAN.md`` (pre-data).

    python3 runs/RBT-129/stage1-readout/stage1_readout.py integrity --go GO_ID   -> stage1-readout/integrity.txt
    python3 runs/RBT-129/stage1-readout/stage1_readout.py readout   --go GO_ID   -> stage1-readout/stage1_readout.txt

**It refuses to run without ``--go ID``**, where ID is a ``GO-ID:`` line the coordinator adds to ``RULINGS-CITED.md``
when it lets the readout open Stage-1 outputs (plan section 1; adversary NOTE 7).  It also refuses while any local ref
names the quarantined unit.  Its tests (``tests/test_rbt129_stage1_readout.py``) use synthetic fixtures only.

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


class ReadoutHelp(RuntimeError):
    """A condition the plan routes to the coordinator (a HELP wake): the readout stops and prints nothing further."""


def label_of(path: str, root: str = ROOT) -> str:
    """``stages._label``: ``rbt-129-<path under runs/RBT-129>``, slashes to dashes."""
    rel = os.path.relpath(_abs(path, root), os.path.join(root, "runs", "RBT-129"))
    return "rbt-129-" + rel.replace(os.sep, "-")


def _abs(path: str, root: str) -> str:
    return os.path.abspath(path if os.path.isabs(path) else os.path.join(root, path))


def _is_quarantined_label(label: str) -> bool:
    """The quarantined label **anywhere** in a ref or label, as a case-insensitive substring: after any prefix
    (``ckpt/``, ``refs/remotes/origin/ckpt/``, ``x-``, ...) and before any suffix (``-``, ``/``, ``.tar``, ``0``, ...).
    No legitimate label contains it (adversary NOTE 6, probe P11; fix-check FC-NOTE 7, Q18)."""
    return QUARANTINED_LABEL.lower() in label.lower()


def _is_quarantined_path(path: str, root: str) -> bool:
    """At or under the quarantined directory, through symlinks too (``realpath``; adversary NOTE 6, probe P10)."""
    q = QUARANTINED_DIR.lower()
    for base, target in ((root, _abs(path, root)), (os.path.realpath(root), os.path.realpath(_abs(path, root)))):
        rel = os.path.relpath(target, base).lower()
        if rel == q or rel.startswith(q + os.sep):
            return True
    return False


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
    """Every run directory's ``platform.json`` (ruling items 6, 7).  One code path writes none: a ``snapshot`` job
    whose S is fully extinct at or before season 60 (``stages.run_job``, fix1b) records ``EXTINCT.txt`` in the unit's
    record and makes ``ckpt60`` with ``_mark`` alone: no ecology runs there and S is not copied.  Such a ckpt60 PASSes
    only when its unit record holds ``EXTINCT.txt`` **and** its done-marker reads ``skipped: extinct pre-merge``; every
    other directory needs a 3.14.0 record.  The expected count is 288 S + the ckpt60s copied from a live S + 37 M/N.
    Returns {"pass", "fail", "extinct_ckpt60"}; the last is a count used only for the PASS/FAIL decision (2.6 prints the
    aggregate verdict alone; the extinct units belong to the survival layer)."""
    res = {"pass": 0, "fail": {}, "extinct_ckpt60": 0}
    snap = {j["dir"]: j for j in jobs if j["job"] == "snapshot"}
    for d in platform_dirs(jobs):
        text = read(label_of(d, root), "platform.json")
        if text is None and d in snap:
            j = snap[d]
            rec = read(label_of(os.path.join(unit_of(j), "record"), root), "EXTINCT.txt")
            mark = read(label_of(d, root), f".rbt129-done-{j['name'].split('/')[-1]}")
            if rec is not None and mark is not None and "skipped: extinct pre-merge" in mark:
                res["extinct_ckpt60"] += 1
                continue
            res["fail"][d] = ["no platform.json, and not an extinct-pre-merge ckpt60 (EXTINCT.txt and its marker)"]
            continue
        verdict, probs = check_platform(text)
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


# -- 2.3 the resume audit ----------------------------------------------------------------------------------------- #

#: the one census source written twice, accepted under the double-write signature exactly as the resume audit and
#: the resume adversary's N5 record it (lineage: 347 rows repeated in seasons 55-59; cohorts: 5 rows, the same
#: seasons; no torn line).  Any other double write is a HELP.
KNOWN_DOUBLE_WRITE = {
    os.path.join("runs", "RBT-129", "stage0", "c1-p010-PW-G", "129003", "S"):
        {"lineage.jsonl": (347, [55, 56, 57, 58, 59]), "cohorts.jsonl": (5, [55, 56, 57, 58, 59])}}


def fetch_label(label: str, root: str = ROOT) -> None:
    """Fetch one checkpoint branch by a **narrow refspec** (never a bare fetch: the default refspec would bring the
    quarantined branch; adversary SHOULD 8, NOTE 9), after the quarantine check."""
    import subprocess
    refuse_quarantined(label=label)
    r = subprocess.run(["git", "fetch", "-q", "origin", f"+refs/heads/ckpt/{label}:refs/remotes/origin/ckpt/{label}"],
                       cwd=root, capture_output=True, timeout=600)
    if r.returncode:
        raise ReadoutHelp(f"fetch of ckpt/{label} failed (exit {r.returncode}): HELP")  # fix-check FC-NOTE 2


def audit_dirs(jobs: list) -> list:
    """Every directory the resume audit covers: the run directories (S, ckpt60, M, N) and the census sources the lanes
    adopt from or K-SALT compares against."""
    out = []
    for j in jobs:
        for d in ([j["dir"]] if j["job"] in RUN_JOBS else []) + ([j["src"]] if j["job"] == "adopt" else []) \
                + ([j["ref"]] if j["job"] == "ksalt" and "ref" in j else []):
            if d not in out:
                out.append(d)
    return out


def _known_signature(d: str, rec: dict, root: str) -> bool:
    want = KNOWN_DOUBLE_WRITE.get(os.path.relpath(_abs(d, root), root))
    if not want:
        return False
    return all(rec.get(name, {}).get("repeated") == n and rec[name].get("repeated_seasons") == seasons
               and rec[name].get("torn") == 0 for name, (n, seasons) in want.items())


def double_writes(jobs: list, written_twice, fetch=None, root: str = ROOT) -> tuple:
    """(bad {dir: record}, accepted [dir]): ``resumed.written_twice`` on every audited directory (S chains, census
    sources and the 37 forks, which ``resumed.py`` itself does not list), each fetched first by its own narrow refspec
    (NOTE 9) and checked against the quarantine before either call.  A double write is a HELP unless it is the listed
    census signature case."""
    bad, accepted = {}, []
    for d in audit_dirs(jobs):
        lab = label_of(d, root)
        refuse_quarantined(label=lab)
        refuse_quarantined(path=d, root=root)
        if fetch is not None:
            fetch(lab)
        rec = written_twice(lab)
        if any(v["repeated"] or v["steps_back"] or v["torn"] for v in rec.values()):
            if _known_signature(d, rec, root):
                accepted.append(d)
            else:
                bad[d] = rec
    return bad, accepted


def gate_valid_from_history(root: str, table: dict, read) -> dict:
    """{point: {j: valid at the merge}} at the M-eligible points, from each unit's ckpt60 ``history.json`` read alone
    through the guarded reader: no directory is restored during integrity (adversary SHOULD 9).  A unit whose ckpt60 has
    no history (extinct pre-merge) is not valid."""
    out = {}
    for pid, (k, _, _) in table.items():
        if k is None:
            continue
        out[pid] = {}
        for j in SEEDS:
            text = read(label_of(os.path.join(unit_dir(root, pid, j), "ckpt60"), root), "history.json")
            out[pid][j] = valid_share(json.loads(text)["history"]) if text else False
    return out


def local_quarantine_refs(root: str = ROOT) -> list:
    """Any local ref naming the quarantined unit (``refs/remotes/origin/ckpt/<label>`` after a bare fetch): listed by
    name only (adversary SHOULD 8)."""
    import subprocess
    r = subprocess.run(["git", "for-each-ref", "--format=%(refname)"], cwd=root, capture_output=True, text=True)
    return [ref for ref in r.stdout.split() if _is_quarantined_label(ref)]


def fork_seed_mismatches(valid: dict, forks: dict) -> list:
    """Each admitted point's M (and N) seeds must be exactly its valid-at-merge seeds (T5's seed rule)."""
    probs = []
    for pid, arms in forks.items():
        want = sorted(j for j, v in valid.get(pid, {}).items() if v)
        for arm in ("M", "N"):
            if arms[arm] and sorted(arms[arm]) != want:
                probs.append(f"{pid}: {arm} seeds {sorted(arms[arm])} are not its valid seeds {want}")
    return probs


# -- integrity driver ---------------------------------------------------------------------------------------------- #

def integrity(root: str, read, have: set, written_twice=None, fetch=None, local_refs: list = ()) -> tuple:
    """(ok, lines, state): plan section 2, in order.  ``read`` is a guarded reader; ``have`` the ``ls-remote`` labels;
    no file from ``stage1-provenance/`` is read (coordinator ruling on FC-MUST 2); ``written_twice`` is ``resumed.written_twice`` and ``fetch`` the narrow-refspec fetch (2.3); ``local_refs`` the local
    refs naming the quarantined unit (must be empty).  A check given None is printed as not run, and fails."""
    lines, ok = [], True
    lines.append(f"2.5 local refs naming the quarantined unit: {len(local_refs)}" + (" (a bare fetch ran: HELP)" if local_refs else ""))
    ok &= not local_refs
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
    lines.append(f"2.2 done-markers: {mk['done'] + mk['extinct']} present (extinct-pre-merge skips included, not split out), "
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
        lines.append("2.3 the resume audit (double writes): NOT RUN")
        ok = False
    else:
        dw, accepted = double_writes(jobs, written_twice, fetch, root)
        n = len(audit_dirs(jobs))
        lines.append(f"2.3 the resume audit: {n - len(dw) - len(accepted)} of {n} directories (S chains, census sources,"
                     f" forks) clean; {len(accepted)} accepted under the listed double-write signature")
        lines += [f"  ACCEPTED (signature) {os.path.relpath(_abs(d, root), root)}" for d in accepted]
        lines += [f"  WRITTEN TWICE {os.path.relpath(_abs(d, root), root)}: HELP" for d in sorted(dw)]
        ok &= not dw
    pl = check_platforms(jobs, read, root)
    lines.append(f"2.6 MuJoCo {MUJOCO}: {'PASS' if not pl['fail'] else 'FAIL: HELP'} (every S, every ckpt60 copied from a live S"
                 " and every M/N carries a 3.14.0 record at the top level and on every resume; each ckpt60 without a"
                 " platform.json is an extinct-pre-merge snapshot verified by its unit record's EXTINCT.txt and marker)")
    for d, p in sorted(pl["fail"].items()):
        lines.append(f"  FAIL {os.path.relpath(_abs(d, root), root)}: {'; '.join(p)}")
    ok &= not pl["fail"]
    ks = check_ksalt(jobs, read, root)
    void = sorted(n for n, (r, _, _) in ks.items() if r != "PASS")
    lines.append(f"2.7 K-SALT: {len(ks) - len(void)} of {len(ks)} PASS (unit record's KSALT.txt)")
    for n, (r, own, note) in sorted(ks.items()):
        if r != "PASS" or own != r or note != "present":
            lines.append(f"  {n}: record {r}, ksalt dir {own}, marker {note}"
                         + ("  (F7: the stream claim re-opens: HELP)" if r != "PASS" else ""))
    ok &= not void
    table = parse_gate_table(os.path.join(root, "runs", "RBT-129", "lanes", "1-MN", "gate_table.txt"))
    gv = gate_valid_from_history(root, table, read)
    gm = gate_mismatches(table, gv) + fork_seed_mismatches(gv, mn_forks(root))
    lines.append(f"2.7 the gate's valid-at-merge counts against gate_table.txt: {'PASS' if not gm else 'FAIL: HELP'}"
                 " (ckpt60 history.json read alone; seen at emission, mn-emitter ruling item 7)")
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
    """(EXCLUDED at >= ceil(5n/8), PARTIAL at < ceil(3n/4)) (F's T6).  n = 0 (every seed K-SALT VOID) is a HELP, never
    NEITHER (adversary NOTE 14)."""
    if n < 1:
        raise ReadoutHelp("a point with no non-VOID seed: HELP (plan 4.1)")
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


def pooled_null(runs: dict) -> dict:
    """{kind: (σ̂², df)} from ``runs[(point, kind)] = [y′, ...]``, **per kind** (DESIGN §6.1 item 6; adversary SHOULD 1),
    each (point, kind) mean removed (O-9): df_kind = Σ over that kind's points of (n − 1)."""
    out = {}
    for kind in FAUNAS:
        ss, df = 0.0, 0
        for (pt, k), ys in runs.items():
            if k == kind and len(ys) >= 2:
                m = sum(ys) / len(ys)
                ss += sum((y - m) ** 2 for y in ys)
                df += len(ys) - 1
        out[kind] = ((ss / df) if df else None, df)
    return out


#: O-9 pin (SHOULD 1): the M arm's y′ is the holistic share change, so its F test divides by the **holistic-null**
#: kind's σ̂² (K = holistic: the relabelled change of the holistic label), and CONTINGENT is callable only when that
#: kind's df reaches 12.  The designed-null kind's σ̂² and df are printed beside it.
CONTINGENT_KIND = H


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
    """{point: 'PASS' | 'FAIL'}: the t test not rejected under BH (over the points with >= 2 runs) **and**
    |mean y′_null| <= 0.15.  At one run the t clause cannot reject, and the size bar alone decides (SHOULD 2)."""
    ps = {pt: one_sample_t(ys)["p"] for pt, ys in null.items()}
    rej = bh(ps)
    return {pt: ("PASS" if pt not in rej and abs(sum(ys) / len(ys)) <= K2_POINT_BAR else "FAIL") for pt, ys in null.items()}


def g0_bounds(g0s: list):
    """The 90% bounds of g0 over seeds (plan 3.4), None at n < 2."""
    if len(g0s) < 2:
        return None
    m, sd = mean_sd(g0s)
    h = t_ppf(0.95, len(g0s) - 1) * sd / math.sqrt(len(g0s))
    return m - h, m + h


PILOT_CONSTANTS = os.path.join(RUNS, "stageP0-readout", "pilot_constants.json")


def scaled_resolvable(pilot: str = PILOT_CONSTANTS):
    """``power.resolvable`` with the replica's drift scaled by the pilot (DESIGN §4.1, §10.1 last bullet: the checks
    are rescaled; #500 item 2 exempts the gate only): ``power.load_pilot`` sets ``Y_SCALE`` (1.5297) first.  Returns
    (resolvable, y_scale) so the scale is printed (adversary MUST 1b)."""
    sys.path.insert(0, RUNS)
    import power  # noqa: E402
    power.load_pilot(pilot)
    return power.resolvable, power.Y_SCALE


def resolving(m_ran: bool, n_ran: bool, g0s: list, n: int, resolvable=None) -> tuple:
    """Ruling item 4(b): only where M and N both ran.  Returns (RESOLVING?, the replica's rows or None).
    ``resolvable`` has ``power.resolvable``'s shape: it returns ``(rows, passes)``, and passes must hold at both 90%
    bounds (MUST 1a: a bare truth test on the tuple was always True)."""
    if not (m_ran and n_ran):
        return False, None
    b = g0_bounds(g0s)
    if b is None:
        return False, None
    if resolvable is None:
        resolvable = scaled_resolvable()[0]
    rows, passes = resolvable(b[0], b[1], "lottery", n, reps=1500)
    return bool(passes), rows


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
TERM_NAMES = {1: "c", 2: "log p", 3: "L=HP", 4: "L=PW", 5: "s=G", 6: "c x log p"}


def world_model(seeds: list, g0: dict = None) -> dict:
    """M2's income fit with COORD-RULING-512 R3 (MUST 3).  ``seeds`` = [(point, x_j)] over the habitable points'
    income-valid seeds.  Support rule: drop a world term whose column has no variation; drop c x log p when c or log p
    has fewer than 2 levels.  T1's df is the number P of remaining world terms; T1 is NOT TESTABLE if P = 0, fewer than
    P + 2 habitable points, or the fit is singular or non-finite under the pinned settings (no retry).  T2 (c) and T3
    (log p) are NOT TESTABLE if their term is dropped or T1 is.  A NOT TESTABLE test enters Holm at p = 1.
    With ``g0`` ({point: census g0}) the census g0 is added as a covariate (the share model, §7.2), held under the same
    support rule, and T1 still tests the world terms alone (the share Wald "net of g0")."""
    import numpy as np
    out = {"dropped": [], "T1": None, "T2": None, "T3": None, "status": "NOT TESTABLE", "fit": None}
    if not seeds:
        out["why"] = "no habitable income-valid seed"
        return out
    rows = [design_row(pid) + ([g0[pid]] if g0 is not None else []) for pid, _ in seeds]
    keep = []
    for t in WORLD_TERMS + ((7,) if g0 is not None else ()):
        levels = {round(r[t], 12) for r in rows}
        if len(levels) < 2:
            out["dropped"].append(TERM_NAMES.get(t, "census g0"))
            continue
        if t == 6 and ({TERM_NAMES[1], TERM_NAMES[2]} & set(out["dropped"])):
            out["dropped"].append(TERM_NAMES[t])
            continue
        keep.append(t)
    P = len([t for t in keep if t in WORLD_TERMS])
    n_points = len({pid for pid, _ in seeds})
    out["P"], out["points"] = P, n_points
    if P == 0 or n_points < len(keep) + 2:
        out["why"] = f"P = {P} world terms ({len(keep)} terms in all), {n_points} points (needs >= terms + 2)"
        return out
    X = [[r[0]] + [r[t] for t in keep] for r in rows]
    try:
        if np.linalg.matrix_rank(np.asarray(X)) < 1 + len(keep):
            raise np.linalg.LinAlgError("rank-deficient design")
        fit = lmm_reml([x for _, x in seeds], X, [pid for pid, _ in seeds])
        if not np.all(np.isfinite(fit["beta"])) or not np.all(np.isfinite(fit["cov"])):
            raise np.linalg.LinAlgError("non-finite fit")
    except np.linalg.LinAlgError as e:
        out["why"] = f"the fit is singular or does not converge ({e}); no retry (R3)"
        return out
    out["fit"], out["status"], out["keep"] = fit, "TESTABLE", keep
    out["T1"] = wald(fit, tuple(i + 1 for i, t in enumerate(keep) if t in WORLD_TERMS))
    for name, term in (("T2", 1), ("T3", 2)):
        if term in keep:
            out[name] = wald_one(fit, keep.index(term) + 1)
    return out


CLIP = 1.0 / 240


def share_logit_change(y_prime: float, s0: float) -> float:
    """§7.2's share response: logit(window share, clipped to [1/240, 1 − 1/240]) − logit(share at the merge)."""
    def logit(s):
        s = min(max(s, CLIP), 1 - CLIP)
        return math.log(s / (1 - s))
    return logit(y_prime + s0) - logit(s0)


def map_holm(model: dict, alpha: float = ALPHA_HOLM) -> tuple:
    """(rejected set, p-values used): Holm over T1–T4 with every NOT TESTABLE test and T4 (NOT MEASURED) at p = 1."""
    ps = {"T1": model["T1"][2] if model.get("T1") else 1.0,
          "T2": model["T2"][1] if model.get("T2") else 1.0,
          "T3": model["T3"][1] if model.get("T3") else 1.0}
    return holm_provisional(ps, alpha), ps


def t1_state(model: dict, rejected: set) -> str:
    if model.get("T1") is None:
        return "NOT TESTABLE"
    return "rejects" if "T1" in rejected else "does not reject"


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
        flank = next((r for r in rows if r["mid"] == mid), None)
        if flank is None:  # O-23 as ruled: a C1 candidate is always the midpoint of a Stage-1 pair
            raise ValueError(f"{mid} is not an R-A midpoint of any Stage-1 pair (O-23)")
        if mid not in chosen:
            rows.append({**flank, "fires": True, "source": "C1"})
            chosen.add(mid)
    fired = [r for r in rows if r["fires"]]

    def key(r):
        """G block first (O-16); within it |Δt| descending (inf first), undefined |Δt| last; ties by midpoint id."""
        dt = r["dt"]
        return (0 if r["smell"] == "G" else 1, dt is None, -(dt if dt is not None else 0.0), r["mid"])
    fired.sort(key=key)
    seen, out = set(), []
    for r in fired:
        if r["mid"] not in seen:
            seen.add(r["mid"])
            out.append(r["mid"])
    return out[:cap], rows


def c1_candidates(readout_txt: str) -> list:
    """Plan 7.1 (O-17; O-23 as ruled by the fix-check adversary, adopted by the coordinator): every sign change on a
    C1-listed row of the committed census readout adds **the R-A midpoint of the adjacent Stage-1 pair that flanks it**.
    Only Stage-1 rows have such a pair, so a candidate is kept only if it is a midpoint of ``ra_pairs()`` (7 from the
    committed readout)."""
    midpoints = {m for _, _, m, _ in ra_pairs()}
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
                        if pid in midpoints and pid not in out:
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


#: the three RBT-118 anchors (DESIGN §9.1); not R-B-eligible (COORD-RULING-512 R4 (ii))
ANCHORS = ("c1-p030-U-L", "c0-p030-U-L", "c1-p030-PW-G")


def rb_select(stats: dict, literal: bool = False, cap: int = RB_CAP) -> list:
    """R-B (plan 7.2; COORD-RULING-512 R4, DATA-INFORMED): eligible when the body call is UNDECIDED or CONTINGENT, or
    (unless ``literal``, the non-registered literal list) NOT RUN with an UNDECIDED income call.  The anchors are never
    eligible (R4 (ii)).  CP is ranked on the share layer at UNDECIDED/CONTINGENT points and on the **income** t and the
    income-valid n at NOT RUN points (R4 (i)).  Ties by point id."""
    cand = []
    for pid, s in stats.items():
        if pid in ANCHORS:
            continue
        body, inc = s["body"], s.get("income") or {}
        ok = body in ("UNDECIDED", "CONTINGENT") or (not literal and body == "NOT RUN" and inc.get("call") == "UNDECIDED")
        if ok:
            layer = s.get("share") if body in ("UNDECIDED", "CONTINGENT") else inc
            cp = conditional_power((layer or {}).get("t"), (layer or {}).get("n", 0))
            cand.append((-(cp if cp is not None else -1), pid, cp))
    cand.sort()
    return [(pid, cp) for _, pid, cp in cand[:cap]]


def rb_core_h(n_points: int, seeds: int = RB_N2, core_s=(23.35, 43.72)) -> tuple:
    """The S arms R-B would add: n points x 8 seeds x 300 arm-seasons, at the pilot's core-s (M and N are gated
    separately and not priced here).  Printed only; R-B needs its own owner GO (R4)."""
    return tuple(n_points * seeds * 300 * c / 3600.0 for c in core_s)


def stage2_income_call(x1: list, x2: list, earns_rejected, tie_rejected) -> str:
    """Stage 2's income call at an R-B point (COORD-RULING-512 R4 (iii)).  Each half's signed z is the inverse normal
    of its one-sided t p-value; Z = (Z1 + Z2)/√2 (Lehmacher & Wassmer).  ``earns_rejected(p_two_sided) -> bool`` is the
    final BH decision on the combined EARNS p, and ``tie_rejected`` the TIE family's on the combined TOST p (the larger
    of the two combined one-sided p, so both must pass).  The |x̄| >= 0.10 bar is read on the pooled mean of all 16
    seeds."""
    def z_one_sided(xs, mu, upper):
        m, sd = mean_sd(xs)
        t = (m - mu) / (sd / math.sqrt(len(xs)))
        p = t_sf(t, len(xs) - 1) if upper else 1 - t_sf(t, len(xs) - 1)
        return norm_ppf(1 - p)

    def combine(mu, upper):
        return (z_one_sided(x1, mu, upper) + z_one_sided(x2, mu, upper)) / math.sqrt(2)
    zc = combine(0.0, True)
    p_earns = 2 * (1 - norm_cdf(abs(zc)))
    pooled = sum(x1 + x2) / len(x1 + x2)
    if earns_rejected(p_earns) and abs(pooled) >= EARNS_MIN and pooled != 0:
        return "EARNS-H" if pooled > 0 else "EARNS-D"
    p_lo = 1 - norm_cdf(combine(-DELTA_I, True))   # H0: mu <= -0.15
    p_hi = 1 - norm_cdf(combine(DELTA_I, False))   # H0: mu >= +0.15
    return "EARNS-TIE" if tie_rejected(max(p_lo, p_hi)) else "UNDECIDED"


# -- 9 the verdict logic (provisional at Stage 1) ------------------------------------------------------------------ #

HABITABLE_OUT = ("EXCLUDED-H", "EXCLUDED-D", "NEITHER", "PARTIAL-H", "PARTIAL-D", "PARTIAL-TIED", "VOID")
T1_STATES = ("rejects", "does not reject", "NOT TESTABLE")
NO_VERDICT_T1 = "NO VERDICT at Stage 1 (T1 NOT TESTABLE)"


def counting_set(calls: list, corroborated: list) -> bool:
    """>= 2 calls, or exactly 1 corroborated by M3 (``corroborated`` parallels ``calls``)."""
    return len(calls) >= 2 or (len(calls) == 1 and bool(corroborated[0]))


def verdicts(points: dict, t1: str, corroborate, earns_habitable_only: bool = False, v5_ignores_tie: bool = False) -> list:
    """The §8 verdicts that hold, in precedence order.  ``points[pid] = {"body", "income", "lever", "vd", "m_arm",
    "resolving"}``; ``t1`` is one of ``T1_STATES``; ``corroborate(pid) -> bool`` is the M3 test on the point's row.

    Registered (COORD-RULING-512): R1, EARNS calls count at every point with an income call (habitability is verdict 3's
    and verdict 6's denominator only); R2, EARNS-TIE is a decided income call, so verdict 5 fails if any exists; R3, a
    NOT TESTABLE T1 makes verdicts 1, 2 and 6 unreachable, and if nothing is reached the result is
    ``NO_VERDICT_T1``.  ``earns_habitable_only`` and ``v5_ignores_tie`` give the non-registered readings, printed as
    labelled descriptive lines only."""
    if t1 not in T1_STATES:
        raise ValueError(t1)
    hab = [p for p, s in points.items() if s["body"] not in HABITABLE_OUT]

    def calls(kind_calls, fauna):
        """Calls of these kinds, LEVER and VARIANCE-DRIVEN removed."""
        return [p for p, s in points.items() if s.get(kind_calls) in fauna and not s.get("lever")
                and not (kind_calls == "body" and s.get("vd")) and (kind_calls != "income" or not earns_habitable_only or p in hab)]

    def cset(pids):
        return counting_set(pids, [corroborate(p) for p in pids])

    eh, ed = calls("income", ("EARNS-H",)), calls("income", ("EARNS-D",))
    ties_all = calls("income", ("EARNS-TIE",))
    wh, wd = calls("body", ("H-WIN",)), calls("body", ("D-WIN",))
    surv_h = [p for p, s in points.items() if s["body"] in ("EXCLUDED-D", "PARTIAL-H")]
    surv_d = [p for p, s in points.items() if s["body"] in ("EXCLUDED-H", "PARTIAL-D")]
    m_points = [p for p, s in points.items() if s.get("m_arm")]
    resolving_pts = [p for p, s in points.items() if s.get("resolving")]
    rejects, testable = t1 == "rejects", t1 != "NOT TESTABLE"
    out = []
    if rejects and cset(eh) and cset(ed):
        out.append("EARNINGS DEPEND")
    if rejects and cset(wh) and cset(wd):
        out.append("DEPENDS")
    for x, ex, oth in (("H", eh, ed + wd + surv_d), ("D", ed, eh + wh + surv_h)):
        if hab and len([p for p in ex if p in hab]) >= len(hab) / 3 and not cset(sorted(set(oth))):
            out.append(f"EARNINGS DOMINATED ({x})")
    for x, w, oth in (("H", wh, ed + wd + surv_d), ("D", wd, eh + wh + surv_h)):
        if m_points and w and len(w) >= len(m_points) / 3 and not cset(sorted(set(oth))):
            out.append(f"ONE BODY DOMINATES ({x})")
    for x, ex, eo, wo, sy in (("H", eh, ed, wd, surv_d), ("D", ed, eh, wh, surv_h)):
        if ex and not cset(eo) and (v5_ignores_tie or not ties_all) and not wo and cset(sy):
            out.append(f"DEPENDS ONLY THROUGH HABITABILITY ({x})")
    ties_hab = [p for p in hab if points[p].get("income") == "EARNS-TIE"]
    no_pairs = not ((cset(eh) and cset(ed)) or (cset(wh) and cset(wd)))
    share_route = len(resolving_pts) >= 6 and len([p for p in resolving_pts if points[p]["body"] == "TIE"]) >= len(resolving_pts) / 2
    if testable and not rejects and no_pairs and ((hab and len(ties_hab) >= len(hab) / 2) or share_route):
        out.append("WORLD-INVARIANT")
    if out:
        return out
    return [NO_VERDICT_T1] if not testable else ["NOT RESOLVED"]


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


REGIME_WINDOWS = ((0, 59), (60, 119), (120, 179), (180, 239), (240, 299))


def guarded_regime(d: str, root: str = ROOT, windows=REGIME_WINDOWS) -> dict:
    """``scripts/regime.py``'s ``regime()`` on one run directory, after the quarantine check (plan 3.5)."""
    refuse_quarantined(path=d, root=root)
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import regime  # noqa: E402
    return regime.regime(_abs(d, root), windows=windows)


def regime_window(res: dict, kind: str, lo: int = WINDOW[0]) -> dict:
    """regime's statistics for the window starting at ``lo`` ({} where it has none)."""
    return next((w for w in res.get("fauna", {}).get(kind, []) if w.get("window", [None])[0] == lo), {})


def per_birth_from_regime(res: dict, kind: str):
    """regime's ``net_per_birth`` in 240-299, or None (no complete life)."""
    return regime_window(res, kind).get("net_per_birth")


def regime_summary(res: dict) -> dict:
    """{kind: [(window lo, saturation_local, viability, alive)]} for the per-60-season regime table (§5.3d)."""
    return {k: [(lo, regime_window(res, k, lo).get("saturation_local"), regime_window(res, k, lo).get("viability"),
                 regime_window(res, k, lo).get("alive")) for lo, _ in REGIME_WINDOWS] for k in FAUNAS}


def income_spread(rows, kind: str, price: float, lo: int = G0_WINDOW[0], hi: int = G0_WINDOW[1]) -> dict:
    """Plan 3.6 (VARIANCE-DRIVEN inputs, M arm, 180-299): the within-member SD of season nets, averaged over members
    with >= 2 member-seasons; the pooled member-season SD beside it; the share of zero-income seasons (food = 0), in which
    **exploded rows count** (their food is zeroed by ``Simulation.harvest``; COORD-RULING-512 R5, NOTE 3), with the
    exploded count printed."""
    by, every, zero, exploded = {}, [], 0, 0
    for r in member_seasons(rows, kind, lo, hi):
        v = season_net(r, price)
        by.setdefault(r.get("name"), []).append(v)
        every.append(v)
        zero += float(r.get("food", 0.0)) == 0.0
        exploded += bool(r.get("exploded"))
    sds = [mean_sd(v)[1] for v in by.values() if len(v) >= 2]
    return {"sd_within": (sum(sds) / len(sds)) if sds else None,
            "sd_pooled": mean_sd(every)[1] if len(every) >= 2 else None,
            "zero_share": (zero / len(every)) if every else None, "exploded": exploded, "n": len(every)}


def s_summary(run: dict) -> dict:
    """Plan §8's descriptive S-arm lines, per fauna: alive at 299, births and deaths over 240-299, the extinction season
    (the first season with alive 0, or None), mean_lifetime_score over 240-299 (continuity), and the mean food, work and
    path over the window's member-seasons."""
    out = {}
    for k in FAUNAS:
        ent = [e for e in run["history"] if e["population"] == k]
        win = [e for e in ent if WINDOW[0] <= e["season"] <= WINDOW[1]]
        ext = next((e["season"] for e in ent if e["alive"] == 0), None)
        if ext is None and ent and ent[-1]["season"] < SEASON_END:
            ext = ent[-1]["season"] + 1
        rows = list(member_seasons(run["rows"], k, *WINDOW))
        mean = lambda f: (sum(float(r.get(f, 0.0)) for r in rows) / len(rows)) if rows else None
        out[k] = {"alive299": alive(run["history"], k, SEASON_END), "births": sum(e["births"] for e in win),
                  "deaths": sum(e["deaths"] for e in win), "starved": sum(e.get("starved", 0) for e in win),
                  "aged": sum(e.get("aged", 0) for e in win), "extinct_season": ext,
                  "mls": (sum(e["mean_lifetime_score"] for e in win) / len(win)) if win and all("mean_lifetime_score" in e for e in win) else None,
                  "food": mean("food"), "work": mean("work"), "path": mean("path")}
    return out


def assemble_point(root: str, pid: str, m_seeds: list = (), n_seeds: list = (), void_seeds: list = (),
                   crashed_seeds: list = (), with_regime: bool = False) -> dict:
    """Per-seed values at one point (plan section 3), from its restored directories.  ``m_seeds`` and ``n_seeds`` are
    the gate's (``lanes/1-MN/launch.txt``); ``crashed_seeds`` are M seeds that are CRASHED, never read and never
    imputed.  Raises :class:`ReadoutHelp` on an income-valid seed with no member-season for a fauna, or on a §3.2
    cross-check mismatch there (adversary SHOULD 3, SHOULD 7)."""
    out = {"pid": pid, "n": 0, "extinct": {H: 0, D: 0}, "merge": {}, "valid_share": 0, "valid_income": 0, "x": {},
           "s0": {}, "y_m": {}, "y_n": {}, "m_flow": {}, "s_flow": {}, "g0": {}, "g0_census_conv": {}, "spread": {},
           "per_birth": {}, "variants": {}, "counts59": {}, "regime_s": {}, "regime_m": {}, "living_share": {},
           "s_summary": {}, "void_seeds": list(void_seeds), "crashed": list(crashed_seeds),
           "m_seeds": list(m_seeds), "n_seeds": list(n_seeds)}
    for j in SEEDS:
        if j in void_seeds:
            continue
        u = unit_dir(root, pid, j)
        s = read_run(os.path.join(u, "S"), root)
        ck = os.path.join(u, "ckpt60")
        merge_hist = read_run(ck, root)["history"] if os.path.exists(os.path.join(_abs(ck, root), "history.json")) else s["history"]
        out["n"] += 1
        out["s_summary"][j] = s_summary(s)
        for k in FAUNAS:
            out["extinct"][k] += extinct_by_end(s["history"], k)
        n_h, n_d = alive(merge_hist, H, SEASON_MERGE), alive(merge_hist, D, SEASON_MERGE)
        out["counts59"][j] = (n_h, n_d)
        out["merge"][j] = (n_h > 0, n_d > 0)
        out["valid_share"] += n_h > 0 and n_d > 0
        if n_h > 0 and n_d > 0:
            out["s0"][j] = merge_share(merge_hist, H)
        if valid_income(s["history"]):
            out["valid_income"] += 1
            fh, fd = flow(s["rows"], H, s["price"]), flow(s["rows"], D, s["price"])
            if fh is None or fd is None:
                raise ReadoutHelp(f"{pid}/{SEED_BASE + j}: income-valid, but a fauna has no member-season in 240-299: HELP")
            for k, f in ((H, fh), (D, fd)):
                bad = history_crosscheck(s, k)
                fh2 = flow_from_history(s["history"], k, s["price"])
                if bad or (fh2 is not None and abs(fh2 - f) > 1e-9):
                    raise ReadoutHelp(f"{pid}/{SEED_BASE + j} {k}: the member-season rows disagree with history.json"
                                      f" ({bad} seasons; flow {f} against the sweep log's {fh2}): HELP")
            out["x"][j] = fh - fd
            out["s_flow"][j] = (fh, fd)
            out["variants"][j] = {v: tuple(flow(s["rows"], k, s["price"], variant=var, net=net) for k in FAUNAS)
                                  for v, var, net in (("last_score", "registered", "last_score"),
                                                      ("survivors", "survivors", "net"), ("p0", "p0", "net"))}
            if with_regime:
                res = guarded_regime(os.path.join(u, "S"), root)
                out["per_birth"][j] = {k: per_birth_from_regime(res, k) for k in FAUNAS}
                out["regime_s"][j] = regime_summary(res)
        if j in m_seeds and j not in crashed_seeds:  # CRASHED (ruling item 1): never read; the N read below still runs
            m = read_run(os.path.join(u, "M"), root)
            out["y_m"][j] = yprime_m(m["history"], merge_hist)
            out["living_share"][j] = living_share_window(m["history"])
            out["m_flow"][j] = (flow(m["rows"], H, m["price"]), flow(m["rows"], D, m["price"]))
            for key, var in (("g0", "registered"), ("g0_census_conv", "p0")):
                pooled = [season_net(r, m["price"]) for k in FAUNAS for r in member_seasons(m["rows"], k, *G0_WINDOW, variant=var)]
                out[key][j] = (sum(pooled) / len(pooled) + G0_OFFSET) if pooled else None
            out["spread"][j] = {k: income_spread(m["rows"], k, m["price"]) for k in FAUNAS}
            if with_regime:
                out["regime_m"][j] = regime_summary(guarded_regime(os.path.join(u, "M"), root))
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
        res, res_rows = (resolving(bool(v["m_seeds"]), True, [g for g in v["g0"].values() if g is not None], share[p]["n"],
                                   resolvable) if p in n_ran else (False, None))
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
                  if p in n_ran else {}, "resolving": res, "resolving_rows": res_rows, "share_family": p in tested}
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


# -- 10 the readout driver (plan sections 3-10; COORD-RULING-512 R5: committed before the go) ------------------- #

def _f(x, fmt="{:+.3f}"):
    return "--" if x is None or (isinstance(x, float) and math.isnan(x)) else fmt.format(x)


def mn_forks(root: str) -> dict:
    """{point: {"M": [j], "N": [j]}} from ``lanes/1-MN/launch.txt``'s forks line (registered input)."""
    out = {}
    for f in read_forks_line(os.path.join(root, "runs", "RBT-129", "lanes", "1-MN", "launch.txt")):
        pid, seed, arm = f.split("/")
        out.setdefault(pid, {"M": [], "N": []})[arm].append(int(seed) - SEED_BASE)
    return out


def census_layer(census_txt: str) -> dict:
    """From the committed census readout: {"ff": {kind: set(points)}, "points": {pid: (saturation_local, g0)}}."""
    ff, pts = {H: set(), D: set()}, {}
    for line in open(census_txt):
        m = re.match(r"\s+(holistic|conventional): \d+ of 150 points: (.*)$", line)
        if m:
            ff[m.group(1)] = set(x.strip() for x in m.group(2).split(","))
            continue
        m = re.match(r"\s+(c\d+-p\d+-\w+-[GL])\s+\S+ \| [^|]+\| ([^|]+)\| [^|]+\| [^|]+\| ([^|]+)\|", line)
        if m:
            pts[m.group(1)] = (m.group(2).strip(), m.group(3).strip())
    return {"ff": ff, "points": pts}


def scorecard(calls: dict, model: dict, holm_rej: set, m3: dict, verdict: list) -> list:
    """§12, pinned (adversary SHOULD 6): AS PREDICTED / OPPOSITE / NOT SHOWN / NOT MEASURED per registered prediction."""
    def test_line(name, res, rejected):
        if res is None:
            return f"  {name} > 0: NOT TESTABLE"
        z = res[0]
        return f"  {name} > 0: " + ("AS PREDICTED" if rejected and z > 0 else "OPPOSITE" if rejected else "NOT SHOWN") + f" (z {z:+.2f})"

    def calls_in(pred):
        return [p for p in calls if pred(*parse_point(p))]

    def earns_line(label, pts, want):
        got = [calls[p]["income"]["call"] for p in pts]
        other = "EARNS-H" if want == "EARNS-D" else "EARNS-D"
        word = ("AS PREDICTED" if want in got and other not in got else "OPPOSITE" if other in got and want not in got
                else "NOT SHOWN")
        return f"  {label}: {word} ({got.count(want)} {want}, {got.count(other)} {other} of {len(pts)} points)"
    L = ["## §12 registered predictions: scorecard (PROVISIONAL where §8 is)"]
    L.append(test_line("T2 (clutter)", model.get("T2"), "T2" in holm_rej))
    L.append(test_line("T3 (price)", model.get("T3"), "T3" in holm_rej))
    for c, ref in ((1.0, 0.018), (0.0, 0.053)):
        for row, f in sorted(m3.items()):
            if row[0] == c and f.get("kind") == "bounded":
                word = "AS PREDICTED" if f["lo"] > ref else "OPPOSITE" if f["hi"] < ref else "NOT SHOWN"
                L.append(f"  M3 p* above {ref} at c = {c:g}, row {row}: {word} (p* {_f(f['p_star'], '{:.4f}')} [{_f(f['lo'], '{:.4f}')}, {_f(f['hi'], '{:.4f}')}])")
            elif row[0] == c:
                L.append(f"  M3 p* above {ref} at c = {c:g}, row {row}: NOT SHOWN (Fieller {f.get('kind')})")
    L.append(earns_line("EARNS-D on flat ground at p <= 0.03", calls_in(lambda c, p, L_, s: c == 0 and p <= 0.03), "EARNS-D"))
    L.append(earns_line("EARNS-H at c >= 1, p >= 0.03", calls_in(lambda c, p, L_, s: c >= 1 and p >= 0.03), "EARNS-H"))
    nr = sum(1 for v in calls.values() if v["body"] in ("NOT RUN", "SATURATED", "RBT-118 (not available)"))
    res_n = sum(1 for v in calls.values() if v.get("resolving"))
    L.append(f"  share NOT RUN or SATURATED at most points, RESOLVING at 0-2: "
             f"{'AS PREDICTED' if nr > len(calls) / 2 and res_n <= 2 else 'NOT SHOWN'} ({nr} of {len(calls)}; RESOLVING {res_n})")
    hab = [p for p in calls_in(lambda c, p, L_, s: p == 0.08 and c >= 1) if calls[p]["body"] in ("EXCLUDED-D", "PARTIAL-H")]
    L.append(f"  EXCLUDED-D or PARTIAL-H at some p = 0.08, c >= 1 point: {'AS PREDICTED' if hab else 'NOT SHOWN'} ({', '.join(hab) or 'none'})")
    L.append("  perception (item 4) and retention (item 6): NOT MEASURED")
    L.append(f"  the framing, EARNINGS DEPEND (item 5): {'AS PREDICTED' if verdict and verdict[0] == 'EARNINGS DEPEND' else 'NOT SHOWN'}"
             f" (provisional: {verdict[0] if verdict else '--'})")
    return L


def readout(root: str = ROOT, restore=None, resolvable=None, y_scale=None, with_regime: bool = True,
            census_txt: str = None, void_seeds: dict = None) -> list:
    """Plan sections 3-10 end to end; returns ``stage1_readout.txt``'s lines.  ``restore`` (default the durable
    restore) and ``resolvable`` (default ``power.resolvable`` scaled by the pilot) are injectable for the synthetic-tree
    test.  ``void_seeds`` is the coordinator's ruled K-SALT VOID seeds per point (none unless ruled: a VOID is a HELP)."""
    census_txt = census_txt or os.path.join(RUNS, "stageP0-readout", "stageP0_readout.txt")
    void_seeds = void_seeds or {}
    if resolvable is None:
        resolvable, y_scale = scaled_resolvable()
    forks = mn_forks(root)
    crashed = {CRASHED_POINT: [CRASHED_SEED - SEED_BASE]}
    L = [f"# RBT-129 Stage 1 readout (READOUT-PLAN.md); claim: {CLAIM}",
         f"# share-layer lines are read {SHARE_QUAL}; the sweep answers which body earns more, where, not which persists",
         f"# replica drift scale for RESOLVING: {_f(y_scale, '{:.4f}')} (pilot_constants.json; DESIGN §4.1, §10.1)", ""]
    # restore (plan section 1, step 2): only the directories the readout reads, each through the quarantine guard
    for pid in STAGE1_POINTS:
        fk = forks.get(pid, {"M": [], "N": []})
        for j in SEEDS:
            u = unit_dir(root, pid, j)
            subs = ["S", "ckpt60"] + (["M"] if j in fk["M"] and j not in crashed.get(pid, []) else []) + (["N"] if j in fk["N"] else [])
            for sub in subs:
                guarded_restore(os.path.join(u, sub), root, restore)
    pts = {pid: assemble_point(root, pid, forks.get(pid, {}).get("M", []), forks.get(pid, {}).get("N", []),
                               void_seeds.get(pid, []), crashed.get(pid, []), with_regime) for pid in STAGE1_POINTS}
    # the nulls: K2 and the pooled per-kind null (5.5; 6.1 item 6; O-9, O-12)
    runs, by_point = {}, {}
    for pid, v in pts.items():
        for j, y in v["y_n"].items():
            runs.setdefault((pid, null_kind(j)), []).append(y)
            by_point.setdefault(pid, []).append(y)
    all_null = [y for ys in by_point.values() for y in ys]
    k2ok, k2m, k2t, k2p = k2_pooled(all_null) if all_null else (True, None, None, None)
    k2pt = k2_per_point(by_point)
    pooled = pooled_null(runs)
    var_null, df_null = pooled[CONTINGENT_KIND]
    calls = call_points(pts, resolvable, var_null, df_null, k2pt, k2ok)
    hab = [p for p, c in calls.items() if c["body"] not in HABITABLE_OUT]
    cen = census_layer(census_txt)
    # 4: the per-point table
    L.append("## per-point table (body call; n valid share/income of n; x̄ SD t p TOST-p; income call; MARGINAL; M, N; y′; g0)")
    for pid in STAGE1_POINTS:
        v, c = pts[pid], calls[pid]
        inc = c["income"]
        pb = [(v["per_birth"].get(j) or {}) for j in v["x"]]
        pbi = {k: [per_birth_income(d.get(k)) for d in pb if d.get(k) is not None] for k in FAUNAS}
        pb_mean = {k: (sum(x) / len(x) if x else None) for k, x in pbi.items()}
        marg = marginal(pb_mean) if inc["call"] in ("EARNS-H", "EARNS-D") else None
        mrow = m_row_label(pid, v["m_seeds"], crashed) if v["m_seeds"] else "M --"
        ym = list(v["y_m"].values())
        g0s = [g for g in v["g0"].values() if g is not None]
        g0c = [g for g in v["g0_census_conv"].values() if g is not None]
        cg = cen["points"].get(pid, ("--", "--"))
        L.append(f"  {pid:14s} {c['body']:24s} share {v['valid_share']}/{v['n']} income {v['valid_income']}/{v['n']}"
                 f" | x̄ {_f(inc['mean'])} sd {_f(inc['sd'], '{:.3f}')} t {_f(inc['t'], '{:+.2f}')} p {_f(inc['p'], '{:.4f}')}"
                 f" tost {_f(inc['tost_p'], '{:.4f}')} | {inc['call']}{' MARGINAL' if marg else ''} LEVER not evaluated"
                 f" | {mrow} N {len(v['n_seeds'])} | y′ {_f(sum(ym) / len(ym) if ym else None)} (descriptive)"
                 f" | g0 M {_f(sum(g0s) / len(g0s) if g0s else None, '{:.3f}')} (census convention {_f(sum(g0c) / len(g0c) if g0c else None, '{:.3f}')}),"
                 f" census {cg[1]}")
        L.append(f"      merge counts (H, D) per seed: {' '.join(f'{SEED_BASE + j}:{a}/{b}' for j, (a, b) in sorted(v['counts59'].items()))}")
        L.append(f"      per-birth income (net of work; O-5) H {_f(pb_mean[H])} D {_f(pb_mean[D])};"
                 f" the other reading (net_per_birth < 0.25) printed: H {_f(pb_mean[H] - LIVING_COST if pb_mean[H] is not None else None)}"
                 f" D {_f(pb_mean[D] - LIVING_COST if pb_mean[D] is not None else None)}")
        for name in ("last_score", "survivors", "p0"):
            xs = [a - b for a, b in (v["variants"][j][name] for j in v["variants"]) if a is not None and b is not None]
            L.append(f"      flow variant {name} (descriptive): x̄ {_f(sum(xs) / len(xs) if xs else None)} over {len(xs)} seeds")
        for k in FAUNAS:
            ss = [v["s_summary"][j][k] for j in sorted(v["s_summary"])]
            L.append(f"      S {k} (descriptive): alive at 299 {_f(_mean([d['alive299'] for d in ss]), '{:.1f}')},"
                     f" births {_f(_mean([d['births'] for d in ss]), '{:.1f}')} and deaths {_f(_mean([d['deaths'] for d in ss]), '{:.1f}')}"
                     f" (starved {_f(_mean([d['starved'] for d in ss]), '{:.1f}')}, aged {_f(_mean([d['aged'] for d in ss]), '{:.1f}')}) in 240-299,"
                     f" extinct on {sum(1 for d in ss if d['extinct_season'] is not None)} seeds"
                     f" (seasons {', '.join(str(d['extinct_season']) for d in ss if d['extinct_season'] is not None) or '-'}),"
                     f" mean_lifetime_score {_f(_mean([d['mls'] for d in ss]), '{:.3f}')},"
                     f" food {_f(_mean([d['food'] for d in ss]), '{:.3f}')} work {_f(_mean([d['work'] for d in ss]), '{:.1f}')}"
                     f" path {_f(_mean([d['path'] for d in ss]), '{:.2f}')} (per member-season)")
        if v["y_m"]:
            ls = [x for x in v["living_share"].values() if x is not None]
            L.append(f"      M share of the living, 240-299 (descriptive; O-4): {_f(_mean(ls), '{:.3f}')} over {len(ls)} seeds;"
                     f" empty world on {len(v['living_share']) - len(ls)}")
        if v["y_n"]:
            L.append("      N runs' y′ (descriptive): " + ", ".join(f"{SEED_BASE + j} ({null_kind(j)}-null) {_f(y)}" for j, y in sorted(v["y_n"].items())))
        if v["void_seeds"]:
            L.append(f"      K-SALT VOID on seeds {', '.join(str(SEED_BASE + j) for j in v['void_seeds'])} (ruled; removed from n)")
    # 5: families
    L.append("")
    L.append("## families (BH q = 0.10; Stage-1 calls provisional)")
    tested = [p for p in calls if calls[p]["income"]["p"] is not None]
    L.append(f"  income EARNS and TIE: {len(tested)} points tested; share WIN/TIE/CONTINGENT: "
             f"{sum(1 for c in calls.values() if c['share_family'])} points (O-22)")
    corr = cross_correlation({p: pts[p]["x"] for p in tested})
    L.append(f"  cross-point correlation of x (pairs with >= 3 common seeds): mean {_f(corr[0], '{:.3f}')} max {_f(corr[1], '{:.3f}')} over {corr[2]} pairs")
    if corr[0] is not None and corr[0] > 0.3:
        by_rej = by({p: calls[p]["income"]["p"] for p in tested})
        for p in tested:
            if calls[p]["income"]["call"] in ("EARNS-H", "EARNS-D") and p not in by_rej:
                L.append(f"  {p}: {calls[p]['income']['call']} holds under BH only (not under BY)")
    L.append(f"  K2 pooled over {len(all_null)} N runs: {'PASS' if k2ok else 'FAIL: the share layer is VOID for the stage'}"
             f" (mean {_f(k2m)}, t {_f(k2t, '{:+.2f}')}, p {_f(k2p, '{:.4f}')})")
    for pid, w in sorted(k2pt.items()):
        L.append(f"  K2 {pid}: {w} ({len(by_point[pid])} runs, mean {_f(sum(by_point[pid]) / len(by_point[pid]))})")
    for k in FAUNAS:
        L.append(f"  pooled null {k}-null: σ̂² {_f(pooled[k][0], '{:.4f}')}, df {pooled[k][1]}"
                 + (" (CONTINGENT's denominator)" if k == CONTINGENT_KIND else ""))
    L.append(f"  CONTINGENT: {'callable' if contingent_callable(df_null) else f'not callable (df {df_null} < {CONTINGENT_MIN_DF})'}")
    for pid in STAGE1_POINTS:
        if calls[pid]["resolving_rows"] is not None or pts[pid]["y_n"]:
            L.append(f"  RESOLVING {pid}: {calls[pid]['resolving']} (descriptive where the body call is already settled)")
    # interference and the one-world column; the CRASHED point
    L.append("")
    L.append("## one-world column and interference (M − S per fauna, S paired on the M arm's completed seeds)")
    for pid in STAGE1_POINTS:
        v = pts[pid]
        if not v["m_seeds"]:
            continue
        inter = interference(v)
        mf = [v["m_flow"][j] for j in v["m_flow"]]
        L.append(f"  {pid}: {m_row_label(pid, v['m_seeds'], crashed)}; M flow H {_f(_mean([a for a, _ in mf]))} D {_f(_mean([b for _, b in mf]))};"
                 f" interference H {_f(inter[H][0])} (n {inter[H][1]}) D {_f(inter[D][0])} (n {inter[D][1]})")
    cp = pts.get(CRASHED_POINT)
    if cp:
        y7 = [cp["y_m"][j] for j in sorted(cp["y_m"])]
        s0 = cp["s0"].get(CRASHED_SEED - SEED_BASE)
        L.append(f"  {CRASHED_POINT}: y′ at n = {len(y7)}: mean {_f(_mean(y7))} (descriptive; NOT RUN)")
        if s0 is not None and len(y7) == N_STAGE1 - 1:
            lo, hi = missingness_bound(y7, s0)
            L.append(f"  {CRASHED_POINT}: bound under arbitrary missingness on the 8-seed mean y′: [{_f(lo)}, {_f(hi)}]"
                     f" (s0 {_f(s0, '{:.3f}')} from 129001's ckpt60; empty-world convention, plan 3.3)")
        L.append(f"  {CRASHED_POINT}: income flow has no logical bound; no min/max-of-7 substitute is printed")
    # §5.3d: the regime readout on every S and M arm, per fauna, per 60-season window (seeds' mean; descriptive)
    L.append("")
    L.append("## regime (regime.py; window-local saturation / viability / alive, mean over seeds; descriptive)")
    for pid in STAGE1_POINTS:
        v = pts[pid]
        for arm, reg in (("S", v["regime_s"]), ("M", v["regime_m"])):
            if not reg:
                continue
            cells = []
            for k in FAUNAS:
                for i, (lo, _) in enumerate(REGIME_WINDOWS):
                    vals = [reg[j][k][i] for j in reg]
                    cells.append(f"{k[0]}{lo}: {_f(_mean([a for _, a, _, _ in vals]), '{:.2f}')}/{_f(_mean([b for _, _, b, _ in vals]), '{:.2f}')}"
                                 f"/{_f(_mean([c for _, _, _, c in vals]), '{:.1f}')}")
            L.append(f"  {pid} {arm} (n {len(reg)}): " + "  ".join(cells))
    # 6: map level
    L.append("")
    L.append("## M1 call table and M4 area shares (PROVISIONAL)")
    for label, group in (("G", [p for p in STAGE1_POINTS if p.endswith("-G")]), ("L", [p for p in STAGE1_POINTS if p.endswith("-L")])):
        counts = {}
        for p in group:
            counts[calls[p]["body"]] = counts.get(calls[p]["body"], 0) + 1
        inc = {}
        for p in group:
            inc[calls[p]["income"]["call"]] = inc.get(calls[p]["income"]["call"], 0) + 1
        L.append(f"  {label} ({len(group)}): body " + ", ".join(f"{k} {n} ({n / len(group):.2f})" for k, n in sorted(counts.items()))
                 + "; income " + ", ".join(f"{k} {n}" for k, n in sorted(inc.items())))
    L.append("## M5 perception map: NOT MEASURED (probe leg not read)")
    decided_share = [p for p in calls if calls[p]["body"] in ("H-WIN", "D-WIN")]
    if decided_share:
        def msign(p):
            mf = [a - b for a, b in pts[p]["m_flow"].values() if a is not None and b is not None]
            return "H" if _mean(mf) and _mean(mf) > 0 else "D"
        k = cohen_kappa([calls[p]["body"][0] for p in decided_share], [msign(p) for p in decided_share])
        L.append(f"## M6 concordance: κ(share sign, M income sign) {_f(k, '{:.3f}')} over {len(decided_share)} points")
    else:
        L.append("## M6 concordance: no decided share call")
    L.append("## M7 monotonicity of x̄ along the Stage-1 rows (points with an estimate at n >= 2; gaps printed as --)")

    def est(r):
        return calls[r]["income"]["mean"] if calls[r]["income"]["p"] is not None else None
    rows7 = [(f"price row c{c} {L_} {s}", [f"c{c}-p{p}-{L_}-{s}" for p in PRICES]) for c in CLUTTERS for L_ in LAYOUTS
             for s in ("G", "L")] + [(f"clutter row p{p} {L_} G", [f"c{c}-p{p}-{L_}-G" for c in CLUTTERS]) for p in PRICES for L_ in LAYOUTS]
    for name, row in rows7:
        if all(r in calls for r in row):
            vals = [est(r) for r in row]
            n = sign_changes(vals)
            L.append(f"  {name}: {n} sign changes" + (" (more than one: listed)" if n > 1 else "")
                     + f" [{' '.join(_f(x) for x in vals)}]")
    seeds = [(p, x) for p in hab for x in pts[p]["x"].values()]
    model = world_model(seeds)
    rej, ps = map_holm(model)
    t1 = t1_state(model, rej)
    L.append("## M2 (income, registered Stage-1 fit) and T1–T3; Holm with T4 NOT MEASURED at p = 1")
    L.append(f"  habitable points {len(hab)}, seeds {len(seeds)}; dropped terms: {', '.join(model['dropped']) or 'none'}; status {model['status']}"
             + (f" ({model['why']})" if model.get("why") else ""))
    if model.get("fit") is not None:
        names = ["intercept"] + [TERM_NAMES[t] for t in model["keep"]]
        for i, n in enumerate(names):
            b, se = float(model["fit"]["beta"][i]), math.sqrt(float(model["fit"]["cov"][i, i]))
            L.append(f"  {n}: {b:+.4f} [{b - 1.96 * se:+.4f}, {b + 1.96 * se:+.4f}]")
    for name in ("T1", "T2", "T3"):
        L.append(f"  {name}: " + ("NOT TESTABLE (p = 1 in Holm)" if model.get(name) is None else
                                  f"stat {model[name][0]:.3f}, p {ps[name]:.4g}") + (" REJECTED" if name in rej else ""))
    L.append(f"  T1 state for §8: {t1}")
    share_seeds, g0c = [], {}
    for p, v in pts.items():
        if v["m_seeds"] and v["y_m"]:
            try:
                g0c[p] = float(cen["points"].get(p, ("--", "--"))[1])
            except ValueError:
                continue
            share_seeds += [(p, share_logit_change(y, v["s0"][j])) for j, y in v["y_m"].items() if j in v["s0"]]
    smodel = world_model(share_seeds, g0c)
    L.append(f"## M2 share model (secondary, descriptive at Stage 1; points with an M arm, census g0 a covariate; the CRASHED"
             f" point at n = 7): status {smodel['status']}" + (f" ({smodel['why']})" if smodel.get("why") else "")
             + f"; dropped {', '.join(smodel['dropped']) or 'none'}; share Wald T1 (net of g0, outside Holm): "
             + (f"χ² {smodel['T1'][0]:.3f}, df {smodel['T1'][1]}, p {smodel['T1'][2]:.4g}" if smodel.get("T1") else "NOT TESTABLE"))
    m3 = {}
    for p in hab:
        c, pr, L_, s = parse_point(p)
        for x in pts[p]["x"].values():
            m3.setdefault((c, L_, s), ([], []))
            m3[(c, L_, s)][0].append(pr)
            m3[(c, L_, s)][1].append(x)
    m3 = {row: fieller(*v) for row, v in m3.items() if len(set(v[0])) >= 2}
    L.append("## M3 break-evens (per-row OLS of x on p, Fieller 95%)")
    for row, f in sorted(m3.items()):
        L.append(f"  {row}: p* {_f(f.get('p_star'), '{:.4f}')} {f['kind']}" + (f" [{f['lo']:.4f}, {f['hi']:.4f}]" if f["kind"] == "bounded" else ""))

    def corroborate(pid):
        c, _, L_, s = parse_point(pid)
        return m3_corroborates(m3.get((c, L_, s), {}))
    vpts = {p: {"body": calls[p]["body"], "income": calls[p]["income"]["call"], "lever": None, "vd": False,
                "m_arm": bool(pts[p]["m_seeds"]), "resolving": calls[p]["resolving"]} for p in STAGE1_POINTS}
    verdict = verdicts(vpts, t1, corroborate)
    L.append("")
    L.append("## §8: PROVISIONAL: Stage-1 calls only; not a verdict (COORD-RULING-512 R1 + R2 + R3)")
    L.append(f"  {verdict[0]}" + (f"; also holding: {', '.join(verdict[1:])}" if len(verdict) > 1 else ""))
    for label, kw in (("EARNS at habitable points only", {"earns_habitable_only": True}),
                      ("verdict 5 ignoring EARNS-TIE", {"v5_ignores_tie": True})):
        L.append(f"  NON-REGISTERED, descriptive only ({label}): {', '.join(verdicts(vpts, t1, corroborate, **kw))}")
    L.append("  perception verdicts: NOT MEASURED; LEVER not evaluated (every EARNS call counted with that caveat)")
    # 7: refinement
    stats = {p: {"body": calls[p]["body"], "resolving": calls[p]["resolving"],
                 "income": {**calls[p]["income"]}, "share": calls[p]["share"]} for p in STAGE1_POINTS}
    sel, rows = ra_select(stats, c1_candidates(census_txt))
    L.append("")
    L.append("## R-A (≤ 16 new points; G block first, then L: L pairs refine only if fewer than 16 G pairs fire)")
    for r in rows:
        if r["fires"]:
            L.append(f"  {r['mid']:14s} {r['source']} pair {r.get('a')} / {r.get('b')} layer {r['layer']} sign {r['sign']} calls {r['calls']}"
                     f" |Δt| {_f(r['dt'], '{:.3f}')}" + (" (no Stage-1 pair)" if r.get("no_stage1_pair") else ""))
    L.append(f"  selected: {', '.join(sel) or 'none'}")
    rb = rb_select(stats)
    rb_lit = rb_select(stats, literal=True)
    ch = rb_core_h(len(rb))
    L.append(f"## R-B (COORD-RULING-512 R4, DATA-INFORMED): {len(rb)} points; S arms {ch[0]:.0f} / {ch[1]:.0f} core-h; needs its own owner GO")
    L += [f"  {p}: CP {_f(c, '{:.3f}')}" for p, c in rb]
    L.append(f"  the literal list (body call UNDECIDED or CONTINGENT; not the registered reading): {', '.join(p for p, _ in rb_lit) or 'empty'}")
    # SHOULD 5 (T3) and the census layer
    L.append("")
    L.append("## founding beside the census (AMENDMENT-FOUNDING T3): census FOUNDING-FAIL (unscreened) | Stage 1 alive at 59 (screened)")
    for pid in STAGE1_POINTS:
        v = pts[pid]
        L.append(f"  {pid:14s} census FF H {'yes' if pid in cen['ff'][H] else 'no'} D {'yes' if pid in cen['ff'][D] else 'no'}"
                 f" | Stage 1 H alive at 59 on {sum(1 for a, _ in v['merge'].values() if a)} of {v['n']}, D on {sum(1 for _, b in v['merge'].values() if b)} of {v['n']}")
    L.append("## census layer at the 114 points never run at Stage 1 (the only habitability proxy; 60-season limit)")
    for pid, (sat, g0) in sorted(cen["points"].items()):
        if pid not in STAGE1_POINTS:
            L.append(f"  {pid:14s} FF H {'yes' if pid in cen['ff'][H] else 'no'} D {'yes' if pid in cen['ff'][D] else 'no'}"
                     f" | saturation 30-59 {sat} | census g0 {g0}")
    L.append("")
    L += scorecard(calls, model, rej, m3, verdict)
    L.append("")
    L.append("# exclusions: none beyond K-SALT VOID (ruled), validity (plan 3.1) and CRASHED; nothing winsorised or re-weighted")
    return L


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs)) if xs else None


RULINGS_CITED = os.path.join(HERE, "RULINGS-CITED.md")


def go_ids(path: str = None) -> set:
    """The go IDs the coordinator has issued, as ``GO-ID: <id>`` lines in RULINGS-CITED.md (adversary NOTE 7)."""
    path = path or RULINGS_CITED
    if not os.path.exists(path):
        return set()
    ids = {line.split(":", 1)[1].strip() for line in open(path) if line.startswith("GO-ID:")}
    return {i for i in ids if i}  # an empty GO-ID line never passes (fix-check FC-NOTE 1)


def ruled_ksalt_void(path: str = None) -> dict:
    """{point: [j]} from ``KSALT-VOID: <point> <seed>`` lines in RULINGS-CITED.md: the K-SALT VOID seeds the coordinator
    has ruled (fix-check FC-SHOULD 2).  A malformed line is a HELP."""
    out, path = {}, path or RULINGS_CITED
    if not os.path.exists(path):
        return out
    for line in open(path):
        if not line.startswith("KSALT-VOID:"):
            continue
        parts = line.split(":", 1)[1].split()
        if len(parts) != 2 or parts[0] not in STAGE1_POINTS or not parts[1].isdigit() \
                or int(parts[1]) - SEED_BASE not in SEEDS:
            raise ReadoutHelp(f"malformed KSALT-VOID line in RULINGS-CITED.md: {line.strip()!r}: HELP")
        out.setdefault(parts[0], []).append(int(parts[1]) - SEED_BASE)
    return out


# -- main ---------------------------------------------------------------------------------------------------------- #

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("step", choices=("integrity", "readout"))
    ap.add_argument("--go", help="the coordinator's go ID, as listed (GO-ID:) in RULINGS-CITED.md (required)")
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args(argv)
    if not a.go or a.go.strip() not in go_ids():
        print("refused: the Stage-1 readout runs only after READOUT-PLAN.md is committed, reviewed and the coordinator"
              " issues a go whose ID is listed in RULINGS-CITED.md (--go ID).  Nothing was read.", file=sys.stderr)
        return 9
    if local_quarantine_refs(a.root):
        print("refused: a local ref names the quarantined unit (a bare fetch ran): HELP.  Nothing was read.", file=sys.stderr)
        return 9
    if a.step == "integrity":
        import resumed
        try:
            ok, lines, _ = integrity(a.root, default_reader(), remote_labels(a.root), resumed.written_twice,
                                     lambda lab: fetch_label(lab, a.root), local_quarantine_refs(a.root))
        except ReadoutHelp as e:
            print(f"HELP: {e}", file=sys.stderr)
            return 1
        text = f"# RBT-129 Stage 1 integrity (READOUT-PLAN.md section 2); go: {a.go}\n" + "\n".join(lines) + \
               f"\nINTEGRITY {'PASS' if ok else 'FAIL: HELP; nothing further is read'}\n"
        with open(os.path.join(HERE, "integrity.txt"), "w") as f:
            f.write(text)
        print(text)
        return 0 if ok else 1
    ipath = os.path.join(HERE, "integrity.txt")
    if not os.path.exists(ipath) or not open(ipath).read().rstrip().endswith("INTEGRITY PASS") or f"go: {a.go}" not in open(ipath).read():
        print("refused: integrity.txt does not read INTEGRITY PASS under this go.  Nothing was read.", file=sys.stderr)
        return 9
    try:
        lines = readout(a.root, void_seeds=ruled_ksalt_void())
    except ReadoutHelp as e:
        print(f"HELP: {e}", file=sys.stderr)
        return 1
    with open(os.path.join(HERE, "stage1_readout.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
