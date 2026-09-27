"""RBT-112's --global-bias-sigma: the global brain's bias step, and nothing else; the stream unchanged."""
import json

import numpy as np

from rabbitstew.cli import build_parser
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.fixed import pioneer_genotype
from rabbitstew.genetics import MutationConfig, mutate, mutate_controller, mutate_weights


def _grown(seed):
    """A pioneer with a populated global brain: 40 default controller mutations."""
    g = pioneer_genotype(np.random.default_rng(seed))
    r = np.random.default_rng(1000 + seed)
    for _ in range(40):
        g = mutate_controller(g, r, MutationConfig())
    assert any(u.kind != "sensor" for u in g.global_brain.units)
    return g


def _links(g):
    return [(owner, l.src, l.dst, l.weight) for owner, b in g.brains() for l in b.links]


def _seg_biases(g):
    return [(owner, k, u.bias) for owner, b in g.brains() if owner is not None for k, u in enumerate(b.units) if u.kind != "sensor"]


def _glob_biases(g):
    return [u.bias for u in g.global_brain.units if u.kind != "sensor"]


def _mutate_weights_before_rbt112(g, rng, config, link_scale=1.0):
    """`mutate_weights` as it was at c872e80, verbatim but for the name (the default's reference)."""
    import math
    child = g.copy()
    for _, brain in child.brains():
        for link in brain.links:
            if rng.random() < config.weight_rate:
                if rng.random() < config.weight_reset_rate:
                    link.weight = float(rng.normal(0.0, 1.0 * link_scale))
                else:
                    link.weight += float(rng.normal(0.0, config.weight_sigma * link_scale))
        for u in brain.units:
            if u.kind != "sensor" and rng.random() < config.weight_rate:
                u.bias += float(rng.normal(0.0, config.weight_sigma))
            elif u.kind == "sensor" and u.source == "oscillator" and rng.random() < config.oscillator_rate:
                u.freq = float(np.clip(u.freq * math.exp(rng.normal(0, 0.2)), 0.1, 5.0))
                u.phase = float((u.phase + rng.normal(0, 0.4)) % (2 * math.pi))
    return child


def test_default_is_the_operator_as_it_was_draw_for_draw():
    """Unset, and set to weight_sigma itself, the operator writes the pre-flag child bit for bit and
    leaves the stream where the pre-flag operator left it."""
    for seed in range(8):
        g = _grown(seed)
        for K in (1.0, 8.0):
            ref_rng = np.random.default_rng(seed)
            ref = _mutate_weights_before_rbt112(g, ref_rng, MutationConfig(), link_scale=K)
            for S in (None, 0.4):
                r = np.random.default_rng(seed)
                got = mutate_weights(g, r, MutationConfig(), link_scale=K, global_bias_sigma=S)
                assert json.dumps(got.to_dict()) == json.dumps(ref.to_dict())
                assert r.bit_generator.state == ref_rng.bit_generator.state
        a = mutate_controller(g, np.random.default_rng(seed), MutationConfig())
        b = mutate_controller(g, np.random.default_rng(seed), MutationConfig(global_bias_sigma=0.4))
        assert json.dumps(a.to_dict()) == json.dumps(b.to_dict())


def test_zero_freezes_global_biases_only_and_every_other_draw_is_unchanged():
    """At S = 0, over 30-generation lineages of the controller operator at K = 1 and 8: the same
    topology, every link weight and every segment bias equal to the default lineage's, draw for
    draw, and the stream in the same place; the weight step never moves a global bias (a unit the
    operator adds is born with its own bias, drawn as before)."""
    for seed in range(6):
        for K in (1.0, 8.0):
            g0 = gd = _grown(seed)
            r0, rd = np.random.default_rng(seed), np.random.default_rng(seed)
            moved = 0
            for _ in range(30):
                w = mutate_weights(g0, np.random.default_rng(99), MutationConfig(link_scale=K), link_scale=K, global_bias_sigma=0.0)
                assert _glob_biases(w) == _glob_biases(g0)  # the weight step alone never moves a global bias
                g0 = mutate_controller(g0, r0, MutationConfig(link_scale=K, global_bias_sigma=0.0))
                gd = mutate_controller(gd, rd, MutationConfig(link_scale=K))
                moved += _glob_biases(gd) != _glob_biases(g0)
                assert _links(g0) == _links(gd)
                assert _seg_biases(g0) == _seg_biases(gd)
                assert [(u.kind, u.func) for u in g0.global_brain.units] == [(u.kind, u.func) for u in gd.global_brain.units]
                assert r0.bit_generator.state == rd.bit_generator.state
            assert moved > 0  # the default lineage's global biases did walk


def test_s_scales_the_global_step_exactly():
    """At S the global bias step is S/weight_sigma times the default step (the same standard normal)."""
    for seed in range(6):
        g = _grown(seed)
        a = mutate_weights(g, np.random.default_rng(seed), MutationConfig())
        b = mutate_weights(g, np.random.default_rng(seed), MutationConfig(), global_bias_sigma=0.1)
        steps_a = np.subtract(_glob_biases(a), _glob_biases(g))
        steps_b = np.subtract(_glob_biases(b), _glob_biases(g))
        assert np.allclose(steps_b, steps_a * 0.25, rtol=1e-9, atol=1e-12)
        assert _seg_biases(a) == _seg_biases(b) and _links(a) == _links(b)


def test_holistic_operator_ignores_it():
    g = _grown(3)
    a = mutate(g, np.random.default_rng(5), MutationConfig())
    b = mutate(g, np.random.default_rng(5), MutationConfig(global_bias_sigma=0.0))
    assert json.dumps(a.to_dict()) == json.dumps(b.to_dict())


def test_config_writes_it_only_when_set():
    d = EvolutionConfig().to_dict()
    assert "global_bias_sigma" not in d["mutation"]
    assert EvolutionConfig.from_dict(json.loads(json.dumps(d))).mutation.global_bias_sigma is None
    d0 = EvolutionConfig(mutation=MutationConfig(global_bias_sigma=0.0)).to_dict()
    assert d0["mutation"]["global_bias_sigma"] == 0.0
    assert EvolutionConfig.from_dict(json.loads(json.dumps(d0))).mutation.global_bias_sigma == 0.0


def test_cli_flags():
    p = build_parser()
    assert p.parse_args(["ecology"]).global_bias_sigma is None
    assert p.parse_args(["ecology", "--global-bias-sigma", "0"]).global_bias_sigma == 0.0
    assert p.parse_args(["ecology"]).crossover == 0.3  # crossover_rate is already exposed, as --crossover
    assert p.parse_args(["ecology", "--crossover", "0"]).crossover == 0.0


def _eco(tmp_path, name, S, seasons=3):
    from rabbitstew.ecology import Ecology, EcologyConfig
    from rabbitstew.simulation import SimConfig
    evo = EvolutionConfig(population_size=6, workers=1, seed=11, sim=SimConfig(duration=0.5), conventional_topology=True,
                          mutation=MutationConfig(global_bias_sigma=S))
    eco = EcologyConfig(seasons=seasons, capacity=6, group_size=2, initial_energy=3.0, birth_threshold=0.0,
                        birth_cost=0.0, living_cost=0.0)
    return Ecology(evo, eco, out_dir=str(tmp_path / name), log=None)


def test_ecology_founders_and_streams_untouched_and_config_records_it(tmp_path):
    from rabbitstew.evolution import CONVENTIONAL, HOLISTIC
    e1, e0 = _eco(tmp_path, "d", None), _eco(tmp_path, "z", 0.0)
    for kind in (HOLISTIC, CONVENTIONAL):
        for a, b in zip(e1.populations[kind], e0.populations[kind]):
            assert json.dumps(a.to_dict()) == json.dumps(b.to_dict())
    for name in e1.rngs:
        assert e1.rngs[name].bit_generator.state == e0.rngs[name].bit_generator.state
    assert "global_bias_sigma" not in json.load(open(tmp_path / "d" / "config.json"))["mutation"]
    assert json.load(open(tmp_path / "z" / "config.json"))["mutation"]["global_bias_sigma"] == 0.0
