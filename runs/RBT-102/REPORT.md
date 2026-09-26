# RBT-102: the routed motif's structure under selection, read without the magnitude gate

Status: final, for review. The pre-registration is `PREREG.md` (commit `f1bc9a9`). It was
committed before any arm was restored.

**Headline.** Under selection, across RBT-90 part 2's ten arms, the routed motif's structure is
**not carried at all**:
- 0 carriers among 12,276 genomes saved at birth, in every season of every arm, founders included.
- The pre-registered verdict is **NOT HELD**: X̄ = 0.0000%, t(9) 95% CI [0, 0], against RBT-91's
  drift upper bound p_u = 0.0520%.
- The positive control passed in all ten arms, 40 of 40 each.
- **The inversion count is 0 of 0.** There is no carrier to sign.

The point prediction (X̄ = 0.000%, NOT HELD, confidence 0.65) held, and no falsifier fired. A zero
does not show that selection holds the structure *below* drift. At the depths these arms reached,
drift itself predicts about 0.3 de novo arrivals across all ten (§2.4).

## 1. RBT-80's own data: what it can and cannot say (ruling (a))

**RBT-80's genomes and lineage were never committed, by design.** RBT-80's description says
"genomes and lineage stay out", and `.gitignore` keeps `runs/**` out of the repository except
`.md`, `.py`, `.sh`, `.txt` and `config.json`.

On 2026-09-26 all 122 remote branches were checked, `ckpt/*` included. Every branch carries the same
24 RBT-80 files: nine `config.json`, ten `docs/artifacts/RBT-80-*.txt` readouts and five
`scripts/rbt80_*.py`. `git log --all -- 'runs/RBT-80*'` shows only config commits. The W4b-801
founders (`runs/RBT-23/W4b-801`) are not committed anywhere either. RBT-80 ran before RBT-95, so its
arms do not reproduce from their configs. RBT-91's structural predicate therefore cannot be applied
to RBT-80's populations.

**The stated bound from the committed summaries** (`docs/artifacts/RBT-80-seed{A,B,C}-depths.txt`,
every 10th season plus season 299, three seeds, 479 / 462 / 461 control genotypes measured over 31 sampled seasons each):

- **Control arm:** `carr d2` = 0 and `inverted d2` = 0 in **every sampled season of every seed**.
  No living control individual had a depth-2 path gain of |a| ≥ 16 in *either* direction of travel.
- **The median depth-2 gain** of the living control population is ±0.0 in every sampled season of
  every seed. So at least half of every sampled control cohort had zero net depth-2
  nose→Effector gain.

That bounds control-arm structural carriage at **≤ ~0.5 per season**, and no tighter. The bound
cannot be compared with RBT-91's drift proposal rate (0.042%). The question this ticket asks,
whether the structure was carried at sub-paying magnitude, **is not answerable from RBT-80's
committed data**.

Three limits of those columns, for anyone quoting them:
1. Every carrier count is gated at |a| ≥ 16, and the depth-2 gain is a path sum, not RBT-91's
   single-interneuron predicate.
2. Direction was probed at 2 seeds × 3 s, not the 16 × 15 s reference.
3. Only counts and medians are stored; there is no per-individual `a`.

The seeded and drift inversion counts in the same tables restate RBT-80 at the magnitude gate, so
they are not re-tabulated here (ruling).

## 2. RBT-90 part 2's ten arms (ruling (c))

The data, the config differences from RBT-80's control arm, the rule and the prediction are in
`PREREG.md`. Readouts are committed here:
- `arm-<seed>.txt`: `analyse.py`, one per arm;
- `aggregate.txt`: `aggregate.py runs/RBT-102/arm-*.txt`;
- `supp_partial.txt`: `supp_partial.py`, post hoc.

Every number below re-derives from those files.

**Provenance.** Each arm was restored from `ckpt/rbt-90-<seed>` at 600/600, and only after its
runner's per-seed post on RBT-90 (seeds 4, 807, 805, 1, 7, 801 and 806 by 13:58; 3 and 804 by
14:20; 2 at 14:55 UTC). `analyse.py` also checks `state.json` = 600 before reading. Seed 3 was
resumed in place after a container restart at season 207, which is byte-exact per RBT-93/95 and was
posted on RBT-90 at 12:51. The restored `config.json` of every arm differs from
`part2-dryrun/config.json` only in `seed`, `seasons`/`generations` and `workers`; this was checked
on seed 4 before its analysis. The first arm alone took 5 s wall, and every arm after it took about
1 s of analysis.

### 2.1 Positive control (run first, in every arm)

In each arm, 20 window genomes were sampled with seed 102, and RBT-87's routed motif was installed
at (w = 1, +) and (w = 8, −). The installed motif was detected **40 of 40 in all ten arms**, with no
invalid installs. The bare sampled genomes read 0 of 20. The predicate can say yes on these
genomes, so its zeros are readings.

### 2.2 Carriage and the verdict

| seed | X (seasons 300–599) | window mean depth | seasons with a carrier | births | carriers born | de novo |
|---|---|---|---|---|---|---|
| 1 | 0.0000% | 14.1 | 0/600 | 1274 | 0 | 0 |
| 2 | 0.0000% | 16.3 | 0/600 | 1025 | 0 | 0 |
| 3 | 0.0000% | 14.5 | 0/600 | 1234 | 0 | 0 |
| 4 | 0.0000% | 14.8 | 0/600 | 1147 | 0 | 0 |
| 7 | 0.0000% | 15.1 | 0/600 | 1177 | 0 | 0 |
| 801 | 0.0000% | 14.0 | 0/600 | 1235 | 0 | 0 |
| 804 | 0.0000% | 16.2 | 0/600 | 1138 | 0 | 0 |
| 805 | 0.0000% | 14.8 | 0/600 | 1226 | 0 | 0 |
| 806 | 0.0000% | 17.5 | 0/600 | 1106 | 0 | 0 |
| 807 | 0.0000% | 15.5 | 0/600 | 1114 | 0 | 0 |

X̄ = 0.0000%, SD 0, t(9) 95% CI [0.0000%, 0.0000%]. U = 0 ≤ p_u = 0.0520%, so the verdict is
**NOT HELD** by the pre-registered rule, and 0 of 10 arms have X > p_u. The resolvable-effect
arithmetic in `PREREG.md` §5 does not bind here: no arm has a single carrier-season.

A counting note. `analyse.py` counts founders and births from the names in `lineage.jsonl`. A
genome saved at birth whose individual never appears in a season row (for example, a founder gone
before the first log) is outside those two counts. It is still inside the predicate's pass over
all saved genomes. The ten arms saved 12,276 genomes. Of these, 592 are logged founders
and 11,676 are logged births, which leaves 8 never logged (8 founders absent from every
season row). `supp_partial.txt` reads 0 carriers over all 12,276.

### 2.3 Signing: the inversion count

There are 0 distinct carriers alive in the window, so none is signed: **compasses 0,
anti-compasses 0, undetermined 0.** The reference probe (16 × 15 s) was never needed.
Pre-registered, "fewer than 10 resolved carriers" means the compass fraction is not interpreted.
Here there is no fraction.

### 2.4 Against drift, on one denominator

The denominator is genomes carrying the structure out of genomes present.
- **RBT-91 (drift, k = 19, evolved parents):** 84 of 200,000 = 0.042% [0.0339, 0.0520].
- **Part 2 under selection, living, seasons 300–599:** 0%, in every arm.
- **Part 2 births at RBT-91's depth (17–21 reproductions):** 0 of 1,863 = 0% [0, 0.206].

The matched-depth interval **does not exclude drift's 0.042%**. So this result says selection did
**not hold the structure above** drift's proposal rate. It cannot say selection held it *below*.

The pooled birth count agrees. There were 0 de novo arrivals in 11,676 births. The pre-registered
estimate was about 2 × 10⁻⁵ per birth, which predicts about 0.26 arrivals, so P(0) ≈ 0.77 under
drift alone. The window's mean depth (14.0–17.5) is below RBT-91's 19, which makes drift's own
expectation smaller still.

### 2.5 Supplementary, post hoc, not verdict-bearing: where the structure fails

`supp_partial.py` was written after seven arms read zero and is labelled post hoc. It uses RBT-91's
own helpers, and it asks which half of the routed structure is missing (`supp_partial.txt`, all ten
arms):

| | genomes | fraction |
|---|---|---|
| predicate applicable (both wheel noses and both drive Effectors present) | 12,276 / 12,276 | 100% |
| some global unit drives both Effectors with the same sign (**out-half**) | 11,044 | 90.0% |
| some global unit takes a link from **at least one** wheel nose | 956 | 7.8% |
| some global unit takes links from **both** wheel noses, any sign | **0** | 0% |
| in-half (both noses, opposite sign) | 0 | 0% |
| both halves on one unit (= the predicate) | 0 | 0% |

The zero is not missing anatomy: every genome has the noses and the Effectors. The output side of
the motif is nearly universal, because a global unit fanning out to both drive wheels with one sign
is simply what these drivers are. The barrier is on the input side. Fewer than 1 genome in 12 wires
even one wheel nose into the global brain, and none wires both. Under selection in this economy,
wheel-nose input to the global brain is rare, and it never occurs on both sides.

This is descriptive. It says where the zero comes from and does not explain why. It carries no
verdict.

### 2.6 What this does and does not show

- **Shown.** In ten founding populations under selection, in the post-RBT-95 dense foraging
  economy, the routed compass structure is never carried at any magnitude. So RBT-80's
  magnitude-gated 0.000 on its control arm has a structural counterpart here: there is no
  sub-paying structure for a magnitude barrier to be withholding. The package's question ("does
  selection hold the structure at sub-paying magnitude above drift's proposal rate?") is answered
  **no**.
- **Not shown.**
  - That selection suppresses the structure below drift: the interval in §2.4 includes drift's rate.
  - Anything about RBT-80's own populations. Part 2 is not RBT-80's control arm: its founders are
    random rather than evolved W4b-801 backward drivers, food regrows, and it runs 600 seasons
    (`PREREG.md` §1).
  - Anything about seeded or drift arms, which part 2 does not have.
- **For the programme.** The binding structural barrier in this economy is the second nose-to-global
  link. This is post hoc (§2.5), so it is a candidate for a pre-registered follow-up, not a
  finding.
