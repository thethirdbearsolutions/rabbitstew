"""RBT-100 (C3) shared-baseline check: RBT-92's shared_baseline_check.py with C3's manipulation check.

Is a C3 shift arm (--shift-at 10 --shift food-items=6) byte-identical to the same seed's plain baseline
before the event season, so that RBT-90 part 2's arm can serve as C3's no-event baseline too?  The
comparison (lineage.jsonl, cohorts.jsonl, history.json and born-genomes, byte for byte before season 10)
is RBT-92's own code, imported; only the manipulation check differs, because C1's (groups of eight at the
event) does not apply to a change in the item count:

  - every history entry of the shift arm from season 10 on, and none before, carries
    shift = {"at": 10, "flag": "food.items", "value": 6}; the plain arm carries none;
  - config.json differs from plain in the ecology's shift and shift_at fields only;
  - the arena groups are fours in both arms at 9 and 10 (the item count, not the group size, changed);
  - printed, not asserted: the mean items eaten per individual-season in lineage.jsonl over [0, 10) and
    [10, 20), per arm and fauna (a 20-season throwaway on random founders, which eat almost nothing:
    read for nothing, printed only to show which column the halving would appear in).

The cull arm of the same short runs is checked as RBT-92 checks it (20 per fauna at season 10).

  python runs/RBT-100/shared_baseline_check.py [DATA_DIR] [SEED] > runs/RBT-100/shared_baseline_check.txt
"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("sbc92", os.path.join(HERE, "..", "RBT-92", "shared_baseline_check.py"))
S = importlib.util.module_from_spec(spec)
argv, sys.argv = sys.argv, sys.argv[:1]  # RBT-92's module reads DATA and SEED from argv at import
spec.loader.exec_module(S)
sys.argv = argv
DATA = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-100/data"
SEED = sys.argv[2] if len(sys.argv) > 2 else "801"
EVENT, K = S.EVENT, S.K
WANT = {"at": EVENT, "flag": "food.items", "value": 6}


def main():
    runs = {a: os.path.join(DATA, f"sbc-{a}-{SEED}") for a in ("plain", "shift", "cull")}
    ok, out = True, []
    P = {f: {a: S.prefix(os.path.join(r, f), key) for a, r in runs.items()}
         for f, key in (("lineage.jsonl", "generation"), ("cohorts.jsonl", "season"))}
    H = {a: json.load(open(os.path.join(r, "history.json")))["history"] for a, r in runs.items()}
    early = sorted(S.born_before(runs["plain"]))
    for arm in ("shift", "cull"):
        out.append(f"== {arm} arm against plain, seed {SEED}, event at season {EVENT}")
        for f, key in (("lineage.jsonl", "generation"), ("cohorts.jsonl", "season")):
            a, b = P[f][arm], P[f]["plain"]
            same = a[0] == b[0]
            ok &= same and a[2] == 0 and b[2] == 0
            out.append(f"  {f:14s} lines with season < {EVENT}: {len(a[0])} vs {len(b[0])}; byte-identical: {same}; "
                       f"sha256 {hashlib.sha256(b''.join(a[0])).hexdigest()[:16]} vs {hashlib.sha256(b''.join(b[0])).hexdigest()[:16]}; "
                       f"out-of-order early lines {a[2]}/{b[2]}; first differing season over the whole file: {S.first_diff(a[1], b[1], key)}")
        ha = [h for h in H[arm] if h["season"] < EVENT]
        hb = [h for h in H["plain"] if h["season"] < EVENT]
        same = json.dumps(ha, sort_keys=True) == json.dumps(hb, sort_keys=True)
        ok &= same
        fd = next((x["season"] for x, y in zip(H[arm], H["plain"]) if json.dumps(x, sort_keys=True) != json.dumps(y, sort_keys=True)), None)
        out.append(f"  {'history.json':14s} entries with season < {EVENT}: {len(ha)} vs {len(hb)}; identical: {same}; first differing season: {fd}")
        pa, pb = [], []
        for pop, name in early:
            x = os.path.join(runs[arm], pop, "genomes", f"{name}.json")
            y = os.path.join(runs["plain"], pop, "genomes", f"{name}.json")
            if os.path.exists(y):
                pa.append(x)
                pb.append(y)
        missing = [p for p in pa if not os.path.exists(p)]
        same = not missing and all(open(x, "rb").read() == open(y, "rb").read() for x, y in zip(pa, pb))
        ok &= same and len(pb) > 0
        out.append(f"  genomes of individuals born before {EVENT}: {len(pb)} files; byte-identical: {same}; missing in arm: {len(missing)}")
    base_cfg = json.load(open(os.path.join(runs["plain"], "config.json")))
    for arm, want in (("shift", ["shift", "shift_at"]), ("cull", ["cull", "cull_at"])):
        cfg = json.load(open(os.path.join(runs[arm], "config.json")))
        diff = sorted(k for k in set(cfg) | set(base_cfg) if cfg.get(k) != base_cfg.get(k))
        eco = sorted(k for k in set(cfg.get("ecology", {})) | set(base_cfg.get("ecology", {}))
                     if cfg.get("ecology", {}).get(k) != base_cfg.get("ecology", {}).get(k))
        ok &= diff in ([], ["ecology"]) and eco == want
        out.append(f"  config.json {arm} vs plain: top-level fields differing {diff}; ecology fields differing {eco} (expected {want}); "
                   f"shift {cfg.get('ecology', {}).get('shift')!r} at {cfg.get('ecology', {}).get('shift_at')!r}")
    # manipulation, C3
    marks = sorted({h["season"] for h in H["shift"] if "shift" in h})
    vals = {json.dumps(h["shift"], sort_keys=True) for h in H["shift"] if "shift" in h}
    good = bool(marks) and marks[0] == EVENT and marks == list(range(EVENT, max(h["season"] for h in H["shift"]) + 1)) \
        and vals == {json.dumps(WANT, sort_keys=True)} and not any("shift" in h for h in H["plain"])
    ok &= good
    out.append(f"  manipulation: shift arm history entries carrying shift: seasons {marks[0] if marks else None}..{marks[-1] if marks else None} "
               f"({len(marks)} seasons), values {sorted(vals)}; plain arm entries carrying shift: {sum('shift' in h for h in H['plain'])}: {'ok' if good else 'FAIL'}")
    coh = {a: [json.loads(l) for l in S.lines(os.path.join(r, "cohorts.jsonl"))] for a, r in runs.items()}
    for arm in ("plain", "shift"):
        for s in (EVENT - 1, EVENT):
            sizes = sorted({len(g) for c in coh[arm] if c["season"] == s for g in c["groups"]})
            ok &= max(sizes) == 4 if sizes else False
            out.append(f"  manipulation: {arm} arm group sizes at season {s}: {sizes} (fours in both: the group size is not the flag)")
    for arm in ("plain", "shift"):
        cells = []
        for pop in ("holistic", "conventional"):
            for lo, hi in ((0, EVENT), (EVENT, 2 * EVENT)):
                v = [json.loads(l).get("food", 0.0) for l in S.lines(os.path.join(runs[arm], "lineage.jsonl"))
                     if json.loads(l)["population"] == pop and lo <= json.loads(l)["generation"] < hi]
                cells.append(f"{pop} [{lo},{hi}) {sum(v) / len(v) if v else float('nan'):.4f} over {len(v)} rows")
        out.append(f"  printed only (founders, read for nothing): mean items eaten per lineage row, {arm}: " + "; ".join(cells))
    culls = {}
    for l in S.lines(os.path.join(runs["cull"], "lineage.jsonl")):
        r = json.loads(l)
        if r.get("death") == "cull":
            culls[(r["population"], r["generation"])] = culls.get((r["population"], r["generation"]), 0) + 1
    out.append(f"  manipulation: cull arm 'death: cull' rows by (fauna, season): {culls}")
    ok &= culls == {("holistic", EVENT): K, ("conventional", EVENT): K}
    out.append("")
    out.append(f"VERDICT: PASS -- the C3 shift arm and the cull arm are byte-identical to the plain baseline before season {EVENT} "
               f"in lineage.jsonl, cohorts.jsonl, history.json and born-genomes; food.items = 6 is in force from season {EVENT}, "
               f"groups stay at four" if ok else "VERDICT: FAIL -- see the lines above")
    print("\n".join(out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
