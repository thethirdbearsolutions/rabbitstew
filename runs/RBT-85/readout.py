"""The pre-registered readout for RBT-85: RBT-74's eight runs again under per-population RNG
streams, protected minus unprotected, paired by seed, with the opponent beside every difference.

1. Pairing check (the point of the ticket): within each seed the two arms' conventional
   lineage lines are byte-identical and so are the terrain and start seeds of every generation.
   A pair that fails this is not a pair and is reported as such, not silently dropped.
2. Primary outcome and verdict rule, RBT-74's unchanged: holistic mean champion fitness over the
   final fifth (checkpoints at generations >= 0.8 * generations), protected minus unprotected,
   per seed, with the zero count (|d| < 0.01), mean, range and
     helps  iff mean >= +0.10 and >= 3 of 4 seeds positive;
     hurts  iff mean <= -0.10 and >= 3 of 4 seeds negative;
     else null.
3. The opponent covariate, reported whether or not it helps: the wheeled side's final-fifth solo
   approach (mean over the analysed conventional bests of generations >= 200, analysis.json),
   for both arms of every pair, beside the paired difference.
4. What the pairing bought: paired SE against unpaired SE and the base/prot correlation across
   seeds (RBT-74: 0.073 against 0.063, r = -0.41), and the smallest paired mean difference four
   seeds resolve at 2 SE, from checkpoint noise alone and from the observed spread.
5. Per-generation summaries: with --write-summaries, each run's generations.txt (one row per
   generation: terrain seed, start seed, both populations' best and mean bout score, best
   distance, best parts and mass, and the checkpoint's holistic mean champion fitness and wins),
   which is the tracked stand-in for history.json.

    python runs/RBT-85/readout.py [runs/RBT-85] [--seeds 201,202,203,204] [--write-summaries]

Reads history.json, lineage.jsonl, config.json and (when present) analysis.json.  No simulation.
With --from-summaries it reads generations.txt instead of history.json, so items 2 and 4 can be
re-derived from a checkout that never held the bulk (items 1 and 3 need the bulk and print as
unavailable).
"""
import hashlib
import json
import math
import os
import statistics as st
import sys

ARMS = ("base", "prot")
COLUMNS = ["generation", "terrain_seed", "start_seed", "h_best", "h_mean", "h_best_distance", "h_best_parts", "h_best_mass", "c_best", "c_mean", "c_best_distance", "c_best_parts", "c_best_mass", "champ_holistic_mean", "champ_holistic_wins", "champ_conventional_wins", "champ_bouts"]


def generation_rows(run):
    h = json.load(open(os.path.join(run, "history.json")))
    champs = {c["generation"]: c for c in h["champions"]}
    by_gen = {}
    for e in h["history"]:
        by_gen.setdefault(e["generation"], {})[e["population"]] = e
    rows = []
    for g in sorted(by_gen):
        ho, co, c = by_gen[g].get("holistic"), by_gen[g].get("conventional"), champs.get(g)
        if not ho or not co:
            continue
        rows.append([g, ho["terrain_seed"], (ho["start_seeds"] or [None])[0],
                     ho["best_fitness"], ho["mean_fitness"], ho["best_distance"], ho["best_parts"], ho["best_mass"],
                     co["best_fitness"], co["mean_fitness"], co["best_distance"], co["best_parts"], co["best_mass"],
                     c["holistic_mean_fitness"] if c else None, c["holistic_wins"] if c else None, c["conventional_wins"] if c else None, c["n_bouts"] if c else None])
    return rows


def write_summary(run):
    rows = generation_rows(run)
    with open(os.path.join(run, "generations.txt"), "w") as f:
        f.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            f.write("\t".join("" if v is None else (f"{v:.6f}" if isinstance(v, float) else str(v)) for v in r) + "\n")
    return len(rows)


def read_summary(run):
    lines = open(os.path.join(run, "generations.txt")).read().splitlines()
    cols = lines[0].split("\t")
    out = []
    for l in lines[1:]:
        vals = l.split("\t")
        out.append([None if v == "" else (float(v) if "." in v else int(v)) for v in vals + [""] * (len(cols) - len(vals))])
    return out


def summary(run, from_summaries=False):
    cfg = json.load(open(os.path.join(run, "config.json")))
    rows = read_summary(run) if from_summaries else generation_rows(run)
    G = cfg["generations"]
    ix = {c: i for i, c in enumerate(COLUMNS)}
    champs = [(r[0], r[ix["champ_holistic_mean"]], r[ix["champ_holistic_wins"]], r[ix["champ_bouts"]]) for r in rows if r[ix["champ_holistic_mean"]] is not None]
    final = [c for c in champs if c[0] >= 0.8 * G]
    reached = rows[-1][0] if rows else -1
    fifths = []
    for i in range(5):
        cs = [c[1] for c in champs if i * G / 5 <= c[0] < (i + 1) * G / 5]
        fifths.append(st.mean(cs) if cs else float("nan"))
    best = max(champs, key=lambda c: c[1]) if champs else None
    return dict(
        run=os.path.basename(run), reached=reached, complete=reached == G - 1 and bool(champs) and champs[-1][0] == G - 1,
        final_fifth=st.mean(c[1] for c in final) if final else float("nan"),
        final_fifth_sd=st.pstdev([c[1] for c in final]) if len(final) > 1 else float("nan"), final_fifth_n=len(final),
        final_fifth_list=[c[1] for c in final],
        wins=sum(c[2] for c in champs), bouts=sum(c[3] for c in champs), best=best, fifths=fifths,
        environment=[(r[0], r[1], r[2]) for r in rows],
        mass_budget=cfg["sim"]["synthesis"]["mass_budget"], settle=cfg["sim"]["settle_time"], k=cfg.get("morph_protection", 0), seed=cfg["seed"],
    )


def conventional_digest(run):
    """sha256 over the conventional population's distinct lineage lines, in order (a resume appends its restart generation twice)."""
    p = os.path.join(run, "lineage.jsonl")
    if not os.path.exists(p):
        return None, 0
    seen, h = set(), hashlib.sha256()
    for l in open(p, "rb"):
        if b'"population": "conventional"' in l and l not in seen:
            seen.add(l)
            h.update(l)
    return h.hexdigest(), len(seen)


def opponent(run):
    """The wheeled side alone from rest: final-fifth mean solo approach (m), steering of 3, and n, from analysis.json."""
    p = os.path.join(run, "analysis.json")
    if not os.path.exists(p):
        return None
    inds = [i for i in json.load(open(p))["individuals"] if i["population"] == "conventional" and i["generation"] >= 200]
    if not inds:
        return None
    return dict(n=len(inds), approach=st.mean(i["capability"]["approach"]["progress"] for i in inds), steering=st.mean(i["capability"]["steering"]["successes"] for i in inds),
                holistic_approach=_holistic(p, "approach"), holistic_terrain=_holistic(p, "terrain"))


def _holistic(path, what):
    inds = [i for i in json.load(open(path))["individuals"] if i["population"] == "holistic" and i["generation"] >= 200]
    if not inds:
        return None
    return st.mean((i["capability"]["approach"]["progress"] if what == "approach" else i["capability"]["terrain"]["success_rate"]) for i in inds)


def corr(x, y):
    mx, my = st.mean(x), st.mean(y)
    sx, sy = math.sqrt(sum((a - mx) ** 2 for a in x)), math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else float("nan")


def main(root="runs/RBT-85", seeds=(201, 202, 203, 204), write=False, from_summaries=False):
    rows = {}
    for seed in seeds:
        for arm in ARMS:
            d = os.path.join(root, f"{arm}-{seed}")
            have = os.path.exists(os.path.join(d, "generations.txt" if from_summaries else "history.json"))
            if have:
                if write and not from_summaries:
                    write_summary(d)
                rows[(arm, seed)] = summary(d, from_summaries)
    print("run        reached complete  final-fifth  sd(ckpt)  wins/bouts   best (gen)   fifths                          k  budget settle")
    for (arm, seed), r in sorted(rows.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        b = f"{r['best'][1]:.2f} ({r['best'][0]})" if r["best"] else "-"
        print(f"{arm}-{seed:<5} {r['reached']:7d} {str(r['complete']):8} {r['final_fifth']:11.3f} {r['final_fifth_sd']:9.3f}  {r['wins']:4d}/{r['bouts']:<5d}  {b:>11}   {', '.join(f'{x:.2f}' for x in r['fifths']):30}  {r['k']}  {r['mass_budget']}  {r['settle']}")

    print("\n1. pairing check: is the wheeled population the same population, on the same terrains?")
    print("seed   conventional lineage (sha256 of distinct lines, n)                        identical   terrain+start seeds identical (generations compared)")
    paired_ok = {}
    for seed in seeds:
        b, p = rows.get(("base", seed)), rows.get(("prot", seed))
        if not b or not p:
            continue
        n = min(len(b["environment"]), len(p["environment"]))
        env_same = b["environment"][:n] == p["environment"][:n]
        if from_summaries:
            print(f"{seed}   (lineage.jsonl is bulk; not available from summaries)                          n/a         {env_same} ({n})")
            paired_ok[seed] = env_same
            continue
        (hb, nb), (hp, np_) = conventional_digest(os.path.join(root, f"base-{seed}")), conventional_digest(os.path.join(root, f"prot-{seed}"))
        same = hb is not None and hb == hp and nb == np_
        paired_ok[seed] = same and env_same
        print(f"{seed}   base {str(hb)[:16]} ({nb})  prot {str(hp)[:16]} ({np_})   {str(same):9}   {env_same} ({n})")

    diffs, used = [], []
    print("\n2-3. paired, protected minus unprotected, with the opponent (wheeled final-fifth solo approach, m; steering of 3) beside it:")
    print("seed   base    prot    d        wins d   best d   complete  paired   opp approach base/prot   opp steering base/prot   holistic solo approach d   terrain d")
    for seed in seeds:
        b, p = rows.get(("base", seed)), rows.get(("prot", seed))
        if not b or not p:
            continue
        d = p["final_fifth"] - b["final_fifth"]
        diffs.append(d)
        used.append(seed)
        ob = None if from_summaries else opponent(os.path.join(root, f"base-{seed}"))
        op = None if from_summaries else opponent(os.path.join(root, f"prot-{seed}"))
        opp = f"{ob['approach']:+7.2f} / {op['approach']:+7.2f}        {ob['steering']:.2f} / {op['steering']:.2f}" if ob and op else "      (analysis.json not available)      "
        solo = f"{op['holistic_approach'] - ob['holistic_approach']:+.2f}                      {op['holistic_terrain'] - ob['holistic_terrain']:+.2f}" if ob and op else ""
        print(f"{seed}   {b['final_fifth']:.3f}   {p['final_fifth']:.3f}   {d:+.3f}   {p['wins'] - b['wins']:+6d}   {p['best'][1] - b['best'][1]:+6.2f}   {str(b['complete'] and p['complete']):8}  {str(paired_ok.get(seed)):6}   {opp}              {solo}")
    if diffs:
        n = len(diffs)
        mean = st.mean(diffs)
        zeros, pos, neg = sum(abs(d) < 0.01 for d in diffs), sum(d > 0 for d in diffs), sum(d < 0 for d in diffs)
        se = st.stdev(diffs) / math.sqrt(n) if n > 1 else float("nan")
        print(f"\nn = {n}  differences: {', '.join(f'{d:+.3f}' for d in diffs)}  mean {mean:+.4f}  range [{min(diffs):+.3f}, {max(diffs):+.3f}]  zeros (|d|<0.01): {zeros}  positive {pos}  negative {neg}  SE of paired mean {se:.4f}")
        if mean >= 0.10 and pos >= 3:
            verdict = "HELPS (mean >= +0.10 and >= 3 seeds positive)"
        elif mean <= -0.10 and neg >= 3:
            verdict = "HURTS (mean <= -0.10 and >= 3 seeds negative)"
        else:
            verdict = "NULL (neither rule met)"
        print("verdict by the pre-registered rule:", verdict)
        if not all(rows[(a, s)]["complete"] for a in ARMS for s in used):
            print("NOT A RESULT: at least one run is incomplete; a partial read of a running arm is not a result.")
        print("\n4. what the pairing bought, and what four seeds resolve:")
        bs, ps = [rows[("base", s)]["final_fifth"] for s in used], [rows[("prot", s)]["final_fifth"] for s in used]
        if n > 1:
            unpaired = math.sqrt(st.variance(bs) / n + st.variance(ps) / n)
            print(f"paired SE {se:.4f}  unpaired SE {unpaired:.4f}  ratio {se / unpaired:.2f}  corr(base, prot) across seeds {corr(bs, ps):+.2f}   (RBT-74 under one shared stream: 0.0729, 0.0628, 1.16, -0.41)")
        sds = [rows[("base", s)]["final_fifth_sd"] for s in used]
        ns = [rows[("base", s)]["final_fifth_n"] for s in used]
        per_run = st.mean(sds) / math.sqrt(st.mean(ns))
        print(f"unprotected final-fifth checkpoint SD {st.mean(sds):.3f} -> SD of a final-fifth mean {per_run:.3f}; resolvable at 2 SE with n={n}: {2 * per_run * math.sqrt(2) / math.sqrt(n):.3f} if the two arms' checkpoint noise were independent (it is not: they now share terrains and opponents)")
        # The paired checkpoint-level noise, which is what the shared streams actually leave: SD of (prot - base) checkpoint by checkpoint.
        cks = []
        for s in used:
            lb, lp = rows[("base", s)]["final_fifth_list"], rows[("prot", s)]["final_fifth_list"]
            if len(lb) == len(lp) and len(lb) > 1:
                cks.append(st.pstdev([y - x for x, y in zip(lb, lp)]) / math.sqrt(len(lb)))
        if cks:
            print(f"checkpoint-paired: SD of a pair's final-fifth difference from checkpoint noise {st.mean(cks):.3f}; resolvable at 2 SE with n={n}: {2 * st.mean(cks) / math.sqrt(n):.3f} (checkpoint noise only)")
        print(f"from the observed spread of the paired differences: {2 * se:.3f} (2 SE; includes the holistic side's run-to-run drift).  |mean| = {abs(mean):.4f} is {'inside' if abs(mean) < 2 * se else 'outside'} it.")
    if write and not from_summaries:
        print(f"\nwrote generations.txt in {len(rows)} run directories")


if __name__ == "__main__":
    args = sys.argv[1:]
    root = next((a for a in args if not a.startswith("--") and not a.replace(",", "").isdigit()), "runs/RBT-85")
    seeds = tuple(int(x) for x in args[args.index("--seeds") + 1].split(",")) if "--seeds" in args else (201, 202, 203, 204)
    main(root, seeds, write="--write-summaries" in args, from_summaries="--from-summaries" in args)
