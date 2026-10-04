"""RBT-116 hooks: the byte-identity digests (PREREGISTRATION.md §3.1: "each off by default and byte-identical when off,
with digests on the pre-hook code").

    python runs/RBT-116/hooks_identity.py [OUT_DIR]      # prints one "name sha256" line per artefact

Run with ``rabbitstew`` importable from the tree under test.  Every case below uses only flags that existed before
the hooks (or a hook flag set to its off value, marked ``explicit-off``), so the same script runs on the pre-hook
commit and on the hooked one.  ``hooks_identity.txt`` holds the digests the pre-hook commit printed; the test
``tests/test_rbt116_hooks.py::test_hooks_off_are_byte_identical_to_the_pre_hook_code`` re-runs the cases on the
current tree and compares.  ``platform.json`` (machine-specific) is not digested.

The cases:
* ``evolve-trunc``: RBT-113's protocol in W1's world block (solo, truncation 0.25 up, elites 0, 2 draws, random
  terrain, random start, the contrast channel at G 2.5 / τ 1 s, root + surface eating, ``--fair``), 8 members, 3
  generations, 2 s seasons;
* ``evolve-default``: the competitive default (tournament, crossover 0.5, elites 2), 4 members, 2 generations;
* ``season-*``: one solo season of a fixed Pioneer and a fixed random holistic body in W1's block, its food, work,
  final root position and the food layout at the end, at two start seeds.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile

W1_WORLD = ("--brain-model foraging --conventional-topology --food-items 12 --food-patches 2 --patch-radius 0.4 "
            "--food-radius 4.0 --regrow-delay 60 --smell log --food-decay 1.5 --smell-contrast 2.5 --smell-tau 1.0 "
            "--eat-radius 0.35 --eat-from root --eat-rule surface --clear-from root --work-cost 0.03 --terrain random "
            "--random-start --score food --fair").split()

CASES = {
    "evolve-trunc": ["--population", "8", "--generations", "3", "--locomotion-phase", "3", "--elites", "0",
                     "--champion-interval", "0", "--draws", "2", "--truncation", "0.25", "--line", "up",
                     "--duration", "2", "--seed", "116001"] + W1_WORLD,
    "evolve-default": ["--population", "4", "--generations", "2", "--champion-interval", "1", "--duration", "2",
                       "--seed", "5", "--unfair-i-know"],
}
#: hook flags at their off values: the hooked tree must give the same bytes with these appended
EXPLICIT_OFF = ["--save-every", "0", "--draws-final", "0"]


def _digest(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run_case(name: str, out: str, extra=()) -> dict:
    """One evolve case into ``out``; the digest of every file it wrote except platform.json."""
    cmd = [sys.executable, "-m", "rabbitstew.cli", "evolve", *CASES[name], *extra, "--out", out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    got = {}
    for root, _, files in os.walk(out):
        for f in sorted(files):
            if f == "platform.json":
                continue
            p = os.path.join(root, f)
            got[f"{name}:{os.path.relpath(p, out)}"] = _digest(p)
    return got


def seasons() -> dict:
    """Solo seasons in W1's block (no hook flag exists at this level before the hooks; FoodConfig's new field is off)."""
    import numpy as np

    from rabbitstew.fixed import pioneer_genotype
    from rabbitstew.genotype import BrainVocabulary, random_genotype
    from rabbitstew.simulation import FoodConfig, SimConfig, Simulation, spawn_layout
    from dataclasses import replace

    cfg = SimConfig(duration=3.0, random_start=True, score="food", opponent_proxy=True,
                    food=FoodConfig(items=12, patches=2, patch_radius=0.4, radius=4.0, regrow_delay=60, smell="log",
                                    decay=1.5, smell_contrast=2.5, smell_tau=1.0, eat_radius=0.35, eat_from="root",
                                    eat_rule="surface", clear_from="root", work_cost=0.03))
    cfg.world.terrain = "random"
    vocab = BrainVocabulary.named("foraging")
    bodies = {"pioneer": pioneer_genotype(np.random.default_rng(3), rich=True, sources=vocab.sensor_sources),
              "holistic": random_genotype(np.random.default_rng(11), vocab=vocab)}
    out = {}
    for name, g in bodies.items():
        for seed in (101, 202):
            c = replace(cfg, world=replace(cfg.world, terrain_seed=seed + 7))
            sim = Simulation([g], c, spawns=[spawn_layout(2, c, seed)[0]])
            sim.set_food_seed(seed)
            sim.run()
            h = sim.harvest(0)
            blob = json.dumps({"food": h["food"], "work": repr(float(h["work"])),
                               "root": [repr(float(x)) for x in sim.data.xpos[sim.robots[0].root_body]],
                               "food_pos": [[repr(float(x)) for x in p] for p in sim.food_pos]}, sort_keys=True)
            out[f"season-{name}-{seed}"] = hashlib.sha256(blob.encode()).hexdigest()
    return out


def all_digests(tmp: str, extra=()) -> dict:
    got = {}
    for name in CASES:
        got.update(run_case(name, os.path.join(tmp, name), extra))
    got.update(seasons())
    return got


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    tmp = argv[0] if argv else tempfile.mkdtemp(prefix="rbt116-identity-")
    for k, v in sorted(all_digests(tmp).items()):
        print(k, v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
