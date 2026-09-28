# RBT-132 gate check of #478 (head `2067b2d`): the calibration screen's "≥ 1 control eats" rule

*2026-09-28, the design adversary. Target: the implementer's `GATE_DIAG.md` proposal (c).*

**How I checked it.**
- #478 was trial-merged onto integration `5eda1db`, giving `39d21f7`.
- All runs used a clean `.[dev]` venv.
- **No-peek:** from the calibration runs I read only the two saved `reachability.json` tables and the gate lines.

## Verdict: **ADOPT (c)**, with three SHOULDs, one of them a pre-data statement for the coordinator

- "≥ 1 control eats" is faithful to MUST 1 and removes the K3 bias. The lifts reproduce exactly.
- The only thing the code changes at the 18 points is the admission rule, and W1 is untouched.
- Every mutant of the rule itself dies.

**What I would change is the diagnosis's wording, not the rule.**
- The "binomial, therefore no unreachable draws" and "6 of 16 never eat" claims are stronger than the counts allow.
- The table should record *which* controls ate, so the calibration can answer the (c) question directly.

## 1. Is "≥ 1" faithful to MUST 1? Does it admit draws that are unreachable for steering?

**What MUST 1 said** (`ADVERSARY.md` §1.1): "Drop or replace draws on which **the positive control eats 0** intact."
- The positive control there was a single strong two-nose steerer (steer2). The worry (M2) was "hopeless layouts"
  where no steering body can reach a patch in 15 s.
- The registration's "at least half of the hosts" was a generalisation to many controls, and was never argued for.
- "≥ 1 of the controls eats" is the direct generalisation of "the positive control eats > 0". **(c) is the faithful
  reading.**

**Does it admit steering-unreachable draws?**
- A draw passes if any one control eats, and a control's eating can be blind luck. Its eating is not evidence that it
  steered: RBT-19's and O1's (a) plants have weak ΔT (FIX-CHECK-RBT132 §4).
- But **"at least half" does not fix that either.** It too counts eating, not steering. With exchangeable draws it
  only counts luck.
- The screen's job is to remove draws on which *no* body at this rung reaches food. At the two cells that set is
  **empty** (0 of 96 draws have no eater, `rbt132_478_screen_check.txt`). There, (c) admits every draw, and the
  battery is the first 36 pool draws: the screen is honestly a no-op.
- **Clutter could differ.** At the cluttered points (c1 and c2, including two pilot points), boxed-in starts could
  exist. There (c) still drops exactly the draws no control reaches, which is MUST 1's criterion.
- **I see no rule that is stricter than (c) and still unbiased while the screen's hosts are K3's own plants** (§2).
  If a stricter screen is ever wanted, the principled route is **screen hosts disjoint from K3's plants.** It is not
  needed now; noted as an option.

## 2. The K3-bias argument: verified

**The mechanism.**
- Screen seasons and the call's intact seasons are the same deterministic seasons: the same host, `cfg`, draw and
  season function.
- A rule that selects draws on the plants' intact eating therefore selects the plants' own good seasons, and
  members are not screened.

**The lifts, recomputed from the saved tables** (`rbt132_478_screen_check.txt`):

| cell | ≥ ½ admits | a control's P(ate \| admitted) vs P(ate) | lift under ≥ ½ | lift under ≥ 1 |
|---|---|---|---|---|
| PW | 5 / 96 | 0.550 vs 0.293 | **×1.877** | ×1.000 |
| HP | 14 / 96 | 0.518 vs 0.366 | **×1.415** | ×1.000 |

- ×1.88 and ×1.42 are exact.
- **≥ 1's ×1.00 holds because it admits all 96 draws here, so there is no selection.** At a point where it drops draws
  (clutter), it selects too, but only against the rare all-zero draws. The fixture's ×1.07 at 45 of 48 shows the size.
- **One precision.** The lift is on *intact eating*. K3's SEEN runs on ΔT (c2) and the veto (c3), not on eating, so
  the bias reaches K3 through the correlation between eating and T. Its direction (K3 optimistic relative to members)
  is right; its size on SEEN is not the ×1.4–1.9. That doesn't change the case for (c).

## 3. The binomial diagnosis, and the (c) plants that never eat

**What the counts can and cannot say.** A per-draw count of how many of 16 controls ate cannot separate two things:
- **host heterogeneity** (some controls rarely eat), which *lowers* the variance below a binomial;
- **draw heterogeneity** (some draws are harder), which *raises* it.

A variance ratio near 1 can hide both at once. So:

| claim in GATE_DIAG | what the tables support |
|---|---|
| "no unreachable draws" | **yes, directly:** 0 of 96 draws have no eater at either cell. **Not** because the counts are binomial |
| "the draws are exchangeable (no over-dispersion)" | **not identifiable.** PW's variance (3.84) is **above** even a homogeneous binomial (3.31). With any never-eaters (which lower it), PW then needs *draw* heterogeneity to reach 3.84. HP's is below (2.34 vs 3.71) |
| "about 6 of 16 controls never eat" | **HP only:** 6 never-eaters with the others at q ≈ 0.585 imply a variance of 2.43, close to 2.34. **PW does not support it:** 0 never-eaters already gives 3.31 < 3.84, and 6 would give 2.49. The fixture's 6 of 6 G8(c) plants at 0.00 are RBT-19 bodies, not O1's |

**What it means for K3's (c) share.**
- If O1's G8(c) plants rarely move toward food, K3's "≥ 1 of each kind" can fail on (c) at any count.
- My fixture measurement (FIX-CHECK-RBT132 §4) had (c) SEEN at 0 of 16. The calibration will now measure it, since it
  is reachable under (c).
- **The carrying share of 8 of 63 (12.7%)** agrees with the fixture's 20 of 120 (17%). Holistic PAYS and K3's (c) half
  rest on a body-selected minority, as ruled (S4, #459).

**Pre-data, the rule should say two things now,** before the re-run's SEEN lines exist:
1. **(S-1, code) Record which controls ate.**
   - Add a per-host field to the screen table: each draw's `ate_by_host`, a list of 0/1 in host order, with the host
     names in the planted log.
   - This reads controls only, so it is no-peek-safe. It turns "6 never eat" from a moment fit into a direct count per
     plant.
   - `screen_dispersion` can then report per-host P(eat), so a (c) plant that never eats is visible *before* its K3
     line.
2. **(S-2, the coordinator's pre-data statement) Say now how a (c)-driven failure reads.** If the calibration's K3 or
   its projection fails on the (c) kind, that is read, as registered, as:
   - "the perception layer is unreadable at a = 6: no holistic control is seeable" (RBT-129 §6.3);
   - **not** a reason to change G8(c)'s layout, its hosts, `c_layout` or the carrying rule after seeing the
     calibration.
   - Any change to G8(c) after the calibration output exists is data-driven. Fixing this now closes that door.

## 4. The identity proof: confirmed, and checked with the rule ON

- **Their `rbt132_battery_identity.py`** sets `SCREEN_ANY` aside, compares, and reproduces on the trial merge.
- **I checked with the rule left on** (`rbt132_478_rule_identity.py/.txt`): `screen_draws` at `914667e` against the
  trial merge, with stub seasons (no simulation) at eat rates of 0.05, 0.3 and 0.6.
  - At all 18 points, every table row agrees on every key but `admissible`.
  - The old flag is exactly 2·ate ≥ hosts and the new one exactly ate ≥ 1.
  - The battery is the first 36 newly admitted draws in pool order.
  - At W1 the screen is identical with the rule on.
- **W1 on the trial merge:**
  - `rbt132_w1_identity.py ce69f17` reproduces;
  - `power_tau1.txt` is byte-identical;
  - the kill-sets reproduce (16/16 and 24/24);
  - the RBT-116 tests and `power.py` have no diff;
  - `screen_draws(W1)`, `_job` and the CLI are identical.
- **Full suite: 772 passed, 1 skipped** (`rbt132_478_w1_suite.txt`).

**On W1's own gate.** GATE_DIAG says W1's registered rule admits 3 of 48 in W1's block, with RBT-19 controls. It is
also right that the "77%" I quoted in FIX-CHECK-476 came from **my** W1-shaped test fixture
(`rbt132_w1_identity_extra.py`: 49 of 64, 3 s seasons, a denser fixture), not W1's block. I withdraw that number. W1's
gate uses its own G8 hosts, so the 3 of 48 is indicative, not a measurement. The same amendment is RBT-116's to
consider before W1's gate runs.

## 5. Tests and mutants (`rbt132_478_mutants.py/.txt`, on the trial merge)

**6 of 10 killed.** Every mutant of the **rule** dies:
- W1 added to `SCREEN_ANY`;
- `SCREEN_ANY` emptied;
- ≥ 2 instead of ≥ 1;
- > ½ instead of ≥ ½ at W1;
- the screen row ignoring the point;
- `any` counting zeros.

**The 4 survivors are all in the diagnostic print, not the decision:**

| survivor | fix |
|---|---|
| `dispersion-ddof0` (variance with ddof 0) | NIT: assert the ratio on a small known table exactly |
| `dispersion-half-strict` (">= half would admit" counts > ½) | NIT: a table with ate = hosts/2 |
| `screen-line-wrong-rule-label` (the log names "≥ half" at an RBT-129 point) | NIT: assert the label at an RBT-129 point and at W1 |
| `pays-screen-line-dropped` (`pays` stops printing the line) | NIT: assert it in `pays.txt` |

(S-3 bundles these four.)

## 6. Base and merge order

- **#478 is stacked on #476.** Its base is `9c0c06c`, #476's head: it contains both of #476's commits, and does not
  contain integration `5eda1db`.
- **#476 has an open FIX** (#479): two test gaps.
- **Merge order:**
  1. land #479's two tests on #476, and merge #476;
  2. merge integration into #478, which is a merge commit and should be conflict-free (I trial-merged cleanly);
  3. merge #478.
- **Do not merge #478 first:** it would bring #476 in without its fixes.
- The §12 amendment for (c), and the re-run of `planted` at both cells, follow #478's merge.

## Findings

- **SHOULD S-1.** Record `ate_by_host` in the screen table, and print each host's P(eat) in `screen_line`. It is
  controls-only and no-peek-safe.
- **SHOULD S-2.** Coordinator: state pre-data that a (c)-driven K3 or projection failure reads as "unreadable at
  a = 6: no seeable holistic control", with no post-hoc change to G8(c).
- **SHOULD S-3.** GATE_DIAG's wording:
  - "no unreachable draws" rests on 0 of 96 draws with no eater, **not** on binomiality;
  - the counts cannot separate host from draw heterogeneity;
  - "6 of 16 never eat" is HP's moment fit only (PW is over-dispersed).
  - Also add the 4 diagnostic-print tests (§5).
- **NIT.** A screen with hosts disjoint from K3's plants is the route to any stricter-than-(c) screen, if one is ever
  wanted.

## Files

In `runs/RBT-116/design-adversary/`:

| file | what |
|---|---|
| `rbt132_478_screen_check.txt` | the lifts and the variance bounds, from the saved tables |
| `rbt132_478_rule_identity.py/.txt` | the 18 points and W1 with the rule on |
| `rbt132_478_mutants.py/.txt` | 10 mutants of the rule and the print |
| `rbt132_478_w1_suite.txt` | the suite and W1 checks on the trial merge |
