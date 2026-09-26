"""RBT-110 C2 (dearer work, RBT-99): the refund/response split, pre-registered on RBT-110, on C2's arms.

Adapted from runs/RBT-101/readout-adversary/probe_refund.py. The only change of substance is the world difference:
C4's was flat against random terrain; C2's is the gain priced at work cost 0.08 (new world) against 0.03 (old world),
on the baseline's own random terrain (terrain seed = the draw, as the adversary did). Everything else is the
adversary's: the ecology's run_group with the run's config, four of a fauna to an arena, groups shuffled by the stream
"{seed} {population} {kind} {draw}", D draws from random.Random("RBT-101 refund {seed}"), each draw a start seed
shared by every population and both worlds. Populations are read from the restored bulk's genomes and lineage
(README rule 6):
    C0      alive in the baseline at T - 1 (the onset population)
    base    alive in the baseline at T + r
    shift   alive in the RBT-99 shift arm at T + r
    cull20  alive in the RBT-92 cull20 arm at T + r (RBT-110's null: turnover without a changed world)
at r = 110 (primary), 50 and 190 (secondary). Definitions (RBT-110):
    REFUND         gain(base, new) - gain(base, old)
    RESPONSE       gain(shift, new) - gain(base, new)
    RESPONSE_null  gain(cull20, new) - gain(base, new)
    paired         co-evolved (holistic) - designed (conventional), per seed
A fauna absent from a population at the read point (extinct) is excluded from every quantity that needs it, and n is
reported. The work cost enters only the pricing (simulation.py: food * value - work_cost * work / 1000), so the two
worlds share their trajectories; both are still simulated, as the adversary's two terrains were.

--check SEED reproduces one recorded pre-T season (T - 1) of the baseline bout for bout, as probe_refund.py --check
does; --check-shift SEED does the same for the shift arm's season T + 1 at work cost 0.08, to show the new world's
pricing is the arm's.

    python runs/RBT-110/C2/probe_split.py BULKDIR --check 3 > runs/RBT-110/C2/check.txt
    python runs/RBT-110/C2/probe_split.py BULKDIR [D] > runs/RBT-110/C2/split.txt
BULKDIR holds base-SEED (ckpt/rbt-90-SEED), shift-SEED (ckpt/rbt-99-shift-SEED), cull20-SEED (ckpt/rbt-92-cull20-SEED).
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
READS = (110, 50, 190)  # primary first
OLD, NEW = 0.03, 0.08
C4_PAIRED = 0.27


def cfg_of(run):
    return SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])


def world(cfg, wc, seed):
    return replace(cfg, world=replace(cfg.world, terrain_seed=int(seed)), food=replace(cfg.food, work_cost=wc))


def alive(run, kind, s):
    out = []
    for line in open(f"{run}/lineage.jsonl"):
        r = json.loads(line)
        if r["generation"] == s and r["population"] == kind and "food" in r:  # played season s
            out.append(r["name"])
    return out


def task(args):
    run, kind, names, cfg_d, wc, seed = args
    cfg = world(SimConfig.from_dict(cfg_d), wc, seed)
    gs = [Genotype.load(f"{run}/{kind}/genomes/{n}.json") for n in names]
    return [r["score"] for r in run_group(gs, cfg, seed)]


def check(bulk, seed, arm="base"):
    run = f"{bulk}/{arm}-{seed}"
    s = TS[seed] - 1 if arm == "base" else TS[seed] + 1
    wc = OLD if arm == "base" else NEW
    h = [e for e in json.load(open(f"{run}/history.json"))["history"] if e["season"] == s]
    rec = {}
    for line in open(f"{run}/lineage.jsonl"):
        r = json.loads(line)
        if r["generation"] == s and "food" in r:
            rec[(r["population"], r["name"])] = r["last_score"]
    cfg = cfg_of(run)
    assert cfg.food.work_cost == OLD, cfg.food.work_cost
    n = bad = 0
    for line in open(f"{run}/cohorts.jsonl"):
        c = json.loads(line)
        if c["season"] != s:
            continue
        kind = c["cohort"]
        ts = [e["terrain_seed"] for e in h if e["population"] == kind][0]
        sim = world(cfg, wc, ts)
        for grp in c["groups"][:4]:
            gs = [Genotype.load(f"{run}/{kind}/genomes/{m['name']}.json") for m in grp]
            got = [r["score"] for r in run_group(gs, sim, c["start_seed"])]
            for m, g in zip(grp, got):
                n += 1
                bad += round(g, 4) != round(rec[(kind, m["name"])], 4)
                print(f"   {kind:12s} {m['name']:8s} recorded {rec[(kind, m['name'])]:+.4f} re-simulated {g:+.4f}")
    print(f"CHECK {arm} seed {seed} season {s} (work cost {wc}): {n - bad}/{n} bouts reproduce the recorded gain to 4 decimals")


# Student t without scipy: the regularised incomplete beta by Lentz's continued fraction (Numerical Recipes 6.4)
def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)), -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1 + aa * d
            d = 1 / (d if abs(d) > 1e-300 else 1e-300)
            c = 1 + aa / c
            c = c if abs(c) > 1e-300 else 1e-300
            h *= d * c
        if abs(d * c - 1) < 1e-14:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0 or x >= 1:
        return max(0.0, min(1.0, x))
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lb) * _betacf(a, b, x) / a
    return 1 - math.exp(lb) * _betacf(b, a, 1 - x) / b


def t_sf(t, df):  # P(T > t)
    p = 0.5 * _ibeta(df / 2, 0.5, df / (df + t * t))
    return p if t > 0 else 1 - p


def t_ppf(q, df):  # inverse of the cdf by bisection
    lo, hi = -50.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1 - t_sf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def summary(v, direction=+1):
    """mean, t(n-1) 95% CI, count positive, one-sided p in the given direction, MDE (80% power)."""
    v = [x for x in v if x is not None]
    n = len(v)
    m = st.fmean(v)
    sd = st.stdev(v)
    se = sd / math.sqrt(n)
    hw = t_ppf(0.975, n - 1) * se
    t = m / se
    p1 = t_sf(direction * t, n - 1)
    mde1 = (t_ppf(0.95, n - 1) + t_ppf(0.80, n - 1)) * se
    mde2 = (t_ppf(0.975, n - 1) + t_ppf(0.80, n - 1)) * se
    return dict(n=n, m=m, sd=sd, lo=m - hw, hi=m + hw, pos=sum(x > 0 for x in v), t=t, p1=p1, mde1=mde1, mde2=mde2)


def line(label, v, direction=+1):
    s = summary(v, direction)
    arrow = ">" if direction > 0 else "<"
    return (f"{label:44s} {s['m']:+.4f} [{s['lo']:+.4f}, {s['hi']:+.4f}] sd {s['sd']:.4f} pos {s['pos']}/{s['n']}  "
            f"one-sided p(mean {arrow} 0) {s['p1']:.4f}  MDE80 {s['mde1']:.3f} one-sided / {s['mde2']:.3f} two-sided")


def fmt(v):
    return "[" + ", ".join("  n/a " if x is None else f"{x:+.3f}" for x in v) + "]"


def main(bulk, D):
    cfgd = json.load(open(f"{bulk}/base-{SEEDS[0]}/config.json"))["sim"]
    assert cfgd["food"]["work_cost"] == OLD
    jobs, keys, npop = [], [], {}
    for s in SEEDS:
        T = TS[s]
        rnd = random.Random(f"RBT-101 refund {s}")
        draws = [rnd.randrange(1, 2**31 - 1) for _ in range(D)]
        pops = {}
        for k in KINDS:
            pops[("C0", k, -1)] = (f"{bulk}/base-{s}", alive(f"{bulk}/base-{s}", k, T - 1))
            for r in READS:
                for p in ("base", "shift", "cull20"):
                    run = f"{bulk}/{p}-{s}"
                    with open(f"{run}/state.json") as f:
                        done = int(json.load(f)["season"])
                    assert T + r < done, f"{run} covers {done} seasons, not T + {r} = {T + r}"  # never substituted
                    pops[(p, k, r)] = (run, alive(run, k, T + r))
        for (p, k, r), (run, names) in pops.items():
            npop[(s, p, k, r)] = len(names)
            for d, seed in enumerate(draws):
                order = names[:]
                random.Random(f"{s} {p} {k} {d}").shuffle(order)
                for gi in range(0, len(order), 4):
                    grp = order[gi:gi + 4]
                    for w, wc in (("old", OLD), ("new", NEW)):
                        jobs.append((run, k, grp, cfgd, wc, seed))
                        keys.append((s, p, k, r, w))
    with ProcessPoolExecutor(int(os.environ.get("WORKERS", "4"))) as ex:
        res = list(ex.map(task, jobs, chunksize=2))
    acc = {}
    for key, out in zip(keys, res):
        acc.setdefault(key, []).extend(out)
    G = {key: st.fmean(v) for key, v in acc.items()}

    def g(s, p, k, r, w):
        return G.get((s, p, k, r, w))  # None when the fauna is absent (extinct) at the read point

    def diff(a, b):
        return None if a is None or b is None else a - b

    print(__doc__.split("\n\n")[0])
    print(f"D = {D} draws per population and world; group bouts simulated: {len(jobs)}; seeds {' '.join(map(str, SEEDS))}")
    print("gain = mean score per robot-bout (items x value - work cost x kJ), simulated")
    print()
    print("population sizes (alive at the read point; 0 = extinct, excluded from every quantity that needs it)")
    for s in SEEDS:
        cells = []
        for r in (-1,) + READS:
            for p in (("C0",) if r == -1 else ("base", "shift", "cull20")):
                cells.append(f"{p}{'' if r == -1 else f'@{r}'} " + "/".join(str(npop[(s, p, k, r)]) for k in KINDS))
        print(f"   {s:4d} T={TS[s]}  (co-evolved/designed)  " + "  ".join(cells))
    print()
    out = {}
    for r in READS:
        for k in KINDS:
            out[("refund", k, r)] = [diff(g(s, "base", k, r, "new"), g(s, "base", k, r, "old")) for s in SEEDS]
            out[("resp", k, r)] = [diff(g(s, "shift", k, r, "new"), g(s, "base", k, r, "new")) for s in SEEDS]
            out[("null", k, r)] = [diff(g(s, "cull20", k, r, "new"), g(s, "base", k, r, "new")) for s in SEEDS]
            out[("respold", k, r)] = [diff(g(s, "shift", k, r, "old"), g(s, "base", k, r, "old")) for s in SEEDS]
            out[("total", k, r)] = [diff(g(s, "shift", k, r, "new"), g(s, "base", k, r, "old")) for s in SEEDS]
            out[("net", k, r)] = [diff(a, b) for a, b in zip(out[("resp", k, r)], out[("null", k, r)])]
        for q in ("refund", "resp", "null", "respold", "total", "net"):
            out[(q, "paired", r)] = [diff(a, b) for a, b in zip(out[(q, "holistic", r)], out[(q, "conventional", r)])]
    for k in KINDS:
        out[("c0", k)] = [g(s, "C0", k, -1, "new") - g(s, "C0", k, -1, "old") for s in SEEDS]

    NAMES = {"refund": "REFUND: base, new - old", "resp": "RESPONSE: shift - base, new world",
             "null": "RESPONSE_null: cull20 - base, new world", "net": "RESPONSE net of null (RESPONSE - null)",
             "respold": "  RESPONSE on the old world (shift - base)", "total": "TOTAL = REFUND + RESPONSE"}
    for r in READS:
        print(f"=== T + {r}{' (PRIMARY)' if r == 110 else ' (secondary)'} ===")
        for k in KINDS + ("paired",):
            print(f"{'paired (co-evolved - designed)' if k == 'paired' else LAB[k]}")
            if k != "paired" and r == 110:
                print("   " + line("C0 REFUND (onset pop, new - old)", out[("c0", k)]))
            for q in ("refund", "resp", "null", "net", "respold", "total"):
                v = out[(q, k, r)]
                direction = -1 if (q in ("resp", "net") and k == "conventional") else +1
                print("   " + line(NAMES[q], v, direction))
                print(f"      per seed {fmt(v)}")
            ex = [str(s) for s, x in zip(SEEDS, out[("resp", k, r)]) if x is None]
            if ex:
                print(f"   excluded from RESPONSE: seeds {', '.join(ex)} (designed fauna extinct in the shift arm at T + {r})")
        print()

    print("=== confirmatory (RBT-110 primary): paired RESPONSE at T + 110, H: mean > 0 ===")
    s = summary(out[("resp", "paired", 110)], +1)
    print(f"   n = {s['n']}  mean {s['m']:+.4f}  95% t({s['n'] - 1}) CI [{s['lo']:+.4f}, {s['hi']:+.4f}]  positive {s['pos']}/{s['n']}  "
          f"t = {s['t']:+.3f}  one-sided p = {s['p1']:.4f}   (Holm across C1-C3 is the coordinator's)")
    print(f"   MDE at 80% power from the observed sd: {s['mde1']:.3f} (one-sided 5%), {s['mde2']:.3f} (two-sided 5%)")
    sn = summary(out[("net", "paired", 110)], +1)
    print(f"   net of the cull20 null: n = {sn['n']}  mean {sn['m']:+.4f} [{sn['lo']:+.4f}, {sn['hi']:+.4f}]  positive {sn['pos']}/{sn['n']}  one-sided p = {sn['p1']:.4f}")
    sd = summary(out[("resp", "conventional", 110)], -1)
    print(f"   designed RESPONSE (H: < 0): n = {sd['n']}  mean {sd['m']:+.4f} [{sd['lo']:+.4f}, {sd['hi']:+.4f}]  one-sided p(< 0) = {sd['p1']:.4f}")
    if s["hi"] < 0:
        v = "CONTRADICTED (the two-sided 95% CI lies entirely below 0)"
    elif s["p1"] >= 0.05 or s["m"] <= 0:
        v = f"NOT DECIDED (unadjusted one-sided p = {s['p1']:.4f} >= 0.05, so no Holm step can reach SUPPORTED; MDE {s['mde1']:.3f})"
    else:
        v = (f"SUPPORTED if the Holm-adjusted p < 0.05 (unadjusted one-sided p = {s['p1']:.4f}; it holds at any Holm step "
             f"if p < 0.0167, else depends on C1 and C3); otherwise NOT DECIDED, MDE {s['mde1']:.3f}")
    print(f"   verdict for C2: {v}")
    inside = s["lo"] <= C4_PAIRED <= s["hi"]
    print(f"   C4's post-hoc +{C4_PAIRED:.2f} is {'inside' if inside else 'outside'} C2's 95% CI (for the coordinator's pooled comparison)")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] in ("--check", "--check-shift"):
        check(sys.argv[1], int(sys.argv[3]), "base" if sys.argv[2] == "--check" else "shift")
    else:
        main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 4)
