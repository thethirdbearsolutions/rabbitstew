# RBT-84 — Attractor or non-divergence: a foraging arm from a second founding population, autopsied along its whole descent DAG

**Run:** `runs/RBT-84/forage-807`, holistic, 600 seasons, clean exit 08:25 UTC.
**Champion:** `he988`, born season 589. 10 parts, 37 units, 38 links.
**Pre-registration:** ticket comment 06:44, amended 06:46 (outcome NOT APPLICABLE) and 07:46 (four
seams: A's middle band, distinct genotypes, the whole DAG, wiring-vs-lesion). Both amendments were
posted before this champion existed. The adversary accepted all four at 08:50 and added a fifth
reading requirement, answered in §4.

**One flag changed from `forage-801`:** `--seed 807`. Nothing was tuned.

---

## 0. Scorecard

| prediction | pre-registered | confidence | outcome |
|---|---|---|---|
| **A** — ≤ 2 saved bests carry a linked oscillator | oscillator drive is discarded | 0.80 | **FALSIFIED, decisively** — 36 distinct genotypes, 45 of 59 snapshots; 65.6% of all births |
| **B** — non-divergence vs attractor on the composite | 0.50 non-divergence | 0.50 | **NOT APPLICABLE** — the champion does not carry the composite. The outcome amendment 1 added. |
| **C** — drive is an effector, not a global neuron, not an oscillator | effector | 0.75 | **FALSIFIED on the lesion reading** (the scoring rule fixed at 07:46); the only resolvable subsystem is the global brain. The "not an oscillator" clause survives. Wiring says twelve link-driven effectors; §5 reports the disagreement rather than resolving it. |
| **D** — the champion does not beat its own gait (\|t\| < 2.5) | RBT-39's null | 0.92 | **HELD, 4 of 4 bests** — t = −1.68, −0.88, +0.71, −0.56 |

Two of four predictions falsified, one not applicable, one held. **The arm's own headline is not any
of the four**: it is that RBT-28's "no oscillator" finding does not survive a second founding
population, and that the composite structure the ticket was written around comes apart into two
halves that go opposite ways along the same lineage.

---

## 1. The seed and its founders (item 1, stated before the run)

The classifier is `runs/RBT-28/adversary_founders.py::wiring`, imported rather than reimplemented.

| seed | founders | link-driven effector | linked oscillator | **both (drive, no osc)** | base rate |
|---|---|---|---|---|---|
| **801** — RBT-28's five arms | 60 | 40 | 13 | **29** | 0.483 |
| **807** — this arm | 60 | 38 | 15 | **29** | 0.483 |

Reproducing 29/60 at seed 801 exactly is the calibration that makes the two numbers one measurement.
**0 of 60 body signatures are shared** between the populations. The base rates coinciding at 0.483
is luck and is convenient: no difference in outcome here can be blamed on a different base rate.

Readout: `runs/RBT-84/founder_base_rate.txt`.

**One founder has no lineage row.** `h0-43` died before its first logged season, so `lineage.jsonl`
carries 59 of the 60. Every base rate quoted in this report is over the **60 regenerated from the
seed** — the same source as the pre-registered 29/60 — with the 59-founder figure printed beside it
in `runs/RBT-84/entry_steps.txt`. They differ in the third decimal and no verdict turns on it.

---

## 2. Prediction A — FALSIFIED, and in the direction neither side predicted

Scored on **distinct genotype names** among the saved bests after season 0, per seam 2, with the
snapshot count beside it and the birth-level rate as the base.

| quantity | seed 807 (this arm) | seed 801 (RBT-28's five, recounted) |
|---|---|---|
| saved bests after season 0 | 59 | 295 |
| snapshots carrying a linked oscillator | **45** | 1 |
| **distinct genotypes carrying one** | **36** | **1** (`he694`, RBT-16) |
| every genome saved at birth | 999 | not available (no genome archive) |
| births carrying a linked oscillator | **655 — 65.6%** | — |
| the population's own founder rate | 25% | 22% |

Bar: ≤ 2 confirms, 3–7 is NOT CONFIRMED, ≥ 8 falsifies. **36.**

**My counter reproduces the adversary's 1 of 295 exactly** (per run: 0, 1, 0, 0, 0; the one is
`he694`), so the contradiction is between the populations, not between the instruments.

**The direction matters more than the falsification.** Seed 801 discarded oscillator drive — 1
genotype in 295. Seed 807 *acquires* it: from 25% of founders to **65.6% of all 999 births**. These
are not two draws from one process. RBT-28's "no oscillator" half — the half both the ticket and I
treated as the stronger of the two — **is one founding population's number.**

Readout: `runs/RBT-84/oscillator_rate.txt`.

---

## 3. The descent DAG, and the multi-path fix that was load-bearing

| | |
|---|---|
| ancestors reached | **138** |
| founders reached | **5** |
| crossover steps on the DAG | **37** |
| genomes missing from disk | **0** |
| following `parents[0]` instead | would have reached **1** founder and called it "the founder" |

Seam 3 was not hypothetical. Of the five founders this champion descends from, **three carry the
composite structure and two do not**; under the old tracer the verdict would have turned on which
parent the ecology happened to list first.

This is the first time the question could be asked at all. RBT-28 had no genome archive;
RBT-27's genome-at-birth saving is what makes the path reconstructable.

Readouts: `runs/RBT-84/descent.txt`, `runs/RBT-84/halves.txt`.

---

## 4. Prediction B — NOT APPLICABLE, and the composite comes apart

`he988` has **twelve link-driven effectors AND two linked oscillators**, so "carries the structure"
is False entirely on the oscillator clause. **B scores NOT APPLICABLE** — the outcome amendment 1
added at 06:46, on partial output, before this champion existed. Without it the rule would have
printed `ATTRACTOR` for a lineage in which the composite is absent at the champion.

Measured separately along the same 138-ancestor DAG, **the two halves go opposite ways**:

| half | champion | founders reached carrying it | ancestors lacking it | founder base rate | random-assembly expectation (base^5) | import steps | acquisition steps |
|---|---|---|---|---|---|---|---|
| **a link into a live effector** | **True** | **5 / 5** | **0 of 138** | 0.633 | **0.102** | **0** | **0** |
| no outgoing oscillator link | False | 3 / 5 | 106 of 138 | 0.750 | 0.237 | 7 | 2 |
| *(the composite)* | False | 3 / 5 | 106 of 138 | 0.483 | 0.026 | 7 | 2 |
| *(an outgoing oscillator link)* | **True** | 2 / 5 | 32 of 138 | 0.250 | 0.001 | **10** | **0** |

The random-assembly column and the import/acquisition split are the adversary's 08:50 requirement,
answered in `runs/RBT-84/entry_steps.py`. An IMPORT step is one where the child carries the property,
at least one parent does and at least one does not — it came across by crossover. An ACQUISITION step
is one where no parent carried it — it appeared there, by mutation.

**Effector drive was in every founder this lineage reaches and in all 138 of its ancestors — never
acquired, never imported, never lost.** That is non-divergence on the half RBT-28 could only call
suggestive. Read honestly against the expectation the adversary asked for: five founders all carrying
it has probability 0.102 under random assembly, so **on the founders alone this is a p ≈ 0.10 result,
not a p ≈ 0.001 one.** The 0-of-138 figure is *not* an independent-draws test — ancestors are a
lineage and heredity makes them correlated, so 0.633^138 is meaningless here. What 0 of 138 does say
is the thing a base rate cannot: **no step anywhere in this DAG ever lost it.**

**And the oscillator arrived entirely by import.** Ten crossover imports, **zero mutation
acquisitions**, in a lineage whose population went from 25% to 65.6% oscillator-linked at birth. Along
this path the rise is shuffling, not invention. One lineage is one lineage — this does not establish
it for the population — but it is a mechanism claim that no run before the genome archive could make,
and it is the one I would test next.

---

## 5. Prediction C — falsified on the lesion reading; the two readings disagree, as ruled

Per seam 4 (fixed 07:46): **C is scored on the lesion reading**; the descent path is classified by
wiring; a disagreement is reported, not resolved.

### The champion's whole subsystems, 64 draws (the pre-registered n)

| mode | items | costs vs intact | paired t | work |
|---|---|---|---|---|
| intact | 2.781 ± 0.284 | — | — | 14.6 |
| `no_osc` | 2.562 ± 0.296 | +0.219 | +0.57 | 10.4 |
| `no_local` | 2.453 ± 0.270 | +0.328 | +0.87 | 10.2 |
| `no_env` = `no_smell` | 2.281 ± 0.242 | +0.500 | +1.36 | 13.5 |
| **`no_global`** | **1.438 ± 0.190** | **+1.344** | **+4.25** | 7.8 |

Power at n = 64: |t| ≥ 2.5 resolves **+0.92 items or larger**. **Exactly one subsystem clears the
bar and it is the global brain**, costing nearly half the champion's intake.

C predicted "an effector, **not a global neuron** and not an oscillator". The clause that survives is
"not an oscillator": `no_osc` costs +0.219 at t = +0.57, nowhere near resolvable. The clause that
fails is the one about global neurons. **C is FALSIFIED.**

### The same pass along the lineage — the ticket's item 2, with paired t

`forage_lab.py`'s whole-subsystem summary prints the cost but not the paired t, which item 2 asks
for, so the six modes were re-run at 64 draws on all four bests
(`runs/RBT-84/subsystems_g{100,300,500}.txt`, `champion_subsystems.txt`).

| paired t vs intact | g100 | g300 | g500 | **g590 (champion)** |
|---|---|---|---|---|
| `no_env` | −0.83 | −0.11 | +0.57 | +1.36 |
| `no_smell` | −0.83 | −0.11 | −0.39 | +1.36 |
| `no_osc` | +0.63 | −0.69 | **+nan** (64/64 zeros) | +0.57 |
| `no_local` | −0.19 | +0.19 | +0.57 | +0.87 |
| **`no_global`** | +1.29 | **+6.02** | **+6.86** | **+4.25** |
| *resolvable at \|t\| ≥ 2.5* | +0.63 | +0.70 | +0.69 | +0.92 |
| *draws needed for a 25% effect* | 280 | 257 | 133 | 113 |

**One subsystem is resolvable at any point in this lineage and it is the same one every time.** The
global brain is not load-bearing at g100 (+0.281 items, t = +1.29, under the bar) and is decisively so
by g300 (+1.281, t = +6.02), staying there through g590. Everything else — smell, the oscillator, the
local per-part neurons — sits in the unresolvable band at all four bests, and **this report claims
nothing about any of them in either direction.** At n = 64 the instrument cannot test a 25% effect on
any of the four; that is the line RBT-28's adversary forced the script to print and it is doing its
job here.

`no_osc` at **g500 is a provable no-op**: +0.000 items with **64 of 64 paired differences exactly
zero**, because that best's oscillator carries no outgoing link. The `nan` is the correct output for
a zero-variance difference, not a failure — and it is what RBT-38's rule (no lesion effect without a
per-seed list and a zero count) exists to make visible.

### Where wiring and lesion disagree, and why they are not actually in conflict

Wiring says **twelve link-driven effectors** — C's prediction, on the classifier the base rate uses.
Lesion says **the global brain**. Both are right about the same robot, and the wiring shows why:
**every one of the twelve effector links originates at global unit 34 (`tanh`) or unit 35
(`integrate`)**, and units 34/35 are the sole destination of both smell sensors and both oscillators.
The effectors are the output stage; the global neurons are the only thing driving them. Lesion the
output and the other eleven effectors carry it; lesion the source and the robot loses 48%.

**This is a defect in the classification, not in the robot.** `wiring()` asks "is there a link into a
live effector", which every multi-effector body with a central driver satisfies, and it cannot
distinguish a body whose drive *is* its effectors from one whose effectors are a fan-out. RBT-28's
29/60 base rate and its "four of five drive through an effector" are both wiring numbers and inherit
this. I am not proposing a replacement here; I am recording that the composite RBT-84 was built
around is measuring something weaker than it reads as.

---

## 6. Prediction D — HELD, 4 of 4

RBT-39's trajectory-preserving null: replay each best's own recorded geom path against the layouts
the world could equally have dealt it. A champion that "forages" rather than mows should beat its own
gait.

| best | body | items | own-gait null | paired t | verdict |
|---|---|---|---|---|---|
| g100 | 2 parts, 8 units | 1.203 ± 0.173 | 1.416 | **−1.68** | indistinguishable |
| g300 | 2 parts, 10 units | 1.406 ± 0.206 | 1.554 | **−0.88** | indistinguishable |
| g500 | 2 parts, 12 units | 1.922 ± 0.281 | 1.781 | **+0.71** | indistinguishable |
| **g590 (champion)** | **10 parts, 37 units** | **2.781 ± 0.284** | **2.890** | **−0.56** | indistinguishable |

**Twenty champions have now been read against their own gait and not one has beaten it.** Sixteen
before this arm, four here, across two founding populations and a ten-part body that eats more than
twice what the earlier ones do. The champion is better at foraging than its ancestors and it gets
there **entirely by moving differently**, not by steering toward food once moving.

The point-robot floor `2 × eat_radius × density` = 0.297 items/m is printed in the readouts **for
reference only**; RBT-39 retired it in both directions and no verdict here uses it. The champion's
own swept corridor is 1.09–1.14 m against the 0.70 m that floor assumes.

---

## 7. What I got wrong in the running of this arm

Four process failures, all of them mine, reported because the programme's value is in the catalogue.

1. **Launcher.** The first attempt used `nohup … &`, which this harness does not track; it was killed
   at season 66 of 600. Diagnosed before relaunch (not disk — 30 G free; not memory — 15.5 G free, no
   OOM; no traceback) and relaunched under the harness's own background mode, where it ran at a steady
   6.5 s/season to a clean exit.
2. **Two wrong ETAs in a row**, 08:15 and then 10:35, the second measured on the *starved* `nohup`
   process. The real figure under the working launcher was 6.5 s/season.
3. **I missed the adversary's four-seam post for 43 minutes** because the run had died and I tunnelled
   onto the diagnosis, skipping the activity check that was step 3 of my own poll. A dead run is when
   the other channel matters most. The poll is now ordered cheap-check-first regardless.
4. **The worst one: I measured my own plumbing twice and destroyed work on the second reading.** I
   reported the champion's per-unit table as costing 4–5 hours and being unaffordable. It costs about
   40 minutes. The "no mode completed in a 110 s window" observation was a `grep -v WARNING` in
   `sweep.sh` block-buffering its output to a file, not slow modes — `forage_lab.py` flushes every
   row. Then, going to kill the process, I checked its progress with a regex that did not match the
   row format, read "0 modes complete", and killed it at 26 of 34, about two minutes from the end.
   Then I relaunched to the same path without saving the partial, overwriting it. Corrected on the
   ticket at 08:58 and the table obtained. The rule I take from it: **before reporting that something
   did not happen, verify the channel that would have shown it.**

The readout headers in `champion_subsystems.txt` and `subsystems_g*.txt` carry the superseded "4–5 h"
cost claim in their comment line; the numbers beneath are unaffected and the claim is withdrawn here
and on the ticket.

---

## 8. What this arm settles, and what it does not

**Settles:**

- **RBT-28's "no oscillator" finding is one founding population's number.** 1 of 295 distinct at seed
  801; 36 of 59 at seed 807, with 65.6% of births. The two populations do not merely differ in degree.
- **Along one lineage, oscillator drive spread by crossover import, not by mutation** — 10 imports, 0
  acquisitions.
- **The composite "link-driven effector and no linked oscillator" is not a single thing.** Its halves
  behave oppositely on the same 138 ancestors: one never lost, the other lacking in 106.
- **Twenty champions, none beats its own gait.**

**Does not settle:**

- **Effector drive as an attractor.** One champion at a 0.483 base rate is a coin flip, as the
  pre-registration said up front. Five founders all carrying it is p ≈ 0.10 under random assembly.
  The 0-of-138 is not an independent test.
- **Whether the import mechanism generalises.** One lineage in one run.
- **Any lesion effect below +0.92 items on the champion.** At n = 64 the instrument resolves that and
  no better; 25% of intake (0.70 items) needs about 113 draws. Everything except `no_global` sits in
  the unresolvable band, and this report claims nothing there in either direction.
- **Why seed 807 acquires oscillator drive and seed 801 discards it.** Two populations is two points.

**The one thing I would do next**, and it follows directly: the import-versus-acquisition split over
*every* birth in the run rather than one champion's DAG. `genomes/` and `lineage.jsonl` already hold
it; the machinery is `entry_steps.py` with the BFS replaced by a full scan. If the population-wide
number is also import-dominated, the 25% → 65.6% rise is recombination redistributing what the
founders brought, which is a claim about the ecology's operators rather than about foraging.

---

## 9. Reproduction

```
# the run (one flag changed from forage-801: --seed 807)
rabbitstew ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers 4 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random \
  --random-start --score food --seed 807 --out runs/RBT-84/forage-807

python3 runs/RBT-84/founder_base_rate.py 801 807        # item 1, the base rates
python3 runs/RBT-84/oscillator_rate.py  runs/RBT-84/forage-807 holistic    # Prediction A
python3 runs/RBT-84/descent.py          runs/RBT-84/forage-807 holistic    # Prediction B
python3 runs/RBT-84/halves.py           runs/RBT-84/forage-807 holistic    # the two halves
python3 runs/RBT-84/entry_steps.py      runs/RBT-84/forage-807 holistic    # import vs acquisition
for g in 100 300 500 590; do            # Predictions C and D
  python3 scripts/forage_lab.py        runs/RBT-84/forage-807 holistic $g 64 120 > runs/RBT-84/lab_g$g.txt
  python3 runs/RBT-84/champion_subsystems.py runs/RBT-84/forage-807 holistic $g 64 120 > runs/RBT-84/subsystems_g$g.txt
done
```

Do not pipe `forage_lab.py` through `grep`; it block-buffers and the run looks hung. See §7.4.

### The package reproduces, and this is checked rather than asserted

`.gitignore` keeps run artifacts out of the tree (`runs/**`, with `.md`/`.py`/`.txt`/`config.json`
allowed) on the repo's standing argument that a seeded run is re-derivable. RBT-71's adversary has
just held a package defective for being unreproducible, so the argument is tested here:
`runs/RBT-84/reproducible.py`, readout `runs/RBT-84/reproducible.txt`.

| check | result |
|---|---|
| the 60 founders, regenerated from the committed `config.json` alone | **60 of 60 identical** |
| the run itself: every genome the killed first attempt saved, against the completed run's genome of the same name | **174 of 174 identical** |

Both comparisons exclude the mutable `record` field (energy, age, born, evals) — the ecology's live
bookkeeping, absent from a freshly synthesised genome and read by nothing in this arm. **Including
it, all 60 founders differ**, which is stated so the number cannot be quoted as a bare "byte-identical".

**What check 2 establishes and what it does not.** The first launch was killed at season 66 (§7.1)
and was kept; it saved 174 genomes, and all 174 come back identical in the completed run. So the
600-season run is a function of the seed and not of the wall clock — **over its first 66 seasons of
600**. The remaining 534 are not covered by any check here; covering them means re-running the arm,
which is 65 minutes and which I have not done. The claim in this report is the narrow one.

The killed attempt itself lives in this session's scratchpad, not in the tree — **correcting what I
told the coordinator at 07:17**, where I said it was kept at `runs/RBT-84/forage-807.killed-at-66/`.
It is 73 M and `.gitignore` would exclude it in either place; check 2 is the reason to mention it at
all, and check 2's readout is committed even though its input is not.
