"""RBT-102 adversary, probe 3: the drift expectation on RBT-102's OWN denominator (pedigree replay).

RBT-102 compares 0 carriers in 12,276 part-2 genomes against RBT-91's drift rate, 84 of 200,000
(0.042%). That rate was measured from different parents (W4b-801 bests, P-801 final 60) at one
depth (k = 19), on independent lineages. Part 2 starts from random founders, its genomes sit at
depths 0..~30, and they share ancestry. So "is zero below drift?" has no matched answer from that
figure alone.

This builds the matched null. For each part-2 arm it takes the arm's OWN founders (the genomes the
arm saved at birth for founders) and replays the arm's OWN pedigree: every birth, in the order the
arm made them, with the same first parent and the same crossover partner, through the same breeding
step as `ecology._breed` for the conventional fauna (`crossover_controller` when there is a second
parent, then one `mutate_controller`, with the arm's own MutationConfig). The replayed genomes are
never scored, so nothing selects on them: the tree was shaped by selection on the REAL genomes, but
it is blind to the replayed ones. What the replay preserves exactly is RBT-102's counting unit: the
same number of genomes, the same depth of every genome, and the same shared ancestry (a carrier
arising in the replay is inherited by its replayed descendants just as a real one would be).

Each replayed genome goes through RBT-91's predicate (imported unmodified, as RBT-102 does), and
the replay also records the post hoc half-structures of `supp_partial.py`, so the supplement's
"7.8% wire one nose, none wires both" can be compared with what drift alone gives on the same tree.

Readouts per arm and replay: carriers among all genomes (founders + births), de novo arrivals,
window carriage X (seasons 300-599, living conventional individuals, as analyse.py), and the
half-structure counts. Pooled: the drift expectation of RBT-102's headline count, and the fraction
of ten-arm replay sets in which every arm reads zero, which is P(RBT-102's result | drift).

    python runs/RBT-102/adversary/replay_null.py --reps 20 --procs 4 runs/RBT-90/forage-{1,2,...}
"""
import argparse
import glob
import importlib.util
import json
import os
import sys
import time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
_argv, sys.argv = sys.argv, ["structural_rate.py"]
_s = importlib.util.spec_from_file_location("sr", os.path.join(ROOT, "runs", "RBT-91", "structural_rate.py"))
sr = importlib.util.module_from_spec(_s)
_s.loader.exec_module(sr)
sys.argv = _argv

from rabbitstew.evolution import EvolutionConfig
from rabbitstew.genetics import crossover_controller, mutate_controller
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize

WINDOW = (300, 599)
MASTER = 102_0926


def halves(ph):
    """(carrier, >=1 nose into a global unit, both noses into one global unit any sign, out-half)."""
    noses = sr._wheel_noses(ph)
    le, re_ = sr.drive_effector_units(ph)
    if noses is None or not le or not re_:
        return (False, False, False, False)
    n_L, n_R = noses
    e_L, e_R = le[0], re_[0]
    w = {}
    for s, d, x in ph.links:
        w[(s, d)] = w.get((s, d), 0.0) + x
    one = both = out = False
    for k, ui in enumerate(ph.units):
        if ui.part is not None or ui.unit.kind == "sensor":
            continue
        a, b = w.get((n_L, k), 0.0), w.get((n_R, k), 0.0)
        c, d = w.get((k, e_L), 0.0), w.get((k, e_R), 0.0)
        one |= a != 0.0 or b != 0.0
        both |= a != 0.0 and b != 0.0
        out |= c != 0.0 and d != 0.0 and np.sign(c) == np.sign(d)
    return (bool(sr.motif_units(ph)), bool(one), bool(both), bool(out))


def load_arm(arm):
    cfg = json.load(open(os.path.join(arm, "config.json")))
    genomes = {}
    for p in sorted(glob.glob(os.path.join(arm, "conventional", "genomes", "*.json"))):
        g = Genotype.load(p)
        genomes[g.name] = g
    alive = {}
    for line in open(os.path.join(arm, "lineage.jsonl")):
        r = json.loads(line)
        if r["population"] != "conventional" or "death" in r:
            continue
        alive.setdefault(r["generation"], []).append(r["name"])
    return cfg, genomes, alive


def order(genomes):
    """Every genome after all of its parents (topological; the arm made them in such an order)."""
    seen, out = set(), []

    def visit(n):
        stack = [n]
        while stack:
            m = stack[-1]
            if m in seen:
                stack.pop()
                continue
            pend = [p for p in genomes[m].parents if p not in seen]
            if pend:
                stack.extend(pend)
                continue
            seen.add(m)
            out.append(m)
            stack.pop()
    for n in sorted(genomes):
        visit(n)
    return out


def replay(task):
    arm, rep = task
    cfg, genomes, alive = load_arm(arm)
    evo = EvolutionConfig.from_dict({k: v for k, v in cfg.items() if k != "ecology"})
    sim = SimConfig.from_dict(cfg["sim"])
    rng = np.random.default_rng(np.random.SeedSequence([MASTER, int(cfg["seed"]), rep]))
    new, flags = {}, {}
    for n in order(genomes):
        g = genomes[n]
        if not g.parents:
            child = g.copy()
        else:
            p = new[g.parents[0]]
            o = new[g.parents[1]] if len(g.parents) > 1 else None
            child = crossover_controller(p, o, rng) if o is not None else p.copy()
            child = mutate_controller(child, rng, evo.mutation)
        new[n] = child
        flags[n] = halves(synthesize(child, sim.synthesis))
    carriers = [n for n in new if flags[n][0]]
    de_novo = [n for n in carriers if genomes[n].parents and not any(flags[p][0] for p in genomes[n].parents)]
    wins = [s for s in alive if WINDOW[0] <= s <= WINDOW[1]]
    C = [sum(flags[n][0] for n in alive[s] if n in flags) / max(1, sum(n in flags for n in alive[s])) for s in wins]
    return dict(arm=arm, seed=int(cfg["seed"]), rep=rep, genomes=len(new), carriers=len(carriers),
                de_novo=len(de_novo), X=float(np.mean(C)),
                one_nose=sum(f[1] for f in flags.values()), both_noses=sum(f[2] for f in flags.values()),
                out_half=sum(f[3] for f in flags.values()),
                real_one_nose=None)


def real_halves(arm):
    cfg, genomes, _ = load_arm(arm)
    sim = SimConfig.from_dict(cfg["sim"])
    f = [halves(synthesize(g, sim.synthesis)) for g in genomes.values()]
    return arm, int(cfg["seed"]), len(f), [sum(x[i] for x in f) for i in range(4)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arms", nargs="+")
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    t0 = time.time()
    tasks = [(arm.rstrip("/"), r) for r in range(a.reps) for arm in a.arms]
    with get_context("fork").Pool(a.procs) as pool:
        rows = pool.map(replay, tasks, chunksize=1)
        real = pool.map(real_halves, [x.rstrip("/") for x in a.arms])
    print("# RBT-102 adversary probe 3: pedigree-replay drift null on RBT-102's own denominator\n")
    print(f"arms {len(a.arms)}; replays per arm {a.reps}; seeds SeedSequence([{MASTER}, arm seed, rep])")
    print("each replay: the arm's own founders, its own pedigree and crossover partners, one mutate_controller")
    print("per birth with the arm's MutationConfig; replayed genomes are never scored (no selection on them)\n")
    print("## Per arm (mean over replays; the real arm's values from the saved genomes beside them)\n")
    print("| seed | genomes | replay carriers mean | replays with >=1 carrier | replay de novo mean | replay X mean "
          "| >=1 nose into global: real / replay mean | both noses into one global: real / replay mean "
          "| out-half: real / replay mean |")
    print("|---|---|---|---|---|---|---|---|---|")
    by = {}
    for r in rows:
        by.setdefault(r["seed"], []).append(r)
    realby = {s: (n, v) for _, s, n, v in real}
    for s in sorted(by):
        rr = by[s]
        n, v = realby[s]
        print(f"| {s} | {rr[0]['genomes']} | {np.mean([r['carriers'] for r in rr]):.2f} | "
              f"{sum(r['carriers'] > 0 for r in rr)}/{len(rr)} | {np.mean([r['de_novo'] for r in rr]):.2f} | "
              f"{100 * np.mean([r['X'] for r in rr]):.4f}% | {v[1]} / {np.mean([r['one_nose'] for r in rr]):.1f} | "
              f"{v[2]} / {np.mean([r['both_noses'] for r in rr]):.1f} | {v[3]} / {np.mean([r['out_half'] for r in rr]):.1f} |")
    # pooled over arms, per replay index: one "ten-arm replay set" per rep
    sets = {}
    for r in rows:
        sets.setdefault(r["rep"], []).append(r)
    tot = [sum(x["carriers"] for x in v) for v in sets.values()]
    dn = [sum(x["de_novo"] for x in v) for v in sets.values()]
    G = sum(x["genomes"] for x in sets[0])
    zero_sets = sum(t == 0 for t in tot)
    lo, hi = sr.wilson(zero_sets, len(tot))
    # the pre-registered verdict rule applied to each drift replay set
    verdicts = []
    for v in sets.values():
        X = np.array([x["X"] for x in v])
        m, sd = X.mean(), X.std(ddof=1)
        L, U = m - 2.262 * sd / np.sqrt(len(X)), m + 2.262 * sd / np.sqrt(len(X))
        verdicts.append("HELD" if L > 0.000520 else "NOT HELD" if U <= 0.000520 else "UNRESOLVED")
    print(f"\n## Pooled over the {len(a.arms)} arms, one set per replay index ({len(tot)} sets)\n")
    print(f"  genomes per set: {G}")
    print(f"  carriers per set under drift: mean {np.mean(tot):.2f}, median {np.median(tot):.0f}, "
          f"range {min(tot)}-{max(tot)}; per-set values {sorted(tot)}")
    print(f"  de novo arrivals per set under drift: mean {np.mean(dn):.2f}, range {min(dn)}-{max(dn)}")
    print(f"  carrier fraction under drift: {100 * np.mean(tot) / G:.4f}% of genomes")
    print(f"  sets with ZERO carriers (RBT-102's observed outcome): {zero_sets} of {len(tot)} = "
          f"{100 * zero_sets / len(tot):.0f}% [{100 * lo:.0f}, {100 * hi:.0f}] (Wilson 95%)  <- P(0 | drift)")
    print(f"  pre-registered verdict rule applied to each drift set: "
          + ", ".join(f"{k} {verdicts.count(k)}" for k in ("NOT HELD", "UNRESOLVED", "HELD")))
    rt = [sum(v[i] for _, _, _, v in real) for i in range(4)]
    print(f"\n  real arms, all genomes: carriers {rt[0]}, >=1 nose {rt[1]}, both noses {rt[2]}, out-half {rt[3]}")
    one = [sum(x["one_nose"] for x in v) for v in sets.values()]
    both = [sum(x["both_noses"] for x in v) for v in sets.values()]
    out = [sum(x["out_half"] for x in v) for v in sets.values()]
    print(f"  drift sets, all genomes: >=1 nose mean {np.mean(one):.0f} (range {min(one)}-{max(one)}), "
          f"both noses mean {np.mean(both):.1f} (range {min(both)}-{max(both)}), out-half mean {np.mean(out):.0f}")
    print(f"\nwall time {time.time() - t0:.0f} s")
    print("ROWS " + json.dumps(rows))


if __name__ == "__main__":
    main()
