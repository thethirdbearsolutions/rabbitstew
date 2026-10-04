# Adversary probe: how much of RBT-91's committed structureless background (|a|>=6.8664) is the `sign` artefact?
# Re-reads ONLY RBT-91's published default / sigma-4.0 background lineages (first 5,000 per pool).
import importlib.util, sys, zlib, copy
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import numpy as np
spec = importlib.util.spec_from_file_location("sr", "runs/RBT-91/structural_rate.py")
sr = importlib.util.module_from_spec(spec); spec.loader.exec_module(sr)
rbt78 = sr.rbt78
from rabbitstew.genetics import mutate_controller
from rabbitstew.synthesis import synthesize
PAY = 6.8664
def chunk(t):
    label, lo, hi, sigma = t
    cfg, pool = rbt78._load(label)
    m = replace(cfg.mutation, add_link_rate=0.15, remove_link_rate=0.1)
    if sigma: m = replace(m, weight_sigma=sigma)
    out = []
    for i in range(lo, hi):
        rng = np.random.default_rng(np.random.SeedSequence([rbt78.MASTER_SEED, zlib.crc32(label.encode()), 19, i]))
        g = pool[i % len(pool)]
        for _ in range(19): g = mutate_controller(g, rng, m)
        ph = synthesize(g, cfg.sim.synthesis)
        a = sr.small_signal_a(ph)
        if not np.isfinite(a): continue
        has = bool(sr.motif_units(ph))
        if abs(a) >= PAY and not has:
            a_small = sr.small_signal_a(ph, drive=0.001)
            ph2 = copy.deepcopy(ph)
            nsign = 0
            for ui in ph2.units:
                if ui.unit.kind == "neuron" and ui.unit.func == "sign":
                    ui.unit.func = "tanh"; nsign += 1
            a_nosign = sr.small_signal_a(ph2)
            out.append((label, i, a, a_small, a_nosign, nsign))
        out.append(("N", has))
    return out
if __name__ == "__main__":
    sigma = float(sys.argv[1]) if sys.argv[1] != "0" else None
    tasks = [(lab, lo, lo + 500, sigma) for lab in rbt78.POOLS for lo in range(0, 5000, 500)]
    with ProcessPoolExecutor(int(sys.argv[2])) as ex:
        res = [r for rr in ex.map(chunk, tasks) for r in rr]
    n_nos = sum(1 for r in res if r[0] == "N" and not r[1])
    hits = [r for r in res if r[0] != "N"]
    print(f"sigma={sigma or 0.4}: structureless n={n_nos}, hits |a|>=6.8664: {len(hits)}")
    art = 0
    for lab, i, a, a1, a2, ns in hits:
        flag = abs(a2) < PAY
        art += flag
        print(f"  {lab} {i}: |a|@0.01={abs(a):.2f} |a|@0.001={abs(a1):.2f} |a| sign->tanh={abs(a2):.2f} n_sign={ns}{'  SIGN-ARTEFACT' if flag else ''}")
    print(f"  hits that fall below 6.8664 when sign units are read as tanh: {art} of {len(hits)}")
