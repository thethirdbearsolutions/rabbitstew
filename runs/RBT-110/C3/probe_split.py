"""RBT-110 C3 (scarce food, RBT-100): the refund/response split, out of sample, from restored bulk.

runs/RBT-101/readout-adversary/probe_refund.py adapted only in the world change (RBT-110 pre-registration):
the new world is 6 food items, the old world 12 (RBT-100's shift, food-items=6).  Everything else is the
adversary's: the ecology's own harness (rabbitstew.simulation.run_group, groups of four as run, the run's
config), random terrain with terrain seed = the draw, D = 4 draws per seed from the same stream
("RBT-101 refund SEED"), each draw a start seed shared by every population and both worlds, and each
population shuffled into groups of four by the stream "SEED POP KIND DRAW".
    REFUND         gain(base pop, 6 items)   - gain(base pop, 12 items)
    RESPONSE       gain(shift pop, 6 items)  - gain(base pop, 6 items)
    RESPONSE_null  gain(cull20 pop, 6 items) - gain(base pop, 6 items)     (RBT-92's cull20 arm)
Populations, read from each restored run's genomes and lineage (README rule 6: no table is read from a ckpt):
    C0      alive in the baseline at T - 1 (the onset population, the same in every arm)
    base    alive in the RBT-90 part 2 baseline at T + r
    shift   alive in the RBT-100 shift arm at T + r
    cull20  alive in the RBT-92 cull20 arm at T + r
r = 110 primary; 50 and 190 secondary.  A fauna with no one alive at T + r in a population is absent there:
that seed is excluded from every quantity involving it, and named.  A read point past a run's coverage is
"not covered" for that seed; nothing is substituted.

--check SEED reproduces one recorded pre-T season of the baseline (season T - 1) bout by bout, as the
adversary's --check does.  --check-new SEED does the same for the shift arm's season T + 110 under this
script's own 6-item world, so the new world is the ecology's too.

    python runs/RBT-110/C3/probe_split.py BULKDIR --check 3 > runs/RBT-110/C3/check.txt
    python runs/RBT-110/C3/probe_split.py BULKDIR [D] > runs/RBT-110/C3/split.txt
BULKDIR holds base-SEED (ckpt/rbt-90-SEED), shift-SEED (ckpt/rbt-100-shift-SEED), cull20-SEED
(ckpt/rbt-92-cull20-SEED), each restored with scripts/durable.sh restore.
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
NEW, OLD = 6, 12  # food items: the challenge's world and the run's own
RS = (110, 50, 190)  # r = 110 primary (pre-registered); 50 and 190 secondary
ARMS = {"base": "base", "shift": "shift", "cull20": "cull20"}


def cfg_of(run):
    return SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])


def world(cfg, items, terrain_seed):
    """The run's world on random terrain (terrain seed given) with `items` food items: the one change."""
    w = replace(cfg.world, terrain="random", terrain_seed=int(terrain_seed))
    return replace(cfg, world=w, food=replace(cfg.food, items=int(items)))


def covered(run):
    return int(json.load(open(f"{run}/state.json"))["season"])  # seasons completed: 0 .. covered - 1


def alive(run, kind, s):
    out = []
    for line in open(f"{run}/lineage.jsonl"):
        r = json.loads(line)
        if r["generation"] == s and r["population"] == kind and "food" in r:  # played season s
            out.append(r["name"])
    return out


def task(args):
    run, kind, names, cfg_d, items, seed = args
    cfg = world(SimConfig.from_dict(cfg_d), items, seed)
    gs = [Genotype.load(f"{run}/{kind}/genomes/{n}.json") for n in names]
    return [r["score"] for r in run_group(gs, cfg, seed)]


def check(bulk, seed, arm="base", s=None, items=OLD):
    run = f"{bulk}/{arm}-{seed}"
    s = TS[seed] - 1 if s is None else s
    h = [e for e in json.load(open(f"{run}/history.json"))["history"] if e["season"] == s]
    rec = {}
    for line in open(f"{run}/lineage.jsonl"):
        r = json.loads(line)
        if r["generation"] == s and "food" in r:
            rec[(r["population"], r["name"])] = r["last_score"]
    cfg = cfg_of(run)
    n = bad = 0
    for line in open(f"{run}/cohorts.jsonl"):
        c = json.loads(line)
        if c["season"] != s:
            continue
        kind = c["cohort"]
        ts = [e["terrain_seed"] for e in h if e["population"] == kind][0]
        sim = world(cfg, items, ts)
        for grp in c["groups"][:4]:
            gs = [Genotype.load(f"{run}/{kind}/genomes/{m['name']}.json") for m in grp]
            got = [r["score"] for r in run_group(gs, sim, c["start_seed"])]
            for m, g in zip(grp, got):
                n += 1
                bad += round(g, 4) != round(rec[(kind, m["name"])], 4)
                print(f"   {kind:12s} {m['name']:8s} recorded {rec[(kind, m['name'])]:+.4f} re-simulated {g:+.4f}")
    print(f"CHECK {arm} seed {seed} season {s} ({items} food items): {n - bad}/{n} bouts reproduce the recorded gain to 4 decimals")
    return bad == 0 and n > 0


# -- Student t, without scipy ------------------------------------------------------------------------------ #
def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(1.0 + aa / c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(1.0 + aa / c) > 1e-300 else 1e-300
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-14:
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
    return 1.0 - math.exp(lb) * _betacf(b, a, 1 - x) / b


def t_sf(t, df):
    """P(T_df > t)."""
    p = 0.5 * _ibeta(df / 2.0, 0.5, df / (df + t * t))
    return p if t >= 0 else 1.0 - p


def t_ppf(q, df):
    lo, hi = -100.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1.0 - t_sf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def one_sided_p(v):
    n, m, sd, _ = R.stat(v)
    return t_sf(m / (sd / math.sqrt(n)), n - 1) if n > 1 and sd > 0 else float("nan")


def mde(v, alpha):
    """Smallest true mean a one-sided one-sample t test at `alpha` detects with 80% power, at the observed sd."""
    n, _, sd, _ = R.stat(v)
    return (t_ppf(1 - alpha, n - 1) + t_ppf(0.80, n - 1)) * sd / math.sqrt(n) if n > 1 else float("nan")


def main(bulk, D):
    cfgd = json.load(open(f"{bulk}/base-{SEEDS[0]}/config.json"))["sim"]
    for s in SEEDS:  # every run shares the sim config; the shift is applied by the ecology, not the config
        for a in ARMS.values():
            assert json.load(open(f"{bulk}/{a}-{s}/config.json"))["sim"] == cfgd, (a, s)
    print(__doc__.split("\n\n")[0])
    print(f"D = {D} draws per population and world; groups of four; new world {NEW} items, old world {OLD}; random terrain")
    print(f"read points T + r, r in {RS} (r = 110 primary)")
    print()
    cov = {(a, s): covered(f"{bulk}/{a}-{s}") for a in ARMS.values() for s in SEEDS}
    print("coverage (seasons completed per restored run; T from runs/RBT-92/onset.txt)")
    for s in SEEDS:
        print(f"   seed {s:4d} T {TS[s]:4d}   " + "  ".join(f"{a} {cov[(a, s)]}" for a in ARMS.values()))
    print()
    jobs, keys, pops = [], [], {}
    for s in SEEDS:
        T = TS[s]
        rnd = random.Random(f"RBT-101 refund {s}")
        draws = [rnd.randrange(1, 2**31 - 1) for _ in range(D)]
        want = [("C0", None, "base", T - 1)] + [(p, r, a, T + r) for r in RS for p, a in ARMS.items()]
        for p, r, a, season in want:
            run = f"{bulk}/{a}-{s}"
            for k in KINDS:
                if season >= cov[(a, s)]:
                    pops[(s, p, r, k)] = None  # not covered
                    continue
                names = alive(run, k, season)
                pops[(s, p, r, k)] = len(names)
                for d, seed in enumerate(draws):
                    order = names[:]
                    random.Random(f"{s} {p} {k} {d}").shuffle(order)
                    for gi in range(0, len(order), 4):
                        grp = order[gi:gi + 4]
                        for items in (OLD, NEW):
                            jobs.append((run, k, grp, cfgd, items, seed))
                            keys.append((s, p, r, k, items))
    print(f"{len(jobs)} group bouts", file=sys.stderr, flush=True)
    with ProcessPoolExecutor(int(os.environ.get("WORKERS", "4"))) as ex:
        res = list(ex.map(task, jobs, chunksize=2))
    acc = {}
    for key, out in zip(keys, res):
        acc.setdefault(key, []).extend(out)
    G = {key: st.fmean(v) for key, v in acc.items()}

    print("population sizes (alive at the read season; '-' = not covered)")
    for s in SEEDS:
        row = []
        for p, r in [("C0", None)] + [(p, r) for r in RS for p in ARMS]:
            lab = "C0" if r is None else f"{p}@{r}"
            row.append(f"{lab} " + "/".join("-" if pops[(s, p, r, k)] is None else str(pops[(s, p, r, k)]) for k in KINDS))
        print(f"   seed {s:4d} (co-evolved/designed)  " + "  ".join(row))
    print()

    def g(s, p, r, k, items):
        n = pops[(s, p, r, k)]
        return G[(s, p, r, k, items)] if n else None  # None: absent (extinct) or not covered

    def diff(a, b):
        return None if a is None or b is None else a - b

    def stat(label, per):  # per: {seed: value or None}
        v = [per[s] for s in SEEDS if per[s] is not None]
        out = [s for s in SEEDS if per[s] is None]
        if len(v) < 2:
            return f"{label:50s} n {len(v)}  (too few)" + (f"  excluded {out}" if out else "")
        n, m, sd, hw = R.stat(v)
        txt = (f"{label:50s} {m:+.4f} [{m - hw:+.4f}, {m + hw:+.4f}] pos {sum(x > 0 for x in v)}/{n} sd {sd:.3f}"
               f"  per seed [{', '.join('  n/a ' if per[s] is None else f'{per[s]:+.3f}' for s in SEEDS)}]")
        return txt + (f"  excluded {out}" if out else "")

    def why(s, p, r, k):
        n = pops[(s, p, r, k)]
        return None if n else ("not covered" if n is None else f"{LAB[k]} extinct in {p} at T+{r}")

    print(f"seeds in order: {SEEDS}")
    print()
    res = {}
    for r in RS:
        print(f"=== r = {r}{' (PRIMARY)' if r == 110 else ' (secondary)'}: read season T + {r} ===")
        q = {}
        for k in KINDS:
            q[("refund", k)] = {s: diff(g(s, "base", r, k, NEW), g(s, "base", r, k, OLD)) for s in SEEDS}
            q[("resp", k)] = {s: diff(g(s, "shift", r, k, NEW), g(s, "base", r, k, NEW)) for s in SEEDS}
            q[("null", k)] = {s: diff(g(s, "cull20", r, k, NEW), g(s, "base", r, k, NEW)) for s in SEEDS}
            q[("net", k)] = {s: diff(q[("resp", k)][s], q[("null", k)][s]) for s in SEEDS}
            q[("resp_old", k)] = {s: diff(g(s, "shift", r, k, OLD), g(s, "base", r, k, OLD)) for s in SEEDS}
            q[("total", k)] = {s: diff(g(s, "shift", r, k, NEW), g(s, "base", r, k, OLD)) for s in SEEDS}
            q[("c0", k)] = {s: diff(g(s, "C0", None, k, NEW), g(s, "C0", None, k, OLD)) for s in SEEDS}
            print(f"{LAB[k]} (mean gain per robot-bout, simulated)")
            print("   " + stat(f"C0 refund, {NEW} - {OLD} items (onset population)", q[("c0", k)]))
            print("   " + stat(f"REFUND: base pop, {NEW} - {OLD} items", q[("refund", k)]))
            print("   " + stat(f"RESPONSE: shift pop - base pop, both {NEW} items", q[("resp", k)]))
            print("   " + stat(f"RESPONSE_null: cull20 pop - base pop, {NEW} items", q[("null", k)]))
            print("   " + stat("RESPONSE net of null", q[("net", k)]))
            print("   " + stat(f"  RESPONSE on the old world ({OLD} items)", q[("resp_old", k)]))
            print("   " + stat("TOTAL = REFUND + RESPONSE", q[("total", k)]))
            for s in SEEDS:
                for p in ("shift", "cull20", "base"):
                    w = why(s, p, r, k)
                    if w:
                        print(f"   excluded seed {s}: {w}")
            print()
        print("paired (co-evolved - designed)")
        for lab, key in (("REFUND", "refund"), ("RESPONSE", "resp"), ("RESPONSE_null", "null"), ("RESPONSE net of null", "net"),
                         (f"RESPONSE on the old world ({OLD} items)", "resp_old"), ("TOTAL", "total")):
            q[("pair", key)] = {s: diff(q[(key, "holistic")][s], q[(key, "conventional")][s]) for s in SEEDS}
            print("   " + stat(lab, q[("pair", key)]))
        print()
        res[r] = q

    q = res[110]
    print("=== PRIMARY (pre-registered): paired RESPONSE at r = 110 ===")
    for lab, key in (("paired RESPONSE", "resp"), ("paired RESPONSE net of null", "net")):
        per = q[("pair", key)]
        v = [per[s] for s in SEEDS if per[s] is not None]
        n, m, sd, hw = R.stat(v)
        p1 = one_sided_p(v)
        print(f"{lab}: n {n}  mean {m:+.4f}  95% CI [{m - hw:+.4f}, {m + hw:+.4f}]  pos {sum(x > 0 for x in v)}/{n}"
              f"  sd {sd:.4f}  one-sided p (H: > 0) {p1:.4f}")
        print(f"   excluded: {[s for s in SEEDS if per[s] is None] or 'none'}")
        print(f"   MDE at 80% power, one-sided: alpha 0.05 {mde(v, 0.05):.3f}; alpha 0.05/3 (Holm's strictest step) {mde(v, 0.05 / 3):.3f}")
    for k in KINDS:
        for key in ("resp", "net"):
            per = q[(key, k)]
            v = [per[s] for s in SEEDS if per[s] is not None]
            n, m, sd, hw = R.stat(v)
            h = "< 0" if k == "conventional" else "> 0"
            p1 = one_sided_p([-x for x in v]) if k == "conventional" else one_sided_p(v)
            print(f"secondary {LAB[k]} {'RESPONSE' if key == 'resp' else 'RESPONSE net of null'}: n {n} mean {m:+.4f} [{m - hw:+.4f}, {m + hw:+.4f}]"
                  f"  one-sided p (H: {h}) {p1:.4f}  MDE(0.05) {mde(v, 0.05):.3f}")
    per = q[("pair", "resp")]
    v = [per[s] for s in SEEDS if per[s] is not None]
    n, m, sd, hw = R.stat(v)
    p1 = one_sided_p(v)
    print()
    print("VERDICT (C3, per the pre-registration; Holm across C1-C3 is the coordinator's):")
    if m + hw < 0:
        print(f"   CONTRADICTED: the two-sided 95% CI [{m - hw:+.4f}, {m + hw:+.4f}] lies entirely below 0")
    elif m > 0 and p1 < 0.05 / 3:
        print(f"   SUPPORTED at any Holm step (one-sided p {p1:.4f} < 0.0167, mean > 0)")
    elif m > 0 and p1 < 0.05:
        print(f"   SUPPORTED only if Holm's step for C3 is at alpha 0.05/2 or 0.05 (one-sided p {p1:.4f}); otherwise NOT DECIDED, MDE {mde(v, 0.05 / 3):.3f}")
    else:
        print(f"   NOT DECIDED (one-sided p {p1:.4f}; not SUPPORTED at any Holm step, CI not below 0); MDE at 80% power {mde(v, 0.05):.3f} (alpha 0.05), {mde(v, 0.05 / 3):.3f} (alpha 0.05/3)")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--check":
        ok = check(sys.argv[1], int(sys.argv[3]))
        sys.exit(0 if ok else 1)
    elif len(sys.argv) > 2 and sys.argv[2] == "--check-new":
        sd = int(sys.argv[3])
        ok = check(sys.argv[1], sd, arm="shift", s=TS[sd] + 110, items=NEW)
        sys.exit(0 if ok else 1)
    else:
        main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 4)
