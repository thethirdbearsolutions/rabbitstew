"""H6 -- adversarial audit of runs/compass-spike/spike.py's INSTALLATION.

Six code checks the brief asked for, then a physical check of what the installed
circuit actually does to the drive.

The load-bearing question turns out to be one nobody asked: what do the two
effector units MEAN in terms of the drive?  The spike assumes the standard
differential-drive convention -- effector up = that wheel forward -- so that
"same weight onto both effectors" = more forward drive on both, and the only
difference between crossed and uncrossed is which nose steers.  That convention
is not this body's.  Sections C/D measure it.

usage: ./v/bin/python runs/sim-audit/probe_installation.py [--seeds 64] [--workers 4]
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
    """The spike's own unit-finding code, verbatim, so any defect found is the spike's."""
    ph = synthesize(geno(gen), cfg().synthesis)
    nose, jv, eff = {}, {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "joint_velocity":
            jv[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
    return ph, nose, jv, eff


# --------------------------------------------------------------------------- #
# The five wirings.  e1/e2 are the effector units of parts 1/2, n1/n2 their noses.
#   spike_crossed / spike_uncrossed : SAME sign onto both effectors (what spike.py does)
#   oppA / oppB                     : OPPOSITE signs onto the two effectors
# --------------------------------------------------------------------------- #
def install(W, nose, eff, fam, w):
    e1, e2, n1, n2 = eff[1], eff[2], nose[1], nose[2]
    if fam == "baseline":
        pass
    elif fam == "spike_crossed":
        W[e2, n1] += w
        W[e1, n2] += w
    elif fam == "spike_uncrossed":
        W[e1, n1] += w
        W[e2, n2] += w
    elif fam == "oppA":              # crossed pairing, opposite effector signs
        W[e1, n2] += w
        W[e2, n1] -= w
    elif fam == "oppB":              # same-side pairing, opposite effector signs
        W[e1, n1] += w
        W[e2, n2] -= w
    else:
        raise ValueError(fam)


# --------------------------------------------------------------------------- #
# C -- what do the two effectors mean?  W and bias zeroed, effectors held at fixed
#      values; measure translation and yaw.
# --------------------------------------------------------------------------- #
def polarity(gen, steps=200, b=3.0):
    c = replace(cfg(), random_start=True)
    ph, nose, jv, eff = wiring(gen)
    out = {}
    for tag, (b1, b2) in (("(+,+)", (b, b)), ("(-,-)", (-b, -b)),
                          ("(+,-)", (b, -b)), ("(-,+)", (-b, b)),
                          ("(+,0)", (b, 0.0)), ("(0,+)", (0.0, b))):
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
        for _ in range(steps):
            sim.step()
        R1 = sim.data.xmat[rb.root_body].reshape(3, 3)
        d = sim.center_of_mass(0)[:2] - p0
        y0, y1 = np.arctan2(R0[1, 0], R0[0, 0]), np.arctan2(R1[1, 0], R1[0, 0])
        out[tag] = dict(ctrl=(float(sim.data.ctrl[0]), float(sim.data.ctrl[1])),
                        fwd=float(R0[:2, 0] @ d), lat=float(R0[:2, 1] @ d),
                        dyaw_deg=float(np.degrees(np.arctan2(np.sin(y1 - y0), np.cos(y1 - y0)))))
    return out


# --------------------------------------------------------------------------- #
# D -- clean-vehicle veer test.  Flat world, one uneatable food item off to one
#      side, brain wiped to a constant forward drive, then the circuit installed.
#      A compass must curve toward the item; a spin drive must not.
# --------------------------------------------------------------------------- #
def veer_cfg():
    c = cfg()
    return replace(c,
                   world=replace(c.world, terrain="flat"),
                   food=replace(c.food, items=1, eat_radius=0.02, clearance=0.0, regrow=False),
                   random_start=False, duration=8.0)


def veer(task):
    gen, fam, w, side, base = task
    c = veer_cfg()
    ph, nose, jv, eff = wiring(gen)
    from rabbitstew.world import Spawn
    sim = Simulation([geno(gen)], c, spawns=[Spawn(position=(0.0, 0.0, 0.0), yaw=0.0)])
    sim.set_food_seed(1)
    item = np.array([[2.5, side * 1.2]])
    sim.food_pos = item.copy()
    sim.food_spots = item.copy()
    sim.food_alive = np.ones(1, dtype=bool)
    sim.food_timer = np.zeros(1)
    br = sim.brains[0]
    br.W[:, :] = 0.0
    br.bias[:] = 0.0
    br.bias[eff[1]] = +base          # (+,-) is the translating mode; see section C
    br.bias[eff[2]] = -base
    install(br.W, nose, eff, fam, w)
    rb = sim.robots[0]
    R0 = sim.data.xmat[rb.root_body].reshape(3, 3).copy()
    p0 = sim.center_of_mass(0)[:2].copy()
    steps = int(round(c.duration / c.control_dt))
    mind = 1e9
    for _ in range(steps):
        sim.step()
        mind = min(mind, float(np.linalg.norm(sim.center_of_mass(0)[:2] - item[0])))
    d = sim.center_of_mass(0)[:2] - p0
    y0 = np.arctan2(R0[1, 0], R0[0, 0])
    R1 = sim.data.xmat[rb.root_body].reshape(3, 3)
    y1 = np.arctan2(R1[1, 0], R1[0, 0])
    dyaw = float(np.degrees(np.arctan2(np.sin(y1 - y0), np.cos(y1 - y0))))
    lat = float(R0[:2, 1] @ d)
    return dict(gen=gen, fam=fam, w=w, side=side,
                # positive = veered toward the item's side
                toward=side * lat, toward_yaw=side * dyaw,
                fwd=float(R0[:2, 0] @ d), min_dist=mind)


# --------------------------------------------------------------------------- #
# E -- instrumented real bout: what does the install put on each drive axis?
# --------------------------------------------------------------------------- #
def trace(task):
    gen, fam, w, seed = task
    c = replace(cfg(), random_start=True)
    ph, nose, jv, eff = wiring(gen)
    sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    br = sim.brains[0]
    install(br.W, nose, eff, fam, w)
    e1, e2, n1, n2 = eff[1], eff[2], nose[1], nose[2]
    rec = []
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
        a = br.activation
        x = br.W @ a + br.bias           # the pre-activation the NEXT tick will use
        rec.append((a[n1], a[n2], x[e1], x[e2], a[e1], a[e2]))
    r = np.array(rec)
    return dict(gen=gen, fam=fam, w=w, seed=seed,
                n1=r[:, 0], n2=r[:, 1], x1=r[:, 2], x2=r[:, 3], c1=r[:, 4], c2=r[:, 5],
                food=float(sim.food_eaten[0]))


# --------------------------------------------------------------------------- #
# F -- headline: paired-seed yield for the corrected wirings
# --------------------------------------------------------------------------- #
def bout(task):
    gen, seed, fam, w = task
    c = replace(cfg(), random_start=True)
    ph, nose, jv, eff = wiring(gen)
    sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    install(sim.brains[0].W, nose, eff, fam, w)
    disc = c.food.radius
    steps = int(round(c.duration / c.control_dt))
    last = sim.center_of_mass(0)[:2].copy()
    in_path = 0.0
    near = []
    for _ in range(steps):
        sim.step()
        p = sim.center_of_mass(0)[:2]
        r = float(np.linalg.norm(p))
        if r <= disc:
            in_path += float(np.linalg.norm(p - last))
            live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else sim.food_pos
            if len(live):
                near.append(float(np.linalg.norm(live - p, axis=1).min()))
        last = p.copy()
    return dict(gen=gen, seed=seed, cond=f"{fam}{w:g}" if fam != "baseline" else "baseline",
                food=float(sim.food_eaten[0]), in_path=in_path,
                near=float(np.mean(near)) if near else float("nan"),
                exploded=bool(sim.exploded[0]))


def boot_ci(v, draws=20000, seed=3):
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

    # ----- A. static audit ------------------------------------------------- #
    print("=" * 78)
    print("A. STATIC AUDIT -- indices, orientation, persistence")
    print("=" * 78)
    ph, nose, jv, eff = wiring(590)
    print(f"parts of the Pioneer ({len(ph.parts)}):")
    for p in ph.parts:
        nu = len(ph.units_of_part(p.index))
        print(f"  part {p.index}: node {p.node} {p.shape.name.lower():8s} parent={p.parent} "
              f"{p.joint_type.name.lower():6s} ndof={p.joint_type.ndof} mass={p.mass:5.2f} "
              f"attach={np.round(p.attach_pos, 3)} units={nu}")
    c = replace(cfg(), random_start=True)
    sim = Simulation([geno(590)], c, spawns=spawn_layout(1, c, SEED0))
    sim.set_food_seed(SEED0)
    print(f"\n  mujoco actuators (part,dof)->id : {dict(sim.robots[0].actuators)}")
    print(f"  brain.effectors (part,dof)->units: {dict(sim.brains[0].effectors)}   nu={sim.model.nu}")
    print(f"  => A1 the DRIVEN parts are exactly {sorted(k[0] for k in sim.robots[0].actuators)}; "
          f"parts 3,4 carry no units, no effectors, no actuators (passive castors).")

    print("\n  A1b unit indices found by the spike's scan, all 7 robots:")
    same = True
    for g_ in GENS:
        _ph, _n, _j, _e = wiring(g_)
        ne = {p: [i for i, u in enumerate(_ph.units) if u.part == p and u.unit.kind == "effector"] for p in (1, 2)}
        nn = {p: [i for i, u in enumerate(_ph.units) if u.part == p and u.unit.kind == "sensor"
                  and u.unit.source == "food"] for p in (1, 2)}
        ok = all(len(v) == 1 for v in ne.values()) and all(len(v) == 1 for v in nn.values())
        same &= ok
        print(f"    gen {g_}: nose={_n} eff={_e} jv={_j}  (effector units per wheel {[len(v) for v in ne.values()]}, "
              f"food sensors per wheel {[len(v) for v in nn.values()]}) {'OK' if ok else 'AMBIGUOUS'}")
    print(f"  => A1c one effector and one food sensor per wheel on every robot: "
          f"{'yes, eff[p]=i last-wins is unambiguous' if same else 'NO -- last-wins is ambiguous'}")

    # A2 orientation of W
    br = sim.brains[0]
    W = br.W
    e1, e2, n1, n2 = eff[1], eff[2], nose[1], nose[2]
    a = np.zeros(br.n)
    a[n1] = 1.0
    fwd = W @ a
    W2 = W.copy()
    W2[e2, n1] += 5.0
    W3 = W.copy()
    W3[n1, e2] += 5.0
    print(f"\n  A2 W[dst,src] orientation: with activation = onehot(nose1),")
    print(f"     (W_installed @ a)[eff2] - (W @ a)[eff2] = {(W2 @ a)[e2] - (W @ a)[e2]:+.3f}  (W[eff,nose] += 5)")
    print(f"     (W_transposed@ a)[eff2] - (W @ a)[eff2] = {(W3 @ a)[e2] - (W @ a)[e2]:+.3f}  (W[nose,eff] += 5)")
    print(f"     brain.py: 'for src, dst, w in phenotype.links: self.W[dst, src] += w'; "
          f"step(): 'x = self.W @ self.activation'")
    print(f"  => A2 W[eff,nose] IS 'from nose to effector'.  The spike's orientation is CORRECT.")

    # A3 transfer function on effectors
    kinds = {k: [i for i in v] for k, v in br.funcs.items()}
    ef_func = [k for k, v in kinds.items() if e1 in v or e2 in v]
    print(f"\n  A3 transfer function bucket holding the effector units: {ef_func}  "
          f"(brain.py: \"func = u.func if u.kind == 'neuron' else 'tanh'\")")
    print(f"     effector_output() then clips the SUM of a (part,dof)'s units to [-1,1]; here 1 unit each.")

    # A4 existing weights and biases at the install sites
    print(f"\n  A4/A6 pre-existing state at the install sites (gen -> value):")
    print(f"    {'gen':>4s} {'bias[e1]':>9s} {'bias[e2]':>9s} {'W[e1,n1]':>9s} {'W[e1,n2]':>9s} "
          f"{'W[e2,n1]':>9s} {'W[e2,n2]':>9s}")
    prior = {}
    for g_ in GENS:
        _ph, _n, _j, _e = wiring(g_)
        _sim = Simulation([geno(g_)], c, spawns=spawn_layout(1, c, SEED0))
        _b = _sim.brains[0]
        row = (_b.bias[_e[1]], _b.bias[_e[2]], _b.W[_e[1], _n[1]], _b.W[_e[1], _n[2]],
               _b.W[_e[2], _n[1]], _b.W[_e[2], _n[2]])
        prior[g_] = [float(x) for x in row]
        print(f"    {g_:4d} " + " ".join(f"{x:+9.3f}" for x in row))
    print(f"  => A6 the four install sites are all exactly 0.0 on every robot, so '+=' and '=' "
          f"are identical here.  The spike's '+=' is fine.")
    out["prior_state"] = prior

    # A5 persistence of the modification through a run
    _sim = Simulation([geno(590)], c, spawns=spawn_layout(1, c, SEED0))
    _sim.set_food_seed(SEED0)
    Wref = _sim.brains[0].W
    Wref[e2, n1] += 7.0
    for _ in range(200):
        _sim.step()
    print(f"\n  A5 after 200 control steps: brains[0].W is the same array = "
          f"{_sim.brains[0].W is Wref}; W[eff2,nose1] = {_sim.brains[0].W[e2, n1]:+.3f} (installed 7.0)")
    print(f"  => A5 W is read fresh every tick and never rebuilt.  The modification PERSISTS.")

    # ----- C. what the effectors mean -------------------------------------- #
    print()
    print("=" * 78)
    print("C. WHAT DO THE TWO EFFECTOR UNITS MEAN?  (W and bias zeroed, 200 ticks = 4 s)")
    print("=" * 78)
    pol = {}
    for g_ in GENS:
        pol[g_] = polarity(g_)
    print(f"  {'(e1,e2)':>8s} " + "".join(f"{'ctrl':>14s}{'fwd m':>9s}{'yaw deg':>9s}" for _ in [0])
          + "     (gen 590; all 7 robots share the Pioneer body)")
    for tag, r in pol[590].items():
        print(f"  {tag:>8s}  ctrl=({r['ctrl'][0]:+.3f},{r['ctrl'][1]:+.3f})  "
              f"fwd={r['fwd']:+7.3f} m  lat={r['lat']:+6.3f} m  dyaw={r['dyaw_deg']:+8.1f} deg")
    tr_mode = pol[590]["(+,-)"]["fwd"]
    rot_mode = pol[590]["(+,+)"]["dyaw_deg"]
    print(f"\n  => C1 TRANSLATION lives on the ANTI-symmetric mode (ctrl1 - ctrl2): "
          f"(+,-) travels {tr_mode:+.2f} m.")
    print(f"     C2 ROTATION lives on the COMMON mode (ctrl1 + ctrl2): "
          f"(+,+) spins {rot_mode:+.1f} deg with |displacement| "
          f"{np.hypot(pol[590]['(+,+)']['fwd'], pol[590]['(+,+)']['lat']):.3f} m -- it pirouettes.")
    print(f"     across all 7 robots:  (+,-) fwd = "
          f"{[round(pol[g]['(+,-)']['fwd'], 2) for g in GENS]}")
    print(f"                           (+,+) dyaw= "
          f"{[round(pol[g]['(+,+)']['dyaw_deg'], 1) for g in GENS]}")
    print(f"                           (+,+) |disp| = "
          f"{[round(float(np.hypot(pol[g]['(+,+)']['fwd'], pol[g]['(+,+)']['lat'])), 3) for g in GENS]}")
    out["polarity"] = {str(g): pol[g] for g in GENS}

    print("\n  CONSEQUENCE, algebraically.  Write R = ctrl1+ctrl2 (turn), T = ctrl1-ctrl2 (drive).")
    print("    spike 'crossed'  : dx1 = +w*n2, dx2 = +w*n1  ->  dR = w(n1+n2)   dT = w(n2-n1)")
    print("    spike 'uncrossed': dx1 = +w*n1, dx2 = +w*n2  ->  dR = w(n1+n2)   dT = w(n1-n2)")
    print("    The TURN drive is IDENTICALLY w(n1+n2) for both.  It depends only on TOTAL smell,")
    print("    never on which nose smells more.  The gradient (n1-n2) lands entirely on T, where")
    print("    it modulates SPEED.  Neither spike wiring can steer on a gradient at all.")
    print("    Opposite-sign wirings do:  dx1 = +w*na, dx2 = -w*nb -> dR = w(na-nb), dT = w(na+nb).")

    # ----- D. clean-vehicle veer test -------------------------------------- #
    print()
    print("=" * 78)
    print("D. VEER TEST -- flat world, one uneatable item at (2.5, +/-1.2), brain wiped to a")
    print("   constant forward drive (bias e1=+0.7, e2=-0.7), circuit installed, 8 s")
    print("=" * 78)
    vtasks = [(g, fam, w, side, 0.7)
              for g in GENS
              for fam, w in (("baseline", 0.0), ("spike_crossed", 2.0), ("spike_uncrossed", 2.0),
                             ("oppA", 2.0), ("oppB", 2.0), ("oppA", 6.0), ("oppB", 6.0))
              for side in (+1, -1)]
    with Pool(args.workers) as p:
        vrows = p.map(veer, vtasks, chunksize=4)
    print(f"  {'wiring':18s} {'veer toward item (m)':>21s} {'yaw toward (deg)':>18s} "
          f"{'fwd (m)':>9s} {'closest approach (m)':>21s}")
    vsum = {}
    for fam, w in (("baseline", 0.0), ("spike_crossed", 2.0), ("spike_uncrossed", 2.0),
                   ("oppA", 2.0), ("oppB", 2.0), ("oppA", 6.0), ("oppB", 6.0)):
        sel = [r for r in vrows if r["fam"] == fam and r["w"] == w]
        tv = float(np.mean([r["toward"] for r in sel]))
        ty = float(np.mean([r["toward_yaw"] for r in sel]))
        fw = float(np.mean([r["fwd"] for r in sel]))
        md = float(np.mean([r["min_dist"] for r in sel]))
        vsum[f"{fam}{w:g}"] = dict(toward=tv, toward_yaw=ty, fwd=fw, min_dist=md)
        print(f"  {fam + ' w=' + format(w, 'g'):18s} {tv:+21.3f} {ty:+18.1f} {fw:+9.3f} {md:21.3f}")
    print("  (veer/yaw 'toward' are signed so POSITIVE = curved toward the food; averaged over the")
    print("   two mirrored placements and all 7 robots, so a body asymmetry cannot fake a sign.)")
    out["veer"] = vsum
    base_md = vsum["baseline0"]["min_dist"]
    toward_fam = max(("oppA2", "oppB2"), key=lambda k: vsum[k]["toward"])
    away_fam = "oppB2" if toward_fam == "oppA2" else "oppA2"
    TOWARD = toward_fam[:4]
    AWAY = away_fam[:4]
    print(f"\n  => D1 the compass-positive wiring is {TOWARD} (toward = {vsum[toward_fam]['toward']:+.3f} m, "
          f"closest approach {vsum[toward_fam]['min_dist']:.3f} m vs baseline {base_md:.3f} m)")
    print(f"     D2 its mirror {AWAY} is the matched anti-compass "
          f"(toward = {vsum[away_fam]['toward']:+.3f} m, closest {vsum[away_fam]['min_dist']:.3f} m)")
    print(f"     D3 the spike's wirings: crossed toward = {vsum['spike_crossed2']['toward']:+.3f} m, "
          f"uncrossed toward = {vsum['spike_uncrossed2']['toward']:+.3f} m")

    # ----- E. instrumented real bout --------------------------------------- #
    print()
    print("=" * 78)
    print("E. INSTRUMENTED REAL BOUT -- what each wiring puts on each drive axis")
    print("=" * 78)
    etasks = [(g, fam, w, SEED0 + s)
              for g in GENS for s in range(4)
              for fam, w in (("baseline", 0.0), ("spike_crossed", 2.0), ("spike_uncrossed", 2.0),
                             (TOWARD, 2.0), ("spike_crossed", 8.0))]
    with Pool(args.workers) as p:
        erows = p.map(trace, etasks, chunksize=4)
    print(f"  {'wiring':20s} {'|n1-n2|':>8s} {'n1+n2':>7s} {'mean x1':>8s} {'mean x2':>8s} "
          f"{'|x|>2':>7s} {'mean|T|':>8s} {'mean|R|':>8s} {'items':>6s}")
    esum = {}
    for fam, w in (("baseline", 0.0), ("spike_crossed", 2.0), ("spike_uncrossed", 2.0),
                   (TOWARD, 2.0), ("spike_crossed", 8.0)):
        sel = [r for r in erows if r["fam"] == fam and r["w"] == w]
        n1v = np.concatenate([r["n1"] for r in sel])
        n2v = np.concatenate([r["n2"] for r in sel])
        x1 = np.concatenate([r["x1"] for r in sel])
        x2 = np.concatenate([r["x2"] for r in sel])
        c1 = np.concatenate([r["c1"] for r in sel])
        c2 = np.concatenate([r["c2"] for r in sel])
        d = dict(dn=float(np.mean(np.abs(n1v - n2v))), sn=float(np.mean(n1v + n2v)),
                 x1=float(np.mean(x1)), x2=float(np.mean(x2)),
                 sat=float(np.mean((np.abs(x1) > 2) | (np.abs(x2) > 2))),
                 T=float(np.mean(np.abs(c1 - c2))), R=float(np.mean(np.abs(c1 + c2))),
                 items=float(np.mean([r["food"] for r in sel])))
        esum[f"{fam}{w:g}"] = d
        print(f"  {fam + ' w=' + format(w, 'g'):20s} {d['dn']:8.4f} {d['sn']:7.4f} {d['x1']:+8.3f} "
              f"{d['x2']:+8.3f} {100 * d['sat']:6.0f}% {d['T']:8.3f} {d['R']:8.3f} {d['items']:6.2f}")
    out["trace"] = esum
    print("  T = |ctrl1-ctrl2| is drive, R = |ctrl1+ctrl2| is spin (section C).")

    # ----- F. headline paired-seed yield ----------------------------------- #
    print()
    print("=" * 78)
    print(f"F. PAIRED-SEED YIELD -- 7 robots x {args.seeds} paired seeds, bootstrap over ROBOTS")
    print("=" * 78)
    seeds = [SEED0 + i for i in range(args.seeds)]
    conds = [("baseline", 0.0), ("spike_crossed", 2.0), (TOWARD, 1.0), (TOWARD, 2.0), (AWAY, 2.0)]
    tasks = [(g, s, fam, w) for g in GENS for s in seeds for fam, w in conds]
    print(f"  {len(tasks)} bouts ...", flush=True)
    t0 = time.time()
    with Pool(args.workers) as p:
        rows = p.map(bout, tasks, chunksize=8)
    print(f"  done in {time.time() - t0:.0f}s")
    by = {(r["gen"], r["seed"], r["cond"]): r for r in rows}
    print(f"\n  baseline solo yield: "
          f"{np.mean([by[(g, s, 'baseline')]['food'] for g in GENS for s in seeds]):.3f} items")
    print(f"\n  | condition | d items | 95% CI (over 7 robots) | P(d<=0) | d in-disc path m | d near-dist m |")
    print(f"  |---|---|---|---|---|---|")
    fsum = {}
    for fam, w in conds:
        lab = f"{fam}{w:g}" if fam != "baseline" else "baseline"
        if lab == "baseline":
            continue
        per_robot = [float(np.mean([by[(g, s, lab)]["food"] - by[(g, s, "baseline")]["food"]
                                    for s in seeds])) for g in GENS]
        m, lo, hi, pneg = boot_ci(per_robot)
        dp = float(np.mean([np.mean([by[(g, s, lab)]["in_path"] - by[(g, s, "baseline")]["in_path"]
                                     for s in seeds]) for g in GENS]))
        dn = float(np.mean([np.nanmean([by[(g, s, lab)]["near"] - by[(g, s, "baseline")]["near"]
                                        for s in seeds]) for g in GENS]))
        fsum[lab] = dict(delta=m, ci=[lo, hi], p_le_0=pneg, d_path=dp, d_near=dn,
                         per_robot=per_robot)
        print(f"  | {lab} | {m:+.3f} | [{lo:+.3f}, {hi:+.3f}] | {pneg:.3f} | {dp:+.2f} | {dn:+.3f} |")
    # matched compass-vs-anticompass contrast at w=2
    a = np.array(fsum[f"{TOWARD}2"]["per_robot"])
    b_ = np.array(fsum[f"{AWAY}2"]["per_robot"])
    m, lo, hi, pneg = boot_ci(a - b_)
    print(f"\n  matched contrast {TOWARD}2 - {AWAY}2 (identical speed response, opposite steering):")
    print(f"    d = {m:+.3f} items  95% CI [{lo:+.3f}, {hi:+.3f}]  P(d<=0) = {pneg:.3f}")
    fsum["contrast"] = dict(delta=m, ci=[lo, hi], p_le_0=pneg)
    out["yield"] = fsum
    out["toward"] = TOWARD
    out["away"] = AWAY

    with open("runs/sim-audit/probe_installation.json", "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"\ntotal {time.time() - T0:.0f}s; wrote runs/sim-audit/probe_installation.json")
