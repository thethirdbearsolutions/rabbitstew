# RBT-129 Stage 2 (2a refinement, 2b extension, the final map): plan (pre-data)

*Written 2026-10-03 by the Stage-2 plan author, session `session_014peDKmK8Qdna38Zav4JWNH`. The coordinator is
`session_017eUHGNdTSsoVFAtLaJWehF`. Authorised by `coordinator/OWNER-DECISIONS-2026-10-03.md`, item 4.*

*Base: `claude/new-session-4cao7d` at `c6b57ecb8cd23d57cf0ad4226f90b879a5cf3155`.*

**No Stage-2 run exists, and nothing has been launched.** This plan is committed, and an adversary reviews it, before any
Stage-2 arm, R-B arm or continuation runs. The quarantined branch `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M` was never
fetched, listed or read.

**What this author has seen (a disclosure, not a peek).**
- **Stage 2 is adaptive by design.** R-A chooses its points from the Stage-1 calls (DESIGN §4.2), so Stage 2 cannot be
  blind to Stage 1.
- The author has read the accepted Stage-1 record in full: `stage1_readout.txt`, `integrity.txt`, `READOUT-STAGE1.md`
  and its corrections.
- **Every choice below that Stage-1 outputs could have motivated is labelled DATA-INFORMED**, and says what it was
  informed by. That covers all five C3 pins (§4), because each one comes from the run adversary's reading of Stage-1
  outputs.
- No Stage-2, R-B or continuation output exists for anyone to have seen.

**Inputs read.**
- `DESIGN.md` r4 in full, and `AMENDMENT-FOUNDING.md` §7 (T1–T13);
- all of `stage1-readout/`: `READOUT-PLAN.md`, `COORD-RULING-512.md`, `COORD-RULING-517.md`, `RULINGS-CITED.md`,
  `READOUT-STAGE1.md`, `READOUT-STAGE1-CORRECTIONS.md`, `stage1_readout.txt`, `integrity.txt` and `stage1_readout.py`;
- `stage1-readout-run-adversary/ADVERSARY.md`;
- `mn-crash/RULING.md` r3, `INTEGRITY-host1.md` and `REPRO-host7.md`;
- PR #520 (`claude/rbt129-crash-diagnosis` at `7849332`: `DIAGNOSIS.md` r2 and `diag/`) and PR #521
  (`claude/rbt129-crash-diagnosis-adversary` at `4b9034a`). Both were fetched by narrow refspec;
- `coordinator/DISCLOSURE-2026-10-02.md` and `OWNER-DECISIONS-2026-10-03.md`;
- `calibration-final/DECISION.md`, `lanes/1/launch.txt`, `lanes/1-MN/launch.txt`, `lanes/1-MN/gate_table.txt`, and
  `stageP0-readout/stageP0_readout.txt` (the census layer);
- source: `launch/stages.py` (gate, K-SALT, `check_mujoco`), `rabbitstew/provenance.py` and `scripts/regime.py`.

The Chaotic issue RBT-129 was not read; this plan relies only on the repository record.

Every call, table and map carries the claim label (T4) **"among holistic and designed stream draws (founders and their
early history) that establish at W118-b"**. Every share line also carries **"under the committed rule"**, and every
verdict carries **"earns, not persists"**.

## 0. In one table

| question | answer | § |
|---|---|---|
| what Stage 2 is | 2a: R-A's 12 points at n = 8 (seeds 129001–129008). 2b: R-B extensions to n = 16 (seeds 129009–129016). Then the final map: BH once over every point, with R-B's combined p-values, and the §8 verdicts | 1 |
| 2a arms | S at 12 points × 8 seeds × 300 seasons. M at 3 points and N at 1 point (the T5 gate on the census), each 240 seasons, on the seeds valid at the merge | 2 |
| 2b | the 9 Stage-1 points are R-B **GO-1** (`RBT129-RB-GO-1`, tooled by another session; this plan only reads them). Stage-2a points take what remains of the cap of 20, at most 11, Stage-1 points first; **they need their own owner GO** | 1.2, 2.4 |
| core-h (this plan's arms; upper bounds; low / high core-s) | **2a ≤ 232 / 434. 2b for Stage-2a points ≤ 221 / 414. Total ≤ 453 / 848.** R-B GO-1 is separate (S 140 / 262, plus its own M/N) | 2.5 |
| not run | the probe leg (perception, levers, T4): **UNREADABLE** at a = 6 (`calibration-final/DECISION.md`). Retention and the sub-studies are outside Stage 2 | 2.6 |
| build | **option (c)**: guard-off instrumented MuJoCo 3.14.0 (`mujoco-3.14.0-epa-horizon.patch`, blob `b90290b`), built by the committed recipe. Byte-identical to stock; it logs every EPA horizon overflow. It is used for every Stage-2 simulation job | 3.1 |
| overflow handling (proposal; the coordinator rules) | unit states CLEAN / OVERFLOW-FLAGGED / CRASHED. **Primary: flagged units are included.** A full sensitivity map excludes them, and any call that differs is marked OVERFLOW-SENSITIVE. A crash is CRASHED only when an overflow line attests it; an unattested crash is a HELP | 3.3–3.5 |
| C3 pins | see §4. In short: (1) K2's pooled VOID reaches share calls at N points only; (2) verdict 5 tolerates one uncorroborated other-fauna EARNS; (3) §12 item 2 is read on where the share layer ran; (4) the share model is habitable-only; (5) MARGINAL uses the uncensored birth cohort 180–239 | 4 |
| Stage-1 rules | all kept. Amendments are listed with reasons and labels | 6 |
| script | `stage2_readout.py` (skeleton: every rule is a tested pure function, and the drivers come before the GO) and `tests/test_rbt129_stage2_plan.py` (28 tests). Locks: `GO-ID-PENDING:`, `OVERFLOW-RULE-PENDING:` and `BUILD-SHA256-PENDING:` in `RULINGS-CITED-S2.md` | 11 |
| open | 30 O-items | 12 |

## 1. What Stage 2 is (DESIGN §4.1, §4.2, §7.1, §11.1 item 4)

- **2a, refinement.** At most 16 new points by R-A, at n = 8, with all layers.
- **2b, extension.** At most 20 points to n = 16 by R-B (seeds 9–16, screened, F5; T8).
- **Order (M12).** 2a and 2b for **Stage-1** points run side by side. 2b for **Stage-2a** points follows 2a, from what
  remains of the cap of 20, with Stage-1 points ranked first.
- **Then the final map.** BH is applied once over all points, with R-B's combined p-values (§7.1), and then the §8
  verdicts.
- **"No other point, seed or arm may be added after Stage 1 is seen, except by a new registration"** (§4.2). This plan
  adds none.

### 1.1 The 12 Stage-2a points (`stage1_readout.txt` L428–L441, as printed)

The census g0, the census FOUNDING-FAIL flags and the C1 rows are from `stageP0_readout.txt` (registered). The holistic
fauna is census FOUNDING-FAIL at all 150 points (unscreened, T3), so that flag is not shown.

| rank | point | why (L429–L440) | layer | census g0 | designed FF | M / N (§2.3) |
|---|---|---|---|---|---|---|
| 1 | `c05-p080-U-G` | R-A (a)+(b), \|Δt\| 15.537 | income | 1.125 | no | — |
| 2 | `c1-p053-U-G` | R-A (a); also C1 | income | 0.996 | no | **M** |
| 3 | `c05-p030-U-G` | C1 | income | 1.332 | no | — |
| 4 | `c0-p018-HP-G` | C1 | income | 2.164 | no | — |
| 5 | `c15-p030-U-G` | R-A (a); also C1 | income | 1.015 | no | — |
| 6 | `c15-p010-U-G` | R-A (a) | income | 1.139 | no | — |
| 7 | `c1-p018-U-G` | C1 | income | 1.070 | no | — |
| 8 | `c2-p053-HP-G` | C1 | income | 1.120 | no | — |
| 9 | `c1-p053-U-L` | R-A (a) | income | 0.963 | no | **M** |
| 10 | `c1-p018-HP-L` | R-A (a) | income | 1.221 | no | — |
| 11 | `c1-p018-U-L` | R-A (a), \|Δt\| 0.039 (noise; corrections A6) | income | 1.174 | no | — |
| 12 | `c1-p018-PW-L` | R-A (b); also C1 | income | 0.551 | no | **M + N** |

- **Why only 12.** 4 G pairs, 4 L pairs and 7 C1 candidates fired, and 3 of them overlap. That is fewer than 16, so
  L pairs refine too (O-16).
- The script checks the record's sha256 (`beb515aa…`, as the run adversary reproduced it) and re-parses both lists
  (`check_inputs`).

### 1.2 R-B: GO-1 (Stage-1 points) and the Stage-2a remainder

- **R-B GO-1** (`OWNER-DECISIONS-2026-10-03.md` item 3; `GO-ID: RBT129-RB-GO-1`).
  - **Points.** The 9 points of L443–L451: `c0-p010-HP-G`, `c1-p010-HP-G`, `c2-p030-U-G`, `c2-p010-HP-G`,
    `c1-p030-U-G`, `c1-p030-HP-L`, `c1-p010-U-G`, `c1-p010-HP-L` and `c1-p010-U-L`.
  - **Arms.** S on seeds 129009–129016, priced at 140 / 262 core-h, plus M/N as its own tooling gates them.
  - **Gates.** Option-(c) build, and the overflow rule registered first.
  - **Who does what.** Another session tools and launches it. **This plan launches none of it and does not re-price
    it.** Its units enter this plan's final map (§5) under the same unit-state and overflow rules (§3), which this plan
    asks GO-1's tooling to adopt so that one rule covers every continuation (O-3).
  - `c2-p030-U-G`'s M stays **CRASHED at 129001**, so its M reads 15 of 16, with no stand-in (RULING item 2).
- **How R-B combines with Stage 2.**
  - **At each extended point** the final income p is the inverse-normal combination Z = (Z₁ + Z₂)/√2. Half 1 is seeds
    1–8 and half 2 is seeds 9–16. Each half's signed z is the inverse normal of its one-sided t p-value (Lehmacher &
    Wassmer; R4 (iii)).
  - **The TOST** combines each one-sided z by the same rule, and EARNS-TIE needs both combined tests to pass.
  - **The |x̄| ≥ 0.10 bar** is read on the pooled 16-seed mean.
  - **The same combination applies to y′** where an extended point has a share test (§5.3).
  - **Where it is computed.** `combined_p`, which reproduces `stage1_readout.stage2_income_call`'s decisions (a test
    pins the two together).
- **The Stage-2a remainder.** After 2a's interim readout (§5.1), Stage-2a points are R-B-eligible:
  - **by R4 as ruled:** a body call UNDECIDED or CONTINGENT, or NOT RUN with an UNDECIDED income call. Anchors are
    never eligible;
  - **ranked by CP** (`conditional_power`; on the income t at NOT RUN points);
  - **capped at 20 − 9 = 11** (`rb_stage2a_slots`).
- **The Stage-2a extension needs its own owner GO.** GO-1 names the 9 Stage-1 points only. The interim readout prints
  that list and its core-h.

## 2. What runs

### 2.1 Stage 2a, the S arm

- **Points and seeds.** 12 points × seeds 129001–129008, with the salts of `lanes/1/launch.txt`: 129002 (1, 0),
  129003 (2, 0), 129007 (1, 0), 129008 (1, 0), and (0, 0) for the rest.
- **Arms.** S60 → ckpt60 → S, to season 300 (seasons 0–299). The world block comes from `blocks.py`'s one table
  (§5.6 item 5), under `--fair --eat-from root --eat-rule surface`, as Stage 1 ran.
- **129001 resumes from the census S 0–59 at the same point** (T10, as at Stage 1). The census ran all 150 points, the
  12 midpoints included. That S60 was simulated on stock pip 3.14.0 and is **not scanned**; it is labelled so (§3.6).
- **K-SALT (F7)** at 129002 and 129003, as at Stage 1: 24 point-seeds, compared against the census references. It is a
  file comparison. The F7 de-duplication ruling (`RULINGS-CITED.md`) applies.
- **Every Stage-2 simulation job runs on the option-(c) build** (§3.1), the census-adopted S60s excepted.

### 2.2 What is measured

These are exactly Stage 1's S-arm measurements (READOUT-PLAN §3):
- validity, extinction and survival;
- the income flow and x_j;
- the per-birth income (amended for MARGINAL, §4.5);
- the regime readout on every arm, per 60-season window;
- the S descriptive lines.

M and N add y′, the one-world column, the interference table, g0 and the VARIANCE-DRIVEN inputs.

### 2.3 Stage 2a, the M/N gate (DESIGN §5.2 as amended by T5 and the #500 ruling, unchanged)

The gate is applied to the 12 points (`mn_gate`; a test reproduces it from the committed census).
- **M.** Census g0 ≤ 1.0, the designed fauna not census FOUNDING-FAIL, not an anchor; lowest g0 first, **up to 4**.
  - The result is **`c1-p018-PW-L` (0.551), `c1-p053-U-L` (0.963) and `c1-p053-U-G` (0.996).** The other 9 points have
    census g0 > 1.0.
- **N.** At M-admitted points with census g0 ≤ 0.8, **up to 2**.
  - The result is **`c1-p018-PW-L`** only.
  - The null is holistic on odd seeds and designed on even seeds.
- **Seeds.** Each fork runs only on the seeds valid at the merge (both faunas alive at 59 in S, read from ckpt60). A
  point with no valid seed frees its slot (T5, DATA-INFORMED at Stage 1, kept). No other point is eligible, so a freed
  slot goes unused.
- **The counts were seen at emission.** As at Stage 1, the emitter reads the valid-at-merge counts after the S60s. They
  are the gate's registered input, recorded in a gate table (mn-emitter ruling item 7).
- **Arms.** M is `--merge-after 60 --pooled-capacity 120`, forked from ckpt60, seasons 60–299. N is `--merge-null K`,
  forked the same way.

### 2.4 Stage 2b for Stage-2a points (needs its own owner GO)

- **Points.** At most 11 (§1.2), chosen by the interim readout.
- **Seeds.** 129009–129016 at the screened salts: 129010 (1, 0), 129016 (1, 0), and (0, 0) for the rest.
- **Arms.** S for seasons 0–299. There is no census S60 for these seeds, so every S60 is fresh.
- **M/N.** Gated by the same T5 rule within DESIGN's R-B caps: M at ≤ 6 R-B points and N at ≤ 2, shared with GO-1,
  Stage-1 points first (§5.2). Of the 2a points, only the three M points above can be admitted.
- **K-SALT.** A seed-9–16 point has no census reference, so K-SALT does not apply there. GO-1's tooling decides the same
  question for its 9 points, and this plan adopts its rule (O-4).

### 2.5 Budget (`budget()`; the pilot's 23.35 / 43.72 core-s per arm-season, T11)

| block | arm-seasons | core-h low / high |
|---|---|---|
| 2a S: 12 × (7 × 300 + 1 × 240 adopted) | 28,080 | 182.1 / 341.0 |
| 2a M: ≤ 3 points × 8 × 240 | ≤ 5,760 | ≤ 37.4 / 70.0 |
| 2a N: ≤ 1 point × 8 × 240 | ≤ 1,920 | ≤ 12.5 / 23.3 |
| **2a total** | | **≤ 231.9 / 434.3** |
| 2b for 2a points, S: ≤ 11 × 8 × 300 | ≤ 26,400 | ≤ 171.2 / 320.6 |
| 2b for 2a points, M: ≤ 3 × 8 × 240 | ≤ 5,760 | ≤ 37.4 / 70.0 |
| 2b for 2a points, N: ≤ 1 × 8 × 240 | ≤ 1,920 | ≤ 12.5 / 23.3 |
| **2b(2a) total (own GO)** | | **≤ 221.0 / 413.9** |
| **this plan, total** | | **≤ 453.0 / 848.2** |
| R-B GO-1 (not this plan's; for reference) | | S 140 / 262, plus its M/N |

**What the bounds assume.**
- M/N are priced at every seed. They run only on the valid seeds.
- 2b(2a) is priced at all 11 slots and at every M-eligible point.

**Not included.** The build's identity checks (the tooling PR, §3.1) and the owner's Stage-1 M/N overflow scan
(~100 core-h, owner decision 1).

**Compared with the design.** DESIGN §11.2 budgeted 2a at ≤ 337–450 and 2b at ≤ 413–557, at 20/25 core-s, before the
pilot re-costing.

### 2.6 What does not run in Stage 2, and why

- **The probe leg, the planted set and the R8 levers.** The K3 calibration ruled the perception layer **UNREADABLE at
  a = 6: no seeable holistic control**, and "no probe leg launches" (`calibration-final/DECISION.md`; §12's S-2
  statement, binding). So in Stage 2 and in the final map:
  - every perception call reads **NOT MEASURED (perception layer unreadable at a = 6)**;
  - **T4 is NOT MEASURED** and enters Holm at p = 1, permanently (§5.5);
  - **LEVER is not evaluated.** The levers are measured on the probed members (§5.3e), and none are probed. Every EARNS
    and WIN call is counted with that caveat printed, as at Stage 1. Whether a lever-only leg should be registered is
    O-13;
  - the perception verdicts read **PERCEPTION NOT MEASURED** (§8's validity clause).
- **Retention (§6.4)** runs at Stage-1 G points only, and depends on PAYS. It is not a Stage-2 arm, and this plan does
  not schedule it.
- **The sub-studies (§9).** RBT-118's and RBT-116's rule-chosen points are chosen after Stage 1, under their own
  registrations.
- **The anchors.** They are never re-run or extended (R4 (ii)), so they stay "RBT-118 (not available)" unless RBT-118
  delivers.

### 2.7 Gates before any Stage-2 launch

1. This plan merged, after its adversary and the coordinator's ruling.
2. The **continuation build** registered (§3.1), with `BUILD-SHA256:` ruled in `RULINGS-CITED-S2.md`.
3. The **overflow-handling rule** ruled, with `OVERFLOW-RULE:` set.
4. The **launch tool** (the continuations tooling PR) does all of the following, after its own adversary pass:
   - emits the 2a lanes;
   - refuses any libmujoco whose sha256 is not the registered one (§3.1);
   - captures each unit's build record (§3.2);
   - keeps RULING item 6's version check.
5. The owner's go for Stage 2a. The owner approved planning, not launching (O-1).
6. Stage 2b for Stage-2a points: a further owner GO after the interim readout.

## 3. The continuation build and how overflows enter the statistics

### 3.1 The build (owner decision 2: option (c))

- **Source.** google-deepmind/mujoco tag 3.14.0 (`9ecbb9d7b5ee623f54745638d36799ff90e6f7cd`) plus
  `runs/RBT-129/mn-crash/diag/mujoco-3.14.0-epa-horizon.patch` (blob `b90290bdc14400b08915b764f76382885f6daf75`, PR #520
  at `7849332`).
- **Recipe.** `diag/build.sh` (blob `bd5121519ba48181b47db9d735ae3815ad478d86`): clang/LLD 18.1.3, cmake 3.28.3 and
  ninja 1.11.1 on Ubuntu 24.04. Release, MuJoCo's defaults, and `-ffile-prefix-map`.
  - **At a fixed absolute WORKDIR.** ThinLTO symbol names depend on it, so the sha is reproducible only there.
  - The wheel's `libmujoco.so.3.14.0` is replaced; the bindings are unchanged.
- **Run setting: guard off.** `RBT_HZN_GUARD` is unset. **A launch with `RBT_HZN_GUARD=1` is refused**, because the
  guard changes the contact at an event (#521 MAJOR 4).
- **Each unit sets** `RBT_HZN_STATS=<unit dir>/hzn_stats.txt`, and its stderr is filtered so that the `RBT_HZN overflow`
  lines go to `<unit dir>/hzn_overflow.txt`.
- **Artifacts from the continuations tooling PR.** That PR does not exist yet. These are its deliverables, with an
  adversary pass:
  - **CT-1.** The pinned image, WORKDIR and recipe, and the produced sha256. The coordinator enters the sha as
    `BUILD-SHA256:`.
  - **CT-2.** Byte identity to stock pip 3.14.0 (`diag/identity.sh` or its successor):
    - on **at least 4 S units and 4 M units, plus 1 N unit**, across c ∈ {0, 1, 2} and the three layouts;
    - **≥ 30 seasons each**;
    - built on the launch image.

    The owner's condition is: "its byte-identity to stock must be shown" (O-6).
  - **CT-3.** The launch refusal: the loaded `libmujoco.so.3.14.0`'s sha256 must equal `BUILD-SHA256`, and `GUARD` must
    be unset. This is beside `check_mujoco` (RULING item 6). The sha is recorded in each unit's record.
  - **CT-4.** The build record per unit (§3.2), saved with the unit's snapshots.
- **Why (c) and not (b).** The owner chose (c). It keeps stock physics, undefined behaviour included, so Stage 2 stays
  comparable with Stage 1 everywhere. What it adds is that every overflow is logged.

### 3.2 The build record per unit (integrity, not outcome)

- **`hzn_overflow.txt`** holds every `RBT_HZN overflow: nedges …` line. Nothing else from stderr is kept.
- **`hzn_stats.txt`** holds one histogram line per process (`epa_iterations N overflow K hist …`).
- **`libmujoco.sha256`** holds the sha of the library that was loaded.

Integrity reads these three files only (`parse_hzn`). They carry no season, fauna or member.

### 3.3 Unit states (`unit_state`)

| state | when | how it enters |
|---|---|---|
| **CLEAN** | done; a build record; 0 overflow lines; stderr and stats counts agree | as any unit |
| **OVERFLOW-FLAGGED** | done; ≥ 1 overflow line (stock behaviour past the event: undefined; it may be silently corrupted) | §3.4 |
| **CRASHED** | RULING item 5's counting rule (two attempts in a row fault inside libmujoco, one at WORKERS=1), **and** an overflow line precedes the fault | §3.4–3.5 |
| HELP | a crash with no overflow line (a new mechanism); a done unit with no build record; counts that disagree; a malformed line; a recorded sha that is not the registered one | nothing further is read until the coordinator rules |
| **UNSCANNED** | a Stage-1 unit (stock build) that no scan has covered | read as it stands, and counted (§3.6) |

### 3.4 How flagged and crashed units enter every Stage-2 statistic (PROPOSAL; the coordinator rules on it)

- **The primary rule is `include-flagged`.**
- **The sensitivity rule is `exclude-flagged`.** Under it, a flagged unit is removed from n exactly as a ruled K-SALT
  VOID seed is (O-7).
- **The whole final map is computed twice**, once under each rule. Every call, family decision, map statistic and
  verdict that differs between the two is printed as **OVERFLOW-SENSITIVE**, with both values.
- **The verdict line carries the label** if its verdict differs.
- **The integrity section prints the counts** of flagged and crashed units per arm.

**Why include-flagged is primary.**
1. Stage-1 units ran on the same stock physics and were **not** scanned. They enter the map as they stand. Including
   flagged Stage-2 units keeps one rule across the map.
2. Overflows come with deep overlaps, which depend on bodies and worlds (#520 (d); c2 and sibling geometry). Dropping
   them would be **informative missingness**, against the registered "nothing winsorised or re-weighted".
3. The build is stock physics. A flagged unit is what the registered pin produces.

The sensitivity rule guards against the cost of all this: a flagged trajectory may be corrupt after the event.

| statistic | the flagged unit (primary) | a CRASHED unit |
|---|---|---|
| S validity, survival (EXCLUDED, PARTIAL, NEITHER) | included | removed from n (as a K-SALT VOID, O-7). The call is also evaluated with the seed restored under every survival state it could have had (`crash_bounded_body`) and marked **CRASH-SENSITIVE** if they differ. The merge validity is known from ckpt60 when the crash is after 59 |
| income x_j, EARNS/TIE tests, R-B CP, M2 sensitivity, M3, M7, cross-correlation | included | removed; no imputation; "income has no logical bound" |
| per-birth income, MARGINAL, regime | included | removed |
| M: y′ (descriptive or tested), one-world column, interference (S paired on M's seeds), g0 and RESOLVING, VARIANCE-DRIVEN | included | removed. The M row reads `M k of n (j CRASHED)`. y′ prints the **bound under arbitrary missingness** (ruling item 4's convention, s₀ from ckpt60) |
| N: K2 per point, K2 pooled, the pooled null σ̂² and df, CONTINGENT | included | removed; the K2 counts are over completed runs |
| §8 verdicts, M1, M4, the scorecard | from the calls above | a unit state, not a call (RULING item 1). It enters no M1 or M4 category |

The script implements the rule as `keep_seed(state, mode)`. `refusal()` refuses to run until `OVERFLOW-RULE:` reads
one of the two values.

### 3.5 CRASHED for continuations: the proposed changes to RULING items 1, 5 and 6

These apply to continuations only. They are proposed here for the coordinator's draft ruling, and **they apply to
nothing that has run**.

- **Item 5's "the same instruction".** This becomes **"an `RBT_HZN overflow` line precedes the fault in the attempt's
  captured stderr"**. The diagnosis showed that the fault site moves with the process layout for this one bug (#520 (b)).
  The two-attempt rule and its WORKERS=1 clause stay.
- **An attested CRASHED unit is the known bug, not a pattern.** It therefore does **not** trigger item 5's stop of
  lane issuance. An **S-arm** attested crash is a unit state with the crash bound of §3.4, **not** a stop of the hive.
- **An unattested crash keeps item 5 exactly as registered.** M/N issuance stops. S stops the hive.
- **Item 2 stands.** There is no re-run, no substitute seed, and no 6N or guarded continuation of any CRASHED unit.
- **Item 6 is extended.** The version check is unchanged, and the registered sha is added to it (CT-3).
- **Quarantine (item 3)** applies to every new CRASHED unit's partial branch. The script holds a list of quarantined
  labels. It is extended by ruling only.

**The label.** These are outcome-blind with respect to Stage 2. They are informed by the crash diagnosis, not by any
Stage-1 outcome.

### 3.6 Stage-1 units in the final map

- **Which are UNSCANNED.** Stage-1 S, M and N units, and the census S60s adopted at 129001, are **UNSCANNED**. The one
  exception is any unit covered by the owner's overflow scan (decision 1: M/N first; the S scan is decided later).
- **What the scan does.** A scanned unit with an overflow becomes OVERFLOW-FLAGGED in the final map, under the same rule
  as Stage 2. A scanned unit without one becomes CLEAN. The scan's record format must give, per unit, the overflow count
  and the season of the first overflow only (O-7).
- **What the final integrity section discloses** (#521 finding 2): "a known memory-safety bug (EPA horizon overflow) can
  corrupt without crashing; the UNSCANNED units were not checked". It gives counts by arm.

## 4. The five COORD-RULING-517 C3 items, pinned before data

**All five are DATA-INFORMED in origin.** The run adversary raised each one after reading Stage-1 outputs, and this
author has read them too. For each pin the plan says:
- the registered text;
- the pin;
- what the Stage-1 output showed;
- why the pin is not chosen for its Stage-1 effect.

The other reading is always printed as a labelled, **non-registered**, descriptive line.

### 4.1 C3-1: the scope of K2's pooled VOID (NOTE 6)

- **The registered text.** §5.5 K2: "pooled: the share layer is VOID for the stage". §6.1 item 8: "NOT RUN … no share
  call is made".
- **The pin** (`share_void`).
  - The pooled VOID makes VOID **the share call at every point where N ran** and whose N runs belong to a stage whose
    pooled K2 failed.
  - **Which stage.** A 16-seed point's share test uses both halves' N runs, so it is VOID if **either** stage failed.
  - **What it never touches:**
    - a point without N (no share call exists there);
    - an income call;
    - a survival call;
    - habitability, except through §6.1 item 3 at an N point that items 1–2 do not settle first.
  - **The stages** are `1`, `2a` and `2b` (2b includes GO-1's N runs).
  - **Stage 1's pooled FAIL stands** (L311). It VOIDs the share call of any Stage-1 point with N, including that point's
    16-seed test if R-B extends it.
- **K2's other clauses are kept from Stage 1.**
  - Pooled PASS: |mean| < 0.05 **and** the t test not rejected (O-12's conjunction).
  - Fewer than 2 runs in a stage reads FAIL (`k2_pooled`).
  - Per point: BH and |mean| ≤ 0.15, with the size bar alone at 1 run.
  - The equivalence reading of O-12 (NOTE 11: "to be ruled before Stage 2") is **not** adopted. It is O-9.
- **Why.**
  - This is the registered text. The pooled K2 is a check on the null, and the null runs only at N points.
  - The alternative turns a null-centring failure into VOID **income** points, which the registered text never does.
    Under it, T1 would have been NOT TESTABLE at Stage 1, so adopting it now would let a known outcome choose a rule.
  - The run adversary agreed with this reading (NOTE 6).

### 4.2 C3-2: verdict 5's tolerance of one other-fauna EARNS (NOTE 7)

- **The registered text.** §8 verdict 5 reads "every decided EARNS call favours one fauna X, **with no counting set for
  the other**". The paragraph on opposite-sign sets adds that the dominance verdicts "tolerate **one** uncorroborated call
  for the other fauna".
- **The pin.** The committed code's reading (`stage1_readout.verdicts`) stands.
  - One uncorroborated other-fauna EARNS call does **not** fail verdict 5. Two calls do, and so does one corroborated by
    M3.
  - **Any EARNS-TIE fails it** (R2).
  - Any share WIN for the other fauna fails it (share "can veto").
- **Why.**
  - Verdict 5's own clause, "no counting set for the other", is defined by §8 as tolerating one call. The literal "every
    … favours X" then carries R2's EARNS-TIE exclusion.
  - Verdict 3 tolerates one call by the same rule. Holding verdict 5 to a stricter bar than verdict 3 would make the
    weaker claim harder to reach.
  - This is the code that the readout adversary passed and that the run adversary reproduced.
- **What Stage 1 showed.** The registered path stopped at verdict 1, and the habitable-only line had no EARNS-H. So
  neither reading changed a Stage-1 line.
- **Printed.** The literal reading, as a non-registered line (`verdict5_literal`).

### 4.3 C3-3: §12 scorecard item 2 (MINOR 1)

- **The registered text.** "SATURATED at most points, **gated out at most (§5.2)**; RESOLVING at 0–2 Stage-1 points".
- **The pin** (`scorecard_item2`). Count **where the share layer ran, not body calls**.
  - The numerator is the points with no N arm (gated out, anchors included), plus SATURATED points.
  - The denominator is every point of the map being scored.
  - **AS PREDICTED** when the numerator exceeds half of the denominator and RESOLVING (over Stage-1 points) is ≤ 2.
    **NOT SHOWN** otherwise.
  - N points settled by survival are in the denominator only.
  - The final scorecard prints it for the Stage-1 points and for the final map.
- **What Stage 1 showed.** This reading gives AS PREDICTED (32 of 36; RESOLVING 0). The script's reading gave NOT SHOWN
  (15 of 36).
- **Why, even though it is the favourable reading.**
  - "Gated out" is §5.2's gate, which is about where N runs, not about the body call.
  - Plan §0 already read NOT RUN that way.
  - The scorecard is descriptive and changes no call.
- **Printed.** The body-call reading, as the non-registered line.

### 4.4 C3-4: the share model's scope (MINOR 2)

- **The registered text.** §7.2 M2 lists the share model and the income model. It then says "**Registered fit:** the
  Stage-1 grid only …, valid seeds, habitable non-VOID points". Stage-1 plan §6 said both "every completed M seed" and
  "not identifiable on 1 habitable point".
- **The pin** (`share_model_points`). The registered share fit uses:
  - points **on the Stage-1 grid** with an M arm that are **habitable** (not EXCLUDED, NEITHER, PARTIAL or VOID);
  - their completed M seeds;
  - R3's support rule and NOT TESTABLE conditions, with its point floor counting census g0 as a term (FC-NOTE 3);
  - its Wald, which stays secondary and outside Holm.

  The sensitivity fit adds the Stage-2a M points under the same filter.
- **Why.** The "Registered fit" sentence follows both model bullets, and habitability is how §8 and M2 define the
  modelling population. Fitting a world model on non-habitable points mixes survival with the share change.
- **What Stage 1 showed.** The all-M fit was p 0.9145 (L414). Under the pin it is NOT TESTABLE (1 habitable M point).
  No call depends on either.
- **Printed.** The all-M fit, labelled non-registered.

### 4.5 C3-5: a non-censored per-birth income (MINOR 3)

- **The registered text.** §6.1 MARGINAL: "either fauna's net income per birth at the point is below the living cost
  (0.25)". READOUT-PLAN §3.5 reads it from `regime.py`'s window 240–299, which averages complete lives only, so it is
  censored towards short lives (`regime.py:175`; corrections A3).
- **The amendment** (`per_birth_uncensored`). It **replaces** that measure for MARGINAL, at every point of the final map,
  Stage-1 points included.
  - **The cohort.** `regime.py`'s window **180–239**, i.e. lives **born** in 180–239.
  - **Why that cohort is uncensored.** At max age 60 every such life ends by season 298, before the last season 299. So
    the cohort is complete in a 300-season S arm. A censored life there is a HELP.
  - **The value** is `net_per_birth` + 0.25 (O-5's reading of "net", kept).
  - **The aggregation** is the mean over the point's income-valid seeds that have one (FC-SHOULD 3).
  - **The rest is unchanged.** MARGINAL is the same bar (< 0.25), and it counts, flagged.
  - **Printed beside:** the 240–299 censored figure, labelled "censored (Stage-1 measure)".
- **Why replace rather than accompany.** A flag that is set at every point by construction carries no information
  (A3). DESIGN's purpose for it is to mark income compression near viability.
- **The label.** DATA-INFORMED. Stage 1 showed MARGINAL on all 8 EARNS calls.
- **Effect.** MARGINAL changes no call and no verdict. It is used by §9.1's rule-chosen RBT-118 points (non-MARGINAL),
  which were chosen after Stage 1, so this does not reach them (O-12).

## 5. The interim readout and the final map

### 5.1 The interim (2a) readout: R-B's Stage-2a list

- **When.** After 2a's units are complete and pass integrity.
- **What it computes.** The 2a points' calls with Stage 1's rules.
- **BH.** It runs over the **Stage-1 ∪ Stage-2a** points at n = 8 (provisional, K = all tested points; O-15).
- **What it prints:**
  - the R-B Stage-2a list (R4 eligibility, CP ranking, ≤ 11) and its core-h;
  - a re-printed, provisional view of the Stage-1 points' calls. **It does not alter GO-1's list**, which the owner fixed.
- **No verdict.** The interim prints none, except a "PROVISIONAL (Stage 1 + 2a)" §8 line.

### 5.2 The final income families (`point_income_test`, `final_income_calls`)

- **Which points.** Every point of the map with ≥ 2 income-valid half-1 seeds: Stage-1 and Stage-2a.
- **Not extended:** the n = 8 two-sided t and TOST.
- **Extended with ≥ 2 income-valid seeds in each half:** the combined p of §1.2.
- **Extended with < 2 in half 2:** the half-1 test, flagged "half 2 short" (O-16).
- **BH** runs once over all of them, at q = 0.10, in the EARNS family and in the TIE family. The calls are by
  `income_call`, with |x̄| ≥ 0.10 on the pooled mean.
- **The cross-point correlation** is printed per layer. If its mean exceeds 0.3, BY is printed beside BH, and a call that
  holds under BH only is marked so.
- **Body calls at extended points** use n = 16 thresholds (⌈5n/8⌉ = 10; ⌈3n/4⌉ = 12), with n reduced by VOID or CRASHED
  S seeds.

### 5.3 Share families

- **Membership.** As at Stage 1 (ruling item 4(a), O-22): only points where N ran and whose body call is not settled by
  items 1–3.
- **The share t and TOST** at an extended point use the same combination on y′.
- **CONTINGENT** stays callable only at a holistic-null df ≥ 12 (O-9 pin). Its df pools the null per kind over every
  N point of the map, plus RBT-118's anchor nulls if delivered.
- **RESOLVING** only where M and N both ran, at both g0 bounds, with the replica scaled by `pilot_constants.json`.
- **VARIANCE-DRIVEN is wired** (FC-NOTE 5). Every share WIN gets `variance_driven` on its M seeds, and a VD WIN is its
  own category, not a WIN in §8.
- **LEVER** stays "not evaluated" (§2.6).

### 5.4 Map statistics

- **M1.** Over every point. Stage-2a points are listed in their own block. The anchor is counted under NOT RUN, with its
  note (corrections A2).
- **M2 income, registered.** The Stage-1 grid, seeds 1–8, and Stage-1 habitability. **Its values are final at Stage 1**
  (L402–L412; NOTE 10), so the final map re-prints them.
  - **Sensitivity fit.** It adds the Stage-2a points and the R-B extensions. At extended points it uses the **median-
    unbiased estimate**: the root in μ of the combined Z(μ) (`median_unbiased`; O-14).
  - Both the registered and the sensitivity fit take seed-level x at their final n.
- **M2 share.** As §4.4.
- **M3.**
  - **Which rows.** Every (c, L, s) row with ≥ 2 price levels among its habitable non-VOID points. Stage-2a points
    included, they give `c05` and `c15` rows and the p018/p053 levels.
  - **Seeds.** Seed-level x at final n.
  - **What it corroborates.** It is the M3 that corroborates a single call in §8.
  - **Printed beside:** the Stage-1-only M3 (O-18).
- **M4.** Equal weights over the 27 G points and the 9 L points, then "with the Stage-2a points added" (`m4_weights`). A
  midpoint takes one quarter of each parent's current weight, then the weights are normalised per smell block (O-17).
- **M5.** NOT MEASURED.
- **M6.** κ over decided share calls. It prints "no decided share call" if there are none.
- **M7.** Sign changes of x̄ along every price and clutter row of the **final** map, gaps printed.

### 5.5 T1–T4 and Holm

- **T1–T3** are the registered Stage-1 fit's: T1 χ² 69.704, p 1.18e-13; T2 z +4.43; T3 z −0.79 (L410–L412).
- **T4 is NOT MEASURED** (§2.6), and enters at p = 1.
- **So the final Holm equals the Stage-1 provisional Holm:** T1 and T2 rejected; T3 not.
- The final map states this, so that no one reads Holm as re-run.

### 5.6 The §8 verdicts on the final map

- **The logic.** `stage1_readout.verdicts` is used unchanged: R1, R2, R3 and the C3-2 pin, over the final calls.
- **Corroboration** comes from §5.4's M3.
- **LEVER** is "not evaluated" (every call is counted, with the caveat). **VD** is wired.
- **What it prints:**
  - the verdict, in precedence order, with those that also hold printed beneath;
  - the two Stage-1 non-registered lines (habitable-only; verdict 5 ignoring EARNS-TIE);
  - the C3-2 literal line;
  - under the sensitivity rule (§3.4), the verdict, marked OVERFLOW-SENSITIVE if it differs.
- **Perception:** PERCEPTION NOT MEASURED.
- **The label.** Every verdict carries the claim label and "earns, not persists".
- **A known fragility.** The Stage-1 headline rested on an H counting set of exactly 2 EARNS-H, both at non-habitable
  points, and one passed BH by 0.0013 (corrections A1). The final BH, with a larger K, decides it. This plan sets no
  rule because of that.

### 5.7 The §12 scorecard

Stage 1's `scorecard` is used with the C3-3 pin, and items 4 and 6 read NOT MEASURED. It is printed for the final map,
and for Stage-1 points beside it.

## 6. Stage-1 registered rules: kept, and the amendments

**Kept unchanged:**
- **The core rules.** Every threshold, margin, family and procedure of READOUT-PLAN §3–§9.
- **The rulings:** R1–R5, O-1 to O-23, and the crash ruling's items 1–4 and 7.
- **The F/T texts:** T4–T8 and T10.
- **How it is done.** By importing the committed `stage1_readout.py` (blob `7b75cbc5f3dc35c85869a27780713b870ba9c1d1`)
  rather than re-implementing it.

**Amendments and new rules:**

| id | what | reason | label |
|---|---|---|---|
| A-1 | MARGINAL's per-birth measure: the uncensored 180–239 cohort (§4.5) | the Stage-1 measure is censored by construction | DATA-INFORMED |
| A-2 | the share model's scope: habitable, Stage-1 grid (§4.4) | it resolves the plan's self-contradiction | DATA-INFORMED |
| A-3 | §12 item 2 read on where the share layer ran (§4.3) | DESIGN's words | DATA-INFORMED (favourable reading; descriptive) |
| A-4 | verdict 5 tolerates one uncorroborated other-fauna EARNS (§4.2) | §8's own definition; parity with verdict 3 | DATA-INFORMED in origin; no Stage-1 effect |
| A-5 | K2 pooled VOID scope (§4.1); O-12 kept as the conjunction | the registered text | DATA-INFORMED in origin |
| A-6 | unit states CLEAN, OVERFLOW-FLAGGED, CRASHED and UNSCANNED, and the include/exclude rule (§3.3–3.4) | owner decision 2 | diagnosis-informed; outcome-blind to Stage 2 |
| A-7 | RULING items 5 and 6 for continuations (§3.5) | the fault site moves (#520 (b)) | diagnosis-informed; proposal for the coordinator |
| A-8 | the interim BH over Stage-1 ∪ 2a for R-B's Stage-2a list (§5.1) | §4.2 M12 needs a 2a list; DESIGN gives no family | new, outcome-blind |
| A-9 | "half 2 short" (§5.2), and the MUE definition (§5.4) | DESIGN names them without defining them | new, outcome-blind |
| A-10 | M4's midpoint weights (§5.4) | DESIGN names them without defining them | new, outcome-blind |

**Consequences, not amendments:**
- T4 is NOT MEASURED, so the final Holm equals Stage 1's.
- LEVER is not evaluated.
- Perception is NOT MEASURED.

## 7. Integrity (the `integrity` step; before any number is read)

The checks mirror READOUT-PLAN §2:
- **branches and done-markers**, against the continuation lane files;
- **the resume audit**, `written_twice`, on every Stage-2 directory;
- **the build record**, for every simulation unit (§3.2–3.3):
  - the recorded library sha256 equals `BUILD-SHA256`;
  - `hzn_stats.txt` is present;
  - the stderr and stats counts agree;
  - the printed figures are counts of CLEAN, FLAGGED and CRASHED units per arm, and nothing else;
- **K-SALT** at 2a's 24 point-seeds;
- **the gate re-check**: the valid-at-merge counts match the 2a gate table;
- **the quarantine refusal**, for the Stage-1 label and every new CRASHED label;
- **MuJoCo provenance**: 3.14.0 on every record and every resume.

**Any failure is a HELP**, and `integrity-s2.txt` is committed before any other output. The `final` step re-runs these
checks on GO-1's units, as GO-1's tooling records them (O-3).

## 8. Descriptive only

Stage 1's descriptive list (READOUT-PLAN §8) is kept, for the Stage-2 points and the final map. In addition:
- the non-registered lines of §4;
- the OVERFLOW-SENSITIVE map;
- the crash bounds;
- the Stage-1-only M3 and M4;
- the censored per-birth figure;
- the interim provisional Stage-1 view.

## 9. Reports

- **`READOUT-STAGE2A.md`** (interim): the 2a per-point table and the R-B Stage-2a list with its core-h, with "needs its
  own owner GO".
- **`READOUT-FINAL.md`:**
  - the final M1/M4;
  - the per-point table, with combined p at extended points;
  - the families, with BH and BY;
  - M2 (registered and sensitivity), M3 and M7;
  - Holm;
  - §8 with its non-registered lines;
  - the scorecard;
  - the integrity disclosure (§3.6);
  - every O-item and how it was applied.

Every number traces to a line of a script output.

## 10. Order of operations

1. This plan: adversary, then the coordinator's ruling, then merge.
2. The continuations tooling PR (CT-1 to CT-4), with its adversary pass.
3. The coordinator rules the overflow rule and the build. The owner gives the 2a go.
4. 2a runs, beside GO-1.
5. 2a integrity, then the interim readout, then the owner's GO for 2b(2a).
6. 2b(2a) runs.
7. The `final` step: integrity over every continuation unit, then the final map.

## 11. The script, the tests and the locks

- **The script.** `runs/RBT-129/stage2-plan/stage2_readout.py` is a skeleton. It imports `stage1_readout.py` and
  implements, as tested pure functions:
  - the inputs check and the 2a gate;
  - the budget;
  - `parse_hzn`, `unit_state`, `keep_seed`, `check_build` and `crash_bounded_body`;
  - the five C3 pins;
  - the R-B combination and the MUE;
  - the final BH;
  - M4's weights;
  - the locks.
- **The tests.** `tests/test_rbt129_stage2_plan.py` holds 28 tests on synthetic numbers. Its only repository reads are
  registered inputs.
- **The full suite** passes in a clean `.[dev]` venv without scipy (the PR states the count).
- **The locks** (`RULINGS-CITED-S2.md`). `refusal()` refuses unless **all** of these hold:
  - `GO-ID: RBT129-S2-READOUT-GO-1` (registered as `GO-ID-PENDING:`);
  - `OVERFLOW-RULE: include-flagged | exclude-flagged` (registered as `-PENDING:`);
  - `BUILD-SHA256: <sha>` (registered as `-PENDING:`);
  - no local ref names the quarantined unit.

  The coordinator opens each lock in a commit of its own.
- **Before the GO** (as COORD-RULING-512 R5 required for Stage 1):
  - the `integrity`, `interim` and `final` drivers and the continuation readers are completed;
  - an **end-to-end synthetic-tree test** covers them. The tree has 2a, GO-1's halves, a flagged unit, a CRASHED M and
    a CRASHED S;
  - the drivers are checked by the same adversary.

  They need the continuation lane format, which does not exist yet. **No rule may be added or changed in that round**:
  only readers and drivers.

## 12. OPEN for the adversary

| id | where | the question | this plan's answer |
|---|---|---|---|
| O-1 | §2.7 | Does owner decision 4 ("plan it") authorise the 2a launch, or is a go still needed? | a go is needed |
| O-2 | §2.1 | Should 129001's census-adopted S60 (stock, unscanned) be re-simulated on the build instead? | no: the same physics off-event; adoption is the registered T10 rule; labelled UNSCANNED |
| O-3 | §1.2, §7 | Will GO-1's tooling adopt §3's unit states and the overflow rule? If not, how do GO-1's units enter the final map? | they must; otherwise the final map is a HELP |
| O-4 | §2.4 | K-SALT for seeds 9–16, where there is no census reference | GO-1's rule, adopted |
| O-5 | §2.3 | The 2a gate's caps (4 / 2) against the three eligible points | 3 M and 1 N; freed slots unused |
| O-6 | §3.1 | Is CT-2's identity scope (4 S + 4 M + 1 N units, ≥ 30 seasons) enough? | proposed minimum |
| O-7 | §3.6 | The format of the owner's Stage-1 scan record, and whether "season of first overflow" is an outcome proxy | count + first season only; the adversary should say if the season must be dropped |
| O-8 | §3.4 | include-flagged primary vs exclude-flagged primary | include (consistency with UNSCANNED Stage 1; no informative missingness) |
| O-9 | §4.1 | O-12's equivalence reading (TOST at ±0.05) for K2 pooled, "to be ruled before Stage 2" | the conjunction kept |
| O-10 | §4.1 | K2 pooled reads FAIL at < 2 runs in a stage (Stage 1's code), so a 2a stage with N at one point on one seed is VOID by construction | kept as conservative; the alternative is "not evaluable" |
| O-11 | §4.3 | Adopting the reading that makes item 2 AS PREDICTED after seeing Stage 1 | adopted, labelled; descriptive only |
| O-12 | §4.5 | MARGINAL replaced (not accompanied); and whether §9.1's RBT-118 choice should be re-read under it | replaced; §9.1 not re-read |
| O-13 | §2.6 | Register a lever-only leg (the R8 levers without the steering instrument)? It could mark Stage-1 EARNS calls LEVER | not registered here; needs its own amendment and cost |
| O-14 | §5.4 | MUE as the root of the combined Z(μ) | adopted |
| O-15 | §5.1 | The interim BH over Stage-1 ∪ 2a, or over 2a alone | Stage-1 ∪ 2a |
| O-16 | §5.2 | An extended point with < 2 income-valid half-2 seeds: the half-1 test, or not tested? | the half-1 test, flagged |
| O-17 | §5.4 | M4's quarter rule | adopted (descriptive) |
| O-18 | §5.4 | M3 for §8 corroboration on the final map (with 2a points), or on Stage-1 points only | the final map |
| O-19 | §5.4 | M2 registered fit frozen at Stage-1 seeds 1–8 and Stage-1 habitability, even where R-B changes a call at n = 16 | frozen (NOTE 10) |
| O-20 | §5.3 | K2 per point on the final map: one t over all of a point's N runs (both halves), BH over every N point of the map | adopted |
| O-21 | §5.3 | The share-test combination on y′ at an extended N point | the same Z rule |
| O-22 | §3.4 | Crashed S seed: removed from n (primary), with the restored-states bound | adopted |
| O-23 | §3.5 | An attested S-arm crash does not stop the hive | proposed; needs the coordinator's ruling (amends item 5) |
| O-24 | §3.3 | A done unit with no build record is a HELP, not CLEAN | HELP |
| O-25 | §2.6 | Should 2a's perception and lever NOT MEASURED lines also be printed for Stage 1 in the final report? | yes, printed |
| O-26 | §5.6 | Verdicts under the sensitivity map: print only, or also a stated "robust" bar? | print and mark only |
| O-27 | §1.2 | GO-1 is ranked from Stage-1 provisional calls, and the interim BH may change them | GO-1 fixed; the change is printed |
| O-28 | §2.5 | The budget prices M/N at every seed | an upper bound; actual from the gate table |
| O-29 | §4.2 | Verdict 5's share veto: one other-fauna WIN fails it (not a counting set) | as coded |
| O-30 | §11 | The drivers come after this review | the GO is conditional on their adversary check |

---
_Generated by [Claude Code](https://claude.ai/code)_
