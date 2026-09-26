"""RBT-92, the first epoch: the readout, from committed tables only.

    python runs/RBT-92/readout.py > runs/RBT-92/readout.txt

Per seed of the seed rule (runs/RBT-92/SEED-RULE.md) it reads four arms that share the seed's
founders, worlds and streams and are byte-identical before the onset T (shared_baseline_check.txt):

    base    the seed's RBT-90 part 2 arm, no event          runs/RBT-90/forage-SEED/
    shift   --shift-at T --shift group-size=8               runs/RBT-92/shift-SEED/
    cull    --cull-at T, k by RBT-89 section 8's rule        runs/RBT-92/cull-SEED/
    cull20  --cull-at T --cull holistic=20,conventional=20   runs/RBT-92/cull20-SEED/

and from each arm only what it commits: seasons.txt, lineage-last.txt, bodysig.txt, events.txt
(tables.py; the baseline's bodysig.txt is at runs/RBT-92/base-SEED/, written by tables.py
--bodysig-only from the RBT-90 arm's restored bulk).  T is read from onset.txt.  Nothing here reads the bulk.

The order is the rule's: VALIDATION first, on the culls, and the shift is read only if the
instrument passed it (RBT-92: "the instrument that reads the event is validated on a random cull
before it reads the shift").

Windows, relative to T (RBT-89 section 8): before [T-100, T), transient [T, T+60), recovery
[T+60, T+160) primary, tail [T+160, T+200).

Readouts (definitions in the pre-registration on RBT-92; restated at each section's head):
  R-body     holistic - conventional mean_lifetime_score, window mean, per arm
  R-shift    shift - base, per fauna;  R-null  shift - cull, per fauna;  R-cull  cull - base
  recovery   first d >= 0 with |x(t) - P| <= h for all t in [T+d, T+d+20): P the fauna's mean
             over [T-100, T), h twice the SD of its per-season values there; "none" if no such
             d <= 180.  Paired form: the same on x_arm(t) - x_base(t) against 0 with the same h.
  carriage   onset cohort C0 = individuals alive at T-1.  L(s): fraction of C0 with a descendant
             (self included, every parent followed: RBT-84's descent rule) alive at s.  B(s):
             fraction of the holistic individuals alive at s whose body structure equals that of
             at least one of their C0 ancestors.  S(s): fraction of the distinct holistic body
             structures present in C0 that are present at s.

Every mean over seeds is printed with its t(n-1) 95% interval and every threshold as k/n.

Environment overrides exist for the smoke test on a throwaway run only: RBT92_WINDOWS
("before,transient,recovery,tail,run" window lengths and the 20-season run length),
RBT92_SEEDS, RBT92_BASE_DIR, RBT92_ARM_DIR, RBT92_ONSET.
"""
import csv
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = ("holistic", "conventional")
SEEDS = [int(s) for s in os.environ.get("RBT92_SEEDS", "801 804 805 806 807 1 2 3 4 7").split()]
BASE_DIR = os.environ.get("RBT92_BASE_DIR", "runs/RBT-90")
ARM_DIR = os.environ.get("RBT92_ARM_DIR", "runs/RBT-92")
ONSET = os.environ.get("RBT92_ONSET", os.path.join(HERE, "onset.txt"))
BEFORE, TRANS, RECOV, TAIL, RUN = (int(x) for x in os.environ.get("RBT92_WINDOWS", "100,60,100,40,20").split(","))
MAXD = TRANS + RECOV + TAIL - RUN
BASAL = 0.25
FLOOR = 12  # a fifth of capacity (RBT-89 section 9, class D)
EPS = 0.10  # the smallest effect worth claiming (RBT-89 section 7)
BMIN = 8  # class B needs >= 8 seeds read: on the prior SD 0.108, t(7) gives 0.090 and t(5) 0.113 (coordinator ruling 13:10 item 4)
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262,
        10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131}
ARMS = ("base", "shift", "cull", "cull20")


def arm_path(arm, seed):
    return os.path.join(BASE_DIR, f"forage-{seed}") if arm == "base" else os.path.join(ARM_DIR, f"{arm}-{seed}")


def tsv(path):
    return list(csv.DictReader(open(path), delimiter="\t"))


def cull_k_of(seed):
    """The k per fauna from cull-k-SEED.txt's rule line, or {} if the file is not there."""
    kf = os.path.join(ARM_DIR, f"cull-k-{seed}.txt")
    if not os.path.exists(kf):
        return {}
    for line in open(kf):
        if line.startswith("cull\t"):
            return {p.split("=")[0]: int(p.split("=")[1]) for p in line.split("\t")[1].strip().split(",")}
    return {}


def onsets():
    out = {}
    for line in open(ONSET):
        f = line.rstrip("\n").split("\t")
        if f[0].lstrip("-").isdigit():
            out[int(f[0])] = int(f[1]) if f[1].isdigit() else f[1]
    return out


class Arm:
    """One arm's committed tables."""

    def __init__(self, path, bodysig=None):
        self.path = path
        rows = tsv(os.path.join(path, "seasons.txt"))
        self.raw = {(int(r["season"]), r["population"]): r for r in rows}
        self.last = max(s for s, _ in self.raw)
        self.x = {k: {} for k in KINDS}
        self.alive = {k: {} for k in KINDS}
        self.deaths = {k: {} for k in KINDS}
        for (s, k), r in self.raw.items():
            self.x[k][s] = float(r["mean_lifetime_score"])
            self.alive[k][s] = int(r["alive"])
            self.deaths[k][s] = int(r["deaths"])
        for k in KINDS:  # a fauna that died out and whose table stops: alive 0 to the end (RBT-89 section 13)
            for s in range(self.last + 1):
                self.alive[k].setdefault(s, 0)
                self.deaths[k].setdefault(s, 0)
                if self.alive[k][s] == 0:
                    # a dead population earns nothing: income 0 in every season from extinction on, in every
                    # window and test (senior review (a), coordinator ruling 13:10 item 1), never skipped
                    self.x[k][s] = 0.0
        self.culled = {}
        self.shift_at = None
        ev = os.path.join(path, "events.txt")
        if os.path.exists(ev):
            for r in tsv(ev):
                if r["kind"] == "cull":
                    self.culled[(r["population"], int(r["season"]))] = r["names"].split(",") if r["names"] else []
                elif r["kind"] == "shift":
                    self.shift_at = int(r["season"])
        culled_names = {n: s for (_, s), ns in self.culled.items() for n in ns}
        self.ind = {}
        self.lastrows = tsv(os.path.join(path, "lineage-last.txt"))
        for r in self.lastrows:
            g, a = int(r["generation"]), int(r["age"])
            if r["name"] in culled_names:
                # a culled row is logged at the top of season T, before the season ages anyone: it repeats the
                # age of season T - 1 (found by V2 in the smoke test), so the individual lived [T-1-a, T-1]
                g -= 1
            self.ind[(r["population"], r["name"])] = (g - a, g, [p for p in r["parents"].split(",") if p])
        self.body = {}
        bs = bodysig or os.path.join(path, "bodysig.txt")
        if os.path.exists(bs):
            for r in tsv(bs):
                if r["body"] != "-":
                    self.body[(r["population"], r["name"])] = r["body"]
        self._alive_sets = {}
        self._anc = {}

    def alive_at(self, kind, s):
        key = (kind, s)
        if key not in self._alive_sets:
            self._alive_sets[key] = {n for (k, n), (b, l, _) in self.ind.items() if k == kind and b <= s <= l}
        return self._alive_sets[key]

    def check_alive(self, kind, s0, s1):
        """Round trip: the reconstruction from lineage-last must equal seasons.txt's alive."""
        return [s for s in range(s0, s1) if len(self.alive_at(kind, s)) != self.alive[kind].get(s, 0)]

    def anc0(self, kind, name, c0):
        """The members of the onset cohort c0 that are name or its ancestors, every parent followed."""
        key = (kind, name)
        if key in self._anc:
            return self._anc[key]
        stack, seen, out = [name], set(), set()
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            if n in c0:
                out.add(n)
                continue
            stack.extend(self.ind.get((kind, n), (0, 0, []))[2])
        self._anc[key] = frozenset(out)
        return self._anc[key]

    def carriage(self, kind, T, s):
        c0 = self.alive_at(kind, T - 1)
        now = self.alive_at(kind, s)
        if not c0:
            return None
        reached = set()
        for n in now:
            reached |= self.anc0(kind, n, c0)
        L = len(reached) / len(c0)
        B = S = None
        if kind == "holistic" and self.body:
            ok = [n for n in now if (kind, n) in self.body]
            if ok:
                B = sum(1 for n in ok if self.body[(kind, n)] in {self.body.get((kind, c)) for c in self.anc0(kind, n, c0)}) / len(ok)
            b0 = {self.body[(kind, c)] for c in c0 if (kind, c) in self.body}
            bn = {self.body[(kind, n)] for n in now if (kind, n) in self.body}
            S = len(b0 & bn) / len(b0) if b0 else None
        return L, B, S


def wmean(series, a, b):
    v = [series[s] for s in range(a, b) if s in series]
    return statistics.fmean(v) if v else float("nan")


def rbody(arm, a, b):
    """Window mean of holistic - conventional income over every season of [a, b); an extinct fauna earns 0."""
    v = [arm.x["holistic"][s] - arm.x["conventional"][s] for s in range(a, b)
         if s in arm.x["holistic"] and s in arm.x["conventional"]]
    return statistics.fmean(v) if v else float("nan")


def recovery(xs, target, h, T):
    """First d in [0, MAXD] with |xs(t) - target(t)| <= h for all t in [T+d, T+d+RUN); None if none."""
    for d in range(0, MAXD + 1):
        ts = range(T + d, T + d + RUN)
        if all(t in xs and abs(xs[t] - target(t)) <= h for t in ts):
            return d
    return None


def classify(n, m, r, pos, neg, e1, dz, e2):
    """RBT-89 section 9's classes as amended here: E1 > D > E2 > A > C > B > F. The sign guard and the class tests
    count over all n seeds read (an extinct fauna earns 0, so no seed drops out: adversary F4)."""
    kk = math.ceil(0.8 * n) if n else 0
    if n < 6:
        return "NONE: below the six-seed floor"
    if e1 >= kk:
        return "E1. both fail"
    if dz >= kk:
        return "D. designed bankrupt"
    if e2 >= kk:
        return ("E2. co-evolved bankrupt, designed not -- reported WITH THE FALSIFIER as its strongest form: "
                "\"the designed body wins after the shift\"")
    if m >= EPS and pos >= kk and abs(m) >= r:
        return "A. co-evolved wins"
    if m <= -EPS and neg >= kk and abs(m) >= r:
        return "C. designed wins -- THE FALSIFIER: \"the designed body wins after the shift\""
    if abs(m) < EPS and r <= EPS and n >= BMIN:
        return "B. draw"
    return "F. unresolved"


def ci(vals):
    v = [x for x in vals if x is not None and not math.isnan(x)]
    n = len(v)
    if n == 0:
        return "n=0"
    m = statistics.fmean(v)
    if n < 2:
        return f"{m:+.4f} (n=1, no interval)"
    sd = statistics.stdev(v)
    hw = T975.get(n - 1, 1.96) * sd / math.sqrt(n)
    pos = sum(1 for x in v if x > 0)
    return f"{m:+.4f}  95% t({n - 1}) [{m - hw:+.4f}, {m + hw:+.4f}]  sd {sd:.4f}  positive {pos}/{n}"


def stat(vals):
    v = [x for x in vals if x is not None and not math.isnan(x)]
    n = len(v)
    m = statistics.fmean(v) if v else float("nan")
    sd = statistics.stdev(v) if n > 1 else float("nan")
    hw = T975.get(n - 1, 1.96) * sd / math.sqrt(n) if n > 1 else float("nan")
    return n, m, sd, hw


def fmt(x, p=4):
    return "  --  " if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.{p}f}"


def fmtd(d):
    return "none" if d is None else str(d)


def main():
    T_of = onsets()
    print(__doc__.split("\n\n")[0])
    print(f"windows: before {BEFORE}, transient {TRANS}, recovery {RECOV}, tail {TAIL}; recovery run {RUN} seasons"
          + ("   ** SMOKE-TEST WINDOWS (RBT92_WINDOWS set): read for nothing **" if "RBT92_WINDOWS" in os.environ else ""))
    print()
    # ---------------------------------------------------------------- seeds, exclusion
    seeds, arms = [], {}
    print("SEEDS (seed rule: all ten, extinction at or before T - 1 in the baseline the only exclusion)")
    for seed in SEEDS:
        T = T_of.get(seed)
        if not isinstance(T, int):
            print(f"  {seed}: no onset ({T}); not read")
            continue
        k00 = cull_k_of(seed) == {"holistic": 0, "conventional": 0}
        missing = [a for a in ARMS if not os.path.exists(os.path.join(arm_path(a, seed), "seasons.txt"))
                   and not (a == "cull" and k00)]
        if missing:
            print(f"  {seed}: T={T}; arms not committed: {missing}; not read (a partial set is not a result)")
            continue
        # the baseline's body digests are RBT-92's derivation from RBT-90's bulk, committed under RBT-92
        A = {a: Arm(arm_path(a, seed), os.path.join(ARM_DIR, f"base-{seed}", "bodysig.txt") if a == "base" else None)
             for a in ARMS if not (a == "cull" and k00)}
        if k00:
            # k = 0 for both faunas: no event, so the null IS the baseline, byte for byte (the cull arm is not
            # run; run_arm.sh exits 0). R-null = R-shift for this seed, said in the line below.
            A["cull"] = A["base"]
            print(f"  {seed}: cull-k is 0/0: the null is the baseline itself; R-null = R-shift on this seed")
        dead = [k for k in KINDS if A["base"].alive[k].get(T - 1, 0) == 0]
        if dead:
            print(f"  {seed}: T={T}; EXCLUDED: {'+'.join(dead)} extinct by T - 1 in the baseline")
            continue
        short = [a for a in ARMS if A[a].last < T + TRANS + RECOV + TAIL - 1]
        if short:
            print(f"  {seed}: T={T}; arms that did not run to T + {TRANS + RECOV + TAIL}: {short}; not read")
            continue
        seeds.append((seed, T))
        arms[seed] = A
        b = A["base"]
        d_after = sum(b.deaths[k].get(s, 0) for s in range(T, T + 10) for k in KINDS)
        d_ref = sum(b.deaths[k].get(s, 0) for s in range(T - 100, T) for k in KINDS) / 10
        flag = d_after > 1.5 * d_ref
        kk_ = cull_k_of(seed)
        print(f"  {seed}: T={T}  read;  baseline deaths [T,T+10) {d_after} against its mean per 10 seasons over [T-100,T) "
              f"{d_ref:.1f}" + ("  ** FLAG: more than half above: the wave drifted off period 60 on this seed (a caveat, "
                                "not a re-pick; coordinator 14:12) **" if flag else "")
              + f";  cull-k {kk_ or 'missing'}" + ("  (k = 0 on both: R-null = R-shift by construction)"
                                                     if kk_ == {"holistic": 0, "conventional": 0} else ""))
    n = len(seeds)
    print(f"  seeds read: {n}/{len(SEEDS)}" + ("   BELOW THE SIX-SEED FLOOR: no verdict is issued" if n < 6 else ""))
    print()

    # ---------------------------------------------------------------- validation
    print("VALIDATION (on the culls, before the shift is read)")
    print("  V0 pre-onset identity: every arm's seasons.txt row equals the baseline's for every season < T, both faunas;")
    print("     and every lineage-last.txt row of an individual that died before T (last row < T - 1) is identical to the baseline's")
    print("  V1 manipulation: events.txt carries exactly the stated cull at T (cull20: min(20, alive) of each fauna; cull:")
    print("     cull-k-SEED.txt), no cull elsewhere; the shift arm's entries carry the shift from T to the end")
    print("  V2 round trip: the alive count rebuilt from lineage-last.txt equals seasons.txt's in every season of [T-100, T+200),")
    print("     every arm and fauna (so the descent tracer reads the population the table reports)")
    print("  V3 manipulation check on the tracer (adversary F2: guaranteed by construction if the tracer reads its files; it")
    print("     validates L, not a shift-sized effect): cull20 - base on L(T+60), holistic, has a t(n-1) 95% interval below 0;")
    print("     the paired alive dip min over [T, T+10) of alive_cull20 - alive_base is below 0 on n/n seeds, both faunas")
    fails = []
    capped = {}
    for seed, T in seeds:
        A = arms[seed]
        for a in ("shift", "cull", "cull20"):
            bad = [(s, k) for (s, k), r in A["base"].raw.items() if s < T and
                   any(r[c] != A[a].raw.get((s, k), {}).get(c) for c in ("alive", "births", "deaths", "mean_lifetime_score", "best_lifetime_score"))]
            if bad:
                fails.append(f"V0 {seed} {a}: {len(bad)} pre-onset rows differ from the baseline, first {sorted(bad)[0]}")
            # every individual that died before T: its committed lineage-last row is identical. Its last row is
            # the season before it died, so "died before T" is generation < T - 1 (who dies DURING season T is
            # the event's business: the smoke test caught the < T form failing on every arm for exactly that)
            key = lambda r: tuple(r[c] for c in ("population", "name", "generation", "age", "evals", "fitness", "parents"))
            pre_b = {key(r) for r in A["base"].lastrows if int(r["generation"]) < T - 1}
            pre_a = {key(r) for r in A[a].lastrows if int(r["generation"]) < T - 1}
            if pre_a != pre_b:
                fails.append(f"V0 {seed} {a}: lineage-last rows ending before T differ from the baseline "
                             f"({len(pre_a ^ pre_b)} rows in one and not the other, of {len(pre_b)})")
        want_k = cull_k_of(seed)
        # the switch removes min(k, alive) (ecology.py _cull), so V1 compares the cull arm with that, as it does
        # cull20; a k at or above the fauna's alive at T - 1 empties it: the null for that fauna is extinction,
        # not turnover, and its R-null is n/a (RBT-99 adversary F1, F3)
        alive_T = {k: A["base"].alive[k].get(T - 1, 0) for k in KINDS}
        capped[seed] = sorted(k for k in KINDS if want_k.get(k, 0) > 0 and want_k.get(k, 0) >= alive_T[k])
        want_cull = {k: min(want_k[k], alive_T[k]) for k in want_k}
        for k in capped[seed]:
            print(f"  V1 note {seed}: cull-k {k}={want_k[k]} >= alive {alive_T[k]} at T - 1: the cull empties the fauna; "
                  f"V1 expects {want_cull[k]}; R-null for {k} on this seed is n/a (the null is extinction, not turnover)")
        for a, want in (("cull20", {k: min(20, alive_T[k]) for k in KINDS}), ("cull", want_cull)):
            got = {k: len(A[a].culled.get((k, T), [])) for k in KINDS}
            other = [key for key in A[a].culled if key[1] != T]
            if got != {k: want.get(k, -1) for k in KINDS} or other:
                fails.append(f"V1 {seed} {a}: culled at T {got}, stated {want}, culls at other seasons {other}")
        if A["shift"].shift_at != T:
            fails.append(f"V1 {seed} shift: shift recorded from {A['shift'].shift_at}, T = {T}")
        for a in ARMS:
            for k in KINDS:
                bad = A[a].check_alive(k, max(0, T - BEFORE), T + TRANS + RECOV + TAIL)
                if bad:
                    fails.append(f"V2 {seed} {a} {k}: rebuilt alive differs from seasons.txt at {len(bad)} seasons, first {bad[0]}")
    L20 = [(A20.carriage("holistic", T, T + TRANS)[0] - Ab.carriage("holistic", T, T + TRANS)[0])
           for (seed, T) in seeds for A20, Ab in [(arms[seed]["cull20"], arms[seed]["base"])]]
    dips = {k: [min(arms[seed]["cull20"].alive[k].get(s, 0) - arms[seed]["base"].alive[k].get(s, 0) for s in range(T, T + 10))
                for seed, T in seeds] for k in KINDS}
    nL, mL, sdL, hwL = stat(L20)
    print(f"  V3 cull20 - base, L(T+{TRANS}) holistic: {ci(L20)}")
    for k in KINDS:
        print(f"  V3 cull20 - base, min paired alive over [T, T+10), {k}: {dips[k]}  below 0 on {sum(1 for d in dips[k] if d < 0)}/{n}")
    v3 = n >= 2 and (mL + hwL) < 0 and all(sum(1 for d in dips[k] if d < 0) == n for k in KINDS)
    for f in fails:
        print("  FAIL " + f)
    v012 = not fails
    print(f"  V0-V2: {'PASS' if v012 else 'FAIL'} on {n - len({f.split()[1] for f in fails})}/{n} seeds;  V3: {'PASS' if v3 else 'FAIL'}")
    print()
    if not v012:
        print("INSTRUMENT FAILED VALIDATION (V0-V2): the shift is not read.")
        return 1
    carriage_note = "" if v3 else "  [UNVALIDATED: the V3 manipulation check failed: the tracer did not register a k = 20 cull at this n]"

    # ---------------------------------------------------------------- power line (RBT-89 section 7)
    print("POWER (RBT-89 section 7's line, from each seed's baseline over [T-100, T))")
    sds = {k: [] for k in KINDS}
    sdd = []
    for seed, T in seeds:
        b = arms[seed]["base"]
        for k in KINDS:
            sds[k].append(statistics.stdev([b.x[k][s] for s in range(T - BEFORE, T)]))
        sdd.append(statistics.stdev([b.x["holistic"][s] - b.x["conventional"][s] for s in range(T - BEFORE, T)]))
    tcrit = T975.get(n - 1, 1.96) if n > 1 else float("nan")
    s_d = statistics.fmean(sdd) if sdd else float("nan")
    season_r = tcrit * s_d / math.sqrt(RECOV) / math.sqrt(n) if n else float("nan")
    rb_rec = [rbody(arms[seed]["shift"], T + TRANS, T + TRANS + RECOV) for seed, T in seeds]
    _, _, sd_seed, hw_seed = stat(rb_rec)
    r = max(season_r, hw_seed) if n > 1 else float("nan")
    print(f"  instrument: baseline window SD of mean_lifetime_score holistic {statistics.fmean(sds['holistic']) if n else float('nan'):.4f}, "
          f"conventional {statistics.fmean(sds['conventional']) if n else float('nan'):.4f} (mean over seeds) -> paired (co-evolved - designed) "
          f"per-season SD {s_d:.4f} -> SD of a {RECOV}-season window mean {s_d / math.sqrt(RECOV):.4f}; smallest R-body resolvable at "
          f"t({n - 1}) 95% with n={n} seeds: {season_r:.4f} (season noise only, ignores autocorrelation) versus {hw_seed:.4f} from the "
          f"observed spread of the per-seed differences (sd {sd_seed:.4f})")
    print(f"  r = {r:.4f} (the larger);  pre-registered expectation from RBT-89's measured SD 0.108: t(5) 0.113 at n=6, t(7) 0.090 at n=8, "
          f"t(9) 0.077 at n=10; class B needs n >= {BMIN}: {'reachable' if n >= BMIN else 'NOT reachable at this n'}")
    print("  note: the season-noise figure divides by sqrt(W) as if seasons were independent; the 60-season wave makes them")
    print("  autocorrelated, so it understates; the between-seed figure is the binding one and r takes the larger")
    print()

    # ---------------------------------------------------------------- the shift and its nulls
    W = {"before": (-BEFORE, 0), "transient": (0, TRANS), "recovery": (TRANS, TRANS + RECOV), "tail": (TRANS + RECOV, TRANS + RECOV + TAIL)}
    print("R-BODY: holistic - conventional mean_lifetime_score, window mean, per seed (the co-evolved against designed contrast)")
    print(f"  {'seed':>5} {'T':>4} {'arm':>7} " + " ".join(f"{w:>10}" for w in W))
    per = {(a, w): [] for a in ARMS for w in W}
    for seed, T in seeds:
        for a in ARMS:
            vals = [rbody(arms[seed][a], T + lo, T + hi) for lo, hi in W.values()]
            for w, v in zip(W, vals):
                per[(a, w)].append(v)
            print(f"  {seed:>5} {T:>4} {a:>7} " + " ".join(f"{fmt(v):>10}" for v in vals))
    for a in ARMS:
        for w in W:
            print(f"  mean {a:>7} {w:>10}: {ci(per[(a, w)])}")
    print()

    print("R-SHIFT (shift - base), R-NULL (shift - cull), R-CULL (cull - base), R-CULL20 (cull20 - base): window mean of the per-season difference, per fauna")
    contrasts = (("R-shift", "shift", "base"), ("R-null", "shift", "cull"), ("R-cull", "cull", "base"), ("R-cull20", "cull20", "base"))
    for name, a1, a0 in contrasts:
        for k in KINDS:
            for w, (lo, hi) in W.items():
                if w == "before":
                    continue
                v = []
                na = []
                for seed, T in seeds:
                    if name == "R-null" and k in capped.get(seed, ()):
                        na.append(seed)  # the null emptied this fauna: extinction, not turnover (F3)
                        v.append(float("nan"))
                        continue
                    x1, x0 = arms[seed][a1].x[k], arms[seed][a0].x[k]
                    d = [x1[s] - x0[s] for s in range(T + lo, T + hi) if s in x1 and s in x0]  # extinct = 0, never skipped
                    v.append(statistics.fmean(d) if d else float("nan"))
                print(f"  {name:8s} {k:12s} {w:9s}: per seed [{', '.join(fmt(x, 3) for x in v)}]  mean {ci(v)}"
                      + (f"  (n/a on {na}: the cull emptied the fauna)" if na else ""))
    print()

    print(f"RECOVERY TIME (seasons after T; run of {RUN}; 'none' = not within {MAXD}). PRIMARY, paired against the control "
          f"(RBT-89 section 8; adversary F10): first d with |x_arm - x_base| <= h for {RUN} seasons. Secondary, in brackets: "
          f"against the pre-event plateau P; the base's own P-form d is that form's floor")
    rec = {(a, k): [] for a in ARMS for k in KINDS}
    recP = {(a, k): [] for a in ARMS for k in KINDS}
    for seed, T in seeds:
        line = []
        for k in KINDS:
            base = arms[seed]["base"]
            pre = [base.x[k][s] for s in range(T - BEFORE, T)]
            P, h = statistics.fmean(pre), 2 * statistics.stdev(pre)
            for a in ARMS:
                d = recovery(arms[seed][a].x[k], lambda t: P, h, T)
                dp = recovery(arms[seed][a].x[k], lambda t: base.x[k].get(t, float("nan")), h, T)
                rec[(a, k)].append(dp)
                recP[(a, k)].append(d)
                line.append(f"{k[:4]} {a}:{fmtd(dp)}[{fmtd(d)}]")
            line.append(f"(P {P:.3f}, h {h:.3f})")
        print(f"  {seed:>5}: " + "  ".join(line))
    for label, R, arms_ in (("paired (primary)", rec, ARMS[1:]), ("against P (secondary)", recP, ARMS)):
        for k in KINDS:
            for a in arms_:
                ds = R[(a, k)]
                fin = [d for d in ds if d is not None]
                print(f"  {label:22s} {k:12s} {a:7s}: recovered within {MAXD} on {len(fin)}/{len(ds)} seeds; median of the "
                      f"recovered {statistics.median(fin) if fin else '--'}; per seed {[fmtd(d) for d in ds]}"
                      + ("   <- the P-form's floor" if a == "base" else ""))
    print()

    print("REMAINDER GROUPS (C1 owes which robots the remainder group held; adversary F5): shift arm, per window and fauna, the")
    print("  robot-weighted share in groups below the modal size, and the robot-weighted mean group size, from groups.txt")
    for seed, T in seeds:
        gp = os.path.join(arm_path("shift", seed), "groups.txt")
        if not os.path.exists(gp):
            print(f"  {seed}: groups.txt missing")
            continue
        G = {}
        for row in tsv(gp):  # not "r": that is the power figure the verdict reads (the smoke test caught the clobber)
            G[(int(row["season"]), row["population"])] = [int(x) for x in row["sizes"].split(",") if x]
        cells = []
        for k in KINDS:
            for w, (lo, hi) in list({"transient": (0, TRANS), "recovery": (TRANS, TRANS + RECOV)}.items()):
                robots = small = wsum = 0
                for s_ in range(T + lo, T + hi):
                    sz = G.get((s_, k), [])
                    if not sz:
                        continue
                    modal = max(set(sz), key=sz.count)
                    robots += sum(sz)
                    small += sum(x for x in sz if x < modal)
                    wsum += sum(x * x for x in sz)
                cells.append(f"{k[:4]} {w}: small {small}/{robots} robot-seasons, mean size {wsum / robots if robots else float('nan'):.2f}")
        print(f"  {seed:>5}: " + ";  ".join(cells))
    print()

    print("ALIVE and deaths: min alive over the transient, recovery, tail; deaths over [T, T+10) (the cull rule's window)")
    for seed, T in seeds:
        for k in KINDS:
            cells = []
            for a in ARMS:
                al = arms[seed][a].alive[k]
                cells.append(f"{a}: " + "/".join(str(min(al.get(s, 0) for s in range(T + lo, T + hi))) for lo, hi in list(W.values())[1:])
                             + f" d10 {sum(arms[seed][a].deaths[k].get(s, 0) for s in range(T, T + 10))}")
            print(f"  {seed:>5} {k:12s} " + "   ".join(cells))
    print()

    print("CARRIAGE through the descent DAG (every parent followed; RBT-84's rule, the protocol's tracer) of the onset cohort")
    print("  C0 = alive at T-1: L = fraction of C0 with a living descendant, holistic and conventional (Lconv)" + carriage_note)
    print("  (B and S, body-structure carriage, are dropped before launch: the digest changes on 85% of births and they read")
    print("  0 on the base by T+79, so they had no range; adversary F3. No claim of a structure acquired after T is made.)")
    marks = {"T+60": TRANS, "T+160": TRANS + RECOV, "T+199": TRANS + RECOV + TAIL - 1}
    car = {(a, m, q): [] for a in ARMS for m in marks for q in ("L", "Lc")}
    for seed, T in seeds:
        for a in ARMS:
            cells = []
            for m, off in marks.items():
                L = arms[seed][a].carriage("holistic", T, T + off)
                Lc = arms[seed][a].carriage("conventional", T, T + off)
                L = L[0] if L else None
                Lc = Lc[0] if Lc else None
                car[(a, m, "L")].append(L)
                car[(a, m, "Lc")].append(Lc)
                cells.append(f"{m}: L {'--' if L is None else f'{L:.3f}'} Lconv {'--' if Lc is None else f'{Lc:.3f}'}")
            print(f"  {seed:>5} {a:>7}  " + "  |  ".join(cells))
    for m in marks:
        for q in ("L", "Lc"):
            for name, a1, a0 in (("shift-base", "shift", "base"), ("shift-cull", "shift", "cull"), ("cull20-base", "cull20", "base")):
                v = [(x - y) if x is not None and y is not None else None for x, y in zip(car[(a1, m, q)], car[(a0, m, q)])]
                print(f"  {m:6s} {q:2s} {name:11s}: {ci(v)}")
    print()

    # ---------------------------------------------------------------- verdict
    print("VERDICT (RBT-89 section 9 on R-body, shift arm, recovery window; r from POWER; sign guard ceil(0.8n)/n)")
    nn, m, _, _ = stat(rb_rec)
    guard = math.ceil(0.8 * nn) if nn else 0
    pos = sum(1 for x in rb_rec if x > 0)
    neg = sum(1 for x in rb_rec if x < 0)
    kk = math.ceil(0.8 * n) if n else 0
    dz = e1 = e2 = 0
    for seed, T in seeds:
        s = arms[seed]["shift"]
        lo, hi = T, T + TRANS + RECOV

        def bankrupt(k):
            # D's test, used for both faunas: transient or recovery income below the basal cost, or alive below a fifth
            # of capacity (which covers reaching 0); an extinct fauna earns 0, so extinction is bankrupt by income too
            return (wmean(s.x[k], T, T + TRANS) < BASAL or wmean(s.x[k], T + TRANS, hi) < BASAL
                    or min(s.alive[k].get(t, 0) for t in range(lo, hi)) < FLOOR)
        bh, bc = bankrupt("holistic"), bankrupt("conventional")
        dz += bc and not bh
        e1 += bh and bc
        e2 += bh and not bc
    print(f"  R-body recovery, shift arm: mean {fmt(m)}  r {r:.4f}  positive {pos}/{nn}  negative {neg}/{nn}  guard {guard}/{nn}")
    print(f"  class tests on {kk}/{n} seeds: E1 both bankrupt {e1}/{n};  D designed bankrupt, co-evolved not {dz}/{n};  "
          f"E2 co-evolved bankrupt, designed not {e2}/{n}")
    cls = classify(n, m, r, pos, neg, e1, dz, e2)
    print(f"  CLASS: {cls}")
    print(f"  equivalence form beside B (adversary F8): |mean| + r = {abs(m) + r:.4f} "
          f"{'<' if abs(m) + r < EPS else '>='} {EPS}: the interval {'lies' if abs(m) + r < EPS else 'does not lie'} inside +-{EPS}")
    rs = []
    for seed, T in seeds:
        x1, x0 = arms[seed]["shift"].x["holistic"], arms[seed]["base"].x["holistic"]
        rs.append(statistics.fmean([x1[s] - x0[s] for s in range(T + TRANS, T + TRANS + RECOV) if s in x1 and s in x0] or [float("nan")]))
    _, mrs, _, _ = stat(rs)
    print(f"  'holds up' needs co-evolved R-shift (recovery) >= -r: {fmt(mrs)} against {-r:+.4f} -> "
          f"{'holds up' if mrs >= -r else 'does not hold up (a class-A result would read: outlasts, not holds up)'}")
    rn = []
    for seed, T in seeds:
        if "holistic" in capped.get(seed, ()):
            continue  # the null emptied the co-evolved fauna on this seed: no turnover to compare with (F3)
        if cull_k_of(seed).get("holistic", 0) == 0:
            continue  # k = 0 for the co-evolved fauna: its null is the control, R-null = R-shift by construction (F6)
        x1, x0 = arms[seed]["shift"].x["holistic"], arms[seed]["cull"].x["holistic"]
        rn.append(statistics.fmean([x1[s] - x0[s] for s in range(T + TRANS, T + TRANS + RECOV) if s in x1 and s in x0] or [float("nan")]))
    _, mrn, _, _ = stat(rn)
    print(f"  turnover guard, on the {len(rn)}/{n} seeds with co-evolved k > 0: co-evolved R-null (recovery) {fmt(mrn)}; |R-null| < r means the shift did to co-evolved income no more than "
          f"a same-size random cull: {'YES' if abs(mrn) < r else 'no'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
