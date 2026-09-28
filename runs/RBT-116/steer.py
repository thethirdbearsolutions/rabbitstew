"""RBT-116: the STEERS battery (PREREGISTRATION.md §1.1–§1.4, r7 with Amendment 1), at its ruled version.

    steer.py --config CONFIG_JSON --battery BATTERY_JSON [--workers W] GENOME.json [GENOME.json ...] > steer.txt

This file is the instrument, not an experiment: it runs nothing on import, and its command line calls the genomes it is
given on the battery it is given.  ``gate.py`` (the draw screen's hosts, G1–G9), ``readout.py`` and the G8 planters are
separate; STEER_NOTES.md lists what they take from here, and every reading of the registration made here, by line.

**The season** (§1.1, §1.2) is the selection's own solo season (``simulation.run_solo``: robot 0 of a two-robot
``spawn_layout``, opponent sensors on the target, the food from the start seed), in the world point's ``SimConfig`` with
the draw's terrain seed, stepped here tick by tick so that it can record:

* ``food`` and ``work`` (an exploded season books neither, as ``Simulation.harvest`` does), and ``net``;
* ``cells``: distinct 0.35 m xy cells under any geom centre, and items per 100 cells (C7);
* ``traj``: the root body's xy at every control tick (tick 0 is the settled start), for the trajectory-identity veto;
* per tick, the CoM's horizontal speed |v| and v · ĝ, with ĝ the unit gradient of the **real, untransformed** field
  Σ exp(−d/decay) over the items standing at the start of the tick, at the CoM at the start of the tick;
* ``pen``: the deepest contact penetration involving the robot; ``disp``: CoM displacement over the season.

**The four conditions** (§1.1).  Only ``food`` sensors are touched; eating, regrowth, depletion and the real items are
not.
* ``intact``: the world's own transform on the real field.
* ``decoy``: the food sensors smell the live layout rotated about the origin by θ, before the transform (both
  ``Simulation._log_smell``, the contrast channel, and ``_intensity``, the legacy reading, are rotated, so the decoy
  cannot fall back to the true layout under either).  θ ~ U[30°, 330°] comes from a stream keyed on the start seed alone
  (:func:`theta_stream`), and is re-drawn from the same stream until no rotated live item lies within the food
  clearance (0.8 m at W1) of the world's clearance points at the start of the season (SHOULD 1).  The world's layout rule must be rotation
  invariant, and :func:`assert_rotation_invariant` refuses one that is not (SHOULD 2).  (Amendment 2: the clearance is
  the world's own rule at spawn, :func:`world_clearance`, not the root alone; S-M1.)
* ``lesion``: ``FoodConfig.smell_lesion``: every food sensor reads the transform's zero-information constant,
  :data:`LESION_CONSTANT` = 0, from the first tick (Amendment 1, item 5; RBT-129's R_marker reads the same flag).
* ``motors-off``: the real field, every actuator command held at 0 (the brain still runs).

**The call** (§1.3): stage 1 (4 draws, intact and decoy) stops a genome whose intact and decoy root trajectories are
identical on all 4.  Stage 2 (16 draws, all four conditions) PASSES iff F ≥ F_MIN with a one-sided 95% t lower bound
> 0, the lower bound on ΔT is > 0, and the trajectories differ on more than half the draws.  STEERS iff it PASSES on
stage 2 and again on the 16 confirmation draws (intact and decoy).  SMELL-USE iff stage 2 meets 1 and 3 but not 2.
Everything else is NONE.  Lines (§1.4) are read at K and at K + 2 (R6-1) by :func:`line_reading`.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass, field, replace
from typing import Callable, Optional, Sequence

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import _SURFACE_CLEAR, CLEAR_FROM, EAT_RULES, SimConfig, Simulation, spawn_layout  # noqa: E402

# --------------------------------------------------------------------------- #
# Registered constants (PREREGISTRATION.md r7 + Amendment 1)
# --------------------------------------------------------------------------- #

F_MIN = 0.25  #: §1.3: items per season gained from smell information
F_MIN_REL = 0.2  #: §1.3 [OPEN]: the relative variant max(F_MIN, 0.2 × food_intact), printed beside the call
N_STAGE1, N_STAGE2, N_CONFIRM = 4, 16, 16  #: §1.1: draws per stage, assigned from the admissible pool in pool order
N_BATTERY = N_STAGE1 + N_STAGE2 + N_CONFIRM  #: 36: fewer admissible draws extends the pool once, then fails the point
POOL_SIZE, POOL_EXTENSION = 64, 32  #: §1.1
THETA_LO_DEG, THETA_HI_DEG = 30.0, 330.0  #: §1.1: the decoy's rotation
THETA_KEY = (116, 97)  #: the θ stream's registered key; the start seed completes it (shared by faunas and paired worlds)
THETA_MAX_DRAWS = 4096  #: a start seed whose stream gives no clear θ in this many draws is refused (STEER_NOTES N5)
POOL_KEY = {"W1": (116, 64, 1)}  #: per world point, the draw pool's registered key (a new point adds its own row)
#: RBT-132: RBT-129's 18 PAYS cells (its 4 pilot points among them), in blocks.PAYS_CELLS order; each gets a pool key
#: (116, 64, 129, k), k = 1..18, registered before any season runs on it (W1's key is untouched)
RBT129_POINTS = ("c0-p030-U-L", "c1-p030-U-L", "c2-p030-U-L", "c0-p030-U-G", "c1-p030-U-G", "c2-p030-U-G",
                 "c0-p030-HP-L", "c1-p030-HP-L", "c2-p030-HP-L", "c0-p030-HP-G", "c1-p030-HP-G", "c2-p030-HP-G",
                 "c0-p030-PW-L", "c1-p030-PW-L", "c2-p030-PW-L", "c0-p030-PW-G", "c1-p030-PW-G", "c2-p030-PW-G")
POOL_KEY.update({pid: (116, 64, 129, k) for k, pid in enumerate(RBT129_POINTS, start=1)})
V_MIN_FRAC = 0.25  #: §1.2 (MUST 2): v_min = 0.25 × the member's median |v| in its intact season on that draw
TRAJ_TOL = 1e-9  #: §1.2, §1.3: trajectories "differ" if the root's xy differs by more than this at some tick
CELL = 0.35  #: §1.2 (C7): the coverage cell (m)
K_REGISTERED = 5  #: §1.4 (R5-1): the crossing count on the priors; the gate re-chooses it before any arm
K_HEADLINE_STEP = 2  #: §6.3 (R6-1): a HOLISTIC/PIONEER verdict is headlined only if it also holds at K + 2
SMELL_TAU = 1.0  #: Amendment 1 (revised): the contrast channel's τ (s), set explicitly (the code's default is 2.0)
MIN_USABLE = 2  #: a battery with fewer usable (non-refused) draws gives no t bound: its stage is not called (FC-M2)
#: RBT-132 (#471's ruling, M1): a point's stage-2 and confirmation count n when the K3 calibration rule raises it
#: (RBT-129 §12: the smallest of 32 / 64 at which the projected SEEN share reaches 0.6).  Empty until a ruled pick is
#: registered here; a point absent from it keeps the registered 16 and the registered pool, exactly as W1.
RAISED_N = {}
#: RBT-132 (the calibration gate diagnosis, GATE_DIAG.md): points whose screen
#: admits a draw when at least ONE positive control eats ≥ 1 item on it (MUST 1's reachability intent: some control
#: reaches food), instead of at least half of them.  ADOPTED (#478, ruled 16:33).  At RBT-129's calibration cells 0 of 96
#: draws have no eater, "at least half" admits 5-15% of them, and it selects on the plants' own intact seasons.
#: W1 keeps the registered rule.
SCREEN_ANY = frozenset(RBT129_POINTS)
#: registered world points (FC-M2, FC-S3): the command line refuses a config that differs from its point's block
REGISTERED_POINTS = {"W1": {"smell_contrast": 2.5, "smell_tau": 1.0, "eat_from": "root", "eat_rule": "surface",
                            "clear_from": "root", "eat_radius": 0.35}}
#: RBT-132: RBT-129's points, as its blocks build them (runs/RBT-129/worlds/<id>.config.json): the ruled eating block
#: everywhere; at a G point the RBT-125 channel at G 2.5 and τ 2 s (RBT-129 §2, the 02:10 ruling); at an L point no
#: channel (smell_contrast 0; the code's default τ, 2 s, sits unused in the config)
REGISTERED_POINTS.update({pid: {"smell_contrast": 2.5 if pid.endswith("-G") else 0.0, "smell_tau": 2.0, "eat_from": "root",
                                "eat_rule": "surface", "clear_from": "root", "eat_radius": 0.35} for pid in RBT129_POINTS})
FAIR_POINTS = frozenset(RBT129_POINTS)  #: points whose config.json must carry RBT-128's marker "fairness": "fair"
#: RBT-132 S1: the hash (sim_hash) of each RBT-129 point's committed ``sim`` block (runs/RBT-129/worlds/<id>.config.json),
#: so a config cannot run under another point's label, pool and τ.  W1 has no committed block and no entry
POINT_SIM_HASH = {
    "c0-p030-U-L": "406f214e01a70faa",
    "c1-p030-U-L": "bbb070ddeef55160",
    "c2-p030-U-L": "10306f66c6b912b0",
    "c0-p030-U-G": "d446b5110ecc3382",
    "c1-p030-U-G": "0f30a26aef53a1cb",
    "c2-p030-U-G": "0d5f8539c680ff32",
    "c0-p030-HP-L": "dd407ef0d7cbd0b3",
    "c1-p030-HP-L": "21e600c122cf1fa0",
    "c2-p030-HP-L": "78d3e402673f2c57",
    "c0-p030-HP-G": "6b762b0bb63e413d",
    "c1-p030-HP-G": "003f7e6c21ac9ec9",
    "c2-p030-HP-G": "5448fa80667295ed",
    "c0-p030-PW-L": "099e52e72c6f9901",
    "c1-p030-PW-L": "c7c996b1121d7a4a",
    "c2-p030-PW-L": "0bc39f24477a2a84",
    "c0-p030-PW-G": "a432b4f10cd75d04",
    "c1-p030-PW-G": "d73f429209a96705",
    "c2-p030-PW-G": "72987ab9dbc89406",
}
LESION_CONSTANT = 0.0  #: the transform's zero-information constant: tanh(G · 0), what any nose reads at its own baseline
CONDITIONS = ("intact", "decoy", "lesion", "motors-off")
STEERS, SMELL_USE, NONE = "STEERS", "SMELL-USE", "NONE"


# --------------------------------------------------------------------------- #
# Draws
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Draw:
    terrain_seed: int
    start_seed: int


@dataclass
class Battery:
    """The three stages' draws, in pool order (§1.1)."""

    stage1: list
    stage2: list
    confirm: list

    def to_dict(self) -> dict:
        return {k: [[d.terrain_seed, d.start_seed] for d in getattr(self, k)] for k in ("stage1", "stage2", "confirm")}

    @staticmethod
    def from_dict(d: dict) -> "Battery":
        return Battery(*[[Draw(int(t), int(s)) for t, s in d[k]] for k in ("stage1", "stage2", "confirm")])


def sizes_at(n: int) -> dict:
    """The battery and pool at stage-2 / confirmation count n (#471's ruling, M1(a), (c)).  At the registered count
    (``N_STAGE2``) they are the module constants, read at call time: 4 + 16 + 16, pool 64 extended by 32.  At a raised
    count: 4 + n + n, and a pool of ⌈(4 + 2n) × 64 / 36⌉ extended once by half again (⌈pool / 2⌉): 121 + 61 at n = 32,
    235 + 118 at n = 64, keeping the registered pool's ratio of candidates to draws needed."""
    if n == N_STAGE2:
        return {"stage1": N_STAGE1, "stage2": N_STAGE2, "confirm": N_CONFIRM, "battery": N_BATTERY,
                "pool": POOL_SIZE, "extension": POOL_EXTENSION}
    need = N_STAGE1 + 2 * n
    pool = -(-need * 64 // 36)
    return {"stage1": N_STAGE1, "stage2": n, "confirm": n, "battery": need, "pool": pool, "extension": -(-pool // 2)}


def battery_size(world: str = "W1") -> dict:
    """A point's battery and pool sizes: :func:`sizes_at` its count, the registered one unless ``RAISED_N`` raises it
    (W1 never)."""
    return sizes_at(N_STAGE2 if world == "W1" else RAISED_N.get(world, N_STAGE2))


def draw_pool(world: str = "W1", extended: bool = False) -> list:
    """The world point's candidate draws: 64 (terrain seed, start seed) pairs, or 96 when extended (at a raised count,
    :func:`battery_size`'s pool).  The extension is the next draws of the same stream, so extending never changes the
    first ones, and a raised pool begins with the registered pool's draws."""
    if world not in POOL_KEY:
        raise KeyError(f"world point {world!r} has no registered pool key; add it to POOL_KEY before its gate")
    rng = np.random.default_rng(list(POOL_KEY[world]))
    size = battery_size(world)
    n = size["pool"] + (size["extension"] if extended else 0)
    return [Draw(int(t), int(s)) for t, s in rng.integers(0, 2**31 - 1, size=(n, 2))]


def assign_battery(admissible: Sequence[Draw], world: str = "W1") -> Optional[Battery]:
    """Stage 1, stage 2 and confirmation, in pool order, from the admissible draws; None if there are fewer than the
    point's battery (36 at the registered count)."""
    a = list(admissible)
    z = battery_size(world)
    if len(a) < z["battery"]:
        return None
    s1, s2 = z["stage1"], z["stage1"] + z["stage2"]
    return Battery(a[:s1], a[s1:s2], a[s2 : z["battery"]])


def assert_battery_size(battery: Battery, world: str) -> None:
    """The battery a planted, pays or probe command reads has the point's counts (#471's ruling, M1(b): plants and
    members alike); a battery screened at another count is refused."""
    z = battery_size(world)
    got = (len(battery.stage1), len(battery.stage2), len(battery.confirm))
    if got != (z["stage1"], z["stage2"], z["confirm"]):
        raise ValueError(f"battery has {got[0]} + {got[1]} + {got[2]} draws; {world} is registered at "
                         f"{z['stage1']} + {z['stage2']} + {z['confirm']} (steer.RAISED_N)")


def draw_sim(cfg: SimConfig, draw: Draw) -> SimConfig:
    """The world point's config on one draw: the draw's terrain seed when the terrain is random (as ``generation_sim``)."""
    if cfg.world.terrain == "random":
        cfg = replace(cfg, world=replace(cfg.world, terrain_seed=int(draw.terrain_seed)))
    return cfg


# --------------------------------------------------------------------------- #
# The decoy
# --------------------------------------------------------------------------- #


def rotate(points: np.ndarray, theta: float) -> np.ndarray:
    """Rotate xy rows counter-clockwise by ``theta`` about the origin (RBT-97's ``RotatedSmell`` convention)."""
    c, s = float(np.cos(theta)), float(np.sin(theta))
    return np.asarray(points, dtype=float).reshape(-1, 2) @ np.array([[c, s], [-s, c]])


def theta_stream(start_seed: int):
    """θ candidates for one start seed, in order, from the registered stream (§3.1 hook 3: keyed on the start seed)."""
    rng = np.random.default_rng([*THETA_KEY, int(start_seed)])
    while True:
        yield float(np.radians(rng.uniform(THETA_LO_DEG, THETA_HI_DEG)))


def points_clear(points: np.ndarray, clearance: float) -> Callable:
    """A clearance test against fixed xy points: items clear iff every item is ≥ ``clearance`` from every point."""
    pts = np.asarray(points, dtype=float).reshape(-1, 2)

    def clear(items: np.ndarray) -> bool:
        items = np.asarray(items, dtype=float).reshape(-1, 2)
        if not len(items) or not len(pts):
            return True
        return float(np.linalg.norm(items[:, None, :] - pts[None, :, :], axis=2).min()) >= clearance
    return clear


def world_clearance(sim: Simulation) -> Callable:
    """The world's own clearance rule at this moment, as a test on candidate item positions (S-M1): the rule
    ``Simulation._food_spot`` places the real items by.  Under ``clear_from=root`` the points are each robot's root; under
    ``clear_from=geoms`` every geom centre; under ``clear_from=geoms`` with ``eat_rule=surface`` the 3-D distance to
    every geom's surface (``Simulation._surface_distance``).

    Under ``eat_rule=surface`` the rule is the tuple ``(_SURFACE_CLEAR, centres, geoms, min_surface)`` that #446 merged
    (``clear_from=geoms``: every geom's surface at the clearance; ``clear_from=root``: the root-centre clearance plus the
    minimal guard, no item within ``eat_radius`` of an eating geom's surface), read here exactly as ``_food_spot``
    reads it.  The eating guard is also checked on its own under ``eat_rule=surface`` (FC-M2), which the merged rule
    already implies, so the decoy never smells an item inside eating reach."""
    f = sim.config.food
    clearance = f.clearance
    pts = sim._clearance_points()
    if isinstance(pts, tuple) and pts and pts[0] is _SURFACE_CLEAR:
        _, centres, geoms, min_surface = pts  # exactly as Simulation._food_spot reads it (RBT-125 #446)

        def base(items: np.ndarray) -> bool:
            if centres is not None and len(centres) and not points_clear(centres, clearance)(items):
                return False
            return not geoms or float(sim._surface_distance(geoms, items).min()) >= min_surface
    elif isinstance(pts, np.ndarray):
        base = points_clear(pts, clearance)
    else:
        raise ValueError(f"unknown clearance rule from Simulation._clearance_points: {type(pts).__name__}; steer.py must mirror it")
    eaters = [g for ri, idx in enumerate(sim.robots) if not idx.spawn.static for g in sim._eat_geoms[ri]]
    guard = f.eat_rule == "surface" and bool(eaters)

    def clear(items: np.ndarray) -> bool:
        items = np.asarray(items, dtype=float).reshape(-1, 2)
        if not len(items):
            return True
        if not base(items):
            return False
        return not guard or float(sim._surface_distance(eaters, items).min()) >= f.eat_radius
    return clear


def draw_theta(start_seed: int, live: np.ndarray, clear: Callable) -> tuple:
    """The decoy's θ for a season: the first θ of the start seed's stream under which the rotated live items pass
    ``clear`` (the world's clearance rule at spawn, :func:`world_clearance`; SHOULD 1, S-M1).  Returns ``(theta,
    redraws)``."""
    live = np.asarray(live, dtype=float).reshape(-1, 2)
    for k, th in enumerate(theta_stream(start_seed)):
        if k >= THETA_MAX_DRAWS:
            break
        if not len(live) or clear(rotate(live, th)):
            return th, k
    raise ThetaRefused(f"start seed {start_seed}: no θ in {THETA_MAX_DRAWS} draws clears the world's clearance points")


class ThetaRefused(RuntimeError):
    """No θ of the start seed's stream clears the world's clearance points for this body on this draw (FC-M2): the draw
    is excluded from that genome's battery and counted, never fatal to the call."""


class DecoySimulation(Simulation):
    """Food sensors smell the live layout rotated by ``_rot`` about the origin, before any transform.  Everything that
    is not a food sensor's reading (eating, regrowth, clearance, the real ``food_pos``) is the parent's."""

    _rot: Optional[float] = None

    def _rotated(self, sources):
        if self._rot is not None and sources is self.food_pos:
            return rotate(sources, self._rot)
        return sources

    def _log_smell(self, point, sources):
        return Simulation._log_smell(self, point, self._rotated(sources))

    def _intensity(self, point, sources):
        return Simulation._intensity(self, point, self._rotated(sources))


_LAYOUT_METHODS = ("_draw_patch_centres", "_food_spot", "set_food_seed", "_install_spots", "_eat", "_regrow_spots", "_clearance_points")


def _fingerprint(fn) -> tuple:
    """What identifies a committed layout method even after a module-level monkeypatch of ``Simulation``: where it was
    defined, and a digest of its bytecode and constants."""
    fn = getattr(fn, "__func__", fn)
    code = getattr(fn, "__code__", None)
    if code is None:
        return (getattr(fn, "__module__", None), getattr(fn, "__qualname__", None), None)
    h = hashlib.sha256(code.co_code + repr(code.co_consts).encode() + repr(code.co_names).encode()).hexdigest()
    return (fn.__module__, fn.__qualname__, h)


#: the committed layout methods, fingerprinted when steer.py is imported; each must also be defined in
#: rabbitstew.simulation as ``Simulation.<name>`` (so a patch applied before this import is refused too)
_COMMITTED_LAYOUT = {m: _fingerprint(getattr(Simulation, m)) for m in _LAYOUT_METHODS}


def assert_rotation_invariant(cfg: SimConfig, cls: type = Simulation) -> None:
    """Refuse a layout rule the rotation does not map to itself (SHOULD 2, R15).  The committed rule draws patch centres
    and items uniformly in a disc about the origin (``Simulation._draw_patch_centres``, ``_food_spot``), which any
    rotation about the origin preserves; a subclass that overrides any layout method, a world whose smell target is
    not a disc about the origin, or no food world at all, is refused."""
    if cfg.food is None:
        raise ValueError("the decoy needs a food world")
    for m in _LAYOUT_METHODS:
        fp = _fingerprint(getattr(cls, m))
        if fp != _COMMITTED_LAYOUT[m] or fp[:2] != ("rabbitstew.simulation", f"Simulation.{m}"):
            raise ValueError(f"the layout method {m} is not the committed one on {cls.__name__}: rotation invariance is not established")
    if not cfg.food.radius > 0:
        raise ValueError("the food disc must have a positive radius")
    if cfg.food.clear_from not in CLEAR_FROM or cfg.food.eat_rule not in EAT_RULES:
        raise ValueError("the decoy's clearance follows the world's clear_from / eat_rule, and these are not committed rules")


# --------------------------------------------------------------------------- #
# One season
# --------------------------------------------------------------------------- #


@dataclass
class Season:
    """What one season records (§1.2).  ``speed``/``proj``/``grad`` are per control tick; T is computed from them against
    a speed bar (:func:`chemotaxis_index`), because the decoy season is read on its intact partner's bar."""

    condition: str
    draw: Draw
    food: float
    work: float
    net: float
    exploded: bool
    cells: int
    traj: np.ndarray = field(repr=False)
    speed: np.ndarray = field(repr=False)
    proj: np.ndarray = field(repr=False)
    grad: np.ndarray = field(repr=False)
    pen: float = 0.0
    disp: float = 0.0
    theta: Optional[float] = None
    redraws: int = 0
    food_abs_max: float = 0.0  #: the largest |reading| of any food sensor over the season (0 under the lesion)

    @property
    def items_per_100_cells(self) -> float:
        return 100.0 * self.food / self.cells if self.cells else 0.0

    @property
    def traj_hash(self) -> str:
        """The root's path, rounded to TRAJ_TOL, hashed (reported; the veto compares the paths themselves)."""
        q = np.round(np.asarray(self.traj) / TRAJ_TOL).astype(np.int64)
        return hashlib.sha256(q.tobytes()).hexdigest()[:16]

    def v_min(self) -> float:
        """This (intact) season's speed bar: 0.25 × its median |v| over every control tick."""
        return V_MIN_FRAC * float(np.median(self.speed)) if len(self.speed) else 0.0


def chemotaxis_index(s: Season, v_min: float) -> tuple:
    """T = Σ|v| cos∠(v, ĝ) / Σ|v| over ticks with |v| > v_min and a defined ĝ (§1.2).  Returns ``(T, flagged,
    excluded_share)``: T := 0 and flagged when no tick qualifies."""
    inc = (s.speed > v_min) & s.grad
    n = len(s.speed)
    excl = 1.0 - (int(inc.sum()) / n if n else 0.0)
    den = float(s.speed[inc].sum())
    if not inc.any() or den <= 0:
        return 0.0, True, excl
    return float(s.proj[inc].sum()) / den, False, excl


def _unit_gradient(p: np.ndarray, live: np.ndarray, decay: float) -> Optional[np.ndarray]:
    """Unit gradient at ``p`` of the real field Σ exp(−d/decay) (analytic); None with no live item or a null gradient."""
    if not len(live):
        return None
    diff = live - p
    d = np.linalg.norm(diff, axis=1)
    ok = d > 1e-12
    if not ok.any():
        return None
    w = np.exp(-d[ok] / decay) / decay
    g = (w[:, None] * diff[ok] / d[ok, None]).sum(axis=0)
    n = float(np.linalg.norm(g))
    return g / n if n > 1e-300 else None


def _live_items(sim: Simulation) -> np.ndarray:
    pos = np.asarray(sim.food_pos, dtype=float).reshape(-1, 2)
    return pos[sim.food_alive] if len(sim.food_alive) == len(pos) else pos[np.abs(pos).max(axis=1) < 1e5]


def registered_tau(point: str = "W1") -> float:
    """The contrast channel's registered τ at ``point`` (RBT-132: per point; W1's is SMELL_TAU).  An unregistered point
    has no τ and is refused."""
    if point not in REGISTERED_POINTS:
        raise KeyError(f"world point {point!r} is not registered: no τ to check the channel against")
    return REGISTERED_POINTS[point]["smell_tau"]


def assert_registered_channel(cfg: SimConfig, point: str = "W1") -> None:
    """Refuse a world whose contrast channel runs at another τ than its point's registration (Amendment 1, revised;
    RBT-132: τ per point, W1's 1 s by default).  A channel at a point that registers none (an L point) is refused too."""
    tau = registered_tau(point)
    f = cfg.food
    if f is not None and f.smell_contrast > 0 and (f.smell_tau != tau or REGISTERED_POINTS[point]["smell_contrast"] <= 0):
        raise ValueError(f"{point} registers smell_tau = {tau} s (channel {'on' if REGISTERED_POINTS[point]['smell_contrast'] > 0 else 'off'}); this world has {f.smell_tau} s")


def assert_world_point(cfg: SimConfig, world: str) -> None:
    """Refuse a config whose food block differs from its registered world point's (FC-M2 eating rule; FC-S3: a lost
    ``--smell-contrast`` would run the legacy channel)."""
    if world not in REGISTERED_POINTS:
        raise KeyError(f"world point {world!r} has no registered block")
    f = cfg.food
    if f is None:
        raise ValueError(f"{world} is a food world")
    bad = {k: (getattr(f, k), v) for k, v in REGISTERED_POINTS[world].items() if getattr(f, k) != v}
    if bad:
        raise ValueError(f"the config differs from {world}'s registered block: " + ", ".join(f"{k} {a!r} (registered {b!r})" for k, (a, b) in bad.items()))


def run_season(genome, cfg: SimConfig, draw: Draw, condition: str, point: str = "W1") -> Season:
    """One solo season of ``genome`` (a Genotype or its dict) in ``cfg`` on ``draw``, under ``condition``.  ``point`` is
    the registered world point whose τ the channel is checked against (RBT-132; W1 by default)."""
    if condition not in CONDITIONS:
        raise ValueError(f"condition must be one of {CONDITIONS}")
    g = genome if isinstance(genome, Genotype) else Genotype.from_dict(genome)
    cfg = replace(draw_sim(cfg, draw), opponent_proxy=True)  # run_solo's season
    if cfg.food is None:
        raise ValueError("the battery needs a food world")
    assert_registered_channel(cfg, point)
    if condition == "lesion":
        cfg = replace(cfg, food=replace(cfg.food, smell_lesion=True))
    cls = DecoySimulation if condition == "decoy" else Simulation
    if condition == "decoy":
        assert_rotation_invariant(cfg, cls)
    spawn = spawn_layout(2, cfg, draw.start_seed)[0]
    sim = cls([g], cfg, spawns=[spawn])
    if cfg.waypoints:
        sim.set_waypoint_seed(draw.start_seed)
    sim.set_food_seed(draw.start_seed)
    idx = sim.robots[0]
    theta, redraws = None, 0
    if condition == "decoy":
        theta, redraws = draw_theta(draw.start_seed, _live_items(sim), world_clearance(sim))
        sim._rot = theta
    if condition == "motors-off":
        sim.brains[0].effector_output = lambda *a: 0.0
    geoms = np.asarray(idx.geoms, dtype=int)
    brain = sim.brains[0]
    food_units = np.array([sp.unit for sp in brain.sensors if sp.source == "food"], dtype=int)
    food_abs = 0.0
    n = int(round(cfg.duration / cfg.control_dt))
    traj = np.zeros((n + 1, 2))
    speed, proj, grad = np.zeros(n), np.zeros(n), np.zeros(n, dtype=bool)
    traj[0] = sim.data.xpos[idx.root_body][:2]
    com = np.array(sim.data.subtree_com[idx.root_body][:2])
    com0 = com.copy()
    cells = {tuple(c) for c in np.floor(sim.data.geom_xpos[geoms][:, :2] / CELL).astype(int).tolist()}
    pen = 0.0
    for t in range(n):
        gdir = _unit_gradient(com, _live_items(sim), cfg.food.decay)
        sim.step()
        if len(food_units):  # this tick's readings, as the brain received them
            food_abs = max(food_abs, float(np.abs(brain.activation[food_units]).max()))
        nxt = np.array(sim.data.subtree_com[idx.root_body][:2])
        v = (nxt - com) / cfg.control_dt
        speed[t] = float(np.linalg.norm(v))
        if gdir is not None:
            grad[t] = True
            proj[t] = float(v @ gdir)
        com = nxt
        traj[t + 1] = sim.data.xpos[idx.root_body][:2]
        cells.update(tuple(c) for c in np.floor(sim.data.geom_xpos[geoms][:, :2] / CELL).astype(int).tolist())
        nc = sim.data.ncon
        if nc:
            con = sim.data.contact
            mine = np.isin(con.geom1[:nc], geoms) | np.isin(con.geom2[:nc], geoms)
            if mine.any():
                pen = max(pen, float(-con.dist[:nc][mine].min()))
    h = sim.harvest(0)
    net = float(h["food"] * cfg.food.value - cfg.food.work_cost * h["work"] / 1000.0)
    return Season(condition, draw, h["food"], h["work"], net, h["exploded"], len(cells), traj, speed, proj, grad,
                  max(pen, 0.0), float(np.linalg.norm(com - com0)), theta, redraws, food_abs)


def trajectories_differ(a: Season, b: Season) -> bool:
    """The veto's test: the root's xy differs by more than TRAJ_TOL at some tick."""
    if a.traj.shape != b.traj.shape:
        return True
    return bool(np.abs(a.traj - b.traj).max() > TRAJ_TOL)


# --------------------------------------------------------------------------- #
# Statistics (no scipy)
# --------------------------------------------------------------------------- #


def _betacf(a: float, b: float, x: float) -> float:
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(1.0 + aa / c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(1.0 + aa / c) > 1e-300 else 1e-300
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-15:
            break
    return h


def _betainc(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1.0 - x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1.0 - x) / b


def t_cdf(t: float, df: int) -> float:
    x = df / (df + t * t)
    p = 0.5 * _betainc(df / 2.0, 0.5, x)
    return 1.0 - p if t > 0 else p


def t_quantile(p: float, df: int) -> float:
    """The Student-t quantile, by bisection on :func:`t_cdf` (t_quantile(0.95, 15) = 1.7531)."""
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def lower_bound(x: Sequence[float]) -> float:
    """One-sided 95% t lower bound on the mean.  With no spread it is the mean (a constant difference is its own
    bound); with one value it is −inf (no bound exists)."""
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return -math.inf
    sd = float(x.std(ddof=1))
    if sd == 0.0:
        return float(x.mean())
    return float(x.mean() - t_quantile(0.95, len(x) - 1) * sd / math.sqrt(len(x)))


# --------------------------------------------------------------------------- #
# The call
# --------------------------------------------------------------------------- #

SeasonFn = Callable[[object, SimConfig, Draw, str], Season]


def _pairs(genome, cfg, draws, season: SeasonFn, conditions=("intact", "decoy")) -> tuple:
    """Every condition on every draw, decoy first: a draw whose decoy has no clear θ (:class:`ThetaRefused`) is
    excluded from all conditions and returned in ``refused`` (FC-M2)."""
    runs, refused = {c: [] for c in conditions}, []
    for d in draws:
        try:
            dec = season(genome, cfg, d, "decoy")
        except ThetaRefused:
            refused.append(d)
            continue
        for c in conditions:
            runs[c].append(dec if c == "decoy" else season(genome, cfg, d, c))
    return runs, refused


def battery_stats(runs: dict) -> dict:
    """F, ΔT and the veto on one battery's intact/decoy pairs (and L and motors-off food when those ran)."""
    I, D = runs["intact"], runs["decoy"]
    fi = np.array([s.food for s in I])
    dF = fi - np.array([s.food for s in D])
    ti, td, flags, excl = [], [], 0, []
    for a, b in zip(I, D):
        vm = a.v_min()
        t_a, f_a, e_a = chemotaxis_index(a, vm)
        t_b, f_b, e_b = chemotaxis_index(b, vm)  # the decoy season on its intact partner's bar (§1.2)
        ti.append(t_a)
        td.append(t_b)
        flags += int(f_a) + int(f_b)
        excl += [e_a, e_b]
    dT = np.array(ti) - np.array(td)
    differ = sum(trajectories_differ(a, b) for a, b in zip(I, D))
    F, lbF, lbT = float(dF.mean()), lower_bound(dF), lower_bound(dT)
    out = {"n": len(I), "F": F, "lbF": lbF, "dT": float(dT.mean()), "lbdT": lbT, "differ": int(differ),
           "food_intact": float(fi.mean()), "T_intact": float(np.mean(ti)), "T_decoy": float(np.mean(td)),
           "flagged": int(flags), "excluded_share": float(np.mean(excl)) if excl else 0.0,
           "F_min_rel": max(F_MIN, F_MIN_REL * float(fi.mean())),
           "redraws": int(sum(s.redraws for s in D))}
    out["c1"] = bool(F >= F_MIN and lbF > 0)
    out["c2"] = bool(lbT > 0)
    out["c3"] = bool(2 * differ > len(I))  # more than half the draws
    out["passes"] = out["c1"] and out["c2"] and out["c3"]
    out["c1_rel"] = bool(F >= out["F_min_rel"] and lbF > 0)
    if "lesion" in runs:
        out["L"] = float(np.mean(fi - np.array([s.food for s in runs["lesion"]])))
    if "motors-off" in runs:
        off = runs["motors-off"]
        out["off_food"] = float(np.mean([s.food for s in off]))
        out["off_disp"] = float(np.mean([s.disp for s in off]))
    return out


def call_genome(genome, cfg: SimConfig, battery: Battery, season: SeasonFn = run_season) -> dict:
    """The §1.3 call on one genome: ``{"call": STEERS | SMELL-USE | NONE, "stage": 1 | 2 | 3, ...}``.

    ``stage`` is where the call was decided: 1 (stopped by the trajectory screen), 2 (not PASS on stage 2), 3 (read on
    the confirmation battery).  ``pass_unconfirmed`` marks a stage-2 PASS that the confirmation did not repeat: it is
    NONE by §1.3's letter and is reported beside the call (STEER_NOTES N3)."""
    s1, ref1 = _pairs(genome, cfg, battery.stage1, season)
    same = [not trajectories_differ(a, b) for a, b in zip(s1["intact"], s1["decoy"])]
    rec = {"call": NONE, "stage": 1, "stage1_identical": int(sum(same)), "pass_unconfirmed": False,
           "theta_attempted": len(battery.stage1), "theta_refused": len(ref1), "too_few_draws": False}
    if same:  # a stage 1 with every draw refused screens nothing, so it cannot stop the genome
        if all(same):
            return _refusal_rate(rec)
    runs2, ref2 = _pairs(genome, cfg, battery.stage2, season, CONDITIONS)
    rec.update(stage=2, theta_attempted=rec["theta_attempted"] + len(battery.stage2), theta_refused=rec["theta_refused"] + len(ref2))
    if len(runs2["intact"]) < MIN_USABLE:
        rec["too_few_draws"] = True
        return _refusal_rate(rec)
    s2 = battery_stats(runs2)
    rec["stage2"] = s2
    if not s2["passes"]:
        rec["call"] = SMELL_USE if (s2["c1"] and s2["c3"] and not s2["c2"]) else NONE
        return _refusal_rate(rec)
    runs3, ref3 = _pairs(genome, cfg, battery.confirm, season)
    rec.update(stage=3, theta_attempted=rec["theta_attempted"] + len(battery.confirm), theta_refused=rec["theta_refused"] + len(ref3))
    if len(runs3["intact"]) < MIN_USABLE:
        rec.update(too_few_draws=True, pass_unconfirmed=True)
        return _refusal_rate(rec)
    c = battery_stats(runs3)
    rec.update(confirm=c)
    _refusal_rate(rec)
    if c["passes"]:
        rec["call"] = STEERS
    else:
        rec["pass_unconfirmed"] = True
    return rec


def _refusal_rate(rec: dict) -> dict:
    rec["theta_refusal_rate"] = rec["theta_refused"] / rec["theta_attempted"] if rec["theta_attempted"] else 0.0
    return rec


# --------------------------------------------------------------------------- #
# The draw screen (MUST 1 / M1)
# --------------------------------------------------------------------------- #


def admissible(ate: int, hosts: int, world: str = "W1") -> bool:
    """The screen's rule for one draw: at least half the hosts eat ≥ 1 item (§1.1, W1), or at a ``SCREEN_ANY`` point at
    least one does."""
    return ate >= 1 if world in SCREEN_ANY else 2 * ate >= hosts


def screen_dispersion(table: list) -> dict:
    """The screen table's eat counts against Binomial(hosts, p̂): p̂, the variance ratio, and how many draws each rule
    admits, and each control's P(eat) where the table has ``ate_by_host``.  A per-draw count sums over the controls, so
    the ratio alone cannot separate host heterogeneity from draw heterogeneity; ``host_p`` shows the hosts' side."""
    if not table:
        return {"p": float("nan"), "ratio": float("nan"), "half": 0, "any": 0, "draws": 0, "host_p": None}
    ate = np.array([r["ate"] for r in table], dtype=float)
    n = table[0]["hosts"]
    p = float(ate.mean() / n)
    vb = n * p * (1 - p)
    by = [r["ate_by_host"] for r in table if "ate_by_host" in r]
    host_p = [float(x) for x in np.mean(by, axis=0)] if len(by) == len(table) else None
    return {"p": p, "ratio": float(ate.var(ddof=1) / vb) if vb > 0 and len(ate) > 1 else float("nan"),
            "half": int((2 * ate >= n).sum()), "any": int((ate >= 1).sum()), "draws": len(table), "host_p": host_p}


def screen_draws(hosts: Sequence, cfg: SimConfig, world: str = "W1", season: SeasonFn = run_season) -> dict:
    """The reachability screen (§1.1): every pool draw is run intact on the positive-control hosts (G8(a) and G8(c),
    which ``gate.py`` supplies).  A draw is admissible iff at least half the hosts eat ≥ 1 item on it.  If fewer than
    the point's battery (36; :func:`battery_size`) are admissible, the pool is extended once (by 32 at the registered
    count); if that still fails, the world point fails its gate
    (``battery`` None, ``passed`` False).  ``table`` is the per-draw reachability table to commit."""
    if not hosts:
        raise ValueError("the screen needs the positive-control hosts")
    if season is run_season and world != "W1":  # RBT-132: the point's own τ, not W1's
        season = point_season(world)

    def run(draws):
        rows = []
        for d in draws:
            by_host = [int(season(h, cfg, d, "intact").food >= 1) for h in hosts]
            ate = sum(by_host)
            rows.append({"terrain_seed": d.terrain_seed, "start_seed": d.start_seed, "hosts": len(hosts), "ate": int(ate), "admissible": admissible(int(ate), len(hosts), world)})
            if world != "W1":  # #478's ruling S-1: which control ate, in host order (W1's table stays as registered)
                rows[-1]["ate_by_host"] = by_host
        return rows

    size = battery_size(world)
    pool = draw_pool(world)
    table = run(pool)
    extended = False
    if sum(r["admissible"] for r in table) < size["battery"]:
        extended = True
        table += run(draw_pool(world, extended=True)[size["pool"]:])
    adm = [Draw(r["terrain_seed"], r["start_seed"]) for r in table if r["admissible"]]
    battery = assign_battery(adm, world)
    return {"world": world, "table": table, "extended": extended, "admissible": len(adm), "battery": battery, "passed": battery is not None}


# --------------------------------------------------------------------------- #
# Lines: the K and K + 2 reading (§1.4, R6-1) and the SMELL-USE print (§6.4)
# --------------------------------------------------------------------------- #


def crossed(n_u: int, n_n: int, k: int) -> bool:
    """§1.4: U has ≥ k confirmed steerers, and ≥ k more than N."""
    return n_u >= k and n_u - n_n >= k


def line_reading(calls_u: Sequence[str], calls_n: Sequence[str], k: int = K_REGISTERED) -> dict:
    """One line at one probe: STEERS and SMELL-USE counts and shares in U and N, the U − N SMELL-USE share (R6-1), and
    crossing at K and at K + 2.  ``calls_*`` are the members' calls."""
    def share(calls, lab):
        return sum(c == lab for c in calls) / len(calls) if calls else 0.0

    su, sn = sum(c == STEERS for c in calls_u), sum(c == STEERS for c in calls_n)
    out = {"M_U": len(calls_u), "M_N": len(calls_n), "steers_U": su, "steers_N": sn,
           "steers_share_U": share(calls_u, STEERS), "steers_share_N": share(calls_n, STEERS),
           "smell_use_share_U": share(calls_u, SMELL_USE), "smell_use_share_N": share(calls_n, SMELL_USE),
           "K": k, "K2": k + K_HEADLINE_STEP, "crossed_K": crossed(su, sn, k), "crossed_K2": crossed(su, sn, k + K_HEADLINE_STEP)}
    out["smell_use_share_diff"] = out["smell_use_share_U"] - out["smell_use_share_N"]
    out["steers_share_diff"] = out["steers_share_U"] - out["steers_share_N"]
    return out


def smell_use_print(label: str, r: dict) -> str:
    """The per-probe line (§6.4, R6-1): STEERS and SMELL-USE shares, U − N, and crossing at K and K + 2."""
    return (f"{label} | STEERS U {r['steers_U']}/{r['M_U']} N {r['steers_N']}/{r['M_N']} (U−N {r['steers_share_diff']:+.3f}) | "
            f"SMELL-USE U {r['smell_use_share_U']:.3f} N {r['smell_use_share_N']:.3f} U−N {r['smell_use_share_diff']:+.3f} | "
            f"crossed K={r['K']} {'yes' if r['crossed_K'] else 'no'}, K+2={r['K2']} {'yes' if r['crossed_K2'] else 'no'}")


# --------------------------------------------------------------------------- #
# Output rows and the command line
# --------------------------------------------------------------------------- #


def format_call(name: str, rec: dict) -> str:
    """One steer.txt row per genome (§9: per probed member)."""
    s2 = rec.get("stage2")
    head = (f"{name} | {rec['call']:9s} | stage {rec['stage']} | stage-1 identical {rec['stage1_identical']}/{N_STAGE1} | "
            f"θ refused {rec.get('theta_refused', 0)}/{rec.get('theta_attempted', 0)}" + (" TOO-FEW-DRAWS" if rec.get("too_few_draws") else ""))
    if s2 is None:
        return head
    row = (f"{head} | F {s2['F']:+.3f} lb {s2['lbF']:+.3f} (F_min_rel {s2['F_min_rel']:.3f}: {'meets' if s2['c1_rel'] else 'fails'}) | "
           f"dT {s2['dT']:+.3f} lb {s2['lbdT']:+.3f} | differ {s2['differ']}/{s2['n']} | L {s2.get('L', float('nan')):+.3f} | "
           f"off food {s2.get('off_food', float('nan')):.2f} disp {s2.get('off_disp', float('nan')):.3f} | "
           f"T-flagged {s2['flagged']} excluded {s2['excluded_share']:.2f} | decoy redraws {s2['redraws']}")
    c = rec.get("confirm")
    if c is not None:
        row += f" | confirm F {c['F']:+.3f} lb {c['lbF']:+.3f} dT lb {c['lbdT']:+.3f} differ {c['differ']}/{c['n']}" + (" | PASS-UNCONFIRMED" if rec["pass_unconfirmed"] else "")
    return row


def _job(args):
    gd, cfg_d, bat_d = args[:3]
    point = args[3] if len(args) > 3 else "W1"
    season = run_season if point == "W1" else point_season(point)
    return call_genome(gd, SimConfig.from_dict(cfg_d), Battery.from_dict(bat_d), season)


def _strip(rec: dict) -> dict:
    return json.loads(json.dumps(rec, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))


def point_season(point: str) -> SeasonFn:
    """``run_season`` at a registered point (RBT-132): the season function ``call_genome`` and ``screen_draws`` take, so
    the τ guard reads that point's registration.  A picklable partial."""
    registered_tau(point)
    return functools.partial(run_season, point=point)


def sim_hash(sim: dict) -> str:
    """A config's ``sim`` block, canonically serialised and hashed (16 hex digits)."""
    return hashlib.sha256(json.dumps(sim, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def assert_point_world(raw: dict, point: str) -> None:
    """RBT-132 S1: at a point with a committed block, the config's whole ``sim`` block must be that block (layout,
    clutter and everything else, not only the smell and eating fields ``assert_world_point`` reads)."""
    if point in POINT_SIM_HASH:
        got = sim_hash(raw.get("sim", raw))
        if got != POINT_SIM_HASH[point]:
            raise ValueError(f"the config's sim block (hash {got}) is not {point}'s committed block ({POINT_SIM_HASH[point]})")


def assert_fair_config(raw: dict, point: str) -> None:
    """RBT-132: an RBT-129 point runs only on a config RBT-128's --fair built (its top-level marker), as steps.py's S12."""
    if point in FAIR_POINTS and raw.get("fairness") != "fair":
        raise ValueError(f"{point} runs only on a --fair config (fairness {raw.get('fairness')!r})")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--config", required=True, help="a SimConfig json (or a run's config.json with a 'sim' block): the world point")
    ap.add_argument("--battery", required=True, help="the screened battery (json with stage1, stage2, confirm), as screen_draws writes it")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--world", default="W1", help="the registered world point the config must match (REGISTERED_POINTS)")
    ap.add_argument("--json", help="also write every call record here")
    ap.add_argument("genomes", nargs="+")
    a = ap.parse_args(argv)
    raw = json.load(open(a.config))
    cfg = SimConfig.from_dict(raw.get("sim", raw))
    battery = Battery.from_dict(json.load(open(a.battery)))
    assert_rotation_invariant(cfg, DecoySimulation)
    assert_registered_channel(cfg, a.world)
    assert_world_point(cfg, a.world)
    assert_fair_config(raw, a.world)
    assert_point_world(raw, a.world)
    tasks = [(Genotype.load(p).to_dict(), cfg.to_dict(), battery.to_dict(), a.world) for p in a.genomes]
    if a.workers > 1:
        with ProcessPoolExecutor(a.workers) as pool:
            recs = list(pool.map(_job, tasks, chunksize=1))
    else:
        recs = [_job(t) for t in tasks]
    print(f"# RBT-116 steer.py: {len(recs)} genomes; F_MIN {F_MIN}; stages {N_STAGE1}+{N_STAGE2}+{N_CONFIRM}; "
          f"smell_contrast {cfg.food.smell_contrast} smell_tau {cfg.food.smell_tau}; pen is sampled per control tick")
    for p, r in zip(a.genomes, recs):
        print(format_call(os.path.basename(p), r), flush=True)
    if a.json:
        with open(a.json, "w") as f:
            json.dump([{"genome": p, **_strip(r)} for p, r in zip(a.genomes, recs)], f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
