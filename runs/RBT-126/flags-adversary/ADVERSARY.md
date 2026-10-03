# RBT-126 flags adversary: PR #419 at `f03d830`

**Verdict: MERGE AFTER FIXES.** One MUST: the warning of item 5 is missing.

The code does what it says:
- **Off is byte-identical,** on the PR's goldens and on six further configurations. That holds on the flags head and
  on a trial merge with #414.
- **The embodied order matches the replica** at every season of real runs.
- **After a merge, the ranking is within each fauna and keeps the shuffle's fauna interleaving.** So the order cannot
  move slots between faunas.
- **No rule except `tickets` draws anything beyond the committed shuffle.** `tickets` adds exactly its own draw.
- **The leak's energy books and the `leaked` field are right.**
- **`--breed-gate none` is refused outside `--neutral`,** from the CLI and from Python.

What is missing: **nothing warns** when a user registers a rule that BREEDING-RULES.md screened as failing, and every
rule except `shuffle` failed it.

All probes and outputs are in `runs/RBT-126/flags-adversary/`. Each tree was installed `-e` into its own fresh venv
with `.[dev]`, and scipy is absent in each.

## 1. Byte-identity when off

**Full suites.**

| tree | result |
|---|---|
| flags head `f03d830` | **475 passed** (310 s) |
| trial merge of flags + #414 (`c591a75`), which merged cleanly | **514 passed** (324 s) |
| trial merge into the integration branch (`e3c9473`, which carries #415) | **481 passed** (317 s) |

- The suites include the RBT-113 goldens (`test_rbt113.py`, `test_salt0_golden.py`) and the PR's own 20 digests
  (`test_off_is_byte_identical_to_the_code_before_the_flags`, with the defaults both absent and named).

**Beyond the goldens** (`adv_off_identity.sh` → `adv_off_identity.txt`).
- I ran the same CLI ecology on the code before the flags (`3503cc2`) and on each new tree, and compared every file
  written: `config.json`, `lineage.jsonl`, `history.json`, `state.json`, `cohorts.jsonl` and the saved genomes.
- Six configurations the goldens do not cover: a merge (`--merge-after 2`), a cull, a shift, `--breed-stream 2`, a
  neutral arm with a merge, and persistent food (`--regrow-delay 2`).
- Each ran twice: with the flags absent, and with `--breed-rule shuffle --breed-gate energy` named.
- **ALL IDENTICAL on both trees,** 27–49 files per configuration, with no extra files.

**The `config.json` strips.**
- `EcologyConfig.to_dict` strips `breed_rule` and `breed_gate` only at their defaults. It is the `ecology` section's
  own writer, separate from `EvolutionConfig.to_dict`, which holds RBT-120's `motor_budget` strip and #414's
  perception strip.
- The trial merge with #414 is conflict-free, and its default `config.json` is byte-identical to `3503cc2`'s in all
  six configurations above. The strips therefore compose.
- On resume, `EcologyConfig(**raw)` refills the defaults, so old runs resume as before.

## 2. Does the embodied implementation match the replica?

`adv_embodied_order.py` wraps `rabbitstew.ecology.order_breeders` for the length of real `Ecology.run()`s:
- 5 rules × {no merge, merge} at 8 seasons, capacity 8;
- plus a 14-season, capacity-12 merged stress run: `adv_embodied_order_stress.txt`.

At every call it checks, on the energies as the embodied code sees them (after the leak and the gain, before births):
- **(a)** the generator's state afterwards equals a bare `rng.shuffle`'s. For `tickets` it is the bare shuffle plus
  one replayed `choice` per fauna with ≥ 2 breeders, with the same weights.
- **(b)** the fauna interleaving equals the bare shuffle's.
- **(c)** within each fauna: `energy` and `leakx` are in descending energy with ties in shuffle order, and `shuffle`
  and `leak` are the bare shuffle.
- **(d)** with one fauna, the order equals `breeding_rules.order` on the integration branch, given the same generator
  state and energies.

**Result:** 0 failures in 201 calls, of which 16 were merged seasons and 96 were compared with the replica, across
every rule.

**The leak's energy accounting**, on each run's own `lineage.jsonl` and `history.json`:
- every member-season satisfies energy_t = energy_{t−1} − leak + last_score − cost − birth cost × children paid, to
  within the log's rounding (worst 0.0007 over 36–150 steps a run);
- every history entry's `leaked` equals the rule's leak summed over that fauna's members entering the season, living
  and dying (worst 0.0010).
- **Energy is conserved, and `leaked` is right.** The PR's own `test_the_leak_conserves_energy` checks the same
  identity on unmerged runs; the probe adds merged ones.

**The leak rules themselves** match the replica: `leak` is e(1 − L), and `leakx` is e − L(e − thr) above the threshold
only, applied before the gain. See `test_the_replica_leaks_what_the_embodied_code_leaks`.

## 3. Within-fauna ranking after `merge_after`

- **It is correct:** see (b) and (c) above, and the PR's 50-seed hand-built test.
- **The breeding loop takes a prefix** of the list until `len(alive) >= slots`, and never skips a breeder. So an
  identical fauna interleaving means each fauna takes exactly the number of slots it would take under `shuffle`, that
  season, from that shuffle. **The order cannot move slots between faunas.**
- **RNG side effects:**
  - `shuffle`, `leak`, `energy` and `leakx` draw nothing beyond the shuffle (a).
  - `tickets` draws once per fauna, in a fixed fauna order (`sorted(groups, key=str)`), from the cohort's stream,
    which after a merge is the holistic one.
  - With the rule off, the code path is `rng.shuffle(breeders)` alone (`test_shuffle_is_the_committed_shuffle_alone`,
    and §1).
- **Not covered by the within-fauna ranking** (SHOULD 2): a rule can still move slots between faunas **indirectly**.
  - `leak` and `leakx` change energies, so they change who is eligible and who starves, and a starvation frees a
    slot.
  - This is inherent to a leak, not a bug, but the help text's "the same for both fauna" should not be read as slot
    parity.
  - In the tiny probe runs, the leak arms died out sooner: `leak:0.3` by season 5–9, `leakx:0.3` by season 7–10, while
    shuffle survived to 13. This is not evidence at scale.

## 4. `--breed-gate none`

- **Refused outside `--neutral`:**
  - in the CLI (`cli.py`: `--breed-gate none` without `--neutral` → SystemExit);
  - in Python, `EcologyConfig.check_breeding` refuses unless starvation is off and the living and birth costs are 0,
    and `Ecology.__init__` calls it.
  - Tested by `test_the_gate_is_removed_only_in_the_no_selection_economy`.
- **Byte-identical when unset:** §1, including a neutral arm with a merge.
- **When set:** `breeders = list(alive)` at the point where `alive` holds only this season's evaluated members,
  because children are appended after the copy. A member at energy −5 breeds (`test_without_the_gate_…`).
- **It is in `UNSHIFTABLE`,** as is `breed_rule`.

## 5. Can a user register a screened-out rule without a warning? **Yes: MUST.**

- **BREEDING-RULES.md on the integration branch recommends no rule.** Of the rules this PR exposes, every one
  except `shuffle` fails the ruling's criterion:
  - `energy` fixes the same-mean variance mutant (0.06–0.34);
  - `leakx:0.3` fixes it at 0.79–1.00, and fixes the 0.9× mean-loss mutant at 0.97 at g0 3;
  - `leakx:1.0` also fails;
  - `tickets` passes the negatives but barely spreads a ×1.25 (fixation 0.00–0.03);
  - `leak:L` collapses the population below the band and is saturated above it.
- **The PR prints nothing.** `ecology --breed-rule {energy, tickets, leak:0.3, leakx:0.3, leakx:1} …` runs silently
  from the CLI (`logs.txt`), and there is no `self.log` warning in `Ecology.__init__`.
- **The help text** describes each rule and cites BREEDING-RULES.md, but does not say that none passed.

## MUST

1. **Print a warning whenever `breed_rule` is not `shuffle`,** from `Ecology.__init__`, so that the CLI, Python and
   resume all see it. Like the retired-economy message, it should name the rule and its screen result, for example:
   > warning: breed_rule 'leakx:0.3' failed RBT-126's breeding-rule screen (it fixes a same-mean, higher-variance
   > mutant; runs/RBT-126/BREEDING-RULES.md). No rule is recommended; register its planted negatives (R10) with any
   > arm that uses it.

   Give one line per rule: energy and leakx, variance; tickets, spreads almost nothing; leak, collapse or saturation.
   Add a test that the warning is emitted, and that it is not emitted under `shuffle`.

## SHOULD

1. **Add one sentence to the `--breed-rule` help:** "no rule passed the screen (BREEDING-RULES.md)". Also replace
   "the same for both fauna" with "applied within each fauna; after a merge each fauna keeps the shuffle's slots".
2. **Document the indirect slot channel (§3).** A leak changes eligibility and starvation per fauna. Any merged arm
   under a leak rule should report births per fauna against its shuffle comparator.
3. **Strengthen the embodied merge test.** `test_after_a_merge_the_rule_runs_on_both_fauna` checks only that both
   faunas have history rows and that `leaked ≥ 0`. Assert (b) inside a real merged run, as `adv_embodied_order.py`
   does, not only on hand-built pools.

## Files

- `adv_off_identity.sh` → `adv_off_identity.txt`: off is byte-identical beyond the goldens, on the flags head and the
  #414 trial merge.
- `adv_embodied_order.py` → `adv_embodied_order.txt` and `adv_embodied_order_stress.txt`: order, RNG, interleaving,
  replica agreement, and the energy and `leaked` books in real runs.
- `logs.txt`: the suite results, the #414 and integration trial merges, and the silent CLI runs.

---
_Generated by [Claude Code](https://claude.ai/code)_
