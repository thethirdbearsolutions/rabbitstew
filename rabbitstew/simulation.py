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
from .genotype import JointType
from .trajectory import SceneryItem, Trajectory, UnitSpec
from .world import RobotIndex, Spawn, WorldConfig, build_model, scenery


@dataclass
@dataclass
class FoodConfig:
    """The foraging world's economy.  Food items lie in a disc; a robot eats one by bringing any
    part within ``eat_radius`` of it, gaining ``value``; an eaten item regrows at a new random
    position.  Nothing reports where food is: the ``food`` sensor reads the summed intensity
    ``sum(exp(-d / decay))`` at the sensing Segment's position."""

    items: int = 12
    radius: float = 3.0  #: food lies within this radius of the centre (m)
    value: float = 1.0  #: energy per item
    eat_radius: float = 0.35  #: m, from any geom centre of the robot
    decay: float = 1.0  #: intensity length scale (m)
    regrow: bool = True
    work_cost: float = 0.0  #: energy charged per kJ of actuator work (metabolism of moving)


@dataclass
class SimConfig:
    synthesis: SynthesisConfig = field(default_factory=SynthesisConfig)
    world: WorldConfig = field(default_factory=WorldConfig)
    control_substeps: int = 4  #: physics steps per brain update
    duration: float = 10.0  #: seconds of simulated time per bout
    start_distance: float = 2.0  #: robots start this far from the centre, on opposite sides
    target: tuple = (0.0, 0.0, 0.0)  #: the point direction sensors (and the fitness) refer to; z is raised to the terrain's height
    record_every: int = 2  #: control ticks between recorded trajectory frames
    explosion_speed: float = 200.0  #: any body moving faster than this (m/s) marks the robot as exploded
    settle_time: float = 1.0  #: seconds of passive settling before the clock starts; bouts begin from rest
    opponent_proxy: bool = False  #: when a robot has no opponent, its opponent sensors point at the target
    random_start: bool = False  #: draw the start bearing, distance and headings of a bout from a seed
    start_distance_range: tuple = (1.5, 2.5)  #: start distances (m) under random_start
    start_heading_range: float = 0.75 * np.pi  #: max |heading offset| (rad) from the direction to the target under random_start
    score: str = "distance"  #: "distance" (the paper's snapshot ratio), "time_at_target", or "closeness" (progress integrated over the whole bout: dense, ranks every body on every bout)
    target_radius: float = 0.5  #: radius (m) that counts as "at the target" for time_at_target scoring
    progress_weight: float = 0.1  #: weight of approach progress added to time_at_target so the score has a gradient before anyone arrives
    waypoints: int = 0  #: > 0: once a robot holds the target for hold_time it is given a new one (per robot), up to this many; demands steering
    waypoint_distance: float = 1.5  #: distance (m) from the current target to the next
    hold_time: float = 1.0  #: seconds within target_radius before a waypoint counts as reached
    food: Optional[FoodConfig] = None  #: the foraging world, when set

    @property
    def control_dt(self) -> float:
        return self.world.timestep * self.control_substeps

    def effective_target(self) -> np.ndarray:
        t = np.array(self.target, dtype=float)
        if t[2] == 0.0:
            t[2] = self.world.target_height
        return t

    def to_dict(self) -> dict:
        from dataclasses import asdict

        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "SimConfig":
        """Rebuild a SimConfig from the nested dict written to an experiment's config.json."""
        d = dict(d)
        synthesis = SynthesisConfig(**d.pop("synthesis", {}))
        world = WorldConfig(**d.pop("world", {}))
        food = d.pop("food", None)
        cfg = SimConfig(synthesis=synthesis, world=world, food=FoodConfig(**food) if food else None, **d)
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
        if self.config.world.terrain == "random":
            from dataclasses import replace

            self.config = replace(self.config, world=replace(self.config.world, keep_clear=tuple((float(sp.position[0]), float(sp.position[1]), 0.6) for sp in spawns)))
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
        self._target = self.config.effective_target()
        self._vel6 = np.zeros(6)
        self.work = np.zeros(len(self.robots))  #: mechanical work (J) done by each robot's actuators so far
        self.at_target_ticks = np.zeros(len(self.robots), dtype=int)  #: control ticks each robot spent within target_radius
        self.waypoints_reached = np.zeros(len(self.robots), dtype=int)
        self._closeness_sum = np.zeros(len(self.robots))
        self._upright_sum = np.zeros(len(self.robots))
        self._hold_ticks = np.zeros(len(self.robots), dtype=int)
        self._targets = [self.config.effective_target().copy() for _ in self.robots]  #: per-robot current target (waypoints)
        self._wp_rng = None
        self.settled = False
        self._actuator_robot = np.full(self.model.nu, -1, dtype=int)
        for ri, idx in enumerate(self.robots):
            for aid in idx.actuators.values():
                self._actuator_robot[aid] = ri
        self.trajectory: Optional[Trajectory] = None
        self.food_eaten = np.zeros(len(self.robots))  #: items eaten by each robot
        self.food_events: list = []  #: (tick, robot, x, y)
        self.food_pos = np.zeros((0, 2))
        self._food_rng = np.random.default_rng(0)
        if self.config.food is not None:
            self.set_food_seed(0)
        if self.config.settle_time > 0:
            self.settle(self.config.settle_time)
        self.start_distances = [self.distance_from_center(i) for i in range(len(self.robots))]

    # -- setup -------------------------------------------------------------- #
    def settle(self, duration: float) -> None:
        """Let every robot come to rest passively, then zero all velocities and re-centre each
        free robot on its spawn point, so a bout starts from rest and the spawn drop cannot be
        harvested as momentum.  The clock, work and recording are untouched."""
        n = int(round(duration / self.config.control_dt)) * self.config.control_substeps
        self.data.ctrl[:] = 0.0
        for _ in range(n):
            mujoco.mj_step(self.model, self.data)
        self.data.qvel[:] = 0.0
        self.data.qacc[:] = 0.0
        self.data.act[:] = 0.0 if self.model.na else self.data.act
        for idx in self.robots:
            if idx.root_qpos_adr < 0:
                continue
            adr = idx.root_qpos_adr
            mujoco.mj_forward(self.model, self.data)
            com = self.data.subtree_com[idx.root_body]
            self.data.qpos[adr] += idx.spawn.position[0] - com[0]
            self.data.qpos[adr + 1] += idx.spawn.position[1] - com[1]
        self.data.time = 0.0
        mujoco.mj_forward(self.model, self.data)
        self.settled = True
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
        scen = [SceneryItem(sc.shape, tuple(sc.dims), tuple(sc.pos), tuple(sc.quat)) for sc in scenery(self.config.world)]
        self.trajectory = Trajectory(dt=self.config.control_dt * every, units=units, robots=[len(ph.parts) for ph in self.phenotypes], scenery=scen)
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
        ph = self.phenotypes[ri]
        vals = np.zeros(len(brain.sensors))
        opp = self._opponent[ri]
        target = self._targets[ri]
        opp_pos = self.data.xpos[self.robots[opp].root_body] if opp is not None else (target if self.config.opponent_proxy else None)
        d = self.data
        m = self.model
        for k, s in enumerate(brain.sensors):
            src = s.source
            if src == "contact":
                vals[k] = 1.0 if idx.bodies[s.part] in touching else 0.0
            elif src == "oscillator":
                vals[k] = float(np.sin(2 * np.pi * s.freq * self.time + s.phase))
            elif src in ("target", "opponent", "target_distance", "opponent_distance"):
                point = target if src.startswith("target") else opp_pos
                if point is None:
                    continue
                gid = idx.geoms[s.part]
                v = point - d.geom_xpos[gid]
                if src.endswith("distance"):
                    dist = float(np.linalg.norm(v[:2]))
                    vals[k] = dist / (1.0 + dist)
                    continue
                n = np.linalg.norm(v)
                if n < 1e-9:
                    continue
                local = d.geom_xmat[gid].reshape(3, 3).T @ (v / n)
                vals[k] = float(local[s.axis])
            elif src == "food":
                vals[k] = self._intensity(d.geom_xpos[idx.geoms[s.part]], self.food_pos)
            elif src == "agent":
                others = np.array([d.xpos[self.robots[j].root_body][:2] for j in range(len(self.robots)) if j != ri and not self.robots[j].spawn.static])
                vals[k] = self._intensity(d.geom_xpos[idx.geoms[s.part]], others)
            elif src == "up":
                gid = idx.geoms[s.part]
                vals[k] = float(d.geom_xmat[gid].reshape(3, 3)[2, s.axis])  # row 2 of R = R^T (0,0,1)
            elif src == "velocity":
                mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_GEOM, idx.geoms[s.part], self._vel6, 1)
                vals[k] = float(np.tanh(self._vel6[3 + s.axis]))
            elif src == "height":
                vals[k] = float(np.tanh(d.geom_xpos[idx.geoms[s.part]][2]))
            elif src in ("joint_angle", "joint_velocity"):
                jid = idx.joints[s.part]
                if jid < 0:
                    continue
                part = ph.parts[s.part]
                if part.joint_type == JointType.BALL:
                    if src == "joint_angle":
                        w = d.qpos[m.jnt_qposadr[jid]]
                        vals[k] = float(2.0 * np.arccos(np.clip(abs(w), 0.0, 1.0)) / np.pi)
                    else:
                        adr = m.jnt_dofadr[jid]
                        vals[k] = float(np.tanh(np.linalg.norm(d.qvel[adr : adr + 3]) / 5.0))
                elif src == "joint_angle":
                    q = float(d.qpos[m.jnt_qposadr[jid]])
                    if part.joint_range is not None:
                        span = max(abs(part.joint_range[0]), abs(part.joint_range[1]), 1e-6)
                        vals[k] = float(np.clip(q / span, -1.0, 1.0))
                    else:
                        vals[k] = float(np.sin(q))
                else:
                    vals[k] = float(np.tanh(d.qvel[m.jnt_dofadr[jid]] / 5.0))
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
            if self.model.nu:
                power = np.abs(self.data.actuator_force * self.data.actuator_velocity)
                np.add.at(self.work, self._actuator_robot[self._actuator_robot >= 0], power[self._actuator_robot >= 0] * self.config.world.timestep)
        self.tick += 1
        self.time = self.tick * self.config.control_dt
        self._eat()
        hold_ticks_needed = int(round(self.config.hold_time / self.config.control_dt))
        for ri in range(len(self.robots)):
            self._closeness_sum[ri] += self.progress(ri)
            self._upright_sum[ri] += max(0.0, float(self.data.xmat[self.robots[ri].root_body].reshape(3, 3)[2, 2]))
            if self.distance_from_center(ri) < self.config.target_radius:
                self.at_target_ticks[ri] += 1
                self._hold_ticks[ri] += 1
                if self.config.waypoints and self.waypoints_reached[ri] < self.config.waypoints and self._hold_ticks[ri] >= hold_ticks_needed:
                    self.waypoints_reached[ri] += 1
                    self._hold_ticks[ri] = 0
                    self._targets[ri] = self._next_waypoint(ri)
                    self.start_distances[ri] = self.distance_from_center(ri)
            else:
                self._hold_ticks[ri] = 0
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
        """Horizontal distance of the robot's centre of mass from its current target point."""
        com = self.center_of_mass(ri)
        return float(np.linalg.norm((com - self._targets[ri])[:2]))

    def set_waypoint_seed(self, seed: Optional[int]) -> None:
        """Seed the sequence of waypoints (shared by every robot in the bout)."""
        self._wp_rng = np.random.default_rng(0 if seed is None else int(seed))
        self._wp_sequence = []

    def set_food_seed(self, seed: Optional[int]) -> None:
        """Place the food from a seed (the bout's start seed, so a season's draw is reproducible)."""
        f = self.config.food
        self._food_rng = np.random.default_rng(0 if seed is None else int(seed))
        self.food_pos = np.array([self._food_spot() for _ in range(f.items)]) if f.items else np.zeros((0, 2))

    def _food_spot(self) -> np.ndarray:
        f = self.config.food
        r = f.radius * np.sqrt(self._food_rng.random())
        a = self._food_rng.uniform(0, 2 * np.pi)
        return np.array([r * np.cos(a), r * np.sin(a)])

    def _eat(self) -> None:
        f = self.config.food
        if f is None or len(self.food_pos) == 0:
            return
        for ri, idx in enumerate(self.robots):
            if self.exploded[ri] or idx.spawn.static:
                continue
            geoms = self.data.geom_xpos[idx.geoms][:, :2]
            d = np.linalg.norm(geoms[:, None, :] - self.food_pos[None, :, :], axis=2).min(axis=0)
            for j in np.nonzero(d < f.eat_radius)[0]:
                self.food_eaten[ri] += 1
                self.food_events.append((self.tick, ri, float(self.food_pos[j, 0]), float(self.food_pos[j, 1])))
                if f.regrow:
                    self.food_pos[j] = self._food_spot()
                else:
                    self.food_pos[j] = (1e6, 1e6)

    def _intensity(self, point: np.ndarray, sources: np.ndarray) -> float:
        if len(sources) == 0:
            return 0.0
        d = np.linalg.norm(sources - point[:2], axis=1)
        i = float(np.exp(-d / self.config.food.decay).sum()) if self.config.food is not None else float(np.exp(-d).sum())
        return i / (1.0 + i)

    def food_score(self, ri: int) -> float:
        """Net energy from foraging: items eaten times their value, minus the work cost of moving."""
        f = self.config.food
        if f is None:
            return 0.0
        return float(self.food_eaten[ri] * f.value - f.work_cost * self.work[ri] / 1000.0)

    def _next_waypoint(self, ri: int) -> np.ndarray:
        k = int(self.waypoints_reached[ri]) - 1  # the k-th waypoint after the initial target
        if self._wp_rng is None:
            self.set_waypoint_seed(None)
        while len(self._wp_sequence) <= k:
            base = self._wp_sequence[-1] if self._wp_sequence else self.config.effective_target()
            ang = self._wp_rng.uniform(0, 2 * np.pi)
            nxt = base + np.array([self.config.waypoint_distance * np.cos(ang), self.config.waypoint_distance * np.sin(ang), 0.0])
            self._wp_sequence.append(nxt)
        return self._wp_sequence[k].copy()

    def time_at_target(self, ri: int) -> float:
        """Fraction of the bout so far spent within ``target_radius`` of the target."""
        return float(self.at_target_ticks[ri] / max(1, self.tick))

    def upright(self, ri: int) -> float:
        """Mean over the bout of the root's up-vector alignment with world up (1 = never tilted)."""
        return float(self._upright_sum[ri] / max(1, self.tick))

    def score_vector(self, ri: int) -> list:
        """Objectives for multi-dimensional selection: closeness, time at target, waypoints, uprightness,
        and mechanical economy (progress per kJ of actuator work)."""
        return [self.closeness(ri), self.time_at_target(ri), float(self.waypoints_reached[ri]), self.upright(ri), float(self.progress(ri) / (1.0 + self.work[ri] / 1000.0))]

    def closeness(self, ri: int) -> float:
        """Mean over the bout of the fraction of the start distance closed: 1 = at the target the whole time."""
        return float(self._closeness_sum[ri] / max(1, self.tick))

    def progress(self, ri: int) -> float:
        """Fraction of the start distance closed, clipped to [0, 1]."""
        d0 = max(self.start_distances[ri], 1e-6)
        return float(np.clip(1.0 - self.distance_from_center(ri) / d0, 0.0, 1.0))

    def score(self, ri: int) -> float:
        """The robot's raw score under ``config.score`` (higher is better).

        With waypoints, each waypoint reached is worth a full bout at the target (1.0), plus
        time at the current target and progress towards it.
        """
        if self.config.score == "time_at_target":
            return float(self.waypoints_reached[ri]) + self.time_at_target(ri) + self.config.progress_weight * self.progress(ri)
        if self.config.score == "closeness":
            return float(self.waypoints_reached[ri]) + self.closeness(ri)
        if self.config.score == "distance":
            return -self.distance_from_center(ri)
        if self.config.score == "food":
            return self.food_score(ri)
        raise ValueError(f"unknown score {self.config.score!r}")


def spawn_layout(n: int, config: "SimConfig", start_seed: Optional[int] = None) -> list[Spawn]:
    """Spawns for a bout.  With ``config.random_start`` and a seed, the robots sit on opposite
    sides of the centre at a random bearing and distance, each with its own random heading
    offset; otherwise they face the centre from ``config.start_distance`` as in the paper."""
    if not config.random_start or start_seed is None:
        return default_spawns(n, config.start_distance)
    rng = np.random.default_rng(int(start_seed))
    bearing = rng.uniform(0, 2 * np.pi)
    dist = rng.uniform(*config.start_distance_range)
    spawns = []
    for i in range(n):
        ang = bearing + 2 * np.pi * i / n
        x, y = dist * np.cos(ang), dist * np.sin(ang)
        towards = float(np.arctan2(-y, -x))
        offset = rng.uniform(-config.start_heading_range, config.start_heading_range)
        spawns.append(Spawn(position=(float(x), float(y), 0.0), yaw=towards + offset))
    return spawns


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
    time_at_target: list = field(default_factory=list)  #: fraction of the bout within target_radius, per robot
    scores: list = field(default_factory=list)  #: raw scores under the configured score
    start_seed: Optional[int] = None
    vectors: list = field(default_factory=list)  #: score_vector per robot

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


def zero_sum_scores(scores, exploded) -> list:
    """Zero-sum fitness from two non-negative scores (``time_at_target`` mode): each robot's share of the total."""
    sa, sb = max(scores[0], 0.0), max(scores[1], 0.0)
    ea, eb = exploded
    if ea and eb:
        return [0.5, 0.5]
    if ea:
        return [0.0, 1.0]
    if eb:
        return [1.0, 0.0]
    total = sa + sb
    if total < 1e-9:
        return [0.5, 0.5]
    return [sa / total, sb / total]


def run_bout(a: Genotype, b: Genotype, config: Optional[SimConfig] = None, record: bool = False, swap: bool = False, start_seed: Optional[int] = None) -> BoutResult:
    """Simulate the two-robot competition and return the result (robot ``a`` first).

    ``start_seed`` draws the start layout when ``config.random_start`` is set;
    both robots share the draw.
    """
    config = config or SimConfig()
    order = [b, a] if swap else [a, b]
    sim = Simulation(order, config, spawns=spawn_layout(2, config, start_seed))
    if config.waypoints:
        sim.set_waypoint_seed(start_seed)
    traj = sim.run(record=record)
    dists = [sim.distance_from_center(i) for i in range(2)]
    tat = [sim.time_at_target(i) for i in range(2)]
    scores = [sim.score(i) for i in range(2)]
    vectors = [sim.score_vector(i) for i in range(2)]
    if config.score in ("time_at_target", "closeness"):
        fit = zero_sum_scores(scores, sim.exploded)
    else:
        fit = zero_sum_fitness(dists, sim.exploded)
    exploded = list(sim.exploded)
    if swap:
        dists, fit, exploded, tat, scores, vectors = dists[::-1], fit[::-1], exploded[::-1], tat[::-1], scores[::-1], vectors[::-1]
    return BoutResult(distances=dists, fitness=fit, exploded=exploded, duration=sim.time, trajectory=traj, time_at_target=tat, scores=scores, start_seed=start_seed, vectors=vectors)


def run_solo(g: Genotype, config: Optional[SimConfig] = None, start_seed: Optional[int] = None) -> dict:
    """One robot alone (opponent sensors pointed at the target): its score, progress and time at target.

    Used for the locomotion phase of an experiment, where fitness is not yet competitive.
    """
    from dataclasses import replace

    config = replace(config or SimConfig(), opponent_proxy=True)
    spawn = spawn_layout(2, config, start_seed)[0]
    sim = Simulation([g], config, spawns=[spawn])
    if config.waypoints:
        sim.set_waypoint_seed(start_seed)
    if config.food is not None:
        sim.set_food_seed(start_seed)
    sim.run()
    return {"score": sim.score(0) if config.score in ("time_at_target", "closeness", "food") else sim.time_at_target(0) + config.progress_weight * sim.progress(0), "distance": sim.distance_from_center(0), "time_at_target": sim.time_at_target(0), "progress": sim.progress(0), "waypoints": int(sim.waypoints_reached[0]), "exploded": bool(sim.exploded[0]), "start_seed": start_seed, "vector": sim.score_vector(0)}


def run_group(genotypes: list, config: Optional[SimConfig] = None, start_seed: Optional[int] = None) -> list[dict]:
    """Several robots in one arena (the foraging world): each robot's food eaten, work and net
    score.  Robots are spread evenly around the centre at a random bearing and heading."""
    from dataclasses import replace

    config = replace(config or SimConfig(), random_start=True)
    spawns = spawn_layout(len(genotypes), config, start_seed)
    sim = Simulation(genotypes, config, spawns=spawns)
    if config.food is not None:
        sim.set_food_seed(start_seed)
    sim.run()
    return [{"score": sim.score(i), "food": float(sim.food_eaten[i]), "work": float(sim.work[i]), "exploded": bool(sim.exploded[i]), "path": float(np.linalg.norm(sim.center_of_mass(i)[:2] - np.array(spawns[i].position[:2]))), "start_seed": start_seed} for i in range(len(genotypes))]
