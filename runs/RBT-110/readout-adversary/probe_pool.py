"""RBT-110 readout adversary: arithmetic on the four committed split.txt files (no simulation).

Reads each analyst's committed runs/RBT-110/<part>/split.txt from its results branch (git show) and parses the
per-seed vectors (seed order 801 804 805 806 807 1 2 3 4 7; n/a and n/c are missing).  Then:
  P1  the pooled paired RESPONSE at T + 110 under every pooling a reader could defend
  P2  cross-challenge correlation of the per-seed paired RESPONSE (do shared base populations tie the challenges?)
  P3  world-specificity: RESPONSE on the new world minus RESPONSE on the old world, per seed (a difference in
      differences: the part of the RESPONSE that is about the changed world, not a general population difference)
  P4  C2's designed RESPONSE and survivorship: all 10 seeds at T + 50 against the 7 survivors
  P5  C4null: the null on both terrains, seed 801's leverage at r = 190, sign and rank summaries
  P6  scale: per-seed RMS of the paired RESPONSE_null against RBT-105's A/A comparator (scale only)

    python runs/RBT-110/readout-adversary/probe_pool.py > runs/RBT-110/readout-adversary/probe_pool.txt
"""
import math
import re
import statistics as st
import subprocess

SEEDS = [801, 804, 805, 806, 807, 1, 2, 3, 4, 7]
BR = {"C1": "results/RBT-110-C1", "C2": "results/RBT-110-C2", "C3": "results/RBT-110-C3", "C4null": "results/RBT-110-C4null"}
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
        20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069}


def text(part):
    return subprocess.run(["git", "show", f"origin/{BR[part]}:runs/RBT-110/{part}/split.txt"],
                          capture_output=True, text=True, check=True).stdout.splitlines()


SECTION = {"C1": "==== T + {r} ", "C2": "=== T + {r}", "C3": "=== r = {r} ", "C4null": "=== r = {r} "}
FAUNA = {"C1": {"co": "co-evolved (mean", "des": "designed (mean", "pair": "paired (co-evolved"},
         "C2": {"co": "co-evolved", "des": "designed", "pair": "paired (co-evolved - designed)"},
         "C3": {"co": "co-evolved (mean", "des": "designed (mean", "pair": "paired (co-evolved - designed)"},
         "C4null": {"co": "co-evolved", "des": "designed", "pair": "paired (co-evolved - designed)"}}
LABEL = {"C1": {"resp": "RESPONSE: shift - base", "null": "RESPONSE_null", "old": "shift - base on the old world"},
         "C2": {"resp": "RESPONSE: shift - base", "null": "RESPONSE_null", "old": "RESPONSE on the old world", "refund": "REFUND: base"},
         "C3": {"resp": "RESPONSE: shift pop", "null": "RESPONSE_null", "old": "RESPONSE on the old world"},
         "C4null": {"resp": "RESPONSE: shift - base", "null": "RESPONSE_null: cull20 - base, flat",
                    "nullr": "(RESPONSE_null on random"}}
C3PAIR = {"resp": "RESPONSE ", "null": "RESPONSE_null ", "old": "RESPONSE on the old world"}


def vec(part, r, fauna, q):
    L = text(part)
    i = next(j for j, x in enumerate(L) if x.startswith(SECTION[part].format(r=r)))
    head = FAUNA[part][fauna]
    i = next(j for j in range(i + 1, len(L)) if L[j].startswith(head))
    lab = C3PAIR[q] if (part == "C3" and fauna == "pair") else LABEL[part][q]
    j = next(j for j in range(i + 1, len(L)) if L[j].strip().startswith(lab.strip()) and (lab != "RESPONSE " or L[j].strip().split()[0] == "RESPONSE"))
    blob = L[j] if "per seed [" in L[j] else L[j + 1]
    inner = blob.split("per seed [")[1].split("]")[0]
    out = []
    for tok in inner.split(","):
        tok = tok.strip().split(":")[-1].strip()
        out.append(None if tok in ("n/a", "n/c") else float(tok))
    assert len(out) == 10, (part, r, fauna, q, out)
    return out


def stat(v):
    v = [x for x in v if x is not None]
    n, m = len(v), st.fmean(v)
    se = st.stdev(v) / math.sqrt(n)
    return n, m, m - T975[n - 1] * se, m + T975[n - 1] * se, se


def fmt(v):
    n, m, lo, hi, _ = stat(v)
    return f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}] n {n} pos {sum(x > 0 for x in v if x is not None)}/{n}"


def sub(a, b):
    return [None if x is None or y is None else x - y for x, y in zip(a, b)]


def main():
    C4 = 0.27
    P = {c: vec(c, 110, "pair", "resp") for c in ("C1", "C2", "C3")}
    P4 = vec("C4null", 110, "pair", "resp")
    print("P1  pooled paired RESPONSE at T + 110 (C1-C3), against C4's +0.27")
    for c in P:
        print(f"   {c}: " + fmt(P[c]) + "   per seed " + " ".join("  .  " if x is None else f"{x:+.3f}" for x in P[c]))
    allv = [x for c in P for x in P[c] if x is not None]
    print(f"   (a) all seed x challenge values as independent, t(n-1):      {fmt(allv)}   ignores the shared base populations")
    agg = [st.fmean([P[c][i] for c in P if P[c][i] is not None]) for i in range(10)
           if any(P[c][i] is not None for c in P)]
    print(f"   (b) seed-aggregated (mean of a seed's available values), t(9): {fmt(agg)}")
    print("       seeds contribute " + ", ".join(f"{s}:{sum(P[c][i] is not None for c in P)}" for i, s in enumerate(SEEDS)) + " challenges")
    # (c) fixed-effect inverse-variance of the three challenge means
    ms = {c: stat(P[c]) for c in P}
    w = {c: 1 / ms[c][4] ** 2 for c in P}
    fe = sum(w[c] * ms[c][1] for c in P) / sum(w.values())
    fse = 1 / math.sqrt(sum(w.values()))
    print(f"   (c) fixed-effect inverse-variance of the 3 challenge means:     {fe:+.3f} [{fe - 1.96 * fse:+.3f}, {fe + 1.96 * fse:+.3f}]  (normal)")
    # (d) random effects: the three challenge means as the units, t(2)
    cm = [ms[c][1] for c in P]
    m3, se3 = st.fmean(cm), st.stdev(cm) / math.sqrt(3)
    print(f"   (d) challenge as the unit (3 means, t(2)):                      {m3:+.3f} [{m3 - T975[2] * se3:+.3f}, {m3 + T975[2] * se3:+.3f}]")
    # (e) DerSimonian-Laird
    Q = sum(w[c] * (ms[c][1] - fe) ** 2 for c in P)
    tau2 = max(0.0, (Q - 2) / (sum(w.values()) - sum(x * x for x in w.values()) / sum(w.values())))
    wr = {c: 1 / (ms[c][4] ** 2 + tau2) for c in P}
    re_ = sum(wr[c] * ms[c][1] for c in P) / sum(wr.values())
    rse = 1 / math.sqrt(sum(wr.values()))
    print(f"   (e) DerSimonian-Laird random effects (Q {Q:.2f}, tau^2 {tau2:.4f}):  {re_:+.3f} [{re_ - 1.96 * rse:+.3f}, {re_ + 1.96 * rse:+.3f}]")
    # (f) seed-aggregated over the 7 seeds with all three... and over the seeds where C1 and C3 exist
    full = [st.fmean([P[c][i] for c in P]) for i in range(10) if all(P[c][i] is not None for c in P)]
    print(f"   (f) seeds with all three challenges only (n {len(full)}):          {fmt(full)}")
    # (g) seed-aggregated, each challenge first centred on nothing: equal-weight mean of challenges per seed, imputing none
    print(f"   C4 (in-sample) paired RESPONSE: {fmt(P4)}")
    diff = sub(P4, [None if not any(P[c][i] is not None for c in P) else st.fmean([P[c][i] for c in P if P[c][i] is not None]) for i in range(10)])
    print(f"   C4 minus the seed-aggregated C1-C3 value, per seed (paired on seed, n {len([x for x in diff if x is not None])}): {fmt(diff)}")
    print()
    print("P2  within-seed correlation of the paired RESPONSE across challenges (shared base populations)")
    names = ["C1", "C2", "C3", "C4null"]
    V = dict(P, C4null=P4)
    for a in range(4):
        for b in range(a + 1, 4):
            idx = [i for i in range(10) if V[names[a]][i] is not None and V[names[b]][i] is not None]
            x = [V[names[a]][i] for i in idx]
            y = [V[names[b]][i] for i in idx]
            print(f"   r({names[a]}, {names[b]}) = {st.correlation(x, y):+.2f}  (n {len(idx)})")
    for q in ("null",):
        Vn = {c: vec(c, 110, "pair", "null") for c in ("C1", "C2", "C3", "C4null")}
        print("   the paired RESPONSE_null (the SAME cull20 and base populations on four worlds):")
        for a in range(4):
            for b in range(a + 1, 4):
                print(f"      r({names[a]}, {names[b]}) = {st.correlation(Vn[names[a]], Vn[names[b]]):+.2f}  (n 10)")
        print("      means: " + ", ".join(f"{c} {fmt(Vn[c])}" for c in names))
    print()
    print("P3  world-specificity at T + 110: RESPONSE(new world) - RESPONSE(old world), per seed")
    for c in ("C1", "C2", "C3"):
        for f in ("co", "des", "pair"):
            new, old = vec(c, 110, f, "resp"), vec(c, 110, f, "old")
            print(f"   {c:6s} {f:4s}  new {fmt(new):38s} old {fmt(old):38s} new - old {fmt(sub(new, old))}")
    # C4: the reproduction block carries 'the same on random terrain' per fauna; parse it
    L = text("C4null")
    blk = L[L.index(next(x for x in L if x.startswith("REPRODUCTION"))):]
    def rep(fauna, lab):
        i = next(j for j, x in enumerate(blk) if x.startswith(fauna))
        j = next(j for j in range(i, len(blk)) if lab in blk[j])
        return [float(t) for t in blk[j].split("per seed [")[1].split("]")[0].split(",")]
    cn, co_ = rep("co-evolved", "RESPONSE at T+110: shift pop"), rep("co-evolved", "the same on random terrain")
    dn, do_ = rep("designed", "RESPONSE at T+110: shift pop"), rep("designed", "the same on random terrain")
    for f, new, old in (("co", cn, co_), ("des", dn, do_), ("pair", sub(cn, dn), sub(co_, do_))):
        print(f"   C4     {f:4s}  new {fmt(new):38s} old {fmt(old):38s} new - old {fmt(sub(new, old))}")
    dnull, dnullr = vec("C4null", 110, "des", "null"), vec("C4null", 110, "des", "nullr")
    print(f"   C4     des   RESPONSE net of null: flat {fmt(sub(dn, dnull))}   random {fmt(sub(do_, dnullr))}")
    print("   (C4 old world = random terrain, the reproduction block of C4null/split.txt = the adversary's probe_refund.txt)")
    print()
    print("P4  C2's designed RESPONSE and survivorship (designed extinct in the shift arm at T + 110 on 806, 807, 2)")
    surv = [i for i, s in enumerate(SEEDS) if s not in (806, 807, 2)]
    doom = [i for i, s in enumerate(SEEDS) if s in (806, 807, 2)]
    for r in (50, 110, 190):
        v = vec("C2", r, "des", "resp")
        vs = [v[i] for i in surv]
        vd = [v[i] for i in doom if v[i] is not None]
        print(f"   r = {r:3d}: all available {fmt(v):40s} the 7 survivors {fmt(vs):40s} the 3 doomed seeds {vd}")
    v50 = vec("C2", 50, "des", "resp")
    print(f"   lower bound at r = 110 if the doomed seeds had kept their r = 50 value: "
          f"{fmt([vec('C2', 110, 'des', 'resp')[i] if i in surv else v50[i] for i in range(10)])}")
    need = (0 - st.fmean([vec('C2', 110, 'des', 'resp')[i] for i in surv]) * 7) / 3
    print(f"   the mean the 3 extinct seeds would need for the 10-seed mean to be 0: {need:+.3f} "
          f"(for scale: the designed REFUND, the whole price, is {stat(vec('C2', 110, 'des', 'refund'))[1]:+.3f})")
    print()
    print("P5  C4null: the null on both terrains and seed 801 at r = 190")
    for r in (50, 110, 190):
        for f in ("co", "des", "pair"):
            nf, nr = vec("C4null", r, f, "null"), vec("C4null", r, f, "nullr")
            print(f"   r = {r:3d} {f:4s} null flat {fmt(nf):36s} null random {fmt(nr):36s} flat - random {fmt(sub(nf, nr))}")
    rp, nl = vec("C4null", 190, "pair", "resp"), vec("C4null", 190, "pair", "null")
    net = sub(rp, nl)
    wo = [x if SEEDS[i] != 801 else None for i, x in enumerate(net)]
    print(f"   r = 190 paired net of null, all: {fmt(net)};  without 801: {fmt(wo)};  median {st.median([x for x in net if x is not None]):+.3f}")
    wo2 = [x if SEEDS[i] != 801 else None for i, x in enumerate(nl)]
    print(f"   r = 190 paired null, all: {fmt(nl)};  without 801: {fmt(wo2)}")
    for r in (50, 110, 190):
        rp, nl = vec("C4null", r, "pair", "resp"), vec("C4null", r, "pair", "null")
        print(f"   r = {r:3d} paired RESPONSE {fmt(rp):36s} null {fmt(nl):36s} share of RESPONSE matched by null "
              f"{stat(nl)[1] / stat(rp)[1]:+.2f}")
    print()
    print("P6  scale: per-seed RMS of the paired RESPONSE_null (cull20 - base, new world) at T + 110")
    for c in names:
        v = vec(c, 110, "pair", "null")
        print(f"   {c:6s} RMS {math.sqrt(st.fmean([x * x for x in v])):.3f}  sd {st.stdev(v):.3f}")
    print("   RBT-105's ecology A/A, as permitted: RMS of a single-seed difference 0.10-0.17 (0.132 at RBT-92's recovery")
    print("   window), a comparator of scale for a paired R-body contrast, not a bound and not a null for any event.")


if __name__ == "__main__":
    main()
