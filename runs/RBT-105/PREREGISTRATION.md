# RBT-105 pre-registration: oscillator fate, founding population or run history?

Written by the RBT-105 designer, 2026-09-26, **before any arm**. No arm has been launched. The adversary is named by the coordinator.

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

**The change** (`rabbitstew/ecology.py`, `rabbitstew/cli.py`; 12 lines). The flag sets `EcologyConfig.breed_stream`.
- Once both faunas' founders and ages are drawn in `Ecology.__init__`, K ≥ 1 replaces the holistic generator with `default_rng(SeedSequence(seed, spawn_key=(0, K)))`. That key is the K-th child of the original holistic stream's own `SeedSequence`, so it is independent of that stream and of the other two.
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

**Tests** (`tests/test_ecology_switches.py`, three new):
- `test_breed_stream_keeps_the_founders_and_replaces_only_the_holistic_history` checks:
  - K = 0 is byte-identical to the flag being absent (`lineage.jsonl`, `cohorts.jsonl`);
  - K = 1 and K = 2 keep the founders' genome files, and each founder's generation-0 name and age;
  - the designed-body lineage and the worlds are byte-identical;
  - the holistic lineage differs from the original's, and between K = 1 and K = 2;
  - K = 1 run twice is byte-identical.
- `test_a_replicate_history_resumes_byte_for_byte`.
- `test_a_negative_breed_stream_is_refused`.
- The switches, RNG-stream, ecology and CLI test files pass: 53 tests (`pytest tests/test_ecology_switches.py tests/test_rng_streams.py tests/test_ecology.py tests/test_cli.py`).

**The throwaway run on a real seed** (`throwaway.sh` → `throwaway.txt`; `throwaway_check.py` reads the bulk):
- Seed 7 ran for 20 seasons at K = 0, 1 and 2 through `run_arm.sh` itself. It was compared with the RBT-90 part 2 arm `forage-7`, restored from `ckpt/rbt-90-7`.
- **ALL PASS.**
  - **Season 0:** every arm's founders were byte-identical to the RBT-90 arm's (genome files with ages), and they match `founders-rbt90.txt`.
  - **K = 0 reproduces the arm:** `lineage.jsonl` (2126 lines) and `cohorts.jsonl` (40 lines) are byte-identical to the RBT-90 arm's first 20 seasons, and `seasons.txt` matches the committed rows.
  - **K = 1 and K = 2 diverge:**
    - the holistic lineage and grouping lines differ from season 0;
    - no birth line is shared with the RBT-90 arm at K = 1, and one at K = 2;
    - the two replicates differ from each other;
    - the designed-body lineage and cohort lines, and the worlds, stay byte-identical.
  - This ran on the current code with numpy 2.4.6 and mujoco 3.14.0, the versions in this container.

**Founder fingerprints** (`founders.py` → `founders-rbt90.txt`):
- The SHA-256 of each RBT-90 part 2 arm's founder genome files, per fauna, for all ten seeds, from their checkpoints.
- Every arm's `post_run.py` compares its own founders against this line (`pairing.txt`), so the founder identity of each replicate is checked from committed files.

## 2. Seeds, replicates and power

**Wave 1** (9 arms, one wave, ≤ 10): the 2 + 2 seeds nearest the boundary by the readout's own count (distinct bests carrying a linked oscillator, `oscillator.txt`):

| seed | RBT-90 fate | distinct | replicate streams |
|---|---|---|---|
| 7 | discarded | 2 | K = 1, 2 |
| 805 | discarded | 1 | K = 1, 2 |
| 4 | acquired | 9 | K = 1, 2 |
| 807 | acquired | 10 | K = 1, 2 |
| 7 | (positive control) | — | K = 0 |

**Wave 2** (8 arms, run only if wave 1's verdict is not HISTORY, and only as capacity allows): the next 2 + 2.
- Acquired: 806 (16) and 2 (18).
- Discarded: 1 and 804. Seeds 801, 804 and 1 all sit at 0 distinct, so the tie is broken by the rate of linked oscillators at birth, highest first: 1 (0.021), 804 (0.018), 801 (0.014), from `part2-readout.txt`.
- Each gets K = 1, 2. The final verdict is computed on the union.
- Adding seeds cannot turn a HISTORY verdict into anything else, and under the founding-population hypothesis a flip has probability 0. The conditional second wave therefore cannot manufacture a HISTORY verdict.

**Two replicate streams per seed, not one or three.**
- Two replicates give each founding population three runs, counting the original.
- They double the chance of seeing a flip where one exists, compared with one replicate.
- A third replicate adds less than a new seed does. The question is about populations, and wave 2 is where the extra runs go.

**Power.** Let q be the chance that a replicate's fate is the opposite of its original's.
- If the fate were pure history (founders irrelevant, each run a fresh draw at the observed 5/10 base rate), q = 0.5.
- If it were fixed by the founders, q = 0.
- The probability that at least one of m replicate arms flips is 1 − (1 − q)^m:

| q per replicate | wave 1 (m = 8) | waves 1 + 2 (m = 16) | P(a FOUNDING POPULATION verdict at wave 1, wrongly) |
|---|---|---|---|
| 0.5 (pure history) | 0.996 | 1.000 | 0.004 |
| 0.3 | 0.942 | 0.997 | 0.058 |
| 0.2 | 0.832 | 0.972 | 0.168 |
| 0.1 | 0.570 | 0.815 | 0.430 |

- At wave 1 the design detects pure history almost surely, and a history effect of q = 0.3 with probability 0.94.
- It cannot tell "fixed by the founders" from "a weak history effect, q ≲ 0.1". A FOUNDING POPULATION verdict therefore means *no flip at m replicates*, and it will be worded with its m.
- These probabilities assume independent replicates with a common q. The boundary seeds are chosen because q should be largest there, so these figures are conservative for wave 1.

## 3. The readout, and the rule (fixed now)

**The count and the bars** are RBT-90 part 2's, imported unchanged.
- `readout.py` loads `runs/RBT-90/part2_readout.py` and uses its `OSC_DISCARD = 2`, `OSC_ACQUIRE = 8` and `osc_fate`.
- The count is `distinct` from RBT-84's `oscillator_rate.py`, run unmodified by `post_run.py`: the distinct saved-best genotypes carrying a linked oscillator.
- ≤ 2 is discarded, ≥ 8 is acquired, and 3–7 is undecided.
- An arm whose holistic fauna has no best at season 590 is EXTINCT, and it is treated as undecided.

**Per seed**, comparing its replicate arms with the RBT-90 part 2 arm (the K = 0 stream):
- **FLIPS**: at least one replicate's fate is decided and opposite to the original's.
- **REPLICATES**: every replicate is decided and equal to the original.
- **UNCLEAR**: anything else (a replicate undecided or extinct, and none flips).

**Overall:**
- **HISTORY**: at least one seed FLIPS. The same founders reach both fates, so the fate is not a property of the founding population. The wording gives the count: "on k of n founding populations".
- **FOUNDING POPULATION**: no seed flips, every seed REPLICATES, and the replicating seeds include ≥ 2 discarded and ≥ 2 acquired founding populations. The fate replicates within populations and differs between them. The wording gives m, per §2.
- **NOT DECIDED at this n**: anything else.

**Gate.** There is no verdict unless both hold (read from `pairing.txt`):
- the positive control reproduced its RBT-90 arm byte for byte (`seasons.txt` and `lineage-last.txt` against the committed files);
- every K ≥ 1 arm kept its founders (fingerprint) and its designed-body `seasons.txt` rows identical to the RBT-90 arm's.

A missing arm is reported as incomplete, with no verdict.

**Reported, not ruled on:**
- the founder lines the living trace to by first parent in each arm (as in `split_probe.txt`);
- whether the RBT-90 winner line wins again.

`smoke.sh` → `smoke.txt` exercises every branch of the rule on synthetic arms built from the committed RBT-90 files. Nothing in it is a result.

## 4. Predictions and cost

**Predictions** (written before any arm):

| prediction | confidence |
|---|---|
| The positive control (seed 7, K = 0) reproduces the RBT-90 arm byte for byte | 0.95 (the throwaway reproduces its first 20 seasons, 20/20 seasons byte for byte) |
| Every K ≥ 1 arm keeps its founders and its designed-body rows identical | 0.97 |
| Wave-1 verdict HISTORY | 0.70 |
| Wave-1 verdict FOUNDING POPULATION | 0.12 |
| Wave-1 verdict NOT DECIDED (replicates landing in 3–7, no flip) | 0.18 |
| The first flip, if any, is on seed 4 or 7 (acquired de novo at 9; discarded at 2 with the most oscillator-carrying founders, 18/60) | 0.60 |
| The RBT-90 winner founder line wins again in fewer than half of the 8 replicate arms | 0.60 |

The reasons for predicting HISTORY come from F4:
- the fate tracked which founder line won (3/5 against 0/5);
- seed 4 acquired entirely de novo;
- neither the early birth rate nor the founders' rate predicts the fate.

**Cost.**
- Each arm is 600 seasons. The RBT-90 part 2 logs for seeds 7, 805, 4 and 807 give 58–68 min per arm at `WORKERS=4` (their `run.log` season timings summed).
- The throwaway, three arms at one worker each sharing four cores, ran at about 36 s a season, which would be about six hours for 600 seasons, so **launch with `WORKERS=4`**. Workers do not change a run (the coordinator's ruling in `part2_run.sh`).
- Wave 1 is 9 arms, about 9 session-hours in one wave. Wave 2 is 8 more.
- The post-run step (summaries and `oscillator_rate.py`) takes minutes, and `readout.py` takes seconds.

## 5. The launcher

`runs/RBT-105/run_arm.sh SEED K` → `runs/RBT-105/forage-SEED-bK/`, checkpoint `ckpt/rbt-105-SEED-bK`.
- Every flag is copied from `runs/RBT-90/part2_run.sh`, plus `--breed-stream K`.
- It follows RBT-92's pattern, and the script does each step itself:
  1. Launch the script as a harness background task, never `nohup` (README rule 1).
  2. It starts the run and, beside it, `scripts/durable.sh every 20` with `DURABLE_WATCH_PID` set to the run.
  3. It waits for both.
  4. It runs `post_run.py`: `seasons.txt`, `lineage-last.txt`, `oscillator.txt` and `pairing.txt`.
  5. It then runs `scripts/durable.sh save` once more, after the tables exist (README rule 6).
- Per arm, commit `config.json`, `seasons.txt`, `lineage-last.txt`, `oscillator.txt` and `pairing.txt`, and push.
- Name the checkpoint label on the ticket at launch (README rule 3).
- A reclaimed arm: `scripts/durable.sh restore DIR LABEL`, then `RESUME=1 WORKERS=4 runs/RBT-105/run_arm.sh SEED K`.
- Wave-1 launch lines:

```
WORKERS=4 runs/RBT-105/run_arm.sh 7 0      # positive control
WORKERS=4 runs/RBT-105/run_arm.sh 7 1      ; WORKERS=4 runs/RBT-105/run_arm.sh 7 2
WORKERS=4 runs/RBT-105/run_arm.sh 805 1    ; WORKERS=4 runs/RBT-105/run_arm.sh 805 2
WORKERS=4 runs/RBT-105/run_arm.sh 4 1      ; WORKERS=4 runs/RBT-105/run_arm.sh 4 2
WORKERS=4 runs/RBT-105/run_arm.sh 807 1    ; WORKERS=4 runs/RBT-105/run_arm.sh 807 2
```

Once all arms are in: `python runs/RBT-105/readout.py > runs/RBT-105/readout.txt`.

## Files

- `PREREGISTRATION.md`: this document.
- `run_arm.sh`: the launcher.
- `post_run.py`: the per-arm tables and the pairing check.
- `readout.py`: the rule.
- `founders.py`, `founders-rbt90.txt`: the founder fingerprints.
- `throwaway.sh`, `throwaway_check.py`, `throwaway.txt`: the 20-season check of the flag.
- `smoke.sh`, `smoke.txt`: the rule's smoke test.
- Code: `rabbitstew/ecology.py`, `rabbitstew/cli.py`, `tests/test_ecology_switches.py`.
