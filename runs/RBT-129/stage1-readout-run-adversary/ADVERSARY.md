# RBT-129 Stage 1 readout (#517): run adversary report

*Reviewed: PR #517, head `e9d400f01f845a3887bf37c4ac5dd311de793cf9`, base `claude/new-session-4cao7d`.*

*Checked against:*
- *the plan `READOUT-PLAN.md` (plan-only `a250b72`, adopted `444a1b1`);*
- *`stage1_readout.py`, `COORD-RULING-512.md` (R1–R5) and `RULINGS-CITED.md`;*
- *the go `GO-RBT129-S1-READOUT-GO-1.md` (#516, `fe3a602`).*

*Hard rules kept:*
- *No bare `git fetch` or `git pull` was run. Every fetch used an explicit narrow refspec.*
- *The quarantined branch `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M` was filtered out of every refspec list. It was never fetched, read or restored, and no local ref names it (checked before and after the runs).*
- *Nothing on the readout branch was changed.*

## Verdict: **ACCEPT WITH CORRECTIONS**

- The committed script reproduces `integrity.txt` and `stage1_readout.txt` **byte-for-byte**, from a clean venv at the go commit.
- Every §8 input call I re-derived by hand from `stage1_readout.txt` follows the plan's decision rules and R1–R5. That covers the body calls, BH on the EARNS and TIE families, the EARNS thresholds, Holm, the support rule, R-A, R-B and the verdict precedence.
- The provisional headline **EARNINGS DEPEND** is what the registered rules produce.
- No finding is BLOCKING or MAJOR, and none changes a call.
- The corrections concern the report's prose and some descriptive outputs where the script reads the plan's text differently from how the plan says it should be read: the scorecard's item 2, the share model's scope, the meaning of MARGINAL, and M1/M4's anchor category. They should be fixed in the report, or annotated, before the coordinator rules.

Findings: 0 BLOCKING, 0 MAJOR, 5 MINOR, 8 NOTE.

## Reproduction

**Environment.**
- A fresh `git worktree` at `fe3a602`, the go commit. `stage1_readout.py` has the same blob there as at `444a1b1` and `e9d400f`.
- A fresh Python 3.11 venv: `mujoco==3.14.0`, `numpy 2.4.6`, `pytest`, and the repo installed with `pip install -e`.

**Fetching.**
- I ran `git ls-remote --heads origin 'refs/heads/ckpt/rbt-129-*'`, which lists names only. It returned 1658 heads.
- I removed every name that matches the quarantined label, case-insensitively. Exactly 1 was removed.
- I prefetched the 1475 `rbt-129-stage1-*` and `rbt-129-stage0-*` heads in batches of 25. Each batch was a `git fetch -q origin +refs/heads/ckpt/X:refs/remotes/origin/ckpt/X …` with explicit refspecs. 0 failures.
- 973 `stage1` heads came back, which matches §2.1's 973 expected labels plus the quarantined name.
- I prefetched only for speed: the script's own `fetch_label` and `branch_file` fetches ran at about 4 branches a minute, so a full pass would have taken hours. Those fetches then re-fetched the same narrow refspecs as no-ops. The script was not changed.

**Runs.**

| step | command | wall | exit | result |
|---|---|---|---|---|
| integrity | `python runs/RBT-129/stage1-readout/stage1_readout.py integrity --go RBT129-S1-READOUT-GO-1` | 23 m 48 s | 0 | `diff` against the committed `integrity.txt`: **identical** |
| readout | `python runs/RBT-129/stage1-readout/stage1_readout.py readout --go RBT129-S1-READOUT-GO-1` | 23 m 28 s | 0 | `diff` against the committed `stage1_readout.txt`: **0 lines**; sha256 `beb515aa7d745e3b98a58c4f0a116b423017476ed39a0e6fb9379e4214f50259` on both |

**Result: reproduced byte-for-byte; no difference to explain.**

## Provenance and order (check a)

- **Commits.** `0f5aee1` (23:25:00Z), `e129dcc` (23:59:19Z) and `e9d400f` (00:02:53Z) each add exactly one file, as their messages claim: `integrity.txt` (15 lines), `stage1_readout.txt` (622) and `READOUT-STAGE1.md` (537). `integrity.txt` is first. Git cannot show push times; the order and the timestamps are consistent with plan §1.
- **The script and tests are unchanged.** `stage1_readout.py` is blob `7b75cbc…` and `tests/test_rbt129_stage1_readout.py` is blob `c741b6a…`, identical at `444a1b1`, `fe3a602`, `e9d400f` and the base `02f7d47`. `READOUT-PLAN.md` is identical (`23a7add…`) at all four. `git diff fe3a602 e9d400f` touches only the three output files.
- Between plan adoption and the go, only `RULINGS-CITED.md` changed under `stage1-readout/` (the GO-ID tag). See NOTE 9 for the imported launch code that also changed.

## Findings

### MINOR 1: the §12 scorecard's item 2 counts body calls, not where the share layer ran

- **Evidence.**
  - `stage1_readout.txt:617` reads `share NOT RUN or SATURATED at most points, RESOLVING at 0-2: NOT SHOWN (15 of 36; RESOLVING 0)`.
  - `stage1_readout.py` `scorecard()` counts body calls in {NOT RUN, SATURATED, RBT-118 (not available)}.
  - Plan §0 says: "Every other point has no N arm. The share call there is NOT RUN". That is 32 of 36 points.
  - DESIGN §12 item 2 predicts the share layer "SATURATED at most points, **gated out at most** (§5.2)".
  - N ran at 4 points. RESOLVING is 0, which is inside "0–2".
- **Effect.** Under the reading in plan §0 and DESIGN, item 2 reads **AS PREDICTED (32 of 36 not run; RESOLVING 0)**, not NOT SHOWN. The script's body-call reading lets EXCLUDED, PARTIAL and NEITHER take precedence, though the share layer did not run at those points either. The scorecard is descriptive (plan §8), so no call changes. But a registered prediction is being reported as not shown.
- **Remedy.** `READOUT-STAGE1.md` §9 should keep the scripted line and add beside it, labelled: "under plan §0's reading (no N arm = share NOT RUN), 32 of 36, RESOLVING 0: AS PREDICTED". It should state that the two readings differ, and record the difference for the Stage-2 plan to pin.

### MINOR 2: the secondary share model was fitted on all 9 M points, 8 of them non-habitable, where the plan expected it not to be identifiable

- **Evidence.**
  - `stage1_readout.txt:414` reads: status TESTABLE, dropped none, χ² 2.056, df 6, p 0.9145.
  - `stage1_readout.py` `readout()` builds `share_seeds` from every point with an M arm, with no habitability filter, and passes them to `world_model(…, g0c)`. Its floor is `len(keep) + 2` = 7 + 2 = 9 points, and 9 M points are present.
  - Plan §6 says: "It is not identifiable on 1 habitable point (ruling NOTE 3)", and that it "runs under the same support rule and NOT TESTABLE conditions", which are stated over habitable points.
  - The same paragraph also says: "Its seeds are every completed M seed". The script followed that sentence.
  - Only `c2-p030-U-G` is habitable among the M points. The other 8 are EXCLUDED-H or PARTIAL-*, several on 1–2 seeds.
- **Effect.** The plan contradicts itself, and the script resolved it one way. The model is descriptive and outside Holm, so no call changes. The report's Observation 4 notes the surprise but not the cause.
- **Remedy.** The report should say that the share Wald was fitted on every completed M seed at all 9 M points. Under the habitable scope that NOTE 3 assumed it would be NOT TESTABLE. It must not be read as a world-model result.

### MINOR 3: MARGINAL at Stage 1 is a window-end censoring artifact by construction; the report leaves this as an open question

- **Evidence.**
  - `scripts/regime.py:175`: `complete = [l for l in lives if l.last_gen < last or l.culled]`. `net_per_birth` (line 191) averages complete lives only. Censored lives are counted in `censored_lives`, not in the mean.
  - In the run's last window (240–299), the lives born there that are complete are mostly those that died early. So per-birth income is biased towards short, low-gain lives.
  - The output matches this:
    - H per-birth income is −0.048 to +0.020 at every point (e.g. L8, L292);
    - the 240 window's viability is about −1 for both faunas, at every point and in every arm (L339–L373);
    - the earlier windows are mostly positive.
- **Effect.**
  - MARGINAL is set on all 8 EARNS calls, mechanically.
  - It is a flag. "MARGINAL calls count in the verdicts, flagged" (DESIGN §6.1). So no call changes.
  - Plan §3.5's wording, "complete lives … Censored lives are counted", is ambiguous on this point. The registered definition was applied as committed.
- **Remedy.**
  - Observation 2 in the report should state the mechanism (regime.py:175, last-window censoring). It should say that MARGINAL at Stage 1 carries no information about the economy, rather than leaving the question open.
  - The Stage-2 plan should register a non-censored per-birth measure, for example from window 180–239.

### MINOR 4: the headline in §1 does not carry the caveat its own §8 gives

- **Evidence.**
  - `READOUT-STAGE1.md` §1 states the provisional §8 as **EARNINGS DEPEND**.
  - Only §8 ("How far the plan's calls allow this to be read") and Observation 5 say that the EARNS-H counting set is 2 calls, both at non-habitable points:
    - `c1-p010-PW-L` is EXCLUDED-H, n = 2, SD 0.011, t +23.91 on df 1, p 0.0266 (L247);
    - `c1-p080-HP-L` is PARTIAL-D, n = 3, p 0.0335 (L290).
  - I re-derived the BH step. 23 tests; the 8th smallest p is 0.0335, against 8 × 0.10 / 23 = 0.0348; the 9th is 0.0429, against 0.0391. So `c1-p080-HP-L` passes BH by 0.0013.
  - The M2 fit behind T1 uses only the 15 habitable points (100 seeds), where there is no EARNS-H.
- **Effect.** The call is correct under R1, which counts EARNS at every point. But the headline line reads stronger than the evidence. Under the labelled non-registered habitable-only reading, the result is DEPENDS ONLY THROUGH HABITABILITY (D) (L424).
- **Remedy.** Add one sentence to the §1 headline bullet: the H side of the counting set is 2 EARNS-H at non-habitable points (EXCLUDED-H at n = 2; PARTIAL-D at n = 3), so the call is fragile to the final BH. No call change.

### MINOR 5: M1/M4 prints the anchor as its own category, against plan §4.2 item 8

- **Evidence.**
  - L377 shows `RBT-118 (not available) 1 (0.11)` as a separate body category for L.
  - Plan §4.2 item 8 says: "M4 counts it under NOT RUN with that note".
  - The scorecard (L617) does count it under NOT RUN.
  - The report's Observation 3 already notices this.
- **Effect.** Presentation only. L's NOT RUN should read 4 (0.44), with the note "including the anchor c1-p030-U-L, RBT-118 (not available)".
- **Remedy.** Correct the §1 headline table, or annotate it, in the report.

### NOTE 6: K2's pooled FAIL is applied as registered, but it is a high-leverage reading

- **Evidence.**
  - L311: K2 pooled FAIL, "the share layer is VOID for the stage".
  - `call_points` applies the pooled VOID only to points where N ran.
  - Plan §2.8 says: "at Stage 1 it changes no call". DESIGN §6.1 item 8 says: "NOT RUN: … no share call is made".
  - I agree with this reading, and the report states it (§4).
- **The alternative reading.** It would turn the pooled VOID into body call VOID at the 15 non-N points. Then:
  - habitable points would drop to 0;
  - T1 would be NOT TESTABLE;
  - §8 would read NO VERDICT.
- **Effect.** None under the registered text. Recorded so that the Stage-2 plan pins it explicitly.

### NOTE 7: the verdict-5 code tolerates one EARNS call for the other fauna

- **Evidence.** `verdicts()` tests `ex and not cset(eo)`. "Every decided EARNS call favours one fauna X" (plan §9, verdict 5) literally forbids any EARNS call for the other fauna. The code allows one uncorroborated call, using the plan's general "dominance verdicts tolerate one uncorroborated call".
- **Effect.**
  - The registered path stops at verdict 1, so there is no effect at Stage 1.
  - The habitable-only line has 0 EARNS-H, so it is unaffected too.
- **Remedy.** The Stage-2 plan should pin which reading applies.

### NOTE 8: the restore set differs slightly from §1 step 2

- Plan §1 step 2 restores "the S, ckpt60 and ksalt directories". `readout()` restores S, ckpt60, M and N, but not ksalt.
- No readout statistic uses ksalt directories; K-SALT is read at integrity with `branch_file`.
- No effect.

### NOTE 9: imported launch code changed between plan adoption and the go

- **What changed.** `runs/RBT-129/launch/stages.py` (+232/−31) and `scripts/durable.sh` (6 lines) changed between `444a1b1` and `fe3a602`, through #510's `_restore` sentinel and receipt logic. The readout imports `stages._restore`, `stages.branch_file` and `stages.expected_branches`.
- **The go's claim.** The go says #510 and #511 touch "neither the pinned trees the runs used nor the readout". Strictly, the readout's restore path did change.
- **What I verified.**
  - The fetch paths are narrow refspecs (`durable.sh:95,118`, `stages.py:2214`).
  - The output reproduces byte-for-byte from the `fe3a602` tree.
  - In a clean checkout, the change adds only crash-safety around unpacking.
- **Effect.** None.
- **Remedy.** The go statement could be worded precisely.

### NOTE 10: runner's note 1 confirmed and benign

- At `fe3a602`, in my clean venv, `tests/test_rbt129_stage1_readout.py` gives **89 passed, 2 failed**: `test_ruled_ksalt_void_go_ids_and_the_readout_input` and `test_a_pending_go_id_is_refused`.
- Both fail at the assertion that `RULINGS-CITED.md` still contains `GO-ID-PENDING: RBT129-S1-READOUT-GO-1` (test file line 1143).
- At the go's parent `14f3c67`, the same tests give **91 passed**.
- The go commit `d11b814` changes only `RULINGS-CITED.md` (1 line: `GO-ID-PENDING:` → `GO-ID:`) and adds the GO file.
- The tests are stale only because of the lock opening. The readout logic is unaffected: the script blob is the same.

### NOTE 11: runner's note 2 (checkout sha `716e2d3` on 26 census runs) is recorded as provenance only

- **How it is recorded.** `READOUT-STAGE1.md` §2 records it as relayed, not read, and "provenance only, not as an outcome". The script reads no `stage1-provenance/` file (plan §2.6; confirmed: no such path in `stage1_readout.py`).
- **Could it matter to a call?** Census runs enter Stage 1 in two ways:
  - as the 36 adopted S60s (seed 129001);
  - as the 72 K-SALT references.
- **What integrity checks.** Integrity checks their MuJoCo version (2.6, every resume entry included) and their double-write state (2.3). It does not check the code checkout. K-SALT reads 72/72 PASS, which is direct evidence that the census references reproduce the stream at seeds 129002 and 129003. It is not evidence for the 129001 adoptions.
- **Effect.** No registered rule reads checkout shas, so no call depends on it.
- **Remedy.** The coordinator should confirm, from #513 and outside this readout, that `716e2d3` has no ecology or simulation diff against the pinned tree. If it does, that is an integrity question for the adopted 129001 S60s, not a readout correction.
- **The aggregate count the runner received.** The runner also received an aggregate count of physics runs during integrity. The outputs are fully scripted and reproduce byte-for-byte, so the runner had no discretion that this count could have influenced.

### NOTE 12: integrity covers plan §2 in full; the extinct-ckpt60 exception re-derives correctly

`integrity.txt` has a line for each of the following:

| § | what is checked |
|---|---|
| 2.5 | local refs |
| 2.1 | 973/973 expected labels, and the quarantined name listed only |
| 2.2 | 973 markers, with no split for extinct-pre-merge skips |
| 2.4 | the CRASHED line, and reconciliation |
| 2.3 | the resume audit: 721 = 576 S/ckpt60 + 108 census sources (36 adopt + 72 K-SALT refs) + 37 forks, 1 accepted under the signature |
| 2.6 | the aggregate PASS only |
| 2.7 | K-SALT 72/72 with the known case's three readings; the gate re-check; K1 status |

My cross-check of the extinct-ckpt60 exception (§2.6), on the directories restored by the reproduction:
- **The comparison.** I took the set of `ckpt60` directories with no `platform.json`, and the set of units whose S history has no living member after season 60.
- **The result.** The two sets are **identical**: no mismatch, in either direction.
- **The count.** I do not repeat it, in keeping with plan §2.6 and the coordinator's sealing.

The sealed per-branch list is re-derived by `check_platforms` from `EXTINCT.txt` plus the done-marker, as plan §2.6 requires.

### NOTE 13: prose details and fragile refinements (no call changes)

- **Wording.** Report §4, "Every point is labelled PW", should read "every N point".
- **One R-A pair is fragile.** R-A pair `c1-p018-U-L` fires on clause (a), on x̄ +0.001 against −0.003 (|Δt| 0.039; L433). That is plan-conformant: a nonzero estimate has a sign. But the selection rests on noise, and the report could say so.
- **Re-derived and matching L428–L452:**
  - the R-A list: 4 G pairs, 4 L pairs and 7 C1 candidates, 3 of them shared, 12 selected, G block first;
  - R-B: 9 eligible points; 140 / 262 core-h = 9 × 8 × 300 × 23.35 / 3600 and × 43.72; anchors excluded.

## Plan conformance (check c): what I re-derived

| item | re-derived from `stage1_readout.txt` | conforms |
|---|---|---|
| body calls | ⌈5n/8⌉ = 5 for EXCLUDED; ⌈3n/4⌉ = 6 for PARTIAL; the survivor majority of invalid seeds, checked on every PARTIAL row from the merge counts | yes |
| income tests | 23 points with ≥ 2 income-valid seeds; BH at q = 0.10 rejects exactly 8 (6 EARNS-D, 2 EARNS-H), each with \|x̄\| ≥ 0.10; the TIE family rejects none (smallest TOST p 0.0472 > 0.0043) | yes |
| EARNS calls at all points (R1) | EARNS-H at the EXCLUDED-H and PARTIAL-D points is counted | yes |
| EARNS-TIE rule (R2) | no EARNS-TIE, so R2 is not engaged; the non-registered line is labelled | yes |
| support rule and NOT TESTABLE (R3) | 15 habitable points, 100 seeds; L = PW dropped; P = 5; 15 ≥ P + 2; TESTABLE; Holm T1 1.2e-13 ≤ 0.0125, T2 9.4e-6 ≤ 0.0167, T3 0.43 > 0.025, T4 = 1 | yes |
| NOT TESTABLE → Holm p = 1 | T4 enters at p = 1; nothing else is NOT TESTABLE | yes |
| "NO VERDICT at Stage 1" | not triggered: T1 is testable and rejects | yes |
| §8 precedence | verdict 1 holds (EARNS-D: 6; EARNS-H: 2). Verdict 3 (D) fails: EARNS-D is at 5/15 habitable points, but H has a pooled counting set (2 EARNS-H + 4 survival calls). Verdicts 5 (H/D) fail on the other fauna's EARNS counting set. Nothing else holds | yes |
| habitable-only line | labelled NON-REGISTERED, descriptive only; kept out of the verdict | yes |
| O-18 / R4 | 9 NOT RUN points with income UNDECIDED; anchor `c1-p030-U-L` excluded; CP on the income t; "needs its own owner GO" | yes |
| O-23 | 7 C1 candidates, all Stage-1 midpoints | yes |
| CRASHED | M reads 7 of 8; S at 129001 stays in every S statistic; no substitute; the bound is [−0.216, −0.091] with s₀ 0.500 from ckpt60 | yes |
| extinct units | read as alive 0, so the share is 0; extinct-pre-merge units excluded from share validity, counted in EXCLUDED | yes |
| K2 and CONTINGENT | pooled FAIL and per-point FAIL change no call (NOTE 6); holistic-null df 2 < 12, so CONTINGENT is not callable | yes |

---
_Generated by [Claude Code](https://claude.ai/code)_
