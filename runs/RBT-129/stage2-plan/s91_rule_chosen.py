#!/usr/bin/env python3
"""DESIGN §9.1's RBT-118 rule-chosen points, computed by DESIGN's rule from the accepted Stage-1 record (STAGE2-PLAN
§4.5; COORD S2-R1, C3-5).  Run once, before any Stage-2 data; its output ``s91_rule_chosen.txt`` is committed.

    python3 runs/RBT-129/stage2-plan/s91_rule_chosen.py > runs/RBT-129/stage2-plan/s91_rule_chosen.txt

DESIGN §9.1: "the habitable, non-LEVER, non-MARGINAL Stage-1 point with the largest BH-significant income effect |x̄|
for each sign, if one exists".  The Stage-1 calls, x̄, habitability and BH come from ``stage1_readout.txt`` (the accepted
record).  Only MARGINAL needs run data: it is recomputed here at full precision, on each EARNS point's income-valid
seeds, under both measures:
  - **registered at Stage 1** (READOUT-PLAN §3.5): regime.py window 240-299 (censored);
  - **amended** (C3-5, DATA-INFORMED): regime.py window 180-238, lives born there, all complete by season 298.
Per-birth income = net_per_birth + 0.25 (O-5), mean over the point's income-valid seeds that have one (FC-SHOULD 3);
MARGINAL when either fauna's is **strictly** below 0.25, at full precision.

Reads only the S directories of the 8 EARNS points, restored through ``stage1_readout``'s quarantine guard; no M, N or
quarantined unit.  LEVER is not evaluated (no probe leg), so no point is excluded on it; that caveat is printed.
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("stage2_readout", os.path.join(HERE, "stage2_readout.py"))
s2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s2)
sr = s2.sr
H, D = sr.H, sr.D


def earns_points(txt: str) -> dict:
    """{pid: (body, call, x̄)} for every EARNS call of the per-point table."""
    out = {}
    for line in open(txt):
        m = re.match(r"  (c\S+)\s+(.+?)\s{2,}share .*\| x̄ (\S+) .*\| (EARNS-[HD])", line)
        if m:
            out[m.group(1)] = (m.group(2).strip(), m.group(4), float(m.group(3)))
    return out


def rule(points: dict, marginal: dict) -> dict:
    """§9.1 per sign: habitable, non-MARGINAL (LEVER not evaluated), largest |x̄|; None if none qualifies."""
    best = {}
    for sign, call in (("H", "EARNS-H"), ("D", "EARNS-D")):
        ok = [(abs(x), p) for p, (body, c, x) in points.items()
              if c == call and body not in sr.HABITABLE_OUT and marginal.get(p) is False]
        best[sign] = max(ok)[1] if ok else None
    return best


def main() -> int:
    if s2.check_inputs():
        raise SystemExit(f"inputs: {s2.check_inputs()}")
    if sr.local_quarantine_refs(sr.ROOT):
        raise SystemExit("a local ref names the quarantined unit: HELP")
    pts = earns_points(s2.STAGE1_TXT)
    pb = {}
    for pid in sorted(pts):
        per = {"240": {H: [], D: []}, "180": {H: [], D: []}}
        wins = ((180, 238), (240, 299))
        for j in sr.SEEDS:
            d = os.path.join("runs", "RBT-129", "stage1", pid, str(sr.SEED_BASE + j), "S")
            sr.guarded_restore(d, sr.ROOT)
            run = sr.read_run(d, sr.ROOT)
            if not sr.valid_income(run["history"]):
                continue
            res = sr.guarded_regime(d, sr.ROOT, windows=wins)
            for k in (H, D):
                v240 = sr.per_birth_income(sr.regime_window(res, k, 240).get("net_per_birth"))
                w180 = sr.regime_window(res, k, 180)
                v180 = s2.per_birth_uncensored(w180)
                if v240 is not None:
                    per["240"][k].append(v240)
                if v180 is not None:
                    per["180"][k].append(v180)
        pb[pid] = {w: {k: (sum(v) / len(v) if v else None) for k, v in per[w].items()} for w in per}
    print("# DESIGN §9.1 rule-chosen points (STAGE2-PLAN §4.5; S2-R1 C3-5); from the accepted Stage-1 record")
    print("# per-birth income = net_per_birth + 0.25, mean over income-valid seeds; MARGINAL: either < 0.25 (strict)")
    print("# LEVER not evaluated (no probe leg): no point excluded on LEVER; every choice carries that caveat")
    marg = {"240": {}, "180": {}}
    for pid in sorted(pts):
        body, call, x = pts[pid]
        cells = []
        for w in ("240", "180"):
            m = sr.marginal(pb[pid][w])
            marg[w][pid] = m
            cells.append(f"{w}: H {pb[pid][w][H]!r} D {pb[pid][w][D]!r} {'MARGINAL' if m else 'not' if m is False else '--'}")
        hab = "habitable" if body not in sr.HABITABLE_OUT else "not habitable"
        print(f"  {pid:14s} {call} x̄ {x:+.3f} {body} ({hab}) | " + " | ".join(cells))
    for w, label in (("180", "AMENDED measure (births 180-238; C3-5, DATA-INFORMED): the registered §9.1 choice"),
                     ("240", "Stage-1 measure (240-299, censored): the counterfactual, printed only")):
        b = rule(pts, marg[w])
        print(f"## {label}: H-sign {b['H'] or 'none'}; D-sign {b['D'] or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
