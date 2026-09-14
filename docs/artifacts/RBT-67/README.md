# RBT-67 — bound the compass prize past a = 64, per population

`compass_dose_response.py` widens the merged RBT-69 harness (`scripts/compass_replication.py`)
to a ∈ {32, 64, 96, 128, 192, 256, 384} on both committed populations, with the chemotactic
sign set per population's direction of travel. `PREREGISTRATION.md` was written before any
bout ran. Readouts land here as `w4b.txt` / `w4b.json` and `p801.txt` / `p801.json`.

## Status

**Run, 2026-09-14.** Both populations, 7,168 bouts, 177 tests passing beforehand. Report in
`runs/RBT-67/REPORT.md`. Verdict: no turnover inside the range on either population; the curve
is still rising at a = 384 (W4b-801 +1.875 [+1.243, +2.438], 7/7; P-801 forward drivers
+8.094 [+4.694, +10.000]). The a = 64 anchor reproduces the source's +0.897 within its CI.

## To run (from the repository root)

The seven W4b-801 bests live on the RBT-45 branch (PR #5) and are not on the integration
branch. Take only those files, not the branch:

```
git fetch origin claude/rbt-45-2oa635
git checkout origin/claude/rbt-45-2oa635 -- \
    docs/artifacts/RBT-23-W4b-801/config.json \
    docs/artifacts/RBT-23-W4b-801/conventional \
    docs/artifacts/RBT-23-W4b-801/README.md \
    docs/artifacts/RBT-23-W4b-801/travel_direction.txt
pip install -e '.[dev]' && pytest -q          # 177 expected to pass

python scripts/travel_direction.py docs/artifacts/RBT-23-W4b-801                 # expect pooled ~ -174 deg, BACKWARD
python scripts/travel_direction.py runs/RBT-19/P-801 0 100 200 300 400 500 590    # expect pooled forward; g100, g400 backward

python docs/artifacts/RBT-67/compass_dose_response.py 64 4 both 2>&1 | tee docs/artifacts/RBT-67/run.log
```

About ten minutes per population on four cores (7 robots × 64 seeds × 8 conditions = 3,584
bouts each). The a = 0 condition is the baseline; `install()` installs nothing at k = 0.

## What the readout carries per cell

Realised a (path-sum readback, never the installed w), |a|/|c|, items, paired Δ with a
bootstrap-over-robots CI, robots improved, the per-seed difference list per robot, zero
differences and zero-item bouts, in-disc path and items per in-disc metre, turns, the
both-effectors-pinned fraction, explosions, and a turnover verdict per population using
the definitions fixed in `PREREGISTRATION.md`.
