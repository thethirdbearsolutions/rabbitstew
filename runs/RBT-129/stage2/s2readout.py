#!/usr/bin/env python3
"""RBT-129 Stage 2's readout drivers: the interim (after 2a) and the final map (STAGE2-PLAN.md §3, §5, §7-§9, §11;
RBT129-OVERFLOW-RULE-1).

    python3 runs/RBT-129/stage2/s2readout.py interim --go RBT129-S2-INTERIM-GO-1
        -> runs/RBT-129/stage2/integrity-interim.txt, then runs/RBT-129/stage2/stage2a_interim.txt
    python3 runs/RBT-129/stage2/s2readout.py final --go RBT129-S2-FINAL-GO-1
        -> runs/RBT-129/stage2/integrity-final.txt, then runs/RBT-129/stage2/stage2_final.txt

**The locks.** Each step refuses unless ``stage2_readout.refusal`` passes for it.  Integrity runs first and its file is
written before anything else is computed; any integrity failure is a HELP and nothing further is read.

**What is read is the emission, not the lane files** (#535 adversary R-1).  Every continuation unit is derived from its
emitter, a pure function of the committed inputs: Stage 2a from ``s2lanes.s2a_units``, R-B (GO-1) from
``stages.rb_units``, 2b(2a) from ``s2b.s2b_units`` over the committed interim's R4 list.  A lane file that omits a unit
(re-emitted without a ruled CRASHED or quarantined run: ``s2lanes.drop``) cannot make that unit vanish.  Each emitted job
is then one of:
- **done** (its done-marker; a seed-rule or pre-merge-extinct skip counts as done);
- **CRASHED**: a ruled ``CRASHED: <run label>`` record, or a run with no marker whose log meets RULING item 5's count with
  both attempts attested (``epa_ecology.crash_state``; the crash record branch when the local log is gone).  One event per
  run directory (rule §4.4);
- **no fork source**: a job whose source is a CRASHED or excluded run (rule §4.3: CRASHED too, no further event);
- **EXCLUDED**: a quarantined run with no ruled CRASHED record (never restored or read; removed from n, as CRASHED);
- **OVERFLOWED-INCOMPLETE**: a ruled ``INCOMPLETE: <run label> <ruling id>`` record (COORD-RULING-RB-HELP-1's kind: a
  non-native repeated failure after a logged overflow): listed among the OVERFLOWED with the ruling's note, removed from
  n, one crash event, never a HELP.  By the ruling's clarification C1 (H3, FC-2), nothing of it or downstream of it
  (its ckpt60, its forks) is restored or read, and its §3.3 bound is the uninformative one (every completion);
- anything else with no marker is a HELP: an unattested crash, or a stage that is not complete.

**Two HELPs of the R4 recheck in the final** (plan §5.1): no committed interim integrity file recording the exclusions
the interim ran under; and a 2a run quarantined after the interim, which the recheck would have to read (a quarantined
run is never read: the coordinator rules).  An exclusion ruled after the interim is otherwise printed apart, and the
recheck uses the interim's own.

**One definition of everything.**
- **Per-seed statistics** are the Stage-1 readout's ``assemble_point``, run under :func:`layout`, which points its
  ``unit_dir`` and ``SEEDS`` at a stage's directories and seeds for the duration of one call.
- **Calls, BH, Holm, verdicts and the scorecard** are ``stage1_readout``'s.
- **The Stage-2 rules** are ``stage2_readout``'s: the combination, the C3 pins, the marks, the unit states through the
  registered ``epa_ecology`` (A1), A2 and A3.

**What the interim prints** (S2-R3): integrity, the 2a gate re-check, operational counts, and the R4 list for 2b(2a)
with CP and core-h.  It prints no call and no §8 line, for any point.

**What the final prints** (plan §5, §8, §9; #535 adversary R-2, R-3): the whole map is computed twice, under
include-flagged (primary) and exclude-known-flagged (sensitivity); every printed line is keyed, and every line whose
sensitivity value differs carries ``OVERFLOW-SENSITIVE`` with that value beside the primary (rule §3.3, §5 item 4).
"""
from __future__ import annotations

import argparse
import contextlib
import glob
import json
import math
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s2b  # noqa: E402
import s2lanes  # noqa: E402

stages, s2 = s2lanes.stages, s2lanes.s2
sr = s2.sr
H, D = sr.H, sr.D
RUNS, ROOT = s2lanes.RUNS, s2lanes.ROOT

#: the directory each stage's units live in (runs/RBT-129/<dir>/<point>/<seed>/<arm>), and its lanes
STAGE_DIRS = {"1": "stage1", "2a": s2lanes.STAGE_DIR, "rb": "rb", "2b": s2b.STAGE_DIR}
LANES = {"2a": s2lanes.NAME, "rb": stages.RB_LANES, "2b": s2b.NAME}
HALF1, HALF2 = s2.SEEDS_HALF1, s2.SEEDS_HALF2
SEED_BASE = sr.SEED_BASE
RUN_KINDS = ("fresh", "resume", "fork")
SKIPPED_NOTES = ("skipped: not valid at the merge", "skipped: extinct pre-merge")
DONE, SKIPPED, CRASHED, UPSTREAM, EXCLUDED = "done", "SKIPPED", s2.CRASHED, "no fork source", "EXCLUDED"
#: COORD-RULING-RB-HELP-1's state: OVERFLOWED and INCOMPLETE (a non-native repeated failure after a logged overflow),
#: ruled by an ``INCOMPLETE: <run label> <ruling id>`` line: listed among the OVERFLOWED with the ruling's note, its value
#: missing (removed from n, its bounds as a CRASHED seed's), one crash event toward the ceiling, never a HELP
INCOMPLETE = "OVERFLOWED-INCOMPLETE"
INCOMPLETE_NOTE = "incomplete: non-native failure after a logged overflow ({})"
REMOVED = (s2.CRASHED, EXCLUDED, INCOMPLETE)
#: a Stage-1 M/N scan replay that does not replay byte for byte (rule §6.1): a flagged state, as OVERFLOWED
SCAN_DIFFER = "SCAN-DIFFER"
PER_BIRTH_WINDOWS = (s2.PER_BIRTH_WINDOW, sr.WINDOW)


class Help(RuntimeError):
    """A HELP: the step stops and prints nothing further (plan §7)."""


# -- reading a stage's directories through the Stage-1 readout's definitions ---------------------------------------- #

@contextlib.contextmanager
def layout(stage_dir: str, seeds):
    """Point ``stage1_readout.unit_dir`` and ``SEEDS`` at a stage's directories and seeds, for one call only."""
    saved = sr.unit_dir, sr.SEEDS
    sr.unit_dir = lambda root, pid, j: os.path.join(root, "runs", "RBT-129", stage_dir, pid, str(SEED_BASE + j))
    sr.SEEDS = tuple(seeds)
    try:
        yield
    finally:
        sr.unit_dir, sr.SEEDS = saved


def assemble(root: str, stage: str, pid: str, seeds, arms: dict, with_regime: bool = False) -> dict:
    """``stage1_readout.assemble_point`` at one stage's units of one point.  ``arms``: void (S seeds out of n), m and
    n (the M and N seeds), crashed (M seeds removed: CRASHED, EXCLUDED, or excluded as flagged; never read)."""
    with layout(STAGE_DIRS[stage], seeds):
        try:
            return sr.assemble_point(root, pid, arms.get("m", ()), arms.get("n", ()), arms.get("void", ()),
                                     arms.get("m_out", ()), with_regime)
        except FileNotFoundError as e:  # R-6: a directory that should have been restored is a HELP, not a traceback
            raise Help(f"{stage}/{pid}: a run directory the readout needs is missing ({e.filename})")


def unit_path(root: str, stage: str, pid: str, sd: int, arm: str) -> str:
    return os.path.join(root, "runs", "RBT-129", STAGE_DIRS[stage], pid, str(sd), arm)


def guarded_restore(root: str, restore, quarantined=()):
    def go(d):
        lab = run_label(os.path.relpath(d, root))
        if s2.is_quarantined(lab) or any(q.lower() in lab.lower() for q in quarantined):
            raise sr.QuarantineRefusal(f"{d}: a quarantined label is never restored or read")
        sr.guarded_restore(d, root, restore)
    return go


def run_label(rel: str) -> str:
    """A repository-relative run directory's checkpoint label (``stages._label``'s, from any root)."""
    return "rbt-129-" + os.path.relpath(rel, os.path.join("runs", "RBT-129")).replace(os.sep, "-")


def _abs(root: str, p: str) -> str:
    return p if os.path.isabs(p) else os.path.join(root, p)


def marker_note(d: str, tag: str):
    path = os.path.join(d, f".rbt129-done-{tag}")
    if not os.path.exists(path):
        return None
    text = open(path).read()
    return text.split(" ", 1)[1].strip() if " " in text else ""


def seasons_ran(d: str, start: int) -> range:
    state = json.load(open(os.path.join(d, "state.json")))
    return range(start, int(state["season"]))


# -- the emission (R-1): every continuation job, from its emitter ------------------------------------------------------ #

def _rel(p: str) -> str:
    return os.path.relpath(os.path.abspath(p), ROOT)


def emission(stage: str, points_2b=()) -> list:
    """Every job the stage's emitter writes, its paths repository-relative (so they can be placed under any root)."""
    if stage == "2a":
        salts, _ = s2lanes.s2a_inputs(RUNS)
        units = s2lanes.s2a_units(RUNS, salts, s2lanes.s2a_gate())
    elif stage == "rb":
        salts, _ = stages.rb_inputs(RUNS)
        units = stages.rb_units(RUNS, salts, stages.rb_gate())
    elif stage == "2b":
        units = s2b.emission(points_2b)[0] if points_2b else []
    else:
        raise ValueError(stage)
    return [{**j, **{k: _rel(j[k]) for k in ("dir", "src", "ref") if k in j}} for u in units for j in u["jobs"]]


def ruled_exclusions(rev: str = "HEAD") -> tuple:
    """(quarantined labels, ruled CRASHED run labels, {ruled INCOMPLETE run label: ruling id}) as committed at ``rev``
    (``s2lanes.ruled_exclusions``)."""
    return s2lanes.ruled_exclusions(rev, ROOT)


def _excl3(excl: tuple) -> tuple:
    return (list(excl[0]), list(excl[1]), dict(excl[2]) if len(excl) > 2 else {})


def lane_files_match(root: str, stage: str, jobs: list, excl: tuple) -> str:
    """The stage's committed lane files hold exactly the emission, or the emission less the ruled exclusions (FC-A);
    a HELP otherwise.  Returns a summary.  (R-B's lanes are the tooling's; their own run-lane checks them.)"""
    d = os.path.join(root, "runs", "RBT-129", "lanes", LANES[stage])
    files = sorted(glob.glob(os.path.join(d, "*.jsonl")))
    have = [json.loads(x) for f in files for x in open(f) if x.strip()]
    if stage == "rb":
        return f"{len(have)} jobs in {len(files)} lane files (the tooling's)"
    names, want = [j["name"] for j in have], {j["name"] for j in jobs}
    gone = s2lanes.droppable(jobs, *excl)
    if not set(names) <= want or len(set(names)) != len(names) or (want - set(names)) - gone:
        raise Help(f"lanes/{LANES[stage]} is not the emission (nor the emission less its ruled exclusions)")
    return f"{len(have)} jobs in {len(files)} lane files; {len(want - set(names))} omitted by ruled exclusions"


# -- each job's status, and each arm-seed's state (R-1; plan §3; rule §4.3, §4.4) --------------------------------------- #

def _crash_state(d: str, epa, crash_log=None):
    import mjbuild
    tmp = tempfile.mkdtemp(prefix="rbt129-readout-crashlog-")
    try:
        log = (crash_log or stages.crash_log)(d, tmp)
        st = epa.crash_state(log, epa.unit_id(d))
        over = bool(st) and bool(epa.read_log(log)["overflow"])
        return st, over
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
        _ = mjbuild


def classify(root: str, stage: str, jobs: list, restore, excl: tuple, epa, crash_log=None) -> dict:
    """{"status": {name: done | SKIPPED | CRASHED | no fork source | EXCLUDED}, "notes", "events": [(pid, stage, dir)],
    "also_overflowed": {dir}}: every emitted job, in its unit's order (sources before the jobs that read them)."""
    quarantined, crashed_list, inc = _excl3(excl)
    crashed_ruled, incomplete = {c.lower() for c in crashed_list}, {k.lower(): v for k, v in inc.items()}
    status, notes, events, also, gone, sealed = {}, {}, [], set(), set(), set()
    for j in jobs:
        rel, tag = j["dir"], j["name"].rsplit("/", 1)[1]
        pid = j["name"].split("/")[1]
        lab = run_label(rel).lower()
        labs = [run_label(j[k]).lower() for k in ("dir", "src", "ref") if k in j]
        if lab in crashed_ruled or lab in incomplete:
            st = CRASHED if lab in crashed_ruled else INCOMPLETE
            if st == INCOMPLETE:
                notes[j["name"]] = INCOMPLETE_NOTE.format(incomplete[lab])
            if rel not in gone:
                events.append((pid, stage, rel))
        elif any(q.lower() in lab_ for q in quarantined for lab_ in labs):
            st = EXCLUDED
        elif rel in sealed or any(j.get(k) in sealed for k in ("src", "ref")):
            st = UPSTREAM  # RB-HELP-1 C1 (H3, FC-2): nothing downstream of an INCOMPLETE run is restored or read
        else:
            d = _abs(root, rel)
            upstream = rel in gone or any(j.get(k) in gone for k in ("src", "ref"))
            note = None
            if not upstream or (j["job"] != "fresh" and rel not in gone):
                restore(d)
                note = marker_note(d, tag)  # a job its source's crash did not reach is done (#535 fix-check 2)
            if note is not None:
                st = SKIPPED if note.startswith(SKIPPED_NOTES) else DONE
                notes[j["name"]] = note
            elif upstream:
                st = UPSTREAM
            elif j["job"] in RUN_KINDS:
                cs, over = _crash_state(d, epa, crash_log)
                if not cs:
                    raise Help(f"{j['name']}: no done-marker and no crash record: the stage is not complete")
                if not cs["attested"]:
                    raise Help(f"{j['name']}: an unattested crash: the hive stops and the coordinator re-rules (rule §4.3)")
                st = CRASHED
                events.append((pid, stage, rel))
                if over:
                    also.add(rel)
            else:
                raise Help(f"{j['name']}: no done-marker: the stage is not complete")
        if st in (CRASHED, UPSTREAM, EXCLUDED, INCOMPLETE):
            gone.add(rel)
        if st == INCOMPLETE or (st == UPSTREAM and (rel in sealed or any(j.get(k) in sealed for k in ("src", "ref")))):
            sealed.add(rel)
        status[j["name"]] = st
    return {"status": status, "notes": notes, "events": events, "also_overflowed": also}


def arm_states(root: str, stage: str, jobs: list, cls: dict, epa) -> tuple:
    """({(pid, seed, arm): state}, exposure): each S, M and N arm-seed's state through the registered definitions
    (``unit_state``; ``s60_state`` for forks, failing closed), CRASHED for a crashed run or one with no fork source,
    EXCLUDED, or SKIPPED; and the near-miss exposure (rule §2, §5 item 3) per arm."""
    out, expo = {}, {}
    for j in jobs:
        if j["job"] not in RUN_KINDS:
            continue
        pid, sd, tag = j["name"].split("/")[1:]
        arm, key, st = ("S" if tag in ("S60", "S") else tag), (pid, int(sd), "S" if tag in ("S60", "S") else tag), \
            cls["status"][j["name"]]
        if st in (CRASHED, UPSTREAM):
            out[key] = CRASHED if out.get(key) != INCOMPLETE else INCOMPLETE
            continue
        if st in (EXCLUDED, INCOMPLETE):
            out[key] = st
            continue
        if tag == "S60" or key in out:
            continue  # S's state is read once, at its full run (the S job)
        if st == SKIPPED:
            out[key] = SKIPPED
            continue
        d = _abs(root, j["dir"])
        try:
            v = s2.unit_state(d, seasons_ran(d, 0 if arm == "S" else stages.MERGE), epa)
            if arm in ("M", "N") and v == s2.CLEAN:
                v = s2.s60_state(d, epa)  # A2, failing closed (#533 adversary MAJOR 4)
        except s2.Stage2Help as e:
            raise Help(str(e))
        if v == CRASHED:
            cls["events"].append((pid, stage, j["dir"]))
        out[key] = v
        import mjbuild
        info = epa.read_log(os.path.join(d, mjbuild.EPA_LOG))
        e = expo.setdefault(arm, {"near_arms": 0, "near": 0, "max_nedges": 0, "events": 0, "iterations": 0})
        e["near_arms"] += bool(info["near"])
        e["near"] += int(info["near"])
        e["events"] += int(info["overflow"])
        e["max_nedges"] = max(e["max_nedges"], info.get("max_nedges") or 0)
        e["iterations"] += info.get("epa_iterations") or 0
    return out, expo


def arms_for(states: dict, pid: str, seeds, mode: str) -> dict:
    """The seeds each arm contributes at one point under ``mode``: a removed (CRASHED, EXCLUDED) or excluded S seed leaves
    n (as a ruled K-SALT VOID, O-7) and takes its M and N with it; an M seed that is removed or excluded is listed in
    ``m_out`` (never read; its y′ bound is printed), with ``m_crashed`` its CRASHED ones; likewise ``n_out``/
    ``n_crashed`` for N (R-5: reported, never dropped silently)."""
    out = {k: [] for k in ("void", "s_crashed", "s_incomplete", "s_excluded", "m", "n", "m_out", "m_crashed",
                           "n_out", "n_crashed")}
    for j in seeds:
        sd = SEED_BASE + j
        s = states.get((pid, sd, "S"), s2.UNSCANNED)
        if s in REMOVED or not s2.keep_seed(s, mode):
            out["void"].append(j)
            if s in (CRASHED, INCOMPLETE):
                out["s_crashed"].append(j)  # the bounds and CRASH-AFFECTED, as a CRASHED seed's (RB-HELP-1 H1)
                if s == INCOMPLETE:
                    out["s_incomplete"].append(j)
            elif s != EXCLUDED:
                out["s_excluded"].append(j)
            continue
        for arm in ("M", "N"):
            a = states.get((pid, sd, arm))
            if a in (None, SKIPPED):
                continue
            k = arm.lower()
            out[k].append(j)
            if a in REMOVED or not s2.keep_seed(a, mode):
                out[f"{k}_out"].append(j)
                if a in (CRASHED, INCOMPLETE):
                    out[f"{k}_crashed"].append(j)
    out["n"] = [j for j in out["n"] if j not in out["n_out"]]
    return out


# -- integrity (plan §7; rule §5) -------------------------------------------------------------------------------------- #

STANDING = ("Continuations ran on MuJoCo 3.14.0 with an instrumented build that is byte-identical to stock on every"
            " trajectory without an overflow (and makes no claim at or after one). The build logs every EPA horizon"
            " overflow (google-deepmind/mujoco#3646), a memory-safety bug that can corrupt a contact without crashing."
            " Every overflow the build logged in these runs is handled by the registered rule. A run whose log is"
            " incomplete is treated as overflowed. Stage-1 units outside the M/N scan's seasons 60-299 were not checked"
            " this way.")


def stage_integrity(root: str, stage: str, jobs: list, restore, excl: tuple, epa, crash_log=None) -> tuple:
    """(lines, states, events) for one continuation stage: the lane files against the emission; every job's status;
    the unit states (A3 whole, A2, foreign units, UNLOGGED); the gate re-check (every M/N fork skipped exactly when its
    seed is not valid at the merge); s60cmp IDENTICAL; K-SALT with N-3; the counts by arm (done, with seed-rule skips
    folded in, R-9), the near-miss exposure, and the units named only when OVERFLOWED, UNLOGGED or CRASHED."""
    lines = [f"## {LANES[stage]}: {len(jobs)} jobs in the emission; {lane_files_match(root, stage, jobs, excl)}"]
    cls = classify(root, stage, jobs, restore, excl, epa, crash_log)
    states, expo = arm_states(root, stage, jobs, cls, epa)
    forks = 0
    for j in jobs:
        st, tag, d = cls["status"][j["name"]], j["name"].rsplit("/", 1)[1], _abs(root, j["dir"])
        if st not in (DONE, SKIPPED):
            continue
        if j["job"] == "fork" and j.get("seed_rule"):
            forks += 1
            note = cls["notes"][j["name"]]
            if not note.startswith(SKIPPED_NOTES[1]):  # extinct before the merge: no season-60 state to read
                if note.startswith(SKIPPED_NOTES[0]) == stages.valid_at_merge(_abs(root, j["src"])):
                    raise Help(f"{j['name']}: the gate re-check fails: the seed rule was not applied as registered")
        if j["job"] == "s60cmp" and s2lanes.s60cmp_word(d) != "IDENTICAL":
            raise Help(f"{j['name']}: S60CMP {s2lanes.s60cmp_word(d)}: the re-simulation is not the census run (O-2)")
        if j["job"] == "ksalt":
            word = open(os.path.join(d, stages.KSALT_FILE)).readline().split()[1].rstrip(":")
            pid, sd = j["name"].split("/")[1:3]
            try:
                s2.ksalt_outcome(word, states.get((pid, int(sd), "S")) in s2.FLAGGED_STATES)
            except s2.Stage2Help as e:
                raise Help(str(e))
            if word != "PASS":
                raise Help(f"{j['name']}: KSALT {word}: a HELP until the coordinator rules (F7)")
    counts = {}
    for (pid, sd, arm), st in states.items():
        c = counts.setdefault(arm, {"done": 0})
        if st in (SKIPPED, s2.CLEAN, s2.OVERFLOWED, s2.UNLOGGED):
            c["done"] += 1
        if st == INCOMPLETE:  # listed among the OVERFLOWED (RB-HELP-1 H1)
            c[s2.OVERFLOWED] = c.get(s2.OVERFLOWED, 0) + 1
            c["incomplete"] = c.get("incomplete", 0) + 1
        elif st != SKIPPED:
            c[st] = c.get(st, 0) + 1
    also = {(j["name"].split("/")[1], int(j["name"].split("/")[2]), "S" if j["name"].endswith(("/S60", "/S"))
             else j["name"].rsplit("/", 1)[1]) for j in jobs if j["dir"] in cls["also_overflowed"]}
    for arm in sorted(counts):
        c = counts[arm]
        e = expo.get(arm, {})
        lines.append(f"  {arm}: done {c['done']}; CLEAN {c.get(s2.CLEAN, 0)}, OVERFLOWED {c.get(s2.OVERFLOWED, 0)}"
                     f" ({c.get('incomplete', 0)} of them incomplete, ruled;"
                     f" +{sum(1 for k in also if k[2] == arm)} CRASHED after an overflow, rule §4.2),"
                     f" UNLOGGED {c.get(s2.UNLOGGED, 0)}, CRASHED {c.get(CRASHED, 0)}, EXCLUDED {c.get(EXCLUDED, 0)};"
                     f" near misses on {e.get('near_arms', 0)} arm-seeds ({e.get('near', 0)} logged, a lower bound),"
                     f" largest horizon {e.get('max_nedges', 0)}, overflow events {e.get('events', 0)},"
                     f" EPA iterations {e.get('iterations', 0)}")
    lines.append(f"  gate re-check: PASS ({forks} M/N forks, the seed rule applied at run time as registered)")
    inc_notes = {(j["name"].split("/")[1], int(j["name"].split("/")[2]),
                  "S" if j["name"].endswith(("/S60", "/S")) else j["name"].rsplit("/", 1)[1]): cls["notes"][j["name"]]
                 for j in jobs if cls["status"][j["name"]] == INCOMPLETE}
    for (pid, sd, arm), st in sorted(states.items()):
        if st == INCOMPLETE:
            lines.append(f"  {s2.OVERFLOWED} ({inc_notes.get((pid, sd, arm), 'incomplete')}): {LANES[stage]}/{pid}/{sd}/{arm}")
        elif st in (s2.OVERFLOWED, s2.UNLOGGED, CRASHED, EXCLUDED) or (pid, sd, arm) in also:
            lines.append(f"  {st}{' (after an overflow)' if (pid, sd, arm) in also else ''}: {LANES[stage]}/{pid}/{sd}/{arm}")
    lines.append(f"  build: every platform record, resume entry and start line at {s2.REGISTERED_SHA} (A3): PASS")
    lines.append(f"  crash events (distinct run directories, rule §4.4): {len(cls['events'])}")
    return lines, states, cls["events"]


def overflow_pattern(states: dict) -> list:
    """Rule §3.4: more than 5% of a stage's arm-seeds, or 3 or more at one point, OVERFLOWED: a disclosure line."""
    out = []
    for stage, sts in sorted(states.items()):
        arms = [k for k, v in sts.items() if v not in (SKIPPED,)]
        flagged = [k for k in arms if sts[k] in s2.FLAGGED_STATES + (INCOMPLETE,)]
        by = {}
        for pid, _, _ in flagged:
            by[pid] = by.get(pid, 0) + 1
        pts = sorted(p for p, n in by.items() if n >= 3)
        if arms and (len(flagged) / len(arms) > 0.05 or pts):
            out.append(f"  overflow is a pattern at {LANES.get(stage, stage)}: {len(flagged)} of {len(arms)} arm-seeds"
                       f" flagged ({100.0 * len(flagged) / len(arms):.1f}%)" + (f"; 3 or more at {', '.join(pts)}" if pts else ""))
    return out


def keep_stage1(state: str, mode: str) -> bool:
    """``stage2_readout.keep_seed`` for a Stage-1 S, M or N arm-seed, with a scan's SCAN-DIFFER flagged as OVERFLOWED
    is."""
    return mode == "include-flagged" if state == SCAN_DIFFER else s2.keep_seed(state, mode)


#: the Stage-1 S silent-corruption scan (OWNER-DECISIONS-2026-10-09 item 1; ``s-corruption-scan/sscan.py``)
SSCAN_LANES = "SSCAN"
#: how far a state is from CLEAN, for combining an arm's own scan state with its upstream S60 phase's
_RANK = {s2.CLEAN: 0, s2.UNSCANNED: 0, s2.UNLOGGED: 1, s2.OVERFLOWED: 2, SCAN_DIFFER: 3, s2.CRASHED: 4}


def _worse(a: str, b: str) -> str:
    return b if _RANK.get(b, 0) > _RANK.get(a, 0) else a


def s60_phase_state(run_s: str, epa) -> str:
    """A Stage-1 S replay's S60 phase (seasons 0-59, or to its pre-merge extinction) from its own EPA log, failing
    closed as ``stage2_readout.s60_state`` does: OVERFLOWED for an overflow in those seasons or before an attempt's
    first season line; UNLOGGED (flagged) for an unreadable log, ``read_log``'s unlogged reasons or a missing season
    line; CLEAN otherwise."""
    import mjbuild

    try:
        info = epa.read_log(os.path.join(run_s, mjbuild.EPA_LOG))
        ran = range(0, min(stages.MERGE, seasons_ran(run_s, 0).stop))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return s2.UNLOGGED
    per = info["seasons"]
    if any(v["overflow"] for s, v in per.items() if s is None or s in ran):
        return s2.OVERFLOWED
    if info["unlogged"] or any(s not in per for s in ran):
        return s2.UNLOGGED
    return s2.CLEAN


def s_scan_states(root: str, restore, epa) -> tuple:
    """(lines, {(pid, seed): S state}, {(pid, seed): S60-phase state}) from the Stage-1 S scan's two comparisons per
    chain, every outcome a defined state, none a HELP (as the M/N scan's):
    - ``S-cmp`` IDENTICAL: the replay S's state over seasons 0-299 (``unit_state``); ``ckpt60-cmp`` IDENTICAL: its S60
      phase's (``s60_phase_state``);
    - DIFFER: SCAN-DIFFER (flagged), named; NO-REFERENCE: UNSCANNED, named;
    - a comparison not done: UNSCANNED, counted, so an incomplete scan is never silent."""
    d = os.path.join(root, "runs", "RBT-129", "lanes", SSCAN_LANES)
    jobs = [json.loads(x) for f in sorted(glob.glob(os.path.join(d, "*.jsonl"))) for x in open(f) if x.strip()]
    s_out, s60, named = {}, {}, []
    verdicts, not_done = {"ckpt60-cmp": {}, "S-cmp": {}}, {"ckpt60-cmp": 0, "S-cmp": 0}
    for j in jobs:
        if j["job"] != "sscancmp":
            continue
        _, pid, s, tag = j["name"].split("/")
        s = int(s)
        rd = _abs(root, j["dir"])
        restore(rd)
        note = marker_note(rd, tag)
        if note is None:
            not_done[tag] += 1
            continue
        word = note.split()[1].rstrip(":") if len(note.split()) > 1 else note
        verdicts[tag][word] = verdicts[tag].get(word, 0) + 1
        if word == "NO-REFERENCE":
            named.append(f"  UNSCANNED (NO-REFERENCE): {j['name']}")
            continue
        if word != "IDENTICAL":
            st = SCAN_DIFFER
        else:
            rs = os.path.join(os.path.dirname(rd), "S")
            restore(rs)
            try:
                st = s2.unit_state(rs, seasons_ran(rs, 0), epa) if tag == "S-cmp" else s60_phase_state(rs, epa)
            except s2.Stage2Help as e:
                raise Help(str(e))
        (s_out if tag == "S-cmp" else s60)[(pid, s)] = st
    n_s = len(sr.STAGE1_POINTS) * len(HALF1)
    chains = sum(1 for j in jobs if j["job"] == "sscancmp" and j["name"].endswith("/S-cmp"))
    lines = [f"## Stage-1 S scan (OWNER-DECISIONS-2026-10-09; rule §6): {chains} chains in lanes/{SSCAN_LANES}"]
    for tag, title, got in (("ckpt60-cmp", "S60 phase (seasons 0-59)", s60), ("S-cmp", "S (seasons 0-299)", s_out)):
        by = {}
        for st in got.values():
            by[st] = by.get(st, 0) + 1
        lines.append(f"  {title}: compared {sum(verdicts[tag].values())}"
                     f" ({', '.join(f'{k} {v}' for k, v in sorted(verdicts[tag].items())) or 'none'}); "
                     + ", ".join(f"{k} {v}" for k, v in sorted(by.items())) + f"{'; ' if by else ''}not done"
                     f" {not_done[tag]}; UNSCANNED {n_s - len(got)} of {n_s}")
    lines += [f"  {st}: SSCAN/{pid}/{s}/S" for (pid, s), st in sorted(s_out.items()) if st != s2.CLEAN]
    lines += [f"  {st} (S60 phase, upstream of its M and N): SSCAN/{pid}/{s}" for (pid, s), st in sorted(s60.items())
              if st != s2.CLEAN]
    return lines + named, s_out, s60


def scan_states(root: str, restore, epa) -> tuple:
    """(lines, {(pid, seed, arm): state}) for Stage 1's M and N from the owner's M/N scan (plan §3.6; rule §6.1), every
    outcome a defined state (the coordinator's ruling on the #535 fix-check 2), none a HELP:
    - a replay done and IDENTICAL: CLEAN (seasons 60-299) or OVERFLOWED (UNLOGGED: flagged, as rule §4.6 defaults it);
    - **DIFFER**: SCAN-DIFFER, a flagged state: kept as observed under include-flagged (the accepted Stage-1 record
      stands, COORD-RULING-517 C1), removed under exclude-known-flagged, named;
    - **NO-REFERENCE**: UNSCANNED, named;
    - a replay not done: UNSCANNED, and counted, so an incomplete scan is never silent.
    The coordinator may still rule otherwise before GO-ID-FINAL."""
    d = os.path.join(root, "runs", "RBT-129", "lanes", stages.SCAN_LANES)
    jobs = [json.loads(x) for f in sorted(glob.glob(os.path.join(d, "*.jsonl"))) for x in open(f) if x.strip()]
    out, verdicts, named, not_done = {}, {}, [], 0
    for j in jobs:
        if j["job"] != "scancmp":
            continue
        pid, s, arm = j["name"].split("/")[1], int(j["name"].split("/")[2]), j["name"].split("/")[3][:-len("-cmp")]
        rd = _abs(root, j["dir"])
        restore(rd)
        note = marker_note(rd, j["name"].rsplit("/", 1)[1])
        if note is None:
            not_done += 1
            continue
        word = note.split()[1].rstrip(":") if len(note.split()) > 1 else note
        verdicts[word] = verdicts.get(word, 0) + 1
        if word == "NO-REFERENCE":
            named.append(f"  UNSCANNED (NO-REFERENCE): SCAN/{pid}/{s}/{arm}")
            continue
        if word != "IDENTICAL":
            out[(pid, s, arm)] = SCAN_DIFFER
            continue
        try:
            out[(pid, s, arm)] = s2.unit_state(rd, seasons_ran(rd, stages.MERGE), epa)
        except s2.Stage2Help as e:
            raise Help(str(e))
    by = {}
    for (pid, s, arm), st in out.items():
        by.setdefault(arm, {}).setdefault(st, 0)
        by[arm][st] += 1
    forks = sr.mn_forks(root)
    n_mn = {a: sum(len(f.get(a, [])) for f in forks.values()) for a in ("M", "N")}
    lines = [f"## Stage-1 M/N scan (plan §3.6; rule §6.1): {sum(verdicts.values())} replays compared"
             f" ({', '.join(f'{k} {v}' for k, v in sorted(verdicts.items())) or 'none'}); {not_done} replays in"
             f" lanes/{stages.SCAN_LANES} not done (UNSCANNED)"]
    for a in ("M", "N"):
        st = by.get(a, {})
        lines.append(f"  {a}: " + ", ".join(f"{k} {v}" for k, v in sorted(st.items()))
                     + f"{'; ' if st else ''}UNSCANNED {n_mn[a] - sum(st.values())} of {n_mn[a]}")
    lines += [f"  {st}: SCAN/{pid}/{s}/{arm}" for (pid, s, arm), st in sorted(out.items()) if st != s2.CLEAN] + named
    # the S scan: each S arm's own state (seasons 0-299), and its S60 phase upstream of that seed's M and N (rule §3.1's
    # propagation, as ``propagate_s60``): a flagged S60 phase flags them, whatever their own 60-299 scan found
    s_lines, s_out, s60 = s_scan_states(root, restore, epa)
    for (pid, s), st in s_out.items():
        out[(pid, s, "S")] = _worse(st, s60.get((pid, s), s2.CLEAN))
    for (pid, s), st in s60.items():
        if _RANK.get(st, 0):
            out.setdefault((pid, s, "S"), st)
            for a in ("M", "N"):
                if s - SEED_BASE in forks.get(pid, {}).get(a, []):
                    out[(pid, s, a)] = _worse(out.get((pid, s, a), s2.UNSCANNED), st)
    lines += s_lines
    lines.append("  UNSCANNED (rule §6.1; COORD-RULING-520 D2): every Stage-1 arm-seed the two scans above did not cover"
                 " (an M or N CLEAN there covers seasons 60-299; its seasons 0-59 are its S chain's S60 phase): a known"
                 " memory-safety bug (EPA horizon overflow) can corrupt without crashing; the UNSCANNED units were not"
                 " checked")
    return lines, out


def integrity(root: str, stage_jobs: dict, restore, excl: tuple, crash_log=None) -> tuple:
    epa = s2.registered_epa()
    lines, states, events = [], {}, []
    for st, jobs in stage_jobs.items():
        ls, sts, ev = stage_integrity(root, st, jobs, restore, excl, epa, crash_log)
        lines += ls
        states[st] = sts
        events += [(pid, stg) for pid, stg, _ in ev]
    pattern = overflow_pattern(states)
    lines += ["## overflow pattern (rule §3.4)"] + (pattern or ["  none"])
    ceiling = s2.crash_ceiling(events)
    lines.append(f"## crash ceiling (rule §4.4): {len(events)} attested crash events: {ceiling}")
    if ceiling != "continue":
        raise Help("the crash ceiling is reached: launches stop and the coordinator re-rules (rule §4.4)")
    lines.append(f"## standing sentence (rule §5.5): {STANDING}")
    return lines, states, bool(pattern)


# -- calls ------------------------------------------------------------------------------------------------------------- #

def stage1_arms(root: str, scan: dict = None, mode: str = "include-flagged") -> dict:
    """Stage 1's S, M and N seeds as the Stage-1 readout read them, its CRASHED unit removed, and under
    exclude-known-flagged the arm-seeds the scans found flagged removed too (plan §3.6): a flagged M or N is listed
    out; a flagged S seed leaves n and takes its M and N with it, as ``arms_for`` does for a continuation's.  The
    CRASHED M stays CRASHED (``m_crashed``) even when its S seed is voided."""
    forks = sr.mn_forks(root)
    scan = scan or {}
    out = {}
    for pid in sr.STAGE1_POINTS:
        fk = forks.get(pid, {"M": [], "N": []})
        void = [j for j in HALF1 if not keep_stage1(scan.get((pid, SEED_BASE + j, "S"), s2.UNSCANNED), mode)]
        # the CRASHED M keeps its label whatever its S seed's scan says (#562 adversary NIT 4): never read either way
        cr = [sr.CRASHED_SEED - SEED_BASE] if pid == sr.CRASHED_POINT else []
        flagged = {a: [j for j in fk.get(a, []) if j not in void
                       and not keep_stage1(scan.get((pid, SEED_BASE + j, a), s2.UNSCANNED), mode)] for a in ("M", "N")}
        out[pid] = {"void": void, "m": [j for j in fk["M"] if j not in void],
                    "n": [j for j in fk["N"] if j not in void and j not in flagged["N"]],
                    "m_out": sorted(set(cr) | set(flagged["M"])), "m_crashed": cr, "n_out": flagged["N"], "n_crashed": [],
                    "s_crashed": [], "s_excluded": list(void)}
    return out


def restore_stage1(root: str, restore) -> None:
    """R-6: every Stage-1 directory the readout reads, as ``stage1_readout.readout`` restored them (S, ckpt60, and the
    gate's M and N bar the CRASHED unit)."""
    forks = sr.mn_forks(root)
    for pid in sr.STAGE1_POINTS:
        fk = forks.get(pid, {"M": [], "N": []})
        for j in HALF1:
            subs = ["S", "ckpt60"] + (["M"] if j in fk["M"] and not (pid == sr.CRASHED_POINT and SEED_BASE + j == sr.CRASHED_SEED)
                                      else []) + (["N"] if j in fk["N"] else [])
            for sub in subs:
                restore(unit_path(root, "1", pid, SEED_BASE + j, sub))


def restore_continuation(root: str, stage: str, states: dict, restore) -> None:
    """Every continuation directory a statistic reads: S and ckpt60 of each seed kept, and its M and N."""
    for (pid, sd, arm), st in states.items():
        if st in REMOVED or st == SKIPPED:
            continue
        restore(unit_path(root, stage, pid, sd, arm))
        if arm == "S":
            restore(unit_path(root, stage, pid, sd, "ckpt60"))


def k2_inputs(halves: dict) -> tuple:
    """(per-point K2 over every N point, its runs pooled across halves; the per-stage pooled verdicts and their
    statistics; the per-kind null)."""
    by_point, by_stage, runs = {}, {}, {}
    for pid, hs in halves.items():
        for stage, h in hs:
            for j, y in h["y_n"].items():
                by_point.setdefault(pid, []).append(y)
                by_stage.setdefault(stage, []).append(y)
                runs.setdefault((pid, sr.null_kind(j)), []).append(y)
    pooled = {st: sr.k2_pooled(ys) for st, ys in by_stage.items()}
    return sr.k2_per_point(by_point), pooled, sr.pooled_null(runs), by_point


def _merge(a: dict, b: dict) -> dict:
    """One point's two halves as one 16-seed record (b may be None)."""
    if not b:
        return a
    out = dict(a)
    for k in ("n", "valid_share", "valid_income"):
        out[k] = a[k] + b[k]
    out["extinct"] = {f: a["extinct"][f] + b["extinct"][f] for f in (H, D)}
    for k, v in a.items():
        if isinstance(v, dict) and k not in ("extinct",):
            out[k] = {**v, **b.get(k, {})}
    for k in ("m_seeds", "n_seeds", "void_seeds", "crashed"):
        out[k] = list(a.get(k, [])) + list(b.get(k, []))
    return out


def share_test(y1: list, y2: list = None) -> dict:
    """The share layer's p-values at a point: the n = 8 t and TOST at ±δ_s, or at an extended point with >= 2 y′ in
    each half the same combination as income (plan §5.3; O-21)."""
    if y2 and len(y1) >= 2 and len(y2) >= 2:
        zc = s2.combined_z(y1, y2, 0.0)
        p_lo = 1 - sr.norm_cdf(s2.combined_z(y1, y2, -sr.DELTA_S))
        p_hi = sr.norm_cdf(s2.combined_z(y1, y2, sr.DELTA_S))
        ys = list(y1) + list(y2)
        return {"p": 2 * (1 - sr.norm_cdf(abs(zc))), "tie_p": max(p_lo, p_hi), "mean": sum(ys) / len(ys), "n": len(ys)}
    ys = list(y1) + list(y2 or [])
    r = sr.one_sample_t(ys)
    return {"p": r["p"], "tie_p": sr.tost_p(ys, sr.DELTA_S), "mean": r["mean"], "n": r["n"], "t": r["t"]}


def call_map(halves: dict, resolvable, crashed_s: dict = None) -> tuple:
    """(calls, families) over ``halves`` ({pid: [(stage, assembled half), ...]}, half 1 first): income by the
    combination and one BH per family (plan §5.2); the share families over N points not settled first (O-22), combined
    at extended points; K2 per point and per stage (C3-1, ``share_void``); body calls at the merged n; VARIANCE-DRIVEN on
    WINs.  ``crashed_s[pid] = {j: merge at 59 or None}``: a point's CRASHED S seeds, whose body call is bounded over
    feasible completions (``stage2_readout.crash_bounded_body``, plan §3.4)."""
    crashed_s = crashed_s or {}
    k2pt, pooled_k2, pooled, k2_runs = k2_inputs(halves)
    pooled_pass = {st: v[0] for st, v in pooled_k2.items()}
    var_null, df_null = pooled[sr.CONTINGENT_KIND]
    merged = {p: _merge(hs[0][1], hs[1][1] if len(hs) > 1 else None) for p, hs in halves.items()}
    tests = {p: s2.point_income_test(list(hs[0][1]["x"].values()), list(hs[1][1]["x"].values()) if len(hs) > 1 else None)
             for p, hs in halves.items()}
    inc_calls = s2.final_income_calls(tests)
    n_ran = {p for p, v in merged.items() if v["y_n"]}
    void = {p: s2.share_void(p in n_ran, [st for st, h in halves[p] if h["y_n"]], pooled_pass, k2pt.get(p)) for p in merged}
    base = lambda p, v: {"n": v["n"], "extinct": v["extinct"], "valid_share": v["valid_share"], "merge": v["merge"]}
    if any(merged[p]["n"] < 1 for p in merged):
        raise Help("a point with no seed left: HELP (plan 4.1)")
    pre = {p for p in n_ran if sr.body_call({**base(p, merged[p]), "void": void[p], "n_ran": False}) != "NOT RUN"}
    tested = n_ran - pre
    ys = lambda h: [h["y_m"][j] for j in h["y_m"] if j in h["s0"]]
    share = {p: share_test(ys(halves[p][0][1]), ys(halves[p][1][1]) if len(halves[p]) > 1 else None) for p in n_ran}
    wins = sr.bh({p: share[p]["p"] for p in tested})
    stie = sr.bh({p: share[p]["tie_p"] for p in tested})
    cont_p = {p: (sr.contingent_p(list(merged[p]["y_m"].values()), var_null, df_null)
                  if sr.contingent_callable(df_null) else None) for p in tested}
    cont = sr.bh(cont_p)
    rej_e = sr.bh({p: t["p_earns"] for p, t in tests.items()})
    rej_t = sr.bh({p: t["p_tie"] for p, t in tests.items()})
    out = {}
    for p, v in merged.items():
        res, rows = False, None
        if p in n_ran:
            res, rows = sr.resolving(bool(v["m_seeds"]), True, [g for g in v["g0"].values() if g is not None],
                                     share[p]["n"], resolvable)
        s = share.get(p, {})
        q = {**base(p, v), "void": void[p], "n_ran": p in n_ran, "anchor": p in sr.ANCHORS_STAGE1,
             "share": {"mean": s.get("mean"), "rejected": p in wins},
             "contingent": p in cont and (cont_p.get(p) or 1) < 0.01, "tie": p in stie, "resolving": res}
        body = sr.body_call(q)
        crash_word = s2.crash_bounded_body(q, crashed_s[p])["word"] if crashed_s.get(p) else None
        vd = False
        if body in ("H-WIN", "D-WIN"):
            js = [j for j in v["y_m"] if j in v["spread"] and v["m_flow"].get(j)]
            dm = [v["m_flow"][j][0] - v["m_flow"][j][1] for j in js]
            dsd = [(v["spread"][j][H]["sd_within"] or 0) - (v["spread"][j][D]["sd_within"] or 0) for j in js]
            vd = bool(sr.variance_driven([v["y_m"][j] for j in js], dm, dsd, 1 if body == "H-WIN" else -1))
        t = tests[p]
        out[p] = {"body": body, "vd": vd, "resolving": res, "share_family": p in tested, "crash_word": crash_word,
                  "income": {"call": inc_calls[p], "mean": t["mean"], "p": t["p_earns"], "n": t["n"], "how": t["how"],
                             "tost_p": t["p_tie"], "t": None}, "share": {**s, "call": body} if p in n_ran else {},
                  "m_arm": bool(v["m_seeds"]), "x": [x for _, h in halves[p] for x in h["x"].values()],
                  "halves": [list(h["x"].values()) for _, h in halves[p]], "merged": v, "void": void[p]}
    fam = {"tested": sorted(p for p in tests if tests[p]["p_earns"] is not None), "earns_bh": rej_e, "tie_bh": rej_t,
           "share_tested": sorted(tested), "wins": wins, "share_tie": stie, "contingent": cont,
           "contingent_callable": sr.contingent_callable(df_null), "df_null": df_null, "pooled": pooled,
           "pooled_k2": pooled_k2, "k2pt": k2pt, "k2_runs": k2_runs}
    return out, fam


# -- the R4 list (plan §5.1), shared by the interim and the final ------------------------------------------------------ #

def r4_list(root: str, states2a: dict, resolvable) -> list:
    """The R4 list over the 2a calls at n = 8 under BH over Stage-1 ∪ 2a (O-15), include-flagged: [(point, CP)]."""
    s1 = stage1_arms(root)
    halves = {p: [("1", assemble(root, "1", p, HALF1, s1[p]))] for p in sr.STAGE1_POINTS}
    for pid in s2.STAGE2A_POINTS:
        halves[pid] = [("2a", assemble(root, "2a", pid, HALF1, arms_for(states2a, pid, HALF1, "include-flagged")))]
    calls = call_map(halves, resolvable)[0]
    stats = {}
    for p in s2.STAGE2A_POINTS:
        t = sr.one_sample_t(calls[p]["x"])
        stats[p] = {"body": calls[p]["body"], "income": {"call": calls[p]["income"]["call"], "t": t["t"], "n": t["n"]},
                    "share": {**calls[p]["share"], "t": calls[p]["share"].get("t"), "n": calls[p]["share"].get("n", 0)}}
    return sr.rb_select(stats, cap=s2.rb_stage2a_slots())


# -- the interim (plan §5.1; S2-R3) ------------------------------------------------------------------------------------ #

def interim(root: str = ROOT, restore=None, resolvable=None, on_integrity=None, excl: tuple = None,
            crash_log=None) -> tuple:
    """(integrity lines, interim lines).  The 2a calls are computed for R4 eligibility only, and never printed."""
    excl = ruled_exclusions() if excl is None else excl
    restore = guarded_restore(root, restore, excl[0])
    if resolvable is None:
        resolvable = sr.scaled_resolvable()[0]
    ilines, states, _ = integrity(root, {"2a": emission("2a")}, restore, excl, crash_log)
    q, c, inc = _excl3(excl)
    ilines = ilines + [f"{EXCL_HEAD} " + json.dumps({"quarantined": sorted(q), "crashed": sorted(c), "incomplete": inc},
                                                    sort_keys=True)]
    if on_integrity:
        on_integrity(ilines)  # written before any other output is computed (plan §7)
    restore_stage1(root, restore)
    restore_continuation(root, "2a", states["2a"], restore)
    rb = r4_list(root, states["2a"], resolvable)
    b2a = s2.ruled("2B2A:")
    gate = s2b.s2b_gate([p for p, _ in rb])
    m_pts, n_pts = [r["point"] for r in gate if r["m"]], [r["point"] for r in gate if r["n"]]
    ch = s2.budget(0, 0, len(rb), len(m_pts), len(n_pts))["2b(2a) total"]
    gm, gn = s2b.go1_slots()
    L = ["# RBT-129 Stage 2a interim (STAGE2-PLAN.md §5.1; S2-R3): integrity and the R4 list only; no call, no §8 line",
         f"# claim: {sr.CLAIM}", ""]
    L.append(f"## 2b(2a): {', '.join(sorted(b2a)) or 'not registered'} (OWNER-DECISIONS-2026-10-03b)")
    if "DECLINED" in b2a:
        L.append(s2b.DECLINED_LINE)
    else:
        L.append(f"{s2b.R4_HEAD} (COORD-RULING-512 R4; CP-ranked; cap {s2.rb_stage2a_slots()}): {len(rb)} points;"
                 f" upper bound {ch[0]:.1f} / {ch[1]:.1f} core-h (S, M at {len(m_pts)}, N at {len(n_pts)};"
                 f" the R-B caps less GO-1's M {gm} and N {gn})")
        L += [f"  {p}: CP {sr._f(c, '{:.3f}')}" for p, c in rb]
    L.append("")
    L.append("# nothing else is printed (S2-R3): the 2a calls were computed for R4 eligibility and discarded")
    return ilines, L


# -- the final map (plan §5) ------------------------------------------------------------------------------------------- #

#: the interim's integrity file records the exclusions in force when it ran; the final rechecks R4 under those
EXCL_HEAD = "## exclusions in force (the R4 list's):"
INTERIM_INTEGRITY_REL = os.path.join("runs", "RBT-129", "stage2", "integrity-interim.txt")


def interim_exclusions(root: str):
    """The exclusions the committed interim ran under (its integrity file's ``EXCL_HEAD`` line), or None."""
    path = os.path.join(root, INTERIM_INTEGRITY_REL)
    if not os.path.exists(path):
        return None
    for line in open(path):
        if line.startswith(EXCL_HEAD):
            d = json.loads(line[len(EXCL_HEAD):])
            return d["quarantined"], d["crashed"], d["incomplete"]
    return None

STAGE1_RECORD = s2.STAGE1_TXT


def registered_stage1(path: str = STAGE1_RECORD) -> dict:
    """R-7: the accepted Stage-1 record's T1-T3 lines (L410-L412) and its per-point body and income calls."""
    lines = open(path).read().splitlines()
    out = {"T": {}, "calls": {}}
    for x in lines:
        for name in ("T1", "T2", "T3"):
            if x.startswith(f"  {name}: "):
                out["T"][name] = x[len(f"  {name}: "):]
    start = next(i for i, x in enumerate(lines) if x.startswith("## per-point table"))
    for x in lines[start + 1:]:
        if x.startswith("## "):
            break
        if x.startswith("  ") and not x.startswith("      ") and " | " in x:
            head, segs = x.split(" share ")[0].strip(), x.split(" | ")
            pid = head.split()[0]
            out["calls"][pid] = (head[len(pid):].strip(), segs[2].split()[0])
    return out


def t_line(model: dict, ps: dict, rej: set, name: str) -> str:
    return ("NOT TESTABLE (p = 1 in Holm)" if model.get(name) is None else
            f"stat {model[name][0]:.3f}, p {ps[name]:.4g}") + (" REJECTED" if name in rej else "")


def check_registered(record: dict, s1calls: dict, model: dict, ps: dict, rej: set) -> None:
    """R-7: the Stage-1 refit must reproduce the accepted record (T1-T3 and every Stage-1 call), or HELP."""
    for name in ("T1", "T2", "T3"):
        if t_line(model, ps, rej, name) != record["T"].get(name):
            raise Help(f"the Stage-1 refit's {name} ({t_line(model, ps, rej, name)}) is not the registered"
                       f" {record['T'].get(name)} (plan §5.5)")
    for p in sr.STAGE1_POINTS:
        got = (s1calls[p]["body"], s1calls[p]["income"]["call"])
        if record["calls"].get(p) != got:
            raise Help(f"the Stage-1 refit's calls at {p} {got} are not the accepted record's {record['calls'].get(p)}")


def final_halves(root: str, states: dict, mode: str, scan: dict, b2_pts) -> tuple:
    """({pid: [(stage, half)]}, {pid: [(stage, arms)]}): every point's halves under ``mode``."""
    s1 = stage1_arms(root, scan, mode)
    halves, arms = {}, {}
    for p in sr.STAGE1_POINTS:
        halves[p], arms[p] = [("1", assemble(root, "1", p, HALF1, s1[p], True))], [("1", s1[p])]
        if p in s2.RB_GO1_POINTS and "rb" in states:
            a = arms_for(states["rb"], p, HALF2, mode)
            halves[p].append(("rb", assemble(root, "rb", p, HALF2, a, True)))
            arms[p].append(("rb", a))
    for p in s2.STAGE2A_POINTS:
        a = arms_for(states["2a"], p, HALF1, mode)
        halves[p], arms[p] = [("2a", assemble(root, "2a", p, HALF1, a, True))], [("2a", a)]
        if p in b2_pts:
            a2 = arms_for(states["2b"], p, HALF2, mode)
            halves[p].append(("2b", assemble(root, "2b", p, HALF2, a2, True)))
            arms[p].append(("2b", a2))
    return halves, arms


def crashed_s_merges(root: str, states: dict) -> dict:
    """{pid: {j: (h alive at 59, d alive at 59) from the unit's ckpt60, or None for a crash before 59}} over every
    CRASHED S seed of every continuation stage (R-5: 2b(2a) included)."""
    out = {}
    for stage, sts in states.items():
        seeds = HALF1 if stage == "2a" else HALF2
        for pid in sorted({k[0] for k in sts}):
            a = arms_for(sts, pid, seeds, "include-flagged")
            for j in a["s_crashed"]:
                ck = unit_path(root, stage, pid, SEED_BASE + j, "ckpt60")
                v = None  # every completion: an INCOMPLETE seed's ckpt60 is never read (RB-HELP-1 C1)
                if j not in a["s_incomplete"] and os.path.exists(os.path.join(ck, "history.json")) and os.path.exists(os.path.join(ck, ".rbt129-done-ckpt60")):
                    h = sr.read_run(ck, root)["history"]
                    v = (sr.alive(h, H, sr.SEASON_MERGE) > 0, sr.alive(h, D, sr.SEASON_MERGE) > 0)
                out.setdefault(pid, {})[j] = v
    return out


_REGIME = {}


def _regime(d: str, root: str, windows) -> dict:
    key = (d, tuple(windows))
    if key not in _REGIME:
        _REGIME[key] = sr.guarded_regime(d, root, windows=windows)
    return _REGIME[key]


def per_birth(root: str, p: str, halves: list) -> dict:
    """C3-5 (plan §4.5): the uncensored per-birth income (births 180-238) and the censored one (240-299) beside it, each
    the mean over the point's income-valid seeds that have one."""
    vals = {"unc": {H: [], D: []}, "cen": {H: [], D: []}}
    for stage, h in halves:
        for j in h["x"]:
            res = _regime(unit_path(root, stage, p, SEED_BASE + j, "S"), root, PER_BIRTH_WINDOWS)
            for k in (H, D):
                try:
                    u = s2.per_birth_uncensored(sr.regime_window(res, k, s2.PER_BIRTH_WINDOW[0]))
                except s2.Stage2Help as e:
                    raise Help(f"{p}/{SEED_BASE + j}: {e}")
                c = sr.per_birth_income(sr.regime_window(res, k, sr.WINDOW[0]).get("net_per_birth"))
                if u is not None:
                    vals["unc"][k].append(u)
                if c is not None:
                    vals["cen"][k].append(c)
    return {w: {k: (sum(v) / len(v) if v else None) for k, v in d.items()} for w, d in vals.items()}


def y_bound(ys: list, s0s: list):
    """The n-seed mean y′'s bound under arbitrary missingness, the missing seeds each in [−s0, 1 − s0] (RULING item 4;
    rule §3.3), over the completed ``ys`` and the missing seeds' ``s0s``; None without every s0."""
    if any(s is None or not 0.0 <= s <= 1.0 for s in s0s):
        return None
    n, t = len(ys) + len(s0s), sum(ys)
    return (t - sum(s0s)) / n, (t + sum(1.0 - s for s in s0s)) / n


def m3_rows(calls: dict, points) -> dict:
    rows = {}
    for p in points:
        if calls[p]["body"] in sr.HABITABLE_OUT:
            continue
        c, pr, L_, s = sr.parse_point(p)
        for x in calls[p]["x"]:
            rows.setdefault((c, L_, s), ([], []))
            rows[(c, L_, s)][0].append(pr)
            rows[(c, L_, s)][1].append(x)
    return {row: sr.fieller(*v) for row, v in rows.items() if len(set(v[0])) >= 2}


def headline(calls: dict, t1: str, m3: dict) -> tuple:
    def corroborate(pid):
        c, _, L_, s = sr.parse_point(pid)
        return sr.m3_corroborates(m3.get((c, L_, s), {}))
    vpts = {p: {"body": c["body"], "income": c["income"]["call"], "lever": None, "vd": c["vd"], "m_arm": c["m_arm"],
                "resolving": c["resolving"]} for p, c in calls.items()}
    return sr.verdicts(vpts, t1, corroborate), vpts, corroborate


def compute_map(root: str, states: dict, mode: str, scan: dict, b2_pts, resolvable, t1: str, crashed: dict,
                everything: list) -> dict:
    """Everything the final map prints, under ``mode`` (rule §3.3: the whole map, recomputed)."""
    halves, arms = final_halves(root, states, mode, scan, b2_pts)
    calls, fam = call_map(halves, resolvable, crashed)  # the feasible-completion bound applies in both analyses
    m3 = m3_rows(calls, everything)
    verdict, vpts, corroborate = headline(calls, t1, m3)
    reg, lit, v5 = s2.v5_mark(vpts, t1, corroborate)
    nonreg = {label: sr.verdicts(vpts, t1, corroborate, **kw)
              for label, kw in (("EARNS at habitable points only", {"earns_habitable_only": True}),
                                ("verdict 5 ignoring EARNS-TIE", {"v5_ignores_tie": True}))}
    crash_s = {p: sum(len(a["s_crashed"]) for st, a in arms[p] if st != "1") for p in everything}
    affected = s2.crash_affected({p: c["income"]["call"] for p, c in calls.items()}, crash_s)
    sets = {k: [p for p, c in calls.items() if c["income"]["call"] == k] for k in ("EARNS-H", "EARNS-D")}
    pb = {p: per_birth(root, p, halves[p]) for p in everything}
    return {"halves": halves, "arms": arms, "calls": calls, "fam": fam, "m3": m3, "verdict": verdict, "vpts": vpts,
            "lit": lit, "v5": v5, "nonreg": nonreg, "affected": affected,
            "cmark": "CRASH-AFFECTED" if s2.verdict_crash_mark(sets, affected) else "", "pb": pb}


def render_map(R: dict, root: str, everything: list, model: dict, ps: dict, rej: set, s1: dict, mode: str) -> list:
    """[(key, text)]: every line of the final map whose value can differ between the two analyses, keyed."""
    calls, fam, out = R["calls"], R["fam"], []
    add = lambda k, t: out.append((k, t))
    add("v.head", R["verdict"][0])
    add("v.also", f"also holding: {', '.join(R['verdict'][1:]) or 'none'}")
    add("v.lit", f"NON-REGISTERED (C3-2 literal verdict 5): {R['lit']}")
    for label, v in R["nonreg"].items():
        add(f"v.nonreg.{label}", f"NON-REGISTERED, descriptive only ({label}): {', '.join(v)}")
    add("v.v5", f"V5 mark: {R['v5'] or 'none'}")
    add("v.crash", f"CRASH mark: {R['cmark'] or 'none'}")
    for p in everything:
        c, v = calls[p], calls[p]["merged"]
        inc, pb = c["income"], R["pb"][p]
        marg = sr.marginal(pb["unc"]) if inc["call"] in ("EARNS-H", "EARNS-D") else None
        marks = (" VARIANCE-DRIVEN" if c["vd"] else "") + (" CRASH-AFFECTED" if R["affected"].get(p) else "") \
            + (f" [body {c['crash_word']}]" if c.get("crash_word") else "")
        a = [x for _, x in R["arms"][p]]
        m_n = sum(len(x["m"]) for x in a)
        m_cr = sum(len(x["m_crashed"]) for x in a)
        m_out = sum(len(x["m_out"]) for x in a)
        n_all = sum(len(x["n"]) + len(x["n_out"]) for x in a)
        n_cr = sum(len(x["n_crashed"]) for x in a)
        ym = list(v["y_m"].values())
        s0s = [v["s0"].get(j) for x in a for j in x["m_out"]]
        bound = y_bound(ym, s0s) if m_out and ym else None
        mrow = (f"M {m_n - m_out} of {m_n}" + (f" ({m_cr} CRASHED" + (f", {m_out - m_cr} excluded as flagged" if m_out > m_cr else "")
                                               + ")" if m_out else "")) if m_n else "M --"
        nrow = f"N {n_all - sum(len(x['n_out']) for x in a)} of {n_all}" + (f" ({n_cr} CRASHED)" if n_cr else "") if n_all else "N --"
        add(f"p.{p}", f"{p:14s} {c['body']:24s} share {v['valid_share']}/{v['n']} income {v['valid_income']}/{v['n']}"
                      f" | x̄ {sr._f(inc['mean'])} p {sr._f(inc['p'], '{:.4f}')} tost {sr._f(inc['tost_p'], '{:.4f}')}"
                      f" ({inc['how']}, n {inc['n']}) | {inc['call']}{' MARGINAL' if marg else ''} LEVER not evaluated"
                      f" | {mrow} {nrow} | y′ {sr._f(sum(ym) / len(ym) if ym else None)} (descriptive)"
                      f"{' RESOLVING' if c['resolving'] else ''}{marks}")
        add(f"p.{p}.pb", f"    per-birth income (C3-5: births {s2.PER_BIRTH_WINDOW[0]}-{s2.PER_BIRTH_WINDOW[1]}; MARGINAL reads"
                         f" it) H {sr._f(pb['unc'][H])} D {sr._f(pb['unc'][D])}; the censored 240-299 figure beside it:"
                         f" H {sr._f(pb['cen'][H])} D {sr._f(pb['cen'][D])}")
        if m_out:
            add(f"p.{p}.ybound", f"    y′ bound under arbitrary missingness ({m_out} M seed(s) missing): "
                                 + (f"[{sr._f(bound[0])}, {sr._f(bound[1])}]" if bound else "not printable (s0 unknown)")
                                 + "; income flow has no logical bound")
        if v["m_seeds"]:
            inter = sr.interference(v)
            mf = list(v["m_flow"].values())
            add(f"p.{p}.m", f"    one-world column: M flow H {sr._f(sr._mean([x for x, _ in mf]))} D"
                            f" {sr._f(sr._mean([y for _, y in mf]))}; interference H {sr._f(inter[H][0])} (n {inter[H][1]})"
                            f" D {sr._f(inter[D][0])} (n {inter[D][1]}); g0 M {sr._f(sr._mean(list(v['g0'].values())), '{:.3f}')}")
        # Stage 1's descriptive list, kept (plan §8)
        add(f"p.{p}.d.merge", "    merge counts (H, D) per seed: " + " ".join(f"{SEED_BASE + j}:{a_}/{b_}" for j, (a_, b_) in sorted(v["counts59"].items())))
        for name in ("last_score", "survivors", "p0"):
            xs = [a_ - b_ for a_, b_ in (v["variants"][j][name] for j in v["variants"]) if a_ is not None and b_ is not None]
            add(f"p.{p}.d.{name}", f"    flow variant {name} (descriptive): x̄ {sr._f(sr._mean(xs))} over {len(xs)} seeds")
        for k in (H, D):
            ss = [v["s_summary"][j][k] for j in sorted(v["s_summary"])]
            add(f"p.{p}.d.s.{k}", f"    S {k} (descriptive): alive at 299 {sr._f(sr._mean([x['alive299'] for x in ss]), '{:.1f}')},"
                                  f" births {sr._f(sr._mean([x['births'] for x in ss]), '{:.1f}')} and deaths"
                                  f" {sr._f(sr._mean([x['deaths'] for x in ss]), '{:.1f}')} in 240-299, extinct on"
                                  f" {sum(1 for x in ss if x['extinct_season'] is not None)} seeds")
        if v["y_m"]:
            ls = [x for x in v["living_share"].values() if x is not None]
            add(f"p.{p}.d.living", f"    M share of the living, 240-299 (descriptive; O-4): {sr._f(sr._mean(ls), '{:.3f}')} over"
                                   f" {len(ls)} seeds; empty world on {len(v['living_share']) - len(ls)}")
        if v["y_n"]:
            add(f"p.{p}.d.n", "    N runs' y′ (descriptive): " + ", ".join(f"{SEED_BASE + j} ({sr.null_kind(j)}-null) {sr._f(y)}"
                                                                         for j, y in sorted(v["y_n"].items())))
        for arm_, reg in (("S", v["regime_s"]), ("M", v["regime_m"])):
            if reg:
                cells = []
                for k in (H, D):
                    for i, (lo, _) in enumerate(sr.REGIME_WINDOWS):
                        vals = [reg[j][k][i] for j in reg]
                        cells.append(f"{k[0]}{lo}: {sr._f(sr._mean([x[1] for x in vals]), '{:.2f}')}/"
                                     f"{sr._f(sr._mean([x[2] for x in vals]), '{:.2f}')}/{sr._f(sr._mean([x[3] for x in vals]), '{:.1f}')}")
                add(f"p.{p}.d.regime.{arm_}", f"    regime {arm_} (n {len(reg)}; window-local saturation/viability/alive;"
                                              " descriptive): " + "  ".join(cells))
        if v["void_seeds"]:
            add(f"p.{p}.void", f"    removed from n: seeds {', '.join(str(SEED_BASE + j) for j in sorted(v['void_seeds']))}"
                               f" ({', '.join(sorted({w for _, x in R['arms'][p] for w, ks in (('CRASHED', [j for j in x['s_crashed'] if j not in x.get('s_incomplete', [])]), ('INCOMPLETE, ruled', x.get('s_incomplete', [])), ('excluded as flagged', x['s_excluded'])) if ks})) or 'ruled K-SALT VOID'})")
    # families (plan §5.2, §5.3)
    add("f.income", f"income EARNS and TIE: {len(fam['tested'])} points tested; BH EARNS rejects"
                    f" {', '.join(sorted(fam['earns_bh'])) or 'none'}; BH TIE rejects {', '.join(sorted(fam['tie_bh'])) or 'none'}")
    add("f.share", f"share families: {len(fam['share_tested'])} points (O-22); WIN rejects {', '.join(sorted(fam['wins'])) or 'none'};"
                   f" TIE rejects {', '.join(sorted(fam['share_tie'])) or 'none'}")
    corr = sr.cross_correlation({p: dict(calls[p]["merged"]["x"]) for p in fam["tested"]})  # paired by seed
    add("f.corr", f"cross-point correlation of x (pairs with >= 3 common seeds): mean {sr._f(corr[0], '{:.3f}')}"
                  f" max {sr._f(corr[1], '{:.3f}')} over {corr[2]} pairs")
    if corr[0] is not None and corr[0] > 0.3:
        by_rej = sr.by({p: calls[p]["income"]["p"] for p in fam["tested"]})
        add("f.by", "BY beside BH: " + (", ".join(f"{p} {calls[p]['income']['call']} holds under BH only" for p in fam["tested"]
                                               if calls[p]["income"]["call"] in ("EARNS-H", "EARNS-D") and p not in by_rej) or "every EARNS call holds under BY"))
    for st, (ok, m, t, pv) in sorted(fam["pooled_k2"].items()):
        add(f"f.k2.{st}", f"K2 pooled, stage {st}: {'PASS' if ok else 'FAIL: the share layer is VOID at its N points (C3-1)'}"
                          f" (mean {sr._f(m)}, t {sr._f(t, '{:+.2f}')}, p {sr._f(pv, '{:.4f}')})")
    for p, w in sorted(fam["k2pt"].items()):
        add(f"f.k2pt.{p}", f"K2 {p}: {w} ({len(fam['k2_runs'][p])} runs)")
    for k in (H, D):
        add(f"f.null.{k}", f"pooled null {k}-null: σ̂² {sr._f(fam['pooled'][k][0], '{:.4f}')}, df {fam['pooled'][k][1]}")
    add("f.cont", f"CONTINGENT: {'callable' if fam['contingent_callable'] else 'not callable'} (df {fam['df_null']};"
                  " never callable on the final map without RBT-118's anchor nulls, finding 15)")
    for p in everything:
        if calls[p]["share"]:
            add(f"f.res.{p}", f"RESOLVING {p}: {calls[p]['resolving']}")
    # M1 and M4 (plan §5.4)
    w = s2.m4_weights(sr.STAGE1_POINTS, s2.STAGE2A_POINTS)
    for s in ("G", "L"):
        for block, pts in (("Stage-1", sr.STAGE1_POINTS), ("Stage-2a", s2.STAGE2A_POINTS)):
            grp = [p for p in pts if p.endswith("-" + s)]
            cnt, inc = {}, {}
            for p in grp:
                b = "NOT RUN" if p in sr.ANCHORS_STAGE1 and calls[p]["body"].startswith("RBT-118") else calls[p]["body"]
                cnt[b] = cnt.get(b, 0) + 1
                inc[calls[p]["income"]["call"]] = inc.get(calls[p]["income"]["call"], 0) + 1
            add(f"m1.{s}.{block}", f"M1 {s} {block} ({len(grp)}): body " + ", ".join(f"{k} {n}" for k, n in sorted(cnt.items()))
                                   + "; income " + ", ".join(f"{k} {n}" for k, n in sorted(inc.items())))
        share = {}
        for p in everything:
            if p.endswith("-" + s):
                share[calls[p]["body"]] = share.get(calls[p]["body"], 0.0) + w[p]
        add(f"m4.{s}", f"M4 {s} (the quarter rule, O-17; descriptive): " + ", ".join(f"{k} {v:.3f}" for k, v in sorted(share.items())))
    # M2 (plan §5.4, §5.5): the registered fit is Stage 1's (checked, R-7); the sensitivity fit and the share model
    sens_seeds = []
    for p in everything:
        if calls[p]["body"] in sr.HABITABLE_OUT:
            continue
        hs = calls[p]["halves"]
        if len(hs) == 2 and len(hs[0]) >= 2 and len(hs[1]) >= 2:
            shift = s2.median_unbiased(hs[0], hs[1]) - sum(calls[p]["x"]) / len(calls[p]["x"])
            sens_seeds += [(p, x + shift) for x in calls[p]["x"]]
        else:
            sens_seeds += [(p, x) for x in calls[p]["x"]]
    smodel = sr.world_model(sens_seeds)
    add("m2.sens", f"M2 sensitivity fit (Stage-2a points and extensions; MUE at extended points, O-14): status {smodel['status']}"
                   + (f"; T1 χ² {smodel['T1'][0]:.3f}, df {smodel['T1'][1]}, p {smodel['T1'][2]:.4g}" if smodel.get("T1") else "; T1 NOT TESTABLE"))
    for scope in ("all", "habitable"):
        pts = s2.share_model_points({p: {"m_arm": calls[p]["m_arm"], "body": calls[p]["body"]} for p in everything}, scope=scope)
        seeds, g0c = [], {}
        for p in pts:
            v = calls[p]["merged"]
            g = [x for x in v["g0"].values() if x is not None]
            if g:
                g0c[p] = sum(g) / len(g)
            seeds += [(p, sr.share_logit_change(y, v["s0"][j])) for j, y in v["y_m"].items() if j in v["s0"]]
        sm = sr.world_model(seeds, g0c)
        add(f"m2.share.{scope}", f"M2 share model ({'registered: every Stage-1-grid point with an M arm' if scope == 'all' else 'NON-REGISTERED: habitable only'};"
                                 f" C3-4; descriptive): status {sm['status']}; share Wald T1 "
                                 + (f"χ² {sm['T1'][0]:.3f}, df {sm['T1'][1]}, p {sm['T1'][2]:.4g}" if sm.get("T1") else "NOT TESTABLE"))
    # M3 (plan §5.4)
    for row, f in sorted(R["m3"].items()):
        add(f"m3.{row}", f"M3 final {row}: p* {sr._f(f.get('p_star'), '{:.4f}')} {f['kind']}"
                         + (f" [{f['lo']:.4f}, {f['hi']:.4f}]" if f["kind"] == "bounded" else ""))
    # M6, M7 (plan §5.4)
    decided = [p for p in everything if calls[p]["body"] in ("H-WIN", "D-WIN")]
    if decided:
        def msign(p):
            mf = [a_ - b_ for a_, b_ in calls[p]["merged"]["m_flow"].values() if a_ is not None and b_ is not None]
            return "H" if sr._mean(mf) and sr._mean(mf) > 0 else "D"
        k = sr.cohen_kappa([calls[p]["body"][0] for p in decided], [msign(p) for p in decided])
        add("m6", f"M6 concordance: κ(share sign, M income sign) {sr._f(k, '{:.3f}')} over {len(decided)} points")
    else:
        add("m6", "M6 concordance: no decided share call")
    rows = {}
    for p in everything:
        c, pr, L_, s = sr.parse_point(p)
        rows.setdefault(("price", c, L_, s), []).append((pr, p))
        rows.setdefault(("clutter", pr, L_, s), []).append((c, p))
    for key, members in sorted(rows.items(), key=lambda kv: str(kv[0])):
        if len(members) >= 3:
            vals = [calls[p]["income"]["mean"] for _, p in sorted(members)]
            n = sr.sign_changes(vals)
            add(f"m7.{key}", f"M7 {key}: {n} sign changes" + (" (more than one: listed)" if n > 1 else "")
                             + f" [{' '.join(sr._f(x) for x in vals)}]")
    # the scorecard (plan §5.7, §4.3)
    sc = sr.scorecard({p: calls[p] for p in everything}, model, rej, R["m3"], R["verdict"])
    for i, x in enumerate(sc[1:]):
        add(f"sc.{i}", x.strip())
    item2 = s2.scorecard_item2({p: {"n_ran": bool(calls[p]["share"]), "body": calls[p]["body"],
                                    "resolving": calls[p]["resolving"]} for p in everything})
    add("sc.item2", f"item 2 (C3-3, registered as the pre-data code scored it): {item2['registered']}")
    add("sc.gated", item2["gated"])
    add("sc.npts", item2["n_points"])
    return out


def final(root: str = ROOT, restore=None, resolvable=None, on_integrity=None, excl: tuple = None, crash_log=None,
          record: dict = None) -> tuple:
    """(integrity lines, final-map lines): plan §5.2-§5.7 under include-flagged, the whole map again under
    exclude-known-flagged, and every line that differs marked OVERFLOW-SENSITIVE beside its primary (rule §3.3)."""
    excl = ruled_exclusions() if excl is None else excl
    restore = guarded_restore(root, restore, excl[0])
    if resolvable is None:
        resolvable = sr.scaled_resolvable()[0]
    record = registered_stage1() if record is None else record
    b2a = s2.ruled("2B2A:")
    interim_txt = os.path.join(root, s2b.INTERIM_REL)
    points = None
    if "COMMITTED" in b2a:
        try:
            points = s2b.parse_interim(open(interim_txt).read())
        except (OSError, SystemExit) as e:
            raise Help(f"{s2b.INTERIM_REL}: no committed interim output with an R4 list ({e}): 2b(2a) cannot be read")
    stage_jobs = {"2a": emission("2a"), "rb": emission("rb")}
    if points:
        stage_jobs["2b"] = emission("2b", points)
    ilines, states, pattern = integrity(root, stage_jobs, restore, excl, crash_log)
    epa = s2.registered_epa()
    scan_lines, scan = scan_states(root, restore, epa)
    ilines = ilines + scan_lines
    if points:  # R-4: lanes/S2B is exactly the emission from the committed interim output
        try:
            s2b.check_s2b(os.path.join(root, "runs", "RBT-129", "lanes", s2b.NAME), points, excl=excl)
        except SystemExit as e:
            raise Help(f"lanes/{s2b.NAME} is not the emission from the committed interim output (exit {e.code})")
    if on_integrity:
        on_integrity(ilines)
    restore_stage1(root, restore)
    for st, sts in states.items():
        restore_continuation(root, st, sts, restore)
    later = []
    if "COMMITTED" in b2a:  # R-4: the committed interim's R4 list is the one the 2a data give, under its own exclusions
        iexcl = interim_exclusions(root)
        if iexcl is None:
            raise Help(f"{INTERIM_INTEGRITY_REL}: no committed interim integrity file with its exclusions: R4 cannot be rechecked")
        try:
            jobs2a = stage_jobs["2a"]
            cls = classify(root, "2a", jobs2a, restore, iexcl, epa, crash_log)
            states_i = arm_states(root, "2a", jobs2a, cls, epa)[0]
        except sr.QuarantineRefusal as e:
            raise Help(f"the R4 recheck must read a run quarantined after the interim ({e}): the coordinator rules")
        again = tuple(p for p, _ in r4_list(root, states_i, resolvable))
        if again != (points or ()):
            raise Help(f"the committed interim's R4 list {list(points or ())} is not the one the 2a data give {list(again)}"
                       " under the interim's exclusions")
        now, then = _excl3(excl), _excl3(iexcl)
        later = ([f"QUARANTINE: {x}" for x in now[0] if x not in then[0]] + [f"CRASHED: {x}" for x in now[1] if x not in then[1]]
                 + [f"INCOMPLETE: {k} {v}" for k, v in now[2].items() if k not in then[2]])
    everything = list(sr.STAGE1_POINTS) + list(s2.STAGE2A_POINTS)
    # the registered M2 and Holm: Stage 1's, refit and checked against the accepted record (plan §5.5; R-7)
    s1arms = stage1_arms(root)
    s1h = {p: [("1", assemble(root, "1", p, HALF1, s1arms[p]))] for p in sr.STAGE1_POINTS}
    s1calls = call_map(s1h, resolvable)[0]
    hab1 = [p for p in sr.STAGE1_POINTS if s1calls[p]["body"] not in sr.HABITABLE_OUT]
    model = sr.world_model([(p, x) for p in hab1 for x in s1calls[p]["x"]])
    rej, ps = sr.map_holm(model)
    check_registered(record, s1calls, model, ps, rej)
    t1 = sr.t1_state(model, rej)
    crashed = crashed_s_merges(root, {k: v for k, v in states.items() if k != "1"})
    b2_pts = set(points or ())
    R = {mode: compute_map(root, states, mode, scan, b2_pts, resolvable, t1, crashed, everything) for mode in s2.OVERFLOW_RULES}
    prim = render_map(R["include-flagged"], root, everything, model, ps, rej, None, "include-flagged")
    sens = dict(render_map(R["exclude-known-flagged"], root, everything, model, ps, rej, None, "exclude-known-flagged"))
    head_sens = R["exclude-known-flagged"]["verdict"][0] != R["include-flagged"]["verdict"][0]
    marks = " ".join(m for m in (R["include-flagged"]["v5"], "OVERFLOW-SENSITIVE" if head_sens else "",
                                 R["include-flagged"]["cmark"]) if m)

    def show(key, text):
        if key not in sens:
            return text + "  [OVERFLOW-SENSITIVE; exclude-known-flagged: absent]"
        if sens[key] != text:
            return text + f"  [OVERFLOW-SENSITIVE; exclude-known-flagged: {sens[key].strip()}]"
        return text
    keyed = dict(prim)
    L = ["# RBT-129 Stage 2 final map (STAGE2-PLAN.md §5; DESIGN §7-§8)", f"# claim: {sr.CLAIM}",
         f"# share-layer lines are read {sr.SHARE_QUAL}; earns, not persists; primary: include-flagged;"
         " sensitivity: exclude-known-flagged (rule §3.3), every difference marked beside its primary", ""]
    L.append("## §8 headline (final map; COORD-RULING-512 R1 + R2 + R3; C3-2 registered reading)")
    L.append(f"  {keyed['v.head']}" + (f"  [{marks}]" if marks else "")
             + (f"  [exclude-known-flagged: {R['exclude-known-flagged']['verdict'][0]}]" if head_sens else ""))
    for k in [k for k, _ in prim if k.startswith("v.") and k != "v.head"]:
        L.append("  " + show(k, keyed[k]))
    L.append(f"  exclude-known-flagged map: {R['exclude-known-flagged']['verdict'][0]} (the UNSCANNED Stage-1 units are unchecked)")
    L.append("  perception: PERCEPTION NOT MEASURED (the perception layer is unreadable at a = 6); LEVER not evaluated")
    if pattern:
        L.append("  overflow is a pattern (rule §3.4): see the integrity file; the OVERFLOW-SENSITIVE marks are on every affected line")
    sections = (("p.", "## per-point table (final calls; income at n = 8, or combined over 16 at extended points; MARGINAL on EARNS calls, C3-5)"),
                ("f.", "## families (BH once per family, q = 0.10; plan §5.2, §5.3)"),
                ("m1.", "## M1 call counts (Stage-2a points in their own block; plan §5.4)"),
                ("m4.", "## M4 area shares"),
                ("m2.", "## M2: the registered fit is Stage 1's (below); the sensitivity fit and the share model"),
                ("m3.", "## M3 break-evens, final map (corroborates §8; O-18)"),
                ("m6", "## M5 perception map: NOT MEASURED; M6 concordance"),
                ("m7.", "## M7 monotonicity of x̄ along every row of the final map"),
                ("sc.", "## §12 registered predictions: scorecard, final map (PROVISIONAL where §8 is)"))
    for prefix, title in sections:
        L.append("")
        L.append(title)
        if prefix == "m2.":
            for name in ("T1", "T2", "T3"):
                L.append(f"  {name}: {record['T'][name]} (registered Stage-1 fit, L410-L412; refit and checked, R-7)")
            L.append(f"  T4: NOT MEASURED (p = 1); Holm is Stage 1's, not re-run: rejected {', '.join(sorted(rej)) or 'none'}"
                     " (plan §5.5)")
        for k, text in prim:
            if k.startswith(prefix):
                L.append("  " + show(k, text))
        for k in sorted(set(sens) - set(keyed)):
            if k.startswith(prefix):
                L.append(f"  [OVERFLOW-SENSITIVE; exclude-known-flagged only] {sens[k].strip()}")
    # the Stage-1-only views (plan §5.4, §5.7)
    m3_s1 = m3_rows(s1calls, sr.STAGE1_POINTS)
    v1 = headline(s1calls, t1, m3_s1)[0]
    L.append("")
    L.append("## M3 break-evens, Stage-1 points only (descriptive)")
    L += [f"  M3 Stage-1 {row}: p* {sr._f(f.get('p_star'), '{:.4f}')} {f['kind']}"
          + (f" [{f['lo']:.4f}, {f['hi']:.4f}]" if f["kind"] == "bounded" else "") for row, f in sorted(m3_s1.items())]
    L.append("## §12 scorecard for the Stage-1 points (plan §5.7)")
    L += sr.scorecard({p: s1calls[p] for p in sr.STAGE1_POINTS}, model, rej, m3_s1, v1)[1:]
    it1 = s2.scorecard_item2({p: {"n_ran": bool(s1calls[p]["share"]), "body": s1calls[p]["body"],
                                  "resolving": s1calls[p]["resolving"]} for p in sr.STAGE1_POINTS})
    L += [f"  item 2 (C3-3): {it1['registered']}", f"  {it1['gated']}", f"  {it1['n_points']}"]
    L.append("")
    L.append("## exclusions ruled after the interim (in force in this map, not in the R4 recheck)")
    L += [f"  {x}" for x in later] or ["  none"]
    L.append("")
    L.append("# exclusions: K-SALT VOID (ruled), validity, CRASHED, INCOMPLETE and EXCLUDED (rule §4.5; their seeds leave n), and under"
             " exclude-known-flagged only the OVERFLOWED and UNLOGGED arms; nothing winsorised or re-weighted")
    return ilines, L


# -- main ------------------------------------------------------------------------------------------------------------ #

def write(path: str, lines: list) -> None:
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("step", choices=("interim", "final"))
    ap.add_argument("--go")
    a = ap.parse_args(argv)
    why = s2.refusal(a.step, a.go)
    if why:
        print(f"refused: {why}.  Nothing was read.", file=sys.stderr)
        return 9
    try:
        fn = interim if a.step == "interim" else final
        _, lines = fn(ROOT, on_integrity=lambda il: write(os.path.join(HERE, f"integrity-{a.step}.txt"),
                                                          [f"# go: {a.go}"] + il + ["INTEGRITY PASS"]))
    except (Help, sr.ReadoutHelp) as e:
        print(f"HELP: {e}", file=sys.stderr)
        return 1
    write(os.path.join(ROOT, s2b.INTERIM_REL) if a.step == "interim" else os.path.join(HERE, "stage2_final.txt"), lines)
    return 0


if __name__ == "__main__":
    sys.exit(main())
