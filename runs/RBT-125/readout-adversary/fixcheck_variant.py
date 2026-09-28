"""#446 FIX-CHECK (d'): root + surface under three clearances, on the designed founders (40 x 8, U-G0) and the tumbler.

  pre-fix   root-centre clearance only (integration's code path; leak-free for root + surface: motors-off 0)
  #446      root-centre clearance AND clearance-distance (0.8 m) from every eating geom's surface
  minimal   root-centre clearance AND eat_radius (0.35 m) from every eating geom's surface: no item placed in reach
Monkeypatches Simulation._food_spot's avoid test only (probe; no code change).

    PYTHONPATH=<fix tree> python fixcheck_variant.py <fix tree>
"""
import os, sys
from dataclasses import replace
import numpy as np
T = os.path.abspath(sys.argv[1]); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, T); sys.path.insert(0, os.path.join(T, "runs/RBT-125/gate"))
import rabbitstew.simulation as S  # noqa: E402
import side_effects as se  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, generation_sim, initial_population, spawn_streams  # noqa: E402
import probe_tumbler_rules as pt  # noqa: E402

MODE = {"m": "#446"}
orig_cp = S.Simulation._clearance_points


def cp(self):
    out = orig_cp(self)
    if isinstance(out, tuple) and out[0] is S._SURFACE_CLEAR and out[1] is not None:
        if MODE["m"] == "pre-fix":
            return out[1]
        if MODE["m"] == "minimal":
            return ("MIN", out[1], out[2])
    return out


orig_fs = S.Simulation._food_spot


def fs(self, avoid=None):
    if not (isinstance(avoid, tuple) and avoid and avoid[0] == "MIN"):
        return orig_fs(self, avoid)
    f = self.config.food
    _, centres, geoms = avoid
    for _ in range(256):
        p = orig_fs(self, None)  # one draw from the world's own sampler (same rng stream shape: one spot per try)
        if np.linalg.norm(centres - p, axis=1).min() >= f.clearance and self._surface_distance(geoms, p[None, :])[0] >= f.eat_radius:
            return p
    return p


S.Simulation._clearance_points = cp
S.Simulation._food_spot = fs


def main():
    evo = se.rbt113.evolution_config("U", "", seed=1)
    f = [m.genotype.to_dict() if hasattr(m, "genotype") else m.to_dict() for m in initial_population(CONVENTIONAL, evo, spawn_streams(1)[CONVENTIONAL]).members]
    base = generation_sim(evo, 1131)
    print("| clearance for root + surface | founders items (net) | vs committed 0.653 | solvent | tumbler 0.45 m U net | 6.46 m U net | 6.46 m motors-off U | 6.46 m PW net |")
    print("|---|---|---|---|---|---|---|---|")
    for mode in ("pre-fix", "#446", "minimal"):
        MODE["m"] = mode
        c = se.cond_cfg("U-G0"); cfg = replace(c, food=replace(c.food, eat_from="root", eat_rule="surface"))
        R = se.run([((i,), gd, cfg, s) for i, gd in enumerate(f) for s in range(126000, 126008)], 4)
        per = np.array([R[(i,)].mean(axis=0) for i in range(len(f))])
        tt = {}
        for cell in ("U-G0", "PW-G0"):
            c0 = se.cond_cfg(cell, base); c1 = replace(c0, food=replace(c0.food, eat_from="root", eat_rule="surface"))
            for L in (0.45, 6.46):
                aa = (L / 0.3) ** 1.5
                for mv in (True, False):
                    g = (se.rod(aa) if mv else pt.rod_off(aa)).to_dict()
                    x = se.run([((0,), g, c1, s) for s in range(2131, 2151)], 4)[(0,)]
                    tt[(cell, L, mv)] = x[:, 1].mean()
        print(f"| {mode} | {per[:, 0].mean():.3f} ({per[:, 1].mean():+.3f}) | {100 * (per[:, 0].mean() / 0.653 - 1):+.0f}% | {(per[:, 1] >= se.LIVING_COST).mean():.2f} | "
              f"{tt[('U-G0', 0.45, True)]:+.2f} | {tt[('U-G0', 6.46, True)]:+.2f} | {tt[('U-G0', 6.46, False)]:+.2f} | {tt[('PW-G0', 6.46, True)]:+.2f} |", flush=True)


if __name__ == "__main__":
    main()
