# RBT-129 steps leg re-measured at c ≥ 1 (`steps2`): readout plan (pre-data addendum)

*Written and committed before any `steps2` output was opened. No `ckpt/rbt-129-stage0-pays-*-steps2` branch had been
fetched or restored when this commit was pushed; its commit timestamp is the audit trail. Inputs read so far: #467's
plan and readout (`runs/RBT-129/legs-readout/`), the rulings cited below, the launch record
`runs/RBT-129/lanes/pays-steps-c1c2/launch.txt`, its check `runs/RBT-129/launch-adversary/CHECK-480.md`, and the source of
`runs/RBT-125/gate/steps.py` at blob `d4b91bf` (what it prints, not what it printed).*

This is an addendum to `runs/RBT-129/legs-readout/READOUT-PLAN.md` (#467). Everything there stands unless this file
changes it.

## 1. What is being re-read

- **The ruling on #467** (comment 5870339780): an exploded season is not a measurement, so at the 12 c ≥ 1 cells the
  steps condition was NOT READABLE and designed PAYS was UNDECIDED. It registered a re-measurement: fresh seeds
  126000–126127, `steps.py --exclude-exploded`, everything else as in A1.4.
- **The ruling on #475** (14:31, comment 5872013112): r is the ratio of the per-host **medians** of the paired,
  non-exploded per-season path speeds. The mean r and the maximum kept path speed are descriptive only.
- **The launch:** #480, head `5cbb2be`, checked OK in `CHECK-480.md`. Its `launch.txt` pins `steps.py` at `d4b91bf` and
  flags `--seed0 126000 --exclude-exploded`.
- **The data:** the 12 branches `ckpt/rbt-129-stage0-pays-<cell>-steps2`, restored with `scripts/durable.sh restore`,
  each holding `steps2/designed.txt`. Nothing else is fetched: no first-leg, Stage P or census branch.

## 2. The line that decides the steps condition (per cell)

**The registered line is exactly one line per cell:** the `STEP <cell> | nose step w 3 -> 3.4 | …` line of that cell's
`designed.txt`, and within it **only the field after `| vs per-unit speed (n N; K out for > 25% exploded): `**, whose form
is `m [lo, hi] READING` or `-- NOT READABLE`.

- The steps condition is **met** iff that field's READING is `NOSE LEADS` or `COMPARABLE` (#467 plan §2; A1.4's labels
  and order, as implemented by `reading()` in `steps.py` `d4b91bf`).
- It is **not met** at `SPEED LEADS` or `TIED, UNRESOLVED`.
- **NOT READABLE** is shown when the field reads `-- NOT READABLE`. `steps.py` prints this when fewer than 2 hosts
  remain in the per-unit line after (a) hosts with > 25% of the nose pair's or the speed@w3 pair's 128 paired seeds
  exploded leave it (the `K out` count), and (b) hosts with median r < 1.10 at w3 leave it. The readout also shows N
  and K, and the number of hosts dropped at r < 1.10 (from the `at w3:` summary line), so it is visible why a line
  has the hosts it has.
- **A missing `STEP … nose step w 3 -> 3.4` line, a missing `designed.txt`, or an integrity failure** is also shown as
  NOT READABLE for that cell (never as a negative finding).
- The `first nose (w 0 -> 0.4)` and `nose step w 1 -> 1.4` STEP lines, and the `vs raw speed@w3 (descriptive, …)` field
  of every STEP line, are printed beside and never decide.

## 3. The verdict per cell

The prize condition is #467's, unchanged (its lower bound is > 0 at 10 of the 12 c ≥ 1 cells, and fails at c2-U-L and
c2-HP-L; the prize was not re-run and is not re-read). Designed PAYS = prize condition AND steps condition. One of
three verdicts, and no other reading:

| prize LB > 0 (#467) | registered steps field | verdict |
|---|---|---|
| yes | NOSE LEADS or COMPARABLE | **PAYS** |
| yes | SPEED LEADS or TIED, UNRESOLVED | **DOES NOT PAY** |
| yes | NOT READABLE | **UNDECIDED (not readable)** |
| no | any | **DOES NOT PAY** (the conjunction fails on the prize alone; the steps field is printed beside) |

The last row is fixed now because the rule is a conjunction: at c2-U-L and c2-HP-L the verdict cannot depend on the
steps. A TIED cell's DOES NOT PAY is labelled "(unresolved)" in the table, as #467 did (#473, SHOULD 2): it is a power
result, not a finding that the nose step does not pay.

## 4. Printed beside the line, descriptive only

Per cell, next to the registered field:
- **the r line (median; the registered r):** the `at w3:` summary: hosts out for > 25% exploded, r mean [t 95%] and
  range, how many of the hosts in enter at r ≥ 1.10, and the per-unit speed step (+25% realised) at w3 with its t 95%;
- **the mean r** at w3 per cell (mean over hosts in of the `r (mean, descriptive)` column), **the maximum kept path
  speed** at w3 (the largest `max path speed arm` / `max path base arm` over hosts), and **the list of hosts whose
  median and mean r fall on opposite sides of 1.10** (the `at w3: mean and median r on opposite sides` line);
- **the raw line:** the `vs raw speed@w3 (descriptive, …)` field of the w 3 → 3.4 STEP line;
- the nose step w 3 → 3.4 and the raw speed step at w3 (items, t 95%, hosts in) from the steps table, per #467 plan §4,
  and the "lead carried by the speed step" flag under the same definition;
- the first-nose and w 1 → 1.4 per-unit readings;
- the hosts in and out: signed hosts, K out for > 25% exploded, dropped at r < 1.10, N in the line.

None of these changes a verdict.

## 5. Robustness (as #467 plan §6.5, adapted)

- Leave one host out of the registered per-unit line, `reading()` applied to each; a verdict that flips under a single
  omission is flagged **FRAGILE** with the omission.
- Under `--exclude-exploded` the per-host table prints each arm's mean over its **own** non-exploded seeds, not the
  per-comparison pairs, so the per-host per-unit values can only be reconstructed approximately:
  `(w3.4 − w3) − (speed@w3 − w3) × 0.25 / (r@w3 − 1)` over the hosts that pass the > 25% and r ≥ 1.10 filters. A first
  check compares the reconstructed full-sample mean and interval with the STEP line. **Where they agree to within
  0.01 on every figure**, the leave-one-out readings are reported. Where they do not, leave-one-out is reported as
  "not reconstructable" for that cell and no FRAGILE flag is given or withheld on it.
- No multiplicity correction (none is registered); 12 cells re-read.

## 6. Caveats carried from #467

The pre-fairness host caveat (#443, S3), no decoy at U and HP, and A1.4's power statement ("The expected reading is TIED,
UNRESOLVED, unless one step leads by about 0.17 or more") all apply unchanged.

## 7. Deliverables

`runs/RBT-129/legs-readout-steps2/`: this plan; `integrity.txt` (branches present, STEP lines present, the
`d4b91bf` / `126000` pins, exploded-season counts per cell); `steps2_readout.py` (parses the 12 `designed.txt` files
into the table above, and prints every number); its output `steps2_readout.txt`; `READOUT-STEPS2.md`, headline first,
with the c ≥ 1 verdicts set beside #467's c = 0 calls.
