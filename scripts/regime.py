"""The ecology's regime, read from a run's lineage (RBT-126; RBT-121 SYNTHESIS R5 with the synthesis check's M2).

Read-only on ``rabbitstew/``: this reads a run directory's ``lineage.jsonl`` (one row per living member per season,
written after births, ``ecology.py:_log_lineage``) and its ``config.json`` (the ecology's living cost, birth threshold,
birth cost and max age), and prints, per fauna and per window of seasons:

  saturation   mean net income (lifetime mean gain - living cost) of the complete lives born in the window that
               *reached breeding*, i.e. were ever eligible (energy >= birth_threshold before that season's births),
               divided by the living cost.  RBT-121 ADVERSARY 1d: the committed lottery is saturated once this is
               about >= 2 (replica: resident gross g0 >= 0.8 at living cost 0.25; see runs/RBT-126/calibration.txt).
  saturation (window-local)
               the same ratio from the window's own seasons only: the mean season gain (``last_score``) of the
               members eligible that season, minus the living cost, over the living cost.  The per-life figure
               above follows each life born in the window to its death, past the window's end; this one does not,
               so it is the one to read for a window next to an event (a shift at T changes the incomes of lives
               born before T).  REGIME.md's band is read from it.
  viability    mean net income per birth: every complete life born in the window, solvent or not, / living cost.
  quintiles    offspring by lifetime-income quintile of the complete lives born in the window (income = the life's
               lifetime mean gain, the lineage's ``fitness``; children = rows whose ``parents[0]`` names it, i.e. the
               breeder that paid the birth cost).
  deaths       the share of deaths *in* the window by age (last row at age >= max_age - 1), by starvation and by cull.
  breeders     the mean count per season of eligible breeders (evaluated members with energy >= threshold before
               that season's births; the lineage stores energy after births, so a parent's pre-birth energy is its
               row's energy + birth_cost x its children that season).
  energy       the mean over the window's seasons of the median energy (after births) of the evaluated living.
  depth        distinct parents, mean parent age at breeding, and generations per season (the change in the mean
               pedigree depth of the living across the window, / its length; founders are depth 0).
  living       the survivor-weighted income, the mean lifetime score of the living averaged over the window's
               seasons (what seasons.txt calls mean_lifetime_score), printed beside the per-birth figure so a reader
               can see which is which (R5).

"Complete lives" are the children born inside the window (first row at age 0, evals 0) that died before the run's
last season; lives still alive at the end are censored and counted.  Founders (born before season 0) are excluded
from the per-life figures but counted in the per-season ones.

A run directory with only ``lineage-last.txt`` (each member's last row: generation, age, evals, fitness, parents)
gets the per-life figures except eligibility (so "saturation" there is over lives that lived >= --min-life seasons,
and says so), and no per-season ones.

    python3 scripts/regime.py RUN_DIR [RUN_DIR ...] [--windows 0-49,50-149,...] [--json OUT.json] [--quiet]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

import numpy as np

DEFAULT_WINDOWS = ((0, 49), (50, 149), (150, 299), (300, 449), (450, 599))
ECO_DEFAULTS = {"living_cost": 0.05, "birth_threshold": 3.0, "birth_cost": 1.0, "max_age": 60, "starvation": True}


def load_eco(run_dir: str) -> dict:
    """The economy's parameters from config.json (EcologyConfig defaults where absent)."""
    eco = dict(ECO_DEFAULTS)
    p = os.path.join(run_dir, "config.json")
    if os.path.exists(p):
        with open(p) as f:
            cfg = json.load(f)
        e = cfg.get("ecology") or {}
        for k in eco:
            if e.get(k) is not None:
                eco[k] = e[k]
    if eco["living_cost"] == "relative":
        raise SystemExit(f"{run_dir}: living_cost 'relative' has no fixed cost to divide by")
    eco["living_cost"] = float(eco["living_cost"])
    return eco


class Life:
    __slots__ = ("born", "first_age", "last_gen", "last_age", "evals", "fitness", "parent", "culled", "elig", "kids",
                 "depth")

    def __init__(self, gen, age, evals, parent, depth):
        self.born = gen - age if not (age == 0 and evals == 0) else gen
        self.first_age, self.last_gen, self.last_age, self.evals = age, gen, age, evals
        self.fitness, self.parent, self.culled, self.elig, self.kids, self.depth = 0.0, parent, False, 0, 0, depth


def read_lineage(run_dir: str):
    """Parse lineage.jsonl into per-fauna lives and per-season rows. Returns (pops, last_season, has_energy)."""
    full = os.path.join(run_dir, "lineage.jsonl")
    last_txt = os.path.join(run_dir, "lineage-last.txt")
    pops = collections.defaultdict(lambda: {"lives": {}, "seasons": collections.defaultdict(list),
                                            "births": collections.Counter(), "kid_at": collections.Counter(),
                                            "parent_ages": collections.defaultdict(list)})
    last = -1
    if os.path.exists(full):
        with open(full) as f:
            for line in f:
                r = json.loads(line)
                P = pops[r["population"]]
                g, name, age, ev = r["generation"], r["name"], r["age"], r["evals"]
                last = max(last, g)
                parents = r.get("parents") or []
                life = P["lives"].get(name)
                if life is None:
                    par = parents[0] if parents else None
                    d = P["lives"][par].depth + 1 if par in P["lives"] else 0
                    life = P["lives"][name] = Life(g, age, ev, par, d)
                    if age == 0 and ev == 0 and par is not None:
                        P["births"][g] += 1
                        P["kid_at"][(g, par)] += 1
                        if par in P["lives"]:
                            P["lives"][par].kids += 1
                if r.get("death") == "cull":
                    life.culled = True
                    continue
                life.last_gen, life.last_age, life.evals, life.fitness = g, age, ev, float(r["fitness"])
                P["seasons"][g].append((name, float(r["energy"]), age, ev, float(r.get("last_score", 0.0))))
        return pops, last, True
    if os.path.exists(last_txt):
        with open(last_txt) as f:
            head = f.readline().rstrip("\n").split("\t")
            rows = [dict(zip(head, l.rstrip("\n").split("\t"))) for l in f if l.strip()]
        for r in rows:
            last = max(last, int(r["generation"]))
        # parents before children: sort by birth season
        for r in sorted(rows, key=lambda r: int(r["generation"]) - int(r["age"])):
            P = pops[r["population"]]
            g, age, ev = int(r["generation"]), int(r["age"]), int(r["evals"])
            par = r["parents"].split(",")[0] if r.get("parents") else None
            d = P["lives"][par].depth + 1 if par in P["lives"] else 0
            life = P["lives"][r["name"]] = Life(g, age, ev, par, d)
            # lineage-last rows are last rows: born = generation - age for everyone; a child's first eval is at born+1
            life.born = g - age
            life.fitness = float(r["fitness"])
            if par is not None:
                P["births"][life.born] += 1
        for P in pops.values():
            for life in P["lives"].values():
                if life.parent in P["lives"]:
                    P["lives"][life.parent].kids += 1
        return pops, last, False
    raise SystemExit(f"{run_dir}: no lineage.jsonl or lineage-last.txt")


def _eligibility(P, eco):
    """Per season: the pre-birth energies of the evaluated living; marks each life's eligible seasons."""
    thr, bc = eco["birth_threshold"], eco["birth_cost"]
    per = {}
    for g, rows in P["seasons"].items():
        n_elig, energies, elig_gain, all_gain = 0, [], [], []
        for name, e, age, ev, gain in rows:
            if ev == 0:
                continue  # a child written in its birth season, not yet evaluated
            k = P["kid_at"].get((g, name), 0)
            if k:
                P["parent_ages"][g].extend([age] * k)
            pre = e + bc * k
            energies.append(e)
            all_gain.append(gain)
            if pre >= thr:
                n_elig += 1
                P["lives"][name].elig += 1
                elig_gain.append(gain)
        depths = [P["lives"][name].depth for name, *_ in rows]
        per[g] = {"alive": sum(1 for r in rows if r[3] > 0), "elig": n_elig, "elig_gain": elig_gain, "all_gain": all_gain,
                  "median_energy": float(np.median(energies)) if energies else float("nan"),
                  "mean_depth": float(np.mean(depths)) if depths else float("nan")}
    return per


def _q(a, i, q):
    return (a >= q[i]) & ((a <= q[i + 1]) if i == 4 else (a < q[i + 1]))


def window_stats(P, per, eco, lo, hi, last, has_energy, min_life=10):
    cost, max_age = eco["living_cost"], eco["max_age"]
    lives = [l for l in P["lives"].values()
             if l.parent is not None and lo <= l.born <= hi and l.evals > 0]
    complete = [l for l in lives if l.last_gen < last or l.culled]
    out = {"window": [lo, hi], "births": int(sum(P["births"][s] for s in range(lo, hi + 1))),
           "complete_lives": len(complete), "censored_lives": len(lives) - len(complete)}
    if complete:
        inc = np.array([l.fitness for l in complete])
        net = inc - cost
        if has_energy:
            solvent = np.array([l.elig > 0 for l in complete])
            out["solvent_rule"] = "ever eligible (energy >= threshold before births)"
        else:
            solvent = np.array([l.evals >= min_life for l in complete])
            out["solvent_rule"] = f"lived >= {min_life} seasons (no energy in lineage-last.txt)"
        out["solvent_share"] = float(solvent.mean())
        out["saturation"] = float(net[solvent].mean() / cost) if solvent.any() and cost > 0 else None
        out["solvent_net"] = float(net[solvent].mean()) if solvent.any() else None
        out["viability"] = float(net.mean() / cost) if cost > 0 else None
        out["net_per_birth"] = float(net.mean())
        kids = np.array([l.kids for l in complete], dtype=float)
        life_len = np.array([l.evals for l in complete], dtype=float)
        aged = np.array([(not l.culled) and l.last_age >= max_age - 1 for l in complete])
        elig = np.array([l.elig for l in complete], dtype=float)
        q = np.quantile(inc, [0, .2, .4, .6, .8, 1])
        quint = []
        for i in range(5):
            m = _q(inc, i, q)
            if not m.any():
                quint.append(None)
                continue
            quint.append({"lo": float(q[i]), "hi": float(q[i + 1]), "n": int(m.sum()), "income": float(inc[m].mean()),
                          "net_over_cost": float(net[m].mean() / cost) if cost > 0 else None,
                          "lifespan": float(life_len[m].mean()), "died_of_age": float(aged[m].mean()),
                          "seasons_eligible": float(elig[m].mean()) if has_energy else None,
                          "children": float(kids[m].mean())})
        out["quintiles"] = quint
        out["children_per_life"] = float(kids.mean())
        out["corr_income_children"] = float(np.corrcoef(inc, kids)[0, 1]) if kids.std() > 0 and inc.std() > 0 else None
        top = [x for x in quint[3:] if x]
        out["q5_over_q4_children"] = (quint[4]["children"] / quint[3]["children"]
                                      if len(top) == 2 and quint[3]["children"] > 0 else None)
    # deaths in the window (death season = last row + 1)
    dead = [l for l in P["lives"].values() if l.last_gen < last and lo <= l.last_gen + 1 <= hi]
    n = len(dead)
    cull = sum(1 for l in dead if l.culled)
    age = sum(1 for l in dead if not l.culled and l.last_age >= max_age - 1)
    out["deaths"] = n
    out["death_share"] = {"age": age / n if n else None, "starvation": (n - age - cull) / n if n else None,
                          "cull": cull / n if n else None}
    if has_energy:
        ss = [s for s in range(lo, hi + 1) if s in per]
        if ss:
            out["alive"] = float(np.mean([per[s]["alive"] for s in ss]))
            out["eligible_breeders"] = float(np.mean([per[s]["elig"] for s in ss]))
            out["median_energy"] = float(np.nanmean([per[s]["median_energy"] for s in ss]))
            eg = [x for s in ss for x in per[s]["elig_gain"]]
            ag = [x for s in ss for x in per[s]["all_gain"]]
            out["saturation_local"] = float((np.mean(eg) - cost) / cost) if eg and cost > 0 else None
            out["season_net_living"] = float((np.mean(ag) - cost) / cost) if ag and cost > 0 else None
            out["living_income"] = float(np.mean([np.mean([P["lives"][nm].fitness for nm, e, a, ev, _ in P["seasons"][s] if ev > 0] or [np.nan]) for s in ss]))
            d0, d1 = per[ss[0]]["mean_depth"], per[ss[-1]]["mean_depth"]
            out["generations_per_season"] = float((d1 - d0) / (ss[-1] - ss[0])) if ss[-1] > ss[0] else None
            ages = [a for s in ss for a in P["parent_ages"].get(s, [])]
            out["parent_age"] = float(np.mean(ages)) if ages else None
            out["distinct_parents"] = len({par for (s, par) in P["kid_at"] if lo <= s <= hi})
            out["seasons"] = [ss[0], ss[-1]]
    return out


def regime(run_dir: str, windows=DEFAULT_WINDOWS, min_life=10) -> dict:
    eco = load_eco(run_dir)
    pops, last, has_energy = read_lineage(run_dir)
    res = {"run": run_dir, "last_season": last, "source": "lineage.jsonl" if has_energy else "lineage-last.txt",
           "economy": eco, "fauna": {}}
    for kind, P in sorted(pops.items()):
        per = _eligibility(P, eco) if has_energy else {}
        res["fauna"][kind] = [window_stats(P, per, eco, lo, min(hi, last), last, has_energy, min_life)
                              for lo, hi in windows if lo <= last]
    return res


def _f(x, fmt="{:.2f}"):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else fmt.format(x)


def render(res: dict, quintile_windows=None) -> str:
    """The tables; the per-quintile lines for every window, or only those in ``quintile_windows``."""
    eco = res["economy"]
    L = [f"## {res['run']}  ({res['source']}; last season {res['last_season']}; living cost {eco['living_cost']}, "
         f"threshold {eco['birth_threshold']}, birth cost {eco['birth_cost']}, max age {eco['max_age']}, "
         f"starvation {eco['starvation']})"]
    for kind, ws in res["fauna"].items():
        L.append(f"### {kind}")
        L.append("| window | births | complete / censored | saturation, window-local (eligible net ÷ cost) | saturation, per life (solvent net ÷ cost) | solvent share | viability (net per birth ÷ cost) "
                 "| living income (survivor-weighted) | deaths: age / starv / cull | eligible breeders / alive | median energy "
                 "| children Q1..Q5 | Q5÷Q4 | distinct parents | parent age | gen / season |")
        L.append("|" + "---|" * 16)
        for w in ws:
            ds = w["death_share"]
            q = w.get("quintiles") or []
            qs = " / ".join(_f(x["children"]) if x else "-" for x in q) if q else "-"
            L.append(f"| {w['window'][0]}-{w['window'][1]} | {w['births']} | {w['complete_lives']} / {w['censored_lives']} "
                     f"| {_f(w.get('saturation_local'))} | {_f(w.get('saturation'))} | {_f(w.get('solvent_share'))} | {_f(w.get('viability'))} "
                     f"| {_f(w.get('living_income'))} | {_f(ds['age'])} / {_f(ds['starvation'])} / {_f(ds['cull'])} "
                     f"| {_f(w.get('eligible_breeders'), '{:.1f}')} / {_f(w.get('alive'), '{:.1f}')} | {_f(w.get('median_energy'))} "
                     f"| {qs} | {_f(w.get('q5_over_q4_children'))} | {_f(w.get('distinct_parents'), '{}')} "
                     f"| {_f(w.get('parent_age'), '{:.1f}')} | {_f(w.get('generations_per_season'), '{:.3f}')} |")
        for w in ws:
            q = w.get("quintiles")
            if not q or (quintile_windows is not None and tuple(w["window"]) not in quintile_windows):
                continue
            L.append(f"  {kind} {w['window'][0]}-{w['window'][1]} quintiles (income = lifetime mean gain; net ÷ cost; "
                     f"lifespan; died of age; seasons eligible; children):")
            for i, x in enumerate(q):
                if x:
                    L.append(f"    Q{i+1} [{x['lo']:+.2f},{x['hi']:+.2f}] n {x['n']:4d}  income {x['income']:+.3f}  "
                             f"net÷cost {_f(x['net_over_cost'], '{:+.2f}')}  lifespan {x['lifespan']:5.1f}  "
                             f"age-death {x['died_of_age']:.2f}  eligible {_f(x['seasons_eligible'], '{:5.1f}')}  "
                             f"children {x['children']:.2f}")
    return "\n".join(L)


def parse_windows(s: str):
    out = []
    for part in s.split(","):
        a, b = part.split("-")
        out.append((int(a), int(b)))
    return tuple(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--windows", type=parse_windows, default=DEFAULT_WINDOWS)
    ap.add_argument("--min-life", type=int, default=10, help="lineage-last.txt only: the solvent rule's lifespan")
    ap.add_argument("--json", help="write every run's result to this file")
    ap.add_argument("--quiet", action="store_true", help="no tables on stdout")
    a = ap.parse_args(argv)
    allres = []
    for rd in a.runs:
        res = regime(rd, a.windows, a.min_life)
        allres.append(res)
        if not a.quiet:
            print(render(res), flush=True)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(allres, f, indent=1)
    return allres


if __name__ == "__main__":
    main()
