"""RBT-121 audit C: auditor B's section 4 (PR #395, ecology_s.py), re-run in the committed *foraging* economy.

B's synthetic model uses the EcologyConfig defaults (living cost 0.05), mu = 0.25 and a Gaussian
member x season noise of 1.16.  Every committed foraging ecology (RBT-19 P-801, RBT-80, RBT-106) instead ran
living cost 0.25 and initial energy 3.0, and P-801's holistic mean lifetime score is about 1.3 (probe_queue.txt).
This keeps B's additive Delta (items/season) and B's sigma, sets mu = 1.3 and cost = 0.25, and reports the
carrier share after 300 seasons (the RBT-80 / paper 10 horizon) and the per-season s fitted from the share
trajectory: logit(share_t) = logit(share_0) + s t.  Six carriers of 60 planted; 400 replicates; with and without
an erosion u per birth (a carrier's child loses the allele with probability u, B's 0.15)."""
import sys
import numpy as np
CAP, THR, BCOST, AGE, INIT, COST, MU, SD = 60, 3.0, 1.0, 60, 3.0, 0.25, 1.3, 1.16


def run(order, delta, u, reps, seasons=300, seed=1):
    rng = np.random.default_rng(seed)
    shares = np.zeros((reps, seasons))
    for r in range(reps):
        pop = [[1 if i < 6 else 0, INIT, int(rng.integers(0, AGE))] for i in range(CAP)]
        for t in range(seasons):
            for p in pop:
                p[1] += MU + (delta if p[0] else 0.0) + SD * rng.standard_normal() - COST
                p[2] += 1
            pop = [p for p in pop if p[1] > 0 and p[2] < AGE]
            br = [p for p in pop if p[1] >= THR]
            rng.shuffle(br)
            if order == "energy":
                br.sort(key=lambda p: -p[1])  # stable, after the shuffle: B's proposal
            for p in br:
                if len(pop) >= CAP:
                    break
                p[1] -= BCOST
                allele = p[0] and not (u and rng.random() < u)
                pop.append([int(allele), BCOST, 0])
            shares[r, t] = sum(p[0] for p in pop) / max(1, len(pop))
    m = shares.mean(axis=0)
    lg = np.log(np.clip(m, 1e-3, 1 - 1e-3) / (1 - np.clip(m, 1e-3, 1 - 1e-3)))
    s = np.polyfit(np.arange(seasons), lg, 1)[0]
    return m[-1], s


reps = int(sys.argv[1]) if len(sys.argv) > 1 else 400
print(f"# committed foraging economy: cost {COST}, mu {MU}, sigma {SD}, init {INIT}; 6/60 carriers; 300 seasons; {reps} reps")
for delta in (0.05, 0.1, 0.2, 0.5, 1.0):
    cells = []
    for u in (0.0, 0.15):
        for order in ("shuffled", "energy"):
            sh, s = run(order, delta, u, reps)
            cells.append(f"{order:8s} u{u:.2f}: share {sh:4.2f} s {s:+.4f}")
    print(f"Delta +{delta:.2f}:  " + "   ".join(cells), flush=True)
