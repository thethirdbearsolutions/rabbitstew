"""The competitive simulation.

A :class:`Simulation` synthesises one or more genotypes, instantiates them in
a MuJoCo world, and steps physics and brains together.  :func:`run_bout` runs
the paper's two-robot, time-limited zero-sum game: each robot's fitness is
the ratio of the *opponent's* final centre-of-mass distance from the world
centre to the sum of both distances, so reaching the centre and keeping the
opponent away from it are both rewarded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import mujoco
import numpy as np

from .brain import RuntimeBrain
from .genotype import Genotype
from .synthesis import Phenotype, SynthesisConfig, synthesize
from .trajectory import Trajectory, UnitSpec
from .world import RobotIndex, Spawn, WorldConfig, build_model


@dataclass
class SimConfig:
    synthesis: SynthesisConfig = field(default_factory=SynthesisConfig)
    world: WorldConfig = field(default_factory=WorldConfig)
    control_substeps: int = 4  #: physics steps per brain update
    duration: float = 10.0  #: seconds of simulated time per bout
    start_distance: float = 2.0  #: robots start this far from the centre, on opposite sides
    target: tuple = (0.0, 0.0, 0.0)  #: the point direction sensors (and the fitness) refer to
    record_every: int = 2  #: control ticks between recorded trajectory frames
    explosion_speed: float = 200.0  #: any body moving faster than this (m/s) marks the robot as exploded

    @property
    def control_dt(self) -> float:
        return self.world.timestep * self.control_substeps

    def to_dict(self) -> dict:
        from dataclasses import asdict

        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "SimConfig":
        """Rebuild a SimConfig from the nested dict written to an experiment's config.json."""
        d = dict(d)
        synthesis = SynthesisConfig(**d.pop("synthesis", {}))
        world = WorldConfig(**d.pop("world", {}))
        cfg = SimConfig(synthesis=synthesis, world=world, **d)
        cfg.target = tuple(cfg.target)
        return cfg


class Simulation:
    def __init__(self, genotypes: list[Genotype], config: Optional[SimConfig] = None, spawns: Optional[list[Spawn]] = None):
        self.config = config or SimConfig()
        self.genotypes = list(genotypes)
        self.phenotypes: list[Phenotype] = [synthesize(g, self.config.synthesis) for g in self.genotypes]
        if spawns is None:
            spawns = default_spawns(len(self.genotypes), self.config.start_distance)
        self.spawns = spawns
        self.model, self.data, self.robots = build_model(self.phenotypes, spawns, self.config.world)
        self.brains = [RuntimeBrain(ph) for ph in self.phenotypes]
        self.time = 0.0
        self.tick = 0
        self.exploded = [False] * len(self.genotypes)
        self._body_to_robot = {}
        for ri, idx in enumerate(self.robots):
            for b in idx.bodies:
                self._body_to_robot[b] = ri
        self._opponent = [self._pick_opponent(i) for i in range(len(self.robots))]
        self.trajectory: Optional[Trajectory] = None

    # -- setup -------------------------------------------------------------- #
    def _pick_opponent(self, i: int) -> Optional[int]:
        for j, idx in enumerate(self.robots):
            if j != i and not idx.spawn.static:
                return j
        return None

    def start_recording(self, every: Optional[int] = None) -> Trajectory:
        every = self.config.record_every if every is None else every
        units = []
        for ph in self.phenotypes:
            units.extend(UnitSpec(p.shape, tuple(p.dims)) for p in ph.parts)
        self.trajectory = Trajectory(dt=self.config.control_dt * every, units=units, robots=[len(ph.parts) for ph in self.phenotypes])
        self._record_every = every
        self._record_frame()
        return self.trajectory

    def _record_frame(self) -> None:
        rows = []
        q = np.zeros(4)
        for idx in self.robots:
            for gid in idx.geoms:
                mujoco.mju_mat2Quat(q, self.data.geom_xmat[gid])
                rows.append(np.concatenate([self.data.geom_xpos[gid], q]))
        self.trajectory.frames.append(np.array(rows))

    # -- sensing ------------------------------------------------------------ #
    def contact_bodies(self) -> set[int]:
        touching = set()
        for c in self.data.contact[: self.data.ncon]:
            touching.add(int(self.model.geom_bodyid[c.geom1]))
            touching.add(int(self.model.geom_bodyid[c.geom2]))
        return touching

    def sensor_values(self, ri: int, touching: set[int]) -> np.ndarray:
        brain = self.brains[ri]
        idx = self.robots[ri]
        vals = np.zeros(len(brain.sensors))
        opp = self._opponent[ri]
        opp_pos = self.data.xpos[self.robots[opp].root_body] if opp is not None else None
        target = np.asarray(self.config.target, dtype=float)
        for k, s in enumerate(brain.sensors):
            if s.source == "contact":
                vals[k] = 1.0 if idx.bodies[s.part] in touching else 0.0
                continue
            gid = idx.geoms[s.part]
            src = target if s.source == "target" else opp_pos
            if src is None:
                continue
            v = src - self.data.geom_xpos[gid]
            n = np.linalg.norm(v)
            if n < 1e-9:
                continue
            local = self.data.geom_xmat[gid].reshape(3, 3).T @ (v / n)
            vals[k] = float(local[s.axis])
        return vals

    # -- stepping ----------------------------------------------------------- #
    def step(self) -> None:
        """One control tick: read sensors, update brains, apply motors, step physics."""
        touching = self.contact_bodies()
        for ri, (brain, idx) in enumerate(zip(self.brains, self.robots)):
            if self.exploded[ri]:
                continue
            brain.step(self.sensor_values(ri, touching))
            for key, aid in idx.actuators.items():
                self.data.ctrl[aid] = brain.effector_output(*key)
        for _ in range(self.config.control_substeps):
            mujoco.mj_step(self.model, self.data)
        self.tick += 1
        self.time = self.tick * self.config.control_dt
        self._check_explosions()
        if self.trajectory is not None and self.tick % self._record_every == 0:
            self._record_frame()

    def _check_explosions(self) -> None:
        if not np.all(np.isfinite(self.data.qpos)) or not np.all(np.isfinite(self.data.qvel)):
            for ri in range(len(self.robots)):
                self.exploded[ri] = True
            return
        speeds = np.linalg.norm(self.data.cvel[:, 3:], axis=1)
        for ri, idx in enumerate(self.robots):
            if self.exploded[ri] or idx.spawn.static:
                continue
            if speeds[idx.bodies].max() > self.config.explosion_speed:
                self.exploded[ri] = True

    def run(self, duration: Optional[float] = None, record: bool = False) -> Optional[Trajectory]:
        duration = self.config.duration if duration is None else duration
        if record and self.trajectory is None:
            self.start_recording()
        n = int(round(duration / self.config.control_dt))
        for _ in range(n):
            self.step()
        return self.trajectory

    # -- measurements ------------------------------------------------------- #
    def center_of_mass(self, ri: int) -> np.ndarray:
        return np.array(self.data.subtree_com[self.robots[ri].root_body])

    def distance_from_center(self, ri: int) -> float:
        """Horizontal distance of the robot's centre of mass from the target point."""
        com = self.center_of_mass(ri)
        target = np.asarray(self.config.target, dtype=float)
        return float(np.linalg.norm((com - target)[:2]))


def default_spawns(n: int, start_distance: float) -> list[Spawn]:
    """Place ``n`` robots evenly on a circle, each facing the centre."""
    spawns = []
    for i in range(n):
        ang = np.pi * (1 + 2 * i / n) if n > 1 else 0.0
        x, y = start_distance * np.cos(ang), start_distance * np.sin(ang)
        spawns.append(Spawn(position=(x, y, 0.0), yaw=float(np.arctan2(-y, -x)) if n > 1 else 0.0))
    return spawns


@dataclass
class BoutResult:
    distances: list  #: final centre-of-mass distance from the centre, per robot
    fitness: list  #: zero-sum fitness per robot (sums to 1)
    exploded: list
    duration: float
    trajectory: Optional[Trajectory] = None

    @property
    def winner(self) -> int:
        return int(np.argmax(self.fitness))


def zero_sum_fitness(distances, exploded) -> list:
    """The paper's ratio-of-distances fitness for two robots.

    ``fitness[a] = d[b] / (d[a] + d[b])``: it rewards reaching the centre and
    keeping the opponent away.  An exploded (numerically unstable) robot
    loses outright.
    """
    da, db = distances
    ea, eb = exploded
    if ea and eb:
        return [0.5, 0.5]
    if ea:
        return [0.0, 1.0]
    if eb:
        return [1.0, 0.0]
    total = da + db
    if total < 1e-9:
        return [0.5, 0.5]
    return [db / total, da / total]


def run_bout(a: Genotype, b: Genotype, config: Optional[SimConfig] = None, record: bool = False, swap: bool = False) -> BoutResult:
    """Simulate the two-robot competition and return the result (robot ``a`` first)."""
    config = config or SimConfig()
    order = [b, a] if swap else [a, b]
    sim = Simulation(order, config)
    traj = sim.run(record=record)
    dists = [sim.distance_from_center(i) for i in range(2)]
    fit = zero_sum_fitness(dists, sim.exploded)
    exploded = list(sim.exploded)
    if swap:
        dists, fit, exploded = dists[::-1], fit[::-1], exploded[::-1]
    return BoutResult(distances=dists, fitness=fit, exploded=exploded, duration=sim.time, trajectory=traj)
