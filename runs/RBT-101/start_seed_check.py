"""RBT-101 start-seed check: does a C4 arm (--shift-at T --shift terrain=flat) keep the control's start seeds
after the onset, as RBT-95's amendment says it should?

RBT-92's shared-baseline check (runs/RBT-92/shared_baseline_check.py) established byte identity BEFORE the
event for a crowding shift and a cull.  A terrain shift is the one event that touches the terrain stream,
which feeds each season's terrain seed and start seed (rabbitstew/ecology.py, the season step): before
RBT-95's amendment a flat season drew no terrain seed, so the shift arm's start seeds fell one draw behind
the control's from the onset.  This extends the check PAST the event, for what the terrain stream feeds.

Reads the two short runs written by runs/RBT-101/start_seed_runs.sh (plain; --shift-at 10 --shift
terrain=flat; 20 seasons; RBT-90 part 2's command otherwise) and reports:

  prefix, as RBT-92's check: lineage.jsonl, cohorts.jsonl and history.json byte/JSON-identical before 10,
      and the first season each differs
  start seeds, every season 0..19: history.json start_seed per fauna and cohorts.jsonl start_seed per
      cohort, flat against plain; must be equal in EVERY season, after the onset included
  terrain seeds: equal before 10; from 10 the flat arm records None (no terrain drawn into the world)
      while the plain arm records the draw, which must be the same stream position either way
  cohorts past the onset: group sizes per season (must match wherever the member counts match), and the first season at which the
      seat assignments (names) differ; they are drawn from each fauna's own stream and may diverge only
      once a death or birth differs, which the terrain can cause
  config: the arms differ only in ecology.shift and ecology.shift_at

  python runs/RBT-101/start_seed_check.py [DATA_DIR] [SEED] > runs/RBT-101/start_seed_check.txt
"""
import hashlib
import json
import os
import sys

DATA = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-101/data"
SEED = sys.argv[2] if len(sys.argv) > 2 else "801"
EVENT = 10


def lines(path):
    with open(path, "rb") as f:
        return [l for l in f.read().split(b"\n") if l.strip()]


def main():
    runs = {a: os.path.join(DATA, f"ssc-{a}-{SEED}") for a in ("plain", "flat")}
    ok = True
    out = [f"== flat arm (--shift-at {EVENT} --shift terrain=flat) against plain, seed {SEED}"]
    # prefix identity, as RBT-92's check
    for f, key in (("lineage.jsonl", "generation"), ("cohorts.jsonl", "season")):
        L = {a: lines(os.path.join(r, f)) for a, r in runs.items()}
        pre = {a: [l for l in L[a] if json.loads(l)[key] < EVENT] for a in L}
        same = pre["flat"] == pre["plain"]
        fd = next((json.loads(x)[key] for x, y in zip(L["flat"], L["plain"]) if x != y), None)
        ok &= same
        out.append(f"  {f:14s} lines with season < {EVENT}: {len(pre['flat'])} vs {len(pre['plain'])}; byte-identical: {same}; "
                   f"sha256 {hashlib.sha256(b''.join(pre['flat'])).hexdigest()[:16]} vs {hashlib.sha256(b''.join(pre['plain'])).hexdigest()[:16]}; "
                   f"first differing line's season: {fd}")
    H = {a: json.load(open(os.path.join(r, "history.json")))["history"] for a, r in runs.items()}
    hpre = {a: [h for h in H[a] if h["season"] < EVENT] for a in H}
    same = json.dumps(hpre["flat"], sort_keys=True) == json.dumps(hpre["plain"], sort_keys=True)
    ok &= same
    out.append(f"  {'history.json':14s} entries with season < {EVENT}: {len(hpre['flat'])} vs {len(hpre['plain'])}; identical: {same}")
    marks = sorted({h["season"] for h in H["flat"] if "shift" in h})
    ok &= bool(marks) and marks[0] == EVENT
    out.append(f"  history entries carrying shift: seasons {marks[0] if marks else None}..{marks[-1] if marks else None}; "
               f"value {next((h['shift'] for h in H['flat'] if 'shift' in h), None)}")
    # start and terrain seeds, every season
    idx = {a: {(h["season"], h["population"]): h for h in H[a]} for a in H}
    seasons = sorted({s for s, _ in idx["plain"]} & {s for s, _ in idx["flat"]})
    out.append(f"  seasons present in both arms: {seasons[0]}..{seasons[-1]} ({len(seasons)})")
    out.append("  season  start_seed plain / flat (history, both faunas)          terrain_seed plain / flat")
    ss_bad = ts_bad = 0
    for s in seasons:
        sp = {idx["plain"][(s, k)]["start_seed"] for k in ("holistic", "conventional") if (s, k) in idx["plain"]}
        sf = {idx["flat"][(s, k)]["start_seed"] for k in ("holistic", "conventional") if (s, k) in idx["flat"]}
        tp = {idx["plain"][(s, k)]["terrain_seed"] for k in ("holistic", "conventional") if (s, k) in idx["plain"]}
        tf = {idx["flat"][(s, k)]["terrain_seed"] for k in ("holistic", "conventional") if (s, k) in idx["flat"]}
        s_ok = sp == sf and len(sp) == 1
        t_ok = (tp == tf) if s < EVENT else (tf == {None} and None not in tp)
        ss_bad += not s_ok
        ts_bad += not t_ok
        out.append(f"  {s:6d}  {sorted(sp)} / {sorted(sf)}  {'same' if s_ok else 'DIFFER'}      {sorted(tp, key=str)} / {sorted(tf, key=str)}  "
                   f"{'as expected' if t_ok else 'UNEXPECTED'}")
    ok &= ss_bad == 0 and ts_bad == 0
    out.append(f"  history start seeds equal in {len(seasons) - ss_bad}/{len(seasons)} seasons "
               f"(of them {sum(1 for s in seasons if s >= EVENT)} at or after the onset); terrain seeds as expected in {len(seasons) - ts_bad}/{len(seasons)}")
    # cohorts: start seeds, sizes, membership
    C = {a: [json.loads(l) for l in lines(os.path.join(r, "cohorts.jsonl"))] for a, r in runs.items()}
    ck = {a: {(c["season"], c["cohort"]): c for c in C[a]} for a in C}
    keys = sorted(set(ck["plain"]) & set(ck["flat"]))
    cs_bad = size_bad = size_same_n = 0
    first_members = None
    same_members = 0
    for key in keys:
        p, f = ck["plain"][key], ck["flat"][key]
        cs_bad += p["start_seed"] != f["start_seed"]
        # group sizes follow from how many are alive; the terrain may change that after the onset, so sizes
        # must match exactly where the member counts match (the grouping rule is the same)
        if sum(map(len, p["groups"])) == sum(map(len, f["groups"])):
            size_same_n += 1
            size_bad += [len(g) for g in p["groups"]] != [len(g) for g in f["groups"]]
        if p["groups"] == f["groups"]:
            same_members += 1
        elif first_members is None or key[0] < first_members:
            first_members = key[0]
    ok &= cs_bad == 0 and size_bad == 0 and len(keys) == len(ck["plain"]) == len(ck["flat"])
    post = [k for k in keys if k[0] >= EVENT]
    out.append(f"  cohorts.jsonl: {len(keys)} (season, cohort) rows in both arms ({len(ck['plain'])} plain, {len(ck['flat'])} flat); "
               f"start_seed equal in {len(keys) - cs_bad}/{len(keys)} ({len(post) - sum(ck['plain'][k]['start_seed'] != ck['flat'][k]['start_seed'] for k in post)}/{len(post)} after the onset); "
               f"group sizes equal in {size_same_n - size_bad}/{size_same_n} rows with equal member counts "
               f"({len(keys) - size_same_n} rows differ in member count, all at or after the onset: "
               f"{all(k[0] >= EVENT for k in keys if sum(map(len, ck['plain'][k]['groups'])) != sum(map(len, ck['flat'][k]['groups'])))})")
    out.append(f"  cohorts.jsonl seat assignments identical in {same_members}/{len(keys)} rows; first season they differ: {first_members} "
               f"(from each fauna's own stream; they may diverge once a death or birth differs, which is the challenge acting)")
    L = {a: [json.loads(l) for l in lines(os.path.join(r, "lineage.jsonl"))] for a, r in runs.items()}
    for a in L:
        d = {}
        for r in L[a]:
            d[r["generation"]] = d.get(r["generation"], 0) + 1
        L[a] = d
    fdl = next((s for s in sorted(L["plain"]) if L["plain"][s] != L["flat"].get(s)), None)
    out.append(f"  first season the lineage row counts differ: {fdl}")
    base_cfg = json.load(open(os.path.join(runs["plain"], "config.json")))
    cfg = json.load(open(os.path.join(runs["flat"], "config.json")))
    diff = sorted(k for k in set(cfg) | set(base_cfg) if cfg.get(k) != base_cfg.get(k))
    eco = sorted(k for k in set(cfg["ecology"]) | set(base_cfg["ecology"]) if cfg["ecology"].get(k) != base_cfg["ecology"].get(k))
    ok &= diff in ([], ["ecology"]) and eco == ["shift", "shift_at"]
    out.append(f"  config.json flat vs plain: top-level fields differing {diff}; ecology fields differing {eco}")
    out.append("")
    out.append(f"VERDICT: {'PASS' if ok else 'FAIL'} -- " + (
        f"the flat arm is identical to plain before season {EVENT}, and after it keeps plain's start seed in every season "
        f"(history and cohorts), records no terrain seed, and groups by the same rule; the arms share start positions throughout"
        if ok else "see the lines above"))
    print("\n".join(out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
