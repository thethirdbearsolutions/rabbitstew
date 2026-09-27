"""RBT-118 prior (EXPLORATORY, descriptive only): independent histories, and every extinction in the committed tables.

    python runs/RBT-118/prior/pool.py > runs/RBT-118/prior/pool.txt

Part A, the default world with random founders of both faunas (12 items, uniform, random terrain, living cost 0.25,
capacity 60 each, separate ecologies).  The independent histories are one per (seed, founders): RBT-90's ten seeds and
RBT-107's twenty fresh base seeds.  Every shift/cull arm of RBT-92/99/100/101 and RBT-107 forks from one of these at
its onset, so its seasons before the onset are these seasons again and are not counted twice.  RBT-105's b1/b2 are
replicate *holistic* histories on RBT-90's founders (the designed side is RBT-90's again) and are listed apart.

Per history: the holistic fauna's fewest alive in seasons 0-59, its extinction season if any, the holistic − designed
income difference (the season table's mean_lifetime_score) over seasons 0-59 and over the last 100, and the HOLD
season: the first season s from which the 60-season trailing mean of that difference stays above 0 to the end of the
run (blank if it never does; the definition was fixed before it was computed, and it is a description, not a
change-point test); and pos>=60, the fraction of seasons from 60 on at which that trailing mean is above 0.

Part B, every fauna extinction in every distinct committed season table, with the arm's world and onset, the season
counted from the onset, and whether a cull removed the whole fauna (an extinction imposed by the null's mechanics,
not by the ecology).
"""
import csv
import os
import re
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROLL = 60
#: fixed windows of H - D; 0-10 and 11-59 split the founders' runway from the rest (adversary MUST-1), 500-599 is the
#: one depth every history reaches (adversary SHOULD-4)
WINDOWS = {"0-10": (0, 11), "11-59": (11, 60), "0-59": (0, 60), "100-199": (100, 200), "200-299": (200, 300),
           "300-399": (300, 400), "400-499": (400, 500), "500-599": (500, 600), "1100-1199": (1100, 1200)}


def series(run):
    t = defaultdict(dict)
    with open(os.path.join(ROOT, run, "seasons.txt")) as f:
        head = f.readline().rstrip("\n").split("\t")
        ix = {k: head.index(k) for k in ("season", "population", "alive", "deaths", "mean_lifetime_score", "births")}
        for line in f:
            r = line.rstrip("\n").split("\t")
            a = int(r[ix["alive"]])
            t[r[ix["population"]]][int(r[ix["season"]])] = (a, float(r[ix["mean_lifetime_score"]]) if a > 0 else np.nan, int(r[ix["deaths"]]), int(r[ix["births"]]))
    s = sorted(t["holistic"])
    H = np.array([t["holistic"][i] for i in s], float)
    D = np.array([t["conventional"].get(i, (0, np.nan, 0, 0)) for i in s], float)
    return np.array(s), H, D


def trailing(d):
    return np.array([np.nanmean(d[max(0, i - ROLL + 1): i + 1]) if np.isfinite(d[max(0, i - ROLL + 1): i + 1]).any() else np.nan for i in range(len(d))])


def hold_season(s, d):
    """First season from which the trailing ROLL-season mean of d stays > 0 to the end (nan seasons skipped)."""
    m = trailing(d)
    ok = np.isfinite(m) & (m > 0)
    if not ok[-1]:
        return None
    i = len(ok) - 1
    while i > 0 and ok[i - 1]:
        i -= 1
    return int(s[i])


def lead_onset(s, d, run_len=20):
    """First season that begins RUN_LEN consecutive seasons of H - D > 0 (added after the adversary, PR #402, MUST-2)."""
    pos = np.isfinite(d) & (d > 0)
    for i in range(len(pos) - run_len + 1):
        if pos[i: i + run_len].all():
            return int(s[i])
    return None


def window_mean(s, d, lo, hi):
    w = d[(s >= lo) & (s < hi)]
    return float(np.nanmean(w)) if len(w) and np.isfinite(w).any() else np.nan


def history_row(run):
    s, H, D = series(run)
    d = H[:, 1] - D[:, 1]
    early, late = d[s < 60], d[-100:]
    hx = next((int(s[i]) for i in range(len(s)) if H[i, 0] == 0 and not H[i:, 0].any()), None)
    early_alive = H[s < 60, 0]
    return dict(run=run, last=int(s[-1]), h_min_0_59=int(early_alive.min()), h_min_at=int(s[s < 60][early_alive.argmin()]), h_extinct=hx,
                early=np.nanmean(early) if np.isfinite(early).any() else np.nan,
                late=np.nanmean(late) if np.isfinite(late).any() else np.nan, hold=hold_season(s, d),
                frac_pos=float(np.mean(trailing(d)[s >= 60] > 0)), onset=lead_onset(s, d),
                w={w: window_mean(s, d, lo, hi) for w, (lo, hi) in WINDOWS.items()},
                h_score_10=H[s == 10, 1][0], h_score_13=H[s == 13, 1][0],
                late_demo={k: (float(A[(s >= 500) & (s < 600), c].mean()) if ((s >= 500) & (s < 600)).any() else np.nan)
                           for k, A, c in (("h_alive", H, 0), ("d_alive", D, 0), ("h_births", H, 3), ("d_births", D, 3), ("h_deaths", H, 2), ("d_deaths", D, 2))})


def main():
    runs = list(csv.DictReader(open(os.path.join(HERE, "runs.tsv")), delimiter="\t"))
    print("# RBT-118 prior, pool.py: EXPLORATORY, descriptive only. Separate ecologies (no merged run exists); income = mean_lifetime_score.")
    print("\n## A. Independent default-world histories, random founders of both faunas (RBT-90 forage-*, RBT-107 fresh base-*)")
    print(f"{'run':34s} {'last':>5s} {'H min 0-59':>10s} {'H extinct':>9s} {'H-D 0-59':>9s} {'H-D last100':>11s} {'HOLD':>6s} {'pos>=60':>7s}")
    indep = sorted(r["run"] for r in runs if re.fullmatch(r"runs/RBT-90/forage-\d+|runs/RBT-107/fresh/base-\d+", r["run"]))
    rows = [history_row(r) for r in indep]
    for r in rows:
        print(f"{r['run']:34s} {r['last']:5d} {r['h_min_0_59']:10d} {str(r['h_extinct'] or ''):>9s} {r['early']:+9.3f} {r['late']:+11.3f} {str(r['hold'] if r['hold'] is not None else ''):>6s} {r['frac_pos']:7.2f}")
    live = [r for r in rows if r["h_extinct"] is None]
    e = np.array([r["early"] for r in rows]); L = np.array([r["late"] for r in live])
    holds = [r["hold"] for r in live if r["hold"] is not None]
    print(f"\nhistories: {len(rows)}; holistic fauna extinct: {len(rows) - len(live)} ({', '.join(r['run'] + ' at ' + str(r['h_extinct']) for r in rows if r['h_extinct'] is not None)}); designed fauna extinct: 0")
    print(f"seasons 0-59, holistic income below designed: {int((e < 0).sum())}/{len(e)}; median H-D {np.median(e):+.3f}")
    print(f"last 100 seasons, holistic income above designed: {int((L > 0).sum())}/{len(L)} surviving; median H-D {np.median(L):+.3f}")
    print("\nper fixed window, H - D income (holistic lower / higher on, median):")
    for w in WINDOWS:
        v = np.array([r["w"][w] for r in rows]); v = v[np.isfinite(v)]
        if len(v):
            print(f"  {w:>9s}: n={len(v):2d}  holistic lower on {int((v < 0).sum()):2d}, higher on {int((v > 0).sum()):2d}; median {np.median(v):+.3f}")
    ons = [r["onset"] for r in live if r["onset"] is not None]
    print(f"lead ONSET (first season beginning 20 consecutive seasons of H - D > 0): found on {len(ons)}/{len(live)} surviving; median {np.median(ons):.0f}, "
          f"IQR {np.percentile(ons, 25):.0f}-{np.percentile(ons, 75):.0f}, range {min(ons)}-{max(ons)}; within the first 60 seasons on {sum(o < 60 for o in ons)}")
    h10 = np.array([r["h_score_10"] for r in live]); h13 = np.array([r["h_score_13"] for r in live])
    print(f"holistic income across the season-11 die-off: median {np.nanmedian(h10):.3f} at season 10, {np.nanmedian(h13):.3f} at season 13; rose on {int((h13 > h10).sum())}/{len(live)}")
    for k in ("h_alive", "d_alive", "h_births", "d_births", "h_deaths", "d_deaths"):
        v = [r["late_demo"][k] for r in live]
        print(f"seasons 500-599, {k}: mean over surviving histories {np.mean(v):.2f} (range {min(v):.2f}-{max(v):.2f})")
    fewer = sum(r["late_demo"]["h_deaths"] < r["late_demo"]["d_deaths"] for r in live)
    print(f"seasons 500-599: holistic deaths a season fewer than designed on {fewer}/{len(live)}")
    print(f"HOLD (a LAST-DIP statistic) season found on {len(holds)}/{len(live)}; median {np.median(holds):.0f}, range {min(holds)}-{max(holds)}; quartiles {np.percentile(holds, 25):.0f}, {np.percentile(holds, 75):.0f}")
    print(f"holistic fewest alive in 0-59: median {np.median([r['h_min_0_59'] for r in rows]):.0f}, range {min(r['h_min_0_59'] for r in rows)}-{max(r['h_min_0_59'] for r in rows)}, "
          f"at season median {np.median([r['h_min_at'] for r in rows]):.0f} (range {min(r['h_min_at'] for r in rows)}-{max(r['h_min_at'] for r in rows)})")
    dmin = [int(series(r['run'])[2][:60, 0].min()) for r in rows]
    print(f"designed fewest alive in 0-59: median {np.median(dmin):.0f}, range {min(dmin)}-{max(dmin)}")
    # H53 (adversary PR #402 addendum): alive is booked after the season's births refill freed slots; alive - births is the pre-refill count
    pre = {k: [] for k in ("holistic", "designed")}
    for r in rows:
        s_, H_, D_ = series(r["run"])
        m = s_ < 60
        pre["holistic"].append(float((H_[m, 0] - H_[m, 3]).min())); pre["designed"].append(float((D_[m, 0] - D_[m, 3]).min()))
    for k, v in pre.items():
        print(f"{k} fewest alive in 0-59 BEFORE same-season refill (alive - births): median {np.median(v):.0f}, range {min(v):.0f}-{max(v):.0f}")

    print("\n## A'. RBT-105 replicate holistic histories (same founders as RBT-90 at that seed; designed side = RBT-90's)")
    # forage-7-b0 is RBT-90's forage-7 (same history), so it is not a replicate: 16 replicates (adversary SHOULD-3)
    for run in sorted(r["run"] for r in runs if r["run"].startswith("runs/RBT-105/") and not r["dup_of"] and not r["run"].endswith("-b0")):
        r = history_row(run)
        print(f"{r['run']:34s} {r['last']:5d} {r['h_min_0_59']:10d} {str(r['h_extinct'] or ''):>9s} {r['early']:+9.3f} {r['late']:+11.3f} {str(r['hold'] if r['hold'] is not None else ''):>6s} {r['frac_pos']:7.2f}")

    print("\n## B. Every extinction in a distinct committed season table")
    print(f"{'run':36s} {'fauna':9s} {'season':>6s} {'onset':>6s} {'from onset':>10s}  world / event                                    imposed by cull?")
    for r in runs:
        if r["dup_of"]:
            continue
        for k, fauna in (("h", "holistic"), ("c", "designed")):
            if not r[f"{k}_extinct"]:
                continue
            ext = int(r[f"{k}_extinct"])
            m = re.search(r"@(\d+)$", r["shift"] or r["cull"] or "")
            T = int(m.group(1)) if m else None
            imposed = "before the onset: the base history's own, not the event's" if T is not None and ext < T else ""
            if r["cull"] and T is not None and ext == T:
                cm = re.search(rf"{'holistic' if k == 'h' else 'conventional'}=(\d+)", r["cull"])
                imposed = f"YES: cull {fauna} k={cm.group(1)} >= alive" if cm and int(cm.group(1)) >= 60 else "at the cull season"
            world = f"items={r['items']} patches={r['patches']} shift={r['shift'] or '-'} cull={r['cull'] or '-'}"
            print(f"{r['run']:36s} {fauna:9s} {ext:6d} {str(T or ''):>6s} {(str(ext - T) if T is not None else ''):>10s}  {world:48s} {imposed}")


if __name__ == "__main__":
    main()
