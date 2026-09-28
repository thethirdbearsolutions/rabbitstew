"""RBT-128 design adversary: every CLI path I could find that starts (or continues) a mixed-fauna run.

    python runs/RBT-128/design-adversary/guard_probe.py > runs/RBT-128/design-adversary/guard_probe.txt

Each row: the command, whether it started, whether config.json exists, its fairness key and the preset's values.
Tiny runs only (<= 2 generations/seasons, 0.2 s bouts).  Nothing here is a registered run.
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

import numpy as np

from rabbitstew.cli import main
from rabbitstew.fixed import pioneer_genotype, quadruped_genotype
from rabbitstew.genotype import random_genotype

EVO = ["--generations", "1", "--population", "3", "--champion-interval", "0", "--duration", "0.2"]
ECO = ["--seasons", "2", "--capacity", "4", "--group-size", "2", "--duration", "0.2"]


def preset_of(run):
    p = os.path.join(run, "config.json")
    if not os.path.exists(p):
        return "no config.json"
    d = json.load(open(p))
    s = d["sim"]
    w = s["world"]
    return (f"fairness={d.get('fairness', '-')} mass={s['synthesis'].get('mass_budget')} motor={w.get('motor_budget', 0)} "
            f"cone={w.get('ball_cone', 0):.4g} hinge={w.get('hinge_range', 0):.4g} settle={s.get('settle_until_rest', 0)}/{s.get('settle_max')} "
            f"ebs={d['mutation'].get('effector_bias_sigma', 'unset')}")


def run(label, argv, out=None):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = main(argv)
        res = f"STARTED rc={rc}"
    except SystemExit as e:
        res = "REFUSED: " + str(e)[:90]
    except Exception as e:
        res = f"ERROR {type(e).__name__}: {str(e)[:70]}"
    warn = " [warned]" if "WITHOUT the fairness set" in buf.getvalue() else ""
    print(f"{label:62s} {res}{warn}")
    if out:
        print(f"{'':62s}   {preset_of(out)}")


def main_():
    tmp = tempfile.mkdtemp()
    h, h2, p, q = (os.path.join(tmp, n) for n in ("h.json", "h2.json", "p.json", "q.json"))
    random_genotype(np.random.default_rng(1)).save(h)
    random_genotype(np.random.default_rng(2)).save(h2)
    pioneer_genotype(np.random.default_rng(0)).save(p)
    quadruped_genotype(np.random.default_rng(0)).save(q)
    print("## simulate: genotype combinations")
    run("simulate hol pioneer", ["simulate", h, p, "--duration", "0.2"])
    run("simulate hol hol pioneer (three robots)", ["simulate", h, h2, p, "--duration", "0.2"])
    run("simulate pioneer quadruped (two designed plans)", ["simulate", p, q, "--duration", "0.2"])
    run("simulate hol (solo)", ["simulate", h, "--duration", "0.2"])
    print("## evolve")
    e = os.path.join(tmp, "e")
    run("evolve (bare)", ["evolve"] + EVO + ["--out", e], e)
    e2 = os.path.join(tmp, "e2")
    run("evolve --fixed-body <holistic file> (designed = a holistic body)", ["evolve"] + EVO + ["--fixed-body", h, "--out", e2], e2)
    ef = os.path.join(tmp, "ef")
    run("evolve --fair", ["evolve", "--fair"] + EVO + ["--generations", "2", "--out", ef], ef)
    run("evolve --resume (a --fair run, to G 3, no flag)", ["evolve", "--resume", "--generations", "3", "--out", ef], ef)
    run("evolve --resume --mass-budget 99 (a --fair run, to G 4)", ["evolve", "--resume", "--generations", "4", "--mass-budget", "99", "--out", ef], ef)
    en = os.path.join(tmp, "en")
    run("evolve --resume on a directory with no run (fresh start?)", ["evolve", "--resume", "--generations", "1", "--out", en], en)
    print("## ecology")
    c = os.path.join(tmp, "c")
    run("ecology (bare)", ["ecology"] + ECO + ["--out", c], c)
    c1 = os.path.join(tmp, "c1")
    run("ecology --only-fauna holistic (bare)", ["ecology"] + ECO + ["--only-fauna", "holistic", "--out", c1], c1)
    c2 = os.path.join(tmp, "c2")
    run("ecology --only-fauna conventional (bare)", ["ecology"] + ECO + ["--only-fauna", "conventional", "--out", c2], c2)
    c3 = os.path.join(tmp, "c3")
    run("ecology --only-fauna holistic --lesion-fauna holistic (bare)", ["ecology"] + ECO + ["--only-fauna", "holistic", "--lesion-fauna", "holistic", "--food-items", "4", "--brain-model", "foraging", "--challenge", "foraging", "--out", c3], c3)
    cf = os.path.join(tmp, "cf")
    run("ecology --fair", ["ecology", "--fair"] + ECO + ["--out", cf], cf)
    run("ecology --resume (a --fair run, to season 3, no flag)", ["ecology", "--resume", "--seasons", "3", "--out", cf], cf)
    cs = os.path.join(tmp, "cs")
    run("ecology --fair --shift-at 1 --shift world.motor_budget=0", ["ecology", "--fair"] + ECO + ["--shift-at", "1", "--shift", "world.motor_budget=0", "--out", cs], cs)
    if os.path.exists(os.path.join(cs, "history.json")):
        hist = json.load(open(os.path.join(cs, "history.json")))
        sh = {json.dumps(e.get("shift")) for e in hist["history"]}
        print(f"{'':62s}   history 'shift' fields: {sorted(sh)}")
    cs2 = os.path.join(tmp, "cs2")
    run("ecology --fair --shift-at 1 --shift synthesis.mass_budget=40", ["ecology", "--fair"] + ECO + ["--shift-at", "1", "--shift", "synthesis.mass_budget=40", "--out", cs2], cs2)
    cs3 = os.path.join(tmp, "cs3")
    run("ecology --fair --shift-at 1 --shift settle_until_rest=0", ["ecology", "--fair"] + ECO + ["--shift-at", "1", "--shift", "settle_until_rest=0", "--out", cs3], cs3)
    ci = os.path.join(tmp, "ci")
    run("ecology --from-run <a bare only-fauna run> (bare)", ["ecology"] + ECO + ["--from-run", c1, "--out", ci], ci)
    print("## flags that do not exist")
    for flag in ("--config-from", "--config"):
        run(f"evolve {flag} <a --fair run's config.json>", ["evolve", flag, os.path.join(ef, "config.json")] + EVO + ["--out", os.path.join(tmp, "x")])
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main_()
