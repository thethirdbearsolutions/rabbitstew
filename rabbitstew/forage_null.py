"""What a gait meets by accident: the trajectory-preserving null for foraging yield (RBT-39).

The family's test for "compass, or just a mower" has compared a robot's yield against
``2 * eat_radius * density``, the rate at which a *point* robot sweeping a fresh straight line
through a uniform field meets items.  Real robots here break all three assumptions.  They are not
points: an item is eaten when *any* geom comes within ``eat_radius`` (:meth:`Simulation._eat` takes
a minimum over geoms), so a multi-part body sweeps a corridor wider than ``2 * eat_radius`` and
clears the floor with no sensing at all.  They are not fresh lines: a robot that circles or retraces
re-covers swept ground.  And with regrowth the field is not stationary.

Counting distinct cells instead of metres does not fix this; it relocates it.  A cell count taken
from the centre of mass, on a grid of ``2 * eat_radius``, is a point-robot denominator under another
name, while the numerator still counts eating by any geom, so a wide body eats in cells its centre
never entered.

The null here removes the assumption rather than correcting it.  Replay the robot's **own recorded
path** against fresh item layouts: the gait, the circling, the retracing and the body geometry are
held exactly as they were, and the only thing removed is any correlation between where the robot
went and where the food actually was.  What it eats under that null is what its gait meets by
accident.  The question the floor was always trying to ask is then

    does this robot collect food faster than its own gait would by accident?

and it is answered by comparing the real bout against the null draws, paired on the same path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

PARKED = 1e6  #: an item eaten in an arena that does not regrow, matching ``Simulation``


@dataclass
class NullResult:
    """A champion's real yield beside what its own gait meets by accident."""

    observed: float  #: items the robot actually ate
    null_mean: float  #: mean items under the trajectory null
    null_sd: float
    draws: int
    path: float  #: in-disc path length (m), for reporting rates as well as counts

    @property
    def ratio(self) -> float:
        """Observed over null. 1.0 is "no better than its own gait by accident"."""
        return self.observed / self.null_mean if self.null_mean > 0 else float("nan")

    @property
    def z(self) -> float:
        """How many null standard deviations the observed yield sits above the null mean."""
        return (self.observed - self.null_mean) / self.null_sd if self.null_sd > 0 else float("nan")

    def verdict(self, margin: float = 2.0) -> str:
        if not np.isfinite(self.z):
            return "undecidable (the null has no spread)"
        if self.z >= margin:
            return "above its own gait's expectation"
        if self.z <= -margin:
            return "below its own gait's expectation"
        return "indistinguishable from its own gait"


def draw_layout(n: int, rng: np.random.Generator, radius: float, avoid: Optional[np.ndarray] = None, clearance: float = 0.0) -> np.ndarray:
    """``n`` items uniform on the disc, honouring the clearance rule the simulator uses."""
    out = np.empty((n, 2))
    for i in range(n):
        for _ in range(64):
            r = radius * np.sqrt(rng.random())
            a = rng.uniform(0, 2 * np.pi)
            p = np.array([r * np.cos(a), r * np.sin(a)])
            if avoid is None or not len(avoid) or np.linalg.norm(avoid - p, axis=1).min() >= clearance:
                break
        out[i] = p
    return out


def replay(geoms: np.ndarray, items: np.ndarray, eat_radius: float, regrow: bool = True,
           rng: Optional[np.random.Generator] = None, radius: float = 3.0, clearance: float = 0.0,
           spot_fn=None) -> tuple:
    """Run a recorded path past a food layout and count what it takes.

    ``geoms`` is ``(frames, geoms, 2)``, the recorded horizontal position of every geom; ``items``
    is ``(n, 2)``.  The eating rule is the simulator's: an item goes when the nearest geom is inside
    ``eat_radius``, and then either regrows at a fresh spot or is parked.  Returns
    ``(eaten, events)``, where each event is ``(frame, x, y)`` so a replay can be checked against a
    recorded bout event for event.

    ``spot_fn(frame) -> (2,)`` supplies a regrown item's spot; pass
    :func:`world_spot_fn` to draw it from the world's own generator (patches, clearance) instead of
    the uniform-disc fallback.
    """
    pos = np.array(items, dtype=float).reshape(-1, 2).copy()
    rng = rng or np.random.default_rng(0)
    eaten, events = 0, []
    for f, frame in enumerate(geoms):
        if not len(pos):
            break
        d = np.linalg.norm(frame[:, None, :] - pos[None, :, :], axis=2).min(axis=0)
        for j in np.nonzero(d < eat_radius)[0]:
            eaten += 1
            events.append((f, float(pos[j, 0]), float(pos[j, 1])))
            if not regrow:
                pos[j] = PARKED
            elif spot_fn is not None:
                pos[j] = spot_fn(frame)
            else:
                pos[j] = draw_layout(1, rng, radius, avoid=frame, clearance=clearance)[0]
    return eaten, events


def replay_many(geoms: np.ndarray, layouts: np.ndarray, eat_radius: float, regrow: bool = True,
                spot_fn=None, rng: Optional[np.random.Generator] = None, radius: float = 3.0,
                clearance: float = 0.0) -> np.ndarray:
    """:func:`replay` for a stack of layouts at once: ``layouts`` is ``(draws, n, 2)``, the return
    is the count each draw yields.  One path against two hundred layouts is the null's whole cost,
    and doing the draws together is what makes it a second rather than a minute.
    """
    pos = np.array(layouts, dtype=float)
    if pos.ndim == 2:
        pos = pos[None]
    pos = pos.copy()
    rng = rng or np.random.default_rng(0)
    counts = np.zeros(len(pos), dtype=int)
    if not pos.shape[1]:
        return counts
    for frame in geoms:
        d = np.linalg.norm(frame[None, :, None, :] - pos[:, None, :, :], axis=3).min(axis=1)
        hit = d < eat_radius
        if not hit.any():
            continue
        counts += hit.sum(axis=1)
        di, ji = np.nonzero(hit)
        if not regrow:
            pos[di, ji] = PARKED
        elif spot_fn is not None:
            for a, b in zip(di, ji):
                pos[a, b] = spot_fn(frame)
        else:
            for a, b in zip(di, ji):
                pos[a, b] = draw_layout(1, rng, radius, avoid=frame, clearance=clearance)[0]
    return counts


def world_spot_fn(sim):
    """A ``spot_fn`` that draws a regrown item the way ``sim``'s world draws one.

    The simulator clears a new spot of the robots' **root body** positions; the recorded trajectory
    carries geom positions, and geom 0 is the root body's own geom, so that is what is passed
    through.  Using this rather than a plain uniform draw is what lets the null describe a patchy
    world as a patchy world.
    """
    def draw(frame: np.ndarray) -> np.ndarray:
        return sim.draw_food_spot(np.asarray(frame[0], dtype=float).reshape(1, 2))
    return draw


def world_layouts(sim, seeds) -> np.ndarray:
    """``(draws, n, 2)`` fresh item layouts from ``sim``'s own generator, one per seed.

    Call this immediately after ``set_food_seed`` and **before stepping**: the clearance rule is
    applied against wherever the robots are standing, which at that moment is the spawn layout the
    real bout also started from.  The caller must re-seed to the real food seed afterwards to put
    the bout back (re-seeding is deterministic given the robots' positions, so it restores exactly).
    """
    out = []
    for s in seeds:
        sim.set_food_seed(int(s))
        out.append(sim.food_pos.copy())
    return np.array(out, dtype=float)


def body_line_rate(shape: np.ndarray, layouts: np.ndarray, eat_radius: float, radius: float,
                   regrow: bool = True, spot_fn=None, step: float = 0.01) -> float:
    """Items per metre a body of this shape meets sweeping a **fresh straight chord** of the disc.

    This is the point-robot floor with exactly one assumption repaired: the robot is no longer a
    point, but it still travels a fresh straight line through a stationary field.  Comparing it with
    ``2 * eat_radius * density`` isolates the body-width term; comparing the trajectory null with
    *it* isolates the gait term -- the circling, the retracing and the time spent off the disc.
    Splitting them matters because the two pull in opposite directions.

    ``shape`` is ``(geoms, 2)`` offsets from the body's centroid, held rigid, which is what makes
    this a property of the body rather than of a bout.  The chord runs through the centre at
    ``step`` metres a frame, fine enough that nothing is missed between frames.
    """
    shape = np.asarray(shape, dtype=float).reshape(-1, 2)
    shape = shape - shape.mean(axis=0)
    xs = np.arange(-radius, radius + step, step)
    path = np.stack([shape + np.array([x, 0.0]) for x in xs])
    counts = replay_many(path, layouts, eat_radius, regrow=regrow, spot_fn=spot_fn, radius=radius)
    return float(counts.mean() / (xs[-1] - xs[0]))


def trajectory_null(geoms: np.ndarray, layouts: np.ndarray, observed: float, eat_radius: float,
                    radius: float, regrow: bool = True, spot_fn=None) -> NullResult:
    """The ticket's null: one recorded path, many layouts the world could equally have dealt it."""
    counts = replay_many(geoms, layouts, eat_radius, regrow=regrow, spot_fn=spot_fn, radius=radius).astype(float)
    return NullResult(observed=float(observed), null_mean=float(counts.mean()),
                      null_sd=float(counts.std(ddof=1)) if len(counts) > 1 else 0.0,
                      draws=len(counts), path=in_disc_path(geoms, radius))


def in_disc_path(geoms: np.ndarray, radius: float) -> float:
    """Path length of the body's centroid while it is inside the food disc."""
    c = geoms.mean(axis=1)
    inside = np.linalg.norm(c, axis=1) <= radius
    steps = np.linalg.norm(np.diff(c, axis=0), axis=1)
    return float(steps[inside[:-1] & inside[1:]].sum())


def swept_width(geoms: np.ndarray, eat_radius: float) -> float:
    """The corridor this body actually clears, as twice the furthest a geom reaches from the
    centroid plus the eat radius.  Reported for comparison with the ``2 * eat_radius`` the old
    floor assumed; the null itself never needs it."""
    reach = np.linalg.norm(geoms - geoms.mean(axis=1)[:, None, :], axis=2).max()
    return 2.0 * (reach + eat_radius)


def live_items(food_frame) -> np.ndarray:
    """The items actually standing at the start of a bout, from a recorded food frame.

    A world's ``items`` setting is a count of *spots*, and where regrowth is delayed roughly half of
    them stand empty when a season opens, so drawing a null of ``items`` live items over-feeds it.
    """
    a = np.asarray(food_frame, dtype=float).reshape(-1, 2)
    return a[np.isfinite(a).all(axis=1)]


def rotation_null(geoms: np.ndarray, items: np.ndarray, observed: float, eat_radius: float, radius: float,
                  draws: int = 180, regrow: bool = False, clearance: float = 0.0, seed: int = 0) -> NullResult:
    """The null of choice for a structured field: the robot's own path against its **own layout,
    rotated** about the disc centre.

    Drawing a fresh uniform layout assumes the world scatters food uniformly, and where it does not
    — patches, a radial density gradient, half the spots standing empty — that null describes a
    different world and the comparison is worthless.  Rotating the real layout holds the item count,
    the clumping and the radial profile exactly, and destroys only the one thing under test: the
    alignment between where the food was and where this robot went.  Angle 0 is skipped, since that
    is the observed bout.
    """
    items = np.asarray(items, dtype=float).reshape(-1, 2)
    rng = np.random.default_rng(seed)
    angles = rng.permutation(np.linspace(0, 2 * np.pi, draws + 1)[1:-1])
    counts = []
    for th in angles:
        c, s = np.cos(th), np.sin(th)
        turned = items @ np.array([[c, -s], [s, c]]).T
        counts.append(replay(geoms, turned, eat_radius, regrow=regrow, rng=rng, radius=radius, clearance=clearance)[0])
    counts = np.array(counts, dtype=float)
    return NullResult(observed=float(observed), null_mean=float(counts.mean()), null_sd=float(counts.std(ddof=1)),
                      draws=len(counts), path=in_disc_path(geoms, radius))


def within_season_regrowth(food) -> bool:
    """Whether an eaten item can come back inside one bout, which decides the replay's eat rule.
    A delayed-regrowth world is depletion-only over a season."""
    return bool(food.regrow and getattr(food, "regrow_delay", 0) <= 0)


def gait_null(geoms: np.ndarray, observed: float, n_items: int, eat_radius: float, radius: float,
              draws: int = 200, regrow: bool = True, clearance: float = 0.0, seed: int = 0) -> NullResult:
    """Replay one recorded path against ``draws`` fresh layouts and compare with what it really ate."""
    rng = np.random.default_rng(seed)
    counts = []
    for _ in range(draws):
        layout = draw_layout(n_items, rng, radius, avoid=geoms[0], clearance=clearance)
        counts.append(replay(geoms, layout, eat_radius, regrow=regrow, rng=rng, radius=radius, clearance=clearance)[0])
    counts = np.array(counts, dtype=float)
    return NullResult(observed=float(observed), null_mean=float(counts.mean()), null_sd=float(counts.std(ddof=1)),
                      draws=draws, path=in_disc_path(geoms, radius))
