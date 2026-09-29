# RBT-129 L1 adversary: the gated Stage-1 M/N emitter (PR #500)

- **PR:** #500, head `ebcd38654fb90f1dc967ddea3fc023276553dde0`, base `claude/new-session-4cao7d` at `184c0c7`.
- **Registered text read:**
  - DESIGN §5.2, §6.1, §4.1, §9.1, §11.1, §11.2 and §15;
  - AMENDMENT-FOUNDING F5, F7, T5, T7 and §6;
  - founding-screen-adversary L1;
  - the rulings on #493 (comment 5883124591) and #495 (comment 5883893234).
- **Nothing was launched.** Only the 108 census runs of the 36 Stage-1 points were restored, read-only, from their
  `ckpt/` branches. **No Stage-1 branch exists** (`git ls-remote origin 'refs/heads/ckpt/rbt-129-stage1*'` → 0), so
  no Stage-1 S60 was read.

## Verdict: **MERGE AFTER FIXES**

The code does what it says. There are no correctness bugs:
- the g0 re-derives exactly;
- the gate's structure, the fork settings and the salt plumbing are right;
- every refusal fires before a lane is written.

What remains are rulings the registered text does not settle, and test gaps in one guard. The rulings must be made
**before `mn-emit` reads any S60**, because each of them changes which points get N, or how many.

### MUST

1. **Rule N's eligibility (OQ1 and more).**
   - T5 item 2 ("N runs only where census g0 ≤ 0.8 … with the same seed rule as M") does not repeat item 1's
     "designed fauna not FOUNDING-FAIL" clause. The PR makes N a subset of the M-admitted points.
   - On the real census the two readings give **different N sets** (`g0_independent.txt`,
     `test_hole_n_eligibility_is_the_m_gate_not_item_2_alone`), assuming every seed is valid:
     - item 2 alone: c0-p080-PW-G, c0-p030-PW-G, **c1-p030-PW-L** (g0 0.525, designed FOUNDING-FAIL), c2-p010-PW-G;
     - the PR: c0-p080-PW-G, c0-p030-PW-G, c2-p010-PW-G, **c1-p010-PW-L**.
   - Rule the PR's reading, N ⊆ the M-admitted points, together with OQ1's slot-freeing for N (below), as one
     DATA-INFORMED addition to T5 item 2.
2. **Rule the rescale sentence (OQ3).** §5.2 still says the gate's thresholds "are rescaled by the same ratio before
   Stage 1", and r = 1.53 was measured. The PR does not rescale, and says so only in a code comment and an open
   question.
   - The readings give different gates:
     - unscaled: 10 M-eligible points and 7 N-eligible;
     - thresholds ÷ r: 5 and 2;
     - thresholds × r: 10 and 10.
   - Recommendation: **not rescaled** (reasons under OQ3). But it has to be a ruling on record, and the emitter's
     comment should cite it.
3. **Test the K-SALT condition both ways.** Two live mutants survive the PR's tests and mine (`mutants_extra.txt`):
   - K-SALT not required at 129001 when (s ≥ 1, t = 0). F7 and `stage1_units` both run it there.
   - K-SALT required where t ≥ 1. No K-SALT runs there, so `mn-emit` could never emit.

   The code is right today. But this is the guard the brief names ("K-SALT PASS must be required"). Add a test at
   j = 1 with (1, 0), and one at j ∈ {1, 2, 3} with (1, 1) that expects no refusal.

### SHOULD

1. **Correct OQ4's premise.** The README and the PR body say `alive > 0` and "before refill" differ "when a fauna's
   every survivor dies in season 59 after breeding". **That cannot happen.**
   - In `Ecology.step`, breeders are drawn from the season's survivors, after deaths.
   - A parent pays `birth_cost`, but it cannot die until a later season.
   - So births > 0 implies alive − births > 0, and the two readings are the same test of extinction.
   - Checked on all 8,584 history rows of the 108 census runs (0 exceptions; 0 of 216 fauna-seeds differ at 59), and
     on a tiny run (`test_confirm_booked_and_before_refill_extinction_agree_in_the_ecology`).
   - The "before refill" mutant survives because it is equivalent.
   - Say this, and add the invariant test to the PR's suite.
2. **Check K-SALT before the extinct short-circuit.** `s60_state` returns False for a unit with `EXTINCT.txt` before it
   reads `KSALT.txt`. A VOID at an M-eligible point whose S also went extinct before the merge is therefore passed over
   (`test_hole_a_ksalt_void_on_an_extinct_unit_is_not_refused`).
   - The lane already stopped loudly on the VOID, so this is a second line of defence only.
   - #495's ruling is "A K-SALT VOID fails loudly".
3. **Hold M/N forks to the gate's admission list in `run_lane`.**
   - `lanes/1-MN/launch.txt` records only `point:Mk/Nk`.
   - A hand-added fork at a point or seed the gate did not admit, with the right salts, passes `check_lane_salts` and
     `check_lane_blocks` (`test_hole_a_hand_added_m_fork_passes_the_lane_checks`).
   - Fresh jobs are held to their blocks. Record the admitted (point, seed, arm) triples, and refuse any fork not
     among them.
4. **Explain the cost basis in the gate table.** The disclosure's N basis is 0.57 core-h an arm at 20 core-s. That is
   102.6 arm-seasons, where the emitted N runs 240 on every seed, 2.34× more. It is offset by M having 10 eligible
   points, not 12. Say this in one line of the gate table.
5. **Add a test that kills the g0 fauna-filter mutant.** It is equivalent on the census, which has only the two
   faunas. A test with a stray population would kill it (nit).
6. **Note what the gate table reveals.** It shows each M-eligible point's valid-seed count. That reveals PARTIAL
   status there before the Stage-1 readout. It is registered input (T5, §6.1 "printed per seed"), not a peek, but
   the Stage-1 readout should note that these counts were seen at emission.

## 1. g0, independently (`g0_independent.py` → `g0_independent.txt`)

**Registered source.**
- DESIGN §5.2 item 1: "census g0 (seasons 30–59, faunas pooled, + 0.35; the early regime, lower than the late one)".
- 0.35 is "the replica's 0.35 (its 0.1 work charge and 0.25 living cost)" (§6.2; `prior_regime.py`:
  g0 = mean_F(n_F) + 0.35).
- T5 fixes the formula "exactly as the Stage-0 readout computed it" (`stageP0_readout.py` lines 311–343):
  - the mean of food − p · work / 1000;
  - over every lineage row except cull and merge-null;
  - generations 30–59;
  - seeds 129001–129003, both faunas pooled;
  - + 0.35.

**Result.**
- My script is stdlib-only and imports nothing from `stages.py`. For all 36 Stage-1 points, **g0 (to 3 decimals) and
  the designed C2 flag agree with the committed readout and with the PR's `mn_rank.txt`: 0 disagreements.**
- `stages.py mn-rank` at the PR head, run on my restored data, reproduces `mn_rank.txt` byte for byte.
- M-eligible (g0 ≤ 1.0, designed not FOUNDING-FAIL, not an anchor): 10 points. N-eligible under the PR's reading:
  7 points.
- The 4 points with no census g0 (c1-p080-PW-G, c1-p080-PW-L, c2-p030-PW-G, c2-p080-PW-G) are excluded, as they must
  be.

## 2. The gate as registered

- **M.** At points with g0 ≤ 1.0, designed not FOUNDING-FAIL (T5), not an anchor (§5.2 item 3), ranked lowest g0
  first, up to 12, "forked only on seeds valid at the merge". **Matches** (`mn_gate`).
- **Slot-freeing.** T5: "a point where M runs on no seed frees its slot for the next point in the ranking". **Matches.**
  At Stage 1 it cannot bind for M: 10 are eligible for 12 slots.
- **N.** "only where census g0 ≤ 0.8, up to 4 … with the same seed rule as M". The PR reads this as N ⊆ M-admitted
  points, with N slots freed alongside M's. **See MUST 1 and OQ1.**
- **Fork settings.** M is `merge_after 60, pooled_capacity 120`. N is the same, plus `merge_null` holistic on odd
  seeds and conventional (designed) on even. Both fork from Stage-1 `ckpt60`, never from the census S. **Matches** the
  §5.2 arm table and the pilot's forks.

**The season-59 read.**
- T5: "At a gated point, M is forked only on seeds valid at the merge (both faunas alive at season 59 in S)." §6.1: "A
  seed is valid for the share test when both faunas are alive at the merge (season 59's counts, printed per seed)".
- So the registered text requires exactly a both-faunas season-59 read at the points the gate can admit. Reading it
  at M-eligible points only is the minimum.

**Is the read limited?** Yes. `s60_state` returns only a boolean, from:
- the unit's pre-merge `EXTINCT.txt`, which is written only when every population is empty at or before season 60
  (`run_job`, snapshot);
- `ckpt60/history.json`, the row for season 59, `alive`.

The other things it reads are provenance checks, and each can only refuse:
- `ckpt60/config.json` against the S60 config at the screened salts;
- `KSALT.txt`.

S's own directory, which runs past the merge, is never read. `test_confirm_the_s60_read_is_the_season_59_state_only`
runs S on and then deletes it; the gate's answer does not change. The emission is a function of (census, salts,
validity booleans), so no post-merge outcome can enter it.

**"Alive at 59" or "before refill".** They are identical in this ecology (SHOULD 1). Keep `alive > 0` and say so.

## 3. The implementer's open questions: recommended answers

1. **N slot-freeing, and N ⊆ M.**
   - Adopt the PR's reading: N at the M-admitted points with g0 ≤ 0.8, in rank order, up to 4, on M's valid seeds.
     A point whose M runs on no seed frees its N slot too.
   - Why:
     - "with the same seed rule as M" (T5) makes N run on no seed wherever M does;
     - a slot held by a point that runs nothing would re-create the waste T5's freeing rule removes;
     - §6.1 says "A share call needs N at the point; an M arm without N reports y′ descriptively", which treats N as
       the null of a point that has M.
   - But this is **not in T5's text**, and item 2 read alone admits the designed-FF point c1-p030-PW-L. Rule both
     halves explicitly and label them DATA-INFORMED with T5's rule (MUST 1).
   - `test_confirm_a_freed_m_slot_also_frees_the_n_slot` shows the other reading: 3 N points instead of 4 when one
     point has no valid seed.
2. **Excluding c1-p030-PW-G (and c1-p030-U-L) takes no slot.** Correct.
   - §5.2 item 3: "The sweep does not re-run them."
   - §9.1: "The sweep does not run M or N at W118-a/b/c."
   - §11.2 prices the anchor fallback as its own optional row (+46–57), not inside the 12 / 4.
   - If RBT-118 declines the salts (T7), the fallback at W118-a and W118-c should fork from those points' own Stage-1
     `ckpt60`: two faunas at (s_j, t_j), at the point. W118-b is not a Stage-1 point, so it forks from F5's fork source.
   - That is a separate command, after that ruling. It is not L1's.
3. **The threshold rescale by r = 1.53.** Recommend **no rescale**, and ask for it to be ruled (MUST 2). Reasons:
   - §4.1, the same registration: "Only those constants may change. The grid, the rules, **the thresholds** and the
     calls may not." The ratio was applied where §4.1 puts it, to the replica's drift SD in `power.py`
     (`power_stageP.txt`).
   - T5 was written and adopted after r was known (#490/#491 → #493). It takes precedence (§15), and it discloses
     171 / 320 on 1.0 / 0.8.
   - "The same ratio" is a ratio of y′ SDs. The thresholds are in income units, so neither direction is registered.
   - Note: the re-run moved shuffle's resolving band to g0 0.50–0.65. The PR's 4 N points with every seed valid all
     sit at g0 ≤ 0.554, so a 0.65 bound would change N only if freeing reached c0-p010-PW-G (0.666) or c1-p080-HP-L
     (0.680).
4. **Validity reading.** They are equivalent (SHOULD 1). Keep `alive > 0` (the readout's y′ count, and the count the
   merge itself uses). Document the equivalence.
5. **A K-SALT VOID fails the whole emission closed.** Right.
   - #495's ruling: "A K-SALT VOID fails loudly".
   - F7: a VOID "voids the point for the seed … and RBT-129c's stream claim is re-opened". A re-opened stream claim
     puts every salted seed in question, not only that one.
   - After a coordinator ruling that closes the claim, dropping that point-seed (not valid) is the F7 outcome. That
     can be a flag added then.
   - Fix the ordering hole (SHOULD 2).
6. **N priced at 240 seasons.** Right. The §5.2 arm table runs N over seasons 60–299 on every seed (K alternating).
   The disclosure's 0.57 core-h an arm is a legacy r3 figure (SHOULD 4).
7. **Valid-seed counts in the table.** Not a peek beyond the registration. They are the gate's registered input, and
   §6.1 prints season-59 counts per seed anyway. Print only the per-point count, as the PR does, not which fauna died
   (SHOULD 6).

## 4. Guards: can M/N be emitted when one fails?

`test_confirm_every_refusal_writes_no_lane` drives `stages.main(["mn-emit", …])` through each failure. Every one exits
8 with no `lanes/1-MN` written:
- the screen gate refuses;
- `lanes/1/launch.txt` is missing;
- `launch.txt` is at other salts;
- an S60 is not done;
- a `ckpt60` is at other salts;
- a K-SALT is not PASS.

Salts are checked three times:
- against each `ckpt60/config.json`, the whole S60 config (`s60_state`);
- in the lane, against `launch.txt` (`check_lane_salts`, fork branch);
- at fork time, against the source (`run_job`).

The PR's mutants kill all three checks, and the salt-0 census adoption is refused at any other salt.

**Holes found:** SHOULD 2 (a K-SALT VOID on an extinct unit is passed over) and SHOULD 3 (a hand-added fork in the
lane). Neither lets `mn-emit` emit past a failed guard.

## 5. Cost (`test_confirm_the_cost_figures`)

- **174 / 326 core-h** is 80 M arms + 32 N arms, all at 240 seasons, at 23.35 / 43.72 core-s (174.3 / 326.4).
- **171 / 320 core-h** is T5's 12 × 8 M arms at 240 seasons, plus 4 × 8 N arms at 0.57 core-h an arm at 20 core-s,
  scaled (`founding_expect.py` line 194): 149.4 + 21.3 = 170.7 at 23.35 core-s, and 279.8 + 39.9 = 319.7 at 43.72.
- **The difference, +3 / +6,** is two effects:
  - M has 10 eligible points, not 12: −24.9 / −46.6;
  - N priced at full length: +28.5 / +53.4.
- This is within T5's "about". Both are upper bounds. Seeds that are invalid at the merge run no M or N.

## 6. Suite and mutants

- **Full `pytest`**, clean `python3 -m venv` + `pip install -e '.[dev]'`, no scipy, at the PR head: **879 passed, 1 skipped** (`suite.txt`). The claim reproduces.
- **`test_adversary.py`:** 10 passed.
- **`mutants_extra.txt`:** 8 new mutants.
  - 3 are killed.
  - 2 are equivalent:
    - "before refill", by SHOULD 1's invariant;
    - the `--fair`/`--eat` string compare, since `check_fair` and `check_eat` already force both to the single
      ruled value.
  - 1 is equivalent on the census: the g0 fauna filter (SHOULD 5).
  - **2 are live: the K-SALT conditions (MUST 3).**

## Reproduce

```
git worktree add /tmp/pr500 ebcd38654fb90f1dc967ddea3fc023276553dde0
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install -e '/tmp/pr500[dev]'
# census data: for each Stage-1 point p and seed s in 129001-129003,
#   scripts/durable.sh restore DATA/runs/RBT-129/stage0/$p/$s/S rbt-129-stage0-$p-$s-S
python3 runs/RBT-129/mn-emitter-adversary/g0_independent.py DATA > g0_independent.txt
cd /tmp/pr500 && PR500=/tmp/pr500 /tmp/venv/bin/python -m pytest <this dir>/test_adversary.py -q -p no:cacheprovider
PR500=/tmp/pr500 python3 <this dir>/mutants_extra.py /tmp/venv/bin/python > mutants_extra.txt
cd /tmp/pr500 && /tmp/venv/bin/python -m pytest -q -p no:cacheprovider      # suite.txt
```
