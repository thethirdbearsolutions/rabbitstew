"""The pre-registered readout for RBT-74: protected minus unprotected, paired by seed.

Primary outcome: holistic mean champion fitness over the final fifth (checkpoints at
generations >= 0.8 * generations), protected minus unprotected, per seed, with the zero count
(|d| < 0.01), mean and range, and the verdict rule posted on RBT-74 before the runs:
  helps  iff mean >= +0.10 and >= 3 of 4 seeds positive;
  hurts  iff mean <= -0.10 and >= 3 of 4 seeds negative;
  else null.
Secondary, same form: holistic wins over the run, best checkpoint, per-fifth means.
Instrument check: from the unprotected arm's checkpoint-to-checkpoint variation in the final
fifth, the paired mean difference four seeds could have resolved (2 SE of the paired mean).

    python runs/RBT-74/readout.py [runs/RBT-74] [--seeds 201,202,203,204]

Reads history.json only.  No simulation.
"""
import json
import math
import os
import statistics as st
import sys


def load(run):
    h = json.load(open(os.path.join(run, "history.json")))
    cfg = json.load(open(os.path.join(run, "config.json")))
    return h["champions"], cfg


def fifths(champs, generations):
    out = []
    for i in range(5):
        lo, hi = i * generations / 5, (i + 1) * generations / 5
        cs = [c for c in champs if lo <= c["generation"] < hi]
        out.append(st.mean(c["holistic_mean_fitness"] for c in cs) if cs else float("nan"))
    return out


def summary(run):
    champs, cfg = load(run)
    G = cfg["generations"]
    final = [c for c in champs if c["generation"] >= 0.8 * G]
    done = champs[-1]["generation"] if champs else -1
    return dict(
        run=os.path.basename(run), reached=done, complete=bool(champs) and done == G - 1,
        final_fifth=st.mean(c["holistic_mean_fitness"] for c in final) if final else float("nan"),
        final_fifth_sd=st.pstdev([c["holistic_mean_fitness"] for c in final]) if len(final) > 1 else float("nan"),
        final_fifth_n=len(final),
        wins=sum(c["holistic_wins"] for c in champs), bouts=sum(c["n_bouts"] for c in champs),
        best=max(champs, key=lambda c: c["holistic_mean_fitness"]) if champs else None,
        fifths=fifths(champs, G),
        mass_budget=cfg["sim"]["synthesis"]["mass_budget"], settle=cfg["sim"]["settle_time"], k=cfg.get("morph_protection", 0),
    )


def main(root="runs/RBT-74", seeds=(201, 202, 203, 204)):
    rows = {}
    for seed in seeds:
        for arm in ("base", "prot"):
            d = os.path.join(root, f"{arm}-{seed}")
            if os.path.exists(os.path.join(d, "history.json")):
                rows[(arm, seed)] = summary(d)
    print("run        reached complete  final-fifth  sd(ckpt)  wins/bouts   best (gen)   fifths                          k  budget settle")
    for (arm, seed), r in sorted(rows.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        b = f"{r['best']['holistic_mean_fitness']:.2f} ({r['best']['generation']})" if r["best"] else "-"
        print(f"{arm}-{seed:<5} {r['reached']:7d} {str(r['complete']):8} {r['final_fifth']:11.3f} {r['final_fifth_sd']:9.3f}  {r['wins']:4d}/{r['bouts']:<5d}  {b:>11}   {', '.join(f'{x:.2f}' for x in r['fifths']):30}  {r['k']}  {r['mass_budget']}  {r['settle']}")
    diffs, wins_d, best_d = [], [], []
    print("\npaired, protected minus unprotected:")
    print("seed   final-fifth d   wins d   best d   complete")
    for seed in seeds:
        b, p = rows.get(("base", seed)), rows.get(("prot", seed))
        if not b or not p:
            continue
        d = p["final_fifth"] - b["final_fifth"]
        diffs.append(d)
        wins_d.append(p["wins"] - b["wins"])
        best_d.append(p["best"]["holistic_mean_fitness"] - b["best"]["holistic_mean_fitness"])
        print(f"{seed}   {d:+13.3f}   {p['wins'] - b['wins']:+6d}   {best_d[-1]:+6.2f}   {b['complete'] and p['complete']}")
    if diffs:
        n = len(diffs)
        mean = st.mean(diffs)
        zeros = sum(abs(d) < 0.01 for d in diffs)
        pos, neg = sum(d > 0 for d in diffs), sum(d < 0 for d in diffs)
        se = st.stdev(diffs) / math.sqrt(n) if n > 1 else float("nan")
        print(f"\nn = {n}  differences: {', '.join(f'{d:+.3f}' for d in diffs)}  mean {mean:+.3f}  range [{min(diffs):+.3f}, {max(diffs):+.3f}]  zeros (|d|<0.01): {zeros}  positive {pos}  negative {neg}  SE of paired mean {se:.3f}")
        if mean >= 0.10 and pos >= 3:
            verdict = "HELPS (mean >= +0.10 and >= 3 seeds positive)"
        elif mean <= -0.10 and neg >= 3:
            verdict = "HURTS (mean <= -0.10 and >= 3 seeds negative)"
        else:
            verdict = "NULL (neither rule met)"
        print("verdict by the pre-registered rule:", verdict)
        # Instrument check: what could four paired seeds have resolved?  Two readings of the same
        # noise: the checkpoint-to-checkpoint SD within the final fifth of the unprotected arm
        # (11 checkpoints, so the SD of an 11-checkpoint mean is that / sqrt(11)) and the SE of
        # the paired mean actually observed.
        sds = [rows[("base", s)]["final_fifth_sd"] for s in seeds if ("base", s) in rows]
        ns = [rows[("base", s)]["final_fifth_n"] for s in seeds if ("base", s) in rows]
        if sds and all(x == x for x in sds):
            per_run = st.mean(sds) / math.sqrt(st.mean(ns))
            print(f"instrument: unprotected final-fifth checkpoint SD {st.mean(sds):.3f} (mean over seeds) -> SD of a final-fifth mean {per_run:.3f}; paired difference of two such means has SD {per_run * math.sqrt(2):.3f}; smallest paired mean difference resolvable at 2 SE with n={n}: {2 * per_run * math.sqrt(2) / math.sqrt(n):.3f} (checkpoint noise only) versus {2 * se:.3f} from the observed spread of the paired differences (includes seed-to-seed drift)")
    json.dump({"rows": {f"{a}-{s}": r for (a, s), r in rows.items()}, "diffs": diffs, "wins_diffs": wins_d, "best_diffs": best_d}, open(os.path.join(root, "readout.json"), "w"), indent=1)


if __name__ == "__main__":
    root = next((a for a in sys.argv[1:] if not a.startswith("--")), "runs/RBT-74")
    seeds = tuple(int(x) for x in sys.argv[sys.argv.index("--seeds") + 1].split(",")) if "--seeds" in sys.argv else (201, 202, 203, 204)
    main(root, seeds)
