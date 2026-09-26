"""RBT-100, epoch C3 (scarce food): the readout, from committed tables only, on RBT-92's instrument.

    python runs/RBT-100/readout.py > runs/RBT-100/readout.txt

Part 1 is RBT-92's readout.py run unchanged (its validation gates V0-V3, power line, R-body, R-shift,
R-null, R-cull, R-cull20, recovery time, alive, carriage and the RBT-89 section 9 verdict), with its arm
paths pointed at C3's arms:

    base    the seed's RBT-90 part 2 arm, no event          runs/RBT-90/forage-SEED/
    shift   --shift-at T --shift food-items=6               runs/RBT-100/shift-SEED/
    cull    --cull-at T, k by RBT-89 section 8's rule        runs/RBT-100/cull-SEED/   (k in runs/RBT-100/cull-k-SEED.txt)
    cull20  --cull-at T --cull holistic=20,conventional=20   runs/RBT-92/cull20-SEED/  (RBT-92's arm: the same command)

T is read from RBT-92's onset.txt, the baseline body digests from RBT-92's base-SEED/.  Whatever RBT-92's
adversary round and answer change in readout.py, onset.py or cull_k.py is therefore what this readout runs.

Part 2 prints the C3-specific lines the RBT-100 pre-registration adds (PREREGISTRATION.md sections 3, 4,
6 and Amendment 2).  None of them changes the class; each is a reading the report prints beside it:

  C3-V1     the shift arm's events.txt records food.items = 6 from T (manipulation, C3's flag and value)
  NULL      diagnostics only (Amendment 2, F1/F2): k; excess deaths shift - base over [T, +10), [T, +30),
            [T, +60), split by cause (starved / aged) and by cohort (born < T / born >= T); births deficit;
            alive deficit at T+10, +30, +40, +60, +100.  C3's turnover guard is not interpretable a priori
  CLAIM 3   (Amendment 2, rescored): designed excess deaths of individuals born >= T exceed those of
            individuals born < T over [T, T+30), on >= ceil(0.8n)/n seeds
  OWN       (F3) from own.txt: stored energy a head, and the season's own net over the survivors and its upper
            bound over everyone who ran; "own net below basal in the recovery window" k/n seeds, per fauna
  ECHO      post-onset 20/60 peaks per seed, arm and fauna; recovery-window count, shift against base
  CLASS D   per seed and fauna in the shift arm, which of RBT-89's triggers fired, and the extinction season
  DEPTH     median reproduction events after T along the lineages alive at T+160
  FOUNDERS  (F5) each seed's founders-at-six arm: HOLD or FAIL at season 59; the co-evolved fauna's recovery-
            window HOLD; the contrast sentence only where the founders FAIL and the established fauna HOLDS
  VERDICT TEXT (F6) the C3 claim lines, the unperceived statement, the owner's falsifier wording, the
            class-D sentence the rule picks, and forbidden readings 12 and 13, verbatim

Environment overrides for the smoke test only: RBT100_ARM_DIR, RBT100_C1_DIR, and RBT-92's RBT92_* ones
(RBT-92's ARM_DIR is set on the imported module to C3's directory, so that its V1 reads C3's cull-k files).
"""
import contextlib
import importlib.util
import io
import re
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C1 = os.environ.get("RBT100_C1_DIR", os.path.join(HERE, "..", "RBT-92"))
C3 = os.environ.get("RBT100_ARM_DIR", "runs/RBT-100")
spec = importlib.util.spec_from_file_location("rbt92_readout", os.path.join(HERE, "..", "RBT-92", "readout.py"))
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
# set on the module, not in os.environ, so that importing this file changes nothing for RBT-92's own readout
R.ONSET = os.environ.get("RBT92_ONSET", os.path.join(C1, "onset.txt"))
R.ARM_DIR = C3  # cull-k-SEED.txt (V1) is C3's own; cull20 and base digests: below
_arm_path_c1 = R.arm_path


def arm_path(arm, seed):
    """C3's own arms are shift and cull; base and cull20 are where RBT-92 reads them."""
    if arm == "cull20":
        return os.path.join(C1, f"cull20-{seed}")
    return os.path.join(C3, f"{arm}-{seed}") if arm in ("shift", "cull") else _arm_path_c1(arm, seed)


class Arm(R.Arm):
    """RBT-92's Arm, with the baseline's body digests read where RBT-92 commits them (C1/base-SEED/)."""

    def __init__(self, path, bodysig=None):
        if bodysig and os.path.dirname(os.path.dirname(bodysig)) == R.ARM_DIR.rstrip("/"):
            bodysig = os.path.join(C1, os.path.basename(os.path.dirname(bodysig)), "bodysig.txt")
        super().__init__(path, bodysig)


R.arm_path = arm_path
R.Arm = Arm
KINDS = R.KINDS
PEAK = 20  # RBT-89 section 8: a ten-season deaths window reaching 20 of 60


def cull_k(seed):
    kf = os.path.join(C3, f"cull-k-{seed}.txt")
    if os.path.exists(kf):
        for line in open(kf):
            if line.startswith("cull\t"):
                return {p.split("=")[0]: int(p.split("=")[1]) for p in line.split("\t")[1].strip().split(",")}
    return {}


def shift_record(path):
    ev = os.path.join(path, "events.txt")
    if os.path.exists(ev):
        for r in R.tsv(ev):
            if r["kind"] == "shift":
                return r
    return None


def peaks(arm, kind, T, lo, hi):
    """Start seasons (relative to T) of each run of 10-season deaths windows reaching PEAK, windows in [T+lo, T+hi)."""
    out, prev = [], False
    for s in range(T + lo, T + hi - 9):
        hit = sum(arm.deaths[kind].get(t, 0) for t in range(s, s + 10)) >= PEAK
        if hit and not prev:
            out.append(s - T)
        prev = hit
    return out


def births(arm, kind, t):
    r = arm.raw.get((t, kind))
    return int(r["births"]) if r else 0


def extinct_at(arm, kind, T):
    return next((s for s in range(T, arm.last + 1) if arm.alive[kind].get(s, 0) == 0), None)


def depth_after(arm, kind, T, s):
    """Reproduction events after T along each lineage alive at s: steps back along the first parent until
    an ancestor born before T.  Returns the median over the living, or None."""
    born = {n: b for (k, n), (b, l, p) in arm.ind.items() if k == kind}
    par = {n: p for (k, n), (b, l, p) in arm.ind.items() if k == kind}
    ds = []
    for n in arm.alive_at(kind, s):
        d, cur = 0, n
        while cur in born and born[cur] >= T:
            d += 1
            ps = par.get(cur) or []
            if not ps:
                break
            cur = ps[0]
        ds.append(d)
    return statistics.median(ds) if ds else None


def split_deaths(arm, kind, T, w):
    """Deaths with death season in [T, T+w), by cause and cohort, from lineage-last.txt alone.  An individual's
    last row is the season before it died (RBT-92's V0 note), so its death season is last + 1; aged if its age
    then reaches max_age (60), starved otherwise; culled individuals are left out.  Cohort by birth season
    b = generation - age of the last row (Arm.ind): born < T is the onset cohort, born >= T its recruits."""
    culled = {n for (k, _), ns in arm.culled.items() if k == kind for n in ns}
    age = {r["name"]: int(r["age"]) for r in arm.lastrows if r["population"] == kind}
    out = {(c, h): 0 for c in ("starved", "aged") for h in ("<T", ">=T")}
    for (k, n), (b, l, _) in arm.ind.items():
        if k != kind or n in culled or l >= arm.last or not (T <= l + 1 < T + w):
            continue
        out[("aged" if age.get(n, 0) + 1 >= 60 else "starved", "<T" if b < T else ">=T")] += 1
    return out


def read_own(path):
    """own.txt (own_table.py) as {(season, kind): row}; {} if it is not there."""
    f = os.path.join(path, "own.txt")
    if not os.path.exists(f):
        return {}
    return {(int(r["season"]), r["population"]): r for r in R.tsv(f)}


def own_mean(own, kind, a, b, col):
    v = [float(own[(s, kind)][col]) for s in range(a, b) if (s, kind) in own and own[(s, kind)][col] != "-"]
    return statistics.fmean(v) if v else None


def founders_outcome(arm, kind, season=59):
    """HOLD if the founders-at-six population has >= FLOOR (12) alive at `season`, else FAIL (extinct included)."""
    return "HOLD" if arm.alive[kind].get(season, 0) >= R.FLOOR else "FAIL"


def parse_part1(text):
    """(class line, r, co-evolved R-shift in recovery) from RBT-92's printed verdict block."""
    cls = re.search(r"^  CLASS: (.*)$", text, re.M)
    r = re.search(r"^  r = ([-+0-9.na]+) \(the larger\)", text, re.M)
    hu = re.search(r"'holds up' needs co-evolved R-shift \(recovery\) >= -r: +(\S+) against", text)
    num = lambda m: float(m.group(1)) if m and m.group(1) not in ("--",) else float("nan")
    return (cls.group(1).strip() if cls else None), num(r), num(hu)


CLAIM_C3 = ("**Claim tested:** as C2, survivorship at a boundary, here the bootstrap line for food; whether an\n"
            "established population holds where random founders could not. Not the owner's contest claim.")
CLAIM_C2 = ("**Claim tested:** survivorship of the co-evolved population at an economic boundary the designed\n"
            "body's budget is not expected to survive. That is a different claim from the owner's (it is about\n"
            "one body's cheapness, not two bodies' contest), and a C2 result is reported as such.")
UNPERCEIVED = ("**These challenges select on standing morphology and gait only.** \"Robust against a novel challenge\" then means\n"
               "**survivorship of standing morphology and gait through a shift, not adaptation during it**")
FALSIFIER = "the designed body wins on the held-out challenge"
FORBIDDEN_12 = ("12. Reading \"the co-evolved population held at the bootstrap line\" when the comparator was bankrupt: that is\n"
                "    class D with the co-evolved side's R-shift beside it, \"outlasts a bankrupt comparator\", not \"holds up\".")
FORBIDDEN_13 = ("13. Reading the recovery-time metric as the population \"not recovering\": under a budget shift the pre-event\n"
                "    plateau was earned at twice the density and is out of reach by arithmetic.")


def verdict_text(cls, rshift_hol, r):
    """The C3 sentences printed after the class (adversary round 1, F6): the claim lines and the unperceived
    statement verbatim, the owner's falsifier wording, the sentence the class rule picks, forbidden readings
    12 and 13.  Pure: cls is RBT-92's class line, rshift_hol the co-evolved R-shift in recovery, r the r."""
    holds = rshift_hol == rshift_hol and r == r and rshift_hol >= -r
    out = ["C3's claim line (docs/held-out-challenges.md section 2, C3), verbatim:", CLAIM_C3,
           "  and C2's, which it refers to:", CLAIM_C2,
           "The statement every C1-C3 pre-registration carries (section 3), verbatim:", UNPERCEIVED,
           f"The owner's falsifier: \"{FALSIFIER}\" (class C)."]
    c = (cls or "").strip()
    if c.startswith("C."):
        out.append(f"CLASS C: {FALSIFIER}.  The falsifier is met.")
    elif c.startswith("D."):
        out.append("CLASS D: the challenge exceeded the designed body's energy budget; reported as D, not A, with the co-evolved R-shift beside it.")
        out.append("  sentence: " + ("holds up against the challenge (co-evolved R-shift >= -r)" if holds
                                     else "outlasts a bankrupt comparator (co-evolved R-shift < -r)"))
    elif c.startswith("A."):
        out.append("CLASS A: the co-evolved body earned more under the shift, both surviving above the floor; not the owner's contest claim (C3's claim line).")
        out.append("  sentence: " + ("holds up against the challenge" if holds else "outlasts, not holds up (co-evolved R-shift < -r)"))
    elif c.startswith("E."):
        out.append("CLASS E: neither body holds up.")
    else:
        out.append(f"CLASS {c or 'NONE'}: as RBT-92's rule prints it.")
    out += ["Forbidden readings C3 adds:", FORBIDDEN_12, FORBIDDEN_13]
    return out


def part2(part1_text=""):
    T_of = R.onsets()
    seeds, arms = [], {}
    for seed in R.SEEDS:
        T = T_of.get(seed)
        if not isinstance(T, int):
            continue
        k00 = cull_k(seed) == {"holistic": 0, "conventional": 0}  # RBT-92 amendment 2: the null is the baseline itself
        if any(not os.path.exists(os.path.join(arm_path(a, seed), "seasons.txt")) and not (a == "cull" and k00) for a in R.ARMS):
            continue
        A = {a: R.Arm(arm_path(a, seed)) for a in ("base", "shift") + (() if k00 else ("cull",))}
        if k00:
            A["cull"] = A["base"]
        if any(A["base"].alive[k].get(T - 1, 0) == 0 for k in KINDS):
            continue
        if any(A[a].last < T + R.TRANS + R.RECOV + R.TAIL - 1 for a in A):
            continue
        seeds.append((seed, T))
        arms[seed] = A
    n = len(seeds)
    kk = math.ceil(0.8 * n) if n else 0
    TR, RE, TA = R.TRANS, R.RECOV, R.TAIL
    print()
    print("=" * 100)
    print("RBT-100 PART 2: the C3-specific lines (PREREGISTRATION.md sections 3, 4, 6 and Amendment 2); none changes the class")
    print(f"  seeds read: {n}  (the same seeds, T and exclusions as part 1)")
    print()
    print("C3-V1 manipulation: the shift arm's events.txt records food.items = 6 from T")
    bad = 0
    for seed, T in seeds:
        r = shift_record(arm_path("shift", seed))
        ok = r is not None and int(r["season"]) == T and '"food.items"' in r["names"] and '"value": 6' in r["names"]
        bad += not ok
        print(f"  {seed:>5} T={T}: {'ok' if ok else 'FAIL'}  {r['names'] if r else 'no shift record'}")
    print(f"  C3-V1: {'PASS' if not bad else 'FAIL'} on {n - bad}/{n}")
    print()
    print("NULL, diagnostics only (Amendment 2, F1/F2): the impulse null removes k residents at random at T; C3's excess")
    print("  deaths are mostly recruits starving while residents live off stored energy.  C3's TURNOVER GUARD (part 1's")
    print("  'turnover guard' line) IS NOT INTERPRETABLE, a priori: the income loss is density arithmetic, not turnover.")
    print("  excess = shift - base; cohorts by birth season (<T: the onset cohort; >=T: recruits)")
    ALIVE_AT = (10, 30, 40, 60, 100)
    for seed, T in seeds:
        b, s = arms[seed]["base"], arms[seed]["shift"]
        kd = cull_k(seed)
        for k in KINDS:
            cells = []
            for w in (10, 30, 60):
                ds, db = split_deaths(s, k, T, w), split_deaths(b, k, T, w)
                cells.append(f"[T,+{w}) " + " ".join(f"{c[0]}{h} {ds[(c, h)] - db[(c, h)]:+d}" for c in ("starved", "aged") for h in ("<T", ">=T")))
            bd = sum(births(b, k, t) - births(s, k, t) for t in range(T, T + 60))
            ad = [b.alive[k].get(T + w, 0) - s.alive[k].get(T + w, 0) for w in ALIVE_AT]
            print(f"  {seed:>5} {k:12s} k {kd.get(k, '?')}  excess deaths: " + " | ".join(cells)
                  + f"  births deficit [T,+60) {bd:+d}  alive deficit T+{',+'.join(map(str, ALIVE_AT))}: {ad}")
    print()
    print("CLAIM 3 (Amendment 2, rescored; the adversary's wording after its probe P1, n = 1, seed 901, T = 100, not a C3 arm):")
    print("  designed excess deaths of recruits (born >= T) exceed those of the onset cohort (born < T) over [T, T+30),")
    print(f"  on >= ceil(0.8n)/n = {kk}/{n} seeds")
    hits = 0
    for seed, T in seeds:
        ds, db = split_deaths(arms[seed]["shift"], "conventional", T, 30), split_deaths(arms[seed]["base"], "conventional", T, 30)
        young = sum(ds[(c, ">=T")] - db[(c, ">=T")] for c in ("starved", "aged"))
        old = sum(ds[(c, "<T")] - db[(c, "<T")] for c in ("starved", "aged"))
        hits += young > old
        print(f"  {seed:>5}: recruits {young:+d}  onset cohort {old:+d}  {'yes' if young > old else 'no'}")
    print(f"  CLAIM 3: {hits}/{n} -> {'HOLDS' if n and hits >= kk else 'FALSIFIED'}")
    print()
    print("OWN (F3), from own.txt (own_table.py): stored energy a head; the season's own net over the survivors of the season,")
    print("  and its upper bound over everyone who ran it, the starved recruits included (net_all_ub)")
    below = {("shift", k): 0 for k in KINDS}
    below.update({("base", k): 0 for k in KINDS})
    have = 0
    for seed, T in seeds:
        own = {"shift": read_own(arm_path("shift", seed)), "base": read_own(os.path.join(C3, f"base-{seed}"))}
        if not own["shift"] or not own["base"]:
            print(f"  {seed:>5}: own.txt missing ({[a for a in own if not own[a]]}); not read")
            continue
        have += 1
        for a in ("shift", "base"):
            cells = []
            for k in KINDS:
                e = [own[a].get((T + d, k), {}).get("energy_head", "-") for d in (-1, 30, 60)]
                ns_t = own_mean(own[a], k, T, T + TR, "net_survivors")
                ub_r = own_mean(own[a], k, T + TR, T + TR + RE, "net_all_ub")
                ns_r = own_mean(own[a], k, T + TR, T + TR + RE, "net_survivors")
                below[(a, k)] += ub_r is not None and ub_r < R.BASAL
                cells.append(f"{k} E/head T-1,+30,+60 {e}  net survivors transient {R.fmt(ns_t, 3)} recovery {R.fmt(ns_r, 3)}  "
                             f"net all (ub) recovery {R.fmt(ub_r, 3)}")
            print(f"  {seed:>5} {a:>5}  " + "  |  ".join(cells))
    for k in KINDS:
        print(f"  {k:12s}: own net (all who ran, upper bound) below basal 0.25 in the recovery window: "
              f"shift {below[('shift', k)]}/{have}, base {below[('base', k)]}/{have} seeds")
    print()
    print(f"ECHO: onsets (seasons after T) of 10-season deaths windows >= {PEAK} in [T, T+{TR + RE + TA}); recovery window starts {TR}..{TR + RE - 10}")
    inrec = {(a, k): 0 for a in ("shift", "base") for k in KINDS}
    for seed, T in seeds:
        for a in ("shift", "base"):
            cells = []
            for k in KINDS:
                p = peaks(arms[seed][a], k, T, 0, TR + RE + TA)
                inrec[(a, k)] += any(TR <= x <= TR + RE - 10 for x in p)
                cells.append(f"{k} {p}")
            print(f"  {seed:>5} {a:>5}  " + "   ".join(cells))
    for k in KINDS:
        print(f"  {k:12s}: a peak starting inside the recovery window on shift {inrec[('shift', k)]}/{n}, base {inrec[('base', k)]}/{n} seeds"
              + ("  -> the recovery window contains the shift's own echo" if n and inrec[("shift", k)] >= kk and inrec[("base", k)] < kk else ""))
    print()
    print("CLASS D triggers in the shift arm, per seed and fauna (RBT-89 section 9): transient mean < 0.25, recovery mean < 0.25,")
    print("  min alive < 12 over [T, T+160); and the season the fauna reached alive = 0 (relative to T), if it did")
    hold = {}
    for seed, T in seeds:
        s = arms[seed]["shift"]
        cells = []
        for k in KINDS:
            tr = R.wmean(s.x[k], T, T + TR)
            rc = R.wmean(s.x[k], T + TR, T + TR + RE)
            ma = min(s.alive[k].get(t, 0) for t in range(T, T + TR + RE))
            ex = extinct_at(s, k, T)
            trig = [nm for nm, hit in (("transient", tr < R.BASAL), ("recovery", rc < R.BASAL), ("alive<12", ma < R.FLOOR)) if hit]
            cells.append(f"{k} trans {R.fmt(tr, 3)} rec {R.fmt(rc, 3)} min alive {ma:>2} extinct {'-' if ex is None else f'T+{ex - T}'} "
                         f"triggers {'+'.join(trig) or 'none'}")
        # F5(b): the survival reading is the recovery window's only, where every living robot was born after T
        mr = min(s.alive["holistic"].get(t, 0) for t in range(T + TR, T + TR + RE))
        own = read_own(arm_path("shift", seed))
        nsr = own_mean(own, "holistic", T + TR, T + TR + RE, "net_survivors") if own else None
        hold[seed] = "HOLD" if mr >= R.FLOOR and nsr is not None and nsr >= R.BASAL else ("FAIL" if mr < R.FLOOR or (nsr is not None and nsr < R.BASAL) else "UNREAD")
        print(f"  {seed:>5}  " + "  |  ".join(cells) + f"  || co-evolved, recovery window only: min alive {mr}, own net (survivors) {R.fmt(nsr, 3)} -> {hold[seed]}")
    print()
    print(f"DEPTH: median reproduction events after T along the lineages alive at T+{TR + RE} (first parent followed)")
    for k in KINDS:
        for a in ("shift", "base", "cull"):
            v = [depth_after(arms[seed][a], k, T, T + TR + RE) for seed, T in seeds]
            vv = [x for x in v if x is not None]
            print(f"  {k:12s} {a:>5}: per seed {v}  median {statistics.median(vv) if vv else '--'}")
    print()
    print("FOUNDERS (F5): random founders at six items from season 0 (founders6-SEED, 60 seasons, no event): HOLD if >= 12 alive at")
    print("  season 59, else FAIL.  The contrast sentence \"an established population holds where random founders could not\" is")
    print("  printed for a seed only where its co-evolved founders FAIL and its established co-evolved fauna HOLDS in the recovery window")
    contrast, informative, fread = 0, 0, 0
    for seed, T in seeds:
        fp = os.path.join(C3, f"founders6-{seed}")
        if not os.path.exists(os.path.join(fp, "seasons.txt")):
            print(f"  {seed:>5}: founders6 not committed; no contrast on this seed")
            continue
        fread += 1
        F = R.Arm(fp)
        fh, fc = founders_outcome(F, "holistic"), founders_outcome(F, "conventional")
        informative += fh == "FAIL"
        yes = fh == "FAIL" and hold.get(seed) == "HOLD"
        contrast += yes
        print(f"  {seed:>5}: founders co-evolved {fh} ({F.alive['holistic'].get(59, 0)} alive at 59), designed {fc} "
              f"({F.alive['conventional'].get(59, 0)}); established co-evolved {hold.get(seed)} -> "
              + ("an established population holds where random founders could not" if yes else
                 ("no contrast: the founders hold at six items on this seed" if fh == "HOLD" else "no: the established population does not hold")))
    print(f"  contrast sentence on {contrast}/{informative} seeds whose founders fail ({fread}/{n} founders arms read)")
    print()
    print("VERDICT TEXT (F6)")
    cls, r, mrs = parse_part1(part1_text)
    for line in verdict_text(cls, mrs, r):
        print("  " + line.replace("\n", "\n  "))
    return 0


def main():
    print(__doc__.split("\n\n")[0])
    print(f"PART 1: RBT-92's readout.py on C3's arms (shift, cull under {C3}; cull20, onset and base digests under {C1})")
    print()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = R.main()
    print(buf.getvalue(), end="")
    if rc:
        print("PART 1 stopped at validation; part 2 is not printed.")
        return rc
    return part2(buf.getvalue())


if __name__ == "__main__":
    sys.exit(main())
