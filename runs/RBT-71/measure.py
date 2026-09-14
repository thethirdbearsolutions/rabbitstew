"""RBT-71 Deliverable A readout: every pre-registered measurement, per seed, never pooled.

usage: measure.py SEED [SEED...]      (reads runs/RBT-71/forage-SEED and runs/RBT-71/neutral-SEED)

File analysis only, no simulation.  The heritability and founder numbers come from the toolkit's own
functions (rabbitstew.analysis.realised_heritability / founder_survival), so they are the same numbers
`rabbitstew heritability RUN --drift-baseline NEUTRAL` prints; the depth is RBT-59's depth.py logic.
"""
import json, os, statistics as st, sys
from collections import defaultdict

from rabbitstew.analysis import ECOLOGY_MIN_EVALS, founder_survival, realised_heritability

ROOT = "runs/RBT-71"
KINDS = ("holistic", "conventional")


def history(run):
    return json.load(open(f"{run}/history.json"))["history"]


def series(hist, kind, key):
    return {h["season"]: h[key] for h in hist if h["population"] == kind}


def depth(run, kind):
    """Median first-parent chain length from the individuals alive at the last season to a founder (RBT-59)."""
    recs = {}
    with open(f"{run}/lineage.jsonl") as f:
        for line in f:
            r = json.loads(line)
            if r["population"] == kind:
                recs[r["name"]] = r
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
    # 2. heritability, both runs
    out["heritability"] = {}
    for label, run in (("selected", sel), ("neutral", neu)):
        if os.path.exists(f"{run}/lineage.jsonl"):
            out["heritability"][label] = {k: realised_heritability(run, k, min_evals=ECOLOGY_MIN_EVALS) for k in KINDS}
    # 3. founders, both runs
    out["founders"] = {}
    for label, run in (("selected", sel), ("neutral", neu)):
        if os.path.exists(f"{run}/lineage.jsonl"):
            out["founders"][label] = {k: founder_survival(run, k) for k in KINDS}
    # 5. depth, both runs
    out["depth"] = {}
    for label, run in (("selected", sel), ("neutral", neu)):
        if os.path.exists(f"{run}/lineage.jsonl"):
            out["depth"][label] = {k: depth(run, k) for k in KINDS}
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
    seeds = sys.argv[1:] or ["804", "805", "806"]
    results = []
    for seed in seeds:
        if not os.path.exists(f"{ROOT}/forage-{seed}/history.json"):
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
