# RBT-132 fix-check of #476 (head `9c0c06c`): the #471 findings, as ruled

*2026-09-28, the design adversary. The ruling checked against is the coordinator's on #471 (comment 5870196335).*

**How I ran it.**
- #476 was trial-merged onto integration `5eda1db`, giving `6900fba`, a clean merge.
- All runs used a clean `.[dev]` venv.
- **No-peek:** from the calibration branches I read only the two `GATE` lines and `reachability.json`. I did not read
  per-host lines, F values or any call.

## Verdict: **FIX**

- The code implements every item as ruled, and W1 is byte-identical.
- The implementer's 45 mutants all die.
- **The fix is one small test.** It concerns S2's trigger: nothing checks that a 64-draw pick calls the second stage.
  Two lesser survivors come with it.

**For the calibration failure,** the pool machinery **can** carry a larger pool or a screen-until-N rule without being
re-architected. Three places would have to change (§3). **But the reachability data say pool size is not the real
problem:** the admission rule is.

## 1. Every item, as ruled

| item | ruled | on `9c0c06c` | verdict |
|---|---|---|---|
| M1(a) | per-point `battery_size`; W1 keeps 4 + 16 + 16 and 64 + 32; threaded through `assign_battery`, `screen_draws` and `draw_pool` | `RAISED_N` (empty) → `battery_size(point)` → `sizes_at(n)`. At the registered count it returns the module constants, read at call time. W1 is hard-wired to the registered count. All three functions take the point's sizes | **as ruled** |
| W1 identity | proved | on the trial merge: `rbt132_w1_identity.py ce69f17` gives the committed file; `power_tau1.txt` byte-identical; the kill-sets reproduce, 16/16 and 24/24; the RBT-116 tests and `power.py` have no diff; `screen_draws`, `_job` and the CLI are IDENTICAL at W1; `rbt132_battery_identity.txt` reproduces (228 comparisons, W1 and all 18 points, `RAISED_N` empty) | **confirmed** |
| M1(b) | planted, probe and pays read the same counts | `assert_battery_size` is called in `planted` (after the screen), `pays` and `probe_members` (on the battery it reads). Members read the planted command's `battery.json` | **as ruled** (S-1: the check is not pinned on the confirmation count) |
| M1(c) | pool = ⌈(4 + 2n) × 64 / 36⌉, extended once by half again; first draws unchanged | `sizes_at`: 121 + 61 at n = 32, 235 + 118 at n = 64 (tested). `draw_pool` is one `default_rng(POOL_KEY)` stream, so a raised pool starts with the registered 96 (tested: `ext[:121] == pool`, `pool[:96] == registered`) | **as ruled** |
| M1(d) | cost printed beside the pick | `probe_cost(n)`: an upper bound in seasons and core-h (members, planted sets, screen over the extended pool) at the pick and at 16 | **as ruled** (NIT N-1) |
| S1 | `report()` per cell; strong/weak test | `per_cell = {p: from_planted([p], pooled)}`. The new test gives a strong and a weak cell and asserts UNREADABLE where pooling would say 32. My survivor `report-projects-pooled-cells` from #471 now dies | **as ruled** |
| S2 | calibration-only confirm-all flag; re-projection on 32 draws, final; trigger: the first branch fails **and** the pick is 64 or UNREADABLE | `planted --calibration`, refused outside `CALIBRATION_CELLS`. `_call` drops the `s2.c2 ∧ s2.c3` gate for (a) and (c); SEEN is unchanged. `--pooled` pools stage 2 and the confirmation exactly (`pool_stats`). `report` prints "SECOND STAGE due" when the pick is 64 or UNREADABLE | **as ruled** (S-1: the 64 case is untested) |
| N1 | the veto from `differ`; P(SEEN) = [P(c2)·P(c3)]² | `p_c3(q, n) = P(Bin(n, q) > n/2)`, with q = differ / n | **as ruled** |
| N2 | refusal counts printed | `theta_refused` sits beside each plant's ΔT in `report` | **as ruled** |

- **Full suite (trial merge): 769 passed, 1 skipped.**
- **The implementer's `rbt132_471_mutants.py` on the trial merge:** 45/45 killed, control sound
  (`rbt132_471_mutants_rerun.txt`).

## 2. Mutants: my further 9 (`rbt132_476_mutants.py/.txt`, on the trial merge)

**6 killed:** the extension floored instead of ceiled, the pool ratio floored, the cost screen left unextended, the
pooled `differ` taken from stage 2 only, the wrong calibration cells, and the cost with one season. **3 survive:**

| survivor | real? | fix |
|---|---|---|
| `second-stage-only-when-unreadable` | **yes, silent, in the ruled decision path.** If the 16-draw projection picks **64**, `report` no longer says "SECOND STAGE due", although the ruling's trigger is "64 or UNREADABLE". The test covers UNREADABLE (due) and 32 (not due), never 64 | **S-1:** add the 64 case to `test_report_projects_each_cell_on_its_own_plants`, or a sibling |
| `battery-check-stage2-only` | real but unlikely: `assert_battery_size` checks all three counts, and no test gives it a battery whose **confirmation** count alone is wrong. `assign_battery` always builds the two equal, but a hand-edited `battery.json` would pass | **S-1:** one more assertion, a battery at 4 + n + 16 refused |
| `pooled-mean-unweighted` | equivalent whenever both batteries have n usable draws (16 + 16). It differs only when θ refusals make them unequal, and the pooled test uses equal n | NIT N-2: give the pooled test unequal n (a refused draw) |

## 3. Can #476's pool machinery carry a larger pool or a screen-until-N rule? Yes, with three changes

**What the calibration's gate data say.** From `reachability.json`: 16 positive-control hosts, 96 draws per cell. A
draw is admissible when at least 8 of the 16 hosts eat ≥ 1 item.

| cell | admissible | hosts eating ≥ 1 item, per draw (count of draws) |
|---|---|---|
| c0-p030-PW-G | **5 / 96 (5.2%)** | 1: 4, 2: 12, 3: 12, 4: 15, 5: 17, 6: 20, 7: 11, **8: 2, 9: 2, 10: 1** |
| c0-p030-HP-G | **14 / 96 (14.6%)** | 3: 6, 4: 14, 5: 18, 6: 26, 7: 18, **8: 11, 9: 2, 10: 1** |

- **The typical draw has 5–6 of 16 hosts eating.** The half-the-hosts bar sits in the tail of the distribution, not
  at an unlucky pool.
- **At these rates, screen-until-N needs about 690 draws (PW) and 250 (HP) at the registered 36.** At n = 64, where
  132 draws are needed, it needs about 2,500 and 900.
- **Compute is not the limit:** about 2,500 × 16 screen seasons, roughly 4 core-h at 0.36 core-s.
- **Validity is.** Such a battery would be the top ~5% of the point's draws by reachability. W1's battery was 77% of
  its pool. PERCEIVES and K3 would then be read on a strongly selected sliver of the world, and the point's perception
  call would describe that sliver.
- **So the registered fix should look at the admission rule** (who the positive controls are, and what "admissible"
  means) **before it reaches for pool size.** That is the implementer's proposal to make; I flag it here so it is
  weighed.

**If a larger pool or screen-until-N is ruled, #476 needs these changes (none architectural):**
1. **`battery_size` / `sizes_at`.** The pool is keyed only on n, and at the registered n it short-circuits to the
   module constants, which must stay for W1. A larger pool **at n = 16** needs its own per-point field, for example a
   `POOL_OVERRIDE[point]` applied in `battery_size` after `sizes_at`. Do not change `sizes_at`'s registered branch.
   Otherwise RAISED_N = 16 would still give 64 + 32.
2. **`screen_draws` and `draw_pool`.**
   - Today there is one pool and one extension: `draw_pool(world, extended: bool)`, and `table += run(...[pool:])`.
   - Screen-until-N needs a loop: extend in fixed chunks until the battery is admissible or a registered cap is hit.
     It also needs `draw_pool(world, count)`, which is safe: the stream is prefix-stable, as the test shows.
   - The `extended` flag in the result, `reachability.json` and the gate line become a count.
   - W1's path must remain the two-step one, byte-identical, and so must `rbt132_battery_identity.py`.
3. **`probe_cost`.** The screen term uses `pool + extension`. With screen-until-N it needs the registered cap, or the
   expected pool at a stated admissible rate, or the cost line understates the screen.

Everything downstream is unaffected: `assign_battery` (pool order), `assert_battery_size`, the per-point counts, and
planted, pays and probe.

## 4. Findings

### SHOULD (the reason for FIX)

**S-1. Kill the two real survivors.**
- Add a `report` test where the 16-draw projection picks 64, and assert "SECOND STAGE due".
- Add an `assert_battery_size` test with a battery whose confirmation count alone is wrong.
- Re-run `rbt132_476_mutants.py`: `second-stage-only-when-unreadable` and `battery-check-stage2-only` must die.

### NIT

- **N-1.** `probe_cost` uses 0.36 core-s per season, RBT-125 §B's figure. The calibration lane has now timed real
  seasons at these cells. If they differ, print the measured figure beside it.
- **N-2.** Give the pooled-projection test unequal n (one refused draw), so `pooled-mean-unweighted` dies.
- **N-3.** When `--pooled` and the measured first branch would pass, `report` still prints "measured SEEN below
  0.45 somewhere". This is harmless, since the second stage runs only after the first branch failed, but the line
  should say "second stage".

## Files

In `runs/RBT-116/design-adversary/`:

| file | what |
|---|---|
| `rbt132_476_w1_suite.txt` | the trial merge's suite and W1 checks |
| `rbt132_471_mutants_rerun.txt` | the implementer's 45 mutants, re-run |
| `rbt132_476_mutants.py/.txt` | 9 further mutants; run on the trial merge, since they target #476's code |
