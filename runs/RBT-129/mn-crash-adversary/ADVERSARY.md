# RBT-129 adversary: the crashed M/N unit `1/c2-p030-U-G/129001/M` (draft ruling `mn-crash/RULING.md`)

- **Ruling reviewed:** `runs/RBT-129/mn-crash/RULING.md` at `1f263d1b` (branch `claude/happy-ramanujan-0jka04`).
- **Registered text read:**
  - DESIGN §4.1, §4.2, §5.2, §5.3, §5.5, §6.1–6.3, §7.1–7.3, §8, §9, §11.1;
  - AMENDMENT-FOUNDING F4, F5, F7, T5, T7, T10;
  - `lanes/1-MN/launch.txt` and `gate_table.txt`;
  - house style from `mn-emitter-adversary/ADVERSARY.md`.
- **Code read:**
  - `runs/RBT-129/launch/stages.py`: `stage1_units`, `run_job`, `_ecology`, `save_now`, `_label`, `mn-emit`;
  - `rabbitstew/simulation.py` (`step`, `_check_explosions`);
  - `rabbitstew/ecology.py` (`run`, `resume`), `rabbitstew/cli.py` (`cmd_ecology`), `pyproject.toml`.
- **No-peek.**
  - Nothing was launched or fetched. No `ckpt/rbt-129-stage1*` branch was listed, fetched or checked out.
  - No season table, history, lineage, run.log or readout of any Stage-1 run was read.
  - The only data read is the gate table: registered input whose valid-seed column the table itself declares as seen.

## Verdict: **ADOPT AFTER FIXES**

The core decision is right. CRASHED with no re-run, no substitute seed and no imputation is the least-biased option the
registered text allows:
- §4.2 (line 378) forbids adding a seed or arm after Stage 1 is seen.
- F4 (line 213) says seeds are "never skipped or replaced".
- Every repair would be designed after a trajectory-dependent event.

The missingness probably is informative. Only M arms put the two faunas' bodies in one arena, so the crash plausibly
needs inter-fauna contact. That would tie it to sustained mixing, and so to y′ and fixation. That bias is tolerable only
because the column is descriptive.

But the ruling's central claim is not true as written: that no verdict or tally can turn on this point's M column.
- Two registered channels exist (MUST 1).
- The inventory of what the M arm feeds is incomplete.
- The partial run is not confined to host1, and its run.log holds per-season outcomes (MUST 2, 3).
- Item 6's "fix it for later stages" would split RBT-129's own physics between Stage 1 and Stage 2 (MUST 4).
- Item 5's per-point threshold is too lax once one crash has already happened (MUST 5).

## MUST

1. **Make item 4's "no verdict or tally can turn on this column" true by pinning two scopes now, and correct the
   inventory.**
   - **(a) The share BH families.**
     - §7.1 (line 870) puts the share WIN family "over every Stage 1–2 point (K ≤ 52)". It does not say "points with
       N".
     - y′ is computed from M alone (§6.1, line 632; §5.3b). A readout that tests y′ at every point with
       an M arm would put this point's 7-seed p-value into the BH ranking, which moves the thresholds at other points.
     - §5.2 (line 443) says a share call needs N. It does not say a NOT RUN point's test stays out of the family.
     - Pin it: the share WIN, TIE and CONTINGENT families contain only points where N ran. A NOT RUN point's y′ is
       never tested.
   - **(b) RESOLVING.**
     - §6.2 (line 723) computes g0 from **the M arm** (seasons 180–299), at its 90% bounds over seeds. Nothing restricts
       RESOLVING to points with N.
     - Verdict 6's share route (§8, line 978) counts "RESOLVING points". So a NOT RUN point whose 7-seed M-arm g0 fell
       in the RESOLVING band would enter that denominator. Its interval at df 6 rather than 7 also changes whether it
       passes.
     - Pin it: RESOLVING is evaluated only where M and N both ran. A NOT RUN point is never counted as RESOLVING, in
       §8, M4 or the §6.3 cross-tab.
   - **(c) Inventory.** "Its M arm feeds only the descriptive one-world income column (y′) and the interference table"
     is incomplete and mislabelled: y′ is the share change, not income. The M arm at this point also feeds:
     - M2's share model and the secondary share Wald T1 (§7.2, line 895; §7.3, line 926);
     - the regime readout "on every S and M arm" (§5.3d, line 506);
     - M6's interference table (line 918);
     - verdict 4's denominator, "points with an M arm" (line 971). This is unchanged by 7 of 8, as the ruling says.

     List each use and state how it handles n = 7. With (a) and (b) pinned, none of them is a verdict or a BH tally.
2. **The partial run is not confined to host1. Quarantine it by name.**
   - The M fork is a long job (240 arm-seasons, at least `DURABLE_MIN` = 120), so `_ecology` ran `_every`.
     `_every` takes periodic snapshots to `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M` (`stages.py` `_label`, lines
     697–720).
   - That branch therefore already holds a partial `history.json`, `lineage.jsonl` and `run.log`.
   - Item 3's "it stays on host1 only as long as host1 exists" is wrong. Replace it with:
     - name the branch;
     - keep the branch (R12);
     - the M/N readout script refuses that label mechanically, with a test;
     - no session restores it before the readout is complete.
3. **State how the crash evidence was read, because run.log carries outcomes.**
   - `Ecology.run` logs every season's alive, births, deaths and lifetime scores per fauna (`ecology.py`, line 896). The
     lane sends that output to `<dir>/run.log` (`stages.py`, line 704).
   - Run 4's faulthandler stack and runs 1–3's tracebacks sit in the same file, after those lines.
   - The ruling's opening claim ("no M/N outcome has been read … including the crashed unit's partial run directory")
     must say how the stack was extracted (for example, only the `Fatal Python error` block, by grep). It must say that
     no season line was displayed, or disclose exactly what was seen.
   - Also strike or justify "about 87 min in" (Facts, line 15). Wall time is a proxy for how far the run got, and for
     its population size. Item 3 itself forbids reporting that.
4. **Item 6: "later stages" must mean later registrations, and the physics must stay pinned for the rest of RBT-129.**
   - RBT-129's Stage 2b combines seeds 1–8 and 9–16 by Z = (Z₁ + Z₂)/√2 (§4.2, lines 371–376). Its families run over
     all Stage 1–2 points (§7.1). The anchor fallback forks M and N too (T7).
   - A MuJoCo or code fix applied to "later stages" of RBT-129 would split one map across two physics.
   - `pyproject.toml` requires only `mujoco>=3.1`, and no launch check pins the version. Add this: every remaining
     RBT-129 launch refuses a MuJoCo other than 3.14.0, checked against `platform.json`.
   - The item-6 diagnosis must not run until the M/N readout plan is committed, or its report must not reach the
     author of that plan before then.
   - The report names the mechanism only: no season, fauna, member, group composition or population figure.
5. **Item 5: after this crash, any further CRASHED unit stops new M/N launches and forces a re-rule.**
   - "More than 1 of its M seeds" at one point is too lax:
     - it lets c0-p010-PW-G and c1-p010-PW-G (M1) lose their only M arm without a re-rule;
     - it lets a point at M8 lose 25% of its seeds.
   - More important: with one crash already on record, a second one anywhere makes crashes a pattern. Their spread over
     points, faunas and seeds then becomes informative, and "isolated, descriptive" no longer holds.
   - Also fix the phrase "stop the hive's new launches at that point". It is ambiguous between a moment in time and a
     world point.

## SHOULD

1. **Reproduce once on a second host.**
   - The Facts claim "the crash belongs to the state, not the host" (line 32), but all four runs were on host1.
   - Run it once on another host, from ckpt60, with output discarded except the exit code and the dmesg or faulthandler
     instruction pointer.
   - Also confirm from `platform.json` (provenance, not outcome) that every Stage-1 S and M/N unit ran MuJoCo 3.14.0.
     Item 2's argument ("alters the physics of one unit against every other unit") assumes they all did. Nothing in the
     launch enforces it.
2. **The item 4 sensitivity is not a bound.**
   - Substituting the min or max of the 7 does not bound informative missingness: the missing seed can lie outside
     them. Printed beside the values, it will read as robustness.
   - Either drop it, or use logical bounds where they exist. For example, y′ lies in [−s₀, 1 − s₀], with s₀ known from
     129001's season-59 counts. Say that income flow has no such bound.
3. **Pair the seeds, and say S is untouched.**
   - Compute the interference table and the one-world column against S on the same 7 seeds (§5.3b, line 483: merged
     minus S, per fauna).
   - Use S at 129001 everywhere else unchanged: income, survival, perception, levers, retention.
   - Dropping it anywhere else would be outcome-free but unregistered.
4. **CRASHED is a unit state, not a call.**
   - It enters no M1 or M4 category.
   - It does not count as an invalid seed. Validity is S at season 59 (§6.1 item 2, line 647; T5, line 444), so the
     point stays 8 of 8 valid.
   - It counts against no registered stop rule. F4 counts SCREEN-CAPPED seeds only, and K2's pooled VOID is N only
     (§5.5, line 567). Say so explicitly.
5. **Label the ruling as what it is.**
   - It is a post-launch, outcome-blind addition: a unit state that the registered text does not have.
   - Record it as an amendment row, in the same way T5's slot-freeing was labelled DATA-INFORMED. Cite §4.2 (line 378)
     and F4 (line 213) as the basis for no substitution.
6. **Give item 2 a better reason against a patched build.**
   - A one-path patch of the same 3.14.0 source, built with the same flags, would be byte-identical on every trajectory
     that never enters the faulting path. That can be checked without reading outcomes, by hash-comparing completed
     units.
   - The real reasons are these:
     - the patched continuation is arbitrary physics at the event;
     - the patch is designed after a trajectory-dependent event;
     - it needs a new pinned tree and an adversary pass, all for a descriptive column.
   - Keep the decision and change the reason.
7. **Restate why an N-arm loss matters.**
   - Item 5 says share calls are at stake at N points, but none is reachable at Stage 1. Every N point has 1–2 valid
     seeds of 8 (`gate_table.txt`, ranks 3, 5, 6, 7), so it is PARTIAL (§6.1 item 2) whatever M and N show.
   - What an N crash does put at stake is K2's pooled stage check, which VOIDs the share layer for the whole stage
     (line 567), and the pooled null variance (§6.1 item 6).
8. **R-B carry-over.** If R-B extends this point (§4.2, line 371), state that 129001's M stays CRASHED at n = 16
   (15 of 16), with no stand-in drawn from seeds 9–16.
9. **Item 5's criteria:**
   - the fault must lie in libmujoco (dmesg, or a faulthandler stack in `mj_step`), at the same instruction on both
     failures;
   - SIGKILL, OOM or a fault in another library is not CRASHED: it is retried;
   - an S-arm crash is outside this ruling and stops the hive (it would touch the income layer and every verdict);
   - the rule covers the anchor fallback's M and N (T7) as well.

## NOTE

1. **The K-SALT fact is wrong for this seed.**
   - At 129001 the salts are (0, 0), so S60 is the adopted census run (`stages.py`, line 1310), and no K-SALT runs
     there. K-SALT applies only where s ≥ 1 and t = 0 (F7, lines 265–266).
   - "Its K-SALT reference is PASS" presumably means 129002 and 129003 at this point. Fix the wording.
2. **Seed 129001 is special.**
   - It is `RESUME_SEED`: its ckpt60 is the adopted census S 0–59 state, the only seed of its kind (F7, line 260; T10,
     line 500).
   - Nothing so far implicates this. S at 129001 ran 60–299 from the same state without crashing.
   - But 129001 also has M forks at five other points and N at two. If a second crash is on 129001, suspect the
     adoption before chance. MUST 5 already forces the re-rule.
3. **The stakes are larger than "one descriptive seed".**
   - By the gate's valid counts, c2-p030-U-G (8 of 8) is the only Stage-1 M point that is not PARTIAL; every other M
     point has 5 or fewer of 8.
   - So this point is almost all of Stage 1's one-world evidence at a habitable point. The lost seed is material to the
     descriptive layer.
   - M2's registered share fit (habitable points, the Stage-1 grid only) would rest on this one point. It is not
     identifiable at Stage 1 either way.
4. **The pilot rescale sentence is unaffected.** It ("if the pilot's M arms find the real drift…", §5.2, line 452) is
   pilot-only and already ruled not to rescale (#500 item 2; `gate_table.txt` header). Stage-1 M arms cannot trigger
   it.
5. **Dropping the whole point's M column**, rather than one seed, would have no missingness bias. Decided now, it would
   be outcome-blind. It is not better: it throws away the only habitable one-world point to avoid a bias in a
   descriptive column. CRASHED at 7 of 8 is preferred.
6. **The crash path is a natural first hypothesis for item 6.**
   - `Simulation.step` stops driving an exploded robot but keeps stepping the physics.
   - A non-finite `qpos` flags every robot in that simulation as exploded (`_check_explosions`).
   - Garbage pointers in `projectOriginPlane` fit non-finite or degenerate geometry.
   - If item 6 finds "our state", ask whether non-finite states occur without crashing in other M arms. That is an
     integrity question for a later registration, not for this readout.

## Answers to the brief

1. **Least biased?** Yes, among the options the registered text allows.
   - Another build or a code guard changes the physics after a trajectory-dependent event.
   - A substitute seed is forbidden (§4.2, line 378; F4, line 213).
   - A resume from an earlier state reproduces the crash (it is deterministic), or needs a perturbation, which is a
     substitute seed.
   - The informative missingness is real but confined to a descriptive column, once MUST 1 is pinned.
2. **Can no verdict or tally turn on the column?** Not yet true.
   - The share BH family scope and RESOLVING's count in verdict 6 are open channels (MUST 1a, 1b).
   - The inventory misses M2's share model and secondary T1, the regime readout, and M6.
   - Verdict 4 is correctly unaffected: X-WIN needs N.
   - K1, K2 and CONTINGENT are pilot-only or N-only.
3. **Item 5:** too lax once one crash exists (MUST 5). Its criteria need the libmujoco and same-instruction conditions
   (SHOULD 9). Its N rationale is mis-stated (SHOULD 7).
4. **Missing:**
   - quarantine of the snapshot branch and of run.log (MUST 2, 3);
   - Stage-2 physics pinning (MUST 4);
   - S untouched, and seeds paired (SHOULD 3);
   - no stop rule counts CRASHED (SHOULD 4);
   - 129001 as the adopted census seed (NOTE 2).

## r2 fix-check (RULING.md at `eba54655`)

- **Read:** RULING.md r2 in full, and every line it cites in DESIGN, AMENDMENT-FOUNDING and `stages.py`.
- **No-peek:** unchanged. Nothing was launched, fetched or restored. No Stage-1 output was read.

### The five MUSTs

| MUST | r2 | status |
|---|---|---|
| 1. Pin share-family and RESOLVING scope; complete the inventory | item 4 (a) and (b) pin both scopes. The table lists y′, the one-world column and interference, the regime readout, M2 and secondary T1, and verdict 4's denominator. The "income (y′)" mislabel is gone. | **met** |
| 2. Quarantine the snapshot branch | item 3 names `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M`. The branch is kept, the readout script refuses the label, and a test covers the refusal. | **met** |
| 3. Say how the stack was read; strike wall time | the "What has been seen" section separates the coordinator, who saw frames only, from the host1 runner, which opened run.log. Wall time is struck. The runner's own account of how it extracted the frames is deferred ("to be recorded"), with no deadline. | **met, with one gap** (remaining MUST R2-2) |
| 4. Later registrations only; pin MuJoCo; diagnosis after the readout plan | items 6 and 7 meet all three. | **met**, but item 7 adds a new defect (remaining MUST R2-1) |
| 5. Any further crash stops launches and forces a re-rule | item 5 does this, in every arm and the anchor fallback, with the criteria from SHOULD 9. | **met** |

### Citations checked

All of these are correct:
- DESIGN 378, 444 (AMENDMENT-FOUNDING T5), 506, 567, 632, 647, 723, 870, 895, 918, 926, 971 and 978;
- AMENDMENT-FOUNDING F4 213, F7 260 and T10 500;
- `ecology.py:896`;
- §6.1 item 6, for the pooled null.

Two citations are wrong:
- **Item 4's table** cites the one-world performance column as "§5.3b line 483". That column is §5.3**a**, line 474. Line
  483 is the interference row, which is correct for the interference table only.
- **Item 3** cites `_every`/`_label` at "lines 697–720". `_every` starts at line 689 and `_label` at 717, so the range
  is 689–720.

### The y′ bound

- §5.3b (lines 480–482) and §6.1 (line 632) define y′_j as the M arm's mean holistic share over seasons 240–299, minus
  the holistic share at the merge, taken from the season-59 counts.
- The first term lies in [0, 1], and s₀ is the second term. So **y′_j ∈ [−s₀, 1 − s₀] is correct.**
- The 8-seed mean's bound is (Σ₇ y′ + [−s₀, 1 − s₀]) / 8, which is what "the missing seed anywhere in its range"
  means.
- Edge case (NOTE): if the pooled world empties before season 240, the share is undefined. The bound then applies only
  if the readout's convention for an empty world sets the share inside [0, 1]. State that convention.

### New defects in r2

- **R2-1 (MUST): the second-host run in item 7 must not create an un-quarantined M outcome.**
  - It starts from `ckpt60`. If it does **not** crash, it runs to season 300 and produces a complete M run of this
    unit on another host.
  - If it runs through `run-lane` in the same directory, `_ecology` takes periodic saves under the **same label**, so
    it writes into the quarantined branch, or creates new outcomes beside it.
  - Fix:
    - run it outside `run-lane`, with `NO_DURABLE=1`, in a scratch directory with a different label;
    - stdout and stderr go only through the frame filter;
    - the directory is deleted unread when the run exits, whether or not it crashed;
    - if it completes without crashing, the run is a re-rule trigger only, and its output is never a stand-in for the
      CRASHED seed (consistent with item 2).
- **R2-2 (MUST): give the runner's account a deadline and a consequence.**
  - "How it extracted the block is to be recorded from its own account" needs a deadline: before the M/N readout plan is
    committed.
  - It also needs a consequence: if the runner displayed any season line, the integrity section discloses which
    seasons, and the runner's session is not used for any M/N readout work.
- **SHOULD: what the launch refusal checks.** Item 6 checks the MuJoCo version "against the unit's `platform.json`",
  but that file exists only after a run. The refusal before launch should check the installed version
  (`importlib.metadata.version("mujoco") == "3.14.0"`). `platform.json` is the readout-time confirmation that item 7
  already describes.
- **SHOULD: fix the two citations above.**

### r2 verdict: **ADOPT AFTER FIXES**

- **Remaining MUSTs:** R2-1 (sandbox the second-host run, and delete its output unread) and R2-2 (a deadline and a
  consequence for the runner's account).
- Both are wording fixes to items 7 and "What has been seen". Neither needs another adversary pass if they are made as
  stated here.
