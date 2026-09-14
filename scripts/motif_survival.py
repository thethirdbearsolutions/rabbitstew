"""How many mutations does an installed compass motif survive?

RBT-65 needs this to know whether "the motif was still there at season 300"
means anything. If the motif survives the arm's realised search depth with high
probability under PURE MUTATION, then retention is uninformative by
construction - neither selection nor its absence could have shown up.

Structural only: the realised steering gain is a path sum over the synthesised
phenotype, so no simulation is needed and 120 chains x 60 mutations is seconds.

Measured on RBT-23/W4b-801 gen 590 with the routed motif installed at w=32:

  mutations   fraction still carrying a >= +16
  0           1.000
  5           0.858     <- drift arm's realised depth (~5 reproductions)
  11          0.575     <- seeded arm's realised depth (~11 reproductions)
  15          0.483     <- median survival
  30          0.225
  60          0.058

So at the seeded arm's depth pure mutation would leave only ~58% of lineages
carrying a usable compass, yet the champion trace holds it in 30/30 snapshots
in BOTH arms. That is not evidence of selection: `best_lifetime_score` picks
the best forager in the drift arm too, and compass carriers forage better, so
the champion is a score-selected sample in both. Answering the retention
question needs POPULATION-level carriage, which the ecology does not save.

Usage: python scripts/motif_survival.py [chains] [steps]
"""
import copy, dataclasses, json, sys, os, numpy as np
from rabbitstew.genotype import Genotype, BrainVocabulary
from rabbitstew.genetics import mutate_controller, MutationConfig
from rabbitstew.synthesis import synthesize
from rabbitstew.simulation import SimConfig
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from genotype_motif import install
import importlib.util
_s = importlib.util.spec_from_file_location(
    "cvf", os.path.join(os.path.dirname(os.path.abspath(__file__)), "compass_vs_flip.py"))
cvf = importlib.util.module_from_spec(_s); _s.loader.exec_module(cvf)

RUN = "runs/RBT-23/W4b-801"
PARENT = 590
THRESHOLD = 16.0


def mutation_config(mut):
    names = {f.name for f in dataclasses.fields(MutationConfig)}
    vals = {k: v for k, v in mut.items() if k in names}
    if isinstance(vals.get("vocab"), dict):
        vals["vocab"] = BrainVocabulary.from_dict(vals["vocab"])
    return dataclasses.replace(MutationConfig(), **vals)


if __name__ == "__main__":
    chains = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    raw = json.load(open(f"{RUN}/config.json"))
    cfg = SimConfig.from_dict(raw["sim"])
    mc = mutation_config(raw["mutation"])
    g0 = install(Genotype.load(f"{RUN}/conventional/best_gen{PARENT:04d}.json"), 32.0)
    a0, _ = cvf.steering_gain(synthesize(g0, cfg.synthesis))
    surv = np.zeros(steps + 1)
    for c in range(chains):
        g = copy.deepcopy(g0)
        rng = np.random.default_rng([99, c])
        alive = True
        surv[0] += 1
        for t in range(1, steps + 1):
            g = mutate_controller(g, rng, mc)
            a, _ = cvf.steering_gain(synthesize(g, cfg.synthesis))
            if alive and (a is None or a < THRESHOLD):
                alive = False
            if alive:
                surv[t] += 1
    surv /= chains
    print(f"seeded founder realised a = {a0:+.1f}; {chains} chains x {steps} mutations")
    print(f"survival = fraction still carrying a >= +{THRESHOLD:g}\n")
    print("| mutations | survival |")
    print("|---|---|")
    for t in (0, 2, 5, 8, 11, 15, 20, 30, 40, steps):
        if t <= steps:
            print(f"| {t} | {surv[t]:.3f} |")
    half = int(np.argmax(surv < 0.5)) if (surv < 0.5).any() else None
    print(f"\nmedian survival: {str(half) + ' mutations' if half else '>' + str(steps)}")
    print(f"at  5 mutations (drift arm depth):  {surv[5]:.3f}")
    print(f"at 11 mutations (seeded arm depth): {surv[11]:.3f}")
