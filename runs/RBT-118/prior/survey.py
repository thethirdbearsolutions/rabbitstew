"""RBT-118 prior (EXPLORATORY, descriptive only): what the committed ecology tables say about the two faunas.

    python runs/RBT-118/prior/survey.py > runs/RBT-118/prior/survey.txt

Reads every committed ``runs/**/seasons.txt`` (and the ``config.json`` beside it when there is one) and writes
``runs.tsv``: one row per run with its world and, per fauna, its alive trajectory summarised (start, end, min, mean,
extinction season, first season under 10 alive).  It scores nothing and tests nothing.

Two facts decide how the columns may be read, and both are checked here rather than assumed:
- ``merge_after`` is null in every committed config, so no committed run put the two faunas in one arena under one
  capacity (``rabbitstew/ecology.py``: separate arena banks and separate ``capacity`` until a merge).  The "holistic
  alive fraction" H/(H+C) below is therefore a *side-by-side* ratio of two separately capped ecologies that share a
  seed and a terrain stream, NOT a competitive share of one world.
- A season table is byte-copied into several tickets (RBT-99's arms re-read by RBT-100/101, RBT-106's HU by RBT-112,
  the H-REP cuts of RBT-107's fresh arms); ``dup_of`` names the first path whose seasons.txt is byte-identical, or of
  which this one is a line-for-line prefix, so that nothing is counted twice.
"""
import glob
import hashlib
import json
import os
import re
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.dirname(os.path.abspath(__file__))
KINDS = ("holistic", "conventional")


def read_seasons(path):
    """(seasons, {fauna: alive array}, {fauna: mean_lifetime_score array (nan where the fauna is empty)})."""
    alive, score = {k: {} for k in KINDS}, {k: {} for k in KINDS}
    with open(path) as f:
        head = f.readline().rstrip("\n").split("\t")
        ia, ip, isn, isc = head.index("alive"), head.index("population"), head.index("season"), head.index("mean_lifetime_score")
        for line in f:
            r = line.rstrip("\n").split("\t")
            if r[ip] in alive:
                alive[r[ip]][int(r[isn])] = int(r[ia])
                score[r[ip]][int(r[isn])] = float(r[isc]) if r[isc] not in ("", "nan", "None") and int(r[ia]) > 0 else np.nan
    seasons = sorted(set(alive["holistic"]) | set(alive["conventional"]))
    return (seasons, {k: np.array([alive[k].get(s, 0) for s in seasons]) for k in KINDS},
            {k: np.array([score[k].get(s, np.nan) for s in seasons]) for k in KINDS})


def world(run_dir):
    """World and protocol fields from config.json; RBT-106 (no configs committed) from its registered arm table."""
    rel = os.path.relpath(run_dir, ROOT)
    arm = os.path.basename(run_dir)
    p = os.path.join(run_dir, "config.json")
    if os.path.exists(p):
        c = json.load(open(p))
        e, food = c.get("ecology", {}), c.get("sim", {}).get("food", {})
        return dict(config="yes", seed=c.get("seed"), challenge=e.get("challenge"), capacity=e.get("capacity"),
                    living_cost=e.get("living_cost"), patches=food.get("patches"), regrow_delay=food.get("regrow_delay"),
                    items=food.get("items"), terrain=c.get("sim", {}).get("world", {}).get("terrain"),
                    shift=f'{e.get("shift")}@{e.get("shift_at")}' if e.get("shift") else "",
                    cull=f'{e.get("cull")}@{e.get("cull_at")}' if e.get("cull") else "",
                    breed_stream=e.get("breed_stream") or "", merge_after=e.get("merge_after"),
                    planted_h="yes" if (e.get("seed_holistic") or e.get("seed_from")) else "",
                    planted_c="yes" if (e.get("seed_conventional") or e.get("seed_from")) else "")
    m = re.match(r"(.+?)-(\d+)$", arm)
    d = dict(config="no", seed=int(m.group(2)) if m else None, challenge="foraging?", capacity=None, living_cost=None,
             patches=None, regrow_delay=None, items=None, terrain=None, shift="", cull="", breed_stream="",
             merge_after="(no config)", planted_h="", planted_c="")
    if rel.startswith("runs/RBT-106"):
        # PREREGISTRATION.md arm table: HU uniform, HP --food-patches 3, P1 = S1 + --food-patches 3 (side/: S1P,S8P patchy)
        tag = m.group(1) if m else arm
        d["patches"] = 3 if tag.endswith("P") or tag == "P1" else 0
        d["planted_h"] = d["planted_c"] = "yes (registered)"
    if "/hrep/" in rel:
        d["breed_stream"] = "H-REP cut"
    return d


def summarise(seasons, a, cap):
    s = np.array(seasons)
    ext = next((int(s[i]) for i in range(len(a)) if a[i] == 0 and not a[i:].any()), None)
    u10 = next((int(s[i]) for i in range(len(a)) if a[i] < 10), None)
    return dict(start=int(a[0]), end=int(a[-1]), min=int(a.min()), mean=round(float(a.mean()), 1), extinct=ext, under10=u10,
                at_cap=round(float(np.mean(a >= cap)), 3) if cap else None)


def main():
    paths = sorted(glob.glob(os.path.join(ROOT, "runs", "**", "seasons.txt"), recursive=True))
    rows, seen = [], {}
    for p in paths:
        d = os.path.dirname(p)
        rel = os.path.relpath(d, ROOT)
        seasons, al, sc = read_seasons(p)
        if not seasons:
            continue
        key = hashlib.sha1(open(p, "rb").read()).hexdigest()
        dup = seen.get(key, "")
        seen.setdefault(key, rel)
        row = dict(run=rel, ticket=rel.split("/")[1], seasons=len(seasons), last_season=seasons[-1], **world(d))
        cap = row["capacity"] or 60
        for k in KINDS:
            for f, v in summarise(seasons, al[k], cap).items():
                row[f"{k[0]}_{f}"] = v
            # income: the season table's mean lifetime score (energy per season), over the whole run and the last 100 seasons
            row[f"{k[0]}_score_all"] = round(float(np.nanmean(sc[k])), 4) if np.isfinite(sc[k]).any() else None
            row[f"{k[0]}_score_last100"] = round(float(np.nanmean(sc[k][-100:])), 4) if np.isfinite(sc[k][-100:]).any() else None
        H, C = al["holistic"], al["conventional"]
        tot = np.maximum(H + C, 1)
        row["h_frac_mean"] = round(float(np.mean(H / tot)), 3)
        row["h_frac_end"] = round(float(H[-1] / max(H[-1] + C[-1], 1)), 3)
        row["dup_of"] = dup
        row["_series"] = (seasons, H, C)
        row["_lines"] = open(p).read().splitlines()
        rows.append(row)
    # prefix duplicates: a run whose (H, C) series equals the first n seasons of an earlier non-duplicate run
    base = [r for r in rows if not r["dup_of"]]
    for r in rows:
        if r["dup_of"]:
            continue
        L = r["_lines"]
        for b in base:
            if b is r or b["seasons"] <= r["seasons"]:
                continue
            if b["_lines"][: len(L)] == L:
                r["dup_of"] = b["run"] + f" (prefix, {r['seasons']} seasons)"
                break
    cols = [c for c in rows[0] if not c.startswith("_")]
    with open(os.path.join(OUT, "runs.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join("" if r[c] is None else str(r[c]) for c in cols) + "\n")
    # per-season holistic/designed alive series, for figures and later re-reading
    with open(os.path.join(OUT, "alive-series.tsv"), "w") as f:
        f.write("run\tseason\tholistic_alive\tdesigned_alive\n")
        for r in rows:
            if r["dup_of"]:
                continue
            s, H, C = r["_series"]
            for i in range(len(s)):
                f.write(f"{r['run']}\t{s[i]}\t{H[i]}\t{C[i]}\n")
    merged = [r for r in rows if r["merge_after"] not in (None, "(no config)")]
    print("# RBT-118 prior, survey.py: EXPLORATORY, descriptive only")
    print(f"season tables: {len(rows)}; distinct (not a byte copy or prefix of another): {len([r for r in rows if not r['dup_of']])}")
    print(f"runs with a config: {sum(r['config'] == 'yes' for r in rows)}; with merge_after set (faunas in ONE arena): {len(merged)}")
    # every committed config.json, not only those beside a season table (adversary PR #402, MUST-6)
    allc = [json.load(open(p)) for p in glob.glob(os.path.join(ROOT, "runs", "**", "config.json"), recursive=True)]
    eco = [c["ecology"] for c in allc if isinstance(c.get("ecology"), dict)]
    print(f"all committed config.json under runs/: {len(allc)}; with an ecology section: {len(eco)}; "
          f"merge_after present and null: {sum('merge_after' in e and e['merge_after'] is None for e in eco)}; "
          f"no merge_after key (predates it, None by default): {sum('merge_after' not in e for e in eco)}; "
          f"merge_after set: {sum(e.get('merge_after') is not None for e in eco)}")
    print(f"season tables with no config beside them: {sum(r['config'] == 'no' for r in rows)} "
          f"({', '.join(sorted(set(r['run'].rsplit('/', 1)[0] for r in rows if r['config'] == 'no')))})")
    for r in merged:
        print("  merged:", r["run"], r["merge_after"])


if __name__ == "__main__":
    sys.exit(main())
