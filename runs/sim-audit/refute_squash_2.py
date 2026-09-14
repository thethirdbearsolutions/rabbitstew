"""REFUTATION CHECK for H4 ("the squash flattens the food field and kills the compass").

Lens: DOES IT MATTER?  H4's own probe already concedes the strong form (the field is not a
disc indicator at decay 1.0; the squash is monotone so it destroys no direction).  What is
left is a contrast tax of ~2.07x.  This script asks the only question that decides severity:

    if the squash is REMOVED, does a hand-installed Braitenberg compass earn anything?

Three fields, same world otherwise, same robots, same PAIRED seeds:
    stock   : smell="sum",  decay 1.0      (the shipped field, squash ON)
    raw     : the squash DELETED           (isolates H4 exactly: only S/(1+S) -> S changes)
    mean05  : smell="mean", decay 0.5      (H4's own recommended fix, claimed 4.4x contrast)

Weights are matched on INJECTED DIFFERENTIAL, not on nominal magnitude, so each field gets
the same steering signal and differs only in the common-mode tax it pays for it.  Ladder
D = 0.018 (the spike's best setting, crossed +0.5), 0.05, 0.14.

Also measured: the mower's OWN wheel-command differential during a normal bout -- the noise
floor any injected steering term has to beat.

Robot is the unit of analysis; CIs bootstrap over the 7 robots.  No library changes
(Simulation._intensity is monkeypatched in-process to add a "raw" mode).
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, "/home/user/rabbitstew")

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "/home/user/rabbitstew/runs/RBT-23/W4b-801"
GENS = (90, 190, 290, 390, 490, 550, 590)
NSEED = 48
SEED0 = 41000
TRACK = 0.3872
DISC = 3.0
ITEMS = 12

# ---------------------------------------------------------------- monkeypatch: add "raw" ----
_orig_intensity = Simulation._intensity


def _intensity(self, point, sources):
    f = self.config.food
    if f is not None and f.smell == "raw":
        if len(sources) == 0:
            return 0.0
        d = np.linalg.norm(sources - point[:2], axis=1)
        return float(np.exp(-d / f.decay).sum())      # the pile, unsquashed
    return _orig_intensity(self, point, sources)


Simulation._intensity = _intensity


# ------------------------------------------------- analytic: DC and differential per field ----
def field_stats(mode: str, decay: float, n_lay=400, n_pt=250, seed=5150):
    rng = np.random.default_rng(seed)
    r = DISC * np.sqrt(rng.random((n_lay, ITEMS)))
    a = rng.uniform(0, 2 * np.pi, (n_lay, ITEMS))
    lays = np.stack([r * np.cos(a), r * np.sin(a)], axis=-1)
    rp = 3.5 * np.sqrt(rng.random((n_lay, n_pt)))
    ra = rng.uniform(0, 2 * np.pi, (n_lay, n_pt))
    pts = np.stack([rp * np.cos(ra), rp * np.sin(ra)], axis=-1)
    head = rng.uniform(0, 2 * np.pi, (n_lay, n_pt))
    perp = np.stack([-np.sin(head), np.cos(head)], axis=-1)

    def val(P, src):
        d = np.linalg.norm(P[:, None, :] - src[None, :, :], axis=2)
        S = np.exp(-d / decay).sum(axis=1)
        if mode == "raw":
            return S
        if mode == "mean":
            i = S / ITEMS
            return i / (1 + i)
        return S / (1 + S)

    dc, df = [], []
    for i in range(n_lay):
        src = lays[i]
        c = val(pts[i], src)
        L = val(pts[i] + (TRACK / 2) * perp[i], src)
        R = val(pts[i] - (TRACK / 2) * perp[i], src)
        dc.append(c)
        df.append(np.abs(L - R))
    dc = np.concatenate(dc)
    df = np.concatenate(df)
    # tanh steering ceiling: best over w of mean |tanh(w L) - tanh(w R)|, and the common drive there
    ws = np.arange(0.05, 60.0, 0.05)
    best = (0.0, 0.0, 0.0)
    Lc, Rc = [], []
    for i in range(0, n_lay, 4):
        src = lays[i]
        Lc.append(val(pts[i] + (TRACK / 2) * perp[i], src))
        Rc.append(val(pts[i] - (TRACK / 2) * perp[i], src))
    Lc, Rc = np.concatenate(Lc), np.concatenate(Rc)
    for w in ws:
        v = float(np.abs(np.tanh(w * Lc) - np.tanh(w * Rc)).mean())
        if v > best[0]:
            best = (v, float(w), float(np.tanh(w * 0.5 * (Lc + Rc)).mean()))
    return dict(mode=mode, decay=decay, DC=float(dc.mean()), diff=float(df.mean()),
                ratio=float((df / np.maximum(dc, 1e-12)).mean()),
                ceiling=best[0], ceiling_w=best[1], ceiling_common=best[2])


# ------------------------------------------------------------------------------- the bouts ----
_CFG = None
_WIRE: dict = {}


def base_cfg():
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


FIELDS = {
    "stock": dict(smell="sum", decay=1.0),
    "raw": dict(smell="raw", decay=1.0),
    "mean05": dict(smell="mean", decay=0.5),
}


def wiring(gen):
    if gen in _WIRE:
        return _WIRE[gen]
    ph = synthesize(Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json"), base_cfg().synthesis)
    nose, eff, effall = {}, {}, {1: [], 2: []}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
            effall[u.part].append(i)
    _WIRE[gen] = (nose, eff, effall)
    return _WIRE[gen]


def bout(task):
    gen, seed, name, field, w = task
    fc = replace(base_cfg().food, **FIELDS[field])
    c = replace(base_cfg(), random_start=True, food=fc)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    nose, eff, effall = wiring(gen)
    W = sim.brains[0].W
    if w != 0.0 and name.startswith("uncross"):    # same links, nose into its OWN wheel
        W[eff[1], nose[1]] += w
        W[eff[2], nose[2]] += w
    elif w != 0.0:                                # crossed: nose on one wheel drives the OTHER
        W[eff[2], nose[1]] += w
        W[eff[1], nose[2]] += w
    steps = int(round(c.duration / c.control_dt))
    br = sim.brains[0]
    cmd_diff, cmd_abs, noses = [], [], []
    for _ in range(steps):
        sim.step()
        a = br.effector_output(1, 0)          # the real clipped wheel command, +-1
        b = br.effector_output(2, 0)
        act = br.activation                   # rebound every tick: must be re-read
        cmd_diff.append(abs(a - b))
        cmd_abs.append(0.5 * (abs(a) + abs(b)))
        noses.append((float(act[nose[1]]), float(act[nose[2]])))
    noses = np.array(noses)
    return dict(gen=gen, seed=seed, cond=name, food=float(sim.food_eaten[0]),
                own_diff=float(np.mean(cmd_diff)), own_abs=float(np.mean(cmd_abs)),
                nose_dc=float(noses.mean()), nose_dif=float(np.abs(noses[:, 0] - noses[:, 1]).mean()),
                exploded=bool(sim.exploded[0]))


def boot(v, draws=20000, seed=7):
    rng = np.random.default_rng(seed)
    v = np.asarray(v, float)
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(draws)])
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def main():
    out = {}
    print("[1] field statistics (analytic, 100k samples/field): DC, track differential, tanh ceiling")
    fs = {}
    for name, kw in FIELDS.items():
        fs[name] = field_stats("sum" if kw["smell"] == "sum" else kw["smell"], kw["decay"])
        s = fs[name]
        print(f"    {name:7s} DC={s['DC']:.4f}  |dI|={s['diff']:.4f}  |dI|/DC={s['ratio']:.4f}  "
              f"tanh ceiling={s['ceiling']:.4f} at w={s['ceiling_w']:.2f} (common drive {s['ceiling_common']:.3f})")
    out["fields"] = fs

    LADDER = (0.018, 0.05, 0.14)          # injected differential targets (0.018 = spike's crossed +0.5)
    wt = {f: [round(D / fs[f]["diff"], 4) for D in LADDER] for f in FIELDS}
    print(f"    weights matched on injected differential {LADDER}: " +
          "; ".join(f"{f}={wt[f]}" for f in FIELDS))
    out["ladder"] = LADDER
    out["weights"] = wt

    PH1 = [("base_stock", "stock", 0.0),
             ("cross_stock_D018", "stock", wt["stock"][0]),
             ("base_raw", "raw", 0.0),
             ("cross_raw_D018", "raw", wt["raw"][0]),
             ("cross_raw_D050", "raw", wt["raw"][1]),
             ("cross_raw_D140", "raw", wt["raw"][2]),
             ("cross_raw_D050neg", "raw", -wt["raw"][1]),
             ("base_mean05", "mean05", 0.0),
             ("cross_mean05_D050", "mean05", wt["mean05"][1]),
             ("cross_mean05_D140", "mean05", wt["mean05"][2])]
    PH2 = [("base_stock", "stock", 0.0),
           ("base_raw", "raw", 0.0),
           ("cross_raw_D018", "raw", wt["raw"][0]),
           ("cross_raw_D050", "raw", wt["raw"][1]),
           ("uncross_raw_D050", "raw", wt["raw"][1])]
    PH3 = [("base_stock", "stock", 0.0),
           ("base_raw", "raw", 0.0),
           ("cross_raw_D050", "raw", wt["raw"][1])]
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    conds = {"1": PH1, "2": PH2, "3": PH3}[arg]
    suffix = "" if arg == "1" else f"_p{arg}"
    seeds = [SEED0 + i for i in range(NSEED)]
    tasks = [(g, s, n, f, w) for (n, f, w) in conds for g in GENS for s in seeds]
    print(f"\n[2] {len(tasks)} bouts ({len(GENS)} robots x {NSEED} paired seeds x {len(conds)} conditions)")
    t0 = time.time()
    with Pool(4) as p:
        rows = p.map(bout, tasks, chunksize=8)
    print(f"    done in {time.time() - t0:.0f}s")
    out["rows"] = rows

    by = {(r["gen"], r["seed"], r["cond"]): r for r in rows}
    print("\n[3] items per bout, and paired delta vs the SAME-FIELD baseline (robot is the unit)")
    print("    condition             items   d vs own-field base   95% CI (bootstrap over 7 robots)")
    res = {}
    for name, field, w in conds:
        basename = f"base_{field}"
        per_robot_abs, per_robot_d = [], []
        for g in GENS:
            a = [by[(g, s, name)]["food"] for s in seeds]
            b = [by[(g, s, basename)]["food"] for s in seeds]
            per_robot_abs.append(float(np.mean(a)))
            per_robot_d.append(float(np.mean(a) - np.mean(b)))
        m, lo, hi = boot(per_robot_d)
        res[name] = dict(items=float(np.mean(per_robot_abs)), d=m, lo=lo, hi=hi,
                         per_robot=per_robot_d, w=w)
        print(f"    {name:20s} {np.mean(per_robot_abs):6.3f}   {m:+7.3f}            [{lo:+.3f}, {hi:+.3f}]")
    out["result"] = res

    # baseline-vs-baseline: does changing the FIELD alone move the mower?
    print("\n[4] field change with NO circuit (does de-squashing help/hurt the mower by itself?)")
    for f in [x for x in ("raw", "mean05") if any(k[2] == f"base_{x}" for k in by)]:
        d = [float(np.mean([by[(g, s, f"base_{f}")]["food"] for s in seeds]) -
                   np.mean([by[(g, s, "base_stock")]["food"] for s in seeds])) for g in GENS]
        m, lo, hi = boot(d)
        print(f"    base_{f:7s} - base_stock = {m:+.3f}  [{lo:+.3f}, {hi:+.3f}]")
        out[f"base_{f}_vs_stock"] = dict(d=m, lo=lo, hi=hi)

    json.dump(out, open(f"/home/user/rabbitstew/runs/sim-audit/refute_squash_2{suffix}.json", "w"), indent=1)
    print("\n[4b] every condition against the SHIPPED baseline (base_stock), paired per robot")
    for name, field, w in conds:
        d = [float(np.mean([by[(g, s, name)]["food"] for s in seeds]) -
                   np.mean([by[(g, s, "base_stock")]["food"] for s in seeds])) for g in GENS]
        m, lo, hi = boot(d)
        res[name]["vs_stock"] = dict(d=m, lo=lo, hi=hi, per_robot=d)
        print(f"    {name:20s} vs base_stock = {m:+.3f}  [{lo:+.3f}, {hi:+.3f}]   per-robot {[round(x,2) for x in d]}")

    print("\n[5] the mower's OWN wheel-command differential (baseline bouts) -- the noise floor")
    for f in [x for x in FIELDS if any(k[2] == f"base_{x}" for k in by)]:
        rr = [by[(g, s, f"base_{f}")] for g in GENS for s in seeds]
        od = float(np.mean([r["own_diff"] for r in rr]))
        oa = float(np.mean([r["own_abs"] for r in rr]))
        nd = float(np.mean([r["nose_dc"] for r in rr]))
        nf = float(np.mean([r["nose_dif"] for r in rr]))
        print(f"    base_{f:7s} mean |cmd_L - cmd_R| = {od:.3f}   mean |cmd| = {oa:.3f}   "
              f"nose DC (in bout) = {nd:.4f}  nose |L-R| = {nf:.4f}")
        out[f"own_{f}"] = dict(own_diff=od, own_abs=oa, nose_dc=nd, nose_diff=nf)
        out[f"own_{f}"]["injected_over_own"] = {str(D): (D / od if od > 0 else None) for D in LADDER}

    json.dump(out, open(f"/home/user/rabbitstew/runs/sim-audit/refute_squash_2{suffix}.json", "w"), indent=1)
    print("\nwrote runs/sim-audit/refute_squash_2.json")


if __name__ == "__main__":
    main()
