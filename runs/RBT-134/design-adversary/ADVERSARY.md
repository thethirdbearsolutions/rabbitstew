# RBT-134 design adversary: review of PR #538 (pre-registration draft r1)

**Reviewed:** `runs/RBT-134/DESIGN.md`, `decompose_arrivals.py`, `power.py` and their outputs at head
`8c271a6902132df25f03e4c6424faaf21992d119`. I also read the ticket (RBT-134, parent RBT-115),
`docs/rbt-91-weight-scale-decision.md`, `ERRATA.md` (H41), `runs/RBT-104/PREREGISTRATION.md` and
`drift-reach-k8.txt`, `runs/RBT-113/{REPORT,PREREGISTRATION}.md` and `power.txt`, `runs/RBT-116/{steer,planters}.py`,
`rabbitstew/{genetics,synthesis,brain}.py` and `runs/RBT-91/structural_rate.py`.

**Not read:** any RBT-129 run, ckpt or epa data, and `ckpt/rbt-113-O1`. No candidate condition was run.

**What I re-computed.** All of it read only RBT-91's published default and σ = 4.0/1.6 conditions, plus arithmetic.
Scripts and outputs are in this directory.

## Verdict: **REGISTER AFTER FIXES**

The instrument and the overall shape are sound:
- the decomposition reproduces byte for byte;
- the rung switch is justified and conservative;
- `power.py` reproduces;
- A0's and P1's exclusions from the family survive.

Four things must change before registration:
1. The slope bound is wrong for `abs`, and control I3 as written would VOID the default operator's own arrivals.
2. The `sign` probe artefact is a window, not a point. I6 does not catch it, and it also carries part of the
   background clause.
3. Two of the four family members (P4 and P5) are decided NULL by the design's own arithmetic. That leaves the
   "no PASS bounds the encoding" reading unsupported.
4. The holistic duplication cut and the H-predicate miss a compass route that needs no differencing unit.

None of these needs a redesign. Each fix is a rule edit, a re-priced value or a scoping sentence.

---

## MUST

### M1. The slope bound sets max f′(`abs`) = 0. That is wrong, nine committed arrivals violate it, and I3 would VOID B0.

`brain.py:85` computes `abs` as `tanh(|x|)`. That function is even about **0**, but the probe reads it at
**b_k**, where the slope is `sign(b_k)·sech²(b_k)`. Its magnitude can be up to 1, not 0.

The committed decomposition shows `abs` arrivals with a non-zero response as is, above the bound of
`|product| × 0`:

```
$ python bound_check.py decompose_arrivals_{baseline,1.6,4.0}.txt        (bound_check.txt)
decompose_arrivals_baseline.txt n= 84 bound violations: 6
   VIOLATION ('W4b-801-bests', '87067', 'abs', '+0.17', 0.3784, 0.4143)  ...
decompose_arrivals_1.6.txt n= 63 bound violations: 2
   VIOLATION ('P-801-final60', '36003', 'abs', '-0.49', 3.5064, 7.8)
decompose_arrivals_4.0.txt n= 66 bound violations: 1
   VIOLATION ('P-801-final60', '36003', 'abs', '-1.17', 1.0839, 41.6038)
   slope bound as committed: {6.2831: 38, 12.5236: 25, 24.7145: 16}  | with f'max(abs)=1: {6.2831: 43, 12.5236: 29, 24.7145: 20}
```

**Consequences.**
- §9 I3 reads: "every arrival's |a| ≤ |product| × max f′ (a single violation means the probe is not what §1 says)".
  As written, **B0 fails I3 on 6 of its own 84 arrivals and the instrument VOIDs itself.**
- **P2's bound at a = 32 is ≤ 29, not ≤ 25.** I3's "P2's k ≤ 25" would VOID a legitimate P2 count of 26–29.
- What survives: A0 stays bounded at 0 at every rung, and P1 at ≤ 2 at a = 32. The corrected counts are unchanged
  for those two. **A0 and P1 correctly stay outside the family.**
- §1 point 3 and §0 item 2 count `abs` among the "deaf" functions, so the "25 zero-response arrivals" grouping must
  be restated. On these arrivals `abs` is attenuated, not deaf.

**Fix.** Set max f′(`abs`) = 1 in `decompose_arrivals.py`, then regenerate the outputs and every bound in §0, §2.1,
§2.2, §9 I3 and §10 (P2 ≤ 29).

### M2. The `sign` artefact is a window |b_k| < |probe input to k|, not |b_k| < 1e-9. It is in the primary and in the background.

In the probe's ±drive pair, `sign(b_k ± δ)` flips whenever |b_k| < δ. Here δ = |u_L − u_R|·0.005 is the net nose
drive into k. I set b_k on committed `sign` arrivals to values inside and outside δ:

```
$ python sign_probe.py <PR#538>/decompose_arrivals.py --readout x        (sign_probe.txt)
sigma=0.4 W4b-801-bests 49535 |input to k at probe|=0.0166  b_k->|a|: 1.00e-09:71.6 ... 1.64e-02:71.6  1.67e-02:0.0
sigma=4.0 W4b-801-bests 40182 |input to k at probe|=0.0748  b_k->|a|: 1.00e-09:62.3 ... 7.40e-02:62.3  7.55e-02:0.0
sigma=4.0 P-801-final60 15505 |input to k at probe|=0.0557  b_k->|a|: 1.00e-09:93.7 ... 5.52e-02:93.7  5.63e-02:0.0
```

At σ = 4.0 the window is up to 0.075 wide, and every reading inside it is far above 12.52. I6 ("|b_k| < 1e-9")
would count such an arrival as ≥ rung. Because f′(`sign`) = 0 in the bound, it would also trip I3 and VOID.

- P2 carries 9 `sign` arrivals.
- P3 redraws biases toward N(0, 0.5), which puts more mass inside the window.

**The same artefact carries part of the background clause.** I re-read RBT-91's committed background lineages
(first 5,000 per pool) and re-probed each structureless hit with every `sign` unit read as `tanh`:

```
$ python bg_sign.py 0 4      (bg_sign_0.4.txt)   26 of 9,996 reproduced; 6 of 26 fall below 6.8664 without sign units
$ python bg_sign.py 4.0 4    (bg_sign_4.0.txt)  164 of 9,994 reproduced; 18 of 164 fall below 6.8664
```

So 23% of B0's background is `sign`-carried. An operator that moves biases toward 0 (P3's reset, A0 at default
links) inflates the background clause through a probe artefact. That can turn a real PASS into
MOVES-WITH-BACKGROUND, which is a wrong answer for the reason that matters most.

**Fix.** Define the artefact by its mechanism: flag any probe in which some `sign` unit's settled output differs
between the +drive and −drive runs.
- Primary: such an arrival is printed and **not counted**.
- Background: register the clause on lineages with no flagged `sign` unit, and print the all-lineage rate beside it.
- Apply the same flag to I3.
- B0 must still reproduce 26 of 9,996 on the unflagged definition's companion column.

### M3. P4 and P5 are decided by the design's own arithmetic, so the family and the both-ways reading must change.

§6.2's rule is: "A0 and P1 are decided by the slope bound. Spending a test on a question already answered from merged
data would only weaken the others." The same rule applies to two of the four family members.

- **P5.** The event's links are |N(0,1)|, followed by the default walk for the remaining mutations. Its own link
  product reaches a = 32 with probability 5 × 10⁻⁷ per event:

  ```
  $ python p5_ceiling.py                        (p5_ceiling.txt)
  rung 12.5236: P(product >= rung | event) = 5.00e-07; expected lineages over 18,169 events = 0.01
  product quantiles: median 0.471  p99.9 4.869  max 13.97
  ```

  §10 gives P(NULL) = 0.8. By arithmetic it is above 0.999, at unit slope.

- **P4.** Take the design's own log-multiplier sd of 1.46 (§2.1). Apply it to every default arrival's product at the
  corrected max f′ and at a unit downstream slope (the best case):

  ```
  $ python p4_ceiling.py                        (p4_ceiling.txt)
  rung 12.5236: expected k <= 2.96 (unit downstream slope, sd 1.46)
  ```

  P(k ≥ 7 | Poisson 2.96) ≈ 0.035 even before the bias walk. As is, the median arrival keeps about 5% of its unit-slope
  response (median as-is 0.037 against unit 0.74; `_baseline.txt:94,103`). So P4's realistic power is near 0.

  P4 is also not "circuit-wise". At fan_rate 0.2 on each of the 4–12 global neurons, every neuron-touching link in the
  brain gets a log-normal multiplier with sd 1.0–1.46 over 19 mutations. That is a whole-brain widening, so "background
  up less than P2's" is doubtful.

**Why it is a MUST.** With P4 and P5 dead and P2 capped by a bound, the family's "no PASS" outcome (P = 0.6 in §10)
is largely fixed in advance. §10's reading of it ("no step distribution on them separates the two", "it bounds the
encoding") would then be a conclusion produced by the design's choice of values, not by data.

**Fix (either way works).**
- (a) Move P4 and P5 to checks beside A0 and P1, with their computed ceilings as I3-type bounds. Then Holm is over
  m = 2 (P2, P3), with k ≥ 6 and 5. Or:
- (b) Re-value them pre-data so each has a stated prior chance of k ≥ 7, priced the same way. Examples: fan_sigma
  large enough that the expected k at unit slope is ≥ 15; P5 magnitudes at a stated multiple. Then keep m = 4.

In both cases, rewrite §10's both-ways statement:
- separate "all NULL" from "moves only with background";
- scope it to "these switches at these values, at depth 19";
- drop "no step distribution separates the two".

### M4. The holistic duplication cut and the H-predicate miss a compass that needs no differencing unit.

§2.3 is right that a **global** unit's input from a duplicated nose is summed over instances
(`synthesis.py:324-332`), so the difference cancels. But the compass does not have to be a global differencing unit.

Local-brain links resolve **per instance** (`synthesis.py:302-321`). A sensor-bearing node can be instanced twice at
lateral positions: two `connections` from a parent to the same child, whose `position` is per connection
(`genetics.py:259-262`). Each instance then carries its own nose → own Effector loop. Uncrossed or crossed
sensor-to-motor wiring on the two sides is a steering circuit in which the **body** does the differencing (the
Braitenberg vehicle). It needs no mirror flag, and both pools have mirroring off (`mirror_rate 0.0`, checked for
RBT-19 P-801 and RBT-113 C).

The H-predicate ("a global non-sensor unit … from food sensors on two distinct single-instance Nodes") cannot see this
route. So:
- H1's STRUCTURE-BOUND verdict says nothing about it;
- §2.3's "a duplication operator cannot propose the compass under this encoding" is not shown.

**Fix.** Either:
- add an H-predicate arm: a node with ≥ 2 instances, each carrying a `food` sensor with a local path to an Effector
  on the same instance. Laterality is left to H2, as for the main arm. Report its counts per condition, and keep
  duplication cut only if that arm is 0 under B0 and is shown not to rise under recursion; or
- scope §2.3 and the STRUCTURE-BOUND wording to "the global differencing route", and name the per-instance route as
  untested.

---

## SHOULD

**S1. The background HOLDS rule: its 2× ratio is inert, and its test differs between candidates.**
- At n_bg = 40,000, a 1.5× inflation is rejected with probability 0.96 (`power.txt`, reproduced identically). So
  conjunct (ii) decides alone, and the effective bar is about 1.3×, not 2×.
- P2 gets McNemar, and P3–P5 get Fisher. That gives different power, so the background criterion is **not equal
  across candidates**.
- A failure-to-reject criterion also makes HOLDS easier the noisier the condition.
- Replace it with one non-inferiority rule for every candidate: HOLDS iff the one-sided 95% upper bound on the
  background ratio (candidate/B0) is ≤ 2, or whatever margin you mean. Pair it with S2.

**S2. Draw the switches' extra numbers from a separate stream.**
- "After all existing draws of the same call" does not preserve the stream past the first call of 19, because every
  later call is shifted.
- Draw P3's coin and redraw, P4's factors and P5's event from a child generator: for example,
  `SeedSequence([MASTER_SEED, crc32(label), 19, i, 134])`.
- The main stream then stays draw for draw B0's. That gives:
  - pairing for every candidate (McNemar throughout);
  - P3 = B0's links + resets, so P3 has an exact twin;
  - E1 stays an identity check for P3 as well.

**S3. Restate the calibration row at the registered background rung.** RBT-104 k = 8's 2.18% is ≥ 6.28 on 3,998
lineages (`drift-reach-k8.txt:113`). At ≥ 12.52 it is 2.05%. The registered rung is 6.8664 on 40,000. The verdict
(MOVES-WITH-BACKGROUND) does not change, but the row should say which rung and n it uses.

**S4. P2 is already determined.** P2's arrivals are RBT-91 σ = 4.0's 66, with B0's biases draw for draw (I verified
the stream argument against `genetics.py:121-146, 374-409`).
- Its primary is computable in seconds from committed data.
- §11 risk 7 rests the no-peek on a pledge. I did not compute it either.
- Record that P2 is a determinate computation, not a sample, and drop the 0.45 "probability" or label it a
  credence.
- If the coordinator wants extra protection, have the readout session compute P2 first, from the registered SHA.

**S5. H2 gating: an alternative exists.** The O1 hosts are needed only for **the registered W1 battery**
(`steer.py:721-777`, `planters.py:7, 100-103`). For a within-ticket comparison, every condition is read on the
same draws, so any fixed battery serves. For example, W1 draws screened on committed hosts (RBT-19 P-801 holistic
finals, RBT-113 C founders), with steer.py's admissible rule.
- Offer it as the fallback if O1 is not released, labelled "not the registered battery, not comparable across
  tickets".
- Then the ticket's "or say why not" is fully met, rather than ending at "gated".

**S6. E3 is under-specified.**
- Define "the strongest MOVES-WITH-BACKGROUND", for example the largest k, with ties broken by the smallest
  background ratio.
- Name E3's verdict set: RAISES / LOWERS / NO CHANGE within ±0.05 σ0 / INCONCLUSIVE.
- Say which fauna's arms run when the switch binds holistic `mutate` (P2–P4 do). RBT-113's Z line was designed-body
  only, so a holistic arm set costs more than 12 CPU-h.

**S7. Re-signing cost for C+.** About 9% of lineages get the C+ event (about 18,000). Of those, about 21% never
perturb b_k afterwards (mean of 0.75^m over the remaining m). That gives thousands of arrivals ≥ 6.28, not "at most a
few hundred". At about 5.6 s per arrival, it is several CPU-h. Cap re-signing at 400 per condition by lineage index:
the compass count is descriptive anyway.

**S8. Several predicate units in one lineage.** `structural_rate` reads `units[0]`. P5's and C+'s event unit is
appended last, so a lineage that already carries an arrival is read on the old unit. Register "max |a| over
predicate units", with units[0] printed for continuity.

**S9. P5's event and the unit cap.** Global brains hold 4–9 units and `max_units_per_brain` is 12 (both pools,
measured). State whether the event respects the cap and how often it is refused.

---

## NOTE

- **N1. The rung switch is justified pre-data and is conservative.** H41 (`ERRATA.md:142`) rules that 6.8664 is
  whole-brain and that like for like at a = 32 is 12.5236 on own links (`probe_rung.txt:3`).
  - Links alone at 0 of 84 ≥ 6.8664 implies 0 ≥ 12.52, so the baseline remains valid.
  - The switch makes moving off 0 **harder**, not easier.
  - Residual: the rung is read on one P-801 parent's b_E. W4b parents' own-link rung differs (§11.3); acceptable as
    ruled.
- **N2. Decomposition: reproduced byte for byte** (all three files; `diff` empty, 84/84, 63/63, 66/66).
  - "The coupled bias walk takes it back" is too strong. At σ = 4.0 the resting drive v·f(b_k) saturates the
    Effector even at default-size b_k (RBT-104's mechanism; the `tE` column recovers 0 of 66). So it is link
    magnitude × bias offset, not the walk alone. §10's P2-NULL reading already says so; §0 item 2 should too.
- **N3. Power reproduces exactly** (`python3 power.py | diff - power.txt` is empty). The Holm thresholds 7/6/6/5 are
  right. With B0 at 0, the exact test reduces to a count threshold. That is fine and equivalent to McNemar on the
  discordant pairs.
- **N4. Seeds.** Sharing lineage seeds across conditions is deliberate (paired), and Holm is valid under any
  dependence. W4b-801-bests has only 7 parents, so lineages cluster by parent. Report counts per parent.
- **N5. The whole-brain probe is strongly drive-dependent** on background hits: for example 8.56 at drive 0.01 against
  126.31 at 0.001 (`bg_sign_0.4.txt`). It is a registered rung reading, not a small-signal gain (cf. H36). Interpret
  the clause as such.
- **N6. C+** is a valid pipeline positive control: it can say PASS. It is not evidence that the background clause can
  pass a real operator. Its structureless lineages are mostly event-free default lineages. Say so.
- **N7. Costs.**
  - 200,000 × 11.2 ms + 40,000 × 12 ms ≈ 0.75 CPU-h per condition, consistent with "about 0.8".
  - H1 at 3.5, H2 at ≤ 62 and E3 at 12 per designed-only candidate are consistent with their sources.
  - Exceptions: S6 (holistic E3 arms) and S7 (C+ re-signing).
- **N8. Erosion (RBT-121 B)** is measured (E1) and correctly identified as blind to weight operators. E2 (u(8)) covers
  that gap on the designed body only, and the holistic gap is stated.

---

## Reproduce

Run from a checkout carrying #538's `runs/RBT-134/` with a `.[dev]` venv:

```
python runs/RBT-134/decompose_arrivals.py --readout docs/artifacts/RBT-91-alone-baseline.txt | diff - runs/RBT-134/decompose_arrivals_baseline.txt
python runs/RBT-134/decompose_arrivals.py --readout docs/artifacts/RBT-91-alone-1.6.txt --sigma 1.6 | diff - runs/RBT-134/decompose_arrivals_1.6.txt
python runs/RBT-134/decompose_arrivals.py --readout docs/artifacts/RBT-91-alone-4.0.txt --sigma 4.0 | diff - runs/RBT-134/decompose_arrivals_4.0.txt
(cd runs/RBT-134 && python power.py | diff - power.txt)
cd runs/RBT-134 && python design-adversary/bound_check.py decompose_arrivals_{baseline,1.6,4.0}.txt
python runs/RBT-134/design-adversary/sign_probe.py runs/RBT-134/decompose_arrivals.py --readout x
python runs/RBT-134/design-adversary/bg_sign.py 0 4 ; python runs/RBT-134/design-adversary/bg_sign.py 4.0 4   # ~20 s each
python runs/RBT-134/design-adversary/p5_ceiling.py
cd runs/RBT-134 && python design-adversary/p4_ceiling.py
```

---

## Fix-check (r2 678681a)

**Checked:** #538 at head `678681ada146ff0b0cd758894e920d0291441f2d` (`DESIGN.md` r2, `decompose_arrivals.py`,
`power.py` and their outputs), against M1–M4, S1–S9 and N1–N8 above. Fetched narrowly. I did not read
`ckpt/rbt-113-O1` or any RBT-129 data, and I ran no candidate condition: everything below re-reads RBT-91's
published default and σ = 4.0 lineages, or edits committed arrivals.

### Verdict: **REGISTER AFTER FIXES**

There is one new MUST. It is a one-number correction: B0's registered "unflagged" background target is my r1 proxy
count, not the count r2's own `sign_flip` rule produces. As written, B0 would fail its own reproduction control.

Every r1 MUST and SHOULD is otherwise answered. Once FC-M1 is corrected, the design can be registered without a
further check. FC-S1 and FC-S2 can be fixed in the same edit, or ruled as accepted limits.

### Reproduced

```
$ python decompose_arrivals.py --readout docs/artifacts/RBT-91-alone-{baseline,1.6,4.0}.txt [--sigma ..] | diff - <committed>
IDENTICAL baseline / IDENTICAL 1.6 / IDENTICAL 4.0
  bound violations among unflagged as-is probes (control I3): 0      (all three)
  SLOPE BOUND ... a32 12.5236 <= 0 / <= 2 / <= 29
`sign`-flip artefact in the as-is links-alone probe: 0 of 84 / 0 of 63 / 0 of 66
$ cd runs/RBT-134 && python3 power.py | diff - power.txt              -> identical
```

`pytest` (full suite, clean venv, `.[dev]`, no scipy): **1122 passed, 2 skipped** (see the end of this section).
`rabbitstew/`, so this checks only that the tree it will be built on is green.

### Item by item

| r1 item | r2 answer | fix-check |
|---|---|---|
| **M1** abs slope | max f′(abs) = 1 | **Closed.** Outputs reproduce. I3 gives 0 violations in all three conditions. P2 ≤ 29, A0 0, P1 ≤ 2. |
| **M2** sign window | `sign_flip`: a `sign` unit whose settled output differs between ±drive | **Closed for the mechanism; see FC-M1 for the number.** On all 21 committed `sign` arrivals (default and σ 4.0) × 8 biases, inside and outside the window and of both signs, the flag fires on every in-window probe and on no out-of-window probe: `probes 168: artefact readings NOT flagged 0; flags outside the window 0` (`fc_sign_flip.txt`). Excluded from k, the background and I3. |
| **M3** P4/P5 | checks with ceilings; Holm m = 2 (k ≥ 6, then 5); §10 scoped; r1's general claim withdrawn | **Closed.** `power.txt` reproduces. P3 shares P2's links through `aux_rng`, so P3 ≤ 29 also holds. Keeping P4 and P5 at their values as priced checks is the ruled route. |
| **M4** holistic route | arm I added; duplication restored; STRUCTURE-BOUND per arm and named | **Closed as scoped.** One gap remains (FC-S1). |
| **S1** background rule | Katz one-sided 95% upper bound on candidate/B0 ≤ 2, the same for every condition | **Closed.** One rule, one n (40,000) and one interval for all conditions. The variance `1/x1 − 1/n + 1/x0 − 1/n` is Katz's. Ignoring the positive pairing widens the interval, which errs against PASS: the safe side. P(HOLDS) at 1.0× / 1.5× / 2× = 0.997 / 0.64 / 0.05. |
| **S2** `aux_rng` | separate child stream for every extra draw; the main-stream step is still drawn and discarded on reset | **Closed. McNemar is valid.** Checked against `genetics.py:121-146, 374-409`: no main-stream draw depends on a weight or bias value. So P2, P3 and P4 keep B0's structure lineage for lineage, and P3/P4 keep B0's arrival sets. The pairs are real pairs, and with B0 at 0 the exact one-sided p is 0.5^k. P5 is a twin only up to its first event, as stated. |
| **S3** calibration | rung and n per row | Closed. |
| **S4** P2 determinate | credence wording; readout computes P2 first | Closed. |
| **S5** H2 | registered W1 battery from released O1 hosts, plus a registered fallback on committed hosts | Closed. See FC-N2. |
| **S6** E3 | carried candidate defined (largest k, then smaller background ratio); 4 verdicts; both faunas in the same arms | **Closed.** RBT-113 arms carry both faunas (`runs/RBT-113/PREREGISTRATION.md:122-126`), so there is no extra cost. One wording point remains (FC-N1). |
| **S7–S9** | re-signing cap 400; max over predicate units; P5 respects `max_units_per_brain` (`genetics.py:103` = 12) | Closed. |
| **N1–N8** | adopted | Closed. |

### FC-M1 (MUST). B0's registered "unflagged" background is 22 of 9,990, not 20 of 9,996.

r2 took "20 of 9,996" from my r1 `bg_sign_0.4.txt`. That file used a cruder proxy: a hit was artefact-carried if it
fell below the rung once every `sign` unit was replaced by `tanh`. r2 registers a different definition, the
mechanism-defined `sign_flip` over all `sign` units of the whole-brain probe, and the flag also drops lineages from
the denominator.

Applied as registered to RBT-91's committed background lineages (first 5,000 per pool):

```
$ python fc_bg_flip.py <r2 decompose_arrivals.py> 0 4 ; ... 4.0 4                (fc_bg_flip.txt)
sigma=0.4: structureless 9996; hits 26; flagged lineages 6 (0.06%), of them hits 4; UNFLAGGED: 22 of 9990 = 0.220%
sigma=4.0: structureless 9994; hits 164; flagged lineages 27 (0.27%), of them hits 13; UNFLAGGED: 151 of 9967 = 1.515%
```

**Why it matters.**
- §9 B0 requires the first 5,000 per pool to reproduce "**20 of 9,996** (unflagged)", and §3.5 repeats it. A correct
  B0 run gives 22 of 9,990, so as written B0 fails its control and the stage VOIDs.
- §6.4's σ = 4.0 row ("146/9,994 unflagged") should read **151 of 9,967**.
- `power.py`'s `P0_BG = 20/9,996` should be 22/9,990. That moves p0 from 0.200% to 0.220%. Power barely changes
  (P(HOLDS | 1.5×) rises slightly, because more hits narrow the interval).

The 2 hits that the proxy called `sign`-carried but `sign_flip` does not flag depend on a `sign` unit's operating
point, not on its flipping. The registered flip rule is the right one: it is the mechanism-defined rule M2 asked for.
Only the target numbers are wrong.

**Fix.**
- B0 targets: **26 of 9,996** (all lineages) and **22 of 9,990** (unflagged).
- σ 4.0 calibration: 151 of 9,967.
- `P0_BG = 22/9_990`, then regenerate `power.txt`.
- Cite `design-adversary/fc_bg_flip.txt`, not `bg_sign_0.4.txt`.

### FC-S1 (SHOULD). Arm I misses the Braitenberg vehicle built from two distinct nodes.

Arm I requires one Node with ≥ 2 instances. Arm G requires a global differencing unit. Neither sees the following:
two **distinct** single-instance nodes, each carrying its own `food` sensor with a local path to an Effector on the
same part. That is the same body-does-the-differencing vehicle as arm I, without duplication.

The claims are scoped per arm, so nothing written is false. But H2 will not call those lineages, and that route then
has no measurement at all.

**Fix.** Widen arm I to "≥ 2 parts (instances of one node **or** distinct nodes), each carrying a `food` sensor with a
local path to an Effector on the same part". Print the duplicated and distinct sub-counts separately, so the
duplication question is still answered.

### NOTE

- **FC-N1. E3's RAISES wording differs from RBT-113's.** RBT-113's RAISES is "the CI on the mean paired difference
  excludes 0 and p < 0.05", checked before NO CHANGE (`runs/RBT-113/PREREGISTRATION.md:242-243`). r2's is "CI entirely
  above 0 **and not within ±0.05 σ0**". Under r2, a CI of [+0.01, +0.04] σ0 is NO CHANGE; under RBT-113 it is RAISES.
  Either cite RBT-113's precedence verbatim, or say that r2 departs from it on purpose.
- **FC-N2. The H2 fallback can also fail its screen.** Its hosts are committed holistic finals and C founders, and
  `screen_draws`' admissible rule needs some host to eat. If the fallback screen also fails, state the outcome: H2
  unmeasured, reported as such (risk 8 covers the H1-only case, not this one).
- **FC-N3. Arm I's local path.** "A direct link, or one through a local neuron" misses chains of two or more local
  neurons. Allow any directed local path, or state the depth limit.
- **FC-N4.** The whole-brain flag drops 0.06% of B0's structureless lineages and 0.27% at σ 4.0, and catches hits at
  roughly 30–250× the base rate (4 of 6 against 0.26%; 13 of 27 against 1.64%). It does its job without materially shrinking the denominator.
  Printing the flagged fraction per condition (r2 §3.5) is enough.

### Reproduce (fix-check)

Run from a checkout carrying #538 r2's `runs/RBT-134/`:

```
python runs/RBT-134/design-adversary/fc_sign_flip.py runs/RBT-134/decompose_arrivals.py
python runs/RBT-134/design-adversary/fc_bg_flip.py runs/RBT-134/decompose_arrivals.py 0 4     # ~20 s
python runs/RBT-134/design-adversary/fc_bg_flip.py runs/RBT-134/decompose_arrivals.py 4.0 4
```

### pytest

Full suite on the tree #538 builds on (base `2b57e39`; r2 changes no code under `rabbitstew/`), clean `.[dev]` venv, no
scipy: **1122 passed, 2 skipped, 16 warnings in 878.56 s**.
