"""RBT-117: the registered holistic-against-designed comparison (runs/RBT-117/compare.py).

* Raw units are identical across faunas: a lineage fitness of either fauna is run_solo's net food score under the
  generation's one SimConfig (the premise of the raw-unit primary).
* The verdict rule: a simulated positive in either direction is detected, a centred null is NOT DECIDED, and the
  control VOIDs only when the C lines differ significantly AND by at least half the primary difference.
* End to end on tiny default-operator seed directories: it runs, prints the scope sentences, refuses a Z directory,
  and a failed RBT-113 control VOIDs it.
"""
import importlib.util
import json
import os
import subprocess
import sys

import numpy as np
import pytest

from rabbitstew.cli import build_parser, evolve_config
from rabbitstew.evolution import Experiment, generation_sim
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import run_solo

ROOT = os.path.join(os.path.dirname(__file__), "..")
FORAGE = ("--brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 --work-cost 0.03 "
          "--mass-budget 15.34 --conventional-topology --terrain random --random-start --score food").split()


def _compare():
    spec = importlib.util.spec_from_file_location("rbt117_compare", os.path.join(ROOT, "runs", "RBT-117", "compare.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run(out, line, seed, extra=(), gens=3, pop=6):
    argv = ["evolve", "--generations", str(gens), "--population", str(pop), "--seed", str(seed), "--locomotion-phase", str(gens),
            "--elites", "0", "--champion-interval", "0", "--duration", "1.5", "--truncation", "0.25", "--line", line,
            "--out", str(out)] + FORAGE + list(extra)
    args = build_parser().parse_args(argv)
    Experiment(evolve_config(args), out_dir=str(out), log=None).run()
    return args


def test_both_faunas_are_scored_in_one_raw_currency(tmp_path):
    args = _run(tmp_path / "r", "up", 3, gens=1, pop=3)
    cfg = evolve_config(args)
    h = json.load(open(tmp_path / "r" / "history.json"))["history"][0]
    sim = generation_sim(cfg, h["terrain_seed"], 0)
    rows = [json.loads(l) for l in open(tmp_path / "r" / "lineage.jsonl")]
    for kind in ("holistic", "conventional"):
        g = Genotype.load(str(tmp_path / "r" / kind / "final" / "000.json"))
        want = [r["fitness"] for r in rows if r["population"] == kind and r["name"] == g.name][0]
        got = np.mean([run_solo(g, sim, s)["score"] for s in h["start_seeds"]])
        assert round(float(got), 4) == pytest.approx(want, abs=1e-4), kind


def test_verdict_rule_detects_simulated_positives_and_holds_the_null():
    cp = _compare()
    rng = np.random.default_rng(117)
    z = np.zeros(12)
    # a simulated positive at a stated effect: mean difference +0.9 raw per seed, SD 0.8 (power.txt's SD(d) scale)
    assert cp.decide(0.9 + 0.8 * rng.standard_normal(12), z)[0] == "HOLISTIC RESPONDS MORE"
    assert cp.decide(-0.9 + 0.8 * rng.standard_normal(12), z)[0] == "DESIGNED RESPONDS MORE"
    null = 0.8 * rng.standard_normal(12)
    assert cp.decide(null - null.mean(), z)[0] == "NOT DECIDED"
    # all 12 seeds positive: the exact test's smallest p is 2/4096
    v, det = cp.decide(np.linspace(0.1, 1.2, 12), z)
    assert v == "HOLISTIC RESPONDS MORE" and det["p"] == pytest.approx(2 / 4096)


def test_the_control_voids_only_a_significant_c_difference_beyond_the_fixed_bound():
    cp = _compare()
    assert cp.C_BOUND == 0.8
    rng = np.random.default_rng(3)
    d = 0.9 + 0.3 * rng.standard_normal(12)
    e = 0.05 * rng.standard_normal(12)
    e -= e.mean()
    assert cp.decide(d, 0.85 + e)[0] == "VOID"                    # significant, just above the bound
    assert cp.decide(d, 0.75 + e)[0] == "HOLISTIC RESPONDS MORE"  # significant, just below: a harmless bias
    assert cp.decide(-3.0 + d, 0.85 + e)[0] == "VOID"             # the bound does not move with d
    noisy = 2.0 * rng.standard_normal(12)
    noisy -= noisy.mean() - 0.9                                   # beyond the bound but not significant
    assert cp.decide(d, noisy)[0] == "HOLISTIC RESPONDS MORE"


def _tiny_default_dirs(tmp_path, seeds=(7, 8), arm=None):
    """Tiny real default-operator seed directories, each under its RUNNER-assigned arm (O1: 1-3 ... O4: 10-12)."""
    dirs = []
    for s in seeds:
        a = arm or f"O{(s - 1) // 3 + 1}"
        for line in ("up", "down", "control"):
            _run(tmp_path / a / str(s) / line[0].upper(), line, s)
        dirs.append(str(tmp_path / a / str(s)))
    return dirs


def test_end_to_end_on_tiny_seed_directories(tmp_path):
    cp = _compare()
    dirs = _tiny_default_dirs(tmp_path)
    script = os.path.join(ROOT, "runs", "RBT-117", "compare.py")
    r = subprocess.run([sys.executable, script, *dirs], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "CONFIRMATORY" in r.stdout and "## VERDICT: " in r.stdout
    assert cp.SCOPE_1 in r.stdout and cp.SCOPE_2 in r.stdout and cp.SCOPE_3 in r.stdout
    assert "Founder sigma0 here: holistic" in r.stdout and "evidence against the mechanism" in r.stdout
    assert "U - C" in r.stdout and "C - D" in r.stdout and "differs from readout.txt" in r.stdout
    assert "WARNING: seeds missing from the 12 registered: [1, 2, 3, 4, 5, 6, 9, 10, 11, 12]" in r.stdout
    assert "no directional verdict is attainable" in r.stdout
    assert "food/work" in r.stdout and "NOT YET RUN" in r.stdout
    rp = subprocess.run([sys.executable, script, "--post-hoc", *dirs], capture_output=True, text=True)
    assert "EXPLORATORY" in rp.stdout and "## VERDICT: EXPLORATORY, post hoc:" in rp.stdout
    # a Z seed directory is refused
    z = tmp_path / "Z9" / "Z7"
    z.mkdir(parents=True)
    rz = subprocess.run([sys.executable, script, str(z)], capture_output=True, text=True)
    assert rz.returncode != 0 and "Z seed directory" in (rz.stdout + rz.stderr)
    # a failed RBT-113 control (the control line's config says "up") VOIDs the comparison
    cfgp = os.path.join(dirs[0], "C", "config.json")
    c = json.load(open(cfgp))
    c["line"] = "up"
    json.dump(c, open(cfgp, "w"))
    rv = subprocess.run([sys.executable, script, *dirs], capture_output=True, text=True)
    assert rv.returncode == 1 and "## VERDICT: VOID" in rv.stdout


def test_food_work_is_printed_per_fauna_from_decompose_json(tmp_path):
    dirs = _tiny_default_dirs(tmp_path)
    for d in dirs:  # synthetic decompose.json in RBT-113's format: a work-only holistic response, a food-led designed one
        g = {"founders": (0.05, 0.02), "U": (0.05, 0.0), "D": (0.05, 0.3), "C": (0.05, 0.01)}
        k = {"founders": (1.1, 0.6), "U": (1.5, 0.5), "D": (0.1, 0.9), "C": (0.9, 0.5)}
        fa = {f: {n: {"food": v[0], "work": v[1], "net": v[0] - v[1]} for n, v in t.items()} for f, t in (("holistic", g), ("conventional", k))}
        json.dump({"faunae": fa}, open(os.path.join(d, "decompose.json"), "w"))
    r = subprocess.run([sys.executable, os.path.join(ROOT, "runs", "RBT-117", "compare.py"), *dirs], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "holistic     U - D: food +0.000" in r.stdout and "food share 0%" in r.stdout
    assert "conventional U - D: food +1.400" in r.stdout


def test_the_seed_set_is_checked(tmp_path):
    """M2: a repeated seed, a seed outside 1..12, a seed under the wrong arm each exit non-zero."""
    script = os.path.join(ROOT, "runs", "RBT-117", "compare.py")
    dirs = _tiny_default_dirs(tmp_path, seeds=(7, 8))
    for bad, why in (([*dirs, dirs[0]], "repeated"),
                     ([*dirs, *_tiny_default_dirs(tmp_path, seeds=(13,), arm="O5")], "outside 1..12"),
                     ([*dirs, *_tiny_default_dirs(tmp_path / "w", seeds=(9,), arm="O2")], "RUNNER-assigned arm")):
        r = subprocess.run([sys.executable, script, *bad], capture_output=True, text=True)
        assert r.returncode != 0 and why in r.stderr, (why, r.stdout, r.stderr)


def _plant(sd, fauna, delta):
    p = os.path.join(sd, "U", "lineage.jsonl")
    rows = [json.loads(l) for l in open(p) if l.strip()]
    G = max(r["generation"] for r in rows) + 1
    for r in rows:
        if r["population"] == fauna and r["generation"] == G - 1:
            r["fitness"] += delta
    with open(p, "w") as fh:
        fh.writelines(json.dumps(r) + "\n" for r in rows)


def test_a_planted_positive_through_main_in_both_directions(tmp_path):
    """S3 (the design adversary's probe_pipeline 1a/1b): +5 raw planted in one fauna's U line at the final generation
    (never a parent generation, so RBT-113's controls still pass), 6 seeds, through compare.py main()."""
    import shutil
    script = os.path.join(ROOT, "runs", "RBT-117", "compare.py")
    hol = _tiny_default_dirs(tmp_path / "hol", seeds=(1, 2, 3, 4, 5, 6))
    shutil.copytree(tmp_path / "hol", tmp_path / "des")
    des = [d.replace(str(tmp_path / "hol"), str(tmp_path / "des")) for d in hol]
    for d in hol:
        _plant(d, "holistic", 5.0)
    for d in des:
        _plant(d, "conventional", 5.0)
    rh = subprocess.run([sys.executable, script, *hol], capture_output=True, text=True)
    rd = subprocess.run([sys.executable, script, *des], capture_output=True, text=True)
    assert rh.returncode == 0 and "## VERDICT: HOLISTIC RESPONDS MORE" in rh.stdout, rh.stdout
    assert rd.returncode == 0 and "## VERDICT: DESIGNED RESPONDS MORE" in rd.stdout, rd.stdout
    assert "seed   1 RBT-113 controls PASS" in rh.stdout
