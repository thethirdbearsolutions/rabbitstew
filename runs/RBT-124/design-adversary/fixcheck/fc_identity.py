"""RBT-124 FIX-CHECK: is the MJCF byte-identical with the flags off, body by body?

    PYTHONPATH=<tree> fc_identity.py > <tree>.txt      (then diff the outputs of two trees)

Hashes build_xml(WorldConfig()) -- every flag off -- for every holistic and designed body of restored RBT-113 O1
(founders and U/D/C finals, seeds 1-3: 960 bodies), 200 random holistic genotypes (random_genotype, rng 124) and the
Pioneer (rng 0..4, rich and plain).  One digest per group and one over everything.  Nothing is written into any run.
"""
import hashlib
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..") if len(sys.argv) < 2 else sys.argv[1]
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
import world  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.fixed import pioneer_genotype  # noqa: E402
from rabbitstew.genotype import Genotype, random_genotype  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402
from rabbitstew.world import Spawn, WorldConfig, build_xml  # noqa: E402

wc = WorldConfig()
total = hashlib.sha256()


def digest(label, genotypes, syn=None):
    h = hashlib.sha256()
    for g in genotypes:
        x = build_xml([synthesize(g, syn) if syn is not None else synthesize(g)], [Spawn()], wc).encode()
        h.update(x)
        total.update(x)
    print(f"{label:28s} {len(genotypes):4d} {h.hexdigest()[:16]}")


arm = os.path.join(ROOT, "runs", "RBT-113", "O1")
for kind in (HOLISTIC, CONVENTIONAL):
    for seed in (1, 2, 3):
        cfg = world.evolution_config("U", "", seed=seed)
        gs = initial_population(kind, cfg, spawn_streams(seed, cfg.holistic_stream_salt)[kind]).members
        for L in "UDC":
            p = os.path.join(arm, str(seed), L, kind, "final")
            gs += [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
        digest(f"O1/{seed} {kind}", gs, cfg.sim.synthesis)
rng = np.random.default_rng(124)
digest("random holistic", [random_genotype(rng) for _ in range(200)])
digest("pioneer", [pioneer_genotype(np.random.default_rng(s), rich=r) for s in range(5) for r in (False, True)])
print(f"{'ALL':28s} {'':4s} {total.hexdigest()[:16]}")
