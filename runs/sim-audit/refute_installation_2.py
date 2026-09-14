"""REFUTATION ATTEMPT against H6 ("spike.py's Braitenberg install is wired wrong").

H6 asserts two things:

  (i)  the body's drive convention is ANTI-symmetric: translation lives on
       T = ctrl1 - ctrl2 and rotation on R = ctrl1 + ctrl2, not the textbook
       "effector up = that wheel forward";
  (ii) THEREFORE spike.py's crossed and uncrossed wirings both inject the
       identical turn command w*(n1+n2) -- "exactly zero gradient steering by
       construction", "a mathematical identity, not a null result" -- and the
       spike's crossed/uncrossed control is void.

(ii) is pure linear algebra: it holds only if the two effectors have the SAME
incremental gain.  H6's own section E reports the operating point of the real
robots as x1 = -0.488, x2 = +2.579, i.e. sech^2 = 0.795 vs 0.023, a 35x gain
asymmetry.  Under that asymmetry dR is NOT symmetric in n1,n2.  This script
measures the actual injected commands instead of assuming linearity.

  S1  re-measures the drive convention with UNWRAPPED yaw (H6's section C reads
      yaw from start/end orientation only, wrapped to +/-180 deg, and its own
      single-wheel rows -148.7 and -82.8 deg are visibly wrapped) and at two
      drive levels, to see whether "rotation = common mode" survives.
  S2  the crux: on real baseline bouts, the EXACT per-tick command each wiring
      injects, c = tanh(x + dx), decomposed into turn/drive and into
      common/gradient, plus a convention-free compass alignment (does the
      injected turn rotate the velocity vector toward the nearest food?).
  S3  does it matter: 7 robots x 64 paired seeds, spike_crossed vs
      spike_uncrossed (H6 says identical by construction) and spike_crossed vs
      the "corrected" oppA (H6 says only oppA is a real compass).

usage: ./v/bin/python runs/sim-audit/refute_installation_2.py [--seeds 64] [--workers 4]
"""

from __future__ import annotations

import argparse
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

_CFG = None


def cfg():
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


def geno(gen):
    return Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")


def wiring(gen):
    ph = synthesize(geno(gen), cfg().synthesis)
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
    return nose, eff


# dx1, dx2 as multiples of (n1, n2): (a1, b1, a2, b2) -> dx1 = w*(a1*n1+b1*n2)
WIRINGS = {
    "spike_crossed":   (0.0, +1.0, +1.0, 0.0),   # W[e1,n2]+=w , W[e2,n1]+=w
    "spike_uncrossed": (+1.0, 0.0, 0.0, +1.0),   # W[e1,n1]+=w , W[e2,n2]+=w
    "oppA":            (0.0, +1.0, -1.0, 0.0),   # crossed pairing, opposite signs
    "oppB":            (+1.0, 0.0, 0.0, -1.0),   # same-side pairing, opposite signs
}


def install(W, nose, eff, fam, w):
    if fam == "baseline":
        return
    a1, b1, a2, b2 = WIRINGS[fam]
    W[eff[1], nose[1]] += w * a1
    W[eff[1], nose[2]] += w * b1
    W[eff[2], nose[1]] += w * a2
    W[eff[2], nose[2]] += w * b2


def yaw_of(sim, rb):
    R = sim.data.xmat[rb.root_body].reshape(3, 3)
    return float(np.arctan2(R[1, 0], R[0, 0]))


# --------------------------------------------------------------------------- #
# S1 -- drive convention, unwrapped
# --------------------------------------------------------------------------- #
def polarity(task):
    gen, b, steps = task
    c = replace(cfg(), random_start=True)
    nose, eff = wiring(gen)
    out = {}
    for tag, (b1, b2) in (("(+,+)", (b, b)), ("(-,-)", (-b, -b)), ("(+,-)", (b, -b)),
                          ("(-,+)", (-b, b)), ("(+,0)", (b, 0.0)), ("(0,+)", (0.0, b))):
        sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, SEED0))
        sim.set_food_seed(SEED0)
        br = sim.brains[0]
        br.W[:, :] = 0.0
        br.bias[:] = 0.0
        br.bias[eff[1]] = b1
        br.bias[eff[2]] = b2
        rb = sim.robots[0]
        R0 = sim.data.xmat[rb.root_body].reshape(3, 3).copy()
        p0 = sim.center_of_mass(0)[:2].copy()
        prev = yaw_of(sim, rb)
        total = 0.0
        for _ in range(steps):
            sim.step()
            y = yaw_of(sim, rb)
            total += float(np.arctan2(np.sin(y - prev), np.cos(y - prev)))
            prev = y
        d = sim.center_of_mass(0)[:2] - p0
        out[tag] = dict(ctrl=(float(sim.data.ctrl[0]), float(sim.data.ctrl[1])),
                        fwd=float(R0[:2, 0] @ d), disp=float(np.linalg.norm(d)),
                        yaw_unwrapped_deg=float(np.degrees(total)))
    return gen, b, out


# --------------------------------------------------------------------------- #
# S2 -- exact injected command on a real baseline bout
# --------------------------------------------------------------------------- #
def trace(task):
    gen, seed = task
    c = replace(cfg(), random_start=True)
    nose, eff = wiring(gen)
    sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    br = sim.brains[0]
    e1, e2, n1, n2 = eff[1], eff[2], nose[1], nose[2]
    rb = sim.robots[0]
    rec = []
    prev_p = sim.center_of_mass(0)[:2].copy()
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
        a = br.activation
        x = br.W @ a + br.bias
        p = sim.center_of_mass(0)[:2]
        v = p - prev_p
        prev_p = p.copy()
        live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else sim.food_pos
        s = 0.0
        if len(live) and np.linalg.norm(v) > 1e-6:
            f = live[int(np.argmin(np.linalg.norm(live - p, axis=1)))] - p
            nf = np.linalg.norm(f)
            if nf > 1e-6:
                # +1 if rotating the body CCW (yaw up) swings the velocity vector
                # toward the food.  Convention-free: uses actual travel direction.
                s = float(np.sign(v[0] * f[1] - v[1] * f[0]))
        rec.append((a[n1], a[n2], x[e1], x[e2], s))
    r = np.array(rec)
    return dict(gen=gen, seed=seed, n1=r[:, 0], n2=r[:, 1], x1=r[:, 2], x2=r[:, 3], s=r[:, 4])


# --------------------------------------------------------------------------- #
# S3 -- paired-seed yield
# --------------------------------------------------------------------------- #
def bout(task):
    gen, seed, fam, w = task
    c = replace(cfg(), random_start=True)
    nose, eff = wiring(gen)
    sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    install(sim.brains[0].W, nose, eff, fam, w)
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
    lab = "baseline" if fam == "baseline" else f"{fam}{w:g}"
    return dict(gen=gen, seed=seed, cond=lab, food=float(sim.food_eaten[0]))


def boot(v, draws=20000, seed=3):
    rng = np.random.default_rng(seed)
    v = np.asarray(v, float)
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(draws)])
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((m <= 0).mean())


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=64)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    T0 = time.time()
    out = {}

    # ---------------- S1 ---------------- #
    print("=" * 92)
    print("S1. DRIVE CONVENTION, yaw accumulated per tick (unwrapped), 200 ticks = 4 s, W/bias zeroed")
    print("=" * 92)
    ptasks = [(g, b, 200) for g in GENS for b in (3.0, 0.7)]
    with Pool(args.workers) as p:
        prows = p.map(polarity, ptasks, chunksize=2)
    pol = {}
    for b in (3.0, 0.7):
        sel = [r for r in prows if r[1] == b]
        ctrl = abs(sel[0][2]["(+,+)"]["ctrl"][0])
        print(f"\n  bias magnitude {b} -> |ctrl| = {ctrl:.3f}   (mean over the {len(sel)} robots)")
        print(f"    {'(e1,e2)':>8s} {'net displ (m)':>14s} {'fwd (m)':>9s} {'yaw UNWRAPPED (deg)':>21s}")
        for tag in ("(+,-)", "(-,+)", "(+,+)", "(-,-)", "(+,0)", "(0,+)"):
            dd = float(np.mean([r[2][tag]["disp"] for r in sel]))
            ff = float(np.mean([r[2][tag]["fwd"] for r in sel]))
            yy = float(np.mean([r[2][tag]["yaw_unwrapped_deg"] for r in sel]))
            pol[f"{b}{tag}"] = dict(disp=dd, fwd=ff, yaw=yy)
            print(f"    {tag:>8s} {dd:14.3f} {ff:+9.3f} {yy:+21.1f}")
    out["polarity"] = pol
    print("\n  read: does translation live on the ANTI-symmetric mode, and is rotation really")
    print("        the common mode alone, or do differential inputs also turn the robot?")

    # ---------------- S2 ---------------- #
    print()
    print("=" * 92)
    print("S2. EXACT INJECTED COMMAND at the real operating point (7 robots x 6 baseline bouts)")
    print("=" * 92)
    ttasks = [(g, SEED0 + s) for g in GENS for s in range(6)]
    with Pool(args.workers) as p:
        trows = p.map(trace, ttasks, chunksize=2)
    n1 = np.concatenate([r["n1"] for r in trows])
    n2 = np.concatenate([r["n2"] for r in trows])
    x1 = np.concatenate([r["x1"] for r in trows])
    x2 = np.concatenate([r["x2"] for r in trows])
    sgn = np.concatenate([r["s"] for r in trows])
    s1 = 1.0 - np.tanh(x1) ** 2
    s2 = 1.0 - np.tanh(x2) ** 2
    print(f"  operating point: mean x1 {x1.mean():+.3f}  mean x2 {x2.mean():+.3f}   "
          f"mean sech^2(x1) {s1.mean():.4f}  mean sech^2(x2) {s2.mean():.4f}  "
          f"gain ratio {s1.mean() / max(s2.mean(), 1e-9):.1f}x")
    print(f"  noses: mean n1+n2 {np.mean(n1 + n2):.4f}   mean|n1-n2| {np.mean(np.abs(n1 - n2)):.4f}   "
          f"ticks with a signed food bearing: {100 * np.mean(sgn != 0):.0f}%")
    out["operating_point"] = dict(x1=float(x1.mean()), x2=float(x2.mean()),
                                  sech1=float(s1.mean()), sech2=float(s2.mean()),
                                  sum_n=float(np.mean(n1 + n2)), dif_n=float(np.mean(np.abs(n1 - n2))))

    print("\n  For each wiring: c = tanh(x + dx) with the SAME activations, so this is exactly what")
    print("  the install adds to the drive on that tick, before any trajectory divergence.")
    print("  dR = turn command injected (R = c1+c2), dT = drive command injected (T = c1-c2).")
    print("  EXACT symmetry split (no linearity assumed): recompute dR with the two nose READINGS")
    print("  swapped.  dR_sym = (dR(n1,n2)+dR(n2,n1))/2 depends only on TOTAL smell; dR_grad =")
    print("  (dR(n1,n2)-dR(n2,n1))/2 is the entire part that depends on WHICH nose smells more.")
    print("  H6's claim 'zero gradient information on the steering axis' is exactly rms(dR_grad)=0.")
    print("  'compass' = cov(dR, s), s = +1 when yaw-up swings the velocity vector toward the")
    print("  nearest food (covariance, so the common-mode DC cannot fake it).")
    com, dif = n1 + n2, n1 - n2
    print(f"  sd(n1+n2) = {com.std():.4f}   sd(n1-n2) = {dif.std():.4f}   mean(s) = {sgn.mean():+.4f}")
    s2r = {}

    def inject(fam, w, a_, b_):
        a1, b1, a2, b2 = WIRINGS[fam]
        dc1 = np.tanh(x1 + w * (a1 * a_ + b1 * b_)) - np.tanh(x1)
        dc2 = np.tanh(x2 + w * (a2 * a_ + b2 * b_)) - np.tanh(x2)
        return dc1 + dc2, dc1 - dc2

    for w in (1.0, 2.0):
        print(f"\n  w = {w:g}")
        print(f"    {'wiring':17s} {'mean dR':>9s} {'rms dR_sym':>11s} {'rms dR_grad':>12s} "
              f"{'grad share':>11s} {'compass cov':>12s} {'mean dT':>9s}")
        for fam in WIRINGS:
            dR, dT = inject(fam, w, n1, n2)
            dRs, _ = inject(fam, w, n2, n1)          # nose readings swapped
            grad = 0.5 * (dR - dRs)
            sym = 0.5 * (dR + dRs)
            rg, rs = float(np.sqrt(np.mean(grad ** 2))), float(np.sqrt(np.mean((sym - sym.mean()) ** 2)))
            comp = float(np.mean(dR * sgn) - dR.mean() * sgn.mean())
            s2r[f"{fam}{w:g}"] = dict(dR=float(dR.mean()), rms_sym=rs, rms_grad=rg,
                                      grad_share=rg / max(rg + rs, 1e-12), compass_cov=comp,
                                      dT=float(dT.mean()))
            print(f"    {fam:17s} {dR.mean():+9.4f} {rs:11.4f} {rg:12.5f} "
                  f"{100 * rg / max(rg + rs, 1e-12):10.1f}% {comp:+12.5f} {dT.mean():+9.4f}")
    out["injected"] = s2r

    # ---------------- S3 ---------------- #
    print()
    print("=" * 92)
    print(f"S3. DOES IT MATTER -- 7 robots x {args.seeds} paired seeds, bootstrap over ROBOTS")
    print("=" * 92)
    seeds = [SEED0 + i for i in range(args.seeds)]
    conds = [("baseline", 0.0), ("spike_crossed", 2.0), ("spike_uncrossed", 2.0), ("oppA", 2.0)]
    tasks = [(g, s, f, w) for g in GENS for s in seeds for f, w in conds]
    print(f"  {len(tasks)} bouts ...", flush=True)
    t0 = time.time()
    with Pool(args.workers) as p:
        rows = p.map(bout, tasks, chunksize=8)
    print(f"  done in {time.time() - t0:.0f}s")
    by = {(r["gen"], r["seed"], r["cond"]): r["food"] for r in rows}
    base = float(np.mean([by[(g, s, "baseline")] for g in GENS for s in seeds]))
    print(f"  baseline {base:.3f} items\n")
    per = {}
    print(f"  | condition | d items vs baseline | 95% CI (7 robots) | P(d<=0) |")
    print(f"  |---|---|---|---|")
    for fam, w in conds[1:]:
        lab = f"{fam}{w:g}"
        per[lab] = [float(np.mean([by[(g, s, lab)] - by[(g, s, "baseline")] for s in seeds])) for g in GENS]
        m, lo, hi, pn = boot(per[lab])
        print(f"  | {lab} | {m:+.3f} | [{lo:+.3f}, {hi:+.3f}] | {pn:.3f} |")
    print()
    for a_, b_ in (("spike_crossed2", "spike_uncrossed2"), ("spike_crossed2", "oppA2")):
        d = np.array(per[a_]) - np.array(per[b_])
        m, lo, hi, pn = boot(d)
        print(f"  paired contrast {a_} - {b_}: d = {m:+.3f} items  95% CI [{lo:+.3f}, {hi:+.3f}]  "
              f"P(d<=0) = {pn:.3f}")
    out["yield"] = dict(baseline=base, per_robot=per)

    with open("runs/sim-audit/refute_installation_2.json", "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"\ntotal {time.time() - T0:.0f}s; wrote runs/sim-audit/refute_installation_2.json")
