#!/usr/bin/env python3
"""RBT-129 Stage-1 S silent-corruption scan (OWNER-DECISIONS-2026-10-09 item 1; COORD-RULING-520 D2; READOUT-STAGE1-
CORRECTIONS A7; OVERFLOW-RULE §6).  Nothing here launches anything.

    /opt/rbt129-venvs/instr/bin/python runs/RBT-129/s-corruption-scan/sscan.py emit [--hosts 10]  -> lanes/SSCAN/
    /opt/rbt129-venvs/instr/bin/python runs/RBT-129/s-corruption-scan/sscan.py run-lane runs/RBT-129/lanes/SSCAN/hostK-laneL.jsonl
    /opt/rbt129-venvs/instr/bin/python runs/RBT-129/s-corruption-scan/sscan.py scan-report        -> scan_report.txt

**What it covers.**  The M/N scan (``stages.py scan-emit``) replayed every Stage-1 M and N fork from its stock ckpt60,
so it says nothing about seasons 0-59, and nothing about the S arms: A7 and OVERFLOW-RULE §6.1 leave **every Stage-1 S
arm (seasons 0-299) and the S60 phase upstream of every Stage-1 M and N (S's seasons 0-59) UNSCANNED**.  This scan
replays each of them on the instrumented build (c), the chain Stage 1 ran, and compares it byte for byte with what
Stage 1 stored:

- **The replay set** is pinned by the committed Stage-1 emission: every unit with an ``S`` resume job in
  ``lanes/1/*.jsonl`` (``stage1_s_chains``), 36 points x seeds 129001-129008 = **288 S chains**.  None is excluded: the
  one CRASHED Stage-1 unit is an M arm (``1/c2-p030-U-G/129001/M``); its S is replayed and its M is never touched.
- **The chain per unit**, as Stage 1 ran it, on the build: ``fresh S60`` (seasons 0-59, at the seed's screened salts
  from ``lanes/1/launch.txt``), ``snapshot ckpt60``, ``resume S`` to 300, into ``s-corruption-scan/replay/<point>/
  <seed>/{S, ckpt60}``.  Stage 1's seed 129001 adopted the census's S 0-59 (F7, salts (0, 0)); its replay runs those
  seasons fresh at (0, 0), as Stage 2a's O-2 re-simulation does.  A pre-merge extinction takes the chain's own path
  (``stages``: EXTINCT.txt, the resume skipped).
- **Two comparisons per unit** (``sscancmp``), each against the stored run restored from its own checkpoint branch:
  ``ckpt60-cmp`` (the replay's ckpt60 against ``ckpt/rbt-129-stage1-<point>-<seed>-ckpt60``: the S60 phase, the
  state every Stage-1 M and N forked from) and ``S-cmp`` (the replay's S at 300 against
  ``ckpt/rbt-129-stage1-<point>-<seed>-S``: seasons 0-299).  Every file is compared byte for byte except logs and
  provenance (``SKIP``); ``config.json`` is compared bar ``workers`` (``stages._arm_config``), as ``adopt_census`` and
  Stage 2a's ``s60cmp`` do, because a fresh run's worker count is the host's.
- **States**, the M/N scan's (OVERFLOW-RULE §6.1), from the replay's own EPA log: **CLEAN (seasons 0-299)** /
  **OVERFLOWED** / **UNLOGGED** for S, and **CLEAN (seasons 0-59)** / **OVERFLOWED** / **UNLOGGED** for the S60 phase;
  verdicts **IDENTICAL** / **DIFFER** / **NO-REFERENCE**.

**Why it lives outside the pinned trees** (NOTE 17).  It changes nothing under ``runs/RBT-129/launch``, ``scripts``
or ``rabbitstew``, and it imports nothing from Stage 2 (``s2lanes``, ``stage2_readout``), so the P-1 fix and a 2b
launch can merge while it runs.  It imports ``stages`` and reuses its job runner, guards and emitter unchanged; its one
override is ``stages.CONTINUATION_PREFIXES`` gaining ``"SSCAN/"`` in its own process, so that every replay runs as a
continuation (the build check, ``epa_ecology.py``, the EPA log, ``check_not_crashed``).

**The lane gates** (``run_lane``), in order: the host, the build and the pinned trees (``stages.check_host``); the
pinned modules are this checkout's (``check_modules``); this file is the launch's, by blob, and committed
(``check_code``); **the scan's GO** on the merged base after a narrow fetch that must succeed (``check_go``,
``LOCKS.md``); the lane file equal to its slice of the emission (``check_emission``); the blocks and salts
(``stages``); every job a scan job of this emission that touches no quarantined label (``check_lane_sscan``).

**No-peek.**  A runner relays start and done lines, each comparison's verdict line (verdict, state, overflow count),
EPA counts, refusals and exit codes only.  ``SSCAN.txt`` (the differing file names, the EPA summary) stays on the
replay's checkpoint branch.  ``scan-report`` writes counts only, and names a unit only when it is DIFFER, NO-REFERENCE,
OVERFLOWED or UNLOGGED.
"""
from __future__ import annotations

import argparse
import fcntl
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
import blocks  # noqa: E402,F401  (pinned module: checked by check_modules)
import stages  # noqa: E402

NAME = "SSCAN"                     # lanes/SSCAN, and the job-name prefix
PREFIX = NAME + "/"
SCAN_DIR = "s-corruption-scan"     # runs/RBT-129/s-corruption-scan/replay/<point>/<seed>/{S, ckpt60}
STAGE1_LANES = "1"
#: the code a scan lane executes outside the pinned trees, pinned by blob in launch.txt (``code:<path>``)
CODE_FILES = ("runs/RBT-129/s-corruption-scan/sscan.py",)
LOCKS_REL = os.path.join("runs", "RBT-129", SCAN_DIR, "LOCKS.md")
GO_TAG, GO_VALUE = "GO-ID-SSCAN:", "RBT129-SSCAN-GO-1"
SSCAN_FILE = "SSCAN.txt"
#: not compared byte for byte: the M/N scan's skip list (logs, provenance, the replay's own EPA log), the verdict, and
#: config.json, which is compared separately bar ``workers``
SKIP = stages.SCAN_SKIP + ("config.json", SSCAN_FILE)
#: the comparisons: job tag -> the stored arm it compares against, and the seasons its state covers
CMP = {"ckpt60-cmp": ("ckpt60", range(0, stages.MERGE)), "S-cmp": ("S", range(0, stages.SEASONS))}
STATE_LABEL = {"ckpt60-cmp": "CLEAN (seasons 0-59)", "S-cmp": "CLEAN (seasons 0-299)"}
#: the planning rates of every RBT-129 scan and continuation estimate (core-s per arm-season; ``stages.MN_CORE_S``)
CORE_S = stages.MN_CORE_S


def with_sscan_prefix() -> None:
    """The one override: scan jobs are continuations in this process (the build, the EPA wrapper, the crash check)."""
    if PREFIX not in stages.CONTINUATION_PREFIXES:
        stages.CONTINUATION_PREFIXES = stages.CONTINUATION_PREFIXES + (PREFIX,)


# -- the replay set and the units ----------------------------------------------------------------------------------- #

def stage1_s_chains(root: str = RUNS) -> list:
    """[(point, seed)]: every Stage-1 S chain, read from the committed Stage-1 emission (each unit with an ``S`` resume
    job in ``lanes/1/*.jsonl``), in point and seed order."""
    d = os.path.join(root, "lanes", STAGE1_LANES)
    out = set()
    for f in sorted(os.listdir(d)):
        if f.endswith(".jsonl"):
            for line in open(os.path.join(d, f)):
                if line.strip():
                    j = json.loads(line)
                    if j["job"] == "resume" and j["name"].startswith("1/") and j["name"].endswith("/S"):
                        _, pid, sd, _ = j["name"].split("/")
                        out.add((pid, int(sd)))
    return sorted(out)


def stage1_salts(root: str = RUNS) -> tuple:
    """(salts, launch): Stage 1's screened salts and flags (``lanes/1/launch.txt``)."""
    launch = stages.read_launch(os.path.join(root, "lanes", STAGE1_LANES, "launch.txt"))
    return stages._salts_line(launch["salts"]), launch


def sscan_units(root: str = RUNS) -> list:
    """One unit per Stage-1 S chain: S60 fresh at the seed's salts, ckpt60, S to 300 (the replay), then ``ckpt60-cmp``
    and ``S-cmp`` against the stored Stage-1 runs.  Seed 129001 (the census adoption, F7) must have salts (0, 0)."""
    salts, _ = stage1_salts(root)
    units = []
    for pid, sd in stage1_s_chains(root):
        s, t = salts[sd]
        if sd == stages.seed(stages.RESUME_SEED) and (s, t) != (0, 0):
            stages._refuse(f"{pid}/{sd}: salts {(s, t)}, not (0, 0): the census adoption's replay needs its salts", 8)
        d = os.path.join(root, SCAN_DIR, "replay", pid, str(sd))
        st1 = os.path.join(root, "stage1", pid, str(sd))
        name = f"{PREFIX}{pid}/{sd}"
        jobs = [{"job": "fresh", "name": f"{name}/S60", "point": pid, "seed": sd, "dir": f"{d}/S",
                 "seasons": stages.MERGE, "extra": stages.salts_argv(s, t), "cost": stages.MERGE},
                {"job": "snapshot", "name": f"{name}/ckpt60", "src": f"{d}/S", "dir": f"{d}/ckpt60", "seed": sd, "cost": 0},
                {"job": "resume", "name": f"{name}/S", "dir": f"{d}/S", "seed": sd, "seasons": stages.SEASONS,
                 "cost": stages.SEASONS - stages.MERGE},
                {"job": "sscancmp", "name": f"{name}/ckpt60-cmp", "dir": f"{d}/ckpt60", "ref": f"{st1}/ckpt60", "seed": sd,
                 "cost": 0},
                {"job": "sscancmp", "name": f"{name}/S-cmp", "dir": f"{d}/S", "ref": f"{st1}/S", "seed": sd, "cost": 0}]
        units.append({"stage": NAME, "seed": sd, "jobs": jobs})
    return units


def arm_seasons(units: list) -> int:
    return sum(j["cost"] for u in units for j in u["jobs"])


def core_h(units: list) -> tuple:
    """The arithmetic at the planning rates.  Not a bound: the rates were not measured on build (c) and exclude restart
    rework (PLAN.md §7: ~560-1,150 core-h, likely near the top).  A pre-merge extinction skips its resume."""
    return tuple(arm_seasons(units) * c / 3600 for c in CORE_S)


# -- the comparison --------------------------------------------------------------------------------------------- #

def scan_files(d: str) -> dict:
    out = {}
    for base, _, files in os.walk(d):
        for n in files:
            if n in SKIP or n.startswith(".rbt129-done-") or n.startswith("epa_overflow"):
                continue
            out[os.path.relpath(os.path.join(base, n), d)] = os.path.join(base, n)
    return out


def verdict(stored: str, replay: str) -> tuple:
    """(IDENTICAL | DIFFER, lines): config.json equal bar ``workers``, and every other compared file byte for byte.
    The lines name files, never contents."""
    lines = []
    if os.path.exists(os.path.join(stored, "config.json")) or os.path.exists(os.path.join(replay, "config.json")):
        try:
            same = stages._arm_config(stored) == stages._arm_config(replay)
        except (OSError, ValueError):
            same = False
        if not same:
            lines.append("DIFFERS: config.json (bar workers)")
    a, b = scan_files(stored), scan_files(replay)
    lines += [f"only in {'stored' if n in a else 'replay'}: {n}" for n in sorted(set(a) ^ set(b))]
    for n in sorted(set(a) & set(b)):
        if open(a[n], "rb").read() != open(b[n], "rb").read():
            lines.append(f"DIFFERS: {n}")
    return ("IDENTICAL" if not lines else "DIFFER"), [f"{len(set(a) & set(b))} files compared"] + lines


def phase_state(info: dict, seasons: range, label: str) -> str:
    """The scan's state of the replay's seasons ``seasons`` (OVERFLOW-RULE §6.1), from ``epa_ecology.read_log``:
    OVERFLOWED when an overflow is logged in them (or before an attempt's first season line, conservatively);
    UNLOGGED (HELP, defaulted to OVERFLOWED by the rule's §4.6) when the log cannot vouch for one of them; else
    ``label`` (CLEAN for those seasons only)."""
    per = info["seasons"]
    if any(v["overflow"] for s, v in per.items() if s is None or s in seasons):
        return "OVERFLOWED"
    if info["unlogged"] or any(s not in per for s in seasons):
        return "UNLOGGED"
    return label


def seasons_ran(replay_s: str, cover: range) -> range:
    """The seasons of ``cover`` the replay's S ran: all of them, or up to its pre-merge extinction (its state's season;
    read here only to bound the log check, never printed)."""
    try:
        at = int(json.load(open(os.path.join(replay_s, "state.json")))["season"])
    except (OSError, ValueError, KeyError):
        return cover
    return range(cover.start, min(cover.stop, at))


def sscan_compare(job: dict, d: str) -> str:
    """One comparison: the stored Stage-1 run (restored from its own branch; a quarantined label is refused) against the
    replay, into ``d/SSCAN.txt`` (kept on the replay's branch, uncommitted), with the replay's EPA summary for the
    seasons it covers.  Prints the verdict, the state and the overflow count only.  Returns the file's first line."""
    import epa_ecology
    import mjbuild

    tag = job["name"].rsplit("/", 1)[1]
    arm, cover = CMP[tag]
    stored = job["ref"]
    for x in (stored, d):
        if stages.is_quarantined(stages._label(x)):
            stages._refuse(f"{job['name']}: a quarantined run is never read (RULING.md item 3)", 4)
    if not stages._done(d, arm):
        raise SystemExit(f"{job['name']}: the replay {stages.rel_or_abs(d)} is not done; run its chain first")
    replay_s = os.path.join(os.path.dirname(d), "S")
    if not stages._done(replay_s, "S"):
        raise SystemExit(f"{job['name']}: the replay's S is not done; run its chain first")
    stages._restore(stored)
    if not stages._done(stored, arm):
        word, lines = "NO-REFERENCE", [f"{stages.rel_or_abs(stored)} has no .rbt129-done-{arm} marker: not compared"]
    else:
        word, lines = verdict(stored, d)
    info = epa_ecology.read_log(os.path.join(replay_s, mjbuild.EPA_LOG))
    ran = seasons_ran(replay_s, cover)
    state = phase_state(info, ran, STATE_LABEL[tag])
    over = sum(len(v["overflow"]) for s, v in info["seasons"].items() if s is None or s in ran)
    unit = job["name"][len(PREFIX):]
    text = (f"SSCAN {word}: {unit} replayed on the instrumented build against ckpt/{stages._label(stored)}\n"
            f"  state: {state}; overflow {over}\n" + "".join(f"  {x}\n" for x in lines)
            + f"  epa (whole replay): near(>={mjbuild.NEAR}) {info['near']} max_horizon {info['max_nedges']}"
              f" epa_iterations {info['epa_iterations']} starts {info['starts']} bad_lines {info['bad_lines']}"
              f" unlogged {info['unlogged']}\n")
    with open(os.path.join(d, SSCAN_FILE), "w") as f:
        f.write(text)
    print(f"{job['name']}: SSCAN {word}; {state}; EPA overflow {over}", flush=True)
    return text.splitlines()[0]


def run_job(job: dict) -> None:
    """``sscancmp`` here (skipped once its marker is on its branch); every replay job through ``stages.run_job``."""
    if job["job"] != "sscancmp":
        stages.run_job(job)
        return
    d, tag = job["dir"], job["name"].rsplit("/", 1)[1]
    # the probe the M/N scan's scancmp uses: a replay directory here (its state.json) is never restored over, so a
    # snapshot older than a final save still in flight cannot replace it; a lost one comes back with its marker
    stages._restore(d)
    if stages._finished(d, tag):
        return
    stages._finish(d, tag, sscan_compare(job, d))


# -- the report --------------------------------------------------------------------------------------------------- #

def scan_report(root: str = RUNS) -> str:
    """COUNTS ONLY: totals of each verdict and state, for the S60 phase (``ckpt60-cmp``) and for S (``S-cmp``); a unit is
    named only when DIFFER, NO-REFERENCE, OVERFLOWED or UNLOGGED.  A comparison not done is PENDING (counted).  No EPA
    figure, season, geom pair, near miss or file name is copied: they stay in each replay's SSCAN.txt, on its branch."""
    units = sscan_units(root)
    totals, named = {"ckpt60-cmp": {}, "S-cmp": {}}, []
    for u in units:
        for j in u["jobs"]:
            if j["job"] != "sscancmp":
                continue
            d, tag = j["dir"], j["name"].rsplit("/", 1)[1]
            stages._restore(d, SSCAN_FILE)
            t = totals[tag]
            if not stages._done(d, tag) or not os.path.exists(os.path.join(d, SSCAN_FILE)):
                t["PENDING"] = t.get("PENDING", 0) + 1
                continue
            first, second = open(os.path.join(d, SSCAN_FILE)).read().splitlines()[:2]
            word = first.split(":")[0].split()[1]
            state = second.split("state: ", 1)[1].split(";")[0]
            over = second.rsplit("overflow ", 1)[1]
            for k in (word, state):
                t[k] = t.get(k, 0) + 1
            if word != "IDENTICAL" or not state.startswith("CLEAN"):
                named.append(f"  {j['name'][len(PREFIX):]}: {word}; {state}; overflow {over}")
    head = ["# RBT-129 Stage-1 S silent-corruption scan (OWNER-DECISIONS-2026-10-09 item 1; A7; OVERFLOW-RULE §6): counts"
            " only",
            f"# every Stage-1 S chain of lanes/{STAGE1_LANES} ({len(units)}), replayed from season 0 on the instrumented build"
            " (S60, ckpt60, S to 300) and compared byte for byte with its stored ckpt60 and S branches",
            "# S60 phase (ckpt60-cmp): seasons 0-59, upstream of every Stage-1 M and N; S (S-cmp): seasons 0-299",
            "# CLEAN = no overflow logged in those seasons and a complete log for them; excluded: none (the CRASHED unit is"
            " an M arm, never touched)",
            f"# compared: every file but {', '.join(SKIP)}, kept EPA logs and done-markers; config.json bar workers."
            " Details stay on the replay branches", ""]
    body = []
    for tag, title in (("ckpt60-cmp", "S60 phase (seasons 0-59)"), ("S-cmp", "S (seasons 0-299)")):
        body.append(f"{title}: " + (", ".join(f"{k} {v}" for k, v in sorted(totals[tag].items())) or "none"))
    body += ["", "named (DIFFER, NO-REFERENCE, OVERFLOWED or UNLOGGED only):"] + (named or ["  none"])
    return "\n".join(head + body + ["", f"units: {len(units)}"]) + "\n"


# -- the emission --------------------------------------------------------------------------------------------------- #

def _git(root: str, *a) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True)


def code_pins(root: str = ROOT) -> dict:
    return {f"code:{p}": _git(root, "rev-parse", f"HEAD:{p}").stdout.strip() for p in CODE_FILES}


def emit(root: str = RUNS, hosts: int = 10) -> list:
    """Write ``lanes/SSCAN/`` (not launched).  Refused (exit 9) unless this process runs the registered build, and
    (exit 5) unless the trees and code the lanes pin are committed."""
    import mjbuild

    stages.check_continuation_build()
    for t in CODE_FILES + stages.PINNED_TREES:
        if stages._git("status", "--porcelain", "--", t):
            stages._refuse(f"uncommitted changes under {t}: emit from a committed tree", 5)
    salts, launch1 = stage1_salts(root)
    units = sscan_units(root)
    lo, hi = core_h(units)
    extra = {stages.BUILD_KEY: mjbuild.BUILD_LINE, "go": GO_VALUE,
             "stage": "Stage-1 S silent-corruption scan (OWNER-DECISIONS-2026-10-09 item 1): every Stage-1 S chain of"
                      " lanes/1 replayed from season 0 on the instrumented build, compared byte for byte with its stored"
                      " ckpt60 and S branches",
             "salts": launch1["salts"], "hosts": hosts, "units": len(units),
             "core_h": f"~560-1,150, likely near the top ({lo:.0f} / {hi:.0f} at {CORE_S[0]} / {CORE_S[1]} core-s over"
                       f" {arm_seasons(units)} arm-seasons; rates not measured on build (c); excludes restart rework)",
             **code_pins()}
    return stages.emit_lanes(NAME, units, hosts, root, launch1["fair"].split(), launch1["eat"].split(), extra)


def lane_jobs_emitted(path: str, launch: dict, root: str = RUNS) -> list:
    """The jobs ``emit`` writes to ``path`` (``hostK-laneL.jsonl``), rebuilt now from the committed Stage-1 emission at
    the launch's host count."""
    import re

    m = re.fullmatch(r"host(\d+)-lane([01])\.jsonl", os.path.basename(path))
    if not m or "hosts" not in launch:
        stages._refuse(f"{path}: not a lane file of an SSCAN launch with a hosts line: re-emit", 4)
    lanes = stages.layout(sscan_units(root), int(launch["hosts"]))
    k = 2 * int(m.group(1)) + int(m.group(2))
    if k >= len(lanes):
        stages._refuse(f"{path}: no such lane in the emission ({len(lanes)} lanes)", 4)
    worlds = os.path.join(root, "worlds")
    return [{kk: (stages.rel(v) if kk in stages.PATH_KEYS else v) for kk, v in {**j, "worlds": worlds}.items()}
            for u in lanes[k] for j in u["jobs"]]


# -- the lane gates ------------------------------------------------------------------------------------------------- #

#: the modules a lane imports from the pinned trees, and where each must come from (a PYTHONPATH entry would otherwise
#: load them from elsewhere, unseen by ``check_host``'s tree pins)
PINNED_MODULES = {"stages": "runs/RBT-129/launch/stages.py", "blocks": "runs/RBT-129/launch/blocks.py",
                  "mjbuild": "runs/RBT-129/launch/mjbuild.py", "epa_ecology": "runs/RBT-129/launch/epa_ecology.py",
                  "rabbitstew": "rabbitstew/__init__.py"}


def check_modules(modules: dict = None, root: str = ROOT) -> None:
    """Refuse (exit 5) unless the pinned modules (imported here if not yet) are this checkout's own files."""
    import importlib

    if modules is None:
        modules = {name: importlib.import_module(name) for name in PINNED_MODULES}
        modules.update({n: m for n, m in list(sys.modules.items()) if n.startswith("rabbitstew.")})
    pkg = os.path.join(os.path.realpath(root), "rabbitstew") + os.sep
    for name, mod in sorted(modules.items()):
        f = os.path.realpath(getattr(mod, "__file__", None) or "")
        want = PINNED_MODULES.get(name)
        ok = f == os.path.realpath(os.path.join(root, want)) if want else f.startswith(pkg)
        if not ok:
            stages._refuse(f"the module {name} is loaded from {f or '(no file)'}, not this checkout's"
                           f" {want or 'rabbitstew/'}: unset PYTHONPATH (the lane runs the pinned trees only)", 5)


def loaded_code(root: str = ROOT) -> set:
    """The repository paths of this process's code under runs/ outside ``stages.PINNED_TREES``."""
    runs = os.path.join(root, "runs") + os.sep
    files = {__file__} | {m.__file__ for m in list(sys.modules.values())
                          if isinstance(getattr(m, "__file__", None), str) and os.path.abspath(m.__file__).startswith(runs)}
    rels = {os.path.relpath(os.path.abspath(f), root) for f in files}
    return {r for r in rels if not any(r == t or r.startswith(t + "/") for t in stages.PINNED_TREES)}


def check_code(launch: dict, root: str = ROOT, loaded=None) -> None:
    """The code the lane executes outside the pinned trees is the launch's, by blob, and committed (exit 5)."""
    pins = {k[len("code:"):]: v for k, v in launch.items() if k.startswith("code:")}
    if set(pins) != set(CODE_FILES):
        stages._refuse(f"launch.txt pins {sorted(pins)}, not {sorted(CODE_FILES)}: re-emit", 5)
    extra = (loaded_code(root) if loaded is None else set(loaded)) - set(CODE_FILES)
    if extra:
        stages._refuse(f"this process runs code outside the pinned trees that launch.txt does not pin: {sorted(extra)}", 5)
    for p, blob in sorted(pins.items()):
        now = _git(root, "rev-parse", f"HEAD:{p}").stdout.strip()
        if now != blob:
            stages._refuse(f"HEAD:{p} is {now or '(absent)'}, not the launch's {blob}: check out the launch commit, or"
                           " re-emit", 5)
    dirty = _git(root, "status", "--porcelain", "--", *CODE_FILES).stdout.strip()
    if dirty:
        stages._refuse("uncommitted changes to the lane's code:\n" + dirty, 5)


def go_open(text: str) -> bool:
    """Exactly one ``GO-ID-SSCAN: RBT129-SSCAN-GO-1`` line (an empty or duplicated GO line is not open)."""
    vals = [x.split(":", 1)[1].strip() for x in text.splitlines() if x.startswith(GO_TAG)]
    return vals == [GO_VALUE]


def fetch_base(base: str = stages.RULE_BASE, root: str = ROOT) -> str:
    """A narrow fetch of the base; a failed fetch refuses (exit 10): the GO is read from the merged base only."""
    r = _git(root, "fetch", "-q", "origin", f"+refs/heads/{base}:refs/remotes/origin/{base}")
    if r.returncode != 0:
        stages._refuse(f"the narrow fetch of origin/{base} failed (exit {r.returncode}): the scan's GO is read from the"
                       " merged base only", 10)
    return f"origin/{base}"


def check_go(base: str = stages.RULE_BASE, root: str = ROOT) -> None:
    """The scan's GO (``LOCKS.md``), read from the merged base after a narrow fetch (exit 10 until it is open)."""
    rev = fetch_base(base, root)
    if not go_open(_git(root, "show", f"{rev}:{LOCKS_REL}").stdout):
        stages._refuse(f"the S scan is not authorised: {LOCKS_REL} on {rev} has no '{GO_TAG} {GO_VALUE}' line"
                       " (the coordinator opens it after the owner's decision and the adversary pass)", 10)


def check_emission(path: str, launch: dict, raw: list, want: list = None) -> None:
    """The lane file is exactly its slice of the emission, job for job and in order (exit 4)."""
    want = lane_jobs_emitted(path, launch) if want is None else want
    if raw != want:
        bad = next((i for i, (a, b) in enumerate(zip(raw, want)) if a != b), min(len(raw), len(want)))
        stages._refuse(f"{os.path.basename(path)}: not the emission's lane (first difference at job {bad + 1};"
                       f" {len(raw)} jobs, {len(want)} expected): re-emit", 4)


ALLOWED = {"S60": "fresh", "ckpt60": "snapshot", "S": "resume", "ckpt60-cmp": "sscancmp", "S-cmp": "sscancmp"}


def check_lane_sscan(jobs: list, launch: dict) -> None:
    """Every job is a scan job of this kind (``SSCAN/<point>/<seed>/<tag>``), at a seed of Stage 1, writing under the
    scan's replay tree, and touches no quarantined label (exit 4)."""
    if stages.BUILD_KEY not in launch or launch.get("go") != GO_VALUE:
        stages._refuse("launch.txt records no build or not the scan's GO: re-emit", 4)
    replay = os.path.join(RUNS, SCAN_DIR, "replay") + os.sep
    for j in jobs:
        parts = j["name"].split("/")
        if len(parts) != 4 or parts[0] != NAME or ALLOWED.get(parts[3]) != j["job"] or str(j["seed"]) != parts[2]:
            stages._refuse(f"{j['name']}: not a job of the S scan", 4)
        if not os.path.abspath(j["dir"]).startswith(replay):
            stages._refuse(f"{j['name']}: writes outside {stages.rel_or_abs(replay)}", 4)
        for k in ("dir", "src", "ref"):
            if k in j and stages.is_quarantined(stages._label(j[k])):
                stages._refuse(f"{j['name']}: touches a quarantined label (RULING.md item 3)", 4)


def run_lane(path: str, base: str = stages.RULE_BASE) -> None:
    with_sscan_prefix()
    launch = stages.read_launch(os.path.join(os.path.dirname(os.path.abspath(path)), "launch.txt"))
    stages.check_host(launch)
    check_modules()
    check_code(launch)
    check_go(base)
    raw = [json.loads(line) for line in open(path) if line.strip()]
    check_emission(path, launch, raw)
    jobs = [{k: (stages.absolute(v) if k in stages.PATH_KEYS else v) for k, v in j.items()} for j in raw]
    stages.check_lane_blocks(jobs, launch)
    stages.check_lane_salts(jobs, launch)
    check_lane_sscan(jobs, launch)
    os.makedirs(stages.LOCKS, exist_ok=True)
    for job in jobs:
        with open(os.path.join(stages.LOCKS, f"seed-{job['seed']}.lock"), "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            t0 = time.time()
            print(f"{time.strftime('%H:%M:%S')} start {job['name']}", flush=True)
            run_job(job)
            print(f"{time.strftime('%H:%M:%S')} done  {job['name']} ({(time.time() - t0) / 60:.1f} min)", flush=True)
            if job["job"] in ("fresh", "resume"):
                stages.epa_note(job)
            fcntl.flock(lock, fcntl.LOCK_UN)
    print(f"lane {os.path.basename(path)} complete: {len(jobs)} jobs")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("emit", help="write lanes/SSCAN (not launched); needs the registered build")
    e.add_argument("--hosts", type=int, default=10)
    r = sub.add_parser("run-lane", help="run one scan lane file (refused until the scan's GO is open)")
    r.add_argument("lane")
    sub.add_parser("scan-report", help="the scan's counts-only report, to s-corruption-scan/scan_report.txt")
    a = ap.parse_args(argv)
    if a.cmd == "emit":
        for p in emit(RUNS, a.hosts):
            print(os.path.relpath(p, ROOT))
        return 0
    if a.cmd == "scan-report":
        text = scan_report(RUNS)
        with open(os.path.join(HERE, "scan_report.txt"), "w") as f:
            f.write(text)
        print(text, end="")
        return 0
    run_lane(a.lane)
    return 0


if __name__ == "__main__":
    sys.exit(main())
