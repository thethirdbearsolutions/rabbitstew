# RBT-121 audit B: the genetic operators and the selection schemes

*Auditor B, on the RBT-121 design pass. Cut from `claude/new-session-4cao7d` @ `152e2df`. The audit is read-only on
scored code: nothing under `rabbitstew/` or any scored run path changed. Probes are the `.py` files beside this one,
and each one's output is the `.txt` of the same name. All probes are seeded and deterministic. Together they run in
about 3 minutes on 4 cores. Two of them need an RBT-113 arm restored from its checkpoint, because the results
branch holds lineages but no final genomes:*

```
git fetch --depth 1 origin ckpt/rbt-113-O1 && git show FETCH_HEAD:run.tar.gz.part000 | tar xz -C $TMP
python runs/RBT-121/ga/noise.py $TMP/O1/1 U;  python runs/RBT-121/ga/effector_bias_lines.py $TMP/O1
```

## Corrections after the adversary (#403)

*These corrections come from PR #403, `runs/RBT-121/adversary/ADVERSARY.md` @ `e9096cb`. The coordinator accepted
all of its verdicts. Where this block and the body below disagree, this block governs. The body is left unchanged.*

**§3 (noise): HOLDS-WITH-CAVEAT.**
- The designed body's 2-draw repeatability of 0.004 is the estimator's floor, not a property of the population. The
  estimator reads 0 in 29% of 6-draw subsets, and on 12 draws it is about 0.03–0.1.
- "The designed U line is ranked on noise" is **OVERSTATED**.
- s does not depend on the repeatability. It is s ≈ i·Δ/σ_P, with i = 1.27 for the top 25%.
- **The hold condition is s > u/(1 − u), not s > u.** Holding requires (1 + s)(1 − u) > 1. That gives a threshold
  of 0.098 at u = 0.089, 0.18 at u = 0.15 and 0.39 at u = 0.28. The u values are imported from paper 10 and RBT-112;
  they have not been re-measured for RBT-113's operator.
- #403's corrected statement: "At 2 draws, s ≈ 1.27 Δ/σ_P, with σ_P ≈ 0.7 (designed) to 1.2 (holistic). A +0.02 to
  +0.05 gain gets s ≈ 0.02–0.09. That is below u/(1 − u) for u = 0.15 or 0.28, and at the boundary for the designed
  body at u_Z = 0.089."

**§4 (breed order): the mechanism HOLDS-WITH-CAVEAT, but only in one income regime.**
- **The rule, stated as net income ÷ living cost:**
  - Selection above viability is weak when solvent members' net income is at least about 2× the living cost
    (resident gross income g0 ≳ 0.8). There the shuffled lottery is saturated.
  - Near the living cost, starvation and the delay in reaching the threshold do the selecting, and the shipped
    lottery selects hard. At g0 ≤ 0.5 it fixes a 1.25× forager readily.
  - The ratio is a parameter of each experiment, measurable from its lineage (`adv_p801_births.py`). It is not a
    constant of the simulator.
- **`ecology_s.py`'s μ/cost of 0.25/0.05 matches no committed foraging run.** Its 2–3× figure is therefore a
  statement about a regime, not a measured effect on any committed result.
- #403's corrected statement: "When the resident population's net income is well above the living cost (committed
  foraging worlds after the first ~50 seasons: g0 ≈ 1.3), the committed lottery gives almost no advantage to
  foraging better than viability. At incomes near the cost it selects strongly."
- **The depth cost of `--breed-order energy`.** It is not a free fix. Under hoarding it produces a gerontocracy
  (#403 item 1i, from `adv_demography_ne.txt`: a neutral population at g0 = 1.3, seasons 200–400):

  | rule | distinct parents | mean age at breeding |
  |---|---|---|
  | shuffle | 137 | 30.6 |
  | energy | 71 | 54.4 |

  - Parents halve.
  - Generation time nearly doubles.
  - **Realised mutational depth per season roughly halves.** A depth mismatch between arms is what already sank
    RBT-80's contrast.
- **Any design that adopts a reordering must report realised depth per arm.** It should also weigh `energy_leak` or
  tickets, which weight income rather than age × income, against `energy`.

## The answer in one paragraph

The operators make the **motor allowance cheap** and **perception wiring expensive and short-lived**.

- **Allowance.** One holistic mutation changes the body's summed motor gear by a factor of 1.5 or more in 7–10% of
  children (SD of the log ratio ≈ 1.0 per mutation).
- **Perception wiring.** A raw food-sensor→effector route between two segments appears in 0.8% of children. It is
  unsigned, and paper 8's coin flip still applies to its sign. A carrier loses the route it already has in 15% of
  children.
- **The walks.** The operators also carry two unbounded walks. One is the global-bias walk that paper 10 measured.
  The other has not been reported: the **Effector-bias walk**, which no flag freezes. It holds motors at constant
  throttle whatever the sensors read, and it is the whole of the designed body's "down" response in RBT-113.
- **Selection.** On top of this sits evaluation noise. In RBT-113 the 2-draw fitness has a repeatability of 0.14
  (holistic) and 0.004 (designed). A perception-sized gain of +0.02–0.05 items therefore gets s ≈ 0.03–0.07 per
  generation, which is **below the operator's own erosion rate**. Selection can find the allowance; it cannot hold a
  small competence.

## Ranked findings

| # | finding | evidence it shaped a committed result | size | fix cost |
|---|---|---|---|---|
| **1** | The Effector-bias walk is unbounded and not frozen by `--global-bias-sigma`; it saturates motors | **direct**: RBT-113 designed D line 99% saturated, C 39%, U 7% | large | tiny |
| **2** | Motor gear is the most mutable phenotype; food wiring is rare and eroded 19:1 | **strong**: RBT-113 holistic D's 10× gear at every seed; U's food is coverage | large | medium (the fix is on the world side) |
| **3** | Evaluation noise swamps perception-sized gains: s lies below the operator's erosion | **strong**: RBT-112/106 s ≤ 0.08; the RBT-113 designed U line is ranked on noise | large | cheap (compute) |
| **4** | The ecology breeds threshold-crossers in shuffled order, so wealth above the threshold is not selected | **plausible**: the paper-10 arms (RBT-106/112) ran this economy | 2–3× on s | tiny |
| **5** | Structural ratchets under drift: node count and global brain go up, wiring goes down | **direct**: RBT-113 C lines, nodes 1.52× (23/24 directories up), links 0.42× | moderate | tiny |

Lower-ranked items, with no probe, are at the end.

---

### 1. The Effector-bias walk: a second unbounded walk that no flag freezes (and the designed body's whole D response)

**Mechanism.**
- `mutate_weights` (`genetics.py:112–138`) *resets* a perturbed link weight with probability 0.02. This bounds its
  variance (paper 8 §3: rms 2.97).
- A **bias has no reset and no clip.** It steps N(0, 0.4) with probability 0.25 in every generation, forever, so its
  variance grows by 0.04 per generation.
- An Effector outputs `tanh(bias + input)`, and outputs on the same DOF are summed and clipped to ±1
  (`brain.py:101–105`). A walked Effector bias is therefore a motor held at constant throttle whatever the sensors
  say.
- RBT-112's `global_bias_sigma` touches only units with `owner is None` (`genetics.py:131`). Effectors live on
  segments (owner = node index), so **the Z operator leaves this walk untouched.** The holistic operator ignores the
  flag entirely.

**Operator alone** (`bias_walk.py`, 80 lineages of RBT-113's seed-1 founders; "resting drive" is |tanh(bias)| > 0.9,
meaning ≥ 90% throttle with zero input):

| generations | designed, default | designed, **Z** | holistic |
|---|---|---|---|
| 0 | 0.0% | 0.0% | 0.8% |
| 23 | 16.9% | 13.1% | 8.1% |
| 60 | 27.5% | 33.8% | 18.2% |
| 150 | 54.4% | **59.4%** | 26.1% |

Under Z the global-unit bias SD stays at 0.49, while the Effector bias SD reaches 2.59.

**In the committed RBT-113 genomes** (`effector_bias_lines.py`, arm O1, all 3 seeds × 40 final members):

| line | designed: resting drive > 0.9 | designed: mean \|bias\| | holistic: resting drive > 0.9 |
|---|---|---|---|
| U | 7.1% | 0.70 | 21.8% |
| **D** | **99.2%** | **2.47** | 21.3% |
| C (no selection) | **39.2%** | 1.22 | 18.0% |

**What this means.**
- **The designed body's D line.** Every motor has been walked to near full throttle. The designed body's D response
  (the work term that RBT-117's "down half" compares) is this walk selected in one direction. ADVERSARY §3 found the
  designed D line at 95% of its fixed work ceiling; this is how it gets there with its gear fixed.
- **The designed body's U line.** In 23 generations the operator alone saturates about 17–39% of motors (C line). The
  designed body's b_up is therefore partly the **purging of the operator's own load** (U line: 7%, against C's 39%),
  not competence. In the holistic body the walk is diluted by Effector turnover (remove and re-add), which is why the
  lines barely differ there. The holistic body's lever is gear (finding 2).
- **Paper 10.** The Effector walk is a candidate share of RBT-112's residual erosion (u 0.089 with global biases
  frozen). That share is **at most about 0.02**, because paper 10 puts the structure's own decay at 0.067. It does
  not overturn paper 10's A3. It does mean "frozen walk" was never a frozen *controller*.

**Could affect:** RBT-113's designed-body b_down and b_up and its h2; the RBT-117 margin (the down half, as the
designed side); any designed-body "work" or "throttle" reading; RBT-112's HZ arm (a small residual).

**Fix (flag, off by default, byte-identical when off).** Add `--effector-bias-sigma S` (`MutationConfig.effector_bias_sigma: Optional[float] = None`).
- It works exactly like `global_bias_sigma` (`genetics.py:131–134`): for `u.kind == "effector"`, the step is
  `rng.normal(0, 1) * S`. That is the same single draw, so the random stream is unchanged at any S, and at S = 0 the
  Effector biases freeze.
- Pass it from both `mutate_controller` and `mutate` (the holistic path), so the two faunas stay at parity. This is
  unlike `global_bias_sigma`, which is designed-body only.
- A bounded alternative is `--bias-reset-rate` (reset a perturbed bias to N(0, 0.5) as weights reset). It would
  consume an extra draw, so it would have to be drawn only when the flag is on.

**Cheap test.**
1. Rerun `bias_walk.py` with S = 0. The share of motors with resting drive > 0.9 at G = 150 must equal the founders'
   (0.0% designed, 0.8% holistic).
2. `tests/`: one generation of RBT-113's C line with the flag unset must be byte-identical to the committed
   `lineage.jsonl` row for generation 1 (seed 1).
3. At S = 0.4 the output must be byte-identical to unset. The draw is N(0, 1) × 0.4 instead of N(0, 0.4); this is the
   same check RBT-112's `byte_identity.py` made, reused.

---

### 2. Motor gear is the most mutable phenotype; food wiring is rare and eroded 19:1

`reach.py` and `gear_levers.py` apply single `mutate` calls (RBT-113's config) to the 160 holistic founders of seeds
1–4, and to a population walked 23 generations under the C line's own scheme. Gear is `world.py:202`'s rule, summed
over driven DOFs on the synthesised phenotype under the mass budget.

| per child (one `mutate`) | founders | after a 23-generation neutral walk |
|---|---|---|
| summed gear × ≥ 1.5 | **7.2%** | **9.7%** |
| summed gear × ≤ 1/1.5 | 8.4% | 6.2% |
| SD of log(gear ratio) | 1.09 | 1.00 |
| driven ball-joint DOFs up / down | 6.4% / 8.4% | 6.5% / **1.9%** |
| a **new** food route (food sensor on segment i → Effector on j ≠ i, direct or via one global unit, any sign) | **0.78%** | 0.00% (no food sensors left) |
| an existing route **lost**, among carriers | **14.6%** | – |
| links lost (by src, dst), mean share | 8.9% | 7.4% |

**Which operator class moves gear** (`gear_levers.py`, share of calls at ×≥ 1.5 / ×≤ 1/1.5):

| class | up | down |
|---|---|---|
| add/remove connection | 4.0% | 4.7% |
| add/remove unit | 1.6% | 0.5% |
| add/remove node | 1.2% | 1.6% |
| joint type | 1.0% | 1.2% |
| recursive limit | 0.5% | 0.5% |
| connection scale | 0.2% | 0.5% |
| segment dims/shape | 0 | 0 |

Two notes on this table:
- `normalized_dims` keeps each segment at unit volume, so mass moves only through scale and the part count. The
  budget then rescales everything.
- A new Connection instances an existing node, *with that node's Effectors*. That is a new driven joint (or three, on a
  ball joint) in one step. This is the "gear jump".

**Reading.**
- **Gear is not a ratchet.** Up and down are roughly symmetric, and the RBT-113 C line's gear ends *below* the
  founders' (ADVERSARY §3: 18 against 22). Gear is simply **the phenotype the operator moves most**. A 1.5× gear
  step is about 9× likelier per child than the bare, unsigned structure of a holistic compass. That structure then
  still needs paper 8's coin flip on sign and a magnitude.
- **Gain and loss are 1:19 for a route and roughly 1:1 for gear.** Under drift a food route cannot persist: after the
  23-generation neutral walk, no member carried one. This is the holistic twin of paper 10's u ≈ 0.28. The per-child
  route loss of 9–15% is already in the same range as what selection can pay (finding 3).
- **Evidence.** This is why RBT-113's D line found 10× gear at every seed within 23 generations, while the U line's
  food gain is coverage, not smell (ADVERSARY §3–4).

**Could affect:** every holistic "responds" result that runs through work or distance (RBT-113's b_div and b_down;
RBT-117); any holistic-versus-designed comparison of motor use; the claim that holistic perception is "not found"
(it is not *offered* at a comparable rate).

**Fixes.**
- **(a) The root fix is on the world side and is auditor A's:** cap the gear a part can grant across all the joints it
  touches. Summed gear on a part's joints should be ≤ 4 × its mass, instead of 4 × max(mass) per DOF
  (`world.py:202`). It goes behind a `--gear-rule shared` flag, and `per-dof` (the default) is byte-identical.
- **(b) The GA side, `--structural-rate-scale K`** (`MutationConfig.structural_rate_scale = 1.0`). Multiply every
  body and graph rate (`_mutate_segments`, `_mutate_connections`, `_mutate_graph`, and the add/remove parts of
  `_mutate_neural`) by K *inside the comparison*: `rng.random() < rate * K`. Every `rng.random()` is still drawn, so
  the stream is unchanged, and K = 1.0 is byte-identical. This slows the gear walk and the route loss together, and it
  is also the parity fix in finding 5 and in the "Lower-ranked" section.

**Cheap test.**
- For (b): `reach.py` at K = 0.25 must bring route loss among carriers from 14.6% to ≤ 4%, and gear × ≥ 1.5 from 7.2%
  to ≤ 2%.
- For (b): the unit test that one RBT-113 generation is byte-identical at K = 1.0.
- For (a): probe_gear's Σgear/(4 × mass) must be ≤ 1 for every member under `shared`.

---

### 3. Evaluation noise: perception-sized gains get s below the operator's erosion

`noise.py` re-scores all 40 final U-line members of RBT-113 seed 1 (both faunas) on 6 fresh draws, exactly as
decompose scores them. Each draw's main effect is removed, because RBT-113 shares a generation's draws, so the noise
selection actually sees is the member × draw interaction.

| RBT-113 U line, seed 1 | holistic | designed |
|---|---|---|
| between-member SD of net yield | 0.336 | **0.056** |
| member × draw SD | 1.158 | 1.343 |
| repeatability of the 2-draw fitness that truncation ranks on | **0.144** | **0.004** |

Selection coefficient on a single carrier of a +Δ gain under RBT-113's truncation (top 10 of 40 on a 2-draw mean;
Monte Carlo on the numbers above):

| Δ (items/season) | s at 2 draws | s at 8 draws | generations to double at 2 draws |
|---|---|---|---|
| +0.02 (ADVERSARY §4: the designed body's intact − decoy) | +0.026 | +0.043 | 27 |
| +0.05 | +0.074 | +0.118 | 10 |
| +0.10 | +0.146 | +0.251 | 5 |
| +0.20 | +0.31 | +0.54 | 2.5 |

**Reading.**
- **A smell gain of +0.02–0.05 items gets s ≈ 0.03–0.07.** That is below the rate at which the operator removes the
  wiring that carries it: 0.09–0.15 per child for a holistic route (finding 2), and u = 0.28 (default) or 0.089 (Z)
  for the designed compass (paper 10). Only gains of about ≥ 0.1 items per season (2 draws) or about ≥ 0.06 (8
  draws) out-select their own erosion. RBT-112's measured s ∈ [0, 0.08] sits exactly in the band this predicts.
- **The designed U line is ranked on noise.** Its heritable spread (0.056) is 4% of its draw noise. Its b_up
  (+0.0375) is a real but tiny response, most plausibly the purging of finding 1's load.
- **The whole motor lever is far above this threshold.** The D line's work moved by about 1 item-equivalent,
  s ≫ 1. Selection sees allowances, and it does not see small competences.

**Could affect:** RBT-113 (the designed-body h2 and b_up; NO CHANGE on Z is uninformative at this power, as
`power.txt` already warns); RBT-106/112 (held versus not held); any "evolution did not find perception" claim at 2
draws.

**Fix.** No code change is needed for the scheme. `--draws` exists, so the fix is to set draws by this table: pick
the draws so that s(Δ_target) exceeds u. For Δ = 0.05 against u = 0.089, that is 8 draws (s 0.118). If code is
wanted, add `--draws-final K`: re-score only the truncation boundary (members ranked k−5 to k+5) on K extra draws
before cutting. It is off by default, and no extra draws are made when it is off, so the run is byte-identical.

**Cheap test.** Rerun `noise.py` at the chosen draws: the s printed for Δ_target must exceed the arm's u. Then run a
one-seed pilot with a planted +Δ allele (paper 10's planted-compass method) and check that it is held.

---

### 4. The ecology selects on crossing a threshold, not on wealth

In `Ecology.step` (`ecology.py:524–545`), breeders are **everyone at or above `birth_threshold`, shuffled**
(`rng.shuffle(breeders)`). They breed in that order while slots are free, and slots open only through deaths.
- When slots are scarce, a robot with energy 30 and one with energy 3.01 have **the same chance to breed that
  season**.
- Wealth above the threshold buys only persistence of eligibility. It does not buy priority.

`ecology_s.py` transcribes the economy with the default EcologyConfig (capacity 60, cost 0.05, threshold 3, birth
cost 1, max age 60), a gain of μ 0.25 + Δ, and member × season noise of 1.16 (from probe 3). It starts a carrier
allele at a 10% share:

| Δ | shipped (shuffled): s/season | proposed (richest first): s/season | shipped, with erosion u 0.15 | proposed, with erosion u 0.15 |
|---|---|---|---|---|
| +0.05 | +0.003 | **+0.008** | −0.004 (share 9%) | **0.000** (17%) |
| +0.10 | +0.008 | **+0.018** | +0.002 (16%) | **+0.013** (41%) |
| +0.20 | +0.014 | **+0.040** | +0.007 (28%) | **+0.026** (81%) |

Richest-first ordering raises s by 2–3×. Under erosion it turns "held on none" (Δ ≤ 0.05) into "break-even".

**Evidence.** This is plausible rather than direct. It is the economy of every ecology run, including the paper 10
arms (RBT-106 and RBT-112, both of which measured s < 0.1). The numbers above are synthetic, and μ and σ are
assumptions.

**Could affect:** paper 10 (HU "held on 0"), paper 5 and 6 ecology results, and any ecology run that reads the
absence of a trait's spread as the absence of an advantage.

**Fix (flag).** Add `--breed-order {shuffled,energy}` (`EcologyConfig.breed_order = "shuffled"`). Under `energy`,
keep the existing `rng.shuffle(breeders)` call and follow it with a **stable** sort by descending energy. The shuffle
still breaks ties, and the random stream is byte-identical in both modes. Only the order changes, and `shuffled` is
the shipped code path.

**Cheap test.** `ecology_s.py` already implements both orders. In the codebase, a 10-season run of `ecology` with
the flag unset must be byte-identical to the current code. With `energy` set, a unit test with three breeders and one
free slot must give the slot to the richest.

---

### 5. Structural ratchets under drift: more nodes, a sticky global brain, fewer links

**In committed runs** (`drift_lineage.py`, all 24 RBT-113 seed directories, generation 0 → 23; the C line is
drift-matched with no selection):

| holistic C line | gen 0 | gen 23 | directories up |
|---|---|---|---|
| nodes | 3.47 | 5.26 (**1.52×**) | **23/24** |
| parts | 4.41 | 5.32 (1.21×) | 13/24 |
| units | 19.5 | 25.2 (1.30×) | 15/24 |
| links | 57.3 | 24.1 (**0.42×**) | **2/24** |

**The operators are growth-biased on the genotype graph:**
- add rates exceed remove rates at every level: node 0.08 against 0.05, connection 0.10 against 0.08, unit 0.10 against
  0.06 (and a vector sensor adds 3 units), link 0.15 against 0.10;
- **crossover** (`genetics.py:469–485`) takes `a[:k] + b[k:]` with k ∈ [1, len(a)]. The child's length is
  `max(k, len(b))`, which is never below b's. `reach.py`: on unequal founder pairs the child has 3.70 nodes against
  the parents' mean of 3.42, and exceeds the mean 64% of the time against 33% below it;
- **the global brain is dominant:** when exactly one parent has a global brain, the child has one **100%** of the time
  (`gb_src` falls back to whichever parent has one).

**Wiring still erodes 0.42× under drift,** because every structural removal and `repair_links` or
`prune_neighbour_links` drops links wholesale. One `add_link` per brain at 0.15 does not replace them.
- Grown nodes are often unreachable, and `size_ratio_limit` counts them (`max_parts = ceil(2 × len(nodes))`). Neutral
  junk nodes therefore raise the part cap of the expressed body.
- The drift direction is **more body graph, less wiring.** More connections is finding 2's main gear lever, and less
  wiring is what perception needs.

**Could affect:** any holistic trend in nodes, parts or links read as adaptive, when the C line shows the operator
alone moves them; paper 4's "evolved lumps"; any morphological-complexity claim.

**Fix (flags).**
- `--crossover-cut {prefix,aligned}`. `aligned` draws k ∈ [1, min(len a, len b)], so the child's length is len(b) and
  the mean child length equals the parents' mean over the parent order. `prefix` is the shipped code, and an unchanged
  `rng.integers` call keeps the stream byte-identical when off.
- Optionally `--balanced-structure`, which sets each remove rate equal to its add rate.

**Cheap test.** `reach.py`'s `crossover_bias` under `aligned` must give a child mean equal to the parents' mean within
0.03, and presence of the global brain must fall to about 50% if its choice is also made a fair coin. A 23-generation
C-line replay (`reach.py`'s `neutral_walk`) must give nodes 1.0× ± 0.1.

---

## Lower-ranked (no probe run, or small)

- **Parity between the faunas' operators** (`parity.py`). The holistic child loses 8.4% of its parent's links
  (children losing any link: 48%). The designed child loses 1.6% (31%). Per child, the holistic operator is about 5×
  more disruptive to wiring, and it adds the whole body walk on top.
  - The two operators also differ in flags. `link_scale` and `global_bias_sigma` act on the designed body only
    (`mutate` ignores both). The Z arm's holistic line is therefore a *replicate*, not a treatment; this is
    documented in RBT-113's `world.py`.
  - Comparisons of "which fauna evolves perception" are made at unequal per-child erosion. `--structural-rate-scale`
    (finding 2b) is the knob for equalising link survival.
- **All-against-best** (`evaluate`, non-solo). Each member's fitness is measured against one opponent, the previous
  best, so opponent-specific exploits are rewarded. The noise is then the opponent × draw interaction, not the
  member × draw interaction. RBT-113 does not use this mode (it is solo), so this was not probed.
- **The recursive limit** is only a moderate gear lever on its own (0.5% per call). It matters in combination: a new
  Connection to a node whose limit is 2–3 instances that node's Effectors several times.
- **Effector duplication on the same DOF.** Outputs are summed and then clipped (`brain.py:105`), so adding Effectors
  saturates a motor more easily. This is a small additional path to throttle.
- **`c.child %= n` in crossover** rewires connections to arbitrary nodes. It mostly produces unreachable nodes and
  feeds finding 5.

## Probes

| file | what | runtime |
|---|---|---|
| `drift_lineage.py` / `.txt` | size traits by line and fauna, gen 0 → 23, all 24 RBT-113 directories | 5 s |
| `reach.py` / `.txt` | per-mutation gear, driven DOFs, link survival, food routes; neutral walk; crossover bias | 11 s |
| `gear_levers.py` / `.txt` | per-operator-class gear moves | 15 s |
| `noise.py` / `.txt` | repeatability and selection coefficients, RBT-113 O1 seed 1 U line (needs the checkpoint) | 60 s |
| `ecology_s.py` / `.txt` | the ecology economy, shuffled against richest-first, with and without erosion | 26 s |
| `bias_walk.py` / `.txt` | walk of Effector and global biases against link weights, default, Z and holistic | 21 s |
| `effector_bias_lines.py` / `.txt` | resting drive by line in the committed RBT-113 O1 genomes (needs the checkpoint) | 3 s |
| `parity.py` / `.txt` | per-child link and route loss, holistic `mutate` against designed `mutate_controller` | 10 s |

The limits of what was measured:
- `noise.py` covers one seed and one line.
- `effector_bias_lines.py` covers one arm (O1, 3 seeds). The designed D result, 99.2% of 240 Effectors, is not
  borderline. The C and U figures should be re-checked on O2–O4.
- `ecology_s.py` is synthetic, and its μ and σ are assumptions.
- "Food route" is a structural predicate (existence and a nonzero weight), not a working compass.
