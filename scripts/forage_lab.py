"""Lab a foraging champion: wiring dump, per-unit lesions and foraging metrics on fresh draws.

The forage-shaped sibling of ``lab.py``.  ``lab.py`` answers "how well does this robot get to
the target and stay there", which is the wrong question for a forager: run it on a mower and
its progress, straightness, arrival and hold columns describe a task the robot was never in.
This keeps ``lab.py``'s shape -- phenotype dump, then one row per lesion mode averaged over N
fresh draws -- and swaps the columns for what a forager is actually doing: items eaten, how far
it travelled, how much of the season it spent inside the food disc, how far from the centre it
stayed, how many items it got per metre of in-disc path (the chance rate is 2 * eat_radius *
item density, so a mower meets it and a compass beats it), and the actuator work it paid.

Items eaten carries a standard error, because an eight-seed probe is what left the series'
champion claims uncertain in the first place (RBT-28).

usage: forage_lab.py RUN_DIR KIND GEN [N_DRAWS]   e.g. forage_lab.py runs/RBT-13/W1-801 holistic 390 12
"""
import json, sys, numpy as np
from dataclasses import replace
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


def trial(g, cfg, ph, gs, seed, mode):
    """One season alone in the arena under one lesion.  Incoming links are cut for a sensor
    (blanking what it reports); a neuron or effector is silenced both ways, as lab.py does."""
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
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
    steps = int(round(cfg.duration / cfg.control_dt))
    path = path_in = 0.0
    inside = 0
    dists = []
    last = sim.center_of_mass(0)[:2].copy()
    p0 = last.copy()
    for t in range(steps):
        sim.step()
        p = sim.center_of_mass(0)[:2]
        r = float(np.linalg.norm(p))
        dists.append(r)
        if r <= R:
            inside += 1
        if t % 10 == 0:
            d = float(np.linalg.norm(p - last))
            path += d
            if r <= R:
                path_in += d
            last = p.copy()
    return {
        "food": float(sim.food_eaten[0]),
        "disp": float(np.linalg.norm(sim.center_of_mass(0)[:2] - p0)),
        "path": path,
        "inside": inside / steps,
        "mean_r": float(np.mean(dists)),
        "path_in": path_in,
        "work": float(sim.work[0]) / 1000,
    }


def main(argv):
    run, kind, gen = argv[1], argv[2], int(argv[3])
    n = int(argv[4]) if len(argv) > 4 else 12
    g, cfg = load(run, kind, gen)
    ph = synthesize(g, cfg.synthesis)
    gs = groups(ph)
    f = cfg.food
    chance = 2 * f.eat_radius * f.items / (np.pi * f.radius ** 2)
    print(f"# {run} {kind} gen {gen}: {len(ph.parts)} parts, {len(ph.units)} units, {len(ph.links)} links")
    print(f"# world: {f.items} items in a {f.radius} m disc ({f.items / (np.pi * f.radius ** 2):.3f} items/m2), "
          f"eat radius {f.eat_radius} m, smell {getattr(f, 'smell', 'sum')} decay {f.decay} m, "
          f"{cfg.duration} s seasons, work cost {f.work_cost}/kJ; blind-mow chance rate {chance:.3f} items per metre")
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
    print(f"\n{'mode':12s} {'items':>13s} {'path':>6s} {'in-disc':>7s} {'mean_r':>6s} {'items/m_in':>10s} {'work':>5s}  unit")
    for m in modes:
        rs = [trial(g, cfg, ph, gs, s, m) for s in seeds]
        mean = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
        se = float(np.std([r["food"] for r in rs], ddof=1)) / np.sqrt(n) if n > 1 else 0.0
        rows[m] = (mean, se)
        who = ""
        if m.startswith("lesion:"):
            u = ph.units[int(m[7:])]
            who = f"part {u.part} {u.unit.kind} {unit_label(u)}"
            if u.unit.kind == "sensor" and u.unit.source in SMELL:
                who += "  <- SMELL"
        rate = mean["food"] / mean["path_in"] if mean["path_in"] > 1e-9 else float("nan")
        print(f"{m:12s} {mean['food']:6.2f} +- {se:4.2f} {mean['path']:6.1f} {mean['inside']:7.2f} "
              f"{mean['mean_r']:6.2f} {rate:10.3f} {mean['work']:5.1f}  {who}", flush=True)

    base, base_se = rows["intact"][0]["food"], rows["intact"][1]
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
