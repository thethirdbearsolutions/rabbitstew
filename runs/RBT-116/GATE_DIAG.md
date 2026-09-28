# RBT-132: why the K3 calibration's reachability screen failed, and a proposed fix

*2026-09-28, the RBT-132 implementer, pre-data. **Ruled: ADOPT (c)** (the coordinator on #478, comment 5874231890,
after gate check #482). The wording below was corrected per that ruling's S-3.*

**What was read and run:**
- **Read:** the two failed runs' `reachability.json` and gate lines only, from `ckpt/rbt-129-calibration-<cell>`, as
  the coordinator cleared. No SEEN verdict, ΔT, call, K3 or tuning line existed or was read.
- **Run:** a screen-only experiment in W1's block, on fixture draws, with committed RBT-19 P-801 bodies planted as
  `planters.py` plants them. Nothing ran on an RBT-129 cell, pool, host or arm.
- **Output:** `gate_diag.py` → `gate_diag.txt`.

## Verdict: **(c)**, a per-point screen rule that is MUST 1's own intent: admit a draw if **at least one** control eats

At the calibration cells, the registered rule ("at least half the controls eat ≥ 1 item") does not measure the draw.
It measures how many controls happen to eat in a 15 s season.
- **It passes 5–15% of draws by chance,** so the gate fails.
- **Screening harder (a) would bias K3:** the admitted draws are the ones where K3's own plants happened to eat.
- **A longer bout (b) does not fix it,** because some controls never eat at any length.

"At least one control eats" keeps the screen's job: it drops only draws no control reaches. It costs nothing extra,
and leaves W1 as registered.

## 1. Why so few draws are admissible

**No draw is unreachable, and "at least half" rejects most of them anyway.**

| | PW (saved) | HP (saved) |
|---|---|---|
| P(a control eats ≥ 1 in a 15 s season) | 0.293 | 0.366 |
| eat-count variance ÷ binomial variance (over-dispersion p) | 1.16 (0.14) | 0.63 (1.00) |
| draws on which **no** control eats | 0 of 96 | 0 of 96 |
| admissible, ≥ half (binomial expects) | 5 (7%) | 14 (19%) |

- **Terrain seeds do nothing here.** Both cells have flat terrain (`terrain_seed` None), so a draw differs only in its
  start pose and food layout (both from the start seed).
- **Every draw is reached by at least one control: 0 of 96 draws have no eater at either cell.** That, and only that,
  is the evidence that no draw is unreachable. The binomial fit is not.
- **The counts cannot separate host heterogeneity from draw heterogeneity.** A per-draw count sums over the controls,
  so a fit to a binomial (or its failure) cannot say whether it is the hosts or the draws that differ. #478's per-control
  record (`ate_by_host`, S-1) makes that visible from now on.
- **"At least half" admits only the upper tail of the counts** (mean ≈ 0.3 × 16): 5% and 15% of draws.
- **HP's counts are under-dispersed** (ratio 0.63). A moment fit to Binomial(m, r) gives r ≈ 0.60 on m ≈ 10 hosts,
  which would fit about 6 of the 16 controls rarely or never eating. **That is HP's moment fit only.** PW's counts are
  over-dispersed (ratio 1.16, p = 0.14), so no such fit exists there, and neither cell shows which controls ate.

**The fixture experiment** (`gate_diag.txt` Part 2) shows the same, and what dominates:

| W1 block | per-control P(eat ≥ 1): 6 G8(a), 6 G8(c) | admissible, ≥ half | admissible, ≥ 1 |
|---|---|---|---|
| random terrain, 15 s | a: 0.21–0.69; **c: 0.00 ×6** | 3 of 48 (6%) | 45 of 48 (94%) |
| random, 30 s | a: 0.40–0.75; c: 0.00 ×6 | 8 (17%) | 46 (96%) |
| random, 45 s | a: 0.50–0.79; c: 0.00 ×6 | 12 (25%) | 48 (100%) |
| flat, 15 s | a: 0.27–0.96; c: 0.00 ×6 | 6 (12%) | 48 (100%) |
| flat, 30 s | a: 0.44–1.00; c: 0.00 ×6 | 12 (25%) | 48 (100%) |

**Which factor dominates: the controls, not the bout, the start or the terrain.**
- **Half the controls cannot eat at all.** These are the G8(c) plants on these holistic bodies. So "≥ half" needs
  nearly every G8(a) plant to eat on the same draw.
- **Doubling or tripling the bout** raises the G8(a) plants' rates, but the admitted share only reaches 25%.
- **Flat terrain beats random,** but only modestly.
- **Start pose and layout** matter less than which controls are present (per-control rates, which this experiment
  records, differ far more than the admitted shares across conditions).
- **Caveat:** these are RBT-19 bodies, not RBT-113 O1's. The O1 controls' rates are not known here; HP's moment fit is
  consistent with the same picture but cannot show it.

**W1 itself is exposed.** W1 is PW's layout at 15 s (RBT-116 §4.1), and its own gate has not run. The 77% quoted
earlier came from a denser W1-*shaped* test fixture, not from W1. In W1's own block, the registered rule admitted
3 of 48 draws here. This is RBT-116's registration to amend, not RBT-132's, so I flag it rather than change it.

## 2. Is "≥ ½ of the controls eat" the right test in patchy worlds?

**No. It is W1-fixture-specific, and it is not what MUST 1 asked for.**
- **What MUST 1 asked for** (`design-adversary/ADVERSARY.md`, MUST 1): "drop or replace draws on which the positive
  control eats 0 intact." That is reachability: can a steering body reach food from this start, in this layout?
- **What "≥ ½ of 16" measures instead:** where the controls eat on about 30% of seasons, it mostly measures how many of
  them happened to eat on that draw, whatever reachability the draw has.
- **It also biases K3.** The screen's hosts are the (a) and (c) plants that K3 then calls on the same draws, and
  seasons are deterministic. So the admitted draws carry the plants' own lucky intact seasons:

| | registered ≥ ½: a control's P(ate \| admitted) ÷ P(ate) | ≥ 1 |
|---|---|---|
| PW (saved) | **×1.88** | ×1.00 |
| HP (saved) | **×1.42** | ×1.00 |
| W1 block, random 15 s (fixture) | ×2.23 | ×1.07 |

  Members are not screened, so K3's plants would be read on draws better for them than for the members. That weakens
  K3 as the member-level guard (#471's ruling) exactly where it is tight.

## 3. The options, with cost

The costs use 0.36 core-s per 15 s season. The probe leg's base is `k3_projection.probe_cost`: about 15.5 core-h at 16
draws, 29.8 at 32, and 58.4 at 64.

| option | calibration cells (both) | probe leg | fixes the gate? | K3 bias |
|---|---|---|---|---|
| **(a)** screen under ≥ ½ until 4 + 2n are admitted, with a cap | PW 691 draws × 16 = 11,000 seasons (1.1 core-h); HP 3,950 (0.4) at n = 16. At n = 64: PW 4.1 and HP 1.5 core-h | about +1 core-h per probed point at PW-like shares (4 points) | yes, if the cap allows | **×1.4–1.9 lift on the plants' intact eating** |
| **(b)** a longer bout at sweep points (W1 unchanged) | ×2–3 on every season | 31 core-h (30 s) to 47 (45 s) at n = 16 | **no:** 17–25% admitted at 30–45 s, because the non-eating controls stay at 0 | reduced, not removed |
| **(c)** ≥ 1 control eats, at RBT-129's points | 0 extra: the screen tables already exist; re-run `planted` at both cells (about 0.6 core-h each) | 0 extra (15.5 core-h at n = 16) | **yes:** 96 of 96 at both cells | **none** (×1.00) |
| **(d)** perception unreadable at these layouts | 0 | 0 | — | — |

- **(b) also changes the question.** Members evolved on 15 s seasons. Probing them at 30–45 s measures perception in a
  regime they were not selected in, and F_MIN and the power were fixed for 15 s.
- **(d) is premature.** The gate has not failed on perception; it has failed on a screen rule that the data show does
  not measure reachability here.

## 4. The proposal: (c), as registered code

In `steer.py`, W1's code path is unchanged:
- **`SCREEN_ANY = frozenset(RBT129_POINTS)`**, and **`admissible(ate, hosts, world)`**: a point in `SCREEN_ANY` admits
  a draw when `ate ≥ 1`; every other point (W1) keeps `2 × ate ≥ hosts`.
- **The rest of the screen is unchanged:** the pool, pool order, extend once then fail, and #476's per-point
  `battery_size`.
- **`screen_dispersion(table)`** and `planters.screen_line`: `planted` and `pays` now print, **before** the gate's
  verdict, the admitted share, P(a control eats), the variance ratio against a binomial, and what each rule would
  admit. A future failure then shows its cause in the log.

**Proof and tests:**
- `rbt132_battery_identity.txt` still finds W1 (against `ce69f17`) and the 18 points (against `914667e`) IDENTICAL:
  the pool, the battery, and the screen with the rule set aside. The only change at the 18 points is the rule itself.
- `tests/test_rbt132.py` covers the rule per point (W1 keeps ≥ ½), a screen at an RBT-129 point that one control
  reaches, the dispersion statistic, and the `planted` log line.

**What (c) does not solve,** which is for the coordinator:
- K3 needs ≥ 1 SEEN plant of each kind. If some of the O1 G8(c) plants never eat, as they don't on the fixture bodies
  and as HP's dispersion suggests, K3's (c) share will be low whatever the screen does.
- The calibration measures exactly this. It is now reachable, and the #471 rule (projection, then the second stage)
  applies to it.
- The carrying share is also thin: (c) 8 of 63, as the failed runs' own carrying line printed.

**If ruled:**
1. The RBT-129 designer records (c) as a dated §12 amendment.
2. The calibration lane re-runs `planted` at both cells, and nothing else changes.
3. W1's own gate should get the same amendment, which is RBT-116's to make, before W1's gate runs.

---
*Files: `gate_diag.py/.txt`; `steer.py` (`SCREEN_ANY`, `admissible`, `screen_dispersion`); `planters.py`
(`screen_line`); tests in `tests/test_rbt132.py`.*
