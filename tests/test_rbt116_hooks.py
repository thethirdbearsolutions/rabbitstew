"""RBT-116's hooks (runs/RBT-116/PREREGISTRATION.md §3.1): each off by default and byte-identical when off, and each
doing what the registration says when on.

1. ``evolve --from-population KIND=DIR``  2. ``--save-every K``  3. ``--smell-decoy rotate|zero``
4. ``--crossover-rate R``  5. ``--draws-final K``

Every simulated test runs on fixture worlds and fixture bodies (2-10 s seasons, 4-8 members).  None runs an RBT-116
arm, W1's draw pool or an RBT-116 host.
"""
import importlib.util
import json
import os
import sys
from dataclasses import replace

import numpy as np
import pytest

from rabbitstew import evolution as evo
from rabbitstew.cli import build_parser, evolve_config
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig, Experiment
from rabbitstew.fixed import LEFT_DRIVE, RIGHT_DRIVE, pioneer_genotype
from rabbitstew.genotype import Genotype, Link, Neuron, Sensor, UnitRef
from rabbitstew.simulation import FoodConfig, SimConfig, Simulation, run_solo, spawn_layout
import rabbitstew.simulation as simmod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE116 = os.path.join(ROOT, "runs", "RBT-116")


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


steer = _load("rbt116_steer", os.path.join(HERE116, "steer.py"))
identity = _load("rbt116_hooks_identity", os.path.join(HERE116, "hooks_identity.py"))

FIXTURE = SimConfig(duration=10.0, random_start=True, start_distance_range=(1.0, 1.5),
                    food=FoodConfig(items=4, radius=2.0, decay=1.0, smell_contrast=2.5, smell_tau=1.0))
#: W1's eating block on the fixture (root + surface + #446's guard), so the decoy's guard path runs
FIXTURE_SURFACE = replace(FIXTURE, food=replace(FIXTURE.food, eat_from="root", eat_rule="surface", clear_from="root"))


def _pioneer(noses=(), throttle=0.6):
    g = pioneer_genotype(np.random.default_rng(0), hidden=0, sources=("contact",))
    for _, b in g.brains():
        for link in b.links:
            link.weight = 0.0
    for nd in noses:
        g.nodes[nd].segment.brain.units.append(Sensor("food"))
    g.nodes[LEFT_DRIVE].segment.brain.units[0].bias = +throttle
    g.nodes[RIGHT_DRIVE].segment.brain.units[0].bias = -throttle
    return g


def two_nose_steerer(w=8.0):
    """test_rbt116_steer's planted compass."""
    g = _pioneer(noses=(LEFT_DRIVE, RIGHT_DRIVE))
    gb = g.global_brain
    gb.units.append(Neuron(0.0, "tanh"))
    k = len(gb.units) - 1
    gb.links += [Link(UnitRef(LEFT_DRIVE, 1), UnitRef(None, k), -1.0), Link(UnitRef(RIGHT_DRIVE, 1), UnitRef(None, k), +1.0)]
    for nd in (LEFT_DRIVE, RIGHT_DRIVE):
        g.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, 0), w))
    assert g.is_valid(), g.validate()
    return g


def _decoy(cfg):
    return replace(cfg, food=replace(cfg.food, smell_decoy="rotate"))


def _hook_season(g, cfg, draw):
    """One solo season through the hook (run_solo's layout), recording the root's xy per tick as steer.py does."""
    cfg = replace(steer.draw_sim(cfg, draw), opponent_proxy=True)
    sim = Simulation([g], cfg, spawns=[spawn_layout(2, cfg, draw.start_seed)[0]])
    sim.set_food_seed(draw.start_seed)
    idx = sim.robots[0]
    n = int(round(cfg.duration / cfg.control_dt))
    traj = np.zeros((n + 1, 2))
    traj[0] = sim.data.xpos[idx.root_body][:2]
    for t in range(n):
        sim.step()
        traj[t + 1] = sim.data.xpos[idx.root_body][:2]
    return sim, traj


# --------------------------------------------------------------------------- #
# Byte identity when off (all five)
# --------------------------------------------------------------------------- #


def _pinned():
    rows = [l.split() for l in open(os.path.join(HERE116, "hooks_identity.txt")) if l.strip() and not l.startswith("#")]
    return {k: v for k, v in rows}


@pytest.mark.parametrize("extra", [(), tuple(identity.EXPLICIT_OFF)], ids=["unset", "explicit-off"])
def test_hooks_off_are_byte_identical_to_the_pre_hook_code(tmp_path, extra):
    """Two evolve runs (RBT-113's truncation protocol in W1's block under --fair, and the competitive default) write
    every file (config.json, history.json, lineage.jsonl, state.json, every saved genome) byte for byte as the pre-hook
    commit wrote them, and four solo seasons in W1's block end identically: hooks_identity.txt was printed by
    hooks_identity.py on that commit (2b57e39)."""
    got = identity.all_digests(str(tmp_path), extra)
    want = _pinned()
    assert set(got) == set(want)
    assert {k for k in want if got[k] != want[k]} == set()


def test_off_configs_write_no_hook_key():
    d = EvolutionConfig().to_dict()
    for k in ("from_population", "save_every", "draws_final"):
        assert k not in d
    assert d["crossover_rate"] == 0.5
    assert "smell_decoy" not in SimConfig(food=FoodConfig()).to_dict()["food"]
    on = SimConfig(food=FoodConfig(smell_decoy="rotate")).to_dict()["food"]
    assert on["smell_decoy"] == "rotate"
    assert SimConfig.from_dict(SimConfig(food=FoodConfig(smell_decoy="rotate")).to_dict()).food.smell_decoy == "rotate"


# --------------------------------------------------------------------------- #
# Hook 3: --smell-decoy rotate | zero
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("cfg", [FIXTURE, FIXTURE_SURFACE], ids=["centre", "surface+guard"])
def test_rotate_hook_is_steer_py_decoy_season_tick_for_tick(cfg):
    """The promoted decoy is the battery's: same theta, same re-draws, the same root path and food, tick for tick, as
    steer.run_season(..., "decoy"), on a steering body, under the default eating and under W1's eating block."""
    g = two_nose_steerer()
    for draw in (steer.Draw(101, 201), steer.Draw(102, 202), steer.Draw(107, 207)):
        ref = steer.run_season(g, cfg, draw, "decoy")
        sim, traj = _hook_season(g, _decoy(cfg), draw)
        assert sim.decoy_theta == ref.theta and sim.decoy_redraws == ref.redraws
        assert np.array_equal(traj, ref.traj)
        h = sim.harvest(0)
        assert (h["food"], h["work"]) == (ref.food, ref.work)


def test_rotate_changes_what_a_steerer_smells_and_nothing_else():
    g = two_nose_steerer()
    draw = steer.Draw(101, 201)
    sim_i, traj_i = _hook_season(g, FIXTURE, draw)
    sim_d, traj_d = _hook_season(g, _decoy(FIXTURE), draw)
    assert not np.array_equal(traj_i, traj_d)  # the steerer smells something else and moves differently
    a, b = Simulation([g], FIXTURE), Simulation([g], _decoy(FIXTURE))
    a.set_food_seed(201)
    b.set_food_seed(201)
    assert np.array_equal(a.food_pos, b.food_pos)  # the real items are where they were


def test_rotate_leaves_a_sensorless_body_byte_identical_and_draws_no_theta():
    g = _pioneer(noses=())  # moving, no food sensor
    for seed in (3, 4):
        assert run_solo(g, FIXTURE, seed) == run_solo(g, _decoy(FIXTURE), seed)
    sim, _ = _hook_season(g, _decoy(FIXTURE), steer.Draw(1, 3))
    assert sim.decoy_theta is None


def test_rotate_theta_is_keyed_on_the_start_seed_alone():
    """The stream is steer.py's and depends only on the start seed, so it is shared by both faunas and by U and N."""
    a, b = simmod.decoy_theta_stream(4242), steer.theta_stream(4242)
    assert [next(a) for _ in range(5)] == [next(b) for _ in range(5)]
    assert simmod.DECOY_THETA_KEY == steer.THETA_KEY and simmod.DECOY_THETA_MAX_DRAWS == steer.THETA_MAX_DRAWS
    th = []
    for g in (two_nose_steerer(4.0), two_nose_steerer(16.0)):
        sim, _ = _hook_season(g, _decoy(FIXTURE), steer.Draw(5, 777))
        th.append(sim.decoy_theta)
    assert th[0] == th[1]


def test_rotate_refuses_a_layout_it_cannot_establish_is_rotation_invariant(monkeypatch):
    class Other(Simulation):
        def _food_spot(self, avoid=None):
            return np.array([1.0, 0.0])

    g = two_nose_steerer()
    with pytest.raises(ValueError, match="rotation invariance"):
        Other([g], _decoy(FIXTURE))
    Other([g], FIXTURE)  # off: nothing is checked
    monkeypatch.setattr(Simulation, "_draw_patch_centres", lambda self: np.zeros((0, 2)))
    with pytest.raises(ValueError, match="rotation invariance"):
        Simulation([g], _decoy(FIXTURE))


def test_rotate_refuses_an_unseeded_food_state_and_a_lesion_beside_it():
    g = two_nose_steerer()
    sim = Simulation([g], _decoy(FIXTURE))
    with pytest.raises(ValueError, match="seeded layout"):
        sim.set_food_state(sim.food_state())
    with pytest.raises(ValueError, match="two different conditions"):
        Simulation([g], replace(FIXTURE, food=replace(FIXTURE.food, smell_decoy="rotate", smell_lesion=True)))
    with pytest.raises(ValueError, match="smell_decoy"):
        FoodConfig(smell_decoy="zero")


def _evolve_args(*extra):
    base = ["evolve", "--population", "4", "--generations", "2", "--locomotion-phase", "99", "--elites", "0",
            "--champion-interval", "0", "--truncation", "0.5", "--draws", "1", "--duration", "2", "--food-items", "4",
            "--food-radius", "2", "--smell-contrast", "2.5", "--smell-tau", "1.0", "--brain-model", "foraging",
            "--conventional-topology", "--random-start", "--score", "food", "--unfair-i-know", "--seed", "3"]
    return build_parser().parse_args(base + list(extra) + ["--out", "/nonexistent"])


def test_cli_smell_decoy_rotate_and_zero():
    assert evolve_config(_evolve_args("--smell-decoy", "rotate")).sim.food.smell_decoy == "rotate"
    z = evolve_config(_evolve_args("--smell-decoy", "zero")).sim.food
    assert z.smell_lesion is True and z.smell_decoy == ""
    off = evolve_config(_evolve_args()).sim.food
    assert off.smell_lesion is False and off.smell_decoy == ""


def test_decoy_and_lesion_runs_share_every_world_with_the_intact_run(tmp_path):
    """U, N and the burn-in B differ only in what the noses read: same terrain and start seeds every generation."""
    hist = {}
    for name, extra in (("U", ()), ("N", ("--smell-decoy", "rotate")), ("B", ("--smell-decoy", "zero"))):
        cfg = evolve_config(_evolve_args(*extra))
        out = str(tmp_path / name)
        Experiment(cfg, out_dir=out, log=None).run()
        hist[name] = [(e["population"], e["terrain_seed"], e["start_seeds"]) for e in json.load(open(os.path.join(out, "history.json")))["history"]]
    assert hist["U"] == hist["N"] == hist["B"]


# --------------------------------------------------------------------------- #
# Hook 4: --crossover-rate
# --------------------------------------------------------------------------- #


class _CountingRng:
    """A Generator proxy that counts .random() calls (the crossover coin is one per child)."""

    def __init__(self, rng):
        self.rng, self.calls = rng, 0

    def random(self, *a, **k):
        self.calls += 1
        return self.rng.random(*a, **k)

    def __getattr__(self, name):
        return getattr(self.rng, name)


def test_crossover_rate_zero_still_draws_the_coin_and_breeds_one_parent_children():
    cfg0 = evolve_config(_evolve_args("--crossover-rate", "0"))
    assert cfg0.crossover_rate == 0.0
    assert evolve_config(_evolve_args()).crossover_rate == 0.5
    rng = np.random.default_rng(1)
    pop = evo.initial_population(HOLISTIC, cfg0, rng)
    pop.fitness = [float(i) for i in range(len(pop.members))]
    c = _CountingRng(np.random.default_rng(9))
    child = evo.reproduce(pop, c, cfg0)
    assert all(len(m.parents) == 1 for m in child.members)
    n_coin = c.calls
    cfg1 = replace(cfg0, crossover_rate=0.5)
    c1 = _CountingRng(np.random.default_rng(9))
    evo.reproduce(pop, c1, cfg1)
    assert n_coin >= len(pop.members)  # at least one coin per child, made at R = 0 too
    with pytest.raises(ValueError):
        EvolutionConfig(crossover_rate=1.5)


# --------------------------------------------------------------------------- #
# Hooks 1 and 2: --from-population, --save-every
# --------------------------------------------------------------------------- #


def test_save_every_writes_loadable_populations_and_from_population_starts_exactly_as_saved(tmp_path):
    a = str(tmp_path / "B")
    cfg = evolve_config(_evolve_args("--generations", "3", "--save-every", "2", "--smell-decoy", "zero"))
    Experiment(cfg, out_dir=a, log=None).run()
    for kind in (HOLISTIC, CONVENTIONAL):
        assert sorted(os.listdir(os.path.join(a, kind))).count("gen0000") == 1
        assert os.path.isdir(os.path.join(a, kind, "gen0002")) and not os.path.isdir(os.path.join(a, kind, "gen0001"))
    lin = [json.loads(l) for l in open(os.path.join(a, "lineage.jsonl"))]
    for kind in (HOLISTIC, CONVENTIONAL):
        rows = open(os.path.join(a, kind, "gen0002", "fitness.txt")).read().split("\n")[:-1]
        want = [(r["name"], round(float(r["fitness"]), 4)) for r in lin if r["generation"] == 2 and r["population"] == kind]
        assert [(r.split()[0], round(float(r.split()[1]), 4)) for r in rows] == want
    src = {k: os.path.join(a, k, "gen0002") for k in (HOLISTIC, CONVENTIONAL)}
    b = str(tmp_path / "U")
    ucfg = evolve_config(_evolve_args("--generations", "2", "--from-population", f"holistic={src[HOLISTIC]}",
                                      "--from-population", f"conventional={src[CONVENTIONAL]}"))
    ex = Experiment(ucfg, out_dir=b, log=None)
    for kind in (HOLISTIC, CONVENTIONAL):
        saved = [json.load(open(os.path.join(src[kind], f))) for f in sorted(os.listdir(src[kind])) if f.endswith(".json")]
        assert [m.to_dict() for m in ex.populations[kind].members] == saved  # exactly as saved: names, genes, record
    ex.run()
    gen0 = [json.loads(l) for l in open(os.path.join(b, "lineage.jsonl")) if json.loads(l)["generation"] == 0]
    names = {k: [r["name"] for r in gen0 if r["population"] == k] for k in (HOLISTIC, CONVENTIONAL)}
    assert names[HOLISTIC] == [r["name"] for r in lin if r["generation"] == 2 and r["population"] == HOLISTIC]
    conf = json.load(open(os.path.join(b, "config.json")))
    assert conf["from_population"] == src
    assert json.load(open(os.path.join(b, "from_population.json")))[HOLISTIC]["replaced"] == []


def test_from_population_on_one_fauna_leaves_the_other_streams_untouched(tmp_path):
    a = str(tmp_path / "A")
    Experiment(evolve_config(_evolve_args()), out_dir=a, log=None).run()
    b, c = str(tmp_path / "B"), str(tmp_path / "C")
    Experiment(evolve_config(_evolve_args()), out_dir=b, log=None).run()
    Experiment(evolve_config(_evolve_args("--from-population", f"conventional={a}/conventional/final")), out_dir=c, log=None).run()
    lb = [l for l in open(os.path.join(b, "lineage.jsonl")) if '"holistic"' in l]
    lc = [l for l in open(os.path.join(c, "lineage.jsonl")) if '"holistic"' in l]
    assert lb == lc  # the holistic fauna and the worlds are the run without the hook
    hb = [(e["terrain_seed"], e["start_seeds"]) for e in json.load(open(os.path.join(b, "history.json")))["history"]]
    hc = [(e["terrain_seed"], e["start_seeds"]) for e in json.load(open(os.path.join(c, "history.json")))["history"]]
    assert hb == hc


def test_from_population_refuses_a_wrong_count_or_kind_and_replaces_an_unbuildable_member(tmp_path):
    a = str(tmp_path / "A")
    Experiment(evolve_config(_evolve_args()), out_dir=a, log=None).run()
    with pytest.raises(ValueError, match="holds 4 members"):
        Experiment(evolve_config(_evolve_args("--population", "5", "--from-population", f"holistic={a}/holistic/final")), log=None)
    with pytest.raises(ValueError, match="not designed"):
        Experiment(evolve_config(_evolve_args("--from-population", f"conventional={a}/holistic/final")), log=None)
    with pytest.raises(SystemExit):
        evolve_config(_evolve_args("--from-population", f"bodies={a}"))
    d = tmp_path / "broken"
    d.mkdir()
    for f in sorted(os.listdir(f"{a}/holistic/final")):
        (d / f).write_text(open(f"{a}/holistic/final/{f}").read())
    g = json.loads((d / "001.json").read_text())
    g["nodes"][0]["connections"].append({"child": 99})  # a connection to a node that does not exist: invalid
    (d / "001.json").write_text(json.dumps(g))
    cfg = evolve_config(_evolve_args("--from-population", f"holistic={d}"))
    pop, rep = evo.load_population(HOLISTIC, str(d), cfg)
    assert [r["slot"] for r in rep["replaced"]] == [1]
    assert pop.members[1].name.endswith("~r1") and pop.members[1].is_valid()
    again, rep2 = evo.load_population(HOLISTIC, str(d), cfg)
    assert rep2 == rep and [m.to_dict() for m in again.members] == [m.to_dict() for m in pop.members]


def test_resume_of_a_from_population_run_needs_no_source(tmp_path):
    a = str(tmp_path / "A")
    Experiment(evolve_config(_evolve_args()), out_dir=a, log=None).run()
    src = tmp_path / "src"
    os.rename(f"{a}/holistic/final", src)
    full, part = str(tmp_path / "full"), str(tmp_path / "part")
    Experiment(evolve_config(_evolve_args("--generations", "3", "--from-population", f"holistic={src}")), out_dir=full, log=None).run()
    Experiment(evolve_config(_evolve_args("--generations", "2", "--from-population", f"holistic={src}")), out_dir=part, log=None).run()
    os.rename(src, tmp_path / "gone")
    Experiment.resume(part, generations=3, log=None).run()
    assert open(f"{full}/lineage.jsonl").read() == open(f"{part}/lineage.jsonl").read()


# --------------------------------------------------------------------------- #
# Hook 5: --draws-final
# --------------------------------------------------------------------------- #


def test_draws_final_boundary_is_ranks_k_minus_5_to_k_plus_5():
    cfg = EvolutionConfig(truncation=0.25, elites=0, draws_final=16, sim=SimConfig(random_start=True))
    assert evo.boundary_ranks(40, cfg) == list(range(4, 15))  # ranks 5..15 of 40 (k = 10): 11 members
    assert evo.boundary_ranks(8, cfg) == list(range(0, 7))  # clipped at rank 1
    with pytest.raises(ValueError, match="truncation"):
        EvolutionConfig(draws_final=4, sim=SimConfig(random_start=True))
    with pytest.raises(ValueError, match="random starts"):
        EvolutionConfig(truncation=0.25, elites=0, draws_final=4)


def test_draws_final_rescores_the_boundary_on_shared_extra_draws_and_moves_no_stream(tmp_path):
    common = ("--population", "8", "--truncation", "0.25", "--draws", "2", "--generations", "2")
    off, on = str(tmp_path / "off"), str(tmp_path / "on")
    Experiment(evolve_config(_evolve_args(*common)), out_dir=off, log=None).run()
    cfg = evolve_config(_evolve_args(*common, "--draws-final", "3"))
    Experiment(cfg, out_dir=on, log=None).run()
    h_off = json.load(open(f"{off}/history.json"))["history"]
    h_on = json.load(open(f"{on}/history.json"))["history"]
    assert [(e["terrain_seed"], e["start_seeds"]) for e in h_off] == [(e["terrain_seed"], e["start_seeds"]) for e in h_on]
    g0 = [e for e in h_on if e["generation"] == 0]
    assert g0[0]["draws_final"]["seeds"] == g0[1]["draws_final"]["seeds"] == evo.draws_final_seeds(cfg, 0)  # both faunas
    assert len(g0[0]["draws_final"]["boundary"]) == 7  # k = 2 of 8: ranks 1..7
    # generation 0 is the same population in both runs: the boundary members' fitness is the mean over D + K draws
    lo = {r["name"]: r["fitness"] for r in map(json.loads, open(f"{off}/lineage.jsonl")) if r["generation"] == 0}
    ln = {r["name"]: r for r in map(json.loads, open(f"{on}/lineage.jsonl")) if r["generation"] == 0}
    for e in g0:
        p = "h0-" if e["population"] == HOLISTIC else "c0-"
        members = [n for n in lo if n.startswith(p)]
        assert set(e["draws_final"]["boundary"]) <= set(members)
        untouched = [n for n in members if n not in e["draws_final"]["boundary"]]
        assert len(untouched) == 1 and all(ln[n]["fitness"] == lo[n] for n in untouched)
    # a U line and an N line at one seed draw the same extra seeds
    n_cfg = evolve_config(_evolve_args(*common, "--draws-final", "3", "--smell-decoy", "rotate"))
    assert evo.draws_final_seeds(n_cfg, 1) == evo.draws_final_seeds(cfg, 1)


def test_draws_final_fitness_is_the_mean_over_all_draws():
    cfg = evolve_config(_evolve_args("--population", "8", "--truncation", "0.125", "--draws", "2", "--draws-final", "2",
                                     "--work-cost", "0.03"))  # the work cost makes every season's score differ
    rngs = evo.spawn_streams(cfg.seed)
    pop = evo.initial_population(HOLISTIC, cfg, rngs[HOLISTIC])
    runner = evo.BoutRunner(cfg.sim, 1)
    seeds = [11, 12]
    evo.evaluate(pop, runner, rngs[HOLISTIC], cfg, None, seeds, solo=True)
    before = list(pop.fitness)
    order = pop.ranked()
    extra = evo.draws_final_seeds(cfg, 0)
    done = evo.rescore_boundary(pop, runner, cfg, None, extra, len(seeds))
    idx = [order[r] for r in evo.boundary_ranks(8, cfg)]
    assert len(idx) == 6 and done["boundary"] == [pop.members[i].name for i in idx]  # k = 1: ranks 1..6
    varied = 0
    for i in range(8):
        if i in idx:
            allf = [run_solo(pop.members[i], cfg.sim, s)["score"] for s in seeds + extra]
            varied += np.mean(allf[2:]) != np.mean(allf[:2])  # the extra draws move this member's mean
            assert pop.fitness[i] == pytest.approx(float(np.mean(allf)), abs=1e-12)
        else:
            assert pop.fitness[i] == before[i]
    assert varied >= 2  # not a vacuous mean
    assert pop.best == pop.ranked()[0]
