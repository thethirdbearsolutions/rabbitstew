"""RBT-105: founders or history?  The pre-registered rule, applied to the committed per-arm files alone.

Reads, per replicate arm ``runs/RBT-105/forage-<seed>-b<K>/``: oscillator.txt (RBT-84 oscillator_rate.py's
last JSON line, "distinct"), pairing.txt, and EXTINCT.txt if present; and, per seed, the original arm's
committed ``runs/RBT-90/forage-<seed>/oscillator.txt`` (the K = 0 stream).  The count, its bars and the
fate function are imported from runs/RBT-90/part2_readout.py unchanged, so the fate is read exactly as
RBT-90 part 2 read it.  It never opens the bulk.

    python runs/RBT-105/readout.py  > runs/RBT-105/readout.txt

The rule (PREREGISTRATION.md section 3), fixed before any arm:
  per seed   FLIPS       a replicate's fate is decided and opposite to the original's
             REPLICATES  every replicate is decided and equal to the original
             UNCLEAR     anything else (a replicate in 3-7, or extinct, and none flips)
  overall    HISTORY                 >= 1 seed FLIPS: the same founders reach both fates
             FOUNDING POPULATION     no seed flips, every seed REPLICATES, and the replicating seeds hold
                                     >= 2 discarded and >= 2 acquired founding populations
             NOT DECIDED at this n   anything else
  gate       no verdict unless the positive control (K = 0) reproduced its RBT-90 arm byte for byte and every
             K >= 1 arm kept its founders and its designed-body fauna identical (pairing.txt)
"""
import importlib.util
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ARMS = pathlib.Path(os.environ.get("RBT105_ARMS", HERE))  #: the override is for the smoke test only
spec = importlib.util.spec_from_file_location("part2", ROOT / "runs" / "RBT-90" / "part2_readout.py")
part2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(part2)
OSC_DISCARD, OSC_ACQUIRE, osc_fate = part2.OSC_DISCARD, part2.OSC_ACQUIRE, part2.osc_fate

#: the pre-registered design (PREREGISTRATION.md section 2): wave 1, and wave 2 only if wave 1 is not HISTORY
WAVE1 = {7: (1, 2), 805: (1, 2), 4: (1, 2), 807: (1, 2)}
WAVE2 = {806: (1, 2), 2: (1, 2), 1: (1, 2), 804: (1, 2)}
CONTROL = (7, 0)   #: the positive control arm (seed, K)
NEED_EACH = 2      #: replicating founding populations of each fate a FOUNDING POPULATION verdict needs
OPPOSITE = {"discarded": "acquired", "acquired": "discarded"}


def arm_dir(seed, k):
    return ARMS / f"forage-{seed}-b{k}"


def fate_of(path):
    """(distinct, fate) from an oscillator.txt, or (None, 'extinct'/'missing')."""
    d = path.parent
    if (d / "EXTINCT.txt").exists():
        return None, "extinct"
    if not path.exists():
        return None, "missing"
    osc = part2.last_json(path)
    return osc["distinct"], osc_fate({"osc": osc})


def winners(arm):
    """The founders the living at the last season trace to by first parent, with counts (reported only)."""
    recs = {}
    with open(arm / "lineage-last.txt") as f:
        f.readline()
        for line in f:
            pop, name, gen, age, evals, fit, parents = line.rstrip("\n").split("\t")
            if pop == "holistic":
                recs[name] = (int(gen), parents.split(",") if parents else [])
    last = max(g for g, _ in recs.values())
    out = {}
    for name, (g, _) in recs.items():
        if g != last:
            continue
        cur, seen = name, set()
        while recs[cur][1] and recs[cur][1][0] in recs and cur not in seen:
            seen.add(cur)
            cur = recs[cur][1][0]
        out[cur] = out.get(cur, 0) + 1
    return " ".join(f"{n} x{c}" for n, c in sorted(out.items(), key=lambda x: -x[1]))


def pairing_ok(seed, k):
    p = arm_dir(seed, k) / "pairing.txt"
    if not p.exists():
        return None
    t = p.read_text()
    need = ["founders (genomes and ages at season 0) identical to the RBT-90 arm: True", "designed-body seasons.txt rows identical over the arm's 600 seasons: True"]
    if k == 0:
        need += ["seasons.txt byte-identical to the RBT-90 arm's committed file: True", "lineage-last.txt byte-identical to the RBT-90 arm's committed file: True"]
    return all(n in t for n in need)


def main():
    design = dict(WAVE1)
    wave2_ran = any(arm_dir(s, k).exists() for s, ks in WAVE2.items() for k in ks)
    if wave2_ran:
        design.update(WAVE2)
    print("RBT-105: oscillator fate from the same founders under replicate breeding streams (--breed-stream K).")
    print(f"Fate as RBT-90 part 2 reads it: distinct saved bests carrying a linked oscillator, <= {OSC_DISCARD} discarded, >= {OSC_ACQUIRE} acquired, 3-7 undecided.")
    print(f"Design: wave 1 {sorted(WAVE1)}" + (f", wave 2 {sorted(WAVE2)}" if wave2_ran else " (wave 2 not run)") + f"; positive control seed {CONTROL[0]} K = {CONTROL[1]}.\n")
    gate, missing = [], []
    ok = pairing_ok(*CONTROL)
    print(f"positive control forage-{CONTROL[0]}-b{CONTROL[1]}: " + {None: "NOT RUN", True: "reproduces the RBT-90 arm byte for byte", False: "FAILED"}[ok])
    if not ok:
        gate.append("positive control")
    print(f"\n{'seed':>5s} {'K':>2s} {'distinct':>8s} {'fate':>10s} {'paired':>6s}  winning founder lines (first parent)")
    per_seed = {}
    for seed, ks in design.items():
        d0, f0 = fate_of(ROOT / "runs" / "RBT-90" / f"forage-{seed}" / "oscillator.txt")
        print(f"{seed:5d} {0:2d} {d0:8d} {f0:>10s} {'orig':>6s}  {winners(ROOT / 'runs' / 'RBT-90' / f'forage-{seed}')}  (the RBT-90 part 2 arm)")
        fates = []
        for k in ks:
            d, f = fate_of(arm_dir(seed, k) / "oscillator.txt")
            p = pairing_ok(seed, k)
            if f == "missing":
                missing.append(f"{seed}-b{k}")
            elif not p:
                gate.append(f"pairing {seed}-b{k}")
            fates.append(f)
            w = winners(arm_dir(seed, k)) if (arm_dir(seed, k) / "lineage-last.txt").exists() else "--"
            print(f"{seed:5d} {k:2d} {d if d is not None else '--':>8} {f:>10s} {str(p):>6s}  {w}")
        if any(f == OPPOSITE.get(f0) for f in fates):
            per_seed[seed] = ("FLIPS", f0)
        elif f0 in OPPOSITE and all(f == f0 for f in fates):
            per_seed[seed] = ("REPLICATES", f0)
        else:
            per_seed[seed] = ("UNCLEAR", f0)
    print()
    for seed, (v, f0) in per_seed.items():
        print(f"  seed {seed:4d} (originally {f0}): {v}")
    flips = [s for s, (v, _) in per_seed.items() if v == "FLIPS"]
    rep = [f0 for v, f0 in per_seed.values() if v == "REPLICATES"]
    if missing:
        verdict = f"incomplete ({', '.join(missing)} not analysed): no verdict"
    elif gate:
        verdict = f"INVALID: {', '.join(gate)} failed; no verdict"
    elif flips:
        verdict = f"HISTORY: the same founders reach both fates on {len(flips)} of {len(per_seed)} founding populations ({', '.join(map(str, flips))})"
    elif len(rep) == len(per_seed) and rep.count("discarded") >= NEED_EACH and rep.count("acquired") >= NEED_EACH:
        verdict = f"FOUNDING POPULATION: the fate replicates on all {len(per_seed)} founding populations ({rep.count('discarded')} discarded, {rep.count('acquired')} acquired)"
    else:
        verdict = "NOT DECIDED at this n"
    if not wave2_ran and not missing and not gate and not flips:
        verdict += "  -> wave 2 is due (PREREGISTRATION.md section 2)"
    print(f"\nverdict: {verdict}")


if __name__ == "__main__":
    main()
