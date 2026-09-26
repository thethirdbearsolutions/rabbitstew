"""RBT-101 (C4, flat terrain): the re-wiring readout, from committed tables only.

    python runs/RBT-101/rewire.py > runs/RBT-101/rewire.txt

C4 is the only challenge in RBT-89's set where "was anything re-wired during the challenge" is a live
question (docs/held-out-challenges.md section 2 C4, section 3, section 14 item 10).  This readout asks it
of the survivors before the onset against the survivors after it, per fauna, never pooled with C1-C3.

Per seed it reads three arms that share founders, worlds and streams and are byte-identical before T:

    base    the seed's RBT-90 part 2 arm           runs/RBT-90/forage-SEED/  (wiring.txt at runs/RBT-101/base-SEED/)
    shift   --shift-at T --shift terrain=flat      runs/RBT-101/shift-SEED/
    cull    --cull-at T, k by RBT-89 section 8     runs/RBT-101/cull-SEED/

and from each only seasons.txt, lineage-last.txt, events.txt (RBT-92's tables.py) and wiring.txt
(runs/RBT-101/wiring.py: per individual, from its genome at birth, the summed |signed_influence| from its
posture sensors -- contact, height, up, joint_angle, joint_velocity -- onto its live effectors; g1 at
depth 1, g2 through depth 2).  T is RBT-92's onset (runs/RBT-92/onset.txt, the same seeds and baselines).

Definitions, per fauna, with C0 the individuals alive at T - 1 (identical in all three arms) and P(s) the
individuals alive at season s, descent by RBT-84's rule (every parent followed; RBT-92's Arm.anc0):

    W(s)       mean g over P(s)
    W-sort(s)  W(s) - W(T - 1): the change in the survivors' posture wiring, sorting and new wiring together
    W-acq(s)   mean over n in P(s) of [ g(n) - mean g over n's C0 ancestors ]: the wiring each survivor
               gained or lost along its own line of descent since T, i.e. what it did not carry at onset
               (section 14 item 10's "acquired something it did not carry at onset")
    new(s)     SCORED.  The fraction of P(s) carrying a NEW DIRECT POSTURE LINK: g1 at least 0.5 (half the
               operator's typical weight, RBT-62: median |w| 0.85-1.13) above the largest g1 among its C0
               ancestors.  A count, so a few bodies with very large g do not carry it (why: section 6.3)
    lost(s)    the mirror: g1 at least 0.5 below the smallest g1 among its C0 ancestors.  Printed, not scored:
               the positive control installs links and does not remove them, so a loss is not validated
    wired(s)   the fraction of P(s) with any direct posture link (g1 > 0), minus the same fraction in C0

Contrasts per seed: shift - base (the challenge) and shift - cull (the challenge against a same-size random
turnover).  Read at T + 60, T + 160 (primary: the end of the recovery window) and T + 199.  Every mean over
seeds is printed with its t(n-1) 95% interval and a sign count k/n.

VERDICT (pre-registered in runs/RBT-101/PREREGISTRATION.md section 6; per fauna, on new, at T + 160):
    RE-WIRED       new, shift - base: the t(n-1) 95% interval lies above 0; and new, shift - cull: the interval
                   lies above 0; and the positive control (control.py) passed for this fauna at this n.  The sign counts k/n are
                   printed beside and are not part of the rule (section 6.3).  Both intervals below 0 print
                   FEWER NEW LINKS, a direction the control does not validate, and it is not called re-wiring.
    SORTED         wired, shift - base excludes 0 and RE-WIRED does not hold.
    NO CHANGE SEEN otherwise; the half-width and the control's smallest detected fraction are printed.
    UNVALIDATED    the positive control did not pass for this fauna at this n: nothing of that fauna's re-wiring
                   readout enters a sentence.
W-acq and W-sort on g1 and g2 are printed and are not scored: they failed the positive control on the
holistic fauna on a development window (section 6.3).

Environment overrides for the smoke test only: RBT101_SEEDS, RBT101_BASE_DIR, RBT101_ARM_DIR,
RBT101_BASE_WIRING_DIR, RBT101_ONSET, RBT101_READ (comma-separated offsets from T), RBT101_CONTROL.
"""
import csv
import importlib.util
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def _rbt92_readout():
    spec = importlib.util.spec_from_file_location("rbt92_readout", os.path.join(ROOT, "runs", "RBT-92", "readout.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


R92 = _rbt92_readout()
KINDS = ("holistic", "conventional")
SEEDS = [int(s) for s in os.environ.get("RBT101_SEEDS", "801 804 805 806 807 1 2 3 4 7").split()]
BASE_DIR = os.environ.get("RBT101_BASE_DIR", "runs/RBT-90")
ARM_DIR = os.environ.get("RBT101_ARM_DIR", "runs/RBT-101")
BASE_WIRING = os.environ.get("RBT101_BASE_WIRING_DIR", "runs/RBT-101")
ONSET = os.environ.get("RBT101_ONSET", os.path.join(ROOT, "runs", "RBT-92", "onset.txt"))
READ = [int(x) for x in os.environ.get("RBT101_READ", "60,160,199").split(",")]
PRIMARY = READ[1]
CONTROL = os.environ.get("RBT101_CONTROL", os.path.join(HERE, "control.txt"))
ARMS = ("base", "shift", "cull")
NEW_LINK = 0.5


def tsv(path):
    return list(csv.DictReader(open(path), delimiter="\t"))


def null_is_base(seed):
    """k = 0 for both faunas: no cull arm is run, and the null is the baseline itself (PREREGISTRATION.md section 7)."""
    kf = os.path.join(ARM_DIR, f"cull-k-{seed}.txt")
    return (not os.path.exists(os.path.join(ARM_DIR, f"cull-{seed}")) and os.path.exists(kf)
            and any(l.rstrip("\n") == "cull\tholistic=0,conventional=0" for l in open(kf)))


def arm_path(arm, seed):
    if arm == "base" or (arm == "cull" and null_is_base(seed)):
        return os.path.join(BASE_DIR, f"forage-{seed}")
    return os.path.join(ARM_DIR, f"{arm}-{seed}")


def wiring_path(arm, seed):
    if arm == "base" or (arm == "cull" and null_is_base(seed)):
        return os.path.join(BASE_WIRING, f"base-{seed}", "wiring.txt")
    return os.path.join(arm_path(arm, seed), "wiring.txt")


def load_wiring(path):
    out = {}
    for r in tsv(path):
        if r["g1"] != "-":
            out[(r["population"], r["name"])] = (float(r["g1"]), float(r["g2"]))
    return out


def measures(arm, wiring, kind, T, s):
    """W(s), W-sort(s), W-acq(s) on g1 and g2, and new(s), for one arm and fauna; None if P(s) or C0 is empty."""
    c0 = arm.alive_at(kind, T - 1)
    now = arm.alive_at(kind, s)
    c0w = [wiring[(kind, c)] for c in c0 if (kind, c) in wiring]
    if not c0w or not now:
        return None
    out = {}
    for j, g in ((0, "g1"), (1, "g2")):
        w0 = statistics.fmean(x[j] for x in c0w)
        ws = [wiring[(kind, n)][j] for n in now if (kind, n) in wiring]
        acq = []
        for n in now:
            anc = [wiring[(kind, a)][j] for a in arm.anc0(kind, n, c0) if (kind, a) in wiring]
            if (kind, n) in wiring and anc:
                acq.append(wiring[(kind, n)][j] - statistics.fmean(anc))
        out[f"W_{g}"] = statistics.fmean(ws) if ws else float("nan")
        out[f"sort_{g}"] = out[f"W_{g}"] - w0
        out[f"acq_{g}"] = statistics.fmean(acq) if acq else float("nan")
    new, lost = [], []
    for n in now:
        anc = [wiring[(kind, a)][0] for a in arm.anc0(kind, n, c0) if (kind, a) in wiring]
        if (kind, n) in wiring and anc:
            new.append(1.0 if wiring[(kind, n)][0] >= max(anc) + NEW_LINK else 0.0)
            lost.append(1.0 if wiring[(kind, n)][0] <= min(anc) - NEW_LINK else 0.0)
    out["new"] = statistics.fmean(new) if new else float("nan")
    out["lost"] = statistics.fmean(lost) if lost else float("nan")
    wired = lambda names: [1.0 if wiring[(kind, x)][0] > 0 else 0.0 for x in names if (kind, x) in wiring]
    out["wired"] = statistics.fmean(wired(now)) - statistics.fmean(wired(c0)) if wired(now) and wired(c0) else float("nan")
    out["n_alive"] = len(now)
    return out


def ci(vals):
    n, m, sd, hw = R92.stat(vals)
    if n == 0:
        return "n=0", None
    if n < 2:
        return f"{m:+.4f} (n=1, no interval)", None
    pos = sum(1 for x in vals if x is not None and not math.isnan(x) and x > 0)
    neg = sum(1 for x in vals if x is not None and not math.isnan(x) and x < 0)
    return (f"{m:+.4f}  95% t({n - 1}) [{m - hw:+.4f}, {m + hw:+.4f}]  sd {sd:.4f}  positive {pos}/{n}  negative {neg}/{n}",
            (n, m, hw, pos, neg))


def excludes_zero(t, need):
    """(sign, ok): the interval excludes 0 and at least `need` seeds share the mean's sign."""
    if t is None:
        return 0, False
    n, m, hw, pos, neg = t
    if m - hw > 0 and pos >= need:
        return 1, True
    if m + hw < 0 and neg >= need:
        return -1, True
    return 0, False


def control_status(n, kind):
    """The positive control's verdict for one fauna at this n, from control.txt's CONTROL-FAUNA lines."""
    if not os.path.exists(CONTROL):
        return None, None
    status, smallest = None, None
    for line in open(CONTROL):
        f = line.split()
        if len(f) >= 4 and f[0] == "CONTROL-FAUNA" and f[1] == f"n={n}" and f[2] == kind:
            status = f[3]
            smallest = " ".join(f[4:])
    return status, smallest


def main():
    T_of = {}
    for line in open(ONSET):
        f = line.rstrip("\n").split("\t")
        if f[0].lstrip("-").isdigit():
            T_of[int(f[0])] = int(f[1]) if f[1].isdigit() else f[1]
    print(__doc__.split("\n\n")[0])
    print(f"read at T + {READ} (primary T + {PRIMARY}); new-link threshold {NEW_LINK}")
    print()
    print("SEEDS (RBT-92's seed rule: all ten, extinction at or before T - 1 in the baseline the only exclusion)")
    seeds, arms, wir = [], {}, {}
    for seed in SEEDS:
        T = T_of.get(seed)
        if not isinstance(T, int):
            print(f"  {seed}: no onset ({T}); not read")
            continue
        missing = [a for a in ARMS if not (os.path.exists(os.path.join(arm_path(a, seed), "seasons.txt"))
                                           and os.path.exists(wiring_path(a, seed)))]
        if missing:
            print(f"  {seed}: T={T}; arms or wiring tables not committed: {missing}; not read (a partial set is not a result)")
            continue
        A = {a: R92.Arm(arm_path(a, seed)) for a in ARMS}
        dead = [k for k in KINDS if A["base"].alive[k].get(T - 1, 0) == 0]
        if dead:
            print(f"  {seed}: T={T}; EXCLUDED: {'+'.join(dead)} extinct by T - 1 in the baseline")
            continue
        short = [a for a in ARMS if A[a].last < T + max(READ)]
        if short:
            print(f"  {seed}: T={T}; arms that did not reach T + {max(READ)}: {short}; not read")
            continue
        seeds.append((seed, T))
        arms[seed] = A
        wir[seed] = {a: load_wiring(wiring_path(a, seed)) for a in ARMS}
        print(f"  {seed}: T={T}  read" + ("  (k = 0 for both faunas: the null is the baseline itself, so shift - cull = shift - base)" if null_is_base(seed) else ""))
    n = len(seeds)
    need = math.ceil(0.8 * n) if n else 0
    print(f"  seeds read: {n}/{len(SEEDS)}; sign guard ceil(0.8 n) = {need}/{n}")
    print()

    # --------------------------------------------------------------- V-W: the wiring tables round-trip
    print("V-W, the wiring tables cover the individuals the readout reads (C0 and every P(s)), per arm")
    bad = 0
    for seed, T in seeds:
        for a in ARMS:
            for kind in KINDS:
                need_names = set(arms[seed][a].alive_at(kind, T - 1))
                for off in READ:
                    need_names |= arms[seed][a].alive_at(kind, T + off)
                have = sum(1 for x in need_names if (kind, x) in wir[seed][a])
                if have != len(need_names):
                    bad += 1
                    print(f"  {seed} {a} {kind}: {have}/{len(need_names)} covered")
    print(f"  {'PASS' if bad == 0 else 'FAIL'}: {bad} arm-fauna tables short")
    # C0's wiring must be identical across the arms (they share the prefix byte for byte)
    diff = 0
    for seed, T in seeds:
        for kind in KINDS:
            c0 = arms[seed]["base"].alive_at(kind, T - 1)
            for a in ("shift", "cull"):
                if arms[seed][a].alive_at(kind, T - 1) != c0 or any(wir[seed][a].get((kind, c)) != wir[seed]["base"].get((kind, c)) for c in c0):
                    diff += 1
    print(f"  C0 and its wiring identical across base, shift and cull: {'PASS' if diff == 0 else 'FAIL'} ({diff} seed-fauna differ)")
    print()

    for kind in KINDS:
        status, smallest = control_status(n, kind)
        print(f"POSITIVE CONTROL at n={n}, {kind}: {status or 'NOT RUN AT THIS n'}" + (f"; {smallest}" if smallest else ""))
    print()

    for kind in KINDS:
        print(f"==== {kind.upper()} fauna (C4 is reported separately from C1-C3 and never pooled with them)")
        M = {}
        for seed, T in seeds:
            for a in ARMS:
                for off in READ:
                    M[(seed, a, off)] = measures(arms[seed][a], wir[seed][a], kind, T, T + off)
        print("  per seed at the primary read point T + %d: W(T-1) on g2, and per arm new, wired, lost, W-acq(g2)" % PRIMARY)
        for seed, T in seeds:
            c0 = arms[seed]["base"].alive_at(kind, T - 1)
            w0 = [wir[seed]["base"][(kind, c)][1] for c in c0 if (kind, c) in wir[seed]["base"]]
            cells = []
            for a in ARMS:
                m = M[(seed, a, PRIMARY)]
                cells.append(f"{a} " + ("extinct" if m is None else f"new {m['new']:.3f} wired {R92.fmt(m['wired'])} lost {m['lost']:.3f} acq_g2 {R92.fmt(m['acq_g2'])}"))
            print(f"    {seed}  W(T-1) {statistics.fmean(w0) if w0 else float('nan'):.4f}  |  " + "  |  ".join(cells))
        verdict = {}
        for off in READ:
            print(f"  -- read at T + {off}" + ("  (PRIMARY)" if off == PRIMARY else ""))
            for q in ("new", "wired", "lost", "acq_g1", "acq_g2", "sort_g1", "sort_g2"):
                for label, x, y in (("shift - base", "shift", "base"), ("shift - cull", "shift", "cull"), ("cull - base", "cull", "base")):
                    vals = []
                    for seed, T in seeds:
                        mx, my = M[(seed, x, off)], M[(seed, y, off)]
                        vals.append(float("nan") if mx is None or my is None else mx[q] - my[q])
                    text, t = ci(vals)
                    print(f"    {q:8s} {label:13s} {text}")
                    if off == PRIMARY:
                        verdict[(q, label)] = t
        status, _ = control_status(n, kind)
        if status != "PASS":
            v = "UNVALIDATED (the positive control did not pass at this n)"
        else:
            s1, ok1 = excludes_zero(verdict.get(("new", "shift - base")), 0)
            s2, ok2 = excludes_zero(verdict.get(("new", "shift - cull")), 0)
            s3, ok3 = excludes_zero(verdict.get(("wired", "shift - base")), 0)
            if ok1 and ok2 and s1 == s2 == 1:
                v = "RE-WIRED (more survivors carry a new direct posture link than in the baseline and the cull)"
            elif ok1 and ok2 and s1 == s2 == -1:
                v = ("FEWER NEW LINKS than the baseline and the cull (the control installs links, so this direction is not "
                     "validated; it enters no sentence as re-wiring)")
            elif ok3:
                v = f"SORTED (the fraction of survivors with any direct posture link {'rose' if s3 > 0 else 'fell'} against the baseline; no new links beyond it)"
            else:
                v = "NO CHANGE SEEN"
        print(f"  RE-WIRING VERDICT, {kind}, 'new' at T + {PRIMARY}: {v}")
        print()
    print("Depth (RBT-89 section 10): T -> T + 160 is about five reproduction events along a lineage; a RE-WIRED")
    print("verdict means posture wiring changed within about five mutations, not that a reflex was searched for.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
