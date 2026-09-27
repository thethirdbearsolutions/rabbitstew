"""RBT-113: the benchmark's one command line (PREREGISTRATION.md §1, §3), in one place.

The world is paper 5's foraging world as RBT-90 part 2 / RBT-106 run it (runs/RBT-104/seed_founders.py PART2):
12 items, radius 3, eat radius 0.35, smell decay 1.0, work cost 0.03 per kJ, 15 s seasons, mass budget 15.34,
random terrain, random start, `--score food`, the `foraging` vocabulary, the designed body's controller topology
evolving.  Here every individual is scored ALONE (`--locomotion-phase` = generations, so every generation is solo)
on DRAWS start draws shared by the whole generation, and its fitness is its mean net yield (items eaten minus
0.03 x kJ of actuator work) over those draws: the trait.  Selection is imposed truncation (`--truncation P
--line up|down|control`, `--elites 0`).  One run carries one line of BOTH faunas (the Experiment always runs
both); the holistic line is primary.

An ARM is one operator at one seed: `runs/RBT-113/<OP><SEED>/` holding the three line runs U/, D/ and C/, which
share the seed and so share their founders and every generation's worlds.  OP "" is the default operator; OP "Z"
adds `--global-bias-sigma 0` (RBT-112's operator, which acts on the designed body only) and
`--holistic-stream-salt 1`, which makes the Z arm's holistic lines an independent second holistic replicate at
that seed while leaving its designed-body lines paired with the default arm's (same founders, same worlds).
"""
import os
import sys

POP = 40          # individuals per line per fauna
TRUNC = 0.25      # proportion kept as parents (k = 10 of 40)
DRAWS = 2         # solo start draws per individual per generation (shared by the generation)
GENERATIONS = 24  # generations 0..23 evaluated; 23 rounds of selection
LINES = {"U": "up", "D": "down", "C": "control"}

WORLD = ("--brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 "
         "--work-cost 0.03 --duration 15 --mass-budget 15.34 --conventional-topology --terrain random "
         "--random-start --score food").split()


def flags(line, operator="", population=POP, generations=GENERATIONS, draws=DRAWS, truncation=TRUNC, workers=2):
    """The `evolve` arguments of one arm (without --seed and --out)."""
    f = ["--population", str(population), "--generations", str(generations), "--locomotion-phase", str(generations),
         "--elites", "0", "--champion-interval", "0", "--draws", str(draws), "--workers", str(workers),
         "--truncation", str(truncation), "--line", LINES[line]] + WORLD
    if operator == "Z":
        f += ["--global-bias-sigma", "0", "--holistic-stream-salt", "1"]
    elif operator:
        raise ValueError(f"unknown operator {operator!r}")
    return f


def command(line, operator, seed, out, workers="2", **kw):
    """One line run of one arm: `line` in U D C, `operator` "" or "Z"."""
    if line not in LINES or operator not in ("", "Z"):
        raise ValueError(f"unknown line {line!r} or operator {operator!r}")
    return ["python", "-m", "rabbitstew.cli", "evolve"] + flags(line, operator, workers=int(workers), **kw) + ["--seed", str(seed), "--out", out]


def evolution_config(line="U", operator="", population=POP, generations=GENERATIONS, draws=DRAWS, seed=0, workers=1, truncation=TRUNC):
    """The EvolutionConfig the arm's command line builds (through the CLI's own parser and builder)."""
    from rabbitstew.cli import build_parser, evolve_config
    args = build_parser().parse_args(["evolve"] + flags(line, operator, population, generations, draws, truncation, workers)
                                     + ["--seed", str(seed), "--out", "/nonexistent"])
    return evolve_config(args)


if __name__ == "__main__":  # world.py LINE OP SEED OUT  ->  the NUL-separated command, for run_arm.sh (OP "-" = default)
    line, op, seed, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    sys.stdout.write("\0".join(command(line, "" if op == "-" else op, seed, out, os.environ.get("WORKERS", "2"))))
