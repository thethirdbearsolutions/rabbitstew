# RBT-106 P1 readout: the primary pair, S1-patchy (P1) against RBT-104's S1-uniform

*Designer's readout, 2026-09-27, run exactly as registered (PREREGISTRATION.md §6.2, the primary P pair,
patchy-scored; the §10 amendment governs). Raw output: `P1-readout.txt` (`readout.py --pairs H,P --no-peek H`).
A readout adversary follows; the designer does not rule.*

## Verdict

**VERDICT P: P-NULL.** In the patchy world, **0 of 7 usable P1 lines** is a COMPASS line: readout (b)'s
primary call FOOD-DEPENDENT and its compass attribution FOOD-DEPENDENT. The paired F(P1) − F(S1),
patchy-scored, is **+0.049 [−0.242, +0.340]**, t(6) over 7 usable pairs. S1 also has 0 COMPASS lines.

**In plain words, with the registered caveat.** We planted the compass's wiring at the weak strength drift
gives it (w = 1, a = 2) in half the founders. The populations then evolved for 600 seasons in a world where
a working compass pays about 2.5× more than in RBT-90's (+2.10 against +0.84 items per bout, §2). **Their
champions steer by food no more than the same populations' champions in the uniform world.**
- **So a 2.5× prize alone, at the default link reach, did not make a compass from a sub-paying planted
  structure.**
- **This says nothing about whether the prize matters once reach is there.** Under "both reach and prize
  are needed", P-NULL fires with probability 0.72, or 0.89 with the measured patchy bare lines (§6.3,
  §10.5). The factorial that could say so is deferred (§10.3), and option H, the direct test of whether a
  *paying* compass is held, is still running.
- **P-NULL's power against "the prize alone suffices"** (the matched-null figure, §6.3 and §10.5, measured
  bare-line model): it misses that hypothesis with probability **0.07** if it held in half the
  populations (q = 0.5), and **0.37** if in a quarter (q = 0.25). The EVOLVED power behind these is an
  upper bound under the F6 attribution rule (§10.4).

**Pre-registered expectation:** P-NULL at 0.72 (P-0), the modal outcome. **It occurred.**

## Usability, per seed (the install control on each arm's own bests, `function.py --install 32`)

| seed | S1 (RBT-104's arm) install control | P1 install control | pair |
|---|---|---|---|
| 801 | FD, F +0.674 [+0.234, +1.114] | **not FD**, F +1.263 [−0.335, +2.862] | UNUSABLE |
| 4 | FD, +0.621 [+0.367, +0.874] | FD, +3.929 [+1.449, +6.408] | usable |
| 804 | FD, +1.100 [+0.537, +1.664] | FD, +1.971 [+0.398, +3.544] | usable |
| 805 | **not FD**, +0.306 [−0.067, +0.678] | FD, +4.203 [+1.505, +6.901] | UNUSABLE |
| 806 | FD, +0.830 [+0.452, +1.209] | FD, +2.205 [+0.601, +3.809] | usable |
| 807 | FD, +0.848 [+0.610, +1.086] | FD, +2.433 [+1.110, +3.756] | usable |
| 1 | FD, +0.966 [+0.573, +1.359] | FD, +1.462 [+0.098, +2.826] | usable |
| 2 | FD, +0.478 [+0.001, +0.954] | FD, +2.891 [+0.764, +5.017] | usable |
| 3 | FD, +0.926 [+0.294, +1.558] | FD, +2.946 [+1.015, +4.877] | usable |
| 7 | FD, +0.768 [+0.562, +0.974] | **not FD**, +1.098 [−0.336, +2.532] | UNUSABLE |

- **Every arm is viable** (60 alive through the window) and on x86_64. Every arm passes analyse.py's
  positive control. Every arm's `rabbitstew/` is c872e80's (`commit.txt`).
- **7 of 10 pairs are usable,** exactly the VOID floor, so the verdict is scored.
- **Unusable arms leave the rules; they are not nulls** (§6.1).

**F12: could any control fail by construction?** (`f12.py` → `f12.txt`; POST HOC, fixed before any arm
was read: median T < 0.10 over the seven bests, or ≥ 4 of 7 bests carrying a planted-type unit with
resting drive > 1.) It imports RBT-104's readout adversary's `sat_probe.body_stats` for the drive
Effectors' operating point under each arm's own install control, and reads each champion's planted-type
units (bias b, output weights v, resting drive |v·f(b)|).

| arm | median T (share of the compass's effect reaching the Effector) | bests with a planted-type unit driving > 1 | install control | by construction |
|---|---|---|---|---|
| P1 (ten arms) | 0.39–0.60 | 0–2 of 7 | 8 FD, 2 not (801, 7) | **no, on all ten** |
| S1 (ten arms) | 0.35–0.61 | 0–2 of 7 | 9 FD, 1 not (805) | **no, on all ten** |

- **For reference:** RBT-104's ×8 hosts read T 0.04–0.08, and its S1 hosts 0.36–0.53. **No P1 seed's
  control could fail by construction.**
- **The three failures** (P1-801, P1-7, S1-805) are interval failures:
  - P1-801's and P1-7's controls have point estimates of +1.26 and +1.10 with wide intervals across the
    seven bodies. Some of their bests sit at high Effector saturation (for example P1-801 g450:
    sat 0.975, T 0.04), next to bodies at T 0.39–0.57;
  - S1-805's is small, +0.31.
- **Under the pre-registration's own rule these three arms are UNUSABLE, not nulls.**

## The numbers beside the verdict (usable pairs unless stated)

| quantity | S1 (uniform) | P1 (patchy) |
|---|---|---|
| COMPASS lines (primary FD and compass attribution FD), patchy-scored | 0 | **0** |
| food-dependent lines, any smell use (primary FD alone), patchy-scored | 0 | 0 |
| compass-lesion income gain, patchy-scored, mean over lines | +0.113 [−0.079, +0.305] | −0.020 [−0.055, +0.015] |
| paired F(P1) − F(S1) | patchy-scored **+0.049 [−0.242, +0.340]**; uniform-scored −0.068 [−0.150, +0.014] | |
| HELD (criterion `same`, k_planted > B at 300 and 599) | 1 (seed 804) | **0** |
| paired log-excess at 599, P1 − S1 | −1.559 [−2.983, −0.136] | |
| k_bare at 599 (crossover transfer, not scored) | 14 | 0 |

**Structure.** The planted structure was held above the operator-alone null on one S1 seed (804) and on
no P1 seed. The paired log-excess is *negative*: P1 kept less of the planted structure, relative to the
no-selection expectation at its depth, than S1 did.

**Sensitivity** (`P1-sensitivity.txt`: all ten seeds, usability ignored; reported, not scored). The one
COMPASS line among all 20 arms is **P1-805**, F +1.942 with compass attribution FOOD-DEPENDENT. Its pair is
unusable because S1-805's control failed. Counting it, P1 has 1 COMPASS line and S1 has 0. The paired
F(P1) − F(S1) over ten seeds is +0.254 [−0.205, +0.714]. **The registered rule would still read P-NULL.**
P1-805 is also P1's highest-carriage arm (X = 468 per 1,000). It is worth the readout adversary's look as
a single case, not as a pattern.

## Registered predictions, scored

| # | prediction (registered) | confidence | outcome |
|---|---|---|---|
| P-0 | primary verdict P-NULL (P-EVOLVED 0.06, NOT DECIDED 0.17, VOID 0.05) | 0.72 | **P-NULL: held** |
| SE-1 | no P1 arm extinct, 10 of 10 viable | 0.90 | 10 of 10 viable: **held** |
| SE-2 | P1 − S1 window income, t interval above zero | 0.85 | +0.384 [+0.297, +0.471] (usable, n = 7); +0.391 [+0.320, +0.462] over all ten: **held** |
| SE-3 | P1 more designed births than S1 on ≥ 8 of 10, and a deeper window on ≥ 8 of 10 | 0.80 | births 10/10, depth 8/10: **held** |
| P-1 | #HELD(P1) − #HELD(S1) ≤ 1 (revised §10.2) | 0.75 | 0 − 1 = −1: **held** |
| P-2 | P1's window carriage X below 250 per 1,000 on ≥ 8 of 10 | 0.65 | 8/10 (X: 4, 0, 0, 468, 130, 51, 184, 0, 283, 240): **held** |

**Side effects, as predicted:** the patchy world is richer (window income +0.38 items), breeds faster
(1,740–2,049 designed births against 1,078–1,267) and sits deeper (window depth 14.4–17.4 against
13.5–16.7). It went extinct nowhere.

## How the readout was made

- **Branch:** `results/RBT-106-P1-readout`, cut from the integration head `011cb79`, with all ten P1 arms
  merged (#268, #269, #271, #272, #275, #283, #288, #306, #322, #326).
- **The S1 side** is RBT-104's ten S1 arms, read by `postrun.sh S1 SEED` (§10.1):
  - each checkpoint `ckpt/rbt-104-S1-SEED` was restored into scratch;
  - RBT-106's S1 command was re-run for 20 seasons and compared with the arm by the design adversary's
    `cross_ticket.py`. **SAME RUN on all ten seeds** (`S1-SEED/cross-ticket.txt`);
  - `commit.txt` was written only then;
  - held.py was run at 300 and 599, and function.py through `cross_world.py` in the patchy world;
  - RBT-104's `platform.txt`, `rbt102.txt`, `function-pc.txt` and `function.txt` (the uniform scoring)
    were copied, not recomputed;
  - the regenerated `seasons.txt` and `lineage-last.txt` are byte-identical to RBT-104's committed ones on
    all ten seeds.
- **Code.** Integration's `rabbitstew/` has moved since c872e80 (RBT-112's `--global-bias-sigma`, ce1e9ce).
  So every S1 read and the F12 probe ran from a scratch worktree of this branch with `rabbitstew/` exactly
  as at c872e80 (a local commit, never pushed; `git diff c872e80 HEAD -- rabbitstew` empty).
  - The P1 arms' own reads were made by their runners at their launch commits, all on c872e80's tree.
  - `readout.py` reads files only.
- **Platform:** x86_64, MuJoCo 3.14.0, numpy 2.4.6, for every arm and every read.
- **No-peek on H.** Option H is 11 of 20 merged. `readout.py` gained a `--no-peek PAIRS` flag, which prints
  a listed pair as **NOT READ** without opening any of its files. No threshold or rule changed. It was run
  as `--pairs H,P --no-peek H`.
  - No H directory was listed, opened or read at any point in this session's readout work.
  - The S1 reads, the F12 probe and the restores touched P1 and S1 only.
- **Suite:** in a clean `pip install -e '.[dev]'` venv with no scipy (see the PR).

## Files

| file | what |
|---|---|
| `P1-READOUT.md` | this |
| `P1-readout.txt` | the raw readout (`readout.py --pairs H,P --no-peek H`) |
| `P1-sensitivity.txt` | all ten seeds, usability ignored (reported, not scored) |
| `f12.py`, `f12.txt` | F12: planted-unit resting drive and the Effector operating point, per champion, all 20 arms |
| `S1-SEED/` | RBT-106's post-run reads of RBT-104's S1 arms: `commit.txt`, `cross-ticket.txt`, `held-{300,599}.txt`, `function-patchy.txt`, and RBT-104's copied files |
| `readout.py` | + `--no-peek`, the per-arm usability lines, the registered predictions scored |
