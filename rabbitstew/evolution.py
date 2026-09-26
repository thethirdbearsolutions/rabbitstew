"""The long-term experiment: holistic versus conventional evolution.

Two populations evolve independently under the same competitive task.  The
*holistic* population starts from random morphologies and evolves bodies and
brains together; the *conventional* population shares the fixed
Pioneer-style body and evolves only its network weights.

Within a population every generation uses an all-versus-best, two-at-a-time
competition: each member is simulated against the previous generation's
best individual (the best itself meets the runner-up), and its fitness is
the ratio-of-distances score from that bout.  At periodic intervals the top
members of each population meet in *champion bouts* which do not affect
evolution and exist only to measure the relative progress of the two
populations.  ``champion_mode="best"`` is the paper's best-versus-best
measurement; ``"roundrobin"`` pits every champion of one population against
every champion of the other, from both starting sides.
"""

from __future__ import annotations

import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass, field
from typing import Callable, Optional

import numpy as np

from .fixed import is_same_morphology, pioneer_genotype, quadruped_genotype, randomize_weights
from .genetics import MutationConfig, body_plan, body_plan_hash, body_signature, crossover, crossover_controller, crossover_weights, mutate, mutate_brain, mutate_controller, mutate_weights
from .genotype import BrainVocabulary, Genotype, JointType, random_genotype
from .simulation import BoutResult, SimConfig, run_bout, run_solo, run_group
from .synthesis import synthesize

HOLISTIC = "holistic"
CONVENTIONAL = "conventional"
TERRAIN = "terrain"
STREAMS = (HOLISTIC, CONVENTIONAL, TERRAIN)  #: spawn order; appending keeps the existing streams where they are


@dataclass
class EvolutionConfig:
    population_size: int = 20
    generations: int = 30
    elites: int = 2  #: best individuals copied unchanged into the next generation
    tournament_size: int = 3
    crossover_rate: float = 0.5
    champion_interval: int = 5  #: generations between inter-population champion bouts (0 disables)
    champions: int = 3  #: top-k of each population that take part
    champion_mode: str = "best"  #: "best" (paper), "roundrobin" (top-k each, both sides) or "all" (every member vs every member, both sides)
    random_sides: bool = True  #: randomise which side of the arena each competitor starts on
    workers: int = 1  #: processes used for bouts (1 = in-process)
    seed: int = 0
    sim: SimConfig = field(default_factory=SimConfig)
    mutation: MutationConfig = field(default_factory=MutationConfig)
    hidden_neurons: int = 6  #: hidden neurons in the fixed body's controller
    brain_model: str = "paper"  #: "paper" (contact + direction sensors, tanh, torque) or "rich"
    conventional_topology: bool = False  #: let the fixed body's controller topology evolve too (body-only comparison)
    opponents: int = 1  #: opponents per member per generation (the previous generation's top ranks); 1 = all-versus-best
    draws: int = 1  #: start-layout draws per pairing (each draw is a fresh start seed shared by every bout of the generation)
    locomotion_phase: int = 0  #: generations of solo (non-competitive) fitness before competition begins
    fixed_body: str = "pioneer"  #: the conventional population's body: "pioneer", "quadruped", or a path to a genotype file (its body with fresh random weights)
    holistic_seed: str = ""  #: path to a genotype the holistic population starts from (its body and brain, fully evolvable) instead of random genotypes
    heading_curriculum: int = 0  #: generations over which the random-start heading offset widens from 0 to its full range (0 = full range from the start)
    survival: bool = False  #: (mu+lambda): parents persist, are re-evaluated every generation, and compete with children on running-mean fitness
    selection: str = "tournament"  #: parent selection: "tournament" on scalar fitness, or "lexicase" over the score vector
    mirror: bool = False  #: allow mirrored (reflected) connections in the holistic encoding
    neighbour_links: bool = False  #: local brains may read neighbouring nodes' units (Sims' encoding)
    archive: bool = False  #: keep a descriptor archive of the best holistic body per structural cell and breed from it too
    archive_parents: float = 0.3  #: share of parents drawn from the archive when it is on
    morph_protection: int = 0  #: morphological innovation protection window k (generations); 0 = off.  See :func:`protected`.
    holistic_stream_salt: int = 0  #: re-spawn only the holistic population's RNG stream (0 = the usual stream); an A/A pair differs in this alone (RBT-96).  See :func:`spawn_streams`.

    def __post_init__(self):
        self.mutation.vocab = BrainVocabulary.named(self.brain_model)
        if self.mirror:
            self.mutation.vocab.mirror_rate = 0.3
        if self.neighbour_links:
            self.mutation.vocab.neighbour_links = True

    def to_dict(self) -> dict:
        d = asdict(self)
        d["mutation"]["vocab"] = self.mutation.vocab.to_dict()
        if d["mutation"]["link_scale"] == 1.0:
            # RBT-104: written only when set, so a run at the default writes the config.json it
            # wrote before the field existed, byte for byte (from_dict fills in the default)
            del d["mutation"]["link_scale"]
        if not d["holistic_stream_salt"]:
            del d["holistic_stream_salt"]  # salt 0 writes the pre-salt config byte for byte (RBT-96)
        return d

    @staticmethod
    def from_dict(d: dict) -> "EvolutionConfig":
        d = dict(d)
        sim = SimConfig.from_dict(d.pop("sim"))
        md = dict(d.pop("mutation", {}))
        md.pop("vocab", None)
        cfg = EvolutionConfig(sim=sim, mutation=MutationConfig(**md), **d)
        return cfg


@dataclass
class Population:
    kind: str
    members: list  #: list[Genotype]
    fitness: list = field(default_factory=list)
    distances: list = field(default_factory=list)
    best: Optional[int] = None  #: index of the best member (from the last evaluation)
    runner_up: Optional[int] = None
    generation: int = 0
    top: list = field(default_factory=list)  #: indices of the top-ranked members from the last evaluation (opponents for the next)
    archive: dict = field(default_factory=dict)  #: descriptor cell -> (fitness, genotype dict); the best body seen per structural cell
    vectors: list = field(default_factory=list)  #: mean score vector per member from the last evaluation

    def ranked(self) -> list[int]:
        return sorted(range(len(self.members)), key=lambda i: -self.fitness[i])

    def champions(self, k: int) -> list[Genotype]:
        return [self.members[i] for i in self.ranked()[:k]]


# --------------------------------------------------------------------------- #
# Bouts (possibly in worker processes)
# --------------------------------------------------------------------------- #


def _bout_task(args) -> dict:
    a, b, sim, swap, start_seed = args
    if b is None:  # solo (locomotion phase)
        r = run_solo(Genotype.from_dict(a), sim, start_seed)
        return {"distances": [r["distance"]], "fitness": [r["score"]], "exploded": [r["exploded"]], "time_at_target": [r["time_at_target"]], "waypoints": [r.get("waypoints", 0)], "solo": True, "start_seed": start_seed, "vectors": [r["vector"]]}
    res = run_bout(Genotype.from_dict(a), Genotype.from_dict(b), sim, swap=swap, start_seed=start_seed)
    return {"distances": res.distances, "fitness": res.fitness, "exploded": res.exploded, "time_at_target": res.time_at_target, "start_seed": start_seed, "vectors": res.vectors}


def _group_task(args) -> list:
    genotypes, sim, start_seed = args
    return run_group([Genotype.from_dict(g) for g in genotypes], sim, start_seed)


def _persistent_group_task(args):
    """One group in a persistent arena: the food it found, and the food state it leaves behind."""
    genotypes, sim, start_seed, food_state, food_seed = args
    return run_group([Genotype.from_dict(g) for g in genotypes], sim, start_seed, food_state=food_state, return_state=True, food_seed=food_seed)


class BoutRunner:
    """Runs batches of bouts, in-process or in a process pool."""

    def __init__(self, sim: SimConfig, workers: int = 1):
        self.sim = sim
        self.workers = max(1, workers)
        self._pool = ProcessPoolExecutor(self.workers) if self.workers > 1 else None

    def run(self, pairs: list, sim: Optional[SimConfig] = None) -> list[dict]:
        """``pairs`` are ``(a, b, swap)`` or ``(a, b, swap, start_seed)``; ``b`` may be None for a solo run."""
        sim = self.sim if sim is None else sim
        tasks = [(pr[0].to_dict(), None if pr[1] is None else pr[1].to_dict(), sim, pr[2], pr[3] if len(pr) > 3 else None) for pr in pairs]
        if self._pool is None:
            return [_bout_task(t) for t in tasks]
        return list(self._pool.map(_bout_task, tasks, chunksize=1))

    def run_groups(self, groups: list, sim: Optional[SimConfig] = None) -> list[list[dict]]:
        """``groups`` are ``(genotypes, start_seed)``: each group shares one arena (the foraging world)."""
        sim = self.sim if sim is None else sim
        tasks = [([g.to_dict() for g in gs], sim, seed) for gs, seed in groups]
        if self._pool is None:
            return [_group_task(t) for t in tasks]
        return list(self._pool.map(_group_task, tasks, chunksize=1))

    def run_persistent_groups(self, groups: list, sim: Optional[SimConfig] = None) -> list:
        """``groups`` are ``(genotypes, start_seed, food_state, food_seed)``: each group takes the
        arena's food as the season before left it and hands back what it leaves.  Returns
        ``(results, food_state)`` per group."""
        sim = self.sim if sim is None else sim
        tasks = [([g.to_dict() for g in gs], sim, seed, state, fseed) for gs, seed, state, fseed in groups]
        if self._pool is None:
            return [_persistent_group_task(t) for t in tasks]
        return list(self._pool.map(_persistent_group_task, tasks, chunksize=1))

    def close(self) -> None:
        if self._pool is not None:
            self._pool.shutdown()
            self._pool = None


# --------------------------------------------------------------------------- #
# Population initialisation
# --------------------------------------------------------------------------- #


def initial_population(kind: str, config: EvolutionConfig, rng: np.random.Generator) -> Population:
    vocab = config.mutation.vocab
    if kind == HOLISTIC:
        if config.holistic_seed:
            template = Genotype.load(config.holistic_seed)
            members = []
            for i in range(config.population_size):
                g = template.copy()
                g.name = f"h0-{i}"
                g.parents = []
                randomize_weights(g, rng, 1.0)
                members.append(g)
        else:
            members = [random_genotype(rng, name=f"h0-{i}", vocab=vocab) for i in range(config.population_size)]
    elif kind == CONVENTIONAL:
        if config.fixed_body == "quadruped":
            members = [quadruped_genotype(rng, hidden=config.hidden_neurons, name=f"c0-{i}", rich=config.brain_model in ("rich", "foraging"), sources=vocab.sensor_sources if config.brain_model == "foraging" else None) for i in range(config.population_size)]
        elif config.fixed_body not in ("pioneer", ""):
            template = Genotype.load(config.fixed_body)
            members = []
            for i in range(config.population_size):
                g = template.copy()
                g.name = f"c0-{i}"
                g.parents = []
                randomize_weights(g, rng, 1.0)
                members.append(g)
        else:
            members = [pioneer_genotype(rng, hidden=config.hidden_neurons, name=f"c0-{i}", rich=config.brain_model in ("rich", "foraging"), sources=vocab.sensor_sources if config.brain_model == "foraging" else None) for i in range(config.population_size)]
    else:
        raise ValueError(f"unknown population kind {kind!r}")
    return Population(kind=kind, members=members)


# --------------------------------------------------------------------------- #
# One generation
# --------------------------------------------------------------------------- #


def generation_sim(config: EvolutionConfig, terrain_seed: Optional[int], generation: Optional[int] = None) -> SimConfig:
    """The simulation configuration for one generation: random terrain takes that generation's seed,
    and under a heading curriculum the start heading range grows with the generation."""
    from dataclasses import replace

    sim = config.sim
    if sim.world.terrain == "random" and terrain_seed is not None:
        sim = replace(sim, world=replace(sim.world, terrain_seed=int(terrain_seed)))
    if config.heading_curriculum > 0 and generation is not None and sim.random_start:
        frac = min(1.0, generation / config.heading_curriculum)
        sim = replace(sim, start_heading_range=config.sim.start_heading_range * frac)
    return sim


def draw_terrain_seed(config: EvolutionConfig, rng: np.random.Generator) -> Optional[int]:
    """A fresh terrain seed for a generation (None when the terrain is not random or is fixed)."""
    if config.sim.world.terrain != "random":
        return None
    if config.sim.world.terrain_seed is not None:
        return int(config.sim.world.terrain_seed)
    return int(rng.integers(0, 2**31 - 1))


def draw_start_seeds(config: EvolutionConfig, rng: np.random.Generator) -> list:
    """Start-layout seeds for one generation (``None`` entries when the start is not random)."""
    if not config.sim.random_start:
        return [None] * max(1, config.draws)
    return [int(rng.integers(0, 2**31 - 1)) for _ in range(max(1, config.draws))]


def evaluate(pop: Population, runner: BoutRunner, rng: np.random.Generator, config: EvolutionConfig, terrain_seed: Optional[int] = None, start_seeds: Optional[list] = None, solo: bool = False) -> None:
    """Evaluate a population; fills ``pop.fitness``, ``pop.distances``, ``pop.best``, ``pop.runner_up``, ``pop.top``.

    Competitive: each member meets the previous generation's top ``config.opponents``
    members (all-versus-best when that is 1; the best itself meets the runner-up) on
    every start draw, and its fitness is the mean.  ``solo``: each member is scored
    alone on every draw (the locomotion phase).
    """
    n = len(pop.members)
    seeds = start_seeds or [None]
    sim = generation_sim(config, terrain_seed, pop.generation)
    pairs = []
    owners = []
    if solo:
        for i in range(n):
            for sd in seeds:
                pairs.append((pop.members[i], None, False, sd))
                owners.append(i)
    else:
        best = pop.best if pop.best is not None else int(rng.integers(0, n))
        top = [t for t in (pop.top or [best]) if 0 <= t < n]
        if not top:
            top = [best]
        k = max(1, config.opponents)
        for i in range(n):
            opps = [t for t in top if t != i][:k]
            if not opps:
                others = [j for j in range(n) if j != i]
                opps = [int(rng.choice(others))] if others else [i]
            for o in opps:
                for sd in seeds:
                    swap = bool(rng.random() < 0.5) if config.random_sides else False
                    pairs.append((pop.members[i], pop.members[o], swap, sd))
                    owners.append(i)
    results = runner.run(pairs, sim)
    fit = [[] for _ in range(n)]
    dist = [[] for _ in range(n)]
    vecs = [[] for _ in range(n)]
    for owner, r in zip(owners, results):
        fit[owner].append(r["fitness"][0])
        dist[owner].append(r["distances"][0])
        vecs[owner].append(r["vectors"][0])
    pop.fitness = [float(np.mean(f)) for f in fit]
    pop.distances = [float(np.mean(d)) for d in dist]
    pop.vectors = [np.mean(v, axis=0).tolist() for v in vecs]
    if config.survival:  # running mean over every evaluation this individual has had
        for i, m in enumerate(pop.members):
            rec = m.record
            rec["evals"] = int(rec.get("evals", 0)) + 1
            rec["fitness_sum"] = float(rec.get("fitness_sum", 0.0)) + pop.fitness[i]
            rec["last_fitness"] = pop.fitness[i]
            rec.setdefault("born", pop.generation)
            pop.fitness[i] = rec["fitness_sum"] / rec["evals"]
    ranked = pop.ranked()
    pop.best = ranked[0]
    pop.runner_up = ranked[1] if n > 1 else ranked[0]
    pop.top = ranked[: max(1, config.opponents) + 1]


def descriptor_cell(g: Genotype, sim: SimConfig) -> tuple:
    """A coarse structural cell for the archive: part-count band, driven-joint band, symmetry band."""
    from .analysis import morphology_descriptors

    ph = synthesize(g, sim.synthesis)
    parts = len(ph.parts)
    driven = len({ui.part for ui in ph.units if ui.unit.kind == "effector" and ui.part is not None and ph.parts[ui.part].parent is not None and ph.parts[ui.part].joint_type != JointType.FIXED})
    pos = np.array([p.attach_pos for p in ph.parts])  # cheap symmetry proxy: attachment points
    sym = 1.0
    if len(pos) > 1:
        m = pos.copy()
        m[:, 1] *= -1
        d = np.array([np.min(np.linalg.norm(pos - q, axis=1)) for q in m])
        sym = 1.0 - float(d.mean()) / max(float(np.ptp(pos, axis=0).max()), 1e-6)
    return (min(parts, 12) // 3, min(driven, 8) // 2, int(np.clip(sym, 0, 0.999) * 4))


def update_archive(pop: Population, sim: SimConfig) -> None:
    for i, m in enumerate(pop.members):
        cell = descriptor_cell(m, sim)
        prev = pop.archive.get(cell)
        if prev is None or pop.fitness[i] > prev[0]:
            pop.archive[cell] = (float(pop.fitness[i]), m.to_dict())


def _select(pop: Population, rng: np.random.Generator, k: int, method: str = "tournament") -> Genotype:
    if method == "lexicase" and pop.vectors:
        return pop.members[lexicase_select(pop.vectors, rng)]
    idx = rng.integers(0, len(pop.members), size=min(k, len(pop.members)))
    winner = max(idx, key=lambda i: pop.fitness[i])
    return pop.members[int(winner)]


def lexicase_select(vectors: list, rng: np.random.Generator, epsilon: float = 0.02) -> int:
    """Epsilon-lexicase selection: shuffle the objectives, keep the candidates within epsilon of the
    best on each in turn, and pick at random among the survivors.  No objective is weighted."""
    V = np.asarray(vectors, dtype=float)
    candidates = list(range(len(V)))
    for j in rng.permutation(V.shape[1]):
        col = V[candidates, j]
        best = col.max()
        keep = [c for c, v in zip(candidates, col) if v >= best - epsilon * max(abs(best), 1e-9)]
        candidates = keep
        if len(candidates) == 1:
            break
    return int(rng.choice(candidates))


def morph_age(g: Genotype) -> Optional[int]:
    """Generations since this lineage's body plan last changed (None for a founder, whose body never changed)."""
    a = g.record.get("morph_age")
    return None if a is None else int(a)


def protected(g: Genotype, k: int) -> bool:
    """Morphological innovation protection (Cheney, Bongard, SunSpiral & Lipson, ALIFE 2016;
    J. R. Soc. Interface 2018, section III.B): a holistic individual whose body plan changed
    fewer than ``k`` generations ago is shielded from elimination, so that control mutations
    can readapt its controller to its new body before it has to compete on fitness.

    Concretely, in :func:`reproduce` every protected *body plan* is guaranteed one child in
    the next generation, bred from its fittest carrier by
    :func:`~rabbitstew.genetics.mutate_brain` (controller only, body plan kept) and
    inheriting ``morph_age + 1``; the remaining slots are filled exactly as without
    protection.  One child per body, not per member, because an elite copy and its
    lineage's readaptation child carry the same body: the lineage is what is shielded, and
    counting it twice would let it crowd another protected lineage out of its slot.  A
    child whose body plan differs from every parent's is novel and starts at ``morph_age``
    0; an elite copy or a body-preserving child inherits its parent's age plus one;
    founders carry no age and are never protected, since no controller of theirs was ever
    tuned to a previous body.  Protection therefore lasts exactly ``k`` reproduction
    rounds: the lineage is present, body unchanged, in generations ``birth + 1`` to
    ``birth + k`` regardless of fitness, and at ``morph_age == k`` competes like everyone
    else.  Distinct protected bodies never outnumber the child slots (every one is either a
    readaptation child of age below ``k`` or a novel free-slot child, and elites only
    duplicate), so the guarantee is exact.
    """
    if k <= 0:
        return False
    a = morph_age(g)
    return a is not None and a < k


def _inherit_age(child: Genotype, parents: list, novel: bool, birth: str) -> None:
    """Stamp a child's morphological age and how it was born into its record."""
    if novel:
        age = 0
    else:
        ages = [morph_age(p) for p in parents]
        age = None if not ages or ages[0] is None else ages[0] + 1
    child.record["morph_age"] = age
    child.record["birth"] = birth


def reproduce(pop: Population, rng: np.random.Generator, config: EvolutionConfig) -> Population:
    """Build the next generation from an evaluated population."""
    ranked = pop.ranked()
    elites = []
    holistic = pop.kind == HOLISTIC
    if config.survival:
        # (mu+lambda): the best population_size individuals survive with their records; a full batch of children joins them.
        survivors = ranked[: config.population_size]
        for i in survivors:
            e = pop.members[i].copy()
            e.parents = list(pop.members[i].parents)
            e.record = dict(pop.members[i].record)
            e.record["survivor_of"] = pop.members[i].name
            _inherit_age(e, [pop.members[i]], False, "survivor")
            elites.append(e)
        n_children = config.population_size
    else:
        for i in ranked[: config.elites]:
            e = pop.members[i].copy()
            e.parents = [pop.members[i].name]
            _inherit_age(e, [pop.members[i]], False, "elite")
            elites.append(e)
        n_children = config.population_size - len(elites)
    children = []
    if holistic and config.morph_protection > 0:
        # Morphological innovation protection: every protected member is carried into the next
        # generation by one controller-only child, youngest bodies first if slots run short.
        carriers = {}  # body plan -> index of its fittest protected carrier
        for i, m in enumerate(pop.members):
            if protected(m, config.morph_protection):
                plan = body_plan(m)
                if plan not in carriers or pop.fitness[i] > pop.fitness[carriers[plan]]:
                    carriers[plan] = i
        shielded = sorted(carriers.values(), key=lambda i: (morph_age(pop.members[i]), -pop.fitness[i], i))
        for i in shielded[:n_children]:
            parent = pop.members[i]
            child = mutate_brain(parent, rng, config.mutation)
            assert body_plan(child) == body_plan(parent), "readaptation changed the body plan"
            child.parents = [parent.name]
            child.record = {}
            _inherit_age(child, [parent], False, "readapt")
            children.append(child)
    use_archive = holistic and config.archive and pop.archive
    while len(children) < n_children:
        if use_archive and rng.random() < config.archive_parents:
            parent = Genotype.from_dict(pop.archive[list(pop.archive)[int(rng.integers(0, len(pop.archive)))]][1])
        else:
            parent = _select(pop, rng, config.tournament_size, config.selection)
        other = _select(pop, rng, config.tournament_size, config.selection) if rng.random() < config.crossover_rate else None
        if holistic:
            child = crossover(parent, other, rng) if other is not None else parent.copy()
            child = mutate(child, rng, config.mutation)
        elif config.conventional_topology:
            child = crossover_controller(parent, other, rng) if other is not None else parent.copy()
            child = mutate_controller(child, rng, config.mutation)
            assert body_signature(child) == body_signature(pop.members[0]), "conventional evolution changed the body"
        else:
            child = crossover_weights(parent, other, rng) if other is not None else parent.copy()
            child = mutate_weights(child, rng, config.mutation)
            assert is_same_morphology(child, pop.members[0]), "conventional evolution changed the morphology"
        child.parents = [parent.name] + ([other.name] if other is not None else [])
        child.record = {}
        if holistic:
            plan = body_plan(child)
            novel = plan != body_plan(parent) and (other is None or plan != body_plan(other))
        else:
            novel = False  # the conventional body never changes; its lineage carries no morphological age
        _inherit_age(child, [parent] + ([other] if other is not None else []), novel, "free")
        children.append(child)
    members = elites + children
    prefix = "h" if holistic else "c"
    for i, m in enumerate(members):
        m.name = f"{prefix}{pop.generation + 1}-{i}"
    new = Population(kind=pop.kind, members=members, generation=pop.generation + 1, archive=dict(pop.archive))
    # The elites keep their ranks so the next all-versus-best round meets the right opponents.
    new.best = 0 if config.elites > 0 else None
    new.runner_up = 1 if config.elites > 1 else None
    new.top = list(range(min(config.elites, max(1, config.opponents) + 1)))
    return new


# --------------------------------------------------------------------------- #
# Inter-population measurement
# --------------------------------------------------------------------------- #


def champion_bouts(holistic: Population, conventional: Population, runner: BoutRunner, config: EvolutionConfig, terrain_seed: Optional[int] = None, start_seed: Optional[int] = None) -> dict:
    """Pit the champions of the two populations against each other.

    Returns a summary with the mean holistic fitness over all bouts (0.5 is
    parity), the number of holistic wins, and every individual result.
    """
    hc = holistic.champions(config.champions)
    cc = conventional.champions(config.champions)
    if config.champion_mode == "best":
        pairs = [(hc[0], cc[0], False, start_seed)]
    elif config.champion_mode == "roundrobin":
        pairs = [(h, c, swap, start_seed) for h in hc for c in cc for swap in (False, True)]
    elif config.champion_mode == "all":
        pairs = [(h, c, swap, start_seed) for h in holistic.members for c in conventional.members for swap in (False, True)]
    else:
        raise ValueError(f"unknown champion_mode {config.champion_mode!r}")
    results = runner.run(pairs, generation_sim(config, terrain_seed, holistic.generation))
    fitness = [r["fitness"][0] for r in results]
    bouts = [
        {"holistic": h.name, "conventional": c.name, "swapped": swap, "holistic_fitness": r["fitness"][0], "distances": r["distances"], "exploded": r["exploded"], "time_at_target": r.get("time_at_target")}
        for (h, c, swap, _), r in zip(pairs, results)
    ]
    return {
        "mode": config.champion_mode,
        "bouts": bouts,
        "holistic_mean_fitness": float(np.mean(fitness)),
        "holistic_wins": int(sum(f > 0.5 for f in fitness)),
        "conventional_wins": int(sum(f < 0.5 for f in fitness)),
        "n_bouts": len(fitness),
        "terrain_seed": terrain_seed,
        "start_seed": start_seed,
    }


# --------------------------------------------------------------------------- #
# Experiment driver
# --------------------------------------------------------------------------- #


def spawn_streams(seed: int, holistic_salt: int = 0) -> dict:
    """One independent generator per population and one for the terrain, all derived from ``seed``.

    Each population's stream feeds its founders, its evaluation draws (sides, fallback
    opponents) and its reproduction; the terrain stream feeds the per-generation terrain and
    start-layout seeds.  Nothing one population does can move another's draws or the terrain
    sequence, so two runs at one seed that differ in one population's reproduction (an arm
    such as ``morph_protection``) meet the same other population on the same terrains, which
    is what pairing arms by seed assumes (RBT-74, RBT-85).

    ``holistic_salt`` > 0 replaces the holistic stream alone with the seed sequence at spawn key
    ``(i, salt)``, ``i`` being the holistic stream's own index: a stream independent of all three
    unsalted ones, while the conventional and terrain streams stay exactly where they are.  Two
    runs at one seed differing only in the salt are an A/A pair: the same wheeled population on
    the same terrains, a different holistic draw, no manipulation (RBT-96).  Salt 0 is the
    unsalted streams exactly, so every run before the salt existed reproduces from its config.
    """
    children = np.random.SeedSequence(seed).spawn(len(STREAMS))
    if holistic_salt:
        i = STREAMS.index(HOLISTIC)
        children[i] = np.random.SeedSequence(seed, spawn_key=(i, int(holistic_salt)))
    return {name: np.random.default_rng(ss) for name, ss in zip(STREAMS, children)}



class Experiment:
    """Runs both populations side by side and records everything to ``out_dir``."""

    def __init__(self, config: Optional[EvolutionConfig] = None, out_dir: Optional[str] = None, log: Optional[Callable[[str], None]] = print):
        self.config = config or EvolutionConfig()
        self.out_dir = out_dir
        self.log = log or (lambda s: None)
        self.rngs = spawn_streams(self.config.seed, self.config.holistic_stream_salt)
        self.runner = BoutRunner(self.config.sim, self.config.workers)
        self.populations = {
            HOLISTIC: initial_population(HOLISTIC, self.config, self.rngs[HOLISTIC]),
            CONVENTIONAL: initial_population(CONVENTIONAL, self.config, self.rngs[CONVENTIONAL]),
        }
        self.history: list[dict] = []
        self.champion_history: list[dict] = []
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, "config.json"), "w") as f:
                json.dump(_jsonable(self.config.to_dict()), f, indent=2)

    # -- checkpointing ----------------------------------------------------- #
    STATE_FILE = "state.json"

    def save_state(self) -> None:
        """Write everything needed to resume: populations, RNG, history."""
        if not self.out_dir:
            return
        state = {
            "populations": {
                kind: {"kind": pop.kind, "generation": pop.generation, "best": pop.best, "runner_up": pop.runner_up, "top": list(pop.top), "archive": [[list(k), v[0], v[1]] for k, v in pop.archive.items()], "members": [m.to_dict() for m in pop.members]}
                for kind, pop in self.populations.items()
            },
            "rngs": {name: rng.bit_generator.state for name, rng in self.rngs.items()},
            "history": self.history,
            "champion_history": self.champion_history,
        }
        tmp = os.path.join(self.out_dir, self.STATE_FILE + ".tmp")
        with open(tmp, "w") as f:
            json.dump(state, f)
        os.replace(tmp, os.path.join(self.out_dir, self.STATE_FILE))

    @staticmethod
    def resume(out_dir: str, generations: Optional[int] = None, workers: Optional[int] = None, log=print) -> "Experiment":
        """Rebuild an experiment from ``out_dir`` and continue it.

        ``generations`` may raise the target; the run continues from the
        generation after the last one whose population was saved.
        """
        with open(os.path.join(out_dir, "config.json")) as f:
            cfg = EvolutionConfig.from_dict(json.load(f))
        if generations is not None:
            cfg.generations = generations
        if workers is not None:
            cfg.workers = workers
        ex = Experiment(cfg, out_dir=None, log=log)
        ex.out_dir = out_dir
        with open(os.path.join(out_dir, "config.json"), "w") as f:
            json.dump(_jsonable(cfg.to_dict()), f, indent=2)
        with open(os.path.join(out_dir, Experiment.STATE_FILE)) as f:
            state = json.load(f)
        ex.populations = {}
        for kind, pd in state["populations"].items():
            ex.populations[kind] = Population(kind=pd["kind"], members=[Genotype.from_dict(m) for m in pd["members"]], best=pd["best"], runner_up=pd["runner_up"], generation=pd["generation"], top=list(pd.get("top", [])), archive={tuple(k): (f, g) for k, f, g in pd.get("archive", [])})
        if "rngs" not in state:
            raise ValueError(f"{out_dir} was checkpointed under the single shared RNG stream (before RBT-85) and cannot be resumed under per-population streams; rerun it from its config")
        for name, rng in ex.rngs.items():
            rng.bit_generator.state = state["rngs"][name]
        ex.history = state["history"]
        ex.champion_history = state["champion_history"]
        ex._start_gen = ex.populations[HOLISTIC].generation
        ex._truncate_lineage(ex._start_gen)
        return ex

    def _truncate_lineage(self, start_gen: int) -> None:
        """Drop lineage.jsonl lines at or after ``start_gen`` (RBT-93).

        ``run`` logs a generation's lineage as soon as it is evaluated and saves
        ``state.json`` only after reproduction, so the restart generation is
        already logged (always for the final generation of a completed run, and
        for whichever population had been evaluated before a kill).  The resume
        re-evaluates it deterministically and would log it a second time; the
        uninterrupted run's bytes are restored by dropping those lines first.
        """
        path = os.path.join(self.out_dir, "lineage.jsonl")
        if not os.path.exists(path):
            return
        with open(path) as f:
            lines = f.readlines()
        keep = [l for l in lines if not l.strip() or json.loads(l)["generation"] < start_gen]
        if len(keep) != len(lines):
            with open(path, "w") as f:
                f.writelines(keep)

    def run(self) -> dict:
        cfg = self.config
        for gen in range(getattr(self, "_start_gen", 0), cfg.generations):
            t0 = time.time()
            terrain_seed = draw_terrain_seed(cfg, self.rngs[TERRAIN])
            start_seeds = draw_start_seeds(cfg, self.rngs[TERRAIN])
            solo = gen < cfg.locomotion_phase
            for kind, pop in self.populations.items():
                evaluate(pop, self.runner, self.rngs[kind], cfg, terrain_seed, start_seeds, solo=solo)
                if cfg.archive and kind == HOLISTIC:
                    update_archive(pop, cfg.sim)
                entry = {
                    "generation": pop.generation,
                    "population": kind,
                    "terrain_seed": terrain_seed,
                    "start_seeds": start_seeds,
                    "solo": solo,
                    "archive_cells": len(pop.archive) if cfg.archive and kind == HOLISTIC else None,
                    "best_fitness": float(max(pop.fitness)),
                    "mean_fitness": float(np.mean(pop.fitness)),
                    "best_distance": float(pop.distances[pop.best]),
                    "mean_distance": float(np.mean(pop.distances)),
                    "best_name": pop.members[pop.best].name,
                    "best_nodes": len(pop.members[pop.best].nodes),
                    **_size_stats(pop.members[pop.best], cfg.sim),
                    "mean_units": float(np.mean([_size_stats(m, cfg.sim)["best_units"] for m in pop.members])),
                    "mean_mass": float(np.mean([_size_stats(m, cfg.sim)["best_mass"] for m in pop.members])),
                }
                self.history.append(entry)
                self._save_best(pop)
                self._log_lineage(pop)
                self.log(f"gen {pop.generation:3d} {kind:12s} best {entry['best_fitness']:.3f} mean {entry['mean_fitness']:.3f} best-dist {entry['best_distance']:.2f} m")
            if cfg.champion_interval and (gen % cfg.champion_interval == 0 or gen == cfg.generations - 1):
                summary = champion_bouts(self.populations[HOLISTIC], self.populations[CONVENTIONAL], self.runner, cfg, terrain_seed, start_seeds[0])
                summary["generation"] = gen
                for pop in self.populations.values():
                    self._save_champions(pop)
                self.champion_history.append(summary)
                self.log(
                    f"gen {gen:3d} champions ({summary['mode']}): holistic mean fitness {summary['holistic_mean_fitness']:.3f}, "
                    f"wins {summary['holistic_wins']}-{summary['conventional_wins']} of {summary['n_bouts']}"
                )
            self._flush()
            if gen < cfg.generations - 1:
                for kind in list(self.populations):
                    self.populations[kind] = reproduce(self.populations[kind], self.rngs[kind], cfg)
                self.save_state()
            self.log(f"gen {gen:3d} took {time.time() - t0:.1f}s")
        self.runner.close()
        self._save_populations()
        return self.summary()

    def summary(self) -> dict:
        return {"history": self.history, "champions": self.champion_history}

    # -- persistence ------------------------------------------------------- #
    def _save_best(self, pop: Population) -> None:
        if not self.out_dir:
            return
        d = os.path.join(self.out_dir, pop.kind)
        os.makedirs(d, exist_ok=True)
        pop.members[pop.best].save(os.path.join(d, f"best_gen{pop.generation:04d}.json"))

    def _log_lineage(self, pop: Population) -> None:
        """Append every member of an evaluated generation to lineage.jsonl: name, parents, fitness, size."""
        if not self.out_dir:
            return
        with open(os.path.join(self.out_dir, "lineage.jsonl"), "a") as f:
            for i, m in enumerate(pop.members):
                rec = {"generation": pop.generation, "population": pop.kind, "name": m.name, "parents": list(m.parents), "fitness": round(float(pop.fitness[i]), 4), "distance": round(float(pop.distances[i]), 4), "nodes": len(m.nodes)}
                if "evals" in m.record:
                    rec["evals"] = m.record.get("evals")
                    rec["last_fitness"] = round(float(m.record.get("last_fitness", pop.fitness[i])), 4)
                    rec["survivor_of"] = m.record.get("survivor_of")
                if pop.vectors:
                    rec["vector"] = [round(float(v), 4) for v in pop.vectors[i]]
                rec["birth"] = m.record.get("birth")  # free-slot child, readaptation child, elite copy or survivor
                if pop.kind == HOLISTIC:
                    rec["body"] = body_plan_hash(m)
                    rec["morph_age"] = m.record.get("morph_age")
                rec.update({k.replace("best_", ""): v for k, v in _size_stats(m, self.config.sim).items()})
                f.write(json.dumps(rec) + "\n")

    def _save_champions(self, pop: Population) -> None:
        """Save the top-k genotypes that took part in a checkpoint's champion bouts."""
        if not self.out_dir:
            return
        d = os.path.join(self.out_dir, pop.kind, f"champions_gen{pop.generation:04d}")
        os.makedirs(d, exist_ok=True)
        for k, g in enumerate(pop.champions(self.config.champions)):
            g.save(os.path.join(d, f"{k}.json"))

    def _save_populations(self) -> None:
        if not self.out_dir:
            return
        for kind, pop in self.populations.items():
            d = os.path.join(self.out_dir, kind, "final")
            os.makedirs(d, exist_ok=True)
            for i, m in enumerate(pop.members):
                m.save(os.path.join(d, f"{i:03d}.json"))

    def _flush(self) -> None:
        if not self.out_dir:
            return
        with open(os.path.join(self.out_dir, "history.json"), "w") as f:
            json.dump(self.summary(), f, indent=1)


def _size_stats(g: Genotype, sim: SimConfig) -> dict:
    """Body and brain size of a genotype's phenotype, for the history log."""
    ph = synthesize(g, sim.synthesis)
    return {"best_parts": len(ph.parts), "best_units": len(ph.units), "best_links": len(ph.links), "best_mass": round(ph.total_mass(), 3)}


def _jsonable(obj):
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    return obj
