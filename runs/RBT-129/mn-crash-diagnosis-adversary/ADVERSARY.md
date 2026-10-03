# RBT-129 crash diagnosis (#520): adversary review

- **Reviewed:** PR #520, head `c3ed55ff7bb841455c8c8a55d8f485dea6da8b80`, base `claude/new-session-4cao7d` (`5bc9c34`).
  The file under review is `runs/RBT-129/mn-crash/DIAGNOSIS.md` and its `diag/` scripts.
- **Reviewer:** a fresh adversary session (`session_01NCv8iQ1MAknkFVwLbeZQ3h`). Coordinator:
  `session_017eUHGNdTSsoVFAtLaJWehF`.
- **Host:** Linux 6.18.44-fc-v64 x86_64, 4 cores, 15 GB, CPython 3.11.15. Pip venv: `mujoco==3.14.0`,
  `numpy==2.4.6`. Every pip-build run asserts `mujoco.__version__ == "3.14.0"`.
- **Discipline:**
  - Only the `-ckpt60` branches were fetched, each by a narrow refspec. The quarantined
    `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M` was never fetched, listed or read: `git show-ref` has no `…-129001-M`.
  - Every ecology run was in `mktemp`/scratch outside `runs/`, with `NO_DURABLE=1`, and its directory was deleted
    unread.
  - Logs were grepped only for the faulthandler block, for `RBT_HZN` lines and for Python exceptions. No season,
    population, fauna, member or outcome line was displayed.
- **Raw outputs:** `probe/`.

## Verdict: **ACCEPT WITH CORRECTIONS**

**The mechanism is right.** I confirmed it independently on a fourth host, against source, and under AddressSanitizer:

- the root cause (an unchecked write to the `int[24]` EPA horizon in `addEdge`);
- the regression since 3.8.0;
- that it is unfixed on main;
- the deterministic single-`mj_step` reproduction;
- the finite state;
- the box/cylinder sibling pair.

**Three parts overclaim, and must be corrected before the diagnosis is cited:**

- the near-miss analysis, section (d);
- the claim that the guard is a "slightly truncated" contact, section (c);
- the silence on forward risk.

They are MAJOR, not BLOCKING. None of them changes the mechanism. Each changes a conclusion that someone will act on: the
Stage-1 integrity statement, and the pin for continuations.

## Findings

### 1. MAJOR: the tail analysis in section (d) is falsified. S arms reach a horizon of 23, one edge below the cap.

- **The claims:**
  - "overall maximum is **16**";
  - "the crash is not the far tail of ordinary contacts";
  - a log-linear fit giving "about 1e-7 expected overflows".
- **Evidence:** the instrumented build with the guard off (stock logic) on **S arms**, which the PR never surveyed.
  Draws are in `probe/s-sample-draws.txt`.

  | sample | unit-seasons | EPA iterations | overflows | max horizon |
  |---|---|---|---|---|
  | 16 S units, seeded random draws (+ c2-p030-U-G/129001), seasons 60–62 | 48 | 2.09e8 | 0 | **19** (c2-p080-HP-G/129004) |
  | c2-p080-HP-G/129004 S, seasons 60–89 | 30 | 4.79e8 | 0 | **23** (counts 16:3, 17:3, 18:4, 19:2, 23:1) |
  | 3 S units (c2-p030-U-G/129001, c1-p080-U-G/129005, c1-p030-HP-G/129006), seasons 60–179 | 360 | 2.80e9 | 0 | 16, 17, 18 |
  | PR: 30 M units, seasons 60–62 | 90 | 4.94e8 | 0 | 16 |

- **What this shows:**
  - One ordinary S unit, never crashed and not chosen for any outcome, came within one edge of overflowing within 30
    seasons. Its one-unit 30-season run had as many EPA iterations as the PR's whole 30-unit survey.
  - The PR's own fit (0.17× per edge from n = 8–15) predicts about 1e-6 expected horizons ≥ 23 in that many
    iterations. One was observed.
  - The log-linear extrapolation therefore underestimates the far tail by **many orders of magnitude**. It must not be
    used for any rate. The tail is a mixture: rare deep-overlap states, as the PR itself suspects, sit on top of the
    ordinary contacts.
  - "Not the far tail of ordinary contacts" stands only in the weak sense that deep overlaps are needed. **They occur
    in ordinary S runs too.**
- **The two "16"s are not comparable.** The PR compares the other units' first 3 seasons against the crashed unit's
  late seasons (its own caveat says so). The headline "against a maximum of 16 across all 30 other units" still reads
  as if the crashed unit were uniquely exposed. My S data says it is not.
- **Remedy:**
  - Strike the extrapolation and the "≈1e-7" figure.
  - Restate the conclusion as: near misses up to 23 occur in ordinary S runs within tens of seasons, so overflow is a
    property of the physics regime, not of one unit.
  - Report S, N and census exposure as not surveyed.

### 2. MAJOR: "0 overflows in 90 M unit-seasons" does not support "no other Stage-1 run was silently corrupted". A census is needed for that claim.

- **The PR's own caveat is right but too weak.** Here is what is unsurveyed:
  - 237 of 240 seasons of each M unit;
  - all 7 N units;
  - all **288 S units** (each 240 seasons after ckpt60);
  - the Stage-0 census (150 points × 3 seeds × 60 seasons) and the pilot.

  That is roughly 1e5 unit-seasons against 90 surveyed.
- **Silent corruption is mechanically possible.**
  - At nedges = 25, `indices[24]` overwrites `edges[0]` and `edges[24]` writes 4 bytes past the buffer. ASan shows the
    write lands in poisoned (unallocated) mjData stack, and the crash comes from a read: `hznVerts[corrupted edge]`
    taken from stack contents.
  - Whether that read faults depends on what the stack holds there. Small garbage gives a wrong face and a silent wrong
    contact, not a SIGSEGV.
- **The census is sound as a detector.** The instrumented guard-off build is byte-identical to pip on non-overflowing
  trajectories (finding 6), so a guard-off re-run reproduces each stock run exactly up to its first overflow, and logs
  that overflow.
- **Recommendation:**
  - **Yes, a full scan is needed** before the Stage-1 readout or integrity section asserts that no unit was silently
    corrupted. It also doubles as a reproduction audit: compare output hashes with the recorded Stage-1 branches.
  - Priority:
    - M and N first: 38 units × 240 seasons, about 100 core-hours at this host's speed (a 120-season S run took about
      80 min);
    - then S: 288 units, roughly 600–800 core-hours;
    - the census last.
  - Without the scan, the integrity section must say: "a known memory-safety bug (EPA horizon overflow) can corrupt
    without crashing; no unit other than the CRASHED one was checked beyond 3 merged seasons (M) or at all (S, N,
    census)."
  - Note for the census: some ckpt60 branches hold no run files, only the done-marker (MANIFEST season "?"):
    c2-p080-PW-G-129003, c1-p030-PW-G-129008 and c1-p080-PW-L-129002 among my draws. Those S units must be sourced
    from their `-record` or `-ksalt` branches, not from ckpt60.

### 3. MAJOR: forward risk on stock 3.14.0 is not addressed. Continuations need a ruling.

- The PR ends with "the RBT-129 pin stays at stock 3.14.0". It gives no estimate of what that costs. See (e) below.
- In short: the chance of at least one more overflow in Stage 2a, 2b and R-B is roughly **50–75%**, by crash or by
  silent corruption.

### 4. MAJOR: the guard is not "a slightly truncated EPA contact", and remedy 1 should be correct sizing, not the guard

- **What the patch does.** I read it line by line.
  - `addEdge` skips writes once `nedges >= 24` but keeps counting. So the writes are bounded at indices 0–23: no
    off-by-one.
  - `epa` then breaks with `face` = the closest face before this iteration. That face was just `deleteFace`d by
    `horizon()`, but its data and vertices are intact.
  - This is the same polytope state as stock's existing out-of-memory branch (`nedges > maxFaces` → `break`). It is
    deterministic and memory-safe. `multicontact` is not reached (rabbitstew does not enable multiccd).
- **What it does to the result.** I compared it on state_2246 against a build with the horizon sized to the face
  budget (6N, the approach of upstream PR #3650; diff in `probe/`):

  | | contact normal | contact pos | depth |
  |---|---|---|---|
  | guard | (0.094, 0.985, −0.144) | (−1.7074, −1.7454, 0.3429) | −0.099862 |
  | 6N sizing | (−0.025, 0.987, −0.161) | (−1.7124, −1.7445, 0.3485) | −0.099862 |

  - The normals differ by **6.9°**.
  - After that one step, qvel differs by up to **3.8** (max |qvel| 36.5) and qpos by 1.9 cm.
  - The guard's continuation is therefore materially different physics from a converged EPA. It is not "slight".
  - The patch does log the overflow to stderr, so it is not silent if the log is kept.
- **"5+N is safe" depends on convexity.** The PR concedes this for remedy 2 but not here. The hard bound is the face
  budget: horizon faces are distinct existing faces, so nedges ≤ nfaces ≤ 6N, and `epa` already checks
  `nedges > maxFaces`.
- **Upstream sizing is byte-identical where it matters.** The 6N build is byte-identical to pip on state_2245
  (non-overflowing).
- **Remedy:**
  - Rank "size both horizon arrays to the face budget (6N)" first. It is identical on every non-overflowing trajectory
    and gives the converged EPA result at the event.
  - Keep the guard only as a fallback, and log every overflow into the run's integrity record.
  - Replace "slightly truncated" with the measured difference.

### 5. MINOR: upstream has already reported this bug, and a fix PR is open

- **google-deepmind/mujoco#3646** was opened 2026-10-02 and is open.
  - It reports a cylinder vs mesh contact, a **25-edge horizon**, SIGSEGV in `projectOriginPlane`, and the same
    `int[24]` / `addEdge` diagnosis.
  - It reports the bug in 3.12.0, 3.13.0, 3.14.0 and main. That is consistent with the 3.8.0 regression.
- **#3650** (third party, opened 2026-10-03, unmerged, no maintainer review) sizes the arrays at `6 * iterations` and
  adds a bound in `addEdge`.
- **Remedy:** replace "An upstream report … is for the owner to file" with these references. Any later registration's
  patched build should track #3650, or its merged successor, rather than the RBT guard.

### 6. MINOR: the patched build is not reproducible from what is documented. Identity holds on a second unit nonetheless.

- **The build record is incomplete.**
  - DIAGNOSIS records "clang, Release" and a sha256. My build of tag 3.14.0 (`9ecbb9d7`) plus the patch has a different
    sha256 (`861a2af8…cda3378` against the PR's `37883e94…7020433`).
  - My build used clang 18.1.3, Release, with MuJoCo's defaults: LTO on and AVX on. The pip wheel is clang 20.1.8 + LLD
    20.1.8.
  - Neither binary has FMA instructions (0 `vfmadd`), and no fast-math is set. So the compiler difference should not
    change IEEE results.
- **My identity test** (the PR's `identity.sh`, unchanged) on **c1-p080-U-L/129004 M**, one merged season: pip, guard
  off and guard on are **identical in all 737 files**.
  - This is a different unit and season from the PR's. The PR does not record which unit or NSEAS gave its 557/557, nor
    commit that output.
  - No overflow occurred in either test, so guard-on identity is expected there, not proven in general.
- **Remedy:**
  - Commit the identity output and name its unit.
  - For any later registration, pin the build recipe (image, compiler version, the full `cmake` line, LTO/AVX options,
    how the `.so` replaces the wheel's) and check identity on several units before adoption.

### 7. MINOR: raw records missing

- The crashed-unit guard run's histogram exists only as prose, and only its second part is given.
- **Remedy:** commit the two raw `RBT_HZN` histogram lines and the overflow line, as `nearmiss-M-3seasons.txt` does.

### 8. NOTE: `repro.sh` works end to end

- The PR says it was not re-run as one script. I ran it unmodified (137 min, sharing 4 cores). Result:
  - ecology exit 139;
  - the same faulthandler frames as host1;
  - the bisect at **simulation 13, `mj_step` 2246**, as the PR found;
  - the standalone replay exits 139.

### 9. NOTE: fault-site variability and ruling item 5

- Repeated attempts of the same job in the same process configuration fault at the same place (host1 ×3; my replay ×3).
  So item 5's two-attempt instruction test should still classify a recurrence of this bug as CRASHED.
- The PR's wording ("in the convex collider") is sensible for later registrations. For RBT-129 it is only a NOTE.

### 10. NOTE: small items

- `tail.py` raises on an empty histogram line (`max()` of empty).
- `.pyc` blobs remain in the PR's history (`31ce8a6`) after `c3ed55f` removed them. They are harmless; a squash-merge
  drops them.

## (a) Root cause against source: CONFIRMED

- **3.14.0** (tag `9ecbb9d7`), `src/engine/engine_collision_gjk.c`:
  - `addEdge` is at **1269–1272**, with no bound: `pt->horizon.edges[pt->horizon.nedges] = edge;
    pt->horizon.indices[pt->horizon.nedges++] = index;`.
  - `mjc_ccdSize` sizes `align8(sizeof(int) * 24)` ×2 at **2358–2359**.
  - The carve in `mjc_ccd` is at **2516–2518**.
  - `epa`'s only check is `nedges > maxFaces(pt)` at **1435**, which runs after `horizon()` has already written.
- **Main** (`16dafd8f`, 2026-10-02): the same `addEdge` (1269–1272) and the same `* 24` (2385–2386). The three commits
  since 3.14.0 touch only multicontact and capsules. **Unfixed.**
- **Regression:** `d9b3faf8` (2026-04-15, "Remove thread_local EPA data in favor of using mjData stack"), first tagged
  in **3.8.0**.
  - Before that, 3.5.0–3.7.0 used `static int index_data[6 + mjMAX_EPA_ITERATIONS]` (170) for N ≤ 170, else an
    allocation of `6 + N`.
  - 3.3.0 used a stack allocation of `6 + max_iterations`.
- **Geometric plausibility.** On a convex polytope the horizon is a simple cycle of distinct vertices. With 36 vertices
  before w (EPA iteration 32), 25 edges is possible. A smooth cylinder with `ccd_tolerance` 1e-6 keeps adding support
  points up to `ccd_iterations`, so a deep overlap builds a fine, nearly flat facet set that one new point can see much
  of.
  - Upstream #3646 independently hit exactly 25 on a cylinder vs mesh.
  - My S scans see 16–23 in ordinary runs.

## (b) Reproduction on this host: REPRODUCED, deterministic, and ASan-confirmed

| test | result |
|---|---|
| `repro.sh` end to end from ckpt60, pip 3.14.0 | exit 139; frames `simulation.py:472 step` ← `:518 run` ← `:1008 run_group` ← `evolution.py:167/197` ← `ecology.py:513` ← `:734` ← `:893` ← `cli.py:447` |
| bisect (`trace.py count`) | simulation 13, `mj_step` 2246 (same as PR) |
| standalone `replay.py dump 2246 step` | SIGSEGV 3 of 3 runs; `state_2245` steps cleanly (ncon 34) |
| state at 2246 | finite; max \|qpos\| 1.953, max \|qvel\| 55.78, max \|geom_xpos\| 2.555 (same as PR) |
| **ASan** (gcc 13, unpatched 3.14.0) | `use-after-poison` **WRITE of size 4** in `addEdge` `engine_collision_gjk.c:1270` ← `horizon` :1331 ← `epa` :1423 ← `mjc_ccd` :2491 ← `mjc_penetration` ← `mjc_Convex` ← `mj_narrowphase`; state_2245 clean |
| instrumented, guard off / on | `nedges 25 (cap 24), EPA iteration 32, nverts 37, nfaces 133`, cylinder (32) vs box (30); off → 139, on → no fault, 91 EPA iterations, 1 overflow (same as PR) |
| option sweep | as the PR states; additionally `ccd_iterations` 21 has no fault and 33 faults |

Valgrind was not used: the overflow stays inside the mjData arena, which memcheck cannot see. MuJoCo's own ASan
poisoning of its stack arena is what catches the write.

## (c) The patch

**Bound and safety.** The bound is correct, and the overflow behaviour is a deterministic break at the pre-iteration
closest face, safe, and the same as stock's OOM branch (finding 4).

**What it does to the contact.** It changes the contact at the event, by 6.9° in the normal here. It does log the event.

**Reproducibility.** It rebuilds from tag plus patch, but not bit-reproducibly, and the build is under-documented (finding 6).

**Byte identity.** It holds on a second unit and season with a different compiler version (737/737). Flag risk:

- no FMA in either build, and no fast-math;
- `-O` level and LTO change inlining, not IEEE semantics.

So I see no plausible route by which flag differences would change results. This is an argument plus two
single-season tests, not a proof over all trajectories. Any adoption should repeat identity on several units over many
seasons.

## (d) Near-miss analysis: explicit answers

- **Is the instrumentation sound, and does it reproduce stock?**
  - Yes. Guard off is the stock code plus a counter and an `fprintf` after `horizon()`.
  - Byte identity is reproduced (737/737).
  - Overflow lines are flushed before the faulting read, so a crash still leaves its line.
  - The histogram is per process; WORKERS=1 is used.
- **Is the sample fair, and was it chosen without regard to outcome?** The 30 M units are **every** M job in
  `lanes/1-MN` except the crashed one (31 M jobs; 31 `-M` branches). So it is a census of M units, not an
  outcome-chosen sample. But it covers 3 of 240 seasons, and **no S (288), N (7), census or pilot unit**.
- **Does "0 overflows" support "no other Stage-1 run silently corrupted"?** **No** (findings 1 and 2).
  - The near-miss tail in ordinary S runs reaches 23.
  - A non-crashing overflow is mechanically possible.
  - The survey covers well under 0.1% of Stage-1 unit-seasons.
- **Recommendation: a full guard-off census is required** for any claim that no other Stage-1 unit was silently
  corrupted. Run M and N first (cheap), then S, then the census.
  - Until then, the readout's integrity section must state the gap as written in finding 2.
  - My own scans are evidence, not a census: 0 overflows in 438 S unit-seasons (seasons 60–179 for 3 units,
    seasons 60–89 for 1, seasons 60–62 for 16), plus a 120-season run of c2-p080-HP-G/129004 S and two 120-season M runs (addendum below).

## (e) Risk going forward on stock 3.14.0

**The rate.**

- Observed: one overflow, which crashed, in roughly 1.0–1.4e5 unit-seasons:
  - census, 27k;
  - pilot, about 12k;
  - Stage-1 S, about 69k after ckpt60;
  - M, about 7.4k;
  - N, about 1.7k.
- An unknown number of silent overflows comes on top of that.

**The exposure ahead.** Stage 2a (≤ 16 points × 8 seeds), 2b/R-B (≤ 20 points × 8 more seeds) and their M/N arms add up
to about 1e5 unit-seasons, comparable to Stage 1.

**The estimate.**

Posterior for one event under a Jeffreys prior, Gamma(1.5):

| assumption | P(≥ 1 further overflow) |
|---|---|
| hazard uniform over arms | about **55%** |
| hazard M-specific (11k M unit-seasons so far, about 19k ahead) | about **75%** |

- The 90% intervals are very wide: with one event, anything from "unlikely" to "several" is consistent.
- The S near misses up to 23 rule out treating S as safe.

**Consequences under the current ruling.**

- An M or N recurrence is a second CRASHED unit (item 5). That stops M/N lane issuance and holds the M/N readout plan
  until a new ruling and its adversary pass.
- An **S-arm recurrence stops the hive**.
- A silent overflow corrupts a unit undetectably.

**Answer: the stock-3.14.0 pin is not "safe" for RBT-129 continuations. A ruling is needed before the next RBT-129
launch.** Options for the coordinator, not for me to choose:

1. **Keep stock 3.14.0**, and pre-register now:
   - that the S arm is covered by the CRASHED state, or by an explicit stop rule;
   - a mechanism check for any crash (a re-run under the guard-off instrumented build must log `RBT_HZN overflow`);
   - that the integrity section discloses unverified silent-overflow exposure.
2. **Re-pin to a 6N-sized 3.14.0 build** (finding 4). It is byte-identical on every non-overflowing trajectory, so
   comparable with all completed Stage-1 runs except at events that are UB under stock. Adoption needs:
   - a pinned build recipe;
   - multi-unit identity checks;
   - its own adversary pass;
   - a ruling that amends RULING items 2 and 6 for continuations only, never for re-running the CRASHED unit.
3. **Run the instrumented guard-off build for continuations.** It is byte-identical to stock and changes nothing, but
   every overflow is logged, so silent corruption becomes visible. This is the cheapest integrity improvement that
   keeps the pin's physics.

## (f) Scope: CONFIRMED clean

- `git diff --stat 5bc9c34...c3ed55f` touches only `runs/RBT-129/mn-crash/DIAGNOSIS.md` and `runs/RBT-129/mn-crash/diag/*`.
- The four commits (`367661b`, `216580e`, `31ce8a6`, `c3ed55f`) add or remove only those, plus `.pyc` files later
  deleted.
- There are no changes to:
  - Stage-1 records or branches;
  - RULING.md;
  - `pyproject.toml` or the pin;
  - `runs/RBT-129/launch/`, DESIGN or any registered plan.
- The quarantined label appears only in a comment in `repro.sh`, which says it is never used. No script fetches it:
  `repro.sh` fetches `…-129001-ckpt60` only.
- This review also never touched the quarantined branch.

## Addendum: long scans (finished before this PR was opened)

All runs used the guard-off instrumented build, from ckpt60, with `NO_DURABLE=1`, and the run directories were deleted
unread. Raw lines are in `probe/nearmiss-S-120seasons.txt` and `probe/nearmiss-M-120seasons.txt`.

| unit | seasons | EPA iterations | overflows | max horizon | counts ≥ 17 |
|---|---|---|---|---|---|
| c2-p080-HP-G/129004 **S** | 60–179 | 1.83e9 | 0 | **23** | 17:5, 18:5, 19:2, 20:1, 21:1, 23:1 |
| c2-p030-U-G/129005 **M** | 60–179 | 1.05e9 | 0 | 18 | 18:1 |
| c1-p010-PW-L/129005 **M** | 60–179 | 1.44e9 | 0 | 17 | 17:1 |

- Both M units, among the heaviest in the PR's 3-season list, pass the PR's "maximum 16 across all other units" once
  they run longer.
- The S unit's tail keeps reaching 20–23.
- These units were chosen by their 3-season horizon tails (a stress probe), never by outcome.
- **Totals for this review: 0 overflows in 528 S unit-seasons and 240 M unit-seasons, about 1e10 EPA iterations.**
  Findings 1–3 stand.

## Fix-check of #520 r2 (head `f221effde94059bf4ed677bf0380fabb580195fa`)

### Final verdict: **ACCEPT**

All four MAJORs and all three MINORs are resolved. Three NOTEs are left open; none blocks. Two concern how option (c)
is packaged. One corrects this review's own finding 4, and r2 already handles it correctly.

- **How I checked.** I fetched the new head by its SHA. Everything else was read from the PR head or from `-ckpt60` and
  `-record` branches fetched one at a time. The quarantined branch was never fetched or read, and `git show-ref` has
  no `…-129001-M`.
- **Raw outputs:** `probe/fixcheck/`.

| finding | r2 change | fix-check |
|---|---|---|
| MAJOR 1: tail framing | (d): "max 16", "not the far tail" and the ~1e-7 extrapolation are **retracted**; this review's S/M scans are cited; S, N, census and pilot are stated as not surveyed; `tail.py` is labelled not for rates | **RESOLVED** |
| MAJOR 2: silent corruption | (d): "ruled out" and "not ruled out" are separated. The crashed-unit "no earlier overflow" claim is scoped to that one trajectory, with the identity caveat. The full census is named as what would settle it, with interim wording | **RESOLVED** |
| MAJOR 3: forward risk | new (e): the 55–75% estimate, RULING item 5 and S-arm consequences, and options (a)–(c), not chosen; the owner's choice of (c) is added and labelled as added later | **RESOLVED** (see NOTEs FC-2 and FC-3 on (c)) |
| MAJOR 4: guard / re-rank | (c) re-ranked: face-budget sizing (#3650 or 6N) first, the guard second. Measured at the event: 6.91°, 7.6 mm, max \|Δqvel\| 3.79, still apart after 10 and 50 steps. 6N equals #3650 there. All six builds are byte-identical off-event on `state_2245`. "Slight truncation" is withdrawn | **RESOLVED**. The numbers agree with mine (6.9°, 3.79). |
| MINOR 5: upstream | #3646 and #3650 cited; the #3650 patch (`f394095`) committed; the three fixes compared | **RESOLVED** |
| MINOR 6: build recipe | `diag/build.sh` (pinned tag, toolchain, flags, prefix map, fixed WORKDIR); a sha table; the ThinLTO path explanation | **RESOLVED and reproduced:** see below |
| MINOR 7: raw records | `diag/records/`: r1 lines transcribed and labelled as such, r2 written directly; the crashed-unit guard record now says part 1's histogram was lost | **RESOLVED** |
| NOTE: marker-only ckpt60 | the three are extinct-pre-merge snapshots (61-byte "skipped: extinct pre-merge" marker; `-record` holds `EXTINCT.txt`) | **CONFIRMED** names-only on c2-p080-PW-G-129003: `-record` holds `record/EXTINCT.txt` and `record/UNIT.txt`. Content not read. |

### What I re-ran on this host

| check | result |
|---|---|
| `diag/build.sh` with the log-only patch, WORKDIR `/tmp/rbt129-mjbuild/logonly` | sha256 **`74e1d8a29d1303108e7b0f8774e9820de103b5307ad0a8c23f0fdbf77e1525ad`**, **identical** to #520's table; clang 18.1.3, 0 `vfmadd`. The recipe reproduces bit-for-bit across hosts. |
| the same patch, WORKDIR `/tmp/rbt129-mjbuild/other-dir` | `4425f3a6…`: a different sha, which confirms r2's path-dependence (ThinLTO) explanation. |
| identity, log-only vs pip, **c2-p030-U-G/129008 M**, 1 merged season (a unit not tested in r2) | **575/575 files identical**; 7.3e6 EPA iterations, 0 overflows |
| identity, log-only vs pip, **c2-p030-U-G/129002 M**, **30 merged seasons** (60–89) | **827/827 files identical**; 1.07e8 EPA iterations, 0 overflows, max horizon 14 |

The 30-season run is the first multi-season identity test of any patched build. All earlier tests, r1, r2 and mine,
covered one season.

### Open NOTEs (non-blocking)

**FC-1. A correction to my own finding 4.**

- I wrote that the hard bound is "nedges ≤ nfaces ≤ 6N (horizon faces are distinct faces)". That is wrong.
  - A non-visible face can border the visible region along two edges, so horizon edges are bounded by live **edges**
    (about 1.5 × live faces, up to about 9N), not by faces.
  - Under convexity the bound is ≤ nverts ≤ 5 + N, which is far below 6N. So 6N sizing is ample in practice, but it is
    not a proof.
- r2 already says the right thing. Its comparison table notes that the 6N diff "is not enforced" with no bound in
  `addEdge`, and that **#3650's bounded write is the stricter fix to track**. Nothing for the author to change.

**FC-2. Option (c) is not "byte-identical to stock, UB included".**

- (e)(c) says the log-only build is "byte-identical to stock, and unchanged physics, UB included".
- Off-event, identity is now tested: 4 units, up to 30 seasons.
- **At an overflow event, though, behaviour is undefined, and depends on the build.** Which bytes the corrupted read
  picks up depends on stack layout and code generation. The log-only build is clang 18 with an extra `fprintf` in
  `epa`; the wheel is clang 20. The same overflow already faulted at different sites in different process layouts
  (r1 (b)).
- So under (c), what happens after an overflow is not evidence of what stock would have done:
  - it may crash where stock would not, or the reverse;
  - it may corrupt differently.
- The `RBT_HZN overflow:` line is the reliable output. Whatever follows it should be treated as UB, and a unit that
  logs one should be handled by rule, not by what came after.
- Suggested wording for (c): "byte-identical to stock off-event; at an overflow both are undefined behaviour, and the
  continuation is build-specific."

**FC-3. Packaging (c): verify the `.so` itself, not just the version.**

- RULING item 6's refusal checks `importlib.metadata.version("mujoco") == "3.14.0"`. The log-only build replaces only
  `libmujoco.so.3.14.0` inside a pip-installed venv, so the metadata still reads 3.14.0. A host running the plain pip
  `.so` would pass the check and log nothing.
- That is a silent loss of exactly the detection (c) exists for.
- For whoever packages (c) (`session_01Pky3gny7iiA4kBkPUcrDtt`):
  - the launch and each emitter should also refuse unless the loaded `libmujoco.so.3.14.0` hashes to `74e1d8a2…`;
  - `platform.json` should record that sha256;
  - the run's stderr, where `RBT_HZN overflow:` lines go, must be captured and grep-checked for that prefix only,
    without reading outcome lines.
- That packaging has its own adversary pass, so this is a NOTE here.

---
_Generated by [Claude Code](https://claude.ai/code)_
