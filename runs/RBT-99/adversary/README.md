# RBT-99 adversary probes (C2, dearer work)

Scope: what is C2-specific in `runs/RBT-99/PREREGISTRATION.md` (PR #80). Nothing here is a result; every
probe is design arithmetic or a resampling model. No RBT-99 arm was run.

Bulk: probes 1-4 read the ten RBT-90 part 2 baselines from their durable checkpoints
(`scripts/durable.sh restore BULKDIR/forage-SEED rbt-90-SEED`), **pre-onset seasons only** (< 340; T is in
[340, 400]), and print nothing RBT-90 part 2 scores. The arms were at 172-413 of 600 when restored
(13:40 UTC), so seeds 1 and 2 read an earlier 40-season window (281-320, 193-232).

| file | what | re-run |
|---|---|---|
| `kj_baseline.{py,txt}` | the population's own kJ and its gain re-priced to 0.08, per seed and fauna | `python runs/RBT-99/adversary/kj_baseline.py BULKDIR` |
| `collapse_mc.{py,txt}` | resampling model of the designed fauna after the shift: deaths in k's window, min alive, the income D reads | `python runs/RBT-99/adversary/collapse_mc.py BULKDIR` (2 min) |
| `kj_heritability.{py,txt}` | repeatability (ICC) and parent-child slope of kJ | `python runs/RBT-99/adversary/kj_heritability.py BULKDIR` |
| `newborn_gain.{py,txt}` | do robots in their first three seasons earn like adults | `python runs/RBT-99/adversary/newborn_gain.py BULKDIR` |
| `run_arm_identity.{sh,txt}` | RBT-92's launcher before PR #80 (`44c4e95`) against merged: every file and message | `runs/RBT-99/adversary/run_arm_identity.sh` |
| `smoke_rederived.txt` | the designer's smoke check re-run from scratch (`smoke_runs.sh 801`, `smoke_check.py`) | as named |

`work_budget.py` was re-run and reproduces `work_budget.txt` byte for byte.
