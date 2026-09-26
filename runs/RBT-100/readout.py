"""RBT-100, epoch C3 (scarce food): the readout, from committed tables only, on RBT-92's instrument.

    python runs/RBT-100/readout.py > runs/RBT-100/readout.txt

Part 1 is RBT-92's readout.py run unchanged (its validation gates V0-V3, power line, R-body, R-shift,
R-null, R-cull, R-cull20, recovery time, alive, carriage and the RBT-89 section 9 verdict), with its arm
paths pointed at C3's arms:

    base    the seed's RBT-90 part 2 arm, no event          runs/RBT-90/forage-SEED/
    shift   --shift-at T --shift food-items=6               runs/RBT-100/shift-SEED/
    cull    --cull-at T, k by RBT-89 section 8's rule        runs/RBT-100/cull-SEED/   (k in runs/RBT-100/cull-k-SEED.txt)
    cull20  --cull-at T --cull holistic=20,conventional=20   runs/RBT-92/cull20-SEED/  (RBT-92's arm: the same command)

T is read from RBT-92's onset.txt, the baseline body digests from RBT-92's base-SEED/.  Whatever RBT-92's
adversary round and answer change in readout.py, onset.py or cull_k.py is therefore what this readout runs.

Part 2 prints the C3-specific lines the RBT-100 pre-registration adds (runs/RBT-100/PREREGISTRATION.md
section 3, 4 and 6).  None of them changes the class; each is a reading the report must print beside it:

  C3-V1    the shift arm's events.txt records food.items = 6 from T (manipulation, C3's flag and value)
  NULL     per fauna: k; excess deaths shift - base over [T, T+10), [T, T+30), [T, T+60); births deficit
           base - shift over [T, T+60); alive deficit base - shift at T+10, T+30, T+60.  The null is an
           impulse of k at T; "UNDERSIZED" when the median alive deficit at T+30 exceeds twice the median
           k + 2, and then the turnover guard for that fauna is printed as not interpretable
  ECHO     per seed, arm (shift, base) and fauna: the onset seasons (relative to T) of every 10-season
           deaths window >= 20 (RBT-89 section 8's peak) in [T, T+200); seeds with a holistic peak
           starting inside the recovery window [T+60, T+150], shift against base
  CLASS D  per seed, which of RBT-89's triggers fired for each fauna in the shift arm, and the season
           each fauna reached alive = 0, if it did
  DEPTH    median reproduction events after T along the lineages alive at T+160 (first parent followed
           back to the first ancestor born before T), per arm and fauna

Environment overrides for the smoke test only: RBT100_ARM_DIR, RBT100_C1_DIR, and RBT-92's RBT92_* ones
(RBT92_ARM_DIR is set here to C3's directory, so that RBT-92's V1 reads C3's cull-k files).
"""
import importlib.util
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C1 = os.environ.get("RBT100_C1_DIR", os.path.join(HERE, "..", "RBT-92"))
C3 = os.environ.get("RBT100_ARM_DIR", "runs/RBT-100")
os.environ.setdefault("RBT92_ONSET", os.path.join(C1, "onset.txt"))
os.environ["RBT92_ARM_DIR"] = C3  # cull-k-SEED.txt (V1) is C3's own; cull20 and base digests: below

spec = importlib.util.spec_from_file_location("rbt92_readout", os.path.join(HERE, "..", "RBT-92", "readout.py"))
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
_arm_path_c1 = R.arm_path


def arm_path(arm, seed):
    """C3's own arms are shift and cull; base and cull20 are where RBT-92 reads them."""
    if arm == "cull20":
        return os.path.join(C1, f"cull20-{seed}")
    return os.path.join(C3, f"{arm}-{seed}") if arm in ("shift", "cull") else _arm_path_c1(arm, seed)


class Arm(R.Arm):
    """RBT-92's Arm, with the baseline's body digests read where RBT-92 commits them (C1/base-SEED/)."""

    def __init__(self, path, bodysig=None):
        if bodysig and os.path.dirname(os.path.dirname(bodysig)) == R.ARM_DIR.rstrip("/"):
            bodysig = os.path.join(C1, os.path.basename(os.path.dirname(bodysig)), "bodysig.txt")
        super().__init__(path, bodysig)


R.arm_path = arm_path
R.Arm = Arm
KINDS = R.KINDS
PEAK = 20  # RBT-89 section 8: a ten-season deaths window reaching 20 of 60


def cull_k(seed):
    kf = os.path.join(C3, f"cull-k-{seed}.txt")
    if os.path.exists(kf):
        for line in open(kf):
            if line.startswith("cull\t"):
                return {p.split("=")[0]: int(p.split("=")[1]) for p in line.split("\t")[1].strip().split(",")}
    return {}


def shift_record(path):
    ev = os.path.join(path, "events.txt")
    if os.path.exists(ev):
        for r in R.tsv(ev):
            if r["kind"] == "shift":
                return r
    return None


def peaks(arm, kind, T, lo, hi):
    """Start seasons (relative to T) of each run of 10-season deaths windows reaching PEAK, windows in [T+lo, T+hi)."""
    out, prev = [], False
    for s in range(T + lo, T + hi - 9):
        hit = sum(arm.deaths[kind].get(t, 0) for t in range(s, s + 10)) >= PEAK
        if hit and not prev:
            out.append(s - T)
        prev = hit
    return out


def births(arm, kind, t):
    r = arm.raw.get((t, kind))
    return int(r["births"]) if r else 0


def extinct_at(arm, kind, T):
    return next((s for s in range(T, arm.last + 1) if arm.alive[kind].get(s, 0) == 0), None)


def depth_after(arm, kind, T, s):
    """Reproduction events after T along each lineage alive at s: steps back along the first parent until
    an ancestor born before T.  Returns the median over the living, or None."""
    born = {n: b for (k, n), (b, l, p) in arm.ind.items() if k == kind}
    par = {n: p for (k, n), (b, l, p) in arm.ind.items() if k == kind}
    ds = []
    for n in arm.alive_at(kind, s):
        d, cur = 0, n
        while cur in born and born[cur] >= T:
            d += 1
            ps = par.get(cur) or []
            if not ps:
                break
            cur = ps[0]
        ds.append(d)
    return statistics.median(ds) if ds else None


def part2():
    T_of = R.onsets()
    seeds, arms = [], {}
    for seed in R.SEEDS:
        T = T_of.get(seed)
        if not isinstance(T, int):
            continue
        k00 = cull_k(seed) == {"holistic": 0, "conventional": 0}  # RBT-92 amendment 2: the null is the baseline itself
        if any(not os.path.exists(os.path.join(arm_path(a, seed), "seasons.txt")) and not (a == "cull" and k00) for a in R.ARMS):
            continue
        A = {a: R.Arm(arm_path(a, seed)) for a in ("base", "shift") + (() if k00 else ("cull",))}
        if k00:
            A["cull"] = A["base"]
        if any(A["base"].alive[k].get(T - 1, 0) == 0 for k in KINDS):
            continue
        if any(A[a].last < T + R.TRANS + R.RECOV + R.TAIL - 1 for a in A):
            continue
        seeds.append((seed, T))
        arms[seed] = A
    n = len(seeds)
    kk = math.ceil(0.8 * n) if n else 0
    TR, RE, TA = R.TRANS, R.RECOV, R.TAIL
    print()
    print("=" * 100)
    print("RBT-100 PART 2: the C3-specific lines (PREREGISTRATION.md sections 3, 4, 6); none changes the class")
    print(f"  seeds read: {n}  (the same seeds, T and exclusions as part 1)")
    print()
    print("C3-V1 manipulation: the shift arm's events.txt records food.items = 6 from T")
    bad = 0
    for seed, T in seeds:
        r = shift_record(arm_path("shift", seed))
        ok = r is not None and int(r["season"]) == T and '"food.items"' in r["names"] and '"value": 6' in r["names"]
        bad += not ok
        print(f"  {seed:>5} T={T}: {'ok' if ok else 'FAIL'}  {r['names'] if r else 'no shift record'}")
    print(f"  C3-V1: {'PASS' if not bad else 'FAIL'} on {n - bad}/{n}")
    print()
    print("NULL sizing: the impulse k at T against the shift's own demographic cost (deaths only; no income column)")
    print(f"  {'seed':>5} {'fauna':12s} {'k':>3}  excess deaths [T,+10) [T,+30) [T,+60)   births deficit [T,+60)   alive deficit T+10 T+30 T+60")
    ks, d30 = {k: [] for k in KINDS}, {k: [] for k in KINDS}
    for seed, T in seeds:
        b, s = arms[seed]["base"], arms[seed]["shift"]
        kd = cull_k(seed)
        for k in KINDS:
            ex = [sum(s.deaths[k].get(t, 0) - b.deaths[k].get(t, 0) for t in range(T, T + w)) for w in (10, 30, 60)]
            bd = sum(births(b, k, t) - births(s, k, t) for t in range(T, T + 60))
            ad = [b.alive[k].get(T + w, 0) - s.alive[k].get(T + w, 0) for w in (10, 30, 60)]
            ks[k].append(kd.get(k, 0))
            d30[k].append(ad[1])
            print(f"  {seed:>5} {k:12s} {kd.get(k, '?'):>3}  {ex[0]:>21} {ex[1]:>7} {ex[2]:>7}   {bd:>22}   {ad[0]:>17} {ad[1]:>4} {ad[2]:>4}")
    for k in KINDS:
        if n:
            mk, md = statistics.median(ks[k]), statistics.median(d30[k])
            flag = md > 2 * mk + 2
            print(f"  {k:12s}: median k {mk}, median alive deficit at T+30 {md} -> "
                  + ("UNDERSIZED: the impulse null is smaller than the shift's cost; the turnover guard is not interpretable for this fauna"
                     if flag else "the null is not undersized by the pre-registered test"))
    print()
    print(f"ECHO: onsets (seasons after T) of 10-season deaths windows >= {PEAK} in [T, T+{TR + RE + TA}); recovery window starts {TR}..{TR + RE - 10}")
    inrec = {(a, k): 0 for a in ("shift", "base") for k in KINDS}
    for seed, T in seeds:
        for a in ("shift", "base"):
            cells = []
            for k in KINDS:
                p = peaks(arms[seed][a], k, T, 0, TR + RE + TA)
                inrec[(a, k)] += any(TR <= x <= TR + RE - 10 for x in p)
                cells.append(f"{k} {p}")
            print(f"  {seed:>5} {a:>5}  " + "   ".join(cells))
    for k in KINDS:
        print(f"  {k:12s}: a peak starting inside the recovery window on shift {inrec[('shift', k)]}/{n}, base {inrec[('base', k)]}/{n} seeds"
              + ("  -> the recovery window contains the shift's own echo" if n and inrec[("shift", k)] >= kk and inrec[("base", k)] < kk else ""))
    print()
    print("CLASS D triggers in the shift arm, per seed and fauna (RBT-89 section 9): transient mean < 0.25, recovery mean < 0.25,")
    print("  min alive < 12 over [T, T+160); and the season the fauna reached alive = 0 (relative to T), if it did")
    for seed, T in seeds:
        s = arms[seed]["shift"]
        cells = []
        for k in KINDS:
            tr = R.wmean(s.x[k], T, T + TR)
            rc = R.wmean(s.x[k], T + TR, T + TR + RE)
            ma = min(s.alive[k].get(t, 0) for t in range(T, T + TR + RE))
            ex = extinct_at(s, k, T)
            trig = [nm for nm, hit in (("transient", tr < R.BASAL), ("recovery", rc < R.BASAL), ("alive<12", ma < R.FLOOR)) if hit]
            cells.append(f"{k} trans {R.fmt(tr, 3)} rec {R.fmt(rc, 3)} min alive {ma:>2} extinct {'-' if ex is None else f'T+{ex - T}'} "
                         f"triggers {'+'.join(trig) or 'none'}")
        print(f"  {seed:>5}  " + "  |  ".join(cells))
    print()
    print(f"DEPTH: median reproduction events after T along the lineages alive at T+{TR + RE} (first parent followed)")
    for k in KINDS:
        for a in ("shift", "base", "cull"):
            v = [depth_after(arms[seed][a], k, T, T + TR + RE) for seed, T in seeds]
            vv = [x for x in v if x is not None]
            print(f"  {k:12s} {a:>5}: per seed {v}  median {statistics.median(vv) if vv else '--'}")
    return 0


def main():
    print(__doc__.split("\n\n")[0])
    print(f"PART 1: RBT-92's readout.py on C3's arms (shift, cull under {C3}; cull20, onset and base digests under {C1})")
    print()
    rc = R.main()
    if rc:
        print("PART 1 stopped at validation; part 2 is not printed.")
        return rc
    return part2()


if __name__ == "__main__":
    sys.exit(main())
