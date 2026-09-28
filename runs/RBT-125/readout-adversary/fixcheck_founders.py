"""#446 FIX-CHECK (d): the designed founders (RBT-113 seed 1, generation 0; 40 x 8 draws) in U-G0 under committed,
root/centre and root/surface, with probe_corpus_rules.block, on whatever tree GATE_DIR belongs to."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
G = os.path.abspath(sys.argv[1]); sys.path.insert(0, G)
sys.argv = [sys.argv[0], G, "/nonexistent"]
import probe_corpus_rules as pc  # noqa: E402
pc.RULES = {"committed": {}, "root/centre": {"eat_from": "root"}, "any/surface/geoms": {"eat_rule": "surface", "clear_from": "geoms"},
            "root/surface": {"eat_from": "root", "eat_rule": "surface"}}
import rabbitstew  # noqa: E402
print("# rabbitstew from", os.path.dirname(rabbitstew.__file__))
evo = pc.se.rbt113.evolution_config("U", "", seed=1)
f = pc.initial_population(pc.CONVENTIONAL, evo, pc.spawn_streams(1)[pc.CONVENTIONAL]).members
pc.block("RBT-113 seed-1 generation-0 designed founders", {pc.CONVENTIONAL: [m.genotype.to_dict() if hasattr(m, "genotype") else m.to_dict() for m in f]},
         [126000 + i for i in range(8)], pc.se.cond_cfg("U-G0"))
