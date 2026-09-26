"""RBT-101 adversary probe A: does the scored statistic `new` track turnover (reproduction depth) with no
terrain change at all?

    PYTHONPATH=. python runs/RBT-101/adversary/turnover_probe.py digest RUN_DIR      -> RUN_DIR/adv_wiring.txt
    PYTHONPATH=. python runs/RBT-101/adversary/turnover_probe.py windows RUN_DIR... > runs/RBT-101/adversary/turnover_probe.txt

Reads baseline arms (RBT-90 part 2, restored from ckpt/rbt-90-SEED; bulk, genomes and lineage only, no income
column).  Per individual: g1 over POSTURE sensors (wiring.py's digest, unchanged) and g1_other, the same depth-1
sum over every NON-posture sensor (the placebo: flat terrain gives no reason to wire smell or compass).
For pseudo-onsets T = 100, 120, ..., (last - 160) and each fauna: C0 alive at T - 1, P alive at T + 160,
  new       rewire.py's statistic (g1 >= max C0-ancestor g1 + 0.5), posture sensors
  new_oth   the same statistic on g1_other (placebo)
  depth     mean over P of the number of births from its nearest C0 ancestor (shortest parent path)
  births    individuals born in [T, T + 160)
Then, pooled within seed (seed means removed), the slope and correlation of new on depth and on new_oth.
If new rises with depth, a challenge that changes the birth rate moves new with no re-wiring in it.
"""
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import wiring  # noqa: E402

KINDS = ("holistic", "conventional")
NEW = 0.5


def g1_other(ph):
    from rabbitstew.analysis import signed_influence
    src = {i: ui.unit.source for i, ui in enumerate(ph.units) if ui.unit.kind == "sensor"}
    return sum(abs(r["gain"]) for r in signed_influence(ph, depth=1) if src[r["sensor"]] not in wiring.POSTURE)


def digest(run):
    from rabbitstew.genotype import Genotype
    from rabbitstew.synthesis import synthesize
    syn = wiring.sim_config(run).synthesis
    with open(os.path.join(run, "adv_wiring.txt"), "w") as f:
        f.write("population\tname\tg1\tg1_other\n")
        for kind in KINDS:
            gd = os.path.join(run, kind, "genomes")
            for fn in sorted(os.listdir(gd)):
                ph = synthesize(Genotype.load(os.path.join(gd, fn)), syn)
                f.write(f"{kind}\t{fn[:-5]}\t{wiring.digest(ph)['g1']:.6f}\t{g1_other(ph):.6f}\n")


def lineage(run):
    life, parents = {}, {}
    for line in open(os.path.join(run, "lineage.jsonl")):
        r = json.loads(line)
        k = (r["population"], r["name"])
        life[k] = (r["generation"] - r["age"], r["generation"])
        parents[k] = list(r["parents"])
    return life, parents


def windows(run):
    life, parents = lineage(run)
    W = {}
    for line in list(open(os.path.join(run, "adv_wiring.txt")))[1:]:
        p, n, a, b = line.split()
        W[(p, n)] = (float(a), float(b))
    last = max(l for _, l in life.values())
    seed = json.load(open(os.path.join(run, "config.json")))["ecology"].get("seed") or os.path.basename(run)
    out = []
    for T in range(100, last - 160 + 1, 20):
        for kind in KINDS:
            alive = lambda s: {n for (k, n), (b, l) in life.items() if k == kind and b <= s <= l}
            c0, P = alive(T - 1), alive(T + 160)
            hits, hits_o, depths = [], [], []
            for n in P:
                # BFS up the parents to the C0 ancestors, recording the shortest depth
                frontier, seen, anc, d, dmin = [n], {n}, set(), 0, None
                while frontier:
                    nxt = []
                    for x in frontier:
                        if x in c0:
                            anc.add(x)
                            dmin = d if dmin is None else dmin
                            continue
                        for q in parents.get((kind, x), []):
                            if q not in seen:
                                seen.add(q)
                                nxt.append(q)
                    frontier, d = nxt, d + 1
                A = [W[(kind, a)] for a in anc if (kind, a) in W]
                if (kind, n) not in W or not A:
                    continue
                g, go = W[(kind, n)]
                hits.append(g >= max(a[0] for a in A) + NEW)
                hits_o.append(go >= max(a[1] for a in A) + NEW)
                depths.append(dmin)
            births = sum(1 for (k, _), (b, _) in life.items() if k == kind and T <= b < T + 160)
            if hits:
                out.append((seed, kind, T, len(P), statistics.fmean(hits), statistics.fmean(hits_o), statistics.fmean(depths), births))
    return out


def within(rows, xi, yi):
    by = {}
    for r in rows:
        by.setdefault(r[0], []).append(r)
    xs, ys = [], []
    for g in by.values():
        mx, my = statistics.fmean(r[xi] for r in g), statistics.fmean(r[yi] for r in g)
        xs += [r[xi] - mx for r in g]
        ys += [r[yi] - my for r in g]
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    syy = sum(y * y for y in ys)
    return sxy / sxx, sxy / math.sqrt(sxx * syy)


if __name__ == "__main__":
    if sys.argv[1] == "digest":
        digest(sys.argv[2])
        sys.exit()
    rows = []
    for run in sys.argv[2:]:
        rows += windows(run)
    print("# RBT-101 adversary probe A: `new` against reproduction depth and against a non-posture placebo, "
          "baseline arms only (no terrain change), pseudo-onsets T every 20 seasons, P at T + 160")
    print("seed\tfauna\tT\t|P|\tnew\tnew_other\tdepth\tbirths")
    for r in rows:
        print(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]:.3f}\t{r[5]:.3f}\t{r[6]:.2f}\t{r[7]}")
    for kind in KINDS:
        R = [r for r in rows if r[1] == kind]
        b1, c1 = within(R, 6, 4)
        b2, c2 = within(R, 7, 4)
        b3, c3 = within(R, 5, 4)
        b4, c4 = within(R, 7, 6)
        print(f"# {kind}: {len(R)} windows over {len(set(r[0] for r in R))} seeds; within-seed:"
              f" new ~ depth slope {b1:+.4f}/event r {c1:+.2f};  new ~ births slope {b2 * 100:+.4f}/100 births r {c2:+.2f};"
              f"  new ~ new_other r {c3:+.2f};  depth ~ births r {c4:+.2f}")
        print(f"#   range of depth {min(r[6] for r in R):.2f}-{max(r[6] for r in R):.2f}, births {min(r[7] for r in R)}-{max(r[7] for r in R)},"
              f" new {min(r[4] for r in R):.3f}-{max(r[4] for r in R):.3f}; mean new {statistics.fmean(r[4] for r in R):.3f}")
