# RBT-105 pre-registration: oscillator fate, founding population or run history?

Written by the RBT-105 designer, 2026-09-26, **before any arm**. No arm has been launched. The adversary is named by the coordinator.

**Amended 2026-09-26, still before any arm**, after the design adversary's report (PR #154, `runs/RBT-105/adversary/ADVERSARY.md`) and the coordinator's ruling on RBT-105 (17:35 UTC, CLEAR-WITH-AMENDMENTS). The eight items, and where each lands:

| # | ruling | where |
|---|---|---|
| 1 | The breed key collided with PR #146's salt key. Move it to a namespace no salt key can reach, refuse the two flags together, test that there is no collision for K, S ≤ 16, and re-run the throwaway's K ≥ 1 legs. | §1 |
| 2 | Qualify "the worlds are untouched" by `regrow_delay`. | §1 |
| 3 | R1, the graded flip count, is the primary rule. R0 is printed, labelled "q > 0 only". | §3 |
| 4 | R2 is the secondary test: a replicate-only permutation test on the late-season oscillator birth rate. | §3 |
| 5 | Every FOUNDERS verdict carries m, the q it excludes at 95%, and P(FOUNDERS \| founders fix the fate). | §3 |
| 6 | Wave 2 runs unconditionally: 17 arms. | §2 |
| 7 | `aa_spread.py` → `aa_spread.txt`, report-only. | §3 |
| 8 | Two arms per session at `WORKERS=2`, paired across seeds; `waves.txt`. | §4, §5 |

The first version's text is replaced where it changed, and the original is in git history (commit 59cdab7).

**The question** (RBT-90 part 2, F4 of `runs/RBT-90/adversary-part2/ADVERSARY.md`, ruled in `runs/RBT-90/PART2-VERDICT.md`):
- Oscillator carriage split 5/5 across ten founding populations: discarded 0, 0, 1, 0, 2 against acquired 16, 10, 18, 39, 9 (`part2-readout.txt`).
- With one run per founding population, founders and history are confounded.
- This design replays each founding population with a different breeding stream and asks whether the fate comes back.

## 1. The flag: `--breed-stream K` (new; no existing flag does this)

**Why no existing flag does it.**
- RBT-95's streams (`spawn_streams` in `rabbitstew/evolution.py`) give each fauna one generator. The holistic stream draws the founders and their staggered ages first, then every later holistic draw.
- `--seed` moves all three streams at once, so it changes the founders as well as the history.
- `--from-holistic RUN` loads the founders but keeps `--seed`'s streams. To vary the history with it, you have to change `--seed`, and that also changes the designed-body fauna and every world.
- `--shift` and `--cull` change the economy, not the stream.
- No existing flag varies only what comes after the founders.

**The change** (`rabbitstew/ecology.py`, `rabbitstew/cli.py`). The flag sets `EcologyConfig.breed_stream`.
- Once both faunas' founders and ages are drawn in `Ecology.__init__`, K ≥ 1 replaces the holistic generator with `default_rng(breed_seed_sequence(seed, K))`, whose spawn key is **`(holistic index, 0, K)`, that is `(0, 0, K)`**.
  - That key is one level below the holistic founders' own key `(0,)`, so the stream is independent of every stream `spawn_streams` makes.
  - It is three long, so it can never equal a two-long key.
- **Amendment 1 (key collision).**
  - The first version used `(0, K)`. That is exactly RBT-96's `--holistic-stream-salt S` key `(0, S)` (PR #146), so K = S gave one generator: 1000 of 1000 draws identical (adversary `probe_streams.txt`). With both flags set, the history would have replayed the founders' own bits.
  - The key is now `(0, 0, K)`.
  - `breed_stream` together with a non-zero `holistic_stream_salt` is **refused** with a ValueError, until a test shows they compose. The check reads the field by `getattr`, so it works whether or not #146 is merged.
  - K = 0 is unaffected: no replacement.
  - No arm had been run under the old key.
- **Amendment 2 (the worlds).**
  - RBT-90 part 2 runs at `regrow_delay` 0.0: `part2_run.sh` sets no `--regrow-delay`, and the committed `config.json`, e.g. `runs/RBT-90/forage-4/config.json`, has `"regrow_delay": 0.0`.
  - There the food layout comes from `start_seed`, a terrain-stream draw, so "the worlds are untouched" holds for every RBT-105 arm.
  - Under persistent food (`regrow_delay > 0`), `_arena_bank` draws the holistic arenas' food seeds from the holistic stream, so K would also move the holistic fauna's arenas. The help text and the field comment say so.
- Everything the holistic fauna draws afterwards comes from the replicate:
  - its season groupings;
  - breeding order, mate choice and crossover decisions;
  - its children's mutations;
  - a cull, if one were set.
- What stays fixed:
  - the designed-body stream and the terrain stream, so the worlds (terrain and start seeds) are untouched;
  - the founders' genomes and ages, which were drawn before the switch.
- `K = 0` (or the flag absent) is the original stream: no replacement, byte for byte.
- The value is written to `config.json` (`ecology.breed_stream`) and survives `--resume`. The checkpoint saves the replaced generator's state, like any stream.
- **One visible difference from an RBT-90 arm:** `config.json` gains the key `"breed_stream"`. `lineage.jsonl`, `cohorts.jsonl` and every table are unaffected at K = 0.

**What "season 0 identical" means here.**
- The founders are identical at season 0: genotypes, names and ages. Each founder's genome file carries its age in `record.age`.
- The worlds are identical too.
- The season-0 contest is not identical. Its groupings are the first draw of the new history, so the holistic season-0 scores already differ at K ≥ 1. This is intended: who meets whom is history.

**Tests** (`tests/test_ecology_switches.py`, five new):
- `test_breed_stream_keeps_the_founders_and_replaces_only_the_holistic_history` checks:
  - K = 0 is byte-identical to the flag being absent (`lineage.jsonl`, `cohorts.jsonl`);
  - K = 1 and K = 2 keep the founders' genome files, and each founder's generation-0 name and age;
  - the designed-body lineage and the worlds are byte-identical;
  - the holistic lineage differs from the original's, and between K = 1 and K = 2;
  - K = 1 run twice is byte-identical.
- `test_a_replicate_history_resumes_byte_for_byte`.
- `test_a_negative_breed_stream_is_refused`.
- `test_the_breed_key_never_collides_with_a_salt_key_or_a_founder_stream` (amendment 1): for K, S ≤ 16 on seeds 7 and 805, the generator states of every breed key and of every salt key `(i, S)`, for all three stream indices, plus the three unsalted streams, are disjoint. The first key would have failed it: 16 of 16 collide.
- `test_breed_stream_is_refused_with_a_holistic_stream_salt` (amendment 1).
- Full suite: `pytest -q`, **289 passed** on this branch (the design adversary counted 287 before the two new tests).
- On a trial merge of this branch with `claude/new-session-4cao7d` and PR #146 (auto-merged, no conflict), `tests/test_ecology_switches.py` and `tests/test_rng_streams.py` pass: 29 tests. There the refusal test exercises #146's real `holistic_stream_salt` field.

**The throwaway run on a real seed** (`throwaway.sh` → `throwaway.txt`; `throwaway_check.py` reads the bulk). It was **re-run after amendment 1 with the new key** (all three legs, K = 0 included), and `throwaway.txt` is the re-run.
- Seed 7 ran for 20 seasons at K = 0, 1 and 2 through `run_arm.sh` itself. It was compared with the RBT-90 part 2 arm `forage-7`, restored from `ckpt/rbt-90-7`.
- **ALL PASS under the new key.**
  - **Season 0:** every arm's founders are byte-identical to the RBT-90 arm's (genome files with ages), and they match `founders-rbt90.txt`.
  - **K = 0 reproduces the arm:** `lineage.jsonl` (2126 lines) and `cohorts.jsonl` (40 lines) are byte-identical to the RBT-90 arm's first 20 seasons, and `seasons.txt` matches the committed rows.
  - **K = 1 and K = 2 diverge:**
    - the holistic lineage and grouping lines differ from season 0;
    - no birth line is shared with the RBT-90 arm at K = 1, and one at K = 2;
    - the two replicates differ from each other;
    - the designed-body lineage and cohort lines, and the worlds, stay byte-identical.
  - **The new key gives new streams:** K = 1 and 2 wrote 2305 and 2181 lineage lines, against 2188 and 2208 under the old key.
  - The post-run step wrote `osc_births.txt` on every leg.
- This ran on the current code with numpy 2.4.6 and mujoco 3.14.0, the versions in this container.
- The design adversary reproduced the first version's checks on a second seed (805, 8 seasons, `WORKERS=2`; `adversary/repro805.txt`). That was under the old key, and K = 0 does not depend on the key.

**Founder fingerprints** (`founders.py` → `founders-rbt90.txt`):
- The SHA-256 of each RBT-90 part 2 arm's founder genome files, per fauna, for all ten seeds, from their checkpoints.
- Every arm's `post_run.py` compares its own founders against this line (`pairing.txt`), so the founder identity of each replicate is checked from committed files.

## 2. Seeds, replicates and power

**Both waves run, unconditionally (amendment 6): 16 replicate arms plus the positive control, 17 arms.**
- The question is how much the founders matter. R1 and R2 only have useful power at 8 seeds (0.84–0.85 at icc 0.7, below).
- The seeds are taken nearest the boundary first, by the readout's own count (distinct bests carrying a linked oscillator, `oscillator.txt`).
- Wave 1 is sessions 1–4 of `waves.txt`, so it launches first.

| wave | seed | RBT-90 fate | distinct | replicate streams |
|---|---|---|---|---|
| 1 | 7 | discarded | 2 | K = 1, 2 |
| 1 | 805 | discarded | 1 | K = 1, 2 |
| 1 | 4 | acquired | 9 | K = 1, 2 |
| 1 | 807 | acquired | 10 | K = 1, 2 |
| 1 | 7 | (positive control) | — | K = 0 |
| 2 | 806 | acquired | 16 | K = 1, 2 |
| 2 | 2 | acquired | 18 | K = 1, 2 |
| 2 | 1 | discarded | 0 | K = 1, 2 |
| 2 | 804 | discarded | 0 | K = 1, 2 |

- Seeds 801, 804 and 1 all sit at 0 distinct. The tie is broken by the rate of linked oscillators at birth, highest first: 1 (0.021), 804 (0.018), 801 (0.014), from `part2-readout.txt`.
- Seed 3 (39) and seed 801 are left out, being the furthest from the boundary on each side.

**Two replicate streams per seed, not one or three.**
- Two replicates give each founding population three runs, counting the original, and double the chance of seeing a flip compared with one.
- A third replicate adds less than a new seed does, because the question is about populations.

**Power, both directions** (the design adversary's `adversary/power.py` → `power.txt`, 4000 simulations per cell).
- Under a latent-propensity model, the founders' share of the variance is icc. icc = 0 is pure history; icc = 1 means the founders fix the fate.
- Seed selection copies this design: the outcome-selected seeds nearest the bars, two replicates each.
- Each cell is the probability that the verdict fires, at 8 seeds × 2 replicates (m = 16), two-state model (primary; RBT-90's counts are bimodal):

| icc | R1 FOUNDERS DOMINANT | R1 SUBSTANTIAL HISTORY | R2 p ≤ 0.05 | R0 HISTORY (q > 0) | R0 FOUNDING |
|---|---|---|---|---|---|
| 0 (pure history) | 0.033 | 0.949 | 0.054 | 1.000 | 0.000 |
| 0.3 | 0.255 | 0.675 | 0.311 | 0.997 | 0.001 |
| 0.5 | 0.552 | 0.382 | 0.587 | 0.969 | 0.012 |
| 0.7 | 0.837 | 0.122 | 0.851 | 0.863 | 0.056 |
| 0.9 | 0.984 | 0.009 | 0.985 | 0.461 | 0.235 |
| 1 (founders fix the fate) | 1.000 | 0.000 | 1.000 | 0.021 | 0.444 |

- Under the secondary lognormal model at m = 16, R1 FOUNDERS DOMINANT has probability 0.028 at icc 0 and 0.997 at icc 1, and R2 has 0.048 and 1.000.
- The icc = 0 row is the matched null for every "founders matter" verdict. The icc = 1 row is the matched null for every "history" verdict.
- R1 and R2 hold their size (0.033, 0.054; lognormal 0.028, 0.048). R0 does not answer "how much": it says HISTORY 0.86 of the time even at icc 0.7. That is why it is demoted to a report.
- At wave 1 alone (m = 8) R1 and R2 detect only icc ≳ 0.8 (0.54 and 0.51 at icc 0.7; `power.txt`). Hence amendment 6.
- The first version's table, P(≥ 1 flip) = 1 − (1 − q)^m, is arithmetically right but covered only one direction. It is superseded by this one.

## 3. The readout, and the rule (fixed now)

**The count and the bars** are RBT-90 part 2's, imported unchanged.
- `readout.py` loads `runs/RBT-90/part2_readout.py` and uses its `OSC_DISCARD = 2`, `OSC_ACQUIRE = 8` and `osc_fate`.
- The count is `distinct` from RBT-84's `oscillator_rate.py`, run unmodified by `post_run.py`: the distinct saved-best genotypes carrying a linked oscillator.
- ≤ 2 is discarded, ≥ 8 is acquired, and 3–7 is undecided.
- An arm whose holistic fauna has no best at season 590 is EXTINCT, and it is treated as undecided.

**Flips.**
- A replicate is *decided* if its fate is discarded or acquired.
- It *flips* if it is decided and its fate is opposite to its original's.
- F = flips among the n decided replicates. All 16 originals are decided.

**R1, the graded flip count: the PRIMARY rule** (amendment 3).
- **FOUNDERS DOMINANT** if P(Bin(n, ½) ≤ F) ≤ 0.05. At n = 16 that is F ≤ 4; at n = 8, F ≤ 1.
  - Under pure history, the balanced design (as many discarded as acquired originals) makes the expected flip rate ½, whatever the base rate of acquisition: a discarded seed flips at rate p, an acquired one at 1 − p.
- **SUBSTANTIAL HISTORY** if P(Bin(n, 0.1) ≥ F) ≤ 0.05. At n = 16 that is F ≥ 5; at n = 8, F ≥ 3.
- **NOT DECIDED** otherwise.
  - At n = 16 the two bars meet (F ≤ 4 or F ≥ 5), so NOT DECIDED arises only when undecided or extinct replicates reduce n. At n = 12, for example, F = 3 is between the bars (`smoke.txt`).
- **The FOUNDERS DOMINANT wording** (amendment 5) always carries:
  - n;
  - the flip rate it excludes at 95%, the one-sided Clopper–Pearson upper bound: 0.17 at F = 0 of 16, 0.26 at 1 of 16, 0.31 at 0 of 8;
  - P(FOUNDERS DOMINANT | founders fix the fate) from `power.txt`: 1.000 two-state and 0.997 lognormal at n = 16; 0.986 and 0.788 at n = 8.

**R2, a replicate-only permutation test: SECONDARY** (amendment 4).
- **The quantity.** Each replicate's y = log((k + 0.5) / (n + 1)), where n is its holistic births in seasons 300–599 and k how many of them carry a linked oscillator.
  - Both come from `osc_births.txt`, written by `osc_births.py` in the post-run step, using the adversary's definition in `probe_distinct.py` unchanged.
  - The +0.5 and +1 keep a zero count finite, as `log(distinct + 0.5)` does in `power.py`.
- **The statistic.** T = mean y over the replicates of originally acquired seeds, minus mean y over the replicates of originally discarded seeds.
- **The p-value.** Exact and one-sided, over all C(16, 8) = 12870 relabellings of the 16 replicate arms.
- **The originals are left out.** They were selected on outcome, and a naive ANOVA F that includes them is anti-conservative: 0.077 and 0.078 false-positive rates against a nominal 0.05, `power.txt`.
- **Verdict:** "founders shift the late oscillator rate" if p ≤ 0.05.
- **Why this quantity.** In seasons 300–599 of the RBT-90 arms, the discarded seeds' late rates are 0.004–0.013 and the acquired ones' 0.221–0.337 (0.869 for seed 3), in `osc-births-rbt90.txt`. That is a far cleaner separation than `distinct`. The originals' rates are there for reference only.

**R0, the first version's rule: printed, labelled "q > 0 only".**
- HISTORY on ≥ 1 flip.
- FOUNDING POPULATION if every replicate is decided and equal to its original, with ≥ 2 of each fate, worded with n and the q it excludes.
- NOT DECIDED otherwise.
- It answers only "is the flip rate above zero?", and its HISTORY line says it does not measure how much the founders shift the fate.
- The per-seed classes FLIPS, REPLICATES and UNCLEAR are reported as before.

**Gate.** There is no verdict unless all 17 arms are in and both of these hold (read from `pairing.txt`):
- the positive control reproduced its RBT-90 arm byte for byte (`seasons.txt` and `lineage-last.txt` against the committed files);
- every K ≥ 1 arm kept its founders (fingerprint) and its designed-body `seasons.txt` rows identical to the RBT-90 arm's.

A missing arm is reported as incomplete, with no verdict.

**Reported, not ruled on:**
- the founder lines the living trace to by first parent in each arm (as in `split_probe.txt`);
- whether the RBT-90 winner line wins again;
- each replicate's late rate.

**The ecology A/A spread** (amendment 7): `aa_spread.py` → `aa_spread.txt`, **report-only; it rules on nothing.**
- It is the adversary's F4 script, adopted with its quantities and windows unchanged.
- It reads committed `seasons.txt` only.
- **Quantities:**
  - holistic `mean_lifetime_score` (0 when the fauna is dead, RBT-92's rule);
  - holistic minus conventional `mean_lifetime_score` (R-body);
  - holistic alive;
  - holistic deaths per 10 seasons.
- **Windows:** RBT-92's before window [T − 100, T) and recovery window [T + 60, T + 160) at each seed's committed onset T (`runs/RBT-92/onset.txt`), plus [300, 600).
- **Output:** the RMS of (replicate − original) and RBT-96's half-width 2.776·RMS/2.
- **The header of the output file states the caveat.** These replicates diverge from season 0, while a challenge arm shares its baseline up to T. For the recovery window the spread is therefore an **upper bound** on a challenge arm's own A/A spread, not an estimate of it.
- Conventional quantities are left out: they are identical by construction.

`smoke.sh` → `smoke.txt` exercises every branch of R1, R2 and R0, and `aa_spread.py`, on synthetic arms built from the committed RBT-90 files. Nothing in it is a result.

## 4. Predictions and cost

**Predictions** (written before any arm; the first version's wave-1 R0 predictions are replaced by these, for the amended rule on all 17 arms):

| prediction | confidence |
|---|---|
| The positive control (seed 7, K = 0) reproduces the RBT-90 arm byte for byte | 0.95 (the throwaway reproduces its first 20 seasons byte for byte) |
| Every K ≥ 1 arm keeps its founders and its designed-body rows identical | 0.97 |
| R1: SUBSTANTIAL HISTORY | 0.50 |
| R1: FOUNDERS DOMINANT | 0.35 |
| R1: NOT DECIDED (undecided replicates reducing n) | 0.15 |
| R2 fires (p ≤ 0.05): the founders shift the late oscillator rate | 0.55 |
| R0 prints HISTORY (at least one flip in 16) | 0.85 |
| At least one flip falls on seed 4 or 7 (acquired de novo at 9; discarded at 2 with the most oscillator-carrying founders, 18/60) | 0.60 |
| The RBT-90 winner founder line wins again in fewer than half of the 16 replicate arms | 0.60 |

The reasons for leaning to history come from F4:
- the fate tracked which founder line won (3/5 against 0/5);
- seed 4 acquired entirely de novo;
- neither the early birth rate nor the founders' rate predicts the fate.

In addition, seeds 7 and 805 carried oscillators at birth at 0.157 and 0.183 in seasons 0–149 and then lost them (`osc-births-rbt90.txt`), so discarding is itself a loss after early carriage.

On the other side, the late rates separate the fates cleanly, which R2 could read as a founder effect. Hence R2 at only 0.55.

**Cost** (amendment 8; adversary `packing.txt`).
- Each arm is 600 seasons.
- Timing measured on this container type:
  - one arm alone at `WORKERS=4` runs at 5.5 s per season, matching the RBT-90 logs (58–68 min an arm);
  - **two arms together at `WORKERS=2` each run at 10.2 s per season apiece, 5.1 s per arm-season**.
- Workers do not change a run: the coordinator's ruling in `part2_run.sh`, re-checked by the adversary on 805 at K = 1.
- **17 arms in 9 sessions** (`waves.txt`):
  - 8 sessions of two arms, about 600 × 10.2 s ≈ 1 h 45 min each;
  - one session of a single arm at `WORKERS=4`, about 1 h.
- Pairs are always **across** seeds. No session holds two arms of one founding population, so one lost container never takes both replicates of the same founders.
- The post-run step (summaries, `oscillator_rate.py` and `osc_births.py`) takes minutes. `readout.py` and `aa_spread.py` take seconds.

## 5. The launcher

`runs/RBT-105/run_arm.sh SEED K` → `runs/RBT-105/forage-SEED-bK/`, checkpoint `ckpt/rbt-105-SEED-bK`.
- Every flag is copied from `runs/RBT-90/part2_run.sh`, plus `--breed-stream K`.
- It follows RBT-92's pattern, and the script does each step itself:
  1. Launch the script as a harness background task, never `nohup` (README rule 1).
  2. It starts the run and, beside it, `scripts/durable.sh every 20` with `DURABLE_WATCH_PID` set to the run.
  3. It waits for both.
  4. It runs `post_run.py`: `seasons.txt`, `lineage-last.txt`, `oscillator.txt`, `osc_births.txt` and `pairing.txt`.
  5. It then runs `scripts/durable.sh save` once more, after the tables exist (README rule 6).
- Per arm, commit `config.json`, `seasons.txt`, `lineage-last.txt`, `oscillator.txt`, `osc_births.txt` and `pairing.txt`, and push.
- Name the checkpoint label on the ticket at launch (README rule 3).
- A reclaimed arm: `scripts/durable.sh restore DIR LABEL`, then `RESUME=1 WORKERS=2 runs/RBT-105/run_arm.sh SEED K`.
- **The launch lines are in `waves.txt`:** 9 sessions, two `run_arm.sh` background tasks per session at `WORKERS=2`, each with its own checkpoint label. The launcher itself is unchanged, apart from WORKERS.

Once all 17 arms are in:

```
python runs/RBT-105/readout.py    > runs/RBT-105/readout.txt
python runs/RBT-105/aa_spread.py  > runs/RBT-105/aa_spread.txt
```

## Files

- `PREREGISTRATION.md`: this document.
- `run_arm.sh`: the launcher.
- `post_run.py`: the per-arm tables and the pairing check.
- `osc_births.py`: the per-arm birth-level oscillator rate, R2's input.
- `osc-births-rbt90.txt`: the RBT-90 originals' rates, from their checkpoints; reference only.
- `readout.py`: the rules R1, R2 and R0.
- `aa_spread.py`: the ecology A/A spread, report-only.
- `waves.txt`: the 9 session pairings.
- `founders.py`, `founders-rbt90.txt`: the founder fingerprints.
- `throwaway.sh`, `throwaway_check.py`, `throwaway.txt`: the 20-season check of the flag.
- `smoke.sh`, `smoke.txt`: the rules' smoke test.
- `adversary/`: the design adversary's probes and report (PR #154), brought onto this branch unchanged.
- Code: `rabbitstew/ecology.py`, `rabbitstew/cli.py`, `tests/test_ecology_switches.py`.
