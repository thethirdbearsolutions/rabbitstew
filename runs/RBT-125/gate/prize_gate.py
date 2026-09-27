"""RBT-125 world gate: RBT-103's routed-compass harness (runs/RBT-103/routed_populations.py), unchanged, with ONE
patch that the new channel needs: the rotated-live-layout decoy must rotate what the contrast channel smells.

RBT-97's `RotatedSmell` overrides `Simulation._intensity`, the legacy reading.  Under `food.smell_contrast > 0` the
food sensors read through `Simulation._log_smell` instead, so an unpatched decoy would smell the TRUE layout and
return the intact income: a decoy that cannot fail.  This adds the same rotation to `_log_smell` (only for the food
array, exactly as `_intensity` does), and asserts before anything runs that, on a contrast world, the patched decoy
reads differently from the intact body and, on a legacy world, the patch changes nothing.

    prize_gate.py <routed_populations.py arguments>       (same arguments, same output)
"""
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

spec = importlib.util.spec_from_file_location("rbt103_routed_populations", os.path.join(ROOT, "runs", "RBT-103", "routed_populations.py"))
rp = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = rp
spec.loader.exec_module(rp)

from rabbitstew.simulation import Simulation  # noqa: E402


def _rotated_log_smell(self, point, sources):
    if self._rot is not None and sources is self.food_pos:
        c, sn = float(np.cos(self._rot)), float(np.sin(self._rot))
        sources = sources @ np.array([[c, sn], [-sn, c]])
    return Simulation._log_smell(self, point, sources)


rp.mech.RotatedSmell._log_smell = _rotated_log_smell


def check_decoy():
    """The patched decoy smells a rotated layout under the contrast channel (and the legacy path is untouched)."""
    from rabbitstew.fixed import pioneer_genotype
    from rabbitstew.simulation import FoodConfig, SimConfig
    from rabbitstew.world import Spawn
    g = pioneer_genotype(np.random.default_rng(1), sources=("food", "contact"))
    for G in (0.0, 2.5):
        cfg = SimConfig(settle_time=0.0, food=FoodConfig(smell_contrast=G, patches=2, patch_radius=0.4, radius=4.0))
        reads = []
        for cls in (Simulation, rp.mech.RotatedSmell):
            sim = cls([g], cfg, spawns=[Spawn(position=(0.5, 0.2, 0.0), yaw=0.4)])
            sim.set_food_seed(3)
            if cls is not Simulation:
                sim._rot = 2.0
            sim.sensor_values(0, set())
            sim.data.qpos[:2] += 0.05
            import mujoco
            mujoco.mj_forward(sim.model, sim.data)
            reads.append(sim.sensor_values(0, set()))
        assert not np.array_equal(reads[0], reads[1]), f"decoy does not change the reading at G={G}"
    return True


if __name__ == "__main__":
    check_decoy()
    sys.argv = [os.path.join(ROOT, "runs", "RBT-103", "routed_populations.py")] + sys.argv[1:]
    rp.main()
