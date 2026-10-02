# RBT-129 Stage 1 M/N: the unit that cannot complete (coordinator ruling, draft for the adversary)

Written 2026-10-02 ~14:40 UTC. No M/N outcome has been read: no season table, lineage or income of any M/N run,
including the crashed unit's partial run directory. This ruling is written before the M/N readout plan, and that plan
must adopt it.

## Facts (errors only)

- **The unit.** Job `1/c2-p030-U-G/129001/M`, host1 lane 0, pinned trees `rabbitstew 144b3b6`, `launch 7921cde`,
  `scripts d517cf5`. It forks from `stage1/c2-p030-U-G/129001/ckpt60`. Its K-SALT reference is PASS.
- **Four runs, four native crashes in MuJoCo 3.14.0 (pip).**

  | run | start | how it ended |
  |---|---|---|
  | 1 | 12:57:51 | about 87 min in: pool worker SIGSEGV → `BrokenProcessPool` |
  | 2 | 14:25:36 | resume, about 20 s: same |
  | 3 | 14:28:22 | resume at WORKERS=1, about 23 s: ecology exits -11 |
  | 4 | 14:29:44 | diagnostic, PYTHONFAULTHANDLER=1 WORKERS=1, about 21 s: -11 |

- **Same instruction every time.** dmesg logs the same faulting instruction for runs 1–3: file offset `0x1adb65`, which
  is vaddr `0x1aeb65` = `projectOriginPlane`+5. That function is a static helper of the native convex collider,
  reached from `mjc_ccd`. The fault addresses are garbage, so a bad pointer is read; it is not a stack overflow.
  Run 4 left no dmesg line (rate limit); its faulthandler stack is the record.
- **The Python stack (run 4).**
  - `simulation.py:472 step` (`mujoco.mj_step`, the control-substep loop)
  - ← `simulation.py:518 run`
  - ← `run_group`
  - ← `evolution.py:197 run_groups`
  - ← `ecology.py:513 _challenge`
  - ← `ecology.py:734 step`
- **Not memory.** No OOM entries; max RSS about 83 MB; about 15 GB available.
- **The crash belongs to the state, not the host or the pool.** It happens in-process at WORKERS=1, and every resume
  reaches it within about 20 s.
- **No other Stage-1 unit has crashed so far.** That covers all 576 S run dirs, and the M/N jobs so far on all 10
  hosts.

## What the unit feeds (DESIGN §5.2; `launch.txt` "admitted")

`c2-p030-U-G` is admitted at **M8/N0**. It has no N arm, so:
- its share layer reads **NOT RUN** whatever happens to M;
- no WIN/TIE/CONTINGENT call can be made there;
- its M arm feeds only the **descriptive** one-world income column (y′) and the interference table.

The point still counts among "the points with an M arm" (§8, ONE BODY DOMINATES). But verdict 4 needs X-WIN, which needs N,
so this point cannot supply or remove an X-WIN.

## Ruling

1. **The unit is CRASHED.** This is a fourth state beside done, VOID (K1/K-SALT) and NOT RUN.
   - It is recorded in the M/N readout's integrity section as
     `CRASHED: 1/c2-p030-U-G/129001/M — native SIGSEGV in libmujoco 3.14.0 (projectOriginPlane under mjc_ccd), x4`.
   - The point's M row reads **M 7 of 8 (1 CRASHED)** wherever its n is printed.
2. **No re-run in Stage 1.**
   - **Not on another MuJoCo build, and no code change.** Either one alters the physics of one unit against every
     other unit in the sweep.
   - **No substitute seed.** That needs a new S chain, and the substitution would be chosen after a crash that depends
     on the trajectory.
   - **No resume from an earlier state.**
3. **The partial run directory is never read for outcomes.**
   - It stays on host1 only as long as host1 exists. It is not saved to a `ckpt/` branch beyond what run-lane already
     saved.
   - It enters no table, mean, figure or check.
   - Nothing about how far it got is reported. In particular, its last season is not reported, because the point at
     which it crashes is itself trajectory-dependent.
4. **How the point's M column is read.** It is computed over the 7 completed seeds, exactly as it would be over 8,
   with these limits:
   - **No imputation.**
   - **Sensitivity.** The readout prints, beside the point's descriptive M values, the range those values would take if
     the missing seed had sat at the minimum or the maximum of the 7. This is descriptive only, and it is labelled as
     such.
   - **No verdict or tally may turn on this point's M column.** None can under §5.2 and §8 today. If a later amendment
     would let one do so, that amendment must re-rule this unit first.
5. **Any further native crash in Stage 1 M/N follows the same rule.**
   - **What counts.** Two failures in a row at the same job with SIGSEGV/SIGBUS (or `BrokenProcessPool` whose
     worker's dmesg line is a segfault in libmujoco), plus one WORKERS=1 confirmation.
   - **Recording.** The coordinator records the unit as CRASHED and gives the lane's remaining jobs a `-b` lane file
     (as thethirdbearsolutions/rabbitstew#506 did).
   - **When to stop and re-rule.** If a point with an N arm loses a unit, or any point loses more than 1 of its M
     seeds, stop the hive's new launches at that point and re-rule before the readout plan is committed. In that case
     share calls are at stake.
6. **Follow-up, outside Stage 1.** In a crash-only session:
   - reproduce from `ckpt60` with core dumps;
   - report the mechanism: our state, such as an exploded robot that is still simulated or non-finite ctrl, or a
     MuJoCo bug;
   - fix it for later stages only, behind the normal PR and adversary process;
   - report outcomes nowhere.

## Asked of the adversary

- Is CRASHED with no re-run the least-biased option available? Weigh this against informative missingness: the crash
  depends on the trajectory, so it may correlate with the M outcome. Weigh it also against the alternatives in item 2.
- Is item 4's statement true, that no registered verdict can turn on this point's M column? Check against DESIGN §5.2,
  §5.3, §6, §8, §9 and AMENDMENT-FOUNDING T5/T7.
- Are item 5's thresholds right?
