"""RBT-110, C4's null: the refund/response split on RBT-101 (flat terrain) with RBT-92's cull20 arm as the null.

Adapted from runs/RBT-101/readout-adversary/probe_refund.py. The world difference is the adversary's, unchanged:
flat (new) against random (old) terrain, random terrain taking terrain seed = the draw. Populations, groups, draws
(D = 4) and seeding are the adversary's: draws from Random("RBT-101 refund SEED"), each population shuffled into groups
of four by Random("SEED POP KIND DRAW"), every population and both terrains on the same start seeds. The only
additions are the cull20 population and the read points r = 50 and 190 (r = 110 primary, run first, and its C0/base/
shift lines are printed in the adversary's format so they can be diffed against probe_refund.txt).
    base    alive in the baseline (RBT-90 part 2) at T + r
    shift   alive in the RBT-101 shift arm at T + r
    cull20  alive in RBT-92's cull20 arm at T + r    (20 of each fauna culled at T, the world unchanged)
    C0      alive in the baseline at T - 1           (the adversary's onset population; r = 110 pass only)
    REFUND        = gain(base, flat)   - gain(base, random)
    RESPONSE      = gain(shift, flat)  - gain(base, flat)
    RESPONSE_null = gain(cull20, flat) - gain(base, flat)
    paired        = co-evolved - designed, per seed
Populations are read from the restored bulk's lineage (README rule 6). A season s is covered by a ckpt only if
s < state.json's season (the lineage past it is a partial season); an uncovered read point, or an extinct population,
is reported per seed and that seed is left out of every value that needs it. Nothing is substituted.

    python runs/RBT-110/C4null/probe_split.py BULKDIR --check 801  > runs/RBT-110/C4null/check.txt
    python runs/RBT-110/C4null/probe_split.py BULKDIR               > runs/RBT-110/C4null/split.txt
BULKDIR holds base-SEED (ckpt/rbt-90-SEED), shift-SEED (ckpt/rbt-101-shift-SEED), cull20-SEED (ckpt/rbt-92-cull20-SEED).
"""
import json
import math
import os
import random
import statistics as st
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-92"))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-101", "readout-adversary"))
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, run_group  # noqa: E402

os.chdir(ROOT)
import readout as R  # noqa: E402
from probe_refund import check  # noqa: E402,F401  (the adversary's harness check, unchanged)

SEEDS, KINDS, TS = R.SEEDS, R.KINDS, R.onsets()
LAB = {"holistic": "co-evolved", "conventional": "designed"}
READS = (110, 50, 190)  # fixed before any number: 110 primary, 50 and 190 secondary
D = 4
ARMS = {"base": "base", "shift": "shift", "cull20": "cull20"}


def world(cfg, terrain, seed):
    w = replace(cfg.world, terrain=terrain, terrain_seed=(int(seed) if terrain == "random" else None))
    return replace(cfg, world=w)


def covered(run):
    return int(json.load(open(f"{run}/state.json"))["season"])  # seasons 0 .. this - 1 are complete


def alive(run, kind, s):
    out = []
    for line in open(f"{run}/lineage.jsonl"):
        r = json.loads(line)
        if r["generation"] == s and r["population"] == kind and "food" in r:  # played season s
            out.append(r["name"])
    return out


def task(args):
    run, kind, names, cfg_d, terrain, seed = args
    cfg = world(SimConfig.from_dict(cfg_d), terrain, seed)
    gs = [Genotype.load(f"{run}/{kind}/genomes/{n}.json") for n in names]
    return [r["score"] for r in run_group(gs, cfg, seed)]


# Student t without scipy: regularised incomplete beta by Lentz's continued fraction.
def _betacf(a, b, x):
    tiny, qab, qap, qam = 1e-300, a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)), -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1 + aa * d
            d = 1 / (d if abs(d) > tiny else tiny)
            c = 1 + aa / c
            c = c if abs(c) > tiny else tiny
            h *= d * c
        if abs(d * c - 1) < 1e-15:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0 or x >= 1:
        return max(0.0, min(1.0, x))
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lb) * _betacf(a, b, x) / a
    return 1 - math.exp(lb) * _betacf(b, a, 1 - x) / b


def tcdf(t, df):
    p = 0.5 * _ibeta(df / 2, 0.5, df / (df + t * t))
    return 1 - p if t > 0 else p


def tq(p, df):
    lo, hi = -100.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tcdf(mid, df) < p else (lo, mid)
    return (lo + hi) / 2


def stats(v, sign=+1):
    """n, mean, sd, 95% t CI, positives, one-sided p in direction sign, MDE at 80% power (one-sided alpha 0.05)."""
    v = [x for x in v if x is not None]
    n = len(v)
    m = st.fmean(v)
    sd = st.stdev(v)
    se = sd / math.sqrt(n)
    hw = tq(0.975, n - 1) * se
    p = 1 - tcdf(sign * m / se, n - 1)
    mde = (tq(0.95, n - 1) + tq(0.80, n - 1)) * se
    return dict(n=n, m=m, sd=sd, lo=m - hw, hi=m + hw, pos=sum(x > 0 for x in v), p=p, mde=mde)


def line(label, v, sign=+1):
    s = stats(v, sign)
    per = ", ".join("  n/a " if x is None else f"{x:+.3f}" for x in v)
    d = ">" if sign > 0 else "<"
    return (f"{label:44s} {s['m']:+.4f} [{s['lo']:+.4f}, {s['hi']:+.4f}] sd {s['sd']:.3f} pos {s['pos']}/{s['n']} "
            f"p1({d}0) {s['p']:.4f} MDE80 {s['mde']:.3f}  per seed [{per}]")


def verdict(v):
    s = stats(v, +1)
    if s["p"] < 0.05 and s["m"] > 0:
        return f"SUPPORTED on the unadjusted one-sided p = {s['p']:.4f} (Holm across challenges left to the coordinator)"
    if s["hi"] < 0:
        return f"CONTRADICTED (95% CI [{s['lo']:+.4f}, {s['hi']:+.4f}] below 0)"
    return f"NOT DECIDED (one-sided p = {s['p']:.4f}; MDE at 80% power {s['mde']:.3f})"


def run_jobs(jobs):
    with ProcessPoolExecutor(int(os.environ.get("WORKERS", "4"))) as ex:
        return list(ex.map(task, jobs, chunksize=2))


def read(bulk, r, with_c0):
    cfgd = json.load(open(f"{bulk}/base-{SEEDS[0]}/config.json"))["sim"]
    jobs, keys, notes = [], [], []
    for s in SEEDS:
        T = TS[s]
        rnd = random.Random(f"RBT-101 refund {s}")
        draws = [rnd.randrange(1, 2**31 - 1) for _ in range(D)]
        pops = {}
        for p, arm in ARMS.items():
            run = f"{bulk}/{arm}-{s}"
            if T + r >= covered(run):
                notes.append(f"  seed {s}: {arm} covers seasons < {covered(run)}; T + {r} = {T + r} NOT COVERED")
                continue
            for k in KINDS:
                pops[(p, k)] = (run, alive(run, k, T + r))
        if with_c0:
            for k in KINDS:
                pops[("C0", k)] = (f"{bulk}/base-{s}", alive(f"{bulk}/base-{s}", k, T - 1))
        for (p, k), (run, names) in pops.items():
            if not names:
                notes.append(f"  seed {s}: {LAB[k]} extinct in {p} at the read point; excluded for that fauna")
            for d, seed in enumerate(draws):
                order = names[:]
                random.Random(f"{s} {p} {k} {d}").shuffle(order)
                for gi in range(0, len(order), 4):
                    grp = order[gi:gi + 4]
                    for terrain in ("random", "flat"):
                        jobs.append((run, k, grp, cfgd, terrain, seed))
                        keys.append((s, p, k, terrain))
    res = run_jobs(jobs)
    acc = {}
    for key, out in zip(keys, res):
        acc.setdefault(key, []).extend(out)
    return {key: st.fmean(v) for key, v in acc.items()}, notes


def diff(G, s, k, a, ta, b, tb):
    x, y = G.get((s, a, k, ta)), G.get((s, b, k, tb))
    return None if x is None or y is None else x - y


def pair(h, c):
    return [None if a is None or b is None else a - b for a, b in zip(h, c)]


def net(a, b):
    return [None if x is None or y is None else x - y for x, y in zip(a, b)]


def adversary_block(G):
    """The adversary's r = 110 lines, in probe_refund.txt's format, for the reproduction diff."""
    def stat(label, v):
        n, m, sd, hw = R.stat(v)
        return f"{label:52s} {m:+.4f} [{m - hw:+.4f}, {m + hw:+.4f}] pos {sum(x > 0 for x in v)}/{n}  per seed [{', '.join(f'{x:+.3f}' for x in v)}]"
    out = {}
    print("REPRODUCTION of runs/RBT-101/readout-adversary/probe_refund.txt (the same lines, the same format)")
    for k in KINDS:
        print(f"{LAB[k]} (mean gain per robot-bout, simulated)")
        out[("c0", k)] = [G[(s, "C0", k, "flat")] - G[(s, "C0", k, "random")] for s in SEEDS]
        out[("refund", k)] = [G[(s, "base", k, "flat")] - G[(s, "base", k, "random")] for s in SEEDS]
        out[("resp", k)] = [G[(s, "shift", k, "flat")] - G[(s, "base", k, "flat")] for s in SEEDS]
        out[("total", k)] = [G[(s, "shift", k, "flat")] - G[(s, "base", k, "random")] for s in SEEDS]
        out[("respr", k)] = [G[(s, "shift", k, "random")] - G[(s, "base", k, "random")] for s in SEEDS]
        print("   " + stat("C0 refund, flat - random (the onset population)", out[("c0", k)]))
        print("   " + stat("REFUND at T+110: base pop, flat - random", out[("refund", k)]))
        print("   " + stat("RESPONSE at T+110: shift pop - base pop, both flat", out[("resp", k)]))
        print("   " + stat("  the same on random terrain (shift pop - base pop)", out[("respr", k)]))
        print("   " + stat("TOTAL = REFUND + RESPONSE (simulated R-shift)", out[("total", k)]))
        print("   " + stat("the refund's drift, T+110 against C0", [a - b for a, b in zip(out[("refund", k)], out[("c0", k)])]))
    print("paired (co-evolved - designed)")
    for lab, key in (("C0 refund", "c0"), ("REFUND at T+110", "refund"), ("RESPONSE at T+110", "resp"), ("TOTAL (simulated event - base)", "total")):
        print("   " + stat(lab, [a - b for a, b in zip(out[(key, "holistic")], out[(key, "conventional")])]))
    print()


def report(G, r, notes):
    print(f"=== r = {r}{' (PRIMARY)' if r == 110 else ' (secondary)'}: read season T + {r}; seeds {' '.join(map(str, SEEDS))}")
    print("coverage and exclusions:" if notes else "coverage and exclusions: every seed covered, no fauna extinct")
    for n_ in notes:
        print(n_)
    v = {}
    for k in KINDS:
        v[("refund", k)] = [diff(G, s, k, "base", "flat", "base", "random") for s in SEEDS]
        v[("resp", k)] = [diff(G, s, k, "shift", "flat", "base", "flat") for s in SEEDS]
        v[("null", k)] = [diff(G, s, k, "cull20", "flat", "base", "flat") for s in SEEDS]
        v[("net", k)] = net(v[("resp", k)], v[("null", k)])
        v[("nullr", k)] = [diff(G, s, k, "cull20", "random", "base", "random") for s in SEEDS]
    for key in ("refund", "resp", "null", "net", "nullr"):
        v[(key, "paired")] = pair(v[(key, "holistic")], v[(key, "conventional")])
    sign = {"holistic": +1, "conventional": -1, "paired": +1}  # H: paired > 0, designed < 0; co-evolved tested > 0
    for k in ("conventional", "holistic", "paired"):
        name = {"conventional": "designed", "holistic": "co-evolved", "paired": "paired (co-evolved - designed)"}[k]
        print(f"{name}")
        print("   " + line(f"REFUND: base, flat - random", v[("refund", k)], +1))
        print("   " + line(f"RESPONSE: shift - base, flat", v[("resp", k)], sign[k]))
        print("   " + line(f"RESPONSE_null: cull20 - base, flat", v[("null", k)], sign[k]))
        print("   " + line(f"RESPONSE net of null (shift - cull20, flat)", v[("net", k)], sign[k]))
        print("   " + line(f"  (RESPONSE_null on random: cull20 - base)", v[("nullr", k)], sign[k]))
    print("n per fauna (seeds entering RESPONSE / RESPONSE_null / net): "
          + "; ".join(f"{LAB[k]} {sum(x is not None for x in v[('resp', k)])}/{sum(x is not None for x in v[('null', k)])}/"
                      f"{sum(x is not None for x in v[('net', k)])}" for k in KINDS)
          + f"; paired {sum(x is not None for x in v[('resp', 'paired')])}/{sum(x is not None for x in v[('null', 'paired')])}/"
            f"{sum(x is not None for x in v[('net', 'paired')])}")
    print(f"verdict, paired RESPONSE at r = {r}: {verdict(v[('resp', 'paired')])}")
    print(f"verdict, paired RESPONSE net of null at r = {r}: {verdict(v[('net', 'paired')])}")
    print(f"verdict, paired RESPONSE_null at r = {r} (turnover alone): {verdict(v[('null', 'paired')])}")
    print()
    sys.stdout.flush()
    return v


def main(bulk):
    print(__doc__.split("\n\n")[0])
    print(f"D = {D} draws per population and terrain; groups of four; read points {READS} (110 primary)")
    print("stats: mean [95% t CI] sd, positives/n, one-sided p in H's direction (paired > 0, designed < 0, co-evolved > 0),")
    print("MDE80 = (t.95 + t.80)(n-1) * sd/sqrt(n), the effect a one-sided alpha 0.05 t test detects with 80% power.")
    print("seasons covered per ckpt (state.json): " + "; ".join(
        f"{s} T={TS[s]} " + "/".join(f"{a}<{covered(f'{bulk}/{a}-{s}')}" for a in ARMS.values()) for s in SEEDS))
    print()
    sys.stdout.flush()
    for r in READS:
        G, notes = read(bulk, r, with_c0=(r == 110))
        if r == 110:
            adversary_block(G)
        report(G, r, notes)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--check":
        check(sys.argv[1], int(sys.argv[3]))
    else:
        main(sys.argv[1])
