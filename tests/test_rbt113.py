"""RBT-113: imposed truncation selection (`evolve --truncation P --line up|down|control`).

* The default is byte-identical: two tiny `evolve` runs (a competitive one and a solo foraging one) write the
  config.json, lineage.jsonl, history.json and state.json whose digests were recorded on the pre-hook code
  (integration head 5d69581), and --truncation 0 writes the same.
* The three lines select as specified: up breeds only from the top k, down only from the bottom k, control from
  k members drawn without regard to fitness; checked on the pool, on reproduce's children and on a run's lineage.
* RBT-112's --global-bias-sigma, now reachable from `evolve`, leaves the holistic population byte-identical and
  moves the designed body's; --holistic-stream-salt moves only the holistic side.
"""
import hashlib
import json
import os
import platform

import numpy as np
import pytest

from rabbitstew.cli import build_parser, evolve_config
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig, Experiment, Population, reproduce, truncation_pool
from rabbitstew.genotype import random_genotype

GOLDEN = {  # sha256 on the pre-hook code (5d69581), x86_64, mujoco 3.14.0, numpy 2.4.6
    "a/config.json": "dc5bc86411c8471856cfc4c818ba2db1706ff6c5be4fed8bd13c3c2b75bfc4ff",
    "a/lineage.jsonl": "bd3b97ebe05c7359ec497a736ee857695417f6774633f8a606168b501386aa05",
    "a/history.json": "6d637f1e65ebe7120a9ba8bbd7a7dff69878b6d55e7d5a2297a3cd69aaf829ef",
    "a/state.json": "36e95f40a2cbd4b4cc9cb94e4519110f69b27b44e77d0ba2cba033294d237528",
    "b/config.json": "0430ccfe7a84e898ef6f18a38752c7d6f47b0bc2aff3aaa8490d73ddc93cb618",
    "b/lineage.jsonl": "a94190bf8d987fbadf72f9d4c906c54b1e64fa24e123baade904bdb7481b2275",
    "b/history.json": "d882a8d8647fc8a5ee16eae8d44311065e1eb103d73d4d9e9dddecdb48f0417e",
    "b/state.json": "c3a509ce85b2fd8831a617cc1fa9bcf3ec2b86d999802fa09b340289e6873ca0",
}
A = "--generations 3 --population 6 --seed 11 --champion-interval 2 --duration 2".split()
FORAGE = ("--brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 --work-cost 0.03 "
          "--mass-budget 15.34 --conventional-topology --terrain random --random-start --score food").split()
B = "--generations 3 --population 6 --seed 12 --locomotion-phase 3 --duration 2".split() + FORAGE + ["--draws", "2"]


def _run(argv, out):
    args = build_parser().parse_args(["evolve"] + argv + ["--out", str(out)])
    Experiment(evolve_config(args), out_dir=str(out), log=None).run()


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _lineage(out, kind):
    return [r for r in map(json.loads, open(os.path.join(out, "lineage.jsonl"))) if r["population"] == kind]


@pytest.mark.skipif(platform.machine() != "x86_64", reason="digests recorded on x86_64 (RBT-96)")
@pytest.mark.parametrize("extra", [[], ["--truncation", "0"], ["--truncation", "0", "--line", "down"]])
def test_default_is_byte_identical_to_the_pre_hook_code(tmp_path, extra):
    _run(A + extra, tmp_path / "a")
    _run(B + extra, tmp_path / "b")
    got = {k: _sha(tmp_path / k) for k in GOLDEN}
    assert got == GOLDEN


def test_config_carries_no_truncation_key_when_off():
    d = EvolutionConfig().to_dict()
    assert "truncation" not in d and "line" not in d
    on = EvolutionConfig(truncation=0.25, line="down", elites=0).to_dict()
    assert on["truncation"] == 0.25 and on["line"] == "down"
    assert EvolutionConfig.from_dict(json.loads(json.dumps(on))).line == "down"


@pytest.mark.parametrize("bad", [dict(truncation=0.25), dict(truncation=0.25, elites=0, survival=True),
                                 dict(truncation=1.5, elites=0), dict(truncation=0.25, elites=0, line="sideways")])
def test_truncation_refuses_what_it_cannot_honour(bad):
    with pytest.raises(ValueError):
        EvolutionConfig(**bad)


def _pop(n=20, seed=3):
    rng = np.random.default_rng(seed)
    members = [random_genotype(rng, name=f"h0-{i}") for i in range(n)]
    fit = rng.permutation(n).astype(float).tolist()  # distinct fitnesses 0..n-1 in random seats
    return Population(kind=HOLISTIC, members=members, fitness=fit, distances=[0.0] * n)


def test_pool_is_the_top_the_bottom_or_a_uniform_draw():
    pop = _pop()
    fit = np.array(pop.fitness)
    for line, want in (("up", set(np.argsort(-fit)[:5])), ("down", set(np.argsort(fit)[:5]))):
        cfg = EvolutionConfig(truncation=0.25, line=line, elites=0)
        assert set(truncation_pool(pop, np.random.default_rng(0), cfg)) == {int(i) for i in want}
    cfg = EvolutionConfig(truncation=0.25, line="control", elites=0)
    seen = np.zeros(20)
    for s in range(400):
        pool = truncation_pool(pop, np.random.default_rng(s), cfg)
        assert len(pool) == len(set(pool)) == 5
        seen[pool] += 1
    # every member is a control parent about a quarter of the time, whatever its fitness
    assert seen.min() > 60 and seen.max() < 140
    assert abs(np.corrcoef(seen, fit)[0, 1]) < 0.3


@pytest.mark.parametrize("line", ["up", "down", "control"])
def test_reproduce_breeds_only_from_the_pool(line):
    pop = _pop()
    cfg = EvolutionConfig(population_size=20, truncation=0.25, line=line, elites=0, crossover_rate=0.5)
    new = reproduce(pop, np.random.default_rng(9), cfg)
    assert len(new.members) == 20
    pool = {pop.members[i].name for i in truncation_pool(pop, np.random.default_rng(9), cfg)}
    parents = [p for m in new.members for p in m.parents]
    assert parents and set(parents) <= pool
    ranks = {m.name: r for r, m in enumerate(sorted(pop.members, key=lambda m: -pop.fitness[pop.members.index(m)]))}
    pr = [ranks[p] for p in parents]
    if line == "up":
        assert max(pr) < 5
    elif line == "down":
        assert min(pr) >= 15
    assert all(m.record.get("birth") == "free" for m in new.members)  # no elite copies


def _solo_run(out, line, extra=(), gens=3, pop=8, seed=5, loco=None):
    argv = ["--generations", str(gens), "--population", str(pop), "--seed", str(seed), "--locomotion-phase", str(loco or gens),
            "--elites", "0", "--champion-interval", "0", "--duration", "1.5", "--truncation", "0.25", "--line", line] + FORAGE + list(extra)
    _run(argv, out)


@pytest.mark.parametrize("line", ["up", "down", "control"])
def test_a_run_selects_as_specified(tmp_path, line):
    _solo_run(tmp_path / line, line)
    for kind in (HOLISTIC, CONVENTIONAL):
        rows = _lineage(tmp_path / line, kind)
        for g in (0, 1):
            gen = [r for r in rows if r["generation"] == g]
            kids = [r for r in rows if r["generation"] == g + 1]
            order = sorted(range(len(gen)), key=lambda i: -gen[i]["fitness"])
            rank = {gen[i]["name"]: r for r, i in enumerate(order)}
            used = {p for r in kids for p in r["parents"]}
            assert len(used) <= 2  # k = round(0.25 x 8) = 2
            ranks = sorted(rank[p] for p in used)
            fits = sorted(r["fitness"] for r in gen)
            parent_fits = [gen[order[rank[p]]]["fitness"] for p in used]
            if line == "up":
                assert min(parent_fits) >= fits[-2] - 1e-12
            elif line == "down":
                assert max(parent_fits) <= fits[1] + 1e-12
            assert ranks  # every child has parents from the previous generation


def test_control_line_is_identical_on_founders_and_worlds(tmp_path):
    """U, D and C at one seed share founders (generation 0) and every generation's worlds: the pairing."""
    for line in ("up", "control"):
        _solo_run(tmp_path / line, line, gens=2)
    h = {line: json.load(open(tmp_path / line / "history.json"))["history"] for line in ("up", "control")}
    assert [e["start_seeds"] for e in h["up"]] == [e["start_seeds"] for e in h["control"]]
    assert [e["terrain_seed"] for e in h["up"]] == [e["terrain_seed"] for e in h["control"]]
    g0 = {line: [r for r in _lineage(tmp_path / line, HOLISTIC) if r["generation"] == 0] for line in ("up", "control")}
    assert g0["up"] == g0["control"]


def test_global_bias_sigma_leaves_the_holistic_line_alone(tmp_path):
    _solo_run(tmp_path / "u", "up", gens=4)
    _solo_run(tmp_path / "z", "up", ["--global-bias-sigma", "0"], gens=4)
    assert _lineage(tmp_path / "u", HOLISTIC) == _lineage(tmp_path / "z", HOLISTIC)
    su = json.load(open(tmp_path / "u" / "state.json"))["populations"][CONVENTIONAL]["members"]
    sz = json.load(open(tmp_path / "z" / "state.json"))["populations"][CONVENTIONAL]["members"]
    assert su != sz  # the designed body's controllers took a different mutation
    assert json.load(open(tmp_path / "z" / "config.json"))["mutation"]["global_bias_sigma"] == 0.0
    assert "global_bias_sigma" not in json.load(open(tmp_path / "u" / "config.json"))["mutation"]


def test_salt_moves_only_the_holistic_line(tmp_path):
    _solo_run(tmp_path / "s0", "down", gens=2)
    _solo_run(tmp_path / "s1", "down", ["--holistic-stream-salt", "1"], gens=2)
    assert _lineage(tmp_path / "s0", CONVENTIONAL) == _lineage(tmp_path / "s1", CONVENTIONAL)
    assert _lineage(tmp_path / "s0", HOLISTIC) != _lineage(tmp_path / "s1", HOLISTIC)


def test_resume_continues_a_truncation_run_byte_for_byte(tmp_path):
    _solo_run(tmp_path / "full", "down", gens=3)
    _solo_run(tmp_path / "cut", "down", gens=2, loco=3)  # every generation solo, as in the arms
    Experiment.resume(str(tmp_path / "cut"), generations=3, log=None).run()
    for f in ("lineage.jsonl", "state.json"):
        assert _sha(tmp_path / "cut" / f) == _sha(tmp_path / "full" / f), f


# --------------------------------------------------------------------------- the readout (runs/RBT-113/readout.py)

def _readout():
    import importlib.util
    path = os.path.join(os.path.dirname(__file__), "..", "runs", "RBT-113", "readout.py")
    spec = importlib.util.spec_from_file_location("rbt113_readout", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_readout_recovers_a_planted_realised_heritability():
    """Round trip (README: every derived metric): lines whose responses are exactly h2 x the cumulative differential."""
    ro = _readout()
    G, h2 = 10, 0.3
    S = {"U": np.full(G - 1, 1.2), "D": np.full(G - 1, -0.8), "C": np.full(G - 1, 0.05)}
    world = np.random.default_rng(0).normal(0, 1, G)  # shared by the lines: cancels in every contrast
    cum = {L: np.concatenate([[0.0], np.cumsum(S[L])]) for L in S}
    m = {L: world + h2 * cum[L] for L in S}
    st = ro.arm_stats({L: (m[L], S[L]) for L in S})
    assert st["h2"] == pytest.approx(h2) and st["h2_up"] == pytest.approx(h2) and st["h2_down"] == pytest.approx(h2)
    assert st["b_div"] == pytest.approx(h2 * 2.0) and st["b_up"] == pytest.approx(h2 * 1.15) and st["b_down"] == pytest.approx(h2 * 0.85)
    assert st["div0"] == 0.0
    # the differential the readout computes from lineage rows: offspring-weighted parents' mean minus the mean
    rows = [{"generation": 0, "name": n, "parents": [], "fitness": f} for n, f in (("a", 1.0), ("b", 2.0), ("c", 6.0))]
    rows += [{"generation": 1, "name": f"k{i}", "parents": p, "fitness": 0.0} for i, p in enumerate((["c"], ["c"], ["b", "c"]))]
    m1, S1, sd0, _ = ro.line_series(rows)
    assert S1[0] == pytest.approx((6 + 6 + 4) / 3 - 3.0)


def test_readout_sign_flip_and_t():
    ro = _readout()
    assert ro.sign_flip_p([1.0] * 6) == pytest.approx(2 / 64)
    m, lo, hi, n = ro.t_ci([1.0, 2.0, 3.0])
    assert (m, n) == (2.0, 3) and lo == pytest.approx(2 - 4.303 / np.sqrt(3)) and hi == pytest.approx(2 + 4.303 / np.sqrt(3))


def test_readout_smoke_on_a_tiny_benchmark(tmp_path):
    """A default and a Z arm at one seed, population 6, 3 generations: every control passes and the readout exits 0."""
    import subprocess
    import sys
    for op in ("", "Z"):
        for line in ("up", "down", "control"):
            extra = ["--global-bias-sigma", "0", "--holistic-stream-salt", "1"] if op else []
            _solo_run(tmp_path / f"{op}7" / line[0].upper(), line, extra, gens=3, pop=6, seed=7)
    path = os.path.join(os.path.dirname(__file__), "..", "runs", "RBT-113", "readout.py")
    r = subprocess.run([sys.executable, path, str(tmp_path / "7"), str(tmp_path / "Z7")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "arm 7      controls PASS" in r.stdout and "arm Z7     controls PASS" in r.stdout
    assert "operator pairing FAIL" not in r.stdout and "## verdicts" in r.stdout
