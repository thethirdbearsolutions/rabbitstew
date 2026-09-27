"""RBT-120 design adversary: the Pioneer's Sum gear / (4 M) under every brain variant and mass budget, and whether
its MJCF is byte-identical at C = 1.77 (margin 0.5%)."""
import sys, os
import numpy as np
from rabbitstew.fixed import pioneer_genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize
from rabbitstew.world import WorldConfig, dof_gears, motor_scale, build_xml, Spawn
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import world as W
src = W.evolution_config("D", seed=5).mutation.vocab.sensor_sources
print("rich foraging mass_budget  sum_gear  mass  ratio  scale@1.77  mjcf_identical@1.77")
for rich, sources in ((False, None), (True, None), (True, src)):
    for mb in (None, 15.34, 10.0, 5.0, 30.0):
        g = pioneer_genotype(np.random.default_rng(1), rich=rich, sources=sources)
        sc = SimConfig(); sc.synthesis.mass_budget = mb
        ph = synthesize(g, sc.synthesis)
        tot = sum(dof_gears(ph, WorldConfig()).values()); m = sum(p.mass for p in ph.parts)
        same = build_xml([ph], [Spawn()], WorldConfig()) == build_xml([ph], [Spawn()], WorldConfig(motor_budget=1.77))
        print(rich, sources is not None, mb, round(tot, 4), round(m, 5), round(tot / (4 * m), 6), motor_scale(ph, WorldConfig(motor_budget=1.77)), same)
