"""RBT-134 control-gate diagnosis, exactly as GATE-FAILURE.md r2 registers it (sections 2-4), run on the owner's approval
(coordinator GO, 2026-10-10).  It reads only B0.json, A0.json, C+.json and readout-controls.txt (lane A's committed
outputs, copied into OUT_DIR from claude/rbt134-runs-A), plus committed inputs; it regenerates B0 lineages only and
computes no family or check condition.

    diagnose.py OUT_DIR [--workers 4]   -> prints the working with its numbers, and the category tokens last

The numbers stay on the designer's branch until r4 is registered and adversary-checked; only the tokens are relayed.
"""
import argparse
import copy
import importlib.util
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

_HERE = os.path.dirname(os.path.abspath(__file__))
_RBT134 = os.path.dirname(_HERE)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, [path]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod


assay = _load("assay134_diag", os.path.join(_RBT134, "assay.py"))
from rabbitstew.genetics import mutate_controller  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

RUNG = assay.RUNGS[assay.PRIMARY]
SWAP = {"food": "agent", "agent": "food"}


# --------------------------------------------------------------------------- #
# U2: the paired exact test (two-sided; rejected iff p <= 0.01; d = 0 is not rejected)
# --------------------------------------------------------------------------- #

def paired_p(x, y):
    """x, y: the two lineage sets.  Discordant lineages are those in exactly one set; d = |x ^ y|.  Under H0 the count
    in x - y is Binomial(d, 1/2); two-sided p = min(1, 2 * min(P(X <= b), P(X >= b)))."""
    b, c = len(x - y), len(y - x)
    d = b + c
    if d == 0:
        return b, c, 1.0
    lo = sum(math.comb(d, j) for j in range(0, b + 1)) / 2 ** d
    hi = sum(math.comb(d, j) for j in range(b, d + 1)) / 2 ** d
    return b, c, min(1.0, 2 * min(lo, hi))


# --------------------------------------------------------------------------- #
# B0 regeneration, predicate only (I5-2), and the food/agent swap (I5-3)
# --------------------------------------------------------------------------- #

def relabel(g):
    """A copy of genotype g with every food sensor made agent and vice versa; nothing else changes."""
    g = copy.deepcopy(g)
    for _, brain in g.brains():
        for u in brain.units:
            if getattr(u, "kind", None) == "sensor" and u.source in SWAP:
                u.source = SWAP[u.source]
    return g


def lineage(label, i, swap):
    cfg, pool = assay.rbt78._load(label)
    mcfg = assay.replace(cfg.mutation, add_link_rate=assay.ADD, remove_link_rate=assay.REM)  # B0: no fields
    seed = [assay.rbt78.MASTER_SEED, assay.zlib.crc32(label.encode()), assay.K, i]
    rng = assay.np.random.default_rng(assay.np.random.SeedSequence(seed))
    aux = assay.np.random.default_rng(assay.np.random.SeedSequence(seed + [assay.AUX_KEY]))
    g = pool[i % len(pool)]
    if swap:
        g = relabel(g)
    for _ in range(assay.K):
        g = mutate_controller(g, rng, mcfg, aux_rng=aux)
    return synthesize(g, cfg.sim.synthesis)


def chunk(task):
    label, lo, hi, swap = task
    food, sham = [], []
    for i in range(lo, hi):
        ph = lineage(label, i, swap)
        if assay.predicate(ph, "food"):
            food.append(i)
        if assay.predicate(ph, "agent"):
            sham.append(i)
    return label, food, sham


def regenerate(n, workers, swap):
    tasks = [(label, lo, min(lo + 2_000, n), swap) for label in assay.rbt78.POOLS for lo in range(0, n, 2_000)]
    food, sham = set(), set()
    with ProcessPoolExecutor(workers) as ex:
        for label, f, s in ex.map(chunk, tasks):
            food |= {(label, i) for i in f}
            sham |= {(label, i) for i in s}
    return food, sham


def phen_signature(ph, swap=False):
    units = []
    for ui in ph.units:
        u = ui.unit
        src = getattr(u, "source", None)
        if swap and src in SWAP:
            src = SWAP[src]
        units.append((ui.part, u.kind, src, getattr(u, "axis", None), getattr(u, "func", None),
                      float(getattr(u, "bias", 0.0) or 0.0)))
    return units, sorted((s, d, float(w)) for s, d, w in ph.links)


def preconditions():
    """GATE-FAILURE.md 4.2 I5-3: (1) every parent carries a food and an agent sensor on each drive-wheel side the
    predicate reads; (2) synthesizing a relabelled parent gives the original phenotype with only the sources swapped."""
    ok1 = ok2 = True
    for label in assay.rbt78.POOLS:
        cfg, pool = assay.rbt78._load(label)
        for g in pool:
            ph = synthesize(g, cfg.sim.synthesis)
            if assay.wheel_sensors(ph, "food") is None or assay.wheel_sensors(ph, "agent") is None:
                ok1 = False
            ph2 = synthesize(relabel(g), cfg.sim.synthesis)
            if phen_signature(ph2) != phen_signature(ph, swap=True):
                ok2 = False
    return ok1, ok2


# --------------------------------------------------------------------------- #

def c_plus_category(cp, b0, readout):
    arrivals = cp["arrivals"]
    A = len(arrivals)
    k = len(assay.k_at(cp, RUNG))
    k_raw = sum(1 for a in arrivals
                if max((abs(u["a"]) for u in a["units"] if math.isfinite(u["a"])), default=0.0) >= RUNG)
    x1, n1 = assay.bg_hits(cp)
    x0, n0 = assay.bg_hits(b0)
    up = assay.katz_upper(x1, n1, x0, n0)
    pe = cp["pair_events"]
    ev, ref, npair = pe["events"], pe["refused"], pe.get("no_pair", 0)
    if k >= 6:
        cat = "C+-BG" if up > assay.MARGIN else "C+-NOT-FAILED"
    elif k_raw >= 6:
        cat = "C+-FLAG"
    elif A >= 84 + 6:
        cat = "C+-RUNG"
    else:
        cat = "C+-SUPPLY-REFUSED" if ref + npair > ev / 2 else "C+-SUPPLY-RARE"
    line = next((l for l in readout.splitlines() if l.startswith("C+: k a32")), "(no C+ line)")
    print(f"C+: A {A}, k {k}, k_raw {k_raw}, background {x1}/{n1} vs B0 {x0}/{n0}, Katz upper {up:.3f}; "
          f"pair events {ev}, refused {ref}, no_pair {npair}")
    print(f"C+ readout line: {line}")
    return cat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--n", type=int, default=100_000)
    a = ap.parse_args()
    b0 = json.load(open(os.path.join(a.out_dir, "B0.json")))
    a0 = json.load(open(os.path.join(a.out_dir, "A0.json")))
    cp = json.load(open(os.path.join(a.out_dir, "C+.json")))
    readout = open(os.path.join(a.out_dir, "readout-controls.txt")).read()
    for line in readout.splitlines():
        if line.startswith(("I5 ", "I4", "I3 ", "I2 ")):
            print(f"readout: {line}")

    tokens = {"I5-2 reproduction": "not run", "swap": "not run"}
    # C+ (section 3.3)
    tokens["C+"] = c_plus_category(cp, b0, readout)

    # I5-1
    print(f"I5-1: B0.sham {b0['sham']}, A0.sham {a0['sham']}, C+.sham {cp['sham']}")
    if tokens["C+"] in ("C+-BG", "C+-FLAG"):
        # GATE-FAILURE.md 3.3 / 3.5: an ESCALATE category means no r4 re-run, and the coordinator's GO says "if any
        # path ESCALATEs, stop and relay that token": the B0 regenerations (I5-2, I5-3) are not run.
        tokens["I5"] = "not determined (stopped: C+ ESCALATE)"
    elif a0["sham"] != b0["sham"]:
        tokens["I5"] = "I5-C"
    else:
        # I5-2
        food, sham = regenerate(a.n, a.workers, swap=False)
        want_food = {(x["label"], x["i"]) for x in b0["arrivals"]}
        committed = {(lab, i) for lab, i, *_ in assay.committed_arrivals("RBT-91-alone-baseline.txt")}
        repro = food == want_food == committed and len(sham) == b0["sham"]
        print(f"I5-2: regenerated food {len(food)} (B0.json {len(want_food)}, RBT-91 committed {len(committed)}, "
              f"equal: {food == want_food == committed}); regenerated sham {len(sham)} (B0.json {b0['sham']})")
        tokens["I5-2 reproduction"] = "YES" if repro else "NO"
        if not repro:
            tokens["I5"] = "I5-C"
        else:
            b, c, p = paired_p(food, sham)
            print(f"I5-2 paired (U2): food-only {b}, sham-only {c}, both {len(food & sham)}, d {b + c}, two-sided p {p:.4g}")
            if p > 0.01:
                tokens["I5"] = "I5-B"
            else:
                # I5-3
                ok1, ok2 = preconditions()
                print(f"I5-3 preconditions: both nose types on both sides {ok1}; synthesis identical up to swap {ok2}")
                if not (ok1 and ok2):
                    tokens["I5"] = "ESCALATE"
                    tokens["swap"] = "not run (precondition)"
                else:
                    sfood, ssham = regenerate(a.n, a.workers, swap=True)
                    exact = sfood == sham and ssham == food
                    print(f"I5-3 swap: swapped food {len(sfood)} == original sham: {sfood == sham}; "
                          f"swapped sham {len(ssham)} == original food: {ssham == food}")
                    tokens["swap"] = "EXACT" if exact else "NOT-EXACT"
                    tokens["I5"] = "I5-A" if exact else "I5-C"
    print("\nTOKENS")
    for key in ("I5", "C+", "I5-2 reproduction", "swap"):
        print(f"  {key}: {tokens[key]}")


if __name__ == "__main__":
    main()
