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

Randomness comes from three streams (RBT-95, mirroring RBT-85's arena change):
one per fauna and one for the terrain, spawned from the seed by
:func:`rabbitstew.evolution.spawn_streams`.  A fauna's stream feeds its
founders, their staggered ages, its seasons' groupings and arena draws, its
breeders' order and mate choice and its children's mutations; the terrain
stream feeds each season's terrain and start seeds.  Nothing one fauna does
can move the other's draws or the worlds, so two runs at one seed that differ
on one fauna's side are a pair.  After a merge the pooled cohort's groupings,
breeding order, crossover decisions and mate choices are drawn from the
holistic stream (each child's own crossover and mutation still from its kind's):
the merge couples the fauna by design, and this is how.  The pair then holds
on founders, ages and worlds for the whole run, and on the comparator's own
reproduction draws only until the first birth or death the contest decides
differently, since energy gates breeding and energy is the contest.  Ecology runs made before the streams
existed drew everything from one generator and do not reproduce from their
configs under this code; their genomes and cohorts on disk are their record.

The run is checkpointed to ``state.json`` after every season and resumes
with :meth:`Ecology.resume`, byte for byte.
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

from .evolution import CONVENTIONAL, HOLISTIC, STREAMS, TERRAIN, BoutRunner, EvolutionConfig, _size_stats, draw_start_seeds, generation_sim, initial_population, spawn_streams
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
    save_genomes: bool = True  #: write every individual's genotype once, when it is born, so any season's cohort can be rebuilt by name (RBT-27); off trades reproducibility for disk
    log_every: int = 1
    shift_at: Optional[int] = None  #: the onset (RBT-95): the season from which `shift` is in force, applied before that season's challenge; energy, age, descent and every stream continue
    shift: Optional[str] = None  #: exactly one parameter, as ``FLAG=VALUE``: an ecology field by name (``group_size=8``) or a simulator field by dotted path (``food.items=6``, ``food.work_cost=0.08``, ``world.terrain=flat``)
    cull_at: Optional[int] = None  #: the random cull (RBT-95): at this season, before its challenge, `cull` living individuals of each fauna are removed, drawn uniformly by that fauna's own stream
    breed_stream: Optional[int] = None  #: the replicate history (RBT-105): K >= 1 replaces the holistic stream, once the founders and their ages are drawn, by an independent one spawned from (seed, K); the founders and every other stream are untouched, and everything the holistic fauna draws afterwards (groupings, arena draws, breeding order, mate choice, crossover, mutation, culls) comes from the new one.  None or 0 is the original stream, byte for byte
    cull: Optional[str] = None  #: how many of each fauna, ``holistic=K1,conventional=K2`` (a bare ``N`` means N of each); the protocol's k is each fauna's own excess deaths, so the two differ and one is often 0, and a 0 draws nothing from that fauna's stream; each is written to lineage.jsonl as a row with ``death: cull`` and counted in the season's deaths; the slots stay free for the economy's own breeding

    #: ``--shift`` accepts RBT-89's challenge flags by their CLI names as well as the field they set
    SHIFT_ALIASES = {"group-size": "group_size", "work-cost": "food.work_cost", "food-items": "food.items", "terrain": "world.terrain"}

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

    #: ecology fields a shift may not touch: not challenge flags, or not changeable in place
    UNSHIFTABLE = ("seasons", "capacity", "merge_after", "pooled_capacity", "seed_from", "seed_holistic", "seed_conventional", "save_genomes", "log_every", "shift_at", "shift", "cull_at", "cull", "breed_stream")

    def merged_at(self, season: int) -> bool:
        return self.merge_after is not None and season >= self.merge_after

    def slots(self, merged: bool) -> int:
        """Capacity in force: per population before the merge, pooled after it."""
        if not merged:
            return self.capacity
        return self.pooled_capacity if self.pooled_capacity is not None else 2 * self.capacity


class Ecology:
    """Runs both populations as ecologies on top of an :class:`EvolutionConfig`'s simulator settings."""

    def __init__(self, evo: EvolutionConfig, eco: Optional[EcologyConfig] = None, out_dir: Optional[str] = None,
                 log: Optional[Callable[[str], None]] = print, trait: Optional[Callable[[Genotype], float]] = None,
                 trait_threshold: float = 0.0, trait_name: str = "trait"):
        """``trait`` measures one scalar on a living genotype and is summarised into every season's
        history entry: how many of the living population carry it at or above ``trait_threshold``,
        and the spread of the scalar itself.

        It exists because the champion is the wrong witness for "is this trait retained?" (RBT-79).
        ``best_gen####.json`` is selected on ``best_lifetime_score``, so for any trait that helps a
        robot forage the saved champion over-reports carriage -- in RBT-65's *drift* arm as much as
        in its selected one, which is why flattening the economy did not give that run a usable
        control.  A count over the living population is the quantity the question actually asks for.
        """
        self.evo = evo
        self.eco = eco or EcologyConfig()
        self.out_dir = out_dir
        self.log = log or (lambda s: None)
        self.trait = trait
        self.trait_threshold = float(trait_threshold)
        self.trait_name = trait_name
        # A genotype never changes after it is born, so the scalar is cached by name: a population of
        # sixty with a couple of births a season costs a couple of evaluations a season rather than
        # sixty, which is what makes an expensive predicate (one that has to synthesise or simulate)
        # affordable every season instead of every Nth.
        self._trait_cache: dict = {}
        retired = self.eco.retired_economy()
        if retired is not None:
            message = f"retired ecology economy (RBT-8): {retired}. Kept only so that paper 3's runs reproduce; use an absolute living cost instead."
            warnings.warn(message, stacklevel=2)
            self.log(message)
        self.rngs = spawn_streams(evo.seed)
        self.shifted: Optional[dict] = None  # the shift record, once the onset has passed
        self._shift = self._resolve_shift()
        self._cull_counts = self._resolve_cull()
        self._culls: dict = {}  # kind -> how many the current season's cull removed
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
                members = list(initial_population(kind, evo, self.rngs[kind]).members)
            for m in members:
                saved_age = int(m.record.get("age", -1)) if seeds[kind] else -1
                age = saved_age if saved_age >= 0 else (int(self.rngs[kind].integers(0, self.eco.max_age)) if self.eco.stagger_ages else 0)
                m.record = {"energy": self.eco.initial_energy, "age": age, "evals": 0, "score_sum": 0.0, "born": -age, "kind": kind}
                m.parents = []
                m.name = self._claim_name(m.name)
            self.populations[kind] = members
        if self.eco.breed_stream:
            # The founders and their ages are drawn; from here on the holistic fauna's history comes from a
            # replicate stream.  spawn_key (index, K) is the K-th child of the original holistic stream's
            # SeedSequence, so it is independent of it and of every other stream (RBT-105).
            if int(self.eco.breed_stream) < 0:
                raise ValueError(f"breed_stream must be >= 0 (0 is the original stream), got {self.eco.breed_stream}")
            self.rngs[HOLISTIC] = np.random.default_rng(np.random.SeedSequence(evo.seed, spawn_key=(STREAMS.index(HOLISTIC), int(self.eco.breed_stream))))
            self.log(f"{HOLISTIC}: founders drawn from the original stream; its history from replicate stream {self.eco.breed_stream}")
        self.merged = False
        self.season = 0
        self.history: list[dict] = []
        # The persistent world (RBT-19): when food regrows at its own spot after a delay, arena food
        # state carries across seasons instead of being re-seeded, so a season starts in a world the
        # season before ate from.  Each cohort keeps its own bank of arenas: the two fauna live in
        # separate ecologies, and sharing food would couple them.
        food = evo.sim.food
        self.persistent = bool(food is not None and food.regrow_delay > 0 and self.eco.challenge == "foraging")
        self.arenas: dict = {}
        self.arena_log: list[dict] = []
        self.counter = {HOLISTIC: len(self.populations[HOLISTIC]), CONVENTIONAL: len(self.populations[CONVENTIONAL])}
        for kind in ORDER:
            for m in self.populations[kind]:
                self._save_genome(kind, m)
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

    # -- persistent arenas -------------------------------------------------- #
    def _arena_bank(self, key: tuple, wanted: int) -> list:
        """The cohort's persistent arenas, created on demand.  An arena is a food seed (its layout
        is drawn from it the first time a group stands in it, so the clearance rule still applies)
        and the food state it was last left in."""
        bank = self.arenas.setdefault(key, [])
        while len(bank) < wanted:
            bank.append({"seed": int(self.rngs[key[0]].integers(0, 2**31 - 1)), "state": None})
        return bank

    def _age_arena(self, state: Optional[dict], dt: float) -> Optional[dict]:
        """Run an unvisited arena's clock forward by one season: the world regrows everywhere, not
        only where somebody was standing."""
        if state is None:
            return None
        alive, timer = list(state["alive"]), list(state["timer"])
        for j, (a, t) in enumerate(zip(alive, timer)):
            if a or not np.isfinite(t):
                continue
            t -= dt
            if t <= 0:
                alive[j], timer[j] = True, 0.0
            else:
                timer[j] = t
        return {**state, "alive": alive, "timer": timer}

    @staticmethod
    def _crop(state: Optional[dict], items: int) -> tuple:
        """(items standing, spots) in an arena; an uncreated arena is a full one."""
        if state is None:
            return items, items
        return int(sum(bool(a) for a in state["alive"])), len(state["alive"])

    # -- one season --------------------------------------------------------- #
    @staticmethod
    def _gain(row: dict) -> dict:
        """Apply the forfeit to one challenge result (RBT-30).

        A robot that went numerically unstable gains nothing, whatever the challenge, so its
        energy moves by the living cost alone.  Without this an exploder either books the work
        its diverging integrator ran up (foraging) or keeps whatever it scored before it went
        (solo), and either way the record cannot tell it from a robot that simply did badly.
        """
        if row.get("exploded"):
            row["gain"] = 0.0
        return row

    def _challenge(self, members: list, sim, start_seed, key: tuple = ()) -> dict:
        """Run one season's challenge for a cohort sharing a world.

        Returns index -> the whole per-robot result, not only the number that feeds energy
        (RBT-27): every row carries ``gain`` and ``exploded``, a foraging row adds the items,
        work and displacement behind the gain, and a solo row its distance from the target.
        Keeping the decomposition is the point: a gain of zero from an empty arena and a gain
        of zero paid away in work are different seasons, and the work-cost arms and the yield
        heritability estimate are measured on exactly that difference.
        """
        eco = self.eco
        rng = self.rngs[key[0]] if key else self.rngs[HOLISTIC]
        if eco.challenge == "foraging":
            order = [int(i) for i in rng.permutation(len(members))]
            groups = [order[i : i + eco.group_size] for i in range(0, len(order), eco.group_size)]
            if self.persistent:
                return self._persistent_forage(members, groups, sim, start_seed, key)
            results = self.runner.run_groups([([members[i] for i in grp], start_seed) for grp in groups], sim)
            rows = {}
            for grp, res in zip(groups, results):
                for i, r in zip(grp, res):
                    rows[i] = self._gain({"gain": r["score"], "food": r["food"], "work": r["work"], "path": r["path"], "exploded": r["exploded"]})
            self._record_cohort(key, groups, members, start_seed)
            return rows
        if eco.challenge == "paired" and len(members) > 1:
            order = rng.permutation(len(members))
            pairs, owners = [], []
            for a, b in zip(order[::2], order[1::2]):
                pairs.append((members[a], members[b], False, start_seed))
                owners.append((a, b))
            results = self.runner.run(pairs, sim)
            rows = {}
            for (a, b), r in zip(owners, results):
                for seat, i in enumerate((a, b)):
                    rows[i] = self._gain({"gain": r["fitness"][seat], "distance": r["distances"][seat], "exploded": bool(r["exploded"][seat]), "opponent": members[b if seat == 0 else a].name})
            if len(members) % 2:
                rows[int(order[-1])] = {"gain": 0.5, "exploded": False, "bye": True}  # the odd one out sits the season out at parity
            self._record_cohort(key, [list(o) for o in owners], members, start_seed)
            return rows
        results = self.runner.run([(m, None, False, start_seed) for m in members], sim)
        rows = {i: self._gain({"gain": r["fitness"][0], "distance": r["distances"][0], "time_at_target": r["time_at_target"][0], "exploded": bool(r["exploded"][0])}) for i, r in enumerate(results)}
        self._record_cohort(key, [[i] for i in range(len(members))], members, start_seed)
        return rows

    def _persistent_forage(self, members: list, groups: list, sim, start_seed, key: tuple) -> dict:
        """A foraging season in persistent arenas: groups are assigned to arenas at random, each
        takes the food the last occupants left, and every other arena's clock runs on too."""
        eco, items = self.eco, self.evo.sim.food.items
        bank = self._arena_bank(key, max(len(groups), eco.slots(self.merged) // max(1, eco.group_size), 1))
        picks = [int(i) for i in self.rngs[key[0]].permutation(len(bank))[: len(groups)]]
        standing = [self._crop(bank[a]["state"], items) for a in picks]
        tasks = [([members[i] for i in grp], start_seed, bank[a]["state"], bank[a]["seed"]) for grp, a in zip(groups, picks)]
        entry_state = [bank[a]["state"] for a in picks]
        out = self.runner.run_persistent_groups(tasks, sim)
        rows, harvest = {}, []
        for grp, a, (res, state) in zip(groups, picks, out):
            bank[a]["state"] = state
            harvest.append(sum(float(r["food"]) for r in res))
            for i, r in zip(grp, res):
                rows[i] = self._gain({"gain": r["score"], "food": r["food"], "work": r["work"], "path": r["path"], "exploded": r["exploded"], "arena": a})
        self._record_cohort(key, groups, members, start_seed, arenas=[{"index": a, "seed": bank[a]["seed"], "state": st} for a, st in zip(picks, entry_state)])
        for a in set(range(len(bank))) - set(picks):  # the arenas nobody visited still regrow
            bank[a]["state"] = self._age_arena(bank[a]["state"], self.evo.sim.duration)
        crop = [c for c, _ in standing]
        spots = sum(n for _, n in standing) or 1
        self.arena_log.append({"season": self.season, "population": "+".join(key), "arenas": len(bank), "groups": len(groups),
                               "season_start_crop_mean": float(np.mean(crop)) if crop else 0.0,
                               "empty_fraction": 1.0 - sum(crop) / spots,
                               "harvest_per_group": float(np.mean(harvest)) if harvest else 0.0,
                               "harvest_total": float(sum(harvest))})
        return rows

    def _merge(self) -> None:
        """Pool the two ecologies into one arena under one capacity (the interchange)."""
        self.merged = True
        counts = {kind: len(self.populations[kind]) for kind in ORDER}
        self.log(f"season {self.season}: the two ecologies merge into one arena, pooled capacity {self.eco.slots(True)} (holistic {counts[HOLISTIC]}, conventional {counts[CONVENTIONAL]})")

    # -- the onset (RBT-95) ------------------------------------------------- #
    def _resolve_shift(self) -> Optional[tuple]:
        """``(owner, attribute, value)`` for ``eco.shift``, checked now so a bad flag fails before a season runs."""
        eco = self.eco
        if eco.shift is None and eco.shift_at is None:
            return None
        if eco.shift is None or eco.shift_at is None:
            raise ValueError("shift_at and shift go together: the season of the onset and the one FLAG=VALUE in force from it")
        if "=" not in eco.shift:
            raise ValueError(f"shift {eco.shift!r} is not FLAG=VALUE")
        flag, raw = eco.shift.split("=", 1)
        flag = eco.SHIFT_ALIASES.get(flag.strip().lstrip("-"), flag.strip())
        if "." in flag:
            owner, *path, attr = [self.evo.sim] + flag.split(".")
            for name in path:
                if not hasattr(owner, name):
                    raise ValueError(f"shift {eco.shift!r}: the simulator has no {name!r}")
                owner = getattr(owner, name)
            if owner is None or not hasattr(owner, attr):
                raise ValueError(f"shift {eco.shift!r}: no such simulator field")
            persistent = self.evo.sim.food is not None and self.evo.sim.food.regrow_delay > 0 and eco.challenge == "foraging"
            if persistent and owner is self.evo.sim.food and attr in ("items", "patches", "patch_radius"):
                raise ValueError(f"shift {eco.shift!r}: the persistent world's arenas hold food state laid out under the old value; not shiftable in place")
            if owner is self.evo.sim.food and attr == "regrow_delay":
                raise ValueError(f"shift {eco.shift!r}: whether the world is persistent is fixed at construction (Ecology.persistent), so regrow_delay cannot be shifted in place")
        else:
            owner, attr = eco, flag
            if attr in eco.UNSHIFTABLE or not hasattr(eco, attr):
                raise ValueError(f"shift {eco.shift!r}: not a shiftable ecology field")
        current = getattr(owner, attr)
        try:
            value = json.loads(raw)
        except ValueError:
            value = raw.strip()
        if isinstance(current, bool):
            value = bool(value)
        elif isinstance(current, int) and not isinstance(value, bool):
            value = int(value)
        elif isinstance(current, float):
            value = float(value)
        elif isinstance(current, str):
            value = str(value)
        return owner, attr, value

    def _apply_shift(self) -> None:
        owner, attr, value = self._shift
        setattr(owner, attr, value)
        self.shifted = {"at": int(self.eco.shift_at), "flag": attr if owner is self.eco else self.eco.SHIFT_ALIASES.get(self.eco.shift.split("=", 1)[0].strip().lstrip("-"), self.eco.shift.split("=", 1)[0].strip()), "value": value}
        self.log(f"season {self.season}: onset, {self.shifted['flag']} = {value!r} from here on; energy, age, descent and every stream continue")

    # -- the random cull (RBT-95) ------------------------------------------- #
    def _resolve_cull(self) -> dict:
        """``{kind: count}`` for ``eco.cull``, checked now; ``{}`` when there is no cull."""
        eco = self.eco
        if eco.cull is None and eco.cull_at is None:
            return {}
        if eco.cull is None or eco.cull_at is None:
            raise ValueError("cull_at and cull go together: the season of the cull and how many of each fauna it removes (holistic=K1,conventional=K2)")
        spec = str(eco.cull).strip()
        counts = {kind: 0 for kind in ORDER}
        try:
            if "=" not in spec:
                counts = {kind: int(spec) for kind in ORDER}
            else:
                for part in spec.split(","):
                    kind, n = part.split("=", 1)
                    if kind.strip() not in counts:
                        raise ValueError(kind)
                    counts[kind.strip()] = int(n)
        except ValueError:
            raise ValueError(f"cull {eco.cull!r} is not holistic=K1,conventional=K2 (or a bare N for both)") from None
        if any(n < 0 for n in counts.values()) or not any(counts.values()):
            raise ValueError(f"cull {eco.cull!r}: counts are non-negative and at least one is positive")
        return counts

    def _cull(self) -> None:
        """Remove each fauna's stated number of living individuals, chosen uniformly without
        replacement by that fauna's own stream: the protocol's null for a challenge, a turnover of
        stated size with nothing else changed (``docs/held-out-challenges.md`` section 8).  A fauna
        whose count is 0 draws nothing, so its stream is exactly where the control's is.  Each is
        written to the lineage as its last observation with ``death: cull``; the slots are left free."""
        for kind in ORDER:
            members = self.populations[kind]
            n = min(self._cull_counts.get(kind, 0), len(members))
            picked = set(int(i) for i in self.rngs[kind].choice(len(members), size=n, replace=False)) if n else set()
            gone = [m for i, m in enumerate(members) if i in picked]
            self.populations[kind] = [m for i, m in enumerate(members) if i not in picked]
            self._log_lineage(kind, gone, extra={"death": "cull"})
            self._culls[kind] = n
            if n:
                self.log(f"season {self.season}: cull, {n} of {len(members)} {kind} removed at random ({', '.join(m.name for m in gone)}); the slots stay free")

    def step(self) -> None:
        eco, evo = self.eco, self.evo
        self._culls = {}
        if self._shift is not None and self.shifted is None and self.season >= eco.shift_at:
            self._apply_shift()
        if self._cull_counts and self.season == eco.cull_at:
            self._cull()
        if not self.merged and eco.merged_at(self.season):
            self._merge()
        # One draw from the terrain stream every season whatever the terrain, used as the terrain seed only when the
        # terrain is random and unfixed: a shift to flat terrain then keeps the start seeds paired with the control's
        # instead of falling one draw behind it (RBT-95's items 1-2 adversary).  Experiment keeps draw_terrain_seed.
        draw = int(self.rngs[TERRAIN].integers(0, 2**31 - 1))
        world = evo.sim.world
        terrain_seed = None if world.terrain != "random" else (int(world.terrain_seed) if world.terrain_seed is not None else draw)
        start_seed = draw_start_seeds(evo, self.rngs[TERRAIN])[0]
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
            rows = self._challenge(members, sim, start_seed, key=tuple(kinds))
            # 2. energy, age, records
            cost = eco.cost([float((rows.get(i) or {}).get("gain", 0.0)) for i in range(len(members))])
            for i, m in enumerate(members):
                rec = m.record
                row = rows.get(i) or {"gain": 0.0}
                g = float(row.get("gain", 0.0))
                rec["energy"] = rec["energy"] + g - cost
                rec["age"] += 1
                rec["evals"] += 1
                rec["score_sum"] += g
                rec["last_score"] = g
                rec["last"] = row  # the whole season, for the lineage row
            # 3. deaths
            alive, dead = [], []
            for m in members:
                ok = (m.record["energy"] > 0 or not eco.starvation) and m.record["age"] < eco.max_age
                (alive if ok else dead).append(m)
            deaths = {kind: sum(1 for m in dead if m.record["kind"] == kind) + self._culls.get(kind, 0) for kind in kinds}
            # 4. births (energy above threshold, a free slot; after the merge a slot freed by
            #    either fauna is open to the other, and only the pooled total is capped)
            births = {kind: 0 for kind in kinds}
            breeders = [m for m in alive if m.record["energy"] >= eco.birth_threshold]
            rng = self.rngs[kinds[0]]  # the cohort's stream: its own fauna's before the merge, holistic after
            rng.shuffle(breeders)
            for parent in breeders:
                if len(alive) >= slots:
                    break
                kind = parent.record["kind"]
                mates = [m for m in breeders if m.record["kind"] == kind]
                other = None
                if eco.crossover_rate > 0 and len(mates) > 1 and rng.random() < eco.crossover_rate:
                    other = mates[int(rng.integers(0, len(mates)))]
                    if other is parent:
                        other = None
                child = self._breed(kind, parent, other)
                parent.record["energy"] -= eco.birth_cost
                child.record = {"energy": eco.birth_cost, "age": 0, "evals": 0, "score_sum": 0.0, "born": self.season + 1, "kind": kind}
                child.name = self._child_name(kind)
                self._save_genome(kind, child)
                alive.append(child)
                births[kind] += 1
            # 5. record, one row per fauna even when they share the arena
            for kind in kinds:
                self.populations[kind] = [m for m in alive if m.record["kind"] == kind]
                self._record(kind, cost=cost, slots=slots, births=births[kind], deaths=deaths[kind], terrain_seed=terrain_seed, start_seed=start_seed)
        self.season += 1

    def _trait_summary(self, alive: list) -> dict:
        """Carriage of ``self.trait`` over the living population, for one season's history entry."""
        if self.trait is None:
            return {}
        vals = []
        for m in alive:
            if m.name not in self._trait_cache:
                self._trait_cache[m.name] = float(self.trait(m))
            vals.append(self._trait_cache[m.name])
        if not vals:
            return {"trait": self.trait_name, "trait_threshold": self.trait_threshold,
                    "carriers": 0, "carrier_fraction": 0.0}
        a = np.asarray(vals, dtype=float)
        carriers = int((a >= self.trait_threshold).sum())
        return {"trait": self.trait_name, "trait_threshold": self.trait_threshold,
                "carriers": carriers, "carrier_fraction": carriers / len(a),
                "trait_median": float(np.median(a)), "trait_q1": float(np.percentile(a, 25)),
                "trait_q3": float(np.percentile(a, 75)), "trait_min": float(a.min()),
                "trait_max": float(a.max())}

    def _record(self, kind: str, cost: float, slots: int, births: int, deaths: int, terrain_seed, start_seed) -> None:
        alive = self.populations[kind]
        scores = [m.record["score_sum"] / max(1, m.record["evals"]) for m in alive]
        ages = [m.record["age"] for m in alive]
        best = max(alive, key=lambda m: m.record["score_sum"] / max(1, m.record["evals"])) if alive else None
        entry = {"season": self.season, "population": kind, "alive": len(alive), "deaths": deaths, "births": births, "mean_lifetime_score": float(np.mean(scores)) if scores else 0.0, "best_lifetime_score": float(max(scores)) if scores else 0.0, "mean_age": float(np.mean(ages)) if ages else 0.0, "max_age": int(max(ages)) if ages else 0, "best_name": best.name if best else None, "terrain_seed": terrain_seed, "start_seed": start_seed, "living_cost": cost, "total_energy": float(sum(m.record["energy"] for m in alive)), "merged": self.merged, "capacity": slots}
        if best is not None:
            entry.update(_size_stats(best, self.evo.sim))
        if self.shifted is not None:
            entry["shift"] = dict(self.shifted)
        if self._culls:
            entry["culled"] = dict(self._culls)  # both fauna's counts, on each fauna's row of the cull season
        entry.update(self._trait_summary(alive))
        self.history.append(entry)
        self._log_lineage(kind, alive)
        if best is not None and self.out_dir and self.season % 10 == 0:
            d = os.path.join(self.out_dir, kind)
            os.makedirs(d, exist_ok=True)
            best.save(os.path.join(d, f"best_gen{self.season:04d}.json"))

    def _breed(self, kind: str, parent: Genotype, other: Optional[Genotype]) -> Genotype:
        evo, rng = self.evo, self.rngs[kind]
        if kind == HOLISTIC:
            child = crossover(parent, other, rng) if other is not None else parent.copy()
            child = mutate(child, rng, evo.mutation)
        elif evo.conventional_topology:
            child = crossover_controller(parent, other, rng) if other is not None else parent.copy()
            child = mutate_controller(child, rng, evo.mutation)
            assert body_signature(child) == body_signature(parent)
        else:
            child = crossover_weights(parent, other, rng) if other is not None else parent.copy()
            child = mutate_weights(child, rng, evo.mutation)
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
            self.save_state()
            if all(len(m) == 0 for m in self.populations.values()):
                self.log("everyone died")
                break
        self.runner.close()
        self._save_populations()
        return {"history": self.history}

    # -- checkpointing ------------------------------------------------------ #
    STATE_FILE = "state.json"

    def save_state(self) -> None:
        """Write everything a resume needs (RBT-95): both fauna with their records, the names
        taken, the season, the merge, the history, the persistent arenas and every stream."""
        if not self.out_dir:
            return
        state = {
            "season": self.season, "merged": self.merged,
            "populations": {kind: [m.to_dict() for m in members] for kind, members in self.populations.items()},
            "names": sorted(self._names), "counter": dict(self.counter),
            "history": self.history, "arena_log": self.arena_log,
            "arenas": {"+".join(k): bank for k, bank in self.arenas.items()},
            "rngs": {name: rng.bit_generator.state for name, rng in self.rngs.items()},
        }
        tmp = os.path.join(self.out_dir, self.STATE_FILE + ".tmp")
        with open(tmp, "w") as f:
            json.dump(_jsonable(state), f)
        os.replace(tmp, os.path.join(self.out_dir, self.STATE_FILE))

    @staticmethod
    def resume(out_dir: str, seasons: Optional[int] = None, workers: Optional[int] = None, log: Optional[Callable[[str], None]] = print,
               trait: Optional[Callable[[Genotype], float]] = None, trait_threshold: float = 0.0, trait_name: str = "trait") -> "Ecology":
        """Rebuild an ecology from ``out_dir`` and continue it from the season after the last saved one.

        ``seasons`` may raise the target.  The logs are cut back to the restart season first, so a
        season the killed attempt had already written is not written twice (RBT-93).  A trait
        predicate is a callable and is not checkpointed: hand it back as ``trait`` (its cache refills
        by name) or the resumed seasons carry no carriage columns.  ``config.json`` is rewritten from
        its own contents with only ``seasons`` and ``workers`` updated, so a seeded run's seed paths
        stay on record; the founders come from the state, not from those paths.
        """
        with open(os.path.join(out_dir, "config.json")) as f:
            raw = json.load(f)
        if "ecology" not in raw:
            raise ValueError(f"{out_dir} is not an ecology run (its config.json has no 'ecology' section); an arena run resumes with `evolve --resume`")
        on_disk = dict(raw)
        eco = EcologyConfig(**raw.pop("ecology"))
        evo = EvolutionConfig.from_dict(raw)
        if seasons is not None:
            eco.seasons = seasons
        if workers is not None:
            evo.workers = workers
        with open(os.path.join(out_dir, Ecology.STATE_FILE)) as f:
            state = json.load(f)
        missing = [name for name in STREAMS if name not in state.get("rngs", {})]
        if missing:
            raise ValueError(f"{out_dir}/state.json carries no state for the {', '.join(missing)} stream(s): it was written under the ecology's single RNG stream (before RBT-95) or is damaged, and cannot be resumed under per-fauna streams; rerun it from its config")
        eco.seed_from = eco.seed_holistic = eco.seed_conventional = None  # in memory only: the founders are in the state, not on the seed path
        e = Ecology(evo, eco, out_dir=None, log=log, trait=trait, trait_threshold=trait_threshold, trait_name=trait_name)
        e.out_dir = out_dir
        on_disk["ecology"] = {**on_disk["ecology"], "seasons": eco.seasons}
        on_disk["workers"] = evo.workers
        with open(os.path.join(out_dir, "config.json"), "w") as f:
            json.dump(on_disk, f, indent=2)
        e.season, e.merged = int(state["season"]), bool(state["merged"])
        e.populations = {kind: [Genotype.from_dict(m) for m in members] for kind, members in state["populations"].items()}
        e._names, e.counter = set(state["names"]), {k: int(v) for k, v in state["counter"].items()}
        e.history, e.arena_log = state["history"], state["arena_log"]
        e.arenas = {tuple(k.split("+")): bank for k, bank in state["arenas"].items()}
        for name in STREAMS:
            e.rngs[name].bit_generator.state = state["rngs"][name]
        if e._shift is not None and e.season > eco.shift_at:
            e._apply_shift()  # the onset is behind the restart: the shifted value is in force
        e._truncate_logs(e.season)
        return e

    def _truncate_logs(self, season: int) -> None:
        """Drop lineage and cohort rows at or after ``season``: what a killed attempt wrote for the
        season it did not finish, which the resume is about to write again (RBT-93)."""
        for name, key in (("lineage.jsonl", "generation"), ("cohorts.jsonl", "season")):
            path = os.path.join(self.out_dir, name)
            if not os.path.exists(path):
                continue
            with open(path) as f:
                lines = f.readlines()
            keep = []
            for i, l in enumerate(lines):
                if not l.strip():
                    keep.append(l)
                    continue
                try:
                    row = json.loads(l)
                except ValueError:
                    if i == len(lines) - 1:
                        continue  # a torn final row: the write a kill interrupted, part of the unfinished season this cut drops anyway
                    raise ValueError(f"{path} line {i + 1} is not JSON and is not the last line; the log is damaged beyond what a resume can cut back") from None
                if row[key] < season:
                    keep.append(l)
            if len(keep) != len(lines):
                with open(path, "w") as f:
                    f.writelines(keep)

    # -- persistence ------------------------------------------------------- #
    def _save_genome(self, kind: str, g: Genotype) -> None:
        """Save an individual's genotype once, as it enters the population (RBT-27).

        A genotype does not change after it is bred, so one file per individual ever born is
        the whole history of the fauna, at a fraction of what a per-season snapshot of the
        population would cost.  With `cohorts.jsonl` naming who stood in which arena, that is
        what any season needs to be rebuilt exactly rather than approximated.
        """
        if not (self.out_dir and self.eco.save_genomes):
            return
        d = os.path.join(self.out_dir, kind, "genomes")
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, f"{g.name}.json")
        if not os.path.exists(path):
            g.save(path)

    def _record_cohort(self, key: tuple, groups: list, members: list, start_seed, arenas: Optional[list] = None) -> None:
        """Who faced the season together, in seat order, by name and fauna.

        The draw is made from this run's rng and is otherwise unrecoverable, so without it a
        season's arena can only be guessed at.  A persistent arena also carries the food state
        the group walked into, since that is the season before's leavings and no seed gives it
        back.  Kinds are recorded per seat because after the merge one cohort holds both.
        """
        if not self.out_dir:
            return
        row = {"season": self.season, "cohort": "+".join(key), "challenge": self.eco.challenge, "start_seed": start_seed,
               "groups": [[{"name": members[i].name, "kind": members[i].record["kind"]} for i in grp] for grp in groups]}
        if arenas is not None:
            row["arenas"] = arenas
        with open(os.path.join(self.out_dir, "cohorts.jsonl"), "a") as f:  # appended, never held: a persistent arena's state is bulky
            f.write(json.dumps(row) + "\n")

    def _log_lineage(self, kind: str, members: list, extra: Optional[dict] = None) -> None:
        """One row per member as of now; ``extra`` marks rows that are not the living population (a cull's dead)."""
        if not self.out_dir:
            return
        with open(os.path.join(self.out_dir, "lineage.jsonl"), "a") as f:
            for m in members:
                rec = {"generation": self.season, "population": kind, "name": m.name, "parents": list(m.parents), "fitness": round(m.record["score_sum"] / max(1, m.record["evals"]), 4), "nodes": len(m.nodes), "energy": round(m.record["energy"], 3), "age": m.record["age"], "evals": m.record["evals"], "last_score": round(float(m.record.get("last_score", 0.0)), 4)}
                rec.update(_season_fields(m.record.get("last")))
                if extra:
                    rec.update(extra)
                f.write(json.dumps(rec) + "\n")

    def _flush(self) -> None:
        if self.out_dir:
            with open(os.path.join(self.out_dir, "history.json"), "w") as f:
                json.dump({"history": self.history, "champions": [], "ecology": True}, f)
            self._flush_arenas()

    def _flush_arenas(self) -> None:
        """The persistent world's food, beside history.json: the per-season standing crop and the
        arenas themselves, so a run's supply can be read back without re-simulating it."""
        if not (self.out_dir and self.persistent):
            return
        arenas = {"+".join(k): [{"seed": a["seed"], "state": a["state"]} for a in bank] for k, bank in self.arenas.items()}
        with open(os.path.join(self.out_dir, "arenas.json"), "w") as f:
            json.dump({"seasons": self.arena_log, "arenas": arenas, "items": self.evo.sim.food.items,
                       "regrow_delay": self.evo.sim.food.regrow_delay, "patches": self.evo.sim.food.patches,
                       "patch_radius": self.evo.sim.food.patch_radius, "duration": self.evo.sim.duration}, f)

    def _save_populations(self) -> None:
        if not self.out_dir:
            return
        for kind, members in self.populations.items():
            d = os.path.join(self.out_dir, kind, "final")
            os.makedirs(d, exist_ok=True)
            for i, m in enumerate(members):
                m.save(os.path.join(d, f"{i:03d}.json"))


#: what a season's own result contributes to an individual's lineage row, rounded for the log
SEASON_FIELDS = ("food", "work", "path", "distance", "time_at_target", "exploded", "arena", "opponent", "bye")


def _season_fields(row: Optional[dict]) -> dict:
    """The season's result as lineage-row fields, whichever of them this challenge measures."""
    if not row:
        return {}
    out = {}
    for k in SEASON_FIELDS:
        if k in row:
            v = row[k]
            out[k] = round(float(v), 4) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
    return out


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
