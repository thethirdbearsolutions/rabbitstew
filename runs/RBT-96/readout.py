"""The pre-registered readout for RBT-96: the arena's A/A pair.  Per seed, two runs of RBT-85's
unprotected configuration that differ only in --holistic-stream-salt (0 and 1): the same wheeled
population on the same terrains, an independently drawn holistic population, no manipulation.
The paired difference s1 - s0 is pure null: its spread is what every arena +-0.10 rule is read against.

1. Pairing check: within each seed the two arms' conventional lineage lines are byte-identical and
   so are the terrain and start seeds of every generation; the holistic lineages differ (else the
   salt did nothing).  A pair that fails is reported, not dropped.
2. The A/A paired columns, RBT-85's readout.py columns with s1 - s0 in place of prot - base:
   final-fifth holistic mean champion fitness per arm, d, wins d, best-checkpoint d, and the
   wheeled side's final-fifth solo approach (both arms) as the covariate, with the holistic solo
   approach and terrain d.
3. The null spread: SD of the four d (3 df), the RMS of d (4 df; the true mean is 0 by
   construction), SE, 2 SE, the t(3) 95% half-width, and the three resolution figures of RBT-85's
   readout (independent checkpoints, checkpoint-paired, observed spread).
4. Against RBT-85 (its committed generations.txt): its A/B differences and their SD beside the
   A/A ones, the variance ratio, RBT-85's mean read against the A/A null (t with 4 df on the RMS),
   and the smallest 4-seed mean the +-0.10 rule could separate from the A/A null at 95%.
5. Cross-machine reproduction: arm s0 is RBT-85's base configuration byte for byte (salt 0 is the
   unsalted stream), so s0-SEED's generations.txt is compared row by row with RBT-85's base-SEED
   (laptop M4 against a cloud x86 core).

    python runs/RBT-96/readout.py [runs/RBT-96] [--seeds 201,202,203,204] [--write-summaries | --from-summaries]

--write-summaries writes each run's generations.txt (RBT-85's columns), opponent.txt (the covariate
row from analysis.json) and conventional-digest.txt (the lineage hash and holistic hash) so that every
item re-derives with --from-summaries from a checkout that never held the bulk.  No simulation.
"""
import importlib.util
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rbt85_readout", os.path.join(HERE, "..", "RBT-85", "readout.py"))
r85 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r85)

ARMS = ("s0", "s1")
T3, T4 = 3.182446, 2.776445  # two-sided 95% t quantiles, 3 and 4 df
RBT85 = os.path.join(HERE, "..", "RBT-85")


def t_sf2(t, df):
    """Two-sided p for Student's t (df small integer), by numerical integration of the density."""
    t = abs(t)
    c = math.gamma((df + 1) / 2) / (math.sqrt(df * math.pi) * math.gamma(df / 2))
    n, hi = 20000, t
    h = hi / n
    s = sum((1 if i in (0, n) else (4 if i % 2 else 2)) * c * (1 + (i * h) ** 2 / df) ** (-(df + 1) / 2) for i in range(n + 1)) * h / 3
    return max(0.0, 1 - 2 * s)


def holistic_digest(run):
    import hashlib
    p = os.path.join(run, "lineage.jsonl")
    if not os.path.exists(p):
        return None, 0
    seen, h = set(), hashlib.sha256()
    for l in open(p, "rb"):
        if b'"population": "holistic"' in l and l not in seen:
            seen.add(l)
            h.update(l)
    return h.hexdigest(), len(seen)


def write_extras(run):
    (hc, nc), (hh, nh) = r85.conventional_digest(run), holistic_digest(run)
    with open(os.path.join(run, "conventional-digest.txt"), "w") as f:
        f.write(f"conventional\t{hc}\t{nc}\nholistic\t{hh}\t{nh}\n")
    o = r85.opponent(run)
    if o:
        with open(os.path.join(run, "opponent.txt"), "w") as f:
            f.write("\t".join(o) + "\n" + "\t".join(f"{o[k]:.6f}" if isinstance(o[k], float) else str(o[k]) for k in o) + "\n")


def read_digests(run, from_summaries):
    if not from_summaries:
        return {"conventional": r85.conventional_digest(run), "holistic": holistic_digest(run)}
    p = os.path.join(run, "conventional-digest.txt")
    if not os.path.exists(p):
        return None
    out = {}
    for l in open(p).read().splitlines():
        k, h, n = l.split("\t")
        out[k] = (h, int(n))
    return out


def read_opponent(run, from_summaries):
    if not from_summaries:
        return r85.opponent(run)
    p = os.path.join(run, "opponent.txt")
    if not os.path.exists(p):
        return None
    k, v = open(p).read().splitlines()[:2]
    return {a: (int(b) if a == "n" else float(b)) for a, b in zip(k.split("\t"), v.split("\t"))}


def rbt85_differences(seeds):
    out = {}
    for s in seeds:
        b, p = os.path.join(RBT85, f"base-{s}"), os.path.join(RBT85, f"prot-{s}")
        if os.path.exists(os.path.join(b, "generations.txt")) and os.path.exists(os.path.join(p, "generations.txt")):
            out[s] = r85.summary(p, True)["final_fifth"] - r85.summary(b, True)["final_fifth"]
    return out


def main(root, seeds, write=False, from_summaries=False):
    rows = {}
    for seed in seeds:
        for arm in ARMS:
            d = os.path.join(root, f"{arm}-{seed}")
            if os.path.exists(os.path.join(d, "generations.txt" if from_summaries else "history.json")):
                if write and not from_summaries:
                    r85.write_summary(d)
                    write_extras(d)
                rows[(arm, seed)] = r85.summary(d, from_summaries)
    print("run        reached complete  final-fifth  sd(ckpt)  wins/bouts   best (gen)   fifths                          salt  budget settle")
    for (arm, seed), r in sorted(rows.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        cfg = json.load(open(os.path.join(root, f"{arm}-{seed}", "config.json")))
        b = f"{r['best'][1]:.2f} ({r['best'][0]})" if r["best"] else "-"
        print(f"{arm}-{seed:<5} {r['reached']:7d} {str(r['complete']):8} {r['final_fifth']:11.3f} {r['final_fifth_sd']:9.3f}  {r['wins']:4d}/{r['bouts']:<5d}  {b:>11}   {', '.join(f'{x:.2f}' for x in r['fifths']):30}  {cfg.get('holistic_stream_salt', 0)}     {r['mass_budget']}  {r['settle']}  k={r['k']}")

    print("\n1. pairing check: same wheeled population on the same terrains, different holistic population?")
    print("seed   conventional sha256 (n) s0 | s1                           identical   holistic differs   terrain+start identical (generations)")
    paired_ok = {}
    for seed in seeds:
        a, b = rows.get(("s0", seed)), rows.get(("s1", seed))
        if not a or not b:
            continue
        n = min(len(a["environment"]), len(b["environment"]))
        env_same = a["environment"][:n] == b["environment"][:n]
        da, db = read_digests(os.path.join(root, f"s0-{seed}"), from_summaries), read_digests(os.path.join(root, f"s1-{seed}"), from_summaries)
        if not da or not db or da["conventional"][0] is None:
            print(f"{seed}   (no lineage digest available)                                         n/a         n/a                {env_same} ({n})")
            paired_ok[seed] = None
            continue
        same = da["conventional"] == db["conventional"]
        hdiff = da["holistic"][0] != db["holistic"][0]
        paired_ok[seed] = same and env_same and hdiff
        print(f"{seed}   {da['conventional'][0][:12]} ({da['conventional'][1]}) | {db['conventional'][0][:12]} ({db['conventional'][1]})   {str(same):9}   {str(hdiff):16}   {env_same} ({n})")

    used, diffs = [], []
    print("\n2. A/A paired columns, s1 minus s0, with the opponent (wheeled final-fifth solo approach, m; steering of 3) beside it:")
    print("seed   s0      s1      d        wins d   best d   complete  paired   opp approach s0/s1       opp steering s0/s1   holistic solo approach d   terrain d")
    covs = []
    for seed in seeds:
        a, b = rows.get(("s0", seed)), rows.get(("s1", seed))
        if not a or not b:
            continue
        d = b["final_fifth"] - a["final_fifth"]
        used.append(seed)
        diffs.append(d)
        oa, ob = read_opponent(os.path.join(root, f"s0-{seed}"), from_summaries), read_opponent(os.path.join(root, f"s1-{seed}"), from_summaries)
        covs.append(oa["approach"] if oa else None)
        opp = f"{oa['approach']:+7.2f} / {ob['approach']:+7.2f}        {oa['steering']:.2f} / {ob['steering']:.2f}" if oa and ob else "      (opponent not available)      "
        solo = f"{ob['holistic_approach'] - oa['holistic_approach']:+.2f}                      {ob['holistic_terrain'] - oa['holistic_terrain']:+.2f}" if oa and ob else ""
        print(f"{seed}   {a['final_fifth']:.3f}   {b['final_fifth']:.3f}   {d:+.3f}   {b['wins'] - a['wins']:+6d}   {b['best'][1] - a['best'][1]:+6.2f}   {str(a['complete'] and b['complete']):8}  {str(paired_ok.get(seed)):6}   {opp}          {solo}")
    if not diffs:
        return
    complete = all(rows[(a, s)]["complete"] for a in ARMS for s in used)
    n = len(diffs)
    mean = st.mean(diffs)
    sd = st.stdev(diffs) if n > 1 else float("nan")
    rms = math.sqrt(sum(d * d for d in diffs) / n)
    se = sd / math.sqrt(n)
    print(f"\n3. the null spread.  n = {n}  d: {', '.join(f'{d:+.3f}' for d in diffs)}  mean {mean:+.4f}  range [{min(diffs):+.3f}, {max(diffs):+.3f}]  |d| < 0.10: {sum(abs(d) < 0.10 for d in diffs)}/{n}  |d| < 0.05: {sum(abs(d) < 0.05 for d in diffs)}/{n}")
    print(f"A/A SD of d {sd:.4f} (3 df)   RMS of d {rms:.4f} (4 df, mean 0 by construction)   SE of the mean {se:.4f}   2 SE {2 * se:.4f}   t(3) 95% half-width {T3 * se:.4f}")
    if all(c is not None for c in covs) and n > 2:
        print(f"corr(d, wheeled final-fifth solo approach) across seeds {r85.corr(diffs, covs):+.2f};  corr(|d|, approach) {r85.corr([abs(x) for x in diffs], covs):+.2f}")
    if not complete:
        print("NOT A RESULT: at least one run is incomplete; a partial read of a running arm is not a result.")
    sds = [rows[("s0", s)]["final_fifth_sd"] for s in used]
    ns = [rows[("s0", s)]["final_fifth_n"] for s in used]
    per_run = st.mean(sds) / math.sqrt(st.mean(ns))
    print(f"resolution, RBT-85's three figures at n={n}:  independent checkpoints {2 * per_run * math.sqrt(2) / math.sqrt(n):.3f}", end="")
    cks = []
    for s in used:
        la, lb = rows[("s0", s)]["final_fifth_list"], rows[("s1", s)]["final_fifth_list"]
        if len(la) == len(lb) and len(la) > 1:
            cks.append(st.pstdev([y - x for x, y in zip(la, lb)]) / math.sqrt(len(la)))
    if cks:
        print(f"   checkpoint-paired {2 * st.mean(cks) / math.sqrt(n):.3f}", end="")
    print(f"   observed spread {2 * se:.3f} (2 SE)   (RBT-85: 0.062, 0.022, 0.046)")
    sd_run = rms / math.sqrt(2)
    print(f"implied SD of one run's final-fifth mean about its seed's expectation (RMS / sqrt 2): {sd_run:.4f};  checkpoint noise alone predicts {per_run:.4f}")

    ab = rbt85_differences(used)
    if ab:
        abd = [ab[s] for s in used if s in ab]
        m85, sd85 = st.mean(abd), st.stdev(abd)
        print(f"\n4. against RBT-85 (committed generations.txt): A/B d {', '.join(f'{x:+.3f}' for x in abd)}  mean {m85:+.4f}  SD {sd85:.4f}  RMS {math.sqrt(sum(x * x for x in abd) / len(abd)):.4f}")
        print(f"SD ratio A/B over A/A {sd85 / sd:.2f}  (variance ratio {sd85 ** 2 / sd ** 2:.2f}, F(3,3); 95% two-sided band for no difference [0.065, 15.44])")
        se0 = rms / math.sqrt(n)
        t = m85 / se0
        print(f"RBT-85's mean {m85:+.4f} against the A/A null: SE of a 4-seed mean under the null {se0:.4f} (RMS, 4 df); t(4) = {t:+.2f}, two-sided p = {t_sf2(t, 4):.3f};  outside the null's 95% band +-{T4 * se0:.4f}: {abs(m85) > T4 * se0}")
        print(f"the +-0.10 rule against the A/A null: a 4-seed mean must clear {T4 * se0:.4f} to be outside the null at 95%; 0.10 is {0.10 / se0:.2f} null SEs (the rule {'can' if 0.10 > T4 * se0 else 'cannot'} be met by noise alone at 95%: P(|mean| >= 0.10 | null) = {t_sf2(0.10 / se0, 4):.3f})")

    print("\n5. cross-machine reproduction: s0-SEED against RBT-85 base-SEED (same configuration byte for byte; laptop M4 then, cloud x86 now)")
    for s in used:
        p85 = os.path.join(RBT85, f"base-{s}", "generations.txt")
        p96 = os.path.join(root, f"s0-{s}", "generations.txt")
        if not (os.path.exists(p85) and os.path.exists(p96)):
            print(f"{s}   (generations.txt missing)")
            continue
        a, b = open(p85).read().splitlines(), open(p96).read().splitlines()
        same = sum(x == y for x, y in zip(a, b))
        first = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)
        print(f"{s}   identical rows {same}/{max(len(a), len(b))}   first differing row: {'none' if first is None else f'generation {first - 1}'}   final-fifth RBT-85 {r85.summary(os.path.dirname(p85), True)['final_fifth']:.4f}  RBT-96 {rows[('s0', s)]['final_fifth']:.4f}")
    if write and not from_summaries:
        print(f"\nwrote generations.txt, opponent.txt and conventional-digest.txt in {len(rows)} run directories")


if __name__ == "__main__":
    args = sys.argv[1:]
    root = next((a for a in args if not a.startswith("--") and not a.replace(",", "").isdigit()), "runs/RBT-96")
    seeds = tuple(int(x) for x in args[args.index("--seeds") + 1].split(",")) if "--seeds" in args else (201, 202, 203, 204)
    main(root, seeds, write="--write-summaries" in args, from_summaries="--from-summaries" in args)
