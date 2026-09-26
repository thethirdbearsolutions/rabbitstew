"""RBT-92 adversary probe C readout: what the shift does to demography, and what the instrument can see.

On one throwaway seed (9902; probe_runs.sh: plain and --shift-at 150 --shift group-size=8, 230
seasons, the RBT-92 baseline command), reading history.json (alive, births, deaths, total_energy;
NOT mean_lifetime_score), lineage.jsonl (energy and age at T - 1), cohorts.jsonl (group sizes) and
the genomes (tables.py's body_structure digest).  One seed is an artifact: every line below is a
property of the instrument or the mechanism, to be checked on the real arms, not an effect size.

  1. Timing of the shift's excess deaths: cull_k.py sizes the null from [T, T+10); how much of the
     excess over [T, T+80) falls inside it, per fauna, and whether the shift's deficit is in deaths
     or in births (a sustained lower alive count that an impulse cull does not reproduce).
  2. The energy buffer at T - 1: seasons an individual survives at zero income (energy / 0.25),
     the lag between a lost income and a starvation death.
  3. Remainder groups under group-size 8: per fauna, the share of robot-seasons in groups smaller
     than 8, the sizes seen, and how often a robot forages alone.
  4. The body-structure digest's granularity: distinct digests among living holistic individuals,
     and B (fraction of the living whose digest equals a C0 ancestor's) and S on the plain arm at
     T+60, where nothing happened.

    python runs/RBT-92/adversary/probe_shift_dynamics.py > runs/RBT-92/adversary/probe_shift_dynamics.txt
"""
import collections
import importlib.util
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "data")
SEED, T = 9902, 150
KINDS = ("holistic", "conventional")


def mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def hist(run):
    return {(h["season"], h["population"]): h for h in json.load(open(os.path.join(run, "history.json")))["history"]}


def main():
    plain, shift = (os.path.join(D, f"probe-{a}-{SEED}") for a in ("plain", "shift"))
    hp, hs = hist(plain), hist(shift)
    last = min(max(s for s, _ in hp), max(s for s, _ in hs))
    print(__doc__.split("\n\n")[0])
    print(f"seed {SEED}, onset T = {T}, seasons read to {last}")
    print()
    print("1. EXCESS DEATHS AND BIRTHS, shift - plain, by window after T (both arms byte-identical before T)")
    for k in KINDS:
        g = lambda h, s, f: h.get((s, k), {}).get(f, 0)
        cum = 0
        rows = []
        for a, b in ((0, 10), (10, 20), (20, 30), (30, 40), (40, 60), (60, last - T + 1)):
            dd = sum(g(hs, s, "deaths") - g(hp, s, "deaths") for s in range(T + a, T + b))
            db = sum(g(hs, s, "births") - g(hp, s, "births") for s in range(T + a, T + b))
            cum += dd
            al = statistics.fmean(g(hs, s, "alive") - g(hp, s, "alive") for s in range(T + a, T + b))
            rows.append(f"[T+{a},T+{b}): deaths {dd:+d} births {db:+d} mean alive gap {al:+.1f}")
        k10 = max(0, sum(g(hs, s, "deaths") - g(hp, s, "deaths") for s in range(T, T + 10)))
        print(f"  {k:12s} " + ";  ".join(rows))
        print(f"  {'':12s} cull_k.py's k = {k10};  cumulative excess deaths to T+{last - T + 1}: {cum:+d};  "
              f"energy per head at T-1 {g(hp, T - 1, 'total_energy') / max(1, g(hp, T - 1, 'alive')):.2f}, "
              f"at T+30: plain {g(hp, T + 30, 'total_energy') / max(1, g(hp, T + 30, 'alive')):.2f} shift {g(hs, T + 30, 'total_energy') / max(1, g(hs, T + 30, 'alive')):.2f}")
    print()
    print("2. THE ENERGY BUFFER AT T - 1 (lineage.jsonl rows at generation T-1): seasons to starve at zero income = energy / 0.25")
    en = collections.defaultdict(list)
    with open(os.path.join(plain, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r["generation"] == T - 1 and "death" not in r:
                en[r["population"]].append(r["energy"])
    for k in KINDS:
        e = sorted(en[k])
        if not e:
            print(f"  {k}: no rows at generation {T - 1}")
            continue
        q = lambda p: e[min(len(e) - 1, int(p * len(e)))]
        print(f"  {k:12s} n={len(e)} energy median {q(0.5):.2f} (quartiles {q(0.25):.2f}..{q(0.75):.2f}); seasons to starve at zero income: "
              f"median {q(0.5) / 0.25:.0f}, {sum(1 for x in e if x / 0.25 < 10)}/{len(e)} would starve inside [T, T+10) even at zero income")
    print()
    print("3. REMAINDER GROUPS in the shift arm from T (cohorts.jsonl)")
    sizes = {k: collections.Counter() for k in KINDS}
    robot = {k: collections.Counter() for k in KINDS}
    with open(os.path.join(shift, "cohorts.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r["season"] < T:
                continue
            k = r["cohort"]
            for grp in r["groups"]:
                sizes[k][len(grp)] += 1
                robot[k][len(grp)] += len(grp)
    for k in KINDS:
        tot = sum(robot[k].values())
        small = sum(v for s, v in robot[k].items() if s < 8)
        mean = sum(s * v for s, v in robot[k].items()) / tot if tot else float("nan")
        print(f"  {k:12s} group sizes (count of groups) {dict(sorted(sizes[k].items()))}; robot-seasons in a group < 8: {small}/{tot} "
              f"({100 * small / max(1, tot):.1f}%); alone: {robot[k][1]}; robot-weighted mean group size {mean:.2f}")
    print()
    print("4. THE BODY-STRUCTURE DIGEST on the plain arm (tables.py's body_structure; readout.py's carriage)")
    tables = mod("tables", os.path.join(HERE, "..", "tables.py"))
    readout = mod("readout", os.path.join(HERE, "..", "readout.py"))
    for run in (plain, shift):
        if not os.path.exists(os.path.join(run, "bodysig.txt")):
            tables.main(run)
    A = {a: readout.Arm(run) for a, run in (("plain", plain), ("shift", shift))}
    for a in ("plain", "shift"):
        arm = A[a]
        for s in (T - 1, T + 30, T + 60, last):
            now = arm.alive_at("holistic", s)
            digs = collections.Counter(arm.body.get(("holistic", n), "-") for n in now)
            top = digs.most_common(1)[0] if digs else ("-", 0)
            print(f"  {a:5s} season {s:3d}: {len(now)} living holistic, {len(digs)} distinct body digests, the commonest carried by {top[1]}")
        for s in (T + 30, T + 60, last):
            c = arm.carriage("holistic", T, s)
            print(f"  {a:5s} carriage at T+{s - T}: L {c[0]:.3f}  B {c[1] if c[1] is None else round(c[1], 3)}  S {c[2] if c[2] is None else round(c[2], 3)}")
    # how often does a child's digest differ from its parent's?
    arm = A["plain"]
    diff = same = 0
    for (k, n), (b, l, parents) in arm.ind.items():
        if k != "holistic" or not parents or (k, n) not in arm.body:
            continue
        pb = [arm.body.get((k, p)) for p in parents]
        if arm.body[(k, n)] in pb:
            same += 1
        else:
            diff += 1
    print(f"  plain: holistic children whose digest equals a parent's: {same}/{same + diff}  (a structural change per birth: {diff}/{same + diff})")


if __name__ == "__main__":
    sys.exit(main())
