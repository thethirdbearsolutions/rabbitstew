"""RBT-101 (C4, flat terrain): the re-wiring readout, from committed tables only.

    python runs/RBT-101/rewire.py > runs/RBT-101/rewire.txt

C4 is the only challenge in RBT-89's set where "was anything re-wired during the challenge" is a live
question (docs/held-out-challenges.md section 2 C4, section 3, section 14 item 10).  This readout asks it
of the survivors before the onset against the survivors after it, per fauna, never pooled with C1-C3.

Per seed it reads four arms that share founders, worlds and streams and are byte-identical before T:

    base    the seed's RBT-90 part 2 arm           runs/RBT-90/forage-SEED/  (wiring.txt at runs/RBT-101/base-SEED/)
    shift   --shift-at T --shift terrain=flat      runs/RBT-101/shift-SEED/
    cull    --cull-at T, k by RBT-89 section 8     runs/RBT-101/cull-SEED/   (k = 0/0: the baseline itself)
    cull20  --cull-at T --cull 20/20, RBT-92's     runs/RBT-92/cull20-SEED/  (wiring.txt written there by RBT-92's
                                                                             post-run step, while its bulk exists)

and from each only seasons.txt, lineage-last.txt, events.txt (RBT-92's tables.py) and wiring.txt
(runs/RBT-101/wiring.py: per individual, from its genome at birth: g1 the summed |direct gain| from its posture
sensors -- contact, height, up, joint_angle, joint_velocity -- onto its live effectors, g2 through depth 2, ns the
number of posture sensors it carries, g1_other the placebo on food, agent and oscillator, g1_vel on velocity).
T is RBT-92's onset (runs/RBT-92/onset.txt).

Definitions, per fauna, with C0 the individuals alive at T - 1 (identical in every arm, gated) and P(s) those alive
at s, descent by RBT-84's rule (every parent followed; RBT-92's Arm.anc0); "ancestors" below are n's C0 ancestors:

    new_existing(s)  SCORED.  The fraction of P(s) carrying a new direct posture link on a sensor its lineage already
                     had: g1 at least 0.5 (half the operator's typical weight, RBT-62) above the largest ancestor g1,
                     AND ns not above the largest ancestor ns.  C4's "a new use of an existing sensor" (protocol
                     section 3).  (Adversary round 1, F2: half the holistic hits of the unrestricted count were bodies
                     that grew posture sensors.)
    new_grown(s)     the same gain with ns above every ancestor's: a grown limb or joint.  Printed, not scored.
    new_other(s)     THE PLACEBO: g1_other at least 0.5 above every ancestor's.  Flat ground gives no posture reason
                     to wire food, agent or oscillator, so a change in turnover moves it and a re-wiring does not.
    new_vel(s)       the same on velocity, apart (obstacles change what velocity reads).  Printed, not scored.
    lost(s)          g1 at least 0.5 below every ancestor's.  Printed, not scored (the control installs, never removes).
    wired(s)         the fraction of P(s) with any direct posture link, minus that fraction in C0.
    depth(s)         mean over P(s) of the fewest births from the individual back to a C0 member (adversary F1:
                     `new` rises about +0.05 per reproduction event on the holistic baseline with nothing re-wired).
    W-acq, W-sort    on g1 and g2, printed, not scored (they fail the positive control, section 6.3).

Contrasts per seed: shift - base (the challenge), shift - cull20 (a same-seed, same-T divergence with no terrain
change: the drift-and-turnover null on every seed), shift - cull (the same-size turnover; on a k = 0/0 seed it IS
shift - base), cull20 - base (the null's own size), and the placebo contrast, (new_existing - new_other) shift - base.
Read at T + 60, T + 160 (primary) and T + 199.  Every mean over seeds: its t(n-1) 95% interval and sign counts k/n.

VERDICT (pre-registered, runs/RBT-101/PREREGISTRATION.md section 6.5 and Amendment 2; per fauna, at T + 160):
    RE-WIRED       new_existing, shift - base: interval above 0; AND shift - cull20: interval above 0; AND the placebo
                   contrast (new_existing - new_other), shift - base: interval above 0; AND the positive control
                   passed for this fauna at this n.  If |depth shift - base| > 0.5 event the line carries it.
    TURNOVER, NOT RE-WIRING   the first two hold and the placebo contrast does not: the non-posture links moved too.
    FEWER NEW LINKS           new_existing shift - base and shift - cull20 both below 0 (direction not validated).
    SORTED         wired, shift - base excludes 0, and none of the above.
    NO CHANGE SEEN otherwise.
    UNVALIDATED    the positive control did not pass for this fauna at this n.
Every verdict line carries the control's resolution: "blind below f ~ X of survivors" (adversary F4).

Environment overrides for the smoke test only: RBT101_SEEDS, RBT101_BASE_DIR, RBT101_ARM_DIR, RBT101_RBT92_DIR,
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
R92_DIR = os.environ.get("RBT101_RBT92_DIR", "runs/RBT-92")
BASE_WIRING = os.environ.get("RBT101_BASE_WIRING_DIR", "runs/RBT-101")
ONSET = os.environ.get("RBT101_ONSET", os.path.join(ROOT, "runs", "RBT-92", "onset.txt"))
READ = [int(x) for x in os.environ.get("RBT101_READ", "60,160,199").split(",")]
PRIMARY = READ[1]
CONTROL = os.environ.get("RBT101_CONTROL", os.path.join(HERE, "control370.txt"))  # Amendment 2: the onset-region control
ARMS = ("base", "shift", "cull", "cull20")
DEPTH_CAVEAT = 0.5
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
    if arm == "cull20":
        return os.path.join(R92_DIR, f"cull20-{seed}")
    return os.path.join(ARM_DIR, f"{arm}-{seed}")


def wiring_path(arm, seed):
    if arm == "base" or (arm == "cull" and null_is_base(seed)):
        return os.path.join(BASE_WIRING, f"base-{seed}", "wiring.txt")
    return os.path.join(arm_path(arm, seed), "wiring.txt")


WCOLS = ("g1", "g2", "ns", "g1_other", "g1_vel")


def load_wiring(path):
    out = {}
    for r in tsv(path):
        if r["g1"] != "-":
            out[(r["population"], r["name"])] = {c: float(r[c]) for c in WCOLS}
    return out


def births_to_c0(arm, kind, name, c0):
    """The fewest births from `name` back to a member of C0 (0 if it is one), every parent followed."""
    frontier, seen, d = {name}, set(), 0
    while frontier:
        if frontier & c0:
            return d
        seen |= frontier
        nxt = set()
        for n in frontier:
            nxt.update(p for p in arm.ind.get((kind, n), (0, 0, []))[2] if p not in seen)
        frontier, d = nxt, d + 1
    return None


def measures(arm, wiring, kind, T, s):
    """Every statistic of the docstring for one arm and fauna at season s; None if P(s) or C0 is empty."""
    c0 = arm.alive_at(kind, T - 1)
    now = arm.alive_at(kind, s)
    c0w = [wiring[(kind, c)] for c in c0 if (kind, c) in wiring]
    if not c0w or not now:
        return None
    out = {}
    for g in ("g1", "g2"):
        w0 = statistics.fmean(x[g] for x in c0w)
        ws = [wiring[(kind, n)][g] for n in now if (kind, n) in wiring]
        acq = []
        for n in now:
            anc = [wiring[(kind, a)][g] for a in arm.anc0(kind, n, c0) if (kind, a) in wiring]
            if (kind, n) in wiring and anc:
                acq.append(wiring[(kind, n)][g] - statistics.fmean(anc))
        out[f"W_{g}"] = statistics.fmean(ws) if ws else float("nan")
        out[f"sort_{g}"] = out[f"W_{g}"] - w0
        out[f"acq_{g}"] = statistics.fmean(acq) if acq else float("nan")
    cnt = {q: [] for q in ("new_existing", "new_grown", "new_all", "new_other", "new_vel", "lost")}
    depth = []
    for n in now:
        if (kind, n) not in wiring:
            continue
        me = wiring[(kind, n)]
        anc = [wiring[(kind, a)] for a in arm.anc0(kind, n, c0) if (kind, a) in wiring]
        if not anc:
            continue
        gain = me["g1"] >= max(a["g1"] for a in anc) + NEW_LINK
        grown = me["ns"] > max(a["ns"] for a in anc)
        cnt["new_all"].append(float(gain))
        cnt["new_existing"].append(float(gain and not grown))
        cnt["new_grown"].append(float(gain and grown))
        cnt["new_other"].append(float(me["g1_other"] >= max(a["g1_other"] for a in anc) + NEW_LINK))
        cnt["new_vel"].append(float(me["g1_vel"] >= max(a["g1_vel"] for a in anc) + NEW_LINK))
        cnt["lost"].append(float(me["g1"] <= min(a["g1"] for a in anc) - NEW_LINK))
        d = births_to_c0(arm, kind, n, c0)
        if d is not None:
            depth.append(d)
    for q, v in cnt.items():
        out[q] = statistics.fmean(v) if v else float("nan")
    out["existing_minus_other"] = out["new_existing"] - out["new_other"]
    wired = lambda names: [1.0 if wiring[(kind, x)]["g1"] > 0 else 0.0 for x in names if (kind, x) in wiring]
    out["wired"] = statistics.fmean(wired(now)) - statistics.fmean(wired(c0)) if wired(now) and wired(c0) else float("nan")
    out["depth"] = statistics.fmean(depth) if depth else float("nan")
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
            for a in ("shift", "cull", "cull20"):
                if arms[seed][a].alive_at(kind, T - 1) != c0 or any(wir[seed][a].get((kind, c)) != wir[seed]["base"].get((kind, c)) for c in c0):
                    diff += 1
    print(f"  C0 and its wiring identical across base, shift, cull and cull20: {'PASS' if diff == 0 else 'FAIL'} ({diff} seed-fauna differ)")
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
        print(f"  per seed at the primary read point T + {PRIMARY}: per arm new_existing (SCORED), new_grown, new_other (placebo), depth")
        for seed, T in seeds:
            cells = []
            for a in ARMS:
                m = M[(seed, a, PRIMARY)]
                cells.append(f"{a} " + ("extinct" if m is None else
                             f"nx {m['new_existing']:.3f} gr {m['new_grown']:.3f} oth {m['new_other']:.3f} d {m['depth']:.2f}"))
            print(f"    {seed}  " + "  |  ".join(cells))
        verdict = {}
        CONTRASTS = (("shift - base", "shift", "base"), ("shift - cull20", "shift", "cull20"),
                     ("shift - cull", "shift", "cull"), ("cull20 - base", "cull20", "base"))
        for off in READ:
            print(f"  -- read at T + {off}" + ("  (PRIMARY)" if off == PRIMARY else ""))
            for q in ("new_existing", "existing_minus_other", "new_other", "new_grown", "new_all", "new_vel", "lost",
                      "wired", "depth", "acq_g1", "acq_g2", "sort_g1", "sort_g2"):
                for label, x, y in CONTRASTS:
                    vals = []
                    for seed, T in seeds:
                        mx, my = M[(seed, x, off)], M[(seed, y, off)]
                        vals.append(float("nan") if mx is None or my is None else mx[q] - my[q])
                    text, t = ci(vals)
                    print(f"    {q:20s} {label:15s} {text}")
                    if off == PRIMARY:
                        verdict[(q, label)] = t
        status, smallest = control_status(n, kind)
        blind = f"; blind below f ~ {smallest.split(':')[-1].strip() if smallest else '?'} of survivors (positive control)"
        dd = verdict.get(("depth", "shift - base"))
        depth_note = (f"; reproduction depth moved {dd[1]:+.2f} events against the baseline, so turnover may carry part of it"
                      if dd and abs(dd[1]) > DEPTH_CAVEAT else "")
        if status != "PASS":
            v = "UNVALIDATED (the positive control did not pass for this fauna at this n)"
        else:
            sa, oka = excludes_zero(verdict.get(("new_existing", "shift - base")), 0)
            sb, okb = excludes_zero(verdict.get(("new_existing", "shift - cull20")), 0)
            sc, okc = excludes_zero(verdict.get(("existing_minus_other", "shift - base")), 0)
            sw, okw = excludes_zero(verdict.get(("wired", "shift - base")), 0)
            if oka and okb and sa == sb == 1 and okc and sc == 1:
                v = ("RE-WIRED (more survivors carry a new direct link from a posture sensor their lineage already had, than in "
                     "the baseline and in cull20, and more than the non-posture placebo moved)" + depth_note)
            elif oka and okb and sa == sb == 1:
                v = ("TURNOVER, NOT RE-WIRING (new posture links rose against the baseline and cull20, but not beyond the "
                     "non-posture placebo)" + depth_note)
            elif oka and okb and sa == sb == -1:
                v = ("FEWER NEW LINKS than the baseline and cull20 (the control installs links, so this direction is not "
                     "validated; it enters no sentence as re-wiring)" + depth_note)
            elif okw:
                v = f"SORTED (the fraction of survivors with any direct posture link {'rose' if sw > 0 else 'fell'} against the baseline; no new links beyond it)"
            else:
                v = "NO CHANGE SEEN"
        print(f"  RE-WIRING VERDICT, {kind}, new_existing at T + {PRIMARY}: {v}{blind}")
        print()
    print("Depth (RBT-89 section 10): T -> T + 160 is about five reproduction events along a lineage; a RE-WIRED")
    print("verdict means posture wiring changed within about five mutations, not that a reflex was searched for.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
