# RBT-130: the RBT-129 sweep's hooks ("RBT-129a")

This is the code gate that the registered RBT-129 design names (`runs/RBT-129/DESIGN.md` r4, §5.6 and §11.1). **Every
flag is off by default, and byte-identical when off.** `tests/test_rbt130.py` shows this against RBT-126's golden runs,
which were recorded on the code before RBT-126's own flags. RBT-113's and RBT-125's goldens pass unchanged in the full
suite.

| flag (CLI / config) | what it does | RBT-129 |
|---|---|---|
| `ecology --merge-null KIND` / `EcologyConfig.merge_null` | See below | the N arm (§5.2); ADVERSARY M8, §1.7 |
| `ecology --lesion-fauna KIND` / `EcologyConfig.lesion_fauna`; `FoodConfig.smell_lesion` | Every food sensor of that fauna reads the zero-information constant, 0, in its own ecology's seasons, under the legacy intensity and the contrast channel alike. Refused with `--merge-after` | the R_marker arm (§6.4; R2-M1) |
| `ecology --only-fauna KIND` / `EcologyConfig.only_fauna` | Only that fauna's ecology runs. The other fauna's founders are drawn from its own stream and then dropped, so this fauna's seasons are its half of a two-fauna run at the same seed, byte for byte (tested). Refused with `--merge-after` | the single-fauna retention arms (§6.4; S3-5) |
| `ecology --sweep-log` / `EcologyConfig.sweep_log` | See below | §5.3; RBT-118 prior §6 |
| `--obstacle-radius R` (evolve, arena, ecology) | Sets `world.random_radius`, which was config-only | §3.1 |

**`--merge-null KIND`.** At `--merge-after`, the other fauna is replaced by **B** (label `null_b`). B is a copy of KIND,
subsampled without replacement to the other fauna's count at the merge. B has:
- **its own mate pool:** a B child never has an A parent (tested);
- **its own stream:** `merge_null_seed_sequence`, at spawn key (index of KIND, 1, 0). That key collides with no other
  stream's (tested), and a null run is byte-identical to the merged run up to the merge (tested);
- **its own names** (`b<original>`, then `be<n>`);
- **KIND's body model.**

The copies keep their originals' records. The merged cohort gets a fresh arena bank at the merge in both M and N, so
the two arms see the same transient (tested in a persistent world). The run resumes byte for byte across the merge.

**`--sweep-log`.** It adds to every history entry:
- `share`;
- `starved` and `aged`;
- `eligible`;
- `median_energy`;
- `food_mean`, `work_mean` and `path_mean`;
- on the merge season, `merge_counts`.

Per-group composition and each member's food are already on disk: join `cohorts.jsonl` (the groups, by name and label)
with `lineage.jsonl` (each member's food that season).

**The strips compose.** One run combines:
- RBT-120's motor budget;
- RBT-125's contrast channel and root eating;
- RBT-126's breed rule (warned);
- `--merge-null` and `--sweep-log`.

Resumed from mid-run, it gives the same bytes (tested). A retention pair (`--only-fauna`, with and without
`--lesion-fauna`) runs under the contrast channel (tested). **RBT-124 (#420) is pending.** Its flags are to be added to
the combined test when it merges.

## The clutter census (`clutter_census.py` → `clutter_census.txt`)

The census covers 100 terrain seeds, with the ecology's own four-robot spawn layouts and 0.6 m keep-clear discs:
- **The 50N-try cap never binds** at any registered level, in either layout.
- **To hold the committed density on free ground**, PW's 3.6 m obstacle disc needs N = **15 / 29 / 44 / 59** at
  c = 0.5 / 1 / 1.5 / 2. The nominal counts in DESIGN §3.1 are 13 / 27 / 40 / 54.
- **The 3 m layouts are unchanged:** 7 / 14 / 21 / 28.

So the sweep's world blocks should use N_free (the DESIGN's S3 fix). The realised free-ground density then matches the
committed 0.815 per m² to within 2%.
