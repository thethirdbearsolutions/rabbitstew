"""RBT-118 prior (EXPLORATORY, descriptive only): the two faunas' alive counts and income by phase of a run.

    python runs/RBT-118/prior/phases.py > runs/RBT-118/prior/phases.txt

Reads ``runs.tsv`` (survey.py) for the distinct season tables and their worlds, and each table's ``seasons.txt``.
Per arm group and window it prints, over the group's runs: median holistic and designed alive, median income (the
table's ``mean_lifetime_score``, energy per season), the median holistic − designed income difference, and on how many
runs the holistic fauna's income was the higher.  Windows are fixed in advance of looking at any window's numbers
(they are the programme's usual landmarks: one max_age, five max_ages, the onset, the onset + 100, the last 100), and
windows after an onset are read only on arms that have one.

The faunas live in SEPARATE ecologies of their own capacity in every run read here (merge_after null throughout; see
survey.py), so "higher income" is a side-by-side comparison under shared seeds and worlds, not a contest for food.
Nothing is tested; no interval is a confidence statement about anything.
"""
import csv
import os
import re
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def load(run):
    t = defaultdict(dict)
    with open(os.path.join(ROOT, run, "seasons.txt")) as f:
        head = f.readline().rstrip("\n").split("\t")
        ix = {k: head.index(k) for k in ("season", "population", "alive", "mean_lifetime_score")}
        for line in f:
            r = line.rstrip("\n").split("\t")
            a = int(r[ix["alive"]])
            t[r[ix["population"]]][int(r[ix["season"]])] = (a, float(r[ix["mean_lifetime_score"]]) if a > 0 else np.nan)
    return t


def window(t, kind, lo, hi):
    rows = [v for s, v in t[kind].items() if lo <= s < hi]
    if not rows:
        return np.nan, np.nan
    a = np.array([r[0] for r in rows], float)
    sc = np.array([r[1] for r in rows], float)
    return float(np.mean(a)), (float(np.nanmean(sc)) if np.isfinite(sc).any() else np.nan)


def onset(r):
    for f in ("shift", "cull"):
        m = re.search(r"@(\d+)$", r[f] or "")
        if m:
            return int(m.group(1))
    return None


def group_of(r):
    parts = r["run"].split("/")
    arm = parts[-1].rsplit("-", 1)[0]
    return "/".join(parts[1:-1] + [arm])


def main():
    runs = [r for r in csv.DictReader(open(os.path.join(HERE, "runs.tsv")), delimiter="\t") if not r["dup_of"]]
    groups = defaultdict(list)
    for r in runs:
        groups[group_of(r)].append(r)
    print("# RBT-118 prior, phases.py: EXPLORATORY, descriptive only. Separate ecologies, shared seeds and worlds; no merged run exists.")
    print("# per window: n runs | median alive H / D | median income H / D | median (H - D) income [min, max] | runs with H income > D")
    for g in sorted(groups):
        rs = groups[g]
        last = int(rs[0]["last_season"]) + 1
        T = onset(rs[0])
        wins = [("0-59", 0, 60), ("60-299", 60, 300)]
        if T:
            wins += [(f"300-onset({T})", 300, T), ("onset..+99", T, T + 100), ("last 100", last - 100, last)]
        else:
            wins += [("300-599", 300, 600)] + ([("600-1199", 600, 1200)] if last > 600 else []) + [("last 100", last - 100, last)]
        r0 = rs[0]
        desc = f"patches={r0['patches']} items={r0['items']} living_cost={r0['living_cost']} shift={r0['shift'] or '-'} cull={r0['cull'] or '-'} planted H/D={r0['planted_h'] or 'no'}/{r0['planted_c'] or 'no'} breed_stream={r0['breed_stream'] or '-'}"
        print(f"\n## {g}  (n={len(rs)}, seasons 0..{last - 1})  {desc}")
        tables = {r["run"]: load(r["run"]) for r in rs}
        for name, lo, hi in wins:
            if hi <= lo or lo >= last:
                continue
            vals = [(window(t, "holistic", lo, hi), window(t, "conventional", lo, hi)) for t in tables.values()]
            aH = [v[0][0] for v in vals]; aD = [v[1][0] for v in vals]
            iH = [v[0][1] for v in vals]; iD = [v[1][1] for v in vals]
            diff = [h - d for h, d in zip(iH, iD) if np.isfinite(h) and np.isfinite(d)]
            win = sum(1 for d in diff if d > 0)
            dtxt = f"{np.median(diff):+.3f} [{min(diff):+.3f}, {max(diff):+.3f}]" if diff else "n/a"
            print(f"  {name:>18}: n={len(vals):2d} | alive {np.nanmedian(aH):5.1f} / {np.nanmedian(aD):5.1f} | income {np.nanmedian(iH):+.3f} / {np.nanmedian(iD):+.3f} | H-D {dtxt} | H>D {win}/{len(diff)}")


if __name__ == "__main__":
    main()
