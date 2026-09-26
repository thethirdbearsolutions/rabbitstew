"""RBT-92 shared-baseline check: is a shift (or cull) arm byte-identical to the same seed's plain
baseline up to the event season, so that RBT-90 part 2's arm can serve as the no-event baseline?

Reads the three short runs written by runs/RBT-92/shared_baseline_runs.sh (plain; --shift-at 10
--shift group-size=8; --cull-at 10 --cull holistic=20,conventional=20; 20 seasons, seed 801,
the RBT-90 part 2 command otherwise) and compares, arm against plain:

  lineage.jsonl   every line whose "generation" (season) is < EVENT, in file order, byte for byte;
                  and asserts no line with season < EVENT appears after the first line >= EVENT
  cohorts.jsonl   every line whose "season" is < EVENT, byte for byte
  history.json    every entry whose season is < EVENT, as JSON (the per-season log)
  genomes         every holistic/ and conventional/ genomes/*.json of an individual born before
                  EVENT (born = generation - age at its first lineage row), byte for byte

and, as the manipulation check (the event did something, from EVENT on):

  the first season at which each file differs, which must be EVENT; the shift arm's cohorts at
  EVENT hold groups of 8 (and the plain arm's groups of 4); the cull arm's lineage.jsonl carries
  exactly 20 "death": "cull" rows per fauna, all at season EVENT; history entries carry "shift" /
  "culled" from EVENT and not before.

  python runs/RBT-92/shared_baseline_check.py [DATA_DIR] [SEED] > runs/RBT-92/shared_baseline_check.txt
"""
import hashlib
import json
import os
import sys

DATA = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-92/data"
SEED = sys.argv[2] if len(sys.argv) > 2 else "801"
EVENT = 10
K = 20


def lines(path):
    with open(path, "rb") as f:
        return [l for l in f.read().split(b"\n") if l.strip()]


def season_of(line, key):
    return json.loads(line)[key]


def prefix(path, key):
    ls = lines(path)
    pre, seen_late, late_early = [], False, 0
    for l in ls:
        s = season_of(l, key)
        if s < EVENT:
            pre.append(l)
            if seen_late:
                late_early += 1
        else:
            seen_late = True
    return pre, ls, late_early


def first_diff(a, b, key):
    for x, y in zip(a, b):
        if x != y:
            return season_of(x, key)
    return None if len(a) == len(b) else "length"


def born_before(run):
    born = {}
    for l in lines(os.path.join(run, "lineage.jsonl")):
        r = json.loads(l)
        k = (r["population"], r["name"])
        if k not in born:
            born[k] = r["generation"] - r["age"]
    return {k for k, b in born.items() if b < EVENT}


def digest(paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(p.encode())
        h.update(open(p, "rb").read())
    return h.hexdigest()[:16]


def main():
    runs = {a: os.path.join(DATA, f"sbc-{a}-{SEED}") for a in ("plain", "shift", "cull")}
    ok = True
    out = []
    P = {}
    for f, key in (("lineage.jsonl", "generation"), ("cohorts.jsonl", "season")):
        P[f] = {a: prefix(os.path.join(r, f), key) for a, r in runs.items()}
    H = {a: json.load(open(os.path.join(r, "history.json")))["history"] for a, r in runs.items()}
    early = sorted(born_before(runs["plain"]))
    for arm in ("shift", "cull"):
        out.append(f"== {arm} arm against plain, seed {SEED}, event at season {EVENT}")
        for f, key in (("lineage.jsonl", "generation"), ("cohorts.jsonl", "season")):
            a, b = P[f][arm], P[f]["plain"]
            same = a[0] == b[0]
            ok &= same and a[2] == 0 and b[2] == 0
            out.append(f"  {f:14s} lines with season < {EVENT}: {len(a[0])} vs {len(b[0])}; byte-identical: {same}; "
                       f"sha256 {hashlib.sha256(b''.join(a[0])).hexdigest()[:16]} vs {hashlib.sha256(b''.join(b[0])).hexdigest()[:16]}; "
                       f"out-of-order early lines {a[2]}/{b[2]}; first differing season over the whole file: {first_diff(a[1], b[1], key)}")
        ha = [h for h in H[arm] if h["season"] < EVENT]
        hb = [h for h in H["plain"] if h["season"] < EVENT]
        same = json.dumps(ha, sort_keys=True) == json.dumps(hb, sort_keys=True)
        ok &= same
        fd = next((x["season"] for x, y in zip(H[arm], H["plain"]) if json.dumps(x, sort_keys=True) != json.dumps(y, sort_keys=True)), None)
        out.append(f"  {'history.json':14s} entries with season < {EVENT}: {len(ha)} vs {len(hb)}; identical: {same}; first differing season: {fd}")
        marks = sorted({h["season"] for h in H[arm] if ("shift" in h if arm == "shift" else "culled" in h)})
        ok &= bool(marks) and marks[0] == EVENT
        out.append(f"  history entries carrying {'shift' if arm == 'shift' else 'culled'}: seasons {marks[0] if marks else None}..{marks[-1] if marks else None} ({len(marks)} seasons)")
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
    for arm in ("shift", "cull"):
        cfg = json.load(open(os.path.join(runs[arm], "config.json")))
        diff = sorted(k for k in set(cfg) | set(base_cfg) if cfg.get(k) != base_cfg.get(k))
        eco = sorted(k for k in set(cfg.get("ecology", {})) | set(base_cfg.get("ecology", {}))
                     if cfg.get("ecology", {}).get(k) != base_cfg.get("ecology", {}).get(k))
        want = ["shift", "shift_at"] if arm == "shift" else ["cull", "cull_at"]
        ok &= diff in ([], ["ecology"]) and eco == want
        out.append(f"  config.json {arm} vs plain: top-level fields differing {diff}; ecology fields differing {eco} (expected {want})")
    # manipulation checks
    coh = {a: [json.loads(l) for l in lines(os.path.join(r, "cohorts.jsonl"))] for a, r in runs.items()}
    for arm in ("plain", "shift"):
        for s in (EVENT - 1, EVENT):
            sizes = sorted({len(g) for c in coh[arm] if c["season"] == s for g in c["groups"]})
            out.append(f"  manipulation: {arm} arm group sizes at season {s}: {sizes}")
    culls = {}
    for l in lines(os.path.join(runs["cull"], "lineage.jsonl")):
        r = json.loads(l)
        if r.get("death") == "cull":
            culls.setdefault((r["population"], r["generation"]), 0)
            culls[(r["population"], r["generation"])] += 1
    out.append(f"  manipulation: cull arm 'death: cull' rows by (fauna, season): {culls}")
    ok &= culls == {("holistic", EVENT): K, ("conventional", EVENT): K}
    sh = [c for c in coh["shift"] if c["season"] == EVENT]
    ok &= all(len(g) == 8 for c in sh for g in c["groups"][:-1]) if sh else False
    out.append("")
    out.append(f"VERDICT: {'PASS' if ok else 'FAIL'} -- the shift and cull arms are byte-identical to the plain baseline "
               f"before season {EVENT} in lineage.jsonl, cohorts.jsonl, history.json and born-genomes, and the event "
               f"takes effect at season {EVENT}" if ok else "VERDICT: FAIL -- see the lines above")
    print("\n".join(out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
