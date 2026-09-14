"""Adversary probe for RBT-28, attacks 2 and 3: the 12-draw figures re-read at 64 paired seeds.

RBT-38's standing rule: a lesion effect is read at 32-64 PAIRED seeds with the per-seed
differences shown, never at 8-16, and no effect is real if the lesion changes nothing on more
than half the seeds (the zero-count veto).  RBT-28 read every mode at 12 draws.  That is enough
to kill a 50% claim and, as its author says, not enough to establish a small one -- so the two
figures that carry a number rather than a "no" are re-read here at the rule's n:

* baseline-801 g300, the family's one wired nose: `no_smell` costs 6% at 12 draws (published 50%
  at 8 seeds).  Is 6% a number or noise?  Also `no_env`, the "sensorium is a net handicap" half.
* RBT-13 g390, the series' headline mower: 3.12 items at 8 seeds, 2.42 +- 0.56 at 12 draws.  The
  author's Q3 rule ("inside its own 95% interval") was, by their own account, too lenient.  What
  does the count read at 64, and where do 3.12 and 2.42 sit against that interval?
* RBT-16 g590 intact at 64, since the report sets its 4.08 beside g390's 2.42.

Same harness as the autopsy (`scripts/forage_lab.py`'s `trial`, `draws=0`: no null replay, the
null is not what is being re-read), same seeds 8000+, extended to 64.  No champion, config or
seed changed.  Usage: python runs/RBT-28/adversary_n64.py  (after runs/RBT-28/extract.sh)
"""
import os, sys

import numpy as np

sys.path.insert(0, "scripts")
from forage_lab import groups, load, trial  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

N = 64
SEEDS = list(range(8000, 8000 + N))
CASES = [  # (label, run, gen, modes)
    ("baseline-801 g300", "runs/RBT-28/data/baseline-801", 300, ("intact", "no_smell", "no_env")),
    ("RBT-13 g390", "runs/RBT-28/data/RBT-13", 390, ("intact", "no_global")),
    ("RBT-16 g590", "runs/RBT-28/data/RBT-16", 590, ("intact",)),
]


def paired(a, b):
    d = np.asarray(a, float) - np.asarray(b, float)
    se = d.std(ddof=1) / np.sqrt(len(d))
    t = d.mean() / se if se > 0 else float("nan")
    return d, float(d.mean()), float(se), float(t), int((d == 0).sum())


def main():
    out = []
    for label, run, gen, modes in CASES:
        g, cfg = load(run, "holistic", gen)
        ph = synthesize(g, cfg.synthesis)
        gs = groups(ph)
        rows = {m: [trial(g, cfg, ph, gs, s, m) for s in SEEDS] for m in modes}
        items = {m: [r["food"] for r in rows[m]] for m in modes}
        work = np.asarray([r["work"] for r in rows["intact"]], float)  # kJ, for the items-per-kJ claim at the same n
        base = np.asarray(items["intact"], float)
        se = base.std(ddof=1) / np.sqrt(N)
        sd = base.std(ddof=1)
        out.append(f"\n=== {label}: {N} draws, seeds {SEEDS[0]}..{SEEDS[-1]} ===")
        out.append(f"intact  {base.mean():.3f} +- {se:.3f} items  (95% interval [{base.mean() - 1.96 * se:.2f}, {base.mean() + 1.96 * se:.2f}]; "
                   f"first 12 draws alone: {base[:12].mean():.3f} +- {base[:12].std(ddof=1) / np.sqrt(12):.3f}; per-draw sd {sd:.2f})")
        out.append(f"        work {work.mean():.3f} +- {work.std(ddof=1) / np.sqrt(N):.3f} kJ; items per kJ {base.mean() / work.mean():.3f}; "
                   f"draws needed to see a 22% drop at t = 2.5: {(2.5 * sd / (0.22 * base.mean())) ** 2:.0f}")
        for m in modes[1:]:
            d, mean, dse, t, zeros = paired(base, items[m])
            out.append(f"{m:8s} {np.mean(items[m]):.3f} items; intact minus {m}: {mean:+.3f} +- {dse:.3f}  "
                       f"({100 * mean / base.mean():+.1f}% of intact), paired t {t:+.2f}, zero differences {zeros}/{N}"
                       f"{'  <- VETOED (unmoved on more than half the seeds)' if zeros > N / 2 else ''}")
            out.append("         per-seed differences: " + " ".join(f"{int(x):+d}" for x in d))
    text = "\n".join(out)
    print(text)
    os.makedirs("docs/runs", exist_ok=True)
    with open("docs/runs/RBT-28-adversary-n64.txt", "w") as f:
        f.write(text.strip() + "\n")


if __name__ == "__main__":
    main()
