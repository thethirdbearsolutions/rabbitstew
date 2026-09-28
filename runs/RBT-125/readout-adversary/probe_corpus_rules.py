"""RBT-125 §C adversary: the eating rules on COMMITTED bodies, per body, with each body's span.

(1) The corpus (RBT-90 part 2 seed 801, the living at season 600, from ckpt/rbt-90-801's state.json: 60 + 60), with
side_effects.py's own season() and draws (127000..127003), in U-G0 under: the committed rule, root/centre (the ruled
rule), any/surface with the fixed surface clearance, and root/surface.  The first two rows must reproduce
side_effects.txt's corpus rows exactly (a check on the measurement).
(2) RBT-113's seed-1 generation-0 DESIGNED founders (40 x 8 draws, 126000..), the same four rules in U-G0.
Per body: span = the largest distance from the root geom's centre to any point of any geom (centre distance + that
geom's largest half-extent), measured on the spawned body.  Printed: fauna means, the root and surface effects, and
the correlation of each body's surface gain with its span (a sweeper exploit shows as a gain that grows with span).

    python probe_corpus_rules.py GATE_DIR BODIES_ROOT
"""
import json, os, sys
from dataclasses import replace
import numpy as np
G = os.path.abspath(sys.argv[1]); B = sys.argv[2]; sys.path.insert(0, G)
import side_effects as se  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import Simulation, spawn_layout  # noqa: E402

RULES = {"committed": {}, "root/centre": {"eat_from": "root"}, "any/surface/geoms": {"eat_rule": "surface", "clear_from": "geoms"},
         "root/surface": {"eat_from": "root", "eat_rule": "surface"}}


def span(gd, cfg):
    sim = Simulation([Genotype.from_dict(gd)], cfg, spawns=spawn_layout(1, cfg, 1))
    idx = sim.robots[0]; d = sim.data; m = sim.model
    r0 = d.geom_xpos[idx.geoms[0]]
    return max(float(np.linalg.norm(d.geom_xpos[g] - r0) + m.geom_size[g].max()) for g in idx.geoms)


def block(label, pops, seeds, base_cfg):
    tasks = [((name, kind, i), gd, replace(base_cfg, food=replace(base_cfg.food, **kw)), s)
             for name, kw in RULES.items() for kind in pops for i, gd in enumerate(pops[kind]) for s in seeds]
    R = se.run(tasks, 4)
    print(f"\n## {label}: U-G0, {len(seeds)} solo draws each; items (net) per season, fauna mean; items vs committed")
    print("| fauna | n | " + " | ".join(RULES) + " | corr(surface gain, span) | span median [p90] m |")
    print("|---|---|" + "---|" * (len(RULES) + 2))
    for kind in pops:
        n = len(pops[kind])
        per = {name: np.array([R[(name, kind, i)].mean(axis=0) for i in range(n)]) for name in RULES}
        ref = per["committed"][:, 0].sum()
        cells = [f"{per[nm][:, 0].mean():.3f} ({per[nm][:, 1].mean():+.3f}){'' if nm == 'committed' else f' {100 * (per[nm][:, 0].sum() / ref - 1):+.0f}%' if ref > 0 else ''}" for nm in RULES]
        sp = np.array([span(gd, base_cfg) for gd in pops[kind]])
        gain = per["any/surface/geoms"][:, 0] - per["committed"][:, 0]
        c = np.corrcoef(gain, sp)[0, 1] if gain.std() > 0 else float("nan")
        print(f"| {kind} | {n} | " + " | ".join(cells) + f" | {c:+.2f} | {np.median(sp):.2f} [{np.quantile(sp, 0.9):.2f}] |", flush=True)
        solv = {nm: (per[nm][:, 1] >= se.LIVING_COST).mean() for nm in RULES}
        print(f"|  | solvent | " + " | ".join(f"{solv[nm]:.2f}" for nm in RULES) + " | | |")


def main():
    cfg = se.cond_cfg("U-G0")
    st = json.load(open(os.path.join(B, "forage-801", "state.json")))
    block(f"corpus, RBT-90 seed 801 season {st['season']}", {k: st["populations"][k] for k in (HOLISTIC, CONVENTIONAL)}, [127000 + i for i in range(4)], cfg)
    evo = se.rbt113.evolution_config("U", "", seed=1)
    f = initial_population(CONVENTIONAL, evo, spawn_streams(1)[CONVENTIONAL]).members
    block("RBT-113 seed-1 generation-0 designed founders", {CONVENTIONAL: [m.genotype.to_dict() if hasattr(m, "genotype") else m.to_dict() for m in f]},
          [126000 + i for i in range(8)], cfg)


if __name__ == "__main__":
    main()
