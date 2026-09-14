"""RBT-67: bound the compass prize -- the dose-response past a = 64, per population.

Every sweep of the hand-installed antisymmetric compass stopped at steering gain a = 64
while still rising (+0.054, +0.246, +0.897 items at a = 16, 32, 64 on the W4b-801 bests).
This widens the ladder to a in {96, 128, 192, 256, 384} on both committed populations,
with the chemotactic sign set per population from its measured direction of travel
(RBT-69, standing rule (a)):

* ``w4b``  -- the seven ``docs/artifacts/RBT-23-W4b-801`` bests, gens 90..590.  They drive
              BACKWARD (pooled -174.1 deg), so the published motif sign IS their compass.
* ``p801`` -- the seven ``runs/RBT-19/P-801`` bests, gens 0..590.  They drive FORWARD
              (pooled +5.1 deg), so the OPPOSITE sign is their compass.  Two of the seven
              (g100, g400) drive backward per generation (PR #11) and are expected to be
              anti-compassed by the population-level sign; the per-robot rows show it.

The four weights are never typed out.  Installation goes through the merged RBT-69
harness, ``scripts/compass_replication.py::install``, which derives them from
``rabbitstew.fixed.drive_commands(steering=k, throttle=0)``.  On this body's antiparallel
drive axes the effector SUM is the steering axis, each link carries ``k``, and the pair
delivers ``2k (n_left - n_right)`` to it, so the steering coefficient is ``a = 2k``
(``runs/RBT-45/calibration.json``: installed w = 8, 16, 32 read back as a = 16, 32, 64).
The ladder is stated in ``a``; ``k = a / 2`` is what gets installed, and every cell reports
the REALISED ``a`` read back from the runtime weight matrix by the signed path sum of
``runs/RBT-45/motif.py::steering_gain`` (depth 4), never the installed ``w``.

a = 32 and a = 64 are run as calibration anchors (rule II: show the instrument registering
the known effect before reading past it).  Seeds start at 7000 (the RBT-69 origin); the
source figure used 9000..9063, so the a = 64 anchor on w4b is a replication on fresh seeds,
not a byte-for-byte reproduction.

Per cell (population x a): items eaten, the paired change against each robot's own
baseline on the same seeds, a 95% CI from a bootstrap over the SEVEN ROBOTS (never over
bouts: lineages cluster, RBT-45 s6.5), robots improved, the full per-seed difference list
per robot, the count of zero differences and of zero-item bouts, path length inside the
food disc and items per in-disc metre (steering against coverage), whole turns of yaw, the
fraction of control ticks with BOTH drive effectors pinned at the same sign (the
pre-registered turnover mechanism: a saturated steering term zeroes the throttle), and the
realised a and the gradient-dominance ratio |a| / |c|.

Usage (from the repository root, ~10 min per population on four cores):

    python docs/artifacts/RBT-67/compass_dose_response.py [n_seeds=64] [workers=4] [w4b|p801|both]

Writes docs/artifacts/RBT-67/<pop>.txt (the readout) and <pop>.json (every cell, every
per-seed difference, every readback).  No library code is touched.
"""

import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np

import compass_replication as cr  # the merged RBT-69 harness: install() goes through drive_commands()
from rabbitstew.brain import RuntimeBrain
from rabbitstew.fixed import drive_commands, drive_effector_units
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

OUT = os.path.join("docs", "artifacts", "RBT-67")

POPULATIONS = {
    "w4b": {
        "run": "docs/artifacts/RBT-23-W4b-801",
        "gens": (90, 190, 290, 390, 490, 550, 590),
        "drives": "BACKWARD",
        "sign": +1.0,  # the published motif sign is this population's compass
        "travel": "pooled -174.1 deg, R=0.756, all seven backward (docs/artifacts/RBT-23-W4b-801/travel_direction.txt)",
    },
    "p801": {
        "run": "runs/RBT-19/P-801",
        "gens": (0, 100, 200, 300, 400, 500, 590),
        "drives": "FORWARD",
        "sign": -1.0,  # the opposite sign is this population's compass
        "travel": "pooled forward (RBT-69); per generation g100 and g400 drive BACKWARD (PR #11), so the population sign anti-compasses those two",
    },
}
LADDER_A = (32.0, 64.0, 96.0, 128.0, 192.0, 256.0, 384.0)  #: steering coefficient a; 32 and 64 are the calibration anchors
SEED0 = 7000
DEPTH = 4  #: motif.py's path-sum depth
BOOT = 20000
RAIL = 0.99


def config(pop: str) -> SimConfig:
    """The population's own committed config, solo random-start bouts."""
    cfg = SimConfig.from_dict(json.load(open(f"{POPULATIONS[pop]['run']}/config.json"))["sim"])
    return replace(cfg, random_start=True)


def genotype(pop: str, gen: int) -> Genotype:
    return Genotype.load(f"{POPULATIONS[pop]['run']}/conventional/best_gen{gen:04d}.json")


def k_of(a: float) -> float:
    """Installed per-link gain for a steering coefficient a: a = 2k on this body."""
    return a / 2.0


# --------------------------------------------------------------------------- #
# Readback: the realised steering coefficient, motif.py's quantity
# --------------------------------------------------------------------------- #


def steering_terms(W: np.ndarray, n_left: int, n_right: int, effs: list, depth: int) -> tuple:
    """Signed path-sum coefficients ``(a, c)`` of ``n_left - n_right`` and ``n_left + n_right``
    on the steering axis (the effector sum), summing every path of up to ``depth`` links.

    Exactly ``runs/RBT-45/motif.py::steering_gain`` with the noses and effectors located by
    side rather than by Node index.  A linearisation: tanh only attenuates, so this is an
    upper bound on what the routes through the evolved brain deliver."""
    n = W.shape[0]
    s = {}
    for side, nose in (("left", n_left), ("right", n_right)):
        v = np.zeros(n)
        v[nose] = 1.0
        tot = np.zeros(n)
        for _ in range(depth):
            v = W @ v
            tot += v
            if not v.any():
                break
        s[side] = float(tot[effs].sum())
    return (s["left"] - s["right"]) / 2.0, (s["left"] + s["right"]) / 2.0


def readback(pop: str, gen: int, a: float) -> dict:
    """Install the motif on a fresh runtime brain and read the steering coefficient back.

    Round-trips the installation (rule III): the depth-1 change in ``a`` must be exactly the
    population-signed ``a`` asked for and the depth-1 change in ``c`` exactly zero, or the
    four weights did not land where ``drive_commands`` says they should."""
    P = POPULATIONS[pop]
    cfg = config(pop)
    ph = synthesize(genotype(pop, gen), cfg.synthesis)
    n_left, n_right = cr.food_noses(ph)
    left_e, right_e = drive_effector_units(ph)
    effs = list(left_e) + list(right_e)
    brain = RuntimeBrain(ph)
    pre1 = steering_terms(brain.W, n_left, n_right, effs, 1)
    pre4 = steering_terms(brain.W, n_left, n_right, effs, DEPTH)
    cr.install(brain, ph, "compass", P["sign"] * k_of(a))
    post1 = steering_terms(brain.W, n_left, n_right, effs, 1)
    post4 = steering_terms(brain.W, n_left, n_right, effs, DEPTH)
    want = P["sign"] * a
    assert abs((post1[0] - pre1[0]) - want) < 1e-9, (pop, gen, a, post1, pre1)
    assert abs(post1[1] - pre1[1]) < 1e-9, (pop, gen, a, post1, pre1)
    a4, c4 = post4
    return {"gen": gen, "a_installed": want, "a_evolved": pre4[0], "c_evolved": pre4[1],
            "a_realised": a4, "c_realised": c4,
            "dominance": abs(a4) / abs(c4) if abs(c4) > 1e-12 else float("inf"),
            "a_direct": post1[0], "c_direct": post1[1]}


def nose_gradient(pop: str, n_seeds: int = 8) -> str:
    """Dynamic range of a wheel nose and the left-right gap it offers on this substrate.

    RBT-69's check, per population: a compass steers on the difference between the two
    noses, so the ladder is only about the circuit if that difference is not saturated
    away.  Also the scale that turns ``a`` into a pre-tanh steering command: a x gap."""
    P = POPULATIONS[pop]
    cfg = config(pop)
    g = genotype(pop, P["gens"][-1])
    ph = synthesize(g, cfg.synthesis)
    n_left, n_right = cr.food_noses(ph)
    level, gap = [], []
    for s in range(n_seeds):
        sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, SEED0 + s))
        sim.set_food_seed(SEED0 + s)
        for _ in range(int(round(cfg.duration / cfg.control_dt))):
            sim.step()
            act = sim.brains[0].activation
            level.append(float(act[n_left]))
            gap.append(abs(float(act[n_left] - act[n_right])))
    level, gap = np.array(level), np.array(gap)
    return (f"nose gradient ({cfg.food.items} items, smell={cfg.food.smell}, decay={cfg.food.decay}, "
            f"patches={cfg.food.patches}, regrow={cfg.food.regrow}): level {level.min():.3f}-{level.max():.3f}, "
            f"left-right gap median {np.median(gap):.4f} p95 {np.percentile(gap, 95):.4f} "
            f"(a x median gap: " + ", ".join(f"a={a:g}:{a * np.median(gap):.2f}" for a in LADDER_A) + ")")


# --------------------------------------------------------------------------- #
# One bout
# --------------------------------------------------------------------------- #


def bout(args) -> dict:
    pop, gen, a, seed = args
    P = POPULATIONS[pop]
    cfg = config(pop)
    g = genotype(pop, gen)
    ph = synthesize(g, cfg.synthesis)
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    brain = sim.brains[0]
    cr.install(brain, ph, "compass", P["sign"] * k_of(a))  # a = 0 installs nothing: the baseline
    left_e, right_e = drive_effector_units(ph)
    idx = sim.robots[0]
    disc = cfg.food.radius
    p0 = sim.center_of_mass(0)[:2].copy()
    last = p0.copy()
    yaw_last = cr._yaw(sim.data.xquat[idx.root_body])
    steps = int(round(cfg.duration / cfg.control_dt))
    turned = path = in_path = 0.0
    in_ticks = rail = 0
    for _ in range(steps):
        sim.step()
        p = sim.center_of_mass(0)[:2]
        d = float(np.linalg.norm(p - last))
        path += d
        if float(np.linalg.norm(p)) <= disc:
            in_path += d
            in_ticks += 1
        last = p.copy()
        yaw = cr._yaw(sim.data.xquat[idx.root_body])
        turned += abs((yaw - yaw_last + math.pi) % (2 * math.pi) - math.pi)
        yaw_last = yaw
        act = brain.activation
        left = float(np.clip(act[left_e].sum(), -1.0, 1.0))
        right = float(np.clip(act[right_e].sum(), -1.0, 1.0))
        if abs(left) > RAIL and abs(right) > RAIL and (left > 0) == (right > 0):
            rail += 1  # both wheels pinned with the same sign: pure steering, zero throttle
    return {"pop": pop, "gen": gen, "a": a, "seed": seed,
            "food": float(sim.food_eaten[0]),
            "path": path, "in_path": in_path, "in_disc": in_ticks / steps,
            "moved": float(np.linalg.norm(last - p0)),
            "turned": turned / (2 * math.pi),
            "both_rail": rail / steps,
            "exploded": bool(sim.exploded[0])}


# --------------------------------------------------------------------------- #
# Analysis
# --------------------------------------------------------------------------- #


def boot_mean(per_robot: list, rng: np.random.Generator) -> tuple:
    v = np.asarray(per_robot, float)
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(BOOT)])
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def analyse(pop: str, rows: list, seeds: list, reads: dict) -> tuple:
    P = POPULATIONS[pop]
    gens = P["gens"]
    by = {(r["gen"], r["a"], r["seed"]): r for r in rows}
    rng = np.random.default_rng(5)
    mean = lambda key, gen, a: float(np.mean([by[(gen, a, s)][key] for s in seeds]))
    cells = []
    for a in (0.0,) + LADDER_A:
        robots = []
        for gen in gens:
            R = [by[(gen, a, s)] for s in seeds]
            B = [by[(gen, 0.0, s)] for s in seeds]
            diffs = [r["food"] - b["food"] for r, b in zip(R, B)]
            items, in_path = mean("food", gen, a), mean("in_path", gen, a)
            rb = reads[(gen, a)] if a else None
            robots.append({"gen": gen, "items": items, "delta": float(np.mean(diffs)), "diffs": diffs,
                           "zero_diff": int(sum(d == 0 for d in diffs)),
                           "zero_items": int(sum(r["food"] == 0 for r in R)),
                           "in_path": in_path, "path": mean("path", gen, a), "moved": mean("moved", gen, a),
                           "in_disc": mean("in_disc", gen, a), "turned": mean("turned", gen, a),
                           "both_rail": mean("both_rail", gen, a),
                           "items_per_m": items / in_path if in_path > 0.05 else float("nan"),
                           "exploded": int(sum(r["exploded"] for r in R)),
                           "a_realised": rb["a_realised"] if rb else None,
                           "c_realised": rb["c_realised"] if rb else None,
                           "dominance": rb["dominance"] if rb else None})
        deltas = [r["delta"] for r in robots]
        d_mean, lo, hi = boot_mean(deltas, rng)
        pooled = [d for r in robots for d in r["diffs"]]
        cells.append({"a": a, "k": k_of(a), "items": float(np.mean([r["items"] for r in robots])),
                      "delta": d_mean, "ci": [lo, hi],
                      "se_seed": float(np.std(pooled, ddof=1) / math.sqrt(len(pooled))),
                      "improved": int(sum(d > 0 for d in deltas)),
                      "zero_diff": int(sum(r["zero_diff"] for r in robots)),
                      "zero_items": int(sum(r["zero_items"] for r in robots)),
                      "items_per_m": float(np.nanmean([r["items_per_m"] for r in robots])),
                      "in_path": float(np.mean([r["in_path"] for r in robots])),
                      "path": float(np.mean([r["path"] for r in robots])),
                      "moved": float(np.mean([r["moved"] for r in robots])),
                      "in_disc": float(np.mean([r["in_disc"] for r in robots])),
                      "turned": float(np.mean([r["turned"] for r in robots])),
                      "both_rail": float(np.mean([r["both_rail"] for r in robots])),
                      "exploded": int(sum(r["exploded"] for r in robots)),
                      "a_realised_median": float(np.median([r["a_realised"] for r in robots])) if a else 0.0,
                      "a_realised": [r["a_realised"] for r in robots] if a else [],
                      "dominance_median": float(np.median([r["dominance"] for r in robots])) if a else float("nan"),
                      "robots": robots})
    # turnover: the best rung, and whether the top of the ladder is credibly below it
    ladder = [c for c in cells if c["a"] > 0]
    peak = max(ladder, key=lambda c: c["delta"])
    top = ladder[-1]
    turnover = {"peak_a": peak["a"], "peak_delta": peak["delta"], "top_a": top["a"], "top_delta": top["delta"]}
    if peak is not top:
        drop = [pr["delta"] - tr["delta"] for pr, tr in zip(peak["robots"], top["robots"])]
        turnover["drop_peak_minus_top"] = boot_mean(drop, rng)
        after = []
        for c in ladder[ladder.index(peak) + 1:]:
            d = [pr["delta"] - cr_["delta"] for pr, cr_ in zip(peak["robots"], c["robots"])]
            after.append({"a": c["a"], "peak_minus_this": boot_mean(d, rng)})
        turnover["after_peak"] = after
    return cells, turnover


def readout(pop: str, cells: list, turnover: dict, reads: dict, n_seeds: int, n_bouts: int, nose: str) -> str:
    P = POPULATIONS[pop]
    gens = P["gens"]
    L = []
    L.append(f"RBT-67: the compass dose-response past a = 64 -- population {pop} ({P['run']})")
    L.append(f"bests {list(gens)}, {n_seeds} paired seeds from {SEED0}, {n_bouts} bouts, ladder a = {[int(a) for a in LADDER_A]}")
    L.append(f"direction of travel: {P['drives']} -- {P['travel']}")
    L.append(f"sign: population sign {P['sign']:+.0f} x published motif; installed k = a/2 on each of the four links via drive_commands()")
    L.append(nose)
    base = cells[0]
    L.append("")
    L.append("baseline items per robot: " + "  ".join(f"g{r['gen']}:{r['items']:.3f}" for r in base["robots"]))
    L.append(f"pooled baseline {base['items']:.3f} items, in-disc path {base['in_path']:.2f} m, "
             f"{base['items_per_m']:.3f} items/m, {base['turned']:.2f} turns, both-rail {100 * base['both_rail']:.1f}%")
    L.append("")
    L.append(f"{'a':>5s} {'k':>5s} | {'a real':>7s} {'min..max':>17s} {'off':>3s} {'|a|/|c|':>8s} | {'items':>6s} {'delta':>7s} {'95% CI (robots)':>17s} {'se/bout':>7s} {'better':>6s} | "
             f"{'zero d':>6s} {'zero i':>6s} | {'in-disc m':>9s} {'items/m':>8s} {'path m':>6s} {'turns':>5s} {'rail%':>5s} {'expl':>4s}")
    for c in cells[1:]:
        want = P["sign"] * c["a"]
        off = sum(abs(x - want) > 0.2 * abs(want) for x in c["a_realised"])  # robots whose depth-4 readback is off by > 20%
        L.append(f"{c['a']:5.0f} {c['k']:5.0f} | {c['a_realised_median']:+7.1f} [{min(c['a_realised']):+7.1f}, {max(c['a_realised']):+7.1f}] {off:3d} {c['dominance_median']:8.1f} | "
                 f"{c['items']:6.3f} {c['delta']:+7.3f} [{c['ci'][0]:+6.3f}, {c['ci'][1]:+6.3f}] {c['se_seed']:7.3f} "
                 f"{c['improved']:>3d}/{len(gens)} | {c['zero_diff']:6d} {c['zero_items']:6d} | "
                 f"{c['in_path']:9.2f} {c['items_per_m']:8.3f} {c['path']:6.2f} {c['turned']:5.2f} {100 * c['both_rail']:5.1f} {c['exploded']:4d}")
    L.append("")
    L.append("a real: median over robots of the realised steering coefficient read back from the runtime weights")
    L.append("(signed path sum to depth 4, motif.py's quantity; the sign is the published motif's frame, so it is")
    L.append("negative on a forward-driving population by construction), with the min..max over robots and the")
    L.append("count of robots whose readback is off the installed value by more than 20%.  The depth-4 sum is a")
    L.append("truncation of a series that does not converge on these brains (spectral radius > 1 on all fourteen,")
    L.append("RBT-67 adversary): where it differs from the installed value it is the readback failing, not the")
    L.append("install; the depth-1 term is exact and is asserted on every robot.  |a|/|c|: gradient over common")
    L.append("mode, same readback.  delta: paired change in items against the robot's own baseline on the same seeds, mean")
    L.append("over the 7 robots, CI bootstrapped over robots (20000 draws); se/bout is the naive per-bout standard")
    L.append("error for comparison only.  zero d: paired differences that are exactly 0; zero i: bouts with no items.")
    L.append("in-disc m: path length while the centre of mass is inside the food disc; items/m: items per in-disc")
    L.append("metre (mean over robots of each robot's ratio).  rail%: control ticks with both drive effectors pinned")
    L.append("beyond |0.99| with the same sign -- pure steering, zero throttle.  expl: bouts that exploded.")
    L.append("")
    L.append("per robot: realised a | evolved a before install | delta per rung")
    L.append("  gen | " + " | ".join(f"a={c['a']:.0f}" for c in cells[1:]))
    for i, gen in enumerate(gens):
        L.append(f"  g{gen:<4d}| " + " | ".join(
            f"{c['robots'][i]['a_realised']:+6.1f} ({reads[(gen, c['a'])]['a_evolved']:+5.2f}) {c['robots'][i]['delta']:+6.3f}" for c in cells[1:]))
    L.append("")
    L.append("per-seed paired differences (items, motif minus baseline, seeds in order), zero differences / zero-item bouts:")
    for c in cells[1:]:
        for r in c["robots"]:
            L.append(f"  a={c['a']:.0f} g{r['gen']}: " + " ".join(f"{int(d):+d}" for d in r["diffs"]) +
                     f"   | zero d {r['zero_diff']}/{len(r['diffs'])}, zero i {r['zero_items']}")
    L.append("")
    t = turnover
    if t["peak_a"] == t["top_a"]:
        L.append(f"TURNOVER: none inside the range tested.  The best rung is the top of the ladder, a = {t['top_a']:.0f} "
                 f"({t['top_delta']:+.3f}); the curve has not turned over by a = {t['top_a']:.0f}.")
    else:
        m, lo, hi = t["drop_peak_minus_top"]
        cred = "credible" if lo > 0 else "NOT credible (CI spans zero)"
        L.append(f"TURNOVER: peak at a = {t['peak_a']:.0f} ({t['peak_delta']:+.3f}); the top rung a = {t['top_a']:.0f} "
                 f"sits {m:+.3f} [{lo:+.3f}, {hi:+.3f}] below it, paired over robots -> decline {cred}.")
        for e in t["after_peak"]:
            mm, l2, h2 = e["peak_minus_this"]
            L.append(f"   a = {e['a']:.0f}: peak minus this rung {mm:+.3f} [{l2:+.3f}, {h2:+.3f}]")
    return "\n".join(L)


# --------------------------------------------------------------------------- #


def run(pop: str, n_seeds: int, workers: int) -> None:
    P = POPULATIONS[pop]
    seeds = [SEED0 + s for s in range(n_seeds)]
    jobs = [(pop, g, a, s) for g in P["gens"] for a in (0.0,) + LADDER_A for s in seeds]
    reads = {(g, a): readback(pop, g, a) for g in P["gens"] for a in LADDER_A}  # asserts the install round-trips
    nose = nose_gradient(pop)
    with ProcessPoolExecutor(workers) as pool:
        rows = list(pool.map(bout, jobs, chunksize=8))
    cells, turnover = analyse(pop, rows, seeds, reads)
    text = readout(pop, cells, turnover, reads, n_seeds, len(jobs), nose)
    print(text)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{pop}.txt"), "w") as f:
        f.write(text + "\n")
    with open(os.path.join(OUT, f"{pop}.json"), "w") as f:
        json.dump({"population": pop, "run": P["run"], "gens": list(P["gens"]), "drives": P["drives"], "sign": P["sign"],
                   "seed0": SEED0, "n_seeds": n_seeds, "ladder_a": list(LADDER_A), "depth": DEPTH, "nose": nose,
                   "readback": [reads[(g, a)] for g in P["gens"] for a in LADDER_A],
                   "cells": cells, "turnover": turnover}, f, indent=1)


def rerender(pop: str) -> None:
    """Re-print <pop>.txt from <pop>.json without re-running anything (the readout columns changed
    after the run, on the adversary's note that the median hid the per-robot spread)."""
    J = json.load(open(os.path.join(OUT, f"{pop}.json")))
    reads = {(r["gen"], abs(r["a_installed"])): r for r in J["readback"]}
    n_bouts = len(J["gens"]) * (1 + len(J["ladder_a"])) * J["n_seeds"]
    text = readout(pop, J["cells"], J["turnover"], reads, J["n_seeds"], n_bouts, J["nose"])
    print(text)
    with open(os.path.join(OUT, f"{pop}.txt"), "w") as f:
        f.write(text + "\n")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--rerender":
        for pop in sys.argv[2:] or ("w4b", "p801"):
            rerender(pop)
        return
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    which = sys.argv[3] if len(sys.argv) > 3 else "both"
    assert drive_commands(1.0, 0.0) == (1.0, 1.0), "steering must land on both wheels with the same sign"
    for pop in (("w4b", "p801") if which == "both" else (which,)):
        run(pop, n_seeds, workers)
        print("\n" + "=" * 100 + "\n")


if __name__ == "__main__":
    main()
