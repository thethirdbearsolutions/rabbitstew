"""The `--fair` preset and the missing-budget guard (RBT-128; RBT-121 SYNTHESIS R9).

RBT-121 found the mass budget set by hand in 439 of 439 configs: one forgotten flag reopens the original artefact.
So a run that pits the holistic fauna against a designed body now has to say which physics it wants:

* ``--fair`` expands to the ruled fairness set (:data:`PRESET`), prints the expanded flags, and records
  ``"fairness": "fair"`` in the run's ``config.json`` beside the expanded values themselves;
* ``--unfair-i-know`` starts the run with whatever flags were given, as every run before RBT-128 did, and writes
  nothing extra, so a registered command line plus the bypass reproduces its old ``config.json`` byte for byte;
* with neither, ``evolve``, ``ecology`` and a mixed two-robot ``simulate`` bout refuse to start.

Resuming a run never passes through the guard: a ``config.json`` with no fairness key replays unchanged.  A run of
one fauna (``ecology --only-fauna``, or a bout between bodies of one kind) is exempt.  RBT-125's perception and eating
rules are world settings, not body fairness, and stay out of the preset.
"""

from __future__ import annotations

import math

#: The ruled fairness set: (argparse dest, value, the flag as printed).  Order is the order printed.
#: effector_bias_sigma is [OPEN] (not yet ruled; runs/RBT-128/DESIGN.md), and cap_on_reachable is not ruled in: both
#: are left out, so the preset leaves them unset.
PRESET = (
    ("mass_budget", 15.34, "--mass-budget 15.34"),
    ("motor_budget", 1.77, "--motor-budget 1.77"),
    ("ball_cone", math.pi / 2, f"--ball-cone {math.pi / 2!r}"),
    ("hinge_range", math.pi / 2, f"--hinge-range {math.pi / 2!r}"),
    ("settle_until_rest", 0.01, "--settle-until-rest 0.01"),
    ("settle_max", 10.0, "--settle-max 10"),
)
#: The values an unset flag holds (the parsers' defaults), so an explicit conflicting value can be told apart.
_UNSET = {"mass_budget": None, "motor_budget": 0.0, "ball_cone": 0.0, "hinge_range": 0.0, "settle_until_rest": 0.0, "settle_max": 10.0}


def expand(args) -> str:
    """Apply ``--fair`` to parsed ``args`` in place and return the fairness marker ("fair", "unfair" or "").

    Every preset flag the command line left unset takes the preset's value.  One set explicitly to a different value
    is refused (``SystemExit``): the preset is a registration, not a default to be half-overridden.  Idempotent."""
    fair, unfair = bool(getattr(args, "fair", False)), bool(getattr(args, "unfair_i_know", False))
    if fair and unfair:
        raise SystemExit("error: --fair and --unfair-i-know contradict each other (RBT-128)")
    if not fair:
        return "unfair" if unfair else ""
    if getattr(args, "_fair_expanded", False):
        return "fair"
    clash = []
    for dest, value, flag in PRESET:
        if not hasattr(args, dest):
            continue
        got = getattr(args, dest)
        if got != _UNSET[dest] and got != value:
            clash.append(f"{flag} (got {got!r})")
        setattr(args, dest, value)
    if clash:
        raise SystemExit("error: --fair sets " + ", ".join(clash) + "; drop the conflicting flag or the preset (RBT-128)")
    args._fair_expanded = True
    return "fair"


def expanded_flags(args) -> str:
    """The preset as the flags it stands for, restricted to those this command has."""
    return " ".join(flag for dest, _, flag in PRESET if hasattr(args, dest))


def announce(args) -> None:
    """Print what ``--fair`` expanded to (the run's log keeps it; ``config.json`` keeps the values)."""
    print(f"--fair expands to: {expanded_flags(args)} (RBT-128; --effector-bias-sigma is [OPEN] and left unset; cap_on_reachable is not ruled in)")


_DESIGNED_PLANS = None


def is_designed(genotype) -> bool:
    """Whether ``genotype`` has one of the designed bodies' body plans (the Pioneer's or the quadruped's), whatever its
    controller."""
    global _DESIGNED_PLANS
    from .genetics import body_plan

    if _DESIGNED_PLANS is None:
        from .fixed import pioneer_genotype, quadruped_genotype
        _DESIGNED_PLANS = {body_plan(pioneer_genotype()), body_plan(quadruped_genotype())}
    return body_plan(genotype) in _DESIGNED_PLANS


def guard(command: str, marker: str, mixed: bool) -> None:
    """Refuse to start a run that mixes the holistic and designed faunas with neither ``--fair`` nor ``--unfair-i-know``."""
    if not mixed or marker:
        if mixed and marker == "unfair":
            print(f"warning: {command} runs the holistic fauna against a designed body WITHOUT the fairness set (--unfair-i-know; RBT-128)")
        return
    raise SystemExit(
        f"error: {command} runs the holistic fauna against a designed body, but neither --fair nor --unfair-i-know is given. "
        f"--fair sets the ruled fairness set ({' '.join(f for _, _, f in PRESET)}); --unfair-i-know runs with only the "
        "flags given, as before RBT-128 (RBT-121 R9: the mass budget was set by hand in 439 of 439 configs).")
