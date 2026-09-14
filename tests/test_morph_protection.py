"""Morphological innovation protection (RBT-74): a holistic lineage whose body plan changed is
shielded from elimination for exactly k generations, evolving its controller only; a child
that differs from its parent only in weights is not."""

import json

import numpy as np

from rabbitstew.cli import main
from rabbitstew.evolution import HOLISTIC, EvolutionConfig, Experiment, Population, morph_age, protected, reproduce
from rabbitstew.genetics import MutationConfig, body_plan, body_plan_hash, mutate, mutate_brain, mutate_weights
from rabbitstew.genotype import random_genotype
from rabbitstew.simulation import SimConfig


def _holistic_population(rng, n=12, generation=0):
    members = [random_genotype(rng, name=f"h{generation}-{i}") for i in range(n)]
    pop = Population(kind=HOLISTIC, members=members, generation=generation)
    pop.fitness = [0.5] * n
    pop.distances = [2.0] * n
    pop.best, pop.runner_up = 0, 1
    return pop


def test_body_plan_ignores_the_controller_and_sees_the_body(rng):
    g = random_genotype(rng)
    weights_only = mutate_weights(g, rng, MutationConfig(weight_rate=1.0))
    assert body_plan(weights_only) == body_plan(g)
    assert body_plan_hash(weights_only) == body_plan_hash(g)
    brain_only = mutate_brain(g, rng, MutationConfig(add_unit_rate=1.0, add_link_rate=1.0, weight_rate=1.0))
    assert body_plan(brain_only) == body_plan(g)
    assert brain_only.to_dict()["nodes"] != g.to_dict()["nodes"]  # the brain did change
    body = g.copy()
    body.nodes[0].segment.dims = tuple(d * 1.5 for d in body.nodes[0].segment.dims)
    assert body_plan(body) != body_plan(g)


def test_mutate_brain_never_touches_the_body(rng):
    aggressive = MutationConfig(add_unit_rate=0.6, remove_unit_rate=0.4, add_link_rate=0.7, remove_link_rate=0.4, weight_rate=1.0)
    for _ in range(20):
        g = random_genotype(rng)
        for _ in range(10):
            g2 = mutate_brain(g, rng, aggressive)
            assert body_plan(g2) == body_plan(g)
            assert g2.validate() == []
            g = g2


def test_full_mutation_almost_always_changes_the_body(rng):
    """The premise of the mechanism on this encoding: the holistic operator leaves no controller-only route."""
    changed = sum(body_plan(mutate(g, rng)) != body_plan(g) for g in (random_genotype(rng) for _ in range(200)))
    assert changed >= 180


def test_novel_lineage_is_shielded_for_exactly_k_generations(rng):
    k = 3
    n = 12
    # Tournaments of the whole population never pick the worst member, so without protection
    # the novel lineage would be gone after one round.
    cfg = EvolutionConfig(population_size=n, elites=1, tournament_size=n, crossover_rate=0.0, morph_protection=k, sim=SimConfig(duration=0.5))
    pop = _holistic_population(rng, n)
    for m in pop.members:
        m.record["morph_age"] = k  # old bodies: unprotected
    novel = pop.members[5]
    novel.record["morph_age"] = 0  # a body that just changed
    novel_body = body_plan(novel)
    pop.fitness = [0.9] * n
    pop.fitness[5] = 0.0  # and it scores worst
    assert protected(novel, k) and not protected(pop.members[0], k)

    for round_no in range(1, k + 1):
        pop = reproduce(pop, rng, cfg)
        carriers = [m for m in pop.members if body_plan(m) == novel_body]
        assert len(carriers) == 1, f"round {round_no}: expected exactly one readaptation child"
        (child,) = carriers
        assert morph_age(child) == round_no
        assert child.record["birth"] == "readapt"
        assert child.parents and child.parents[0].startswith("h")
        assert protected(child, k) == (round_no < k)
        pop.fitness = [0.9] * n
        pop.fitness[pop.members.index(child)] = 0.0  # its controller never catches up
        pop.distances = [2.0] * n
        pop.best = pop.ranked()[0]
    # Round k + 1: the window has closed, the lineage competes on fitness and, being worst, is eliminated.
    pop = reproduce(pop, rng, cfg)
    assert not any(body_plan(m) == novel_body for m in pop.members)


def test_weight_only_mutant_is_not_shielded(rng):
    k = 3
    n = 12
    cfg = EvolutionConfig(population_size=n, elites=1, tournament_size=n, crossover_rate=0.0, morph_protection=k, sim=SimConfig(duration=0.5))
    pop = _holistic_population(rng, n)
    for m in pop.members:
        m.record["morph_age"] = k
    parent = pop.members[0]
    mutant = mutate_weights(parent, rng, MutationConfig(weight_rate=1.0))
    mutant.name = "h0-mutant"
    mutant.record = {"morph_age": morph_age(parent) + 1, "birth": "free"}  # what reproduce() stamps on a body-preserving child
    assert body_plan(mutant) == body_plan(parent)
    pop.members[5] = mutant
    pop.fitness = [0.9] * n
    pop.fitness[5] = 0.0
    assert not protected(mutant, k)
    pop = reproduce(pop, rng, cfg)
    assert not any(m.record.get("birth") == "readapt" for m in pop.members)
    assert not any(m.parents == ["h0-mutant"] for m in pop.members)


def test_reproduce_stamps_novelty_from_the_body_plan(rng):
    """Free-slot children: novel when the body differs from every parent (age 0), else parent's age + 1; elites age."""
    k = 4
    n = 10
    cfg = EvolutionConfig(population_size=n, elites=2, tournament_size=3, morph_protection=k, sim=SimConfig(duration=0.5))
    pop = _holistic_population(rng, n)
    for m in pop.members:
        m.record["morph_age"] = k
    pop.fitness = list(np.linspace(0.9, 0.1, n))
    new = reproduce(pop, rng, cfg)
    births = [m.record["birth"] for m in new.members]
    assert births[:2] == ["elite", "elite"] and all(morph_age(m) == k + 1 for m in new.members[:2])
    assert "readapt" not in births  # nothing was protected
    old_bodies = {body_plan(m) for m in pop.members}
    for m in new.members[2:]:
        assert m.record["birth"] == "free"
        assert morph_age(m) == (0 if body_plan(m) not in old_bodies else k + 1)
    # Founders carry no age and are never protected, whatever k.
    founders = Experiment(EvolutionConfig(population_size=4, generations=1, morph_protection=k, sim=SimConfig(duration=0.5))).populations[HOLISTIC].members
    assert all(morph_age(f) is None and not protected(f, k) for f in founders)


def test_unprotected_config_leaves_reproduction_untouched(rng):
    """With the window off the holistic population is bred exactly as before; only the record gains a stamp."""
    n = 10
    pop = _holistic_population(rng, n)
    pop.fitness = list(np.linspace(0.9, 0.1, n))
    off = EvolutionConfig(population_size=n, morph_protection=0, sim=SimConfig(duration=0.5))
    a = reproduce(pop, np.random.default_rng(7), off)
    b = reproduce(pop, np.random.default_rng(7), off)
    assert [m.to_dict() for m in a.members] == [m.to_dict() for m in b.members]
    assert not any(m.record.get("birth") == "readapt" for m in a.members)
    assert all(not protected(m, 0) for m in a.members)


def test_config_round_trip_and_cli_flag(tmp_path):
    cfg = EvolutionConfig(morph_protection=4)
    assert EvolutionConfig.from_dict(cfg.to_dict()).morph_protection == 4
    assert EvolutionConfig.from_dict({k: v for k, v in cfg.to_dict().items() if k != "morph_protection"}).morph_protection == 0  # old configs still load
    run = str(tmp_path / "run")
    assert main(["evolve", "--generations", "4", "--population", "6", "--elites", "1", "--champion-interval", "0", "--duration", "0.3", "--protect-morphology", "2", "--seed", "3", "--out", run]) == 0
    assert json.load(open(tmp_path / "run" / "config.json"))["morph_protection"] == 2
    recs = [json.loads(l) for l in open(tmp_path / "run" / "lineage.jsonl")]
    hol = [r for r in recs if r["population"] == "holistic"]
    assert all("body" in r and "morph_age" in r and "birth" in r for r in hol)
    # Every readaptation child carries its parent's body hash forward.
    by_name = {r["name"]: r for r in hol}
    readapts = [r for r in hol if r["birth"] == "readapt"]
    assert readapts, "a 4-generation protected run must breed readaptation children"
    assert all(by_name[r["parents"][0]]["body"] == r["body"] for r in readapts)
    assert all(r["morph_age"] == by_name[r["parents"][0]]["morph_age"] + 1 for r in readapts)
    # The conventional population is untouched by the flag: birth types are logged, no body or age.
    conv = [r for r in recs if r["population"] == "conventional"]
    assert all("body" not in r and "morph_age" not in r for r in conv)
    assert {r["birth"] for r in conv if r["generation"] > 0} == {"free", "elite"}


def test_one_readaptation_child_per_protected_body(rng):
    """A protected elite is copied and readapted, but its body takes one readaptation slot, not two."""
    k = 3
    n = 12
    cfg = EvolutionConfig(population_size=n, elites=2, tournament_size=3, morph_protection=k, sim=SimConfig(duration=0.5))
    pop = _holistic_population(rng, n)
    for m in pop.members:
        m.record["morph_age"] = k
    for i in (0, 1):
        pop.members[i].record["morph_age"] = 0  # the two best are also novel
    pop.fitness = list(np.linspace(0.9, 0.1, n))
    new = reproduce(pop, rng, cfg)
    readapts = [m for m in new.members if m.record["birth"] == "readapt"]
    assert len(readapts) == 2
    assert {body_plan(m) for m in readapts} == {body_plan(pop.members[0]), body_plan(pop.members[1])}
    elites = [m for m in new.members if m.record["birth"] == "elite"]
    assert {body_plan(m) for m in elites} == {body_plan(m) for m in readapts}
    assert all(morph_age(m) == 1 for m in elites + readapts)
    # Two carriers of one protected body (an elite copy beside its readaptation child) still yield one child.
    pop2 = new
    pop2.fitness = list(np.linspace(0.9, 0.1, n))
    pop2.distances = [2.0] * n
    pop2.best = 0
    again = reproduce(pop2, rng, cfg)
    readapts2 = [m for m in again.members if m.record["birth"] == "readapt"]
    assert len({body_plan(m) for m in readapts2}) == len(readapts2)
    assert {body_plan(m) for m in readapts2} >= {body_plan(m) for m in readapts}
