"""How strong is selection in this ecology? (RBT-59)

Prediction posted on the issue before this was run: the standardised difference
in lifetime yield between individuals that ever bred and those that never did
is under 0.3 SD in every arm and under 0.15 in most, because ~89% of the
population qualifies to breed and `Ecology.step` draws parents in random order
from the qualifying set.

Confound named in advance: individuals that live longer get both more chances
to breed and more evaluations, so age is controlled by comparing within age
bands and pooling, and the age-controlled figure is treated as the answer.
"""
import json, os, statistics as st
from collections import defaultdict

import numpy as np

DATA = "runs/RBT-59/data"
MIN_EVALS = 5
BAND = 10  # age band width, seasons


def arm_rows(arm, kind):
    recs = {}
    with open(f"{DATA}/{arm}/lineage.jsonl") as f:
        for line in f:
            r = json.loads(line)
            if r["population"] == kind:
                recs[r["name"]] = r  # last record per individual
    bred = {r["parents"][0] for r in recs.values() if r["parents"] and r["parents"][0] in recs}
    rows = [(r["name"] in bred, float(r["fitness"]), int(r["age"]))
            for r in recs.values() if r["evals"] >= MIN_EVALS]
    return rows


def standardised(rows):
    y = np.array([f for _, f, _ in rows], dtype=float)
    b = np.array([bred for bred, _, _ in rows], dtype=bool)
    if b.sum() < 5 or (~b).sum() < 5 or y.std(ddof=1) == 0:
        return float("nan"), int(b.sum()), int((~b).sum())
    return float((y[b].mean() - y[~b].mean()) / y.std(ddof=1)), int(b.sum()), int((~b).sum())


def age_controlled(rows):
    """Pool the within-band standardised differences, weighted by band size."""
    bands = defaultdict(list)
    for bred, f, age in rows:
        bands[age // BAND].append((bred, f, age))
    num = den = 0.0
    for _, sub in bands.items():
        d, nb, nn = standardised(sub)
        if d == d:
            w = nb + nn
            num += d * w
            den += w
    return num / den if den else float("nan")


hdr = f"{'arm':13} {'pop':12} {'n bred':>7} {'n not':>6} {'raw SD':>7} {'age-ctrl SD':>11} {'mean age bred':>13} {'not':>6}"
print(hdr); print("-" * len(hdr))
out = []
for arm in sorted(os.listdir(DATA)):
    for kind in ("holistic", "conventional"):
        try:
            rows = arm_rows(arm, kind)
        except Exception:
            continue
        if len(rows) < 40:
            continue
        raw, nb, nn = standardised(rows)
        ac = age_controlled(rows)
        ab = st.mean([a for bred, _, a in rows if bred]) if nb else float("nan")
        an = st.mean([a for bred, _, a in rows if not bred]) if nn else float("nan")
        print(f"{arm:13} {kind:12} {nb:7d} {nn:6d} {raw:+7.3f} {ac:+11.3f} {ab:13.1f} {an:6.1f}")
        out.append(dict(arm=arm, kind=kind, n_bred=nb, n_not=nn, raw_sd=raw, age_controlled_sd=ac,
                        mean_age_bred=ab, mean_age_not=an))
json.dump(out, open("runs/RBT-59/selection.json", "w"), indent=2, default=float)

acs = [r["age_controlled_sd"] for r in out if r["age_controlled_sd"] == r["age_controlled_sd"]]
raws = [r["raw_sd"] for r in out if r["raw_sd"] == r["raw_sd"]]
print(f"\nage-controlled standardised difference over {len(acs)} rows:"
      f"  min {min(acs):+.3f}  median {st.median(acs):+.3f}  max {max(acs):+.3f}")
print(f"raw (uncontrolled):                          min {min(raws):+.3f}  median {st.median(raws):+.3f}  max {max(raws):+.3f}")
print(f"rows with age-controlled |d| > 0.3: {sum(1 for d in acs if abs(d) > 0.3)} of {len(acs)}")
print(f"rows with age-controlled |d| > 0.15: {sum(1 for d in acs if abs(d) > 0.15)} of {len(acs)}")
