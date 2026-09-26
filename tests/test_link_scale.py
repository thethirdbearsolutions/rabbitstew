"""RBT-104's --link-scale: one flag, the designed body's link-weight reach, nothing else."""
import json

import numpy as np

from rabbitstew.cli import build_parser
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.fixed import pioneer_genotype
from rabbitstew.genetics import MutationConfig, mutate, mutate_controller


def _zeroed(rng):
    g = pioneer_genotype(rng)
    for _, brain in g.brains():
        for link in brain.links:
            link.weight = 0.0
    return g


def _links(g):
    return [(l.src, l.dst, l.weight) for _, b in g.brains() for l in b.links]


def _biases(g):
    return [u.bias for _, b in g.brains() for u in b.units if u.kind != "sensor"]


def test_link_scale_multiplies_every_link_draw_and_no_bias(rng):
    """From all-zero link weights, every link weight a lineage writes -- steps, resets and new
    links -- is a draw, so at K it is exactly K times the draw at 1; biases are untouched, and
    the topology (which consumes the same random numbers) is the same."""
    parent = _zeroed(rng)
    for K in (0.5, 4.0):
        g1, gK = parent, parent
        r1, rK = np.random.default_rng(7), np.random.default_rng(7)
        for _ in range(30):
            g1 = mutate_controller(g1, r1, MutationConfig())
            gK = mutate_controller(gK, rK, MutationConfig(link_scale=K))
        l1, lK = _links(g1), _links(gK)
        assert [(s, d) for s, d, _ in l1] == [(s, d) for s, d, _ in lK]
        assert any(w != 0.0 for _, _, w in l1)
        for (_, _, w1), (_, _, wK) in zip(l1, lK):
            assert np.isclose(wK, K * w1, rtol=1e-12, atol=1e-15)
        assert _biases(g1) == _biases(gK)


def test_link_scale_default_is_the_operator_as_it_was(rng):
    parent = pioneer_genotype(rng)
    a = mutate_controller(parent, np.random.default_rng(3), MutationConfig())
    b = mutate_controller(parent, np.random.default_rng(3), MutationConfig(link_scale=1.0))
    assert json.dumps(a.to_dict()) == json.dumps(b.to_dict())


def test_holistic_operator_ignores_link_scale(rng):
    parent = pioneer_genotype(rng)
    a = mutate(parent, np.random.default_rng(5), MutationConfig())
    b = mutate(parent, np.random.default_rng(5), MutationConfig(link_scale=8.0))
    assert json.dumps(a.to_dict()) == json.dumps(b.to_dict())


def test_config_writes_link_scale_only_when_set():
    d = EvolutionConfig().to_dict()
    assert "link_scale" not in d["mutation"]  # a default run's config.json is the pre-flag one
    assert EvolutionConfig.from_dict(json.loads(json.dumps(d))).mutation.link_scale == 1.0
    d4 = EvolutionConfig(mutation=MutationConfig(link_scale=4.0)).to_dict()
    assert d4["mutation"]["link_scale"] == 4.0
    assert EvolutionConfig.from_dict(json.loads(json.dumps(d4))).mutation.link_scale == 4.0


def test_cli_flag():
    p = build_parser()
    assert p.parse_args(["ecology"]).link_scale == 1.0
    assert p.parse_args(["ecology", "--link-scale", "6"]).link_scale == 6.0


def _eco(tmp_path, name, k, seasons=2):
    from rabbitstew.ecology import Ecology, EcologyConfig
    from rabbitstew.simulation import SimConfig
    sim = SimConfig(duration=0.5)
    evo = EvolutionConfig(population_size=6, workers=1, seed=11, sim=sim, conventional_topology=True,
                          mutation=MutationConfig(link_scale=k))
    eco = EcologyConfig(seasons=seasons, capacity=6, group_size=2, initial_energy=3.0, birth_threshold=0.0,
                        birth_cost=0.0, living_cost=0.0)
    return Ecology(evo, eco, out_dir=str(tmp_path / name), log=None)


def test_ecology_scales_designed_founders_only_and_draws_nothing(tmp_path):
    """Founders at K are the default founders with every designed-body link weight times K, the
    holistic founders are identical, and every stream is where it would have been."""
    from rabbitstew.evolution import CONVENTIONAL, HOLISTIC
    e1, e4 = _eco(tmp_path, "k1", 1.0), _eco(tmp_path, "k4", 4.0)
    for a, b in zip(e1.populations[HOLISTIC], e4.populations[HOLISTIC]):
        assert json.dumps(a.to_dict()) == json.dumps(b.to_dict())
    for a, b in zip(e1.populations[CONVENTIONAL], e4.populations[CONVENTIONAL]):
        la, lb = _links(a), _links(b)
        assert [(s, d) for s, d, _ in la] == [(s, d) for s, d, _ in lb]
        assert all(wb == 4.0 * wa for (_, _, wa), (_, _, wb) in zip(la, lb))
        assert _biases(a) == _biases(b)
        assert a.record == b.record
    for name in e1.rngs:
        assert e1.rngs[name].bit_generator.state == e4.rngs[name].bit_generator.state
    assert "link_scale" not in json.load(open(tmp_path / "k1" / "config.json"))["mutation"]
    assert json.load(open(tmp_path / "k4" / "config.json"))["mutation"]["link_scale"] == 4.0
