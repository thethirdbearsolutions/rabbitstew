"""RBT-121 audit B, probe 3: how much of a selected trait's variance is evaluation noise, and what gain selection sees.

    python runs/RBT-121/ga/noise.py CKPT_SEED_DIR [LINE] > runs/RBT-121/ga/noise.txt

CKPT_SEED_DIR is one RBT-113 seed directory restored from its checkpoint (e.g. O1/1 from `ckpt/rbt-113-O1`, which
holds the final genomes the results branch does not).  Every final member of the line, both faunas, is scored alone on
6 fresh draws (terrain 3131+j, start 4131+j) under the arm's own config (runs/RBT-113/world.py), exactly as decompose
scores them.  Printed: between-member and within-member (draw-to-draw) SD of net yield, the repeatability of RBT-113's
2-draw fitness, and, by Monte Carlo on those numbers, the selection coefficient a carrier of a +delta gain gets under
RBT-113's truncation (top 10 of 40 on a 2-draw mean): s = P(carrier kept) / P(non-carrier kept) - 1.
"""
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "RBT-113"))
import world as W  # noqa: E402

from rabbitstew.evolution import generation_sim  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import run_group  # noqa: E402

DRAWS = [(3131 + j, 4131 + j) for j in range(6)]


def _solo(args):
    gd, sim, seed = args
    return run_group([Genotype.from_dict(gd)], sim, seed)[0]["score"]


def selection_s(mu, sb, sw, delta, draws=2, n=40, k=10, reps=20000, rng=None):
    """Truncation on a noisy mean: one carrier (+delta) among n; P(kept) against a non-carrier's k/n baseline."""
    rng = rng or np.random.default_rng(5)
    g = rng.normal(mu, sb, size=(reps, n))
    g[:, 0] += delta
    obs = g + rng.normal(0, sw / np.sqrt(draws), size=(reps, n))
    rank = (obs > obs[:, :1]).sum(axis=1)  # members beating the carrier
    p_c = np.mean(rank < k)
    p_nc = (k - p_c) / (n - 1)
    return p_c / p_nc - 1


def main(argv):
    d = argv[1]
    line = argv[2] if len(argv) > 2 else "U"
    seed = int(os.path.basename(d.rstrip("/")))
    cfg = W.evolution_config(line, "", seed=seed)
    sims = [generation_sim(cfg, t) for t, _ in DRAWS]
    print(f"# {d} line {line}: every final member, 6 solo draws each")
    with Pool(4) as pool:
        for kind in ("holistic", "conventional"):
            p = os.path.join(d, line, kind, "final")
            ms = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
            tasks = [(g.to_dict(), sims[j], s) for g in ms for j, (_, s) in enumerate(DRAWS)]
            A = np.array(pool.map(_solo, tasks, chunksize=2), float).reshape(len(ms), len(DRAWS))
            # RBT-113 shares each generation's draws, so a draw's main effect moves everyone alike and cannot
            # mis-rank: remove it, and keep only the member x draw interaction as the noise selection sees.
            mu, sw = A.mean(), np.sqrt((A - A.mean(axis=0)).var(axis=1, ddof=1).mean() * len(DRAWS) / (len(DRAWS) - 1))
            print(f"    raw draw-to-draw SD {np.sqrt(A.var(axis=1, ddof=1).mean()):.3f}; draw main effects {np.round(A.mean(axis=0), 2).tolist()}")
            sb2 = max(A.mean(axis=1).var(ddof=1) - sw ** 2 / len(DRAWS), 0.0)
            sb = np.sqrt(sb2)
            rep2 = sb2 / (sb2 + sw ** 2 / 2)
            print(f"{kind:12s} n {len(ms)}  mean net {mu:.3f}  between-member SD {sb:.3f}  member x draw SD {sw:.3f}  "
                  f"repeatability of one draw {sb2 / (sb2 + sw ** 2):.3f}, of the 2-draw fitness {rep2:.3f}")
            for delta in (0.02, 0.05, 0.1, 0.2, 0.5):
                s2 = selection_s(mu, sb, sw, delta)
                s8 = selection_s(mu, sb, sw, delta, draws=8)
                print(f"    gain +{delta:<4} (x draw SD {delta / sw:.2f}): s at 2 draws {s2:+.3f}, at 8 draws {s8:+.3f}; "
                      f"generations for a carrier lineage to double at s: {np.log(2) / np.log1p(s2) if s2 > 0 else float('inf'):.1f}")


if __name__ == "__main__":
    main(sys.argv)
