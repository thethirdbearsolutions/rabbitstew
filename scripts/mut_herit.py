"""Is the fitness signal unheritable because the operators are too disruptive?  Parent-child correlation
of body and controller descriptors under one round of mutation, no selection, no bouts: what a child
inherits before the world has any say.  usage: mut_herit.py RUN N"""
import json, sys, numpy as np
from rabbitstew.analysis import controller_descriptors, morphology_descriptors
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.genetics import mutate, mutate_controller
from rabbitstew.genotype import Genotype
run, n = sys.argv[1], int(sys.argv[2])
cfg = EvolutionConfig.from_dict(json.load(open(f"{run}/config.json")))
state = json.load(open(f"{run}/state.json"))
rng = np.random.default_rng(0)
def vec(g):
    m = morphology_descriptors(g, cfg.sim); c = controller_descriptors(g, cfg.sim)
    keys_m = [k for k, v in m.items() if isinstance(v, (int, float))]; keys_c = [k for k, v in c.items() if isinstance(v, (int, float))]
    return {**{"m:" + k: float(m[k]) for k in keys_m}, **{"c:" + k: float(c[k]) for k in keys_c}}
for kind, op in (("holistic", mutate), ("conventional", mutate_controller)):
    members = [Genotype.from_dict(d) for d in state["populations"][kind]["members"]]
    pairs = []
    for i in range(n):
        p = members[i % len(members)]
        c = op(p, rng, cfg.mutation)
        pairs.append((vec(p), vec(c)))
    common = set.intersection(*[set(a) & set(c) for a, c in pairs])
    keys = [k for k in pairs[0][0] if k in common and np.std([a[k] for a, _ in pairs]) > 1e-9]
    rows = []
    for k in keys:
        a = np.array([p[k] for p, _ in pairs]); b = np.array([c[k] for _, c in pairs])
        r = float(np.corrcoef(a, b)[0, 1]) if np.std(b) > 1e-9 else float("nan")
        rows.append((k, r, float(np.mean(np.abs(b - a)) / (np.std(a) + 1e-9))))
    print(f"{kind}: {n} parent-child pairs, descriptor parent-child correlation (r) and mean |change| in parent SDs:")
    for k, r, d in sorted(rows, key=lambda t: t[1]):
        print(f"   {k:28s} r={r:+.2f}  change={d:.2f} sd")
    print(f"   median r over descriptors: {np.nanmedian([r for _, r, _ in rows]):+.2f}", flush=True)
