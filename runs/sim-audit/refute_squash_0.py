"""REFUTATION CHECK for H4 ("the squash flattens the food field into an 'am I in the disc' scalar").

Lens: is the MEASUREMENT sound?  probe_squash.py is a purely analytic probe.  It never runs the
simulator.  Every headline number is computed over a SYNTHETIC occupancy -- robot positions drawn
uniform in a 3.5 m disc, food drawn uniform in the 3.0 m disc, 12 live items -- and the only
anchor to reality is a single bout on a single robot (DC 0.3283, |dI|/DC 0.1215).

This script re-measures the same quantities where they actually apply: at the nose positions the
Pioneer's noses actually occupy, over 7 evolved robots x 32 paired seeds, unmodified robots.
Every smell mode/decay is evaluated at the SAME sampled points, so the mode comparison is exactly
paired by construction; intervals bootstrap over the 7 robots (RBT-45 6.5).

Sections
  1  real occupancy vs the probe's assumed occupancy (distance to nearest live item, live count)
  2  field statistics at real occupancy: DC, track differential, squash tax, mode comparison
  3  the "am I in the disc" test (E) redone at real occupancy
  4  directionality (F) redone at real occupancy
  5  the tanh ceiling (H/I) redone with the REAL wheel pre-activation instead of a zero baseline
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, "/home/user/rabbitstew")

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout

RUN = "runs/RBT-23/W4b-801"
GENS = (90, 190, 290, 390, 490, 550, 590)      # the spike's 7 robots
SEEDS = [9000 + s for s in range(32)]           # 32 paired seeds
DECAY = 1.0
NITEMS = 12                                     # the sim's divisor for mean/log: len(food_pos)
BOOT = 4000
RNG = np.random.default_rng(7)

BASE = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
CFG = replace(BASE, random_start=True)
STEPS = int(round(CFG.duration / CFG.control_dt))
out: dict = {}


def modes(S: np.ndarray) -> dict[str, np.ndarray]:
    """Every smell mode from the same raw pile S -- exactly _intensity's algebra."""
    return {"sum": S / (1.0 + S),
            "mean": (S / NITEMS) / (1.0 + S / NITEMS),
            "log": np.clip(np.log1p(S) / np.log1p(NITEMS), 0.0, 1.0),
            "raw": S}


def bout(gen: int, seed: int) -> dict:
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = Simulation([g], CFG, spawns=spawn_layout(1, CFG, seed))
    sim.set_food_seed(seed)
    idx = sim.robots[0]
    br = sim.brains[0]
    gm = [idx.geoms[p] for p in (0, 1, 2)]                 # chassis nose, wheel nose 1, wheel nose 2
    eL, eR = br.effectors[(1, 0)], br.effectors[(2, 0)]    # the two drive-wheel effector units
    rec = {k: [] for k in ("S1", "S2", "Sc", "sep", "d1", "lat", "rad", "live", "xL", "xR", "dnear1", "dnear2")}
    for _ in range(STEPS):
        # pre-activation the wheel effectors are about to see (brain.step: x = W a + b, then tanh)
        x = br.W @ br.activation + br.bias
        rec["xL"].append(float(x[eL].sum()))
        rec["xR"].append(float(x[eR].sum()))
        sim.step()
        d = sim.data
        p1 = d.geom_xpos[gm[1]][:2].copy()
        p2 = d.geom_xpos[gm[2]][:2].copy()
        pc = d.geom_xpos[gm[0]][:2].copy()
        src = sim.food_pos                                   # parked items sit at 1e6 -> contribute 0
        for tag, p in (("1", p1), ("2", p2), ("c", pc)):
            rec["S" + tag].append(float(np.exp(-np.linalg.norm(src - p, axis=1) / DECAY).sum()))
        mid = 0.5 * (p1 + p2)
        rec["sep"].append(float(np.linalg.norm(p1 - p2)))
        rec["rad"].append(float(np.linalg.norm(mid)))
        live = src[sim.food_alive]
        rec["live"].append(int(sim.food_alive.sum()))
        if len(live):
            dl = np.linalg.norm(live - mid, axis=1)
            j = int(dl.argmin())
            rec["d1"].append(float(dl[j]))
            perp = (p1 - p2) / max(np.linalg.norm(p1 - p2), 1e-12)   # unit vector nose2 -> nose1
            to = live[j] - mid
            rec["lat"].append(float((to / max(np.linalg.norm(to), 1e-12)) @ perp))
            rec["dnear1"].append(float(np.linalg.norm(live - p1, axis=1).min()))
            rec["dnear2"].append(float(np.linalg.norm(live - p2, axis=1).min()))
        else:
            for k in ("d1", "lat", "dnear1", "dnear2"):
                rec[k].append(np.nan)
    return {k: np.asarray(v, dtype=float) for k, v in rec.items()}


print(f"{len(GENS)} robots x {len(SEEDS)} paired seeds x {STEPS} control steps = "
      f"{len(GENS) * len(SEEDS)} bouts, {len(GENS) * len(SEEDS) * STEPS} nose samples", flush=True)
per_robot: dict[int, dict[str, np.ndarray]] = {}
for gen in GENS:
    parts = [bout(gen, s) for s in SEEDS]
    per_robot[gen] = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    print(f"  gen {gen}: {len(per_robot[gen]['S1'])} samples, mean live {np.nanmean(per_robot[gen]['live']):.2f}", flush=True)


def boot_ci(vals: list[float]) -> tuple[float, float, float]:
    v = np.asarray(vals, float)
    d = np.array([RNG.choice(v, len(v), replace=True).mean() for _ in range(BOOT)])
    return float(v.mean()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def per_robot_stat(fn) -> tuple[float, float, float, list[float]]:
    vals = [float(fn(per_robot[g])) for g in GENS]
    m, lo, hi = boot_ci(vals)
    return m, lo, hi, vals


# ============================================================ 1: is the assumed occupancy right? =
print("\n[1] REAL OCCUPANCY vs the occupancy probe_squash assumed")
m, lo, hi, v = per_robot_stat(lambda r: np.nanmean(r["d1"]))
print(f"    distance to nearest LIVE item, real bouts : {m:.3f} m  [{lo:.3f}, {hi:.3f}] over {len(GENS)} robots")
print(f"                                    per robot : {', '.join(f'{x:.2f}' for x in v)}")
mL, loL, hiL, _ = per_robot_stat(lambda r: np.nanmean(r["live"]))
print(f"    live items during the bout                : {mL:.2f}  [{loL:.2f}, {hiL:.2f}]  (probe section I assumed 4)")
ms, _, _, _ = per_robot_stat(lambda r: np.nanmean(r["sep"]))
print(f"    measured nose separation                  : {ms:.4f} m (probe assumed TRACK = 0.3872)")
mr, _, _, _ = per_robot_stat(lambda r: np.nanmean(r["rad"]))
print(f"    distance of body midpoint from the origin : {mr:.3f} m")
out["1_occupancy"] = dict(d1=m, d1_lo=lo, d1_hi=hi, d1_per_robot=v, live=mL, sep=ms, radius=mr)

# the probe's own synthetic occupancy, regenerated for a like-for-like comparison
rg = np.random.default_rng(20260913)
lr = 3.0 * np.sqrt(rg.random((400, NITEMS))); la = rg.uniform(0, 2 * np.pi, (400, NITEMS))
lays = np.stack([lr * np.cos(la), lr * np.sin(la)], axis=-1)
pr = 3.5 * np.sqrt(rg.random(400 * 250)); pa = rg.uniform(0, 2 * np.pi, 400 * 250)
pts = np.stack([pr * np.cos(pa), pr * np.sin(pa)], axis=-1).reshape(400, 250, 2)
syn_d1 = np.concatenate([np.linalg.norm(pts[i][:, None, :] - lays[i][None], axis=2).min(axis=1) for i in range(400)])
print(f"    probe_squash's synthetic occupancy        : mean nearest-item distance {syn_d1.mean():.3f} m")
print(f"    -> the probe places the robot {m / syn_d1.mean():.2f}x FURTHER... no: real/synthetic = {m / syn_d1.mean():.2f}")
out["1_synthetic_d1"] = float(syn_d1.mean())

# =================================================== 2: field statistics at the real operating pt =
print("\n[2] FIELD AT REAL NOSE POSITIONS (all modes evaluated at identical points -> exactly paired)")
print("    mode      DC        mean|dI|    |dI|/DC   [bootstrap CI over robots]")
rows = []
for mode in ("sum", "mean", "log", "raw"):
    def dc(r, mode=mode):
        return modes(r["Sc"])[mode].mean()

    def rel(r, mode=mode):
        M = modes(r["Sc"])[mode]
        a, b = modes(r["S1"])[mode], modes(r["S2"])[mode]
        return (np.abs(a - b) / np.maximum(M, 1e-12)).mean()

    def absd(r, mode=mode):
        return np.abs(modes(r["S1"])[mode] - modes(r["S2"])[mode]).mean()

    d_, _, _, _ = per_robot_stat(dc)
    a_, _, _, _ = per_robot_stat(absd)
    r_, rlo, rhi, rv = per_robot_stat(rel)
    rows.append(dict(mode=mode, DC=d_, absd=a_, rel=r_, lo=rlo, hi=rhi, per_robot=rv))
    print(f"    {mode:8s} {d_:8.4f}  {a_:9.5f}   {r_:7.4f}   [{rlo:.4f}, {rhi:.4f}]")
# 'nearest' needs live-only distances
nm, _, _, _ = per_robot_stat(lambda r: np.nanmean(np.exp(-0.5 * (r["dnear1"] + r["dnear2"]))))
nr, nlo, nhi, _ = per_robot_stat(lambda r: np.nanmean(
    np.abs(np.exp(-r["dnear1"]) - np.exp(-r["dnear2"])) / np.maximum(np.exp(-0.5 * (r["dnear1"] + r["dnear2"])), 1e-12)))
print(f"    {'nearest*':8s} {nm:8.4f}  {'':9s}   {nr:7.4f}   [{nlo:.4f}, {nhi:.4f}]   (* not a sim mode)")
rows.append(dict(mode="nearest", DC=nm, rel=nr, lo=nlo, hi=nhi))
out["2_field"] = rows
sq = [r for r in rows if r["mode"] == "sum"][0]
rw = [r for r in rows if r["mode"] == "raw"][0]
mn = [r for r in rows if r["mode"] == "mean"][0]
tax, tlo, thi, _ = per_robot_stat(lambda r: (np.abs(modes(r["S1"])["raw"] - modes(r["S2"])["raw"]) / np.maximum(r["Sc"], 1e-12)).mean()
                                  / (np.abs(modes(r["S1"])["sum"] - modes(r["S2"])["sum"]) / np.maximum(modes(r["Sc"])["sum"], 1e-12)).mean())
print(f"\n    SQUASH TAX at the real operating point (raw rel / squashed rel) = {tax:.3f}x  [{tlo:.3f}, {thi:.3f}]")
print(f"    probe_squash headline (synthetic, 12 live) = 0.1549/0.0750 = 2.07x")
print(f"    MEAN-mode gain over sum at the real point  = {mn['rel'] / sq['rel']:.3f}x  (probe claimed 1.88x)")
out["2_squash_tax"] = dict(tax=tax, lo=tlo, hi=thi, mean_gain=mn["rel"] / sq["rel"])

# ================================================== 3: "am I in the disc" test at real occupancy ==
print("\n[3] THE 'AM I IN THE DISC' CLAUSE, at real occupancy (probe section E, synthetic: R^2 0.450, CV 0.139)")
e_rows = []
for mode in ("sum", "mean", "raw"):
    def r2(r, mode=mode):
        v = modes(r["Sc"])[mode]
        b = np.clip((r["rad"] / 3.5 * 20).astype(int), 0, 19)
        prof = np.array([v[b == k].mean() if (b == k).sum() else 0.0 for k in range(20)])
        return 1.0 - (v - prof[b]).var() / v.var()

    def cv(r, mode=mode):
        v = modes(r["Sc"])[mode][r["rad"] < 2.5]
        return v.std() / max(v.mean(), 1e-12)

    a, alo, ahi, _ = per_robot_stat(r2)
    c, clo, chi, _ = per_robot_stat(cv)
    e_rows.append(dict(mode=mode, r2=a, r2_lo=alo, r2_hi=ahi, cv=c, cv_lo=clo, cv_hi=chi))
    print(f"    {mode:5s}: R^2 of a pure radial profile {a:.3f} [{alo:.3f}, {ahi:.3f}] | "
          f"CV inside 2.5 m {c:.3f} [{clo:.3f}, {chi:.3f}]")
out["3_radial"] = e_rows

# ================================================================ 4: directionality, real points ==
print("\n[4] DIRECTIONALITY at real nose positions (probe section F, synthetic: sign-acc 0.789)")


def sign_acc(r, mode="sum", near=None):
    a, b = modes(r["S1"])[mode], modes(r["S2"])[mode]
    ok = np.isfinite(r["lat"])
    if near is not None:
        ok &= r["d1"] < near
    s = np.sign(a[ok] - b[ok]) * np.sign(r["lat"][ok])
    return (s > 0).mean()


for lab, near in (("all samples", None), ("nearest item < 1 m", 1.0), ("nearest item < 0.5 m", 0.5)):
    m_, lo_, hi_, v_ = per_robot_stat(lambda r, n=near: sign_acc(r, "sum", n))
    print(f"    higher nose is on the nearest item's side, {lab:20s}: {m_:.3f} [{lo_:.3f}, {hi_:.3f}]")
    out.setdefault("4_sign", {})[lab] = dict(mean=m_, lo=lo_, hi=hi_, per_robot=v_)
same, _, _, _ = per_robot_stat(lambda r: float(np.mean(np.sign(modes(r["S1"])["sum"] - modes(r["S2"])["sum"])
                                                        == np.sign(r["S1"] - r["S2"]))))
print(f"    squashed and raw track differentials agree in sign: {same:.6f}  (a monotone map cannot flip a sign)")
out["4_sign_identity"] = same

# ======================================= 5: tanh authority with the REAL wheel pre-activation =====
print("\n[5] THE tanh CEILING, redone LIKE-FOR-LIKE with the real wheel drive")
print("    probe section H models the wheel command as tanh(w*I) -- baseline ZERO.  In the spike the")
print("    crossed link is ADDED to a running mower, so the command is tanh(x_gait + w*I).")
xl, _, _, _ = per_robot_stat(lambda r: r["xL"].mean())
xr, _, _, _ = per_robot_stat(lambda r: r["xR"].mean())
sl, _, _, _ = per_robot_stat(lambda r: np.mean(1.0 - np.tanh(r["xL"]) ** 2))
sr, _, _, _ = per_robot_stat(lambda r: np.mean(1.0 - np.tanh(r["xR"]) ** 2))
absx, _, _, _ = per_robot_stat(lambda r: np.mean(np.abs(np.r_[r["xL"], r["xR"]])))
print(f"    real wheel pre-activation: mean xL {xl:+.3f}, xR {xr:+.3f}, mean |x| {absx:.3f}")
print(f"    mean tanh slope at the real operating point: left {sl:.4f}, right {sr:.4f}  (slope at x=0 is 1.0)")
out["5_operating_point"] = dict(xL=xl, xR=xr, slope_L=sl, slope_R=sr, abs_x=absx)

print("\n    w   | zero-baseline model (probe H/I)      | REAL baseline (x_gait held fixed)")
print("        | turn gap  common drive               | turn gap  common-drive shift")
h_rows = []
for w in (0.5, 1.0, 2.0, 4.0, 8.0):
    def zero_gap(r, w=w):
        a, b = modes(r["S1"])["sum"], modes(r["S2"])["sum"]
        return np.abs(np.tanh(w * a) - np.tanh(w * b)).mean() * 2.0

    def zero_com(r, w=w):
        a, b = modes(r["S1"])["sum"], modes(r["S2"])["sum"]
        return (0.5 * (np.tanh(w * a) + np.tanh(w * b))).mean()

    def real_gap(r, w=w):
        a, b = modes(r["S1"])["sum"], modes(r["S2"])["sum"]
        cl = np.clip(np.tanh(r["xL"] + w * b), -1, 1); cr = np.clip(np.tanh(r["xR"] + w * a), -1, 1)  # crossed
        ul = np.clip(np.tanh(r["xL"] + w * a), -1, 1); ur = np.clip(np.tanh(r["xR"] + w * b), -1, 1)  # uncrossed
        return np.abs((cl - cr) - (ul - ur)).mean()

    def real_shift(r, w=w):
        a, b = modes(r["S1"])["sum"], modes(r["S2"])["sum"]
        base = 0.5 * (np.tanh(r["xL"]) + np.tanh(r["xR"]))
        new = 0.5 * (np.clip(np.tanh(r["xL"] + w * b), -1, 1) + np.clip(np.tanh(r["xR"] + w * a), -1, 1))
        return (new - base).mean()

    zg, _, _, _ = per_robot_stat(zero_gap)
    zc, _, _, _ = per_robot_stat(zero_com)
    rg_, rglo, rghi, _ = per_robot_stat(real_gap)
    rs, _, _, _ = per_robot_stat(real_shift)
    h_rows.append(dict(w=w, zero_gap=zg, zero_common=zc, real_gap=rg_, real_gap_lo=rglo, real_gap_hi=rghi, real_shift=rs))
    print(f"    {w:4.1f} |  {zg:7.4f}   {zc:7.4f}                |  {rg_:7.4f} [{rglo:.4f},{rghi:.4f}]   {rs:+7.4f}")
out["5_tanh"] = h_rows
print("    'turn gap' = mean |(L-R)_crossed - (L-R)_uncrossed|, the ENTIRE behavioural difference")
print("    between the two wirings the spike compared, out of a +-2 range of turn command.")

with open("/home/user/rabbitstew/runs/sim-audit/refute_squash_0.json", "w") as fh:
    json.dump(out, fh, indent=1)
print("\nwrote runs/sim-audit/refute_squash_0.json")
