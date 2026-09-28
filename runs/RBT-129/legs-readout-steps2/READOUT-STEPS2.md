# RBT-129: readout of the designed steps leg re-measured at c ≥ 1 (`steps2`)

*Rules: `READOUT-PLAN.md` (this directory), an addendum to #467's plan. It was committed and pushed pre-data at `5938b41`
(19:25:54Z). Integrity was committed at `d96b099` (19:28:21Z), before any readout number was computed. Every number
below is a line of `steps2_readout.txt` or `integrity.txt`, both printed by `steps2_readout.py`. The prize figures are
#467's (`legs-readout/legs_readout.txt`), which were not re-run. Only the 12 `ckpt/rbt-129-stage0-pays-<cell>-steps2`
branches were read.*

## Headline

**Designed PAYS holds at none of the 12 c ≥ 1 cells. All 12 are now readable, and the verdict at each is not PAYS.**
- **8 cells are TIED, UNRESOLVED:** not PAYS (unresolved). This is a power result: the steps were not resolved, and it is
  not a finding that the nose step fails to pay.
- **2 cells read SPEED LEADS:** c2-U-G and c1-PW-L.
- **2 cells fail on the prize** (#467), whatever the steps read. c2-U-L reads COMPARABLE there, and c2-HP-L reads SPEED
  LEADS.

**Together with #467's c = 0 calls, designed PAYS holds at 2 of 18 cells: c0-PW-G, and c0-HP-G, which is FRAGILE and has
no decoy check.** No cell is UNDECIDED any more.

| cell | c = 0 (#467) | c = 1 (this readout) | c = 2 (this readout) |
|---|---|---|---|
| U-L | not PAYS (SPEED LEADS) | not PAYS (unresolved) | not PAYS (prize; steps COMPARABLE) |
| U-G | not PAYS (unresolved) | not PAYS (unresolved) | not PAYS (SPEED LEADS) |
| HP-L | not PAYS (SPEED LEADS) | not PAYS (unresolved) | not PAYS (prize; steps SPEED LEADS) |
| HP-G | **PAYS** (FRAGILE, no decoy) | not PAYS (unresolved) | not PAYS (unresolved) |
| PW-L | not PAYS (prize; steps SPEED LEADS) | not PAYS (SPEED LEADS) | not PAYS (unresolved) |
| PW-G | **PAYS** | not PAYS (unresolved) | not PAYS (unresolved) |

**Summary.** Designed PAYS at c ≥ 1 is not met at any cell. The re-measurement removed the reason these cells were
UNDECIDED. No host left any line for > 25% exploded seeds, and the median r now sits at 1.10–1.22 per cell (host range
0.82–2.05), where the first leg reached 943. As a result all 12 lines are readable. None reads NOSE LEADS, so the first
readout's NOSE LEADS at c1-PW-G and c2-PW-G (withdrawn under the #467 ruling) are not reproduced; both now read TIED.
The only COMPARABLE is at c2-U-L, whose prize lower bound is ≤ 0 (#467), so it cannot pay. Where the reading is TIED (8
cells), "not PAYS (unresolved)" means unresolved: the 95% intervals are 0.34 to 1.09 wide against δ = 0.10, as A1.4's power
statement predicted. With #467's c = 0 calls, designed PAYS holds at 2 of 18 cells, both at c = 0 and s = G (PW-G, and
HP-G, which is FRAGILE and has no decoy). **Caveats:**
- The per-unit lines are thin at PW: 6 to 8 hosts, because the r ≥ 1.10 filter drops 6 to 8 of 14 or 15 hosts there.
- The leave-one-out check was reconstructable at 4 of 12 cells only (§3), so fragility is unshown at the other 8.
- The pre-fairness host caveat and the no-decoy caveat at U and HP carry over from #467.

## 1. Integrity (`integrity.txt`): PASS

- **All 12 branches exist.** Every MANIFEST reads "consistent", and each `designed.txt` has its 3 `STEP` lines, labelled
  with its own cell.
- **Every header reads** `# fairness: 'fair'`, `# world from runs/RBT-129/worlds/config/<cell>/config.json; 128 paired
  seeds from 126000`.
- **The pins.**
  - `launch.txt` (#480) records `tool:runs/RBT-125/gate/steps.py d4b91bf…` and `flags --seed0 126000
    --exclude-exploded`, with `--fair` and `--eat-from root --eat-rule surface`. Its `cells` line is exactly the 12 c ≥ 1
    cells.
  - Each of the 3 runners carries the exit-6 blob guard on `d4b91bf`, and each of their 12 jobs passes `--seed0 126000`.
  - `steps.py` is `d4b91bf` at #480's head `5cbb2be` and at this branch's base.
- **Exploded seasons, over all hosts and 9 arms** (arm-seasons, out of 128 × 9 × 14 or 15 ≈ 16–17 thousand per cell):

  | U-L c1 / c2 | U-G | HP-L | HP-G | PW-L | PW-G |
  |---|---|---|---|---|---|
  | 51 / 87 | 42 / 97 | 51 / 84 | 46 / 79 | 74 / 76 | 78 / 78 |

  - About 0.2–0.6% of arm-seasons exploded.
  - **No host was out for > 25% exploded in any line at any cell.**
  - The per-arm counts are in `integrity.txt`.
- **What the branches cannot show:** as at #467, the snapshots record no commit (MANIFEST progress is "?"). The tie to
  `d4b91bf` rests on the runners' exit-6 guard, `launch.txt` and CHECK-480.

## 2. Per cell (`steps2_readout.txt` §1–§3)

**The registered line** is the per-unit field of `STEP <cell> | nose step w 3 -> 3.4`, the nose step minus the per-unit
+25% speed step at w3, paired per host, t 95%. It uses median r (the #475 ruling). "In" is the number of hosts in the
line, then the number out for > 25% exploded, from the hosts signed. **The prize is #467's.** The last column is descriptive only (#475 ruling; #488 SHOULD 3): the per-unit line rebuilt
from the per-host table with hosts entering at **mean** r ≥ 1.10, approximate for the pairing reason in §3. It moves two
labels (c1-U-L to SPEED LEADS, c2-U-G to TIED), grows the PW lines to 9–11 hosts, and moves no verdict: no prize-met
cell reaches NOSE LEADS or COMPARABLE under it.

| cell | prize [t(9) 95%] | LB > 0 | nose − speed, per-unit (in; out) | label | **verdict** | mean-r line (n), descriptive |
|---|---|---|---|---|---|---|
| c1-U-L | +0.102 [+0.012, +0.192] | yes | −0.110 [−0.279, +0.059] (10; 0) | TIED, UNRESOLVED | **not PAYS (unresolved)** | −0.132 [−0.263, −0.001] (13) SPEED LEADS |
| c2-U-L | +0.043 [−0.015, +0.102] | no | −0.007 [−0.109, +0.096] (9; 0) | COMPARABLE | **not PAYS (prize)** | −0.030 [−0.118, +0.058] (8) TIED |
| c1-U-G | +0.531 [+0.304, +0.759] | yes | −0.147 [−0.368, +0.074] (11; 0) | TIED, UNRESOLVED | **not PAYS (unresolved)** | −0.141 [−0.306, +0.024] (14) TIED |
| c2-U-G | +0.307 [+0.185, +0.430] | yes | −0.204 [−0.394, −0.014] (10; 0) | SPEED LEADS | **not PAYS (SPEED LEADS)** | −0.082 [−0.222, +0.058] (10) TIED |
| c1-HP-L | +0.179 [+0.112, +0.246] | yes | −0.136 [−0.371, +0.098] (12; 0) | TIED, UNRESOLVED | **not PAYS (unresolved)** | −0.114 [−0.293, +0.066] (14) TIED |
| c2-HP-L | +0.056 [−0.024, +0.135] | no | −0.194 [−0.328, −0.059] (13; 0) | SPEED LEADS | **not PAYS (prize)** | −0.156 [−0.267, −0.045] (14) SPEED LEADS |
| c1-HP-G | +1.013 [+0.486, +1.540] | yes | +0.222 [−0.321, +0.765] (10; 0) | TIED, UNRESOLVED | **not PAYS (unresolved)** | +0.433 [−0.062, +0.928] (15) TIED |
| c2-HP-G | +0.717 [+0.340, +1.094] | yes | −0.052 [−0.336, +0.233] (11; 0) | TIED, UNRESOLVED | **not PAYS (unresolved)** | +0.048 [−0.217, +0.314] (11) TIED |
| c1-PW-L | +0.087 [+0.040, +0.135] | yes | −0.328 [−0.622, −0.034] (6; 0) | SPEED LEADS | **not PAYS (SPEED LEADS)** | −0.348 [−0.551, −0.145] (10) SPEED LEADS |
| c2-PW-L | +0.071 [+0.007, +0.136] | yes | −0.135 [−0.326, +0.055] (6; 0) | TIED, UNRESOLVED | **not PAYS (unresolved)** | −0.153 [−0.324, +0.019] (10) TIED |
| c1-PW-G | +0.580 [+0.304, +0.857] | yes | −0.013 [−0.340, +0.315] (8; 0) | TIED, UNRESOLVED | **not PAYS (unresolved)** | +0.223 [−0.143, +0.589] (11) TIED |
| c2-PW-G | +0.500 [+0.315, +0.686] | yes | +0.029 [−0.366, +0.424] (8; 0) | TIED, UNRESOLVED | **not PAYS (unresolved)** | −0.030 [−0.387, +0.327] (9) TIED |

**The r line and the descriptive columns beside it (w3).** None of these decides a verdict.
- **r (median)** is the registered r: its mean over hosts, [t 95%], and range.
- **Mean r** is the mean over hosts of the ratio-of-means r.
- **Max kept path** is the largest non-exploded per-season path speed, in m/s, in the speed arm and the base arm.
- **Cross 1.10** counts the hosts whose median r and mean r fall on opposite sides of 1.10.
- **The raw line** is the nose step minus the raw speed step.

| cell | r (median) (range) | in at r ≥ 1.10 | per-unit speed step | mean r | max kept path | cross 1.10 | raw line (n) |
|---|---|---|---|---|---|---|---|
| c1-U-L | 1.163 [1.083, 1.244] (0.90–1.37) | 10 of 14 | +0.164 [+0.047, +0.281] | 1.211 | 1.95 / 1.58 | 3 | −0.155 [−0.284, −0.026] SPEED LEADS (14) |
| c2-U-L | 1.181 [1.015, 1.347] (0.89–2.05) | 9 of 14 | −0.029 [−0.148, +0.089] | 1.137 | 2.79 / 5.02 | 1 | −0.088 [−0.163, −0.013] SPEED LEADS (14) |
| c1-U-G | 1.166 [1.113, 1.218] (1.05–1.40) | 11 of 15 | +0.308 [+0.145, +0.470] | 1.194 | 1.89 / 4.94 | 5 | −0.075 [−0.204, +0.054] TIED (15) |
| c2-U-G | 1.114 [1.077, 1.151] (0.97–1.21) | 10 of 15 | +0.259 [+0.060, +0.459] | 1.147 | 2.72 / 3.33 | 6 | −0.019 [−0.118, +0.081] TIED (15) |
| c1-HP-L | 1.217 [1.137, 1.296] (0.89–1.48) | 12 of 15 | +0.180 [−0.026, +0.386] | 1.239 | 4.67 / 1.74 | 2 | −0.186 [−0.383, +0.011] TIED (15) |
| c2-HP-L | 1.208 [1.135, 1.281] (0.87–1.43) | 13 of 15 | +0.211 [+0.077, +0.345] | 1.217 | 4.67 / 1.74 | 1 | −0.172 [−0.269, −0.076] SPEED LEADS (15) |
| c1-HP-G | 1.117 [1.037, 1.197] (0.82–1.34) | 10 of 15 | +0.243 [−0.083, +0.569] | 1.185 | 4.36 / 3.33 | 5 | +0.465 [+0.084, +0.845] NOSE LEADS (15) |
| c2-HP-G | 1.117 [1.062, 1.171] (0.92–1.33) | 11 of 15 | +0.282 [+0.056, +0.508] | 1.154 | 2.28 / 4.50 | 6 | +0.122 [−0.051, +0.296] TIED (15) |
| c1-PW-L | 1.099 [1.047, 1.151] (0.98–1.29) | 6 of 14 | +0.306 [+0.007, +0.604] | 1.155 | 3.63 / 3.88 | 4 | −0.170 [−0.305, −0.035] SPEED LEADS (14) |
| c2-PW-L | 1.097 [1.047, 1.148] (0.96–1.26) | 6 of 14 | +0.193 [−0.002, +0.388] | 1.142 | 3.30 / 3.88 | 4 | −0.048 [−0.153, +0.057] TIED (14) |
| c1-PW-G | 1.120 [1.050, 1.191] (0.89–1.40) | 8 of 15 | +0.143 [−0.237, +0.523] | 1.157 | 4.15 / 7.09 | 3 | +0.187 [−0.019, +0.393] TIED (15) |
| c2-PW-G | 1.100 [1.065, 1.135] (1.01–1.25) | 8 of 15 | +0.052 [−0.285, +0.390] | 1.136 | 2.75 / 2.33 | 3 | +0.122 [−0.037, +0.281] TIED (15) |

- The crossing hosts are named in `steps2_readout.txt` §2. **Membership in the per-unit line depends on the median r
  choice for 1 to 6 hosts per cell.** The #475 ruling fixed the median, and the mean r is descriptive only.
- The max kept path speeds are all under 7.1 m/s. In the first leg a single exploded season moved at 52,340 m/s.
- The raw line reads NOSE LEADS at c1-HP-G, while the registered line there is TIED. It is descriptive and decides
  nothing.

**The steps themselves** (items, t 95%, all hosts in; `steps2_readout.txt` §3):
- **At all six G cells the nose step w3 → 3.4 pays on its own, with a lower bound > 0:**

  | cell | nose step w3 → 3.4 |
  |---|---|
  | c1-HP-G | +0.464 [+0.162, +0.766] |
  | c2-HP-G | +0.277 [+0.118, +0.436] |
  | c1-PW-G | +0.253 [+0.090, +0.417] |
  | c2-PW-G | +0.174 [+0.053, +0.295] |
  | c1-U-G | +0.132 [+0.042, +0.222] |
  | c2-U-G | +0.083 [+0.008, +0.158] |

  At c1-U-G and c2-U-G the raw speed step pays too, with a lower bound > 0 (+0.206 and +0.102).
- **At the s = L cells the nose step's interval covers 0,** except at c2-U-L, where it is −0.050 [−0.086, −0.014].
- **The per-unit speed step's interval covers 0** at c1-PW-G, c2-PW-G, c1-HP-G, c2-U-L, c1-HP-L and c2-PW-L. So at the
  PW-G and c1-HP-G cells a nose step that pays sits against a speed step that is not resolved, and the difference is
  TIED because the per-unit speed step is wide (95% half-widths of 0.33 to 0.38) on 8 to 10 hosts.
- **No NOSE LEADS on the registered line,** so the "lead carried by the speed step" flag does not arise.
- **The first-nose and w 1 → 1.4 per-unit lines** read SPEED LEADS or TIED at every cell.

## 3. Robustness: leave one host out (`steps2_readout.txt` §4)

- **The method.** Under `--exclude-exploded` the per-host table gives each arm's mean over its own non-exploded seeds,
  not the per-comparison pairs. So the per-host per-unit values were reconstructed from it, and checked against each
  cell's `STEP` line with the tolerance fixed pre-data (0.01 on every figure).
- **Reconstructable at 4 cells:** c2-U-L, c1-U-G, c2-U-G and c1-HP-L.
  - c1-U-G and c1-HP-L stay TIED under every single omission.
  - c2-U-G reaches TIED under 7 of its 10 omissions. Its SPEED LEADS is fragile, but the verdict is not PAYS either
    way.
  - c2-U-L goes between COMPARABLE and TIED. Its verdict is fixed by the prize.
  - **So no verdict flips at these 4 cells.**
- **Not reconstructable at 8 cells.** There the reconstruction misses the registered interval by 0.012 to 0.071 on its
  worst figure, the effect of pairing. No FRAGILE flag is given or withheld there. For a PAYS, a single omission would have to lift a lower
  bound above 0, or shrink a 90% interval inside ±0.10. The registered lower bounds are −0.321, −0.336, −0.340 and
  −0.366 at c1-HP-G, c2-HP-G, c1-PW-G and c2-PW-G, so that looks unlikely, but it is **not shown**.

## 4. Caveats

- **"not PAYS (unresolved)" at 8 cells is a power result.** A1.4 said that the expected reading is TIED, UNRESOLVED
  unless one step leads by about 0.17 or more. It must not be read as "the nose step does not pay" in those worlds:
  at every G cell the nose step alone pays (§2).
- **The lines are thin at PW:** 6 to 8 hosts. The r ≥ 1.10 filter removes 6 to 8 hosts there, because the median r at
  PW sits near 1.10 (1.097–1.120). **At PW this filter, not explosions, decides who is in the line.**
- **Median r against mean r.** For 1 to 6 hosts per cell, whether the host enters the line depends on the ruled median
  r. The mean-r version is not computed as a verdict.
- **The prize is not re-measured.** The steps now run on seeds 126000–126127, and the prize still runs on #467's.
  c2-U-L and c2-HP-L fail on #467's prize lower bound alone. #467's lower bound is ≤ 0 at c2-U-L (−0.015) and c2-HP-L
  (−0.024); the ruling's "the prize condition stands at all 18 cells" validates the prize measurement, not LB > 0 at
  every cell.
- **Carried from #467:**
  - pre-fairness hosts (#443, S3);
  - no decoy at U and HP, including the c0-HP-G PAYS;
  - no multiplicity correction (none is registered): 12 cells re-read, 18 in all.
- **Explosions no longer drive r.** They are 0.2–0.6% of arm-seasons, and no host is out for them. The re-measurement
  removed the contamination the #467 ruling named.
