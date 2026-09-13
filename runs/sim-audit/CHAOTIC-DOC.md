# The transposed drive: a wiring-convention defect, what it invalidates, and where the programme stands

**Posted to the RBT project doc store.** Source of truth is this file on branch
`claude/rbt-45-2oa635`; if the two diverge, the branch wins.

**Author:** the RBT-45 delegate, acting as lead researcher while the coordinator was away, at the
user's direction. **Nobody has reviewed any of this.** Branch `claude/rbt-45-2oa635`, commits `85fc9ae` … `0991702`. Open PR:
https://github.com/thethirdbearsolutions/rabbitstew/pull/5

---

## 1. The finding, in one paragraph

`rabbitstew/fixed.py:76` mounts each of the Pioneer's drive wheels about **its own outward
normal** (`axis=(1,0,0)`, with the two wheels mirrored by `side=±1`). Mirroring the mount mirrors
the axis, so the two hinge axes are **antiparallel** — measured world-frame dot product exactly
**−1.0000**. On this body the **sum** of the two effector commands is the steering axis and their
**difference** is the throttle: the transpose of a textbook differential drive. Every Braitenberg
circuit this programme has installed or counted was therefore wired onto the wrong axis. Wired
onto the right one, a hand-installed compass earns **+0.897 items against a 1.516 baseline
(+59%), 7 of 7 robots**. The world rewards chemotaxis richly, and the question of the last ten
world-variant arms was never answerable as posed.

---

## 2. The defect in detail

### 2.1 What the code does

```python
# rabbitstew/fixed.py:68-76
def wheel_connection(child: int, x: float, side: float) -> Connection:
    return Connection(
        position=(x, side, -0.6),
        ...
        axis=(1.0, 0.0, 0.0),   # about the wheel's own length axis (the outward normal)
    )
```

Two wheels, `side=+1` and `side=−1`. Each hinges about the outward normal of its own body, and
those normals point away from each other.

### 2.2 Measured consequence

| measurement | value |
|---|---|
| wheel 1 hinge axis, world frame | `[ 0.9642,  0.2650, 0]` |
| wheel 2 hinge axis, world frame | `[−0.9642, −0.2650, 0]` |
| dot product | **−1.0000** |
| open loop, command `(+1, +1)` | spins at **1.221 rad/s**, travels **0.19 m** in 15 s |
| open loop, command `(+1, −1)` | **0.0005 rad/s**, travels **24.95 m** in 15 s |

So `e1 + e2` steers and `e1 − e2` drives.

### 2.3 Why nobody caught it

The library already knows. `drive_straight_genotype` hardcodes `(+1, −1)` with the comment *"the
right wheel needs the opposite sign"*. But that knowledge lives inside one function and is
surfaced **nowhere** at the brain/genotype interface, in `synthesis.py`, or in any analysis
tooling. Anyone writing a controller or a structural statistic sees two effectors on two wheels
and assumes a differential drive.

This is not hypothetical. During the audit, **three separate agents independently wrote
"corrected" compasses that still routed the common mode onto the throttle**, after being told the
axis convention was under suspicion. The convention is invisible from where circuits are written,
and that is the actual defect — the physics is fine.

---

## 3. How this was found

It was not found by any internal check. The compass spike (§4) had passed a held-out test, a
multiple-comparison discipline, a paired-seed design at 64 seeds, and bootstrapping over robots
rather than bouts. All four were methodologically sound and all four were applied to the wrong
circuit.

What broke it was the user's objection: *Braitenberg vehicles demonstrably work, so if a
hand-installed one earns nothing, the prior should be that something in the simulation or the
method prevents the mechanism — not that the mechanism is invalid.*

That objection was acted on with a seven-hypothesis audit (20 agents, each claimed defect
adversarially refuted from three angles, `runs/sim-audit/`). Both load-bearing claims were then
reproduced from scratch by the orchestrator in `runs/sim-audit/verify_independent.py`, written
without reusing any audit script, and matched to three decimals.

**The process lesson is the uncomfortable one:** four layers of internal verification agreed on a
wrong answer. The check that did the work was an outside appeal to physics.

---

## 4. What this invalidates

### 4.1 The compass spike (RBT-61) — withdrawn, not amended

`runs/compass-spike/spike.py` applies the same signed magnitude to **all six** `W[dst,src] +=`
assignments. With matched signs the two nose contributions *add* on the steering axis and *cancel*
on the throttle. So every one of its 30 conditions delivered:

- `steer = w(n₁ + n₂)` — the **common mode**, a smell-triggered spin
- `drive = ±w(n₁ − n₂)` — the **gradient**, to an axis that does not turn

It installed a smell-gated pirouette and never once installed a compass. At w=8 the robot is not
"starving because a compass disrupts its gait" — it is pinned in a spin (mean |translation|
1.140 → 0.132, mean |rotation| 0.774 → 1.867).

Its reported finding that *crossed and uncrossed were behaviourally identical* was the symptom,
read as a result. Both arms shared the same dominant spin term.

**Two published lines are now the reverse of the evidence and must go:** "there is no gradient for
selection to climb even when the wiring is present… a flat plain and then a downhill", and the
crossed/uncrossed equivalence claim.

### 4.2 RBT-45 — the arithmetic stands, the interpretation is dead

Its central claim, *"the crossed pairing — the only one that steers"*, is false. `reach.py:159-160`
defines `crossed` as each wheel nose reaching the **other wheel's** effector — a 2-link pattern
which on this body **is the spinner** (−1.502 items, 0/7 robots at w=32).

Three reasons its classifier could not have found the working circuit even in principle:

1. **It counts the wrong motif.** The circuit that steers is 4-link; RBT-45's classifier counts it
   as *both* crossed and uncrossed and never reports it as its own cell.
2. **It is sign-blind.** `influence_split` builds `M[d,s] += abs(w)`, and the working motif is
   *defined* by a sign pattern.
3. **It clamps each link at 3.0** (`M = np.minimum(M, 3.0)`) while the circuit needs an effective
   steering gain of order 16–64.

What survives untouched: the grid's reproducibility, the §6.5 design-effect correction, the §6.1
docs correction, and — most usefully — **§4's lineage depth: 600 seasons is a median of 19
reproduction events, maximum 23.**

### 4.3 Audit debt: the nose taxonomy should be re-read

`docs/foraging-world.md` classifies the nose behaviours that did appear as a **brake**, a
**throttle**, and a **sweep modulator**. Those are *mechanistic* interpretations of what a circuit
does, and every one was made under an assumed differential drive. The **behavioural** lesion
results are unaffected — RBT-38's 64-paired-seed work stands. But the mechanistic readings should
be re-derived against `e1+e2` steering. I have not done this and am not asserting they are wrong.

---

## 5. What actually works

A **4-link antisymmetric motif**:

```
W[e1,n1] += w     W[e2,n1] += w
W[e1,n2] -= w     W[e2,n2] -= w
```

Both noses reach **both** effectors; opposite sign between noses, same sign across effectors.
This puts `2w(n₁ − n₂)` on the steering axis and **exactly zero** on the throttle. It is *not*
the 2-link crossed pair.

### Dose-response (7 robots × 64 paired seeds, bootstrapped over robots, baseline 1.516 items)

| circuit | steering gain k | Δ items | 95% CI | robots improved |
|---|---|---|---|---|
| antisymmetric, w=8 | +16 | +0.054 | [−0.040, +0.158] | 3/7 |
| antisymmetric, w=16 | +32 | +0.246 | [+0.147, +0.353] | 7/7 |
| **antisymmetric, w=32** | **+64** | **+0.897** | **[+0.632, +1.176]** | **7/7** |
| the spike's own wiring, w=32 | ~0 | −1.502 | [−1.614, −1.375] | 0/7 |

Monotone in k, sign-antisymmetric about zero, and **still rising at the top of every sweep**. A
yoked phantom-food control (decorrelated items, same generator and disc, drive amplitude matched
to 94%) earns +0.163, so the **taxis-specific gain is +0.723, i.e. +48%** — and the phantom still
shares r=0.45 with the real drive through the disc's radial structure, so that is a lower bound.

---

## 6. Two hypotheses that were refuted along the way

Both were mine, both were plausible, both are dead. Recording them so nobody re-runs them.

**The DC pedestal.** The smell sensor sits at a common mode of ~0.33 with a left–right
differential of ~0.04, an 8:1 ratio, and I argued this swamps any installed gradient. **Refuted:**
the DC-free crossed circuit it prescribes earns **−0.011** [−0.143, +0.109]; a magnitude-matched
constant is worth −0.018; and stripping every constant out of the circuit that *does* work leaves
**+0.844 of the +0.897 intact**. The DC matters only as a design constraint — do not route a
sustained constant onto the spin axis (adding one back costs −1.013).

**The `i/(1+i)` squash.** Refuted 3/3 independently. It is **strictly monotone**, so it destroys
**zero** directional information (sign agreement with the raw sum = 1.000000 over 168,000 real
samples). It is a ~2.08× contrast tax, exactly invertible, and absorbed by the per-unit bias the
brain already carries. Removing it makes the shipped mower *worse* (1.516 → 1.288). One residual
cuts the other way and is recorded honestly: excluding gen90, a de-squashed sensor plus a
hand-built compass beats the shipped baseline by +0.111 [+0.066, +0.153] on 6/6 robots, so the
squash is on the causal path even though removing it buys nothing on the shipped population.

---

## 7. The reachability recount, and the sharpened puzzle

With the payoff established, the live question became: **does the operator ever propose the motif
that pays, at a magnitude where it pays?** `runs/RBT-45/motif.py` recounts the same drift process
against the quantity that decides whether a robot steers — the **signed** coefficient on
`(n₁ − n₂)` arriving at `e1 + e2`, over paths up to four links, with **no per-link clamp**. No
simulation at all.

### What the evolved population carries

| | |
|---|---|
| final population, n=60 | median \|a\| **0.000**, max \|a\| **0.708**, **0 of 60** above the inert boundary, **0 of 60** gradient-dominant |

### What drift proposes (2000 lineages per cell)

Thresholds are in units of **a**, calibrated by installing the motif and reading `a` back
(`runs/RBT-45/calibration.json`, median over the 7 robots): **a = 16** is the inert boundary
(+0.054, CI straddling zero), **a = 32** gives +0.246 items, **a = 64** gives +0.897.

| add_link_rate | mutations | a ≥ 16 (inert) | a ≥ 32 (+0.246) | a ≥ 64 (+0.897) | a ≥ 32 *and* gradient-dominant |
|---|---|---|---|---|---|
| 0.15 (default) | **19 (realistic)** | 1.45% | **0.70%** | **0.05%** | 0.35% |
| 0.15 | 23 | 1.60% | 0.70% | 0.15% | 0.20% |
| 0.15 | 50 | 4.15% | 1.90% | 0.65% | 0.70% |
| 0.15 | 200 | 11.15% | 7.00% | 3.70% | 2.75% |
| 0.3 | 20 | 3.50% | 0.95% | 0.10% | 0.25% |
| 0.6 | 20 | 9.35% | 3.80% | 1.30% | 1.85% |
| 1.0 | 20 | 17.25% | 9.05% | 3.20% | 5.65% |
| 1.0 | 50 | 39.75% | 32.40% | 23.35% | 19.10% |

**Correction, made after the RBT-8 delegate caught it.** The first version of this recount
returned `s1 − s2`, which is **2a**, and compared it against thresholds that are in `a` units —
so every rate was counted at half the intended gain. The table above is the corrected one; the
figures first circulated (2.95% at realistic depth) were two times permissive. The correction
runs *against* my previous framing, and is recorded here rather than quietly folded in.

The **gradient-dominance** column requires |a| > |c|, i.e. the gradient term beats the
common-mode term on the steering axis — the common mode being the pirouette worth −1.502 items.
Note a single wired nose forces |a| = |c| identically, so that filter excludes every single-nose
wiring. The RBT-8 delegate predicted in advance, confidence 0.6, that this filter would cut the
rate *by at least an order of magnitude*. **It does not: measured, it costs a factor of 1.6 to
3.8 across all eight cells** (0.70% → 0.35% at the realistic cell). Their prediction is
falsified. The reason their evolved-population intuition did not carry over is that drift wires
both noses often enough that most high-gain drift lineages are not single-nose.

**Caveat, stated up front: this is a linearisation.** Gain routed through neurons is attenuated
by `tanh` (the audit measured per-effector gains of 0.407 and 0.197 on shipped robots), so these
fractions remain a **permissive upper bound**. The calibration also found that indirect routing
makes the delivered `a` phenotype-dependent: on 5 of 7 robots it is exactly the nominal value, on
one it doubles, and on one (gen 490) it **reverses sign** — the same installed circuit steers the
opposite way. That is worth knowing on its own.

### The puzzle, restated on the corrected numbers

Selection had access to a circuit worth **+59% yield**. At the default operator and realistic
depth, drift reaches a gain that earns anything measurable (a ≥ 32) in **0.70%** of lineages, and
the strong point (a ≥ 64) in **0.05%** — one lineage in two thousand. The final population carries
none (0/60, median |a| 0.000).

Hazard arithmetic, redone on the corrected rates: 1364 birth events across the run is roughly 72
independent 19-mutation lineage-spans, so the expected number of times the run ever produced a
circuit worth +0.246 items is about **0.5**, and worth +0.897 about **0.04**.

**This reverses what I said on the inflated numbers.** I had concluded the motif probably appeared
once or twice and failed to establish. On the corrected rates it probably **never arrived at all**
at a gain that pays. That restores something close to the programme's original "the search never
proposes it" — but now for the right motif, with a number, and with the payoff independently
established at +59%.

## 8. Recommended next steps, in priority order

1. **The co-adaptation run — now the experiment that matters.** Seed from gen 590 with the motif
   installed at k=32 and let selection run a few hundred seasons. Does it *keep* it? Everything
   measured so far is a circuit bolted onto a finished controller: **+0.897 is an upper bound on
   the prize, not evidence evolution can hold it.** Given ~3% proposal and 0/60 carriage, the live
   hypothesis is that it appears and is lost — either to drift before it pays, or because a
   partially-formed version costs more than it earns. Nothing else distinguishes these.

2. **Fix the convention so this cannot recur — I would rank this above more science.** A named
   accessor for the steering and throttle channels at the brain/effector interface, plus one test
   asserting the two wheel axes are antiparallel, would have made every error in this document
   impossible. The defect has a demonstrated four-incident history (one voided experiment, one
   misdirected structural statistic, one withdrawn ticket, three agents writing wrong corrections)
   against roughly an hour of work.

3. **Re-read the nose taxonomy** in `docs/foraging-world.md` against `e1+e2` steering (§4.3).

4. **Bound the prize.** k=64 was the top of every sweep and every positive was at its ceiling. One
   wider sweep on the existing 7 robots × 64 paired seeds, ~5 minutes, says whether the prize is
   0.9 items or 2.5.

5. **Do not spend RBT-42 yet.** Widening `add_link_rate` to 1.0 does lift the a ≥ 32 rate from
   0.70% to 9.05% at realistic depth, so it would work mechanically. But its success criterion must be rewritten against
   the 4-link antisymmetric motif *and* against a weight scale an order of magnitude above the
   operator's usual draw — and running it before the co-adaptation question risks discovering that
   the operator proposes the motif fine and selection discards it anyway.

6. **RBT-46's B1** gates on a non-zero crossed rate. The control cell I supplied measures the wrong
   motif and should not be used; the replacement numbers are in §7.

---

## 9. Open caveats, unburied

- **n = 7 robots from one run.** What carries the key claims is 7/7 unanimity (sign test
  p = 0.0078) and four independently-written scripts agreeing, **not** the confidence intervals.
- **Solo bouts only.** Every measurement here is single-robot. Whether the compass survives
  competition in the ecology's four-robot arena is untested.
- **The optimum is unbounded above.** k = 64 was the top of every sweep run.
- **No co-adaptation anywhere.** Every compass was bolted onto a finished controller.
- **The reachability recount is a linearisation** (§7) and reads as an upper bound.
- **One audit build resists explanation.** `refute_actuation_1`'s "anti" at w=10 had the correct
  steering sign and per-nose DC subtracted and still scored −0.379. The synthesis attributes it to
  a residual constant on the steer axis; that is an asserted reconciliation, not a measurement, and
  it is the weakest link in the chain.
- **`probe_oracle` wrote no output artifact.** Its +2.484 exists only as dossier text. It is
  corroborative, not load-bearing — the headroom conclusion is independently implied by the
  compass results.
- **Two headline ratios from the actuation probe are inflated** and should not be requoted: the
  "988:1" and "27,800:1" channel-authority figures divide by a quantity that vanishes by symmetry.
  Off-symmetry the flat ratio is ~71:1 and on the random terrain that actually applies it is
  unresolvable (R² = 0.014).

---

## 10. Where the programme stands

The explanation for six hundred seasons of blind mowers is no longer *"the world does not reward
sensing"* — it does, richly — nor *"the search never proposes the wiring"*, which was measured
against a circuit that cannot work. It is now a claim about the search, with a number attached: at the
default operator and realistic depth the motif arrives at a gain that pays in **0.70%** of
lineages and at the strong point in **0.05%**, the population carries none, and the hazard
arithmetic says it probably never arrived at all across six hundred seasons. Whether a motif that
*is* present could be held is still untested, and is what the co-adaptation run would settle.

Ten world-variant arms were spent on a question a wiring convention made unanswerable. The
cheapest thing that would have caught it was an assertion about two dot products.
