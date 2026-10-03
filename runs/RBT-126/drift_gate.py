"""RBT-126 item 4: how often does the eligibility test bite in a no-selection (drift) arm?

ecology.py:524 takes as breeders the living with ``energy >= birth_threshold``.  A drift arm (RBT-65 drift, RBT-71
neutral-*, RBT-80 seed*/drift) sets living_cost 0, birth_threshold 0, birth_cost 0 and starvation off.  A member's
energy is then its starting energy + its cumulative gross gain, and it is barred while that is below 0:
  * a founder starts at initial_energy (3.0, ecology.py:212): barred while its cumulative gain is below -3;
  * a child starts at birth_cost (0.0 in a drift arm, ecology.py:539): barred while its cumulative gain is below 0,
    i.e. from its first net-negative season.  (RBT-121 ADVERSARY "also noticed" gives -3 for everyone; that is
    the founders' margin only.)

Two readings:
  actual          on a committed threshold-0 arm.  From lineage.jsonl: exactly, the share of evaluated member-seasons
                  with energy < threshold, and of lives ever barred.  From lineage-last.txt (each life's last row
                  only): each life's final cumulative gain = fitness x evals, so "barred at its last season" is
                  exact; its barred seasons are estimated with a constant per-season rate (a child with fitness < 0:
                  all its seasons; a founder: evals - ceil(3 / |fitness|)).  Exact at the last row, approximate
                  before it.
  counterfactual  on a committed arm WITH the economy (RBT-99, which has no drift arm): the arm itself cannot show
                  the gate, because the living cost starves a member long before its gain goes negative for long.
                  Instead, the share of the children born in the window whose lifetime mean gain is < 0: such a
                  child, born into a drift arm on these bodies and prices, would be barred from its first seasons.
                  Every birth counts (a 1-season life's mean is one noisy draw, so this over-reads), beside only the
                  lives of >= 10 seasons (the committed sieve's survivors, so this under-reads).  It says what a
                  drift arm run on these bodies and prices would lose, not what any run did.

python3 runs/RBT-126/drift_gate.py actual RUN_DIR [...]
python3 runs/RBT-126/drift_gate.py counterfactual RUN_DIR:LO-HI [...]
"""
import importlib.util, json, math, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("regime", HERE.parents[1] / "scripts" / "regime.py")
rg = importlib.util.module_from_spec(spec); spec.loader.exec_module(rg)


def economy(run_dir):
    p = pathlib.Path(run_dir) / "config.json"
    e = (json.load(open(p)).get("ecology") or {}) if p.exists() else {}
    return (float(e.get("initial_energy", 2.0)), float(e.get("birth_cost", 1.0)), float(e.get("birth_threshold", 3.0)))


def actual(run_dir):
    e0, bc, thr = economy(run_dir)
    pops, last, has_energy = rg.read_lineage(run_dir)
    for kind, P in sorted(pops.items()):
        lives = [l for l in P["lives"].values() if l.evals > 0]
        if has_energy:
            seasons = barred = 0
            ever = set()
            for g, rows in P["seasons"].items():
                for name, e, age, ev, _ in rows:
                    if ev == 0:
                        continue
                    seasons += 1
                    if e < thr:
                        barred += 1
                        ever.add(name)
            print(f"{run_dir} {kind}: exact from lineage.jsonl: barred member-seasons {barred}/{seasons} = "
                  f"{barred / max(1, seasons):.4f}; lives ever barred {len(ever)}/{len(lives)} = {len(ever) / max(1, len(lives)):.4f}")
            continue
        out = {}
        for who, sel, margin in (("founders", lambda l: l.parent is None, e0 - thr), ("children", lambda l: l.parent is not None, bc - thr)):
            ls = [l for l in lives if sel(l)]
            if not ls:
                continue
            tot = sum(l.evals for l in ls)
            at_end = [l for l in ls if l.fitness * l.evals < -margin]
            est = sum(max(0, l.evals - (math.ceil(margin / -l.fitness) if margin > 0 else 0)) for l in ls if l.fitness < 0)
            out[who] = (len(ls), len(at_end), est, tot, margin, at_end)
        allt = sum(v[3] for v in out.values())
        alle = sum(v[2] for v in out.values())
        parts = [f"{who} (margin {v[4]:+.0f}): {v[1]}/{v[0]} lives barred at their last season ({v[1] / v[0]:.3f}), "
                 f"est. barred member-seasons {v[2]}/{v[3]} ({v[2] / max(1, v[3]):.3f})" for who, v in out.items()]
        bar = [l.fitness for v in out.values() for l in v[5]]
        print(f"{run_dir} {kind} (lineage-last.txt, seasons 0-{last}): " + "; ".join(parts) +
              f"; all: est. barred member-seasons {alle / max(1, allt):.3f}; median lifetime mean gain of the barred "
              f"{np.median(bar) if bar else float('nan'):+.3f}")


def counterfactual(spec_):
    run_dir, win = spec_.rsplit(":", 1)
    lo, hi = map(int, win.split("-"))
    pops, last, _ = rg.read_lineage(run_dir)
    for kind, P in sorted(pops.items()):
        lives = [l for l in P["lives"].values() if l.parent is not None and lo <= l.born <= hi and l.evals > 0]
        if not lives:
            print(f"{run_dir} {kind} births {lo}-{hi}: no births")
            continue
        parts = []
        for label, keep in (("all births", 1), (">= 10 seasons", 10)):
            ms = np.array([l.fitness for l in lives if l.evals >= keep])
            parts.append(f"{label}: none" if not len(ms) else f"{label} n {len(ms)}: lifetime mean gain < 0 {np.mean(ms < 0):.3f}")
        print(f"{run_dir} {kind} births {lo}-{hi}: " + "; ".join(parts))


if __name__ == "__main__":
    mode, *args = sys.argv[1:]
    for a in args:
        (actual if mode == "actual" else counterfactual)(a)
