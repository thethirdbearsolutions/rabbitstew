"""RBT-134 H1 (DESIGN.md 5.2, registered r3): the holistic structural census, two arms.

Pools: (a) runs/RBT-19/P-801/holistic/final (60), under P-801's own config; (b) RBT-113's C-config holistic
founders, seeds 1-4, from `initial_population` (160), as RBT-121 audit B draws them.  100,000 lineages per pool,
19 holistic `mutate` steps under the pool's MutationConfig with the condition's fields (assay.CONDITIONS; the
holistic operator ignores global_bias_sigma and the designed-body pair event), lineage seeds
SeedSequence([MASTER_SEED, crc32(label), 19, i]) and the auxiliary stream (... + [134]).

ARM G (the global differencing route): a global non-sensor unit whose summed in-links come from `food` sensors on
two distinct Nodes, each with exactly one instance, of opposite sign, and which has >= 1 out-link to an Effector.
ARM I (the local, body-differencing route; FC-S1, FC-N3): >= 2 parts each carrying a `food` sensor joined to an
Effector ON THE SAME PART by a directed path inside that part's own local brain (any depth; every link's summed
weight nonzero).  Sub-counts: I-dup (two such parts are instances of one Node) and I-dist (such parts on >= 2
distinct Nodes); arm I is their union.  Laterality is checked by neither arm: H2 adjudicates it.

    h1_census.py run COND --go [--n 100000] [--workers 4]   -> out/h1-COND.json
    h1_census.py readout                                    -> the per-arm table and the STRUCTURE-BOUND rule
"""
import argparse
import importlib.util
import json
import os
import sys
import zlib
from dataclasses import replace

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "runs", "RBT-113"))

from rabbitstew.analysis import _run_config  # noqa: E402
from rabbitstew.evolution import HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genetics import mutate  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

MASTER_SEED = 20260912  #: RBT-78's (runs/RBT-78/reconcile.py:45), as the Pioneer assay
K = 19
OUT = os.path.join(_HERE, "out")
HOL_CONDITIONS = ("B0", "A0", "P1", "P2", "P3", "P4")  #: DESIGN.md 5.2 (A0 is effector_bias_sigma 0 here)
_POOLS = {}


def _conditions():
    spec = importlib.util.spec_from_file_location("assay134", os.path.join(_HERE, "assay.py"))
    mod = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, ["assay.py"]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod.CONDITIONS


def pool(label):
    if label not in _POOLS:
        if label == "P-801-holistic-final60":
            d = os.path.join(_ROOT, "runs", "RBT-19", "P-801")
            cwd = os.getcwd()
            os.chdir(_ROOT)
            try:
                cfg = _run_config("runs/RBT-19/P-801")
            finally:
                os.chdir(cwd)
            members = [Genotype.load(os.path.join(d, "holistic", "final", f))
                       for f in sorted(os.listdir(os.path.join(d, "holistic", "final")))]
        else:
            import world as W
            cfg = W.evolution_config("C", "", seed=1)
            members = []
            for seed in (1, 2, 3, 4):
                members += initial_population(HOLISTIC, cfg, spawn_streams(seed, cfg.holistic_stream_salt)[HOLISTIC]).members
        _POOLS[label] = (cfg, members)
    return _POOLS[label]


POOLS = ("P-801-holistic-final60", "RBT-113-C-founders160")


def arms(ph):
    """(G, I_dup, I_dist, food_any, food_single_two, multi_food_node) for one phenotype."""
    w = {}
    for s, d, wt in ph.links:
        w[(s, d)] = w.get((s, d), 0.0) + wt
    w = {k: v for k, v in w.items() if v != 0.0}
    food = [i for i, ui in enumerate(ph.units) if ui.unit.kind == "sensor" and ui.unit.source == "food" and ui.part is not None]
    inst = {nd: len(parts) for nd, parts in ph.node_instances.items()}
    node_of = {i: ph.parts[ph.units[i].part].node for i in food}
    # arm G
    G = False
    for k, ui in enumerate(ph.units):
        if ui.part is not None or ui.unit.kind == "sensor":
            continue
        ins = [(node_of[s], w[(s, k)]) for s in food if (s, k) in w and inst.get(node_of[s], 0) == 1]
        pos = {nd for nd, x in ins if x > 0}
        neg = {nd for nd, x in ins if x < 0}
        if not any(a != b for a in pos for b in neg):
            continue
        if any(ph.units[d].unit.kind == "effector" for (s, d) in w if s == k):
            G = True
            break
    # arm I: food sensor -> Effector on the same part, by a directed path inside that part's local units
    by_part = {}
    for i, ui in enumerate(ph.units):
        if ui.part is not None:
            by_part.setdefault(ui.part, set()).add(i)
    out_edges = {}
    for (s, d) in w:
        out_edges.setdefault(s, []).append(d)
    carrying = []
    for s in food:
        p = ph.units[s].part
        local = by_part[p]
        seen, stack, hit = {s}, [s], False
        while stack and not hit:
            u = stack.pop()
            for v in out_edges.get(u, ()):
                if v in local and v not in seen:
                    if ph.units[v].unit.kind == "effector":
                        hit = True
                        break
                    if ph.units[v].unit.kind != "sensor":
                        seen.add(v)
                        stack.append(v)
        if hit:
            carrying.append(p)
    parts = set(carrying)
    nodes = {}
    for p in parts:
        nodes.setdefault(ph.parts[p].node, set()).add(p)
    I_dup = any(len(ps) >= 2 for ps in nodes.values())
    I_dist = len(nodes) >= 2
    food_nodes = {node_of[s] for s in food}
    return (G, I_dup, I_dist, bool(food), sum(1 for nd in food_nodes if inst.get(nd, 0) == 1) >= 2,
            any(inst.get(nd, 0) >= 2 for nd in food_nodes))


def chunk(task):
    cond, label, lo, hi = task
    fields = _conditions()[cond]
    cfg, members = pool(label)
    m = replace(cfg.mutation, **fields)
    rows = []
    for i in range(lo, hi):
        seed = [MASTER_SEED, zlib.crc32(label.encode()), K, i]
        rng = np.random.default_rng(np.random.SeedSequence(seed))
        aux = np.random.default_rng(np.random.SeedSequence(seed + [134]))
        g = members[i % len(members)]
        for _ in range(K):
            g = mutate(g, rng, m, aux_rng=aux)
        r = arms(synthesize(g, cfg.sim.synthesis))
        if any(r):
            rows.append([label, i] + [bool(x) for x in r])
    return label, hi - lo, rows


def run(cond, n, workers, go):
    if cond not in HOL_CONDITIONS:
        sys.exit(f"{cond!r} is not a holistic H1 condition ({', '.join(HOL_CONDITIONS)})")
    if not go:
        sys.exit("refused: registered conditions run only after the merge and the coordinator's GO (pass --go)")
    from concurrent.futures import ProcessPoolExecutor
    tasks = [(cond, label, lo, min(lo + 2_000, n)) for label in POOLS for lo in range(0, n, 2_000)]
    import subprocess
    head = subprocess.check_output(["git", "-C", _ROOT, "rev-parse", "HEAD"], text=True).strip()
    res = {"condition": cond, "n_per_pool": n, "git": head, "pools": {}, "rows": []}
    with ProcessPoolExecutor(workers) as ex:
        for label, cnt, rows in ex.map(chunk, tasks):
            res["pools"][label] = res["pools"].get(label, 0) + cnt
            res["rows"] += rows
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"h1-{cond}.json")
    with open(path + ".tmp", "w") as f:  # atomic: a partial JSON never sits at the final path (lane restarts)
        json.dump(res, f)
    os.replace(path + ".tmp", path)


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return max(0.0, c - h), min(1.0, c + h)


def readout(out=None):
    """The per-arm table with a Wilson interval per arm and condition (F4), and the per-arm STRUCTURE-BOUND rule,
    which is WITHHELD until all six registered conditions are present (F4): a verdict about "no operator in this
    set" needs the whole set."""
    out = out or OUT
    print("# RBT-134 H1 census (DESIGN.md 5.2)\n")
    print("| condition | lineages | arm G [Wilson 95%, per 200,000] | arm I [Wilson 95%, per 200,000] | I-dup | I-dist "
          "| any food sensor | food on >= 2 single-instance Nodes | multi-instance food Node |")
    print("|---|---|---|---|---|---|---|---|---|")
    tot = {"G": 0, "I": 0}
    present = []
    for c in HOL_CONDITIONS:
        path = os.path.join(out, f"h1-{c}.json")
        if not os.path.exists(path):
            continue
        present.append(c)
        r = json.load(open(path))
        n = sum(r["pools"].values())
        col = list(zip(*[row[2:] for row in r["rows"]])) or [()] * 6
        G, dup, dist = (sum(col[j]) for j in range(3))
        I = sum(1 for row in r["rows"] if row[3] or row[4])
        tot["G"] += G
        tot["I"] += I
        cell = {}
        for name, k in (("G", G), ("I", I)):
            lo, hi = wilson(k, n)
            cell[name] = f"{k} [{2e5 * lo:.1f}, {2e5 * hi:.1f}]"
        print(f"| {c} | {n} | {cell['G']} | {cell['I']} | {dup} | {dist} | {sum(col[3])} | {sum(col[4])} | {sum(col[5])} |")
    missing = [c for c in HOL_CONDITIONS if c not in present]
    for arm, v in tot.items():
        what = "global differencing" if arm == "G" else "local body-differencing"
        if v:
            print(f"\narm {arm}: {v} arrivals in total over {', '.join(present)}: H2 runs for it")
        elif missing:
            print(f"\narm {arm}: 0 arrivals so far; STRUCTURE-BOUND WITHHELD until all six conditions are present "
                  f"(missing: {', '.join(missing)})")
        else:
            print(f"\narm {arm}: STRUCTURE-BOUND: no operator in this set proposes the holistic {what} structure at "
                  "depth 19 from these pools; H2 is not run for it")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("cond")
    p.add_argument("--n", type=int, default=100_000)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--go", action="store_true")
    sub.add_parser("readout")
    a = ap.parse_args()
    if a.cmd == "run":
        run(a.cond, a.n, a.workers, a.go)
    else:
        readout()


if __name__ == "__main__":
    main()
