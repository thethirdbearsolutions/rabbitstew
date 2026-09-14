# RBT-81 — the steering-gain instrument, with its two defects retired

What is here:

- `steering_gain_P-801_before.txt` / `_after.txt` — `runs/compass-gain/steering_gain.py` run on
  `runs/RBT-19/P-801` before and after the change. Same population, same files; the columns
  are what changed. (P-801's final sixty carry no two-nose pair, so the numbers are zeros
  either way; the `rho > 1: 60/60` line is the point.)
- `motif.py` — `runs/RBT-45/motif.py` as it should read. That file lives on PR #5's branch
  (`claude/rbt-45-2oa635`), which is not merged, so it cannot be edited from the integration
  branch; this is the full corrected file, and `motif.py.patch` is the unified diff against the
  branch's current version, for PR #5's author to apply.

For `runs/RBT-45/REPORT.md` (same branch), the one-line pointer to add beside the PATH
paragraph of §2 and the `motif.py` rates it quotes:

> **RBT-81:** the depth-4 path `a` these rates use diverges on these brains (spectral radius
> 1.57–4.92 on all fourteen bests); `|a| > |c|` is the sign test `s₁·s₂ < 0`. The instrument now
> reports the depth-1 term, a balance ratio and the sign (`rabbitstew.analysis.steering_terms`);
> the figures here are left as reported.

The instrument itself is `rabbitstew.analysis.steering_terms` (tested in
`tests/test_steering_terms.py`); `runs/compass-gain/steering_gain.py` and the patched
`motif.py` both call it. Report: `runs/RBT-81/REPORT.md`.
