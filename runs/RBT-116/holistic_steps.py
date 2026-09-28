"""RBT-132 item 4: the holistic nose step, RBT-125 §B's harness run with G8(c) as the motif (RBT132.md §4).

    holistic_steps.py POINT CONFIG OUT --hosts HOSTS_ROOT [--workers W]    -> OUT/holistic-steps/steps.txt, steps.json
    holistic_steps.py call OUT      -> the cell's holistic PAYS, from OUT/holistic/pays.json and OUT/holistic-steps/steps.json

Authorised by the coordinator once #459's fix-check passed (#459 merged at 914667e), with the rung and step as ruled on
#459 (07:10, item 4): **both are totals, split evenly over the plant's n one-sided output links**.

**Hosts.**
- The first 8 holistic hosts in ``planters.host_pool``'s registered permutation that carry G8(c): two single-instance
  noses, one either side of the heading, and one-sided effectors. This is the same walk as ``planters.py pays``, so
  the two legs use the same hosts.
- Each host's G8(c) sign is tuned at a = 6 on the point's first 4 pool draws, as ``pays`` does. c6.8 keeps that sign
  and layout.

**Arms.** Per host, on §B's 128 paired start seeds (``steps.SEEDS``, 125000..125127), in the cell's world (the
point's committed ``sim`` block):

| arm | what | parity with §B |
|---|---|---|
| c0 | the host as it is | = §B's w0 |
| c6 | G8(c) at a total a = 6, over its n output links | = §B's w3 (a = 6 over the compass's 2 links) |
| c6.8 | the nose step: a total a = 6.8 (+0.8, as §B's +0.4 on each of 2 links) | = §B's w3.4 |
| speed@c0, speed@c6 | ``world.joint_damping / 1.25`` (``steps.SPEED``) | = §B's speed@w |

**Seasons.** Each is §B's ``bout`` exactly: a solo season with ``spawn_layout(1, cfg, seed)`` and
``set_food_seed(seed)``. It records items (``harvest.food``), net (``food_score``), and the CoM path speed.

**The reading.** §B's own ``steps.reading`` over hosts: nose step (c6.8 − c6) against speed step (speed@c6 − c6),
paired per host, both raw and per realised unit of speed.
- The per-unit speed step is ``step × 0.25 / (r − 1)``, with r = the path speed of speed@c6 ÷ that of c6. A host with
  r < ``steps.R_MIN`` (1.10) leaves the per-unit comparison.
- The per-unit reading governs R4. If more than half of the hosts leave it, the nose step is **NOT READABLE**, and
  holistic PAYS falls back to its F leg alone, labelled "information only; no speed comparison". That fallback is
  barred from any §8 statement that needs R4.
- **R4**: MET on NOSE LEADS or COMPARABLE; NOT MET on SPEED LEADS or TIED, UNRESOLVED.
- **The speed step's own payoff** (speed@c6 − c6), raw and per unit, is printed beside each reading (the coordinator's
  08:10 pre-data note).
- **The call** (:func:`call`): holistic PAYS at a cell = the F leg (``planters.py pays``: holistic F, the mean over
  hosts of each host's stage-2 F, with a one-sided t bound over hosts) > 0 **and** R4 MET. Where the nose step is
  NOT READABLE, it is the F leg alone, labelled as above. Both legs must be the same cell and hosts.

**Cost.** 8 hosts × 5 arms × 128 seeds = 5,120 seasons per cell.

Nothing runs on import. The tests use a test-only point, committed RBT-19 bodies and a few seeds.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import planters  # noqa: E402

steer = planters.steer
steps = planters._load("rbt125_steps", os.path.join(planters.ROOT, "runs", "RBT-125", "gate", "steps.py"))
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402

A_STEP = 0.8  #: the nose step, a total: §B's +0.4 on each of the compass's 2 links
ARMS = (("c0", 0.0, False), ("c6", planters.A_RUNG, False), ("c6.8", planters.A_RUNG + A_STEP, False),
        ("speed@c0", 0.0, True), ("speed@c6", planters.A_RUNG, True))
NOSE, SPEED_STEP, BASE = "c6.8", "speed@c6", "c6"
READS = {"NOSE LEADS": "MET", "COMPARABLE (equivalent within +-0.10)": "MET", "SPEED LEADS": "NOT MET",
         "TIED, UNRESOLVED": "NOT MET"}


def arm_genome(host: Genotype, layout: dict, sign: float, a: float) -> Genotype:
    """The arm's body: the host (a = 0), or the host with G8(c) at a total ``a`` over its n links."""
    return host if a == 0 else planters.plant_c(host, layout, sign, a)


def bout(task):
    """§B's ``steps.bout``, on a genome given as a dict: (key, seed, items, net, path speed)."""
    key, gd, cfg_d, seed, speed = task
    cfg = SimConfig.from_dict(cfg_d)
    if speed:
        cfg = replace(cfg, world=replace(cfg.world, joint_damping=cfg.world.joint_damping / steps.SPEED))
    sim = Simulation([Genotype.from_dict(gd)], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    path, last = 0.0, sim.center_of_mass(0)[:2].copy()
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        now = sim.center_of_mass(0)[:2]
        path += float(np.linalg.norm(now - last))
        last = now.copy()
    return key, seed, sim.harvest(0)["food"], sim.food_score(0), path / cfg.duration


def readout(M: dict) -> dict:
    """The §B reading from per-host arm means ``M[host][arm] = (items, net, speed)`` (means over the seeds)."""
    hosts = list(M)
    nose = {h: M[h][NOSE][0] - M[h][BASE][0] for h in hosts}
    speed = {h: M[h][SPEED_STEP][0] - M[h][BASE][0] for h in hosts}
    r = {h: M[h][SPEED_STEP][2] / max(M[h][BASE][2], 1e-9) for h in hosts}
    r0 = {h: M[h]["speed@c0"][2] / max(M[h]["c0"][2], 1e-9) for h in hosts}
    unit_hosts = [h for h in hosts if r[h] >= steps.R_MIN]
    raw = [nose[h] - speed[h] for h in hosts]
    unit = {h: speed[h] * 0.25 / (r[h] - 1.0) for h in unit_hosts}  #: the speed step rescaled to a realised +25%
    pu = [nose[h] - unit[h] for h in unit_hosts]
    readable = 2 * len(unit_hosts) >= len(hosts) and len(pu) > 1  # NOT READABLE when more than half leave
    per_unit = steps.reading(pu) if readable else "NOT READABLE"
    return {"n_hosts": len(hosts), "nose": nose, "speed": speed, "r": r, "r_c0": r0, "unit_hosts": len(unit_hosts),
            "raw": raw, "per_unit": pu, "speed_raw": [speed[h] for h in hosts], "speed_unit": list(unit.values()), "reading_raw": steps.reading(raw) if len(raw) > 1 else "NOT READABLE",
            "reading": per_unit, "R4": READS.get(per_unit, "NOT READABLE")}


def holistic_steps(point: str, config: str, out: str, hosts_root: str, workers: int = 1, seeds=None) -> int:
    seeds = list(steps.SEEDS if seeds is None else seeds)
    path = os.path.join(config, "config.json") if os.path.isdir(config) else config
    raw = json.load(open(path))
    cfg = SimConfig.from_dict(raw.get("sim", raw))
    steer.assert_world_point(cfg, point)
    steer.assert_registered_channel(cfg, point)
    steer.assert_fair_config(raw, point)
    steer.assert_point_world(raw, point)
    season = steer.point_season(point)
    tune_draws = steer.draw_pool(point)[:planters.N_TUNE]
    out = os.path.join(out, "holistic-steps")  # stages.py pays_jobs saves <out>/holistic-steps
    os.makedirs(out, exist_ok=True)
    log = open(os.path.join(out, "steps.txt"), "w")

    def say(*x):
        print(*x, file=log, flush=True)

    say(f"# RBT-132 holistic nose step at {point}: {path}; tau {cfg.food.smell_tau} (registered {steer.registered_tau(point)}); "
        f"{len(seeds)} paired seeds from {seeds[0]}; arms {', '.join(a for a, _, _ in ARMS)} (a totals, split over n links)")
    hosts, tried = [], 0
    for f in planters.host_pool(hosts_root, "holistic"):
        if len(hosts) == planters.N_HOSTS:
            break
        tried += 1
        g = Genotype.load(f)
        geom = planters.body_geometry(g, cfg, tune_draws[0])
        lay = planters.c_layout(g, geom) if geom is not None else None
        if lay is None:
            continue
        _, _, table = planters.tune([planters.plant_c(g, lay, s) for s in (+1.0, -1.0)], cfg, tune_draws, season)
        sign = +1.0 if table[0][1] >= table[1][1] else -1.0  # tune's argmax: ties go to the first (+1)
        n = len(planters.c_links(g, lay))
        hosts.append((f, g, lay, sign))
        say(f"host {f}: {n} output links (a 6 -> {6 / n:.3g} each, a 6.8 -> {6.8 / n:.3g} each), sign {sign:+g}")
    say(f"carrying share: {len(hosts)} of {tried} holistic hosts tried carry two single-instance noses")
    if len(hosts) < planters.N_HOSTS:
        say(f"REFUSED: {len(hosts)} hosts carry G8(c), {planters.N_HOSTS} needed")
        return 7
    cfg_d = cfg.to_dict()
    tasks = [((i, arm), arm_genome(g, lay, sign, a).to_dict(), cfg_d, s, sp)
             for i, (_, g, lay, sign) in enumerate(hosts) for arm, a, sp in ARMS for s in seeds]
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            rows = list(ex.map(bout, tasks, chunksize=8))
    else:
        rows = [bout(t) for t in tasks]
    got = {}
    for key, s, items, net, v in rows:
        got.setdefault(key, []).append((items, net, v))
    M = {i: {arm: tuple(float(x) for x in np.mean(got[(i, arm)], axis=0)) for arm, _, _ in ARMS} for i in range(len(hosts))}
    res = readout(M)
    say("\n| host | " + " | ".join(a for a, _, _ in ARMS) + " | r@c0 | r@c6 |")
    say("|---|" + "---|" * (len(ARMS) + 2))
    for i, (f, _, _, _) in enumerate(hosts):
        say(f"| {os.path.relpath(f, hosts_root)} | " + " | ".join(f"{M[i][a][0]:.3f}" for a, _, _ in ARMS)
            + f" | {res['r_c0'][i]:.3f} | {res['r'][i]:.3f} |")
    fmt = lambda x: "{:+.3f} [{:+.3f}, {:+.3f}]".format(*steps.t_int(x)) if len(x) > 1 else "--"
    say(f"\n## steps across {len(hosts)} hosts, per-host means over {len(seeds)} paired seeds; mean [t 95%]")
    say(f"installed a = 6 (c6 - c0): {fmt([M[i]['c6'][0] - M[i]['c0'][0] for i in M])}")
    say(f"nose step (c6 -> c6.8): {fmt(list(res['nose'].values()))}")
    say(f"speed step at c6 (raw): {fmt(list(res['speed'].values()))}; at c0 (raw): {fmt([M[i]['speed@c0'][0] - M[i]['c0'][0] for i in M])}")
    say(f"realised r at c6: {fmt(list(res['r'].values()))}; {res['unit_hosts']} of {len(hosts)} hosts at r >= {steps.R_MIN:.2f} "
        "enter the per-unit comparison")
    say(f"STEP {point} | nose step c6 -> c6.8 | vs raw speed@c6: {fmt(res['raw'])} {res['reading_raw']} "
        f"(speed step itself {fmt(res['speed_raw'])}) | vs per-unit speed (n {len(res['per_unit'])}): {fmt(res['per_unit'])} "
        f"{res['reading']} (speed step itself, per unit {fmt(res['speed_unit'])})")
    if res["reading"] == "NOT READABLE":
        say(f"R4 {point}: NOT READABLE (more than half the hosts leave the per-unit column): holistic PAYS here is the F leg alone, "
            "'information only; no speed comparison', barred from any §8 statement that needs R4")
    else:
        say(f"R4 {point}: {res['R4']} ({res['reading']}); holistic PAYS needs this and the F leg (planters.py pays)")
    with open(os.path.join(out, "steps.json"), "w") as fh:
        json.dump({"point": point, "seeds": seeds, "hosts": [f for f, _, _, _ in hosts], "signs": [s for _, _, _, s in hosts],
                   "carrying": f"{len(hosts)} of {tried}", "M": {str(i): M[i] for i in M},
                   **{k: v for k, v in res.items() if k not in ("nose", "speed", "r", "r_c0")},
                   "r": list(res["r"].values()), "r_c0": list(res["r_c0"].values())}, fh, indent=1)
    return 0


def call(out: str, point: str = "") -> str:
    """Holistic PAYS at one cell, from its two legs under ``out`` (``stage0/pays/<cell>``): the F leg
    (``holistic/pays.json``, ``planters.py pays``) and the nose step (``holistic-steps/steps.json``).
    - PAYS: the F leg's bound over hosts > 0 **and** R4 MET.
    - F LEG ONLY: the nose step is NOT READABLE; the F leg's verdict stands alone, labelled "information only; no speed
      comparison", barred from any §8 statement that needs R4.
    - DOES NOT PAY: otherwise (the F leg's bound ≤ 0, or R4 NOT MET)."""
    fl = json.load(open(os.path.join(out, "holistic", "pays.json")))
    st = json.load(open(os.path.join(out, "holistic-steps", "steps.json")))
    if fl["point"] != st["point"] or fl["hosts"] != st["hosts"]:
        raise ValueError(f"the two legs under {out} are not the same cell and hosts")
    f_ok = fl["lb"] > 0
    head = (f"HOLISTIC PAYS {fl['point']}: F {fl['mean']:+.3f} (bound over hosts {fl['lb']:+.3f}); nose step R4 {st['R4']} "
            f"({st['reading']}) -> ")
    if st["R4"] == "NOT READABLE":
        return head + (f"F LEG ONLY: {'pays' if f_ok else 'does not pay'} (information only; no speed comparison; "
                       "barred from any §8 statement that needs R4)")
    return head + ("PAYS" if f_ok and st["R4"] == "MET" else "DOES NOT PAY")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["call"]:  # holistic_steps.py call OUT: the cell's holistic PAYS from its two legs
        print(call(argv[1]))
        return 0
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("point")
    ap.add_argument("config", help="the point's config.json, or a directory holding one")
    ap.add_argument("out")
    ap.add_argument("--hosts", required=True, help="HOSTS_ROOT: ckpt/rbt-113-O1 restored (O1/<seed>/U/<kind>/final)")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    return holistic_steps(a.point, a.config, a.out, a.hosts, a.workers)


if __name__ == "__main__":
    sys.exit(main())
