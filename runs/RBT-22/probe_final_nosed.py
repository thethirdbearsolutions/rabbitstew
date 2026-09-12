"""The nosed holistic individuals of the final population, probed like the bests.

This arm saved no holistic best carrying a smell sensor, so the issue's "probe every saved
holistic best that carries a food sensor" has an empty set.  Ten of the sixty final members do
carry one, and they are the only nosed lumps the arm produced, so they get the probe instead.
Usage: probe_final_nosed.py <run> [n_seeds]
"""
import glob, json, os, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

run = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-22/W1b-801"
n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])


def trial(g, seed, mode):
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed)); sim.set_food_seed(seed)
    b = sim.brains[0]; ph = synthesize(g, c.synthesis)
    for i, ui in enumerate(ph.units):
        k = ui.unit.kind
        if mode == "no_food" and k == "sensor" and ui.unit.source in ("food", "agent"): b.W[:, i] = 0
        elif mode == "no_env" and k == "sensor" and ui.unit.source != "oscillator": b.W[:, i] = 0
    steps = int(round(c.duration / c.control_dt)); path = 0.0
    last = sim.center_of_mass(0)[:2].copy()
    for t in range(steps):
        sim.step()
        if t % 10 == 0:
            p = sim.center_of_mass(0)[:2]; path += float(np.linalg.norm(p - last)); last = p.copy()
    return dict(food=float(sim.food_eaten[0]), path=path, work=float(sim.work[0]) / 1000)


members = sorted(glob.glob(f"{run}/holistic/final/**/*.json", recursive=True))
seeds = range(9000, 9000 + n)
print(f"{len(members)} final holistic members in {run}; n = {n} seeds each")
print(f"{'member':28s} {'smell units (linked?)':34s} {'intact':>16s} {'no_food':>8s} {'no_env':>8s} {'work':>6s}")
worst = []
for m in members:
    g = Genotype.load(m)
    ph = synthesize(g, cfg.synthesis)
    linked = {i for s, d, _ in ph.links for i in (s, d)}
    sm = [(i, u.unit.source, u.part, i in linked) for i, u in enumerate(ph.units)
          if u.unit.kind == "sensor" and u.unit.source in ("food", "agent")]
    if not sm:
        continue
    desc = ", ".join(f"{src}@p{part}{'' if lk else ' UNLINKED'}" for _, src, part, lk in sm)
    res = {mode: np.mean([trial(g, s, mode)["food"] for s in seeds]) for mode in ("intact", "no_food", "no_env")}
    work = np.mean([trial(g, s, "intact")["work"] for s in seeds])
    se = np.std([trial(g, s, "intact")["food"] for s in seeds], ddof=1) / np.sqrt(n)
    cost = (res["intact"] - res["no_food"]) / res["intact"] * 100 if res["intact"] else 0.0
    print(f"{os.path.basename(m)[:28]:28s} {desc[:34]:34s} {res['intact']:6.2f} +- {se:4.2f} "
          f"{res['no_food']:8.2f} {res['no_env']:8.2f} {work:6.1f}   no_food costs {cost:+.0f}%")
    worst.append((cost, os.path.basename(m), any(lk for *_, lk in sm)))
print()
print(f"any smell sensor wired in at all: {sum(1 for _, _, lk in worst if lk)} of {len(worst)}")
if worst:
    c, who, _ = max(worst)
    print(f"largest no_food cost: {c:+.0f}% ({who}); threshold for a headline is +25%")
