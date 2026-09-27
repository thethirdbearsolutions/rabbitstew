# RBT-120 runner brief: one wave, two sessions (Sa, Sb), two arms each

**Do not launch until the coordinator has ruled on the design adversary and merged the design.** No arm runs
before that ruling.

**Follow `runs/RBT-113/RUNNER.md` §0–§5 in full**, including the no-peek rules, durable checkpoints, resume, the
38-file commit by role with `git add -f`, and one PR per arm. Make only the substitutions below. Change no script.

| RBT-113 | RBT-120 |
|---|---|
| ticket RBT-113 | ticket **RBT-120** |
| `runs/RBT-113/...` | `runs/RBT-120/...` |
| arms O1–O4, Z1–Z4 | arms **B1–B4** only (default operator plus `--motor-budget 1.77`) |
| durable label `rbt-113-ARM` | `rbt-120-ARM` (checkpoint branch `ckpt/rbt-120-ARM`) |
| results branch `results/RBT-113-ARM` | `results/RBT-120-ARM` |
| §1.3 `prelaunch.py` | `runs/RBT-120/prelaunch.sh` must end `PRELAUNCH: PASS`. It runs the full suite and rewrites `runs/RBT-120/controls/prelaunch.txt` for this tree; do not commit that file. |

| session | arm A | arm B | seeds |
|---|---|---|---|
| Sa | B1 | B2 | 1 2 3 · 4 5 6 |
| Sb | B3 | B4 | 7 8 9 · 10 11 12 |

- **An arm** is nine `evolve` runs (3 seeds × U, D, C), exactly as an RBT-113 O arm, with one flag added.
- **Seed directories** are `runs/RBT-120/B1/1` and so on: the seed alone, no prefix, so that RBT-113's `readout.py`
  and `decompose.py` parse them unchanged.
- **Time:** RBT-113's O arms took about 1.9 h each (2.5 h for the slowest) with two arms side by side at
  WORKERS=2. Budget **2.5 h per session**.
- **Launch:** `WORKERS=2 runs/RBT-120/run_arm.sh ARM`. The durable loop is
  `DURABLE_WATCH_PID=<pid> scripts/durable.sh every 20 runs/RBT-120/ARM rbt-120-ARM`. Find the pid with
  `pgrep -f "^/bin/bash runs/RBT-120/run_arm.sh ARM$"`.
- **Wake prompts:** "Delegate wake: RBT-120 session Sx done, PRs #a #b", and
  "Delegate wake: RBT-120 session Sx, <what>; read it and act".

## 6. The readout (the designer, not the runners)

Once all four arm PRs are merged, on an x86_64 checkout of the merged integration branch (PREREGISTRATION.md §4–§5):

1. **Restore** the four B arms, and the four RBT-113 O arms they are paired with:
   ```
   for A in B1 B2 B3 B4; do scripts/durable.sh restore runs/RBT-120/$A rbt-120-$A; done
   for A in O1 O2 O3 O4; do scripts/durable.sh restore runs/RBT-113/$A rbt-113-$A; done
   ```
   `status` must read 216/216 for each. Afterwards `git diff --quiet -- runs/RBT-120 runs/RBT-113` must succeed.
2. **Decompose.** RBT-113's `decompose.py`, unchanged, run under the budget:
   ```
   python runs/RBT-120/decompose_budgeted.py --workers 4 runs/RBT-120/B[1-4]/[0-9]* > runs/RBT-120/decompose.txt
   ```
   This takes about 25 min on 4 cores and writes `decompose.json` into each B seed directory.
3. **RBT-113's readout.py, unchanged**, against the frozen σ0 (descriptive; `budget.py` carries the verdicts):
   ```
   python runs/RBT-113/readout.py --reference runs/RBT-113/sigma0_reference.json runs/RBT-120/B[1-4]/[0-9]* > runs/RBT-120/readout.txt
   ```
4. **The registered readout.** Q1 and Q2, with controls K1–K5:
   ```
   python runs/RBT-120/budget.py runs/RBT-120/B[1-4]/[0-9]* > runs/RBT-120/budget.txt
   ```
5. **Q3.** RBT-117's `compare.py`, unchanged:
   ```
   python runs/RBT-120/compare_budgeted.py runs/RBT-120/B[1-4]/[0-9]* > runs/RBT-120/compare.txt
   ```
6. **The motor table** (deliverable 2):
   ```
   python runs/RBT-120/motor_report.py runs/RBT-120/B[1-4]/[0-9]* > runs/RBT-120/motors_B.txt
   ```
7. **The per-line lever probes** (DESIGN.md §7.6), unchanged and run under the budget:
   ```
   B="runs/RBT-120/B[1-4]/[0-9]*"
   python runs/RBT-120/levers_budgeted.py runs/RBT-121/physics/probe_static.py $B > runs/RBT-120/levers_static_B.txt
   python runs/RBT-120/levers_budgeted.py runs/RBT-121/adversary/phys_ghost.py --workers 4 $B > runs/RBT-120/levers_ghost_B.txt
   python runs/RBT-120/levers_budgeted.py runs/RBT-121/adversary/phys_passive.py --workers 4 $B > runs/RBT-120/levers_passive_B.txt
   ```
   The O baselines (`levers_*_O.txt`) are already committed.
8. **Commit by role:** `decompose.txt`, the 12 `decompose.json`, `readout.txt`, `budget.txt`, `compare.txt`,
   `motors_B.txt` and `levers_*_B.txt`. The restored bulk stays out.
