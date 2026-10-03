#!/usr/bin/env python3
"""RBT-129 Stage 2 (2a, 2b and the final map): the script SKELETON of ``STAGE2-PLAN.md`` (pre-data).

    python3 runs/RBT-129/stage2-plan/stage2_readout.py integrity --go GO_ID  -> stage2-plan/integrity-s2.txt
    python3 runs/RBT-129/stage2-plan/stage2_readout.py interim   --go GO_ID  -> stage2-plan/stage2a_interim.txt
    python3 runs/RBT-129/stage2-plan/stage2_readout.py final     --go GO_ID  -> stage2-plan/stage2_final.txt

**It refuses to run** unless ``--go ID`` matches a ``GO-ID:`` line of ``RULINGS-CITED-S2.md`` (the ID is registered
there as ``GO-ID-PENDING:``, which is never accepted), **and** the overflow-handling rule and the continuation build's
sha256 are ruled there (``OVERFLOW-RULE:`` and ``BUILD-SHA256:`` lines; today both are ``-PENDING:``).  It also refuses
while any local ref names the quarantined Stage-1 unit (``stage1_readout.local_quarantine_refs``).

**What is committed now (plan §11).** Every rule that a Stage-2 call, family, map statistic or verdict depends on is a
pure function below, tested on synthetic numbers in ``tests/test_rbt129_stage2_plan.py``.  The readers of continuation
run directories and the ``integrity``/``interim``/``final`` drivers are **not** written yet: the continuation lane
format does not exist (the continuations tooling PR).  Plan §11 makes the full drivers, with an end-to-end
synthetic-tree test, a precondition of the GO (as COORD-RULING-512 R5 did for Stage 1).  Until then the drivers raise.

Everything the Stage-1 readout already registered is **imported, not re-implemented**: the statistics, BH, Holm, the
body and income calls, the verdict logic, the quarantine guard (``runs/RBT-129/stage1-readout/stage1_readout.py``,
blob pinned in the plan).  Section numbers below are the plan's.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
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

GO_TAG, GO_PENDING_TAG = "GO-ID:", "GO-ID-PENDING:"
GO_ID = "RBT129-S2-READOUT-GO-1"


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


def budget(m2a: int, n2a: int, rb2a_points: int, m2b: int, n2b: int) -> dict:
    """Upper-bound core-h (low, high) of the arms this plan registers (plan §2.5).  2a: S at 12 points x 8 seeds,
    129001's S60 adopted from the census (240 arm-seasons), 300 elsewhere; M and N at every seed (an upper bound: they
    fork only on seeds valid at the merge), 240 arm-seasons each.  2b for Stage-2a points: S at ``rb2a_points`` x 8
    fresh seeds x 300; M/N likewise.  K-SALT is a file comparison and costs nothing."""
    s2a = len(STAGE2A_POINTS) * (7 * SEASONS_S + SEASONS_ADOPTED)
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


# -- 3 the continuation build and overflow handling (plan §3) ------------------------------------------------------- #

OVERFLOW_RE = re.compile(r"^RBT_HZN overflow: nedges (\d+) \(cap (\d+)\), EPA iteration (\d+), nverts (\d+), nfaces (\d+),"
                         r" geom (\d+) type (\d+), geom (\d+) type (\d+)$")
STATS_RE = re.compile(r"^epa_iterations (\d+) overflow (\d+) hist(.*)$")

#: unit states (plan §3.3); CRASHED as RULING item 1; UNSCANNED for Stage-1 units the scan has not covered
CLEAN, FLAGGED, CRASHED, UNSCANNED = "CLEAN", "OVERFLOW-FLAGGED", "CRASHED", "UNSCANNED"


def parse_hzn(stderr_lines, stats_lines) -> dict:
    """The build's integrity record of one unit (plan §3.2): ``RBT_HZN overflow`` lines from the unit's captured
    stderr (``hzn_overflow.txt``), and the per-process histogram lines from ``RBT_HZN_STATS`` (``hzn_stats.txt``).
    Reads nothing else: no outcome."""
    over = [OVERFLOW_RE.match(l.rstrip("\n")) for l in stderr_lines if l.startswith("RBT_HZN overflow")]
    if any(m is None for m in over):
        raise Stage2Help("a malformed RBT_HZN overflow line")
    procs, iters, ovf, hmax = 0, 0, 0, 0
    for l in stats_lines:
        m = STATS_RE.match(l.rstrip("\n"))
        if not m:
            continue
        procs += 1
        iters += int(m.group(1))
        ovf += int(m.group(2))
        bins = [int(x.split(":")[0]) for x in m.group(3).split()]
        hmax = max([hmax] + bins)
    return {"overflow_lines": len(over), "processes": procs, "epa_iterations": iters, "stats_overflow": ovf,
            "max_horizon": hmax, "events": [tuple(int(g) for g in m.groups()) for m in over]}


def unit_state(done: bool, hzn: dict, crashed: bool = False) -> str:
    """Plan §3.3.  ``done``: the unit's done-marker; ``crashed``: two attempts in a row faulted inside libmujoco
    (RULING item 5's counting rule).  A crash is CRASHED only when the build attests the mechanism (an ``RBT_HZN
    overflow`` line before the fault); otherwise it is a new mechanism: HELP.  A done unit without its build record, or
    whose stderr count and stats count disagree, is a HELP (an S-arm unit with no record cannot be classified)."""
    if crashed:
        if hzn and hzn["overflow_lines"] >= 1:
            return CRASHED
        raise Stage2Help("a crash with no RBT_HZN overflow line: an unattested mechanism (RULING item 5)")
    if not done:
        raise Stage2Help("a unit neither done nor CRASHED")
    if not hzn or hzn["processes"] == 0:
        raise Stage2Help("no build record (hzn_stats.txt) for a done unit")
    if hzn["overflow_lines"] != hzn["stats_overflow"]:
        raise Stage2Help("RBT_HZN stderr lines and the stats histogram disagree")
    return FLAGGED if hzn["overflow_lines"] else CLEAN


def check_build(recorded_sha: str, registered_sha: str) -> bool:
    """Every Stage-2 unit records the sha256 of the libmujoco it loaded; it must equal the ruled build (plan §3.1)."""
    return bool(registered_sha) and recorded_sha == registered_sha


#: the proposed handling (plan §3.4); the coordinator's OVERFLOW-RULE line in RULINGS-CITED-S2.md selects it
OVERFLOW_RULES = ("include-flagged", "exclude-flagged")


def keep_seed(state: str, mode: str) -> bool:
    """Whether a seed's unit enters a statistic (plan §3.4).  ``mode`` is ``"primary"`` (the ruled rule) or
    ``"sensitivity"`` (the other one).  CRASHED never enters (RULING item 1: no imputation).  UNSCANNED (a Stage-1 unit
    no scan has covered) is read as it stands in both modes, and counted."""
    if state == CRASHED:
        return False
    if state == FLAGGED:
        return mode == "include-flagged"
    return state in (CLEAN, UNSCANNED)


def crash_bounded_body(p: dict, crashed: dict) -> tuple:
    """An S-arm CRASHED seed (plan §3.4): the primary body call removes it from n, as a K-SALT VOID seed (O-7).  The
    bound evaluates the call with the seed restored under every survival state it could have had at 299, with its
    known merge validity (``crashed[j] = (h alive at 59, d alive at 59)``; a crash before 59 enumerates validity too).
    Returns (primary call, set of possible calls, "crash-robust" | "CRASH-SENSITIVE")."""
    primary = sr.body_call(p)
    states = []
    for j, v in crashed.items():
        merges = [v] if v is not None else [(True, True), (True, False), (False, True), (False, False)]
        states.append([(j, mv, eh, ed) for mv in merges for eh in (0, 1) for ed in (0, 1)])
    calls = set()

    def rec(i, q):
        if i == len(states):
            calls.add(sr.body_call(q))
            return
        for j, mv, eh, ed in states[i]:
            q2 = dict(q, n=q["n"] + 1, extinct={H: q["extinct"][H] + eh, D: q["extinct"][D] + ed},
                      valid_share=q["valid_share"] + (1 if (mv[0] and mv[1]) else 0), merge={**q["merge"], j: mv})
            rec(i + 1, q2)
    rec(0, p)
    return primary, calls, ("crash-robust" if calls == {primary} else "CRASH-SENSITIVE")


# -- 4 the five COORD-RULING-517 C3 pins (plan §4) ------------------------------------------------------------------ #

def share_void(n_ran: bool, n_stages: list, pooled_pass: dict, per_point: str) -> bool:
    """C3-1, K2's scope.  The pooled VOID applies **only to share calls at points where N ran** in a stage whose pooled
    K2 failed (``n_stages``: the stages whose N runs the point's share test uses; a 16-seed point uses both halves'
    stages).  It never VOIDs a point without N, an income call, a survival call, or habitability (an N point's VOID body
    call still makes it non-habitable through §6.1 item 3 only when items 1-2 do not settle it first)."""
    if not n_ran:
        return False
    return any(not pooled_pass.get(s, False) for s in n_stages) or per_point == "FAIL"


def verdict5_literal(points: dict, corroborate) -> list:
    """C3-2: the **non-registered** literal reading of verdict 5 ("every decided EARNS call favours X", no EARNS call
    at all for the other fauna), printed as a labelled line.  The registered reading is ``sr.verdicts``': one
    uncorroborated other-fauna EARNS is tolerated; any EARNS-TIE fails (R2)."""
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


def scorecard_item2(points: dict, stage1_points=sr.STAGE1_POINTS) -> tuple:
    """C3-3, §12 item 2, pinned to DESIGN's words ("SATURATED at most points, gated out at most (§5.2); RESOLVING at
    0-2 Stage-1 points"): the share layer is counted where it **ran or not**, not by body call.  Numerator: points with
    no N arm (gated out, anchors included) plus SATURATED points; denominator: every point of the map.  RESOLVING is
    counted over the Stage-1 points.  ``points[pid] = {"n_ran", "body", "resolving"}``.  Returns (word, numerator,
    denominator, resolving)."""
    num = sum(1 for s in points.values() if not s["n_ran"] or s["body"] == "SATURATED")
    res = sum(1 for p, s in points.items() if p in stage1_points and s.get("resolving"))
    word = "AS PREDICTED" if num > len(points) / 2 and res <= 2 else "NOT SHOWN"
    return word, num, len(points), res


def share_model_points(points: dict, stage1_points=sr.STAGE1_POINTS, scope: str = "habitable") -> list:
    """C3-4, the share model's scope (§7.2's "Registered fit: the Stage-1 grid only, valid seeds, habitable non-VOID
    points" read as governing both M2 models): points with an M arm, on the Stage-1 grid, habitable.  ``scope="all"``
    is the non-registered Stage-1 script's set (every point with an M arm), printed as a labelled line."""
    out = []
    for p, s in sorted(points.items()):
        if not s.get("m_arm") or p not in stage1_points:
            continue
        if scope == "habitable" and s["body"] in sr.HABITABLE_OUT:
            continue
        out.append(p)
    return out


PER_BIRTH_WINDOW = (180, 239)   # C3-5: births 180-239 complete by 298 (max age 60), so no life is censored


def per_birth_uncensored(win: dict):
    """C3-5: the per-birth income for MARGINAL from ``scripts/regime.py``'s window 180-239 (lives **born** in it;
    each is complete by season 298 at max age 60): its ``net_per_birth`` + the living cost (O-5's reading kept).
    ``None`` when the window has no complete life.  A censored life there is impossible in a 300-season S arm, so one
    is a HELP."""
    if not win or not win.get("complete_lives"):
        return None
    if win.get("censored_lives"):
        raise Stage2Help("a censored life born in 180-239: the arm did not reach season 299")
    return sr.per_birth_income(win.get("net_per_birth"))


# -- 5 the final map: R-B combination and the final BH (plan §5) ---------------------------------------------------- #

def _z_upper(xs: list, mu: float) -> float:
    """The signed z of one half's one-sided t test of H0: mean <= mu (inverse normal of its upper-tail p)."""
    m, sd = sr.mean_sd(xs)
    if sd == 0:
        return 40.0 if m > mu else -40.0 if m < mu else 0.0
    t = (m - mu) / (sd / math.sqrt(len(xs)))
    p = min(max(sr.t_sf(t, len(xs) - 1), 1e-300), 1 - 1e-16)
    return sr.norm_ppf(1 - p)


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
    """M4 with the Stage-2a points (plan §5.4, O-17): each Stage-1 point of a smell block starts at weight 1; a
    midpoint takes one quarter of each parent's current weight (midpoints in id order); weights are then normalised
    per smell block.  Parents come from ``sr.ra_pairs``."""
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


# -- 6 the go lock and the ruled lines (plan §11) ------------------------------------------------------------------- #

def ruled(tag: str, path: str = None) -> set:
    """Non-empty values of lines that begin with ``tag`` (e.g. ``GO-ID:``); ``-PENDING:`` tags never match."""
    path = path or RULINGS
    if not os.path.exists(path):
        return set()
    vals = {line.split(":", 1)[1].strip() for line in open(path) if line.startswith(tag)}
    return {v for v in vals if v}


def go_ids(path: str = None) -> set:
    return ruled(GO_TAG, path)


def refusal(go: str, path: str = None) -> str:
    """Why the script must not run (empty = it may)."""
    if not go or go.strip() not in go_ids(path):
        return "no GO: the Stage-2 readout runs only under a GO-ID listed in RULINGS-CITED-S2.md"
    rule = ruled("OVERFLOW-RULE:", path)
    if len(rule) != 1 or next(iter(rule)) not in OVERFLOW_RULES:
        return "the overflow-handling rule is not ruled (OVERFLOW-RULE:)"
    if len(ruled("BUILD-SHA256:", path)) != 1:
        return "the continuation build is not registered (BUILD-SHA256:)"
    if sr.local_quarantine_refs(ROOT):
        return "a local ref names the quarantined unit (a bare fetch ran): HELP"
    return ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("step", choices=("integrity", "interim", "final"))
    ap.add_argument("--go")
    a = ap.parse_args(argv)
    why = refusal(a.go)
    if why:
        print(f"refused: {why}.  Nothing was read.", file=sys.stderr)
        return 9
    raise NotImplementedError("SKELETON: the drivers are completed, with an end-to-end synthetic-tree test, before the"
                              " GO (STAGE2-PLAN.md §11)")


if __name__ == "__main__":
    sys.exit(main())
