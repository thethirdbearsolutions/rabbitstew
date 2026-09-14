"""Whole-subsystem lesions with a paired t, at the pre-registered 64 draws (RBT-84).

`forage_lab.py` prints a per-unit ranking but no paired t against intact, and RBT-84's item 2 asks
for `no_osc`/`no_global`/`no_env`/`no_smell` **with** paired t. That is what this adds; extra modes
can be named on the command line to get the same for specific units.

WITHDRAWN, and left here because the claim went on the ticket: this script was written believing the
full per-unit table cost 4-5 hours on the 10-part champion and was therefore unaffordable at n = 64.
**It costs about 40 minutes.** The "no mode completed in a 110 s window" observation behind the 4-5 h
figure was `grep -v WARNING` in `sweep.sh` block-buffering its output to a file -- `forage_lab.py`
flushes every row -- so I had measured my own plumbing. The table was obtained and is in the report.
Readouts written before 09:30 carry the superseded figure in their header comment; their numbers are
unaffected. See REPORT.md section 7.4.

Prediction C is scored on the lesion reading per the 07:46 seam-4 amendment, and the six whole
subsystems answer its trichotomy (effector / global neuron / oscillator) directly.

This imports `forage_lab.trial` unchanged rather than editing the shared script mid-arm, so the
bouts are the same bouts the full table would have run.

usage: champion_subsystems.py RUN_DIR KIND GEN [N_DRAWS] [N_LAYOUTS]
"""
import importlib.util
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
spec = importlib.util.spec_from_file_location("flab", ROOT / "scripts" / "forage_lab.py")
flab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flab)

run, kind, gen = sys.argv[1], sys.argv[2], int(sys.argv[3])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 64
draws = int(sys.argv[5]) if len(sys.argv) > 5 else 120

g, cfg = flab.load(run, kind, gen)
ph = flab.synthesize(g, cfg.synthesis)
gs = flab.groups(ph)
# Default: the six whole subsystems.  Extra modes may be named on the command line (e.g.
# "lesion:20 lesion:34") to get a paired t against intact for specific units -- forage_lab.py's
# per-unit ranking prints the cost but not the t, and a cost is not a result without one.
MODES = ["intact", "no_env", "no_smell", "no_osc", "no_global", "no_local"] + sys.argv[6:]
seeds = list(range(8000, 8000 + n))

print(f"# {run} {kind} gen {gen}: {len(ph.parts)} parts, {len(ph.units)} units, {len(ph.links)} links")
print(f"# whole-subsystem modes only, {n} draws x {draws} null layouts "
      f"(forage_lab.py's own per-unit table takes about 40 minutes on this 10-part body)")
print(f"\n{'mode':12s} {'items':>13s} {'null':>7s} {'items/m_in':>10s} {'t vs null':>9s} {'work':>6s}")
rows = {}
for m in MODES:
    rs = [flab.trial(g, cfg, ph, gs, s, m, draws=draws) for s in seeds]
    mean = {k: float(np.nanmean([r.get(k, float("nan")) for r in rs])) for k in rs[0]}
    se = float(np.std([r["food"] for r in rs], ddof=1)) / np.sqrt(n)
    d = np.array([r["food"] - r["null"] for r in rs], dtype=float)
    t = float(d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))) if d.std(ddof=1) > 0 else float("nan")
    rows[m] = (mean, se, np.array([r["food"] for r in rs], dtype=float))
    rate = mean["food"] / mean["path_in"] if mean["path_in"] > 1e-9 else float("nan")
    print(f"{m:12s} {mean['food']:6.3f} +- {se:4.3f} {mean['null']:7.3f} {rate:10.3f} {t:+9.2f} {mean['work']:6.1f}",
          flush=True)

base = rows["intact"][0]["food"]
print(f"\nintact against its own gait: {base:.3f} items vs a null of {rows['intact'][0]['null']:.3f}")
print(f"{'lesion':12s} {'costs':>8s} {'paired t':>9s} {'zeros':>6s}")
for m in MODES[1:]:
    diff = rows["intact"][2] - rows[m][2]
    se = float(diff.std(ddof=1) / np.sqrt(n)) if diff.std(ddof=1) > 0 else 0.0
    t = float(diff.mean() / se) if se > 0 else float("nan")
    print(f"{m:12s} {diff.mean():+8.3f} {t:+9.2f} {int((diff == 0).sum()):5d}/{n}")
sd = float(np.median([ (rows['intact'][2]-rows[m][2]).std(ddof=1) for m in MODES[1:]
                       if (rows['intact'][2]-rows[m][2]).std(ddof=1) > 0 ] or [np.nan]))
print(f"\npower at n = {n}: |t| >= 2.5 resolves {2.5*sd/np.sqrt(n):+.2f} items or larger "
      f"(median per-draw sd {sd:.2f}); 25% of intact is {0.25*base:.2f} items, needing about "
      f"{int(np.ceil((2.5*sd/(0.25*base))**2))} draws.")
