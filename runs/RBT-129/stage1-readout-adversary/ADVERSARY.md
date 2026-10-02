# RBT-129 Stage 1 readout plan (#512 at e83ef23): adversary report

*PR #512, head `e83ef2355e35241ca03ef515c8b1ff40b9898ce3`, base `claude/new-session-4cao7d` at `9edecbd`. The plan-only
first commit is `a250b72`. I read the registered and ruled texts, the lane files (job lines only), the M/N launch
record and gate table, the committed census readout, and source code. **No `ckpt/rbt-129-stage1-*` branch was
fetched, checked out, restored or read, and no Stage-1 output was opened. `stage1_readout.py` was never run against
real data.** The quarantined branch was not touched. Every probe below runs on synthetic values or on registered
inputs:*

- *`counts.py` → `counts.txt`: the integrity counts, from the lane files, without `stages.py` or the plan's script;*
- *`probe.py` → `probe.txt`: imports the plan's script and `power.py`, and calls single functions on made-up values.*

*Test run: a clean venv (`python -m venv /tmp/v && /tmp/v/bin/pip install -e ".[dev]"`, no scipy), then
`/tmp/v/bin/python -m pytest -q` on the head: **972 passed, 1 skipped** (16 min). The plan's own file,
`tests/test_rbt129_stage1_readout.py`, has 62 passed.*

## Verdict: **ADOPT AFTER FIXES**

| item | count |
|---|---|
| MUST | 5 |
| SHOULD | 9 |
| NOTE | 15 |

**What holds.**
- The integrity counts reproduce exactly (§5 below): 973 labels, 973 markers, 613 `platform.json`, 37 loaded forks
  plus 1 CRASHED, which makes 38.
- The crash ruling (r3) is quoted verbatim. The quoted text is byte-identical to `mn-crash/RULING.md` from `## Ruling`
  to the adversary record, at blob `69b2c50`. Items 1–7 are all placed in the plan.
- The quarantine refusal fires on every reader path the script has.
- The `--go` guard works.
- The claim that no share call is reachable at Stage 1 is right. Its wording needs one correction (NOTE 1).
- Most OPEN resolutions are defensible and were made before data.

**What blocks adoption.**
- **RESOLVING is computed wrongly, twice** (MUST 1).
- **The readout's computing layer is not committed.** Too much is left for the readout session (MUST 2).
- **M2/T1 has no rule for an inestimable design.** The registered gate table makes that outcome likely (MUST 3).
- **Two readings in the §8 logic flip the headline verdict.** One of them is not listed as OPEN (MUST 4).
- **O-18 changes what R-B spends.** It needs an explicit, labelled ruling and two missing pins (MUST 5).

## 1. Pre-data discipline

| check | finding |
|---|---|
| Order | `a250b72` (19:26:49Z) holds only the plan. `31c595e` and `49ea8b5` (19:28:34Z) and `e83ef23` (19:41:59Z) follow. The plan's diff after `a250b72` is 22+/8−: O-22, names, the driver's scope, and O-1 cited. No rule moved toward a known outcome |
| Inputs the plan says it read | All registered or ruled. The gate table's valid-seed counts were seen at emission (mn-emitter ruling item 7), and the plan says so (§0, §2.7) |
| Data-informed choices | **O-18** was made knowing, from the gate table, that the literal R-B list is empty (MUST 5). Nothing else depends on the gate table except the §0 statements |
| Git evidence | Git cannot show when a branch was first fetched. "No Stage-1 branch opened" rests on the author's statement, as in every prior plan |

## 2. Fidelity (registered text against the plan)

Each line is a departure, or a place where the registered text is ambiguous and the plan has chosen a reading. Items
that match exactly are not listed. These include:
- the per-point statistics (DESIGN §6.1, lines 627–637);
- the margins;
- the body-call order (lines 644–668), with T6's thresholds;
- the families (§7.1, lines 868–877);
- the BH step-up;
- Holm with T4 entered at p = 1 (a valid lower bound on the final rejections);
- M2's term list (§7.2, lines 895–907);
- the verdict terms (§8, lines 948–958);
- the claim label (T4).

| # | registered | plan / script | severity |
|---|---|---|---|
| F1 | §4.1, lines 343–345, and §10.1's last bullet (line 1116): the replica's drift SD **is scaled by the pilot's estimate**, and "the gate and the checks are rescaled by it". #500 item 2 exempts **the gate** only. `pilot_constants.json`: `y_scale` 1.5297 | `resolving()` calls `power.resolvable` with `Y_SCALE` left at 1.0. `load_pilot` is never called | MUST 1 |
| F2 | §6.2: RESOLVING iff the check passes at both bounds | `bool(resolvable(...))` on a `(rows, passes)` tuple is always True (probe P1) | MUST 1 |
| F3 | §8, lines 962–976: verdicts 1, 2 and 5 count EARNS calls with no habitability restriction. Only verdict 3's **denominator** is "the habitable points" | `verdicts()` drops every EARNS call at a non-habitable point (plan §4.3 and §9). This is **not in the OPEN table**. Probe P7: EARNINGS DEPEND becomes DEPENDS ONLY THROUGH HABITABILITY | MUST 4 |
| F4 | §8, line 948: "a **decided income call** is EARNS-H, EARNS-D or EARNS-TIE"; verdict 5, line 974: "every decided EARNS call favours one fauna X" | O-20b: EARNS-TIE is ignored. Probe P6: 1 EARNS-H among 20 EARNS-TIE gives verdict 5 ahead of WORLD-INVARIANT | MUST 4 |
| F5 | §4.2, line 371: R-B takes "every point whose **body call** is UNDECIDED or CONTINGENT" | O-18 adds NOT RUN points with an income UNDECIDED, and the code also adds "RBT-118 (not available)" anchors (probe P9) | MUST 5 |
| F6 | §6.1 item 6 (lines 654–662): σ̂²_null is "pooled **per kind**", and CONTINGENT is not callable at "a stage whose pooled **per-kind** df is below 12" | `pooled_null` sums df over both kinds into one σ̂². Probe P4: per-kind df of 12 and 1 gives 13, so callable | SHOULD 1 |
| F7 | §5.5 K2 per point: "the t test is not rejected under BH **and** \|mean y′_null\| ≤ 0.15" | At 1 run the plan reads UNTESTABLE and skips the size bar, although the bar is evaluable. Probe P3: y′_null = 0.40 is not VOID | SHOULD 2 |
| F8 | §4.2, line 365: C1 adds "**the pair flanking** each extra sign change"; §5.1 C1 (line 409): the rows "enter R-A's pair list" | The plan names one census point per sign change. 11 of its 18 C1 candidates are not R-A midpoints of any Stage-1 pair (probe P2), e.g. `c05-p018-HP-L`. This mapping is not in the OPEN table | SHOULD 4 |
| F9 | AMENDMENT-FOUNDING T3: at Stage-1 points, the census's holistic FOUNDING-FAIL layer and Stage 1's founding are "printed side by side" | Printed only at the 114 unrun points (§6 M1) | SHOULD 5 |
| F10 | §12: registered predictions, "'no' is a finding" | No scorecard. Only M2's signs and M3's p* are printed "beside" | SHOULD 6 |
| F11 | `mn-crash/RULING.md` item 4: s₀ is "read from S60 at readout time" | Read from the unit's `ckpt60`. That is correct: S60 writes `S`, whose latest snapshot is season 300, and `ckpt60` is the season-60 copy. It should be said | NOTE 2 |
| F12 | §5.3a and §6.2: the flow and g0 are over "living members" | O-3 includes the season's starved and aged rows. Defensible: they lived that season, and RBT-130 S1 added those rows for this purpose. The survivors-only variant is printed | OK (O-3) |

## 3. The OPEN items

| id | resolution | defensible? | outcome-blind? | verdict |
|---|---|---|---|---|
| O-1 | coordinator ruling, cited | n/a | DATA-INFORMED, as labelled | **accept**. The quote is relayed and cannot be checked from the repo: the go should confirm it (NOTE 13) |
| O-2 | K1 never on PW: qualify, VOID nothing | yes. §5.5 VOIDs only on a K1 **failure**, and K1 failed nowhere | yes | **accept** |
| O-3 | evaluated rows, starved and aged included, food − p·kJ | yes (F12). Variant (i) is not a variant (NOTE 3) | yes | **accept** |
| O-4 | y′ as registered (/120 window, living share at the merge) | it is the registered text | yes | **accept** |
| O-5 | per-birth income = `net_per_birth` + cost < 0.25 | yes. DESIGN §13 r3 item 4 ("…so the bar is strict. Should it be half the living cost?") only makes sense when the per-birth figure is gross of the living cost | yes | **accept**. Both are printed |
| O-6 | within-member SD | yes; not reachable at Stage 1 | yes | **accept** |
| O-7 | a K-SALT VOID seed is removed from n | yes. F7: "voids the point for the seed". Counting it as invalid would let a code fault make PARTIAL | yes | **accept** |
| O-8 | PARTIAL survivor by majority; PARTIAL-TIED otherwise | yes. PARTIAL-TIED is a new label, a survival call for neither. It feeds §8's survival sets, so its rule matters; it is pinned | yes | **accept** |
| O-9 | per-(point, kind) means removed; df = Σ(n − 1) | the mean removal matches r3's "(k × 4 − k) per kind". **The df and σ̂² are summed across kinds**, against "per kind" | yes | **fix** (SHOULD 1) |
| O-10 | anchors read "RBT-118 (not available)"; no block | yes | yes | **accept** |
| O-11 | income test at ≥ 2 income-valid seeds, at every point | yes for the **test**. But it carries an unlisted second resolution, "§8 counts EARNS only at habitable points", which is a verdict rule (F3) | test yes; §8 part not listed | **split, and list** (MUST 4) |
| O-12 | K2 pooled: \|mean\| < 0.05 **and** t not rejected | defensible. An equivalence reading (TOST at ±0.05) also exists, and it would VOID the stage's share layer far more often. No Stage-1 effect | yes | **accept for Stage 1**; rule before Stage 2 (NOTE 11) |
| O-13 | Wald χ²/z on the GLS covariance, no df correction | DESIGN names a Wald test and no df rule. Anti-conservative at about 30 groups; acceptable as pinned | yes | **accept** |
| O-14 | M3: per-row OLS of seed-level x on p, Fieller | it is the registered "line in p per row" | yes | **accept** |
| O-15 | R-A (b) on the pair's layer; "of the winner" means the winner is absent | yes. "EXCLUDED-X" names the extinct fauna and "PARTIAL-X" the survivor, so "of the winner" needs a reading, and this one marks a boundary | yes | **accept** |
| O-16 | "smell G first" as a block order | defensible. Consequence: L pairs refine only if fewer than 16 G pairs fire (NOTE 12) | yes | **accept** |
| O-17 | every sign change on a listed C1 row | defensible. **The point mapping behind it is not listed** (F8) | yes | **accept O-17; list the mapping** (SHOULD 4) |
| O-18 | income UNDECIDED at a NOT RUN point is R-B-eligible | **textually defensible**: §5.2 r4 says "at a NOT RUN point the body call falls to the income and survival layers"; §10 prices "income MDE80 … n = 16 (after R-B)"; and §11.2 budgets 2b at 20 points, which the literal rule could never fill under the gate. **But** the author chose it knowing the literal list is empty, it turns R-B from 0 points into up to 20 (≤ 413–473 core-h, §11.2), and the plan leaves the ranking layer and the anchors unpinned | outcome-blind as to income; **informed by the gate table** | **ruling required** (MUST 5) |
| O-19 | α = 0.05 (BH half), z from the t p-value | it matches §10's pricing at q/2. The formula checks: CP(t₁ = 0) = 2Φ(−√2·1.96) | yes | **accept** |
| O-20 | (a) verdict 3's "no counting set" pools across kinds | (a) yes. DESIGN's own parenthetical, "(at most one uncorroborated call)", is a pooled count | yes | **accept (a)** |
| O-20 | (b) verdict 5 ignores EARNS-TIE | (b) contradicts the defined term at line 948, and flips 5 against 6 (F4) | yes, but consequential | **rule, and print both** (MUST 4) |
| O-21 | c − 1, log(p/0.03); U, L reference | yes. T1 is invariant to this coding, and T2 and T3 then read at the committed world. The grid's geometric-mean price is 0.0289 | yes | **accept** |
| O-22 | an N point already settled by items 1–3 is in no share family | yes. It cannot take a call, and including it would only raise K for others. The share families are empty at Stage 1 | yes | **accept** |

**The claim "no share call is reachable at Stage 1".** It is correct.
- The 4 N points have 2, 2, 2 and 1 valid seeds (gate table). ⌈3n/4⌉ = 6, so item 1 or item 2 settles each of them
  before item 4.
- This still holds if K-SALT VOIDs shrink n: at n = 7 the PARTIAL bar is 6, and at n = 6 it is 5, while the valid
  counts are ≤ 2.
- The wording "each is PARTIAL" is too strong; see NOTE 1.
- A VOID body call is also unreachable at Stage 1. K1 failed nowhere, and K2 sits behind PARTIAL.

## 4. Missing degrees of freedom

These are what the plan leaves open for a readout author who has seen the data.

| # | what is open | where it bites | item |
|---|---|---|---|
| D1 | The whole `readout` assembly: which seeds feed each test; σ̂²_null and df by (point, kind); K2's inputs; the R-A and R-B `stats` dicts; the `corroborate` callable (which M3 row and fit); `m_arm`; the per-birth incomes (`regime.py` is never called); §3.6's SDs and zero-income share; M1, M4 and M7 tallies; BY marking; the census layer; the regime readout; the flow variants | every call and verdict | MUST 2 |
| D2 | M2 with a zero or constant world column, a singular X′H X, or too few habitable points; T2 and T3 if their term is dropped; Holm with a missing p (`holm()` raises on None) | T1, which gates verdicts 1, 2 and 6 | MUST 3 |
| D3 | An income-valid seed with no member-season for a fauna: `flow()` returns None, and `fh − fd` raises | the income layer | SHOULD 7 |
| D4 | A §3.2 cross-check mismatch (member-season rows against history) is "counted and printed", with no stop rule. Duplicated lineage rows bias the flow directly | the income layer | SHOULD 3 |
| D5 | The S-chain resume audit (`resumed-readout.txt`) is not read by the integrity verdict, so `INTEGRITY PASS` can print beside a listed double write | integrity | SHOULD 3 |
| D6 | No explicit statement that no seed or run is excluded, winsorised or re-weighted beyond K-SALT VOID, validity and CRASHED. The P+0 readout added a post-plan exclusion (P+0 adversary §1, item 1) | every layer | SHOULD 7 |
| D7 | Exploded rows are 0-food seasons: do they count in VARIANCE-DRIVEN's zero-income share? | VARIANCE-DRIVEN (Stage 2) | NOTE 3 |
| D8 | R-B ranking layer (income t at NOT RUN points); anchors' eligibility; the Stage-2 combination for TOST and for the \|x̄\| ≥ 0.10 bar | R-B | MUST 5 |
| D9 | Printing precision. Calls use unrounded floats, which is pinned by the code; printed rounding is cosmetic | none | — |
| D10 | **NOT MEASURED legs.** Perception families are empty at this stage. T4 enters Holm at p = 1, which can only under-reject T1–T3. LEVER is "not evaluated", so every EARNS call counts, with the caveat. All three are pinned; the final §8 must re-evaluate them once LEVER and T4 are read | §8, provisional | OK |
| D11 | Outliers, extinction, tie-breaks | extinction is pinned (missing row = 0; `EXTINCT.txt`). BH ties are handled by step-up. R-A ties go by midpoint id; R-B ties by point id | OK |

## 5. Integrity counts, recomputed (`counts.py` → `counts.txt`)

| quantity | plan | recomputed |
|---|---|---|
| `lanes/1` job lines (distinct names) | 936 | **936** (936) |
| by type: fresh / adopt / ksalt / snapshot / resume | 252 / 36 / 72 / 288 / 288 | **252 / 36 / 72 / 288 / 288** |
| `lanes/1` run directories: S / ckpt60 / ksalt | 288 / 288 / 72 = 648 | **648** |
| unit records | 288 | **288** |
| K-SALT point-seeds | 72 (129002 and 129003 × 36) | **72** (36 + 36) |
| `host1-lane0` minus `host1-lane0b` | {`1/c2-p030-U-G/129001/M`} | **same**. lane0b ⊂ lane0 |
| `lanes/1-MN` loaded (lane0b in place of lane0): forks, distinct directories | 37 | **37** (30 M, 7 N). None is scheduled twice in the loaded set |
| `launch.txt` forks line | 38 (31 M, 7 N), 9 points | **38** (31 M, 7 N). Line minus loaded = the CRASHED unit; loaded minus line = ∅ |
| expected labels | 973 | **973** = 648 + 288 + 37. The quarantined directory is not among them |
| done-markers (one per job) | 973 | **973** = 936 + 37. This equals the label count by coincidence |
| `platform.json` directories | 613 | **613** = 288 S + 288 ckpt60 + 30 M + 7 N |
| N runs by null kind | df_null = 2 | holistic-null 6 runs (2 + 2 + 1 + 1), designed-null 1. Per-(point, kind) df: **holistic 2, designed 0** |

From the gate table (registered input), **9 of the 10 M-eligible points already have < 6 valid seeds**. Only
`c2-p030-U-G` (8/8) can be habitable. Six of the 12 PW points have ≤ 2 valid seeds, and five more are designed
FOUNDING-FAIL in the census. This is why MUST 3 is likely to bite.

## 6. The script

- **The quarantine.** Every path that reads, restores, fetches or lists goes through `refuse_quarantined`:
  - `guarded_reader`, `guarded_restore` and `read_run`;
  - `load_jobs`, which refuses `host1-lane0.jsonl` and any lane that schedules the directory;
  - `expected_labels`, `fork_double_writes` and `gate_valid_from_ckpt60`.

  `crash_reconcile` reads only job names, and `remote_labels` lists names only. I found **no path that reads the
  quarantined label**.
  - The label normaliser misses `remotes/origin/ckpt/<label>`, and `abspath` does not resolve a symlink alias (probe
    P10–P11). Nothing generates either today (NOTE 6).
  - The real exposure is outside the script: the repo's fetch refspec is `+refs/heads/*:refs/remotes/origin/*`, so a
    bare `git fetch` or `git pull` in the readout session would fetch the quarantined branch (SHOULD 8).
  - The guard cannot cover the uncommitted driver (MUST 2).
- **`--go`.** `main` returns 9 with nothing read when `--go` is absent or empty, and its test covers that. Any
  non-empty string passes (NOTE 7). The `readout` step is not implemented: it raises `SystemExit` (MUST 2).
- **The statistics against the plan.** These match the plan:
  - t, TOST, BH, BY, Holm and Holm-provisional;
  - thresholds, the body-call order, the income call, MARGINAL;
  - pooled null, K2 pooled;
  - Wald, Fieller, κ, sign changes;
  - the 42 R-A pairs, the CP formula;
  - the verdict precedence.

  The distributions, written without scipy, reproduce known values (t₀.₉₇₅,₁ = 12.7062; P(T₇ > 2) = 0.04281). The
  departures are `resolving` (MUST 1), `pooled_null`'s df (SHOULD 1), `k2_per_point` at 1 run (SHOULD 2),
  `verdicts` (MUST 4) and `rb_select`'s anchors (MUST 5).
- **The tests mask MUST 1.** `test_contingent_k2_and_resolving` stubs `resolvable` with a function that returns a
  bare `True`, not `power.resolvable`'s `(rows, passes)`.

## MUST

1. **RESOLVING is wrong in two independent ways** (DESIGN §6.2, §4.1 lines 343–345, §10.1 line 1116; crash ruling
   item 4(b)).
   - **(a) The result is always True.** `stage1_readout.resolving` returns `bool(resolvable(...))`, but
     `power.resolvable` (`power.py:339–349`) returns `(rows, all(passes))`. A non-empty tuple is always True, so every
     N point with ≥ 2 M seeds reads RESOLVING (probe P1).
   - **(b) The replica is unscaled.** It runs at `Y_SCALE` = 1.0. DESIGN scales the replica's drift by the pilot's
     ratio (`stageP0-readout/pilot_constants.json`, `y_scale` 1.5297), and the P+0 readout's RESOLVING bands already
     use it. #500 item 2 exempts the gate's thresholds only.
   - **Effect.** At Stage 1 it misprints RESOLVING at `c0-p030-PW-G`, `c2-p010-PW-G` and `c1-p010-PW-L` (descriptive
     only). At Stage 2, which the plan says this script serves, it would decide TIE, SATURATED and UNDECIDED, and
     R-A's layer.
   - **Fix.** `rows, ok = resolvable(...)`. Call `power.load_pilot(pilot_constants.json)` first, and print the scale.
     Test against `power.resolvable`'s real return shape.
2. **Commit the readout's computing layer before the go** (plan §1: "every statistic and call as a pure function,
   each pinned by a test"; and "Added in the readout session: only the `readout` step's printing driver").
   - **The claim is not true at `e83ef23`.** The items in D1 are uncommitted. Each one is a choice the readout author
     would make with the data open.
   - **Fix.**
     - Commit the `readout` step in full: `stage1_readout.txt` end to end.
     - Add a synthetic-tree test that produces every section's lines, including the CRASHED point at M 7 of 8 with
       its bound and paired S.
     - Have the adversary fix-check it before the go.
   - **What is left for the readout session:** running it, and a reader adapter for `stage1-provenance/` if its form
     differs.
3. **Pin M2's behaviour when the design is not estimable** (§7.2; T1–T3, §7.3).
   - **Why it is likely.** From the gate table, 6 of 12 PW points have ≤ 2 valid seeds (so they are not habitable).
     Five more are designed FOUNDING-FAIL in the census. The L smell has 2 points at 5/8 and 1 at 2/8.
   - **What breaks.** If no habitable point is PW (or L), that column is zero, X′H X is singular, and `lmm_reml`
     raises. T1, which gates verdicts 1, 2 and 6, then has no registered value, and `holm()` raises on a None p. One
     habitable PW point leaves the PW coefficient confounded with its own random intercept.
   - **Fix.** Register now:
     - **A support rule.** Drop a world term whose column has no variation among the habitable income-valid seeds,
       and drop c × log p when c or log p has fewer than 2 levels. Print the dropped terms.
     - **T1's df** is then the number of remaining world terms.
     - **T2 and T3** read NOT TESTABLE if their term is dropped, and enter Holm at p = 1 (or as the coordinator
       rules).
     - **A minimum.** For example, T1 is NOT TESTABLE with fewer than P + 2 habitable points.
     - **What a NOT TESTABLE T1 does to verdicts 1, 2 and 6.**
4. **The §8 logic: two readings change the headline verdict, and must be listed, printed both ways and ruled**
   (§8, lines 948 and 960–982).
   - **(a) EARNS at habitable points only.** The plan counts EARNS calls only at habitable points (§4.3, §9;
     `verdicts()`). DESIGN restricts only verdict 3's denominator. The restriction is not in the OPEN table. Probe P7
     (T1 rejects; 2 EARNS-H at habitable points; EARNS-D at a PARTIAL-D and an EXCLUDED-H point) reads EARNINGS
     DEPEND under DESIGN and DEPENDS ONLY THROUGH HABITABILITY (H) under the plan.
   - **(b) O-20b.** It drops EARNS-TIE from verdict 5's "every decided EARNS call", although §8 defines a decided
     income call to include EARNS-TIE. Probe P6 (20 EARNS-TIE, 1 uncorroborated EARNS-H, 2 survival calls for D, T1
     not rejected) gives verdict 5 ahead of WORLD-INVARIANT. Under the defined term, 5 fails and the verdict is
     WORLD-INVARIANT.
   - **Fix.** Add (a) as an OPEN item. Print the provisional §8 under each combination of (a) and (b), and have the
     coordinator choose before the go. Neither can be chosen by its effect once the calls are known.
5. **O-18 needs an explicit coordinator ruling, labelled DATA-INFORMED, before the go, and two missing pins**
   (§4.2, line 371; §5.2; §10; §11.2).
   - **Defensible on the text.** §5.2 r4 says the body call "falls to the income and survival layers" at NOT RUN
     points. §10 prices R-B on income. §11.2 budgets 20 points.
   - **Why it needs a ruling.**
     - It was registered knowing, from the gate table, that the literal list is empty.
     - It turns R-B from 0 points into up to 20 (≤ 413–473 core-h), which is owner cost.
     - A readout plan cannot itself change what runs.
   - **What the plan must also pin.**
     - **(i) The ranking layer.** CP uses the **income** t and n at NOT RUN points. The code does this; the plan does
       not say it.
     - **(ii) The anchors.** Are the "RBT-118 (not available)" anchors eligible? The code says yes (probe P9). The
       plan's words say "NOT RUN" only. §5.2 item 3 says the sweep does not re-run the anchors' M/N, and T7 routes
       their seeds through RBT-118.
     - **(iii) Stage 2's test.** At Stage 2, the combined Z applies to the EARNS t. State how the TOST (EARNS-TIE) is
       combined, and over which seeds \|x̄\| ≥ 0.10 is read.

## SHOULD

1. **O-9: per kind** (§6.1 item 6). Compute σ̂²_null and df **per kind**. CONTINGENT is callable only when the
   per-kind df reaches 12 (pin: each kind, or the kind the F test uses), and the plan must state which kind's σ̂²
   divides a point's var(y′). `pooled_null` currently sums both kinds (probe P4). There is no Stage-1 effect, since
   df is 2 and 0.
2. **K2 per point at one run** (§5.5). The size bar \|y′_null\| ≤ 0.15 is evaluable, and the t clause cannot reject.
   Read PASS iff the bar holds, else FAIL. Probe P3 shows a single run at 0.40 escaping VOID. There is no Stage-1
   effect.
3. **Make the integrity verdict fail on all the plan's own HELP conditions.**
   - Read `resumed-readout.txt` (or call `resumed.py`'s checker) into `integrity()`, and FAIL on any double write
     other than the listed census signature case.
   - Make a §3.2 cross-check mismatch at an income-valid seed a HELP, not a printed count. Repeated lineage rows enter
     the flow twice.
4. **List the C1 point mapping as an OPEN item** (F8). Of the 18 candidates, 11 are census points that are not R-A
   midpoints of any Stage-1 pair. Examples are `c05-p018-HP-L` (an L point at c = 0.5) and `c05-p053-U-L`. The
   alternative reading, "the Stage-1 pair flanking the sign change", admits only sign changes on Stage-1 rows and
   drops all 11. §4.2's last line forbids any point not added by the rule, so the reading must be registered, not
   implied.
5. **T3.** At each Stage-1 point, print the census holistic FOUNDING-FAIL layer beside Stage 1's founding (validity
   at 59 per fauna), as AMENDMENT-FOUNDING T3 requires.
6. **A §12 scorecard, pinned now.** For each registered prediction, give the statistic and what reads "as
   predicted", "not as predicted" or "not measured":
   - item 1: T2 > 0, T3 > 0, M3 p* above 0.018 at c = 1 and above 0.053 at c = 0, EARNS-D on flat p ≤ 0.03, EARNS-H
     at c ≥ 1, p ≥ 0.03;
   - item 2: share NOT RUN or SATURATED at most points, RESOLVING at 0–2;
   - item 3: EXCLUDED-D or PARTIAL-H at some p = 0.08, c ≥ 1 point;
   - item 5: EARNINGS DEPEND.
7. **State the exclusions and the empty flows.**
   - State that no seed or run is excluded, winsorised or re-weighted for any reason but K-SALT VOID, validity (§3.1)
     and CRASHED. The P+0 precedent is a post-plan exclusion.
   - Pin the empty-flow case: an income-valid seed with no member-season for a fauna is a HELP, not a crash.
     `assemble_point` raises on `None − x`.
8. **Fetch hygiene for the quarantine.**
   - The plan should forbid a bare `git fetch`, `git pull` or `git fetch --all` in the readout session, because the
     default refspec fetches `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M`. Only narrow refspecs should be allowed.
   - Integrity should assert that `refs/remotes/origin/ckpt/<quarantined>` does not exist locally.
9. **Integrity should not restore 80 `ckpt60` directories.** `gate_valid_from_ckpt60` calls `stages._restore`, which
   unpacks the full S 0–59 state. That breaks §1 ("Restore. Only after integrity passes"; integrity reads "the
   season-59 alive counts … and nothing else"). Read `history.json` alone with `branch_file`.

## NOTE

1. §0, §4.5 and the ruling say "every N point is PARTIAL". The exact statement is "settled by §6.1 item 1 or 2".
   `c0-p030-PW-G` has 6 invalid seeds, and if one fauna is the dead one on ≥ 5 of them, the call is EXCLUDED. The
   conclusion is unchanged.
2. s₀ for the bound is read from `ckpt60`, not "S60" (F11). This is the right branch; say so in §4.6.
3. Variant (i), `last_score`, is not a variant. `Simulation.harvest` already zeroes food and work on an explosion
   (`simulation.py:774–778`), so the primary net is 0 on exploded rows too, and the plan's "differs only on exploded
   rows" is wrong. Exploded rows are 0-food seasons. Pin whether they count in VARIANCE-DRIVEN's zero-income share;
   the legs readout showed explosions can drive a statistic (`legs-readout-adversary/` §3).
4. The M-arm g0 (§3.4) excludes newborn rows. The census g0 (T5, `stageP0_readout.py:315`) reads them as 0. "Census g0
   beside M g0" is therefore not like-for-like; print the M g0 under the census convention as well.
5. In `assemble_point`, the CRASHED-M `continue` also skips that seed's N read (probe P8). This is harmless at Stage 1,
   where `c2-p030-U-G` has no N.
6. `_is_quarantined_label` misses the `remotes/origin/ckpt/` prefix, and the path check does not resolve symlinks
   (probe P10–P11). Use `realpath`, and strip any prefix ending in `ckpt/`.
7. `--go` accepts any non-empty string. Consider checking it against an entry in `RULINGS-CITED.md`.
8. Plan §2.5 names `tests/test_stage1_readout.py`. The file is `tests/test_rbt129_stage1_readout.py`.
9. `fork_double_writes` calls `resumed.written_twice`, which reads `origin/ckpt/<label>` without fetching. It works
   only because `check_markers` fetched the same refs first. Make the fetch explicit.
10. T1–T3 on the registered fit (Stage-1 grid, seeds 1–8) are already their final values (§7.2). Only Holm waits on
    T4. "Provisional" should be said of Holm and §8, not of the coefficients.
11. O-12 has an equivalence reading. Rule it before Stage 2.
12. Under O-16, L pairs are refined only if fewer than 16 G pairs fire. Say so in the report.
13. O-1's ruling is quoted as relayed (`RULINGS-CITED.md`) and cannot be checked from the repository. The go should
    confirm it.
14. `thresholds(0)` is (0, 0), so an all-VOID point reads NEITHER. A HELP precedes this in practice; guard it anyway.
15. A SATURATED point with an income UNDECIDED is not R-B-eligible, while a NOT RUN point is (O-18). This follows the
    §5.2 sentence. There is no Stage-1 instance.

## Answers to the brief

| question | answer |
|---|---|
| 1. Fidelity | §2: F1–F12. Departures are F1–F10. The rest match, with line references |
| 2. O-2 to O-22 | §3. Most are accepted. O-9 needs a fix. O-11 must be split. O-17's mapping must be listed. O-18 needs a ruling and pins. O-20b must be ruled and printed both ways. The share-call claim is correct, with NOTE 1's wording |
| 3. Missing degrees of freedom | §4, D1–D11. The largest is the uncommitted driver (MUST 2) |
| 4. Crash ruling | Quoted verbatim (byte-identical). Items 1–7 are all placed. Item 4's S60 is read from ckpt60, which is correct (NOTE 2). Item 4(b) is implemented, but RESOLVING itself is broken (MUST 1). The code lacks item 4's regime readout and M2's share model at n = 7 (MUST 2) |
| 5. Counts | 973, 973 markers, 613 and 38 = 37 + 1 all reproduce. N kinds: holistic df 2, designed 0 (§5) |
| 6. Script | The refusal fires on every path in the script (§6). The statistics match except MUST 1, SHOULD 1–2, MUST 4 and MUST 5. `--go` works. Clean venv without scipy: 972 passed, 1 skipped |

## Files (`runs/RBT-129/stage1-readout-adversary/`)

- `ADVERSARY.md`: this report.
- `counts.py` → `counts.txt`: the integrity counts from the lane files.
- `probe.py` → `probe.txt`: P1–P12, single-function probes on synthetic values. Run it as
  `python3 probe.py <worktree at e83ef23>`.
- `probe2.py` → `probe2.txt`: Q1–Q20, the fix-check probes (below). Run it as `python3 probe2.py <worktree at eaab9c8>`.

## Fix-check (eaab9c8)

*Head `eaab9c80361cdcfad5a169e884284df0fd18844d`. My round-1 report was cherry-picked onto it as `84f9760`, and the
coordinator's `COORD-RULING-512.md` (R1–R5) was added. I fetched the PR branch by its own narrow refspec only. **No
`ckpt/rbt-129-stage1-*` branch and no Stage-1 output was fetched or read**, and the quarantined branch was not touched.
I did not open PR #513, `claude/rbt129-stage1-provenance`, or the coordinator's disclosure file. The probes are
`probe2.py` → `probe2.txt`, run on synthetic values and registered inputs only.*

*Test run: a fresh clean venv (`python -m venv /tmp/v2 && /tmp/v2/bin/pip install -e ".[dev]"`, no scipy), then
`pytest -q` on eaab9c8: **running at commit time; the result is recorded in the next commit**. The plan's own file has 82 passed.*

### Verdict: **ADOPT AFTER FIXES**

There are **2 MUSTs**, and both are small:
- **FC-MUST 1** implements my ruling on O-23, which the coordinator delegated to me;
- **FC-MUST 2** closes a path by which text from outside the readout could be written into `integrity.txt`.

All 5 round-1 MUSTs, all 9 SHOULDs and every listed NOTE are fixed. COORD-RULING-512's R1–R5 are implemented exactly.

**Timing of the ruling.** COORD-RULING-512 was committed in `eaab9c8` at 20:28:19Z. The coordinator's exposure to an
aggregate Stage-1 figure came at about 20:45, as the coordinator reported it. The exposure postdates R1–R5, so it does
not touch them. O-23 is ruled below from the registered text alone.

### Round-1 items

| item | status | evidence |
|---|---|---|
| MUST 1a | **fixed** | `resolving()` unpacks `(rows, passes)`. Q1: a stub with the real return shape that fails at both bounds gives False. The test now drives the real `power.resolvable` |
| MUST 1b | **fixed** | `scaled_resolvable()` calls `power.load_pilot(pilot_constants.json)`, giving Q2's y_scale 1.5297. The scale is printed in the readout header |
| MUST 2 | **fixed, with gaps** | `readout()` writes `stage1_readout.txt` end to end, covered by `test_the_readout_runs_end_to_end_on_a_synthetic_tree` (36 × 8 points and seeds, the registered forks line, the CRASHED directory poisoned). Some descriptive §8 outputs are still missing (FC-SHOULD 1) |
| MUST 3 (R3) | **fixed exactly** | Support rule: Q9 drops `L=PW` and `s=G` and stays TESTABLE at P = 4. Singular → NOT TESTABLE: Q10. No seed → NOT TESTABLE, all Holm p = 1: Q12. The P + 2 point floor is enforced. T2/T3 are NOT TESTABLE with their term or with T1. Verdicts 1, 2 and 6 are unreachable: Q7 gives "NO VERDICT at Stage 1 (T1 NOT TESTABLE)", while Q8 still reaches verdict 3 |
| MUST 4 (R1, R2) | **fixed exactly** | Round-1 P7 now reads EARNINGS DEPEND, and the habitable-only line is labelled non-registered (Q6). Round-1 P6 now reads WORLD-INVARIANT, and the v5-ignores-TIE line is labelled non-registered (Q5) |
| MUST 5 (R4) | **fixed exactly** | Anchors are excluded from R-B. CP uses the income t and income-valid n at NOT RUN points. The literal list is printed. The core-h line says "needs its own owner GO". `stage2_income_call` combines both one-sided TOSTs and reads \|x̄\| on the pooled 16 (Q16: TIE at a true 0; Q17: EARNS-H at +0.5) |
| SHOULD 1 | fixed | per-kind σ̂² and df (Q3: holistic 12, designed 1). The holistic-null pin is accepted: the M arm's y′ is the holistic share change |
| SHOULD 2 | fixed | Q4: one run at 0.40 gives FAIL; at 0.10, PASS |
| SHOULD 3 | fixed | the resume audit runs inside `integrity()` over 576 S/ckpt60 directories, the census sources and the 37 forks. The accepted signature (347/5 rows, seasons 55–59, 0 torn) matches `resume-audit/resumed-2026-10-01.txt:92`. A cross-check mismatch, or a flow disagreeing with the sweep log, raises `ReadoutHelp` |
| SHOULD 4 | listed as O-23 | ruled below (FC-MUST 1) |
| SHOULD 5, 6, 7 | fixed | the T3 founding table (36 rows); `scorecard()` with the item 1–5 rules pinned in code; the exclusions line; an empty flow is a HELP |
| SHOULD 8 | fixed | `fetch_label` uses a narrow refspec. `local_quarantine_refs` refuses in `main` and fails integrity. `durable.sh restore` also fetches narrowly (`scripts/durable.sh:91`) |
| SHOULD 9 | fixed | `gate_valid_from_history` reads ckpt60's `history.json` with `branch_file`, and integrity restores nothing. `fork_seed_mismatches` adds T5's seed rule |
| NOTE 1–4, 6, 8, 9, 14 | fixed | Quarantine: Q18 refuses the `remotes/origin/ckpt/…`, `.tar` and space-prefixed forms, and Q19 refuses a symlink alias. n = 0 is a HELP |
| NOTE 5 | fixed | the CRASHED seed's N read is no longer skipped |
| NOTE 7 | fixed | `--go` must match a `GO-ID:` line. Q13: none exists at head, so the script refuses. See FC-NOTE 1 |
| NOTE 10–13, 15 | wording, done | |

### O-23 (the C1 point mapping): my ruling

**Adopt the "Stage-1 flanking pair" reading.** A census sign change on a C1-listed row adds the **R-A midpoint of the
pair of adjacent Stage-1 points that flanks it**. So only sign changes on **Stage-1 rows** count:
- price rows at c ∈ {0, 1, 2} (G), and at c = 1 (L);
- clutter rows at p ∈ {0.01, 0.03, 0.08} (G).

The plan's other 11 candidates are dropped. That leaves **7 candidates**: `c0-p018-HP-G`, `c1-p018-PW-L`,
`c1-p018-U-G`, `c1-p053-U-G`, `c2-p053-HP-G`, `c05-p030-U-G` and `c15-p030-U-G` (Q15). Each ranks by its flanking
pair's |Δt|, as the plan already does.

**Why, from the registered text:**
1. **§5.1 C1** says the rows that break monotonicity "**enter R-A's pair list**". R-A's list is a list of pairs of
   adjacent **Stage-1** points (§4.2, "for each pair of Stage-1 points adjacent on the price axis … or on the clutter
   axis"). A census row off the Stage-1 grid has no such pair to enter.
2. **§4.2** says C1 adds "**the pair** flanking each extra sign change, **ranked in the same list**". The ranking is
   |t₁ − t₂| on the pair's layer, which is defined only for two Stage-1 points with estimates. A census-only
   candidate has no |Δt|. That is why the plan had to invent a rank-last rule for it, and the invented rule is the
   sign that the reading has left the text.
3. **R-A adds "the registered midpoint … at the same other levels"** as the Stage-1 pair. The 11 dropped points are
   not such midpoints. For example, `c05-p018-HP-L` sits at two refinement levels, and is an L point at c = 0.5, where
   no Stage-1 L point exists.
4. **§4.1** defines Stage 2a as "≤ 16 new points by rule R-A". **§4.2's last line** says "No other point … may be
   added after Stage 1 is seen, except by a new registration". Admitting non-midpoints would need that registration.

The plan's reading ("the census point at a refinement level of the row's own axis") appears nowhere in DESIGN. On
Stage-1 rows the two readings name the same points, so nothing that the registered text covers is lost.

### FC-MUST

1. **Implement O-23 as ruled.**
   - Restrict `c1_candidates` (or `ra_select`'s C1 intake) to midpoints of `ra_pairs()`, so that a C1 candidate always
     has a flanking Stage-1 pair. Drop the "no Stage-1 pair: ranks after every ranked pair" branch.
   - Update §7.1 and the O-23 row.
   - Update `test_c1_candidates_from_the_committed_census_readout`. It currently asserts that `c05-p018-U-G` and
     `c0-p018-PW-L` are candidates, so it must instead assert the 7.
2. **The provenance input must be validated, and must never be echoed** (plan §2.6; `stage1_readout.py:530` and
   `:2026`).
   - **The leak.** `integrity()` prints `stage1-provenance {provenance.get(k)}` for every key on which the readout and
     the file disagree. `verdicts.json` is loaded with no shape check. So any extra key or non-verdict value in that
     file is copied verbatim into `integrity.txt`, which is committed before anything else is produced. You have said
     an earlier revision of that work carried an outcome summary. This is a path from it into the readout's first
     committed output.
   - **The fix.**
     - Validate first. The file must be a JSON object whose keys are exactly the 613 `platform_dirs` paths and whose
       values are each exactly `"PASS"` or `"FAIL"`.
     - On any other shape, print `stage1-provenance/verdicts.json: malformed: HELP` and nothing from the file.
     - Print disagreements only as `<expected dir>: readout X, provenance Y`, with X and Y each in {PASS, FAIL}.
     - Remove §1's "reader adapter at readout" exception. With the format pinned (below) it is not needed, and it is
       the last piece of code the readout session could write.
   - **A missing file is fine as coded.** The script's own check of all 613 `platform.json` files satisfies ruling
     item 7 by itself, and the cross-check is extra.

**The file the plan needs from the provenance session.** Please arrange exactly this:
- path: `runs/RBT-129/stage1-provenance/verdicts.json`;
- a single JSON object with **613 keys**;
- each key is a repo-relative run directory spelled exactly as the lane files' `dir` field, e.g.
  `runs/RBT-129/stage1/c0-p010-U-G/129001/S`, and the same for `…/ckpt60`, `…/M` and `…/N`;
- each value is `"PASS"` or `"FAIL"`;
- **no other key, field, count or text**.

The readout reads no other file in that directory. The only provenance claim it may rely on is the one you stated:
every physics-running directory is at 3.14.0.

### FC-SHOULD

1. **The driver does not produce every descriptive output that the plan's §8 and §10 promise.** Missing:
   - the living-share variant (§3.3; `living_share_window` is never called);
   - the N runs' y′ per run (only K2's per-point mean is printed);
   - M6 (κ; at Stage 1 the line "no decided share call");
   - alive, births, deaths and the extinction season;
   - food, work and path per season;
   - `mean_lifetime_score`;
   - the M5 "NOT MEASURED" line.

   None of these is a call. But the point of round-1 MUST 2 was that the readout session writes nothing, so either add
   them now or strike them from §8 and §10.
2. **K-SALT VOID seeds have no input path.** `main` calls `readout(a.root)` with no `void_seeds`. If a VOID is ruled,
   the readout session would have to edit the call. Read ruled VOIDs from a fixed line format in `RULINGS-CITED.md`
   (for example `KSALT-VOID: <point> <seed>`), as is already done for `GO-ID:`.
3. **Make the plan and the code say the same thing.**
   - **M7.** The plan says it counts sign changes over points with an estimate at n ≥ 2. The code uses `income.mean`,
     which exists at n = 1. Make the code skip n < 2, and print gaps.
   - **MARGINAL.** The plan should state the aggregation the code pins: per-birth income is the mean over the point's
     income-valid seeds of each seed's regime `net_per_birth` + 0.25.

### FC-NOTE

1. **Empty GO-ID lines.** `go_ids()` keeps an empty value. With a stray `GO-ID:` line and nothing after it,
   `--go " "` would pass (Q14). Reject empty IDs, or the coordinator should never write an empty line.
2. **Failed fetches.** `fetch_label` ignores the fetch's exit code. A failed fetch then surfaces as a
   `CalledProcessError` in `written_twice`, so it is a crash, not a HELP line. That is fail-closed, but it is not
   labelled.
3. **The share model's floor.** It applies the P + 2 rule to all its terms, including census g0, which comes to P + 3.
   That is slightly stricter than "the same conditions". It is descriptive only.
4. **Collinear designs.** Under R3 as ruled, a collinear design is NOT TESTABLE as a whole; it does not just lose its
   interaction. An example is habitable points that lie on a c/log p diagonal (Q10). This is as ruled, and noted only
   so that the outcome is not a surprise.
5. **Stage 2 wiring.** The driver hard-wires `vd` to False and `lever` to None. Both are unreachable at Stage 1 (no
   share WIN; LEVER not measured). The claim that "the same script serves Stage 2" needs the Stage-2 plan to wire them.
6. **A spare anchor.** R4 (ii)'s anchor list includes `c0-p030-U-L`, which is not a Stage-1 point. This is harmless.
7. **Labels the guard does not refuse.** `x-<label>` and `<label>0` are not refused (Q18). No real ref or path takes
   either form.

### Fix-check files

- `probe2.py` → `probe2.txt`: Q1–Q20.
