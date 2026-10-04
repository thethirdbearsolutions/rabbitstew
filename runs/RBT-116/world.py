"""RBT-116: world point W1's block and every `evolve` command line of the design (PREREGISTRATION.md §4.1, §5.1, §8).

    python runs/RBT-116/world.py RUN UNIT OUT [--draws-option D16|D8|DF16]   # the NUL-separated command, for a lane

Nothing here runs a simulation.  ``gate/lanes.py`` emits the gate's lanes from it; the arms' lanes (after the GO) use
the same functions.

**Units.**  Unit j = 1 … 24 is one RBT-113 seed directory (§2.2): j = 1 … 12 are ``O1/1`` … ``O4/12`` and j = 13 … 24
are ``Z1/Z1`` … ``Z4/Z12``, restored from ``ckpt/rbt-113-<ARM>`` into ``runs/RBT-113/<ARM>/``.  Each unit's start is
its seed directory's **U line finals** (both faunas, 40 each).  The Z starts are only start populations: every RBT-116
run uses each fauna's default operators (§8: global-bias walk "default (not frozen)").

**Runs per unit** (§5.1), seed 116000 + j, N = 40 per fauna, solo throughout (``--locomotion-phase`` = generations),
``--truncation 0.25 --line up --elites 0 --crossover-rate 0``, W1's block and the fairness block (``--fair``),
``--save-every 12``:
* **B**, the burn-in: lesioned smell (``--smell-decoy zero``), from the RBT-113 U finals (``--from-population``);
* **U**: real smell, from B's generation-12 population;
* **N**: the rotated decoy (``--smell-decoy rotate``), from the same.

**Generation numbering (reading H1, for the ruling).**  "Generation g" is the population after g rounds of selection,
evaluated (``Population.generation`` = g; ``--save-every 12`` writes it to ``<kind>/gen<g>``).  So B runs
``--generations 13`` (generations 0 … 12 evaluated; 12 rounds of selection) and U and N run ``--generations 49``
(0 … 48; 48 rounds), and the probes at 12, 24, 36 and 48 read saved, evaluated populations.  This evaluates one
generation more per run than §9's 12 + 48 + 48 (111 against 108 generations, +2.8%).  RBT-113's convention
(``--generations 24``: 0 … 23, 23 rounds) would instead make "generation 48" the 47th round.

**Draws (G6).**  ``D16`` (16 draws), ``D8`` (8) or ``DF16`` (4 draws, ``--draws-final 16``).  B's draws are not
registered (G6 measures σ_P on B's own finals, so B runs before D is chosen: reading H2); ``B_DRAWS_OPTION`` is the
default the gate's lanes use, the registration's own fallback D = 16 (§2.4: "If neither passes, D = 16").
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

POINT = "W1"
POP = 40
TRUNC = 0.25
SEED_BASE = 116000
UNITS = tuple(range(1, 25))
GEN_B, GEN_UN = 13, 49  #: reading H1: generations 0..12 (B) and 0..48 (U, N) evaluated
SAVE_EVERY = 12
DRAWS_OPTIONS = {"D16": ["--draws", "16"], "D8": ["--draws", "8"], "DF16": ["--draws", "4", "--draws-final", "16"]}
B_DRAWS_OPTION = "D16"  #: reading H2: the burn-in's draws, before G6 can choose (the registration's fallback)
RUNS = ("B", "U", "N")

#: §4.1 W1 and §8's fairness block, every row explicit (the code's defaults differ: smell_tau 2.0, eat any/centre)
W1_WORLD = ("--brain-model foraging --conventional-topology "
            "--food-items 12 --food-patches 2 --patch-radius 0.4 --food-radius 4.0 --regrow-delay 60 "
            "--smell log --food-decay 1.5 --smell-contrast 2.5 --smell-tau 1.0 "
            "--eat-radius 0.35 --eat-from root --eat-rule surface --clear-from root "
            "--work-cost 0.03 --terrain random --random-start --duration 15 --score food --fair").split()


def unit_start(j: int, hosts_root: str = os.path.join("runs", "RBT-113")) -> str:
    """Unit j's RBT-113 seed directory's U line (holding ``<kind>/final``)."""
    if j not in UNITS:
        raise ValueError(f"unit {j} is not one of 1..24")
    op, s = ("O", j) if j <= 12 else ("Z", j - 12)
    arm = f"{op}{(s - 1) // 3 + 1}"
    seed_dir = str(s) if op == "O" else f"Z{s}"
    return os.path.join(hosts_root, arm, seed_dir, "U")


def unit_dir(j: int, base: str = os.path.join("runs", "RBT-116", "W1")) -> str:
    return os.path.join(base, f"unit{j:02d}")


def flags(run: str, j: int, draws_option: str, workers: int = 4, hosts_root: str = os.path.join("runs", "RBT-113"),
          base: str = os.path.join("runs", "RBT-116", "W1"), generations: int | None = None) -> list:
    """The ``evolve`` arguments of one run of unit j (without ``--out``)."""
    if run not in RUNS:
        raise ValueError(f"run must be one of {RUNS}")
    if draws_option not in DRAWS_OPTIONS:
        raise ValueError(f"draws option must be one of {sorted(DRAWS_OPTIONS)}")
    g = generations if generations is not None else (GEN_B if run == "B" else GEN_UN)
    if run == "B":
        src = {k: os.path.join(unit_start(j, hosts_root), k, "final") for k in ("holistic", "conventional")}
    else:
        src = {k: os.path.join(unit_dir(j, base), "B", k, f"gen{GEN_B - 1:04d}") for k in ("holistic", "conventional")}
    f = ["--population", str(POP), "--generations", str(g), "--locomotion-phase", str(g), "--elites", "0",
         "--champion-interval", "0", "--truncation", str(TRUNC), "--line", "up", "--crossover-rate", "0",
         "--save-every", str(SAVE_EVERY), "--workers", str(workers), *DRAWS_OPTIONS[draws_option], *W1_WORLD,
         "--from-population", f"holistic={src['holistic']}", "--from-population", f"conventional={src['conventional']}",
         "--seed", str(SEED_BASE + j)]
    if run == "B":
        f += ["--smell-decoy", "zero"]
    elif run == "N":
        f += ["--smell-decoy", "rotate"]
    return f


def command(run: str, j: int, out: str, draws_option: str, workers: int = 4, **kw) -> list:
    return [sys.executable if kw.pop("abs_python", False) else "python", "-m", "rabbitstew.cli", "evolve",
            *flags(run, j, draws_option, workers, **kw), "--out", out]


def evolution_config(run: str = "U", j: int = 1, draws_option: str = "D16", **kw):
    """The EvolutionConfig a run's command line builds, through the CLI's own parser and builder (no file is read:
    ``--from-population`` is only recorded until an Experiment loads it)."""
    from rabbitstew.cli import build_parser, evolve_config

    args = build_parser().parse_args(["evolve", *flags(run, j, draws_option, **kw), "--out", "/nonexistent"])
    return evolve_config(args)


def w1_sim_config():
    """W1's intact world (U's ``sim`` block): the config every gate season runs in (steer.py adds the condition)."""
    return evolution_config("U").sim


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("run", choices=RUNS)
    ap.add_argument("unit", type=int)
    ap.add_argument("out")
    ap.add_argument("--draws-option", default=None)
    a = ap.parse_args()
    opt = a.draws_option or (B_DRAWS_OPTION if a.run == "B" else None)
    if opt is None:
        raise SystemExit("U and N need --draws-option (G6's choice)")
    sys.stdout.write("\0".join(command(a.run, a.unit, a.out, opt, int(os.environ.get("WORKERS", "4")))))
