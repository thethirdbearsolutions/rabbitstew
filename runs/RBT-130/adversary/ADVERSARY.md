# RBT-130 adversary: the RBT-129 sweep's hooks (PR #424 @ 424b82a)

**Verdict: MERGE AFTER FIXES.** There are three MUST items. Each fix is small and local.

- **M1. N does not start from M's composition when the copied fauna is the minority.** B is capped at KIND's own
  count. So N starts at 1 : 1 exactly where ADVERSARY M1 says it must not.
- **M2. The registered fork crashes.** Forking an S checkpoint into N raises `KeyError: 'null_b'`. A one-line fix
  makes the fork byte-identical to a straight N run.
- **M3. The census's N table for PW is wrong.** The census's free area ignores the generator's `foot/2` exclusion.
  The PW N_free is 16/32/48/64, not 15/29/44/59.

The rest holds under probing:
- B's stream collides with nothing.
- The subsample is uniform.
- The lesion is clean on both channels, touches only its own fauna, and leaves the motor path alone.
- `--only-fauna` is its half, byte for byte, in every configuration I tried.
- Off is byte-identical.
- Every strip composes with RBT-124 #420's current head.

**Environment.** A clean `.[dev]` venv (no scipy; Python 3, mujoco and numpy from `pyproject`), x86_64.
- **Full suite on the PR head: 562 passed** (6 min 48 s). This matches the PR's claim.
- **Trial merge of #424 @ 424b82a with #420 @ 5c959ba: 586 passed** (see §4).

Probes (all under this directory; they write only to temp dirs):

| probe | → | covers |
|---|---|---|
| `probe_hooks.py` | `probe_hooks.txt` | P1 the B count; P2 the spawn-key census; P3 `--only-fauna` in six configurations; P4 the lesion under workers and persistent food; P5 the season's dead |
| `probe_fork.py` | `probe_fork.txt` | DESIGN §5.6 item 2: fork S → M / N by resume |
| `probe_census.py` | `probe_census.txt` | the census's free area, with the generator's own exclusion radius |
| `test_rbt130_x124_adv.py` | (§4) | every strip plus RBT-124's, on the trial merge |

## MUST

### M1. B is capped at KIND's count, so N does not carry M's merge-time composition (M1, R10)

**The code.** `_replace_with_null` draws `k = min(len(gone), len(src))` copies without replacement. When the copied
fauna KIND has fewer members than the fauna it replaces, B gets `len(src)` members, not the replaced count. The PR's
own test asserts `len(copies) == min(n_other, len(before))`. The README and the PR body say "subsampled to the other
fauna's count", with no caveat.

**`probe_hooks.txt` P1.** A cull at season 2 leaves one fauna short at the merge (season 3):

| arm | counts at the merge | A share at the merge in N | M's share for the same fauna |
|---|---|---|---|
| N-holistic | holistic 1, conventional 6 | **0.50** (B = 1, should be 6) | 0.14 |
| N-conventional | conventional 2, holistic 5 | **0.50** (B = 2, should be 5) | 0.29 |

**Why it matters.**
- The registered N (DESIGN §5.2, "subsampled to the replaced fauna's count at season 59, so that N starts from M's
  composition (M1)") takes KIND = holistic on odd seeds and designed on even ones. So on every seed where KIND is the
  minority at 59, **N starts at 1 : 1**. Roughly half the seeds with any imbalance are affected.
- That is precisely ADVERSARY §1.1's failure. It hits hardest in the poor worlds (g0 ≤ 0.8), which are the only
  worlds where N runs.
- **K2** reads y′ from the merge on, so its centring survives. But **the drift SD of y′ at that point's turnover**
  (§5.3(b)(ii)) and **the fixation-time distribution** (iii) are then measured from the wrong start. Near 1 : 1 the
  drift SD of a share is at its largest, and fixation is slowest.

**Fix.**
- When the replaced count n exceeds |KIND| = m, fill B with ⌊n/m⌋ full copies of KIND plus a without-replacement
  subsample of n mod m. Every draw comes from B's stream. This is stratified, so each member is copied ⌊n/m⌋ or
  ⌈n/m⌉ times. It stays unbiased and has the least clone load.
- Plain sampling with replacement is the other option. Record the rule in the docstring and README.
- Names stay unique without new code: `_claim_name` already suffixes a repeat (`bh12`, `bh12-1`). The test should
  still check it.
- **Test:** force the minority case (a cull before the merge, as P1 does) and assert B's count equals the replaced
  count, for both KIND.
- If m = 0, B is empty. Log it. The seed is invalid under M2's rule anyway.

### M2. The fork at season 59 crashes for N (DESIGN §5.2, §5.6 item 2, K1)

**What happens.** N and M are registered as forks of S's season-59 checkpoint. The code path is an S `state.json`
with `merge_after` and `merge_null` set in `config.json`, then `Ecology.resume`. `Ecology.__init__` sets
`counter[null_b] = 0`. But `resume` then replaces `counter` wholesale with the checkpoint's, and an S checkpoint has
no `null_b` key. So B's first birth raises `KeyError: 'null_b'`.

**`probe_fork.txt`:**
- M forks byte-identically to a straight M run.
- N-holistic and N-conventional both **fail with `KeyError: 'null_b'`**.
- With `if eco.merge_null is not None: e.counter.setdefault(NULL_B, 0)` after the counter is restored in `resume`,
  all three arms fork **byte-identically** to the straight runs (lineage, cohorts, history). That includes N's
  `merge_counts`, because `_merge` runs after the resume.

**The PR's resume test misses this.** It resumes a run that already had `merge_null` from season 0.

**Fix.**
- Apply the one line above.
- Add a test: fork S → N for both KIND and assert bytes equal to the straight run. This is §5.6 item 2's
  "fork … and its K1 test", which the PR does not claim and §11.1 gates on.
- Add a README paragraph on how to fork: which `config.json` keys to edit, and at which saved season.

### M3. The census's N_free for PW uses the wrong exclusion radius (S3, §3.1)

**The mismatch.**
- `world.random_terrain` rejects a centre within **0.6 m + foot/2** of a spawn, with foot ~ U(0.15, 0.7). DESIGN §3.1
  says the same.
- `clutter_census.py` computes `free_area` with **0.6 m** alone. The realised density it prints is N/A_free of that
  same area, so its "matches the committed 0.815 to within 2%" is circular.

**`probe_census.txt`** measures acceptance with the footprint drawn per point, as the generator draws it, over the
same 100 spawn layouts:

| exclusion | A_free(2.6) | excluded (3 m) | A_free(3.6) | excluded (PW) | PW N_free at c = 0.5 / 1 / 1.5 / 2 |
|---|---|---|---|---|---|
| census (0.6 m) | 17.19 | 19.1% | 36.20 | 11.1% | 15 / 29 / 44 / 59 |
| generator (0.6 + foot/2) | 14.23 | 33.0% | 32.33 | 20.6% | **16 / 32 / 48 / 64** |

- The 3 m layouts are unchanged at 7/14/21/28.
- The PW table the README reports (and that the world blocks would be built from) sets PW about **7–8% below** the
  committed free-ground density at every level.
- That is a layout confound in the clutter axis, which is what S3 existed to remove.

**Fix.**
- Use `cr + foot/2`, with foot drawn per point, in `free_area`.
- Regenerate the `.txt` and README numbers.
- Print the realised free-ground density against the footprint-aware area. It is still one number per level, but no
  longer circular.

**Also state the census's assumption.** It uses the committed start-distance range for PW's spawns (a default
`SimConfig`). If PW's world block moves the spawns, re-run it with that block's `SimConfig`.

## SHOULD

**S1. The season's dead are not on disk, so §5.6 item 3's "per group … each member's food" and the sweep means
are survivor-only.**
- `lineage.jsonl` gets one row per **living** member per season. Rows for the dead are written only for culls and
  merge-null departures, and starvation and old age are neither.
- `probe_hooks.txt` P5: of 74 cohort seats in a 7-season N run, **18 have no lineage row for their season**. That is
  exactly the 18 deaths in history. They are the season's starved and aged, the members whose food matters most to
  interference.
- The README's "join cohorts.jsonl with lineage.jsonl (each member's food that season)" is therefore false for them.
- Likewise `food_mean` / `work_mean` / `path_mean` average survivors only. That is the survivor weighting S-3
  warned about for the flow. §5.3(a)'s net income per birth needs the dead's income too.
- **Fix, under `--sweep-log` only, so off stays byte-identical:**
  - write each season's dead to the lineage with `death: starved | aged`, as the cull already does;
  - compute the three means over all evaluated members, or print both over-all and survivor-only.

**S2. The lesion blinds every food sensor, and the DESIGN says "the motif's food sensors" (§6.4).**
- Founders planted at a = 6 probably carry only the motif's noses, so at season 0 the two agree.
- Over 300 seasons, a food sensor gained by mutation in R_marker is also blind, and in R_sel it is not. That makes
  R_marker a "no smell at all" floor rather than "the motif is uninformative".
- It is arguably the cleaner planted negative, and a motif held for its motor effect is still held in both arms. The
  motor path, `eat_from` and every non-food sensor are untouched (the code reads 0 at `src == "food"` and skips the
  contrast baseline, nothing else).
- But it is a deviation from the registered wording. Get a one-line coordinator ruling, or lesion by sensor
  identity.

**S3. `--only-fauna` writes a different `culled` field.** `probe_hooks.txt` P3 checked six configurations:
- persistent food;
- persistent food with workers 2;
- stagger ages;
- a cull;
- `breed_stream 3`;
- `sweep_log` with `leakx`.

The lineage and cohorts are byte-identical in all six, for both fauna. So is the history, with one exception: under a
cull, the history entry's `culled` field names the absent fauna's count as 0 rather than its two-fauna value. That
field is bookkeeping (the other fauna's cull draws nothing from this fauna's stream), and the retention arms have no
cull. Either document it or write only the own fauna's count under `only_fauna`.

## NITS

- `lesion_fauna` together with `only_fauna` naming the other fauna is accepted, and it lesions nothing. Refuse it.
- After a merge under `merge_null`, `_cull` iterates `ORDER`, so B cannot be culled. The sweep has no post-merge
  cull. Refuse `cull_at >= merge_after` with `merge_null`, or iterate the cohort's labels.
- The comment at `ecology.py` `rng = self.rngs[kinds[0]]` ("holistic after") is stale under N. It is KIND's stream.
- **A note for the DESIGN, not the code.** B's members are clones of A's at the merge. Clone pairs meet in shared
  arenas and correlate early outcomes, so N's drift SD in the first seasons after the merge includes that correlation.
  M1's stratified fill should keep the clone load minimal. It fades within one lifespan.

## What holds (the checks, in the brief's order)

### 1. N is a null for M, apart from M1

**B differs from A only by label, names, stream and mate pool.**
- `_breed` uses `rngs[label]` for mutation and crossover, and the body model is `_body(label)`.
- Mates are filtered by `record["kind"]`.
- Names are `b<orig>`, then `be<n>`.
- Records (energy, age, evals, score) are deep-copied.

**The subsample is unbiased.** It is `rng.choice(len(src), k, replace=False)` from B's stream, which is uniform over
positions, so it is independent of age, energy and fitness. The positions are then sorted, which fixes list order and
does not change who is drawn.

**The stream never collides.** `probe_hooks.txt` P2 enumerated 405 streams at seed 11:
- the three spawned streams, `(i,)`;
- `breed_stream` K = 1..200, `(0, 0, K)`;
- RBT-96's salt S = 1..200, `(0, S)`;
- both null keys, `(0, 1, 0)` and `(1, 1, 0)`.

There are no duplicate keys and no duplicate first draws. The cull, the shift and the merge draw no stream of their
own. The cull uses `rngs[kind]`, the shift draws nothing, and the merge draws only from B's stream. B's stream is
created without drawing from any other stream. The PR's test shows the N run equals M up to the merge.

**No asymmetric advantage after the merge.**
- Member order [A…, B…] only indexes a uniform permutation (groupings) and a shuffle (breeding order).
- RBT-126's `order_breeders` ranks within each label, over positions the shuffle fixed. `sorted(groups, key=str)`
  only fixes the tickets draw order.
- Crossover draws come from the cohort stream for both labels, as in M.
- The arena bank is fresh at the merge in both arms, keyed on the labels. Under N-holistic its seeds come from the
  holistic stream at the same state as in M. Under N-conventional they come from the conventional stream: the same
  transient in distribution (full arenas), not in seeds. That is what M8 asked for.

### 2. The lesion is a valid planted negative (R2-M1, R7)

**The value.** A food sensor reads 0 in `sensor_values`.
- Under the contrast channel, 0 is `tanh(G(x − b))` at the baseline. `_food_contrast` is skipped, so the running
  baseline never advances, and nothing else reads it.
- Under the legacy intensity, 0 is probe_food's blind reading.

**What it touches.**
- It is applied only to a cohort whose kinds are exactly `(lesion_fauna,)`, on a deep-copied sim.
- `probe_hooks.txt` P4: the other fauna is byte-identical under persistent food, and workers 1 and 2 are
  byte-identical (the flag survives pickling to the workers).
- It adds no RNG draws.
- The motor path is untouched: actuators, `eat_from` (including `"sensor"`, which reads which Parts carry noses, not
  their values) and every other sensor source.

### 3. `--only-fauna` gives its half

Byte-identical as §S3 lists. It holds because:
- the other fauna's founders (and staggered ages) are drawn from its own stream and then dropped;
- the terrain stream is drawn once a season whatever the cohorts;
- arena seeds and groupings come from the fauna's own stream;
- names are per-fauna counters.

### 4. Off is byte-identical, and the strips compose

**Off.** The RBT-113, RBT-125 and RBT-126 goldens pass in the 562. The defaults write no new `config.json` keys, and
`smell_lesion: false` is stripped. An old `config.json` resumes through the dataclass defaults.

**The trial merge with #420 @ 5c959ba.**
- It conflicts in `evolution.py` (imports) and `simulation.py` (`_eating_geoms` beside `_settle_until_rest`). Both
  conflicts are additive, and they come from #420's older base, not from #424.
- Resolved by keeping both sides. `test_rbt130_x124_adv.py` then runs every strip in one run, for both KIND, and it
  resumes byte for byte:
  - `motor_budget` 1.77;
  - `ball_cone` and `hinge_range` π/2;
  - `effector_bias_sigma` 0;
  - `settle_until_rest` 0.01;
  - contrast 2.5 with root eating;
  - `random_radius` 3.6;
  - `leakx`;
  - `merge_null` and `sweep_log`.
- The same test checks the retention pair (only-fauna equal to its half, and the lesion different) under RBT-124.
- With `test_rbt130.py` and `test_rbt124.py`: **52 passed**. **The full suite on the trial merge: 586 passed**
  (562 + #420's 20 + these 4; `trial_suite.txt`).

### 5. The sweep log and the census

**The sweep log.**
- `share` = alive / capacity in force. After the merge that is the pooled slots, which is §5.3(b)'s share.
- `starved` + `aged` = deaths − culls (the PR's test).
- `eligible` and `median_energy` are taken after deaths and before births.
- `merge_counts` appears only on the merge season, and is both fauna's counts after season `merge_after − 1`. That is
  "the counts at season 59".
- The gaps are S1.

**The census.** The 50N cap never binds. The N table is M3.

**Out of scope, not asked of #424, but gated by §11.1.** §5.6 item 5 (the world-block export) and §5.3's "unreachable
items per clutter level" have no code here. M2 supplies item 2.
