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


def _reads(cls, cfg, g, rot):
    import mujoco
    from rabbitstew.world import Spawn
    sim = cls([g], cfg, spawns=[Spawn(position=(0.5, 0.2, 0.0), yaw=0.4)])
    sim.set_food_seed(3)
    if rot is not None:
        sim._rot = rot
    first = sim.sensor_values(0, set())
    sim.data.qpos[:2] += 0.05
    mujoco.mj_forward(sim.model, sim.data)
    return np.r_[first, sim.sensor_values(0, set())]


def check_decoy():
    """(1) On a contrast world (G = 2.5) the patched decoy reads differently from the intact body, and the UNPATCHED
    decoy reads exactly as the intact body (so the patch is what makes it a decoy).  (2) On a legacy world (G = 0) the
    patch is a no-op: the patched decoy's readings equal the unpatched decoy's, bit for bit."""
    from rabbitstew.fixed import pioneer_genotype
    from rabbitstew.simulation import FoodConfig, SimConfig
    g = pioneer_genotype(np.random.default_rng(1), sources=("food", "contact"))
    cls = rp.mech.RotatedSmell
    for G in (0.0, 2.5):
        cfg = SimConfig(settle_time=0.0, food=FoodConfig(smell_contrast=G, patches=2, patch_radius=0.4, radius=4.0))
        intact = _reads(Simulation, cfg, g, None)
        patched = _reads(cls, cfg, g, 2.0)
        del cls._log_smell
        try:
            unpatched = _reads(cls, cfg, g, 2.0)
        finally:
            cls._log_smell = _rotated_log_smell
        assert not np.array_equal(intact, patched), f"the patched decoy does not change the reading at G={G}"
        if G:
            assert np.array_equal(intact, unpatched), "at G > 0 the unpatched decoy was expected to read the true layout"
        else:
            assert np.array_equal(patched, unpatched), "the patch changed a legacy (G = 0) reading"
    return True


if __name__ == "__main__":
    check_decoy()
    sys.argv = [os.path.join(ROOT, "runs", "RBT-103", "routed_populations.py")] + sys.argv[1:]
    rp.main()
