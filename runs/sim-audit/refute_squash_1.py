"""Refutation probe for H4 ("the squash flattens the field and destroys the gradient").

Two independent lines of attack on the CAUSAL claim.

PART A (analytic, my own implementation, validated against Simulation._intensity):
  A1  Does the squash destroy DIRECTION?  Sign/argmax agreement between the squashed
      field's differential and the raw sum's differential.  A monotone map cannot
      reorder, so if agreement is 1.000 the squash removes exactly zero directional bits.
  A2  ALTERNATIVE EXPLANATION: geometry, not the squash.  Sweep nose separation for the
      RAW (unsquashed) sum.  If contrast is ~linear in track/decay and the raw field at the
      real 0.3872 m track is already only ~0.15 of DC, then the small contrast is a
      property of sampling a 1.0 m exponential with a 0.39 m baseline, and the squash is
      one factor of ~2 on top of a number that was already tiny.
  A3  Is the squash INVERTIBLE / is its cost recoverable by machinery the brain already
      has?  RuntimeBrain carries a per-unit bias (brain.py: self.bias[i] = u.bias).  Compare
      the tanh steering ceiling for squash+bias vs raw+no-bias vs raw+bias vs nearest+no-bias.
      If squash+bias >= raw+no-bias, then "remove the squash" is worth LESS than a knob the
      brain already has, which is not what a major defect looks like.

PART B (decisive, in the live sim):  monkeypatch Simulation._intensity to drop the squash
  entirely (raw sum, same decay, same sources), install the hand-built crossed compass at
  three magnitudes, and measure items eaten.  7 evolved Pioneers x 64 PAIRED seeds.
  Robot is the unit of analysis; bootstrap over the 7 robots.
  If the compass still earns nothing with the squash GONE, H4's causal claim fails: the
  squash is not what prevented the mechanism from working.

No library files are modified; the patch is applied inside worker processes only.
"""

from __future__ import annotations

import json
import time
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "runs/RBT-23/W4b-801"
GENS = (90, 190, 290, 390, 490, 550, 590)
SEED0 = 9000
NSEEDS = 64
TRACK = 0.3872      # measured wheel-nose separation, metres
DECAY = 1.0
NITEM = 12
FRAD = 3.0
EAT = 0.35

_CFG = None


def cfg():
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


# ---------------------------------------------------------------- PART A ----

def field(pts, src, mode):
    """pts (N,2), src (M,2) -> (N,) field value.  'squash' is exactly the library's sum mode."""
    d = np.linalg.norm(pts[:, None, :] - src[None, :, :], axis=2)
    e = np.exp(-d / DECAY)
    if mode == "raw":
        return e.sum(axis=1)
    if mode == "squash":
        s = e.sum(axis=1)
        return s / (1.0 + s)
    if mode == "nearest":
        return e.max(axis=1)
    raise ValueError(mode)


def layout(rng, n=NITEM):
    r = FRAD * np.sqrt(rng.random(n))
    a = rng.uniform(0, 2 * np.pi, n)
    return np.stack([r * np.cos(a), r * np.sin(a)], axis=1)


def validate_against_library():
    """My `squash` must equal Simulation._intensity exactly."""
    c = cfg()
    g = Genotype.load(f"{RUN}/conventional/best_gen0590.json")
    sim = Simulation([g], replace(c, random_start=True), spawns=spawn_layout(1, c, 9000))
    sim.set_food_seed(9000)
    rng = np.random.default_rng(0)
    err = 0.0
    for _ in range(200):
        p = np.array([rng.uniform(-4, 4), rng.uniform(-4, 4), 0.05])
        mine = float(field(p[None, :2], sim.food_pos, "squash")[0])
        err = max(err, abs(mine - sim._intensity(p, sim.food_pos)))
    return err


def part_a():
    rng = np.random.default_rng(7)
    out = {}

    # ---- A1: does a monotone squash destroy direction? ----
    agree_sign = 0
    n_tot = 0
    rel = {"squash": [], "raw": [], "nearest": []}
    dc = {"squash": [], "raw": [], "nearest": []}
    for _ in range(400):
        src = layout(rng)
        cen = np.stack([rng.uniform(-FRAD, FRAD, 250), rng.uniform(-FRAD, FRAD, 250)], axis=1)
        th = rng.uniform(0, 2 * np.pi, len(cen))
        off = 0.5 * TRACK * np.stack([np.cos(th), np.sin(th)], axis=1)
        L, R = cen + off, cen - off
        d_ = {}
        for m in rel:
            a, b = field(L, src, m), field(R, src, m)
            d_[m] = a - b
            rel[m].append(np.abs(a - b) / np.maximum(field(cen, src, m), 1e-12))
            dc[m].append(field(cen, src, m))
        agree_sign += int(np.sum(np.sign(d_["squash"]) == np.sign(d_["raw"])))
        n_tot += len(cen)
    out["A1_sign_agreement_squash_vs_raw"] = agree_sign / n_tot
    out["A1_rel_contrast"] = {m: float(np.mean(np.concatenate(v))) for m, v in rel.items()}
    out["A1_DC"] = {m: float(np.mean(np.concatenate(v))) for m, v in dc.items()}
    out["A1_n_samples"] = n_tot

    # ---- A2: geometry sweep -- raw (squash-free) contrast vs nose separation ----
    tracks = [0.0968, 0.1936, 0.3872, 0.7744, 1.5488]
    geo = []
    for t in tracks:
        acc = {"raw": [], "squash": []}
        for _ in range(120):
            src = layout(rng)
            cen = np.stack([rng.uniform(-FRAD, FRAD, 250), rng.uniform(-FRAD, FRAD, 250)], axis=1)
            th = rng.uniform(0, 2 * np.pi, len(cen))
            off = 0.5 * t * np.stack([np.cos(th), np.sin(th)], axis=1)
            for m in acc:
                a, b = field(cen + off, src, m), field(cen - off, src, m)
                acc[m].append(np.abs(a - b) / np.maximum(field(cen, src, m), 1e-12))
        geo.append({"track": t, "track_over_decay": t / DECAY,
                    "rel_raw": float(np.mean(np.concatenate(acc["raw"]))),
                    "rel_squash": float(np.mean(np.concatenate(acc["squash"])))})
    out["A2_geometry_sweep"] = geo

    # ---- A3: tanh steering ceiling, with and without a bias the brain already has ----
    def ceiling(mode, with_bias, live=NITEM):
        vals_L, vals_R = [], []
        r2 = np.random.default_rng(11)
        for _ in range(160):
            src = layout(r2, live)
            cen = np.stack([r2.uniform(-FRAD, FRAD, 120), r2.uniform(-FRAD, FRAD, 120)], axis=1)
            th = r2.uniform(0, 2 * np.pi, len(cen))
            off = 0.5 * TRACK * np.stack([np.cos(th), np.sin(th)], axis=1)
            vals_L.append(field(cen + off, src, mode))
            vals_R.append(field(cen - off, src, mode))
        L, R = np.concatenate(vals_L), np.concatenate(vals_R)
        ws = np.geomspace(0.05, 200.0, 90)
        best = {"w": 0.0, "b": 0.0, "steer": 0.0, "common": 0.0}
        mu = 0.5 * (L.mean() + R.mean())
        for w in ws:
            blist = [0.0] if not with_bias else (-w * mu + np.linspace(-3.0, 3.0, 61))
            for b in np.atleast_1d(blist):
                s = float(np.mean(np.abs(np.tanh(w * L + b) - np.tanh(w * R + b))))
                if s > best["steer"]:
                    com = float(np.mean(0.5 * (np.tanh(w * L + b) + np.tanh(w * R + b))))
                    best = {"w": float(w), "b": float(b), "steer": s, "common": com}
        return best

    out["A3_tanh_ceiling"] = {
        "squash_nobias": ceiling("squash", False),
        "squash_bias": ceiling("squash", True),
        "raw_nobias": ceiling("raw", False),
        "raw_bias": ceiling("raw", True),
        "nearest_nobias": ceiling("nearest", False),
    }
    return out


# ---------------------------------------------------------------- PART B ----

def _patch(mode):
    """Replace Simulation._intensity with a squash-free (or nearest-source) version."""
    def _i(self, point, sources):
        if len(sources) == 0:
            return 0.0
        d = np.linalg.norm(sources - point[:2], axis=1)
        e = np.exp(-d / (self.config.food.decay if self.config.food is not None else 1.0))
        if mode == "raw":
            return float(e.sum())
        if mode == "nearest":
            return float(e.max())
        s = float(e.sum())
        return s / (1.0 + s)
    Simulation._intensity = _i


def wiring(gen):
    ph = synthesize(Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json"), cfg().synthesis)
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
    return nose, eff


CONDS = [
    ("base",      "squash", None, 0.0),
    ("base_raw",  "raw",    None, 0.0),
    ("X_raw_0.4", "raw",    "crossed",   0.4),
    ("X_raw_0.8", "raw",    "crossed",   0.8),
    ("X_raw_1.6", "raw",    "crossed",   1.6),
    ("U_raw_0.8", "raw",    "uncrossed", 0.8),
]


def bout(task):
    gen, seed, ci = task
    name, mode, fam, m = CONDS[ci]
    _patch(mode)
    c = replace(cfg(), random_start=True)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    nose, eff = wiring(gen)
    W = sim.brains[0].W
    if fam == "crossed":
        W[eff[2], nose[1]] += m
        W[eff[1], nose[2]] += m
    elif fam == "uncrossed":
        W[eff[1], nose[1]] += m
        W[eff[2], nose[2]] += m
    disc = c.food.radius
    steps = int(round(c.duration / c.control_dt))
    last = sim.center_of_mass(0)[:2].copy()
    in_path = 0.0
    for _ in range(steps):
        sim.step()
        p = sim.center_of_mass(0)[:2]
        if float(np.linalg.norm(p)) <= disc:
            in_path += float(np.linalg.norm(p - last))
        last = p.copy()
    return {"gen": gen, "seed": seed, "cond": name,
            "food": float(sim.food_eaten[0]), "in_path": in_path,
            "exploded": bool(sim.exploded[0])}


def boot(v, draws=20000, seed=3):
    rng = np.random.default_rng(seed)
    v = np.asarray(v, float)
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(draws)])
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((m <= 0).mean())


# --- Stage C: the audit's own top-recommended fix, a nearest-source sensor.  This removes
# --- BOTH halves of "squash-over-a-sum" at once (no squash, no summing of 12 items).  w=1.6 is
# --- the steering-optimal magnitude for that mode from A3 (best_w 1.73).
CONDS_C = [
    ("base_near",  "nearest", None, 0.0),
    ("X_near_1.6", "nearest", "crossed",   1.6),
    ("U_near_1.6", "nearest", "uncrossed", 1.6),
]


def bout_c(task):
    gen, seed, ci = task
    global CONDS
    CONDS = CONDS_C
    return bout((gen, seed, ci))


def stage_c():
    seeds = [SEED0 + i for i in range(NSEEDS)]
    tasks = [(g, s, i) for g in GENS for s in seeds for i in range(len(CONDS_C))]
    print(f"\nSTAGE C: {len(GENS)} robots x {len(seeds)} paired seeds x {len(CONDS_C)} conditions = {len(tasks)} bouts", flush=True)
    t0 = time.time()
    with Pool(4) as p:
        rows = p.map(bout_c, tasks, chunksize=16)
    print(f"STAGE C done in {time.time()-t0:.0f}s", flush=True)
    by = {(r["gen"], r["seed"], r["cond"]): r for r in rows}
    out = {"rows": rows, "table": {}}
    print("\n| condition | mean items | d vs base_near | 95% CI | P(d<=0) |")
    for name, mode, fam, m in CONDS_C:
        absv, d = [], []
        for g in GENS:
            absv.append(np.mean([by[(g, s, name)]["food"] for s in seeds]))
            d.append(np.mean([by[(g, s, name)]["food"] - by[(g, s, "base_near")]["food"] for s in seeds]))
        mu, lo, hi, p0 = boot(d) if any(abs(x) > 0 for x in d) else (0.0, 0.0, 0.0, 1.0)
        out["table"][name] = {"mean_items": float(np.mean(absv)), "d_vs_base_near": float(np.mean(d)),
                              "ci": [lo, hi], "p_le0": p0, "per_robot_d": [float(x) for x in d]}
        print(f"| {name} | {np.mean(absv):.3f} | {np.mean(d):+.3f} | [{lo:+.3f}, {hi:+.3f}] | {p0:.3f} |")
    cu = [np.mean([by[(g, s, "X_near_1.6")]["food"] - by[(g, s, "U_near_1.6")]["food"] for s in seeds]) for g in GENS]
    mu, lo, hi, p0 = boot(cu)
    out["crossed_minus_uncrossed_nearest"] = {"mean": mu, "ci": [lo, hi], "per_robot": [float(x) for x in cu]}
    print(f"\ncrossed - uncrossed at w=1.6 with a NEAREST-SOURCE sensor: {mu:+.3f} items  CI [{lo:+.3f}, {hi:+.3f}]")
    return out


if __name__ == "__main__":
    import sys
    if "--stage-c" in sys.argv:
        res = json.load(open("runs/sim-audit/refute_squash_1.json"))
        res["C_nearest"] = stage_c()
        json.dump(res, open("runs/sim-audit/refute_squash_1.json", "w"), indent=1)
        print("\nupdated runs/sim-audit/refute_squash_1.json")
        raise SystemExit
    res = {}
    res["A0_max_abs_error_vs_library"] = validate_against_library()
    print(f"A0 validation max|err| vs Simulation._intensity: {res['A0_max_abs_error_vs_library']:.3e}", flush=True)

    t0 = time.time()
    res.update(part_a())
    print(f"PART A done in {time.time()-t0:.0f}s", flush=True)
    print("A1 sign agreement squash vs raw:", res["A1_sign_agreement_squash_vs_raw"])
    print("A1 rel contrast:", res["A1_rel_contrast"])
    print("A2 geometry sweep:")
    for r in res["A2_geometry_sweep"]:
        print(f"   track {r['track']:.4f}  raw {r['rel_raw']:.4f}  squash {r['rel_squash']:.4f}")
    print("A3 tanh ceilings:")
    for k, v in res["A3_tanh_ceiling"].items():
        print(f"   {k:16s} steer {v['steer']:.4f}  common {v['common']:+.3f}  w {v['w']:.2f} b {v['b']:+.2f}")

    seeds = [SEED0 + i for i in range(NSEEDS)]
    tasks = [(g, s, i) for g in GENS for s in seeds for i in range(len(CONDS))]
    print(f"\nPART B: {len(GENS)} robots x {len(seeds)} paired seeds x {len(CONDS)} conditions = {len(tasks)} bouts", flush=True)
    t0 = time.time()
    with Pool(4) as p:
        rows = p.map(bout, tasks, chunksize=16)
    print(f"PART B done in {time.time()-t0:.0f}s", flush=True)

    by = {(r["gen"], r["seed"], r["cond"]): r for r in rows}
    res["B_rows"] = rows
    tab = {}
    print("\n| condition | mean items | d vs base | d vs base_raw | 95% CI (vs own ref) | P(d<=0) |")
    print("|---|---|---|---|---|---|")
    for name, mode, fam, m in CONDS:
        per_robot_abs, d_base, d_raw = [], [], []
        for g in GENS:
            per_robot_abs.append(np.mean([by[(g, s, name)]["food"] for s in seeds]))
            d_base.append(np.mean([by[(g, s, name)]["food"] - by[(g, s, "base")]["food"] for s in seeds]))
            d_raw.append(np.mean([by[(g, s, name)]["food"] - by[(g, s, "base_raw")]["food"] for s in seeds]))
        ref = d_base if mode == "squash" or name == "base_raw" else d_raw
        mu, lo, hi, p0 = boot(ref) if any(abs(x) > 0 for x in ref) else (0.0, 0.0, 0.0, 1.0)
        tab[name] = {"mean_items": float(np.mean(per_robot_abs)),
                     "per_robot_items": [float(x) for x in per_robot_abs],
                     "d_vs_base": float(np.mean(d_base)), "d_vs_base_raw": float(np.mean(d_raw)),
                     "ci": [lo, hi], "p_le0": p0,
                     "per_robot_d_ref": [float(x) for x in ref]}
        print(f"| {name} | {np.mean(per_robot_abs):.3f} | {np.mean(d_base):+.3f} | {np.mean(d_raw):+.3f} | [{lo:+.3f}, {hi:+.3f}] | {p0:.3f} |")
    res["B_table"] = tab

    # crossed vs uncrossed under the squash-free sensor
    cu = []
    for g in GENS:
        cu.append(np.mean([by[(g, s, "X_raw_0.8")]["food"] - by[(g, s, "U_raw_0.8")]["food"] for s in seeds]))
    mu, lo, hi, p0 = boot(cu)
    res["B_crossed_minus_uncrossed_raw"] = {"mean": mu, "ci": [lo, hi], "per_robot": [float(x) for x in cu]}
    print(f"\ncrossed - uncrossed at w=0.8 WITH THE SQUASH REMOVED: {mu:+.3f} items  CI [{lo:+.3f}, {hi:+.3f}]")

    json.dump(res, open("runs/sim-audit/refute_squash_1.json", "w"), indent=1)
    print("\nwrote runs/sim-audit/refute_squash_1.json")
