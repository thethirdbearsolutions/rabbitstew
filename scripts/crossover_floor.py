"""The no-selection retention floor, WITH crossover. RBT-80.

My pre-registered floor came from scripts/motif_survival.py, which applies
mutation only. The coordinator pointed out it is the wrong reference: the drift
arm breeds by crossover a third of the time, and the observed drift plateau
(0.60-0.68) sits BELOW the mutation-only depth-5 floor of 0.858 — which a
mutation-only model cannot explain.

It cannot explain it because `crossover_controller` is not gentle to this
motif. With conventional_topology the child takes parent A's body and LOCAL
brains, and with probability 0.5 takes parent B's GLOBAL brain, keeping only
links that still resolve. The routed compass is split across both: its tanh
neuron and the two nose inputs live in the global brain, the two
neuron->effector links live in the node brains. So a crossover that swaps in a
non-carrier's global brain decapitates the motif's input half and leaves its
output half dangling. That is a far larger loss channel than mutation, and it
is why the drift arm loses carriers faster than mutation alone predicts.

This measures the real per-reproduction retention using the ecology's own
operators and its own mate rule (uniform over same-kind breeders; in the drift
arm birth_threshold is 0, so that is the whole living population).

Structural only - realised gain is a path sum over the synthesised phenotype -
so no simulation and light on CPU, as asked.

CAVEAT, stated rather than hidden: this scores carriage by structural gain
a >= +16 WITHOUT re-signing against direction of travel, because that needs
simulation. Inversion only ever removes carriers, so the retention measured
here is an UPPER bound and the floor it implies is a permissive one.

Usage: python scripts/crossover_floor.py [arm-dir] [season] [trials]
"""
import copy, dataclasses, json, os, sys, numpy as np
from rabbitstew.genotype import Genotype, BrainVocabulary
from rabbitstew.genetics import MutationConfig, mutate_controller, crossover_controller
from rabbitstew.synthesis import synthesize
from rabbitstew.simulation import SimConfig
import importlib.util
_d = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("cvf", os.path.join(_d, "compass_vs_flip.py"))
cvf = importlib.util.module_from_spec(_s); _s.loader.exec_module(cvf)

ARM = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-80/seedA/drift"
SEASON = int(sys.argv[2]) if len(sys.argv) > 2 else 150
TRIALS = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
THRESH = 16.0


def mutation_config(mut):
    names = {f.name for f in dataclasses.fields(MutationConfig)}
    vals = {k: v for k, v in mut.items() if k in names}
    if isinstance(vals.get("vocab"), dict):
        vals["vocab"] = BrainVocabulary.from_dict(vals["vocab"])
    return dataclasses.replace(MutationConfig(), **vals)


def main():
    raw = json.load(open(f"{ARM}/config.json"))
    cfg = SimConfig.from_dict(raw["sim"])
    mc = mutation_config(raw["mutation"])
    xrate = raw["ecology"]["crossover_rate"]

    alive = {}
    for line in open(f"{ARM}/lineage.jsonl"):
        r = json.loads(line)
        if r["population"] == "conventional":
            alive.setdefault(r["generation"], []).append(r["name"])
    names = alive[SEASON]
    pop, gains = [], []
    for n in names:
        p = f"{ARM}/conventional/genomes/{n}.json"
        if not os.path.exists(p):
            continue
        g = Genotype.load(p)
        a, _ = cvf.steering_gain(synthesize(g, cfg.synthesis))
        pop.append(g); gains.append(0.0 if a is None else float(a))
    gains = np.array(gains)
    carr = [g for g, a in zip(pop, gains) if a >= THRESH]
    print(f"{ARM}, season {SEASON}: {len(pop)} living genomes, "
          f"{len(carr)} carriers ({len(carr)/max(1,len(pop)):.3f}), crossover_rate {xrate}")
    if not carr:
        print("no carriers at this season; nothing to measure")
        return

    rng = np.random.default_rng(17)
    kept = {"clone": [0, 0], "cross": [0, 0]}
    for t in range(TRIALS):
        parent = carr[int(rng.integers(0, len(carr)))]
        use_x = rng.random() < xrate and len(pop) > 1
        if use_x:
            mate = pop[int(rng.integers(0, len(pop)))]
            child = crossover_controller(parent, mate, np.random.default_rng([17, t]))
            child = mutate_controller(child, np.random.default_rng([18, t]), mc)
            key = "cross"
        else:
            child = mutate_controller(copy.deepcopy(parent), np.random.default_rng([18, t]), mc)
            key = "clone"
        a, _ = cvf.steering_gain(synthesize(child, cfg.synthesis))
        kept[key][1] += 1
        if a is not None and a >= THRESH:
            kept[key][0] += 1

    ck, cn = kept["clone"]; xk, xn = kept["cross"]
    r_clone = ck / max(1, cn); r_cross = xk / max(1, xn)
    r = (ck + xk) / max(1, cn + xn)
    print(f"\nper-reproduction retention, carrier parent -> carrier child:")
    print(f"  clone + mutation only : {r_clone:.3f}   (n={cn})")
    print(f"  crossover + mutation  : {r_cross:.3f}   (n={xn})")
    print(f"  combined at rate {xrate}: {r:.3f}")
    # The structural motif is robust; what erodes without selection is the SIGN
    # MATCH between motif and gait. Direction inverts at 0.076 per mutation
    # (scripts/direction_heritability.py, 288 offspring, 95% CI [0.017, 0.142])
    # and inversion is not absorbing - a lineage can flip back - so alignment is
    # a two-state chain: P(aligned after d) = 0.5 * (1 + (1-2q)^d).
    q = 0.076
    print(f"\nimplied NO-SELECTION floor on RE-SIGNED carriage, after d reproductions")
    print(f"  structural retention {r:.3f}/reproduction, direction inversion q={q}")
    print("| depth | structural | aligned | floor (product) | mutation-only ref |")
    print("|---|---|---|---|---|")
    ref = {2: 0.967, 5: 0.858, 8: 0.700, 11: 0.575, 15: 0.483}
    for d in (2, 5, 8, 11, 15):
        al = 0.5 * (1 + (1 - 2 * q) ** d)
        print(f"| {d} | {r**d:.3f} | {al:.3f} | **{r**d * al:.3f}** | {ref[d]:.3f} |")
    print("\nCompare each arm against the floor AT ITS OWN realised depth, not")
    print("against a shared one: seed A drift ran 5.0 births/slot, seeded 11.0.")


if __name__ == "__main__":
    main()
