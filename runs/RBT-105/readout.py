"""RBT-105: founders or history?  The pre-registered rule, applied to the committed per-arm files alone.

Reads, per replicate arm ``runs/RBT-105/forage-<seed>-b<K>/``: oscillator.txt (RBT-84 oscillator_rate.py's
last JSON line, "distinct"), pairing.txt, and EXTINCT.txt if present; and, per seed, the original arm's
committed ``runs/RBT-90/forage-<seed>/oscillator.txt`` (the K = 0 stream).  The count, its bars and the
fate function are imported from runs/RBT-90/part2_readout.py unchanged, so the fate is read exactly as
RBT-90 part 2 read it.  It never opens the bulk.

    python runs/RBT-105/readout.py  > runs/RBT-105/readout.txt

The rules (PREREGISTRATION.md section 3, as amended after the design adversary, coordinator's ruling 17:35 UTC),
fixed before any arm.  A replicate is decided if its fate is; F = flips (a decided replicate whose fate is opposite
to its original's) among the n decided replicates.
  R1 (PRIMARY)   FOUNDERS DOMINANT     P(Bin(n, 1/2) <= F) <= 0.05      (n = 16: F <= 4; n = 8: F <= 1)
                 SUBSTANTIAL HISTORY   P(Bin(n, 0.1) >= F) <= 0.05      (n = 16: F >= 5; n = 8: F >= 3)
                 NOT DECIDED           otherwise
                 a FOUNDERS verdict carries n and the flip rate q it excludes at 95% (one-sided Clopper-Pearson
                 upper bound on F/n), with P(FOUNDERS DOMINANT | founders fix the fate) from the adversary's power.txt
  R2 (secondary) T = mean y over the replicates of originally acquired seeds - mean y over the replicates of
                 originally discarded seeds, y = log((k + 0.5) / (n + 1)) of the late (300-599) birth-level
                 linked-oscillator rate (osc_births.txt); exact one-sided permutation p over the replicate arms'
                 labels, the originals left out (they were selected on outcome); "founders shift the late rate" if p <= 0.05
  R0 (printed, q > 0 only)  the first rule: HISTORY on >= 1 flip; FOUNDING POPULATION if every replicate is decided and
                 equal to its original with >= 2 of each fate; else NOT DECIDED.  It answers only "is q > 0?"
  per seed       FLIPS / REPLICATES / UNCLEAR, as before (reported)
  gate           no verdict unless the positive control (K = 0) reproduced its RBT-90 arm byte for byte, every
                 K >= 1 arm kept its founders and designed-body fauna (pairing.txt), and all 17 arms are in
"""
import importlib.util
import itertools
import json
import math
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ARMS = pathlib.Path(os.environ.get("RBT105_ARMS", HERE))  #: the override is for the smoke test only
spec = importlib.util.spec_from_file_location("part2", ROOT / "runs" / "RBT-90" / "part2_readout.py")
part2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(part2)
OSC_DISCARD, OSC_ACQUIRE, osc_fate = part2.OSC_DISCARD, part2.OSC_ACQUIRE, part2.osc_fate

#: the pre-registered design (PREREGISTRATION.md section 2, amended): both waves run unconditionally, 17 arms
WAVE1 = {7: (1, 2), 805: (1, 2), 4: (1, 2), 807: (1, 2)}
WAVE2 = {806: (1, 2), 2: (1, 2), 1: (1, 2), 804: (1, 2)}
DESIGN = {**WAVE1, **WAVE2}
ALPHA = 0.05
Q_SUBST = 0.1      #: R1's "substantial history" null flip rate
#: P(FOUNDERS DOMINANT | the founders fix the fate), R1 at icc = 1, from runs/RBT-105/adversary/power.txt (PR #154)
P_FOUNDERS_GIVEN_FIXED = {8: "0.986 (two-state model), 0.788 (lognormal)", 16: "1.000 (two-state model), 0.997 (lognormal)"}
CONTROL = (7, 0)   #: the positive control arm (seed, K)
NEED_EACH = 2      #: replicating founding populations of each fate a FOUNDING POPULATION verdict needs
OPPOSITE = {"discarded": "acquired", "acquired": "discarded"}


def arm_dir(seed, k):
    return ARMS / f"forage-{seed}-b{k}"


def fate_of(path):
    """(distinct, fate) from an oscillator.txt, or (None, 'extinct'/'missing')."""
    d = path.parent
    if (d / "EXTINCT.txt").exists():
        return None, "extinct"
    if not path.exists():
        return None, "missing"
    osc = part2.last_json(path)
    return osc["distinct"], osc_fate({"osc": osc})


def winners(arm):
    """The founders the living at the last season trace to by first parent, with counts (reported only)."""
    recs = {}
    with open(arm / "lineage-last.txt") as f:
        f.readline()
        for line in f:
            pop, name, gen, age, evals, fit, parents = line.rstrip("\n").split("\t")
            if pop == "holistic":
                recs[name] = (int(gen), parents.split(",") if parents else [])
    last = max(g for g, _ in recs.values())
    out = {}
    for name, (g, _) in recs.items():
        if g != last:
            continue
        cur, seen = name, set()
        while recs[cur][1] and recs[cur][1][0] in recs and cur not in seen:
            seen.add(cur)
            cur = recs[cur][1][0]
        out[cur] = out.get(cur, 0) + 1
    return " ".join(f"{n} x{c}" for n, c in sorted(out.items(), key=lambda x: -x[1]))


def pairing_ok(seed, k):
    p = arm_dir(seed, k) / "pairing.txt"
    if not p.exists():
        return None
    t = p.read_text()
    need = ["founders (genomes and ages at season 0) identical to the RBT-90 arm: True", "designed-body seasons.txt rows identical over the arm's 600 seasons: True"]
    if k == 0:
        need += ["seasons.txt byte-identical to the RBT-90 arm's committed file: True", "lineage-last.txt byte-identical to the RBT-90 arm's committed file: True"]
    return all(n in t for n in need)


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1)) if k >= 0 else 0.0


def q_upper(F, n, alpha=ALPHA):
    """One-sided 95% upper bound on the flip rate: the q at which P(Bin(n, q) <= F) = alpha (Clopper-Pearson)."""
    lo, hi = F / n, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if binom_cdf(F, n, mid) > alpha else (lo, mid)
    return hi


def r1(F, n):
    if n == 0:
        return "NOT DECIDED (no decided replicate)"
    if binom_cdf(F, n, 0.5) <= ALPHA:
        pf = P_FOUNDERS_GIVEN_FIXED.get(n, "not simulated at this n")
        return (f"FOUNDERS DOMINANT: {F} flip(s) in {n} decided replicates (P(Bin({n}, 1/2) <= {F}) = {binom_cdf(F, n, 0.5):.4f}); "
                f"this excludes a flip rate q >= {q_upper(F, n):.2f} at 95%. P(FOUNDERS DOMINANT | founders fix the fate) = {pf}")
    if 1 - binom_cdf(F - 1, n, Q_SUBST) <= ALPHA:
        return f"SUBSTANTIAL HISTORY: {F} flips in {n} decided replicates (P(Bin({n}, {Q_SUBST}) >= {F}) = {1 - binom_cdf(F - 1, n, Q_SUBST):.4f})"
    return f"NOT DECIDED: {F} flips in {n} decided replicates, between the two bars"


def late_y(arm):
    """R2's y for one arm: log((k + 0.5) / (n + 1)) of its late (300-599) birth-level rate, or None."""
    path = arm / "osc_births.txt"
    if not path.exists():
        return None, None
    d = part2.last_json(path)
    n, k = d["late_n"], d["late_k"]
    return (math.log((k + 0.5) / (n + 1)) if n else None), (k / n if n else None)


def r2(ys):
    """ys: [(side, y)] over the replicate arms, side +1 acquired original, -1 discarded.  Exact one-sided permutation."""
    y = [v for _, v in ys]
    acq = [i for i, (side, _) in enumerate(ys) if side > 0]
    m, h = len(ys), len(acq)
    stat = lambda idx: sum(y[i] for i in idx) / h - sum(y[i] for i in range(m) if i not in idx) / (m - h)
    t = stat(set(acq))
    null = [stat(set(c)) for c in itertools.combinations(range(m), h)]
    return t, sum(1 for v in null if v >= t - 1e-12) / len(null), len(null)


def main():
    print("RBT-105: oscillator fate from the same founders under replicate breeding streams (--breed-stream K).")
    print(f"Fate as RBT-90 part 2 reads it: distinct saved bests carrying a linked oscillator, <= {OSC_DISCARD} discarded, >= {OSC_ACQUIRE} acquired, 3-7 undecided.")
    print(f"Design (both waves, unconditional): seeds {sorted(WAVE1)} then {sorted(WAVE2)}, K = 1, 2 each; positive control seed {CONTROL[0]} K = {CONTROL[1]}.\n")
    gate, missing = [], []
    ok = pairing_ok(*CONTROL)
    if ok is None:
        missing.append(f"{CONTROL[0]}-b{CONTROL[1]}")
    print(f"positive control forage-{CONTROL[0]}-b{CONTROL[1]}: " + {None: "NOT RUN", True: "reproduces the RBT-90 arm byte for byte", False: "FAILED"}[ok])
    if ok is False:
        gate.append("positive control")
    print(f"\n{'seed':>5s} {'K':>2s} {'distinct':>8s} {'fate':>10s} {'late rate':>9s} {'paired':>6s}  winning founder lines (first parent)")
    per_seed, F, n, ys = {}, 0, 0, []
    for seed, ks in DESIGN.items():
        d0, f0 = fate_of(ROOT / "runs" / "RBT-90" / f"forage-{seed}" / "oscillator.txt")
        print(f"{seed:5d} {0:2d} {d0:8d} {f0:>10s} {'':>9s} {'orig':>6s}  {winners(ROOT / 'runs' / 'RBT-90' / f'forage-{seed}')}  (the RBT-90 part 2 arm)")
        fates = []
        for k in ks:
            d, f = fate_of(arm_dir(seed, k) / "oscillator.txt")
            p = pairing_ok(seed, k)
            if f == "missing":
                missing.append(f"{seed}-b{k}")
            elif not p:
                gate.append(f"pairing {seed}-b{k}")
            fates.append(f)
            y, rate = late_y(arm_dir(seed, k))
            if f != "missing":
                if y is None:
                    missing.append(f"{seed}-b{k} osc_births")
                else:
                    ys.append((1 if f0 == "acquired" else -1, y))
            if f in OPPOSITE and f0 in OPPOSITE:
                n += 1
                F += f == OPPOSITE[f0]
            w = winners(arm_dir(seed, k)) if (arm_dir(seed, k) / "lineage-last.txt").exists() else "--"
            print(f"{seed:5d} {k:2d} {d if d is not None else '--':>8} {f:>10s} {rate if rate is not None else float('nan'):9.3f} {str(p):>6s}  {w}")
        if any(f == OPPOSITE.get(f0) for f in fates):
            per_seed[seed] = ("FLIPS", f0)
        elif f0 in OPPOSITE and all(f == f0 for f in fates):
            per_seed[seed] = ("REPLICATES", f0)
        else:
            per_seed[seed] = ("UNCLEAR", f0)
    print()
    for seed, (v, f0) in per_seed.items():
        print(f"  seed {seed:4d} (originally {f0}): {v}")
    flips = [s for s, (v, _) in per_seed.items() if v == "FLIPS"]
    rep = [f0 for v, f0 in per_seed.values() if v == "REPLICATES"]
    if flips:
        v0 = f"HISTORY (q > 0 only): the same founders reach both fates on {len(flips)} of {len(per_seed)} founding populations ({', '.join(map(str, flips))}); this does not say how much the founders shift the fate (R1, R2)"
    elif len(rep) == len(per_seed) and rep.count("discarded") >= NEED_EACH and rep.count("acquired") >= NEED_EACH:
        v0 = f"FOUNDING POPULATION (q > 0 only): no flip in {n} decided replicates; this excludes q >= {q_upper(0, n):.2f} at 95%"
    else:
        v0 = "NOT DECIDED (q > 0 only)"
    print(f"\nflips F = {F} among n = {n} decided replicates")
    if missing:
        print(f"\nverdict: incomplete ({', '.join(missing)} not analysed): no verdict; all 17 arms are pre-registered")
        return
    if gate:
        print(f"\nverdict: INVALID: {', '.join(gate)} failed; no verdict")
        return
    print(f"\nR1 (primary) verdict: {r1(F, n)}")
    if len({side for side, _ in ys}) == 2:
        t, p2, nperm = r2(ys)
        print(f"R2 (secondary): T = {t:+.3f} (mean log late rate, replicates of acquired minus discarded originals), exact permutation p = {p2:.4f} over {nperm} labellings -> "
              + ("founders shift the late oscillator rate" if p2 <= ALPHA else "not shown at p <= 0.05"))
    print(f"R0 (reported, q > 0 only): {v0}")


if __name__ == "__main__":
    main()
