"""RBT-134 E1 (DESIGN.md 8): RBT-121 audit B's per-child structural erosion under every registered condition.

`runs/RBT-121/ga/parity.py`, unchanged in what it measures (RBT-113 C config, founders of seeds 1-4, 25 children per
founder, rng 12106; link survival, children losing any link, food-route loss among carriers), with the condition's
MutationConfig fields (assay.CONDITIONS) and the registered auxiliary stream: one generator, rng seed 12106 + [134].
B0 must print RBT-121's `parity.txt` exactly; under P1-P4 (the main stream untouched, no structural draw) the
structural numbers must equal B0's exactly (DESIGN.md 9, I2).  P5's event is designed-body only and adds links.

    e1_parity.py [COND ...] [--go]   (default: every registered condition)  > out/e1.txt

Every condition but B0 refuses without --go (B0's output must equal a committed file; F1).
"""
import importlib.util
import os
import sys
from dataclasses import replace

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "runs", "RBT-121", "ga"))
sys.path.insert(0, os.path.join(_ROOT, "runs", "RBT-113"))
import world as W  # noqa: E402
from reach import food_routes, link_keys  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genetics import mutate, mutate_controller  # noqa: E402


def _conditions():
    spec = importlib.util.spec_from_file_location("assay134", os.path.join(_HERE, "assay.py"))
    mod = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, ["assay.py"]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod.CONDITIONS


def parity(fields):
    rng = np.random.default_rng(12106)
    aux = np.random.default_rng(np.random.SeedSequence([12106, 134]))
    cfg = W.evolution_config("C", "", seed=1)
    m = replace(cfg.mutation, **fields)
    out = {}
    for kind, fn in ((HOLISTIC, mutate), (CONVENTIONAL, mutate_controller)):
        surv, anyloss, rl, carriers = [], [], [], 0
        for seed in (1, 2, 3, 4):
            for g in initial_population(kind, cfg, spawn_streams(seed, cfg.holistic_stream_salt)[kind]).members:
                L0, R0 = link_keys(g), food_routes(g)
                for _ in range(25):
                    c = fn(g, rng, m, aux_rng=aux)
                    L1 = link_keys(c)
                    s = sum((L0 & L1).values()) / max(1, sum(L0.values()))
                    surv.append(s)
                    anyloss.append(s < 1)
                    if R0:
                        carriers += 1
                        rl.append(len(R0 - food_routes(c)) / len(R0))
        out[kind] = (float(np.mean(surv)), 100 * float(np.mean(anyloss)), carriers,
                     100 * float(np.mean(rl)) if rl else float("nan"))
    return out


def main():
    conds = _conditions()
    args = sys.argv[1:]
    go = "--go" in args
    names = [a for a in args if a != "--go"] or list(conds)
    if not go and any(c != "B0" for c in names):
        sys.exit("refused: registered conditions run only after the merge and the coordinator's GO (pass --go; "
                 "B0 alone needs none)")
    ref = None
    print("# RBT-134 E1: RBT-121 audit B parity under each condition (B0 must equal runs/RBT-121/ga/parity.txt)\n")
    print("| condition | fauna | link survival per child | children losing any link | food-route carriers | route loss per child |")
    print("|---|---|---|---|---|---|")
    for c in names:
        r = parity(conds[c])
        if c == "B0":
            ref = r
        for kind, (s, a, n, l) in r.items():
            same = "" if ref is None or c == "B0" else (" (= B0)" if ref[kind] == r[kind] else " (differs from B0)")
            print(f"| {c} | {kind} | {s:.4f} | {a:5.1f}% | {n} | {l:.2f}%{same} |")


if __name__ == "__main__":
    main()
