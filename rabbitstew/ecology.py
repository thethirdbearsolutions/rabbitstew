"""An ecology instead of a genetic algorithm.

No ranking and no culling round.  Every individual has *energy* and *age*.
Each season it faces one challenge (a solo run on that season's terrain and
start draw, or a foraging season in a shared arena) and gains energy equal to
its score; living costs a fixed amount of energy per season.  The economy is
*absolute*: energy enters the population from the world, so an individual that
scores above the living cost accumulates whatever anyone else does, and a
population that is uniformly competent still breeds.  Founders start at
staggered ages so that cohorts do not die together.  When energy crosses the birth threshold
the individual breeds, paying part of its energy into the child, provided a
slot is free; slots open only through deaths, which come from starvation or
old age, never from a rank.  Generations are decoupled from challenges: the
population is a mixture of ages and lineages at any time, and an
individual's lifetime record is a high-resolution measure of what it can do.

Two earlier economies are retired (RBT-8).  A *relative* living cost charges
each population its own mean gain that season, which conserves energy exactly:
with a fixed birth threshold, a converged population has nobody far enough
above its own average to afford a child and ages out, as both non-foraging
ecologies of paper 3 did (solo: 196 seasons; paired: 444).  The ``paired``
challenge shares that fate: its bouts hand out 0 and 1 whatever the competence,
so energy tracks a win rate against neighbours rather than anything the world
pays out.  Neither is a default or a documented way to run the ecology any
more; both stay reachable so that paper 3's runs can be reproduced, and
selecting either warns.

Both populations of an experiment (holistic bodies and the designed body
with an evolving controller) live in separate ecologies of the same size
under the same seasons, so that the comparison with the GA is like for like.

They can also be made to meet.  With ``merge_after`` set, the two
populations share one arena from that season on, under one pooled capacity:
one challenge, one living cost, deaths pooled, and a slot freed by either
fauna open to the next breeder of either kind, so the run records which
fauna persists rather than holding both at a fixed size.  Breeding stays
within a fauna, there being nothing to cross between a holistic genotype and
a fixed body.  The merge season and the pooled capacity are settings rather
than outcomes, so they are written to the run's config before the first
season.  Either population can also be started from a saved one (see
:func:`load_population`), which is what carrying a fauna into a poorer world,
or into the other's, needs.
"""

from __future__ import annotations

import glob
import json
import os
import time
import warnings
from dataclasses import dataclass, field
from typing import Callable, Optional, Union

import numpy as np

from .evolution import CONVENTIONAL, HOLISTIC, BoutRunner, EvolutionConfig, _size_stats, draw_start_seeds, draw_terrain_seed, generation_sim, initial_population
from .fixed import is_same_morphology
from .genetics import body_signature, crossover, crossover_controller, crossover_weights, mutate, mutate_controller, mutate_weights
from .genotype import Genotype

ORDER = (HOLISTIC, CONVENTIONAL)


@dataclass
class EcologyConfig:
    seasons: int = 300
    capacity: int = 60  #: slots per population
    living_cost: Union[float, str] = 0.05  #: energy per season just to exist, charged against a gain that comes from the world (calibrated on random founders of both populations; see the README); the retired "relative" charges each population its own mean gain that season, which conserves energy and stops a converged population breeding at all (RBT-8)
    birth_threshold: float = 3.0  #: energy needed to breed
    birth_cost: float = 1.0  #: energy passed from parent to child
    initial_energy: float = 2.0
    max_age: int = 60  #: seasons
    stagger_ages: bool = True  #: founders start at ages spread over [0, max_age) so cohorts do not die together
    starvation: bool = True  #: False: nobody dies of energy loss, only of age (a neutral-drift control when breeding is also free)
    crossover_rate: float = 0.3  #: a breeder may mix with a random other breeder-eligible individual
    challenge: str = "solo"  #: "solo" (every individual alone) or "foraging" (groups share an arena with food; gain = net food energy); the retired "paired" (random pairs, zero-sum bout score) pays out a fixed pot whatever the competence (RBT-8)
    group_size: int = 4  #: robots per arena under the foraging challenge
    merge_after: Optional[int] = None  #: season at which the two ecologies merge into one arena under one pooled capacity; None keeps them apart for the whole run
    pooled_capacity: Optional[int] = None  #: slots in the merged arena; None means twice `capacity`, so neither fauna gains or loses room by merging
    seed_from: Optional[str] = None  #: load both populations' founders from this run directory instead of generating them
    seed_holistic: Optional[str] = None  #: load only the holistic founders, from this run directory, population directory or genotype file (overrides `seed_from`)
    seed_conventional: Optional[str] = None  #: the same for the designed-body population
    log_every: int = 1

    def retired_economy(self) -> Optional[str]:
        """Why this economy was retired under RBT-8, or None if it is a current one.

        Both retirements are the same failure: energy that comes from the
        neighbours rather than from the world cannot pay for reproduction.
        A run that sets one is still run, so paper 3 reproduces, but it is
        warned about rather than silently accepted.
        """
        if self.living_cost == "relative":
            return 'living_cost="relative" conserves energy within each population, so a converged population has nobody above its own average to breed and ages out (paper 3: 196 seasons)'
        if self.challenge == "paired":
            return 'challenge="paired" pays out one unit per bout whatever the competence, so energy tracks a win rate against neighbours rather than anything the world yields (paper 3: 444 seasons)'
        return None

    def cost(self, gains: list) -> float:
        if self.living_cost == "relative":
            return float(np.mean(gains)) if gains else 0.0
        return float(self.living_cost)

    def merged_at(self, season: int) -> bool:
        return self.merge_after is not None and season >= self.merge_after

    def slots(self, merged: bool) -> int:
        """Capacity in force: per population before the merge, pooled after it."""
        if not merged:
            return self.capacity
        return self.pooled_capacity if self.pooled_capacity is not None else 2 * self.capacity


class Ecology:
    """Runs both populations as ecologies on top of an :class:`EvolutionConfig`'s simulator settings."""

    def __init__(self, evo: EvolutionConfig, eco: Optional[EcologyConfig] = None, out_dir: Optional[str] = None, log: Optional[Callable[[str], None]] = print):
        self.evo = evo
        self.eco = eco or EcologyConfig()
        self.out_dir = out_dir
        self.log = log or (lambda s: None)
        retired = self.eco.retired_economy()
        if retired is not None:
            message = f"retired ecology economy (RBT-8): {retired}. Kept only so that paper 3's runs reproduce; use an absolute living cost instead."
            warnings.warn(message, stacklevel=2)
            self.log(message)
        self.rng = np.random.default_rng(evo.seed)
        self.runner = BoutRunner(evo.sim, evo.workers)
        evo.population_size = self.eco.capacity
        self.populations = {}
        self._names: set = set()
        seeds = {HOLISTIC: self.eco.seed_holistic or self.eco.seed_from, CONVENTIONAL: self.eco.seed_conventional or self.eco.seed_from}
        for kind in ORDER:
            if seeds[kind]:
                members = load_population(seeds[kind], kind, self.eco.capacity)
                self.log(f"{kind}: {len(members)} founders loaded from {seeds[kind]}")
            else:
                members = list(initial_population(kind, evo, self.rng).members)
            for m in members:
                saved_age = int(m.record.get("age", -1)) if seeds[kind] else -1
                age = saved_age if saved_age >= 0 else (int(self.rng.integers(0, self.eco.max_age)) if self.eco.stagger_ages else 0)
                m.record = {"energy": self.eco.initial_energy, "age": age, "evals": 0, "score_sum": 0.0, "born": -age, "kind": kind}
                m.parents = []
                m.name = self._claim_name(m.name)
            self.populations[kind] = members
        self.merged = False
        self.season = 0
        self.history: list[dict] = []
        self.counter = {HOLISTIC: len(self.populations[HOLISTIC]), CONVENTIONAL: len(self.populations[CONVENTIONAL])}
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, "config.json"), "w") as f:
                json.dump({**_jsonable(evo.to_dict()), "ecology": self.eco.__dict__}, f, indent=2)

    # -- names -------------------------------------------------------------- #
    def _claim_name(self, name: str) -> str:
        """Reserve `name`, suffixing it if a loaded population already used it."""
        base, i = name or "x", 1
        name = base
        while name in self._names:
            name, i = f"{base}-{i}", i + 1
        self._names.add(name)
        return name

    def _child_name(self, kind: str) -> str:
        self.counter[kind] += 1
        return self._claim_name(f"{'h' if kind == HOLISTIC else 'c'}e{self.counter[kind]}")

    # -- one season --------------------------------------------------------- #
    def _challenge(self, members: list, sim, start_seed) -> dict:
        """Run one season's challenge for a cohort sharing a world; returns index -> energy gain."""
        eco = self.eco
        if eco.challenge == "foraging":
            order = [int(i) for i in self.rng.permutation(len(members))]
            groups = [order[i : i + eco.group_size] for i in range(0, len(order), eco.group_size)]
            results = self.runner.run_groups([([members[i] for i in grp], start_seed) for grp in groups], sim)
            gains = {}
            for grp, res in zip(groups, results):
                for i, r in zip(grp, res):
                    gains[i] = r["score"]
            return gains
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
            return gains
        results = self.runner.run([(m, None, False, start_seed) for m in members], sim)
        return {i: r["fitness"][0] for i, r in enumerate(results)}

    def _merge(self) -> None:
        """Pool the two ecologies into one arena under one capacity (the interchange)."""
        self.merged = True
        counts = {kind: len(self.populations[kind]) for kind in ORDER}
        self.log(f"season {self.season}: the two ecologies merge into one arena, pooled capacity {self.eco.slots(True)} (holistic {counts[HOLISTIC]}, conventional {counts[CONVENTIONAL]})")

    def step(self) -> None:
        eco, evo = self.eco, self.evo
        if not self.merged and eco.merged_at(self.season):
            self._merge()
        terrain_seed = draw_terrain_seed(evo, self.rng)
        start_seed = draw_start_seeds(evo, self.rng)[0]
        sim = generation_sim(evo, terrain_seed, self.season)
        slots = eco.slots(self.merged)
        if self.merged:
            cohorts = [(ORDER, [m for kind in ORDER for m in self.populations[kind]])]
        else:
            cohorts = [((kind,), list(self.populations[kind])) for kind in ORDER]
        for kinds, members in cohorts:
            if not members:
                continue
            # 1. challenge: one world per cohort, so after the merge both fauna meet in it
            gains = self._challenge(members, sim, start_seed)
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
            alive, dead = [], []
            for m in members:
                ok = (m.record["energy"] > 0 or not eco.starvation) and m.record["age"] < eco.max_age
                (alive if ok else dead).append(m)
            deaths = {kind: sum(1 for m in dead if m.record["kind"] == kind) for kind in kinds}
            # 4. births (energy above threshold, a free slot; after the merge a slot freed by
            #    either fauna is open to the other, and only the pooled total is capped)
            births = {kind: 0 for kind in kinds}
            breeders = [m for m in alive if m.record["energy"] >= eco.birth_threshold]
            self.rng.shuffle(breeders)
            for parent in breeders:
                if len(alive) >= slots:
                    break
                kind = parent.record["kind"]
                mates = [m for m in breeders if m.record["kind"] == kind]
                other = None
                if eco.crossover_rate > 0 and len(mates) > 1 and self.rng.random() < eco.crossover_rate:
                    other = mates[int(self.rng.integers(0, len(mates)))]
                    if other is parent:
                        other = None
                child = self._breed(kind, parent, other)
                parent.record["energy"] -= eco.birth_cost
                child.record = {"energy": eco.birth_cost, "age": 0, "evals": 0, "score_sum": 0.0, "born": self.season + 1, "kind": kind}
                child.name = self._child_name(kind)
                alive.append(child)
                births[kind] += 1
            # 5. record, one row per fauna even when they share the arena
            for kind in kinds:
                self.populations[kind] = [m for m in alive if m.record["kind"] == kind]
                self._record(kind, cost=cost, slots=slots, births=births[kind], deaths=deaths[kind], terrain_seed=terrain_seed, start_seed=start_seed)
        self.season += 1

    def _record(self, kind: str, cost: float, slots: int, births: int, deaths: int, terrain_seed, start_seed) -> None:
        alive = self.populations[kind]
        scores = [m.record["score_sum"] / max(1, m.record["evals"]) for m in alive]
        ages = [m.record["age"] for m in alive]
        best = max(alive, key=lambda m: m.record["score_sum"] / max(1, m.record["evals"])) if alive else None
        entry = {"season": self.season, "population": kind, "alive": len(alive), "deaths": deaths, "births": births, "mean_lifetime_score": float(np.mean(scores)) if scores else 0.0, "best_lifetime_score": float(max(scores)) if scores else 0.0, "mean_age": float(np.mean(ages)) if ages else 0.0, "max_age": int(max(ages)) if ages else 0, "best_name": best.name if best else None, "terrain_seed": terrain_seed, "start_seed": start_seed, "living_cost": cost, "total_energy": float(sum(m.record["energy"] for m in alive)), "merged": self.merged, "capacity": slots}
        if best is not None:
            entry.update(_size_stats(best, self.evo.sim))
        self.history.append(entry)
        self._log_lineage(kind, alive)
        if best is not None and self.out_dir and self.season % 10 == 0:
            d = os.path.join(self.out_dir, kind)
            os.makedirs(d, exist_ok=True)
            best.save(os.path.join(d, f"best_gen{self.season:04d}.json"))

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


def population_files(path: str, kind: str) -> list:
    """Genotype files for `kind` under `path`.

    Accepts what a run leaves behind: a run directory (``RUN/<kind>/final``),
    a population directory itself, the ``RUN/<kind>`` directory of
    ten-season bests, or a single genotype file.
    """
    p = str(path)
    for cand in (os.path.join(p, kind, "final"), os.path.join(p, "final"), os.path.join(p, kind), p):
        if os.path.isdir(cand):
            files = [f for f in sorted(glob.glob(os.path.join(cand, "*.json"))) if os.path.basename(f) not in ("config.json", "history.json")]
            if files:
                return files
    if os.path.isfile(p):
        return [p]
    return []


def load_population(path: str, kind: str, count: int) -> list:
    """Load `count` founders of `kind` from a saved population.

    Fewer files than slots are cycled (the extra copies are clones, not
    fresh draws); more files than slots are truncated in filename order, so
    the same path and count always give the same founders.
    """
    files = population_files(path, kind)
    if not files:
        raise FileNotFoundError(f"no {kind} genotypes under {path!r} (looked for {kind}/final, final, {kind}, and *.json)")
    members = []
    for i in range(count):
        g = Genotype.load(files[i % len(files)])
        members.append(g)
    return members


def _jsonable(obj):
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    return obj
