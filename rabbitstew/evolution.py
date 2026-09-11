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

from .fixed import is_same_morphology, pioneer_genotype
from .genetics import MutationConfig, crossover, crossover_weights, mutate, mutate_weights
from .genotype import Genotype, random_genotype
from .simulation import BoutResult, SimConfig, run_bout
from .synthesis import synthesize

HOLISTIC = "holistic"
CONVENTIONAL = "conventional"


@dataclass
class EvolutionConfig:
    population_size: int = 20
    generations: int = 30
    elites: int = 2  #: best individuals copied unchanged into the next generation
    tournament_size: int = 3
    crossover_rate: float = 0.5
    champion_interval: int = 5  #: generations between inter-population champion bouts (0 disables)
    champions: int = 3  #: top-k of each population that take part
    champion_mode: str = "best"  #: "best" (paper) or "roundrobin"
    random_sides: bool = True  #: randomise which side of the arena each competitor starts on
    workers: int = 1  #: processes used for bouts (1 = in-process)
    seed: int = 0
    sim: SimConfig = field(default_factory=SimConfig)
    mutation: MutationConfig = field(default_factory=MutationConfig)
    hidden_neurons: int = 6  #: hidden neurons in the fixed body's controller

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Population:
    kind: str
    members: list  #: list[Genotype]
    fitness: list = field(default_factory=list)
    distances: list = field(default_factory=list)
    best: Optional[int] = None  #: index of the best member (from the last evaluation)
    runner_up: Optional[int] = None
    generation: int = 0

    def ranked(self) -> list[int]:
        return sorted(range(len(self.members)), key=lambda i: -self.fitness[i])

    def champions(self, k: int) -> list[Genotype]:
        return [self.members[i] for i in self.ranked()[:k]]


# --------------------------------------------------------------------------- #
# Bouts (possibly in worker processes)
# --------------------------------------------------------------------------- #


def _bout_task(args) -> dict:
    a, b, sim, swap = args
    res = run_bout(Genotype.from_dict(a), Genotype.from_dict(b), sim, swap=swap)
    return {"distances": res.distances, "fitness": res.fitness, "exploded": res.exploded}


class BoutRunner:
    """Runs batches of bouts, in-process or in a process pool."""

    def __init__(self, sim: SimConfig, workers: int = 1):
        self.sim = sim
        self.workers = max(1, workers)
        self._pool = ProcessPoolExecutor(self.workers) if self.workers > 1 else None

    def run(self, pairs: list[tuple[Genotype, Genotype, bool]]) -> list[dict]:
        tasks = [(a.to_dict(), b.to_dict(), self.sim, swap) for a, b, swap in pairs]
        if self._pool is None:
            return [_bout_task(t) for t in tasks]
        return list(self._pool.map(_bout_task, tasks, chunksize=1))

    def close(self) -> None:
        if self._pool is not None:
            self._pool.shutdown()
            self._pool = None


# --------------------------------------------------------------------------- #
# Population initialisation
# --------------------------------------------------------------------------- #


def initial_population(kind: str, config: EvolutionConfig, rng: np.random.Generator) -> Population:
    if kind == HOLISTIC:
        members = [random_genotype(rng, name=f"h0-{i}") for i in range(config.population_size)]
    elif kind == CONVENTIONAL:
        members = [pioneer_genotype(rng, hidden=config.hidden_neurons, name=f"c0-{i}") for i in range(config.population_size)]
    else:
        raise ValueError(f"unknown population kind {kind!r}")
    return Population(kind=kind, members=members)


# --------------------------------------------------------------------------- #
# One generation
# --------------------------------------------------------------------------- #


def evaluate(pop: Population, runner: BoutRunner, rng: np.random.Generator, config: EvolutionConfig) -> None:
    """All-versus-best evaluation; fills ``pop.fitness`` and ``pop.distances``."""
    n = len(pop.members)
    best = pop.best if pop.best is not None else int(rng.integers(0, n))
    runner_up = pop.runner_up
    if runner_up is None or runner_up == best:
        others = [i for i in range(n) if i != best]
        runner_up = int(rng.choice(others)) if others else best
    pairs = []
    for i in range(n):
        opponent = runner_up if i == best else best
        swap = bool(rng.random() < 0.5) if config.random_sides else False
        pairs.append((pop.members[i], pop.members[opponent], swap))
    results = runner.run(pairs)
    pop.fitness = [r["fitness"][0] for r in results]
    pop.distances = [r["distances"][0] for r in results]
    ranked = pop.ranked()
    pop.best = ranked[0]
    pop.runner_up = ranked[1] if n > 1 else ranked[0]


def _select(pop: Population, rng: np.random.Generator, k: int) -> Genotype:
    idx = rng.integers(0, len(pop.members), size=min(k, len(pop.members)))
    winner = max(idx, key=lambda i: pop.fitness[i])
    return pop.members[int(winner)]


def reproduce(pop: Population, rng: np.random.Generator, config: EvolutionConfig) -> Population:
    """Build the next generation from an evaluated population."""
    ranked = pop.ranked()
    elites = [pop.members[i].copy() for i in ranked[: config.elites]]
    children = []
    holistic = pop.kind == HOLISTIC
    while len(elites) + len(children) < config.population_size:
        parent = _select(pop, rng, config.tournament_size)
        if rng.random() < config.crossover_rate:
            other = _select(pop, rng, config.tournament_size)
            child = crossover(parent, other, rng) if holistic else crossover_weights(parent, other, rng)
        else:
            child = parent.copy()
        child = mutate(child, rng, config.mutation) if holistic else mutate_weights(child, rng, config.mutation)
        if not holistic:
            assert is_same_morphology(child, pop.members[0]), "conventional evolution changed the morphology"
        children.append(child)
    members = elites + children
    prefix = "h" if holistic else "c"
    for i, m in enumerate(members):
        m.name = f"{prefix}{pop.generation + 1}-{i}"
    new = Population(kind=pop.kind, members=members, generation=pop.generation + 1)
    # The elites keep their ranks so the next all-versus-best round meets the right opponents.
    new.best = 0 if config.elites > 0 else None
    new.runner_up = 1 if config.elites > 1 else None
    return new


# --------------------------------------------------------------------------- #
# Inter-population measurement
# --------------------------------------------------------------------------- #


def champion_bouts(holistic: Population, conventional: Population, runner: BoutRunner, config: EvolutionConfig) -> dict:
    """Pit the champions of the two populations against each other.

    Returns a summary with the mean holistic fitness over all bouts (0.5 is
    parity), the number of holistic wins, and every individual result.
    """
    hc = holistic.champions(config.champions)
    cc = conventional.champions(config.champions)
    if config.champion_mode == "best":
        pairs = [(hc[0], cc[0], False)]
    elif config.champion_mode == "roundrobin":
        pairs = [(h, c, swap) for h in hc for c in cc for swap in (False, True)]
    else:
        raise ValueError(f"unknown champion_mode {config.champion_mode!r}")
    results = runner.run(pairs)
    fitness = [r["fitness"][0] for r in results]
    bouts = [
        {"holistic": h.name, "conventional": c.name, "swapped": swap, "holistic_fitness": r["fitness"][0], "distances": r["distances"], "exploded": r["exploded"]}
        for (h, c, swap), r in zip(pairs, results)
    ]
    return {
        "mode": config.champion_mode,
        "bouts": bouts,
        "holistic_mean_fitness": float(np.mean(fitness)),
        "holistic_wins": int(sum(f > 0.5 for f in fitness)),
        "conventional_wins": int(sum(f < 0.5 for f in fitness)),
        "n_bouts": len(fitness),
    }


# --------------------------------------------------------------------------- #
# Experiment driver
# --------------------------------------------------------------------------- #


class Experiment:
    """Runs both populations side by side and records everything to ``out_dir``."""

    def __init__(self, config: Optional[EvolutionConfig] = None, out_dir: Optional[str] = None, log: Optional[Callable[[str], None]] = print):
        self.config = config or EvolutionConfig()
        self.out_dir = out_dir
        self.log = log or (lambda s: None)
        self.rng = np.random.default_rng(self.config.seed)
        self.runner = BoutRunner(self.config.sim, self.config.workers)
        self.populations = {
            HOLISTIC: initial_population(HOLISTIC, self.config, self.rng),
            CONVENTIONAL: initial_population(CONVENTIONAL, self.config, self.rng),
        }
        self.history: list[dict] = []
        self.champion_history: list[dict] = []
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, "config.json"), "w") as f:
                json.dump(_jsonable(self.config.to_dict()), f, indent=2)

    def run(self) -> dict:
        cfg = self.config
        for gen in range(cfg.generations):
            t0 = time.time()
            for kind, pop in self.populations.items():
                evaluate(pop, self.runner, self.rng, cfg)
                entry = {
                    "generation": pop.generation,
                    "population": kind,
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
                self.log(f"gen {pop.generation:3d} {kind:12s} best {entry['best_fitness']:.3f} mean {entry['mean_fitness']:.3f} best-dist {entry['best_distance']:.2f} m")
            if cfg.champion_interval and (gen % cfg.champion_interval == 0 or gen == cfg.generations - 1):
                summary = champion_bouts(self.populations[HOLISTIC], self.populations[CONVENTIONAL], self.runner, cfg)
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
                    self.populations[kind] = reproduce(self.populations[kind], self.rng, cfg)
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
