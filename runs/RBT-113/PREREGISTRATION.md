# RBT-113 pre-registration: how evolvable is the simulator? A bidirectional selection-response benchmark

*Designer's pre-registration, 2026-09-27. **No arm has been launched.** The only simulations made for it are the
founder pilot (§2.2), the golden runs of the byte-identity test (§3), a throwaway 8-generation U/D/C smoke at seed 1
(outside the checkout, used only for timing, §9) and the pre-launch controls' tiny arms (§6).
**Gating (the ticket, the coordinator's 14:25 comment):** the arms wait for a design adversary and the coordinator's
ruling. Nothing from RBT-107 was read. Every number below is read from a committed file beside this one, named at the
number.*

**The question.** One number for how strongly this simulator responds to selection, measured by the classic
bidirectional design: replicate lines selected **up** and **down** on one heritable whole-body trait, plus
unselected **control** lines, so that a later tweak of the operator or the world can be scored by whether it raises
the response while the controls stay flat.

**The design in one paragraph.**
- **The trait:** an individual's **solo net foraging yield** (items eaten minus 0.03 per kJ of actuator work) in
  paper 5's foraging world, averaged over two start draws shared by its generation: the ecology's own income,
  measured alone, with no arena and no opponent (§2).
- **The population:** the **holistic fauna** from random founders is primary. The designed body (compass-free,
  random controllers, controller topology evolving) is carried in the same runs at no design cost and is where the
  operator comparison lives (§4.3).
- **The mechanism:** `evolve` (discrete generations) with a new, tested, off-by-default hook,
  `--truncation 0.25 --line up|down|control` (§3).
- **The design:** 40 individuals per line per fauna, the top / bottom / a random 10 bred each generation, 24
  generations, 12 seeds; U, D and C at a seed share their founders and every generation's worlds (§4).
- **Operators:** default and RBT-112's `--global-bias-sigma 0` (Z). **Z does not reach the holistic fauna** (it acts
  only through the designed body's controller mutation; pinned by a test), so the Z arms run with
  `--holistic-stream-salt 1`: their holistic lines become 12 more independent holistic replicates, while their
  designed-body lines stay paired seed for seed with the default arms (§4.3).
- **Readout:** divergence per generation and realised heritability, each with a t CI and a sign-flip p across seeds;
  up and down responses against the control; verdicts fixed in `readout.py` (§5).
- **Power:** a planted h2 of 0.02 is detected with probability 0.99 at 12 units, with a 3% (arm) / 1% (seed) false
  positive rate at the null (`power.txt`, §5.3).
- **Cost:** 8 arms of about 1.5 h, two per session, four sessions (§9).

---

## 1. Why this shape

- **Why `evolve` and not the ecology.** The ecology has overlapping generations, no rank and slot-limited
  reproduction (paper 5 §3: about thirty seasons per reproduction event), so "response per generation" is not
  defined there and truncation would have to be bolted onto a birth-death economy. `evolve` already has discrete
  generations, a solo evaluation path (`--locomotion-phase`), per-fauna random streams (RBT-85) and a byte-exact
  resume (RBT-93). Imposed truncation is one parent-choice rule in `reproduce`. This is the smallest honest hook.
- **Why solo yield.** It is the only candidate whose heritability can be checked on committed data (§2.1), it is
  the quantity natural selection acts on in the ecology (so the benchmark measures the currency the programme cares
  about), it has room in both directions (up: find and eat food, stop wasting work; down: eat nothing and burn work),
  and it is measured alone. **Distance per kJ was rejected:** a random holistic founder's median work is 4 kJ per
  season and its tenth percentile is 0 (`pilot.txt`), so the ratio is undefined or explosive for a large share of the
  founders, and it is not recorded per individual in any committed data.
- **Why random founders.** The holistic fauna's evolvability *from scratch* is the funder's question ("holistic
  evolution working"). An evolved base population would give a cleaner Gaussian trait but no committed genomes exist
  (they are bulk), and the answer would then be about one population's residual variance rather than the simulator.

## 2. The population and the trait, with its heritability checked

### 2.1 On committed data (`h2_committed.py` → `h2_committed.txt`)

Parent-offspring correlation of lifetime mean yield (paper 5 §4's statistic, children and parents with ≥ 5
evaluations), read from committed `lineage-last.txt` of the foraging ecology, the trait's ecology twin:

| runs | holistic r | designed body r |
|---|---|---|
| RBT-71 forage-804/805/806 (paper 5's fresh seeds) | **0.399, 0.381, 0.337** | 0.229, 0.276, 0.252 |
| RBT-71 neutral-804/805/806 (paired drift controls) | 0.070, −0.063, −0.129 | 0.237, 0.338, 0.351 |
| RBT-106 HU-801/804/805 (w = 32 designed body) | 0.352, 0.354, 0.361 | 0.416, 0.400, 0.465 |

Each with 592–713 pairs and a bootstrap CI in the file. This reproduces paper 5 §4 exactly (0.40, 0.38, 0.34; the
controls +0.07, −0.06, −0.13; the wheeled 0.24, 0.34, 0.35 under drift). What it certifies, as paper 5 says: yield is
a heritable measurement for any body that eats; the holistic *drift* control reads zero because random lumps never
learn to eat. That is the warning the pilot answers.

### 2.2 On the benchmark's own founders (`pilot.py` → `pilot.txt`)

40 founders per fauna drawn as `evolve` draws them, one child each by the fauna's own operator (no crossover, no
selection), each scored solo on 2 fresh draws of the benchmark world:

| | holistic | designed body |
|---|---|---|
| yield: mean, SD, p10 / p50 / p90 | +0.012, 0.136, −0.056 / 0.000 / 0.000 | +0.078, 0.709, −0.736 / +0.007 / +1.031 |
| child-on-parent slope of yield [95% CI] | −0.06 [−2.5, +1.1] | **+0.43 [+0.12, +0.70]** |
| child-on-parent slope of work (kJ) | **+1.04 [+0.86, +1.34]** | +0.68 [+0.40, +0.90] |
| child-on-parent slope of path (m) | +1.79 [+0.51, +2.72] | +0.79 [+0.08, +1.06] |
| founders with \|yield\| > 0.001 | 38% | 100% |
| seconds per solo season (1 core) | 0.27 | 0.35 |

So the designed body's yield is heritable among its founders (0.43), and the holistic founders' yield is a
zero-inflated trait whose variation is mostly its work term, which is strongly heritable (+1.04): a founder that
flails passes flailing on. **Stated expectation, before any arm:** the holistic down line will respond fast (select
flailers), the up line more slowly and in two phases (stop wasting work, then find food), so the up-down asymmetry is
expected and is reported, never averaged away (§5.2). The throwaway 8-generation smoke at seed 1 (timing only, not
committed, not evidence) was consistent with a response in both faunas.

## 3. The mechanism (`rabbitstew/evolution.py`, `rabbitstew/cli.py`; `tests/test_rbt113.py`)

- `EvolutionConfig.truncation` (default 0.0 = off) and `line` ("up", "down", "control"). When on, `reproduce` draws
  every child's parent, and its crossover partner (probability `crossover_rate`, 0.5), uniformly from
  `truncation_pool`: the top `k = round(P n)` by fitness (up), the bottom `k` (down), or `k` drawn uniformly without
  replacement from the fauna's own stream (control). Each parent's expected share of the next generation is `1/k` on
  every line: the three lines differ in which members breed and in nothing else, so the control has the same number
  of parents and the same drift.
- It refuses `elites`, `survival`, `archive` and `morph_protection`, which would breed outside the pool.
- `evolve --truncation P --line L` sets it; `evolve --global-bias-sigma S` passes RBT-112's field into the mutation
  config (as `ecology` already does). `cmd_evolve`'s config construction moved into `evolve_config(args)` unchanged,
  so the pilot, the tests and the arms build their config through the CLI's own code.
- **Byte identity.** Off, `config.json` carries neither key, and nothing else changes. Two tiny `evolve` runs (the
  default competitive task, and the benchmark's solo foraging world under tournament selection) write
  `config.json`, `lineage.jsonl`, `history.json` and `state.json` with sha256 digests **recorded on the pre-hook
  code** (integration head 5d69581); the test asserts the new code writes the same bytes with the flags absent, with
  `--truncation 0`, and with `--truncation 0 --line down`.
- **The modes select as specified** (tests): the pool is exactly the top / bottom k, or a uniform draw uncorrelated
  with fitness (400 draws); `reproduce`'s children have parents only in the pool, none an elite copy; a real run's
  `lineage.jsonl` has every U parent among the top 2 of 8 and every D parent among the bottom 2, generation by
  generation, in both faunas; U and C at one seed have identical founders and identical worlds; `--global-bias-sigma
  0` leaves the holistic lineage identical and changes the designed body's; the salt moves only the holistic lineage;
  a truncation run resumed mid-way is byte-identical to an uninterrupted one.

## 4. The design

### 4.1 Lines, sizes, selection intensity (`world.py`, the single source)

| parameter | value | why |
|---|---|---|
| individuals per line per fauna | N = 40 | two faunas x 40 x 2 draws = 160 solo seasons a generation, 12.6 s on 4 cores |
| proportion selected | P = 0.25, k = 10 | intensity i ≈ 1.27 (standard normal truncation), k large enough that drift (Ne ≈ 2k) does not dominate 24 generations |
| draws per individual per generation | D = 2, shared by the generation and every line at the seed | halves the per-season noise; sharing makes the world a common effect that cancels in U − D, U − C, C − D |
| generations | G = 24 (23 rounds of selection) | responses show within tens of generations (the ticket); fits the timetable |
| seeds | 12 (1–12) | power (§5.3) |
| elites | 0 | discrete, non-overlapping generations |

The world is paper 5's (RBT-90 part 2's flags): 12 items, radius 3, eat radius 0.35, decay 1.0, work cost 0.03,
15 s, mass budget 15.34, random terrain and start, `foraging` vocabulary, `--conventional-topology`, `--score food`.
Every generation is solo (`--locomotion-phase 24`); champion bouts are off.

### 4.2 Arms

An **arm** is one operator on a block of three seeds, each seed's U, D, C runs in sequence (`run_arm.sh`):
O1–O4 (default operator; seeds 1–3, 4–6, 7–9, 10–12) and Z1–Z4 (Z; the same seed blocks). 8 arms, 72 line runs.

### 4.3 The operator, and why the Z arms are salted

`--global-bias-sigma 0` freezes the global-brain biases in `mutate_weights`, which the designed body reaches through
`mutate_controller`. The holistic `mutate` never passes it: **the holistic fauna is untouched by construction**
(the flag's own help, and `test_global_bias_sigma_leaves_the_holistic_line_alone`). Running Z unsalted would
therefore duplicate the default holistic lines byte for byte and buy nothing on the primary fauna. With
`--holistic-stream-salt 1` (RBT-96) the Z arm's holistic lines are drawn from an independent stream: new founders,
new mutations, the same worlds, while the designed body's founders, mutations and worlds are exactly the default
arm's at that seed (`test_salt_moves_only_the_holistic_line`). So:
- **holistic:** 24 independent replicate triplets under the (only) operator that reaches it, averaged in pairs
  into 12 per-seed units (the two replicates at a seed share their worlds, so they are not counted as independent);
- **designed body:** 12 default and 12 Z triplets, **paired by seed**, for the before-and-after number.

**Is the fixed-body side worth a line?** Yes, and it costs nothing extra: `Experiment` always runs both faunas, so
every run is also a designed-body line. It is secondary for the funder's question and primary for the operator
question, because that is the only fauna the operator acts on.

## 5. Statistics (`readout.py`, fixed before any data)

### 5.1 Per arm (one seed, one fauna), in units of σ0

**σ0 is one scale per fauna:** the median, over that fauna's arms, of the SD of generation-0 fitness (which is
identical on an arm's three lines). Not each arm's own SD: the pre-launch run found one holistic founder that ate
about six items in its single draw, which made that arm's generation-0 SD 1.68 against 0.056 at the other seed
(`controls/smoke-readout.txt`). A per-arm scale would weight seeds by their founders' luck; one scale per fauna keeps
every statistic in the trait's own units up to one constant. `h2` is scale-free.

- `m_L(t)`: the line's mean trait in generation t; `S_L(t)`: the realised selection differential, the mean over
  generation t+1's children of their parents' mean fitness, minus `m_L(t)` (so a parent counts once per child).
- `div(t) = m_U(t) − m_D(t)`, zero at t = 0 by construction (a control, §6).
- **`b_div`**: OLS slope of `div(t)` on t, the divergence per generation. **Primary statistic.**
- **`h2`**: realised heritability, the regression through the origin of `div(t)` on the cumulative divergent
  differential `Σ_{τ<t}(S_U − S_D)(τ)` (Falconer and Mackay ch. 11; Hill 1972).
- `b_up`, `b_down`: OLS slopes of `m_U − m_C` and `m_C − m_D` on t, and `h2_up`, `h2_down` likewise against their
  own cumulative differentials: the asymmetry.
- `b_C`: the control's own trend, `m_C(t) − m_C(0)` on t (mutational bias plus the worlds).

### 5.2 Across units

Mean, two-sided 95% t CI (a t table for df ≤ 40 is in the file; no scipy), and an exact sign-flip p (≤ 16 units; else
20,000 draws). Units: holistic, one per seed (salt-0 and salt-1 replicates averaged); designed body, one per arm per
operator; the operator comparison, the paired per-seed difference Z − default.

### 5.3 Null and power at the planned n (`power.py` → `power.txt`)

- **The null** is *nothing heritable*: h2 = 0 and no mutational variance. Under it U and D are two drift lines
  with exchangeable signs, so `b_div` has mean 0 and the sign-flip test is exact. (Mutational input is itself
  heritable variance and a response built on it is real evolvability, not a false positive; an earlier version of
  the power model that put mutational variance into the "null" found it responding, which is why the null is stated
  this way.) The **matched empirical null** is the control line: every response is read against C at the same seed.
- **The model:** founders with breeding values of variance h2 and phenotypic SD 1; a world effect (SD 0.3) shared
  by the lines each generation; truncation of k = 10 of 40; parents from the pool with a partner at 0.5 (mid-parent
  plus segregation); a mutational bias of −0.02 σ0 per generation on every line; and a `floor` variant with the
  lower 40% of the trait censored to one value, a crude stand-in for the holistic founders' mass at zero yield. It
  goes through the readout's own `arm_stats`, `t_ci`, `sign_flip_p` and verdict rule.
- **Result** (150 simulated benchmarks per row, 12 units; `power.txt`):

  | scenario | planted h2 (V_m = 0) | P(RESPONDS), arm unit | P(RESPONDS), seed unit (2 replicates) | realised h2 estimated |
  |---|---|---|---|---|
  | gaussian | 0 (null) | 0.033 | 0.007 | 0.000 |
  | gaussian | 0.02 | 0.987 | 1.000 | 0.009 |
  | gaussian | 0.05 | 1.000 | 1.000 | 0.020 |
  | gaussian | 0.40 | 1.000 | 1.000 | 0.123 |
  | floor | 0 (null) | 0.013 | 0.033 | 0.000 |
  | floor | 0.02 | 0.813 | 0.987 | 0.007 |
  | floor | 0.05 | 0.953 | 1.000 | 0.015 |

  The false-positive rate is at or below 0.05 in both scenarios; a planted h2 of 0.05, a seventh of the smallest
  committed estimate (0.34), is detected with probability ≥ 0.95 even when 40% of the trait is censored. With
  V_m = 0.01 and h2 = 0 (mutation alone) every benchmark responds, as it should. **The realised h2 reads 0.3–0.5 of
  the founders' h2** in this model because 24 generations at k = 10 with no mutational input exhaust the variance
  (drift, Bulmer): the benchmark's h2 is a property of the whole 24-generation run, and it is compared across
  operators only at this design.
- **The operator comparison is the weak part.** In the same model, unpaired (conservative: the real pairs share
  founders and worlds), 12 pairs detect Z raising h2 from 0.2 to 0.4 with probability 0.53, to 0.3 with 0.28, and
  call it at Δh2 = 0 with 0.073 (150 draws; within noise of 0.05). So a Z RAISES or LOWERS verdict is informative,
  and an INCONCLUSIVE one is the expected outcome for a modest operator effect. Doubling the designed body's pairs
  would need four more sessions; the design does not do it, and says so.

### 5.4 Pre-registered thresholds (constants in `readout.py`)

- `MDE_DIV = 0.05` σ0 per generation: the divergence rate a NO RESPONSE call must exclude.
- `EQUIV_OP = 0.05` σ0 per generation: the operator comparison's equivalence margin.
- The per-arm check that the manipulation reached the trait is scale-free (§7.4). A threshold in σ0 per
  generation was drafted and dropped before any data: the pre-launch run failed it on the arm with the lucky founder,
  where the holistic U line sat within 0.011 of zero yield from generation 1 on, and a realised differential near 0
  is the right answer, not a broken manipulation.

## 6. Verdict rules (as coded)

- **Any per-arm control fails → the whole readout is VOID** (no verdict is printed from it).
- Per fauna (holistic; designed body under each operator):
  - **RESPONDS** if the 95% t CI on mean `b_div` excludes 0 above and the sign-flip p < 0.05. The benchmark
    number is then `b_div` and `h2`, each with its CI, and `b_up`, `b_down` beside them.
  - **NO RESPONSE at the powered effect** if the CI's upper end is below `MDE_DIV`.
  - **INCONCLUSIVE** otherwise.
- **Operator (designed body), paired by seed:** **Z RAISES** (or **LOWERS**) the divergence rate if the CI on the
  mean paired difference excludes 0 and p < 0.05; **NO CHANGE** if the CI lies inside ±`EQUIV_OP`; else
  **INCONCLUSIVE**.
- The headline sentence for the funder is the holistic `b_div` and `h2` with CIs, with the asymmetry stated.

## 7. Per-arm controls, shown passable (`prelaunch.py` → `controls/prelaunch.txt`, `controls/smoke-readout.txt`)

Checked by `readout.py` on every arm, each shown passing on a tiny real benchmark (population 12, 5 generations, a
default and a Z arm at seed 1) through the arms' own command line, and required by `run_arm.sh` (exit 7):
1. **The configs** are the pre-registered ones: line, truncation, generations, solo throughout, no elites, operator
   and salt matching the arm; U, D and C differ in the line alone.
2. **The pairing:** generation 0 (names and fitness) is identical on U, D and C, in both faunas; and the designed
   body's generation 0 is identical between the default and Z arms at a seed.
3. **The selection mechanics** (the manipulation, not only its intent): in every generation of every line, at most
   k distinct parents, all from the previous generation; every U parent is in the top k and every D parent in the
   bottom k by recorded fitness.
4. **The manipulation reached the trait:** the cumulative divergent differential `Σ_t (S_U − S_D)(t)` is positive
   in every arm and fauna (without it `h2` is undefined). Exact pool membership (3) is the manipulation check proper;
   the realised differential can legitimately be near zero, or even negative in one generation, when a line has
   lost its variance or its pool holds one outlier (the offspring-weighted mean of a skewed pool can sit below the
   generation mean), so it is required only on balance.
5. **Complete:** every line has all 24 generations.
Plus the **positive control** (a simulated positive at a stated effect size): P(RESPONDS) ≥ 0.80 at planted
h2 = 0.05 per-arm units and ≤ 0.10 at the null, in both scenarios, re-run by `prelaunch.py` on the tree the arms run;
and the **round-trip** of the readout (`test_readout_recovers_a_planted_realised_heritability`): lines built to
respond exactly h2 x their cumulative differential return h2, `b_up`, `b_down`, `b_div` exactly, and the realised
differential from lineage rows is the offspring-weighted one.

## 8. Side effects, and correlated responses

**Side effects.**
- Code: `evolve` gains three flags; off, every existing run reproduces byte for byte (§3). The ecology is untouched.
  `cmd_evolve` is refactored into `evolve_config(args)` with the same fields.
- Compute and storage: 8 arms, about 24 CPU-hours (§9); per arm about 6 MB of committed evidence (38 files,
  `lineage.jsonl` about 0.6 MB each) and a checkpoint branch `ckpt/rbt-113-ARM` for the bulk.
- Interpretation: this measures evolvability *of solo yield from random founders in paper 5's world at N = 40 over
  24 generations*. It is not the ecology's rate, not a statement about competitive scores, and it is a property of
  the world as well as the operator (RBT-19: patchiness halved yield heritability). A tweak to the world needs its
  own benchmark run.

**Correlated responses (descriptive only; no verdict, no test).** `readout.py` prints, per fauna, the U − D
divergence slope per generation of distance, nodes, parts, units, links and mass, each in its founders' SD with a t
CI. What else in the body and brain moves is read from that table and not claimed beyond it.

## 9. Cost and the wave plan

- **Measured:** a solo season costs 0.27 s (holistic) and 0.35 s (designed body) on one core (`pilot.txt`); a
  benchmark generation (160 solo seasons plus bookkeeping) took 12.6 s on 4 workers in the 8-generation smoke,
  flat across generations (11–18 s) and lines, about 50 CPU-seconds.
- **Per arm:** 9 runs x 24 generations = 216 generations x 50 CPU-s = 3.0 CPU-h, **about 1.5 h wall** at WORKERS=2
  with two arms side by side on 4 cores. Budgeted at **2.25 h** (x1.5 for bodies that grow costlier under selection
  and for contention).
- **Total:** 8 arms, 24 CPU-h, **4 sessions x 1.5–2.25 h = 6–9 session-hours**, plus about 10 minutes per session
  for the venv, suite and pre-launch controls.
- **Timetable fit:** ruling about 16:45; sessions launched by about 17:00; arms complete by 18:30 (2.25 h budget:
  19:15); eight arm PRs merged by about 19:30; readout (seconds) and its report by 20:30; the readout adversary and
  ruling by 22:00. **The full design fits.** If a session is lost, its two arms' seeds are dropped and the readout
  runs on the rest at reduced power (not re-simulated: `power.py` fixes 12 units); the controls are never
  trimmed. If the coordinator can afford a fifth session, seeds 13–15 (O5, Z5) are the largest version that still
  fits, and `run_arm.sh` would need only the two case lines.

## 10. What the adversary should attack first

1. Whether the realised differential should be the pool's (intended) or the offspring-weighted one (used here).
2. Whether σ0 units are the right yardstick for the holistic fauna, whose trait is zero-inflated and heavy-tailed
   (SD 0.136 in the pilot with 2 draws; 0.056 and 1.68 at two seeds of the tiny pre-launch run): the pooled median
   is the design's answer, and `readout.py` prints each arm's own SD in raw units beside it. The verdicts are
   sign and CI rules on means across seeds, so a single scale only relabels the thresholds.
5. Whether the holistic U line stalls at zero yield (non-movers) once work is selected away, so that the benchmark
   reads mostly the down line: the pre-launch run's holistic U lines sat within 0.011 of zero from generation 2 (1 on Z1). That is the expected
   two-phase response (§2.2), `b_up` and `b_down` report it separately, and the headline states it.
3. Whether the salted Z holistic replicates are exchangeable with the default ones (they share worlds per seed; the
   per-seed averaging is the conservative answer).
4. Whether 24 generations of truncation at k = 10 exhaust the holistic founders' variance (the realised h2 is an
   average over the run and falls below the founders' h2 as drift and the Bulmer effect erode it; `power.txt` shows
   by how much in the model).
