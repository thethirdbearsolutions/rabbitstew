"""The pre-registered readout for RBT-111: are the arena's stream keys exchangeable?

Twelve fresh seeds (217-228), each at holistic stream salts 0, 1 and 2 (arms s0, s1, s2), on RBT-96's
instrument exactly as RBT-108 ran it.  Per run, y = the mean champ_holistic_mean over the checkpoints at
generation >= 200 (RBT-85's summary(), as RBT-96 and RBT-108 read it).  Per seed:

    c0  = (y_s1 + y_s2) / 2 - y_s0     salt 0 against the non-zero salts
    c12 = y_s2 - y_s1                  two non-zero salts

1. Completion and the pairing check per seed: the three arms' conventional lineage hashes identical, their
   holistic lineage hashes pairwise different, terrain and start seeds identical at every generation.
   A seed that fails is reported, not dropped; any incomplete arm makes the readout NOT A RESULT.
2. Primary: per contrast, mean, median, 20%-trimmed mean, count positive, and the exact two-sided sign-flip
   p (all 2^12 sign assignments); Holm over the two at alpha = 0.05.
3. The reading, fixed in PREREGISTRATION.md before any arm (READING below).
4. Descriptive: c0's 95% interval by inverting the sign-flip test, and what it says at delta = 0.082 and 0.05.
5. Secondary (stated before any arm): the same two contrasts on generation 0's champion row, same test, Holm.
6. Descriptive only, no reading: s1 - s0 (RBT-108's contrast out of sample), s2 - s0, and the RMS of c12.

    python runs/RBT-111/readout.py [--seeds 217,...,228] [--root runs/RBT-111] [--write-summaries | --from-summaries]

--write-summaries writes generations.txt, opponent.txt and conventional-digest.txt (RBT-96's summaries) in
every arm directory that holds analysis.json, then reads as usual.  No simulation.
"""
import importlib.util
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rbt96_readout", os.path.join(HERE, "..", "RBT-96", "readout.py"))
r96 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r96)
r85 = r96.r85

SEEDS = tuple(range(217, 229))
ARMS = ("s0", "s1", "s2")
ALPHA = 0.05
DELTA_OBSERVED, DELTA_SMALL = 0.082, 0.05  # RBT-108's post hoc mean d over 205-216, and a winner's-curse allowance

READING = {
    "keys": "KEYS NOT EXCHANGEABLE: c12 != 0, so two non-zero salts differ. Re-examine every key contrast in the programme"
            " (every A/A, RBT-105's replicate histories, possibly seeds).",
    "salt0": "SALT 0's OFFSET: c0 != 0 and c12 ~ 0. Search outside the salt code path; every salt-0 run carries that stream family's bias.",
    "chance": "CHANCE at an offset the size of RBT-108's (delta ~ 0.082): RBT-108's offset was a post hoc false alarm and the"
              " registered RMS null (h 0.159) stands.  A null at delta = 0.05 is NOT DECIDED (the design's power there is under one half).",
}


# --- the test --------------------------------------------------------------------------------------

def sign_flip_p(xs):
    """Exact two-sided sign-flip test on the mean: the share of the 2^n sign assignments whose |sum| reaches
    the observed |sum|.  Returns (p, count, 2^n).  Pure Python, so the readout needs no package."""
    n, obs = len(xs), abs(sum(xs))
    sums = [0.0]
    for x in xs:  # all 2^n signed partial sums, built one element at a time
        sums = [s + x for s in sums] + [s - x for s in sums]
    hit = sum(abs(s) >= obs - 1e-12 for s in sums)
    return hit / 2 ** n, hit, 2 ** n


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


def sign_flip_ci(xs, alpha=ALPHA, step=0.001):
    """95% interval for the centre of xs by inverting the sign-flip test: walking out from the mean in steps
    of 0.001, the outermost mu on each side with p(xs - mu) > alpha."""
    m0 = round(st.mean(xs) / step) * step
    ends = []
    for direction in (-1, 1):
        mu = m0
        while sign_flip_p([x - mu - direction * step for x in xs])[0] > alpha:
            mu += direction * step
        ends.append(mu)
    return ends[0], ends[1]


def describe(name, xs):
    p, hit, tot = sign_flip_p(xs)
    pos, neg = sum(x > 0 for x in xs), sum(x < 0 for x in xs)
    return dict(name=name, xs=xs, n=len(xs), mean=st.mean(xs), median=st.median(xs), trimmed=trimmed_mean(xs),
                pos=pos, neg=neg, p=p, hit=hit, tot=tot)


# --- the data --------------------------------------------------------------------------------------

def gen0(run):
    lines = open(os.path.join(run, "generations.txt")).read().splitlines()
    head, row = lines[0].split("\t"), lines[1].split("\t")
    assert row[0] == "0", run
    return float(row[head.index("champ_holistic_mean")])


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


def main(root, seeds, write=False, from_summaries=False):
    if write:
        for s in seeds:
            for a in ARMS:
                d = os.path.join(root, f"{a}-{s}")
                if os.path.exists(os.path.join(d, "analysis.json")):
                    r85.write_summary(d)
                    r96.write_extras(d)
                    print(f"wrote summaries in {d}")
        from_summaries = True
    rows, missing = load(root, seeds, from_summaries)
    print(f"RBT-111 readout: {root}, seeds {seeds[0]}-{seeds[-1]}, {'summaries' if from_summaries else 'bulk'}")
    print("\nrun        reached complete  final-fifth  gen-0 champ  salt")
    import json
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

    y = {(a, s): rows[(a, s)]["final_fifth"] for a in ARMS for s in full}
    c0 = [(y[("s1", s)] + y[("s2", s)]) / 2 - y[("s0", s)] for s in full]
    c12 = [y[("s2", s)] - y[("s1", s)] for s in full]
    print("\nper seed (final fifth):  seed   s0       s1       s2       c0        c12")
    for s, a, b in zip(full, c0, c12):
        print(f"                         {s}   {y[('s0', s)]:.4f}   {y[('s1', s)]:.4f}   {y[('s2', s)]:.4f}   {a:+.4f}   {b:+.4f}")

    def block(title, contrasts):
        ds = {k: describe(k, v) for k, v in contrasts.items()}
        adj = holm({k: d["p"] for k, d in ds.items()})
        print(title)
        print("contrast  n    mean      median    20%-trim  positive  exact sign-flip p (count)   Holm p   rejected at 0.05")
        for k, d in ds.items():
            print(f"{k:8}  {d['n']:<3}  {d['mean']:+.4f}   {d['median']:+.4f}   {d['trimmed']:+.4f}   {d['pos']:>2}/{d['n']:<2}     {d['p']:.4f} ({d['hit']}/{d['tot']}){' ' * (10 - len(str(d['hit'])) - len(str(d['tot'])))}  {adj[k][0]:.4f}   {adj[k][1]}")
        return ds, adj

    ds, adj = block("\n2. PRIMARY: exact two-sided sign-flip test on each contrast, Holm over the two", {"c0": c0, "c12": c12})
    key = reading(adj["c0"][1], adj["c12"][1])
    print(f"\n3. READING: {READING[key]}")
    if key == "salt0" and ds["c0"]["mean"] < 0:
        print("   note: c0 < 0, the opposite sign to RBT-108's s1 - s0 (salt 0 ahead, not behind).")
    if not complete:
        print("   (NOT A RESULT: see above)")

    lo, hi = sign_flip_ci(c0)
    print(f"\n4. descriptive: c0's 95% interval by inverting the sign-flip test [{lo:+.4f}, {hi:+.4f}]")
    for dl, name in ((DELTA_OBSERVED, "RBT-108's observed offset"), (DELTA_SMALL, "the winner's-curse allowance")):
        print(f"   delta = {dl}: {name} is {'inside' if lo <= dl <= hi else 'outside'} the interval")
    if key == "chance" and lo <= DELTA_OBSERVED <= hi:
        print("   qualifier to the reading (PREREGISTRATION.md): the interval still contains delta = 0.082, so 'chance' is stated"
              " with RBT-108's offset NOT excluded by these seeds.")

    g = {}
    if from_summaries:
        g = {(a, s): gen0(os.path.join(root, f"{a}-{s}")) for a in ARMS for s in full}
        block("\n5. SECONDARY (stated before any arm): the same contrasts on generation 0's champion row (the founders)",
              {"c0 gen0": [(g[("s1", s)] + g[("s2", s)]) / 2 - g[("s0", s)] for s in full],
               "c12 gen0": [g[("s2", s)] - g[("s1", s)] for s in full]})
    else:
        print("\n5. SECONDARY: needs generations.txt (run with --from-summaries or --write-summaries)")

    print("\n6. descriptive only (no reading, not in Holm):")
    for name, xs in (("s1 - s0", [y[("s1", s)] - y[("s0", s)] for s in full]), ("s2 - s0", [y[("s2", s)] - y[("s0", s)] for s in full])):
        d = describe(name, xs)
        print(f"   {name}: mean {d['mean']:+.4f}, {d['pos']}/{d['n']} positive, exact sign-flip p {d['p']:.4f}")
    print(f"   RMS of c12 (an A/A d under every reading but 'keys'): {math.sqrt(sum(x * x for x in c12) / len(c12)):.4f}"
          f"  (RBT-108 pooled RMS d 0.1146; not a registered update of h)")
    return dict(c0=c0, c12=c12, stats=ds, holm=adj, reading=key, complete=complete, ci=(lo, hi), gen0=g)


if __name__ == "__main__":
    args = sys.argv[1:]
    root = args[args.index("--root") + 1] if "--root" in args else os.path.join("runs", "RBT-111")
    seeds = tuple(int(x) for x in args[args.index("--seeds") + 1].split(",")) if "--seeds" in args else SEEDS
    main(root, seeds, write="--write-summaries" in args, from_summaries="--from-summaries" in args)
