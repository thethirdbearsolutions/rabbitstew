"""RBT-104: the seeded founders, for the two primary arms (PREREGISTRATION.md section 3).

For RBT-90 part 2 seed SEED, draw that arm's own sixty designed-body (conventional) founders
exactly as the ecology draws them, and install RBT-87's routed motif in half of them:

  founder i, i % 4 == 0 : routed motif, sign +1   (15 founders)
  founder i, i % 4 == 2 : routed motif, sign -1   (15 founders)
  founder i odd         : bare                    (30 founders)

The motif is RBT-97's installer (`runs/RBT-97/routed_p801.py`, the one RBT-103 used): a new
global tanh unit, bias 0, fed by the two wheel noses at +sign and -sign, feeding both drive
Effectors at w.  **w = 1**, so every link has |weight| 1 and the linear gain is a = 2w = 2: the
typical geometry of a structure drift proposes at the default scale (RBT-91's 84 arrivals have
|u|, |v| of 0.02 to 4.2 and linear gains of at most 7.4 in size; `anatomy.txt`), and a
sixteenth of the null rung.  Both signs, because a compass's sign belongs to the direction a
population ends up driving, which no founder has yet.

Both primary arms load these same files with `--from-conventional`; the arm at `--link-scale K`
multiplies every designed-body founder link (the motif's included) by K at founding, which is
the flag and nothing else.  Ages are the ones the ecology drew for these founders, saved in each
file's record, so they are kept on load.

The founders are regenerated, not committed (they are bulk); `SHA256SUMS` in OUT pins them, and
`founders-digests.txt` beside this script commits each seed's digest of it, and `run_arm.sh`
refuses to launch on founders that do not match.  The script also asserts that the configuration it drew
them under equals the committed `runs/RBT-90/forage-SEED/config.json` outside seasons,
generations and workers.

Usage: seed_founders.py SEED OUT
"""
import copy
import hashlib
import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


routed = _load("rbt97_routed", os.path.join(_ROOT, "runs", "RBT-97", "routed_p801.py"))

from rabbitstew.cli import _sim_config, build_parser  # noqa: E402
from rabbitstew.ecology import Ecology, EcologyConfig  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, EvolutionConfig  # noqa: E402
from rabbitstew.genetics import MutationConfig  # noqa: E402

W = 1.0
PART2 = ("ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers 1 "
         "--brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 "
         "--work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 "
         "--duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start "
         "--score food").split()  # runs/RBT-90/part2_run.sh, verbatim
VOLATILE = {"seasons", "generations", "workers"}


def _strip(d):
    return {k: _strip(v) for k, v in d.items() if k not in VOLATILE} if isinstance(d, dict) else d


def part2_ecology(seed):
    """The ecology RBT-90 part 2 ran at this seed, built the way `cmd_ecology` builds it."""
    args = build_parser().parse_args(PART2 + ["--seed", str(seed), "--out", "/nonexistent"])
    evo = EvolutionConfig(
        population_size=args.capacity, generations=args.seasons, workers=args.workers, seed=args.seed,
        sim=_sim_config(args), mutation=MutationConfig(link_scale=args.link_scale),
        brain_model=args.brain_model, conventional_topology=args.conventional_topology,
        fixed_body=args.fixed_body, hidden_neurons=args.hidden, mirror=args.mirror,
        neighbour_links=args.neighbour_links, holistic_seed=args.holistic_seed or "",
        heading_curriculum=args.heading_curriculum)
    eco = EcologyConfig(
        seasons=args.seasons, capacity=args.capacity, group_size=args.group_size,
        living_cost=args.living_cost, birth_threshold=args.birth_threshold, birth_cost=args.birth_cost,
        initial_energy=args.initial_energy, max_age=args.max_age, stagger_ages=not args.no_stagger_ages,
        crossover_rate=args.crossover, challenge=args.challenge)
    got = _strip({**json.loads(json.dumps(evo.to_dict())), "ecology": dict(eco.__dict__)})
    ref = _strip(json.load(open(os.path.join(_ROOT, "runs", "RBT-90", f"forage-{seed}", "config.json"))))
    assert got == ref, "the founders would not be RBT-90 part 2's: config differs from the committed one"
    return Ecology(evo, eco, out_dir=None, log=None)


def seeded(seed):
    e = part2_ecology(seed)
    out = []
    for i, g in enumerate(e.populations[CONVENTIONAL]):
        rec = dict(g.record)
        if i % 2 == 0:
            g = routed.install(g, W, sign=+1.0 if i % 4 == 0 else -1.0)
            g.record = rec
        out.append(g)
    e.runner.close()
    return out


def write(seed, outdir):
    d = os.path.join(outdir, CONVENTIONAL)
    os.makedirs(d, exist_ok=True)
    sums = []
    for i, g in enumerate(seeded(seed)):
        path = os.path.join(d, f"{i:03d}.json")
        g.save(path)
        sums.append(f"{hashlib.sha256(open(path, 'rb').read()).hexdigest()}  {CONVENTIONAL}/{i:03d}.json")
    with open(os.path.join(outdir, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sums) + "\n")
    return sums


if __name__ == "__main__":
    seed, outdir = int(sys.argv[1]), sys.argv[2]
    sums = write(seed, outdir)
    print(f"seed {seed}: {len(sums)} founders written to {outdir}/{CONVENTIONAL}, 30 carrying the routed "
          f"motif at w = {W:g} (15 at +1, 15 at -1); SHA256SUMS digest "
          f"{hashlib.sha256(''.join(sums).encode()).hexdigest()[:16]}")
