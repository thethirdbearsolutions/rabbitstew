#!/usr/bin/env python3
"""RBT-129 Stage 2 (2a, 2b and the final map): the script SKELETON of ``STAGE2-PLAN.md`` (pre-data).

    python3 runs/RBT-129/stage2-plan/stage2_readout.py interim --go RBT129-S2-INTERIM-GO-1  -> stage2a_interim.txt
    python3 runs/RBT-129/stage2-plan/stage2_readout.py final   --go RBT129-S2-FINAL-GO-1    -> stage2_final.txt

Each step runs its own integrity first (plan §7) and writes it before anything else.

**The locks** (``RULINGS-CITED-S2.md``; S2-R3).  A step refuses unless all of these are ruled and well formed:
- its own GO line (``GO-ID-INTERIM:`` or ``GO-ID-FINAL:``);
- ``GO-ID-2A:`` (2a was authorised), which may open only after ``2B2A: COMMITTED | DECLINED`` is registered;
- ``OVERFLOW-RULE:`` and ``BUILD-SHA256:`` (64 hex digits).
Today each is ``-PENDING:``, which never matches.  It also refuses while any local ref names a quarantined unit, or
when the registered inputs fail to check.

**What is committed now (plan §11).** Every rule that a Stage-2 call, family, map statistic or verdict depends on is a
pure function below, tested on synthetic numbers in ``tests/test_rbt129_stage2_plan.py``.  The readers of continuation
run directories and the drivers are **not** written yet: they need the continuation lane format (the continuations
tooling).  Plan §11 makes the full drivers, with an end-to-end synthetic-tree test, a precondition of the first GO (as
COORD-RULING-512 R5 did for Stage 1).  Until then the drivers raise.

Everything the Stage-1 readout already registered is **imported, not re-implemented**: the statistics, BH, Holm, the
body and income calls, the verdict logic, the quarantine guard (``runs/RBT-129/stage1-readout/stage1_readout.py``,
blob pinned in the plan).  Section numbers below are the plan's.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUNS))
S1_DIR = os.path.join(RUNS, "stage1-readout")
S1_SCRIPT = os.path.join(S1_DIR, "stage1_readout.py")
STAGE1_TXT = os.path.join(S1_DIR, "stage1_readout.txt")
CENSUS_TXT = os.path.join(RUNS, "stageP0-readout", "stageP0_readout.txt")
RULINGS = os.path.join(HERE, "RULINGS-CITED-S2.md")


def _load_stage1():
    spec = importlib.util.spec_from_file_location("stage1_readout", S1_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sr = _load_stage1()
H, D = sr.H, sr.D

# -- 1 the registered inputs (plan §1) ------------------------------------------------------------------------------ #

#: sha256 of the accepted Stage-1 record (COORD-RULING-517 C1; run adversary's reproduction)
STAGE1_TXT_SHA256 = "beb515aa7d745e3b98a58c4f0a116b423017476ed39a0e6fb9379e4214f50259"

#: R-A's selection as printed (stage1_readout.txt L441), in its printed order
STAGE2A_POINTS = ("c05-p080-U-G", "c1-p053-U-G", "c05-p030-U-G", "c0-p018-HP-G", "c15-p030-U-G", "c15-p010-U-G",
                  "c1-p018-U-G", "c2-p053-HP-G", "c1-p053-U-L", "c1-p018-HP-L", "c1-p018-U-L", "c1-p018-PW-L")

#: R-B's Stage-1 list as printed (L443-L451); GO-ID RBT129-RB-GO-1, tooled by another session
RB_GO1_POINTS = ("c0-p010-HP-G", "c1-p010-HP-G", "c2-p030-U-G", "c2-p010-HP-G", "c1-p030-U-G", "c1-p030-HP-L",
                 "c1-p010-U-G", "c1-p010-HP-L", "c1-p010-U-L")

SEEDS_HALF1 = tuple(range(1, 9))     # 129001-129008, salts as lanes/1/launch.txt
SEEDS_HALF2 = tuple(range(9, 17))    # 129009-129016, screened (F5)
RB_CAP = 20
M_CAP = {"2a": 4, "2b": 6}           # DESIGN 5.2 item 1 (2b: shared with R-B GO-1)
N_CAP = {"2a": 2, "2b": 2}
M_G0_MAX, N_G0_MAX = 1.0, 0.8
CORE_S = (23.35, 43.72)              # the pilot's core-s per arm-season (T11), low / high
SEASONS_S, SEASONS_ADOPTED, SEASONS_FORK = 300, 240, 240



class Stage2Help(RuntimeError):
    """A condition the plan routes to the coordinator (a HELP wake): nothing further is read."""


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def parse_ra_selected(txt: str) -> tuple:
    """The R-A selection line of the Stage-1 readout (plan §1.1)."""
    in_ra = False
    for line in open(txt):
        if line.startswith("## R-A"):
            in_ra = True
        elif line.startswith("## "):
            in_ra = False
        elif in_ra and line.strip().startswith("selected:"):
            return tuple(x.strip() for x in line.split(":", 1)[1].split(","))
    raise Stage2Help("no R-A selection line in the Stage-1 readout")


def parse_rb_list(txt: str) -> tuple:
    """R-B's eligible list (registered reading, R4) as printed, in CP order (plan §1.1)."""
    out, in_rb = [], False
    for line in open(txt):
        if line.startswith("## R-B"):
            in_rb = True
            continue
        if in_rb:
            m = re.match(r"\s+(c\d+-p\d+-\w+-[GL]): CP ", line)
            if m:
                out.append(m.group(1))
            elif line.startswith("## ") or "literal list" in line:
                break
    return tuple(out)


def check_inputs(stage1_txt: str = STAGE1_TXT) -> list:
    """Problems with the registered inputs (empty = PASS)."""
    bad = []
    if sha256_file(stage1_txt) != STAGE1_TXT_SHA256:
        bad.append("stage1_readout.txt is not the accepted record (sha256)")
    if parse_ra_selected(stage1_txt) != STAGE2A_POINTS:
        bad.append("R-A selection differs from STAGE2A_POINTS")
    if parse_rb_list(stage1_txt) != RB_GO1_POINTS:
        bad.append("R-B list differs from RB_GO1_POINTS")
    return bad


# -- 2 what runs: the M/N gate and the budget (plan §2) ------------------------------------------------------------- #

def mn_gate(points, census: dict, m_cap: int, n_cap: int, valid: dict = None, anchors=sr.ANCHORS) -> tuple:
    """DESIGN 5.2 as amended by T5 and the #500 ruling, applied to ``points`` (plan §2.3): M where census g0 <= 1.0,
    the designed fauna not FOUNDING-FAIL in the census, not an anchor; lowest g0 first (ties by id), up to ``m_cap``;
    N at the M-admitted points with g0 <= 0.8, in the same order, up to ``n_cap``.  With ``valid`` ({point: number of
    seeds valid at the merge}), a point with 0 valid seeds frees its slot (T5, DATA-INFORMED at Stage 1).  Before the
    S60s exist (``valid`` None) the lists are the upper bound.  Returns (M points, N points, rows)."""
    rows = []
    for pid in points:
        g0s = census["points"].get(pid, (None, "--"))[1]
        g0 = None if g0s in ("--", None) else float(g0s)
        why = ("anchor" if pid in anchors else "census g0 unknown" if g0 is None else
               "designed FOUNDING-FAIL in the census" if pid in census["ff"].get(D, set()) else
               "census g0 > 1.0" if g0 > M_G0_MAX else None)
        rows.append((g0 if g0 is not None else math.inf, pid, why))
    rows.sort()
    m, n = [], []
    for g0, pid, why in rows:
        if why or len(m) >= m_cap:
            continue
        if valid is not None and valid.get(pid, 0) == 0:
            continue
        m.append(pid)
        if g0 <= N_G0_MAX and len(n) < n_cap:
            n.append(pid)
    return m, n, rows


def core_h(arm_seasons: float, core_s=CORE_S) -> tuple:
    return tuple(arm_seasons * c / 3600.0 for c in core_s)


def budget(m2a: int, n2a: int, rb2a_points: int, m2b: int, n2b: int, resim_129001: bool = True) -> dict:
    """Upper-bound core-h (low, high) of the arms this plan registers (plan §2.5).  2a: S at 12 points x 8 seeds x 300.
    With ``resim_129001`` (O-2, S2-R4: REQUIRED, pending the owner's cost OK) 129001's S 0-59 is re-simulated on the
    build and adopted only on byte equality with the census, so every 2a S chain is 300 arm-seasons; without it,
    129001 adopts the census S60 (240).  M and N at every seed (an upper bound: they fork only on seeds valid at the
    merge), 240 arm-seasons each.  2b for Stage-2a points: S at ``rb2a_points`` x 8 fresh seeds x 300; M/N likewise.
    K-SALT is a file comparison and costs nothing."""
    s2a = len(STAGE2A_POINTS) * (7 * SEASONS_S + (SEASONS_S if resim_129001 else SEASONS_ADOPTED))
    out = {"2a S": core_h(s2a), "2a M": core_h(m2a * 8 * SEASONS_FORK), "2a N": core_h(n2a * 8 * SEASONS_FORK),
           "2b(2a) S": core_h(rb2a_points * 8 * SEASONS_S), "2b(2a) M": core_h(m2b * 8 * SEASONS_FORK),
           "2b(2a) N": core_h(n2b * 8 * SEASONS_FORK)}
    out["2a total"] = tuple(sum(out[k][i] for k in ("2a S", "2a M", "2a N")) for i in (0, 1))
    out["2b(2a) total"] = tuple(sum(out[k][i] for k in ("2b(2a) S", "2b(2a) M", "2b(2a) N")) for i in (0, 1))
    out["total"] = tuple(out["2a total"][i] + out["2b(2a) total"][i] for i in (0, 1))
    return out


def rb_stage2a_slots(rb_go1: int = len(RB_GO1_POINTS), cap: int = RB_CAP) -> int:
    """DESIGN 4.2 (M12): Stage-2a points are extended from what remains of the cap of 20, Stage-1 points first."""
    return max(0, cap - rb_go1)


# -- 3 the continuation build and overflow handling (plan §3; S2-R2) ------------------------------------------------ #
#
# The rule itself is the coordinator's standalone continuation ruling (built from the tooling session's
# OVERFLOW-RULE-DRAFT and this plan; S2-R2), cited, not redefined here.  What follows is how the Stage-2 readout reads
# the registered build's per-run log (``epa_overflow.jsonl``: one O_APPEND write per line; COORD-RULING-520 D3, FC-2,
# FC-3) and maps its states onto every Stage-2 statistic.  No destructor-written stats file is used (finding 1).
#
# The log's lines, as the continuations tooling writes them (``launch/epa_ecology.py``), plus the two fields this plan
# asks the tooling to add (plan §3.2; PENDING its registration):
#   {"start": ..., "pid": .., "attempt": k, "workers": W, "build": .., "libmujoco_sha256": ..}   one per attempt
#   {"season": s, "pid": ..}                                                                    as season s begins
#   {"event": "near" | "overflow", "nedges": n, ...}                                            horizon >= 17 / > 24
#   {"exit": {"attempt": k, "code": C, "signal": S, "native": bool}}                            run-lane, after exit
#   {"hist": {...}, ...}                                                                         histograms (not read)

#: unit states (plan §3.3).  OVERFLOWED is the draft's name for a flagged unit; CRASHED as RULING item 1
CLEAN, OVERFLOWED, UNLOGGED, CRASHED, UNSCANNED = "CLEAN", "OVERFLOWED", "UNLOGGED", "CRASHED", "UNSCANNED"
FLAGGED_STATES = (OVERFLOWED, UNLOGGED)        # UNLOGGED is treated as OVERFLOWED (the draft §5.2)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def parse_epa_log(lines) -> dict:
    """Attempts, in file order, from the run's ``epa_overflow.jsonl``.  Each attempt: {"attempt", "workers",
    "sha", "seasons": {season: overflow count}, "overflow_any": events anywhere in the attempt, "exit": {...} | None}.
    Kept data follow the tooling's ``read_log``: a season counts from its last attempt.  A line cut by a kill mid-write
    is counted in ``bad`` and skipped.  Reads no outcome: event lines are counted, never read for values."""
    attempts, cur, season, bad = [], None, None, 0
    for raw in lines:
        try:
            rec = json.loads(raw)
        except ValueError:
            bad += 1
            continue
        if "start" in rec:
            cur = {"attempt": rec.get("attempt"), "workers": rec.get("workers"), "sha": rec.get("libmujoco_sha256"),
                   "seasons": {}, "overflow_any": 0, "exit": None}
            attempts.append(cur)
            season = None
        elif "exit" in rec:
            ex = rec["exit"]
            hit = [a for a in attempts if a["attempt"] == ex.get("attempt")]
            if not hit:
                raise Stage2Help("an exit line with no matching attempt")
            hit[-1]["exit"] = ex
        elif "season" in rec and "event" not in rec:
            season = rec["season"]
            if cur is not None:
                cur["seasons"].setdefault(season, 0)
        elif rec.get("event") in ("near", "overflow"):
            if cur is None:
                raise Stage2Help("an EPA event before any start line")
            if rec["event"] == "overflow":
                cur["seasons"][season] = cur["seasons"].get(season, 0) + 1
                cur["overflow_any"] += 1
    kept = {}
    for a in attempts:
        kept.update(a["seasons"])
    return {"attempts": attempts, "kept": kept, "bad": bad}


def attested(attempt: dict) -> bool:
    """S2-R2: an attempt's abnormal exit is attested when an overflow record of the **same unit and attempt id** was
    logged before that attempt's exit line, and the exit is native (a signal inside the process or a dead pool worker)."""
    ex = attempt.get("exit") or {}
    return attempt["overflow_any"] >= 1 and bool(ex.get("native"))


def crash_attested(log: dict) -> bool:
    """RULING item 5's two counting attempts (the last two, both native exits; one at workers = 1), each attested."""
    natives = [a for a in log["attempts"] if (a.get("exit") or {}).get("native")]
    if len(natives) < 2:
        raise Stage2Help("CRASHED needs two native exits in a row (RULING item 5)")
    two = natives[-2:]
    if two[0] is not log["attempts"][log["attempts"].index(two[1]) - 1]:
        raise Stage2Help("the two native exits are not consecutive attempts (RULING item 5)")
    if not any(a.get("workers") == 1 for a in two):
        raise Stage2Help("neither counting attempt ran at WORKERS=1 (RULING item 5)")
    return all(attested(a) for a in two)


def unit_state(log: dict, seasons_run, crashed: bool = False, registered_sha: str = None) -> str:
    """Plan §3.3.  ``seasons_run``: the seasons the unit ran (from its state, not its outcomes).
    - CRASHED: RULING item 5's counting rule holds and both counting attempts are attested (S2-R2).  An unattested crash
      is a crash under RULING item 5 as registered: HELP (the M/N stop, or the S hive stop, applies).
    - UNLOGGED: a run season with no season line in the log (treated as OVERFLOWED).
    - OVERFLOWED: an overflow in the kept data.
    - CLEAN otherwise.
    Any attempt whose recorded library sha differs from the registered build is a HELP."""
    if not log or not log["attempts"]:
        raise Stage2Help("no epa_overflow.jsonl, or no start line: the unit cannot be classified")
    if registered_sha and any(a["sha"] != registered_sha for a in log["attempts"]):
        raise Stage2Help("an attempt ran a library other than the registered build")
    if crashed:
        if crash_attested(log):
            return CRASHED
        raise Stage2Help("an unattested crash: RULING item 5 as registered (stop and re-rule)")
    if any(s not in log["kept"] for s in seasons_run):
        return UNLOGGED
    return OVERFLOWED if any(log["kept"].values()) else CLEAN


def propagate_s60(states: dict, s60_overflow: dict) -> dict:
    """The draft's §3.1: an overflow in S's S60 phase (seasons 0-59) sits upstream of S, M and N of that seed, so all
    three take OVERFLOWED (a CRASHED arm keeps CRASHED).  ``states[(seed, arm)]``; ``s60_overflow[seed]`` bool."""
    out = dict(states)
    for (seed, arm), st in states.items():
        if s60_overflow.get(seed) and st not in (CRASHED, UNLOGGED):
            out[(seed, arm)] = OVERFLOWED
    return out


#: S2-R2: the ceiling.  A second attested CRASHED unit at one point, or a third overall (Stage 2 and GO-1), stops
#: launches for a re-rule.
CEILING_PER_POINT, CEILING_TOTAL = 2, 3


def crash_ceiling(crashes: list) -> str:
    """``crashes`` = [(point, stage)] of attested CRASHED units, Stage 2 and GO-1 together (the Stage-1 unit excluded)."""
    per = {}
    for pt, _ in crashes:
        per[pt] = per.get(pt, 0) + 1
    if any(v >= CEILING_PER_POINT for v in per.values()) or len(crashes) >= CEILING_TOTAL:
        return "STOP: re-rule (S2-R2 ceiling)"
    return "continue"


def ksalt_outcome(verdict: str, overflowed: bool) -> str:
    """N-3: a K-SALT mismatch in a unit whose log holds an overflow is a HELP, not a VOID (the build at the event, not
    the stream, may explain it)."""
    if verdict == "PASS":
        return "PASS"
    if overflowed:
        raise Stage2Help("K-SALT mismatch with an EPA overflow in the unit: HELP")
    return verdict


def check_build(recorded_sha: str, registered_sha: str) -> bool:
    """Every Stage-2 attempt records the sha256 of the libmujoco it mapped; it must equal the ruled build."""
    return bool(registered_sha) and bool(SHA256_RE.match(registered_sha)) and recorded_sha == registered_sha


#: the primary rule (S2-R2, O-8) and its sensitivity
OVERFLOW_RULES = ("include-flagged", "exclude-known-flagged")


def keep_seed(state: str, mode: str) -> bool:
    """Whether a seed's unit enters a statistic (plan §3.4).  CRASHED never enters (RULING item 1: no imputation).
    UNSCANNED (a Stage-1 unit no scan has covered) is read as it stands in both modes: the sensitivity excludes only
    *known* flags, and the UNSCANNED units are unchecked."""
    if state == CRASHED:
        return False
    if state in FLAGGED_STATES:
        return mode == "include-flagged"
    if state in (CLEAN, UNSCANNED):
        return True
    raise ValueError(state)


def crash_bounded_body(p: dict, crashed: dict) -> dict:
    """An S-arm CRASHED seed (plan §3.4; S2-R2 fix of MAJOR 3 (iii)): the primary body call removes it from n, as a
    K-SALT VOID seed (O-7).  The bound restores it under **feasible** states only: ``crashed[j] = (h alive at 59, d
    alive at 59)`` from ckpt60, or None for a crash before 59.  A fauna dead at 59 is extinct at 299 (the ecology never
    re-seeds); a fauna alive at 59 may or may not be.  Returns {"primary", "feasible" (set), "word"}: "crash-robust",
    "CRASH-SENSITIVE", or "primary infeasible given ckpt60" when the primary call is not among the feasible ones."""
    primary = sr.body_call(p)
    options = []
    for j, v in crashed.items():
        merges = [v] if v is not None else [(True, True), (True, False), (False, True), (False, False)]
        opts = []
        for mh, md in merges:
            for eh in ((1,) if not mh else (0, 1)):
                for ed in ((1,) if not md else (0, 1)):
                    opts.append((j, (mh, md), eh, ed))
        options.append(opts)
    feasible = set()

    def rec(i, q):
        if i == len(options):
            feasible.add(sr.body_call(q))
            return
        for j, mv, eh, ed in options[i]:
            rec(i + 1, dict(q, n=q["n"] + 1, extinct={H: q["extinct"][H] + eh, D: q["extinct"][D] + ed},
                            valid_share=q["valid_share"] + (1 if (mv[0] and mv[1]) else 0), merge={**q["merge"], j: mv}))
    rec(0, p)
    word = ("primary infeasible given ckpt60" if primary not in feasible else
            "crash-robust" if feasible == {primary} else "CRASH-SENSITIVE")
    return {"primary": primary, "feasible": feasible, "word": word}


def crash_affected(income_points: dict, crashed_s: dict) -> dict:
    """S2-R2 (MAJOR 3 (ii)): an income call at a point with a CRASHED S seed is CRASH-AFFECTED (income has no logical
    bound).  ``income_points[pid]`` = call; ``crashed_s[pid]`` = number of CRASHED S seeds."""
    return {p: bool(crashed_s.get(p)) for p in income_points}


def verdict_crash_mark(counting_sets: dict, affected: dict) -> bool:
    """The §8 line carries CRASH-AFFECTED when a CRASH-AFFECTED point belongs to a counting set of <= 2 calls that the
    verdict uses (``counting_sets[name] = [pids]``)."""
    return any(len(pids) <= 2 and any(affected.get(p) for p in pids) for pids in counting_sets.values())


# -- 4 the five COORD-RULING-517 C3 pins (plan §4; S2-R1: the pre-data committed code governs) -------------------- #

def share_void(n_ran: bool, n_stages: list, pooled_pass: dict, per_point: str) -> bool:
    """C3-1 (the pre-data code, ``call_points``), K2's scope.  The pooled VOID applies **only to share calls at points
    where N ran** in a stage whose pooled K2 failed (``n_stages``: the stages whose N runs the point's share test uses; a
    16-seed point uses both halves' stages).  It never VOIDs a point without N, an income call, a survival call, or
    habitability, except through §6.1 item 3 at an N point that items 1-2 do not settle first (O-10's disclosure)."""
    if not n_ran:
        return False
    return any(not pooled_pass.get(s, False) for s in n_stages) or per_point == "FAIL"


def verdict5_literal(points: dict, corroborate) -> list:
    """C3-2: the **non-registered** literal reading of verdict 5 ("every decided EARNS call favours X": no EARNS call
    at all for the other fauna).  The registered reading is the pre-data code's (``sr.verdicts``): one uncorroborated
    other-fauna EARNS is tolerated; any EARNS-TIE fails (R2)."""
    out = []
    inc = {p: s.get("income") for p, s in points.items() if not s.get("lever")}
    ties = [p for p, c in inc.items() if c == "EARNS-TIE"]
    for x, mine, other, owin, surv_y in (("H", "EARNS-H", "EARNS-D", "D-WIN", ("EXCLUDED-H", "PARTIAL-D")),
                                         ("D", "EARNS-D", "EARNS-H", "H-WIN", ("EXCLUDED-D", "PARTIAL-H"))):
        ex = [p for p, c in inc.items() if c == mine]
        eo = [p for p, c in inc.items() if c == other]
        wo = [p for p, s in points.items() if s["body"] == owin and not s.get("vd") and not s.get("lever")]
        sy = [p for p, s in points.items() if s["body"] in surv_y]
        if ex and not eo and not ties and not wo and sr.counting_set(sy, [corroborate(p) for p in sy]):
            out.append(f"DEPENDS ONLY THROUGH HABITABILITY ({x})")
    return out


def verdicts_literal(points: dict, t1: str, corroborate) -> list:
    """The §8 list under the literal verdict-5 reading (non-registered): the registered list with any verdict-5 line
    the literal reading does not support removed; if nothing is left, the registered fallback."""
    reg = sr.verdicts(points, t1, corroborate)
    lit5 = set(verdict5_literal(points, corroborate))
    out = [v for v in reg if not v.startswith("DEPENDS ONLY THROUGH HABITABILITY") or v in lit5]
    if out and out != [sr.NO_VERDICT_T1] and out != ["NOT RESOLVED"]:
        return out
    return [sr.NO_VERDICT_T1] if t1 == "NOT TESTABLE" else ["NOT RESOLVED"]


def v5_mark(points: dict, t1: str, corroborate) -> tuple:
    """S2-R1 / MAJOR 6: (registered headline, literal headline, mark).  The mark is V5-TOLERANCE-SENSITIVE whenever the
    two headlines differ; it is printed on the headline line itself."""
    reg = sr.verdicts(points, t1, corroborate)[0]
    lit = verdicts_literal(points, t1, corroborate)[0]
    return reg, lit, ("V5-TOLERANCE-SENSITIVE" if reg != lit else "")


SCORE2_BODIES = ("NOT RUN", "SATURATED", "RBT-118 (not available)")


def scorecard_item2(points: dict, stage1_points=sr.STAGE1_POINTS) -> dict:
    """C3-3 (S2-R1: the C3-3 pin is REJECTED): §12 item 2 is scored as the pre-data code scored it (``sr.scorecard``),
    on body calls in {NOT RUN, SATURATED, RBT-118 (not available)}, AS PREDICTED when more than half and RESOLVING <= 2.
    Two **non-registered, descriptive** lines are returned beside it: the gated-out count ("by design; §5.2: not
    evidence"), and the share layer's own status at the points where N ran.  ``points[pid] = {"n_ran", "body",
    "resolving"}``."""
    nr = sum(1 for s in points.values() if s["body"] in SCORE2_BODIES)
    res = sum(1 for s in points.values() if s.get("resolving"))
    word = "AS PREDICTED" if nr > len(points) / 2 and res <= 2 else "NOT SHOWN"
    gated = sum(1 for s in points.values() if not s["n_ran"])
    n_pts = [s for s in points.values() if s["n_ran"]]
    nres = sum(1 for s in n_pts if not s.get("resolving"))
    return {"registered": f"{word} ({nr} of {len(points)}; RESOLVING {res})",
            "gated": f"NON-REGISTERED: gated out at {gated} of {len(points)} (by design; §5.2: not evidence)",
            "n_points": f"NON-REGISTERED: share layer at the N points: not RESOLVING at {nres} of {len(n_pts)}",
            "word": word, "nr": nr, "res": res}


def share_model_points(points: dict, stage1_points=sr.STAGE1_POINTS, scope: str = "all") -> list:
    """C3-4 (S2-R1: the pre-data code governs): the registered share fit uses every point **on the Stage-1 grid** with
    an M arm (its every completed M seed), as ``stage1_readout.readout`` did.  ``scope="habitable"`` is the
    non-registered line.  No call or verdict reads either fit, at Stage 1 or on the final map."""
    out = []
    for p, s in sorted(points.items()):
        if not s.get("m_arm") or p not in stage1_points:
            continue
        if scope == "habitable" and s["body"] in sr.HABITABLE_OUT:
            continue
        out.append(p)
    return out


PER_BIRTH_WINDOW = (180, 238)   # C3-5: births 180-238; each life's last row is <= 298, before the last season 299


def per_birth_uncensored(win: dict):
    """C3-5: the per-birth income for MARGINAL from ``scripts/regime.py``'s window 180-238 (lives **born** in it).

    Why 238 and not 239: regime.py counts a life complete when its last row precedes the run's last season
    (``l.last_gen < last``, line 175).  A life born at 239 is evaluated in 240-299 and dies aged in 299 (max age 60), so
    its last row *is* season 299 and regime.py counts it censored.  Births up to 238 end by 298 at the latest.  (Found by
    ``s91_rule_chosen.py`` before any Stage-2 data; the plan's first draft said 180-239.)  The value is regime's
    ``net_per_birth`` + the living cost (O-5's reading kept).  ``None`` when the window has no complete life.  A
    censored life there is impossible in a 300-season S arm, so one is a HELP."""
    if not win or not win.get("complete_lives"):
        return None
    if win.get("censored_lives"):
        raise Stage2Help("a censored life born in 180-238: the arm did not reach season 299")
    return sr.per_birth_income(win.get("net_per_birth"))


# -- 5 the final map: R-B combination and the final BH (plan §5) ---------------------------------------------------- #

def _z_upper(xs: list, mu: float) -> float:
    """The signed z of one half's one-sided t test of H0: mean <= mu, computed symmetrically from the smaller tail
    (finding 12): z = sign(t) * -Phi^-1(p_tail), with the same clamp on both sides (|z| <= 40)."""
    m, sd = sr.mean_sd(xs)
    if sd == 0:
        return 40.0 if m > mu else -40.0 if m < mu else 0.0
    t = (m - mu) / (sd / math.sqrt(len(xs)))
    if t == 0:
        return 0.0
    p_tail = max(sr.t_sf(abs(t), len(xs) - 1), 1e-300)
    return math.copysign(min(-sr.norm_ppf(p_tail), 40.0), t)


def combined_z(x1: list, x2: list, mu: float = 0.0) -> float:
    """Lehmacher & Wassmer's fixed-weight inverse normal, Z = (Z1 + Z2)/√2 (DESIGN 4.2; R4 (iii))."""
    return (_z_upper(x1, mu) + _z_upper(x2, mu)) / math.sqrt(2)


def combined_p(x1: list, x2: list) -> dict:
    """{p_earns (two-sided), p_tie (TOST: the larger of the two combined one-sided p), mean (pooled over 16)}.  The
    TOST halves follow ``sr.stage2_income_call``: H0 mu <= -0.15 by the upper z, H0 mu >= +0.15 by the lower z."""
    zc = combined_z(x1, x2, 0.0)
    p_lo = 1 - sr.norm_cdf(combined_z(x1, x2, -sr.DELTA_I))
    p_hi = sr.norm_cdf(combined_z(x1, x2, sr.DELTA_I))
    xs = list(x1) + list(x2)
    return {"p_earns": 2 * (1 - sr.norm_cdf(abs(zc))), "p_tie": max(p_lo, p_hi), "mean": sum(xs) / len(xs),
            "n": len(xs), "z": zc}


def median_unbiased(x1: list, x2: list, lo: float = None, hi: float = None, steps: int = 200):
    """§7.2's sensitivity-fit estimate at an R-B point: the mu at which the combined statistic Z(mu) is 0 (the root of
    the stage-wise combination; plan O-14).  Z(mu) decreases in mu; bisection on the pooled range ± 10."""
    xs = list(x1) + list(x2)
    lo = min(xs) - 10 if lo is None else lo
    hi = max(xs) + 10 if hi is None else hi
    for _ in range(steps):
        mid = (lo + hi) / 2
        if combined_z(x1, x2, mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def point_income_test(x1: list, x2: list = None) -> dict:
    """One point's income test for the final families (plan §5.2).  Not extended: the half-1 t test and TOST.
    Extended with >= 2 income-valid seeds in each half: the combination.  Extended with < 2 in half 2: the half-1 test,
    flagged "half 2 short" (its seeds printed only).  Fewer than 2 in half 1: not tested."""
    if len(x1) < 2:
        return {"p_earns": None, "p_tie": None, "mean": None, "n": len(x1), "how": "not tested"}
    if x2 is not None and len(x2) >= 2:
        return dict(combined_p(x1, x2), how="combined")
    r = sr.one_sample_t(x1)
    return {"p_earns": r["p"], "p_tie": sr.tost_p(x1, sr.DELTA_I), "mean": r["mean"], "n": r["n"],
            "how": "half 2 short" if x2 is not None else "half 1"}


def final_income_calls(tests: dict, q: float = sr.Q_BH) -> dict:
    """The final BH, once, over every tested point (DESIGN 7.1), in the EARNS family and the TIE family separately;
    the calls by ``sr.income_call`` (|x̄| >= 0.10 on the pooled mean).  ``tests[pid]`` from :func:`point_income_test`."""
    rej_e = sr.bh({p: t["p_earns"] for p, t in tests.items()}, q)
    rej_t = sr.bh({p: t["p_tie"] for p, t in tests.items()}, q)
    return {p: sr.income_call(t["mean"], p in rej_e, p in rej_t) for p, t in tests.items()}


def m4_weights(stage1_points, stage2a_points) -> dict:
    """M4 with the Stage-2a points (plan §5.4, O-17; S2-R4: the quarter rule, stated): each Stage-1 point of a smell
    block starts at weight 1; a midpoint takes one quarter of each parent's **current** weight, midpoints processed in
    id order; weights are then normalised per smell block.  Parents come from ``sr.ra_pairs``.  Its stated departures
    from an axis-Voronoi split (finding 14): a parent split on both sides keeps 0.5625 rather than 0.5 of its weight;
    edge points are treated as interior ones; the result depends on the (fixed) id order.  M4 is descriptive."""
    parents = {mid: (a, b) for a, b, mid, _ in sr.ra_pairs(stage1_points)}
    w = {p: 1.0 for p in stage1_points}
    for mid in sorted(stage2a_points):
        a, b = parents[mid]
        take_a, take_b = w[a] / 4, w[b] / 4
        w[a] -= take_a
        w[b] -= take_b
        w[mid] = take_a + take_b
    out = {}
    for s in ("G", "L"):
        tot = sum(v for p, v in w.items() if p.endswith("-" + s))
        out.update({p: v / tot for p, v in w.items() if p.endswith("-" + s)})
    return out


# -- 6 the locks and the ruled lines (plan §11; S2-R3) ------------------------------------------------------------ #

#: per-step GO locks (S2-R3): each step opens only under its own GO line
STEP_GO = {"interim": "GO-ID-INTERIM:", "final": "GO-ID-FINAL:"}
GO_IDS = {"GO-ID-2A:": "RBT129-S2-2A-GO-1", "GO-ID-INTERIM:": "RBT129-S2-INTERIM-GO-1",
          "GO-ID-FINAL:": "RBT129-S2-FINAL-GO-1"}
RULED_TAGS = ("GO-ID-2A:", "GO-ID-INTERIM:", "GO-ID-FINAL:", "2B2A:", "OVERFLOW-RULE:", "BUILD-SHA256:")
B2A_VALUES = ("COMMITTED", "DECLINED")

#: every quarantined label (RULING item 3; plan §3.5).  The Stage-1 unit now; a new attested CRASHED unit's label is
#: added by ruling only (a ``QUARANTINE:`` line).
QUARANTINED = (sr.QUARANTINED_LABEL,)


def ruled_lines(path: str = None) -> dict:
    """{tag: [values]} for every ruled tag (and ``QUARANTINE:``) at the start of a line; ``-PENDING:`` tags never
    match.  A duplicated or empty ruled line is a HELP (finding 13 (b))."""
    path = path or RULINGS
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path):
        for tag in RULED_TAGS + ("QUARANTINE:",):
            if line.startswith(tag):
                out.setdefault(tag, []).append(line.split(":", 1)[1].strip())
    for tag, vals in out.items():
        if any(not v for v in vals):
            raise Stage2Help(f"an empty {tag} line in RULINGS-CITED-S2.md")
        if tag != "QUARANTINE:" and len(vals) > 1:
            raise Stage2Help(f"a duplicated {tag} line in RULINGS-CITED-S2.md")
    return out


def ruled(tag: str, path: str = None) -> set:
    return set(ruled_lines(path).get(tag, []))


def quarantined(path: str = None) -> tuple:
    return QUARANTINED + tuple(ruled_lines(path).get("QUARANTINE:", []))


def is_quarantined(label: str, path: str = None) -> bool:
    """Case-insensitive substring, as ``sr._is_quarantined_label`` does for the Stage-1 unit (finding 13 (c))."""
    low = label.lower()
    return any(q.lower() in low for q in quarantined(path))


def refusal(step: str, go: str, path: str = None, root: str = ROOT) -> str:
    """Why ``step`` must not run (empty = it may).  Every lock must be ruled and well formed, the 2b(2a) decision must
    be registered before the 2a GO can open (S2-R3, N-5), and the registered inputs must check (finding 13 (d))."""
    try:
        r = ruled_lines(path)
    except Stage2Help as e:
        return f"HELP: {e}"
    tag = STEP_GO[step]
    if not go or r.get(tag) != [go.strip()] or go.strip() != GO_IDS[tag]:
        return f"no GO for {step}: needs '{tag} {GO_IDS[tag]}' in RULINGS-CITED-S2.md"
    if r.get("GO-ID-2A:") != [GO_IDS["GO-ID-2A:"]]:
        return "2a was not authorised (GO-ID-2A:)"
    if r.get("2B2A:", [None])[0] not in B2A_VALUES:
        return "the owner's 2b(2a) decision is not registered (2B2A: COMMITTED | DECLINED)"
    if r.get("OVERFLOW-RULE:", [None])[0] not in OVERFLOW_RULES:
        return "the overflow-handling rule is not ruled (OVERFLOW-RULE:)"
    if not SHA256_RE.match(r.get("BUILD-SHA256:", [""])[0]):
        return "the continuation build is not registered (BUILD-SHA256: 64 hex digits)"
    if check_inputs():
        return "the registered inputs do not check: " + "; ".join(check_inputs())
    if sr.local_quarantine_refs(root):
        return "a local ref names the quarantined unit (a bare fetch ran): HELP"
    return ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("step", choices=tuple(STEP_GO))
    ap.add_argument("--go")
    a = ap.parse_args(argv)
    why = refusal(a.step, a.go)
    if why:
        print(f"refused: {why}.  Nothing was read.", file=sys.stderr)
        return 9
    raise NotImplementedError("SKELETON: the drivers are completed, with an end-to-end synthetic-tree test, before the"
                              " first GO (STAGE2-PLAN.md §11)")


if __name__ == "__main__":
    sys.exit(main())
