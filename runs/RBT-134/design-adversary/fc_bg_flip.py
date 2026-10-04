# Fix-check (r2): RBT-91's committed background lineages (first 5,000 per pool) under r2's whole-brain sign_flip.
# Usage: fc_bg_flip.py <r2 decompose_arrivals.py> <sigma or 0> <workers>
import importlib.util, sys, zlib
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import numpy as np
DA, SIG, W = sys.argv[1], float(sys.argv[2]) or None, int(sys.argv[3])
def load():
    spec = importlib.util.spec_from_file_location("da", DA); da = importlib.util.module_from_spec(spec)
    argv = sys.argv; sys.argv = [argv[0], "--readout", "x"]; spec.loader.exec_module(da); sys.argv = argv
    return da
PAY = 6.8664
def chunk(t):
    da = load(); sr = da.sr; rbt78 = sr.rbt78
    label, lo, hi = t
    cfg, pool = rbt78._load(label)
    m = replace(cfg.mutation, add_link_rate=0.15, remove_link_rate=0.1)
    if SIG: m = replace(m, weight_sigma=SIG)
    out = []
    for i in range(lo, hi):
        rng = np.random.default_rng(np.random.SeedSequence([rbt78.MASTER_SEED, zlib.crc32(label.encode()), 19, i]))
        g = pool[i % len(pool)]
        for _ in range(19): g = da.mutate_controller(g, rng, m)
        ph = da.synthesize(g, cfg.sim.synthesis)
        a = sr.small_signal_a(ph)
        if not np.isfinite(a): continue
        out.append((bool(sr.motif_units(ph)), abs(a) >= PAY, da.sign_flip(ph)))
    return out
if __name__ == "__main__":
    da = load()
    tasks = [(lab, lo, lo + 500) for lab in da.sr.rbt78.POOLS for lo in range(0, 5000, 500)]
    with ProcessPoolExecutor(W) as ex:
        res = [r for rr in ex.map(chunk, tasks) for r in rr]
    nos = [r for r in res if not r[0]]
    hits = sum(h for _, h, _ in nos); fl = [r for r in nos if r[2]]
    unf = [r for r in nos if not r[2]]
    print(f"sigma={SIG or 0.4}: structureless {len(nos)}; hits {hits}; flagged lineages {len(fl)} ({100*len(fl)/len(nos):.2f}%), "
          f"of them hits {sum(h for _, h, _ in fl)}; UNFLAGGED: {sum(h for _, h, _ in unf)} of {len(unf)} = {100*sum(h for _, h, _ in unf)/len(unf):.3f}%")
