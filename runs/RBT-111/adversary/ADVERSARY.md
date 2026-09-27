# RBT-111 design adversary

This report attacks the RBT-111 design, PR #257 (`results/RBT-111-design`, head `2fc6a87`), before any arm. I am a fresh session: I did not design RBT-111 or run RBT-108. **No arm was run.** Everything here is either a code read or a computation on synthetic numbers.

## Verdict

**Two MUST-FIXes, both before any arm. The design is otherwise faithful and its power figures re-derive.**

1. **F1: `drive.sh` stalls every session after slot 2.**
   - After each slot, drive.sh calls the full readout on that slot's seeds.
   - From slot 2 on, one seed has all three arms, so the readout reaches c0's interval inversion with n = 1.
   - At n = 1 that loop never ends. At n ≤ 5 no shift can reach p ≤ 0.05.
   - The output goes to `/dev/null`, so the session hangs silently. Slots 3–6, 32 of the 48 arms, never launch.
2. **F2: my ruling on c0.** Switch c0 to the **within-seed permutation test, enumerated exactly**.
   - c0 depends only on which run carries the s0 label, so the 6¹⁶ labellings collapse to 3¹⁶ = 43,046,721 equally likely values of c0's sum.
   - Meet in the middle enumerates them exactly in pure Python, in well under 0.1 s per p. **No Monte Carlo is needed.**
   - **Validity:** it is exact under key exchangeability whatever the noise.
   - **Power:** it is **more** powerful than the registered sign-flip test on c0 in every salt-0 cell. At δ = 0.082, Holm power is **0.972 / 0.829 / 0.887**, against 0.955 / 0.785 / 0.807.
   - **Why the sign-flip test fails:** under the tail model, its size excess lands in c0 > 0, the direction RBT-108 suggested.

## Files by role

| role | path | how it was run |
|---|---|---|
| the exact within-seed permutation test for c0: p, interval, checks against 6ⁿ brute force and a 10⁵-draw Monte Carlo | `perm.py` → `perm.txt` | `python runs/RBT-111/adversary/perm.py`: pure Python, about 1 s |
| power and size, registered test (SF) against the permutation alternative (PERM), 16 seeds, three registered noise models plus one stress model | `power_adv.py` → `power_adv.txt` | `python runs/RBT-111/adversary/power_adv.py 10000 16`, numpy only, `default_rng(20260927)`, about 9 min |
| readout.py's sign-flip p, Holm and interval inversion against my own implementations | `checks.py` → `checks.txt` | `python runs/RBT-111/adversary/checks.py`, about 20 s |
| readout.py end to end on synthetic summaries (three readings, the qualifier, NOT A RESULT twice, drive.sh's per-slot call) | `synthetic.py` → `synthetic.txt` | `python runs/RBT-111/adversary/synthetic.py SCRATCH`, about 2 min, 2 of which are the hang's timeout |

**How to run them.**
- `perm.py` and `power_adv.py` import nothing from `runs/RBT-111/`. `power_adv.py` shares no code with the designer's `power.py`: its enumeration is meet in the middle, not the 2¹⁶ sign matrix, and its generator seed differs.
- `checks.py` and `synthetic.py` load the design's `runs/RBT-111/readout.py`, so they run on PR #257's tree.
  - I ran them there, with this directory copied in.
  - This branch is cut from `claude/new-session-4cao7d`, which does not yet hold `runs/RBT-111/readout.py`. They run once #257 merges.
- Environment: a clean `pip install -e '.[dev]'` venv (Python 3.11.15, numpy 2.4.6, MuJoCo 3.14.0, no scipy), x86_64.
  - On #257's head the full suite gives **335 passed**.
  - On this branch it gives **325 passed**, the integration branch's count, since this branch adds no test.

## Findings

| # | severity | one line |
|---|---|---|
| F1 | **MUST-FIX** | drive.sh's per-slot `readout.py --write-summaries --seeds A,B` never returns once one seed is complete (slot 2), because `sign_flip_ci` cannot end for n ≤ 5. Every session stalls silently after 2 of 6 slots. |
| F2 | **MUST-FIX** (the ruling asked for) | Replace c0's sign-flip test with the exact within-seed permutation test over 3¹⁶ labellings. It is exact under exchangeability, and more powerful in every salt-0 cell. Under the one-sided tail, the sign-flip test's excess size lies in c0 > 0, RBT-108's direction. |
| F3 | NONE | Faithful to the ticket and to the 00:50 amendment: seeds, salts, contrasts, test, Holm, the reading table, "NOT DECIDED at δ = 0.05", the gen-0 secondary and the completion rule are all there. |
| F4 | NONE | The runner's evolve arguments are character-identical to rbt96_run.sh's, and salt 2 moves the holistic stream alone. Key (0, 2) collides with nothing: 3,900 distinct states. |
| F5 | NONE | Slot pairing cannot create an offset. Runs are deterministic at a fixed `--workers 2`, and no salt is systematically placed. The pairing check re-tests determinism on the data. |
| F6 | CAVEAT | Durability. The docs say the checkpoint label is `rbt-111-SEED-ARM`, but the code uses `rbt-111-ARM-SEED`. The platform file is overwritten on every re-run. There are no restore instructions. |
| F7 | CAVEAT | When NOT A RESULT, the readout still prints a bare `3. READING: …` line. It should carry the prefix itself. |
| F8 | CAVEAT | The gen-0 secondary has no stated consequence if it rejects. Fix it now. |
| F9 | CAVEAT | A salt-1-only (or salt-2-only) excess that c12 misses reads "salt 0's offset". The probability is 0.02–0.07 at δ = 0.082 and up to 0.12 at δ = 0.05 (SF). PERM lowers it. State it in the pre-registration. |
| F10 | NONE | Power re-derives. My independent code and generator seed agree with every cell of `power.txt` to within 2 Monte Carlo SE of the difference. |
| F11 | NONE | readout.py's sign-flip enumeration, Holm and interval inversion are correct, except for termination (F1). |

### F1. drive.sh stalls every session after slot 2 (MUST-FIX)

**What drive.sh runs.** After each slot, `drive.sh` runs `python runs/RBT-111/readout.py --write-summaries --seeds "$SEEDS_IN_SLOT" > /dev/null`. That writes the summaries and then runs the **whole** readout on the slot's seeds.

**Where it hangs.**
- **Slot 1** (s0-A, s1-A) has no complete seed, so `main` returns before any statistics.
- **Slot 2** (s2-A, s0-B) completes seed A, so `full = [A]` and the readout reaches `sign_flip_ci(c0)` with one value.
- With one value, both sign assignments reach |sum|, so p = 1 at every μ. The `while … > alpha` loop never exits.
- More generally, the smallest attainable sign-flip p is 2/2ⁿ, so the walk can end only at n ≥ 6.
- Each slot holds at most two seeds, so **every per-slot call from slot 2 on hangs**.

**Reproduced.**
- `synthetic.txt`, last block: a slot-2-shaped root with s0/s1/s2-217 and s0-218 present, running `readout.py --from-summaries --seeds 217,218`, is **still running after 120 s**, pinned at 100% CPU, and is killed.
- Before writing the scripts I saw the same on a 60 s `timeout`.
- `drive.sh` never checks the call, and its stdout goes to `/dev/null`.

**Consequence.** Each session runs slots 1–2, then hangs forever. It never launches slots 3–6, and it never prints "all done". That is 32 of 48 arms, and the hours are lost until someone notices.

**Fix: all three parts.**
1. **Write summaries without reading.** Give `readout.py` a `--summaries-only` flag that writes and exits, or have drive.sh call `r85.write_summary` and `r96.write_extras` directly. drive.sh uses that flag.
2. **Guard the interval.** If even the most extreme assignment has p > α, return (−∞, +∞) without walking:
   - sign-flip: 2/2ⁿ > α, which is n ≤ 5;
   - permutation (F2): 1/3ⁿ > α, which is n ≤ 2.

   `perm.py` implements and tests the permutation guard.
3. **Test it.** Run drive.sh's exact per-slot command on a slot-2-shaped root under a `timeout`, and assert that it returns.

### F2. The ruling on c0: switch to the exact within-seed permutation test (MUST-FIX, before any arm)

**The problem.**
- c0 = (y₁ + y₂)/2 − y₀. The sign-flip test assumes c0 is symmetric about 0 under H0.
- Key exchangeability gives c0 mean 0, but not symmetry. The noise is one-sided (discoveries are gains): a discovery in s0 moves c0 by −0.25, and one in s1 or s2 by +0.125.
- c12 = y₂ − y₁ **is** symmetric under exchangeability, so its sign-flip test is exact and stays.

**The alternative, and why it is cheap.**
- Under H0 the three runs of a seed are exchangeable, so all 3! labellings per seed are equally likely.
- c0 is unchanged by swapping s1 and s2. So it takes only **3 values per seed**, one per choice of the run labelled s0, and those three values sum to 0.
- The 6ⁿ labellings therefore give 3ⁿ equally likely values of sum(c0), each counted 2ⁿ times. At n = 16 that is **3¹⁶ = 43,046,721**.
- **Meet in the middle** splits the seeds into two halves of 3⁸ = 6,561 partial sums, sorts one half, and uses two bisects per element of the other. That is exact, pure Python, and well under 0.1 s per p.
- **Monte Carlo is unnecessary.** The coordinator's "6¹⁶ too large, so 10⁵ draws" does not arise.

**`perm.py` checks** (`perm.txt`):
- At n = 1–5, on 15 random datasets with a one-sided tail, the meet-in-the-middle p equals the 6ⁿ brute-force definition to 1e-12.
- At n = 16, the exact p is 0.003495 (150,463/3¹⁶). A 10⁵-draw Monte Carlo gives 0.003540, 0.24 SE away. So a Monte Carlo version would carry a relative error of about 5% at p ≈ 0.0035. The exact count carries none.
- On data shifted by +0.040, the inverted 95% interval for the salt-0 shift is [+0.019, +0.085].
- The interval returns (−∞, ∞) at n ≤ 2, the only sizes where no labelling can reach p ≤ 0.05. It is finite from n = 3.

**Size and power** (`power_adv.txt`). 10,000 trials per cell at 16 seeds, and MC SE ≤ 0.005 (0.0022 at 0.05).
- **SF** is the registered test (sign-flip on c0 and c12, Holm, then the table).
- **PERM** tests c0 by permutation and c12 by sign-flip, then Holm and the table.
- **T8\*** is a stress model: normal 0.030 plus +0.30 with probability 1/8. **It is not registered.**

*Under the null:*

| model | SF raw c0 (c0 > 0 / c0 < 0) | PERM raw c0 (> 0 / < 0) | SF Holm c0 | PERM Holm c0 | P(reading = salt 0), SF / PERM |
|---|---|---|---|---|---|
| N62 | 0.049 (0.022 / 0.027) | 0.048 (0.023 / 0.025) | 0.026 | 0.024 | 0.023 / 0.022 |
| N81 | 0.048 (0.024 / 0.024) | 0.049 (0.026 / 0.023) | 0.026 | 0.023 | 0.024 / 0.022 |
| **T** | **0.060 (0.045 / 0.015)** | 0.053 (0.020 / 0.034) | **0.032** | 0.026 | **0.030** / 0.024 |
| T8\* | **0.063 (0.051 / 0.011)** | 0.049 (0.016 / 0.033) | 0.034 | 0.027 | 0.031 / 0.025 |

*Under a salt-0 deficit:*

| scenario | model | SF Holm power, c0 | **PERM Holm power, c0** | P(reading = salt 0), SF / PERM |
|---|---|---|---|---|
| δ = 0.082 | N62 | 0.955 | **0.972** | 0.908 / 0.924 |
| | N81 | 0.785 | **0.829** | 0.741 / 0.783 |
| | T | 0.807 | **0.887** | 0.768 / 0.844 |
| | T8\* | 0.552 | **0.627** | 0.524 / 0.596 |
| δ = 0.05 | N62 | 0.570 | **0.615** | 0.540 / 0.583 |
| | N81 | 0.343 | **0.378** | 0.322 / 0.355 |
| | T | 0.500 | **0.537** | 0.473 / 0.506 |
| | T8\* | 0.281 | 0.281 | 0.264 / 0.264 |

*Under a salt-1 excess (the "keys" power, c12 Holm):* SF 0.902 / 0.679 / 0.793 and PERM 0.898 / 0.673 / 0.782 at δ = 0.082. At δ = 0.05 they are 0.459 / 0.277 / 0.430 and 0.457 / 0.276 / 0.421. PERM's ≤ 0.011 loss arises because its c0 rejects less often under a salt-1 excess, so Holm tests c12 at 0.05 less often.

**What the tables show.**
- **SF's size excess sits in the hypothesised tail.** Under T, SF rejects c0 > 0 at **0.045** against a nominal 0.025. That is about 10 MC SE high, 1.8× nominal, and exactly the direction in which RBT-108's offset would "replicate". The c0 < 0 tail is under-sized (0.015), so the two-sided total, 0.060, looks almost innocent.
  - The designer's "0.057 unadjusted, 0.031 in Holm" is correct (I get 0.060 and 0.032), but it hides this.
  - SF's false "salt 0" reading under the null is 0.030 under T and 0.031 under T8\*, against PERM's 0.024 and 0.025.
- **PERM is exact overall.** Its two-sided size is 0.048–0.053, within 1.4 SE of 0.05 in every model. Its tails are not individually 0.025 each, but the test is two-sided, and the reading's false-positive rate sits at nominal.
- **PERM is also more powerful for the question asked.** It gains +0.02 to +0.08 of Holm power on c0 in every salt-0 cell except T8\* at δ = 0.05, which ties. The permutation distribution uses all three runs' spread, not only c0's.
- **Under a salt-1 excess,** PERM also misreads less often as "salt 0" (F9).
- **The ruling:** switch. Validity is exact where the sign-flip test is not, power is higher, and the cost is about 60 lines of pure Python. It must be fixed **before any arm**, because swapping tests after seeing data is exactly the two-ways reading this pre-registration exists to prevent.

**What changes in `readout.py`:**
1. **Add `perm_c0_p(rows)`**, where rows are (y_s0, y_s1, y_s2) per seed. It returns (p, count, 3ⁿ) by meet in the middle, with the same 1e-12 tie tolerance as `sign_flip_p`. `perm.py` has a reference implementation to port.
2. **Primary:** c0's p is `perm_c0_p`. c12's p stays `sign_flip_p`. Holm is over those two.
   - The table's c0 row prints "exact permutation p (count/43046721)".
   - Mean, median, 20%-trimmed mean and count positive are unchanged.
3. **Secondary (gen 0):** the same change, with c0 gen0 by `perm_c0_p` on the gen-0 rows.
4. **Interval and qualifier:** invert the permutation test for a salt-0 shift μ. The interval holds each μ for which `perm_c0_p` on (y_s0 + μ, y_s1, y_s2) exceeds 0.05. Walk in 0.001 steps, with the guard 1/3ⁿ > α (F1).
   - `perm_c0_ci` in `perm.py` is the reference.
   - The chance-row qualifier reads this interval. `sign_flip_ci` is no longer used for c0; if it is kept anywhere, give it F1's guard.
5. **The `READING["chance"]` string:** the power at δ = 0.05 becomes "0.38–0.62 at 16 seeds", from the PERM c0 Holm column for N81 / N62, with T at 0.54.
6. **`--summaries-only`** (F1), and the NOT A RESULT prefix (F7).

**What changes in `PREREGISTRATION.md`:**
- **§3:** c0 is tested by the exact within-seed permutation test over the 3¹⁶ labellings of the s0 label, which is exact under key exchangeability. c12 is tested by the exact sign-flip test. Holm is over the two.
- **§4:** the qualifier's interval inverts the permutation test, and the δ = 0.05 power figure is updated.
- **§5:** the secondary uses the same tests.
- **§6:** re-run `power.py` with a PERM column. Its vectorised permutation p must be asserted equal to `readout.perm_c0_p`, as the designer already does for the sign-flip. The registered power becomes the PERM figures, which agree with mine within MC error.
- **§6's validity note** becomes "resolved: c0 uses the permutation test", with the tail-split size table above.
- **§1 and drive.sh's header:** fix the label (F6).
- **§4:** add F9's sentence.
- **§5:** add F8's consequence sentence.

**What the tests must check:**
1. At n ≤ 5, `perm_c0_p` equals the brute-force 6ⁿ definition to 1e-12, on data with a one-sided tail.
2. Its count at n = 16 on a fixed dataset is pinned. `perm.txt` §2 gives one such dataset and its count.
3. **Invariance:** p is unchanged by swapping y_s1 and y_s2 within any seed, by adding a constant to all three runs of any seed, and by reordering the seeds.
4. `perm_c0_ci` returns (−∞, ∞) at n ≤ 2 and terminates at every n.
5. **End to end:** the c0 row's denominator is 3¹⁶. The three synthetic readings still come out as specified.
6. **F1:** drive.sh's per-slot call returns on a slot-2-shaped root under a `timeout`. In `synthetic.py` the registered code fails this test.
7. **F7:** in the NOT A RESULT case, the reading line itself contains "NOT A RESULT".

### F3. Faithfulness to the ticket (NONE)

| ticket item | in the design | where |
|---|---|---|
| 16 seeds, 217–232 (the 00:50 amendment) | yes | `readout.SEEDS`; `waves.txt` (4 × 4 seeds, test-pinned); PREREGISTRATION §1 |
| salts 0, 1, 2 on RBT-96's configuration exactly | yes | `rbt111_run.sh`, F4 |
| c0 = (s1 + s2)/2 − s0 and c12 = s2 − s1 on `final_fifth` | yes | `readout.main`, recomputed from injected constants to 1e-9 in `synthetic.txt` |
| exact sign-flip test, two-sided, Holm at 0.05 | yes (F2 changes c0's test) | `sign_flip_p` and `holm`, F11 |
| mean, median, 20%-trimmed mean, count positive, exact p | yes | `describe` |
| the reading table, including "any \| ≠ 0 → keys" taking precedence | yes | `reading()`; `synthetic.txt` gives salt0 / keys / chance as intended |
| "a null at δ = 0.05 is NOT DECIDED" | yes, in the pre-registration and in the printed chance reading | `READING["chance"]` |
| the chance-row qualifier (the interval still contains 0.082) | yes; fires as specified | `synthetic.txt`, 4th case |
| gen-0 secondary, separate Holm | yes (F8 adds its consequence) | readout §5 |
| completion rule: NOT A RESULT | yes, for a missing arm and for an arm truncated before generation 249 | `synthetic.txt` (F7 on its wording) |

Two textual slips, fixed with F2's edits:
- The pre-registration says the power at δ = 0.05 is "0.35–0.57". Its own table gives 0.347–0.572, and under PERM it becomes 0.38–0.62.
- The coordinator quoted "0.96 / 0.80 / 0.82". The table's middle figure is 0.792.

### F4. The runner and the keys (NONE)

- **The evolve arguments are identical.** The whole `rabbitstew evolve --generations … --out "$OUT"` block of `rbt111_run.sh` is character-identical to `rbt96_run.sh`'s, by `diff`. That is independent of the test's regex.
- **The only other differences** are `OUT=runs/RBT-111/…` and the `s2) SALT=2` case.
- **Nothing of RBT-96's is touched.** `scripts/rbt96_run.sh`, `runs/RBT-96/` and `rabbitstew/` are unchanged against integration (`git diff --quiet`).
- **Salt 2 moves the holistic stream alone.**
  - `spawn_streams` (`rabbitstew/evolution.py:539`) replaces only `children[STREAMS.index(HOLISTIC)]`, with `SeedSequence(seed, spawn_key=(0, 2))`. The conventional (1,) and terrain (2,) children are untouched.
  - The design's test checks the first 8 draws of each stream at salts 0, 1 and 2.
  - The readout's pairing check re-checks this on the data, through the conventional lineage hashes and the terrain and start rows.
- **Key (0, 2) collides with nothing.**
  - **Keys in use:** unsalted (0,), (1,), (2,); salts (0, 1), (0, 2); RBT-105's `breed_seed_sequence` (0, 0, K), which is three long by design.
  - **Nothing spawns from a stream.** There is no `.spawn(` or `seed_seq` outside `spawn_streams`, so no grandchild (0, 2) of (0,) can arise.
  - **Checked directly:** over seeds 1–300 and 217–232, crossed with those 13 keys (K = 1…8), all **3,900** `generate_state(8)` vectors are distinct.
  - **Terrain and s2 cannot alias.** SeedSequence appends the key after the pool-padded entropy, so (2,) and (0, 2) assemble different word sequences.

### F5. Slot pairing and load (NONE)

**The slot pattern.** drive.sh pairs arms in the order s0-A s1-A | s2-A s0-B | s1-B s2-B, repeated for two seed pairs per session.
- s1 always shares its slot with a sibling of its own seed.
- s0 and s2 each share with a sibling for half the seeds, and with a cross-seed partner for the other half.
- The position is not aligned with c0's contrast (s0 against the mean of s1 and s2) or with c12's.

**Why position cannot matter.**
- An offset from position needs the outcome to depend on the schedule. It does not: every arm runs at `--workers 2`.
- The RBT-108 adversary's F4 found no wall-clock read outside log lines. I re-checked this: `time` is used only for the "took N s" log lines, in `evolution.py` and `ecology.py`.
- Resume restores the generator states.
- RBT-108's s0 and s1 also ran concurrently, and their conventional lineage digests matched exactly across 16 seeds.

**The data re-test it.** Here the pairing check compares the conventional hash and the terrain and start rows across **three** arms that ran in different slot positions and with different partners. Any schedule dependence would fail it. So load symmetry is not needed for validity.

### F6. Durability and the platform file (CAVEAT)

- **The label is documented wrong.**
  - `PREREGISTRATION.md` §1 and drive.sh's header say snapshots are labelled `rbt-111-SEED-ARM`. The code uses `rbt-111-$AS`, which is `rbt-111-ARM-SEED`, as in `rbt-111-s0-217`.
  - A runner restoring from the documented label finds no branch. It would re-run the arm from generation 0: deterministic, so the same result, but hours lost. Or it would report the arm as lost.
  - **Fix:** make the docs say `rbt-111-ARM-SEED`, or change the code to `rbt-111-$SEED-$ARM` to match RBT-96's convention. Either way, pin the choice in a test.
- **The platform file is overwritten.** `drive.sh` writes `platform-A-D.txt` with `>` on every invocation. A session resumed on a different machine overwrites the record of where slots 1–k ran. **Fix:** append with `>>`, with a UTC timestamp and the slot number.
  - The registration assumes one platform. MuJoCo's floating point can differ across CPU instruction sets, so a mid-arm platform change must be recorded, not hidden.
- **No restore procedure is written.** `waves.txt` should give the restore line, as RBT-96's runners used: `scripts/durable.sh restore runs/RBT-111/ARM-SEED rbt-111-ARM-SEED` for each unfinished arm, then re-run the same `drive.sh A B C D`. drive.sh skips arms with `analysis.json` and resumes those with `state.json`, which I read and found correct.

### F7. NOT A RESULT should be on the reading line (CAVEAT)

With an arm missing or truncated, the readout prints "NOT A RESULT: …" near the top and then a normal `3. READING: CHANCE …` line, followed by `(NOT A RESULT: see above)` on the next line (`synthetic.txt`). A quoted reading line would carry no qualifier. **Fix:** when incomplete, print `3. READING (NOT A RESULT, n = k of 16): …`, and have the test assert on that line.

### F8. What a gen-0 rejection means (CAVEAT)

The secondary is registered, but the pre-registration gives no consequence for a rejection.
- A rejection at generation 0 would mean the founders differ by salt: a stream-quality or draw-level effect. That contradicts the RBT-108 adversary's 300-seed founder check.
- **Fix, stated now:**
  - A gen-0 rejection does not change the primary reading.
  - It is reported as "founders differ by salt", and it opens a code-path search at the draw level.
  - If the primary reads "chance" while gen 0 rejects, the reading is qualified: the founders differ by salt, but the final fifth does not.
- The gen-0 c0 uses the permutation test (F2), for the same reason as the primary.

### F9. "Salt 0's offset" can be a missed salt-1 excess (CAVEAT)

- A salt-1-only excess δ gives c0 = δ/2 > 0, the same sign as a salt-0 deficit, and c12 = −δ.
- If c12 misses it and c0 is rejected, the table reads "salt 0's offset".
- **The misread rates** (`power_adv.txt`, P(reading = salt0) under salt1):

  | δ | SF | PERM |
  |---|---|---|
  | 0.082 | 0.027 / 0.056 / 0.074 | 0.022 / 0.049 / 0.061 |
  | 0.05 | 0.069 / 0.059 / **0.116** | 0.062 / 0.054 / 0.067 |

- **Fix:** add one sentence to §4 giving these figures, and print s1 − s0 and s2 − s0 (already descriptive) beside a "salt 0" reading.
  - A salt-0 offset predicts both have the same sign and a similar size.
  - This stays descriptive. Adding it to the rule now would change the test's size.

### F10. Power re-derived (NONE)

**The setup.** My own code (`power_adv.py`) uses:
- the same three models and scenarios, 16 seeds and 10,000 trials;
- a different generator seed, with fresh draws per cell;
- a different enumeration.

SF columns, designer's → mine:

| cell | c0 Holm (or c12 → keys) N62 | N81 | T |
|---|---|---|---|
| null, c0 size | 0.025 → 0.026 | 0.025 → 0.026 | 0.031 → 0.032 |
| null, c12 size | 0.026 → 0.025 | 0.026 → 0.025 | 0.024 → 0.027 |
| null, raw c0 | 0.050 → 0.049 | 0.050 → 0.048 | 0.057 → 0.060 |
| salt 0, δ 0.082 | 0.959 → 0.955 | 0.792 → 0.785 | 0.817 → 0.807 |
| salt 0, δ 0.05 | 0.572 → 0.570 | 0.347 → 0.343 | 0.491 → 0.500 |
| salt 1, δ 0.082 → keys | 0.903 → 0.902 | 0.671 → 0.679 | 0.787 → 0.793 |
| salt 1, δ 0.05 → keys | 0.454 → 0.459 | 0.270 → 0.277 | 0.431 → 0.430 |

- **Agreement.** Every difference is within 2 SE of a difference between two independent 10,000-trial estimates, which is about 0.006 at these shares. The largest is 0.010, for salt 0 at δ 0.082 under T, about 1.8 SE.
- **The null sizes re-derive.** They are 0.024–0.027 inside Holm for the normal models, and 0.032 for c0 under T. F2 explains where that 0.032 comes from.
- **Not re-derived:** the 12-seed comparison table (`power-12.txt`). It is not the registered design.

### F11. readout.py's statistics (NONE, apart from F1)

From `checks.txt`:
- **`sign_flip_p`** matches an independent meet-in-the-middle enumeration exactly (max |diff| 0) on 200 random 16-seed sets with a tail. The design's own test pins RBT-108's 10/4096.
- **`holm`** makes 0 disagreements with the textbook step-down over 20,000 random p pairs. That covers the adjusted p, which is 2·p₍₁₎ and then max(2·p₍₁₎, p₍₂₎), and the rejections, which need p₍₁₎ ≤ 0.025 and then p₍₂₎ ≤ 0.05.
- **`sign_flip_ci`** passes on 30 random sets. At each end p > 0.05, and one grid step beyond each end p ≤ 0.05. No μ out to 0.1 beyond either end is accepted, which checks monotonicity on the grid. Its only defect is termination at n ≤ 5 (F1).
- **End to end** (`synthetic.txt`):

  | case | c0 p / Holm | c12 p / Holm | reading |
  |---|---|---|---|
  | s0 −0.082 | 0.0022 / 0.0044, rejected | 0.63 | **salt 0** |
  | s2 +0.12 | — | 0.0009, rejected | **keys** (c0 also rejected) |
  | no offset | 0.24 | 0.20 | **chance** |

  - A chance case whose interval is [−0.048, +0.116] prints the qualifier, "RBT-108's offset NOT excluded".
  - A missing arm and a truncated arm each print NOT A RESULT.
  - On each case the permutation p is printed beside the sign-flip p. For example, in the salt-0 case PERM gives 0.00024 where SF gives 0.0022.

## What survives

- The design is the ticket's T3 at the amended 16 seeds, 217–232. The runner, the keys, the contrasts, Holm, the reading table, "NOT DECIDED at δ = 0.05", the gen-0 secondary and the completion rule are all as filed (F3, F4).
- The power figures re-derive independently (F10), and the slot pairing cannot bias the contrast (F5).
- **Before any arm:**
  1. **F1** (drive.sh would stall every session after slot 2);
  2. **F2**, c0 by the exact 3¹⁶ within-seed permutation test, with the listed readout, pre-registration and test changes. Both its size and its power are better than the registered test's.
  3. **F6–F9** are one-line edits, and should ride the same amendment.

---
_Generated by [Claude Code](https://claude.ai/code)_
