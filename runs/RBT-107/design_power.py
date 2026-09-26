"""RBT-107 design stage: the arithmetic, the null and the power, from the design-stage garden rows (no C4 shift arm read).

    python runs/RBT-107/design_power.py > runs/RBT-107/design_power.txt

Reads runs/RBT-107/garden/ files written by garden_run.sh design / c2control:
    c0-SEED-KIND                     C0 (alive at T-1), from the RBT-90 checkpoint              -> Delta0, the arithmetic
    base-SEED-KIND-s599              RBT-90 base at 599 (d = 599 - T, 217..247)                  -> the null's reference
    cull20-SEED-KIND-s599            RBT-92 cull20 at 599: the divergence null at d ~ 240        -> A_NB, the null spread
    c2base-SEED-KIND-s599, c2shift-SEED-KIND-s599   the garden at work_cost 0.08 on RBT-90 base and RBT-99's C2 shift arm
                                     at 599: THE POSITIVE CONTROL (a challenge with a known direction of selection,
                                     cheaper gaits; the price is the same for both populations in the garden, so the
                                     arithmetic that decided RBT-99 cancels)
Prints: Delta0 per seed and fauna; the null A_NB and I_NB at d ~ 240 and their RMS; the drift sd per arm; the
resolution (smallest A detected at 80% by readout.py's two-interval rule) at n = 10, 8, 6 on the measured null, and on
the null scaled to d = 800 by sqrt(800/240) (neutral drift variance grows with depth; stated as an assumption); the
standing between-individual sd of flat-specific income in C0 (per-individual flat - random, J-draw noise removed by a
split-half estimate); and the C2 control's A_SB with its interval.
"""
import importlib.util
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rbt107_readout", os.path.join(HERE, "readout.py"))
RO = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RO)
RO.GARDEN = os.path.join(HERE, "garden")  # the design stage's 8-world rows (the readout's live in garden/readout/)
RO.SEEDS = RO.OLD_SEEDS
KINDS = RO.KINDS
SEEDS = RO.SEEDS


def main():
    print(__doc__.split("\n\n")[0])
    print("\n== ARITHMETIC: Delta0 = G_C0^flat - G_C0^random (income per robot-bout; the ecology's season gain)")
    d0 = {}
    for kind in KINDS:
        for s in SEEDS:
            g = RO.G(RO.garden(f"c0-{s}-{kind}"))
            if g:
                d0[(s, kind)] = g[0] - g[1]
                print(f"seed {s:>4} {kind:12s} C0 flat {g[0]:+.3f} random {g[1]:+.3f} Delta0 {g[0] - g[1]:+.3f}")
        print(f"DELTA0 {kind:12s} {RO.fmt([d0[(s, kind)] for s in SEEDS if (s, kind) in d0])}")
    body = [d0[(s, 'holistic')] - d0[(s, 'conventional')] for s in SEEDS if (s, 'holistic') in d0 and (s, 'conventional') in d0]
    print(f"DELTA0 holistic - conventional (the arithmetic R-body shift - base for an unchanged pair) {RO.fmt(body)}")

    print("\n== STANDING VARIATION in C0: per-individual flat-specific income (flat - random), sd across individuals")
    for kind in KINDS:
        sds = []
        for s in SEEDS:
            rows = RO.garden(f"c0-{s}-{kind}")
            if rows and len(rows) > 2:
                sds.append(statistics.stdev(v[0] - v[1] for v in rows.values()))
        if sds:
            print(f"{kind:12s} sd of individual (flat - random) income, median over seeds {statistics.median(sds):.3f} "
                  f"(range {min(sds):.3f}..{max(sds):.3f}); includes the 8-world draw noise, so an upper bound")

    print("\n== NULL at d ~ 240: cull20 - base, both at season 599 (no terrain change in either)")
    null = {}
    for kind in KINDS:
        ab, ii = [], []
        for s in SEEDS:
            n, b = RO.G(RO.garden(f"cull20-{s}-{kind}-s599")), RO.G(RO.garden(f"base-{s}-{kind}-s599"))
            if n and b:
                ab.append(n[0] - b[0])
                ii.append((n[0] - n[1]) - (b[0] - b[1]))
                print(f"seed {s:>4} {kind:12s} A_NB {n[0] - b[0]:+.3f}  I_NB {(n[0] - n[1]) - (b[0] - b[1]):+.3f}  "
                      f"(base flat {b[0]:+.3f} random {b[1]:+.3f})")
        null[kind] = ab
        if ab:
            rms = math.sqrt(statistics.fmean(x * x for x in ab))
            print(f"NULL {kind:12s} A_NB {RO.fmt(ab)}; RMS {rms:.3f}; drift sd per arm {rms / math.sqrt(2):.3f}; "
                  f"I_NB {RO.fmt(ii)} RMS {math.sqrt(statistics.fmean(x * x for x in ii)):.3f}")

    print("\n== RESOLUTION: smallest true A detected on >= 80% by the two-interval rule (readout.py mde)")
    for kind in KINDS:
        ab = null.get(kind) or []
        if len(ab) < 2:
            continue
        scaled = [x * math.sqrt(800 / 240) for x in ab]
        dz = [d0[(s, kind)] for s in SEEDS if (s, kind) in d0]
        ref = abs(statistics.fmean(dz)) if dz else float("nan")
        for n in (20, 10, 8, 6):
            m1, m2 = RO.mde(ab, n), RO.mde(scaled, n)
            print(f"RESOLUTION {kind:12s} n={n:>2}: null as measured at d~240 {m1:.3f} ({m1 / ref:.2f} x |Delta0|); "
                  f"null scaled to d=800 {m2:.3f} ({m2 / ref:.2f} x |Delta0|)")

    print("\n== POWER FOR RBT-101 F2's HYPOTHESIS (Amendment 1): the designed RESPONSE_flat of -0.22 at T+110 (probe_refund.txt)")
    ab = null.get("conventional") or []
    if len(ab) >= 2:
        scaled = [x * math.sqrt(800 / 240) for x in ab]
        for delta in (-0.22, -0.15, -0.10, +0.10, +0.22):
            print(f"POWER designed true A = {delta:+.2f}: n=10 {RO.power(delta, ab, 10):.2f} / n=20 {RO.power(delta, ab, 20):.2f} "
                  f"(null as measured at d~240); n=10 {RO.power(delta, scaled, 10):.2f} / n=20 {RO.power(delta, scaled, 20):.2f} "
                  f"(null scaled to d=800)")

    print("\n== POSITIVE CONTROL: C2 (RBT-99) at season 599, both populations in the garden at work_cost 0.08")
    for kind in KINDS:
        ab = []
        for s in SEEDS:
            S, B = RO.G(RO.garden(f"c2shift-{s}-{kind}-s599")), RO.G(RO.garden(f"c2base-{s}-{kind}-s599"))
            if S and B:
                ab.append(S[1] - B[1])  # the random-terrain column: C2 changed the price, not the ground
                print(f"seed {s:>4} {kind:12s} A_SB(C2, random ground, 0.08) {S[1] - B[1]:+.3f}  (shift {S[1]:+.3f} base {B[1]:+.3f})")
            elif B and not S:
                print(f"seed {s:>4} {kind:12s} C2 shift fauna extinct at 599: not read")
        if ab:
            print(f"CONTROL {kind:12s} A_SB(C2) {RO.fmt(ab)}; detected (interval above 0): {'YES' if RO.above(ab) else 'NO'}")


if __name__ == "__main__":
    main()
