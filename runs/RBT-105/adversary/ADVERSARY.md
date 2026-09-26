# RBT-105 design adversary: findings on PR #150

Written by the RBT-105 design adversary (session_01Js5wfxCDBhvC9uvN6reHj3), 2026-09-26, **before any arm**. It measures and does not tune. No designer file is edited. Every number below comes from a file in this directory.

| # | finding | status |
|---|---|---|
| F1 | `--breed-stream K` isolates post-founder history; K = 0 is byte-identical; tests pass. **Its spawn key collides with PR #146's salt.** | **partly holds** (fix the key before any arm) |
| F2 | Can noise in `distinct` alone manufacture HISTORY? No. The real asymmetry is inferential, and a sharper quantity exists. | concern **fails**; rule **weak** |
| F3 | Matched-null power, both directions, and the FOUNDING wording | **partly holds** |
| F4 | The replicates as a free ecology A/A, report-only | **yes**: `aa_spread.py` |
| F5 | Packing | **pair two arms per session** |

## F1. The flag: partly holds

**(a) Only post-founder holistic draws change. Holds.**
- In `Ecology.__init__`, the holistic founders and their ages are drawn first, then the designed-body founders and ages from their own stream, then the switch. No holistic draw falls between the founders and the switch.
- After the switch, every holistic draw uses `self.rngs[HOLISTIC]`:
  - groupings (`rng.permutation`, `ecology.py:305`);
  - the breeder shuffle, crossover and mate choice (`:511`);
  - mutation (`_breed`, `:577`);
  - a cull (`:454`).
- No founder property is drawn lazily after the switch.
- Season-0 groupings count as history, as the designer says.
- **Caveat on "the worlds are untouched":**
  - At this baseline's `regrow_delay 0` the food layout comes from `start_seed`, the terrain stream, so the claim holds here.
  - Under persistent food (`regrow_delay > 0`), `_arena_bank` (`:252`) draws the holistic arenas' food seeds from the holistic stream. K would then change the holistic fauna's worlds too.
  - The help text and docstring should say "at `regrow_delay 0`". This does not affect RBT-105.

**(b) K = 0 is byte-identical, and K ≥ 1 isolates the history. Reproduced on a second seed.** File: `repro805.txt`, **ALL PASS**.
- Setup: seed 805, 8 seasons, `WORKERS=2`, through `run_arm.sh` and `throwaway_check.py` unmodified, against `ckpt/rbt-90-805`. The designer's throwaway used seed 7, 20 seasons, one worker.
- Founder genome files, including ages: byte-identical.
- K = 0 reproduces `lineage.jsonl` (959 lines) and `cohorts.jsonl` (16 lines) byte for byte.
- K = 1 diverges at season 0.
- The designed-body lines and the worlds are byte-identical.
- K = 1 at `WORKERS=4` against `WORKERS=2`: `lineage.jsonl` is identical over the 8 seasons (`packing.txt`).

**(c) Tests pass.** File: `tests.txt`.

| tree | result |
|---|---|
| PR head | 287 passed |
| trial merge into `claude/new-session-4cao7d` | 287 passed |
| trial merge with PR #146 as well (auto-merged, no textual conflict) | 289 passed |

**(d) PR #146 conflicts semantically, not textually. This must be fixed before any arm.** Files: `probe_streams.py`, `probe_streams.txt`.
- `--breed-stream K` seeds `SeedSequence(seed, spawn_key=(0, K))`. RBT-96's `--holistic-stream-salt S` seeds `SeedSequence(seed, spawn_key=(0, S))`. When K = S they are **the same generator**: the first 1000 draws are identical for seeds 7 and 805 at K = S = 1 and at K = S = 2.
- On the trial merge with both flags set (salt 1, breed 1), the history generator is the salted founders' generator **rewound to draw 0**. The history re-uses the bits that drew the founders.
- The salt then no longer moves the history: salt 2 with breed 1 gives the same history stream as salt 1 with breed 1.
- RBT-105's own arms set no salt, and RBT-96's salt runs are arena runs, so **no planned result is wrong today**.
- But the docstring's claim that the stream is "independent of … every other stream" is false across the programme. The founder-sharing ecology A/A that RBT-96 proposes would reuse RBT-105's history bits as its founders.
- **Fix, before wave 1, because afterwards it would orphan the arms:**
  - Key the replicate one level down, e.g. `spawn_key = (*founder_key, 0, K)`. Unsalted, that is `(0, 0, K)`; with salt S it is `(0, S, 0, K)`. A salt key always has length 2, so neither can equal one.
  - Alternatively, refuse the two flags together.
  - Either way, re-run the throwaway's K ≥ 1 legs, about 20 min.
  - K = 0 is unaffected.

## F2. The rule's asymmetry: the noise concern fails, but the rule is weak

**Noise in `distinct` cannot manufacture a flip from the discarded side.** Files: `probe_distinct.py`, `probe_distinct.txt`.
- The probe re-scores all ten RBT-90 arms with RBT-84's own definition over seven windows. The `all` column reproduces the committed counts 10/10.
- Seeds 805 and 7, at the bar, stay at ≤ 2 in **every** window: `to580`, `to500`, `early`, `late`, `odd`, `even`. Their counts range from 0 to 2.
- No discarded arm exceeds 2 in any window. Their oscillator-carrying bests are season 70 only (805) and seasons 10 and 70 only (7).
- **The fragile side is the acquired one.** Seed 4 (9) drops to 4–5 in the `early`, `late` and `even` half-windows, and seed 807 (10) drops to 5–7 in four of them.
- So noise in the count pushes acquired replicates into 3–7 (UNCLEAR). It **suppresses FOUNDING POPULATION and cannot create HISTORY**.
- In the simulation, with the fate fixed by the founders (icc = 1, two-state model), P(HISTORY) is **0.021** at wave 1 (`power.txt`).

**The real asymmetry is what HISTORY means.**
- HISTORY answers "is the flip probability q > 0?", which is true unless the founders fix the fate completely.
- In `power.txt` (two-state model, wave 1), P(HISTORY) is:

| icc (founders' share of the latent variance) | P(HISTORY) |
|---|---|
| 0.5 | 0.83 |
| 0.7 | 0.62 |
| 0.9 | 0.26 |

- So HISTORY is the likely verdict even when the founders explain most of the variation, and the readout would print "the same founders reach both fates" without saying how much the founders shift the fate.

**A sharper quantity is in the data.**
- Per 150-season block, the birth-level rate of a linked oscillator (`probe_distinct.txt`, right-hand columns) separates the fates far more cleanly than `distinct`.
- In each 150-season block of seasons 300–599, the five discarded arms are ≤ 0.023 and the five acquired arms are ≥ 0.213: **a 9× gap, with none between**.
- It also shows what "discarded" means. Seeds 7 and 805 carried oscillators at birth at **0.157** and **0.183** in seasons 0–149, as high as seed 4 (0.069) or 807 (0.372), and then lost them. Discarding is a loss after early carriage, which is itself history-shaped.

**Proposal, pre-registered beside the existing rule, not replacing it.** Keep R0's question ("is the fate fixed by the founders?"), but word its answer as that question, and add two rules:
- **R1, the flip count.** F is the number of flips among the n decided replicates.
  - **FOUNDERS SHIFT THE FATE** if P(Bin(n, ½) ≤ F) ≤ 0.05. At n = 8 that is F ≤ 1 (p = 0.035); at n = 16, F ≤ 4 (p = 0.038).
  - **HISTORY SUBSTANTIAL** if P(Bin(n, 0.1) ≥ F) ≤ 0.05. At n = 8 that is F ≥ 3 (p = 0.038); at n = 16, F ≥ 5 (p = 0.017).
  - Otherwise, not decided.
  - The balanced 2 + 2 design makes the q = ½ null hold whatever the base rate of acquisition: a discarded seed flips at rate p, an acquired one at 1 − p, and the average is ½.
- **R2, a replicate-only continuous test (the ICC-like statistic).**
  - T = mean y of the replicates of originally acquired seeds, minus mean y of the replicates of originally discarded seeds.
  - y is log(distinct + 0.5), or better, log of the late-season (300–599) oscillator birth rate.
  - The p-value is an exact permutation over the replicate run labels.
  - **The originals must be left out.** They were selected on outcome, and a naive one-way ANOVA F on original + replicates is anti-conservative: 0.077 and 0.063 false-positive rates against a nominal 0.05.

Power, in `power.txt` (two-state model; the lognormal model is beside it and agrees in direction). Each cell is P(the test fires):

| icc | R1 SHIFT, m = 8 | R2, m = 8 | R1 SHIFT, m = 16 | R2, m = 16 |
|---|---|---|---|---|
| 0 (matched null) | 0.020 | 0.028 | 0.033 | 0.054 |
| 0.5 | 0.31 | 0.28 | 0.55 | 0.59 |
| 0.7 | 0.54 | 0.51 | 0.84 | 0.85 |
| 0.9 | 0.83 | 0.81 | 0.98 | 0.985 |

- At 4 seeds × 2 replicates, R1 and R2 detect only a strong founder effect (icc ≳ 0.8).
- At 8 seeds × 2 replicates they detect icc ≈ 0.7 with power 0.85.
- **Recommendation:** if the question is "how much", run wave 2 **unconditionally**, not only when wave 1 is not HISTORY. Under this model, wave 1 alone will usually say HISTORY and stop.
- An ICC with originals included, on 4 seeds × 3 runs, is not recommended, for the selection reason above.

## F3. Matched-null power: partly holds

- The designer's table is arithmetically right: 1 − (1 − q)^8 is 0.996, 0.942, 0.832 and 0.570.
- **It covers only one direction**, P(HISTORY | q), and treats every replicate as decided.
- The other direction is missing. Its matched null is "the fate is fixed by the founders", and the power of a FOUNDING POPULATION verdict under that null is **0.53 at wave 1 and 0.44 at waves 1 + 2** (two-state model).
  - With more seeds it gets *harder*, because more acquired replicates near 8 must all clear the bar.
  - The designer's 0.12 prediction implicitly allows for this, but the table does not show it.
- **The wording fails.**
  - `PREREGISTRATION.md` §2 promises that a FOUNDING verdict "will be worded with its m".
  - `readout.py` prints "the fate replicates on all N founding populations", with no m and no bound.
  - Suggested wording: "no flip in m decided replicates; under a common q this excludes q ≥ 1 − 0.05^(1/m) at 95%", which is **0.31 at m = 8 and 0.17 at m = 16**.
  - HISTORY should read: "the fate is not fixed by the founders (k of n); this does not say how much they shift it (R1/R2)".
- A missing replicate is counted "incomplete", and an EXTINCT one as undecided. Both are correct.

## F4. An ecology A/A for free: yes, report-only

- File: `aa_spread.py`, smoke-tested on fake replicates in `aa_spread_smoke.txt`. That smoke output is **not a result**: its "replicates" are other seeds.
- Proposed as `runs/RBT-105/aa_spread.py`, writing `runs/RBT-105/aa_spread.txt`. It reads committed `seasons.txt` only.
- It uses RBT-92's windows at each seed's committed onset T (`runs/RBT-92/onset.txt`): before [T−100, T), recovery [T+60, T+160) (RBT-92's primary window), and late [300, 600).
- It prints, per arm and window:
  - `x_h`: holistic `mean_lifetime_score`, the income RBT-92's R-body and R-shift read, set to 0 for a dead fauna as RBT-92 does;
  - `body`: holistic minus conventional `mean_lifetime_score` (R-body);
  - `alive_h`: holistic alive;
  - `deaths_h`: holistic deaths per 10 seasons.
- It then prints the RMS of (replicate − original) and RBT-96's half-width, 2.776·RMS/2.
- It **rules on nothing**.
- Conventional quantities are left out: they are identical across replicates by construction, so their spread is 0.
- **Caveat, printed with it:**
  - These replicates diverge from season 0, while a challenge arm shares its baseline up to T.
  - For the recovery window the spread is an **upper bound** on the challenge arms' own A/A, not an estimate of it.
  - A matched A/A for RBT-92/99/100/101 would switch the stream **at T**. That would be a later flag (`--breed-stream-at T`), not RBT-105's.

## F5. Cost and packing: pair two arms per session

File: `packing.txt`, measured on this container, seed 805, first 8 seasons.
- One arm at `WORKERS=4`: 5.5 s per season. That matches RBT-90's 5.8–6.8 s logs, about 1 h an arm.
- Two arms together at `WORKERS=2` each: 10.2 s per season apiece, which is **5.1 s per arm-season**.
- So pairing costs no throughput, and the worker count does not change a run (re-checked above).
- **Wave 1 then takes 5 sessions of about 1 h 45 min instead of 9 sessions of about 1 h:**
  - 4 pairs, plus the control alone or paired with one replicate;
  - `run_arm.sh` works unchanged, with two background tasks per session, each with its own `durable.sh` label.
- Pair across seeds, e.g. 7-b1 with 805-b1, so that one lost container never takes both replicates of the same founding population.

## Files

| file | what it holds |
|---|---|
| `probe_distinct.py`, `probe_distinct.txt` | F2: `distinct` over seven windows, and the birth rate per block, all ten RBT-90 arms (from `ckpt/rbt-90-*`) |
| `power.py`, `power.txt` | F2/F3: matched-null power of R0, R1, R2 and the naive ICC F, two models, m = 8 and 16 |
| `probe_streams.py`, `probe_streams.txt` | F1(d): the key collision with PR #146 |
| `repro805.txt` | F1(b): the throwaway check on seed 805 |
| `tests.txt` | F1(c) |
| `aa_spread.py`, `aa_spread_smoke.txt` | F4 |
| `packing.txt` | F5 |
