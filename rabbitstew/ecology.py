"""An ecology instead of a genetic algorithm.

No ranking and no culling round.  Every individual has *energy* and *age*.
Each season it faces one challenge (a solo run on that season's terrain and
start draw, or a paired bout) and gains energy equal to its score; living
costs energy per season, by default the population's mean gain that season,
so that energy is conserved within a population and only individuals that do
better than their contemporaries accumulate it.  Founders start at staggered
ages so that cohorts do not die together.  When energy crosses the birth threshold
the individual breeds, paying part of its energy into the child, provided a
slot is free; slots open only through deaths, which come from starvation or
old age, never from a rank.  Generations are decoupled from challenges: the
population is a mixture of ages and lineages at any time, and an
individual's lifetime record is a high-resolution measure of what it can do.

Both populations of an experiment (holistic bodies and the designed body
with an evolving controller) live in separate ecologies of the same size
under the same seasons, so that the comparison with the GA is like for like.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Callable, Optional, Union

import numpy as np

from .evolution import CONVENTIONAL, HOLISTIC, BoutRunner, EvolutionConfig, _size_stats, draw_start_seeds, draw_terrain_seed, generation_sim, initial_population
from .fixed import is_same_morphology
from .genetics import body_signature, crossover, crossover_controller, crossover_weights, mutate, mutate_controller, mutate_weights
from .genotype import Genotype


@dataclass
class EcologyConfig:
    seasons: int = 300
    capacity: int = 60  #: slots per population
    living_cost: Union[float, str] = "relative"  #: energy per season just to exist; "relative" charges each population its own mean gain that season, so energy is conserved and only above-average individuals accumulate it
    birth_threshold: float = 3.0  #: energy needed to breed
    birth_cost: float = 1.0  #: energy passed from parent to child
    initial_energy: float = 2.0
    max_age: int = 60  #: seasons
    stagger_ages: bool = True  #: founders start at ages spread over [0, max_age) so cohorts do not die together
    starvation: bool = True  #: False: nobody dies of energy loss, only of age (a neutral-drift control when breeding is also free)
    crossover_rate: float = 0.3  #: a breeder may mix with a random other breeder-eligible individual
    challenge: str = "solo"  #: "solo" (every individual alone) or "paired" (random pairs, zero-sum bout score)
    log_every: int = 1

    def cost(self, gains: list) -> float:
        if self.living_cost == "relative":
            return float(np.mean(gains)) if gains else 0.0
        return float(self.living_cost)


class Ecology:
    """Runs both populations as ecologies on top of an :class:`EvolutionConfig`'s simulator settings."""

    def __init__(self, evo: EvolutionConfig, eco: Optional[EcologyConfig] = None, out_dir: Optional[str] = None, log: Optional[Callable[[str], None]] = print):
        self.evo = evo
        self.eco = eco or EcologyConfig()
        self.out_dir = out_dir
        self.log = log or (lambda s: None)
        self.rng = np.random.default_rng(evo.seed)
        self.runner = BoutRunner(evo.sim, evo.workers)
        evo.population_size = self.eco.capacity
        self.populations = {}
        for kind in (HOLISTIC, CONVENTIONAL):
            pop = initial_population(kind, evo, self.rng)
            for m in pop.members:
                age = int(self.rng.integers(0, self.eco.max_age)) if self.eco.stagger_ages else 0
                m.record = {"energy": self.eco.initial_energy, "age": age, "evals": 0, "score_sum": 0.0, "born": -age}
            self.populations[kind] = list(pop.members)
        self.season = 0
        self.history: list[dict] = []
        self.counter = {HOLISTIC: len(self.populations[HOLISTIC]), CONVENTIONAL: len(self.populations[CONVENTIONAL])}
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, "config.json"), "w") as f:
                json.dump({**_jsonable(evo.to_dict()), "ecology": self.eco.__dict__}, f, indent=2)

    # -- one season --------------------------------------------------------- #
    def step(self) -> None:
        eco, evo = self.eco, self.evo
        terrain_seed = draw_terrain_seed(evo, self.rng)
        start_seed = draw_start_seeds(evo, self.rng)[0]
        sim = generation_sim(evo, terrain_seed, self.season)
        for kind, members in self.populations.items():
            if not members:
                continue
            # 1. challenge
            if eco.challenge == "paired" and len(members) > 1:
                order = self.rng.permutation(len(members))
                pairs, owners = [], []
                for a, b in zip(order[::2], order[1::2]):
                    pairs.append((members[a], members[b], False, start_seed))
                    owners.append((a, b))
                results = self.runner.run(pairs, sim)
                gains = {}
                for (a, b), r in zip(owners, results):
                    gains[a] = r["fitness"][0]
                    gains[b] = r["fitness"][1]
                if len(members) % 2:
                    gains[int(order[-1])] = 0.5
            else:
                results = self.runner.run([(m, None, False, start_seed) for m in members], sim)
                gains = {i: r["fitness"][0] for i, r in enumerate(results)}
            # 2. energy, age, records
            cost = eco.cost([float(gains.get(i, 0.0)) for i in range(len(members))])
            for i, m in enumerate(members):
                rec = m.record
                g = float(gains.get(i, 0.0))
                rec["energy"] = rec["energy"] + g - cost
                rec["age"] += 1
                rec["evals"] += 1
                rec["score_sum"] += g
                rec["last_score"] = g
            # 3. deaths
            alive = [m for m in members if (m.record["energy"] > 0 or not eco.starvation) and m.record["age"] < eco.max_age]
            deaths = len(members) - len(alive)
            # 4. births (energy above threshold, a free slot)
            breeders = [m for m in alive if m.record["energy"] >= eco.birth_threshold]
            self.rng.shuffle(breeders)
            births = 0
            for parent in breeders:
                if len(alive) >= eco.capacity:
                    break
                other = None
                if eco.crossover_rate > 0 and len(breeders) > 1 and self.rng.random() < eco.crossover_rate:
                    other = breeders[int(self.rng.integers(0, len(breeders)))]
                    if other is parent:
                        other = None
                child = self._breed(kind, parent, other)
                parent.record["energy"] -= eco.birth_cost
                child.record = {"energy": eco.birth_cost, "age": 0, "evals": 0, "score_sum": 0.0, "born": self.season + 1}
                self.counter[kind] += 1
                child.name = f"{'h' if kind == HOLISTIC else 'c'}e{self.counter[kind]}"
                alive.append(child)
                births += 1
            self.populations[kind] = alive
            # 5. record
            scores = [m.record["score_sum"] / max(1, m.record["evals"]) for m in alive]
            ages = [m.record["age"] for m in alive]
            best = max(alive, key=lambda m: m.record["score_sum"] / max(1, m.record["evals"])) if alive else None
            entry = {"season": self.season, "population": kind, "alive": len(alive), "deaths": deaths, "births": births, "mean_lifetime_score": float(np.mean(scores)) if scores else 0.0, "best_lifetime_score": float(max(scores)) if scores else 0.0, "mean_age": float(np.mean(ages)) if ages else 0.0, "max_age": int(max(ages)) if ages else 0, "best_name": best.name if best else None, "terrain_seed": terrain_seed, "start_seed": start_seed, "living_cost": cost, "total_energy": float(sum(m.record["energy"] for m in alive))}
            if best is not None:
                entry.update({k.replace("best_", "best_"): v for k, v in _size_stats(best, evo.sim).items()})
            self.history.append(entry)
            self._log_lineage(kind, alive)
            if best is not None and self.out_dir and self.season % 10 == 0:
                d = os.path.join(self.out_dir, kind)
                os.makedirs(d, exist_ok=True)
                best.save(os.path.join(d, f"best_gen{self.season:04d}.json"))
        self.season += 1

    def _breed(self, kind: str, parent: Genotype, other: Optional[Genotype]) -> Genotype:
        evo = self.evo
        if kind == HOLISTIC:
            child = crossover(parent, other, self.rng) if other is not None else parent.copy()
            child = mutate(child, self.rng, evo.mutation)
        elif evo.conventional_topology:
            child = crossover_controller(parent, other, self.rng) if other is not None else parent.copy()
            child = mutate_controller(child, self.rng, evo.mutation)
            assert body_signature(child) == body_signature(parent)
        else:
            child = crossover_weights(parent, other, self.rng) if other is not None else parent.copy()
            child = mutate_weights(child, self.rng, evo.mutation)
            assert is_same_morphology(child, parent)
        child.parents = [parent.name] + ([other.name] if other is not None else [])
        return child

    def run(self) -> dict:
        for s in range(self.season, self.eco.seasons):
            t0 = time.time()
            self.step()
            h = [e for e in self.history if e["season"] == s]
            if self.season % self.eco.log_every == 0:
                self.log("  ".join(f"season {e['season']:3d} {e['population']:12s} alive {e['alive']:3d} births {e['births']:2d} deaths {e['deaths']:2d} best lifetime {e['best_lifetime_score']:.3f} mean {e['mean_lifetime_score']:.3f} max age {e['max_age']:2d}" for e in h) + f"  ({time.time() - t0:.1f}s)")
            self._flush()
            if all(len(m) == 0 for m in self.populations.values()):
                self.log("everyone died")
                break
        self.runner.close()
        self._save_populations()
        return {"history": self.history}

    # -- persistence ------------------------------------------------------- #
    def _log_lineage(self, kind: str, members: list) -> None:
        if not self.out_dir:
            return
        with open(os.path.join(self.out_dir, "lineage.jsonl"), "a") as f:
            for m in members:
                rec = {"generation": self.season, "population": kind, "name": m.name, "parents": list(m.parents), "fitness": round(m.record["score_sum"] / max(1, m.record["evals"]), 4), "distance": None, "nodes": len(m.nodes), "energy": round(m.record["energy"], 3), "age": m.record["age"], "evals": m.record["evals"], "last_score": round(float(m.record.get("last_score", 0.0)), 4)}
                f.write(json.dumps(rec) + "\n")

    def _flush(self) -> None:
        if self.out_dir:
            with open(os.path.join(self.out_dir, "history.json"), "w") as f:
                json.dump({"history": self.history, "champions": [], "ecology": True}, f)

    def _save_populations(self) -> None:
        if not self.out_dir:
            return
        for kind, members in self.populations.items():
            d = os.path.join(self.out_dir, kind, "final")
            os.makedirs(d, exist_ok=True)
            for i, m in enumerate(members):
                m.save(os.path.join(d, f"{i:03d}.json"))


def _jsonable(obj):
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    return obj
