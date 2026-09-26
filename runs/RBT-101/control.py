"""RBT-101: the re-wiring readout's positive control, on real evolved bodies (RBT-66's rule).

Two steps, so that every number in control.txt re-derives from committed text:

  python runs/RBT-101/control.py extract RUN_DIR SEED [TCAL] > runs/RBT-101/control/SEED.txt
      From one seed's baseline economy (RBT-90 part 2's arm, restored from its checkpoint; bulk, read for
      its genomes and lineage only -- no income, alive count or deaths column is read), per fauna:
        C0 = the individuals alive at TCAL - 1, P = the individuals alive at TCAL + 160,
      exactly the two groups rewire.py compares across a real onset at T = TCAL.  One row per individual:
      its posture-wiring digest (wiring.py: g1, g2), and for P its C0 ancestors (RBT-84's descent rule,
      every parent followed) and the digest with ONE KNOWN POSTURE REFLEX INSTALLED: a direct link from one
      of its own posture sensors (contact, height, up, joint_angle, joint_velocity) to one of its live
      effectors, at w = 1.0 (the operator's typical weight, RBT-62: median |w| 0.85-1.13) and at w = 0.5.
      The pair is drawn by a stream seeded from the individual's name, so it is fixed.  A body with no
      posture sensor or no live effector cannot carry the reflex (installable = 0): a re-wiring in C4 can
      only be a new use of a sensor the body carries (docs/held-out-challenges.md section 3).
      Also a liveness check on the installed reflex, with RBT-66's frozen-trajectory probe generalised to
      any body: in one bout on flat terrain, every 10 ticks the brain state is saved and stepped 8 ticks
      with the posture sensors at their readings and again with them zeroed, every other sensor held;
      the response is the peak over the 8 ticks of the mean |difference| over the body's driven degrees
      of freedom.  Read on up to PROBE bodies of P per fauna, with and without the reflex installed.

  python runs/RBT-101/control.py analyse [DIR] > runs/RBT-101/control.txt
      Arithmetic on the committed tables only.  For each n (10 down to 6) and each installed fraction f
      of P's installable bodies, R replicates of:
        - draw n seeds of the ten; in each, install the reflex on a random fraction f of P (pseudo-shift);
        - pair every drawn seed with another drawn seed by a random derangement, twice, for the pseudo-base
          and the pseudo-cull: their P and C0 carry no install;
        - compute rewire.py's scored statistic per seed and the contrasts pseudo-shift - pseudo-base and
          pseudo-shift - pseudo-cull, and apply rewire.py's RE-WIRED rule (both t(n-1) 95% intervals
          exclude 0, the same sign).
      The scored statistic (STAT = new) is rewire.py's: the fraction of P carrying a NEW DIRECT POSTURE
      LINK, g1 at least 0.5 above the largest g1 among its C0 ancestors.  The mean-wiring statistics
      (g1, g2, log(1 + g2), as W-acq) are available with RBT101_STAT and were measured on a development
      window and rejected before any C4 arm exists: on the holistic fauna their between-seed drift (g2: sd
      1.56 against an installed +1.0) hides an installed reflex on every survivor (PREREGISTRATION.md
      section 6.3).  The sign guard (>= ceil(0.8 n)/n seeds) is off by default (RBT101_SIGN_GUARD=1 turns it
      on) for the reason given there.
      The noise is BETWEEN SEEDS: a seed's own base and shift arms share C0 byte for byte and differ only
      in what happened after T, so a between-seed pairing overstates the noise, and the control is
      conservative.  (It also makes the no-install mean exactly 0 by construction, because every drawn seed
      appears once on each side; so the false-positive check is run on a second model, a random half-split
      of each seed's P into pseudo-shift and pseudo-base, which can err either way.)

PASS at n (pre-registered in PREREGISTRATION.md section 6): at f = 1.0, w = 1.0 the RE-WIRED rule fires in
>= 95% of replicates, in the right direction, for each fauna; and the half-split no-install false-positive
rate is <= 10%.  The line "CONTROL n=N PASS|FAIL ..." carries the smallest f detected in >= 80% of
replicates at w = 1.0.  Liveness is REPORTED, not gated: a reflex on a sensor that reads 0 on flat ground
(a contact sensor never touched) is present in the wiring and silent in the bout, and the structural
readout counts it; "re-wired" means wiring acquired, not wiring shown to be used.
"""
import json
import math
import os
import random
import statistics
import sys
import zlib
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wiring  # noqa: E402

TCAL = 140
READ = 160
PROBE = 3
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
KINDS = ("holistic", "conventional")
FRACTIONS = (0.05, 0.1, 0.2, 0.3, 0.5, 1.0)
WEIGHTS = (1.0, 0.5)
REPS = int(os.environ.get("RBT101_REPS", "400"))
NEW_LINK = 0.5  # half the operator's typical weight, as rewire.py
LIVE = 0.01  # a change of 1% of an effector's output range
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}


# ------------------------------------------------------------------ extract (reads bulk)

def lineage(run):
    last, parents = {}, {}
    with open(os.path.join(run, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            k = (r["population"], r["name"])
            last[k] = (r["generation"] - r["age"], r["generation"])
            parents[k] = list(r["parents"])
    return last, parents


def alive_at(last, kind, s):
    return {n for (k, n), (b, l) in last.items() if k == kind and b <= s <= l}


def anc0(parents, kind, name, c0):
    stack, seen, out = [name], set(), set()
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        if n in c0:
            out.add(n)
            continue
        stack.extend(parents.get((kind, n), []))
    return out


def reflex_pair(ph, kind, name):
    """The (posture sensor, live effector) pair this individual's reflex is installed on; None if it has none."""
    from rabbitstew.analysis import _live_effector_units
    sens = [i for i, ui in enumerate(ph.units) if ui.unit.kind == "sensor" and ui.unit.source in wiring.POSTURE]
    eff = list(_live_effector_units(ph))
    if not sens or not eff:
        return None
    rng = np.random.default_rng(zlib.crc32(f"RBT-101 reflex {kind}/{name}".encode()))
    return int(sens[rng.integers(len(sens))]), int(eff[rng.integers(len(eff))])


def install(ph, pair, w):
    return replace(ph, links=list(ph.links) + [(pair[0], pair[1], w)])


def probe_response(g, cfg, pair, w, seed, horizon=8, every=10):
    """Mean over probe ticks of the peak (over `horizon`) mean |d effector output| when the posture sensors
    are zeroed, trajectory frozen (RBT-66's probe, on every driven degree of freedom of any body)."""
    from rabbitstew.simulation import Simulation, spawn_layout
    c = replace(cfg, random_start=True, world=replace(cfg.world, terrain="flat"))
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    b = sim.brains[0]
    if pair is not None and w:
        b.W[pair[1], pair[0]] += w
    keys = sorted(b.effectors)
    post = [j for j, s in enumerate(b.sensors) if s.source in wiring.POSTURE]
    out = []
    for tick in range(int(round(c.duration / c.control_dt))):
        sim.step()
        if tick % every or not post or not keys:
            continue
        sens = sim.sensor_values(0, sim.contact_bodies())
        keep = (b.activation.copy(), b._prev_input.copy())
        tr = []
        for kill in (False, True):
            b.activation, b._prev_input = keep[0].copy(), keep[1].copy()
            s = sens.copy()
            if kill:
                s[post] = 0.0
            row = []
            for _ in range(horizon):
                b.step(s)
                row.append(np.array([b.effector_output(*k) for k in keys]))
            tr.append(row)
        b.activation, b._prev_input = keep
        out.append(max(float(np.mean(np.abs(x - y))) for x, y in zip(*tr)))
    return float(np.mean(out)) if out else 0.0


def extract(run, seed, tcal=TCAL):
    from rabbitstew.genotype import Genotype
    from rabbitstew.synthesis import synthesize
    cfg = wiring.sim_config(run)
    last, parents = lineage(run)
    have = max(l for _, l in last.values())
    if have < tcal + READ:
        raise SystemExit(f"{run} reaches season {have}; the control needs {tcal + READ}")
    print(f"# RBT-101 positive-control table, seed {seed}: C0 alive at {tcal - 1}, P alive at {tcal + READ}; "
          f"from {run} (lineage and genomes only)")
    print("\t".join(("role", "population", "name", "g1", "g2", "installable", "g1_w1", "g2_w1", "g1_w05", "g2_w05",
                     "probe_off", "probe_on", "c0_ancestors")))
    for kind in KINDS:
        c0 = alive_at(last, kind, tcal - 1)
        P = alive_at(last, kind, tcal + READ)
        probed = 0
        for role, group in (("C0", sorted(c0)), ("P", sorted(P))):
            for name in group:
                g = Genotype.load(os.path.join(run, kind, "genomes", f"{name}.json"))
                ph = synthesize(g, cfg.synthesis)
                d = wiring.digest(ph)
                row = [role, kind, name, f"{d['g1']:.6f}", f"{d['g2']:.6f}"]
                if role == "C0":
                    print("\t".join(row + ["-"] * 7 + ["-"]))
                    continue
                pair = reflex_pair(ph, kind, name)
                if pair is None:
                    row += ["0"] + ["-"] * 4
                else:
                    d1, d05 = wiring.digest(install(ph, pair, 1.0)), wiring.digest(install(ph, pair, 0.5))
                    row += ["1", f"{d1['g1']:.6f}", f"{d1['g2']:.6f}", f"{d05['g1']:.6f}", f"{d05['g2']:.6f}"]
                if pair is not None and probed < PROBE:
                    ps = zlib.crc32(f"{seed}/{name}".encode()) % 100000
                    row += [f"{probe_response(g, cfg, pair, 0.0, ps):.6f}", f"{probe_response(g, cfg, pair, 1.0, ps):.6f}"]
                    probed += 1
                else:
                    row += ["-", "-"]
                row.append(",".join(sorted(anc0(parents, kind, name, c0))) or "-")
                print("\t".join(row))


# ------------------------------------------------------------------ analyse (committed text only)

def load_tables(d):
    out = {}
    for seed in SEEDS:
        p = os.path.join(d, f"{seed}.txt")
        if not os.path.exists(p):
            continue
        rows = [l.rstrip("\n").split("\t") for l in open(p) if not l.startswith("#")]
        head, rows = rows[0], rows[1:]
        T = {}
        for r in rows:
            r = dict(zip(head, r))
            k = r["population"]
            T.setdefault(k, {"C0": {}, "P": []})
            if r["role"] == "C0":
                T[k]["C0"][r["name"]] = r
            else:
                T[k]["P"].append(r)
        out[seed] = T
    return out


STAT = os.environ.get("RBT101_STAT", "new")
SIGN_GUARD = os.environ.get("RBT101_SIGN_GUARD", "0") == "1"


def val(r, installed, w, stat=None):
    """An individual's statistic: g1 or g2 (wiring.py), or lg2 = log(1 + g2); with the reflex if installed."""
    stat = stat or STAT
    base = "g1" if stat == "g1" else "g2"
    x = float(r[f"{base}_{w}"]) if r["name"] in installed else float(r[base])
    return math.log1p(x) if stat == "lg2" else x


def seed_stats(t, kind, installed=frozenset(), w="w1", subset=None):
    """(W-acq, W-sort) on STAT for one seed's fauna, with the reflex installed on the P names in `installed`."""
    c0 = t[kind]["C0"]
    P = [r for r in t[kind]["P"] if subset is None or r["name"] in subset]
    if not P or not c0:
        return None
    if STAT == "new":
        # the fraction of P carrying a new direct posture link: g1 at least NEW_LINK above every C0 ancestor's g1;
        # W-sort's analogue is the change in the fraction carrying any direct posture link (g1 > 0)
        c0g1 = {n: float(r["g1"]) for n, r in c0.items()}
        g1 = [val(r, installed, w, "g1") for r in P]
        hits = []
        for r, x in zip(P, g1):
            anc = [c0g1[a] for a in r["c0_ancestors"].split(",") if a in c0g1] if r["c0_ancestors"] != "-" else []
            if anc:
                hits.append(1.0 if x >= max(anc) + NEW_LINK else 0.0)
        wired = statistics.fmean(1.0 if x > 0 else 0.0 for x in g1) - statistics.fmean(1.0 if x > 0 else 0.0 for x in c0g1.values())
        return (statistics.fmean(hits) if hits else float("nan"), wired)
    g = [val(r, installed, w) for r in P]
    acq = []
    c0v = {n: val(r, (), "w1") for n, r in c0.items()}
    for r, x in zip(P, g):
        anc = [c0v[a] for a in r["c0_ancestors"].split(",") if a in c0v] if r["c0_ancestors"] != "-" else []
        if anc:
            acq.append(x - statistics.fmean(anc))
    return (statistics.fmean(acq) if acq else float("nan"), statistics.fmean(g) - statistics.fmean(c0v.values()))


def fires(vals, need):
    n = len(vals)
    m, sd = statistics.fmean(vals), statistics.stdev(vals)
    hw = T975[n - 1] * sd / math.sqrt(n)
    pos = sum(v > 0 for v in vals)
    neg = sum(v < 0 for v in vals)
    if not SIGN_GUARD:
        need = 0
    return (1 if (m - hw > 0 and pos >= need) else -1 if (m + hw < 0 and neg >= need) else 0), m, hw


def derange(xs, rnd):
    while True:
        p = xs[:]
        rnd.shuffle(p)
        if all(a != b for a, b in zip(xs, p)):
            return p


def analyse(d):
    tabs = load_tables(d)
    seeds = [s for s in SEEDS if s in tabs]
    print(f"# RBT-101 positive control: analysis of runs/RBT-101/control/SEED.txt ({len(seeds)} seeds: {seeds})")
    print(f"# C0 alive at {TCAL - 1}, P alive at {TCAL + READ}; reflex = one direct posture-sensor -> live-effector link; "
          f"{REPS} replicates per cell; statistic g2 (wiring.py)")
    print()
    for kind in KINDS:
        nP = [len(tabs[s][kind]["P"]) for s in seeds]
        inst = [sum(r["installable"] == "1" for r in tabs[s][kind]["P"]) for s in seeds]
        gain1 = [float(r["g2_w1"]) - float(r["g2"]) for s in seeds for r in tabs[s][kind]["P"] if r["installable"] == "1"]
        gain05 = [float(r["g2_w05"]) - float(r["g2"]) for s in seeds for r in tabs[s][kind]["P"] if r["installable"] == "1"]
        acq0 = [seed_stats(tabs[s], kind)[0] for s in seeds]
        sort0 = [seed_stats(tabs[s], kind)[1] for s in seeds]
        g2P = [float(r["g2"]) for s in seeds for r in tabs[s][kind]["P"]]
        print(f"== {kind}: |P| per seed {nP}; installable {inst} ({sum(inst)}/{sum(nP)})")
        print(f"   g2 over P: mean {statistics.fmean(g2P):.4f}, median {statistics.median(g2P):.4f}; "
              f"installed reflex raises g2 by median {statistics.median(gain1):.4f} at w=1.0, {statistics.median(gain05):.4f} at w=0.5")
        print(f"   no install, per seed W-acq(g2): mean {statistics.fmean(acq0):+.4f} sd {statistics.stdev(acq0):.4f}; "
              f"W-sort(g2): mean {statistics.fmean(sort0):+.4f} sd {statistics.stdev(sort0):.4f}  (the natural drift over {READ + 1} seasons)")
        probes = [(float(r["probe_off"]), float(r["probe_on"])) for s in seeds for r in tabs[s][kind]["P"] if r["probe_off"] != "-"]
        live = sum(abs(on - off) >= LIVE for off, on in probes)
        print(f"   liveness (frozen probe, flat terrain): the reflex moves the posture response by >= {LIVE} on {live}/{len(probes)} probed bodies; "
              f"median without {statistics.median([p[0] for p in probes]):.4f}, with {statistics.median([p[1] for p in probes]):.4f}")
        tabs_k = kind
        results = {}
        for n in range(len(seeds), 5, -1):
            need = math.ceil(0.8 * n)
            rnd = random.Random(zlib.crc32(f"RBT-101 control {kind} {n}".encode()))
            row = []
            for w in ("w1", "w05"):
                for f in FRACTIONS:
                    hit = 0
                    for _ in range(REPS):
                        draw = rnd.sample(seeds, n)
                        b, c = derange(draw, rnd), derange(draw, rnd)
                        installed = {}
                        for s in draw:
                            names = [r["name"] for r in tabs[s][tabs_k]["P"] if r["installable"] == "1"]
                            installed[s] = frozenset(rnd.sample(names, int(round(f * len(names)))))
                        sh = {s: seed_stats(tabs[s], kind, installed[s], w) for s in draw}
                        nb = {s: seed_stats(tabs[s], kind) for s in draw}
                        sb, _, _ = fires([sh[s][0] - nb[x][0] for s, x in zip(draw, b)], need)
                        sc, _, _ = fires([sh[s][0] - nb[x][0] for s, x in zip(draw, c)], need)
                        hit += sb == 1 and sc == 1
                    row.append((w, f, hit / REPS))
            # the false-positive check: half-split of each seed's P, no install
            fp = 0
            for _ in range(REPS):
                draw = rnd.sample(seeds, n)
                va, vb = [], []
                for s in draw:
                    names = [r["name"] for r in tabs[s][kind]["P"]]
                    rnd.shuffle(names)
                    h = len(names) // 2
                    A, B = set(names[:h]), set(names[h:])
                    xa, xb = seed_stats(tabs[s], kind, subset=A), seed_stats(tabs[s], kind, subset=B)
                    va.append(xa[0] - xb[0])
                    names2 = names[:]
                    rnd.shuffle(names2)
                    C = set(names2[:h])
                    vb.append(xa[0] - seed_stats(tabs[s], kind, subset=C)[0])
                s1, _, _ = fires(va, need)
                s2, _, _ = fires(vb, need)
                fp += s1 != 0 and s1 == s2
            full = dict(((w, f), r) for w, f, r in row)[("w1", 1.0)]
            smallest = next((f for w, f, r in row if w == "w1" and r >= 0.8), None)
            ok = full >= 0.95 and fp / REPS <= 0.10
            results[n] = (ok, smallest, full, fp / REPS)
            print(f"   n={n:2d}  detection rate of RE-WIRED by installed fraction f of P:")
            for w in ("w1", "w05"):
                print(f"          w={'1.0' if w == 'w1' else '0.5'}: " + "  ".join(f"f={f:<4} {r:.3f}" for ww, f, r in row if ww == w))
            print(f"          no-install false-positive rate (half-split model): {fp}/{REPS} = {fp / REPS:.3f}")
        print()
        tabs[f"_{kind}"] = results
    for n in range(len(seeds), 5, -1):
        parts = []
        ok_all = True
        for kind in KINDS:
            ok, smallest, full, fp = tabs[f"_{kind}"][n]
            ok_all &= ok
            parts.append(f"{kind}: f=1.0 detected {full:.3f}, false-positive {fp:.3f}, smallest f detected >= 0.8: {smallest}")
        print(f"CONTROL n={n} {'PASS' if ok_all else 'FAIL'} " + "; ".join(parts))


if __name__ == "__main__":
    if sys.argv[1] == "extract":
        extract(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else TCAL)
    else:
        analyse(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "control"))
