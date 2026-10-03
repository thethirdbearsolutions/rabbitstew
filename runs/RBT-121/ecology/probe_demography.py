"""RBT-121 audit C: does the ecology's breeding rule reward being a *better* forager, or only a good-enough one?

A bodiless replica of ``Ecology.step`` (ecology.py:476-560): 60 slots, gain per season drawn per
individual, living cost, starvation at energy <= 0, death at max_age, then every individual at or above
birth_threshold is shuffled and breeds in that order while a slot is free (a uniform lottery among the
eligible), paying birth_cost into the child.  Two heritable types: the resident (mean gain g0) and a
mutant forager that earns ``m`` times as much.  Gains are Poisson(g) items minus a fixed work charge, the
shape of a foraging season.  We plant 6 mutants among 54 residents with staggered ages and report how
often the mutant type makes up the whole population after 400 seasons (fixation), and its mean share,
under the committed rule and under candidate fixes:

  lottery        the committed rule: uniform shuffle of the eligible
  energy-order   eligible breed in descending energy (the richest first)
  tickets        eligible drawn with probability proportional to energy (a weighted lottery)
  leak-20%       committed lottery, but stored energy decays 20% per season (no hoarding)
  cost-binding   committed lottery, living cost raised to the resident's mean gain

python3 runs/RBT-121/ecology/probe_demography.py [reps]
"""
import sys

import numpy as np

CAP, THR, BCOST, AGE, INIT = 60, 3.0, 1.0, 60, 3.0


def run(rule, g0, mult, cost, reps, seasons=400, seed=0, work=0.1):
    rng = np.random.default_rng(seed)
    fixed, share = 0, []
    for _ in range(reps):
        # (type, energy, age)
        pop = [[1 if i < 6 else 0, INIT, int(rng.integers(0, AGE))] for i in range(CAP)]
        leak = 0.2 if rule == "leak-20%" else 0.0
        c = g0 if rule == "cost-binding" else cost
        for _ in range(seasons):
            for p in pop:
                g = rng.poisson(g0 * (mult if p[0] else 1.0)) - work
                p[1] = p[1] * (1 - leak) + g - c
                p[2] += 1
            pop = [p for p in pop if p[1] > 0 and p[2] < AGE]
            elig = [p for p in pop if p[1] >= THR]
            if rule == "energy-order":
                elig.sort(key=lambda p: -p[1])
            elif rule == "tickets" and elig:
                w = np.array([p[1] for p in elig]); idx = rng.choice(len(elig), size=len(elig), replace=False, p=w / w.sum())
                elig = [elig[i] for i in idx]
            else:
                rng.shuffle(elig)
            for p in elig:
                if len(pop) >= CAP:
                    break
                p[1] -= BCOST
                pop.append([p[0], BCOST, 0])
            if not pop:
                break
            frac = sum(p[0] for p in pop) / len(pop)
            if frac in (0.0, 1.0):
                break
        frac = sum(p[0] for p in pop) / max(1, len(pop))
        fixed += frac == 1.0
        share.append(frac)
    return fixed / reps, float(np.mean(share))


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print(f"# {reps} replicates per cell; 6 mutants planted among 60; 400 seasons; neutral fixation = 0.10")
    print("# gain = Poisson(g) - 0.1 work;  g0 = 1.3 (RBT-19 P-801 holistic lifetime mean score ~1.3)")
    for cost in (0.25, 0.05):
        for mult in (1.0, 1.25, 2.0):
            cells = []
            for rule in ("lottery", "energy-order", "tickets", "leak-20%", "cost-binding"):
                if cost == 0.05 and rule != "lottery":
                    continue
                f, s = run(rule, 1.3, mult, cost, reps)
                cells.append(f"{rule} fix {f:4.2f} share {s:4.2f}")
            print(f"living cost {cost:.2f}  mutant x{mult:4.2f}:  " + "   ".join(cells), flush=True)
