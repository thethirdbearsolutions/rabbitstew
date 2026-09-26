# RBT-102: the routed motif's structure under selection, read without the magnitude gate

Status: final, amended after the adversary (coordinator ruling on RBT-102, 16:55 UTC). The
pre-registration is `PREREG.md` (commit `f1bc9a9`). It was committed before any arm was restored.
The adversary's probes are in `adversary/` (PR #143).

**Headline, as ruled.** The count stands. The verdict is **not informative about selection at
this n**.
- 0 carriers among 12,276 genomes saved at birth, in every season of every arm, founders included.
  This re-derives exactly on all ten arms (`adversary/reproduce.txt`).
- The pre-registered rule returns NOT HELD: X̄ = 0.0000%, t(9) 95% CI [0, 0], against RBT-91's
  drift upper bound p_u = 0.0520%. **Pure drift returns the same verdict.** The adversary built a
  drift null matched to these arms: each arm's own founders and pedigree, replayed with no
  selection (`adversary/replay_null.txt`). It expects **0.93 carriers** in 12,276 genomes and reads
  **zero in 81 of 100 replays [72, 87]**. The pre-registered rule says NOT HELD on **91 of 100**
  pure-drift replays. So the zero cannot tell selection removing the structure from drift not
  producing it.
- **A zero would be informative at about 184,000 genomes, 150 arms of this size**
  (`informative_n.txt`). That is where P(0 | matched drift) falls below 5%. Across the null's Wilson
  interval it is 123,000–282,000 genomes (100–230 arms).
- The instrument sees carriers: natural drift carriers, installed motifs, and 24 carriers planted
  end to end in a real arm (`adversary/detect.txt`). The result is not "undetectable".
- The positive control passed in all ten arms, 40 of 40 each.
- **The inversion count is 0 of 0.** There is no carrier to sign.

The point prediction (X̄ = 0.000%, NOT HELD, confidence 0.65) held, and no falsifier fired. That
prediction was right for the reason the adversary names: at these depths, from these founders, the
structure is rarely proposed at all. The pre-registration did not include a matched drift null, so
it did not see that its rule could not separate selection from drift here (§2.7).

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

**Amended (adversary F4).** RBT-91's 0.042% comes from different parents. Its evolved pools already
wire wheel noses into the global brain, and part 2's random founders do not. The drift rate matched
to these arms' own founders and pedigrees is **0.0076% of genomes** (`adversary/replay_null.txt`),
about 5.5 times lower. Setting 0.042% beside part 2 therefore adds nothing, and the pre-registered
p_u was built on the wrong population. The verdict does not move, since U = 0. Against the matched
rate, 0 of 12,276 is the modal drift outcome (81%).

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

The zero is not missing anatomy: every genome has the noses and the Effectors. The output half is
nearly universal. Fewer than 1 genome in 12 wires even one wheel nose into the global brain, and
none wires both.

**Withdrawn as a barrier (adversary F5, coordinator ruling).** The same counts under the matched
drift null, with no selection, fall in the same range:
- at least one nose into a global unit: mean 1,244 (range 501–2,288) against 956 real;
- both noses into one global unit: mean 7.7, and **0 in 35 of 100** drift sets;
- out-half: 11,089 against 11,044.

The rarity of nose-to-global input is set by the mutation operator and the random founders. It is
not set by selection or the economy. The table stays as a description of these genomes and carries
no verdict. A per-arm pattern is visible (seeds 1, 4 and 805 below drift, seed 807 above), and only
a follow-up pre-registered against this null could test it.

### 2.6 What this does and does not show

- **Shown.** In ten founding populations under selection, in the post-RBT-95 dense foraging
  economy, 0 of 12,276 genomes carry the routed compass structure at any magnitude. The instrument
  can see it (adversary F2).
- **Not shown: anything about selection.** The package asks whether selection holds the structure
  at sub-paying magnitude above drift's proposal rate. **At this n, that question is not answered.**
  A matched drift null reads zero 81% of the time, and the pre-registered rule says NOT HELD on 91%
  of pure-drift replays. This result neither supports nor contradicts "selection does not carry the
  structure". About 184,000 genomes (roughly 150 arms) would be needed before a zero means anything.
  Deeper runs, or founders that already wire noses into the global brain, would raise drift's rate
  and lower that n. Either would have to be pre-registered against a matched replay null.
- **Also not shown.**
  - Anything about RBT-80's own populations. Part 2 is not RBT-80's control arm: its founders are
    random rather than evolved W4b-801 backward drivers, food regrows, and it runs 600 seasons
    (`PREREG.md` §1).
  - Anything about seeded or drift arms, which part 2 does not have.
- **For the programme.** RBT-102 contributes nothing to strand 3's question about selection (the
  coordinator's ruling). The §2.5 "barrier" is withdrawn.

### 2.7 What the pre-registration missed

The rule compared carriage under selection with an **unmatched** drift rate, one from different
parents. It had no replay null on the arms' own pedigrees, so it could not show that NOT HELD was
also drift's modal verdict (91%). The PREREG §5 arithmetic implied as much: HELD needed at least 4
arms at about 1.7% or more, which is about 220 times the matched drift carriage. I did not draw that
conclusion before the data. Any follow-up should pre-register against the adversary's
`replay_null.py`, with n set from `informative_n.py`.
