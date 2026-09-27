"""RBT-107 H-REP: the registered replication of RBT-101 F2 at T + 110 on the 20 fresh seeds (A2.1, A2.2, A2.8, A2.9).

    python runs/RBT-107/hrep/hrep_readout.py > runs/RBT-107/hrep/readout.txt

Reads ONLY runs/RBT-107/hrep/: the cut tables (tables/ARM-SEED/: seasons 0..470, hrep_cut.py) and the T + 110 garden
(garden/: fresh-ARM-SEED-KIND-d110, J = 32 as halves 0..15 and 16..31, merged; z10-fresh-SEED.txt).  Nothing from season
>= 471 of any arm exists in those files.  The scored rule is readout.py's own code (iut, scored_p, specificity,
contrasts), imported, not re-implemented:
  H-REP-DES   designed A_SB < 0 AND designed A_SN < 0        each Yuen 20% one-sided, alpha 0.05; a Yuen p in (0.04, 0.05]
  H-REP-PAIR  P > 0 AND P_N > 0                              counts only with the exact Wilcoxon p <= 0.05; IUT p = max;
                                                             Holm over DES and PAIR
  A2.9        I and I - I_N beside each line, direction-aware; "general, not flat-specific" where H is SUPPORTED and I is
              not SPECIFIC
A fauna extinct at season 470 has no garden population: that seed reads UNREAD for it (A1.2), so DES and PAIR are each
scored on their own complete seeds. Gates first: completeness (60 arms, 120 populations), V0 (base, shift and cull20
identical before T = 360 on the five shared seasons.txt columns), V-G (each garden population's n equals seasons.txt
alive at 470). Then Z10 (the arithmetic, seasons 360..369), the scored lines, and the printed-not-scored lines.
"""
import importlib.util
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
spec = importlib.util.spec_from_file_location("rbt107_readout", os.path.join(os.path.dirname(HERE), "readout.py"))
RO = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RO)
RO.GARDEN = os.path.join(HERE, "garden")
SEEDS = list(range(11, 31))
T, D = 360, 110
KINDS = RO.KINDS
ARMS = ("base", "shift", "cull20")


def tables(arm, seed):
    return os.path.join(HERE, "tables", f"{arm}-{seed}")


def main():
    print(__doc__.split("\n\n")[0])
    sm = RO.Sample("FRESH", SEEDS, True)
    print("\n== PROVENANCE (each arm's T + 110 population comes from a restored copy of its checkpoint, cut to season 470)")
    for s in SEEDS:
        print("  " + " | ".join(open(os.path.join(tables(a, s), "source.txt")).read().strip() for a in ARMS
                                if os.path.exists(os.path.join(tables(a, s), "source.txt"))))
    print("\n== GATES")
    arms, ok, missing = {}, True, []
    for s in SEEDS:
        for a in ARMS:
            p = tables(a, s)
            if os.path.exists(os.path.join(p, "seasons.txt")):
                arms[(a, s)] = RO.R92.Arm(p)
            else:
                missing.append(f"{a}-{s}")
    pops = [RO.garden(sm.label(a, s, k, D)) for s in SEEDS for a in ARMS for k in KINDS]
    npop = sum(p is not None for p in pops)
    print(f"  COMPLETENESS: {len(arms)}/60 arms' cut tables, {npop}/120 garden populations"
          + (f"; missing tables {missing}" if missing else ""))
    ok &= len(arms) == 60 and npop == 120
    last = max((a.last for a in arms.values()), default=-1)
    print(f"  NO-PEEK: the last season in any cut table is {last} (must be <= 470)")
    ok &= last <= 470
    bad0 = []
    for s in SEEDS:
        B = arms.get(("base", s))
        for a in ("shift", "cull20"):
            X = arms.get((a, s))
            if B and X:
                bad = [t for t in range(T) for k in KINDS
                       if any(B.raw.get((t, k), {}).get(c) != X.raw.get((t, k), {}).get(c) for c in RO.V0_COLS)]
                if bad:
                    bad0.append(f"{a}-{s} at {bad[0]}")
    print(f"  V0 (seasons 0..359 identical across base, shift, cull20): {'PASS' if not bad0 else 'FAIL ' + str(bad0)}")
    ok &= not bad0
    badg = []
    for s in SEEDS:
        for a in ARMS:
            for k in KINDS:
                rows, arm = RO.garden(sm.label(a, s, k, D)), arms.get((a, s))
                if rows is not None and arm is not None:
                    alive = arm.alive[k].get(T + D, -1)
                    if len(rows) != alive or set(rows) != arm.alive_at(k, T + D):
                        badg.append(f"{a}-{s}-{k} n={len(rows)} alive={alive}")
    print(f"  V-G (garden population = the fauna alive at the end of season 470, by name): {'PASS' if not badg else 'FAIL ' + str(badg)}")
    ok &= not badg
    print(f"  ALL GATES: {'PASS' if ok else 'FAIL: nothing below enters a sentence'}")

    print("\n== THE ARITHMETIC: Z10 (the ecology's own seasons 360..369, pre-onset individuals paired by name)")
    RO.z10(sm)

    print(f"\n== H-REP (T + {D} = season {T + D}): §5.5 as amended by A2.8 (IUT) and A2.9 (interpretation), fresh seeds 11-30")
    dsb, dsn = RO.table(sm, "conventional", D, "SB"), RO.table(sm, "conventional", D, "SN")
    pb, pn = RO.paired(sm, D, "SB"), RO.paired(sm, D, "SN")
    # A1.2: a fauna extinct at the read point has no garden population, and that seed reads UNREAD for that fauna.
    # DES needs the designed fauna in all three arms; PAIR needs both faunas.  Each is scored on its own complete seeds.
    sd = [s for s in SEEDS if s in dsb and s in dsn]
    sp = [s for s in SEEDS if s in pb and s in pn]
    seeds = sp
    for k in KINDS:
        un = [f"{s} ({', '.join(a for a in ARMS if not RO.garden(sm.label(a, s, k, D)))} extinct)" for s in SEEDS
              if not all(RO.garden(sm.label(a, s, k, D)) for a in ARMS)]
        print(f"  {k:12s} UNREAD (A1.2, extinct at season {T + D}): {', '.join(un) if un else 'none'}")
    print(f"  DES n = {len(sd)} seeds (designed A_SB and A_SN); PAIR n = {len(sp)} seeds (both faunas)")
    print(f"  designed A_SB {RO.fmt([dsb[s] for s in sd])} | designed A_SN {RO.fmt([dsn[s] for s in sd])}")
    print(f"  paired P {RO.fmt([pb[s] for s in sp])} | paired P_N {RO.fmt([pn[s] for s in sp])}")
    p_des, l1 = RO.iut("H-REP-DES designed", [dsb[s] for s in sd], [dsn[s] for s in sd], -1)
    p_pair, l2 = RO.iut("H-REP-PAIR paired", [pb[s] for s in sp], [pn[s] for s in sp], +1)
    rej = RO.ST.holm([p_des, p_pair], RO.ALPHA)
    print("\n".join(l1 + l2))
    print(f"  H-REP (IUT, Holm at alpha {RO.ALPHA} over DES and PAIR): H-REP-DES {'SUPPORTED' if rej[0] else 'NOT SUPPORTED'} "
          f"(IUT p {p_des:.4f}); H-REP-PAIR {'SUPPORTED' if rej[1] else 'NOT SUPPORTED'} (IUT p {p_pair:.4f})")
    for half, label, supported, direction in (("DES", "designed", rej[0], -1), ("PAIR", "paired", rej[1], +1)):
        if half == "DES":
            ii = [RO.table(sm, "conventional", D, "I")[s] for s in sd]
            iin = [RO.table(sm, "conventional", D, "I")[s] - RO.table(sm, "conventional", D, "IN")[s] for s in sd]
        else:
            ico, ide = RO.table(sm, "holistic", D, "I"), RO.table(sm, "conventional", D, "I")
            ino, ind = RO.table(sm, "holistic", D, "IN"), RO.table(sm, "conventional", D, "IN")
            ii = [ico[s] - ide[s] for s in sp]
            iin = [(ico[s] - ide[s]) - (ino[s] - ind[s]) for s in sp]
        split = RO.specificity(ii, iin, direction)
        reading = ("flat-specific" if split == "SPECIFIC" else "general, not flat-specific") if supported else "not supported"
        print(f"    H-REP-{half} specialisation ({label}): I {RO.fmt(ii)}; I - I_N {RO.fmt(iin)}; I is {split}; reading: {reading}")

    print("\n== PRINTED, NOT SCORED")
    rr = RO.table(sm, "conventional", D, "RSB")
    print(f"  designed RESPONSE_random (G_S^random - G_B^random) {RO.fmt([rr[s] for s in sd])}")
    nr = {s: RO.G(RO.garden(sm.label("cull20", s, "conventional", D)))[1] - RO.G(RO.garden(sm.label("base", s, "conventional", D)))[1]
          for s in sd}
    print(f"  A2.9 point 3 (post hoc, to watch): designed RESPONSE_random net of the null (G_S^random - G_N^random) "
          f"{RO.fmt([rr[s] - nr[s] for s in sd])}")
    ref = RO.table(sm, "conventional", D, "REF")
    print(f"  designed REFUND at T+110 (G_B^flat - G_B^random) {RO.fmt([ref[s] for s in sd])}")
    for k in KINDS:
        sb, sn, nb = (RO.table(sm, k, D, key) for key in ("SB", "SN", "NB"))
        sk = [s for s in SEEDS if s in sb and s in sn]
        print(f"  {k:12s} (n {len(sk)}) A_SB {RO.fmt([sb[s] for s in sk])} | A_SN {RO.fmt([sn[s] for s in sk])} | null A_NB {RO.fmt([nb[s] for s in sk])}")
    m = statistics.fmean(pb[s] for s in seeds)
    print(f"  paired P in paired A/A units: {m / RO.PAIRED_AA[1]:+.1f} to {m / RO.PAIRED_AA[0]:+.1f}")
    full = RO.below([dsb[s] for s in sd]) and RO.below([rr[s] for s in sd]) and RO.above([pb[s] for s in sp])
    print(f"  RBT-101 F2's full pattern (designed flat and random below 0, paired above 0; t intervals): {'HOLDS' if full else 'does not hold'}")
    print("  split-half (worlds 0..15 against 16..31):")
    for k in KINDS:
        diffs = []
        for s in SEEDS:
            a, b = RO.contrasts(sm, s, k, D, "w00-15"), RO.contrasts(sm, s, k, D, "w16-31")
            if a and b:
                diffs.append(a["SB"] - b["SB"])
        if diffs:
            print(f"    {k:12s} measurement sd of a seed's A_SB at J=32 ~ {math.sqrt(statistics.fmean(x * x for x in diffs)) / 2:.3f}")
    print("  per seed (designed A_SB, designed A_SN, paired P, paired P_N; UNREAD where a fauna is extinct):")
    f = lambda t, s: f"{t[s]:+.3f}" if s in t else "UNREAD"
    for s in SEEDS:
        print(f"    seed {s:>2}: {f(dsb, s)} {f(dsn, s)} {f(pb, s)} {f(pn, s)}")


if __name__ == "__main__":
    main()
