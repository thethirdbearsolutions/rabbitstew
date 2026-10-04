# RBT-134 design (pre-registration draft r1, DESIGN ONLY): operator changes that let mutation propose a paying compass

**Status.** Draft for the design adversary. Nothing here has run as an assay. No switch is implemented. Nothing under
`rabbitstew/`, `scripts/` or `runs/RBT-129/` is touched by this PR. The only new files are under `runs/RBT-134/`.

**What was run to price and ground this design.** Each item is listed with what it read. None of them read RBT-129
data, a run log, an `epa_overflow` file or a `ckpt/*` branch.

- **`decompose_arrivals.py`.** It regenerates RBT-91's committed structural arrivals (84, 63 and 66) from their lineage
  indices. It then re-reads their links-alone response under single-factor counterfactual edits. Outputs are
  `decompose_arrivals_{baseline,1.6,4.0}.txt`. It reproduces every committed links-alone value: 84 of 84, 63 of 63 and
  66 of 66 (`decompose_arrivals_baseline.txt:90`, `_1.6.txt:69`, `_4.0.txt:72`). It reads only conditions that RBT-91
  already ran and published. **No candidate condition was run.**
- **`power.py` → `power.txt`.** Stdlib only. It reads no data.
- **Timings only, not committed.**
  - `structural_rate.py --n 2000`: 4,000 lineages in 44.6 CPU-s.
  - `--background 4000`: about 12 ms per background lineage.
  - RBT-112's `baseline.py` for seed 801: 65 CPU-s, and it reproduces the committed `baseline-w32-801.txt` byte for byte.
  - 19 holistic `mutate` steps plus `synthesize`: 10–15 ms per lineage on the two holistic pools of §5.

---

## 0. Summary

1. **The ticket's premise needs two corrections from the merged record.**
   - **The rung.** The 6.8664 in "0 of 84" is a **whole-brain** reading of the installed motif. The motif's own links
     read **12.5236** at the first paying rung (a = 32). They read 6.2831 at a = 16 and 24.7145 at a = 64
     (`ERRATA.md:142`, H41; `runs/RBT-72-adversary/probe_rung.txt:2-4`). This design scores links alone against
     12.5236. It also prints the other three readings. The default operator's 84 arrivals read 0 at every rung
     (`decompose_arrivals_baseline.txt:106`).
   - **Prior art.** One operator change aimed at the magnitude has already gone through this exact instrument.
     RBT-104's `--link-scale K` scales the link step, the link draws **and the parents' links** together. At K = 8 it
     moved links-alone ≥ 12.52 to **8 of 84**. It also lifted the structureless whole-brain background to **2.18%**
     against 0.26% (`runs/RBT-104/PREREGISTRATION.md:127-130`; `runs/RBT-104/drift-reach-k8.txt:105-117`).
   - So "no ticket tests an operator change aimed at the mechanism" is not quite right. What has not been tested is a
     change that grows **the circuit relative to its host**. RBT-104's readout adversary found that a uniform scale
     cannot do that, because it scales both (`runs/RBT-104/PREREGISTRATION.md:148-153`).
2. **The mechanism, measured on RBT-91's own arrivals** (§1). The widening did reach the magnitude. At
   `weight_sigma` 4.0 the four links' product clears 12.52 in **42 of 66** arrivals (`_4.0.txt:91`). Every one of them
   reads 0 as is (`_4.0.txt:88`).
   - The coupled bias walk takes it back. The median |b_k| is 6.41 and the median max|b_E| is 9.48 (`_4.0.txt:92`).
   - The draw of a deaf transfer function takes the rest: `abs`, `sign` and `differentiate` units have zero
     small-signal slope at the probe, and they are 25 of the 84 default arrivals (`_baseline.txt:91`).
   - At the default step no bias treatment can help. The links' product never exceeds 3.68 (`_baseline.txt:113`).
3. **The slope bound decides two candidates before they run** (§2.2).
   - Under a change that moves only biases, a lineage's links and structure are unchanged, because these switches
     keep the random stream. So its links-alone response is at most |product| × max f′.
   - **A0, a bias decoupling alone at the default link step, is bounded at 0 of 84** at every rung
     (`_baseline.txt:112`).
   - **P1, the link step decoupled at 1.6, is bounded at ≤ 2** at a = 32 (`_1.6.txt:91`). The first Holm step needs 7.
   - Neither is spent on the family. Both run as checks of the bound.
4. **The registered family is four candidates on the Pioneer, Holm at 0.05.**
   - **P2**: the link step at 4.0 with the bias steps left at 0.4. It is bounded at ≤ 25 (`_4.0.txt:94`).
   - **P3**: P2 plus a bias reset.
   - **P4**: a multiplicative fan step on a neuron's links.
   - **P5**: a differencing-unit event.
   - Each verdict is PASS, MOVES-WITH-BACKGROUND or NULL (§6). The calibration of §6.4 shows the rule able to return
     each verdict on measurements already merged.
5. **The holistic fauna** (§5).
   - Run now: a structural census on the same lineage protocol, cheap and genotype-only.
   - Gated: the functional call by `steer.py`. It needs a W1 battery, and building one needs RBT-113 O1 hosts from
     `ckpt/rbt-113-O1` (`runs/RBT-116/planters.py:7, 607`), which this designer may not read.
   - There is **no holistic links-alone rung**, and the reason is given in §5.1.
   - The ticket's duplication candidate is **cut**, because recursion cannot make a differencing input (§2.3).
6. **Costs.**
   - The Pioneer assay with all its controls is about 10 CPU-h budgeted.
   - The functional erosion u(8) is about 1.1 CPU-h, and the holistic census about 3.5 CPU-h.
   - The gated holistic stage is up to about 62 CPU-h, and RBT-113 is about 12 CPU-h per PASSing candidate.
   - Nothing needs an ecology run. Nothing merges while RBT-129 is live.

---

## 1. The mechanism RBT-91 named, measured factor by factor

RBT-91's decision names three things (`docs/rbt-91-weight-scale-decision.md:45-48, 242-245`):
- `weight_sigma` drives both the link-weight step and the unit-bias step (`rabbitstew/genetics.py:134-146`);
- biases have no reset and no clip, so `sd(b) = 0.2·√depth` and `sech²(b)` collapses;
- widening inflates the recurrent background, not the circuit (decision `:28-43`).

**The response being decomposed.** The predicate unit's links-alone response (`runs/RBT-91/structural_rate.py:143-163`)
is a chain:

`a = (u_L − u_R)/2 · f′(b_k) · mean_E[v_E · sech²(b_E + v_E·f(b_k))]`

Here f is the unit's transfer function, and `brain.py:78-93` lists the seven. The two drive Effectors are `tanh`
(`brain.py:54`). The predicate requires v_L and v_R to have the same sign (`structural_rate.py:96-98`). So
`|a| ≤ |(u_L − u_R)/2 · (v_L + v_R)/2| · max f′`. Call the first factor the **link product**.

**The method.** `decompose_arrivals.py` edits one phenotype at a time and re-reads the response:
- `tanh` sets the predicate unit's function to tanh;
- `b_k=0` sets its bias to 0;
- `b_E=0` sets the drive Effectors' biases to 0;
- the pairs of these, and all three together ("unit slope").

These edits are bounds on what a bias or function change could buy **the arrivals that exist**. None of them is an
operator.

| RBT-91 condition | arrivals | as is, ≥ a32 | tanh + b_k=0 | b_k=0 + b_E=0 (non-`sign`) | unit slope (= link product) | slope bound ≥ a32 (§2.2) | \|b_k\| median | max\|b_E\| median |
|---|---|---|---|---|---|---|---|---|
| `weight_sigma` 0.4 (default) | 84 | 0 | 0 | 0 of 72 | **0** (max 3.68) | **0** | 0.76 | 1.26 |
| 1.6 | 63 | 0 | 1 of 55 | 2 of 55 | 2 | **2** | 2.59 | 3.44 |
| 4.0 | 66 | 0 | 3 of 57 | 24 of 57 | **42** | **25** | 6.41 | 9.48 |

Sources: `decompose_arrivals_baseline.txt:106-113`, `_1.6.txt:85-92` and `_4.0.txt:88-95`. The a = 16 and a = 64
columns are printed beside these lines.

**What the table says.**

1. **At the default step, magnitude binds absolutely.** The largest link product among the 84 is 3.68, below even the
   null rung of 6.28. No change to biases or functions can lift a default-step arrival to any own-link rung. That is
   RBT-91's "magnitude is the barrier that binds" (decision `:52-55`), now with a proof attached.
2. **At 4.0 the links get there and the slopes take it away.** In 42 of 66 arrivals the link product clears a = 32,
   yet the response as is clears it in 0.
   - Zeroing the two biases alone recovers 24 of the 57 non-`sign` arrivals.
   - Fixing the interneuron alone (tanh, b_k = 0) recovers 3. The Effector bias is the larger single factor.
   - This is RBT-104's saturation mechanism seen from the other side: the resting drive v·f(b_k) on the Effector
     (`runs/RBT-104/PREREGISTRATION.md:136-146`). It is also RBT-121 audit B's finding 1, the Effector-bias walk
     (`runs/RBT-121/ga/AUDIT.md:90-100`).
3. **The transfer-function draw is a third factor, and RBT-91 did not name it.** `random_neuron` draws the function
   uniformly from seven (`rabbitstew/genotype.py:596-598`; vocabulary `genotype.py:71`). At the probe, three of the
   seven have zero small-signal slope:
   - `abs` is even;
   - `differentiate` is 0 once settled;
   - `sign` is 0 at any b_k ≠ 0.

   Together they are 25 of the 84 default arrivals (`_baseline.txt:91`), the same "25 zero-response arrivals" as
   RBT-104 (`runs/RBT-104/PREREGISTRATION.md:142`).

   *Probe artefact, flagged for the assay.* A `sign` unit with b_k set exactly to 0 reads about 1/drive (about 100).
   This is the 11–12 "≥ rung" arrivals in the raw `b_k=0` column (`_baseline.txt:101`). The assay must exclude it
   (§9, I6).
4. **The widening also made the background.** RBT-91's structureless background rose from 0.26% to 1.64%
   (decision `:30-32`). That rise belongs to the links, not the biases: biases only *lower* slopes. A link-only
   widening (P2) is therefore **predicted to inflate the background at least as much** as the coupled one did. This
   is the clause most likely to fail (§10).

---

## 2. Candidate switches

Every switch is a `MutationConfig` field, off by default.

**Shared requirements.**
- Off, the operator is byte for byte as it is now: no extra random number is drawn, and this is tested.
- Where possible a switch uses the RBT-112/124 draw convention: a step is `N(0,1) × S`, so the random stream is
  unchanged at any S (`genetics.py:59-75`). A switch that must draw extra numbers (a coin, a factor) draws them only
  when it is on, after all existing draws of the same call.
- Implementation stays on this branch until RBT-129 releases `rabbitstew/`.

### 2.1 The registered family (Pioneer, `mutate_controller`)

| id | switch (field = value) | mechanism targeted (§1) | stream | implementable today without touching `rabbitstew/`? |
|---|---|---|---|---|
| **P2** | `link_sigma = 4.0` (the link step N(0,1) × 4.0; every bias step stays N(0, 0.4); new links still N(0, 1)) | magnitude, with the bias walk decoupled from it | preserved (twin of RBT-91's σ = 4.0 links and B0's biases) | **yes, on the Pioneer.** It equals `weight_sigma 4.0, global_bias_sigma 0.4, effector_bias_sigma 0.4`, because the designed parents carry only global neurons and segment Effectors: W4b-801 has 49 global neurons and 14 Effectors, P-801 393 and 120, and no other non-sensor unit (measured here). `mutate_controller` adds neurons only to the global brain (`genetics.py:389-391`). The new field is needed for the holistic fauna, and its equality to this composition is a byte-identity test. |
| **P3** | P2 + `bias_reset_rate = 0.2`: a perturbed non-sensor bias is redrawn from its birth law N(0, 0.5) with probability 0.2, instead of stepped | the resting-drive saturation: b_k and b_E far from 0 (§1, point 2) | one extra coin per perturbed bias | no |
| **P4** | `fan_rate = 0.2, fan_sigma = 0.75`: after all existing draws, each Neuron (any owner), with probability 0.2, has all its in-links or all its out-links (by a fair coin) multiplied by `exp(N(0, 0.75))`, across every brain | magnitude as a **product**: one event scales a circuit's links together, preserving signs and the in-pair's antisymmetry (the ticket's "magnitude step") | extra draws when on | no |
| **P5** | `pair_event_rate = 0.005`: with that probability per mutation, a global `tanh` neuron with bias N(0, 0.5) is added, with in-links from the left and right wheel food noses of opposite sign and out-links to both drive Effectors of the same sign. Magnitudes are \|N(0,1)\| × `link_scale`, and the two signs are fair coins. | structure supply ("a sensor pair and its differencing unit as one event"; on the Pioneer the pair exists, so the event is the differencing unit) | extra draws when on | no |

**Why each value.**

- **P2 at 4.0, not 1.6.** 4.0 is RBT-91's post-hoc widening, so P2's links and structure are **draw for draw** those
  of `RBT-91-alone-4.0.txt` (66 arrivals). P2's count is therefore bounded at ≤ 25 at a = 32 (`_4.0.txt:94`). The
  only open question is what the default-step bias walk leaves of it. 1.6 is P1 and is decided (§2.2).
- **P3 at a reset rate of 0.2.** A reset at the link rate (0.02) is useless within 19 mutations. With reset
  probability ρ, the stationary bias variance is about 0.16/ρ, so 0.02 gives sd ≈ 2.8. Reset 0.2 gives sd ≈ 0.9,
  which keeps the median sech² above 0.4.
  - P3 resets Effector biases too, because b_E is the larger factor (§1, point 2).
  - The host's throttle lives in b_E (`AUDIT.md:97-98`), so P3's costs (§8) are expected to be the largest.
- **P4's rate and size.** They are chosen so that the log link product's sd from fan events over 19 mutations,
  `0.75·√(19·0.2) = 1.46`, matches the median arrival's shortfall to a = 32, `ln(12.52/0.74)/2 = 1.41`.
  - Over 19 mutations each side of a unit gets about 19·0.2/2 ≈ 1.9 events.
  - The step is symmetric in log space, so it shrinks gains as often as it grows them. It is a walk, not a drive.
  - Restricting it to Neurons keeps it off the Effectors' fan-in, the host's gait wiring, except through a
    neuron's own out-links.
- **P5's rate and the tanh choice.**
  - At 0.005 per mutation, about 9% of lineages receive an event. That is about 200 times the default arrival rate
    of 0.042% (decision `:30`), so the structure supply rises by two orders of magnitude while the magnitudes stay
    the operator's own N(0, 1).
  - **The function is fixed to tanh. This is a designer choice for the adversary to attack.** A differencing unit
    with an even or flat function is not one (§1, point 3).
  - The prediction does not depend on the choice. With four |N(0,1)| links the link product's 99.9th percentile is
    far below 12.52 (§10).

### 2.2 Decided by the slope bound: run as checks, outside the family

**The bound.** Take any switch that leaves a lineage's link weights and structure unchanged and moves only biases.
Under the `N(0,1) × S` convention, the global/Effector bias sigmas draw exactly the numbers the default draws. Each
such lineage then has its twin's link product, so

`|a_links-alone| ≤ |product| × max f′`

The values of max f′ at the probe (SETTLE = 12 ticks from rest, `structural_rate.py:58`) are:
- tanh, sin and relu: 1;
- integrate: 2(1 − 0.9¹²) = 1.436 (`brain.py:90-91`);
- abs, differentiate and sign: 0.

The count of arrivals that can reach each rung is printed as `SLOPE BOUND` in `decompose_arrivals.py`.

- **A0**: `global_bias_sigma = 0, effector_bias_sigma = 0` with links at the default. These are existing switches. Its
  bound is **0 of 84 at every own-link rung** (`_baseline.txt:112`). The ticket's first bullet ("decouple the bias
  step … a bias reset") **cannot move the primary at the default link step, whatever it does to the biases.** A bias
  reset at the default link step falls under the same bound.
- **P1**: `link_sigma = 1.6` (RBT-91's pre-registered widening, decoupled). Its bound is **≤ 2 at a = 32**
  (`_1.6.txt:91`), below the 7 that the first Holm step needs (`power.txt`).

Both still run, at about 0.8 CPU-h each:
- A0 must read 0, and P1 must read ≤ 2. Either exceeding its bound VOIDs the instrument (§9, I3).
- P1's background is the one direct measurement of a link-only widening's background at a scale RBT-91 also ran
  coupled.

### 2.3 Cut, with reasons

- **"Duplication of a sensor-bearing part with its local brain" (holistic).** Recursion copies a Node's local brain,
  sensors included, verbatim onto every instance (`rabbitstew/synthesis.py:270-273, 289-322`).
  - A global unit's link from a local unit is **summed over every instance of the node** (`synthesis.py:323-332`).
    Two copies of one nose therefore feed any global unit with the *same* weight, and their left–right difference
    cancels.
  - Mirroring reflects only geometry (`mirror_connection`, `synthesis.py:113-121`). `_synthesize_brains` never reads
    the `mirrored` flag, so no sign flips.
  - A duplicated nose therefore supplies the common-mode input, never the differencing one. That is why RBT-116's
    holistic plant restricts noses to single-instance Nodes (`runs/RBT-116/planters.py:240-245`).
  - A duplication operator cannot propose the compass under this encoding. Making mirrored instances enter global
    sums with opposite sign is an **encoding (synthesis) change**, outside this ticket's operator scope. I name it as
    a possible follow-up, not a candidate.
- **The holistic version of P5 (add two noses and a differencing unit).** "Left" and "right" on a holistic body are a
  phenotype property: the planters read them from an intact season's heading (`planters.py:220-237`).
  - An operator that must read the phenotype to place its sensors is an encoding change, not a switch.
  - It is deferred. It becomes worth designing only if the Pioneer P5 shows that structure supply moves the primary,
    and P5 is predicted not to (§10).
- **`link_scale` (RBT-104) is not re-registered.** It has been measured on this instrument (§0.1). It is the
  calibration case for MOVES-WITH-BACKGROUND (§6.4).
- **Restricting the vocabulary to odd-slope functions** is not a candidate. Functions are drawn by `random_neuron`
  from the vocabulary (`genotype.py:596-598`), which is an encoding choice shared with everything else the brain
  does. The function share is reported per condition as a covariate. P5 fixes tanh for its own unit only.

---

## 3. The assay, Pioneer (designed body)

**The protocol is RBT-91's, unchanged.**
- 19 `mutate_controller` mutations from committed parents.
- Two pools, `W4b-801-bests` and `P-801-final60`, at 100,000 lineages each: **200,000 per condition**.
- `add = 0.15`, `rem = 0.1`, and `MASTER_SEED 20260912`.
- Lineage i's generator is `SeedSequence([MASTER_SEED, crc32(label), 19, i])` (`structural_rate.py:199-203`;
  `runs/RBT-78/reconcile.py:45, 51-54`).
- Everything is **imported** from `runs/RBT-91/structural_rate.py`, as RBT-104's `drift_reach.py` does
  (`runs/RBT-104/drift_reach.py:1-12`): the predicate, the probes and the generator.
- The one change is the condition's `MutationConfig`, made by `dataclasses.replace` on the pool's config.

**The script.** `runs/RBT-134/assay.py`, to be written after the ruling. Per condition it prints:

1. **Structure.** The arrival count per pool. The predicate is unchanged (`structural_rate.py:76-100`).
2. **The primary.** Every arrival's links-alone |a| against 6.2831, **12.5236 (primary)** and 24.7145, plus 6.8664
   for continuity with the ticket's "0 of 84". It gives the count k at a = 32, with Wilson intervals per 200,000
   lineages and per arrival.
3. **The decomposition columns of §1 for every arrival, and the slope bound.**
4. **Background.**
   - The whole-brain |a| (`small_signal_a`, `:103-129`) of the **first 20,000 lineages per pool (40,000)**. It is
     split structureless/structured, at 6.8664 and at 24.7145. The second matches RBT-104's table.
   - The first 5,000 per pool are RBT-91's committed background lineages, so B0 must reproduce 26 of 9,996 on them
     (§9, I1).
   - The background uses one task per 5,000 lineages, not one per pool (`structural_rate.py:366` runs two tasks), so
     it parallelises.
5. **Re-signing per robot at the reference probe**, for every arrival with own-link |a| ≥ 6.2831.
   - The heading probe is RBT-91's reference probe: 16 seeds × 15 s, with an UNDETERMINED band of ±15°
     (`runs/RBT-91/resign_arrivals.py:86-114, 195-213`).
   - The sign is taken **on the motif's own links**, not the whole brain (`ERRATA.md:141`, H41).
   - Output: compass / anti / undetermined counts.
6. **The sham predicate.** The same predicate with the wheel `agent` sensors in place of the `food` noses. Both
   wheels carry an `agent` sensor and a `food` sensor on the same parts (measured on both pools). This is an
   instrument control (§9, I5).
7. **The transfer-function census of the predicate units**, a covariate.

---

## 4. Registered questions and decision rule, per candidate

**Primary (one per candidate P2–P5).**
- *Does the count k move off the default operator's 0?*
- k is the number of lineages, out of 200,000, that carry the structure **and** whose own links read |a| ≥ 12.5236.
  The default's count on the same seeds is **0**: `RBT-91-alone-baseline.txt`, and `runs/RBT-104/drift-reach-k1.txt`
  at K = 1.
- **The test.** Under H0, the candidate's per-lineage rate equals the default's. Conditional on k + 0 events, the
  candidate's share is Binomial(k, ½), so the exact one-sided p is 0.5^k.
- k uses the a = 32 rung for the reason in §0.1. Counts at the other rungs are printed and decide nothing.
- The count is **unconditional**, per 200,000 lineages, not "of the arrivals". A per-arrival fraction rewards a
  candidate for *reducing* arrivals, and P5 multiplies them. The per-arrival fraction is printed beside it, which
  answers the ticket's "off 0 of 84" literally.

**Background clause (per candidate).**
- *Does the structureless background stay where it is?*
- The measure is the rate of structureless lineages with whole-brain |a| ≥ 6.8664 among the 40,000. 6.8664 is a
  whole-brain reading, so here it is like for like.
- **HOLDS** iff both:
  - (i) the point estimate is ≤ 2 × B0's on the same 40,000 seeds;
  - (ii) a one-sided exact test of the candidate against B0 does not reject at 0.05. Where the stream is preserved
    (P2) this is McNemar on lineage pairs; otherwise it is Fisher on the two 2×2 margins.

**Verdict per candidate.**

| primary (Holm) | background | verdict | reading |
|---|---|---|---|
| rejects | HOLDS | **PASS** | the operator proposes circuits whose own gain pays, without pumping whole-brain gain |
| rejects | fails | **MOVES-WITH-BACKGROUND** | a gain pump, not a circuit proposer: RBT-91's reading of the widening, and RBT-104's of `link_scale` |
| does not reject | either | **NULL** (background reported) | report k with its Wilson upper bound per 200,000 and per arrival |

**The compass count is reported, not tested.** That is the arrivals ≥ 12.52 re-signed as compasses. A drift
proposal's sign is a coin: it is symmetric in expectation whatever the carrier's direction (decision `:103-112`). On
own links the measured share was 30 of 58 = 51.7% (`ERRATA.md:141`). So the compass count is about Binomial(k, ½).
Testing it would halve the power and add nothing about the operator. The ticket's "re-signed per robot at the
reference probe" is met as a registered secondary.

---

## 5. The assay, holistic fauna

### 5.1 Why not links alone, and why not `steer.py` on 200,000 lineages

- **There is no holistic links-alone rung.** The links-alone probe needs a drive-Effector pair and a steering axis.
  `drive_effector_units` is "Pioneer-shaped bodies only" (`rabbitstew/fixed.py:218-235`).
  - A holistic body's turning is not a linear readout of named Effectors.
  - The only holistic rung on record is G8(c)'s planted total gain, a = 6 split over its output links
    (`runs/RBT-116/planters.py:86-88`). That is a parameter of a plant, not a small-signal reading through this
    probe.
- **`steer.py` is the body-general functional instrument.** It compares intact against decoy seasons with a
  trajectory veto (`runs/RBT-116/steer.py:631-702`). A full call is up to 104 seasons, about 37 core-s, and a
  stage-1 stop is about 3 core-s (`runs/RBT-116/PREREGISTRATION.md:956-970`).
  - On 200,000 lineages that is 170 to 2,000 CPU-h per condition, so it is not run on every lineage.
  - It is run on the **structural arrivals** and on a matched structureless sample. That is the same split as the
    Pioneer: structure first, function on the carriers.
- **Its battery is not buildable here.** A W1 battery needs W1 screen hosts (`steer.py:721-777`). Those come from
  RBT-113 O1 finals restored from `ckpt/rbt-113-O1` (`planters.py:7, 100-103, 607`). Under the no-peek constraint
  this designer may not read them. No W1 battery JSON is committed.

### 5.2 Stage H1 (runnable after the ruling): the structural census

**Pools.**
- (a) `runs/RBT-19/P-801/holistic/final`, 60 parents. Only 2 of 60 synthesise a food sensor (measured here). P-801 has
  `mirror false` and `neighbour_links false` (`runs/RBT-19/P-801/config.json:153-154, 172-173`).
- (b) RBT-113's C-config holistic founders, seeds 1–4, from `initial_population`, as audit B draws them
  (`runs/RBT-121/ga/parity.py:26-31`). That is 160 founders, 37 with a food sensor (measured here).
- 100,000 lineages per pool and 19 holistic `mutate` steps. Seeds take the same SeedSequence form, keyed by pool
  label.

**The H-predicate.** A global non-sensor unit k whose summed in-links come from `food` sensors on **two distinct
Nodes, each with exactly one instance** (`ph.node_instances`; the reason is §2.3), with opposite signs, and which has
at least one out-link to an Effector.
- Laterality is **not** checked. It needs a season (`planters.py:220-237`), and the functional stage adjudicates it.
  So the H-predicate over-counts on purpose.

**Conditions.** B0, P1, P2, P3 and P4, through the new fields:
- `link_sigma`, `bias_reset_rate` and `fan_*` bind `mutate` because `mutate_weights` reads them from the config, as
  `effector_bias_sigma` does (`genetics.py:143-144`).
- `global_bias_sigma` does not bind the holistic fauna (`genetics.py:64-66`). The holistic P1/P2 therefore need the
  new field.
- P5 holistic is deferred (§2.3).

**Output.** H-arrival counts with Wilson intervals, and the share of children with any food sensor and with food
sensors on two or more single-instance Nodes.

**H1 rule.** If B0 and every candidate have **0 H-arrivals in 200,000**, the holistic verdict is
**STRUCTURE-BOUND**: "no operator in the family proposes the holistic differencing structure at depth 19 from these
pools". Stage H2 is not run, and the reason is printed.

### 5.3 Stage H2 (gated on a W1 battery and coordinator release of the RBT-113 O1 hosts): the functional call

- **Call.** At W1, call every H-arrival with `steer.py`, up to 400 per condition, subsampled by lineage index if
  there are more. Call each STEERS arrival again with the predicate unit's out-links zeroed: the **circuit knockout**.
- **Circuit-owned STEERS** = STEERS intact and NONE knocked out. This is the holistic analogue of "links alone": the
  circuit, not the background.
- **Background.** A matched sample of 400 structureless lineages per condition is called. Their STEERS rate is the
  holistic background.
- **Rule.** The structure is the same as §4: an exact count test against B0's circuit-owned STEERS count, and the
  background clause on the structureless STEERS rate.
- **Holm.** A separate family, over the conditions that reach H2.
- **Power.** The detection floor at 400 calls is about 1/133 per arrival (one-sided 95%, zero events).
- **Planted positive control.** The planted G8(c) plants that `steer.py` already reads (`STEER_NOTES.md:44-58`).
  Their known sub-unit confirmation sensitivity is a stated limit (§11).

---

## 6. Multiplicity, and the calibration of the rule

### 6.1 The families

- **Pioneer primary:** P2, P3, P4 and P5, with Holm at family-wise 0.05 (`power.txt`). The thresholds are
  0.0125, 0.0167, 0.025 and 0.05, so k ≥ 7, 6, 6 and 5.
- **The background clause is per candidate and is not corrected.** It enters only as a conjunct that can turn a
  rejection into MOVES-WITH-BACKGROUND, never into PASS. An intersection–union conjunction needs no correction.
- **Holistic H2:** a separate Holm family, if run.
- **Not tested:** B0, A0, P1, C+ and the costs of §8. They are controls or descriptive measures.

### 6.2 Why m = 4 and not 7

A0 and P1 are decided by the slope bound (§2.2). Spending a test on a question already answered from merged data
would only weaken the others.

### 6.3 What is fixed now

The values in §2.1, the rung 12.5236, the background rung 6.8664, the 2× ratio and the n.

**No condition is re-run at another value after seeing data.** A follow-up value is a new pre-registration.

### 6.4 Calibration: the rule can say each verdict, on merged measurements

| case | k at a = 32 | background | the rule says |
|---|---|---|---|
| default (RBT-91 / RBT-104 K = 1) | 0 | 0.26% | NULL (the baseline) |
| RBT-91 coupled `weight_sigma 4.0` | 0 of 66 (`_4.0.txt:88`) | 1.64% (decision `:32`) | **NULL** |
| RBT-104 `link_scale 8` | 8 (`drift-reach-k8.txt:107`) | 2.18% at 6.28 (`:113`), about 8× | **MOVES-WITH-BACKGROUND** |
| **C+** (instrument positive control, run with B0) | must be ≥ 7 | must HOLD | **PASS** |

**C+ is new.** It is P5 with its event's link magnitudes multiplied by 16, the installed motif's output w at the
paying rung (`probe_rung.txt:3`), and with bias 0.
- It proposes exactly the structure at the paying magnitude and touches no other link. So it must PASS.
- If C+ does not PASS, the instrument is VOID (§9, I4).

---

## 7. Power at the planned n (`power.py` → `power.txt`)

**Primary.**
- With N = 200,000 and a first-step threshold of k ≥ 7, power is 80% at a per-lineage rate of 4.5 × 10⁻⁵ and 95% at
  5.9 × 10⁻⁵. Against an 84-arrival denominator that is 10.8% and 14.1%.
- RBT-104's `link_scale 8` reached 9.5% (8 of 84), where power is 0.69.
- **A candidate that delivers less than about 2 per 200,000 is undetectable at this n.** The design reports its
  Wilson upper bound and does not call it absent.
- The n is the ticket's (200,000). Raising it to 400,000 costs about 0.7 CPU-h per condition. It is **not**
  registered, because the slope bound already caps P2 at 25 and the decision for P3–P5 should not lean on a borderline
  count.

**Background.**
- At 40,000 per condition, an unchanged background HOLDS with probability about 0.95.
- A 1.5× inflation is rejected with probability 0.96, and a 2× with probability above 0.99.
- At RBT-91's 10,000 those figures are 0.56 and 0.95, which is why n_bg is raised.
- power.py treats B0's rate as known. B0 is in fact re-measured on the same 40,000 seeds, and the paired test (P2)
  is stronger than the unpaired approximation printed.

---

## 8. What a change costs elsewhere

Each cost is measured for every candidate and for A0/P1. None enters the primary verdict. Each is a registered
descriptive number with a stated reading.

### E1. Structural erosion per child (RBT-121 audit B, `runs/RBT-121/ga/parity.py`)

- **Measures.** Link survival per child, the share of children losing any link, and food-route loss among carriers.
  The config is RBT-113 C with seeds 1–4 × 25 children, for both faunas.
- **Default** (`runs/RBT-121/ga/parity.txt:1-2`):
  - holistic: 0.9162, 48.1%, 8.98%;
  - designed: 0.9839, 31.0%, 0.00%.
- **Wrapping.** `parity.py` hard-codes the operator and has no CLI. It is wrapped with `replace(cfg.mutation, …)`, as
  `runs/RBT-124/bias_walk_s0.py` does. This is a new script under `runs/RBT-134/`.
- **It is blind to weight operators by construction.** It counts (owner, src, dst) keys. Under P2 and P1 it must
  equal the default **exactly**, because the stream is preserved and structural draws are untouched. That makes it a
  stream-identity check (§9, I2).
  - P3 and P4 shift structural draws but not their law, so the prediction there is the default within sampling.
  - P5 adds links and never removes them.

### E2. Functional erosion: RBT-112's erasure rate u(8)

- **Measure.** On RBT-106's planted w = 32 founders: 10 seeds × 30 founders × 20 lineages, the pay32 persistence
  f(d), and `u = 1 − f(8)^(1/8)` (`runs/RBT-112/erasure.py:1-6`).
- **Default:** u(8) = **0.282**. At `global_bias_sigma 0` it is **0.089** (`runs/RBT-112/erasure.txt:25`;
  `runs/RBT-112/PREREGISTRATION.md:27, 132-138`).
- **This is the erosion a weight operator actually causes,** so it is the cost E1 cannot see.
- **Running it.** RBT-112's `baseline.py` already patches one field into RBT-104's `persistence.lineage()`
  (`runs/RBT-112/baseline.py:1-14`). It is generalised to take the candidate's fields. Without them it must
  reproduce the committed table byte for byte, which it does for seed 801 (measured here).
- **Holistic.** E2 has no holistic planted founders. E1's route loss is the holistic proxy.
- **Reading, registered.** A candidate whose u(8) is above 0.5 is reported as **"proposes but cannot keep"**: a
  paying compass it builds is more likely than not erased within a generation and a half. This is not a veto.
  RBT-112 showed that the erasure rate is not what stops selection holding the compass
  (`ERRATA.md:125`, H65), so u is a cost, not a verdict.

### E3. The RBT-113 selection response

- **Measure.** The designed body's divergence slope `b_div` in σ0 units against the benchmark's frozen reference,
  σ0 = 0.7545 for the designed body (`runs/RBT-113/sigma0_reference.json:3`), and the holistic σ0 = 0.2212 where the
  candidate binds holistic `mutate`.
  - Default: +0.038 raw yield per generation, h2 0.067 (`runs/RBT-113/REPORT.md:49`).
  - Z − default was NO CHANGE within ±0.05 σ0 (`REPORT.md:51`).
- **Rule.** The same equivalence margin, ±0.05 σ0 per generation, over 12 pairs.
- **Limit.** It is weak: P(detect an h2 change of +0.2) = 0.53 (`runs/RBT-113/power.txt:37`). This is stated, not
  fixed.
- **Gated** on (i) a PASS (or the strongest MOVES-WITH-BACKGROUND, if there is no PASS) and (ii) RBT-129 releasing
  `rabbitstew/`. It needs:
  - an `evolve` flag per field: `evolve` has `--global-bias-sigma` (`rabbitstew/cli.py:594`) and no `--link-scale`
    or `--weight-sigma`;
  - a new operator case in `runs/RBT-113/world.py` and `run_arm.sh`, which reject anything but `""` and `"Z"`;
  - a fresh `prelaunch.py` PASS, because `run_arm.sh` refuses a stale tree;
  - readout prefix logic.
- **Cost.** 4 arms × 3.0 CPU-h = **12 CPU-h per candidate** (`runs/RBT-113/PREREGISTRATION.md:302-306`). The committed
  O1–O4 are reused as the paired default if one O line reproduces byte for byte on the new tree. Otherwise O is
  re-run, at another 12 CPU-h.

---

## 9. Matched nulls and instrument controls (any failure VOIDs the stage it guards)

| id | control | requirement |
|---|---|---|
| **B0** | the default operator, re-run by `assay.py` | arrival list identical to `RBT-91-alone-baseline.txt` (84; lineage, units and both responses line for line, as `drift_reach.py`'s self-check); background on the first 5,000 per pool reproduces **26 of 9,996** |
| **I1** | seed pairing | every condition uses B0's lineage seeds; P2 and P1 are draw-for-draw twins (links = RBT-91's σ lineages, biases = B0's) |
| **I2** | stream identity under P1/P2 | E1 identical to the default; P2's arrival set equal to `RBT-91-alone-4.0.txt`'s 66; P1's equal to `-1.6.txt`'s 63 |
| **I3** | the slope bound | A0's k = 0 at every own-link rung; P1's k ≤ 2 at a = 32; P2's k ≤ 25; every arrival's \|a\| ≤ \|product\| × max f′ (a single violation means the probe is not what §1 says) |
| **I4** | positive control C+ | PASS (§6.4) |
| **I5** | the sham (`agent`) predicate | its arrival count within the 99% binomial range of the `food` predicate's in every condition. The operator is sensor-blind, so a divergence is an instrument bug, not biology |
| **I6** | the `sign` artefact | no arrival with a `sign` unit at \|b_k\| < 1e-9 is counted ≥ rung; any such arrival is printed |
| **I7** | byte identity when off | each new field at its default is byte-identical to the current operator on a fixed 1,000-lineage stream; `link_sigma = S` equals the composition of §2.1 on the Pioneer; full `pytest` passes in a clean `.[dev]` venv without scipy |
| **I8** | holistic H2 | a no-food-sensor body reads NONE (`steer.py`'s own I1, `runs/RBT-116/PREREGISTRATION.md:754-755`) |

**Matched nulls, stated as such.**

- **P2's matched null is RBT-91's coupled σ = 4.0 run.** It has the same links, and only the bias step differs. Its
  readout is committed: 0 of 66, background 1.64%. P2 against it is the direct test of "the coupling is what takes the
  gain".
- **Every candidate's matched null is B0** on the same seeds.
- **The background is the matched null for "circuit, not whole brain".** The sham predicate cannot be one, because the
  operator does not know which sensor is food.

---

## 10. Predictions, both ways (fixed now; probabilities are mine)

| id | prediction | P(prediction) | if wrong, it means |
|---|---|---|---|
| A0 | k = 0 (bound) | 1.0 (proof) | the probe or the stream convention is not as documented: VOID |
| P1 | k ≤ 2 (bound), so not significant; background above B0's, about as high as RBT-91's coupled 1.41% or higher | 1.0 / 0.7 | — / that biases, not links, carried RBT-91's background |
| **P2** | **MOVES-WITH-BACKGROUND**: k between 7 and 25, background at or above 1.64% | 0.45 | if NULL (k < 7), even default-step biases saturate wide links. Parents already carry \|b_E\| median 1.26 (`_baseline.txt:110`), so decoupling is not enough and the resting drive binds (RBT-104). |
| P3 | **MOVES-WITH-BACKGROUND**, k > P2's; E2's u(8) the highest of the family | 0.5 | if PASS, resetting biases also tames recurrence, which would be the first operator to buy circuit gain without whole-brain gain |
| P4 | **NULL** or weak MOVES: k in 0–8; background up less than P2's | 0.6 | if PASS, multiplicative circuit-wise magnitude is the missing move, and the cheapest change to adopt |
| P5 | **NULL on the primary** with arrivals up about 100–300×: k ≤ 2 | 0.8 | if it moves, structure supply *was* binding at the tail, against RBT-91's "structure is proposed" (decision `:66-69`) |
| holistic H1 | at most a handful of H-arrivals per 200,000 under every condition; likely STRUCTURE-BOUND | 0.6 | if H-arrivals are common, the holistic barrier is functional, and H2 is worth unblocking |
| **programme** | **no PASS in the family** | **0.6** | — |

**If no candidate PASSes, the result is this, and it bounds the encoding.**
- Within the routed-motif encoding, at the assay's depth, an operator buys the circuit's own gain only as whole-brain
  gain. The link weights that carry the motif's magnitude are the same weights that set the recurrent background, so
  no step distribution on them separates the two.
- The remaining levers are outside the operator:
  - the encoding (P5's tanh and the mirror-sign rule of §2.3);
  - selection, which RBT-112, RBT-106 and RBT-113 address.
- "Widening does not help" (decision `:4-6`) is then generalised from one knob to the family.

**If a candidate PASSes,** the operator, not the encoding, was what withheld circuit magnitude. That candidate goes
to E3 and then to an ecology design of its own. This ticket does not schedule one.

---

## 11. Risks

1. **The probe's operating point is conventional.** Links alone reads the Effector's slope at b_E with every other
   input silenced, which is not the in-situ operating point. The b_E factor in §1 is partly a property of that
   convention.
   - Mitigation: `assay.py` also prints, as a descriptive column, the predicate circuit's response with the
     Effectors held at their whole-brain resting input. The registered rung is a reading through the same
     convention (`probe_rung.txt:3`), so the primary stays like for like.
2. **One value per switch.** A NULL at P4's (0.2, 0.75) or P3's 0.2 does not refute the mechanism. Each NULL is
   worded "at this value". The adversary should attack the values in §2.1 before the ruling, not after.
3. **The rung comes from one parent.** 12.5236 was measured on one installed P-801 parent. Rungs vary with the
   parent's b_E. This is the ERRATA-ruled number and is used as is.
4. **Depth 19 is fixed by the mandate.** An operator that acts slowly is penalised. The asymptote (decision
   `:199-209`) is not the question.
5. **P3–P5 lose draw-for-draw pairing.** The exact count test does not need pairing. The background test falls back
   to Fisher.
6. **P5 makes many lineages structured.** The structureless background is then a selected subset (about 91% of
   lineages). The all-lineage whole-brain rate is printed beside it.
7. **No peeking at P1/P2.** P1 and P2 on the Pioneer are exactly computable today from RBT-91's committed σ = 1.6 and
   4.0 lineages, with links from those lineages and biases from B0's. **That computation has not been done and must
   not be done before the ruling.** Only the bound, which is the arrival set's link products, has been read. The
   adversary may verify the bound from `decompose_arrivals_*.txt`.
8. **The holistic stage may end unmeasured.** If H2's hosts stay blocked, the holistic answer is H1's structural
   census alone, and the report says so.
9. **CPU contention with RBT-129.** The work is about 15 CPU-h of short jobs. It should run on a host that carries no
   RBT-129 lane, from a pinned branch SHA, and touch no pinned path.
10. **`steer.py`'s confirmed sensitivity is below 1.** Planted G8(f) plants fail the confirmation's F bound
    (`runs/RBT-116/STEER_NOTES.md:44-58`). A holistic H2 NULL is therefore an upper bound on circuit-owned steering,
    not a proof of absence.

---

## 12. Costs (CPU-h)

| item | basis | CPU-h |
|---|---|---|
| Pioneer assay, per condition | 200,000 lineages × 11.2 ms (44.6 CPU-s per 4,000, measured) + 40,000 background × 12 ms (measured) + probes | about 0.8 |
| conditions B0, C+, A0, P1, P2, P3, P4, P5 (8) | ×1.5 margin | **about 10** |
| re-signing (arrivals ≥ 6.28, at most a few hundred) | 16 × 15 s seasons × 0.35 s per robot (`runs/RBT-113/PREREGISTRATION.md:302`) | < 0.5 |
| E1 (parity, both faunas, 7 operators) | about 10 s each (`runs/RBT-121/ga/AUDIT.md:376-383`) | < 0.1 |
| E2 (u(8), 10 seeds, 6 operators plus the default check) | 65 CPU-s per seed (measured) | about 1.3 |
| holistic H1 (5 conditions × 200,000) | 12.5 ms per lineage (measured) | about 3.5 |
| **runnable after the ruling, in total** | | **about 15** |
| holistic H2 (gated) | at most (400 arrivals × 2 calls × 37 s + 400 structureless × up to 37 s) per condition, × 5 | at most about 62 |
| E3 (gated, per candidate) | 4 arms × 3.0 CPU-h | 12 (24 if O must be re-run) |

---

## 13. Order of work

1. **Design review.** The adversary reviews this draft, and the coordinator and owner rule. No assay runs before the
   ruling.
2. **Code, on this branch only, not merged.**
   - `rabbitstew/genetics.py`: the fields `link_sigma`, `bias_reset_rate`, `fan_rate`/`fan_sigma` and
     `pair_event_rate`, all default-off.
   - Tests for I7.
   - `runs/RBT-134/assay.py`, plus the E1 and E2 wrappers and the H1 census.
   - The full `pytest` in a clean `.[dev]` venv without scipy.
   - The runs execute from the pinned branch SHA. Nothing touches `scripts/` or `runs/RBT-129/`.
3. **Controls first:** B0, C+, A0 and P1. I1–I7 must pass. A failure stops the run and is reported.
4. **The family:** P2–P5 on the Pioneer, then the readout and verdicts (§4, §6).
5. **Costs:** E1 and E2 for every operator, and holistic H1.
6. **Gated:** E3 for a PASS, after RBT-129 releases `rabbitstew/`. Holistic H2 after a W1 battery exists and the
   coordinator releases the RBT-113 O1 hosts.

Steps 3–5 are about 15 CPU-h, about 4 h wall on 4 cores. Nothing waits on RBT-129 Stage 2 except E3's merge.

---

## 14. What the adversary should attack first

1. **The slope bound** (§2.2). Is max f′ right for every function at SETTLE = 12, including `integrate` and `relu`
   at b_k = 0? Does the `N(0,1) × S` convention really keep P1/P2 draw-for-draw twins of RBT-91's σ lineages
   (`genetics.py:141-146`)? If not, A0 and P1 belong back in the family.
2. **The rung.** 12.5236 (own links, ERRATA H41) against the ticket's literal 6.8664.
3. **The background clause.** Is a 2× ratio together with a one-sided test right? Is whole-brain 6.8664 the right
   background rung when the primary uses own links at 12.5236?
4. **P5's tanh and C+.** Is fixing the event's function a designer's thumb on the scale? Is C+ a positive control or
   a tautology?
5. **The holistic cut** (§2.3, §5.1). Is the synthesis reading right, and is there a local-brain route (with
   `neighbour_links` off in P-801) that the H-predicate misses?
