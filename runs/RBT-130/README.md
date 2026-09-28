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

**`--merge-null KIND`.** At `--merge-after`, the other fauna is replaced by **B** (label `null_b`). B is a copy of KIND
of **exactly the other fauna's count at the merge**, so N starts from M's composition (adversary M1). When that count
n is at most |KIND| = m, B is a without-replacement draw. When n > m, B is ⌊n/m⌋ full copies of KIND plus a
without-replacement draw of n mod m: a stratified fill, where every member is copied ⌊n/m⌋ or ⌈n/m⌉ times, which keeps
the clone load as low as possible. Every draw comes from B's stream. B has:
- **its own mate pool:** a B child never has an A parent (tested);
- **its own stream:** `merge_null_seed_sequence`, at spawn key (index of KIND, 1, 0). That key collides with no other
  stream's (tested), and a null run is byte-identical to the merged run up to the merge (tested);
- **its own names** (`b<original>`, suffixed on a repeat, then `be<n>`);
- **KIND's body model.**

The copies keep their originals' records. The merged cohort gets a fresh arena bank at the merge in both M and N, so
the two arms see the same transient (tested in a persistent world). The run resumes byte for byte across the merge.

**Forking an S checkpoint into M or N** (DESIGN §5.2, §5.6 item 2; adversary M2):
1. Run S to its season-59 checkpoint (`--seasons 60` writes `state.json` at season 60).
2. In that directory's `config.json`, set `ecology.merge_after` to 60, and for N also `ecology.merge_null`.
3. Resume with `ecology --resume --out DIR --seasons 300`, or `Ecology.resume(DIR, seasons=300)`.

The fork is byte-identical to a straight M or N run, which is tested for M and for both kinds of N. Copy the S
directory first, so that S itself continues unmerged.

**`--sweep-log`.** It adds to every history entry:
- `share`;
- `starved` and `aged`;
- `eligible`;
- `median_energy`;
- `food_mean`, `work_mean` and `path_mean`, over every member evaluated that season, the dead included;
- `food_mean_living`, `work_mean_living` and `path_mean_living`, over the survivors alone;
- on the merge season, `merge_counts`.

It also writes the season's starved and aged to `lineage.jsonl`, with `death: starved | aged` and their season's food
(adversary S1). So joining `cohorts.jsonl` (the groups, by name and label) with `lineage.jsonl` gives every seat's
food. Without the flag, the dead are not written, as before.

**`--only-fauna` and a cull.** Under a cull, the history's `culled` field gives the dropped fauna's count as 0, since
it has nobody to cull. Everything else is that fauna's half of the two-fauna run, byte for byte. The retention arms
have no cull (adversary S3).

**`--lesion-fauna` covers every food sensor of the fauna**, not only the planted motif's. DESIGN §6.4 is amended to
say so, with the reason it is still a valid floor (adversary S2).

**The strips compose.** One run combines:
- RBT-120's motor budget;
- RBT-125's contrast channel and root eating;
- RBT-126's breed rule (warned);
- `--merge-null` and `--sweep-log`.

Resumed from mid-run, it gives the same bytes (tested). A retention pair (`--only-fauna`, with and without
`--lesion-fauna`) runs under the contrast channel (tested). **RBT-124 (#420) is pending.** Its flags are to be added to
the combined test when it merges.

## The clutter census (`clutter_census.py` → `clutter_census.txt`)

The census covers 100 terrain seeds, with the ecology's own four-robot spawn layouts. It uses the generator's own
keep-clear, 0.6 m + foot/2, with the footprint drawn per point (adversary M3; the first version used 0.6 m alone):
- **The free areas** are 14.23 m² of the committed 2.6 m disc and 32.33 m² of PW's 3.6 m disc.
- **The 50N-try cap never binds** at any registered level, in either layout.
- **To hold the committed density on free ground**, PW needs N = **16 / 32 / 48 / 64** at c = 0.5 / 1 / 1.5 / 2. The
  nominal counts are 13 / 27 / 40 / 54.
- **The 3 m layouts are unchanged:** 7 / 14 / 21 / 28.

DESIGN §3.1 registers the PW counts as a dated pre-data amendment. The census assumes the committed start-distance
range. Re-run it with a world block's own `SimConfig` if that block moves the spawns.
