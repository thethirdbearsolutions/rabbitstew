"""RBT-71 Deliverable A readout: every pre-registered measurement, per seed, never pooled.

usage: measure.py SEED [SEED...]      (reads runs/RBT-71/forage-SEED and runs/RBT-71/neutral-SEED)
       measure.py --summarise [SEED...] (writes each run's seasons.txt and lineage-last.txt from its bulk)

Runs from the repository alone: when a run's history.json / lineage.jsonl are absent (they are not
committed, per runs/README.md) it reads the committed seasons.txt and lineage-last.txt instead, and
when both are present it checks that the toolkit's functions and the summary-derived ones agree.
MEASURE_FROM_SUMMARY=1 forces the summary path so the round trip can be checked.

File analysis only, no simulation.  The heritability and founder numbers come from the toolkit's own
functions (rabbitstew.analysis.realised_heritability / founder_survival), so they are the same numbers
`rabbitstew heritability RUN --drift-baseline NEUTRAL` prints; the depth is RBT-59's depth.py logic.
"""
import json, os, statistics as st, sys
from collections import defaultdict

from rabbitstew.analysis import ECOLOGY_MIN_EVALS, founder_survival, realised_heritability

ROOT = "runs/RBT-71"
KINDS = ("holistic", "conventional")


FROM_SUMMARY = os.environ.get("MEASURE_FROM_SUMMARY") == "1"  # force the committed-summary path, for the round trip
SEASON_KEYS = ("season", "population", "alive", "births", "deaths", "mean_lifetime_score", "best_lifetime_score")
LINEAGE_KEYS = ("population", "name", "generation", "age", "evals", "fitness", "parents")


def summarise(run):
    """Write the two committed summaries a run's argument rests on (adversary finding, RBT-71):
    seasons.txt, one row per (season, fauna) from history.json; lineage-last.txt, each individual's
    last lineage row (name, born-season via age, evals, lifetime mean yield, parents). Both TSV, both
    kilobytes, both tracked by the runs/** rule, so measure.py runs from the repository alone."""
    hist = json.load(open(f"{run}/history.json"))["history"]
    with open(f"{run}/seasons.txt", "w") as f:
        f.write("\t".join(SEASON_KEYS) + "\n")
        for h in hist:
            f.write("\t".join(str(h[k]) for k in SEASON_KEYS) + "\n")
    last = {}
    with open(f"{run}/lineage.jsonl") as f:
        for line in f:
            r = json.loads(line)
            last[(r["population"], r["name"])] = r
    with open(f"{run}/lineage-last.txt", "w") as f:
        f.write("\t".join(LINEAGE_KEYS) + "\n")
        for r in last.values():
            f.write("\t".join([r["population"], r["name"], str(r["generation"]), str(r["age"]), str(r["evals"]),
                                repr(r["fitness"]), ",".join(r["parents"])]) + "\n")


def history(run):
    if os.path.exists(f"{run}/history.json") and not FROM_SUMMARY:
        return json.load(open(f"{run}/history.json"))["history"]
    out = []
    with open(f"{run}/seasons.txt") as f:
        keys = f.readline().rstrip("\n").split("\t")
        for line in f:
            v = line.rstrip("\n").split("\t")
            h = dict(zip(keys, v))
            for k in ("season", "alive", "births", "deaths"):
                h[k] = int(h[k])
            for k in ("mean_lifetime_score", "best_lifetime_score"):
                h[k] = float(h[k])
            out.append(h)
    return out


def lineage_last(run):
    """{kind: {name: last record}} from lineage.jsonl, or from the committed lineage-last.txt."""
    recs = defaultdict(dict)
    if os.path.exists(f"{run}/lineage.jsonl") and not FROM_SUMMARY:
        with open(f"{run}/lineage.jsonl") as f:
            for line in f:
                r = json.loads(line)
                recs[r["population"]][r["name"]] = r
        return recs
    with open(f"{run}/lineage-last.txt") as f:
        f.readline()
        for line in f:
            pop, name, gen, age, evals, fit, parents = line.rstrip("\n").split("\t")
            recs[pop][name] = {"population": pop, "name": name, "generation": int(gen), "age": int(age),
                               "evals": int(evals), "fitness": float(fit), "parents": parents.split(",") if parents else []}
    return recs


def heritability_local(recs, min_evals=ECOLOGY_MIN_EVALS):
    """rabbitstew.analysis.realised_heritability, re-derived on the summary (same pairing, same filter)."""
    import numpy as np
    xs, ys = [], []
    for r in recs.values():
        if not r["parents"] or int(r["evals"] or 0) < min_evals:
            continue
        ps = [recs[p]["fitness"] for p in r["parents"] if p in recs and int(recs[p]["evals"] or 0) >= min_evals]
        if ps:
            xs.append(float(np.mean(ps))); ys.append(float(r["fitness"]))
    n = len(xs)
    if n < 10 or np.std(xs) == 0 or np.std(ys) == 0:
        return {"n": n, "heritability": None}
    return {"n": n, "heritability": round(float(np.corrcoef(xs, ys)[0, 1]), 4)}


def founders_local(recs):
    """rabbitstew.analysis.founder_survival, re-derived on the summary (all parents followed)."""
    last = max(r["generation"] for r in recs.values())
    names = [n for n, r in recs.items() if r["generation"] == last]
    roots = set()
    for name in names:
        stack, seen = [name], set()
        while stack:
            cur = stack.pop()
            if cur in seen or cur not in recs:
                continue
            seen.add(cur)
            if not recs[cur]["parents"]:
                roots.add(cur)
            stack.extend(recs[cur]["parents"])
    return {"generation": last, "founders": len(roots), "of": len(names)}


def series(hist, kind, key):
    return {h["season"]: h[key] for h in hist if h["population"] == kind}


def depth(run, kind, recs=None):
    """Median first-parent chain length from the individuals alive at the last season to a founder (RBT-59)."""
    recs = recs if recs is not None else lineage_last(run).get(kind, {})
    if not recs:
        return None
    last = max(r["generation"] for r in recs.values())
    alive = [r for r in recs.values() if r["generation"] == last]
    ds, founders = [], set()
    for r in alive:
        d, cur, seen = 0, r, set()
        while cur["parents"] and cur["parents"][0] in recs and cur["name"] not in seen:
            seen.add(cur["name"]); cur = recs[cur["parents"][0]]; d += 1
        ds.append(d); founders.add(cur["name"])
    return dict(season=last, alive=len(alive), median=st.median(ds), min=min(ds), max=max(ds),
                predicted=2 * last / 60, founders=len(founders))


def crossover(hm, wm, hold=20):
    """First season S from which holistic > wheeled for `hold` consecutive seasons (sustained crossover)."""
    seasons = sorted(set(hm) & set(wm))
    lead = [hm[s] > wm[s] for s in seasons]
    for i, s in enumerate(seasons):
        if all(lead[i:i + hold]) and len(lead[i:i + hold]) == hold:
            return s
    return None


def measure(seed):
    out = {"seed": seed}
    sel, neu = f"{ROOT}/forage-{seed}", f"{ROOT}/neutral-{seed}"
    hist = history(sel)
    last = max(h["season"] for h in hist)
    out["last_season"] = last
    hm, wm = series(hist, "holistic", "mean_lifetime_score"), series(hist, "conventional", "mean_lifetime_score")
    ha, wa = series(hist, "holistic", "alive"), series(hist, "conventional", "alive")
    hd = series(hist, "holistic", "deaths")
    # 1. crossover
    window = [s for s in range(100, 600) if s in hm and s in wm]
    out["crossover_sustained"] = crossover(hm, wm)
    out["window_seasons"] = len(window)
    out["holistic_leads_frac_100_599"] = (sum(hm[s] > wm[s] for s in window) / len(window)) if window else None
    out["holistic_leads_frac_all"] = sum(hm[s] > wm[s] for s in hm if s in wm) / len(hm)
    out["mean_lead_100_599"] = (sum(hm[s] - wm[s] for s in window) / len(window)) if window else None
    out["gain"] = {s: (hm.get(s), wm.get(s)) for s in (100, 300, 500, 599) if s in hm}
    # 4. the wave and the minima
    out["holistic_deaths_s11"] = hd.get(11)
    out["holistic_deaths_s10_12"] = [hd.get(s) for s in (10, 11, 12)]
    hmin_s = min(ha, key=lambda s: (ha[s], s)); wmin_s = min(wa, key=lambda s: (wa[s], s))
    out["holistic_min"] = (ha[hmin_s], hmin_s); out["wheeled_min"] = (wa[wmin_s], wmin_s)
    back = [s for s in sorted(ha) if s > hmin_s and ha[s] >= 60]
    out["holistic_back_at_60"] = back[0] if back else None
    out["extinct"] = {k: (min(a.values()) == 0) for k, a in (("holistic", ha), ("conventional", wa))}
    # 2, 3, 5. heritability, founders and depth, both runs, from the last lineage row per individual.
    # With the bulk present the toolkit's own functions are computed too and must agree exactly
    # (protocol III: round-trip the derived metric); without it, the committed summary is the source.
    out["heritability"], out["founders"], out["depth"] = {}, {}, {}
    for label, run in (("selected", sel), ("neutral", neu)):
        if not (os.path.exists(f"{run}/lineage.jsonl") or os.path.exists(f"{run}/lineage-last.txt")):
            continue
        recs = lineage_last(run)
        out["heritability"][label] = {k: heritability_local(recs[k]) for k in KINDS}
        out["founders"][label] = {k: founders_local(recs[k]) for k in KINDS}
        out["depth"][label] = {k: depth(run, k, recs[k]) for k in KINDS}
        if os.path.exists(f"{run}/lineage.jsonl") and not FROM_SUMMARY:
            for k in KINDS:
                lib_h = realised_heritability(run, k, min_evals=ECOLOGY_MIN_EVALS)
                lib_f = founder_survival(run, k)
                assert lib_h["heritability"] == out["heritability"][label][k]["heritability"] and lib_h["n"] == out["heritability"][label][k]["n"], (run, k, lib_h)
                assert lib_f["founders"] == out["founders"][label][k]["founders"] and lib_f["of"] == out["founders"][label][k]["of"], (run, k, lib_f)
    # neutral demography, for the record
    if os.path.exists(f"{neu}/history.json"):
        nh = history(neu)
        nhm, nwm = series(nh, "holistic", "mean_lifetime_score"), series(nh, "conventional", "mean_lifetime_score")
        nl = max(nhm)
        out["neutral"] = dict(last_season=nl, gain_0=(nhm.get(0), nwm.get(0)), gain_last=(nhm[nl], nwm[nl]),
                              alive_min=(min(series(nh, "holistic", "alive").values()), min(series(nh, "conventional", "alive").values())))
    return out


def fmt_h(h):
    return "n/a" if h is None or h.get("heritability") is None else f"{h['heritability']:+.3f} (n={h['n']})"


def report(o):
    s = o["seed"]
    print(f"=== seed {s}  (selected run through season {o['last_season']}) ===")
    print(f"  extinct: {o['extinct']}")
    print(f"  season-11 wave: holistic deaths at 10/11/12 = {o['holistic_deaths_s10_12']}")
    print(f"  holistic minimum {o['holistic_min'][0]} at season {o['holistic_min'][1]}, back at 60 by {o['holistic_back_at_60']};  wheeled minimum {o['wheeled_min'][0]} at {o['wheeled_min'][1]}")
    print(f"  mean gain hol/wheel at 100/300/500/599: " + "  ".join(f"{k}: {v[0]:+.2f}/{v[1]:+.2f}" for k, v in o["gain"].items()))
    fr = o["holistic_leads_frac_100_599"]
    print(f"  sustained crossover (20-season hold): {o['crossover_sustained']}")
    frs = "n/a" if fr is None else f"{fr:.3f}"
    ml = o["mean_lead_100_599"]; mls = "n/a" if ml is None else f"{ml:+.3f}"
    print(f"  holistic leads in {frs} of seasons 100-599 ({o['window_seasons']} seasons), {o['holistic_leads_frac_all']:.3f} of all; mean lead 100-599 {mls}")
    for label in ("selected", "neutral"):
        if label in o["heritability"]:
            h = o["heritability"][label]; f = o["founders"][label]; d = o["depth"][label]
            print(f"  [{label}] heritability hol {fmt_h(h['holistic'])}  wheel {fmt_h(h['conventional'])}   (evals >= {ECOLOGY_MIN_EVALS})")
            print(f"  [{label}] founders  hol {f['holistic']['founders']} of {f['holistic']['of']}  wheel {f['conventional']['founders']} of {f['conventional']['of']}  at season {f['holistic']['generation']}")
            for k in KINDS:
                if d[k]:
                    print(f"  [{label}] depth {k:12s} median {d[k]['median']:.0f} ({d[k]['min']}-{d[k]['max']}) at season {d[k]['season']}, 2S/A {d[k]['predicted']:.1f}, ratio {d[k]['median']/d[k]['predicted']:.2f}")
    if "neutral" in o:
        n = o["neutral"]
        print(f"  neutral demography: through season {n['last_season']}, mean gain s0 {n['gain_0'][0]:+.2f}/{n['gain_0'][1]:+.2f} -> last {n['gain_last'][0]:+.2f}/{n['gain_last'][1]:+.2f}, alive min {n['alive_min']}")


def main():
    args = sys.argv[1:]
    if args and args[0] == "--summarise":
        for seed in args[1:] or ["804", "805", "806"]:
            for kind in ("forage", "neutral"):
                summarise(f"{ROOT}/{kind}-{seed}"); print(f"summarised {kind}-{seed}")
        return
    seeds = args or ["804", "805", "806"]
    results = []
    for seed in seeds:
        if not (os.path.exists(f"{ROOT}/forage-{seed}/history.json") or os.path.exists(f"{ROOT}/forage-{seed}/seasons.txt")):
            print(f"seed {seed}: no history yet"); continue
        o = measure(seed); results.append(o); report(o)
    json.dump(results, open(f"{ROOT}/measure.json", "w"), indent=1, default=str)
    if len(results) > 1:
        table(results)


def table(results):
    """One column per seed, never pooled: the pre-registered quantities side by side."""
    def h(o, label, k):
        x = o["heritability"].get(label, {}).get(k)
        return "n/a" if not x or x.get("heritability") is None else f"{x['heritability']:+.3f} (n={x['n']})"
    def f(o, label, k):
        x = o["founders"].get(label, {}).get(k)
        return "n/a" if not x else f"{x['founders']}"
    def d(o, label, k):
        x = o["depth"].get(label, {}).get(k)
        return "n/a" if not x else f"{x['median']:.0f} ({x['min']}-{x['max']})"
    rows = [
        ("holistic deaths at season 11", lambda o: str(o["holistic_deaths_s11"])),
        ("holistic minimum (season)", lambda o: f"{o['holistic_min'][0]} ({o['holistic_min'][1]})"),
        ("holistic back at 60", lambda o: str(o["holistic_back_at_60"])),
        ("wheeled minimum (season)", lambda o: f"{o['wheeled_min'][0]} ({o['wheeled_min'][1]})"),
        ("sustained crossover", lambda o: str(o["crossover_sustained"])),
        ("holistic leads, seasons 100-599", lambda o: f"{o['holistic_leads_frac_100_599']:.3f}"),
        ("mean lead, seasons 100-599", lambda o: f"{o['mean_lead_100_599']:+.3f}"),
        ("gain hol/wheel at 100", lambda o: f"{o['gain'][100][0]:+.2f} / {o['gain'][100][1]:+.2f}"),
        ("gain hol/wheel at 300", lambda o: f"{o['gain'][300][0]:+.2f} / {o['gain'][300][1]:+.2f}"),
        ("gain hol/wheel at 500", lambda o: f"{o['gain'][500][0]:+.2f} / {o['gain'][500][1]:+.2f}"),
        ("gain hol/wheel at 599", lambda o: f"{o['gain'][599][0]:+.2f} / {o['gain'][599][1]:+.2f}"),
        ("heritability holistic, selected", lambda o: h(o, "selected", "holistic")),
        ("heritability wheeled, selected", lambda o: h(o, "selected", "conventional")),
        ("heritability holistic, neutral", lambda o: h(o, "neutral", "holistic")),
        ("heritability wheeled, neutral", lambda o: h(o, "neutral", "conventional")),
        ("founders holistic, selected / neutral", lambda o: f"{f(o, 'selected', 'holistic')} / {f(o, 'neutral', 'holistic')}"),
        ("founders wheeled, selected / neutral", lambda o: f"{f(o, 'selected', 'conventional')} / {f(o, 'neutral', 'conventional')}"),
        ("depth holistic at 599, selected", lambda o: d(o, "selected", "holistic")),
        ("depth wheeled at 599, selected", lambda o: d(o, "selected", "conventional")),
        ("depth holistic at 599, neutral", lambda o: d(o, "neutral", "holistic")),
        ("depth wheeled at 599, neutral", lambda o: d(o, "neutral", "conventional")),
        ("neutral gain hol/wheel at last season", lambda o: f"{o['neutral']['gain_last'][0]:+.2f} / {o['neutral']['gain_last'][1]:+.2f}" if "neutral" in o else "n/a"),
    ]
    seeds = [str(o["seed"]) for o in results]
    print("\n| measurement | " + " | ".join(seeds) + " |")
    print("|---|" + "---|" * len(seeds))
    for name, fn in rows:
        cells = []
        for o in results:
            try:
                cells.append(fn(o))
            except Exception:
                cells.append("n/a")
        print(f"| {name} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
