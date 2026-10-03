# RBT-129 steps2 readout (#487 @ `623af31`): adversary

**Verdict: CONFIRMED WITH CAVEATS.**

Designed PAYS holds at none of the 12 c ≥ 1 cells. I re-derived that independently from the 12 restored `designed.txt`
files, and it survives every check below. No MUST findings. Two SHOULDs concern wording and one concerns how a
coordinator note is phrased. Neither changes a verdict.

My parser is `adv_rederive.py` (this directory). It does not share code with `steps2_readout.py`, and it tabulates its
own t quantiles. Its output is in `adv_rederive.txt`.

## 1. Plan before data

- **The commit order is as stated.** `5938b41` (19:25:54Z) adds only `READOUT-PLAN.md`, and no later commit edits that
  file. Integrity follows at `d96b099` (19:28:21Z), then the readout at `0f7c03a` and a range correction at `623af31`.
- **The only change to the script after integrity is a parser fix.** In `0f7c03a` the host-table parse moved from a
  regex to a split, and the first table's interval print was tidied. No rule, threshold or label changed.
- **Git cannot prove the data was not read early.** The ckpt branches were already on the remote before the plan: the
  last one, c2-PW-G, is stamped 19:23:11Z. So "not read before `5938b41`" rests on the author's statement, as it did at
  #467. That is NIT 1.
- **The mapping is #467's registered one.** Steps met ⇔ the per-unit field of the `nose step w 3 -> 3.4` line reads
  NOSE LEADS or COMPARABLE (#467 plan §2, as re-registered by the ruling on #467). Designed PAYS = that AND the prize's
  t(9) 95% lower bound > 0 (#467 plan §3). The plan's §3 truth table is exactly that conjunction.
- **TIED is handled correctly.**
  - #467 plan §2 fixes that TIED does not pay "at least comparably". So TIED means not PAYS.
  - The "(unresolved)" qualifier carries #473 SHOULD 2 and the ruling's "TIED means unresolved".
  - UNDECIDED stays reserved for NOT READABLE, which is the category the ruling used for contaminated input.

## 2. Integrity

My independent parse agrees with `integrity.txt` on every point.

| check | result |
|---|---|
| headers | All 12 files carry `# fairness: 'fair'`, their own `worlds/config/<cell>/config.json`, and `128 paired seeds from 126000` |
| signed hosts | 14 / 14 / 15 / 15 / 15 / 15 / 15 / 15 / 14 / 14 / 15 / 15, in the table's cell order. The per-host table lists exactly the signed hosts |
| exploded arm-seasons, summed from the per-host columns | 51, 87, 42, 97, 51, 84, 46, 79, 74, 76, 78, 78, equal to `integrity.txt` |
| hosts out for > 25% exploded | 0 in the w3 line at every cell |
| hosts out at r < 1.10 | Recounted from the per-host median r at w3, N equals the STEP line's n at all 12 cells: 10, 9, 11, 10, 12, 13, 10, 11, 6, 6, 8, 8 |
| `d4b91bf` / `--seed0 126000` pins | `designed.txt` records no blob, so these rest on `launch.txt`, the runners' exit-6 guard and CHECK-480, as the readout says. I did not re-audit #480 |

## 3. The 12 rows, re-derived

For each cell I parsed the STEP w3 per-unit field and recomputed its label from m [lo, hi] and n:
- the t(n−1) standard error is backed out of the 95% half-width;
- the 90% interval is then checked against ±0.10.

The prize is parsed from #467's `legs_readout.txt`, first row per cell.

| cell | per-unit m [95%] (n) | label (printed = recomputed) | prize LB (#467) | PAYS |
|---|---|---|---|---|
| c1-U-L | −0.110 [−0.279, +0.059] (10) | TIED | +0.012 | no (unresolved) |
| c2-U-L | −0.007 [−0.109, +0.096] (9) | COMPARABLE | **−0.015** | no (prize) |
| c1-U-G | −0.147 [−0.368, +0.074] (11) | TIED | +0.304 | no (unresolved) |
| c2-U-G | −0.204 [−0.394, −0.014] (10) | SPEED LEADS | +0.185 | no |
| c1-HP-L | −0.136 [−0.371, +0.098] (12) | TIED | +0.112 | no (unresolved) |
| c2-HP-L | −0.194 [−0.328, −0.059] (13) | SPEED LEADS | **−0.024** | no (prize) |
| c1-HP-G | +0.222 [−0.321, +0.765] (10) | TIED | +0.486 | no (unresolved) |
| c2-HP-G | −0.052 [−0.336, +0.233] (11) | TIED | +0.340 | no (unresolved) |
| c1-PW-L | −0.328 [−0.622, −0.034] (6) | SPEED LEADS | +0.040 | no |
| c2-PW-L | −0.135 [−0.326, +0.055] (6) | TIED | +0.007 | no (unresolved) |
| c1-PW-G | −0.013 [−0.340, +0.315] (8) | TIED | +0.304 | no (unresolved) |
| c2-PW-G | +0.029 [−0.366, +0.424] (8) | TIED | +0.315 | no (unresolved) |

**All 12 rows match `steps2_readout.txt` §1:**
- the numbers, n, labels and verdicts;
- the 8 TIED, the 2 SPEED LEADS, and the 2 prize failures.

I also spot-checked §2, and it agrees:
- the median-r summaries and "k of N enter";
- the crossing hosts at c1-PW-L;
- the raw line.

The readout's descriptive claims hold on the printed numbers:
- the TIED 95% widths run 0.34 to 1.09;
- the per-unit speed step half-widths are 0.33 to 0.38 at PW-G and c1-HP-G;
- the nose step has LB > 0 at all six G cells;
- at the L cells the nose step covers 0, except c2-U-L (−0.050 [−0.086, −0.014]).

**The r in use is the median, as the #475 ruling requires.** Every file's r table is headed "r = median path (speed
arm) / median path (base arm) per host". The per-host table header reads "r is the paired median r".

## 4. The prize: which account is right

- **The prize figures used match #467's merged `legs_readout.txt` exactly, at all 12 cells.**
- **#467 does show a lower bound ≤ 0 at c2-U-L and c2-HP-L:**
  - c2-U-L: +0.043 [**−0.015**, +0.102], "no";
  - c2-HP-L: +0.056 [**−0.024**, +0.135], "no".
- The same holds at c0-PW-L (−0.062), where #467 already called not PAYS.

The coordinator's phrase "the prize condition stands at all 18 cells" comes from the ruling on #467 (comment
5870339780). The same sentence goes on: "Explosions touch it at no more than 1% of seasons". So it rules that the prize
*measurement* is valid at all 18 cells. It does not say that the prize's lower bound is > 0 at all 18.

**The readout's reading is the right one.** The prize condition is met at 15 of 18 cells, and it fails at c2-U-L and
c2-HP-L (and c0-PW-L). Those two cells are DOES NOT PAY on the prize alone. This does not change the headline: without
the prize failures, c2-U-L's COMPARABLE would be the only steps-met cell at c ≥ 1, and c2-HP-L reads SPEED LEADS
anyway. That is SHOULD 2.

## 5. Robustness (descriptive only; nothing re-decided)

- **The mean-r line.** I rebuilt it from the per-host table, entering hosts at mean r ≥ 1.10. It is approximate for the
  same pairing reason the plan gives.
  - It changes two labels: c1-U-L goes from TIED to SPEED LEADS (−0.132 [−0.263, −0.001]), and c2-U-G goes from SPEED
    LEADS to TIED.
  - c2-U-L goes from COMPARABLE to TIED, and its prize fails either way.
  - It gives n = 9 to 11 at PW, against 6 to 8 under the median.
  - **No verdict flips.** No prize-met cell reaches NOSE LEADS or COMPARABLE. The nearest is c1-HP-G, at +0.433
    [−0.062, +0.928], which is TIED.
- **Leave one host out.** At the 4 cells where the reconstruction meets the plan's 0.01 tolerance, my readings agree
  with §4 of the readout: c2-U-L (COMPARABLE/TIED), c1-U-G (TIED), c2-U-G (SPEED/TIED) and c1-HP-L (TIED).
- **The 8 cells outside tolerance.** The reconstruction misses there by 0.012 to 0.071, as the readout says. Running
  leave-one-out on the approximate reconstruction anyway (outside the plan, descriptive), no omission at any cell
  reaches NOSE LEADS or COMPARABLE. The readings reached are TIED, or SPEED LEADS/TIED.
  - This supports the readout's "looks unlikely", but it is still not a registered check.
  - **The plan's "not reconstructable" is the right label,** and the readout keeps to it.

## 6. Wording: "DOES NOT PAY (unresolved)" versus "UNDECIDED"

- **UNDECIDED would be wrong.** Under the plan and the #467 ruling, UNDECIDED means the line was not readable. All 12
  lines are readable (n ≥ 6, 0 hosts out for explosions), and TIED is a registered label that does not meet the steps
  condition. Calling these cells UNDECIDED would understate a registered result.
- **"DOES NOT PAY (unresolved)" is faithful to the rule,** because PAYS is false. It was fixed pre-data in plan §3. The
  readout also says three times that it is a power result, and not a finding that the nose step does not pay (headline,
  summary and §4). That is not overclaiming.
- **However, the vocabulary is inconsistent** (SHOULD 1). The ruling on #467 asked that "TIED means unresolved, not
  'does not pay'", and #467 printed "not PAYS (unresolved)". The readout's headline table sets "not PAYS" at c = 0
  beside "DOES NOT PAY" at c ≥ 1 for the same condition. Someone reading only a row could take "DOES NOT PAY" as a
  negative finding.

## Findings

**MUST:** none.

**SHOULD 1 (wording).** Print the verdict at the TIED cells as #467 did: "not PAYS (unresolved)". Better, use "not
PAYS" throughout, with "(unresolved)", "(SPEED LEADS)" or "(prize)" in brackets.
- Do this in the headline table, §2 and `steps2_readout.txt` §5, and in the script's `verdict()` labels.
- It aligns with the ruling's own words ("TIED means unresolved, not 'does not pay'") and with the c = 0 column.
- No verdict changes.

**SHOULD 2 (prize provenance).** Add one sentence to the readout (§4, "The prize is not re-measured"):
- "#467's lower bound is ≤ 0 at c2-U-L (−0.015) and c2-HP-L (−0.024); the ruling's 'the prize condition stands at all
  18 cells' validates the prize measurement, not LB > 0 at every cell."
- That closes off the misreading in the coordinator's note.

**SHOULD 3 (robustness, descriptive).** Optionally, print the mean-r labels beside the verdicts. Two labels move
(c1-U-L to SPEED LEADS, c2-U-G to TIED), and the PW lines grow from n = 6–8 to n = 9–11. No verdict moves. That makes
the "Median r against mean r" caveat concrete. The #475 ruling keeps it descriptive.

**NIT 1.** "Written and committed before any `steps2` output was opened" cannot be checked from git: the ckpt branches
predate `5938b41` by about 2.5 minutes. State it as the author's attestation, as #467 did, or cite the session log.

**NIT 2.** In §2 the headline table abbreviates "TIED, UNRESOLVED" as "TIED" in the raw-line column but not in the
registered column. It is harmless, but a legend line would help.

---
Reproduce: restore the 12 `ckpt/rbt-129-stage0-pays-<cell>-steps2` branches into `DIR/<cell>` with `scripts/durable.sh
restore`, then run `python3 runs/RBT-129/legs-readout-steps2-adversary/adv_rederive.py DIR` from the repo root. It
needs no scipy.
