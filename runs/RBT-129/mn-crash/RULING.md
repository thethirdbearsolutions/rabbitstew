# RBT-129 Stage 1 M/N: the unit that cannot complete (coordinator ruling, r3)

- **r1:** `1f263d1b`, reviewed in `mn-crash-adversary/ADVERSARY.md`: ADOPT AFTER FIXES. r2 meets all five MUSTs and
  SHOULDs 1–9; NOTES 1–2 are corrected.
- **r2:** `eba5465`, fix-check: ADOPT AFTER FIXES (R2-1, R2-2 and two citations). r3 fixes all of these.
- **When and what kind of ruling.** Written 2026-10-02, after launch. It is an **outcome-blind amendment**: it adds a
  unit state that the registered text does not have. It is labelled as such, in the way T5's slot-freeing was labelled
  DATA-INFORMED.
- **Why no substitute.** DESIGN §4.2 (line 378: no seed or arm is added after Stage 1 is seen) and F4 (line 213: seeds
  are "never skipped or replaced").
- **The M/N readout plan must adopt this ruling verbatim.**

## What has been seen, and by whom (MUST 3)

- **The coordinator** has read no M/N outcome. That covers the crashed unit's partial run, its run.log and its
  snapshot branch. What it has seen:
  - job names and exit codes;
  - kernel log lines (dmesg);
  - the Python faulthandler frames (file:line and function names only) as relayed by the host1 runner, with values
    excluded at the coordinator's instruction;
  - start times and crash times of each attempt.
- **The host1 runner** pulled those frames from the unit's `run.log`. That file also holds per-season outcome lines
  (`ecology.py:896`). The runner was told to read errors only and relay frames only, but it did open that file. How it
  extracted the block is to be recorded from its own account (integrity section). **That account is due before the
  M/N readout plan is committed (R2-2).** If the runner saw any per-season line, even in part, the readout's integrity
  section discloses how many lines, which seasons and for which unit (never their content). That runner's session then
  does no M/N readout work of any kind. The runner session authors no
  analysis, and it is archived when its lanes finish.
- **Wall time.** Run 1's wall time before the crash is a proxy for how far the run got, so it is **struck** from this
  ruling. It will not be reported again.

## Facts (errors only)

- **The unit.** Job `1/c2-p030-U-G/129001/M`, host1 lane 0, pinned trees `rabbitstew 144b3b6`, `launch 7921cde`,
  `scripts d517cf5`. It forks from `stage1/c2-p030-U-G/129001/ckpt60`.
  - Seed 129001 is `RESUME_SEED`, and its salts are (0, 0). So its S60 is the adopted census S 0–59 (F7, line 260;
    T10, line 500), and no K-SALT applies to it.
  - S at 129001 ran seasons 60–299 from that same state without crashing.
- **Four attempts, four native crashes in MuJoCo 3.14.0 (pip).**
  - Attempts 1–2 used `WORKERS=2`; a pool worker died, giving `BrokenProcessPool`.
  - Attempts 3–4 used `WORKERS=1`; ecology exited -11. Attempt 4 ran with `PYTHONFAULTHANDLER=1`.
  - Attempts 2–4 were resumes, and each crashed within about 20 s.
- **Same instruction every time.** For attempts 1–3, dmesg logs the same faulting instruction: file offset `0x1adb65`,
  which is vaddr `0x1aeb65` = `projectOriginPlane`+5. That is a static helper of the native convex collider, reached
  from `mjc_ccd`. The fault addresses are garbage, so a bad pointer is read.
- **The Python stack (attempt 4).**
  - `simulation.py:472 step` (`mujoco.mj_step`)
  - ← `run`
  - ← `run_group`
  - ← `evolution.py:197 run_groups`
  - ← `ecology.py:513 _challenge`
  - ← `ecology.py:734 step`
- **Not memory.** No OOM entries, and the process stayed small (it peaked at well under 1% of the host's 16 GB).
- **Reproduced on host1 only.** A second-host check is item 7. No other Stage-1 unit has crashed so far.

## Ruling

1. **The unit is CRASHED.**
   - CRASHED is a **unit state, not a call** (SHOULD 4). It sits beside done, VOID (K1/K-SALT) and NOT RUN.
   - It enters no M1 or M4 category. It is not an invalid seed: validity is S at season 59 (§6.1 item 2, line 647;
     T5, line 444), so the point stays 8 of 8 valid.
   - It counts against no registered stop rule. F4 counts SCREEN-CAPPED seeds only; K2's pooled VOID is N only (§5.5,
     line 567).
   - The integrity section records:
     `CRASHED: 1/c2-p030-U-G/129001/M (native SIGSEGV in libmujoco 3.14.0, projectOriginPlane under mjc_ccd), x4`.
   - The point's M row reads **M 7 of 8 (1 CRASHED)** wherever its n is printed.
2. **No re-run in Stage 1 or anywhere in RBT-129** (SHOULD 6, SHOULD 8).
   - **Not on another MuJoCo build or a patched build, and no code guard.** A one-path patch could be byte-identical on
     every trajectory that never enters the faulting path. Even so:
     - the patched continuation is arbitrary physics at the event;
     - the patch would be designed after a trajectory-dependent event;
     - it needs a new pinned tree and an adversary pass, all for a column that can decide nothing (item 4).
   - **No substitute seed** (§4.2, line 378; F4, line 213).
   - **No resume from an earlier state.** The crash is deterministic, so this would need a perturbation, which is a
     substitute seed.
   - **If R-B extends this point to n = 16**, 129001's M stays CRASHED: 15 of 16, with no stand-in drawn from seeds
     9–16.
3. **Quarantine** (MUST 2).
   - **Where the partial run lives.** Periodic snapshots of the partial run already sit on
     `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M` (`stages.py` `_every` line 689, `_label`). The partial `run.log`
     also sits there and in host1's unit directory.
   - **Keep the branch (R12).** No session restores, checks out or reads it before the RBT-129 readout is complete.
     After that, only the item-7 diagnosis may use it, and that diagnosis reads crash data only.
   - **The M/N readout script refuses the label `rbt-129-stage1-c2-p030-U-G-129001-M` mechanically**, and a test
     covers that refusal. Neither its files nor its branch enter any table, mean, figure or check.
   - **Nothing about how far the unit got is reported**: no season, wall time, population, fauna or member.
4. **What the point's M arm feeds, and how n = 7 is handled** (MUST 1). To make "no verdict or BH tally turns on this
   column" true, two scopes are **pinned now**:
   - **(a) Share BH families hold only points where N ran.** The share WIN, TIE and CONTINGENT families (§7.1, line 870)
     contain only those points. A NOT RUN point's y′ (§6.1, line 632; §5.3b) is printed descriptively and never
     tested, so it never enters a BH ranking.
   - **(b) RESOLVING is evaluated only where M and N both ran.** That is, the M-arm g0 at its 90% bounds (§6.2,
     line 723). A NOT RUN point is never counted as RESOLVING: not in §8 (verdict 6's share route, line 978), not in
     M4, and not in the §6.3 cross-tab.

   With (a) and (b) pinned, this point's M arm feeds only descriptive outputs, each computed on the 7 completed seeds
   with no imputation:

   | output | ref | how the 7 seeds are used |
   |---|---|---|
   | the share change y′ (descriptive) | §5.3b, §6.1 | printed at n = 7 |
   | the one-world performance column and the interference table (M minus S, per fauna) | §5.3a line 474, §5.3b line 483; M6 line 918 | **S paired on the same 7 seeds** (SHOULD 3) |
   | the regime readout "on every S and M arm" | §5.3d, line 506 | M arm at n = 7 |
   | M2's share model and the secondary share Wald T1 | §7.2, line 895; §7.3, line 926 | n = 7 at this point; both are descriptive at Stage 1 because they are not identifiable on one habitable point (NOTE 3) |
   | verdict 4's denominator, "points with an M arm" | §8, line 971 | unchanged: the point still has an M arm; X-WIN needs N |

   - **S at 129001 is untouched everywhere else**: income, survival, perception, levers, retention.
   - **Sensitivity** (SHOULD 2). Where a logical bound exists, the readout prints the logical bounds of the 8-seed value
     with the missing seed anywhere in its range. For y′ the range is [−s₀, 1 − s₀], where s₀ is 129001's holistic share
     at season 59, read from S60 at readout time. It is labelled "bound under arbitrary missingness". It holds only under the readout's convention for a world that
     empties before season 240; the readout plan states that convention, and if it sets the share outside [0, 1], the
     bound is not printed. Income flow has no
     such bound, and the readout says so. No min/max-of-7 substitute is printed.
5. **Future crashes** (MUST 5, SHOULD 7, SHOULD 9).
   - **What counts as CRASHED.**
     - It counts only if two attempts in a row of the same job fault **inside libmujoco**, at **the same instruction**,
       by dmesg or by a faulthandler stack in `mj_step`.
     - One of those two attempts must run at WORKERS=1.
     - SIGKILL, OOM, or a fault in any other library is not CRASHED. It is retried under the runner's brief.
   - **With one CRASHED unit already on record, any further CRASHED unit, at any point and in any arm** (M, N, or the
     anchor fallback's M and N under T7), means:
     - the coordinator stops issuing new lane files and restarts for M/N jobs;
     - in-flight jobs finish;
     - no unit is excluded, re-run or replaced until there is a new ruling;
     - the M/N readout plan is not committed until that ruling has an adversary pass.

     A second crash makes crashes a pattern. Their spread over points, faunas and seeds is then informative, and in
     particular a second crash on 129001 implicates the census adoption first (NOTE 2).
   - **Why an N-arm crash matters.** It is not a share call: none is reachable at Stage 1, because every N point is
     PARTIAL, by §6.1 item 2 and the gate table. It matters because of K2's pooled stage check, which VOIDs the stage's
     share layer (§5.5, line 567), and because of the pooled null variance (§6.1 item 6).
   - **An S-arm crash** is outside this ruling. It stops the hive at once, because it touches the income layer and every
     verdict.
6. **Physics pinned for the rest of RBT-129** (MUST 4).
   - Every remaining RBT-129 launch must refuse any installed MuJoCo other than 3.14.0
     (`importlib.metadata.version("mujoco")`). The unit's `platform.json` is the confirmation at readout time
     (item 7). This applies to Stage 2, R-B, the retention arms and the anchor fallback.
   - The refusal is added to the launch tool before the next RBT-129 launch, with its own adversary pass.
   - `pyproject.toml`'s `mujoco>=3.1` stays as it is for other work.
7. **Diagnosis and the second host** (MUST 4, SHOULD 1).
   - **Second host, before the readout plan is committed.** Run the job once on a second host, starting from `ckpt60`,
     not from the quarantined branch. **Outside run-lane (R2-1):** call the job's ecology command directly with
     `NO_DURABLE=1`, in a scratch directory outside `runs/`, so no save can reach any `ckpt/` branch. The run uses a
     label of its own. Its stdout and stderr pass only through a filter that keeps the `Fatal Python error` block. If it
     runs past the crash, stop it at 2 h. Either way, delete the scratch directory unread when it exits. A run that does
     not crash is a re-rule trigger only, never a stand-in for the CRASHED seed (item 2). Keep only:
     - the exit code;
     - the dmesg instruction pointer, or the faulthandler frames, captured by a filter that prints only the
       `Fatal Python error` block.
     If it does not crash on the second host, the unit is re-ruled before the readout plan: physics is then
     host-dependent, which is a sweep-wide integrity question.
   - **Version provenance.** At readout, the integrity section confirms from every Stage-1 unit's `platform.json` that
     each one ran MuJoCo 3.14.0. `platform.json` is provenance, not outcome. Any other version is re-ruled.
   - **Mechanism.** The full diagnosis runs only **after the M/N readout plan is committed**, in a crash-only session.
     It reports the mechanism only: no season, fauna, member, group composition or population figure. Its fix applies
     to **later registrations only**, never to RBT-129.
     - A first hypothesis: `Simulation.step` keeps stepping an exploded robot. If confirmed, whether non-finite states
       occur without crashing in other M arms is an integrity question for a later registration (NOTE 6).

## Adversary record

| item | resolution in r2 |
|---|---|
| MUST 1 | item 4 (a), (b) and the table |
| MUST 2 | item 3 |
| MUST 3 | "What has been seen", and the wall time struck |
| MUST 4 | items 6 and 7 |
| MUST 5 | item 5 |
| SHOULD 1 | item 7 |
| SHOULD 2 | item 4, sensitivity |
| SHOULD 3 | item 4 table |
| SHOULD 4 | item 1 |
| SHOULD 5 | header |
| SHOULD 6 | item 2 |
| SHOULD 7 | item 5 |
| SHOULD 8 | item 2 |
| SHOULD 9 | item 5 |
| NOTE 1 | Facts |
| NOTE 2 | Facts; item 5 |
| NOTE 3 | item 4 table |
| NOTE 6 | item 7 |
| R2-1 | item 7 (outside run-lane, `NO_DURABLE=1`, scratch dir deleted unread) |
| R2-2 | "What has been seen" (deadline and disclosure) |
| citations | item 3 (`_every` line 689); item 4 table (§5.3a line 474) |
