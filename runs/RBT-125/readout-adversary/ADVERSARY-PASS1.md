# RBT-125 readout adversary, pass 1: #436 at 5f12c5c (§A committed layouts, §C on the fixed code)

*This is the coordinator's task of 05:57 UTC. §B is still running and will be reviewed in pass 2. Everything below is
recomputed from committed outputs, plus my earlier runs on committed bodies (#445, #448). Nothing new was run on real
hosts.*

## Verdict: **CONFIRMED WITH CAVEATS**

| item | count |
|---|---|
| MUST | 1: a descriptive ranking claim is read from point estimates and partly contradicted by its own paired test |
| SHOULD | 4 |
| NIT | 2 |

Every number in the new §A and §C text reproduces.

## Checks

| check | result | evidence |
|---|---|---|
| Base | 5f12c5c does **not** contain integration's head (ce69f17), but merges clean, and integration changed nothing under `runs/RBT-125/` since. NIT 1 | `git merge-tree` |
| Registered paired design and t(9) CIs | **reproduce to the digit**: all 9 cells, every paired cell − G0, same-signed, and G10 − G2.5 | `recompute_layouts.py` / `.txt`: an independent parser of the harness tables, with scipy t |
| `prize.txt` (final re-render) | `prize_readout.py` re-run on the committed outputs gives **byte-identical** output | local re-render |
| Every cited `prize/*.txt` committed | **yes**: 10 cells × 10 populations plus 2 harness checks = 102 files | `git ls-files` |
| Scripts unchanged since the launch | `prize_readout.py`, `run_gate.sh`, `prize_gate.py` and `worlds/` have no diff c591a75..5f12c5c | `git diff` |
| G0 is the right control | **yes**. In every layout, each G2.5 and G10 world differs from its G0 world only in `food.smell_contrast` and `food.smell_tau` | world diff |
| Decoy n/a for HP and U | **registered**, not an omission. §A: "In the PW cells, the rotated decoy also runs at w = 3". `run_gate.sh` step 4 calls `prize` without `--decoy` | REGISTRATION.md, run_gate.sh |
| §C `root` + `surface` on the fixed code | **corroborated independently**. `side_effects_surface.txt` matches my runs on committed bodies before the fix (#445), and the merged minimal guard is bitwise the pre-fix placement for compact roots (#448) | see below |

**What G0 is.** G0 is the *legacy* food reading (squashed intensity). It is not a lesion. So "the channel's
contribution" is contrast channel against legacy channel, which is what A1.1 registered. The coordinator's brief says
"the channel lesioned"; the readout itself does not, and does not need to.

### §A, the committed layouts: recomputed (`recompute_layouts.txt`)

Paired by population, t(9):

| contrast | readout | recomputed | **absolute motif income (added)** | base change (added) |
|---|---|---|---|---|
| HP-G2.5 − HP-G0 | +0.797 [+0.314, +1.279] | same | +0.798 [+0.412, +1.183] | +0.001 [−0.264, +0.266] |
| HP-G10 − HP-G0 | +0.870 [+0.471, +1.269] | same | +0.833 [+0.447, +1.220] | −0.036 [−0.258, +0.185] |
| U-G2.5 − U-G0 | +0.395 [+0.204, +0.586] | same | **+0.283 [+0.122, +0.444]** | **−0.113 [−0.213, −0.013]** |
| U-G10 − U-G0 | +0.400 [+0.144, +0.656] | same | **+0.258 [+0.005, +0.511]** | **−0.142 [−0.259, −0.025]** |
| HP-G10 − HP-G2.5 | +0.073 [−0.078, +0.225] | same | | |
| U-G10 − U-G2.5 | +0.005 [−0.112, +0.122] | same | | |

## MUST

**M1. "It ranks HP (+0.80) > PW (+0.49) > U (+0.40), which is the ranking of the legacy prizes' layouts. The channel
multiplies what the layout already rewards; it does not make PW special … the audit's view … holds on real bodies"
rests on point estimates. Where the paired test exists, it only half supports the claim.**

The channel's contributions (cell − G0 at G2.5), compared pairwise, paired by population:

| comparison | t(9) 95% | resolved? |
|---|---|---|
| HP − PW | +0.308 [+0.080, +0.536] | yes |
| **PW − U** | **+0.093 [−0.127, +0.314]** | **no** |
| HP − U | +0.401 [+0.050, +0.752] | yes |

The "legacy prizes' ranking" it is matched to is **not resolved at a = 6 at all**:

| comparison | t(9) 95% |
|---|---|
| HP-G0 − PW-G0 | +0.040 [−0.051, +0.132] |
| PW-G0 − U-G0 | +0.024 [−0.029, +0.077] |
| HP-G0 − U-G0 | +0.064 [−0.048, +0.176] |

- **The ratio behind "multiplies".** It is 5.8 in HP, 4.9 in PW and 4.9 in U, which are point estimates with no
  interval.
- **None of this was registered.** A ranking of layouts, and "the audit's view holds", are the kind of sentence RBT-129
  would carry forward.
- **Fix.** Report what is resolved:
  - the channel pays more in HP than in PW or U;
  - PW and U are not distinguished;
  - the G0 prizes do not rank the layouts at a = 6.

  Drop "the ranking of the legacy prizes' layouts" and "the audit's view … holds on real bodies", or mark them as
  conjecture.

## SHOULD

1. **In U, part of the "channel pays" contrast is the base falling, and the fall is resolved.**
   - Base change: −0.113 [−0.213, −0.013] at G2.5, and −0.142 [−0.259, −0.025] at G10. The readout calls it "not
     tested for significance".
   - The contrast in absolute motif income is **+0.283 [+0.122, +0.444]** at U-G2.5, against the prize contrast's
     +0.395, and **+0.258 [+0.005, +0.511]** at U-G10.
   - So the channel still pays in absolute terms in every layout, and U-G10 only just. State the resolved base drop
     in U, and add the absolute-income column, as for PW in #431.
2. **HP and U have no decoy, so "the channel pays the installed compass in every layout" is not shown to be
   food-dependent there.**
   - The registration's decoy is PW-only, so this is not a violation. But the channel also changes what the bodies'
     own evolved noses read (the base moves in U), so the HP and U gain could in part be gait.
   - Add: "in HP and U without a food-dependence check".
3. **Audit C's second prediction also fails, and the readout should say so.**
   - AUDIT.md L450–451: "at a = 6 in the committed HU it should not [pass]".
   - U-G0 pays +0.101 [+0.016, +0.187], with a lower bound > 0. The readout's "the legacy reading pays a little in
     every layout" states the fact, but not the failed prediction. #430 did state it for PW.
4. **The §C wording "the corpus `surface` row was measured before #446" is stale.**
   - `side_effects_surface.txt` re-ran the corpus U-G0/surface row on the fixed code, and it reproduces +30% / +15% to
     the digit.
   - Say that, so the corpus row is not read as leak-affected.
   - With the merged minimal guard, `any` + `surface` still pays the long sweeper +2.96 (U) and +1.71 (PW), and the
     readout correctly keeps refusing it.

## NIT

1. Merge integration (ce69f17) into the branch before merge. It is clean, and nothing under `runs/RBT-125` differs.
2. The saturation link ("the saturation cost of G = 10 does not show at an installed weight") is fair as a
   description. It leans on HP G10 − G2.5 +0.073 [−0.078, +0.225] and U +0.005 [−0.112, +0.122], which are null
   results, not equivalence. "Is not detectably worse" is the accurate wording.

## §C on the fixed code: corroborated

`side_effects_surface.txt` ran on integration 01f113d with the minimal guard. My independent runs on the same committed
bodies (#445 `probe_corpus_rules.txt` and `probe_tumbler_rules.txt`, and #448 `fixcheck_variant.txt`) give identical
figures:

| row | `side_effects_surface.txt` | mine |
|---|---|---|
| designed founders, root + surface | 0.656 items, 0.38 solvent | 0.656, 0.38 |
| corpus, root + surface | +0.998 holistic / +0.620 designed | +0.998 / +0.620 |
| tumbler, root + surface (0.45 m U, 6.46 m U, 0.45 m PW, 6.46 m PW) | +1.30 / +0.66 / +0.80 / +0.06 | same |

- The re-ruled rule's STOP condition (solvency well below 0.38) is not met.
- The readout's findings on root + surface match my #445 and #448 reports:
  - it restores the designed founders;
  - it removes span;
  - it raises compact blind coverage.

## Files

| file | what it holds |
|---|---|
| `recompute_layouts.py` / `.txt` | all 9 §A cells; the paired contrasts, same-signed, absolute income, base change, G10 − G2.5; the layout-ranking and legacy-ranking tests |
