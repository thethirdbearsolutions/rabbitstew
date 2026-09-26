"""RBT-99 adversary probe 2: what 0.08 does to the designed fauna's alive count and to the axis class D reads.

A resampling model, not a run.  Start: every individual alive at the last pre-onset season read by probe 1
(window end E = min(340, seasons written); every season read is < 340 <= T), with its logged energy, age,
lifetime score and evals (ckpt/rbt-90-SEED lineage.jsonl).  Each later season it draws one of ITS OWN
season rows from the 40-season window (a fauna-pool row if it has < 3), re-priced to w by the exact
identity gain(w) = gain(0.03) - (w - 0.03) kJ (simulation.py food_gain), and pays the 0.25 basal cost; it
dies at energy <= 0 or age 60 and breeds at energy >= 3 into a free slot of 60, paying 1 (ecology.py
steps 2-4).  A child (energy 1) takes its parent's rows with probability b, else a random window
individual's rows: b is the parent-child slope of kJ, measured at 0.29-0.92 (probe 3), so b = 0.5 is
central, b = 0 is "kJ not heritable" and b = 1 is the upper bound.  No new variation: mutation's cheaper
bodies are not modelled, which errs toward the designed fauna failing.

Per seed, fauna and b, 100 replicates, reported as medians over replicates:
  deaths[T,T+10)   the shift arm's deaths in cull_k.py's window (k = this minus the baseline's)
  deaths[T+10,60)  deaths the k window does not see
  min alive        over the transient [T, T+60)
  inc trans/rec    the fauna's mean_lifetime_score (ecology.py _record: mean over the living of
                   score_sum / evals, pre-T seasons included; 0 if extinct) averaged over the transient
                   [T, T+60) and the recovery window [T+60, T+160)
  D-half           the designed half of class D on this seed: inc trans < 0.25 or inc rec < 0.25 or
                   min alive < 12 (share of replicates)
Instrument check: the same model at w = 0.03 must hold both faunas near capacity at an income near the
baseline's own (the last column: the baseline's mean_lifetime_score over the window read, history.json).

    python runs/RBT-99/adversary/collapse_mc.py BULKDIR > runs/RBT-99/adversary/collapse_mc.txt
"""
import json
import os
import statistics as st
import sys

import numpy as np

BASAL, CAP, MAXAGE, BT, BC = 0.25, 60, 60, 3.0, 1.0
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
REPS, H = 100, 160


def load(d):
    end = min(340, json.load(open(os.path.join(d, "state.json")))["season"])
    rows, last = {}, {}
    for line in open(os.path.join(d, "lineage.jsonl")):
        r = json.loads(line)
        g = r["generation"]
        if end - 40 <= g < end and "work" in r:
            rows.setdefault((r["population"], r["name"]), []).append((r["last_score"], r["work"] / 1000))
        if g == end - 1:
            last[(r["population"], r["name"])] = (r["energy"], r["age"], r["fitness"] * r["evals"], r["evals"])
    hist = {(h["season"], h["population"]): h for h in json.load(open(os.path.join(d, "history.json")))["history"]}
    return end, rows, last, hist


def sim(fauna, rows, last, w, b, rng):
    pool = [x for (f, _), v in rows.items() if f == fauna for x in v]
    srcs = [v for (f, _), v in rows.items() if f == fauna and len(v) >= 3]
    own = lambda k: rows[k] if len(rows.get(k, [])) >= 3 else pool
    # member: [energy, age, score_sum, evals, rows]
    pop = [[e, a, ss, ev, own(k)] for k, (e, a, ss, ev) in last.items() if k[0] == fauna and e > 0]
    alive, inc, d10, d60 = [], [], 0, 0
    for d in range(H):
        dead = 0
        for m in pop:
            s, kj = m[4][rng.integers(len(m[4]))]
            g = s - (w - 0.03) * kj
            m[0] += g - BASAL
            m[1] += 1
            m[2] += g
            m[3] += 1
        keep = [m for m in pop if m[0] > 0 and m[1] < MAXAGE]
        dead = len(pop) - len(keep)
        pop = keep
        for i in rng.permutation(len(pop)):
            if len(pop) >= CAP:
                break
            m = pop[i]
            if m[0] >= BT:
                m[0] -= BC
                pop.append([BC, 0, 0.0, 0, m[4] if rng.random() < b else srcs[rng.integers(len(srcs))]])
        if d < 10:
            d10 += dead
        elif d < 60:
            d60 += dead
        alive.append(len(pop))
        inc.append(float(np.mean([m[2] / max(1, m[3]) for m in pop])) if pop else 0.0)
    return alive, inc, d10, d60


def main(bulk):
    print(__doc__.split("\n\n")[0])
    print()
    rng = np.random.default_rng(99)
    print(f"{'seed':>4} {'fauna':12} {'w':>4} {'b':>3} {'deaths[T,T+10)':>14} {'deaths[T+10,60)':>15} {'min alive':>9} "
          f"{'inc trans':>9} {'inc rec':>8} {'D-half':>6}   baseline income, window")
    summ = {}
    for seed in SEEDS:
        end, rows, last, hist = load(os.path.join(bulk, f"forage-{seed}"))
        for fauna in ("holistic", "conventional"):
            real = st.mean(hist[(s, fauna)]["mean_lifetime_score"] for s in range(end - 40, end))
            for w, b in ((0.03, 0.5), (0.08, 0.0), (0.08, 0.5), (0.08, 1.0)):
                res = [sim(fauna, rows, last, w, b, rng) for _ in range(REPS)]
                mins = [min(a[:60]) for a, *_ in res]
                itr = [np.mean(i[:60]) for _, i, *_ in res]
                irc = [np.mean(i[60:160]) for _, i, *_ in res]
                dh = np.mean([(x < .25) or (y < .25) or (z < 12) for x, y, z in zip(itr, irc, mins)])
                row = (np.median([r[2] for r in res]), np.median([r[3] for r in res]), np.median(mins),
                       np.median(itr), np.median(irc), dh)
                summ.setdefault((fauna, w, b), []).append(row)
                print(f"{seed:>4} {fauna:12} {w:4.2f} {b:3.1f} {row[0]:14.0f} {row[1]:15.0f} {row[2]:9.0f} "
                      f"{row[3]:9.3f} {row[4]:8.3f} {row[5]:6.2f}   {real:.3f}")
    print()
    for (fauna, w, b), v in summ.items():
        v = np.array(v)
        print(f"  {fauna:12} w={w:.2f} b={b:.1f}: deaths[T,T+10) {np.median(v[:, 0]):.0f} ({v[:, 0].min():.0f}..{v[:, 0].max():.0f}); "
              f"min alive {v[:, 2].min():.0f}..{v[:, 2].max():.0f}; inc trans {v[:, 3].min():.3f}..{v[:, 3].max():.3f}; "
              f"inc rec {v[:, 4].min():.3f}..{v[:, 4].max():.3f}; seeds D-half in >= half the replicates: {int((v[:, 5] >= .5).sum())}/10")


if __name__ == "__main__":
    main(sys.argv[1])
