# RBT-106 H readout: option H, a paying compass planted at the default reach, HU (uniform) against HP (patchy)

*Designer's readout, 2026-09-27, run exactly as registered (PREREGISTRATION.md §6.2 Pair H; §10 governs).
Raw output: `H-readout.txt` (`readout.py --pairs H`; the `--no-peek` flag is unused). No H number was read before
all 20 H arms were merged (head `daf4f90`). The code that prints H-0, the gate and the power at the usable n was
committed (`b8edb98`) before the readout was run. RBT-112's `gate.py` was not run. A readout adversary
follows; the designer does not rule.*

## Verdict

**VERDICT H: SUPPORTED: the larger prize held the paying compass where the uniform prize did not.**

`HELD: HU 0, HP 9;  paired log-excess at 599, HP - HU: +2.240 [+1.556, +2.925]`
- **The rule** is #HELD(HP) − #HELD(HU) ≥ 3 and the paired log-excess interval above zero. It is met:
  9 − 0 = 9, and the interval is above zero.
- **"HELD"** means the planted-rooted living carry a paying compass (own links ≥ 12.52 with the root's sign)
  above the operator-alone bound B at matched depth, at both 300 and 599, scored on k_planted only (§10.2).
- **Usable pairs: 10 of 10.**

**Function follows** (reported, not in the verdict; §10.4's COMPASS count):

| | HU | HP |
|---|---|---|
| COMPASS lines (primary FD and compass attribution FD), patchy-scored | 0 | 10 |
| food-dependent lines, any smell use (primary FD alone) | 0 | 10 |
| compass-lesion income gain, patchy-scored | +0.520 [−0.041, +1.080] | +4.804 [+4.059, +5.549] |

- Paired F(HP) − F(HU), patchy-scored: **+3.858 [+2.965, +4.750]**.
- Paired F(HP) − F(HU), uniform-scored: +0.925 [+0.610, +1.241].

**In plain words.** We planted a compass that already pays (the routed motif at a = 64) in half the
founders of ten populations, at the default link reach. Each population evolved for 600 seasons twice,
once in RBT-90's uniform world and once in the patchy world where a working compass pays about 2.5×
more. The operator erodes the compass at the same rate in both (u ≈ 0.29 per generation, §5.1).
- **In the uniform world** no population held it above what the operator alone leaves, and no line's
  champions steered by food.
- **In the patchy world** nine of ten held it, and all ten lines' champions are food-dependent through
  the compass: removing the compass's input links removes their gain.

With the erosion the same and only the prize different, **the size of the prize decided whether a
paying compass was held.**

**Scope.**
- It covers a compass planted at the paying magnitude, at the default reach, in one patchy world
  (12 items in 3 patches, instant regrowth), over 600 seasons.
- It says nothing about whether the prize makes a compass from a sub-paying structure. The P1 readout
  (#342, P-NULL) is the registered answer to that, and that answer says nothing about the prize once
  reach is there.

**Pre-registered expectation:** H-0 gave SUPPORTED 0.25, FALSIFIED-a 0.30, FALSIFIED-b 0.15,
NOT DECIDED 0.25 and VOID 0.05. **SUPPORTED occurred.** The design's lean toward FALSIFIED-a
("the uniform prize already holds it", §6.4) was wrong: HU held on no seed.

## Usability, per seed pair (the install control on each arm's own bests, `function.py --install 32`)

| seed | HU install control | HP install control | pair |
|---|---|---|---|
| 801 | FD, F +0.721 [+0.213, +1.229] | FD, +4.627 [+1.951, +7.303] | usable |
| 4 | FD, +0.779 [+0.178, +1.380] | FD, +7.152 [+6.568, +7.736] | usable |
| 804 | FD, +0.623 [+0.246, +1.000] | FD, +6.911 [+5.464, +8.357] | usable |
| 805 | FD, +0.908 [+0.315, +1.502] | FD, +5.199 [+2.751, +7.646] | usable |
| 806 | FD, +0.654 [+0.315, +0.993] | FD, +4.824 [+3.005, +6.643] | usable |
| 807 | FD, +1.272 [+0.893, +1.652] | FD, +5.473 [+2.709, +8.237] | usable |
| 1 | FD, +0.531 [+0.220, +0.843] | FD, +6.766 [+5.324, +8.207] | usable |
| 2 | FD, +0.779 [+0.342, +1.216] | FD, +6.415 [+5.516, +7.315] | usable |
| 3 | FD, +0.788 [+0.216, +1.360] | FD, +6.962 [+6.313, +7.611] | usable |
| 7 | FD, +1.078 [+0.567, +1.589] | FD, +5.440 [+2.652, +8.228] | usable |

Every arm is viable (60 alive through the window) and on x86_64. Every arm passes analyse.py's control, and
every arm's `rabbitstew/` is c872e80's (`commit.txt`). HP's controls read high because the champion's own
planted compass and the installed one add (RBT-104 readout adversary §5.2); a control only has to pass.

### F12: resting drive and Effector saturation, every HU and HP champion (`f12.py` → `f12-H.txt`)

`f12.py` was fixed before any arm was read, and is unchanged. It imports RBT-104's readout adversary's
`sat_probe.body_stats`. It prints, per best, every planted-type unit (bias b, output weights v, resting
drive |v·tanh(b)|) and the drive Effectors' operating point under the arm's own install control (sat, T).

| arm | median T | bests with a planted-type unit driving > 1 | install control | F12 flag |
|---|---|---|---|---|
| HU (ten arms) | 0.37–0.54 | 0–3 of 7 | FD on all ten | none |
| HP (seven arms: 801, 807, 1, 2, 3, 4, 7) | 0.31–0.74 | 0–3 of 7 | FD on all seven | none |
| **HP-804** | 0.273 | **4/7** | FD, +6.911 [+5.464, +8.357] | **MASKED (heuristic)** |
| **HP-805** | 0.483 | **6/7** | FD, +5.199 [+2.751, +7.646] | **MASKED (heuristic)** |
| **HP-806** | 0.349 | **7/7** | FD, +4.824 [+3.005, +6.643] | **MASKED (heuristic)** |

**What F12 says, and what it does not.**
- **No control is masked in fact.** Every one of the 20 install controls reads FOOD-DEPENDENT, and median T
  is 0.27–0.74 on every arm, against 0.04–0.08 for RBT-104's ×8 hosts.
- **The heuristic's second criterion fired on HP-804, HP-805 and HP-806.** Their champions carry the
  planted unit (v ≈ 32) with its bias drifted to |b| ≈ 0.1–0.2, so the resting drive is 3–7.
  - For example, HP-806's g350 has b +0.215 and drive 6.7, and g450 has b −0.190 and drive 6.3
    (`f12-H.txt`).
  - F12 anticipated that such a drive would mask the control, following RBT-104 readout adversary §5.2's
    probe: b = 0.1 masked one host of two.
  - **In these evolved hosts it did not.** Their controls pass with the largest F in the design, and
    their own lines are food-dependent through the compass.
- **Under the pre-registration's own rule these arms are USABLE.** An arm is usable iff its control
  passes (§6.1), and F12 is a POST HOC diagnostic whose flag matters only for a control that fails. I
  report the flag and do not act on it. The readout adversary should rule on it.
- **Sensitivity** (`H-sensitivity.txt`; reported, not scored). Without HP-804, HP-805 and HP-806 (n = 7):
  - HELD: HU 0, HP 6. The paired log-excess is +2.304 [+1.257, +3.352].
  - COMPASS lines: HU 0, HP 7. The paired F is +3.986 [+2.920, +5.051].
  - **The registered rule would still read SUPPORTED.**
- **A detail on the drift:** the bias gate, a resting drive above ~1 (§5.1), is what erodes the planted
  compass under the operator alone. The patchy arms' champions carry drifted planted units that still
  steer, so evolved hosts can tolerate what the operator-alone reading treats as loss.
  - HP-806's g550 carries the planted unit with its function mutated to `sin` at b = 0.000, so its
    resting drive is 0.
  - This bears on the "held" null's per-lineage criterion (own links ≥ 12.52), not on the verdict, which
    uses the same criterion in both worlds.

## Beside the verdict

| seed | HELD 300 / 599 (k_planted(k_bare)/n/B), HU | HP | HELD (HU, HP) | F patchy, compass attribution: HU | HP |
|---|---|---|---|---|---|
| 801 | 0(17)/12/2 · 0(0)/0/0 | 5(2)/54/3 · 20(0)/60/2 | no, **yes** | +1.650, no compass gain | +3.415, FD |
| 4 | 1(0)/14/3 · 0(0)/19/1 | 24(6)/50/5 · 23(0)/60/2 | no, **yes** | +0.828, no compass gain | +5.763, FD |
| 804 | 3(4)/4/1 · 0(0)/0/0 | 9(2)/58/4 · 15(0)/60/1 | no, **yes** | +0.252, no compass gain | +5.402, FD |
| 805 | 2(3)/4/1 · 0(0)/0/0 | 18(9)/31/4 · 7(0)/50/2 | no, **yes** | +1.431, no compass gain | +3.228, FD |
| 806 | 1(0)/45/5 · 0(0)/40/1 | 23(2)/51/4 · 7(0)/60/1 | no, **yes** | −0.078, no compass gain | +3.652, FD |
| 807 | 0(1)/0/0 · 0(0)/0/0 | 2(10)/37/3 · 0(6)/27/1 | no, no | −0.040, no compass gain | +4.538, FD |
| 1 | 0(0)/52/4 · 0(0)/60/2 | 29(11)/47/3 · 6(2)/48/1 | no, **yes** | −0.042, no compass gain | +4.835, FD |
| 2 | 0(0)/47/4 · 0(0)/56/2 | 21(0)/60/5 · 16(0)/60/2 | no, **yes** | −0.196, no compass gain | +4.051, FD |
| 3 | 0(0)/43/4 · 0(0)/24/1 | 26(1)/56/4 · 35(0)/60/2 | no, **yes** | +0.377, no compass gain | +4.759, FD |
| 7 | 3(0)/14/2 · 0(0)/0/0 | 11(3)/50/5 · 15(8)/30/1 | no, **yes** | +0.391, no compass gain | +3.507, FD |

- **In the uniform arms, the planted-rooted lineages themselves were often lost.** n = 0 at 599 on 801,
  804, 805, 807 and 7, meaning every living genome descends from a bare founder. Where planted roots
  survived, none carried a paying compass (k_planted = 0).
- **HP-807 is the one patchy arm not HELD.** At 599 its planted-rooted living carry none (0 of 27), while 6
  bare-rooted genomes carry the compass by crossover (k_bare, not scored). Its line is still
  food-dependent through the compass (F +4.538).
- **k_bare at 599:** HU 0, HP 16. The patchy world also spread the compass across lineages; it is not
  scored.
- **Carriage X per 1,000** (analyse.py): HU 0–260, HP 293–828.

## Registered prediction, gate and power at the usable n

- **H-0** (SUPPORTED 0.25, FALSIFIED-a 0.30, FALSIFIED-b 0.15, NOT DECIDED 0.25, VOID 0.05): **SUPPORTED.**
- **The gate** (season 150; §7.2, §10.2): HP-801 and HP-4 both read **HELD ABOVE NO-SELECTION**
  (HP-801 k_planted 15, B 11; HP-4 k_planted 30, B 10), so H1 was launched. It is futility-only and
  enters no verdict. The null chance of ≥ 1 of 2 CONTINUE is 0.16.
- **Power at the usable n = 10** (all ten pairs usable, so the usable n is the planned n; `power.outcomes`,
  q = P(an arm is HELD)):

| truth (q_U, q_P) | P(SUPPORTED count) | P(FALSIFIED-a count) | P(FALSIFIED-b count) |
|---|---|---|---|
| no effect at the measured null rate (0.01, 0.01) | 0.000 | 0.000 | 0.996 |
| no effect, inflated (0.08, 0.08) | 0.020 | 0.001 | 0.812 |
| the prize decides (0.15, 0.60) | 0.852 | 0.010 | 0.002 |
| the prize decides, weaker (0.15, 0.40) | 0.504 | 0.010 | 0.046 |
| the uniform prize suffices (0.60, 0.70) | 0.241 | 0.834 | 0.000 |

- **SUPPORTED's count** fires under no effect with probability ≤ 0.020, even at an inflated null rate of 0.08
  (measured 0.01). The paired log-excess condition only lowers that.
- **The absent-type verdicts, FALSIFIED-a and FALSIFIED-b,** did not fire. Their miss rates at n = 10 are
  in the table.

**Side effects** (descriptive; the pre-registration registered no H side-effect prediction):
- viable: HU 10/10, HP 10/10;
- window income HP − HU: **+1.771 [+1.419, +2.122]**;
- births: HP more than HU on 10/10 seeds;
- window depth: HU 14.1–16.6, HP 14.3–17.6.

## How the readout was made

- **Branch:** `results/RBT-106-H-readout`, cut from the integration head `daf4f90`, with all 20 H arms merged.
- **The H arms' reads** (held, function in both worlds, install control, analyse.py) were made by their
  runners at their launch commits. `readout.py` reads files only.
- **F12** restored all 20 checkpoints (`ckpt/rbt-106-HU|HP-SEED`) into scratch, outside the checkout.
  - Each restored bulk regenerates the committed `seasons.txt` and `lineage-last.txt` byte for byte
    (20 of 20).
  - F12 ran from a scratch worktree with `rabbitstew/` exactly at c872e80, a local commit never pushed.
    Integration carries RBT-112's change.
- **Platform:** x86_64, MuJoCo 3.14.0, numpy 2.4.6.
- **Suite:** in a clean `pip install -e '.[dev]'` venv with no scipy (see the PR).

## Files

| file | what |
|---|---|
| `H-READOUT.md` | this |
| `H-readout.txt` | the raw readout (`readout.py --pairs H`) |
| `H-sensitivity.txt` | the counts without the three F12-flagged HP arms (reported, not scored) |
| `f12-H.txt` | F12 for all 20 H arms (`f12.py`, unchanged) |
| `readout.py` | + the H prediction, gate and usable-n power printout (committed before the readout was run) |
