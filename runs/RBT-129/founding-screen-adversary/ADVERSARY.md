# RBT-129c (founding screen): adversary report

PR #495, head `71c7d38`, base `claude/new-session-4cao7d` at `fbfdac3`. I checked it against the registered text:
- `AMENDMENT-FOUNDING.md` (F1–F8, T1–T13, §10);
- DESIGN.md §15;
- the ruling on #493 (comment 5883124591);
- `founding-amendment-adversary/ADVERSARY.md`.

I read the whole diff: `rabbitstew/{evolution,ecology,cli}.py`, `runs/RBT-129/launch/stages.py` and the tests.

**What I ran.** Tiny, non-sweep worlds only. I did not run the screen, a salt-0 attempt, or any sweep-world arm. I
restored four committed census and pilot checkpoints read-only, so I could check the new code against real reference
files. That ran no simulator.

The files in this directory:

| file | what it checks |
|---|---|
| `salt0_crossversion.py → .txt` | salt 0, base tree against head tree, every file of 6 arm shapes × 2 seeds × {no flag, explicit `0` flags} |
| `test_founding_screen_adversary.py` | 29 tests, run at the PR head. `test_hole_*` tests pass on the head and pin a defect reported below |
| `mutants.py → mutants.txt` | 30 mutants the implementer did not try, run against the PR's tests and then against mine |
| `cmdlines.txt` | the screen's command lines against the real census `command.txt` |
| `real_checks.py → real_checks.txt` | the adopt config rule, the byte-compare's reference files and the side-effect solvency, all on restored census and pilot checkpoints |

## Verdict: **MERGE AFTER FIXES** (2 MUST, 8 SHOULD; plus 1 condition on the Stage-1 launch, not on this merge)

The core is right:
- the designed salt;
- salt 0's byte identity;
- key safety;
- the screen rule, the cap, the order and the stop rule;
- the gate's logic;
- the 129001 adopt rule;
- K-SALT's placement in Stage 1.

**I found no way to emit Stage-1 lanes when the screen is incomplete, a salt-0 compare is not PASS, or the stop rule
fires,** as long as the records are the lane's own. The gate trusts the records as text (SHOULD 1).

The two MUSTs are small, but each is a registered item the code does not deliver:
- K-SALT is missing on the fork source, where F7 names it;
- F8's founder solvency is not the definition the PR says it is.

## 1. Salt 0 is byte-identical to today: **CONFIRMED**

- **Across versions** (`salt0_crossversion.txt`). The base tree (fbfdac3) and the head tree ran the same tiny world.
  **Every file was IDENTICAL on all 24 comparisons**, `config.json` included:
  - arm shapes: S (two faunas); H alone and D alone (the screen's salt-0 attempt); S killed and `--resume`d; M (the
    season-2 state forked with the merge); N (the same with `merge_null`);
  - seeds 7 and 129002;
  - head runs with no salt flag, and with `--holistic-stream-salt 0 --designed-stream-salt 0` given explicitly, which
    is what `screen_argv` passes at salt 0.
- **The census config.** `adopt_census`'s rule, the census `config.json` against the chain's own S60 config, is
  **EQUAL on the real census `c1-p030-U-L/129001/S`** (`real_checks.txt`). So the 129001 adopt will not be refused
  at launch by a config drift since the census.
- **Keys** (`test_no_key_collides_across_every_stream_the_sweep_can_make`). I checked every stream the sweep can make,
  for seeds 129001–129016:
  - `(i,)`, `(0, s)`, `(1, t)` for s, t in 1–20;
  - the breed stream `(0, 0, K)` for K in 1–20;
  - the merge-null stream `(i, 1, 0)`.

  All 1,040 **pool states** (65 per seed) are distinct, not just the keys. `spawn_streams(seed, s, t)` moves exactly the salted
  entries, for every (s, t) in {0, 1, 20}². Nothing calls `.spawn()` on a population stream, so no child key
  `(1, t)` can arise another way.
- **Isolation and composition on a run** (`test_each_salt_moves_its_own_half_only_and_the_two_compose`, and the
  persistent-food / random-terrain / patches / smell variant):
  - a holistic salt leaves the designed half and the worlds (`terrain_seed`, `start_seed`) byte for byte;
  - a designed salt leaves the holistic half the same way;
  - under (s, t), the holistic half is the (s, 0) run's and the designed half is the (0, t) run's.

  That is K-SALT's premise at the PW points too.
- **Salts survive a fork and a resume** (`test_salts_reach_the_ckpt60_fork_and_every_resume`). At (3, 7), S60 →
  snapshot → resume equals a straight run byte for byte (`history.json`, `lineage.jsonl`, `state.json`). The
  snapshot, the resumed S and an M fork all carry both salts in `config.json`.
- `breed_stream` is refused with either salt, and negative salts are refused on every path.

## 2. Screen semantics

- **W118-b exactly as the census ran it: CONFIRMED.**
  - The emitted `worlds/c0-p030-U-L.json` is identical to the committed one.
  - The screen's command (`cmdlines.txt`) is the **real census `command.txt` for 129002, token for token**, plus only
    `--only-fauna K --{holistic,designed}-stream-salt S`, inserted before `--seed` (checked at salts 0, 1 and 20).
  - The config differs from the census config only in `ecology.only_fauna`, and in the salt key when S ≥ 1.
  - `--capacity 60`, `--fair`, `--sweep-log` and the ruled eating rule are all there; the run is S 0–59
    (`--seasons 60`).
- **"Before refill" is the right reading.** Refill is step 4 of `Ecology.step`: after the season's deaths, breeders
  (energy ≥ `birth_threshold`) fill free slots up to capacity, each child costing its parent `birth_cost`. The history
  row's `alive` is counted after that. So `alive − births` is the number of members who lived through season 59's
  challenge, starvation and age deaths.
  - This is DESIGN §5.1's H53 count and the readouts' count (`stageP0_readout.py`, `stage1_points.py`).
  - On the real census it gives 60 / 59 for 129001 H / D and 0 for 129002 H (last alive at season 10, matching
    `founders.txt`); on the pilot it gives 60 / 60 for 129004 (`real_checks.txt`).
- **Order, first pass kept, cap: CONFIRMED.** At the boundaries:
  - 29 fails and exactly 30 passes;
  - salt 20 is still tried; salt 21 never is;
  - a capped fauna keeps salt 0 and is labelled SCREEN-CAPPED.

  The attempt loop runs no salt after a pass.
- **Stop rule: CONFIRMED** on a table of 9 cases, including {8, 16} (does not fire) and {7, 8} (fires). A seed capped
  on both faunas counts once. Boundary mutants (`>` for `≥`, first half 1–7, holistic only) are killed.
- **Gate: CONFIRMED, with one gap.** `stage1-emit` and `fork-source-emit` refuse (exit 8) on each of these:
  - a missing record;
  - a SALT0 FAIL or a missing SALT0;
  - two capped of seeds 1–8;
  - out-of-order, skipped, extended or re-derived-differently records.

  **The gap** (`test_hole_the_gate_accepts_records_with_no_attempt_behind_them`): SCREEN.json and SALT0.txt are taken
  as text. Hand-written records pass the gate, and 288 Stage-1 units are emitted from them, even with:
  - no attempt directory;
  - a wrong `point`;
  - `criterion: 1`.

  The PR body says "every reader re-derives it from its own attempts". It re-derives the kept salt from the record's
  own alive counts, not from the attempts' `history.json` → SHOULD 1.

## 3. salt0cmp (K-SALT for the screen)

- **Valid.** It compares one fauna's `history.json` rows, re-serialized in order, and its raw `lineage.jsonl` lines,
  at generations / seasons 0–59, between:
  - the single-fauna salt-0 attempt; and
  - the census S (129001–129003) or the pilot S (129004) at W118-b.

  That is F5's registered scope ("that fauna's rows of `history.json` and its lines in `lineage.jsonl`"). RBT-130's
  claim makes it exact: pre-merge cohorts are per fauna, the terrain draws are once per season whatever the cohorts,
  child names are prefixed per fauna, and a dropped fauna's founders are still drawn from their own stream.
  Checked on real references (`real_checks.txt`):
  - the census and pilot halves have 0 duplicated lineage lines in 0–59;
  - living lineage rows equal `alive` at every season;
  - the pilot's S ran on to 300, and its rows after 59 are filtered out. The `generation` of a lineage row is the
    season it was logged. Stage P's double-writes (`dupverify.txt`) were all after season 60.
- **Not vacuous.** An attempt with no history rows or no lineage lines is `EMPTY` → FAIL; a missing reference is a
  length mismatch → FAIL. Killed mutants: the EMPTY guard removed, lineage ignored, the wrong fauna.
  - **One surviving mutant, on both test sets:** the compare drops season 59 from the history rows (`<` for `≤`). The
    PR's tiny tests compare identical runs, so dropping a season changes nothing. I added
    `test_the_byte_compare_sees_season_59_and_nothing_after` → SHOULD 7 (add it).
- **Limited to 129001–129004: consistent with the ruling.** Item 8 says "for 129001–129004", and F5 names the census
  and pilot runs only. But the A-stage S runs for 129005–129008 at W118-b **exist on their checkpoint branches**
  (`ckpt/rbt-129-stage0-c0-p030-U-L-12900{5..8}-S`). They ran under the same launch as the census. Comparing them costs
  no core-h and tests the same claim → SHOULD 2 (open question 3).

## 4. Fork source and Stage 1

- **Fork source: CONFIRMED.** Two faunas, S 0–59, at W118-b at (s_j, t_j), 8 or 16 seeds, gated like Stage 1.
  `test_a_salted_fauna_alone_is_its_half_of_the_salted_two_fauna_run` shows that each screened attempt is its fauna's
  half of the (s_j, t_j) two-fauna run, which is what makes the single-fauna screen valid for this fork source.
- **MISSING: K-SALT at W118-b** (`test_hole_no_ksalt_on_the_fork_source_where_f7_says_the_runs_overlap`). F7 says:
  "The census and the Stage-1 runs overlap for 129002 and 129003 (**and 129007 and 129008 at W118-b**)". Wherever a
  seed runs with s ≥ 1 and t = 0 at a point the census also ran, the designed half must equal. The fork source is
  exactly that run at W118-b, where these two-fauna runs exist:
  - census S for 129001–129003;
  - pilot S for 129004;
  - A-stage S for 129005–129008.

  `fork_source_units` emits no `ksalt` job → **MUST 1**.
- **Stage 1: CONFIRMED.**
  - 36 points × n = 8 = 288 units.
  - 129001 is `adopt` only at (0, 0). At (1, 0), (0, 1) or (2, 3) it is fresh.
  - Every other seed is fresh, with only its non-zero salts in `extra`.
  - K-SALT runs exactly where j ∈ {1, 2, 3}, s ≥ 1 and t = 0. It runs after S60 and before the snapshot, so it reads
    seasons 0–59 of a 60-season directory.
  - Salts reach S60, ckpt60, the S resume and any later M/N fork (§1).
  - K-SALT placement mutants are killed.
- **M / N not emitted: acceptable for this merge.** T9's list of RBT-129c deliverables does not include them, and
  ckpt60 is kept as their fork source. But see **L1** below and open question 2.

## 5. Mutants

- **The implementer's survivor (the explicit order check removed) is equivalent.** `check_screen_record` compares
  `again == {tried, salt, capped}` as a dict, which already fixes the order, the length and the content of `tried`.
  The one record the order check alone might have treated differently is salts written as floats (`0.0 == 0`), and
  it passes with or without the check. `test_a_float_salt_record_is_accepted_equivalent_mutant_reasoning` shows this.
  The only difference is the refusal message.
- **30 new mutants** (`mutants.txt`): MUTANT_SUMMARY

## 6. Suite

SUITE_SUMMARY

## MUST (before merge)

1. **K-SALT on the fork source (F7, "129007 and 129008 at W118-b").** In `fork_source_units`, for each j with
   s_j ≥ 1 and t_j = 0, add a `ksalt` job after the fresh S. Its reference is the two-fauna W118-b run of that seed:
   - `stage0/c0-p030-U-L/<seed>/S` for 1–3 and 5–8;
   - `stageP/c0-p030-U-L/129004/S` for 4.

   Add a test. Seeds 9–16 have no reference and get none.
2. **F8's founder solvency must be the Stage-0 readout's.** `side_effects` keeps only lineage rows with no `death`.
   So a founder that dies in season 0 is not counted as a founder, and every founder's last, dying season is left out
   of its mean. The readout (`stageP0_readout.py` `rows()`) keeps the starved and aged rows; it drops only `cull` and
   `merge-null`.
   - The bias is upward, and it is largest for draws that starve early, which are the rejected ones. So it is biased
     exactly in the accepted-against-rejected contrast R10 asks for.
   - On a written lineage the PR gives 1 / 1 solvent where the readout gives 0 / 2
     (`test_hole_side_effect_solvency_on_a_written_lineage`).
   - On the real census halves it counts 58–59 founders instead of 60 (`real_checks.txt`).
   - **Fix:** founders are the no-parent rows at generations 0–14, death rows included. Solvency is the mean net over
     all their rows (as the readout does, over 0–14). Per-season income should include the season's dead, as the
     readout's `flows` does. Keep `founders_alive` on the living rows.

## Condition on the Stage-1 launch (not on this merge)

- **L1. The gated M/N emitter (T5) must be written, adversaried and merged before any Stage-1 S60 result is read.**
  - T5's seed rule (M only on seeds valid at the merge) and its **DATA-INFORMED slot-freeing rule** decide which points
    get M and N. That is about 171 / 320 core-h of the cost the owner approves.
  - The g0 ranking can be computed now, from the census alone.
  - If the emitter is written after Stage 1's S60 states exist, the selection code is written with the data in view.
    Registering it in code now keeps it pre-data for Stage 1.

## SHOULD

1. **The gate re-derives from the attempts, not from SCREEN.json's numbers.** In `load_screen`, for each attempt,
   check that:
   - `alive59` and `last` equal `attempt_outcome(attempt_dir)`;
   - the attempt's `config.json` is `blocks.config_dict(block argv + screen_argv(fauna, salt), seed, 60)` (bar
     workers);
   - `rec["point"] == SCREEN_POINT`.

   Re-read SALT0's verdict with `half_compare`, not from the first word of `SALT0.txt`. This makes the PR's claim true
   and costs seconds.
2. **Extend salt0cmp to 129005–129008** against the A-stage S at W118-b (branches exist; zero compute), and gate on it
   like 1–4. Otherwise report it; that is the coordinator's call (open question 3).
3. **The side-effect table's groups:** accepted, rejected, and **capped (kept salt 0)** as a third group. A capped
   fauna's salt-0 draw is the one Stage 1 runs, so it should not be pooled with draws that are never run.
4. **Print the census FOUNDING-FAIL layer's numbers beside the founding layer**, not a pointer: holistic 150 / 150,
   designed 34 / 150, from the committed `stageP0-readout/stageP0_readout.txt`, with that source named (open question 5).
5. **`screen-table`, `stage1-emit` and `fork-source-emit` should restore missing `stageF/…/<seed>/<fauna>` directories
   from their checkpoint branches**, as `run_job` does. As written, on any checkout but the lanes' own, the gate says
   "not complete" and the table raises `FileNotFoundError`.
6. **K-SALT VOID should be loud.** Write it to the unit record and print it as a status line that the coordinator sees
   during the run. F7 says a VOID re-opens the stream claim, and waiting for the readout means about 1,000 core-h
   later.
7. **Add `test_the_byte_compare_sees_season_59_and_nothing_after`**, which kills the surviving `≤`→`<` mutant.
8. **Stage-1 unit files survive a lost container.** `restore_record` and `expected_branches` handle only `P/` names.
   A Stage-1 unit's `EXTINCT.txt` is saved to its record branch but never restored, so after a lost container an
   extinct unit's S resume runs on an empty state. The result is harmless but untidy. Extend both to `1/`.

**Nits:**
- `emit_lanes` writes `launch.txt` and an empty lane file before `rel()` refuses a root outside the repository;
- `run_lane` could check a Stage-1 lane's salts against its `launch.txt` `salts` line.

## Open questions: recommended answers

1. **Side-effect table columns.** Keep the four, with MUST 2's founder definition (death rows included) and SHOULD 3's
   third group. The meanings are then:
   - founder solvency = the readout's, over 0–14;
   - founder node count = the mean over the founders drawn;
   - income = the mean net over every member-season, the dead included;
   - births per season.
2. **M/N not emitted.** Acceptable for merging RBT-129c, since T9 does not list it. It is a **launch condition (L1)**: an
   M/N emitter, with its own adversary pass, merged before any Stage-1 S60 result is read.
3. **Salt-0 compare scope.** 129001–129004 is what the ruling requires, and it is met. Add 129005–129008 against the
   A-stage S (SHOULD 2). It costs nothing and tests the same claim; a mismatch there would be the same finding.
4. **Salt 0 writes no config key.** Accept it. Absence reads back as 0 (`EvolutionConfig` default; `from_dict` is strict,
   so an older tree refuses a salted config instead of dropping the key).
   - **Writing `0` would break byte identity**: not of the trajectories, but of `config.json`. That would break the
     golden config test, `adopt`'s census-config equality for 129001, and the cross-version check here.
   - For provenance, `lanes/1/launch.txt` and `lanes/F-fork/launch.txt` already carry `salts 129001:s/t …`, beside
     `stageF/screen_table.txt`. That is enough.
   - Ask the coordinator to note on F3: "written when non-zero; absent means 0, the pre-salt config byte for byte".
5. **The census FOUNDING-FAIL layer is a pointer.** Not enough for F8's "beside it". Print its numbers from the
   committed readout (SHOULD 4). Recomputing it is not needed.
6. **Naming.** F8 is right; the brief's "F6" is a typo. Keep F8.

## Reproduce

At a checkout of the PR head, with this directory copied in, in a clean `.[dev]` venv:

```
python -m pytest runs/RBT-129/founding-screen-adversary/test_founding_screen_adversary.py -q
python3 runs/RBT-129/founding-screen-adversary/salt0_crossversion.py --base <checkout at fbfdac3> --head . > salt0_crossversion.txt
python3 runs/RBT-129/founding-screen-adversary/mutants.py <scratch checkout at 71c7d38 with this dir copied in> > mutants.txt
# real_checks: restore the four checkpoints with scripts/durable.sh restore <dir>/<label> rbt-129-<label> for
#   stage0-c0-p030-U-L-129001-S, stage0-c0-p030-U-L-129002-S, stage0-c1-p030-U-L-129001-S, stageP-c0-p030-U-L-129004-S
python3 runs/RBT-129/founding-screen-adversary/real_checks.py <dir> > real_checks.txt
```
