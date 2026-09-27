"""RBT-120: the budgeted rerun's one command line.  RBT-113's O arms (runs/RBT-113/world.py, unchanged and imported)
with ONE flag added, `--motor-budget 1.77`: nothing else differs, so the designed body's lines reproduce the O arms'
byte for byte (the budget does not bind on the Pioneer, 1.7605 < 1.77; tests/test_rbt120.py), and the holistic
lines start from the O arms' founders (same streams, same names and genomes) in the same worlds.

An ARM is B1..B4, the default operator on RBT-113's seed blocks (B1: 1 2 3, B2: 4 5 6, B3: 7 8 9, B4: 10 11 12); a
SEED DIRECTORY is `runs/RBT-120/<ARM>/<SEED>` holding U/, D/, C/, named exactly as RBT-113's default-operator seed
directories so that RBT-113's readout.py and decompose.py parse them unchanged.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rbt113_world", os.path.join(HERE, "..", "RBT-113", "world.py"))
W113 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(W113)

MOTOR_BUDGET = 1.77  # the registered C: the designed Pioneer's 1.7605 rounded up (DESIGN.md §3)
BUDGET = ["--motor-budget", str(MOTOR_BUDGET)]
POP, TRUNC, DRAWS, GENERATIONS, LINES = W113.POP, W113.TRUNC, W113.DRAWS, W113.GENERATIONS, W113.LINES
WORLD = W113.WORLD + BUDGET
ARMS = {"B1": (1, 2, 3), "B2": (4, 5, 6), "B3": (7, 8, 9), "B4": (10, 11, 12)}
ARM_OF = {s: a for a, ss in ARMS.items() for s in ss}


def flags(line, operator="", **kw):
    """RBT-113's default-operator `evolve` arguments plus the budget.  Only the default operator is registered."""
    if operator:
        raise ValueError("RBT-120 registers the default operator only")
    return W113.flags(line, "", **kw) + BUDGET


def command(line, operator, seed, out, workers="2", **kw):
    if line not in LINES or operator:
        raise ValueError(f"unknown line {line!r} or operator {operator!r}")
    return ["python", "-m", "rabbitstew.cli", "evolve"] + flags(line, workers=int(workers), **kw) + ["--seed", str(seed), "--out", out]


def evolution_config(line="U", operator="", population=POP, generations=GENERATIONS, draws=DRAWS, seed=0, workers=1, truncation=TRUNC):
    """The EvolutionConfig the arm's command line builds (through the CLI's own parser and builder)."""
    from rabbitstew.cli import build_parser, evolve_config
    args = build_parser().parse_args(["evolve"] + flags(line, operator, population=population, generations=generations, draws=draws,
                                                        truncation=truncation, workers=workers) + ["--seed", str(seed), "--out", "/nonexistent"])
    return evolve_config(args)


if __name__ == "__main__":  # world.py LINE OP SEED OUT  ->  the NUL-separated command, for run_arm.sh (OP "-" = default)
    line, op, seed, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    sys.stdout.write("\0".join(command(line, "" if op == "-" else op, seed, out, os.environ.get("WORKERS", "2"))))
