"""RBT-104 item 1: what does --link-scale K do to the own-link response of the routed motif as
drift proposes it?  RBT-91's instrument, unchanged, with one field set.

Everything is imported from `runs/RBT-91/structural_rate.py` (the predicate, the links-alone
probe, the lineage generator, RBT-78's pools and MASTER_SEED): 19 `mutate_controller`
mutations from the committed parents, 100,000 lineages per pool, add 0.15 rem 0.1.  The only
change is the flag, applied as the ecology applies it: the committed parents' link weights are
multiplied by K (`scale_links`, as founders are at founding) and `MutationConfig.link_scale = K`.
Because the lineage seeds are the same and the flag multiplies draws without consuming any extra,
a lineage at K draws exactly the random numbers it drew at K = 1 and every link weight it holds
is exactly K times larger; biases are unchanged.  So the structure count should barely move
(a summed weight's sign is scale-free) and each arrival's linear gain is K^2 times its own.

THE SELF-CHECK.  At K = 1 the arrival list (lineage, units, links alone, whole brain) must equal
`docs/artifacts/RBT-91-alone-baseline.txt` line for line, and the script says whether it does.

THE RUNGS are paper 8's like-for-like links-alone readings of the installed routed motif
(`runs/RBT-72-adversary/probe_rung.txt`): 6.2831 at w = 8 (a = 16, the null rung on W4b),
12.5236 at w = 16 (a = 32, pays on 5 of 10 RBT-90 part 2 populations, RBT-103) and 24.7145 at
w = 32 (a = 64, pays on 8 of 10).  Each arrival's own links are re-read against them; the sign
is not read here (half of arrivals point the wrong way for their carrier, paper 8 section 3.4).

Usage: drift_reach.py --k 4 [--n 100000] [--workers 4] [--background 2000]
"""
import argparse
import importlib.util
import os
import re
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("sr91", os.path.join(_ROOT, "runs", "RBT-91", "structural_rate.py"))
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)
rbt78 = sr.rbt78

from rabbitstew.genetics import mutate_controller, scale_links  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

RUNGS = (("a=16 (null, w=8)", 6.2831), ("a=32 (w=16)", 12.5236), ("a=64 (w=32)", 24.7145))
DEPTH = 19


def _lineage(label, i, k, K, mcfg, pool):
    rng = np.random.default_rng(np.random.SeedSequence([rbt78.MASTER_SEED, zlib.crc32(label.encode()), k, i]))
    g = scale_links(pool[i % len(pool)].copy(), K)
    for _ in range(k):
        g = mutate_controller(g, rng, mcfg)
    return g


def chunk(task):
    label, lo, hi, k, K = task
    cfg, pool = rbt78._load(label)
    mcfg = replace(cfg.mutation, add_link_rate=0.15, remove_link_rate=0.1, link_scale=K)
    hits, n = [], 0
    for i in range(lo, hi):
        ph = synthesize(_lineage(label, i, k, K, mcfg, pool), cfg.sim.synthesis)
        n += 1
        units = sr.motif_units(ph)
        if units:
            hits.append((i, len(units), float(sr.small_signal_a(ph)), float(sr.links_alone_a(ph, units[0]))))
    return label, n, hits


def background(task):
    """Whole-brain response of structureless lineages: the recurrent-gain side effect."""
    label, n, k, K = task
    cfg, pool = rbt78._load(label)
    mcfg = replace(cfg.mutation, add_link_rate=0.15, remove_link_rate=0.1, link_scale=K)
    vals = []
    for i in range(n):
        ph = synthesize(_lineage(label, i, k, K, mcfg, pool), cfg.sim.synthesis)
        if sr.motif_units(ph):
            continue
        v = sr.small_signal_a(ph)
        if np.isfinite(v):
            vals.append(abs(v))
    return label, vals


def committed_hits():
    path = os.path.join(_ROOT, "docs", "artifacts", "RBT-91-alone-baseline.txt")
    pat = re.compile(r"^\s+(\S+) lineage (\d+): (\d+) unit\(s\), LINKS ALONE ([-+]\d+\.\d+) .*whole brain ([-+]\d+\.\d+)$")
    out = []
    for line in open(path):
        m = pat.match(line)
        if m:
            out.append((m.group(1), int(m.group(2)), int(m.group(3)), m.group(4), m.group(5)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=float, required=True, help="link_scale")
    ap.add_argument("--n", type=int, default=100000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--background", type=int, default=0)
    a = ap.parse_args()
    K = a.k

    print(f"# RBT-104: the routed motif as drift proposes it, at link_scale K = {K:g}\n")
    print(f"RBT-91's instrument, imported: {DEPTH} mutate_controller mutations from committed parents,")
    print(f"{a.n} lineages per pool, add 0.15 rem 0.1, MASTER_SEED {rbt78.MASTER_SEED}. One field set: link_scale.\n")
    tasks = []
    for label in rbt78.POOLS:
        step = max(1, a.n // (a.workers * 4))
        for lo in range(0, a.n, step):
            tasks.append((label, lo, min(lo + step, a.n), DEPTH, K))
    agg = {label: [0, []] for label in rbt78.POOLS}
    with ProcessPoolExecutor(a.workers) as ex:
        for label, n, hits in ex.map(chunk, tasks):
            agg[label][0] += n
            agg[label][1] += hits

    print("| pool | lineages | structure present | rate |")
    print("|---|---|---|---|")
    N = P = 0
    for label, (n, hits) in agg.items():
        N += n
        P += len(hits)
        print(f"| {label} | {n} | {len(hits)} | {100.0 * len(hits) / n:.3f}% |")
    lo_, hi_ = sr.wilson(P, N)
    print(f"| both | {N} | **{P}** | **{100.0 * P / N:.4f}%** [{100 * lo_:.4f}, {100 * hi_:.4f}] |\n")

    print("## Every arrival: links alone (the circuit under test) and whole brain\n")
    mine = []
    for label, (n, hits) in agg.items():
        for i, u, wb, alone in sorted(hits):
            mine.append((label, i, u, f"{alone:+.4f}", f"{wb:+.4f}"))
            print(f"    {label} lineage {i}: {u} unit(s), LINKS ALONE {alone:+.4f}; whole brain {wb:+.4f}")

    allg = np.array([abs(h[3]) for _, (_, hits) in agg.items() for h in hits if np.isfinite(h[3])])
    print(f"\n## Own-link response |a| of the {len(allg)} arrivals, against the like-for-like rungs\n")
    if len(allg):
        q = np.quantile(allg, [0.5, 0.75, 0.9])
        nz = allg[allg >= 1e-4]
        print(f"  median {q[0]:.4f}  p75 {q[1]:.4f}  p90 {q[2]:.4f}  max {allg.max():.4f}")
        print(f"  responding (|a| >= 1e-4): {len(nz)} of {len(allg)}"
              + (f"; their median {np.median(nz):.4f}" if len(nz) else ""))
        print("\n| rung | links-alone reading | arrivals at or above | of all, Wilson 95% | of responding |")
        print("|---|---|---|---|---|")
        for name, r in RUNGS:
            c = int((allg >= r).sum())
            l, h = sr.wilson(c, len(allg))
            frac_nz = f"{100.0 * c / len(nz):.1f}%" if len(nz) else "n/a"
            print(f"| {name} | {r:.4f} | {c} | {100.0 * c / len(allg):.1f}% [{100 * l:.1f}, {100 * h:.1f}] | {frac_nz} |")

    if a.background:
        with ProcessPoolExecutor(a.workers) as ex:
            bg = []
            for _, vals in ex.map(background, [(label, a.background, DEPTH, K) for label in rbt78.POOLS]):
                bg += vals
        bg = np.array(bg)
        print(f"\n## Side effect: whole-brain |a| of {len(bg)} STRUCTURELESS lineages (first {a.background} per pool)\n")
        print(f"  median {np.median(bg):.4f}  p90 {np.quantile(bg, 0.9):.4f}")
        for name, r in RUNGS:
            c = int((bg >= r).sum())
            l, h = sr.wilson(c, len(bg))
            print(f"  >= {r:.4f} ({name}): {c} = {100.0 * c / len(bg):.2f}% [{100 * l:.2f}, {100 * h:.2f}]")

    if K == 1.0 and a.n == 100000:
        ref = committed_hits()
        same = ref == mine
        print(f"\n## Self-check at K = 1: arrival list against docs/artifacts/RBT-91-alone-baseline.txt\n")
        print(f"  committed {len(ref)} arrivals, this run {len(mine)}: "
              + ("IDENTICAL, line for line" if same else "DIFFERENT -- the instrument is not the committed one"))
        if not same:
            for x, y in zip(ref, mine):
                if x != y:
                    print(f"  first difference: committed {x} / here {y}")
                    break
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
