# RBT-106 P1 readout adversary (PR #342, `results/RBT-106-P1-readout` at `cdd8d3c`)

*Readout adversary, 2026-09-27. Target: `P1-READOUT.md`, `P1-readout.txt`, `P1-sensitivity.txt`, `f12.py`/`f12.txt`,
`readout.py`'s diff and the `S1-SEED/` reads, against `PREREGISTRATION.md` §6.1–6.4 and §10 (which governs).
NO-PEEK held: no HU-* or HP-* file was opened, printed or computed from. `readout.py` was run only as
`--pairs H,P --no-peek H`, with every file access traced (item 5).*

## Overall verdict: **CONFIRMED-WITH-CAVEATS**

- **VERDICT P: P-NULL is right.** I re-derived it with my own code (no scipy, and no import of `readout.py` or
  `function.py`) from the committed per-body tables:
  - on the 7 usable pairs;
  - on all ten pairs;
  - with any one of the three unusable pairs added back.
- **Every per-arm call re-derives:** 60 function files, 0 mismatches.
- **The S1 side, F12 and the `--no-peek` diff all reproduce** on the arms I re-ran from checkpoint.
- **One MUST-FIX, on the report's wording only.** The absent-verdict power it quotes is the **n = 10** figure.
  At the usable **n = 7**, P-NULL misses "the prize alone suffices" with probability:
  - **0.22** at q = 0.5, not 0.07;
  - **0.58** at q = 0.25, not 0.37.
- **Fix before merge:** the report and the ticket post must restate P-NULL's reach with the n = 7 figures. The
  verdict and every other number stand.

| # | finding | class |
|---|---|---|
| A1 | Power quoted at n = 10, not the usable n = 7: the miss rates are 0.22 / 0.58, not 0.07 / 0.37 | **MUST-FIX** (wording) |
| A2 | The report suggests saturated bodies explain P1-801's failed control; per body they do not | CAVEAT (wording) |
| A3 | F12's thresholds were set post hoc, and "fixed before any arm was read" cannot be checked from git | CAVEAT (immaterial: far from both thresholds) |
| A4 | The zero-count veto calls 19 of 20 patchy-scored lines; the one COMPASS line is dropped with its twin | CAVEAT (reported correctly; context for the reader) |
| A5 | Usability rule, the three failures, the VOID floor, the verdict arithmetic | NONE |
| A6 | S1 side: SAME RUN, byte-identical tables, same world and harness | NONE |
| A7 | `readout.py --no-peek H` cannot touch a P number | NONE |
| A8 | Predictions P-0, SE-1..3, P-1, P-2 | NONE (all held); one wording nit on SE-2 |
| A9 | S1-1's install control is over 6 bodies (g500's sign UNDETERMINED) | NONE (function.py's own rule, RBT-104's file) |

---

## 1. Usability (A5, A2, A3, A9)

**The rule is the registered one, applied identically.** Usable (§6.2 as amended by §10.1) means all of:
- viable: reached 599, never extinct, ≥ 30 designed alive on average in 300–599;
- x86_64;
- analyse.py's control passed;
- the install control (`function.py --install 32` on the arm's own bests, own world) reads FOOD-DEPENDENT;
- `rabbitstew/` is c872e80's tree.

`recompute.py` checks each input independently of `readout.py`:
- It parses `seasons.txt`.
- It resolves each recorded launch commit's `rabbitstew` tree with `git rev-parse` rather than trusting `commit.txt`.
  All 20 give `9cc84cde…`, which is `c872e80:rabbitstew`.
- It re-classifies the install control from the per-body table with function.py's rule: t over bodies, lo > 0, and
  zeros ≤ half the bouts.

The result is 17 usable arms. The same three are unusable, each for the install control alone.

**Each failure is "not food-dependent" on interval, a reason the registration names** (§6.1: "must read
FOOD-DEPENDENT"). None fails on the zero-count veto, and none on any other criterion:

| arm | control F [95%] | zeros / bouts (veto at > 224) | world |
|---|---|---|---|
| P1-801 | +1.263 [−0.335, +2.862] | 201 / 448 | patchy (own) |
| P1-7 | +1.098 [−0.336, +2.532] | 210 / 448 | patchy (own) |
| S1-805 | +0.306 [−0.067, +0.678] | 154 / 448 | uniform (own; RBT-104's file) |

- "Identically" here means the registered rule: each arm's control runs in its own world. S1's controls are
  therefore scored in the uniform world, where the installed compass pays about 2.5× less. That is what §6.1
  says, not a deviation.
- The pass rates are S1 9/10 and P1 8/10.

**F12, re-run** (`spot/f12-rerun.txt`). I ran the committed `f12.py` from a worktree with `rabbitstew/` at
c872e80 (`git diff c872e80 HEAD -- rabbitstew` empty), on each arm restored from its checkpoint:
- **P1-801 and P1-7**, the two P1 failures;
- **S1-805**, the S1 failure;
- **P1-805**, the one COMPASS line.

Every per-body row matches `f12.txt` **byte for byte** on all four arms: planted-type units, b, v, resting drive,
median |x_host|, sat and T. Summary:
- median T is 0.390, 0.406, 0.443 and 0.429;
- at most 1 of 7 bests has a planted-type unit driving > 1;
- **no arm is masked by construction.**

**A2 (CAVEAT, wording).** The report says the failed P1 controls have "some of their bests at high Effector
saturation (for example P1-801 g450: sat 0.975, T 0.04)". The juxtaposition invites the reading that saturation is
part of why the interval is wide. Per body, it is not. Pairing each best's control F with its F12 T:

| P1-801 | g300 | g350 | g400 | g450 | g500 | g550 | g590 |
|---|---|---|---|---|---|---|---|
| control F | +5.00 | +1.44 | +1.25 | +0.14 | +0.19 | +0.59 | +0.23 |
| T (F12) | 0.57 | 0.22 | 0.17 | 0.04 | 0.39 | 0.57 | 0.54 |

- **P1-801:** two of the three saturated bests (g350, g400) have the 2nd and 3rd highest control F. The wide
  interval comes from one very large body (g300, +5.0) beside several small ones, most of them unsaturated.
- **P1-7:** it has no best with sat > 0.71, and its negative bodies (g450 −0.22, g500 −0.13) sit at T 0.52 and 0.37.

So both are plain heterogeneity failures of the interval. This supports the report's conclusion ("not by
construction") more strongly than its own wording does. **Suggested wording:** "the failures are interval failures
from heterogeneous bodies; they do not track F12's saturation."

**A3 (CAVEAT).** `f12.py` calls itself POST HOC, with its flag "fixed here before reading any arm". The P1 arms'
`function-pc.txt` files were public on integration before 90fd963, so git cannot verify that claim. It does not
matter here:
- the thresholds come from RBT-104's reference (the ×8 hosts' T 0.04–0.08 → 0.10) and §5.1's bias gate;
- every arm sits far from both: the lowest median T is 0.35 against 0.10, and the most driven bests are 2/7
  against 4.

**The VOID floor (A5).** §6.2 reads "VOID if fewer than 7 paired seeds are usable", and `readout.py` has
`MIN_USABLE = 7` with `len(use) < MIN_USABLE`. 7 of 10 is not fewer than 7, so the verdict is scored. There is no
rounding: the count is an integer, re-derived by my code from the inputs above.

**Sensitivity on all ten** (`recompute.txt`) reproduces `P1-sensitivity.txt`:
- COMPASS lines: S1 0, P1 1 (805);
- paired F +0.254 [−0.205, +0.714], t(9);
- **P-NULL.**

Adding back any single unusable pair (n = 8) also reads P-NULL:
- 801: +0.081 [−0.174, +0.336];
- 805: +0.282 [−0.321, +0.884];
- 7: +0.040 [−0.204, +0.284].

P-EVOLVED needs ≥ 3 COMPASS lines. There is at most one under any usability choice, so **no usability decision can
move this verdict.**

**A9 (NONE).** S1-1's install control is over 6 bodies. g500's travel sign is UNDETERMINED, and function.py drops
such a body. The file is RBT-104's, copied byte-identical. It passes at t(5): +0.966 [+0.573, +1.360].

## 2. The verdict arithmetic (A4, A5)

`recompute.py` reads only the per-body tables (intact, decoy, lesion per best) and the zero counts. It then
re-derives the calls with its own Student-t, which uses the incomplete beta and checks t.975(6) = 2.44691 and
t.975(9) = 2.26216:
- the primary call (F = intact − decoy, t over bodies, with the RBT-38 zero-count veto);
- the attribution: gain = intact − lesion; decoy = decoy − lesion; "no compass gain" unless gain's lo > 0;
  FOOD-DEPENDENT iff the decoy share is < 0.25 and gain − decoy excludes zero;
- the COMPASS call: primary FD **and** attribution FD (§10.4).

**All 60 files' calls and bodies agree with the committed LINE lines,** and the F intervals agree to rounding
(≤ 0.001, from the 3-decimal per-body table).

| quantity (usable n = 7) | mine | report |
|---|---|---|
| COMPASS lines S1 / P1 | 0 / 0 | 0 / 0 |
| primary-only FD S1 / P1 | 0 / 0 | 0 / 0 |
| paired F(P1) − F(S1), patchy, t(6) | +0.049 [−0.242, +0.339] | +0.049 [−0.242, +0.340] |
| uniform-scored | −0.068 [−0.150, +0.014] | same |
| lesion gain S1 / P1 | +0.113 [−0.079, +0.305] / −0.020 [−0.055, +0.014] | same (P1 hi +0.015) |
| HELD S1 / P1; log-excess | 1 / 0; −1.559 [−2.983, −0.136] | same |

- **The thresholds match §6.2 and §10:**
  - P-EVOLVED needs COMPASS ≥ 3 and the interval above 0;
  - P-NULL needs COMPASS ≤ 1 and the interval not above 0;
  - otherwise NOT DECIDED; VOID below 7.
- **P-NULL's two conditions both hold with room:** 0 ≤ 1, and the interval's lower bound is −0.242.
- **t(6), not the registered "t(9)":** §6.2's t(9) is written for n = 10, and power.py uses t(n − 1).
  t(n − 1) is the only coherent reading.

**A4 (CAVEAT, context).** In the patchy scoring, the zero-count veto decides 19 of 20 lines' primary call. Every
S1 and P1 line is VETOED except P1-805:
- in more than half the paired bouts, real and rotated smell give *identical* intake;
- so "0 COMPASS lines" is mostly "smell does not change behaviour", which is a stronger null than "an interval
  straddling zero".

It is registered and correctly applied. The one exception, P1-805 (the only COMPASS line in 20 arms), leaves the
rules because its *uniform twin's* control failed (S1-805). This is the pair rule working as written, and the
report flags it. The adversary's single-case look (as asked):
- **for P1-805:**
  - 4 of 7 bodies have a large F (+2.3 to +4.4), the other three are near zero, and the decoy share is 12.6%;
  - HELD reads AT OR BELOW NO-SELECTION at both seasons (k_planted 23 then 2);
  - X is 468;
- **against it:** it does not score in the uniform world (+0.529 [−0.002, +1.060]).

One such line in ten is what P-NULL allows (≤ 1). It is worth a sentence in the H/next-step discussion, not a
change here.

## 3. The absent-verdict power (A1: MUST-FIX)

**What the report quotes.** "P-NULL's power against 'the prize alone suffices' … misses with probability **0.07**
if q = 0.5 and **0.37** if q = 0.25", and "under 'both needed' P-NULL fires with probability 0.72, or 0.89".

**Where the figures come from.** They are the design adversary's `power_adv.txt` part B, the §10.5 / F8
measured-bare-line model. **That table is at n = 10 only.** The readout has **n = 7** usable pairs. The
pre-registration's own §6.3 table prints the n = 7 figure in brackets (0.18 at q = 0.5, first model), so the n = 7
question was registered.

**Recomputed at n = 7** (`power_n7.py` → `power_n7.txt`):
- `power_n7.py` is the adversary's `factorial_b`, ported line for line with a scipy-free t quantile.
- **The port check:** it reproduces part B's four n = 10 rows exactly (0.892 / 0.067 / 0.373 / 0.892).

| truth | model | P-NULL fires, n = 10 (quoted) | **n = 7 (usable)** | P-EVOLVED, n = 7 |
|---|---|---|---|---|
| the prize alone suffices, q = 0.5 | measured bare lines (§10.5) | 0.067 | **0.215** | 0.274 |
| the prize suffices, weakly, q = 0.25 | measured bare lines | 0.373 | **0.579** | 0.037 |
| the prize alone suffices, q = 0.5 | designer's first model | 0.050 | 0.176 | 0.267 |
| the prize suffices, weakly, q = 0.25 | designer's first model | 0.267 | 0.472 | 0.042 |
| nothing holds / both needed | measured / first | 0.892 / 0.718 | **0.932 / 0.828** | 0.000 / 0.001 |

The miss rate across q at n = 7 (measured model) is:

| q | 0.25 | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 |
|---|---|---|---|---|---|---|
| P-NULL misses "the prize suffices" | 0.58 | 0.34 | 0.22 | 0.12 | 0.05 | 0.02 |

**What the n = 7 figures support.** They support only this: *P-NULL is fair evidence against the 2.5× prize alone
making a compass in most populations (q ≥ 0.6: miss ≤ 0.12). At q = 0.5 it would still read P-NULL about one time
in five, and at q = 0.25 more often than not.* The quoted 0.07 would license "fair evidence against the prize alone
at q = 0.5", which at n = 7 it is not.

**MUST-FIX.** Change the four places in `P1-READOUT.md` (the plain-words bullets) and the ticket post that quote
the figures, as follows. The EVOLVED-power caveat (upper bounds under the §10.4 attribution rule) stays as written.
- "0.07 … 0.37" becomes "**0.22 (q = 0.5) and 0.58 (q = 0.25) at the usable n = 7** (0.07 and 0.37 at n = 10)".
- "0.72, or 0.89" becomes "**0.83, or 0.93 at n = 7**".

## 4. The S1 side (A6: NONE)

**Spot-check: S1-805**, the S1 failure and the twin of the one COMPASS line.
- **Restore:** `ckpt/rbt-104-S1-805` restored at 600/600.
- **Founders:** regenerated with `founders.py 805 1`. The sha256 of its SHA256SUMS is `c4292175…`, equal to
  RBT-104's `founders-digests.txt` entry.
- **Cross-ticket, re-run** (`spot/cross-ticket-S1-805.txt`): RBT-106's S1 command, run for 20 seasons at c872e80
  and compared by the adversary's `cross_ticket.py`:
  - `seasons.txt` is BYTE-IDENTICAL over 40 rows;
  - `lineage.jsonl` is IDENTICAL over 2,285 records;
  - the verdict is **SAME RUN (prefix)**.
- **Regenerated tables:** `measure.summarise` on a copy of the restored run, with its tables deleted first. The
  regenerated `seasons.txt` and `lineage-last.txt` have the same sha256 as:
  - RBT-106's `S1-805/` copies;
  - RBT-104's committed `S1-805/` files;
  - the checkpoint's own copies.
- **Patchy scoring, re-run** (`spot/S1-805-function-patchy-rerun.txt`): `cross_world.py --world
  runs/RBT-106/world-patchy` on the restored run is identical to the committed `function-patchy.txt` from the
  per-body table to the LINE, in every digit.

**All ten S1 seeds.**
- `platform.txt`, `rbt102.txt`, `function-pc.txt`, `seasons.txt` and `lineage-last.txt` are `cmp`-identical to
  RBT-104's.
- `function-uniform.txt` is `cmp`-identical to RBT-104's `function.txt`.
- All ten `cross-ticket.txt` read SAME RUN.

**The same harness and world.**
- S1's patchy scoring is `cross_world.py`: RBT-104's `function.py` imported unchanged, with only
  `routed_populations.config` replaced by `world-patchy/config.json`'s `sim`.
- That `sim` block is **equal, key for key, to P1-801's and P1-805's own configs**, including `terrain_seed: null`
  and `food.patches 3`.
- S1-805's own config differs from them only in `food.patches` (0).
- The bodies, the 64 seeds from 7000, the decoy, the lesion and the rules are function.py's in both. So P1 is
  scored by `function.py` in its own world, and S1 by the same code in a world that is P1's.

**One more re-run: P1-7's install control** (`spot/P1-7-function-pc-rerun.txt`). Re-run from checkpoint, it is
identical to the committed file: not food-dependent, +1.098 [−0.336, +2.532].

## 5. `readout.py --no-peek H` (A7: NONE)

**Reading the diff** (011cb79 → cdd8d3c; integration's `readout.py` has not moved since 011cb79). It adds three
things:
- **The `--no-peek` argument:** in `main()`, a listed pair prints NOT READ and `continue`s *before* `pair()` is
  called, so no H path is formed.
- **A per-arm usability print:** it reads the `rows` already computed and assigns nothing.
- **`predictions_p()`:** it is called after the verdict string is final, and it only prints.

No threshold, rule or input changed.

**Executed** (`nopeek_check.py` → `nopeek_check.txt`, in a scratch venv with scipy, which `readout.py`'s t needs).
It wraps `open`, `os.path.exists`, `os.listdir` and `os.scandir` to refuse and record any HU-/HP- path:
- **(a)** `readout.py --pairs H,P --no-peek H` reproduces `P1-readout.txt` **byte for byte**.
- **(b)** It touched 405 paths, all in `S1-*`, `P1-*` or `runs/RBT-106/` itself, and **no HU-/HP- path**.
- **(c)** The pre-change `readout.py` (011cb79), loaded as a module and asked for `pair("P")` alone, prints a P
  section identical to the new one once the two added print blocks are removed.

So the diff cannot change a P number.

A cosmetic nit, not a finding: the NOT READ text says "its arms are not all merged", which is a reason the flag
does not check.

## 6. The predictions (A8: NONE)

I re-scored each against its registered wording (§4, §6.4, §10.2):

| # | registered wording | mine | report |
|---|---|---|---|
| P-0 | primary verdict P-NULL (0.72) | P-NULL | held |
| SE-1 | no P1 arm extinct, 10/10 viable (≥ 30 alive) | 10/10 | held |
| SE-2 | P1 − S1 window income, t interval above zero | n = 7: +0.384 [+0.297, +0.471]; n = 10: +0.391 [+0.320, +0.462] | held |
| SE-3 | more designed births on ≥ 8/10 and a deeper window on ≥ 8/10 | births 10/10; depth 8/10 (not deeper: 806 15.3 → 14.9, 3 16.7 → 14.4) | held |
| P-1 | #HELD(P1) − #HELD(S1) ≤ 1 | 0 − 1 = −1 (all ten too) | held |
| P-2 | P1's X below 250/1,000 on ≥ 8 of 10 | 8/10 (805 468, 3 283 over) | held |

**Nit:** `readout.py` labels SE-2 "(paired over usable seeds, as registered)". §4 does not name the seed set. It
holds on both, so nothing turns on it, but "as registered" should read "over usable seeds".

## Files

| file | what |
|---|---|
| `ADVERSARY.md` | this |
| `recompute.py` → `recompute.txt` | the P pair re-derived from the per-body tables; usability; verdict at n = 7, n = 10 and n = 8 ± one pair; predictions |
| `power_n7.py` → `power_n7.txt` | P-NULL / P-EVOLVED power at n = 7 (port check against `power_adv.txt` B) |
| `nopeek_check.py` → `nopeek_check.txt` | `--no-peek H` reproduces `P1-readout.txt`, touches no H path, and leaves the P section unchanged (scratch venv with scipy; not in the suite) |
| `spot/` | re-runs from checkpoint at c872e80: F12 on P1-801, S1-805, P1-805 and P1-7; S1-805's cross-ticket and patchy scoring; P1-7's install control (`$SCRATCH` = the adversary's scratch dir) |

- **Bulk:** the restores (`ckpt/rbt-104-S1-805`, `ckpt/rbt-106-P1-{801,805,7}`) and the scratch worktree
  (`rabbitstew/` at c872e80, a local commit, never pushed) stayed in scratch.
- **Platform:** x86_64, MuJoCo 3.14.0, numpy 2.4.6.
- **Suite:** in a clean `pip install -e '.[dev]'` venv with no scipy; the result is in the PR.
