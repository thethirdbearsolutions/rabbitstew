"""The `--fair` preset and the missing-budget guard (RBT-128; RBT-121 SYNTHESIS R9).

RBT-121 found the mass budget set by hand in 439 of 439 configs: one forgotten flag reopens the original artefact.
So a run that pits the holistic fauna against a designed body now has to say which physics it wants:

* ``--fair`` expands to the ruled fairness set (:data:`PRESET`), prints the expanded flags, and records
  ``"fairness": "fair"`` in the run's ``config.json`` beside the expanded values themselves;
* ``--unfair-i-know`` starts the run with whatever flags were given, as every run before RBT-128 did, and writes
  nothing extra, so a registered command line plus the bypass reproduces its old ``config.json`` byte for byte;
* with neither, every fresh ``evolve`` and ``ecology`` run (``--only-fauna`` included: its seasons are read against
  two-fauna arms) and a mixed ``simulate`` bout refuse to start.

Resuming a run never passes through the guard: a ``config.json`` with no fairness key replays unchanged.  A ``simulate``
bout between bodies of one kind, or a solo one, is exempt.  :func:`check` reads the same guarantee off a config.json.  RBT-125's perception and eating
rules are world settings, not body fairness, and stay out of the preset.
"""

from __future__ import annotations

import math

#: The ruled fairness set: (argparse dest, value, the flag as printed).  Order is the order printed.
#: effector_bias_sigma = 0 was ruled in at 02:17 (it freezes the Effector-bias walk; it does NOT bound resting throttle,
#: which selection reaches through neurons and weights and R1 prices: runs/RBT-128/DESIGN.md section 3).
#: cap_on_reachable and structural_rate_scale are not ruled in, and are left out.
PRESET = (
    ("mass_budget", 15.34, "--mass-budget 15.34"),
    ("motor_budget", 1.77, "--motor-budget 1.77"),
    ("ball_cone", math.pi / 2, f"--ball-cone {math.pi / 2!r}"),
    ("hinge_range", math.pi / 2, f"--hinge-range {math.pi / 2!r}"),
    ("settle_until_rest", 0.01, "--settle-until-rest 0.01"),
    ("settle_max", 10.0, "--settle-max 10"),
    ("effector_bias_sigma", 0.0, "--effector-bias-sigma 0"),
)
#: Where each preset value lands in an EvolutionConfig dict (config.json), for :func:`check` and the shift refusal.
CONFIG_PATH = {"mass_budget": "sim.synthesis.mass_budget", "motor_budget": "sim.world.motor_budget", "ball_cone": "sim.world.ball_cone",
               "hinge_range": "sim.world.hinge_range", "settle_until_rest": "sim.settle_until_rest", "settle_max": "sim.settle_max",
               "effector_bias_sigma": "mutation.effector_bias_sigma"}
#: The values an unset flag holds (the parsers' defaults), so an explicit conflicting value can be told apart.
_UNSET = {"mass_budget": None, "motor_budget": 0.0, "ball_cone": 0.0, "hinge_range": 0.0, "settle_until_rest": 0.0, "settle_max": 10.0,
          "effector_bias_sigma": None}


def expand(args) -> str:
    """Apply ``--fair`` to parsed ``args`` in place and return the fairness marker ("fair", "unfair" or "").

    Every preset flag the command line left unset takes the preset's value.  One set explicitly to a different value
    is refused (``SystemExit``): the preset is a registration, not a default to be half-overridden.  An explicit value
    equal to the parser's default (``--motor-budget 0``) cannot be told from unset and is overridden to the preset: the
    safe direction.  Under ``--fair`` an ecology ``--shift`` onto a preset field is refused too (a fair run must not
    turn its fairness off mid-run while its config.json still says fair).  Idempotent."""
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
    bad = shift_on_preset(getattr(args, "shift", None))
    if bad:
        raise SystemExit(f"error: --fair fixes {bad} for the whole run; --shift {args.shift!r} would change it mid-run (RBT-128)")
    args._fair_expanded = True
    return "fair"


def shift_on_preset(shift) -> str:
    """The preset field an ecology ``--shift FLAG=VALUE`` targets, or "" (resolving the ecology's CLI aliases)."""
    if not shift or "=" not in shift:
        return ""
    from .ecology import EcologyConfig
    flag = shift.split("=", 1)[0].strip()
    flag = EcologyConfig.SHIFT_ALIASES.get(flag.lstrip("-"), flag)
    targets = {path[len("sim."):] for path in CONFIG_PATH.values() if path.startswith("sim.")}
    return flag if flag in targets else ""


def check(config: dict) -> list:
    """The ways an EvolutionConfig dict (a run's ``config.json``) falls short of the fairness set: a missing
    ``"fairness": "fair"`` marker, each preset value that differs, and an ecology shift onto a preset field.  Empty
    means fair.  This is the config-level check for the places the CLI guard cannot reach (programmatic runs,
    ``runs/*/world.py``, a readout's arms); RBT-129's stages.py calls it."""
    out = []
    if config.get("fairness") != "fair":
        out.append(f"fairness marker is {config.get('fairness')!r}, not 'fair'")
    for dest, value, flag in PRESET:
        node = config
        for key in CONFIG_PATH[dest].split("."):
            node = node.get(key) if isinstance(node, dict) else None
        if node is None or (isinstance(value, float) and not (isinstance(node, (int, float)) and math.isclose(node, value, rel_tol=0, abs_tol=1e-12))):
            out.append(f"{CONFIG_PATH[dest]} is {node!r}, the preset's is {value!r} ({flag})")
    shift = (config.get("ecology") or {}).get("shift")
    if shift_on_preset(shift):
        out.append(f"ecology.shift {shift!r} changes a preset field mid-run")
    return out


def expanded_flags(args) -> str:
    """The preset as the flags it stands for, restricted to those this command has."""
    return " ".join(flag for dest, _, flag in PRESET if hasattr(args, dest))


def announce(args) -> None:
    """Print what ``--fair`` expanded to (the run's log keeps it; ``config.json`` keeps the values)."""
    print(f"--fair expands to: {expanded_flags(args)} (RBT-128; cap_on_reachable and structural_rate_scale are not ruled in)")


def note_resume(args) -> None:
    """A fairness flag given with --resume is ignored (the run's config.json decides); say so once."""
    if getattr(args, "fair", False) or getattr(args, "unfair_i_know", False):
        print("note: --fair / --unfair-i-know are ignored on --resume: the run continues under its own config.json (RBT-128)")


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
        "flags given, as before RBT-128 (RBT-121 R9: the mass budget was set by hand in 439 of 439 configs). Giving the "
        "same values by hand is not enough: add --fair (accepted when they match) so the run is marked fair.")
