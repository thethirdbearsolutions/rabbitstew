"""RBT-90 part 2: the ten-seed readout, from the committed per-seed text files alone.

Reads, per arm ``runs/RBT-90/forage-<seed>/``: seasons.txt, lineage-last.txt, oscillator.txt,
descent.txt, lab.txt, subsystems.txt, topunit.txt, power.txt (all written by part2_analyse.py from
other tickets' unmodified instruments).  It never opens the bulk, so it prints the same thing from a
checkout that never held it.  Written and smoke-tested on a throwaway run before any arm launched.

    python runs/RBT-90/part2_readout.py [SEED ...]  > runs/RBT-90/part2-readout.txt

The rules below are the pre-registration's (RBT-90, posted before launch); they are constants here so
that the verdict is a derivation from the committed tables and not a reading of them.
"""
import json
import os
import pathlib
import re
import statistics as st
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ARMS = pathlib.Path(os.environ.get("PART2_ARMS", ROOT / "runs" / "RBT-90"))  # the override is for the smoke test only

SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
#: composite (drive, no oscillator) of the founders each arm actually runs, k of 60, from
#: docs/artifacts/RBT-90-head-founders.txt; fixed before launch.  Halves split at the generator's median, 30/60.
COMPOSITE = {801: 28, 804: 37, 805: 36, 806: 28, 807: 35, 1: 30, 2: 26, 3: 33, 4: 30, 5: 34, 7: 26}
OSC_FOUNDERS = {801: 15, 804: 11, 805: 10, 806: 18, 807: 7, 1: 8, 2: 16, 3: 16, 4: 8, 5: 14, 7: 18}
MEDIAN = 30
BAR = 2.5           #: |paired t| at n = 64 (RBT-38)
OSC_DISCARD, OSC_ACQUIRE = 2, 8   #: distinct bests carrying a linked oscillator: <= 2 discarded, >= 8 acquired (RBT-84's bars)
DEPTH_PI = (15, 26)  #: 95% t(6) prediction interval for the holistic median depth from RBT-59's seven 600-season rows
NEED = 8            #: of 10: a property of the search


def last_json(path):
    for line in reversed(path.read_text().splitlines()):
        if line.startswith("{"):
            return json.loads(line.replace("NaN", "null"))
    return None


def kind_of(desc):
    """RBT-28's drive kinds from the lab's unit description, e.g. 'part 5 effector effector dof0'."""
    t = desc.split()
    part, typ, sub = t[1], t[2], (t[3] if len(t) > 3 else "")
    if typ == "effector":
        return "effector"
    if typ == "neuron":
        return "global neuron" if part == "None" else "local neuron"
    if typ == "sensor" and sub == "oscillator":
        return "oscillator"
    return f"{typ}:{sub}"


def depth(arm, kind="holistic"):
    """Median first-parent chain length of those alive at the last season (RBT-59's depth, RBT-71's code path)."""
    recs = {}
    with open(arm / "lineage-last.txt") as f:
        f.readline()
        for line in f:
            pop, name, gen, age, evals, fit, parents = line.rstrip("\n").split("\t")
            if pop == kind:
                recs[name] = (int(gen), parents.split(",") if parents else [])
    last = max(g for g, _ in recs.values())
    ds, founders = [], set()
    for name, (g, _) in recs.items():
        if g != last:
            continue
        d, cur, seen = 0, name, set()
        while recs[cur][1] and recs[cur][1][0] in recs and cur not in seen:
            seen.add(cur)
            cur = recs[cur][1][0]
            d += 1
        ds.append(d)
        founders.add(cur)
    return {"season": last, "alive": len(ds), "median": st.median(ds), "min": min(ds), "max": max(ds), "founders": len(founders)}


def read(seed):
    arm = ARMS / f"forage-{seed}"
    lab = (arm / "lab.txt").read_text()
    o = {"seed": seed}
    m = re.search(r"intact against its own gait: ([\d.]+) items vs a null of ([\d.]+), paired t = ([+-][\d.]+|[+-]?nan) over (\d+) draws", lab)
    o["items"], o["null"], o["gait_t"], o["n"] = float(m[1]), float(m[2]), float(m[3]), int(m[4])
    o["power"] = float(re.search(r"resolves a lesion difference of ([+-][\d.]+) items", lab)[1])
    o["units"] = [(int(u), float(c), kind_of(d)) for u, c, d in re.findall(r"^\s+lesion:(\d+)\s+costs ([+-][\d.]+) items \([^)]*\)\s+(part .*)$", lab, flags=re.M)]
    sub = (arm / "subsystems.txt").read_text()
    o["t"] = {mode: (float(c), float(t), z) for mode, c, t, z in re.findall(r"^(\S+)\s+([+-][\d.]+)\s+([+-]?(?:nan|[\d.]+))\s+(\d+/\d+)\s*$", sub, flags=re.M)}
    o["failed"] = [p.name for p in arm.glob("*.txt") if "STEP FAILED" in p.read_text()]
    o["top"] = last_json(arm / "topunit.txt") if (arm / "topunit.txt").exists() else None
    o["osc"] = last_json(arm / "oscillator.txt")
    o["dag"] = last_json(arm / "descent.txt")
    o["ladder"] = last_json(arm / "power.txt")
    o["depth"] = depth(arm)
    o["depth_designed"] = depth(arm, "conventional")
    return o


def drive(o):
    """The drive kind by the lesion reading: the kind of the single most costly unit lesion (RBT-28), if that
    lesion clears the bar against intact; UNDECIDED if the runner-up is another kind and the two cannot be
    separated on the same paired seeds (RBT-84 section 5); UNRESOLVED if no unit clears the bar."""
    if not o["units"]:
        return "UNRESOLVED"
    (u1, c1, k1), rest = o["units"][0], o["units"][1:]
    t1 = o["t"].get(f"lesion:{u1}", (None, float("nan"), ""))[1]
    if not t1 >= BAR:
        return "UNRESOLVED"
    if rest and rest[0][2] != k1:
        t2 = o["t"].get(f"lesion:{rest[0][0]}", (None, float("nan"), ""))[1]
        sep = o["top"]["t"] if o["top"] and o["top"]["t"] is not None else float("nan")
        if t2 >= BAR and not abs(sep) >= BAR:
            return f"UNDECIDED ({k1} / {rest[0][2]})"
    return k1


def osc_fate(o):
    d = o["osc"]["distinct"]
    return "discarded" if d <= OSC_DISCARD else "acquired" if d >= OSC_ACQUIRE else "undecided"


def tally(rows, name, holds):
    out = []
    for label, sel in (("pooled", rows), (f"composite <= {MEDIAN}/60", [r for r in rows if COMPOSITE[r["seed"]] <= MEDIAN]), (f"composite > {MEDIAN}/60", [r for r in rows if COMPOSITE[r["seed"]] > MEDIAN])):
        k = sum(1 for r in sel if holds(r))
        out.append(f"{label}: {k} of {len(sel)}")
    k, n = sum(1 for r in rows if holds(r)), len(rows)
    verdict = "A PROPERTY OF THE SEARCH" if n == len(SEEDS) and k >= NEED else "its negation is a property of the search" if n == len(SEEDS) and n - k >= NEED else "SPLITS: a founding-population property" if n == len(SEEDS) else "incomplete set: no verdict"
    print(f"  {name}\n    {'; '.join(out)}  ->  {verdict}")


def main(seeds):
    rows = []
    for s in seeds:
        if not (ARMS / f"forage-{s}" / "lab.txt").exists():
            print(f"seed {s}: not analysed yet; a partial set is not a result and carries no verdict")
            continue
        rows.append(read(s))
    print("RBT-90 part 2: ten founding seeds under the dense foraging baseline, 600 seasons, one flag changed (the seed).")
    print("Per seed; champion = best_gen0590; lesions and the gait null at n = 64 paired draws, bar |t| >= 2.5.\n")
    print(f"{'seed':>5s} {'comp':>5s} {'osc f':>5s} | {'births':>6s} {'osc@birth':>9s} {'bests':>5s} {'osc bests':>9s} {'fate':>10s} | {'items':>5s} {'gait t':>6s} {'ladder':>6s} | {'power':>5s} {'no_osc t':>8s} {'no_glob t':>9s}  drive kind (top units)")
    for o in rows:
        osc = o["osc"]
        units = ", ".join(f"{u}:{k} {c:+.2f} t{o['t'].get(f'lesion:{u}', (0, float('nan'), ''))[1]:+.2f}" for u, c, k in o["units"][:2])
        sep = f"; top two differ by t{o['top']['t']:+.2f}" if o["top"] and o["top"]["t"] is not None else ""
        print(f"{o['seed']:5d} {COMPOSITE[o['seed']]:3d}/60 {OSC_FOUNDERS[o['seed']]:2d}/60 | {osc['births']:6d} {osc['birth_rate']:9.3f} {osc['bests']:5d} {osc['distinct']:9d} {osc_fate(o):>10s} | "
              f"{o['items']:5.2f} {o['gait_t']:+6.2f} {o['ladder']['threshold_items'] if o['ladder'] else '--':>6} | {o['power']:5.2f} {o['t'].get('no_osc', (0, float('nan'), ''))[1]:+8.2f} {o['t'].get('no_global', (0, float('nan'), ''))[1]:+9.2f}  "
              f"{drive(o)} ({units}{sep})" + (f"  FAILED STEPS: {o['failed']}" if o["failed"] else ""))
    print(f"\n{'seed':>5s} | depth holistic median (min-max) founders | designed | champion DAG: ancestors founders crossover-steps missing")
    for o in rows:
        d, c, g = o["depth"], o["depth_designed"], o["dag"]
        print(f"{o['seed']:5d} | {d['median']:5.1f} ({d['min']}-{d['max']}) {d['founders']:2d} at season {d['season']} | {c['median']:5.1f} ({c['min']}-{c['max']}) | {g['ancestors']:4d} {g['founders']:3d} {g['crossover_steps']:4d} {g['genomes_missing']:3d}")
    print(f"\nRegularities, by the pre-registered rule (holds on >= {NEED} of 10: a property of the search; otherwise it splits):")
    tally(rows, "no champion beats its own gait (paired t < +2.5 against its trajectory-preserving null)", lambda r: not r["gait_t"] >= BAR)
    tally(rows, "the champion's drive kind is an effector (lesion reading)", lambda r: drive(r) == "effector")
    tally(rows, "the champion's drive is not an oscillator (no_osc |t| < 2.5 and the top unit is no oscillator)", lambda r: not abs(r["t"].get("no_osc", (0, 0.0, ""))[1]) >= BAR and drive(r) != "oscillator")
    tally(rows, f"oscillator drive is discarded (<= {OSC_DISCARD} distinct bests carry a linked oscillator)", lambda r: osc_fate(r) == "discarded")
    tally(rows, f"oscillator drive is acquired (>= {OSC_ACQUIRE} distinct bests)", lambda r: osc_fate(r) == "acquired")
    tally(rows, f"holistic median depth inside the prediction interval {list(DEPTH_PI)}", lambda r: DEPTH_PI[0] <= r["depth"]["median"] <= DEPTH_PI[1])
    births = [(OSC_FOUNDERS[r["seed"]] / 60, r["osc"]["birth_rate"]) for r in rows]
    if len(births) > 2:
        mx, my = st.mean(x for x, _ in births), st.mean(y for _, y in births)
        sxy = sum((x - mx) * (y - my) for x, y in births)
        sxx, syy = sum((x - mx) ** 2 for x, _ in births), sum((y - my) ** 2 for _, y in births)
        print(f"\n  founders' linked-oscillator rate against the rate at birth over the run: r = {sxy / (sxx * syy) ** 0.5 if sxx and syy else float('nan'):+.2f} over {len(births)} seeds (reported, not ruled on)")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or SEEDS)
