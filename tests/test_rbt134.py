"""RBT-134: the operator switches (runs/RBT-134/DESIGN.md section 2, registered r3), off by default.

I7: each switch at its default is byte for byte the operator as it was (a digest taken on the pre-switch tree),
`link_sigma = S` equals the composition (weight_sigma S, global/effector bias sigmas at the old step) on the
designed body, and the auxiliary stream leaves the main stream untouched (the pairing the design relies on).
"""
import hashlib
import importlib.util
import json
import os
from dataclasses import replace

import numpy as np
import pytest

from rabbitstew import genetics
from rabbitstew.analysis import _run_config
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.genetics import MutationConfig, mutate, mutate_brain, mutate_controller, mutate_weights
from rabbitstew.genotype import Genotype
from rabbitstew.synthesis import synthesize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "runs", "RBT-19", "P-801")
#: sha256 of 50 lineages x 19 mutations x {mutate_controller, mutate_weights on the designed best; mutate, mutate_brain
#: on a holistic final}, seeds SeedSequence([134, i]), computed on the tree before RBT-134 (bc06cea).
GOLDEN = "a7cf53fea179bbdee98a404344d3cadad239b13639f3b9da1173849c07accce5"


@pytest.fixture(scope="module")
def setup():
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        cfg = _run_config("runs/RBT-19/P-801")
    finally:
        os.chdir(cwd)
    des = Genotype.load(os.path.join(D, "conventional", "best_gen0590.json"))
    hol = Genotype.load(os.path.join(D, "holistic", "final", "000.json"))
    return cfg, des, hol


def _digest(cfg, des, hol, mcfg, aux=False, n=50):
    h = hashlib.sha256()
    for fn, g0 in ((mutate_controller, des), (mutate_weights, des), (mutate, hol), (mutate_brain, hol)):
        for i in range(n):
            rng = np.random.default_rng(np.random.SeedSequence([134, i]))
            arng = np.random.default_rng(np.random.SeedSequence([134, i, 134])) if aux else None
            g = g0
            for _ in range(19):
                g = fn(g, rng, mcfg, aux_rng=arng) if aux else fn(g, rng, mcfg)
            h.update(json.dumps(g.to_dict(), sort_keys=True).encode())
    return h.hexdigest()


def _lineage(g, mcfg, i, fn=mutate_controller, aux=True, k=19):
    rng = np.random.default_rng(np.random.SeedSequence([134, i]))
    arng = np.random.default_rng(np.random.SeedSequence([134, i, 134])) if aux else None
    for _ in range(k):
        g = fn(g, rng, mcfg, aux_rng=arng)
    return g


def _links(g):
    return [(o, (l.src.node, l.src.index, l.dst.node, l.dst.index), l.weight) for o, b in g.brains() for l in b.links]


def _biases(g):
    return [(o, j, u.bias) for o, b in g.brains() for j, u in enumerate(b.units) if u.kind != "sensor"]


def test_defaults_are_off():
    m = MutationConfig()
    assert (m.link_sigma, m.bias_reset_rate, m.fan_rate, m.fan_sigma, m.pair_event_rate, m.pair_event_scale,
            m.pair_event_zero_bias) == (None, 0.0, 0.0, 0.0, 0.0, 1.0, False)


def test_off_is_byte_identical_to_the_pre_switch_operator(setup):
    cfg, des, hol = setup
    assert _digest(cfg, des, hol, cfg.mutation) == GOLDEN
    # explicit off values, and an auxiliary generator that every off switch must ignore
    off = replace(cfg.mutation, link_sigma=None, bias_reset_rate=0.0, fan_rate=0.0, pair_event_rate=0.0)
    assert _digest(cfg, des, hol, off, aux=True) == GOLDEN


def test_off_writes_the_old_config_json(setup):
    cfg, _, _ = setup
    d = cfg.to_dict()
    for key in ("link_sigma", "bias_reset_rate", "fan_rate", "fan_sigma", "pair_event_rate", "pair_event_scale",
                "pair_event_zero_bias"):
        assert key not in d["mutation"]
    on = replace(cfg, mutation=replace(cfg.mutation, link_sigma=4.0, bias_reset_rate=0.2))
    back = EvolutionConfig.from_dict(json.loads(json.dumps(on.to_dict())))
    assert back.mutation.link_sigma == 4.0 and back.mutation.bias_reset_rate == 0.2 and back.mutation.fan_rate == 0.0


def test_link_sigma_at_weight_sigma_is_the_default(setup):
    cfg, des, hol = setup
    assert _digest(cfg, des, hol, replace(cfg.mutation, link_sigma=cfg.mutation.weight_sigma), n=20) == \
        _digest(cfg, des, hol, cfg.mutation, n=20)


def test_link_sigma_equals_the_composition_on_the_designed_body(setup):
    """P2 (DESIGN.md 2.1): link_sigma S == weight_sigma S with the global and Effector bias steps held at 0.4,
    because a designed parent carries only global neurons and segment Effectors."""
    cfg, des, _ = setup
    ws = cfg.mutation.weight_sigma
    a = replace(cfg.mutation, link_sigma=4.0)
    b = replace(cfg.mutation, weight_sigma=4.0, global_bias_sigma=ws, effector_bias_sigma=ws)
    for i in range(30):
        assert _lineage(des, a, i, aux=False).to_dict() == _lineage(des, b, i, aux=False).to_dict()


def test_link_sigma_moves_links_not_biases(setup):
    cfg, des, hol = setup
    for g0, fn in ((des, mutate_controller), (hol, mutate)):
        base = _lineage(g0, cfg.mutation, 3, fn=fn)
        wide = _lineage(g0, replace(cfg.mutation, link_sigma=4.0), 3, fn=fn)
        assert _biases(wide) == _biases(base)
        assert [x[:2] for x in _links(wide)] == [x[:2] for x in _links(base)]
        assert _links(wide) != _links(base)


def test_bias_reset_keeps_the_main_stream(setup):
    """P3 shares P2's links and structure lineage for lineage: the coin and the redraw are on the aux stream."""
    cfg, des, hol = setup
    p2 = replace(cfg.mutation, link_sigma=4.0)
    p3 = replace(p2, bias_reset_rate=0.2)
    changed = 0
    for g0, fn in ((des, mutate_controller), (hol, mutate)):
        for i in range(10):
            a, b = _lineage(g0, p2, i, fn=fn), _lineage(g0, p3, i, fn=fn)
            assert _links(a) == _links(b)
            assert [x[:2] for x in _biases(a)] == [x[:2] for x in _biases(b)]
            changed += _biases(a) != _biases(b)
    assert changed > 0


def test_bias_reset_rate_one_redraws_every_perturbed_bias(setup):
    cfg, des, _ = setup
    m = replace(cfg.mutation, bias_reset_rate=1.0)
    rng = np.random.default_rng(1)
    child = mutate_weights(des, rng, replace(m, weight_rate=1.0), aux_rng=np.random.default_rng(2))
    # every non-sensor bias redrawn from N(0, 0.5): none keeps the parent's value plus a step
    for (o, j, b0), (_, _, b1) in zip(_biases(des), _biases(child)):
        assert b1 != b0 and abs(b1) < 5 * 0.5


def test_fan_step_scales_whole_sides_and_keeps_signs(setup):
    cfg, des, hol = setup
    m = replace(cfg.mutation, fan_rate=0.2, fan_sigma=0.75)
    moved = 0
    for g0, fn in ((des, mutate_controller), (hol, mutate)):
        for i in range(10):
            a, b = _lineage(g0, cfg.mutation, i, fn=fn), _lineage(g0, m, i, fn=fn)
            la, lb = _links(a), _links(b)
            assert [x[:2] for x in la] == [x[:2] for x in lb]  # structure: the main stream is untouched
            assert _biases(a) == _biases(b)
            moved += la != lb
    assert moved > 0
    # within one call (no later additive step) the step is a positive factor: every sign is kept
    for g0 in (des, hol):
        one = mutate_weights(g0, np.random.default_rng(9), replace(m, weight_rate=0.0, fan_rate=1.0),
                             aux_rng=np.random.default_rng(10))
        assert [np.sign(w) for *_, w in _links(one)] == [np.sign(w) for *_, w in _links(g0)]
        assert _links(one) != _links(g0)


def test_fan_step_scales_a_neurons_in_side_together():
    g = Genotype.load(os.path.join(D, "conventional", "best_gen0590.json"))
    m = MutationConfig(fan_rate=1.0, fan_sigma=1.0)

    class Fixed:  # every coin passes, side "in", factor e
        def random(self):
            return 0.0

        def normal(self, *a):
            return 1.0
    before = {id(l): l.weight for _, b in g.brains() for l in b.links}
    genetics._fan_step(g, Fixed(), m)
    gb_neurons = {genetics.UnitRef(None, k) for k, u in enumerate(g.global_brain.units) if u.kind == "neuron"}
    for _, b in g.brains():
        for l in b.links:
            if l.dst in gb_neurons:
                assert l.weight == pytest.approx(before[id(l)] * np.e)


def _structural_rate():
    spec = importlib.util.spec_from_file_location("sr91", os.path.join(ROOT, "runs", "RBT-91", "structural_rate.py"))
    sr = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        spec.loader.exec_module(sr)
    finally:
        os.chdir(cwd)
    return sr


def test_pair_event_builds_the_predicate_structure(setup):
    cfg, des, _ = setup
    sr = _structural_rate()
    genetics.PAIR_EVENT_COUNTS.update(events=0, refused=0, no_pair=0)
    m = replace(cfg.mutation, pair_event_rate=1.0, add_unit_rate=0.0, remove_unit_rate=0.0,
                add_link_rate=0.0, remove_link_rate=0.0, weight_rate=0.0, func_rate=0.0)
    child = mutate_controller(des, np.random.default_rng(5), m, aux_rng=np.random.default_rng(6))
    assert genetics.PAIR_EVENT_COUNTS == {"events": 1, "refused": 0, "no_pair": 0}
    assert len(child.global_brain.units) == len(des.global_brain.units) + 1
    new = child.global_brain.units[-1]
    assert new.kind == "neuron" and new.func == "tanh"
    ph = synthesize(child, cfg.sim.synthesis)
    k_new = [i for i, ui in enumerate(ph.units) if ui.part is None and ui.unit is new][0]
    assert k_new in sr.motif_units(ph)
    assert np.isfinite(sr.links_alone_a(ph, k_new))


def test_pair_event_c_plus_scale_and_zero_bias(setup):
    cfg, des, _ = setup
    m = replace(cfg.mutation, pair_event_rate=1.0, pair_event_scale=16.0, pair_event_zero_bias=True)
    child = mutate_controller(des, np.random.default_rng(5), m, aux_rng=np.random.default_rng(6))
    new = child.global_brain.units[-1]
    assert new.bias == 0.0
    k = genetics.UnitRef(None, len(child.global_brain.units) - 1)
    ws = [abs(l.weight) for _, b in child.brains() for l in b.links if l.src == k or l.dst == k]
    assert len(ws) == 4 and all(w > 0 for w in ws)
    one = mutate_controller(des, np.random.default_rng(5), replace(m, pair_event_scale=1.0),
                            aux_rng=np.random.default_rng(6))
    k1 = genetics.UnitRef(None, len(one.global_brain.units) - 1)
    ws1 = [abs(l.weight) for _, b in one.brains() for l in b.links if l.src == k1 or l.dst == k1]
    # the same aux draws, and the event comes after the call's weight steps, so its magnitudes are exactly x16
    assert sorted(ws) == pytest.approx(sorted(16 * w for w in ws1), rel=1e-12)


def test_pair_event_refused_when_the_global_brain_is_full(setup):
    cfg, des, _ = setup
    genetics.PAIR_EVENT_COUNTS.update(events=0, refused=0, no_pair=0)
    full = len(des.global_brain.units)
    m = replace(cfg.mutation, pair_event_rate=1.0, max_units_per_brain=full, add_unit_rate=0.0, remove_unit_rate=0.0)
    child = mutate_controller(des, np.random.default_rng(5), m, aux_rng=np.random.default_rng(6))
    assert genetics.PAIR_EVENT_COUNTS == {"events": 1, "refused": 1, "no_pair": 0}
    assert len(child.global_brain.units) == full


def test_pair_event_keeps_the_main_stream_until_it_fires(setup):
    """Up to its first event P5 is B0's twin: the event's coin is on the aux stream."""
    cfg, des, _ = setup
    m = replace(cfg.mutation, pair_event_rate=1e-12)  # never fires, but draws its coin every call
    for i in range(10):
        assert _lineage(des, m, i).to_dict() == _lineage(des, cfg.mutation, i).to_dict()


def test_holistic_mutate_ignores_the_pair_event(setup):
    cfg, _, hol = setup
    m = replace(cfg.mutation, pair_event_rate=1.0)
    for i in range(5):
        assert _lineage(hol, m, i, fn=mutate).to_dict() == _lineage(hol, cfg.mutation, i, fn=mutate).to_dict()


def test_pair_event_without_a_wheel_pair_is_counted_apart_from_a_full_brain(setup):
    """F6: "global brain full" (the registered refusal, S9) and "no wheel pair" are separate counts."""
    cfg, _, hol = setup
    genetics.PAIR_EVENT_COUNTS.update(events=0, refused=0, no_pair=0)
    m = replace(cfg.mutation, pair_event_rate=1.0)
    g = hol.copy()
    genetics._pair_event(g, np.random.default_rng(3), m)
    assert genetics._wheel_pairs(hol) is None
    assert genetics.PAIR_EVENT_COUNTS == {"events": 1, "refused": 0, "no_pair": 1}
    assert g.to_dict() == hol.to_dict()
