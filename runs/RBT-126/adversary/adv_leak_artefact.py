"""RBT-126 adversary, probe 2: does --energy-leak 0.3 (leakx:0.3) read things other than a mean-income edge as selection?

Uses the PR's replica (runs/RBT-126/breeding_rules.py) unchanged, by passing a different income draw for the mutant.
Design as the PR's invasion cell: 6 mutants among 60, 400 seasons, living cost 0.25, work 0.1; share and fixation.

  (a) reproduce: x1.25 mean-income mutant, shuffle vs leakx:0.3, g0 1.0 / 1.3 / 3.0;
  (b) a *variance-only* mutant: the same mean gross income g0, drawn as g0 * 2 * Bernoulli(0.5) - i.e. feast or
      famine - so its season score has the same mean but far higher variance.  A rule that ranks by recent energy
      can favour it with no mean edge.  Also a milder one: Poisson(2 g0) * Bernoulli(0.5);
  (c) a *mean-cost, variance-gain* mutant: 0.9 x mean, feast-or-famine.  Under a rule that selects on mean income it
      should lose; if it wins, the rule is selecting on variance.

python3 runs/RBT-126/adversary/adv_leak_artefact.py [reps] > runs/RBT-126/adversary/adv_leak_artefact.txt
"""
import importlib.util, pathlib, sys
from multiprocessing import Pool
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("breeding_rules", HERE.parents[2] / "runs/RBT-126/breeding_rules.py")
br = importlib.util.module_from_spec(spec)
spec.loader.exec_module(br)


class Proxy:
    """The generator br.run is given: every call is the real Generator's except poisson, which is overridden."""
    def __init__(self, rng, poisson):
        self._rng, self.poisson = rng, poisson

    def __getattr__(self, k):
        return getattr(self._rng, k)


def cell(args):
    rule, g0, kind, reps, seed = args
    rng = np.random.default_rng(seed)
    real_poisson = rng.poisson

    # br.run calls rng.poisson(g_of(type)).  g_of returns a sentinel for the mutant; we intercept it here.
    def poisson(lam):
        if lam >= 0:
            return real_poisson(lam)
        m = -lam  # the mutant's mean gross income
        if kind.startswith("ff"):  # feast or famine: 2m with p 0.5, else 0 (mean m)
            return 2 * m if rng.random() < 0.5 else 0.0
        if kind.startswith("pb"):  # Poisson(2m) half the seasons, else 0 (mean m)
            return real_poisson(2 * m) if rng.random() < 0.5 else 0.0
        return real_poisson(m)
    prng = Proxy(rng, poisson)
    mult = {"x1.25": 1.25, "ff1.0": 1.0, "pb1.0": 1.0, "ff0.9": 0.9, "pb0.9": 0.9}[kind]
    # the mutant's mean is passed as a negative sentinel so poisson() above can tell it apart
    g_of = (lambda t: g0 * (1.25 if t else 1.0)) if kind == "x1.25" else (lambda t: -(g0 * mult) if t else g0)
    fr = np.array([br.run(prng, g_of=g_of, n_mut=6, seasons=400, rule=rule)["share"] for _ in range(reps)])
    return rule, g0, kind, float(fr.mean()), float(fr.std() / np.sqrt(reps)), float(np.mean(fr == 1.0)), float(np.mean(fr == 0.0))


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    cells = [(r, g, k, reps, 9000 + i) for i, (r, g, k) in enumerate(
        (r, g, k) for k in ("x1.25", "ff1.0", "pb1.0", "ff0.9", "pb0.9") for g in (1.0, 1.3, 3.0) for r in ("shuffle", "leakx:0.3"))]
    print(f"# 6 mutants among 60, 400 seasons, {reps} reps; neutral share 0.10")
    print("# kind: x1.25 = Poisson(1.25 g0); ff1.0 = 2 g0 w.p. 0.5 else 0 (same mean, high variance); pb1.0 = Poisson(2 g0) w.p. 0.5 else 0;")
    print("#       ff0.9 / pb0.9 = the same at 0.9 x the mean (a mean LOSS with a variance gain)")
    print("# kind | g0 | rule | share ± SE | fixed | lost")
    with Pool(4) as pool:
        for rule, g0, kind, sh, se, fx, lo in pool.imap(cell, cells):
            print(f"{kind:6s} | g0 {g0:3.1f} | {rule:9s} | {sh:.3f}±{se:.3f} | fixed {fx:.2f} | lost {lo:.2f}", flush=True)
