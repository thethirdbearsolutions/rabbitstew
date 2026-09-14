"""Lab a foraging champion: wiring dump, per-unit lesions and foraging metrics on fresh draws.

The forage-shaped sibling of ``lab.py``.  ``lab.py`` answers "how well does this robot get to
the target and stay there", which is the wrong question for a forager: run it on a mower and
its progress, straightness, arrival and hold columns describe a task the robot was never in.
This keeps ``lab.py``'s shape -- phenotype dump, then one row per lesion mode averaged over N
fresh draws -- and swaps the columns for what a forager is actually doing: items eaten, how far
it travelled, how much of the season it spent inside the food disc, how far from the centre it
stayed, how many items it got per metre of in-disc path, and the actuator work it paid.

Items eaten carries a standard error, because an eight-seed probe is what left the series'
champion claims uncertain in the first place (RBT-28).

**The items-per-metre column is read against each mode's own trajectory-preserving null, not
against ``2 * eat_radius * item_density``** (RBT-39).  That closed form is a *point* robot's rate on
a fresh straight line and it bounds the real expectation in neither direction: body width raises it
1.54x to 2.87x on the measured champions while circling and retracing lower it 0.39x to 1.08x, so
the honest null lands anywhere from 0.70x to 1.67x the formula.  Holding the path length fixed is
not sufficient either -- at pinned length and zero steering, shape alone moves the rate by 2.07x.
So each mode's recorded path is replayed against layouts the world could equally have dealt it
(:mod:`rabbitstew.forage_null`), and the column answers "did this robot beat what its own gait meets
by accident".  A mower sits on its null; only a compass is above it.

usage: forage_lab.py RUN_DIR KIND GEN [N_DRAWS]   e.g. forage_lab.py runs/RBT-13/W1-801 holistic 390 12
"""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.forage_null import (in_disc_path, replay_many, swept_width, within_season_regrowth,
                                    world_layouts, world_spot_fn)
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

SMELL = ("food", "agent")


def load(run, kind, gen):
    """The champion and the world it evolved in, with random starts on so the draws differ."""
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    if cfg.food is None:
        raise SystemExit(f"{run} is not a foraging run (no food config); use scripts/lab.py instead")
    return Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json"), replace(cfg, random_start=True)


def unit_label(u):
    k = u.unit.kind
    return getattr(u.unit, "label", None) or (u.unit.func if k == "neuron" else f"effector dof{u.unit.dof}")


def groups(ph):
    """The unit index sets each whole-subsystem lesion blanks."""
    us = ph.units
    return {
        "global": [i for i, u in enumerate(us) if u.part is None],
        "env": [i for i, u in enumerate(us) if u.unit.kind == "sensor" and u.unit.source != "oscillator"],
        "smell": [i for i, u in enumerate(us) if u.unit.kind == "sensor" and u.unit.source in SMELL],
        "osc": [i for i, u in enumerate(us) if u.unit.kind == "sensor" and u.unit.source == "oscillator"],
        "local": [i for i, u in enumerate(us) if u.part is not None and u.unit.kind != "effector"],
    }


def trial(g, cfg, ph, gs, seed, mode, draws=0):
    """One season alone in the arena under one lesion.  Incoming links are cut for a sensor
    (blanking what it reports); a neuron or effector is silenced both ways, as lab.py does.

    With ``draws`` above zero the bout is recorded frame by frame and its own path is replayed
    against ``draws`` layouts the world could equally have dealt it, so the mode's items-per-metre
    can be read against what its gait meets by accident (RBT-39) rather than against a point robot.
    """
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    layouts = None
    if draws:
        # Drawn at the spawn, before anything moves, so the clearance rule sees the real start
        # positions; re-seeding restores the bout's own layout bit for bit.
        real = sim.food_pos.copy()
        layouts = world_layouts(sim, [800000 + 997 * seed + d for d in range(draws)])
        sim.set_food_seed(seed)
        assert np.array_equal(sim.food_pos, real), "re-seeding did not restore the bout's layout"
    b = sim.brains[0]

    def silence(i):
        b.W[i, :] = 0
        b.W[:, i] = 0
        b.bias[i] = 0

    if mode in ("no_env", "no_smell", "no_osc"):
        for i in gs[{"no_env": "env", "no_smell": "smell", "no_osc": "osc"}[mode]]:
            b.W[:, i] = 0
    elif mode in ("no_global", "no_local"):
        for i in gs[mode[3:]]:
            silence(i)
    elif mode.startswith("lesion:"):
        silence(int(mode[7:]))  # as lab.py does: for a sensor this is just its outgoing column

    R = cfg.food.radius
    if draws:
        sim.start_recording(every=1)
    steps = int(round(cfg.duration / cfg.control_dt))
    path = path_in = 0.0
    inside = 0
    dists = []
    last = sim.center_of_mass(0)[:2].copy()
    p0 = last.copy()
    # Every tick, not every tenth: sampling the path coarsely understates it and so *overstates*
    # items per metre, by 1.17x on the widest body measured (RBT-39's interim on the per-cell rule).
    for t in range(steps):
        sim.step()
        p = sim.center_of_mass(0)[:2]
        r = float(np.linalg.norm(p))
        dists.append(r)
        if r <= R:
            inside += 1
        d = float(np.linalg.norm(p - last))
        path += d
        if r <= R:
            path_in += d
        last = p.copy()
    out = {
        "food": float(sim.food_eaten[0]),
        "disp": float(np.linalg.norm(sim.center_of_mass(0)[:2] - p0)),
        "path": path,
        "inside": inside / steps,
        "mean_r": float(np.mean(dists)),
        "path_in": path_in,
        "work": float(sim.work[0]) / 1000,
        "null": float("nan"),
        "swept": float("nan"),
    }
    if draws:
        # Frame 0 is the spawn, recorded before any step and never tested for eating, so the replay
        # starts at frame 1 (RBT-39).
        geoms = sim.trajectory.as_array()[:, :, :2]
        counts = replay_many(geoms[1:], layouts, cfg.food.eat_radius,
                             regrow=within_season_regrowth(cfg.food), spot_fn=world_spot_fn(sim))
        out["null"] = float(counts.mean())
        out["swept"] = swept_width(geoms, cfg.food.eat_radius)
        out["com_path_in"] = in_disc_path(geoms, R)
    return out


def main(argv):
    run, kind, gen = argv[1], argv[2], int(argv[3])
    n = int(argv[4]) if len(argv) > 4 else 12
    draws = int(argv[5]) if len(argv) > 5 else 120
    g, cfg = load(run, kind, gen)
    ph = synthesize(g, cfg.synthesis)
    gs = groups(ph)
    f = cfg.food
    chance = 2 * f.eat_radius * f.items / (np.pi * f.radius ** 2)  # reported, but not a null
    print(f"# {run} {kind} gen {gen}: {len(ph.parts)} parts, {len(ph.units)} units, {len(ph.links)} links")
    print(f"# world: {f.items} items in a {f.radius} m disc ({f.items / (np.pi * f.radius ** 2):.3f} items/m2), "
          f"eat radius {f.eat_radius} m, smell {getattr(f, 'smell', 'sum')} decay {f.decay} m, "
          f"{cfg.duration} s seasons, work cost {f.work_cost}/kJ")
    print(f"# items/m_in is read against each mode's OWN trajectory null over {draws} world-dealt layouts "
          f"(RBT-39).  The point-robot rate 2*eat*density = {chance:.3f} items/m is printed for reference\n"
          f"# only: it bounds the null in neither direction and no verdict here uses it.")
    for p in ph.parts:
        print(f"part {p.index}: {p.shape.name.lower()} dims={tuple(round(float(x), 3) for x in p.dims)} "
              f"joint={p.joint_type.name} parent={p.parent} mass={p.mass:.2f}")
    linked = set()
    for s, d, _ in ph.links:
        linked.add(s)
        linked.add(d)
    for i, u in enumerate(ph.units):
        bias = f" bias={getattr(u.unit, 'bias', 0.0):+.2f}" if u.unit.kind != "sensor" else ""
        smell = "  <- SMELL" if u.unit.kind == "sensor" and u.unit.source in SMELL else ""
        print(f"unit {i:3d} part {str(u.part):4s} {u.unit.kind:8s} {unit_label(u):16s}{bias}"
              f"{'' if i in linked else '   (unlinked)'}{smell}")
    print("links:")
    for s, d, w in ph.links:
        print(f"  {s:3d} -> {d:3d} : {w:+.2f}")

    modes = ["intact", "no_env", "no_smell", "no_osc", "no_global", "no_local"] + [f"lesion:{i}" for i in sorted(linked)]
    seeds = list(range(8000, 8000 + n))
    rows = {}
    print(f"\n{'mode':12s} {'items':>13s} {'null':>6s} {'path':>6s} {'in-disc':>7s} {'mean_r':>6s} "
          f"{'items/m_in':>10s} {'null/m':>7s} {'t':>6s} {'work':>5s}  unit")
    for m in modes:
        rs = [trial(g, cfg, ph, gs, s, m, draws=draws) for s in seeds]
        mean = {k: float(np.nanmean([r.get(k, float("nan")) for r in rs])) for k in rs[0]}
        se = float(np.std([r["food"] for r in rs], ddof=1)) / np.sqrt(n) if n > 1 else 0.0
        # Paired over draws, each bout against its own null: the verdict statistic (RBT-39).
        d = np.array([r["food"] - r["null"] for r in rs], dtype=float)
        t = float(d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))) if len(d) > 1 and d.std(ddof=1) > 0 else float("nan")
        rows[m] = (mean, se, t, np.array([r["food"] for r in rs], dtype=float))
        who = ""
        if m.startswith("lesion:"):
            u = ph.units[int(m[7:])]
            who = f"part {u.part} {u.unit.kind} {unit_label(u)}"
            if u.unit.kind == "sensor" and u.unit.source in SMELL:
                who += "  <- SMELL"
        rate = mean["food"] / mean["path_in"] if mean["path_in"] > 1e-9 else float("nan")
        nrate = mean["null"] / mean["path_in"] if mean["path_in"] > 1e-9 else float("nan")
        print(f"{m:12s} {mean['food']:6.2f} +- {se:4.2f} {mean['null']:6.2f} {mean['path']:6.1f} {mean['inside']:7.2f} "
              f"{mean['mean_r']:6.2f} {rate:10.3f} {nrate:7.3f} {t:+6.2f} {mean['work']:5.1f}  {who}", flush=True)

    base, base_se = rows["intact"][0]["food"], rows["intact"][1]
    i0, it = rows["intact"][0], rows["intact"][2]
    # What effect size this n can resolve at all (RBT-28's adversary).  A lesion table read at an n
    # too small to reject anything is a design that cannot fail, which is worse than a wrong number
    # because it looks like a measurement.  The per-draw sd of the paired intact-minus-lesion
    # difference is estimated over the lesion modes actually run.
    BAR = 2.5
    sds = []
    for m, v in rows.items():
        if m == "intact":
            continue
        diff = rows["intact"][3] - v[3]
        # A lesion that is a provable no-op (an unlinked sensor) has zero variance by construction
        # and says nothing about resolving power, so it is not part of the estimate.
        if len(diff) > 1 and np.isfinite(diff).all() and diff.std(ddof=1) > 0:
            sds.append(float(diff.std(ddof=1)))
    intact_sd = float(rows["intact"][3].std(ddof=1)) if n > 1 else float("nan")
    # Fall back to the intact spread scaled for a paired difference of two equal-variance arms,
    # so a champion whose every lesion is a no-op still reports the n it would need.
    sd = float(np.median(sds)) if sds else intact_sd * np.sqrt(2)
    resolvable = BAR * sd / np.sqrt(n) if np.isfinite(sd) else float("nan")
    quarter = 0.25 * base
    need = int(np.ceil((BAR * sd / quarter) ** 2)) if np.isfinite(sd) and quarter > 0 else 0
    print(f"\npower at n = {n} draws: |t| >= {BAR} resolves a lesion difference of "
          f"{resolvable:+.2f} items or larger (median per-draw sd of the paired difference {sd:.2f}).")
    print(f"  resolving 25% of intact ({quarter:.2f} items) needs about {need} draws. "
          f"{'THIS n CANNOT TEST a 25% effect.' if need > n else 'This n can test a 25% effect.'}"
          + ("" if sds else "  (no lesion varied; sd taken from the intact spread)"))
    verdict = ("ABOVE its own gait" if it >= 2.5 else "BELOW its own gait" if it <= -2.5
               else "INDISTINGUISHABLE from its own gait")
    print(f"\nintact against its own gait: {i0['food']:.2f} items vs a null of {i0['null']:.2f}, "
          f"paired t = {it:+.2f} over {n} draws  ->  {verdict}")
    print(f"  swept corridor {i0['swept']:.2f} m against the point-robot rate's assumed "
          f"{2 * f.eat_radius:.2f} m; point-robot rate {chance:.3f} items/m, reference only")
    work = rows["intact"][0]["work"]
    per_kj = base / work if work > 1e-9 else float("nan")
    print(f"\nintact: {base:.2f} +- {base_se:.2f} items on {work:.2f} kJ = {per_kj:.2f} items per kJ over {n} draws")
    costs = sorted(((base - v[0]["food"], m) for m, v in rows.items() if m.startswith("lesion:")), reverse=True)
    for cost, m in costs[:5]:
        u = ph.units[int(m[7:])]
        share = cost / base * 100 if base else float("nan")
        print(f"  {m:12s} costs {cost:+.2f} items ({share:+.0f}%)  part {u.part} {u.unit.kind} {unit_label(u)}")
    whole = [(base - rows[m][0]["food"], m) for m in ("no_env", "no_smell", "no_osc", "no_global", "no_local")]
    print("  whole-subsystem: " + ", ".join(f"{m} {c:+.2f}" for c, m in whole))
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    sys.exit(main(sys.argv))
