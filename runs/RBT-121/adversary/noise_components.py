"""RBT-121 adversary on audit B finding 3: variance components behind the '0.144 / 0.004' repeatability.

    python runs/RBT-121/adversary/noise_components.py /tmp/claude-0/adv_noise/O1/1 U > runs/RBT-121/adversary/noise_components.txt

Independent re-score of every final RBT-113 O1 seed-1 U-line member on 12 fresh draws (terrain 5131+j, start 6131+j;
disjoint from audit B's 3131/4131), keeping food items and work separately.  Reports: raw matrix summaries, zero share,
distinct genomes, two-way (member x draw) ANOVA variance components with an F-test for 'between-member variance > 0'
and a bootstrap CI on ICC(1 draw); also RBT-113-style draws (ONE terrain, 2 starts) vs independent terrains.
"""
import hashlib
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, "/home/user/rabbitstew/runs/RBT-113")
import world as W  # noqa: E402
from rabbitstew.evolution import generation_sim  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import run_group  # noqa: E402

J = 12
DRAWS = [(5131 + j, 6131 + j) for j in range(J)]


def _solo(a):
    gd, sim, s = a
    r = run_group([Genotype.from_dict(gd)], sim, s)[0]
    return r["score"], r["food"], r["work"]


_NULL = {}


def f_sf(F, d1, d2):
    """P(F' >= F) under the F(d1, d2) null, by simulation (no scipy here)."""
    if (d1, d2) not in _NULL:
        r = np.random.default_rng(0)
        _NULL[(d1, d2)] = (r.chisquare(d1, 200000) / d1) / (r.chisquare(d2, 200000) / d2)
    return float(np.mean(_NULL[(d1, d2)] >= F))


def components(A):
    n, k = A.shape
    gm = A.mean()
    rm, cm = A.mean(1), A.mean(0)
    ms_r = k * ((rm - gm) ** 2).sum() / (n - 1)
    res = A - rm[:, None] - cm[None, :] + gm
    ms_e = (res ** 2).sum() / ((n - 1) * (k - 1))
    sb2 = (ms_r - ms_e) / k
    F = ms_r / ms_e
    p = f_sf(F, n - 1, (n - 1) * (k - 1))
    return sb2, ms_e, F, p


def main(argv):
    d, line = argv[1], argv[2] if len(argv) > 2 else "U"
    seed = int(os.path.basename(d.rstrip("/")))
    cfg = W.evolution_config(line, "", seed=seed)
    sims = [generation_sim(cfg, t) for t, _ in DRAWS]
    one_terrain = generation_sim(cfg, 5131)
    rng = np.random.default_rng(121)
    print(f"# {d} line {line}: every final member, {J} solo draws (independent terrain+start each)")
    with Pool(4) as pool:
        for kind in ("holistic", "conventional"):
            p = os.path.join(d, line, kind, "final")
            fs = sorted(os.listdir(p))
            ms = [Genotype.load(os.path.join(p, f)) for f in fs]
            hashes = [hashlib.md5(json.dumps({k: v for k, v in json.load(open(os.path.join(p, f))).items() if k not in ("name", "parents", "record")}, sort_keys=True).encode()).hexdigest() for f in fs]
            tasks = [(g.to_dict(), sims[j], s) for g in ms for j, (_, s) in enumerate(DRAWS)]
            R = np.array(pool.map(_solo, tasks, chunksize=2), float).reshape(len(ms), J, 3)
            A, F_, Wk = R[..., 0], R[..., 1], R[..., 2]
            np.save(f"/tmp/claude-0/adv_noise/noise_{kind}.npy", R)
            sb2, se2, F, pv = components(A)
            icc1 = sb2 / (sb2 + se2)
            icc2 = sb2 / (sb2 + se2 / 2)
            boots = []
            for _ in range(2000):
                ii = rng.integers(0, len(ms), len(ms)); jj = rng.integers(0, J, J)
                b, e, *_ = components(A[np.ix_(ii, jj)])
                boots.append(max(b, 0) / (max(b, 0) + e / 2))
            lo, hi = np.percentile(boots, [2.5, 97.5])
            print(f"\n== {kind}: n {len(ms)}, distinct genomes {len(set(hashes))}")
            print(f"   net: mean {A.mean():.3f}; items: mean {F_.mean():.3f}, share of runs with 0 items {np.mean(F_ == 0):.2f}, "
                  f"items histogram {np.bincount(F_.astype(int).ravel()).tolist()}; work kJ mean {Wk.mean() / 1000:.2f} (between-member SD {Wk.mean(1).std(ddof=1) / 1000:.3f})")
            print(f"   member means of net: min {A.mean(1).min():.3f} median {np.median(A.mean(1)):.3f} max {A.mean(1).max():.3f}; SD {A.mean(1).std(ddof=1):.3f}"
                  f"  (pure-noise expectation sqrt(ms_e/{J}) = {np.sqrt(se2 / J):.3f})")
            print(f"   two-way ANOVA: between-member var {sb2:+.4f} (SD {np.sqrt(max(sb2, 0)):.3f}), member x draw var {se2:.4f} (SD {np.sqrt(se2):.3f}); "
                  f"F({len(ms) - 1},{(len(ms) - 1) * (J - 1)}) = {F:.2f}, p = {pv:.3g}")
            print(f"   ICC one draw {icc1:+.3f}; repeatability of the 2-draw mean {icc2:+.3f}; bootstrap 95% CI (members x draws) [{lo:.3f}, {hi:.3f}]")
            sb2i, se2i, Fi, pvi = components(F_)
            print(f"   items only: between var {sb2i:+.4f}, within var {se2i:.4f}, ICC2 {max(sb2i, 0) / (max(sb2i, 0) + se2i / 2):.3f}, p {pvi:.3g}")
            # RBT-113's real 2-draw fitness: one terrain per generation, two starts
            t2 = [(g.to_dict(), one_terrain, s) for g in ms for s in (7001, 7002)]
            B = np.array(pool.map(_solo, t2, chunksize=2), float).reshape(len(ms), 2, 3)[..., 0]
            r = np.corrcoef(B[:, 0], B[:, 1])[0, 1]
            print(f"   same terrain, two starts: member correlation of the two draws {r:+.3f} (a within-terrain repeatability of one draw)")


if __name__ == "__main__":
    main(sys.argv)
