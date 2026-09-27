"""RBT-126: the tables of REGIME.md from regime/corpus.json (runs/RBT-126/corpus.py).

Per ticket, arm and fauna: for each window, the median over the arm's seeds (and the range) of the readout.
Band, from the window-local saturation (the eligible members' season net / living cost) against the replica's
calibration (calibration.txt; invasion.txt for the fixation figures):
  saturated   >= 1.9     (replica g0 >= 0.8: a x2 mutant fixes <= 0.01, a x1.25 one 0.00; ADVERSARY 1d)
  transition  1.2 - 1.9  (replica g0 0.6-0.7: x2 fixes 0.27-0.04, x1.25 0.01-0.00)
  selecting   < 1.2      (replica g0 <= 0.5: x1.25 fixes 0.18-0.85, x2 0.87-1.00)
  none        no member eligible in the window (the fauna extinct or never solvent)
  few         fewer than 10 eligible breeders a season on average: the ratio is read off a handful of lucky
              members (the replica reads 2.6 at g0 0.3, on the way to extinction), so no band is given
"""
import collections, json, pathlib, re, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def band(s, elig=None):
    if s is None or s != s:
        return "none"  # no member eligible in the window (the fauna extinct, or never solvent)
    if elig is not None and elig < 10:
        return "few"
    return "saturated" if s >= 1.9 else ("transition" if s >= 1.2 else "selecting")


def arm_type(t, arm):
    if t == 90:
        return "base"
    if t == 105:
        return arm.split("-")[1]
    if t == 19:
        return "P-801"
    return re.sub(r"-\d+$", "", arm)


def agg(vals):
    v = [x for x in vals if x is not None and x == x]
    if not v:
        return "-", None
    m = float(np.median(v))
    return (f"{m:.2f}" if len(v) == 1 else f"{m:.2f} [{min(v):.2f}, {max(v):.2f}]"), m


def main():
    res = json.load(open(HERE / "regime" / "corpus.json"))
    groups = collections.defaultdict(list)
    for r in res:
        groups[(r["ticket"], arm_type(r["ticket"], r["arm"]))].append(r)
    cols = ("saturation_local", "saturation", "viability", "net_per_birth", "solvent_share", "age", "starvation", "cull", "eligible_breeders",
            "median_energy", "q5_over_q4_children", "generations_per_season", "living_income")
    out = []
    for (t, at), rs in sorted(groups.items()):
        seeds = sorted({r["seed"] for r in rs if r["seed"] is not None})
        out.append(f"\n#### RBT-{t} `{at}` — {len(rs)} run(s){': seeds ' + ', '.join(map(str, seeds)) if len(seeds) > 1 else ''}; last season {max(r['last_season'] for r in rs)}\n")
        out.append("| fauna | window | band | saturation (window-local) | saturation (per life) | viability | net / birth | solvent share | deaths by age | by starvation | by cull | eligible breeders | median energy | Q5÷Q4 children | gen / season | living income |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        labels = {}
        for r in rs:
            for lab, lo, hi in r["headline"]:
                labels.setdefault((lo, hi), set()).add(lab)
        for fauna in sorted({k for r in rs for k in r["fauna"]}):
            # windows: by (lo, hi) for fixed ones; headline ones by label (onset-relative windows differ per seed)
            rows = collections.OrderedDict()
            for r in rs:
                hl = {(lo, hi): lab for lab, lo, hi in r["headline"]}
                for w in r["fauna"].get(fauna, []):
                    key = hl.get(tuple(w["window"])) or f"{w['window'][0]}-{w['window'][1]}"
                    if key in rows and tuple(w["window"]) in hl and any(tuple(x["window"]) == tuple(w["window"]) for x in rows[key] if x.get("_run") == r["run"]):
                        continue
                    w = dict(w, _run=r["run"], age=w["death_share"]["age"], starvation=w["death_share"]["starvation"], cull=w["death_share"]["cull"])
                    rows.setdefault(key, []).append(w)
            for key, ws in rows.items():
                cells = {c: agg([w.get(c) for w in ws]) for c in cols}
                sat = cells["saturation_local"][1]
                bands = collections.Counter(band(w.get("saturation_local"), w.get("eligible_breeders")) for w in ws)
                bstr = band(sat, cells["eligible_breeders"][1]) + ("" if len(bands) == 1 else " (" + ", ".join(f"{k} {v}" for k, v in bands.most_common()) + ")")
                label = f"**{key}**" if not re.match(r"^\d+-\d+$", key) else key
                out.append(f"| {fauna} | {label} | {bstr} | " + " | ".join(cells[c][0] for c in cols) + " |")
    print("\n".join(out))



def headline():
    """One row per ticket, arm, fauna and headline window: the compact table at the top of REGIME.md."""
    res = json.load(open(HERE / "regime" / "corpus.json"))
    groups = collections.defaultdict(list)
    for r in res:
        groups[(r["ticket"], arm_type(r["ticket"], r["arm"]))].append(r)
    cols = ("saturation_local", "saturation", "viability", "age", "eligible_breeders", "q5_over_q4_children",
            "generations_per_season")
    print("| ticket | arm (runs) | fauna | window | band (runs per band) | saturation, window-local | saturation, per life "
          "| viability | deaths by age | eligible breeders | Q5÷Q4 children | gen / season |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    order = {19: 0, 90: 1, 99: 2, 100: 3, 101: 4, 104: 5, 105: 6, 106: 7, 107: 8, 112: 9}
    for (t, at), rs in sorted(groups.items(), key=lambda kv: (order.get(kv[0][0], 99), kv[0][1])):
        if at.startswith("adv"):
            continue
        for fauna in sorted({k for r in rs for k in r["fauna"]}):
            labs = list(dict.fromkeys(lab for r in rs for lab, _, _ in r["headline"]))
            for lab in labs:
                ws = []
                for r in rs:
                    win = [(lo, hi) for l2, lo, hi in r["headline"] if l2 == lab]
                    for w in r["fauna"].get(fauna, []):
                        if win and tuple(w["window"]) == (win[0][0], min(win[0][1], r["last_season"])):
                            ws.append(dict(w, age=w["death_share"]["age"]))
                            break
                if not ws:
                    continue
                cells = {c: agg([w.get(c) for w in ws]) for c in cols}
                bands = collections.Counter(band(w.get("saturation_local"), w.get("eligible_breeders")) for w in ws)
                b = band(cells["saturation_local"][1], cells["eligible_breeders"][1])
                bstr = b if len(bands) == 1 else f"{b} ({', '.join(f'{k} {v}' for k, v in bands.most_common())})"
                print(f"| RBT-{t} | {at} ({len(rs)}) | {fauna} | {lab} | {bstr} | " + " | ".join(cells[c][0] for c in cols) + " |")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "headline":
    headline()
    sys.exit()


if __name__ == "__main__":
    main()
