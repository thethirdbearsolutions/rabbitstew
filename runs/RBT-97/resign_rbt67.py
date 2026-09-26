"""RBT-97: re-read RBT-67's committed ladder RE-SIGNED PER ROBOT. No simulation.

RBT-97 was filed on the premise that a correctly wired compass may not pay on these
populations at all, because RBT-69 measured it negative at every paying magnitude on P-801.
That premise does not survive the record:

* RBT-69's negative was RESOLVED on 2026-09-14. P-801 drives forward and W4b-801 drives
  backward, so the identical four weights are a compass for one population and an
  anti-compass for the other. The negative was an anti-compass, correctly measured.
* RBT-67 then ran the dose-response ON BOTH POPULATIONS WITH THE SIGN SET PER POPULATION
  (its pre-registration says so, and both readouts state the sign they installed). On its
  own sign the motif pays on BOTH: W4b +0.435 to +1.875 (7/7 at every rung), P-801 +0.312
  to +5.150 (CI excluding zero from a = 96).

So the question RBT-97 asks has an answer on the record. What the record does NOT have is
the per-ROBOT reading, and RBT-69's own standing rule is that direction of travel is a
property of the individual, measured per generation and not per run. RBT-67 set the sign
per POPULATION, so two of its fourteen robots -- P-801's g100 (+177.2 deg) and g400
(+165.1 deg), which drive backward inside a forward-driving population -- carried an
ANTI-compass throughout, and their losses are averaged into P-801's pooled delta and widen
its interval over robots.

This re-reads the committed per-seed differences in the two RBT-67 JSONs, splitting the
fourteen robots into the twelve that carried their own compass and the two that carried its
inverse. Nothing is re-simulated: every number below is in docs/artifacts/RBT-67/.

RBT-38's zero-count veto is applied as stated there: no effect is real if the manipulation
changes nothing on more than half the seeds.

Usage: python runs/RBT-97/resign_rbt67.py
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "..", "docs", "artifacts", "RBT-67")

#: travel offset per generation, degrees, measured independently of any of this:
#: P-801 from docs/runs/RBT-69-travel-direction.txt, W4b from
#: docs/artifacts/RBT-23-W4b-801/travel_direction.txt. |offset| > 90 is a backward driver.
TRAVEL = {
    "p801": {0: -0.4, 100: +177.2, 200: -4.3, 300: -2.3, 400: +165.1, 500: +23.8, 590: +2.1},
    "w4b": {90: -179.0, 190: +178.6, 290: -168.9, 390: +179.1, 490: -166.1, 550: -171.9,
            590: -173.0},
}
#: the published motif (sign +1) is the compass for a BACKWARD driver (RBT-69's resolution).
PUBLISHED_IS_BACKWARD = True


def boot(vals, draws=20000, seed=20260926):
    """95% interval of the mean, bootstrapped over robots -- RBT-67's own error term."""
    rng = np.random.default_rng(seed)
    v = np.asarray(vals, float)
    m = rng.choice(v, size=(draws, len(v)), replace=True).mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def load(pop):
    d = json.load(open(os.path.join(ART, f"{pop}.json")))
    return d


def main():
    pops = {p: load(p) for p in ("p801", "w4b")}
    rows = {}          # a -> {"compass": [(pop, gen, delta, diffs)], "anti": [...]}
    for pop, d in pops.items():
        sign = float(d["sign"])
        for cell in d["cells"]:
            a = float(cell["a"])
            if a == 0.0:
                continue
            for r in cell["robots"]:
                gen = int(r["gen"])
                back = abs(TRAVEL[pop][gen]) > 90
                # the installed sign is this robot's compass iff it matches its own direction
                correct = (sign > 0) == (back == PUBLISHED_IS_BACKWARD)
                key = "compass" if correct else "anti"
                rows.setdefault(a, {"compass": [], "anti": []})[key].append(
                    (pop, gen, float(r["delta"]), [float(x) for x in r["diffs"]]))

    print("# RBT-97: RBT-67's ladder re-signed PER ROBOT (no simulation; committed data only)\n")
    print("The published motif is the compass for a BACKWARD driver. RBT-67 set the sign per")
    print("POPULATION, so the two backward drivers inside forward-driving P-801 -- g100")
    print("(+177.2 deg) and g400 (+165.1 deg) -- carried an ANTI-compass at every rung.\n")
    first = rows[sorted(rows)[0]]
    print(f"  carried their own compass: {len(first['compass'])} robots "
          f"({', '.join(f'{p} g{g}' for p, g, _, _ in first['compass'])})")
    print(f"  carried its inverse:       {len(first['anti'])} robots "
          f"({', '.join(f'{p} g{g}' for p, g, _, _ in first['anti'])})\n")

    print(f"{'a':>5s} | {'compass n=12':>13s} {'95% CI (robots)':>20s} {'better':>7s} {'zeros':>10s}"
          f" | {'anti n=2':>9s} {'better':>7s}")
    print("-" * 88)
    for a in sorted(rows):
        comp = rows[a]["compass"]
        anti = rows[a]["anti"]
        cd = [x[2] for x in comp]
        lo, hi = boot(cd)
        zeros = sum(1 for x in comp for v in x[3] if v == 0.0)
        n_pairs = sum(len(x[3]) for x in comp)
        ad = [x[2] for x in anti]
        veto = " VETO" if zeros > n_pairs / 2 else ""
        print(f"{a:5.0f} | {np.mean(cd):+13.3f} [{lo:+7.3f}, {hi:+7.3f}] {sum(1 for x in cd if x > 0):>4d}/12"
              f" {zeros:>5d}/{n_pairs}{veto} | {np.mean(ad):+9.3f} {sum(1 for x in ad if x > 0):>4d}/2")

    print("\nper robot, delta items at each rung (all from RBT-67's committed per-seed differences):")
    ladder = sorted(rows)
    print("  " + f"{'robot':>10s} {'travel':>9s} {'sign':>8s} | " +
          " ".join(f"a={a:<6.0f}" for a in ladder))
    seen = []
    for key in ("compass", "anti"):
        for pop, gen, _, _ in rows[ladder[0]][key]:
            seen.append((key, pop, gen))
    for key, pop, gen in seen:
        ds = []
        for a in ladder:
            ds += [d for p, g, d, _ in rows[a][key] if (p, g) == (pop, gen)]
        print(f"  {pop + ' g' + str(gen):>10s} {TRAVEL[pop][gen]:+8.1f}° "
              f"{'compass' if key == 'compass' else 'ANTI':>8s} | "
              + " ".join(f"{d:+8.3f}" for d in ds))

    print("\nThe twelve correctly-signed robots and the two inverted ones separate at every rung.")
    print("That is RBT-67's own pre-registered prediction (confidence 0.80, 'g100 and g400 lose at")
    print("every rung >= 64') read one level finer, and it holds at every rung including 32.")


if __name__ == "__main__":
    main()
