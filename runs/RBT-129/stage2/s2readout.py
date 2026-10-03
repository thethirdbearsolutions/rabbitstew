#!/usr/bin/env python3
"""RBT-129 Stage 2's readout drivers: the interim (after 2a) and the final map (STAGE2-PLAN.md §5, §7, §9, §11).

    python3 runs/RBT-129/stage2/s2readout.py interim --go RBT129-S2-INTERIM-GO-1
        -> runs/RBT-129/stage2/integrity-interim.txt, then runs/RBT-129/stage2/stage2a_interim.txt
    python3 runs/RBT-129/stage2/s2readout.py final --go RBT129-S2-FINAL-GO-1
        -> runs/RBT-129/stage2/integrity-final.txt, then runs/RBT-129/stage2/stage2_final.txt

**The locks.** Each step refuses unless ``stage2_readout.refusal`` passes for it (its own GO, ``GO-ID-2A``, ``2B2A``,
the overflow rule, the build sha, the registered inputs, no local ref naming a quarantined label).  Integrity runs
first and its file is written before anything else is computed; any integrity failure is a HELP and nothing further is
read.

**One definition of everything.**
- **Per-seed statistics** are the Stage-1 readout's ``assemble_point``, run under :func:`layout`, which points its
  ``unit_dir`` and ``SEEDS`` at a stage's directories and seeds for the duration of one call.
- **Calls, BH, Holm, verdicts and the scorecard** are ``stage1_readout``'s.
- **The Stage-2 rules** are ``stage2_readout``'s: the combination, the C3 pins, the marks, the unit states through the
  registered ``epa_ecology`` (A1), A2 and A3.
- **The lane layouts** are the emitters': ``lanes/S2A`` (``s2lanes.py``), ``lanes/RB`` (the tooling), ``lanes/S2B`` (2b
  for Stage-2a points, emitted after the interim).

**What the interim prints** (S2-R3, MAJOR 7): integrity, the 2a gate re-check, operational counts, and the R4 list for
2b(2a) with CP and core-h.  **It prints no call and no §8 line**, for any point: the 2a calls are computed for R4 and
discarded.
"""
from __future__ import annotations

import argparse
import contextlib
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s2lanes  # noqa: E402

stages, s2 = s2lanes.stages, s2lanes.s2
sr = s2.sr
H, D = sr.H, sr.D
RUNS, ROOT = s2lanes.RUNS, s2lanes.ROOT

#: the directory each stage's units live in (runs/RBT-129/<dir>/<point>/<seed>/<arm>), and its lanes
STAGE_DIRS = {"1": "stage1", "2a": s2lanes.STAGE_DIR, "rb": "rb", "2b": "stage2b"}
LANES = {"2a": s2lanes.NAME, "rb": stages.RB_LANES, "2b": "S2B"}
HALF1, HALF2 = s2.SEEDS_HALF1, s2.SEEDS_HALF2
SEED_BASE = sr.SEED_BASE
RUN_KINDS = ("fresh", "resume", "fork")
SKIPPED_NOTES = ("skipped: not valid at the merge", "skipped: extinct pre-merge")


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


def assemble(root: str, stage: str, pid: str, seeds, arms: dict) -> dict:
    """``stage1_readout.assemble_point`` at one stage's units of one point.  ``arms``: void (S seeds out of n), m and
    n (the M and N seeds read), crashed (M seeds CRASHED, never read)."""
    with layout(STAGE_DIRS[stage], seeds):
        return sr.assemble_point(root, pid, arms.get("m", ()), arms.get("n", ()), arms.get("void", ()),
                                 arms.get("crashed", ()), False)


def guarded_restore(root: str, restore):
    def go(d):
        if s2.is_quarantined(stages._label(d)) or s2.is_quarantined(os.path.relpath(d, root)):
            raise sr.QuarantineRefusal(f"{d}: a quarantined label is never restored or read")
        sr.guarded_restore(d, root, restore)
    return go


# -- the lanes, the arms, and their states (plan §3; RBT129-OVERFLOW-RULE-1) ---------------------------------------- #

def lane_jobs(root: str, stage: str) -> list:
    d = os.path.join(root, "runs", "RBT-129", "lanes", LANES[stage])
    jobs = []
    for f in sorted(glob.glob(os.path.join(d, "*.jsonl"))):
        jobs += [json.loads(x) for x in open(f) if x.strip()]
    return jobs


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


def stage_states(root: str, stage: str, restore, epa=None) -> dict:
    """{(pid, seed, arm): state} for every S, M and N arm of a stage's lanes, after integrity's restore: the rule's
    state through the registered definitions (``stage2_readout.unit_state``), SKIPPED for a fork the seed rule or an
    extinct-pre-merge state skipped, with A2's S60-phase propagation to M and N.  An unattested crash, a wrong build, a
    missing log or a missing marker is a :class:`Help`."""
    epa = epa or s2.registered_epa()
    out, crashed = {}, []
    for j in lane_jobs(root, stage):
        if j["job"] not in RUN_KINDS:
            continue
        pid, sd, tag = j["name"].split("/")[1:]
        arm = "S" if tag in ("S60", "S") else tag
        d = _abs(root, j["dir"])
        restore(d)
        note = marker_note(d, tag)
        if note is None:
            raise Help(f"{j['name']}: no done-marker: the stage is not complete")
        if note.startswith(SKIPPED_NOTES) and arm in ("M", "N"):
            out[(pid, int(sd), arm)] = "SKIPPED"  # the seed rule, or extinct before the merge: no such arm
            continue
        if tag == "S60":
            continue  # S's state is read once, at its full run (the S job)
        try:
            st = s2.unit_state(d, seasons_ran(d, 0 if arm == "S" else stages.MERGE), epa)
        except s2.Stage2Help as e:
            raise Help(str(e))
        if arm in ("M", "N") and st not in (s2.CRASHED,) and s2.s60_overflowed(d, epa):
            st = s2.OVERFLOWED
        out[(pid, int(sd), arm)] = st
        if st == s2.CRASHED:
            crashed.append((pid, stage))
    return out


def arms_for(states: dict, pid: str, seeds, mode: str) -> dict:
    """The seeds each arm contributes at one point under ``mode`` (``include-flagged`` or ``exclude-known-flagged``):
    a CRASHED or excluded S seed leaves n (as a ruled K-SALT VOID, O-7) and takes its M and N with it; a CRASHED M seed
    is ``crashed`` (never read); an excluded M or N seed is not read."""
    out = {"void": [], "m": [], "n": [], "crashed": [], "s_crashed": []}
    for j in seeds:
        sd = SEED_BASE + j
        s = states.get((pid, sd, "S"), s2.UNSCANNED)
        if not s2.keep_seed(s, mode):
            out["void"].append(j)
            if s == s2.CRASHED:
                out["s_crashed"].append(j)
            continue
        for arm in ("M", "N"):
            a = states.get((pid, sd, arm))
            if a in (None, "SKIPPED"):
                continue
            if a == s2.CRASHED:
                if arm == "M":
                    out["crashed"].append(j)
                    out["m"].append(j)
                continue
            if s2.keep_seed(a, mode):
                out[arm.lower()].append(j)
    return out


# -- integrity (plan §7) --------------------------------------------------------------------------------------------- #

def stage_integrity(root: str, stage: str, restore, epa=None) -> tuple:
    """(lines, states) for one continuation stage: every job's marker; the build (A3: every platform record and resume
    entry, and every start line, at the registered sha); the unit states; s60cmp IDENTICAL; K-SALT with N-3.  Counts
    only; units are named only when OVERFLOWED, UNLOGGED or CRASHED (rule §5)."""
    epa = epa or s2.registered_epa()
    jobs = lane_jobs(root, stage)
    if not jobs:
        raise Help(f"lanes/{LANES[stage]} holds no job")
    lines = [f"## {LANES[stage]}: {len(jobs)} jobs"]
    for j in jobs:
        d = _abs(root, j["dir"])
        restore(d)
        if marker_note(d, j["name"].rsplit("/", 1)[1]) is None:
            raise Help(f"{j['name']}: no done-marker")
    states = stage_states(root, stage, restore, epa)
    for (pid, sd, arm), st in states.items():
        if st == "SKIPPED":
            continue
        d = os.path.join(root, "runs", "RBT-129", STAGE_DIRS[stage], pid, str(sd), arm)
        rec = json.load(open(os.path.join(d, "platform.json")))
        shas = [((rec.get("mujoco_build") or {}).get("libmujoco_sha256"))] + \
               [((r.get("mujoco_build") or {}).get("libmujoco_sha256")) for r in rec.get("resumes", [])]
        if any(x != s2.REGISTERED_SHA for x in shas):
            raise Help(f"{stage}/{pid}/{sd}/{arm}: a platform record at a build other than the registered one (A3)")
    for j in jobs:
        tag, d = j["name"].rsplit("/", 1)[1], _abs(root, j["dir"])
        if j["job"] == "s60cmp":
            word = open(os.path.join(d, s2lanes.S60CMP_FILE)).readline().split()[1].rstrip(":")
            if word != "IDENTICAL":
                raise Help(f"{j['name']}: S60CMP {word}: the re-simulation is not the census run (O-2)")
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
    for (_, _, arm), st in states.items():
        counts.setdefault(arm, {}).setdefault(st, 0)
        counts[arm][st] += 1
    for arm in sorted(counts):
        lines.append(f"  {arm}: " + ", ".join(f"{k} {v}" for k, v in sorted(counts[arm].items())))
    for (pid, sd, arm), st in sorted(states.items()):
        if st in (s2.OVERFLOWED, s2.UNLOGGED, s2.CRASHED):
            lines.append(f"  {st}: {LANES[stage]}/{pid}/{sd}/{arm}")
    lines.append(f"  build: every platform record and start line at {s2.REGISTERED_SHA} (A3): PASS")
    return lines, states


STANDING = ("Continuations ran on MuJoCo 3.14.0 with an instrumented build that is byte-identical to stock on every"
            " trajectory without an overflow (and makes no claim at or after one). The build logs every EPA horizon"
            " overflow (google-deepmind/mujoco#3646), a memory-safety bug that can corrupt a contact without crashing."
            " Every overflow the build logged in these runs is handled by the registered rule. A run whose log is"
            " incomplete is treated as overflowed. Stage-1 units outside the M/N scan's seasons 60-299 were not checked"
            " this way.")


def integrity(root: str, stages_: tuple, restore) -> tuple:
    epa = s2.registered_epa()
    lines, states, crashes = [], {}, []
    for st in stages_:
        ls, sts = stage_integrity(root, st, restore, epa)
        lines += ls
        states[st] = sts
        crashes += [(pid, st) for (pid, _, _), v in sts.items() if v == s2.CRASHED]
    ceiling = s2.crash_ceiling(crashes)
    lines.append(f"## crash ceiling (rule §4.4): {len(crashes)} attested crash events: {ceiling}")
    if ceiling != "continue":
        raise Help("the crash ceiling is reached: launches stop and the coordinator re-rules (rule §4.4)")
    lines.append(f"## standing sentence (rule §5.5): {STANDING}")
    return lines, states


# -- calls ----------------------------------------------------------------------------------------------------------- #

def stage1_arms(root: str) -> dict:
    """Stage 1's M and N seeds and its CRASHED unit, as the Stage-1 readout read them."""
    forks = sr.mn_forks(root)
    out = {}
    for pid in sr.STAGE1_POINTS:
        fk = forks.get(pid, {"M": [], "N": []})
        cr = [sr.CRASHED_SEED - SEED_BASE] if pid == sr.CRASHED_POINT else []
        out[pid] = {"void": [], "m": list(fk["M"]), "n": list(fk["N"]), "crashed": cr}
    return out


def k2_inputs(halves: dict) -> tuple:
    """(per-point K2 over every N point, its runs pooled across halves; the per-stage pooled verdicts; the per-kind null)."""
    by_point, by_stage, runs = {}, {}, {}
    for pid, hs in halves.items():
        for stage, h in hs:
            for j, y in h["y_n"].items():
                by_point.setdefault(pid, []).append(y)
                by_stage.setdefault(stage, []).append(y)
                runs.setdefault((pid, sr.null_kind(j)), []).append(y)
    pooled_pass = {st: sr.k2_pooled(ys)[0] for st, ys in by_stage.items()}
    return sr.k2_per_point(by_point), pooled_pass, sr.pooled_null(runs)


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


def call_map(halves: dict, resolvable, crashed_s: dict = None) -> dict:
    """The calls over ``halves`` ({pid: [(stage, assembled half), ...]}, half 1 first): income by the combination and
    one BH per family (plan §5.2); the share families over N points not settled first (O-22), combined at extended
    points; K2 per point and per stage (C3-1, ``share_void``); body calls at the merged n; VARIANCE-DRIVEN on WINs.
    ``crashed_s[pid] = {j: merge at 59 or None}``: a point's CRASHED S seeds, whose body call is bounded over feasible
    completions (``stage2_readout.crash_bounded_body``, plan §3.4)."""
    crashed_s = crashed_s or {}
    k2pt, pooled_pass, pooled = k2_inputs(halves)
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
    out = {}
    for p, v in merged.items():
        res = False
        if p in n_ran:
            res, _ = sr.resolving(bool(v["m_seeds"]), True, [g for g in v["g0"].values() if g is not None],
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
                  "halves": [list(h["x"].values()) for _, h in halves[p]]}
    return out


# -- the interim (plan §5.1; S2-R3) --------------------------------------------------------------------------------- #

def interim(root: str = ROOT, restore=None, resolvable=None, on_integrity=None) -> tuple:
    """(integrity lines, interim lines).  The 2a calls are computed under BH over Stage-1 ∪ 2a at n = 8 (O-15) for R4
    eligibility only, and are never printed."""
    restore = guarded_restore(root, restore)
    if resolvable is None:
        resolvable = sr.scaled_resolvable()[0]
    ilines, states = integrity(root, ("2a",), restore)
    if on_integrity:
        on_integrity(ilines)  # written before any other output is computed (plan §7)
    s1 = stage1_arms(root)
    for pid in sr.STAGE1_POINTS:
        for sub in ("S", "ckpt60"):
            for j in HALF1:
                restore(os.path.join(root, "runs", "RBT-129", "stage1", pid, str(SEED_BASE + j), sub))
    halves = {p: [("1", assemble(root, "1", p, HALF1, s1[p]))] for p in sr.STAGE1_POINTS}
    for pid in s2.STAGE2A_POINTS:
        arms = arms_for(states["2a"], pid, HALF1, "include-flagged")
        halves[pid] = [("2a", assemble(root, "2a", pid, HALF1, arms))]
    calls = call_map(halves, resolvable)
    stats = {}
    for p in s2.STAGE2A_POINTS:
        t = sr.one_sample_t(calls[p]["x"])
        stats[p] = {"body": calls[p]["body"], "income": {"call": calls[p]["income"]["call"], "t": t["t"], "n": t["n"]},
                    "share": {**calls[p]["share"], "t": calls[p]["share"].get("t"), "n": calls[p]["share"].get("n", 0)}}
    b2a = s2.ruled("2B2A:")
    rb = sr.rb_select(stats, cap=s2.rb_stage2a_slots())
    gate = s2lanes.s2a_gate()
    m_pts = [r["point"] for r in gate if r["m"] and r["point"] in [p for p, _ in rb]][:s2.M_CAP["2b"]]
    n_pts = [r["point"] for r in gate if r["n"] and r["point"] in [p for p, _ in rb]][:s2.N_CAP["2b"]]
    ch = s2.budget(0, 0, len(rb), len(m_pts), len(n_pts))["2b(2a) total"]
    L = ["# RBT-129 Stage 2a interim (STAGE2-PLAN.md §5.1; S2-R3): integrity and the R4 list only; no call, no §8 line",
         f"# claim: {sr.CLAIM}", ""]
    L.append(f"## 2b(2a): {', '.join(sorted(b2a)) or 'not registered'} (OWNER-DECISIONS-2026-10-03b)")
    if "DECLINED" in b2a:
        L.append("  declined: the Stage-2a points stay at n = 8 in the final map")
    else:
        L.append(f"## R4 list for 2b(2a) (COORD-RULING-512 R4; CP-ranked; cap {s2.rb_stage2a_slots()}): {len(rb)} points;"
                 f" upper bound {ch[0]:.1f} / {ch[1]:.1f} core-h (S, M at {len(m_pts)}, N at {len(n_pts)})")
        L += [f"  {p}: CP {sr._f(c, '{:.3f}')}" for p, c in rb]
    L.append("")
    L.append("# nothing else is printed (S2-R3): the 2a calls were computed for R4 eligibility and discarded")
    return ilines, L


# -- the final map (plan §5) ------------------------------------------------------------------------------------------ #

def final_halves(root: str, states: dict, mode: str) -> dict:
    s1 = stage1_arms(root)
    rb_pts = {j["name"].split("/")[1] for j in lane_jobs(root, "rb")}
    b2_pts = {j["name"].split("/")[1] for j in lane_jobs(root, "2b")} if "2b" in states else set()
    halves = {}
    for p in sr.STAGE1_POINTS:
        halves[p] = [("1", assemble(root, "1", p, HALF1, s1[p]))]
        if p in rb_pts:
            halves[p].append(("rb", assemble(root, "rb", p, HALF2, arms_for(states["rb"], p, HALF2, mode))))
    for p in s2.STAGE2A_POINTS:
        halves[p] = [("2a", assemble(root, "2a", p, HALF1, arms_for(states["2a"], p, HALF1, mode)))]
        if p in b2_pts:
            halves[p].append(("2b", assemble(root, "2b", p, HALF2, arms_for(states["2b"], p, HALF2, mode))))
    return halves


def crashed_s_merges(root: str, states: dict) -> dict:
    """{pid: {j: (h alive at 59, d alive at 59) from the unit's ckpt60, or None for a crash before 59}} over every
    CRASHED S seed of the continuation stages (plan §3.4)."""
    out = {}
    for stage, sts in states.items():
        seeds = HALF1 if stage == "2a" else HALF2
        for pid in sorted({k[0] for k in sts}):
            for j in arms_for(sts, pid, seeds, "include-flagged")["s_crashed"]:
                ck = os.path.join(root, "runs", "RBT-129", STAGE_DIRS[stage], pid, str(SEED_BASE + j), "ckpt60")
                v = None
                if os.path.exists(os.path.join(ck, "history.json")):
                    h = sr.read_run(ck, root)["history"]
                    v = (sr.alive(h, H, sr.SEASON_MERGE) > 0, sr.alive(h, D, sr.SEASON_MERGE) > 0)
                out.setdefault(pid, {})[j] = v
    return out


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


def final(root: str = ROOT, restore=None, resolvable=None, on_integrity=None) -> tuple:
    """(integrity lines, final-map lines): plan §5.2-§5.7 under include-flagged, the whole map again under
    exclude-known-flagged, and every difference marked OVERFLOW-SENSITIVE (rule §3.3)."""
    restore = guarded_restore(root, restore)
    if resolvable is None:
        resolvable = sr.scaled_resolvable()[0]
    b2a = s2.ruled("2B2A:")
    stages_ = ("2a", "rb") + (("2b",) if "COMMITTED" in b2a else ())
    ilines, states = integrity(root, stages_, restore)
    if on_integrity:
        on_integrity(ilines)
    for pid in sr.STAGE1_POINTS:
        for sub in ("S", "ckpt60"):
            for j in HALF1:
                restore(os.path.join(root, "runs", "RBT-129", "stage1", pid, str(SEED_BASE + j), sub))
    maps = {}
    crashed = crashed_s_merges(root, states)
    for mode in s2.OVERFLOW_RULES:
        calls = call_map(final_halves(root, states, mode), resolvable, crashed if mode == "include-flagged" else None)
        maps[mode] = calls
    calls = maps["include-flagged"]
    sens = maps["exclude-known-flagged"]
    everything = list(sr.STAGE1_POINTS) + list(s2.STAGE2A_POINTS)
    # the registered M2 (Stage-1 grid, seeds 1-8, Stage-1 habitability): its values are final at Stage 1 (O-19)
    s1h = {p: [("1", assemble(root, "1", p, HALF1, stage1_arms(root)[p]))] for p in sr.STAGE1_POINTS}
    s1calls = call_map(s1h, resolvable)
    hab1 = [p for p in sr.STAGE1_POINTS if s1calls[p]["body"] not in sr.HABITABLE_OUT]
    model = sr.world_model([(p, x) for p in hab1 for x in s1calls[p]["x"]])
    rej, ps = sr.map_holm(model)
    t1 = sr.t1_state(model, rej)
    m3 = m3_rows(calls, everything)
    m3_s1 = m3_rows(s1calls, sr.STAGE1_POINTS)
    verdict, vpts, corroborate = headline(calls, t1, m3)
    reg, lit, v5 = s2.v5_mark(vpts, t1, corroborate)
    sverdict = headline(sens, t1, m3_rows(sens, everything))[0]
    osens = "OVERFLOW-SENSITIVE" if sverdict[0] != verdict[0] else ""
    crash_s = {p: len(arms_for(states.get("2a" if p in s2.STAGE2A_POINTS else "rb", {}), p,
                               HALF1 if p in s2.STAGE2A_POINTS else HALF2, "include-flagged")["s_crashed"])
               for p in everything}
    affected = s2.crash_affected({p: c["income"]["call"] for p, c in calls.items()}, crash_s)
    sets = {k: [p for p, c in calls.items() if c["income"]["call"] == k] for k in ("EARNS-H", "EARNS-D")}
    cmark = "CRASH-AFFECTED" if s2.verdict_crash_mark(sets, affected) else ""
    marks = " ".join(m for m in (v5, osens, cmark) if m)
    L = ["# RBT-129 Stage 2 final map (STAGE2-PLAN.md §5; DESIGN §7-§8)", f"# claim: {sr.CLAIM}",
         f"# share-layer lines are read {sr.SHARE_QUAL}; earns, not persists; primary: include-flagged", ""]
    L.append("## §8 headline (final map; COORD-RULING-512 R1 + R2 + R3; C3-2 registered reading)")
    L.append(f"  {verdict[0]}" + (f"  [{marks}]" if marks else "") + (f"; also holding: {', '.join(verdict[1:])}" if len(verdict) > 1 else ""))
    L.append(f"  NON-REGISTERED (C3-2 literal verdict 5): {lit}")
    L.append(f"  exclude-known-flagged map: {sverdict[0]} (the UNSCANNED Stage-1 units are unchecked)")
    L.append("  perception: PERCEPTION NOT MEASURED (the perception layer is unreadable at a = 6); LEVER not evaluated")
    L.append("")
    L.append("## per-point table (final calls; income at n = 8, or combined over 16 at extended points)")
    for p in everything:
        c = calls[p]
        mark = " OVERFLOW-SENSITIVE" if (sens[p]["body"], sens[p]["income"]["call"]) != (c["body"], c["income"]["call"]) else ""
        mark += " CRASH-AFFECTED" if affected.get(p) else ""
        mark += f" [body {c['crash_word']}]" if c.get("crash_word") else ""
        L.append(f"  {p:14s} {c['body']:24s} income {c['income']['call']} ({c['income']['how']}, n {c['income']['n']},"
                 f" x̄ {sr._f(c['income']['mean'])}, p {sr._f(c['income']['p'], '{:.4f}')}){' VARIANCE-DRIVEN' if c['vd'] else ''}{mark}")
    L.append("")
    tested = [p for p in everything if calls[p]["income"]["p"] is not None]
    corr = sr.cross_correlation({p: dict(enumerate(calls[p]["x"])) for p in tested})
    L.append(f"## families: income EARNS and TIE over {len(tested)} points (BH once, q = 0.10); share families"
             f" {sum(1 for c in calls.values() if c['share_family'])} points; cross-point correlation mean {sr._f(corr[0], '{:.3f}')}")
    if corr[0] is not None and corr[0] > 0.3:
        by_rej = sr.by({p: calls[p]["income"]["p"] for p in tested})
        L += [f"  {p}: {calls[p]['income']['call']} holds under BH only" for p in tested
              if calls[p]["income"]["call"] in ("EARNS-H", "EARNS-D") and p not in by_rej]
    L.append("## M2 (registered: Stage-1 grid, seeds 1-8; final at Stage 1, O-19) and Holm (T4 NOT MEASURED, p = 1)")
    for name in ("T1", "T2", "T3"):
        L.append(f"  {name}: " + ("NOT TESTABLE" if model.get(name) is None else f"stat {model[name][0]:.3f}, p {ps[name]:.4g}")
                 + (" REJECTED" if name in rej else ""))
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
    L.append(f"## M2 sensitivity fit (Stage-2a points and extensions; MUE at extended points, O-14): status {smodel['status']}"
             + (f"; T1 χ² {smodel['T1'][0]:.3f}, df {smodel['T1'][1]}, p {smodel['T1'][2]:.4g}" if smodel.get("T1") else ""))
    L.append("## M3 break-evens, final map (corroborates §8; O-18) and Stage-1 only (descriptive)")
    for label, rows in (("final", m3), ("Stage-1 only", m3_s1)):
        for row, f in sorted(rows.items()):
            L.append(f"  {label} {row}: p* {sr._f(f.get('p_star'), '{:.4f}')} {f['kind']}"
                     + (f" [{f['lo']:.4f}, {f['hi']:.4f}]" if f["kind"] == "bounded" else ""))
    w = s2.m4_weights(sr.STAGE1_POINTS, s2.STAGE2A_POINTS)
    L.append("## M1 and M4 (Stage-2a points added; the quarter rule, O-17)")
    for s in ("G", "L"):
        share = {}
        for p in everything:
            if p.endswith("-" + s):
                share[calls[p]["body"]] = share.get(calls[p]["body"], 0.0) + w[p]
        L.append(f"  {s}: " + ", ".join(f"{k} {v:.3f}" for k, v in sorted(share.items())))
    L.append("## M5 perception map: NOT MEASURED")
    L.append("## M7 monotonicity of x̄ along every row of the final map")
    rows = {}
    for p in everything:
        c, pr, L_, s = sr.parse_point(p)
        rows.setdefault(("price", c, L_, s), []).append((pr, p))
        rows.setdefault(("clutter", pr, L_, s), []).append((c, p))
    for key, members in sorted(rows.items(), key=lambda kv: str(kv[0])):
        if len(members) >= 3:
            vals = [calls[p]["income"]["mean"] for _, p in sorted(members)]
            L.append(f"  {key}: {sr.sign_changes(vals)} sign changes [{' '.join(sr._f(x) for x in vals)}]")
    L.append("")
    sc = sr.scorecard({p: {**c, "income": c["income"]} for p, c in calls.items()}, model, rej, m3, verdict)
    L += sc
    item2 = s2.scorecard_item2({p: {"n_ran": bool(calls[p]["share"]), "body": calls[p]["body"],
                                    "resolving": calls[p]["resolving"]} for p in everything})
    L += [f"  {item2['gated']}", f"  {item2['n_points']}"]
    L.append("")
    L.append("# exclusions: K-SALT VOID (ruled), validity, CRASHED (rule §4.5), and under exclude-known-flagged only the"
             " OVERFLOWED and UNLOGGED arms; nothing winsorised or re-weighted")
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
    write(os.path.join(HERE, "stage2a_interim.txt" if a.step == "interim" else "stage2_final.txt"), lines)
    return 0


if __name__ == "__main__":
    sys.exit(main())
