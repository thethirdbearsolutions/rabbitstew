"""RBT-90 part 2 adversary, probe G: the gait row on more draws and on disjoint draw blocks.

The pre-registered gait row reads every champion at the SAME 64 draws, seeds 8000-8063 (forage_lab.py),
which fix the spawn and the real food layout of each bout.  So the ten per-seed t's are not ten
independent draws of the instrument: a block whose real layouts happen to be poor for a mower pulls
all ten down together.  RBT-39's power ladder reads the same champions on seeds 9000-9063.

This re-runs the lab's own bout, ``forage_lab.trial`` imported unchanged, mode "intact", with the lab's
120 null layouts, on the lab's block (8000-8063, a re-derivation of the committed gait t) and on
BLOCKS fresh disjoint blocks of 64 (seeds 20000 + 64 b + i).  Per champion it prints the t on each
block and on all fresh draws pooled (n = 64 * BLOCKS), and writes every per-draw (food, null) pair
as JSON so that cross-champion correlation within a block can be computed.

usage: gait_blocks.py BULK_ROOT OUT_JSON [BLOCKS] [WORKERS] [SEED ...]
"""
import importlib.util
import json
import pathlib
import sys
from multiprocessing import Pool

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("flab", ROOT / "scripts" / "forage_lab.py")
flab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flab)

SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
DRAWS = 120  # the lab's null layouts per bout
_cache = {}


def one(job):
    bulk, seed, s = job
    if seed not in _cache:
        g, cfg = flab.load(f"{bulk}/forage-{seed}", "holistic", 590)
        ph = flab.synthesize(g, cfg.synthesis)
        _cache[seed] = (g, cfg, ph, flab.groups(ph))
    g, cfg, ph, gs = _cache[seed]
    r = flab.trial(g, cfg, ph, gs, s, "intact", draws=DRAWS)
    return seed, s, r["food"], r["null"]


def t_of(d):
    d = np.asarray(d, float)
    return float(d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))) if d.std(ddof=1) > 0 else float("nan")


if __name__ == "__main__":
    bulk, out = sys.argv[1], sys.argv[2]
    blocks = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    seeds = [int(a) for a in sys.argv[5:]] or SEEDS
    lab = list(range(8000, 8064))
    fresh = [20000 + 64 * b + i for b in range(blocks) for i in range(64)]
    jobs = [(bulk, seed, s) for seed in seeds for s in lab + fresh]
    res = {}
    with Pool(workers) as p:
        for seed, s, food, null in p.imap_unordered(one, jobs, chunksize=8):
            res.setdefault(seed, {})[s] = (food, null)
    json.dump({str(k): {str(s): v for s, v in d.items()} for k, d in res.items()}, open(out, "w"))
    print(f"gait t per champion: lab block (8000-8063, the committed reading) and {blocks} fresh blocks of 64; "
          f"pooled = all {64 * blocks} fresh draws")
    print(f"{'seed':>5s} {'lab':>6s} " + " ".join(f"{'b' + str(b):>6s}" for b in range(blocks))
          + f" {'max':>6s} {'pooled':>7s} {'items':>6s} {'null':>6s}")
    for seed in seeds:
        d = res[seed]
        tl = t_of([d[s][0] - d[s][1] for s in lab])
        tb = [t_of([d[20000 + 64 * b + i][0] - d[20000 + 64 * b + i][1] for i in range(64)]) for b in range(blocks)]
        tp = t_of([d[s][0] - d[s][1] for s in fresh])
        print(f"{seed:5d} {tl:+6.2f} " + " ".join(f"{t:+6.2f}" for t in tb) + f" {max(tb):+6.2f} {tp:+7.2f} "
              f"{np.mean([d[s][0] for s in fresh]):6.3f} {np.mean([d[s][1] for s in fresh]):6.3f}", flush=True)
    # the shared-draw effect: per block, the mean over champions of the per-champion t
    print("\nmean over the ten champions of the per-champion t, per block (independent readings would scatter "
          "about 0 with sd 1/sqrt(10) = 0.32 if every champion sits on its null):")
    rows = [("lab", lab)] + [(f"b{b}", [20000 + 64 * b + i for i in range(64)]) for b in range(blocks)]
    for name, blk in rows:
        ts = [t_of([res[sd][s][0] - res[sd][s][1] for s in blk]) for sd in seeds]
        print(f"  {name:>4s}: mean t {np.mean(ts):+.2f}   champions with t >= +2.5: {sum(t >= 2.5 for t in ts)}")
    # cross-champion correlation of the per-draw difference, within the same draws
    D = np.array([[res[sd][s][0] - res[sd][s][1] for s in lab + fresh] for sd in seeds])
    C = np.corrcoef(D)
    off = C[~np.eye(len(seeds), dtype=bool)]
    print(f"\ncorrelation across champions of the per-draw (items - null), same spawn and layout seed: "
          f"mean {off.mean():+.3f}, min {off.min():+.3f}, max {off.max():+.3f} over {len(off) // 2} pairs")
