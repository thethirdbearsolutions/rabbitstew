# RBT-104 report: is link-weight reach the cause?

*Designer's readout, 2026-09-27. **Rewritten after 01:52 UTC per the readout adversary** (PR #264,
`runs/RBT-104/readout-adversary/READOUT-ADVERSARY.md`, F1–F4, F7, F10) and the coordinator's ruling of
01:52. The scored verdict and every scored line are unchanged; the interpretation of the VOID is
corrected. Everything below is either **SCORED**, meaning read by the rules
fixed in `PREREGISTRATION.md` (§6.1, §6.5; Amendment 3 merged at `3f2878e`) and printed by
`readout.py` unchanged, or **POST HOC**, labelled as such at each place. No threshold or rule was
changed after the numbers were seen.*

**Order on the record:**
- Amendment 3's window readings were regenerated from the ten S8 checkpoints, with integration's
  `peek.py` (unchanged since the cleared `2524ae6`), and committed on their own in `42e19ef`
  **before `readout.py` ran**.
- `readout.py`'s output is `readout.txt`.
- The post hoc descriptions are `posthoc.py` and `posthoc.txt`.

**Platform:** all 20 arms ran on x86_64 / MuJoCo 3.14.0 / numpy 2.4.6 (`platform.txt` per arm,
checked by `readout.py`).

**Suite:** at `f5f402c` (all 20 arms merged), in a clean `pip install -e '.[dev]'` venv with
no scipy, **325 passed**; after the rewrite and a merge of integration (`d8b5c3f`), **342 passed**.

## The verdict (SCORED, verbatim from `readout.txt` §4)

```
  S8 viable 10, usable 2; S8 compass-FD 0 (primary FD 0); S1 primary FD 2 (compass-FD 0); F(S8 - S1) lower bound -2.248; held 0; in-host carriage 0
  VERDICT: VOID: fewer than 7 of 10 S8 arms usable (viable, with both positive controls passing); the side effect, not link-weight reach, is what was measured
```

**VOID.**
- All 20 arms are viable. Readout (a)'s positive control passes on all 20.
- **Readout (b)'s per-arm install control** (an installed a = 64 routed motif on the arm's own bests
  at seasons 300–590 must read FOOD-DEPENDENT) **fails on 8 of the 10 S8 arms.** It passes only on
  S8-807 and S8-4.
- So only 2 S8 arms are usable, against the 7 the verdict needs.

**Why VOID: the registered install control cannot pass on a ×8 host** (readout adversary F1,
groups B, D and E; POST HOC probes, `function.py` unchanged).
- The control installs the a = 64 motif at the **default** scale: inputs ±1, output 32. Nothing applies the
  arm's `link_scale` to it.
- In a ×8 host the drive Effectors sit at |x| ≈ 14–27 and are saturated on 91–96% of ticks, so only
  2–8% of the installed compass's effect reaches them (against 36–53% in S1 hosts; adversary §1.2).
- **Group B:** three S1 hosts that pass the control fail it 3 of 3 once their links are scaled ×8.
- **Groups D and E:** the same control built at the arm's own scale (±8, 256) passes on **5 of 5** failing
  S8 hosts and **3 of 3** synthetic ×8 hosts (F +1.2 to +2.3).
- So "8 of 10 S8 arms fail" was the expected reading whatever S8 evolved. The VOID measures the control's
  scale, not whether S8 hosts let a compass through. The two S8 passes (807, 4) have transmission of
  only 4% and 8% (adversary F5).

In the adversary's words: *"A compass built at the default scale is invisible in a host built at
×8."* The ticket's question, whether link-weight reach ×8 lets selection keep a working compass, **is
not answered by this experiment.**
- **Not FALSIFIED.** Absence was not read.
- **Not SUPPORTED.** No S8 line is compass-food-dependent, or even primary-food-dependent.

**The honest prior** (adversary F2). Given §2's founding measurement (whole-brain 0.0025 against own
links 46.0) and a control that had never been run on a K = 8 host (§4.2 limit 1), the prior should have
been *"VOID unless selection desaturates the host"*, far above the registered 0.15. A ten-minute
pre-arm check (group B, on the ×8 founders) would have shown it.

**Matched-null power** (§6.3, §6.5). VOID carries no power figure because it is not a
reading of H. Had the arms been usable:
- P(SUPPORTED | H) was ≤ 0.11–0.14 at n = 10, and ≤ 0.023–0.028 at n = 7;
- P(FALSIFIED's count | H) was 0.011.

## The other registered lines (SCORED, verbatim from `readout.txt`)

**§0, the wave-0 gate** (futility only; it entered no verdict):
```
  seed 801: k = 18, n = 26, B = 8 -> CONTINUE
  seed 4: k = 8, n = 51, B = 16 -> FUTILE
```
Under Amendment 3's full-operator null, the gate as defined reads CONTINUE on at least one seed
with probability 0.44 (`null_rates.txt`). So its CONTINUE was not evidence of selection (§6.5).

**§1, side effects, S8 − S1:**
```
  income n=10  +0.052 [-0.011, +0.115]
  alive  n=10  +0.000 [+0.000, +0.000]
  S1 viable on 10 of 10
  S8 viable on 10 of 10
```
Lesson 5 applies: alive = 60 is the ecology's refill, not a result. The non-refilling survival fact
is that there was **no extinction in any of the 20 arms**.

**§2, readout (a):**
```
  carriage X, S8 - S1, paired over seeds: n=10  +103.494 [-161.920, +368.908] per 1000
  S8 held its planted paying motif (k_planted, Amendment 3) above the full-operator no-selection bound at seasons 300 and 599 on 0 usable seed(s): []  (null rate per seed 0.005, null_rates.txt)
  S8 seeds with >= 10 window carriers paying IN HOST, and >= 10% of its window carriers: 0 []
```

**§3, readout (b):**
```
  S1: COMPASS food-dependent (ATTRIBUTION) on 0 of 9 usable seeds []; primary food-dependent (any food use) on 2 [804, 2]
  S8: COMPASS food-dependent (ATTRIBUTION) on 0 of 2 usable seeds []; primary food-dependent (any food use) on 0 []
  F, S8 - S1, paired over seeds usable in both: n=2  +0.115 [-2.248, +2.478]
```
S1-805 also fails its install control, so S1 has 9 usable seeds.

## Predictions, scored

| # | prediction (as registered) | confidence | outcome |
|---|---|---|---|
| outcome | SUPPORTED 0.10 / FALSIFIED 0.35 / NOT DECIDED 0.40 / **VOID 0.15** (Amendment 3, §6.5) | — | **VOID** |
| P-0 | the gate stops the ticket after wave 0 | 0.45 | wrong (CONTINUE on 801) |
| S-1 | no primary arm goes extinct (20 of 20 viable) | 0.80 | **right** (20/20; see lesson 5 above) |
| S-2 | S8 − S1 income has its t(9) interval below zero | 0.55 | **wrong**: +0.052 [−0.011, +0.115] |
| S-3 | S8 ≥ 0.5 × S1 income on ≥ 8 of 10 seeds | 0.70 | right (10/10) |
| S-4 | S8 has more births than S1 on ≥ 7 of 10 seeds | 0.60 | right (10/10; e.g. 801: 1,700 against 1,124) |
| P-5 | S1 food-dependent on ≤ 1 of the usable seeds | 0.85 | **wrong**: 2 of 9 (804, 2), primary call, with compass-FD 0 |
| P-6 | S1's window carriage X below 250 per 1,000 on ≥ 8 of 10 | 0.60 | **wrong**: 5 of 10 (X is 0 to 413 per 1,000) |
| P-7 | S8 holds above the no-selection bound at 300 and 599 on ≥ 2 usable seeds | 0.35 | **wrong**: 0 |

The births for S-4 come from `readout.side()` on each arm's committed `seasons.txt`. They are
printed in this report because `readout.py` does not print them.

## Post hoc descriptions (POST HOC, `posthoc.txt`; none of this is scored)

**P1 (POST HOC). The installed a = 64 motif at default scale, in S8 hosts against S1 hosts.**
- It is FOOD-DEPENDENT on **9 of 10 S1 hosts** and on **2 of 10 S8 hosts**. Paired over seeds, its F is
  lower in the S8 host by **−0.609 [−0.804, −0.414]** (t(9)).
- **This is the link scale's instantaneous effect on a default-scale compass, not 600 seasons of
  selection** (adversary F3). Scaling a fixed S1 host ×8 costs about as much: −0.591, −0.594 and −0.788,
  mean −0.66, against the evolved contrast's −0.486, −0.074 and −0.680 on the same seeds.
- Adversary F3's suggested sentence: *"the installed a = 64 motif, at default scale, is masked in ×8
  hosts. The same motif at the arm's scale is not (adversary D/E)."*
- Not a bias gate: the installed unit's bias is 0. What masks it is the ×8 host's own drive on the
  Effectors.

**P2 (POST HOC). The evolved champions, all ten seeds, usable or not.**
- F(S8) − F(S1) = **+0.055 [−0.034, +0.144]**.
- Primary FD: S8 on **0 of 10**, S1 on 2 of 10 (804, 2).
- Compass-FD (ATTRIBUTION): **0 of 10 in both arms**.
- An S8 zero here is not a reading of "no compass". The default-scale control cannot pass on these
  ×8 hosts (F1), so the instrument's ability to see a compass in them was never established.

**P3 (POST HOC). Amendment 3's window readings on all ten S8 seeds.**
- **Held at both seasons: 0 of 10.** The full-operator null rate is 0.005 per seed.
- Five of the 20 single-season readings exceed B: 801 at 300, 804, 805 and 4 at 599, and 2 at 300.
  They are **not read**. For the record (readout adversary F10, `readout-adversary/p3_null.txt`): the
  null's single-season rate on k_planted is 0.035 per reading, so 0.70 of 20 are expected against 5
  observed. P(≥ 5 | null) is 0.0002 with the cells as measured, and 0.053 with each 0/20 cell at its
  upper bound. No sentence rests on it.
- **On several seeds the planted-rooted lineages are gone by 599** (n = 0 on 801, 807, 1 and 2):
  every living genome is bare-rooted.
- **801's gate reading, described** (the coordinator's 21:21 request). At season 300, S8-801 has
  k_bare = 11 against k_planted = 5, so most of its payers are bare-rooted. By Amendment 3's
  full-operator null, that is the crossover transfer of a planted global unit into a bare lineage
  (33% of k under no selection; 92 of 198 on 801's genealogy). Individual genomes were not traced,
  so "de novo arrival" is not excluded genome by genome. It is not needed to explain the count.

**P4 (POST HOC). Own links against host.** S8's window carriers include many that pay on their own
links (for example 75 of 348 on 801, 59 of 301 on 805, 43 of 384 on 4). Few pay in host: 0–9 per arm,
and fewer than 10 on every seed. But the in-host rung (13.35) is a K = 1 host's reading of a K = 1
install, so on a ×8 host it inherits F1. **This is not read as masking of the carriers' compass.**

## What this does to strand 3's explanation

- **Scored:** nothing. VOID answers neither way.
- **Described (POST HOC, readout adversary F4):**
  - *A uniform link scale cannot supply the compass's magnitude relative to its host, because it scales
    both. At ×8, the paying geometry is (±8, 256), as far out in the operator's own units as (±1, 32) is
    at ×1.*
  - This **corrects §1.4's reading as well as this report's first version**, which said "the scale that
    lifts the compass's own gain also saturates the host". A compass scaled *with* the host pays in every
    S8 host tried (groups D and E).
  - The planted founding geometry (±8, 8) is masked in ×8 hosts (group G, 3 of 3), consistent with this.
- **Withdrawn from the first version:**
  - "the evolved hosts mask an installed compass";
  - "§1.4's bias gate, seen in evolved brains".
- **What stays open** (adversary F11): whether selection keeps a compass whose magnitude is within reach
  *relative to its host*. RBT-106's option H (K = 1, a paying planted compass, its control at its own
  scale) is that test, and it is in flight.

**The runner-made `peek-a3-*` files** (adversary F7). Runners on S8-1, S8-2 and S8-805 made them
because §5 step 3's text, as amended at `2524ae6`, told them to. That text conflicted with the
coordinator's 23:15 ruling and was never reconciled. `42e19ef` replaced all three pairs, and only the
header path differs.

## Files

| file | what |
|---|---|
| `readout.txt` | `readout.py`, as registered (SCORED) |
| `S8-SEED/peek-a3-{300,599}.txt`, `regen_a3.sh` | Amendment 3's window readings, regenerated from the checkpoints and committed first (`42e19ef`). Their verdict lines match the runner-made files on S8-1, S8-2 and S8-805 |
| `posthoc.py`, `posthoc.txt` | the POST HOC descriptions P1–P4 |
| per arm | `seasons.txt`, `lineage-last.txt`, `rbt102.txt`, `function.txt`, `function-pc.txt`, `platform.txt` (runners), and the launch-commit `peek-*` (never scored) |
