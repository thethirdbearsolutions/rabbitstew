"""RBT-126: breeding-rule options in the bodiless replica, with their depth cost.

Extends runs/RBT-121/adversary/adv_demography.py (the adversary's independent replica of Ecology.step's demography,
ecology.py:505-548: living cost, age, death by starvation or age, eligible = energy >= threshold, crossover mate
choice at rate 0.3, birth cost 1 paid by the breeder, child at energy 1 and age 0).  Gain = Poisson(g) - 0.1 work, as
the adversary and audit C.  The committed economy: 60 slots, living cost 0.25, threshold 3, birth cost 1, initial
energy 3, max age 60, founders' ages staggered U[0, 60).

Only the breeders' ORDER (and, for the leak rules, the stored energy) differs between rules:

  shuffle        committed: eligible shuffled, breed in that order while slots are free (ecology.py:524-529)
  energy         shuffle, then a stable sort by descending energy (audit C's --breed-order energy)
  tickets        eligible drawn without replacement with probability proportional to energy (audit C's tickets)
  leak:L         audit C's leak: stored energy decays by L each season (e <- e(1-L) + gain - cost), order shuffled.
                 Raises the bar to breed: a steady net n settles at n/L, so n >= 3L is needed to ever be eligible.
  life           rank the eligible by lifetime mean gain per season (RBT-126 fixes)
  mavg:K         rank by a moving mean of gain over about K seasons
  lcb:z          rank by the lifetime mean minus z standard errors (variance-penalised)
  leakx:L        leak only ABOVE the threshold (e <- e - L max(0, e - thr) before this season's gain), then energy
                 order.  Hoards are capped near thr + n/L, so the order ranks recent income, not age x income; below
                 the threshold nothing changes, so viability is the committed rule's.

Measures (``--mode``):
  depth      neutral population (every member the same g0), seasons 200-400: distinct parents, mean age at
             breeding, generations per season (mean pedigree depth of the living, change / 200 seasons), births
             per season, and the share of the living eligible;
  invasion   the adversary's design: 6 mutants with income x mult among 60, 400 seasons: mean share and fixation;
  retention  RBT-80's numbers: all 60 founders carriers (gross gc = 1.05), per-birth erosion u = 0.06 to a
             non-carrier (gn), 300 seasons; carriage at season 300 under each rule and with no selection (the
             drift arm's economy: cost 0, threshold 0, birth cost 0, no starvation);
  screen     every rule against the planted negatives (DRAWS) at g0 1.0, 1.3 and 3.0 (--rules to choose);
  small      as invasion with a neutral (x1.00) and a x1.10 mutant, at g0 0.5, 1.3 and 3.0;
  lineage    write a lineage.jsonl + config.json in the ecology's format for one cell, for scripts/regime.py's
             calibration and tests.

python3 runs/RBT-126/breeding_rules.py depth|invasion|retention [reps] [--workers N]
python3 runs/RBT-126/breeding_rules.py lineage OUT_DIR --g0 0.8 [--rule shuffle] [--seasons 600] [--seed 1]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

THR, BCOST, AGE, INIT, XRATE, CAP, COST, WORK = 3.0, 1.0, 60, 3.0, 0.3, 60, 0.25, 0.1
RULES = ("shuffle", "energy", "tickets", "leak:0.05", "leak:0.2", "leakx:0.1", "leakx:0.3")
NOSEL = ("no-sel", "no-sel-nogate")  # the drift arm's economy, with the committed gate and without it (item 4)
G0S = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.3, 2.0, 3.0)


def income_score(p, rule):
    """The ranking score of the income-based rules (RBT-126 fixes, adversary M3), from a member's income record:
    ``life`` the lifetime mean gain per season; ``mavg:K`` a moving mean over about K seasons (the running mean for
    the first K, then exponential with weight 1/K); ``lcb:z`` the lifetime mean minus z standard errors, a
    variance-penalised score (fewer than 2 seasons: ranked last)."""
    n = p[6]
    if rule == "life":
        return p[5] / max(1, n)
    if rule.startswith("mavg"):
        return p[10]
    if rule.startswith("lcb"):
        if n < 2:
            return -1e9
        z = float(rule.split(":")[1])
        m = p[5] / n
        var = max(0.0, (p[9] - n * m * m) / (n - 1))
        return m - z * (var / n) ** 0.5
    raise ValueError(rule)


def order(rng, elig, rule):
    """The breeders' order this season under ``rule`` (elig: list of members [type, energy, age, id, depth, ...])."""
    rng.shuffle(elig)
    if rule == "energy" or rule.startswith("leakx"):
        elig.sort(key=lambda p: -p[1])  # stable: ties keep the shuffle
    elif rule == "life" or rule.startswith(("mavg", "lcb")):
        elig.sort(key=lambda p: -income_score(p, rule))
    elif rule == "tickets" and len(elig) > 1:
        w = np.array([max(p[1], 1e-9) for p in elig])
        idx = rng.choice(len(elig), size=len(elig), replace=False, p=w / w.sum())
        elig = [elig[i] for i in idx]
    return elig


def run(rng, *, g_of, n_mut, seasons, rule="shuffle", cost=COST, thr=THR, bcost=BCOST, starvation=True, u=0.0,
        track_from=None, stop_on_fix=True, log=None, gate=True, mutant_draw=None):
    """One population. Member: [type, energy, age, id, depth, score_sum, evals, parent, last gain, sum of squared
    gains, moving mean]. Returns a dict of readouts.

    ``mutant_draw(rng, mean)`` replaces the mutants' (type 1) Poisson gross income with another draw of the same
    ``g_of`` mean: the planted negatives of the RBT-126 fixes (``DRAWS``).

    ``gate=False`` drops the eligibility test entirely (every living, evaluated member may breed): RBT-126 item 4's
    proposed drift-arm fix, used only with the no-selection economy."""
    leak = float(rule.split(":")[1]) if rule.startswith("leak") else 0.0
    K = float(rule.split(":")[1]) if rule.startswith("mavg") else 0.0
    pop = [[1 if i < n_mut else 0, INIT, int(rng.integers(0, AGE)), i, 0, 0.0, 0, None, 0.0, 0.0, 0.0] for i in range(CAP)]
    nid = CAP
    parents, parent_ages, births = set(), [], 0
    d0 = None
    elig_counts = []
    for s in range(seasons):
        for p in pop:
            g = (mutant_draw(rng, g_of(1)) if (mutant_draw is not None and p[0] == 1) else rng.poisson(g_of(p[0]))) - WORK
            if rule.startswith("leak:"):
                p[1] = p[1] * (1 - leak)
            elif rule.startswith("leakx") and p[1] > thr:
                p[1] -= leak * (p[1] - thr)
            p[1] += g - cost
            p[2] += 1
            p[5] += g
            p[6] += 1
            p[8] = g
            p[9] += g * g
            p[10] += (g - p[10]) / min(p[6], K) if K else 0.0
        pop = [p for p in pop if (p[1] > 0 or not starvation) and p[2] < AGE]
        elig = [p for p in pop if (p[1] >= thr or not gate)]
        tracking = track_from is not None and s >= track_from
        if tracking:
            elig_counts.append(len(elig) / max(1, len(pop)))
            if d0 is None:
                d0 = np.mean([p[4] for p in pop]) if pop else 0.0
        elig = order(rng, elig, rule)
        mates = list(elig)
        born = []
        for p in elig:
            if len(pop) + len(born) >= CAP:
                break
            t = p[0]
            if XRATE > 0 and len(mates) > 1 and rng.random() < XRATE:
                o = mates[int(rng.integers(0, len(mates)))]
                if o is not p and rng.random() < 0.5:
                    t = o[0]
            if t == 1 and u > 0 and rng.random() < u:
                t = 0
            p[1] -= bcost
            born.append([t, bcost, 0, nid, p[4] + 1, 0.0, 0, p[3], 0.0, 0.0, 0.0])
            nid += 1
            if tracking:
                parents.add(p[3])
                parent_ages.append(p[2])
                births += 1
        pop.extend(born)
        if log is not None:
            for p in pop:
                log.append({"generation": s, "population": "replica", "name": f"r{p[3]}",
                            "parents": [f"r{p[7]}"] if p[7] is not None else [],
                            "fitness": round(p[5] / max(1, p[6]), 4), "energy": round(p[1], 3), "age": p[2],
                            "evals": p[6], "last_score": round(float(p[8]), 4), "type": p[0]})
        if not pop:
            break
        if stop_on_fix and n_mut and not u and track_from is None:
            f = sum(p[0] for p in pop) / len(pop)
            if f in (0.0, 1.0):
                break
    out = {"share": sum(p[0] for p in pop) / max(1, len(pop)), "alive": len(pop)}
    if track_from is not None:
        span = max(1, seasons - track_from)
        d1 = np.mean([p[4] for p in pop]) if pop else float("nan")
        out.update(parents=len(parents), parent_age=float(np.mean(parent_ages)) if parent_ages else float("nan"),
                   gens_per_season=float((d1 - d0) / span) if d0 is not None else float("nan"),
                   births_per_season=births / span, elig_share=float(np.mean(elig_counts)) if elig_counts else 0.0)
    return out


# -- modes ----------------------------------------------------------------- #

def _depth_cell(args):
    rule, g0, reps, seed = args
    rng = np.random.default_rng(seed)
    rs = [run(rng, g_of=lambda t: g0, n_mut=0, seasons=400, rule=rule, track_from=200) for _ in range(reps)]
    keys = ("parents", "parent_age", "gens_per_season", "births_per_season", "elig_share", "alive")
    return rule, g0, {k: (float(np.nanmean([r[k] for r in rs])), float(np.nanstd([r[k] for r in rs]) / np.sqrt(reps)))
                      for k in keys}


def _inv_cell(args):
    rule, g0, mult, reps, seed = args
    rng = np.random.default_rng(seed)
    fr = np.array([run(rng, g_of=lambda t: g0 * (mult if t else 1.0), n_mut=6, seasons=400, rule=rule)["share"]
                   for _ in range(reps)])
    return rule, g0, mult, float(fr.mean()), float(np.mean(fr == 1.0)), float(fr.std() / np.sqrt(reps))


def _ret_cell(args):
    rule, gn, reps, seed = args
    rng = np.random.default_rng(seed)
    if rule in ("no-sel", "no-sel-nogate"):
        kw = dict(cost=0.0, thr=0.0, bcost=0.0, starvation=False, gate=(rule == "no-sel"))
    else:
        kw = dict(rule=rule)
    fr = np.array([run(rng, g_of=lambda t: 1.05 if t else gn, n_mut=CAP, seasons=300, u=0.06, **kw)["share"]
                   for _ in range(reps)])
    return rule, gn, float(fr.mean()), float(fr.std() / np.sqrt(reps))


def depth(reps, workers):
    print(f"# DEPTH: neutral population (all members gross g0), 60 slots, cost {COST}, seasons 200-400; reps = {reps}")
    print("# rule | g0 | distinct parents (200 seasons) | mean age at breeding | generations / season | births / season | eligible share of living | alive")
    cells = [(r, g, reps, 1000 + i) for i, (r, g) in enumerate((r, g) for r in RULES for g in G0S)]
    with Pool(workers) as pool:
        for rule, g0, m in pool.imap(_depth_cell, cells):
            print(f"{rule:10s} g0 {g0:4.2f} | parents {m['parents'][0]:6.1f}±{m['parents'][1]:.1f} | age {m['parent_age'][0]:5.1f}±{m['parent_age'][1]:.1f} "
                  f"| gen/season {m['gens_per_season'][0]:.4f}±{m['gens_per_season'][1]:.4f} | births {m['births_per_season'][0]:5.2f} "
                  f"| eligible {m['elig_share'][0]:.2f} | alive {m['alive'][0]:5.1f}", flush=True)


def invasion(reps, workers):
    print(f"# INVASION (adversary's design): 6 mutants with gross income x mult among 60; share / fixation at 400 seasons; reps = {reps}")
    print("# rule | g0 | mult | mean share (±SE) | fixation rate; neutral share = 0.10")
    cells = [(r, g, m, reps, 2000 + i) for i, (r, g, m) in enumerate((r, g, m) for r in RULES for g in G0S for m in (1.25, 2.0))]
    with Pool(workers) as pool:
        for rule, g0, mult, share, fix, se in pool.imap(_inv_cell, cells):
            print(f"{rule:10s} g0 {g0:4.2f} x{mult:4.2f} | share {share:.3f}±{se:.3f} | fix {fix:.2f}", flush=True)


def _ff(rng, m):
    return 2.0 * m if rng.random() < 0.5 else 0.0


def _pb(rng, m):
    return float(rng.poisson(2.0 * m)) if rng.random() < 0.5 else 0.0


#: the planted negatives (adversary #417 §3): mutant income draws with a given mean
DRAWS = {"x1.00": (1.0, None), "x1.25": (1.25, None), "x1.10": (1.10, None),
         "ff1.0": (1.0, _ff), "pb1.0": (1.0, _pb), "ff0.9": (0.9, _ff), "pb0.9": (0.9, _pb)}
SCREEN_RULES = ("shuffle", "energy", "tickets", "leakx:0.3", "leakx:1.0", "life", "mavg:10", "mavg:30", "lcb:1", "lcb:2")


def _screen_cell(args):
    rule, g0, kind, reps, seed = args
    mult, draw = DRAWS[kind]
    rng = np.random.default_rng(seed)
    fr = np.array([run(rng, g_of=lambda t: g0 * (mult if t else 1.0), n_mut=6, seasons=400, rule=rule, mutant_draw=draw)["share"]
                   for _ in range(reps)])
    return rule, g0, kind, float(fr.mean()), float(fr.std() / np.sqrt(reps)), float(np.mean(fr == 1.0))


def screen(reps, workers):
    print(f"# SCREEN (RBT-126 fixes; adversary #417 M3 / R10): 6 mutants among 60, 400 seasons; reps = {reps}; neutral share 0.10")
    print("# mutants: x1.00 neutral marker; x1.25 / x1.10 Poisson mean gains; ff1.0 same mean, feast or famine (2m w.p. 0.5, else 0);")
    print("#          pb1.0 same mean, Poisson(2m) w.p. 0.5 else 0; ff0.9 / pb0.9 the same at 0.9 x the mean (a mean LOSS with a variance gain)")
    print("# rule | g0 | mutant | mean share (±SE) | fixation")
    cells = [(r, g, k, reps, 6000 + i) for i, (r, g, k) in enumerate(
        (r, g, k) for r in RULES for g in (1.0, 1.3, 3.0) for k in DRAWS)]
    with Pool(workers) as pool:
        for rule, g0, kind, share, se, fix in pool.imap(_screen_cell, cells):
            print(f"{rule:10s} g0 {g0:4.2f} {kind:6s} | share {share:.3f}±{se:.3f} | fix {fix:.2f}", flush=True)


def small(reps, workers):
    print(f"# SMALL EFFECTS: as INVASION, with a neutral (x1.00) and a x1.10 mutant; reps = {reps}")
    print("# rule | g0 | mult | mean share (±SE) | fixation rate; neutral share = 0.10")
    cells = [(r, g, m, reps, 4000 + i) for i, (r, g, m) in enumerate((r, g, m) for r in RULES for g in (0.5, 1.3, 3.0) for m in (1.0, 1.1))]
    with Pool(workers) as pool:
        for rule, g0, mult, share, fix, se in pool.imap(_inv_cell, cells):
            print(f"{rule:10s} g0 {g0:4.2f} x{mult:4.2f} | share {share:.3f}±{se:.3f} | fix {fix:.2f}", flush=True)


def retention(reps, workers):
    print(f"# RETENTION at RBT-80's numbers: 60 founders all carriers (gross 1.05), erosion u 0.06 per birth to a non-carrier (gross gn); carriage at season 300; reps = {reps}")
    print("# gn from RBT-80-within-arm.txt: seed A 0.08, B 0.64, C 0.47 (plateau non-carrier means); 0.84 and 1.05 (neutral) added")
    print("# rule | gn | carriage (±SE)")
    cells = [(r, gn, reps, 3000 + i) for i, (r, gn) in enumerate((r, gn) for r in RULES + NOSEL for gn in (0.08, 0.47, 0.64, 0.84, 1.05))]
    with Pool(workers) as pool:
        for rule, gn, m, se in pool.imap(_ret_cell, cells):
            print(f"{rule:10s} gn {gn:4.2f} | carriage {m:.3f}±{se:.3f}", flush=True)


def write_lineage(out_dir, g0, rule="shuffle", seasons=600, seed=1, mult=1.0, n_mut=0):
    """A replica run in the ecology's lineage.jsonl format (plus the config.json regime.py reads)."""
    os.makedirs(out_dir, exist_ok=True)
    log = []
    run(np.random.default_rng(seed), g_of=lambda t: g0 * (mult if t else 1.0), n_mut=n_mut, seasons=seasons,
        rule=rule, log=log, stop_on_fix=False)
    with open(os.path.join(out_dir, "lineage.jsonl"), "w") as f:
        for r in log:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(out_dir, "config.json"), "w") as f:
        json.dump({"ecology": {"living_cost": COST, "birth_threshold": THR, "birth_cost": BCOST, "max_age": AGE,
                               "initial_energy": INIT, "starvation": True, "capacity": CAP}}, f)
    return log


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("depth", "invasion", "retention", "lineage", "small", "screen"))
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--rules", help="comma-separated subset or extension of RULES, e.g. leakx:0.6,leakx:1.0")
    ap.add_argument("--g0", type=float, default=0.8)
    ap.add_argument("--rule", default="shuffle")
    ap.add_argument("--seasons", type=int, default=600)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    if a.rules:
        RULES = tuple(a.rules.split(","))
    if a.mode == "lineage":
        write_lineage(a.arg, a.g0, a.rule, a.seasons, a.seed)
    else:
        reps = int(a.arg) if a.arg else 100
        {"depth": depth, "invasion": invasion, "retention": retention, "small": small, "screen": screen}[a.mode](reps, a.workers)
