# RBT-125 readout adversary: the world-gate readout (PR #430), §A

*This review covers PR #430 (`results/RBT-125-gate-readout` at 897174e) under the coordinator's task of 01:18 UTC.
§A is reviewed here, and §B, §C, the τ = 1 s cell and the committed layouts are pending: they have not landed yet.
Everything below comes from committed files, server-side timestamps, my own recomputation, and one population I
re-simulated from its checkpoint.*

## Verdict on §A: **CONFIRMED WITH CAVEATS**

"PASS at G = 2.5, and the channel pays" is earned under the registration as amended:
- every registered number reproduces exactly;
- the channel's contribution survives the two ways it could have been flattered: body re-signing, and a lower base.

The caveats are two wording fixes (SHOULD). There is no MUST.

## 1. No-peek and the timeline

| check | result | evidence |
|---|---|---|
| Amendment 1 (5f3c8e2) and amendment 2 (c591a75) existed before the launch | **yes** | Both hashes are quoted in RBT-125 comments whose **server** timestamps are 22:30:51 and 22:42:42 UTC. The launch was at 23:01:31 (`launch.txt`). A commit hash quoted before 23:01 proves its content existed before 23:01 |
| The gate ran the amended code | **yes** | `launch.txt`: `commit c591a757…`, `rabbitstew_tree 2e2e505…` |
| The parity condition held before any cell ran | **yes** | `parity.txt` is IDENTICAL on all 10 cells. `run_gate.sh` exits 5 before any cell unless all are IDENTICAL |
| The readout scripts did not change after the launch | **yes** | `git diff c591a75 897174e -- runs/RBT-125/gate/*.py run_gate.sh` is empty. 897174e adds only outputs, `READOUT.md` and `launch.txt`. `prize_readout.py` re-run on the committed outputs reproduces `prize.txt` **byte for byte** |
| No output predates the amendments | **supported, but not provable from git** | git stores no mtimes. What stands is the 23:01 refusal in every version of `run_gate.sh`, the two stopped launchers reported in server-stamped comments (22:25 and 22:31), and `started 23:01:31` in `launch.txt` |
| Later changes to `rabbitstew/` | **harmless** | Integration's `simulation.py` gained RBT-130's `smell_lesion`, off by default and stripped when off. The gate ran on the pinned tree anyway |

**SHOULD 1.** For the next gate, commit `ls -l --time-style=full-iso` of the output directory with the outputs. The
"first output at 23:06:45" in the audit trail is then checkable rather than asserted.

## 2. §A reproduced

**The registered script.** `prize_readout.py` from c591a75, re-run on the committed `prize/` files, gives a
`prize.txt` identical to the committed one.

**An independent parser** (`recompute_A.py` / `.txt`) reads the harness's own tables line by line (direction signs,
per-body base and delta, the mechanism block) and uses scipy's t quantile:

| cell | signed | prize a = 6, t(9) | motif − decoy, t(9) | base | zero pairs |
|---|---|---|---|---|---|
| PW-G2.5 | 70/70 | +0.614 [+0.276, +0.951] | +0.702 [+0.413, +0.991] | 1.049 | 2861/4480 |
| PW-G10 | 70/70 | +0.708 [+0.381, +1.034] | +0.912 [+0.654, +1.169] | 1.056 | 2806/4480 |
| PW-G0 | 70/70 | +0.125 [+0.056, +0.194] | +0.167 [+0.050, +0.284] | 1.118 | 3345/4480 |

- All three cells, all 10 per-population prizes and both contrasts match the readout to the digit.
- The all-10 counting is moot: 10/10 are readable in every cell.

**The channel's contribution (A1.1, the registered test):**

| contrast | all bodies | same-signed bodies | **absolute motif income (not registered, added here)** | base change |
|---|---|---|---|---|
| PW-G2.5 − PW-G0 | +0.488 [+0.155, +0.822] | +0.526 [+0.155, +0.897]; 3/70 bodies change sign | **+0.420 [+0.158, +0.682]** | −0.069 [−0.198, +0.060] |
| PW-G10 − PW-G0 | +0.582 [+0.255, +0.910] | +0.676 [+0.310, +1.042]; 5/70 change sign | **+0.520 [+0.253, +0.787]** | −0.062 [−0.187, +0.063] |

- The prize is motif − *own base in that cell*. The channel lowers the base a little (point estimate −0.07), so part
  of the +0.488 could in principle be the base falling rather than the motif earning.
- The absolute-income contrast asks whether bodies carrying the installed compass *eat more* under the channel than
  under legacy smell. Its lower bound is **+0.16**. **The channel pays with or without crediting the base drop.**
- Re-signing does not flatter it either: the same-signed figure is larger.

**Re-simulation.** Population 805 was re-run from `ckpt/rbt-90-805` with the gate's own `prize_gate.py`, in PW-G2.5
and PW-G0 with the decoy. Both outputs are **identical, line for line**, to the committed files (§6).

## 3. The harness checks: identical, and on what

- **uniform (RBT-103 seed 801).**
  - The whole file is identical to `docs/artifacts/RBT-103-seed-801.txt`, apart from the bodies' path line and the
    MuJoCo warnings, which the committed artifact carried in stdout.
  - That covers every body's direction angles, the readback and the per-body incomes, not just the ROW.
- **HP (RBT-106 HP-801 through `--config-from`, with the decoy at a = 64).**
  - The whole file is identical to `runs/RBT-106/prize/patchy-801.txt`, apart from the two path lines.
  - That includes the decoy block (+0.083 decoy, 3.5% retained). The config-from path and the patched decoy's legacy
    branch are therefore exact.
- **What they do not cover:** both checks are at G = 0. Under G > 0, the patched decoy is covered by the extended
  `check_decoy()` (A1.8) and by my probe of the patch (`runs/RBT-125/adversary/probe_decoy.txt`). The contrast code is
  covered by the parity digests against 0ec395f.

## 4. Is the reading faithful to the registration?

- **"The channel pays": earned.** A1.1's condition is the paired (PW-G2.5 − PW-G0) t(9) lower bound > 0, and it is
  +0.155. The fallback was not used, and the α statement (≤ 5% familywise) is correct.
- **The PW-G0 PASS is worded correctly.**
  - "PW-G0 also passes, by the world rule … the PW layout alone already makes a weak, installed compass pay a little",
    and "that multiplication, not the pass itself, is what M1's paired test attributes to the channel". This matches
    A1.1.
  - The attribution to audit C is also right. AUDIT.md L271–272 says "the prize should become positive at a = 6 only
    with it [the knob]". (L450–451's "should not" concerns HU, not PW-G0.)
- **SHOULD 2: the base-income cost is stated as a fact, but it is unresolved on these bodies.**
  - READOUT: "The channel lowers these evolved bodies' own base income in PW (1.049 … against 1.118)".
  - Paired by population, the change is −0.069 [−0.198, +0.060] at G2.5 and −0.062 [−0.187, +0.063] at G10. The
    interval includes 0.
  - Word it as a point estimate with its interval. Routing it to §C is correct for the phenomenon, but §C measures
    founders and the seed-801 corpus, not these 70 bests. So say that §C tests the same mechanism on other bodies,
    not this number.
  - Add the absolute-income contrast beside M1's. It is the direct answer to "does the channel make a
    compass-carrying body eat more".
- **SHOULD 3: "the channel is responsible for most of it" and "multiplies the prize by about 5".**
  - These are ratios of point estimates (+0.614 / +0.125).
  - Only the difference has an interval, [+0.155, +0.822], and a lower bound of +0.155 is only about a quarter of
    +0.614.
  - Keep "multiplies" as descriptive, and replace "most of it" with the contrast and its interval.
- **The decoy's negative retention is described correctly.**
  - The rotated decoy costs income, so motif − decoy exceeds the prize.
  - The PASS requires both lower bounds, and the prize's (+0.276) does not lean on the decoy. The conservative reading
    therefore passes on its own.
- **The planted-positive caveat is adequate.** It says §A shows that the world and the channel pay a compass that
  exists, at a weight evolution has reached, and not that a compass evolves or that the step path pays. That is the
  right boundary, and §B and the sweep are named as the places those questions go.
  - I would add one sentence: the bodies' own evolved nose wiring also reads the contrast, so "the channel" here
    means the channel as read by the installed motif *plus* whatever the base body already did with its noses.
    The prize subtracts the base, but not interactions between the two.

## 5. Pending: §B, §C, the τ = 1 s cell and the committed layouts

To be reviewed when they land, against the amended registration:
- **§B:** 128 seeds, speed arms at the same base w, the realised-speed rescaling with the r < 1.10 exclusion counted,
  TOST at δ = 0.10, and the expected reading of TIED, UNRESOLVED.
- **§C:** saturation on the §A bodies, the PW coverage cells, and births and depth stated as out of scope.

## 6. Re-simulation of population 805

- **The population.** 805 has the largest channel contrast of the ten: +1.049 at G2.5 against −0.009 at G0.
- **The bodies.** They were extracted from `origin/ckpt/rbt-90-805` (`run.tar.gz.part000`, MANIFEST 600/600).
- **The code.** It ran with #430's head tree (897174e: `prize_gate.py` puts that repo root first on `sys.path`).
  That tree is the pinned c591a75 plus RBT-130's off-by-default lesion flag, and on 4 cores.
- **The result.** Every line below the two path lines is identical to `prize/PW-G2.5-805.txt` and
  `prize/PW-G0-805.txt`:
  - the direction angles and signs;
  - the install readback;
  - all 7 bodies' base and delta;
  - the zero count;
  - the decoy block;
  - ROW.

  Both `.diff` files are empty.
- **What this establishes.** The committed outputs are what the registered instrument produces from the registered
  bodies. It also shows that the later integration tree computes the same thing.

## Files

| file | what it does |
|---|---|
| `recompute_A.py` / `.txt` | the independent §A parser and statistics, including the absolute-income contrast and the base change |
| `rerun_805_PW-G2.5.txt`, `rerun_805_PW-G0.txt` (+ `.diff`, `.err`) | the population-805 re-simulation from `ckpt/rbt-90-805` |
