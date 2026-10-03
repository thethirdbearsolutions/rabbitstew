# RBT-129 Stage 2 plan: adversary report (pre-data)

*Fresh, independent adversary for PR #523 (`claude/rbt129-stage2-plan`, head `242528f`, base `claude/new-session-4cao7d`
at `c6b57ec`). Written 2026-10-03. Coordinator: `session_017eUHGNdTSsoVFAtLaJWehF`.*

**What I did and did not touch.**
- Every fetch used a narrow refspec: the plan branch, the base, and the crash PRs' branches (#520 now at `f05c6bb`,
  #521 at `4b9034a`).
- `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M` was never fetched, listed or read. `git for-each-ref` shows 0 local refs
  naming it.
- I modified nothing on the plan branch and launched nothing.
- I read only public, accepted records. My Stage-1 numbers come from `stage1_readout.txt` (sha256 `beb515aa…`, verified).
  The scripts in `probe/` read that file and nothing else. No Stage-2, R-B or continuation output exists.

## Verdict: **ADOPT WITH CHANGES**

- **Counts:** 0 BLOCKING, 7 MAJOR, 8 MINOR and 7 NOTE.
- **What is sound:**
  - The plan's skeleton, budget, seeds, gate, combination and locks are correct where I could check them.
  - Its R-A, R-B and final-BH structure follows DESIGN §4.1, §4.2 and §7.1.
- **The MAJORs fall in three groups:**
  - **The overflow record and the crash amendment cannot be implemented as written** (findings 1–3). The stats check
    fails at the registered WORKERS = 2. "Attested" cannot be checked from the record that is specified. And the S-arm
    amendment has no ceiling and enumerates impossible states.
  - **The C3 pins** (findings 4–6):
    - C3-5 decides DESIGN §9.1's RBT-118 rule-chosen points, which have never been chosen. The plan says the reverse.
    - The five pins rest on two opposite principles. Each time the choice matters, it lands on the favourable side.
    - C3-2 is the hinge of the most likely way the final headline could move, and the plan does not say so.
  - **Optional stopping** (finding 7). The interim readout prints a provisional §8 before a discretionary owner GO for
    2b(2a).
- **None of the changes needs Stage-2 data,** and all of them can be made before the drivers round (O-30).

## Findings

### 1. MAJOR: the build-record agreement check fails at the registered WORKERS = 2, so every flagged unit would be a HELP

- **Evidence.**
  - **Where the stats are written.** `mujoco-3.14.0-epa-horizon.patch` (blob `b90290b`) writes the `RBT_HZN_STATS` line
    from an ELF `__attribute__((destructor))`.
  - **Workers never write it.** RBT-129 lanes run `WORKERS=2` (`launch/stages.py:859`, and the lane layout at lines 9
    and 83). The physics then runs in `ProcessPoolExecutor` workers (`rabbitstew/evolution.py:182`), which are forked on
    Linux under Python ≤ 3.13. A forked multiprocessing child leaves through `os._exit`, so ELF destructors never run.
  - **I reproduced it.** In `probe/destructor_in_pool_workers.py` (Python 3.11), a library with the same destructor
    pattern, loaded in a 2-worker pool, wrote one stats line, from the parent only. The two workers that did the work
    wrote none.
  - **Fork also copies the counters.** A forked worker inherits the parent's `rbt_iters` and `rbt_overflow`. If workers
    ever did write a line, counts made before the fork would be counted twice.
  - **The diagnosis never met this.** It ran the build at WORKERS = 1 (#521 §(d): "The histogram is per process;
    WORKERS=1 is used").
- **Effect.**
  - `unit_state` returns HELP when `overflow_lines != stats_overflow`.
  - At WORKERS = 2, an overflow inside a worker prints its stderr line but adds nothing to the stats. **Every flagged
    unit becomes a HELP.**
  - For clean units the check is vacuous, because only the parent's line exists.
  - **The rule in §3.3 cannot be implemented as written under the registered lane layout.**
- **Remedy.** Choose one before CT-1/CT-2:
  - **(a) Run every Stage-2 unit at WORKERS = 1.** Use four single-worker lanes per 4-core host, which gives the same
    throughput. Register it, and keep the agreement check. **This is my recommendation**, because it also matches RULING
    item 5's WORKERS = 1 clause.
  - **(b) Weaken the check** to `stats_overflow ≤ overflow_lines` and `processes ≥ 1`, and say that the stats cover the
    parent only.
  - **Either way, CT-2 must exercise the build record at the launch's real WORKERS.** That means a forced-overflow replay
    (the diagnosis's `state_2246`), with the stderr and stats files checked.

### 2. MAJOR: "attested" is not verifiable from the record the plan specifies, and the code checks a weaker condition than the text

- **What the text requires.** §3.5 makes the crash count as CRASHED when "an `RBT_HZN overflow` line precedes the fault in
  **the attempt's** captured stderr". RULING item 5's counting needs **two** attempts in a row.
- **What the record holds.**
  - §3.2 keeps only the overflow lines in `hzn_overflow.txt`. It keeps no attempt delimiter, no fault marker and no exit
    signal.
  - Its lines carry no pid, attempt or time. That is right for blinding, but then **order relative to the fault cannot
    be read.**
- **What the code checks.** `unit_state(done, hzn, crashed=True)` returns CRASHED if the **unit's** file has at least one
  overflow line anywhere. That passes a unit like this one:
  - an earlier attempt or resume segment overflowed and survived (a FLAGGED-type event);
  - later, a different mechanism crashed twice with no overflow line.

  The unattested new mechanism would then be scored as the known bug. That is exactly the case the amendment means to
  route to item 5.
- **Answer to (c), "is attested verifiable from the instrumented log alone?"** **No.** The record also needs the
  runner's per-attempt boundaries and exit status. Those are not outcomes.
- **Remedy.**
  - The runner's stderr filter writes per-attempt markers into the same file:
    `RBT_ATTEMPT k START workers=W` and `RBT_ATTEMPT k EXIT code=C signal=S`.
  - CRASHED (attested) requires **each** of the two counting attempts to have:
    - at least one overflow line between its START and its EXIT;
    - an EXIT with a native signal;
    - and, for one of the two, `workers=1`.

    dmesg or faulthandler still confirms "inside libmujoco", as item 5 requires.
  - Any other combination is unattested, which means HELP and item 5 as registered.
  - `unit_state` takes the parsed attempts, not one pooled count, and a test pins the case "earlier attempt flagged,
    later crash unattested → HELP".

### 3. MAJOR: the S-arm crash amendment has no ceiling, gives the income layer no sensitivity, and its survival bound enumerates impossible states

- **Against the current RULING.**
  - Item 5 says an S-arm crash "stops the hive at once", on the **first** crash. It is not a second-CRASHED rule; that
    rule is for M/N.
  - The amendment turns an attested S crash into a unit state, removed from n, with no stop.
  - Overflows are likely. #521 puts P(≥ 1 further overflow in 2a, 2b and R-B) at **≈ 50–75%**. Without the amendment, one
    S crash halts Stage 2 and GO-1.
  - **So the amendment is sound in direction, and it is not steering:** it is outcome-blind, and it is decided before any
    Stage-2 data. It has three gaps.
- **(i) No ceiling.**
  - Attested crashes may accrue without limit. Overflows depend on bodies and worlds (#520 (d); plan §3.4 reason 2), so
    several crashes at one point or in one fauna's worlds are themselves informative missingness. The plan rejects that
    argument when it is made against excluding flagged units.
  - **Remedy:** stop and rule (item 5's stop) at either:
    - a second attested CRASHED unit at the same point; or
    - a third attested CRASHED unit across Stage 2, GO-1 included.
- **(ii) No sensitivity on income.**
  - `crash_bounded_body` bounds the body call only. Income x_j "has no logical bound" (RULING item 4), so a crashed S seed
    silently lowers the income n.
  - **Remedy.** Mark the point's income call **CRASH-AFFECTED**. Where that point is a member of a counting set of ≤ 2
    calls, the §8 line is printed with the mark.
- **(iii) Impossible states are enumerated.**
  - `crash_bounded_body` enumerates extinct-at-299 ∈ {0, 1} for each fauna, even when ckpt60 shows that fauna dead at 59.
    `ecology.py` never re-seeds (AMENDMENT-FOUNDING F7), so a fauna dead at 59 is extinct at 299.
  - **A worked case.** Seven completed seeds with H extinct on 4, and the crashed seed's ckpt60 showing H dead at 59.
    - The primary call is **NOT RUN**.
    - The function returns {NOT RUN, EXCLUDED-H}, CRASH-SENSITIVE.
    - The only feasible completion is **EXCLUDED-H** (5 of 8 ≥ ⌈5·8/8⌉).
  - So the "bound" contains a call no completion can have. **The primary call is itself impossible.**
  - **Remedy:**
    - Enumerate feasible states only.
    - Print "primary call infeasible given ckpt60" when the primary call is not among the feasible ones.
    - Test this case.

### 4. MAJOR: C3-5 decides DESIGN §9.1's RBT-118 rule-chosen points; the plan says they "were chosen after Stage 1"

- **What DESIGN §9.1 says.** It picks "the habitable, non-LEVER, **non-MARGINAL** Stage-1 point with the largest
  BH-significant income effect |x̄| for each sign", "chosen by script after Stage 1".
- **Nothing has computed it.**
  - `stage1_readout.txt` has no §9.1 line.
  - `git grep rule-chosen` on the base finds only DESIGN and an R3-CHECK sentence.
  - **Plan §4.5's "which were chosen after Stage 1, so this does not reach them" is false.** Whoever computes §9.1 next
    meets the amendment.
- **The counterfactual** (`probe/c3_5_marginal.txt`). The regime table's viability is `net_per_birth / 0.25`, so
  per-birth = 0.25·(viability + 1). That reproduces L8's +0.010 / −0.121.

  | EARNS call (L) | habitable? | 240–299 (registered, censored) | 180–239 (the amendment) |
  |---|---|---|---|
  | c0-p010-U-G EARNS-D | yes | MARGINAL | not (H 0.637, D 1.192) |
  | c0-p030-U-G EARNS-D | yes | MARGINAL | not (0.427, 0.980) |
  | c0-p030-HP-G EARNS-D | yes | MARGINAL | not (0.400, 1.147) |
  | c0-p080-U-G EARNS-D | yes | MARGINAL | not (0.425, 0.492) |
  | c0-p080-HP-G EARNS-D | yes | MARGINAL | **edge**: D 0.250 at the table's 2-decimal precision |
  | c1-p030-HP-G EARNS-D | no (PARTIAL-D) | MARGINAL | not (0.392, 0.357) |
  | c1-p010-PW-L EARNS-H | no (EXCLUDED-H) | MARGINAL | MARGINAL (D −0.042) |
  | c1-p080-HP-L EARNS-H | no (PARTIAL-D) | MARGINAL | MARGINAL (D −0.440) |

  The table averages over the arm's seeds in the window, not exactly the income-valid seeds, so this is approximate.
- **Effect on MARGINAL.** It goes from **8 of 8** EARNS calls to **2 of 8** (3 with the edge case). Both that remain are
  EARNS-H. **All 6 EARNS-D are cleared.**
- **Effect on §9.1.**
  - Under the registered measure, **no** point qualifies: every EARNS point is MARGINAL.
  - Under the amendment, **one D-sign point** qualifies: `c0-p080-HP-G` (|x̄| 1.653) if its D per-birth is ≥ 0.25, else
    `c0-p030-HP-G` (1.331). No H-sign point qualifies, because both EARNS-H are non-habitable.
  - The "non-LEVER" clause cannot be certified while LEVER is not evaluated (§2.6). That is a further open question for
    §9.1.
- **Is it steering?**
  - **The measure itself is natural:** it is the latest complete birth cohort in the arm, and the run adversary proposed
    it before this plan.
  - **But it was pinned with the regime table public.** That table already showed positive 180-window viabilities.
  - **And its unstated effect is fauna-asymmetric, and it creates an RBT-118 replication target that the registered
    measure does not.**
- **Remedy.**
  - Correct §4.5.
  - Print this counterfactual in the plan.
  - Have the coordinator rule §9.1 explicitly. Either:
    - (a) §9.1 is computed on the registered measure (no point), with the amended measure's choice printed as
      DATA-INFORMED; or
    - (b) §9.1 is deferred to RBT-118's own registration, with this table disclosed to it.
  - Pin how a per-birth figure exactly at 0.25 is read: "below" is strict, at full precision.

### 5. MAJOR: the five pins use two opposite principles, and where a pin has stakes it lands on the favourable side

- **The principle the plan cites for each pin:**

  | pin | the pre-data committed code | the plan's pin | the principle cited |
  |---|---|---|---|
  | C3-1 | pooled VOID at N points only (`call_points`) | the same | the registered text, and the code |
  | C3-2 | tolerates one other EARNS (`verdicts`) | the same, **code over the literal text** | "the code the adversaries passed" |
  | C3-3 | body calls in {NOT RUN, SATURATED, anchor}: **NOT SHOWN 15/36** | **text over code: AS PREDICTED 32/36** | "DESIGN's words" |
  | C3-4 | all M points (p 0.9145) | **text over code: habitable only** | "the registered-fit sentence" |
  | C3-5 | censored 240–299 | amended | a defect |

- **The pattern.** Where the code reading is favourable or decisive (C3-2), the code governs. Where the text reading is
  favourable (C3-3), the text governs.
- **C3-3 is the clearest case:**
  - it flips a scored registered prediction from NOT SHOWN to AS PREDICTED after Stage 1 was seen;
  - it overturns code that was committed before the data;
  - the plan labels it "favourable reading" itself.
- **C3-3 is also vacuous by construction.**
  - The numerator counts gated-out points. The gate caps N at 4 + 2 + 2 points.
  - On the final map, at most 6 of about 48 points can have N: 4 from Stage 1, 1 from 2a, and only `c1-p018-PW-L` again
    from 2b(2a).
  - So the numerator is ≥ 42 of 48 whatever happens. The item can fail only through RESOLVING > 2.
  - DESIGN §5.2 also says NOT RUN is "a gating decision, not a measurement, and **never evidence of anything**".
- **Remedy.** Adopt **one** principle for all five, and state it. Mine: **the pre-data committed code governs unless the
  registered text unambiguously contradicts it; the other reading is printed, labelled.** Under it:
  - **C3-1 and C3-2** are unchanged.
  - **C3-3** stays as the script scored it: NOT SHOWN at Stage 1. Two lines are printed beside it, labelled:
    - "gated out at x of y (by design; §5.2: not evidence)";
    - the share layer's own status at the points where N ran ("not RESOLVING at k of m").

    The second line is the falsifiable part of the prediction. It reads 4 of 4 at Stage 1.
  - **C3-4** reverts to all-M as the registered descriptive fit, with the habitable line printed. No call reads either.
  - **C3-5** stays an explicit DATA-INFORMED amendment, with finding 4's remedies.

  If the coordinator prefers "text governs", then C3-2 should move to the literal reading for consistency. Either way, one
  rule applies to all five.

### 6. MAJOR: C3-2 is the hinge of the likeliest change to the final headline; "no Stage-1 effect" understates it

- **The setup.** T1 is frozen as "rejects" (plan §5.5, O-19). So the final headline turns only on counting sets.
- **The H side is 2 EARNS-H** (corrections A1):
  - `c1-p010-PW-L`, p 0.0266;
  - `c1-p080-HP-L`, p 0.0335, which passes BH by 0.0013.

  Neither is R-B-eligible, so their p-values are fixed. The final BH's K grows from 23 to as many as 35.
- **What each scenario gives** (`probe/c3_2_hinge.py`, using the committed `sr.verdicts` on the 36 Stage-1 calls exactly
  as printed; it reproduces L423–L424):

  | scenario | registered (the pin) | literal (non-registered) |
  |---|---|---|
  | as printed (2 EARNS-H) | EARNINGS DEPEND | — (fails verdict 5) |
  | **exactly one EARNS-H survives, uncorroborated** | **DEPENDS ONLY THROUGH HABITABILITY (D)** | **NOT RESOLVED** |
  | both EARNS-H drop | DEPENDS ONLY THROUGH HABITABILITY (D) | the same |
  | one EARNS-H plus any EARNS-TIE | NOT RESOLVED | NOT RESOLVED |

  Verdict 3 is blocked in every row: the survival set for H (`c1-p080-U-G`, `c2-p080-U-G`, `c2-p080-HP-G`, `c1-p080-U-L`)
  is a counting set.
- **Steering assessment.**
  - **The pin is not outcome-chosen in origin.** It is the code reading committed before data, and DESIGN §8 does say the
    dominance verdicts "tolerate one uncorroborated call for the other fauna". Verdict 5's own clause, "no counting set
    for the other", uses the defined term.
  - **It is the most consequential pin.** The author knew the H set's fragility (plan §5.6).
  - **R2's own logic points the other way.** R2 holds that an EARNS-TIE is "a decided EARNS call" not favouring X. By the
    same logic, an EARNS-H call is one too.
- **O-18 is a second hinge.** It uses the final-map M3 for corroboration. The 2a point `c1-p018-HP-L` gives row
  (1, HP, L) a third habitable price level, where Stage 1's Fieller was "whole line". A bounded p* in [0.01, 0.08] there
  would corroborate a lone `c1-p080-HP-L` EARNS-H and keep EARNINGS DEPEND. That is the registered-natural reading
  (DESIGN §8 "from the final map"), but it should be disclosed beside C3-2.
- **Remedy.**
  - State this table in §4.2.
  - Wherever the registered verdict and the literal line differ, mark the verdict line **V5-TOLERANCE-SENSITIVE**, as
    OVERFLOW-SENSITIVE is marked.
  - The coordinator rules C3-2 with this table in view (finding 5's principle).

### 7. MAJOR: the interim readout plus a discretionary owner GO for 2b(2a) is optional stopping

- **The sequence.** §5.1's interim readout prints three things before the owner's GO for 2b(2a):
  - the R-B list;
  - a "provisional, re-printed view of the Stage-1 points' calls";
  - **a "PROVISIONAL (Stage 1 + 2a)" §8 line.**

  The owner may then extend, or not extend, the Stage-2a points.
- **Why that is a problem.** Lehmacher–Wassmer protects each extended point's combined test against data-dependent
  extension. It does **not** protect the **map-level** verdict when the decision to extend is made by a person looking
  at a provisional verdict. Example: decline 2b(2a) if the provisional §8 is the preferred one.
- **The GO lock adds to it.** There is one GO-ID (`RBT129-S2-READOUT-GO-1`) for all three steps, so once it opens the
  `final` step can be run before 2b(2a) exists.
- **Remedy.**
  - **The interim prints only:**
    - integrity;
    - the mechanical R4 list with CP and core-h;
    - the 2a gate re-check.

    It prints no §8 line and no provisional calls. The R4 eligibility needs the 2a calls, so they are computed but not
    printed; or they are printed to the coordinator only, never to the owner, before the GO.
  - **The owner decides 2b(2a) before 2a data exist,** as a budget commitment: "extend whatever R4 lists, ≤ 11 points,
    ≤ 221 / 414 core-h". Or the owner declines now, and the final map is then n = 8 at those points by rule.
  - **Use separate locks:** `GO-ID-INTERIM:` and `GO-ID-FINAL:`. The final lock opens only after 2b(2a) has completed, or
    has been declined in writing.

### 8. MINOR: include-flagged's reason 3 is false; the sensitivity covers only known flags

- **Reason 3 is false.** It reads: "The build is stock physics. A flagged unit is what the registered pin produces."
  - At an overflow, stock writes past the horizon arrays. What it overwrites depends on stack layout (#521 finding 2:
    ASan shows the write lands in unallocated mjData stack).
  - The instrumented build adds statics, an `fprintf` and a different toolchain (clang/ThinLTO, not pip's). So
    **after the event its trajectory need not match stock's.** Byte identity holds only off-event ("No overflow occurred
    in any identity run", DIAGNOSIS).
  - A flagged Stage-2 unit is therefore neither stock nor defined after its first overflow.
- **The sensitivity covers only known flags.** Exclude-flagged drops scanned flags only. Stage-1 S (unscanned) keeps any
  silent overflow.
- **Remedy.**
  - Keep include-flagged as primary if the coordinator wishes; reasons 1–2 suffice, and with ~1 expected event the choice
    rarely bites.
  - Delete reason 3.
  - Name the sensitivity **exclude-known-flagged**, and say in it that the UNSCANNED units are unchecked.
- **Non-steering:** yes. It is chosen blind.
- **Pre-registerable:** yes. But the verdict-level OVERFLOW-SENSITIVE mark belongs on the headline line itself, not only
  beneath it (O-26).

### 9. MINOR: crash RULING items 2 and 7 are amended by owner decision 2, but §6 lists them as "kept unchanged"

- **What the RULING says.**
  - Item 2: "Not on another MuJoCo build or a patched build, and no code guard."
  - Item 7: "Its fix applies to later registrations only, **never to RBT-129**."
- **What the plan does.** Every Stage-2 job runs on a patched (instrumented) build.
- **Remedy.** Add **A-11**:
  - item 7's last sentence, and item 2's build clause as it bears on continuations, are superseded for **new**
    continuation units by OWNER-DECISIONS-2026-10-03 item 2;
  - item 2 still bars any re-run of a CRASHED unit.

### 10. MINOR: adopting 129001's census S60 at the 12 midpoints extends a Stage-1-scoped rule; re-simulate it instead (O-2)

- **The rule is Stage-1 scoped.** F7 and the 02:22 note say "Stage 1's S arms … at all 36 points". Adopting it at the
  Stage-2a midpoints is a natural extension, but it should be labelled as one.
- **The adopted S60 is stock and unscanned.** It is the only stock, unscanned simulation inside a Stage-2 unit.
- **Remedy.**
  - Re-run 129001's S 0–59 at the 12 midpoints on the build: 720 arm-seasons, ≈ 4.7 / 8.7 core-h.
  - Byte-compare it with the census.
  - **Equal:** adopt, now scanned. This doubles as CT-2 identity evidence on real Stage-2 units.
  - **Not equal:** HELP.
- **This resolves O-2.**

### 11. MINOR: a K-SALT mismatch under the new build is not necessarily a stream fault

- **What K-SALT does now.** It compares 2a's instrumented 0–59 designed rows with the census's stock rows. That is also
  free identity evidence, at 24 point-seeds.
- **The risk.** An overflow in seasons 0–59 makes the post-event comparison UB-dependent, so the mismatch could come from
  the build. §6.1 item 3 would VOID the point-seed for a build effect.
- **Remedy.**
  - A K-SALT mismatch in a unit whose `hzn_overflow.txt` is non-empty is a **HELP**, not a VOID.
  - Print K-SALT's PASS count as identity evidence beside CT-2.

### 12. MINOR: `_z_upper` clamps asymmetrically; a huge positive t gives +∞ and dominates the combination

- **The bug.** The p clamp at `1e-300` makes `1 − p == 1.0`, so `norm_ppf` returns +∞. The negative side is capped by
  `1 − 1e-16` at z ≈ −8.21.
- **The test.** I gave a half with t ≫ 0:
  - `_z_upper` = **inf**;
  - `combined_p` gave `z: inf`, `p_earns 0.0`, whatever the other half held;
  - the mirrored data gave z = −9.84.
- **Effect.** Practically rare, since it needs t at roughly the hundreds at df 7, but the combination becomes
  sign-asymmetric.
- **Remedy.**
  - Compute z = −Φ⁻¹(p_upper) from the tail directly: `-sr.norm_ppf(p)` with the same clamp on both sides.
  - Add a test with a near-degenerate half, in both signs.
  - `sr.stage2_income_call` has the same unclamped behaviour. The pinning test should cover the extreme.

### 13. MINOR: lock and guard hygiene

- **(a) BUILD-SHA256 is not validated.** `ruled("BUILD-SHA256:")` accepts any non-empty string (the test uses `abc`).
  Require `^[0-9a-f]{64}$`.
- **(b) Duplicate lines are not a HELP.** RULINGS-CITED-S2 says "a malformed or duplicated ruled line is a HELP". `ruled`
  returns a set, so two identical lines are silently merged. Two different GO-IDs are both accepted.
- **(c) The quarantine list is missing.** §3.5 says "the script holds a list of quarantined labels". It does not: only the
  Stage-1 label is refused, through `sr.local_quarantine_refs`. Add the list, and its refusal test, now.
- **(d) Inputs are not checked at run time.** `check_inputs()` is not called by `refusal()` or `main()`.
- **(e) A test will go stale.** `test_the_committed_locks_are_closed` asserts that the `-PENDING:` lines exist. It will
  go stale when the coordinator opens the locks, which repeats COORD-RULING-517 C5 / NOTE 10. Assert "either pending or
  well-formed ruled" instead.
- **(f) Fetch guards.** No fetch code exists yet (the drivers come later). The drivers round must reuse
  `sr.fetch_label`'s narrow refspecs and the guarded readers.
- **(g) Label namespaces.** The tooling must keep GO-1's and 2b(2a)'s branch labels disjoint from each other and from
  Stage 1's. Both are "2b".

### 14. MINOR: M4's quarter rule departs from DESIGN's "the weight its bisection splits off its parent pair"

- **Where it agrees.** For an interior point split once, giving a quarter of each parent's weight equals the axis-Voronoi
  split.
- **Where it departs.**
  - **A parent split on both sides.** `c1-p030-U-G` is split by both `c1-p018-U-G` and `c1-p053-U-G`. The rule gives it
    0.5625 instead of 0.5.
  - **Edge points.** It treats them like interior ones.
  - **Order.** It depends on the processing order (sorted ids).
- **Remedy.** Use the axis-Voronoi cell (half-intervals on log p or c), or state that the deviation is accepted. It is
  descriptive (O-17).

### 15. MINOR: the share layer at 2a is VOID almost by construction; CONTINGENT is never callable on the final map

- **K2 pooled at 2a has a low pass rate.**
  - At 2a, N runs only at `c1-p018-PW-L`, on its valid-at-merge seeds. Its Stage-1 neighbour `c1-p010-PW-L` had 2.
  - With Stage 1's null spread (sd ≈ 0.293, from L311's mean −0.125, t −1.13, n 7), P(|mean| < 0.05 | centred null) is
    about **0.19 at 2 runs** and **0.37 at 8 runs**. At fewer than 2 runs it is FAIL by code (O-10).
  - Through §6.1 item 3, a pooled FAIL can VOID that point's body call if items 1–2 do not settle it. That removes it from
    habitability, M3 rows and verdict 3's denominator. **O-10 is not purely conservative.**
- **CONTINGENT can never be called.** Its holistic-null df is 2 (Stage 1), plus at most 3 (2a), plus at most 3 (2b(2a)).
  That is < 12, so CONTINGENT is never callable unless RBT-118's anchor nulls arrive.
- **Remedy.**
  - Disclose both points in §5.3.
  - The coordinator rules O-9 and O-10 knowing them. My recommendation is to keep the registered conjunction and FAIL at
    < 2 runs, as the Stage-1 code does.

### 16. NOTE: budget, seeds and design arithmetic verified

- **Core-h.**
  - 2a S: 12 × (7 × 300 + 240) = 28,080 arm-seasons → **182.1 / 341.0**.
  - M: 5,760 → **37.4 / 70.0**.
  - N: 1,920 → **12.5 / 23.3**.
  - 2a total: **231.9 / 434.3**.
  - 2b(2a): 11 × 2,400 + 5,760 + 1,920 → **221.0 / 413.9**.
  - Sum: **453.0 / 848.2**.
  - Within DESIGN §11.2 (2a ≤ 337–450).
- **Not priced, and small.** CT-2 (about 9 units × 30 seasons × 2 builds ≈ 3.5 / 6.6), finding 10's re-run (4.7 / 8.7),
  and GO-1's M at `c2-p030-U-G` (12.5 / 23.3).
- **Seeds and salts.**
  - Salts are per seed, screened once at W118-b and held at every point (AMENDMENT-FOUNDING (a)). So 2a's and 2b's salts
    are copied correctly from `lanes/1/launch.txt`.
  - (point, seed) pairs are disjoint across Stage 1, 2a, GO-1 and 2b(2a). There is no collision with 129009–129016 at
    GO-1's points.
  - K-SALT applies at 129002/129003 only (24 point-seeds). It does **not** apply at seeds 9–16: F7 reads "wherever … the
    census also ran", which **resolves O-4 from the text**, without deferring to GO-1's tooling.
- **Gate.** `mn_gate` reproduces M = {`c1-p018-PW-L` 0.551, `c1-p053-U-L` 0.963, `c1-p053-U-G` 0.996} and N =
  {`c1-p018-PW-L`} from the census record. The caps (4 / 2) are DESIGN §5.2's.
- **Power.** The plan makes no power claim. None is needed for 2a (DESIGN §10 prices R-B, not 2a).

### 17. NOTE: fidelity to DESIGN and the Stage-1 rules is otherwise good

These all match DESIGN, as amended:
- R-A's 12 points, as printed (C1-accepted record);
- R-B under R4, with GO-1 fixed;
- the cap of 20 and M12's order;
- the inverse-normal combination, with TOST and the pooled-mean bar (R4 (iii));
- BH once over all points (§7.1);
- the final T1 on the registered Stage-1 fit (§7.3: "a Wald test on the registered (Stage-1) fit");
- M2's sensitivity fit with the MUE (§7.2).

C3-4's registered share fit is NOT TESTABLE **by construction** on the final map. The Stage-1-grid M points are fixed,
and only `c2-p030-U-G` is habitable. Say so in §4.4.

### 18. NOTE: PR #520's head moved

- It moved from `7849332` (cited) to `f05c6bb`.
- The pinned blobs are unchanged: the patch `b90290b` and `build.sh` `bd51215`.
- Pinning by blob is right. CT-1 should cite blobs, not the PR head.

### 19. NOTE: O-7, drop "season of first overflow"

- No rule reads it: units are included or excluded whole.
- It is a how-far proxy of the kind the crash RULING struck (wall time).
- Keep the count only, plus a per-unit output-hash comparison with the recorded branch, which #521 recommends as a free
  reproduction audit.

### 20. NOTE: the "NOTE 10" citation is ambiguous

- In plan §5.4 and O-19, "NOTE 10" means the #512 adversary's NOTE 10 (READOUT-PLAN L610).
- COORD-RULING-517 C5 and the run adversary also have a NOTE 10, which is about stale tests.
- Cite it as "#512 adversary NOTE 10".

### 21. NOTE: tests

- **The plan's tests.** `tests/test_rbt129_stage2_plan.py` passes 28/28. Together with the Stage-1 readout tests it reads
  **119 passed**, in a clean `.[dev]` venv (Python 3.11) with **no scipy** (`import scipy` → ModuleNotFoundError).
- **The full suite.** 1057 passed, 1 skipped (see the end of this report).
- **What the tests pin:**
  - the gate, budget, locks, combination-vs-Stage-1 agreement, unit states, `keep_seed` and the five pin functions, on
    synthetic numbers.
- **What they do not pin:**
  - findings 1–3 (WORKERS, per-attempt attestation, feasible states);
  - 12 (the extreme z);
  - 13 (a)–(c).

### 22. NOTE: the expected number of overflow events makes §3 consequential

- Stage 2 is roughly 0.7–1.0 × 10⁵ unit-seasons with GO-1, against about one observed overflow per 1.0–1.4 × 10⁵.
- So ≥ 1 event is more likely than not (#521: 50–75%).
- That is why findings 1–3 are MAJOR, though no data exist yet.

## Per-C3-pin steering analysis (numbers from the public Stage-1 record)

| pin | what the alternative would have done to Stage-1 provisional §8 / outputs | prospective stake | steering verdict |
|---|---|---|---|
| **C3-1** K2 pooled VOID at N points only | Alternative (VOID every point's share layer, so the body call goes VOID at the 15 non-N habitable points): habitable 15 → **0**, T1 **NOT TESTABLE**, §8 **NO VERDICT** (run adversary NOTE 6). Pin: EARNINGS DEPEND, unchanged | the alternative would freeze NO VERDICT (T1 is frozen); the pin keeps income independent of null centring | **Not steering.** It is the registered text and the pre-data code (`call_points`). Adopt |
| **C3-2** verdict 5 tolerates one uncorroborated other EARNS | Stage 1: identical (EARNINGS DEPEND; the habitable-only line is D under both) | **Decisive** if exactly one EARNS-H survives final BH uncorroborated: pin gives **DEPENDS ONLY THROUGH HABITABILITY (D)**, literal gives **NOT RESOLVED** (finding 6) | **Not steering in origin** (pre-data code; DESIGN §8's symmetric-tolerance sentence), but **high-stakes and favourable**. Adopt only with disclosure and the V5-TOLERANCE-SENSITIVE mark, under one principle (finding 5) |
| **C3-3** §12 item 2 on where the share layer ran | Pin **AS PREDICTED (32/36; RESOLVING 0)**; pre-data script **NOT SHOWN (15/36)**; share status at N points 4/4 not RESOLVING; body SATURATED at N points 0/4 | none on calls; the scorecard is public-facing. Under the pin the item is ≥ 42/48 by construction on the final map | **Favourable and data-informed; overturns pre-data code; vacuous.** Replace (finding 5) |
| **C3-4** share model habitable-only | Pin: **NOT TESTABLE** (1 habitable M point). Pre-data code: TESTABLE, χ² 2.056, p 0.9145. No call or verdict reads either | none: secondary, outside Holm. The registered fit stays NOT TESTABLE by construction on the final map | **Not steering** (no stakes), but text-over-code, inconsistent with C3-2. Either is acceptable under one stated principle |
| **C3-5** MARGINAL on the 180–239 cohort | MARGINAL on EARNS calls goes from **8/8 to 2/8** (3/8 with `c0-p080-HP-G` at the 0.250 edge). All 6 EARNS-D cleared; both EARNS-H stay. Across all 26 points with a regime line: 26/26 → 11/26 (+1 edge) | DESIGN §9.1's rule-chosen RBT-118 points: registered measure gives **none**; amendment gives **one D-sign point** (`c0-p080-HP-G` or `c0-p030-HP-G`), no H point | **Measure natural** (latest complete cohort; the run adversary's proposal), **but its effect is fauna-asymmetric and undisclosed, and it reaches §9.1, contrary to the plan.** Adopt the measure; rule §9.1 explicitly (finding 4) |

## O-item disposition

**Who decides:** **R** = resolved here (adopt as proposed, or with the stated change); **C** = the coordinator must
rule; **Ow** = the owner.

| id | disposition | who | note |
|---|---|---|---|
| O-1 | a go is needed | **Ow** | owner decision 4 was "plan it" |
| O-2 | re-simulate 129001 S0–59 at the 12 midpoints on the build; adopt only on byte equality | **C** (+Ow for ~5–9 core-h) | finding 10 |
| O-3 | one overflow and crash rule for every continuation, ruled once in a standalone ruling binding GO-1 and Stage 2 | **C** | GO-1's gate already requires "an overflow-handling rule registered first" |
| O-4 | K-SALT does not apply at seeds 9–16 (F7's text) | **R** | finding 16 |
| O-5 | 3 M, 1 N; freed slots unused | **R** | as registered |
| O-6 | adequate for off-event identity, with additions: a forced-overflow replay at the launch WORKERS (finding 1), and finding 10's 12 S60 byte-compares and K-SALT as real-unit identity | **C** | |
| O-7 | count only; drop the season; add the output-hash comparison | **R** | finding 19 |
| O-8 | include primary is acceptable; delete reason 3; call the sensitivity exclude-known-flagged | **C** | finding 8 |
| O-9 | keep the conjunction; disclose the pass rate at small n | **C** | finding 15 |
| O-10 | keep FAIL at < 2 runs; disclose that it can VOID the point's body | **C** | finding 15 |
| O-11 | **reject the pin**; score as the pre-data code did, and print the gated-out count and the share status at N points | **C** | finding 5 |
| O-12 | replace (accepted); **§9.1 must be ruled explicitly**, with the counterfactual disclosed | **C**, and **Ow** if RBT-118's target changes | finding 4 |
| O-13 | not here; a new registration with its own cost | **Ow** | |
| O-14 | MUE = root of the combined Z(μ) (the stage-wise ordering) | **R** | |
| O-15 | Stage-1 ∪ 2a, but print only the R4 list (finding 7) | **R** with finding 7 | |
| O-16 | the half-1 test, flagged (valid under adaptive extension) | **R** | |
| O-17 | prefer axis-Voronoi; the quarter rule is acceptable if stated | **C** (minor) | finding 14 |
| O-18 | final-map M3 (DESIGN §8 "from the final map"); disclose that it is a hinge | **R** + disclosure | finding 6 |
| O-19 | frozen at the Stage-1 fit (DESIGN §7.3) | **R** | |
| O-20 | adopt | **R** | |
| O-21 | adopt | **R** | |
| O-22 | adopt, with feasible-state enumeration and the infeasible-primary print | **R** with finding 3 | |
| O-23 | adopt with a ceiling (a second attested crash at a point, or a third overall, stops) and CRASH-AFFECTED income | **C** | finding 3 |
| O-24 | HELP | **R** | |
| O-25 | yes | **R** | |
| O-26 | print and mark, **on the headline line itself**, with no "robust" bar | **R** | |
| O-27 | GO-1 fixed; the change is printed (at the final, not the interim) | **R** with finding 7 | |
| O-28 | an upper bound | **R** | |
| O-29 | as coded; it matches DESIGN "any share WINs must also favour X" | **R** | |
| O-30 | yes, and the drivers round must also carry findings 1–3 and 12–13 | **R** | |

**New items for the coordinator:**
- **N-1:** per-step GO locks and the interim's content (finding 7).
- **N-2:** amendment A-11 (finding 9).
- **N-3:** a K-SALT mismatch with an overflow is a HELP (finding 11).
- **N-4:** the WORKERS choice (finding 1).

**New item for the owner:**
- **N-5:** commit to, or decline, 2b(2a) before 2a data exist (finding 7).

## Full test suite

**1057 passed, 1 skipped, 16 warnings** (27 min 38 s), plan head `242528f`, clean `.[dev]` venv, Python 3.11, scipy absent.

## Fix-check of r2 (head `3a8587e`)

*Requested by the coordinator (`session_017eUHGNdTSsoVFAtLaJWehF`, 13:36Z).*

**What r2 contains.** The plan branch now carries:
- base `b8e6a01` merged in (`46e5019`);
- the fix round `cbb3972`;
- the log-format commits `4287d5d` and `3a8587e`.

**How I checked it.**
- Fetched by narrow refspec only. The quarantined branch was not fetched; 0 local refs name it.
- Nothing modified on the plan branch; nothing launched.
- The re-run steering analysis reads only the public `stage1_readout.txt`
  (`probe/fixcheck/c3_steering_r2.py` → `.txt`).
- I did **not** fetch `claude/rbt129-continuations-tooling`. Claims about that branch below are the plan's, checked for
  consistency only. They are: the forced-overflow record, the build blobs and sha, and the `epa_ecology.attested` match.

### Final verdict: **ADOPT** (r2, conditional on the coordinator ruling O-31 and the pending locks)

- **All 7 MAJORs are fixed**, and the fixes match S2-R1 to S2-R4.
- Every MINOR is fixed or carried, with a stated owner, to the drivers round.
- **Nothing outcome-steering entered in the fix round.** The only data-touching step is `s91_rule_chosen.py`, which
  computes per-birth values from Stage-1 S runs. Its one consequential choice (238 vs 239) is forced by code, not by
  outcome (O-31 below).
- **Three new items, none blocking:**
  - **FC-1, MINOR:** `refusal()` does not check ruled `QUARANTINE:` labels against local refs.
  - **FC-2, MINOR:** the 2B2A-before-GO-ID-2A order cannot be checked from file contents.
  - **FC-3, NOTE:** the §9.1 choice sits on a 0.0073 margin.

### Each original finding against r2

| # | sev | r2 answer | status |
|---|---|---|---|
| 1 | MAJOR | Destructor stats dropped. The record is the per-event O_APPEND `epa_overflow.jsonl`, written by every process (workers included), with `unit`/`attempt` on every event. CT-2 adds a forced overflow at WORKERS = 2; the plan reports the tooling did one: both workers logged, then attempt 1 exited native and was attested. `parse_epa_log` reads no histogram | **fixed** (the tooling record is not verified by me) |
| 2 | MAJOR | Per-attempt `start`/`exit` lines; `attested` = an overflow with the same attempt id, earlier in the log than that attempt's native exit. `crash_attested` = the last two attempts consecutive, both native, one at workers 1, **each** attested. Tests: "earlier flagged, later unattested → HELP" and "overflow after the exit does not attest" | **fixed** |
| 3 | MAJOR | `crash_ceiling` (2 at a point / 3 overall, GO-1 included); `crash_affected` + `verdict_crash_mark`; `crash_bounded_body` feasible-only, printing "primary infeasible given ckpt60". My worked case is now a test (`test_crash_bound_enumerates_feasible_states_only`) | **fixed** |
| 4 | MAJOR | "Were chosen" withdrawn. §9.1 computed and committed (`s91_rule_chosen.*`): **D `c0-p080-HP-G`, H none**; counterfactual on the censored measure: none. Strict bar at full precision. A test ties the censored column to the Stage-1 per-birth line | **fixed**; see FC-3 |
| 5 | MAJOR | S2-R1: pre-data code governs all five. C3-3 pin rejected; C3-4 reverted to all-M | **fixed** |
| 6 | MAJOR | Hinge table in §4.2; `v5_mark` puts V5-TOLERANCE-SENSITIVE on the headline; O-18 disclosed as the second hinge | **fixed** |
| 7 | MAJOR | `2B2A: COMMITTED\|DECLINED` before `GO-ID-2A`. The interim prints integrity, operational counts and the mechanical R4 list only. Separate `GO-ID-2A`/`-INTERIM`/`-FINAL` locks | **fixed**; see FC-2 and NOTE FC-4 |
| 8 | MINOR | Reason 3 deleted; `exclude-known-flagged` | fixed |
| 9 | MINOR | A-11 drafted | fixed (coordinator to rule) |
| 10 | MINOR | O-2 re-simulation REQUIRED (A-12); budget re-priced: 2a 236.6 / 443.0, total 457.7 / 856.9 (I re-derived these) | fixed (owner cost OK pending) |
| 11 | MINOR | `ksalt_outcome` | fixed |
| 12 | MINOR | `_z_upper` is now sign(t)·(−Φ⁻¹(p_tail)), clamped at ±40 both sides; tests in both signs | fixed |
| 13 | MINOR | (a) 64-hex; (b) `ruled_lines` HELPs on duplicates and empties; (c) the `QUARANTINED` list plus `QUARANTINE:` lines; (d) `check_inputs` inside `refusal`; (e) a non-stale lock test; (f), (g) carried to the drivers | fixed, except FC-1 |
| 14 | MINOR | Quarter rule kept, departures stated (S2-R4) | fixed as ruled |
| 15 | MINOR | Disclosed (§4.1, §5.3) | fixed |
| 16–22 | NOTE | All dispositioned (§13) | done |

### C3 steering re-run under the r2 pins

Source: `probe/fixcheck/c3_steering_r2.txt`, which imports r2's `stage2_readout.py` and reads the 36 Stage-1 calls as
printed.

| pin (r2) | the Stage-1 result under r2 | steering verdict |
|---|---|---|
| C3-1 (code) | unchanged: **EARNINGS DEPEND** | not steering |
| C3-2 (code, plus mark) | as printed: EARNINGS DEPEND / literal the same / no mark. One EARNS-H dropped (either one): **DEPENDS ONLY THROUGH HABITABILITY (D)** vs literal **NOT RESOLVED**, marked **V5-TOLERANCE-SENSITIVE**. Both dropped: the same under both, no mark. One left plus an EARNS-TIE: NOT RESOLVED under both | **disclosed and marked as required**; the mark fires exactly when the readings differ |
| C3-3 (code) | registered **NOT SHOWN (15 of 36; RESOLVING 0)**, matching L617. Non-registered lines: gated out 32/36 "by design; not evidence", and not RESOLVING at 4 of 4 N points | **the favourable pin is gone**; no steering |
| C3-4 (code) | the registered fit is all 9 M points (Stage-1 L414's fit); the non-registered fit is `c2-p030-U-G` only | no stakes |
| C3-5 (amended, 180–238) | MARGINAL on EARNS calls goes from 8/8 to 2/8 (both EARNS-H). §9.1: D `c0-p080-HP-G`, H none; counterfactual none | **disclosed**; measure natural; see O-31 and FC-3 |

Each of r2's stated Stage-1 effects reproduces from the public record, given the full-precision values in
`s91_rule_chosen.txt`. My r1 table, read from 2-decimal regime means on the 180–239 window, agrees on every call. The
one exception is the `c0-p080-HP-G` edge, which r2 resolves to "not" at 0.2573.

### O-31 view: **ADOPT 180–238**

- **The code check.** In `rabbitstew/ecology.py`, a child created in season s gets `born = s + 1`, age 0 and evals 0,
  and is logged in s. Each season adds 1 to its age, and it dies when `age < max_age` (60) fails.
  - So a child born in s is evaluated in seasons s+1 … s+60. Every RBT-129 block passes `--sweep-log`
    (`launch/blocks.py:113`), so the dead are logged in their death season (`ecology.py:759–763`), and its last
    lineage row is s+60.
  - `regime.py` takes `born` from the age-0, evals-0 row (= s) and counts a life complete only if
    `last_gen < last` (line 175), where `last` = 299.
  - **So a birth at 239 that lives out its 60 seasons ends at 299 and is censored. Births ≤ 238 end by 298.** The plan's
    reading is correct.
- **It is forced, not chosen.**
  - Under r1's own rule, a censored life in the window is a HELP, so the 180–239 window cannot be computed at all.
  - The only 180–239 alternative is "complete lives only". That keeps season-239 births that starved early and drops
    those that aged out, which is exactly the short-life bias A-1 exists to remove.
  - **238 is the principled cohort** whichever way it moves a number, and S2-R1 (the code's censoring definition)
    points to it.
- **Its effect.** It moves `c0-p080-HP-G`'s D from my r1 edge reading (≈ 0.250 on 180–239, complete-only, all seeds)
  to 0.2573 (180–238, income-valid seeds), and so decides §9.1's D-sign point (FC-3). It touches no call and no
  verdict.
- **The plan's stated Stage-1 effect is computed on 180–238.** `s91_rule_chosen.py` passes `windows=((180, 238),
  (240, 299))` to regime and `per_birth_uncensored`. The 8/8 → 2/8 count and 0.2573 come from that run.
- **What I did not do.** I did not re-execute it, because that needs the Stage-1 S branches restored. The committed
  test ties its censored column to the accepted record's per-birth lines.

### New items

- **FC-1, MINOR: ruled quarantine labels are not refused at the ref level.**
  - The gap. `refusal()` calls `sr.local_quarantine_refs(root)`, which matches only the Stage-1 label.
    `is_quarantined()` (Stage-1 label plus ruled `QUARANTINE:` lines) is defined but not used there.
  - The effect. Once a Stage-2 CRASHED label is ruled, a bare fetch that created its local ref would not stop a step.
  - The remedy. In `refusal`, check every `git for-each-ref` name with `is_quarantined`, and add a test. This can go in
    the drivers round.
- **FC-2, MINOR: the order "2B2A before GO-ID-2A" is not machine-checked.**
  - The gap. `refusal()` checks that both lines exist, not that `2B2A:` was committed first.
  - The remedy. Either have the coordinator open them in separate commits, with the integrity step printing both
    commits' SHAs and dates from `git log -S'2B2A:' -S'GO-ID-2A:'` and refusing if GO-ID-2A's commit is not a
    descendant of 2B2A's; or state it as a coordinator procedure in §11.
- **FC-3, NOTE: §9.1's D-sign point rests on a 0.0073 margin.**
  - `c0-p080-HP-G`'s D per-birth is 0.2573 against the 0.25 bar. If it were MARGINAL, §9.1 would pick
    `c0-p030-HP-G` (|x̄| 1.331): the same sign, and the same "D earns more on flat ground" target.
  - No call or verdict depends on it.
  - Recommendation: RBT-118's registration should see this margin beside the choice.
- **FC-4, NOTE: the interim's R4 list carries information.**
  - The interim prints which 2a points are R4-eligible (UNDECIDED, so not EARNS) and their CP, which is monotone in
    |t|. With `2B2A` fixed before 2a data, no discretionary decision remains for it to steer.
  - Optionally, print the list to the tooling session only.
- **FC-5, NOTE: residual on attestation.** The "native" exit includes a non-zero exit after a worker died on a fatal
  signal, and the log cannot prove that the fault was inside libmujoco. Under S2-R2, an overflow earlier in the same
  attempt is the ruled attestation, and that is a reasonable proxy. Keep dmesg/faulthandler as corroboration in the
  integrity record where available.
- **FC-6, NOTE: `scorecard_item2`'s `stage1_points` parameter is unused.** RESOLVING is counted over every point, as the
  pre-data `sr.scorecard` does on its map. The Stage-1-points view in §5.7 is produced by passing only the Stage-1
  points. Remove the parameter, or use it.

### Tests at `3a8587e`

- **The full suite:** (running at commit time; the count follows in the next commit), in a clean `.[dev]` venv, Python 3.11, with **no scipy** (`import scipy` →
  ModuleNotFoundError).
- **The plan's own file** has 43 tests, covering the fixes for findings 1–4, 6, 11, 12 and 13.

### Open items after r2

- **For the coordinator:**
  - O-31 (my view: adopt 238);
  - A-7 / A-11 and the standalone continuation overflow rule;
  - the lock openings (`OVERFLOW-RULE`, `BUILD-SHA256`, `GO-ID-*`);
  - FC-1 and FC-2;
  - the fix-check of the drivers round (O-30).
- **For the owner:**
  - `2B2A: COMMITTED | DECLINED` before `GO-ID-2A`;
  - O-2's cost OK (≈ 4.7 / 8.7 core-h);
  - O-13;
  - whether RBT-118 takes the §9.1 point (O-12), with FC-3's margin.

---
_Generated by [Claude Code](https://claude.ai/code)_
