"""RBT-110 C1 (crowding, RBT-92): the refund/response split of RBT-101's probe_refund.py, out of sample.

Adapted from runs/RBT-101/readout-adversary/probe_refund.py in the world change only (RBT-110 pre-registration):
    old world  groups of 4 (the baseline's group_size), random terrain, the run's config
    new world  groups of 8 (C1's shift: --shift group-size=8), random terrain, the run's config
The shift changes an ecology field, not the simulator config, so both worlds run the same SimConfig; they differ
only in how each shuffled population is cut into arenas: consecutive runs of 4, or of 8 with the remainder as a
smaller last group, exactly as the ecology cuts a season's permutation (rabbitstew/ecology.py _challenge).  Random
terrain takes terrain seed = the draw on both worlds, as the adversary's random world did.

Per seed and fauna, populations read from restored bulk (README rule 6: genomes and lineage.jsonl, no table):
    base    alive in the RBT-90 part 2 baseline at T + r
    shift   alive in the RBT-92 shift arm at T + r
    cull20  alive in the RBT-92 cull20 arm at T + r   (the null: turnover without a changed world)
    REFUND        gain(base, new)  - gain(base, old)
    RESPONSE      gain(shift, new) - gain(base, new)
    RESPONSE_null gain(cull20, new) - gain(base, new)
    net           RESPONSE - RESPONSE_null = gain(shift, new) - gain(cull20, new)
    paired        co-evolved (holistic) - designed (conventional), per seed
Draws, shuffles and seeding are the adversary's: D start seeds per seed from Random("RBT-101 refund SEED"), shared by
every population and both worlds; each population shuffled by Random("SEED POP KIND DRAW"); the same order is cut
into 4s (old) and 8s (new).  The adversary's C0 population is not needed by any RBT-110 quantity and is not run.
Read points r = 110 (primary), 50 and 190 (secondary).  A read point beyond a ckpt's coverage is "not covered" for
that seed and no other season is substituted.

--check BULK SEED reproduces one recorded pre-T season (T - 1) of the baseline bout for bout against lineage.jsonl,
as probe_refund.py --check does (first four groups per fauna); --check-shift BULK SEED does the same on the shift
arm's season T + 110, whose recorded groups are of 8, so the new world's harness is checked too.

    python runs/RBT-110/C1/probe_split.py BULK --check 3 > runs/RBT-110/C1/check.txt
    python runs/RBT-110/C1/probe_split.py BULK [D] > runs/RBT-110/C1/split.txt
BULK holds base-SEED (ckpt/rbt-90-SEED), shift-SEED (ckpt/rbt-92-shift-SEED), cull20-SEED (ckpt/rbt-92-cull20-SEED).
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
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, run_group  # noqa: E402

os.chdir(ROOT)
import readout as R  # noqa: E402

SEEDS, KINDS, TS = R.SEEDS, R.KINDS, R.onsets()
LAB = {"holistic": "co-evolved", "conventional": "designed"}
RS = (110, 50, 190)  # 110 primary
OLD, NEW = 4, 8
POPS = ("base", "shift", "cull20")
C4_PAIRED = 0.27  # RBT-101 adversary, post hoc, the value H was drawn from


def cfg_of(run):
    return SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])


def world(cfg, seed):
    w = replace(cfg.world, terrain="random", terrain_seed=int(seed))
    return replace(cfg, world=w)


def alive_by_season(run, kind, seasons):
    out = {s: [] for s in seasons}
    for line in open(f"{run}/lineage.jsonl"):
        r = json.loads(line)
        if r["generation"] in out and r["population"] == kind and "food" in r:  # played season s
            out[r["generation"]].append(r["name"])
    return out


def coverage(run):
    """Seasons the bulk covers: the highest season any individual played, plus one."""
    last = -1
    for line in open(f"{run}/lineage.jsonl"):
        r = json.loads(line)
        if "food" in r and r["generation"] > last:
            last = r["generation"]
    return last + 1


def task(args):
    run, kind, names, cfg_d, seed = args
    cfg = world(SimConfig.from_dict(cfg_d), seed)
    gs = [Genotype.load(f"{run}/{kind}/genomes/{n}.json") for n in names]
    return [r["score"] for r in run_group(gs, cfg, seed)]


def check(run, s, label):
    h = [e for e in json.load(open(f"{run}/history.json"))["history"] if e["season"] == s]
    rec = {}
    for line in open(f"{run}/lineage.jsonl"):
        r = json.loads(line)
        if r["generation"] == s and "food" in r:
            rec[(r["population"], r["name"])] = r["last_score"]
    cfg = cfg_of(run)
    n = bad = 0
    sizes = []
    for line in open(f"{run}/cohorts.jsonl"):
        c = json.loads(line)
        if c["season"] != s:
            continue
        kind = c["cohort"]
        ts = [e["terrain_seed"] for e in h if e["population"] == kind][0]
        sim = replace(cfg, world=replace(cfg.world, terrain_seed=int(ts)))
        sizes.append((kind, [len(g) for g in c["groups"]]))
        for grp in c["groups"][:4]:
            gs = [Genotype.load(f"{run}/{kind}/genomes/{m['name']}.json") for m in grp]
            got = [r["score"] for r in run_group(gs, sim, c["start_seed"])]
            for m, g in zip(grp, got):
                n += 1
                bad += round(g, 4) != round(rec[(kind, m["name"])], 4)
                print(f"   {kind:12s} {m['name']:8s} recorded {rec[(kind, m['name'])]:+.4f} re-simulated {g:+.4f}")
    for kind, z in sizes:
        print(f"   recorded group sizes, {kind}: {z}")
    print(f"CHECK {label} season {s}: {n - bad}/{n} bouts reproduce the recorded gain to 4 decimals")
    return n > 0 and bad == 0


# Student t, without scipy: the CDF by the regularised incomplete beta (Numerical Recipes' continued fraction).
def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(1 + aa / c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(1 + aa / c) > 1e-300 else 1e-300
        de = d * c
        h *= de
        if abs(de - 1) < 1e-14:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lb) * _betacf(a, b, x) / a
    return 1 - math.exp(lb) * _betacf(b, a, 1 - x) / b


def t_sf(t, df):
    """P(T > t) for Student t with df degrees of freedom."""
    p = 0.5 * _ibeta(df / 2, 0.5, df / (df + t * t))
    return p if t > 0 else 1 - p


def t_ppf(q, df):
    lo, hi = -50.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1 - t_sf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def summary(v):
    v = [x for x in v if x is not None and not math.isnan(x)]
    n = len(v)
    m = st.fmean(v) if v else float("nan")
    sd = st.stdev(v) if n > 1 else float("nan")
    se = sd / math.sqrt(n) if n > 1 else float("nan")
    hw = t_ppf(0.975, n - 1) * se if n > 1 else float("nan")
    p1 = t_sf(m / se, n - 1) if n > 1 and se > 0 else float("nan")  # one-sided, H1: mean > 0
    mde = (t_ppf(0.95, n - 1) + t_ppf(0.80, n - 1)) * se if n > 1 else float("nan")
    mde3 = (t_ppf(1 - 0.05 / 3, n - 1) + t_ppf(0.80, n - 1)) * se if n > 1 else float("nan")
    return dict(n=n, m=m, sd=sd, lo=m - hw, hi=m + hw, pos=sum(x > 0 for x in v), p1=p1, mde=mde, mde3=mde3)


def line(label, vals):
    z = summary([vals[s] for s in SEEDS if vals.get(s) is not None])
    per = ", ".join(f"{s}:{vals[s]:+.3f}" if vals.get(s) is not None else f"{s}:n/c" for s in SEEDS)
    return (f"{label:44s} {z['m']:+.4f} [{z['lo']:+.4f}, {z['hi']:+.4f}] pos {z['pos']}/{z['n']}  "
            f"p1(>0) {z['p1']:.4f}  sd {z['sd']:.3f}  MDE80 {z['mde']:.3f} (a/3 {z['mde3']:.3f})\n      per seed [{per}]"), z


def main(bulk, D):
    cfgd = json.load(open(f"{bulk}/base-{SEEDS[0]}/config.json"))["sim"]
    for s in SEEDS:  # every arm must run the baseline's simulator config: the shift is an ecology field
        for p in POPS:
            assert json.load(open(f"{bulk}/{p}-{s}/config.json"))["sim"] == cfgd, (p, s)
    cov = {(p, s): coverage(f"{bulk}/{p}-{s}") for p in POPS for s in SEEDS}
    jobs, keys, npop = [], [], {}
    for s in SEEDS:
        T = TS[s]
        rnd = random.Random(f"RBT-101 refund {s}")
        draws = [rnd.randrange(1, 2**31 - 1) for _ in range(D)]
        for p in POPS:
            run = f"{bulk}/{p}-{s}"
            want = [T + r for r in RS if T + r < cov[(p, s)]]
            for k in KINDS:
                al = alive_by_season(run, k, want)
                for r in RS:
                    if T + r not in al:
                        continue
                    names = al[T + r]
                    npop[(s, p, k, r)] = len(names)
                    for d, seed in enumerate(draws):
                        order = names[:]
                        random.Random(f"{s} {p} {k} {d}").shuffle(order)
                        for gsz, w in ((OLD, "old"), (NEW, "new")):
                            if p == "cull20" and w == "old":
                                continue  # the null is read on the new world only
                            for gi in range(0, len(order), gsz):
                                jobs.append((run, k, order[gi:gi + gsz], cfgd, seed))
                                keys.append((s, p, k, r, w))
    with ProcessPoolExecutor(int(os.environ.get("WORKERS", "4"))) as ex:
        res = list(ex.map(task, jobs, chunksize=2))
    acc = {}
    for key, out in zip(keys, res):
        acc.setdefault(key, []).extend(out)
    G = {key: st.fmean(v) for key, v in acc.items()}

    print(__doc__.split("\n\n")[0])
    print(f"D = {D} draws per population and world; old world groups of {OLD}, new world groups of {NEW}; "
          f"read points T + {RS[0]} (primary), T + {RS[1]}, T + {RS[2]}; {len(jobs)} group bouts")
    print()
    print("coverage (seasons in each restored ckpt's lineage.jsonl) and T per seed")
    for s in SEEDS:
        print(f"   {s:4d}  T {TS[s]}  " + "  ".join(f"{p} {cov[(p, s)]}" for p in POPS)
              + "   not covered: " + (", ".join(f"{p} T+{r}" for p in POPS for r in RS if TS[s] + r >= cov[(p, s)]) or "none"))
    print()
    print("population sizes (alive at T + r), per seed: base/shift/cull20")
    for r in RS:
        for k in KINDS:
            print(f"   T+{r:<3d} {LAB[k]:10s} " + "  ".join(
                f"{s}:" + "/".join(str(npop.get((s, p, k, r), "n/c")) for p in POPS) for s in SEEDS))
    print()

    def g(s, p, k, r, w):
        return G.get((s, p, k, r, w))

    def diff(a, b):
        return None if a is None or b is None else a - b

    for r in RS:
        tag = "PRIMARY" if r == 110 else "secondary"
        print(f"==== T + {r} ({tag}) ====")
        q = {}
        for k in KINDS:
            q[("refund", k)] = {s: diff(g(s, "base", k, r, "new"), g(s, "base", k, r, "old")) for s in SEEDS}
            q[("resp", k)] = {s: diff(g(s, "shift", k, r, "new"), g(s, "base", k, r, "new")) for s in SEEDS}
            q[("null", k)] = {s: diff(g(s, "cull20", k, r, "new"), g(s, "base", k, r, "new")) for s in SEEDS}
            q[("net", k)] = {s: diff(q[("resp", k)][s], q[("null", k)][s]) for s in SEEDS}
            q[("respold", k)] = {s: diff(g(s, "shift", k, r, "old"), g(s, "base", k, r, "old")) for s in SEEDS}
            q[("total", k)] = {s: diff(g(s, "shift", k, r, "new"), g(s, "base", k, r, "old")) for s in SEEDS}
        for key in ("refund", "resp", "null", "net", "respold", "total"):
            q[(key, "paired")] = {s: diff(q[(key, "holistic")][s], q[(key, "conventional")][s]) for s in SEEDS}
        names = {"refund": "REFUND: base, new - old", "resp": "RESPONSE: shift - base, new world",
                 "null": "RESPONSE_null: cull20 - base, new world", "net": "RESPONSE net of null (shift - cull20, new)",
                 "respold": "  shift - base on the old world (4s)", "total": "TOTAL: shift new - base old"}
        zs = {}
        for k in (*KINDS, "paired"):
            print(f"{LAB.get(k, 'paired (co-evolved - designed)')} (mean gain per robot-bout, simulated)")
            for key in ("refund", "resp", "null", "net", "respold", "total"):
                txt, zs[(key, k)] = line(names[key], q[(key, k)])
                print("   " + txt)
            print()
        if r == 110:
            z = zs[("resp", "paired")]
            print("VERDICT INPUTS (primary: paired RESPONSE at T + 110)")
            print(f"   n {z['n']}, mean {z['m']:+.4f}, 95% t CI [{z['lo']:+.4f}, {z['hi']:+.4f}], positive {z['pos']}/{z['n']}, "
                  f"one-sided p (H: > 0) {z['p1']:.4f}")
            print(f"   MDE at 80% power (one-sided t, from the observed per-seed sd): {z['mde']:.3f} at a = 0.05, "
                  f"{z['mde3']:.3f} at a = 0.05/3 (Holm's strictest step)")
            if z["hi"] < 0:
                v = "CONTRADICTED (two-sided 95% CI entirely below 0), whatever Holm gives"
            elif z["p1"] >= 0.05 or z["m"] <= 0:
                v = "NOT DECIDED: not SUPPORTED at any Holm step (unadjusted one-sided p >= 0.05 or mean <= 0); not CONTRADICTED"
            elif z["p1"] < 0.05 / 3:
                v = "SUPPORTED at every Holm step (p < 0.05/3), mean > 0"
            else:
                v = "depends on Holm: SUPPORTED only if C1's Holm-adjusted p < 0.05 (coordinator's step)"
            print(f"   verdict for C1 before Holm: {v}")
            print(f"   C4's post-hoc +{C4_PAIRED:.2f} inside C1's 95% CI: {'yes' if z['lo'] <= C4_PAIRED <= z['hi'] else 'no'}")
            d = zs[("resp", "conventional")]
            print(f"   H's second clause (designed RESPONSE < 0): mean {d['m']:+.4f} [{d['lo']:+.4f}, {d['hi']:+.4f}], pos {d['pos']}/{d['n']}")
            zn = zs[("net", "paired")]
            print(f"   paired RESPONSE net of null: {zn['m']:+.4f} [{zn['lo']:+.4f}, {zn['hi']:+.4f}], pos {zn['pos']}/{zn['n']}, one-sided p {zn['p1']:.4f}")
            print()
            obs = {s: R.rbody(R.Arm(f"runs/RBT-92/shift-{s}"), TS[s] + 60, TS[s] + 160)
                   - R.rbody(R.Arm(f"runs/RBT-90/forage-{s}"), TS[s] + 60, TS[s] + 160) for s in SEEDS}
            print("   cross-check: " + line("observed shift - base, recovery R-body (committed tables)", obs)[0])
            tot = [q[("total", "paired")][s] for s in SEEDS if q[("total", "paired")][s] is not None]
            ob = [obs[s] for s in SEEDS if q[("total", "paired")][s] is not None]
            print(f"   per-seed r(simulated paired TOTAL at T+110, observed) {st.correlation(tot, ob):+.2f}")
            print()


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--check":
        s = int(sys.argv[3])
        ok = check(f"{sys.argv[1]}/base-{s}", TS[s] - 1, f"baseline seed {s}")
        sys.exit(0 if ok else 1)
    elif len(sys.argv) > 2 and sys.argv[2] == "--check-shift":
        s = int(sys.argv[3])
        ok = check(f"{sys.argv[1]}/shift-{s}", TS[s] + 110, f"shift arm seed {s} (groups of 8)")
        sys.exit(0 if ok else 1)
    else:
        main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 4)
