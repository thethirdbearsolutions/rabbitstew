# RBT-134b readout: the registered run at `MASTER_SEED 20260912`

**Status.** This is the registered readout of RBT-134b (DESIGN-134b.md §9 step 5), written by the readout session.
It reports the scripted outputs as they stand. Nothing was re-run, and nothing computed here changes a call.

**Sources.**
- **Registered run.** `claude/rbt134b-runs` @ `a075fcaa`, outputs under `runs/RBT-134/out/134b-20260912/`. They were
  written at the registration merge `92798b32` (every `.head` file records that sha).
- **Lane B.** `claude/rbt134-runs-B` @ `321710ee`, outputs under `runs/RBT-134/out/`, written at r3 GO `0ad0afae`.
- **Authorisation.** The run was registered by #580 → `92798b32`. The owner's first-hand GO is
  OWNER-DECISIONS-2026-10-10 item 11 (#584 → `d5cf0c69`).

**How numbers are cited.**
- `R:n` is line n of `readout.txt`, and `RC:n` is line n of `readout-controls.txt`.
- Lane B files are cited as `file:n`.
- Every call below is the script's own.
- §10 holds anything the scripts do not print. It is marked **descriptive** and changes no call.

---

## 0. Summary

| item | registered result | cite |
|---|---|---|
| control gate | VOID `none`; the checks and family ran | RC:99–101 |
| controls I2, I3, I4, I5-S, I9, B0 r3 prefix | all YES / PASS | R:202–226 |
| **P3** (Holm step 1, α 0.025) | **NULL**: k a32 = 4, p = 0.0625 | R:230 |
| **P2** (Holm step 2, α 0.05) | **NULL**: k a32 = 2, p = 0.25 | R:231 |
| family | **no PASS**, and both are NULL. This is DESIGN.md §10's "all NULL" case | R:228–231 |
| checks A0, P1, P4, P5 | each within its bound or ceiling | R:5–12, R:209–214 |
| EXCLUSION-FLAG | set on **P5** only; neither P2 nor P3 is flagged | R:12, R:9–10 |
| VOID | `none` | R:233–235 |
| lane B unseal | E1 B0 = parity YES; E2 B0 = RBT-112 tables YES; H1 read | §6 |
| cost | about 12.3 CPU-h of the 30 CPU-h cap | §9 |

---

## 1. Integrity of the outputs

Before reading, the 24 relayed SHA256 values were checked against the files committed on `claude/rbt134b-runs` @
`a075fcaa`.

- **23 of 24 matched byte for byte**: every JSON, every `*-resign.txt`, `cpu-ledger.jsonl`, `readout-controls.txt`
  and `readout.txt`.
- **`lane-134b.log` matched as a prefix.**
  - The committed log is 4,410 bytes (sha256 `a53bcd77…24d5`).
  - Those bytes are the first 4,410 of the relayed 4,617-byte local log (`e344da1d…ec78`). This is the runner's check
    on the run host, relayed by the coordinator.
  - **The mechanism.** `common.sh` `commit_outputs` (l.129–140) copies the log into the output worktree. It then
    appends the git commit and push output to the *local* log. The RELAY hashes that local log afterwards
    (`lane134b.sh` l.162–163: commit, then `relay done`).
  - The 207 extra bytes are that git output.
- **This changes no call.** The readout files, the run records and the ledger are byte-exact. The log carries no
  registered value.

The coordinator ruled that the readout proceed on this basis.

---

## 2. Controls and the gate

**The control gate.** `readout-controls.txt` was run over B0, C+L1 and A0 alone. Its VOID list is `none` (RC:99–101),
so the lane went on to the checks and the family. Its rows and controls equal the corresponding lines of the full
readout:
- the rows, RC:5–7 = R:5–7;
- the controls, RC:82–93 = R:202–203, 207–209, 215–217, 219–220, 225–226.

**Controls of the registered run.** These are DESIGN-134b.md §7's table. Any failure would VOID.

| id | requirement | readout | cite |
|---|---|---|---|
| I2 B0 | arrival set = RBT-91 baseline's 84, responses line for line | YES; YES | R:202 |
| I2 A0 | arrival set = baseline's 84 | YES | R:203 |
| I2 P1 | = RBT-91-alone-1.6's 63 | YES | R:204 |
| I2 P2, P3 | = RBT-91-alone-4.0's 66 | YES, YES | R:205–206 |
| I2 (E1 stream identity, P1–P4, both faunas) | E1 equal to the default | `(= B0)` on every P1–P4 row | `e1.txt:11–18` |
| I3 slope bound | 0 violations, every condition | 0 for B0, C+L1, A0, P1, P2, P3, P4, P5 | R:207–214 |
| I3 bounds | A0 k ≤ 0; P1 ≤ 2; P2, P3 ≤ 29 | 0 ≤ 0, 0 ≤ 2, 2 ≤ 29, 4 ≤ 29: YES | R:209–212 |
| B0 r3 background prefix | all **26 of 9,996**; unflagged **22 of 9,990** | 26 of 9996: YES; 22 of 9990: YES | R:215–216 |
| **I4** (C+ = C+L1 PASSes) | McNemar p ≤ 0.025, k ≥ 6, clause HOLDS | k a32 51, 51 up / 0 down, p = 4.441e-16; never-structured 135/39905 vs B0 135/39944, ratio upper bound 1.222: **PASS** | R:226 |
| **I9** | never-structured background remnant-proof, C+L1 and P5 | YES, YES | R:217–218 |
| **I5-S** B0 | cited: the diagnosis's EXACT swap at `MASTER_SEED` | YES | R:219 |
| **I5-S** A0, P1–P4 | swapped food = sham, and swapped sham = food | YES ×5 | R:220–224 |
| I6 | no `sign`-flipped probe counted | no I6 line is printed. Each §3 table states the arrivals excluded whole for a flagged unit: 0 everywhere except C+L1's 4 | R:18, 41, 64, 87, 110, 133, 156, 179 |
| VOID | — | `none` | R:233–235 |

U2 is printed descriptively, as a property of the parents (DESIGN-134b.md §6.1): B0 food-only 84, sham-only 21,
two-sided exact p 4.157e-10 (R:225). That is the parents' food/agent asymmetry, as the diagnosis's I5-A token said.
It is not a control.

I1 (pairing) and I7 (byte identity when off) are code properties, tested at registration. The readout prints no line
for them.

---

## 3. The family: Holm m = 2, the background clause and the verdicts

The registered rule (DESIGN.md §4, §6; background DESIGN-134b.md §4.1):
- **The test.** McNemar against B0, one-sided p = 0.5^k.
- **Holm** over P2 and P3 at α = 0.05: the smaller p is tested first at 0.025, then the other at 0.05.
- **The clause** HOLDS iff the one-sided 95% Katz upper bound on the never-structured ratio is ≤ 2.

| step | condition | k a32 [Wilson 95%, per 200,000] | discordant | p | α | never-structured bg vs B0 | ratio upper bound | verdict | r3 measure (descriptive) | cite |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **P3** | 4 [1.56, 10.29] | 4 up / 0 down | 0.0625 | 0.0250 | 978/39784 vs 135/39944 | 8.456 | **NULL** | 8.446, fails | R:133, R:230 |
| 2 | **P2** | 2 [0.55, 7.29] | 2 up / 0 down | 0.25 | 0.0500 | 885/39785 vs 135/39944 | 7.659 | **NULL** | 7.647, fails | R:110, R:231 |

**Neither primary rejects**, so both verdicts are NULL, with the background reported, as DESIGN.md §4's verdict table
requires.
- Neither k reaches the first Holm step's k ≥ 6.
- Both backgrounds would fail the clause: their upper bounds are 7.659 and 8.456 against 2. The clause does not enter
  a NULL verdict, so it does not decide either call here.

**What the result says** (DESIGN.md §10, scoped). This is the **"all NULL"** case, not "moves only with background".
DESIGN.md §10 registered this statement:

> "At depth 19, on these pools, a link step decoupled from the bias step at 4.0 — with the default bias walk, or with
> biases reset to N(0, 0.5) at rate 0.2 — does not make drift propose routed motifs whose own links reach the a = 32
> rung without raising the structureless background above 2×."

(For 134b the "structureless background" in that statement is the never-structured measure; DESIGN-134b.md §10.)

On this run the slopes bind even with wide links: k stays below the Holm threshold for both switches. The statement
is for these two switches at these values only.

**E3 is not run.** DESIGN.md §8 E3: "If both P2 and P3 are NULL, E3 is not run."

---

## 4. The checks (outside the family)

| check | bound or ceiling (DESIGN.md §2.2) | k a32 | held | cite |
|---|---|---|---|---|
| A0 | 0 at every own-link rung | 0; a16/a32/a64 all 0 on "as is" | yes | R:64, R:72, R:209 |
| P1 | ≤ 2 | 0 | yes | R:87, R:210 |
| P4 | ceiling: k ≥ 6 would be a ceiling failure (expected ≤ 2.96) | 0 | yes | R:156 |
| P5 | ceiling: k ≥ 6 would be a ceiling failure (expected ≈ 0.01) | 0 | yes | R:179 |

---

## 5. The background clause, I9, I5-S and the EXCLUSION-FLAG

### 5.1 The background, per condition (R:3–12)

| condition | arrivals | k a32 | planted | remnants (ever, not final) | bg never-structured (134b) | bg structureless at 19 (r3, descriptive) | remnant share over B0's / threshold | pair events (refused / no pair) | cite |
|---|---|---|---|---|---|---|---|---|---|
| B0 | 84 | 0 | 0 | 16 | 135/39944 | 136/39960 | +0.00000 / 0.00338 | 0 | R:5 |
| C+L1 | 200 | 51 | 197 | 33 | 135/39905 | 138/39938 | +0.00043 / 0.00338 | 199 (1 / 0) | R:6 |
| A0 | 84 | 0 | 0 | 16 | 158/39937 | 159/39953 | +0.00000 / 0.00338 | 0 | R:7 |
| P1 | 63 | 0 | 0 | 24 | 718/39842 | 727/39865 | +0.00018 / 0.00338 | 0 | R:8 |
| P2 | 66 | 2 | 0 | 28 | 885/39785 | 891/39813 | +0.00030 / 0.00338 | 0 | R:9 |
| P3 | 66 | 4 | 0 | 28 | 978/39784 | 985/39811 | +0.00028 / 0.00338 | 0 | R:10 |
| P4 | 73 | 0 | 0 | 17 | 364/39903 | 365/39920 | +0.00003 / 0.00338 | 0 | R:11 |
| P5 | 7433 | 0 | 18095 | 2176 | 123/36280 | 134/38455 | +0.05402 / 0.00338 **EXCLUSION-FLAG** | 19070 (182 / 0) | R:12 |

**The background clause.**
- The clause is applied by the readout only to C+ (I4b) and the family.
- **C+L1: HOLDS**, with a ratio upper bound of 1.222 (R:226).
- **P2 and P3** would fail it, at 7.659 and 8.456 (R:230–231). That does not enter their NULL verdicts (§3).
- **B0's r3-measure continuity control** reproduces exactly: 26 of 9,996 and 22 of 9,990 (R:215–216).

**I9.** YES on C+L1 and P5 (R:217–218).
- (Descriptive) C+L1's never-structured background is 135, the same count as B0's (R:6 vs R:5), on 39 fewer
  lineages: its planted lineages are removed.
- C+L1 planted 197 lineages and made 33 remnants (R:6). §10 compares these with the priced figures.

**I5-S (DESIGN-134b.md §6.2, row I5-A).**
- The diagnosis's token was I5-A, so I5-S is the registered form for the sensor-blind conditions.
- B0's swap is cited, EXACT (R:219).
- A0, P1, P2, P3 and P4 each hold the swap identity lineage by lineage (R:220–224).
- U2 is reported descriptively as the parents' asymmetry (R:225).
- C+L1 and P5 are not sensor-blind and have no swap. I9 (c) covers their sham sets on unplanted lineages.

### 5.2 The EXCLUSION-FLAG (DESIGN-134b.md §4.6)

- **P5 is flagged.** Its remnant share over B0's is +0.05402, against the threshold x₀/n₀ = 0.00338 (R:12). P5 is a
  check, not a family member, and its k is 0 (R:179). So the flag sits beside no family or C+ verdict.
- **Not flagged:** C+L1 (+0.00043), P1, **P2 (+0.00030)**, **P3 (+0.00028)**, P4 and A0 (R:6–11).
- So no family verdict could have been carried by the exclusion. The r3-measure bounds printed beside P2 and P3 are
  7.647 and 8.446 (R:230–231). (Descriptive: both are within 0.013 of their 134b bounds and on the same side of 2.)

The flag is descriptive. It changes no verdict.

---

## 6. Lane B, unsealed (DESIGN-134b.md §7, §9 step 4)

This session read lane B's committed outputs **after** the owner's GO for the registered run (OD item 11). It read
them **before** opening `readout-controls.txt` or `readout.txt`.
- Source: `claude/rbt134-runs-B` @ `321710ee`. Every `.head` file records r3 GO `0ad0afae`.
- Nothing was re-run.
- The two RELAY tokens were recomputed read-only, with lane B's own `relay.py` checkers (`e1_b0_matches`,
  `e2_b0_matches`), on the committed files.

**E1** (`e1.txt`).
- **The B0 token.** `E1-B0-equals-parity.txt`: **YES**. B0 holistic reads 0.9162 / 48.1% / 625 / 8.98%, and
  conventional reads 0.9839 / 31.0% / 4000 / 0.00% (`e1.txt:5–6`). These are `runs/RBT-121/ga/parity.txt`'s values.
- **P1–P4.** Every row reads `(= B0)` in both faunas (`e1.txt:11–18`). That is the I2 stream identity DESIGN.md §9
  requires.
- **A0** reads `(= B0)` in both faunas (`e1.txt:9–10`).
- **P5's conventional row reads `(differs from B0)`** (`e1.txt:20`). This is expected: P5 adds links (DESIGN.md §8 E1).
  It is not under I2.
- **C+'s conventional row** also reads `(differs from B0)` (`e1.txt:8`). That row is **r3's C+ at rate 0.005**, not
  134b's C+L1. DESIGN-134b.md §7 says it is not a 134b item and is read as r3's.

**E2** (`e2-summary-*.txt`).
- **The B0 token.** `E2-B0-equals-RBT-112-tables`: **YES**.
- The registered reading is that u(8) ≤ 0.5 is a cost, never a veto. No condition exceeds 0.5, so none reads
  "proposes but cannot keep".

| condition | pooled u(8) on pay32 | per-seed mean [t(9) 95%] | cite |
|---|---|---|---|
| A0 | 0.079 | +0.079 [+0.076, +0.082] | `e2-summary-A0.txt:1–2` |
| P1 | 0.313 | +0.315 [+0.303, +0.326] | `e2-summary-P1.txt:1–2` |
| P2 | 0.314 | +0.316 [+0.303, +0.329] | `e2-summary-P2.txt:1–2` |
| P3 | 0.315 | +0.316 [+0.303, +0.329] | `e2-summary-P3.txt:1–2` |
| P4 | 0.292 | +0.293 [+0.283, +0.302] | `e2-summary-P4.txt:1–2` |
| P5 | 0.280 | +0.281 [+0.274, +0.288] | `e2-summary-P5.txt:1–2` |

The reference values are the default 0.282 and `global_bias_sigma 0` at 0.089 (`runs/RBT-112/erasure.txt:25`).

**H1** (`h1-readout.txt`).

| condition | arm G [Wilson 95%, per 200,000] | arm I [Wilson 95%] | cite |
|---|---|---|---|
| B0 | 20 [12.9, 30.9] | 6100 [5951.1, 6252.5] | `h1-readout.txt:5` |
| A0 | 20 [12.9, 30.9] | 6100 | `:6` |
| P1 | 17 [10.6, 27.2] | 6100 | `:7` |
| P2 | 17 [10.6, 27.2] | 6100 | `:8` |
| P3 | 17 [10.6, 27.2] | 6100 | `:9` |
| P4 | 21 [13.7, 32.1] | 6100 | `:10` |

- **Totals.** Arm G has 112 arrivals and arm I 36,600 in total (`h1-readout.txt:12, 14`). Both lines read "H2 runs
  for it".
- **H2 stays gated** (LAUNCH.md, "Gated, not run by these lanes"). It waits for a committed W1 battery
  (DESIGN.md §5.3). I8 belongs to H2 and is not read here.

---

## 7. C−'s sealed held-out counts (DESIGN-134b.md §4.4)

The registered readout does **not** print them: `readout.txt` has no C− line.
- §4.4 says they "may be printed" here. The design does not require it.
- C−'s JSON remains on `claude/rbt134b-validation`. This session neither fetched nor read that branch.
- The validation's REGISTER verdict tells us one thing: C− failed clearly on both held-out seeds, because otherwise
  the §5.3 outcome table's first row (ESCALATE) would have matched.

The held-out seeds are never pooled with this run (§5.3), and nothing here does so.

---

## 8. Predictions scorecard (DESIGN-134b.md §10, with DESIGN.md §10 for the checks)

### 8.1 Validation (DESIGN-134b.md §10)

These are scored only from the verdict line registered in `REGISTRATION-134b.md` §1:
`REGISTER C+ = C+L1 (…)`.
- This session read no held-out output.
- Under §5.3 that line implies:
  - neither seed matched the ESCALATE row, so C− failed clearly, I5-S B0 held and there was no VOID on either seed;
  - L1 was ACCEPTED on both seeds, which includes I9.

| id | prediction | credence | outcome |
|---|---|---|---|
| V1 | REGISTER C+ = C+L1 | 0.7 | **held** |
| V1′ | REGISTER some rung | 0.8 | **held** |
| V2 | C− fails clearly on both seeds | 0.9 | **held** (implied by REGISTER) |
| V3 | I9 holds for every C+ rung run | 0.97 | **held** (only L1 ran; ACCEPTED needs I9). Also YES at `MASTER_SEED` (R:217) |
| V4 | I5-S B0 holds on both seeds | 0.97 | **held** (implied by REGISTER) |
| V5 | B0's never-structured background within sampling of r3's 22/9,990 on both held-out seeds | 0.85 | **not scored here**: the held-out B0 counts are on `claude/rbt134b-validation`, not read |

### 8.2 The family, restated for the never-structured measure (DESIGN-134b.md §10)

| id | prediction | credence | outcome | cite |
|---|---|---|---|---|
| P2-b | NULL: k < 6 | 0.55 | **held**: k = 2, NULL | R:231 |
| P2-bg | P2's never-structured ratio ≥ 2 (point estimate) | 0.75 | **held**: point ratio about 6.6 (arithmetic on R:9 and R:5; see §10). The upper bound is 7.659 | R:231 |
| P3-b | MOVES-WITH-BACKGROUND: k ≥ 6, clause fails | 0.40 | **wrong**: k = 4, **NULL**, the 0.48 branch. The registered reading for NULL is that "the reset's N(0, 0.5) leaves f(b_k) too large against v ≈ 4.5". The background would have failed (8.456) | R:230 |
| flag | neither P2 nor P3 carries the EXCLUSION-FLAG | 0.8 | **held** | R:9–10 |
| family-b | no PASS | 0.85 | **held** | R:230–231 |

### 8.3 The checks and H1 (DESIGN.md §10, carried over)

| id | prediction | credence | outcome | cite |
|---|---|---|---|---|
| A0 | k = 0 (bound) | 1.0 | **held** | R:64, R:209 |
| P1 | k ≤ 2; background above B0's, about RBT-91's coupled 1.41% or higher | 1.0 / 0.7 | k: **held** (0). Background: **held**, 718/39842 against B0's 135/39944, about 1.8% (§10) | R:8, R:210 |
| P4 | k ≤ 2 (ceiling 2.96); background up | 0.95 | **held**: k = 0; 364/39903 against 135/39944 | R:11, R:156 |
| P5 | k ≤ 1 (ceiling 0.01), with arrivals up about 200× | 0.99 | **partly wrong**. k: **held** (0). Arrivals clause: **wrong** (88× against about 200×: 7,433 against B0's 84, §10). DESIGN.md:648 | R:12, R:179 |
| holistic H1 | arm G near 0; arm I non-zero under B0 | 0.6 | arm I: **held** (6100). Arm G: **not scorable as registered** (20 [12.9, 30.9] per 200,000 reported; "near 0" was given no number) | `h1-readout.txt:5` |

DESIGN.md §10's P2, P3 and family rows are replaced for 134b by §8.2's (DESIGN-134b.md §10).

---

## 9. Re-signing and cost

### 9.1 Re-signing (registered secondary)

The re-signing ran after the aggregate check `re-signing check: within the cap` (`lane-134b.log:30`). The cap was 400
per condition. A0 is not re-signed (OD item 8).

| condition | compasses | anti | undetermined | of | cite |
|---|---|---|---|---|---|
| B0 | 0 | 0 | 0 | 0 | `B0-resign.txt:7` |
| C+L1 | 30 | 28 | 2 | 60 | `C+L1-resign.txt` (last line) |
| P1 | 0 | 0 | 0 | 0 | `P1-resign.txt:7` |
| P2 | 2 | 3 | 0 | 5 | `P2-resign.txt:11` |
| P3 | 1 | 5 | 0 | 6 | `P3-resign.txt:12` |
| P4 | 0 | 0 | 0 | 0 | `P4-resign.txt:7` |
| P5 | 1 | 0 | 0 | 1 | `P5-resign.txt:7` |

Each "of" equals that condition's "as is" count at a16 in its §3 table: R:49, 95, 118, 141, 164, 187, and 0 for B0
at R:26. The compass count is reported, not tested (DESIGN.md §4).

### 9.2 Cost against the 30 CPU-h cap

This is the sum of `cpu-ledger.jsonl`'s `cpu_s`, plus the validation's registered `VALIDATION_SPENT_H = 4.6`. It is the
same quantity `assay.spent_134b` returns on the registered run's checkout. The sum is plain arithmetic on the ledger
and changes no call.

| item | ledger lines | CPU-h |
|---|---|---|
| assay, 8 conditions | 800 | 5.22 |
| I5-S swaps (A0, P1–P4) | 500 | 2.32 |
| re-signing (72 robots) | 72 | 0.12 |
| **registered run** | 1,372 | **7.67** |
| held-out validation (`VALIDATION_SPENT_H`) | — | 4.6 |
| **RBT-134b total** | | **≈ 12.3 of 30** |

- **No STOP-COST fired.** Every stage ran, and the lane exited 0 with status `done`.
- **No hand-entered lines.** The ledger has no `untracked` line.
- **What the ledger leaves out.** It records worker CPU per chunk. Process start-up is not counted, as DESIGN-134b.md
  §8 states.
- **Against the plan.** The total is well under DESIGN-134b.md §8's planning figures: base 21.8, and base plus the
  reserve 29.7.

---

## 10. Descriptive (not registered; changes no call)

Everything below is arithmetic on printed counts, or a reading the design did not register.

- **Point ratios on the never-structured measure** (each condition's x/n over B0's 135/39944, from R:5–12):
  - A0 1.17, P1 5.33, P2 6.58, P3 7.27, P4 2.70;
  - C+L1 1.00 and P5 1.00, where I9 makes each the unplanted subset of B0's background.
- **Background rates (never-structured):**
  - B0 0.338%, P1 1.80%, P2 2.22%, P3 2.46% and P4 0.91%;
  - RBT-91's coupled σ = 4.0 read 1.64% on r3's measure (DESIGN.md §9), against P2's 2.22% here on the
    never-structured measure. The measures and lineage windows differ, so this is not a test.
- **B0's background outside the registered prefix.** The 5,000-per-pool prefix reproduces 22 of 9,990 unflagged
  (R:216). On all 20,000 per pool, B0 reads 136/39960 on r3's measure and 135/39944 never-structured (R:5).
  - That is 0.34%, against the prefix's 0.22%. DESIGN-134b.md §1.2 priced against the prefix rate (about 88 per
    40,000).
  - The registered flag threshold and clause use the full-block count (R:5), so no call depends on the prefix rate.
  - The priced remnant shares in DESIGN-134b.md §3.2 are about 1.5× too high against the full-block rate. That only
    widens L1's margin.
- **C+L1 against its price.**
  - C+L1 has 17 excess remnants over B0 (33 − 16; excess share +0.00043 = 17/39,938) against about 12 priced
    (DESIGN-134b §3.2, L1 row). Sources: R:5, R:6.
  - The registered run planted 197 lineages (R:6). §3.2 priced 190 per 200,000 as an upper bound, ignoring
    refusals; 1 event was refused here.
  - k a32 = 51 (R:41) lies inside §3.2's priced E[k] range of 43 (w = 0.5) to 85 (w = 1).
  - The k ≥ 20 tuning bar is not part of I4 at `MASTER_SEED` (DESIGN-134b.md §7). k = 51 would clear it.
- **P2 and P3 share their arrivals** (66 each, the same per-parent arrival counts; R:113, R:136), as I2 requires.
  Their k a32 differ (2 against 4) only through the bias reset, because P3's matched null is P2 (DESIGN.md §9). This
  readout does not say which lineages those are.
- **The re-signing of P2 and P3** shows anti headings in the majority (3 of 5, 5 of 6). Those counts are too small to
  read, and the compass count is not tested.

---

## 11. Files

- `runs/RBT-134/READOUT-134b.md`: this document.

Neither REGISTRATION-134b.md nor LAUNCH.md asks for the scripted readout files to be copied here. They stay on
`claude/rbt134b-runs` (`readout.txt` sha256 `59cd9032…0f33`; `readout-controls.txt` `a53efe09…560c`).
