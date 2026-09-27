"""The pre-registered readout for RBT-111: are the arena's stream keys exchangeable?

Sixteen fresh seeds (217-232), each at holistic stream salts 0, 1 and 2 (arms s0, s1, s2), on RBT-96's
instrument exactly as RBT-108 ran it.  Per run, y = the mean champ_holistic_mean over the checkpoints at
generation >= 200 (RBT-85's summary(), as RBT-96 and RBT-108 read it).  Per seed:

    c0  = (y_s1 + y_s2) / 2 - y_s0     salt 0 against the non-zero salts
    c12 = y_s2 - y_s1                  two non-zero salts

1. Completion and the pairing check per seed: the three arms' conventional lineage hashes identical, their
   holistic lineage hashes pairwise different, terrain and start seeds identical at every generation.
   A seed that fails is reported, not dropped; any incomplete arm makes the readout NOT A RESULT.
2. Primary: per contrast, mean, median, 20%-trimmed mean, count positive, and an exact two-sided p; Holm over
   the two at alpha = 0.05.  c0 by the exact within-seed permutation test over the 3^16 labellings of the s0
   label (exact under key exchangeability whatever the run noise; RBT-111 design adversary F2); c12 by the exact
   sign-flip test over its 2^16 sign assignments (c12 is symmetric under exchangeability).
3. The reading, fixed in PREREGISTRATION.md before any arm (READING below).
4. Descriptive: c0's 95% interval by inverting the permutation test, and what it says at delta = 0.082 and 0.05.
5. Secondary (stated before any arm): the same two contrasts and tests on generation 0's champion row, Holm.
6. Descriptive only, no reading: s1 - s0 (RBT-108's contrast out of sample), s2 - s0, and the RMS of c12.

    python runs/RBT-111/readout.py [--seeds 217,...,232] [--root runs/RBT-111] [--write-summaries | --from-summaries | --summaries-only]

--write-summaries writes generations.txt, opponent.txt and conventional-digest.txt (RBT-96's summaries) in
every arm directory that holds analysis.json, then reads as usual.  --summaries-only writes them and exits
without reading (drive.sh's per-slot call).  No simulation.  Pure Python: no package needed.
"""
import bisect
import importlib.util
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rbt96_readout", os.path.join(HERE, "..", "RBT-96", "readout.py"))
r96 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r96)
r85 = r96.r85

SEEDS = tuple(range(217, 233))
ARMS = ("s0", "s1", "s2")
ALPHA = 0.05
TOL = 1e-12
DELTA_OBSERVED, DELTA_SMALL = 0.082, 0.05  # RBT-108's post hoc mean d over 205-216, and a winner's-curse allowance

READING = {
    "keys": "KEYS NOT EXCHANGEABLE: c12 != 0, so two non-zero salts differ. Re-examine every key contrast in the programme"
            " (every A/A, RBT-105's replicate histories, possibly seeds).",
    "salt0": "SALT 0's OFFSET: c0 != 0 and c12 ~ 0. Search outside the salt code path; every salt-0 run carries that stream family's bias.",
    "chance": "CHANCE at an offset the size of RBT-108's (delta ~ 0.082): RBT-108's offset was a post hoc false alarm and the"
              " registered RMS null (h 0.159) stands.  A null at delta = 0.05 is NOT DECIDED (the design's power there is"
              " 0.38-0.62 at 16 seeds).",
}
GEN0_CONSEQUENCE = ("FOUNDERS DIFFER BY SALT: a generation-0 contrast is rejected.  This does not change the primary reading;"
                    " it opens a draw-level code-path search.")
GEN0_CHANCE_QUALIFIER = "qualifier: the founders differ by salt, but the final fifth does not."
SALT0_BESIDE = ("beside the 'salt 0' reading (description only; a salt-0 offset predicts both of the same sign and similar size,"
                " and a missed salt-1 or salt-2 excess can also read 'salt 0'):")


# --- the tests -------------------------------------------------------------------------------------

def sign_flip_p(xs):
    """Exact two-sided sign-flip test on the mean: the share of the 2^n sign assignments whose |sum| reaches
    the observed |sum|.  Returns (p, count, 2^n)."""
    n, obs = len(xs), abs(sum(xs))
    sums = [0.0]
    for x in xs:  # all 2^n signed partial sums, built one element at a time
        sums = [s + x for s in sums] + [s - x for s in sums]
    hit = sum(abs(s) >= obs - TOL for s in sums)
    return hit / 2 ** n, hit, 2 ** n


def _c0_choices(row):
    """The three values c0 takes for one seed as the s0 label moves over its three runs (they sum to 0)."""
    a, b, c = row
    return ((b + c) / 2 - a, (a + c) / 2 - b, (a + b) / 2 - c)


def _half_sums(choices):
    sums = [0.0]
    for ch in choices:
        sums = [s + v for s in sums for v in ch]
    return sums


def perm_c0_p(rows):
    """Exact two-sided within-seed permutation test for c0.  rows = [(y_s0, y_s1, y_s2), ...].  Under key
    exchangeability all 3! labellings of a seed are equally likely; c0 depends only on which run carries the s0
    label, so the 6^n labellings give 3^n equally likely values of sum(c0), each counted 2^n times.  Enumerated
    exactly by meet in the middle (two halves of partial sums, one sorted, bisect).  Returns (p, count, 3^n)."""
    choices = [_c0_choices(r) for r in rows]
    obs = abs(sum(ch[0] for ch in choices))
    tot = 3 ** len(rows)
    h = len(choices) // 2
    left, right = _half_sums(choices[:h]), sorted(_half_sums(choices[h:]))
    if obs <= TOL:
        return 1.0, tot, tot
    n_r, hit = len(right), 0
    for a in left:
        hit += n_r - bisect.bisect_left(right, obs - TOL - a)  # a + b >= obs
        hit += bisect.bisect_right(right, -obs + TOL - a)      # a + b <= -obs
    return hit / tot, hit, tot


def perm_c0_ci(rows, alpha=ALPHA, step=0.001):
    """95% interval for c0's shift mu by inverting perm_c0_p on (y_s0 + mu, y_s1, y_s2), which removes a shift mu from c0: walking out from the mean
    of c0 in steps of 0.001, the outermost mu on each side that is not rejected.  Returns (-inf, inf) when even the
    most extreme labelling has p > alpha (1 / 3^n > alpha, n <= 2), so it always terminates (design adversary F1)."""
    if not rows or 1 / 3 ** len(rows) > alpha:
        return float("-inf"), float("inf")
    m0 = round(sum(_c0_choices(r)[0] for r in rows) / len(rows) / step) * step
    ends = []
    for d in (-1, 1):
        mu = m0
        while perm_c0_p([(r[0] + mu + d * step, r[1], r[2]) for r in rows])[0] > alpha:
            mu += d * step
        ends.append(mu)
    return ends[0], ends[1]


def holm(ps, alpha=ALPHA):
    """Holm's step-down over a dict of p values: {name: (adjusted p, rejected)}."""
    order = sorted(ps, key=lambda k: ps[k])
    out, running, going = {}, 0.0, True
    for i, k in enumerate(order):
        running = max(running, min(1.0, (len(ps) - i) * ps[k]))
        going = going and ps[k] <= alpha / (len(ps) - i)
        out[k] = (running, going)
    return out


def reading(rej_c0, rej_c12):
    if rej_c12:
        return "keys"
    return "salt0" if rej_c0 else "chance"


def trimmed_mean(xs, prop=0.2):
    x = sorted(xs)
    k = int(prop * len(x))
    return st.mean(x[k:len(x) - k])


def describe(name, xs, test):
    """test is ("perm", rows) for c0 or ("signflip", None) for a difference."""
    kind, rows = test
    p, hit, tot = perm_c0_p(rows) if kind == "perm" else sign_flip_p(xs)
    return dict(name=name, xs=xs, n=len(xs), mean=st.mean(xs), median=st.median(xs), trimmed=trimmed_mean(xs),
                pos=sum(x > 0 for x in xs), neg=sum(x < 0 for x in xs), p=p, hit=hit, tot=tot, kind=kind)


# --- the data --------------------------------------------------------------------------------------

def gen0(run):
    lines = open(os.path.join(run, "generations.txt")).read().splitlines()
    head, row = lines[0].split("\t"), lines[1].split("\t")
    assert row[0] == "0", run
    return float(row[head.index("champ_holistic_mean")])


def write_summaries(root, seeds):
    for s in seeds:
        for a in ARMS:
            d = os.path.join(root, f"{a}-{s}")
            if os.path.exists(os.path.join(d, "analysis.json")):
                r85.write_summary(d)
                r96.write_extras(d)
                print(f"wrote summaries in {d}")


def load(root, seeds, from_summaries):
    rows, missing = {}, []
    for s in seeds:
        for a in ARMS:
            d = os.path.join(root, f"{a}-{s}")
            if os.path.exists(os.path.join(d, "generations.txt" if from_summaries else "history.json")):
                rows[(a, s)] = r85.summary(d, from_summaries)
            else:
                missing.append(f"{a}-{s}")
    return rows, missing


def pairing(root, seed, rows, from_summaries):
    ds = [r96.read_digests(os.path.join(root, f"{a}-{seed}"), from_summaries) for a in ARMS]
    envs = [rows[(a, seed)]["environment"] for a in ARMS]
    n = min(len(e) for e in envs)
    env_same = all(e[:n] == envs[0][:n] for e in envs)
    if any(d is None or d["conventional"][0] is None for d in ds):
        return dict(ok=None, conv=None, env_same=env_same, gens=n)
    conv_same = all(d["conventional"] == ds[0]["conventional"] for d in ds)
    hol = [d["holistic"][0] for d in ds]
    hol_distinct = len(set(hol)) == 3
    return dict(ok=conv_same and hol_distinct and env_same, conv=ds[0]["conventional"], conv_same=conv_same,
                hol_distinct=hol_distinct, env_same=env_same, gens=n)


def block(title, contrasts):
    """contrasts: {name: (xs, test)}.  Prints the table; returns (stats, holm)."""
    ds = {k: describe(k, xs, test) for k, (xs, test) in contrasts.items()}
    adj = holm({k: d["p"] for k, d in ds.items()})
    print(title)
    print("contrast  n    mean      median    20%-trim  positive  exact p (count / labellings)                 Holm p   rejected at 0.05")
    for k, d in ds.items():
        test = "permutation" if d["kind"] == "perm" else "sign-flip"
        cell = f"{test} {d['p']:.6f} ({d['hit']}/{d['tot']})"
        print(f"{k:8}  {d['n']:<3}  {d['mean']:+.4f}   {d['median']:+.4f}   {d['trimmed']:+.4f}   {d['pos']:>2}/{d['n']:<2}     {cell:44} {adj[k][0]:.4f}   {adj[k][1]}")
    return ds, adj


def main(root, seeds, write=False, from_summaries=False):
    if write:
        write_summaries(root, seeds)
        from_summaries = True
    rows, missing = load(root, seeds, from_summaries)
    print(f"RBT-111 readout: {root}, seeds {seeds[0]}-{seeds[-1]}, {'summaries' if from_summaries else 'bulk'}")
    print("\nrun        reached complete  final-fifth  gen-0 champ  salt")
    for s in seeds:
        for a in ARMS:
            if (a, s) in rows:
                r = rows[(a, s)]
                cfg = json.load(open(os.path.join(root, f"{a}-{s}", "config.json")))
                g0 = gen0(os.path.join(root, f"{a}-{s}")) if from_summaries else float("nan")
                print(f"{a}-{s:<5} {r['reached']:7d} {str(r['complete']):8} {r['final_fifth']:11.4f}  {g0:11.4f}  {cfg.get('holistic_stream_salt', 0)}")
    full = [s for s in seeds if all((a, s) in rows for a in ARMS)]
    complete = not missing and all(rows[(a, s)]["complete"] for a in ARMS for s in full)
    if missing:
        print(f"missing arms: {', '.join(missing)}")
    if not complete:
        print("NOT A RESULT: at least one arm is missing or incomplete; a partial read of a running arm is not a result.")

    print("\n1. pairing check per seed: conventional hash identical across s0/s1/s2, holistic hashes pairwise different, terrain+start identical")
    print("seed   conventional sha256 (n)   conv identical   holistic distinct   terrain+start identical (gens)   PASS")
    for s in full:
        p = pairing(root, s, rows, from_summaries)
        if p["ok"] is None:
            print(f"{s}   (no lineage digest available)                                          {p['env_same']} ({p['gens']})   n/a")
        else:
            print(f"{s}   {p['conv'][0][:12]} ({p['conv'][1]})     {str(p['conv_same']):15}  {str(p['hol_distinct']):18}  {str(p['env_same']):5} ({p['gens']})                      {p['ok']}")
    if not full:
        return None

    trip = [(rows[("s0", s)]["final_fifth"], rows[("s1", s)]["final_fifth"], rows[("s2", s)]["final_fifth"]) for s in full]
    c0 = [(b + c) / 2 - a for a, b, c in trip]
    c12 = [c - b for a, b, c in trip]
    d10 = [b - a for a, b, c in trip]
    d20 = [c - a for a, b, c in trip]
    print("\nper seed (final fifth):  seed   s0       s1       s2       c0        c12")
    for s, (a, b, c), x, z in zip(full, trip, c0, c12):
        print(f"                         {s}   {a:.4f}   {b:.4f}   {c:.4f}   {x:+.4f}   {z:+.4f}")

    ds, adj = block("\n2. PRIMARY: c0 by the exact within-seed permutation test (3^n labellings), c12 by the exact sign-flip test"
                    " (2^n), Holm over the two",
                    {"c0": (c0, ("perm", trip)), "c12": (c12, ("signflip", None))})
    key = reading(adj["c0"][1], adj["c12"][1])
    tag = "" if complete else f" (NOT A RESULT, n = {len(full)} of {len(seeds)})"
    print(f"\n3. READING{tag}: {READING[key]}")
    if key == "salt0":
        if ds["c0"]["mean"] < 0:
            print("   note: c0 < 0, the opposite sign to RBT-108's s1 - s0 (salt 0 ahead, not behind).")
        print(f"   {SALT0_BESIDE}")
        for name, xs in (("s1 - s0", d10), ("s2 - s0", d20)):
            print(f"     {name}: mean {st.mean(xs):+.4f}, {sum(x > 0 for x in xs)}/{len(xs)} positive")

    lo, hi = perm_c0_ci(trip)
    print(f"\n4. descriptive: c0's 95% interval by inverting the permutation test [{lo:+.4f}, {hi:+.4f}]")
    for dl, name in ((DELTA_OBSERVED, "RBT-108's observed offset"), (DELTA_SMALL, "the winner's-curse allowance")):
        print(f"   delta = {dl}: {name} is {'inside' if lo <= dl <= hi else 'outside'} the interval")
    if key == "chance" and lo <= DELTA_OBSERVED <= hi:
        print("   qualifier to the reading (PREREGISTRATION.md): the interval still contains delta = 0.082, so 'chance' is stated"
              " with RBT-108's offset NOT excluded by these seeds.")

    g, g0_rejected = {}, None
    if from_summaries:
        g = {(a, s): gen0(os.path.join(root, f"{a}-{s}")) for a in ARMS for s in full}
        gtrip = [(g[("s0", s)], g[("s1", s)], g[("s2", s)]) for s in full]
        _, gadj = block("\n5. SECONDARY (stated before any arm): the same contrasts and tests on generation 0's champion row (the founders)",
                        {"c0 gen0": ([(b + c) / 2 - a for a, b, c in gtrip], ("perm", gtrip)),
                         "c12 gen0": ([c - b for a, b, c in gtrip], ("signflip", None))})
        g0_rejected = any(r for _, r in gadj.values())
        if g0_rejected:
            print(f"   {GEN0_CONSEQUENCE}")
            if key == "chance":
                print(f"   {GEN0_CHANCE_QUALIFIER}")
    else:
        print("\n5. SECONDARY: needs generations.txt (run with --from-summaries or --write-summaries)")

    print("\n6. descriptive only (no reading, not in Holm):")
    for name, xs in (("s1 - s0", d10), ("s2 - s0", d20)):
        d = describe(name, xs, ("signflip", None))
        print(f"   {name}: mean {d['mean']:+.4f}, {d['pos']}/{d['n']} positive, exact sign-flip p {d['p']:.4f}")
    print(f"   RMS of c12 (an A/A d under every reading but 'keys'): {math.sqrt(sum(x * x for x in c12) / len(c12)):.4f}"
          f"  (RBT-108 pooled RMS d 0.1146; not a registered update of h)")
    return dict(c0=c0, c12=c12, stats=ds, holm=adj, reading=key, complete=complete, ci=(lo, hi), gen0=g,
                gen0_rejected=g0_rejected)


if __name__ == "__main__":
    args = sys.argv[1:]
    root = args[args.index("--root") + 1] if "--root" in args else os.path.join("runs", "RBT-111")
    seeds = tuple(int(x) for x in args[args.index("--seeds") + 1].split(",")) if "--seeds" in args else SEEDS
    if "--summaries-only" in args:
        write_summaries(root, seeds)
        sys.exit(0)
    main(root, seeds, write="--write-summaries" in args, from_summaries="--from-summaries" in args)
