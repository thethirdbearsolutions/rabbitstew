"""RBT-128 FIX-CHECK probe (#432 at f8f903e): the guard on --only-fauna, resume, fair.check on every single deviation,
the --shift refusal's reach, and S = 0 expanded/printed/written.

    python runs/RBT-128/design-adversary/fc_probe.py > runs/RBT-128/design-adversary/fc_probe.txt

Tiny runs only (<= 3 seasons/generations, 0.2 s bouts); nothing here is a registered run.
"""
import contextlib
import copy
import io
import json
import os
import tempfile

from rabbitstew import fair
from rabbitstew.cli import build_parser, evolve_config, main

ECO = ["ecology", "--seasons", "2", "--capacity", "4", "--group-size", "2", "--duration", "0.2"]
EVO = ["evolve", "--generations", "2", "--population", "3", "--champion-interval", "0", "--duration", "0.2"]


def run(label, argv):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = main(argv)
        res = f"STARTED rc={rc}"
    except SystemExit as e:
        res = "REFUSED: " + str(e)[:100]
    except Exception as e:
        res = f"ERROR {type(e).__name__}: {str(e)[:80]}"
    print(f"  {label:58s} {res}")
    return buf.getvalue()


def main_():
    t = tempfile.mkdtemp()
    print("## (2) the guard on --only-fauna; resume never meets it")
    for kind in ("holistic", "conventional"):
        run(f"ecology --only-fauna {kind} (bare)", ECO + ["--only-fauna", kind, "--out", os.path.join(t, f"o{kind}")])
    run("ecology --only-fauna holistic --lesion-fauna holistic (bare)", ECO + ["--only-fauna", "holistic", "--lesion-fauna", "holistic", "--food-items", "4",
                                                                         "--brain-model", "foraging", "--challenge", "foraging", "--out", os.path.join(t, "ol")])
    of = os.path.join(t, "of")
    run("ecology --only-fauna holistic --fair", ECO + ["--only-fauna", "holistic", "--fair", "--out", of])
    print(f"    check(config.json) = {fair.check(json.load(open(os.path.join(of, 'config.json'))))}")
    run("ecology --resume of it, no flag", ["ecology", "--resume", "--seasons", "3", "--out", of])
    ou = os.path.join(t, "ou")
    run("ecology --only-fauna holistic --unfair-i-know", ECO + ["--only-fauna", "holistic", "--unfair-i-know", "--out", ou])
    run("ecology --resume of the bypassed run, no flag", ["ecology", "--resume", "--seasons", "3", "--out", ou])
    print(f"    check(config.json) names {len(fair.check(json.load(open(os.path.join(ou, 'config.json')))))} deviations")
    eu = os.path.join(t, "eu")
    run("evolve --unfair-i-know", EVO + ["--unfair-i-know", "--out", eu])
    out = run("evolve --resume --fair of the bypassed run", ["evolve", "--resume", "--generations", "3", "--fair", "--out", eu])
    print(f"    note printed: {'ignored on --resume' in out}; fairness key after: {json.load(open(os.path.join(eu, 'config.json'))).get('fairness', '-')}")

    print("## (3) fair.check: one deviation at a time on a --fair evolve config, then on an ecology config")
    good = evolve_config(build_parser().parse_args(EVO[:1] + ["--fair", "--out", "/nonexistent"])).to_dict()
    print(f"  good: {fair.check(good)}")
    cases = [("fairness", None), ("fairness", "unfair"), ("sim.synthesis.mass_budget", 15.35), ("sim.synthesis.mass_budget", None),
             ("sim.world.motor_budget", 1.7605), ("sim.world.motor_budget", 0.0), ("sim.world.ball_cone", 1.5), ("sim.world.hinge_range", 3.0),
             ("sim.settle_until_rest", 0.02), ("sim.settle_until_rest", 0.0), ("sim.settle_max", 9.9), ("sim.settle_max", 20.0),
             ("mutation.effector_bias_sigma", None), ("mutation.effector_bias_sigma", 1e-6), ("mutation.effector_bias_sigma", 0.05)]
    for path, v in cases:
        d = copy.deepcopy(good)
        node = d
        *parents, last = path.split(".")
        for k in parents:
            node = node[k]
        if v is None:
            node.pop(last, None)
            vs = "(key removed)"
        else:
            node[last] = v
            vs = repr(v)
        r = fair.check(d)
        print(f"  {path} = {vs:14s} -> {len(r)} deviation(s): {r}")
    eco_run = os.path.join(t, "ef")
    run("ecology --fair (for an ecology config)", ECO + ["--fair", "--out", eco_run])
    ed = json.load(open(os.path.join(eco_run, "config.json")))
    print(f"  ecology good: {fair.check(ed)}")
    for shift in ("world.motor_budget=0", " world.motor_budget =0", "synthesis.mass_budget=40", "world.ball_cone=0", "world.hinge_range=3",
                  "--world.motor_budget=0", "food.work_cost=0.05", "terrain=flat", "world.motor_strength=2"):
        d = copy.deepcopy(ed)
        d["ecology"]["shift"], d["ecology"]["shift_at"] = shift, 1
        print(f"  ecology.shift {shift!r:28s} -> {fair.check(d)}")

    print("## (1)/S1: the --shift refusal at the CLI, alias and spelling forms")
    for shift in ("world.motor_budget=0", " world.motor_budget =0", "synthesis.mass_budget=40", "world.ball_cone=0", "world.hinge_range=0",
                  "--world.motor_budget=0", "world.motor_strength=2", "food.work_cost=0.05", "terrain=flat"):
        run(f"ecology --fair --shift {shift!r}", ECO + ["--fair", "--food-items", "4", "--shift-at", "1", "--shift", shift, "--out", os.path.join(t, "s" + str(abs(hash(shift))))])

    print("## (4) S = 0 expanded, printed and written")
    ef2 = os.path.join(t, "ef2")
    out = run("evolve --fair", EVO + ["--fair", "--out", ef2])
    print("    printed: " + [l for l in out.splitlines() if l.startswith("--fair expands")][0])
    print(f"    written: mutation.effector_bias_sigma = {json.load(open(os.path.join(ef2, 'config.json')))['mutation'].get('effector_bias_sigma', 'ABSENT')!r}")
    print(f"    ecology written: mutation.effector_bias_sigma = {ed['mutation'].get('effector_bias_sigma', 'ABSENT')!r}")
    run("evolve --fair --effector-bias-sigma 0.4", EVO + ["--fair", "--effector-bias-sigma", "0.4", "--out", os.path.join(t, "x1")])
    run("evolve --fair --effector-bias-sigma 0", EVO + ["--fair", "--effector-bias-sigma", "0", "--out", os.path.join(t, "x2")])
    s = build_parser().parse_args(["simulate", "g.json", "--fair"])
    fair.expand(s)
    print(f"    simulate --fair expands to: {fair.expanded_flags(s)} (has effector_bias_sigma arg: {hasattr(s, 'effector_bias_sigma')})")


if __name__ == "__main__":
    main_()
