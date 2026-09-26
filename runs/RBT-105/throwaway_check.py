"""RBT-105: the throwaway's three claims about --breed-stream, checked on the bulk against the seed's RBT-90 arm.

    python runs/RBT-105/throwaway_check.py RBT90_ARM SEED ARM_b0 ARM_b1 [ARM_b2 ...]

1. season 0: every arm's founders (genome files, which carry the staggered ages) are byte-identical to the
   RBT-90 arm's, and match the committed fingerprint in founders-rbt90.txt;
2. K = 0 reproduces the RBT-90 arm: lineage.jsonl and cohorts.jsonl, every line of the seasons the throwaway
   ran, byte for byte;
3. K >= 1 diverges: its holistic lines differ (the first differing season is printed), two replicates differ
   from each other, and the designed-body lines and the worlds (terrain and start seeds) stay byte-identical.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import founders  # noqa: E402


def lines(run, name, key, upto, kind=None):
    out = []
    for l in (pathlib.Path(run) / name).read_bytes().splitlines():
        r = json.loads(l)
        if r[key] < upto and (kind is None or r.get("population", r.get("cohort")) == kind):
            out.append(l)
    return out


def worlds(run, upto):
    hist = json.loads((pathlib.Path(run) / "history.json").read_text())["history"]
    return [(e["season"], e["population"], e["terrain_seed"], e["start_seed"]) for e in hist if e["season"] < upto]


def first_diff(a, b, key):
    for x, y in zip(a, b):
        if x != y:
            return json.loads(x)[key]
    return None if len(a) == len(b) else "length"


def main(base, seed, arms):
    base = pathlib.Path(base)
    ref = {l.split()[0]: l.split(" ", 1)[1] for l in (HERE / "founders-rbt90.txt").read_text().splitlines() if not l.startswith("#")}
    ok = True

    def check(label, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")

    base_fp = founders.line(base, seed).split(" ", 1)[1]
    print(f"RBT-105 throwaway: seed {seed}, against {base.name} (the RBT-90 part 2 arm restored from ckpt/rbt-90-{seed})")
    check(f"the restored RBT-90 arm's founders match the committed fingerprint (founders-rbt90.txt)", base_fp == ref[seed])
    hol = {}
    for arm in map(pathlib.Path, arms):
        cfg = json.loads((arm / "config.json").read_text())
        k, n = cfg["ecology"].get("breed_stream"), cfg["ecology"]["seasons"]
        print(f"\n{arm.name}: breed_stream {k}, {n} seasons")
        check("1. founders' genome files (genotypes, names, ages) byte-identical to the RBT-90 arm's at season 0",
              founders.line(arm, seed).split(" ", 1)[1] == base_fp)
        for name, key in (("lineage.jsonl", "generation"), ("cohorts.jsonl", "season")):
            a, b = lines(arm, name, key, n), lines(base, name, key, n)
            print(f"      {name}: {len(a)} lines in the arm, {len(b)} in the RBT-90 arm's first {n} seasons")
        la, lb = lines(arm, "lineage.jsonl", "generation", n), lines(base, "lineage.jsonl", "generation", n)
        ca, cb = lines(arm, "cohorts.jsonl", "season", n), lines(base, "cohorts.jsonl", "season", n)
        check("   the worlds (terrain and start seeds, both fauna) identical", worlds(arm, n) == worlds(base, n))
        con = lambda run, nm, key: lines(run, nm, key, n, "conventional")
        check("   designed-body lineage and cohort lines byte-identical",
              con(arm, "lineage.jsonl", "generation") == con(base, "lineage.jsonl", "generation") and con(arm, "cohorts.jsonl", "season") == con(base, "cohorts.jsonl", "season"))
        h_a, h_b = lines(arm, "lineage.jsonl", "generation", n, "holistic"), lines(base, "lineage.jsonl", "generation", n, "holistic")
        hol[k] = h_a
        if not k:
            check("2. K = 0 reproduces the RBT-90 arm: lineage.jsonl byte for byte", la == lb)
            check("   and cohorts.jsonl byte for byte", ca == cb)
        else:
            d = first_diff(h_a, h_b, "generation")
            check(f"3. K = {k} diverges: holistic lineage lines differ from the RBT-90 arm's (first differing season: {d})", h_a != h_b)
            dc = first_diff(lines(arm, "cohorts.jsonl", "season", n, "holistic"), lines(base, "cohorts.jsonl", "season", n, "holistic"), "season")
            print(f"      holistic cohort (grouping) lines: first differing season {dc}")
            births = lambda ls: sorted(json.loads(x)["name"] for x in ls if json.loads(x)["parents"])
            print(f"      holistic births named alike in the arm and the RBT-90 arm: {len(set(births(h_a)))} vs {len(set(births(h_b)))} names;"
                  f" identical lineage lines among them: {len(set(x for x in h_a if json.loads(x)['parents']) & set(x for x in h_b if json.loads(x)['parents']))}")
    reps = [k for k in hol if k]
    if len(reps) >= 2:
        check(f"3. two replicate streams ({reps[0]}, {reps[1]}) are two histories", hol[reps[0]] != hol[reps[1]])
    print(f"\n{'ALL PASS' if ok else 'SOME CHECK FAILED'}")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1], sys.argv[2], sys.argv[3:]) else 1)
