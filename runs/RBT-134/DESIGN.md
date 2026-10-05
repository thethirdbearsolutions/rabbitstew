# RBT-134 design (pre-registration draft r3, DESIGN ONLY): operator changes that let mutation propose a paying compass

**Status.** r2 answers the design adversary's review of r1 (PR #539, `runs/RBT-134/design-adversary/ADVERSARY.md`,
verdict REGISTER AFTER FIXES) and the coordinator's rulings on it. r3 makes only the fix-check's edits on r2
(`ADVERSARY.md`, "## Fix-check (r2 678681a)"): FC-M1, FC-S1 and FC-N1–N3. The revision log is §R at the end.

- Nothing here has run as an assay, and no switch is implemented.
- Nothing under `rabbitstew/`, `scripts/` or `runs/RBT-129/` is touched. The only files are under `runs/RBT-134/`.

**What was run to price and ground this design.** None of it read RBT-129 data, a run log, an `epa_overflow` file or
any `ckpt/*` branch. `ckpt/rbt-113-O1` has been released read-only for building the H2 battery (§5.3). It has
**not** been fetched for this revision.

- **`decompose_arrivals.py`.** It regenerates RBT-91's committed structural arrivals (84, 63 and 66) from their lineage
  indices and re-reads their links-alone response under single-factor counterfactual edits. Outputs are
  `decompose_arrivals_{baseline,1.6,4.0}.txt`.
  - It reproduces every committed links-alone value: 84 of 84, 63 of 63 and 66 of 66 (`decompose_arrivals_baseline.txt:90`,
    `_1.6.txt:69`, `_4.0.txt:72`). The adversary reproduced the r1 outputs byte for byte (ADVERSARY N2).
  - r2 changes two things in it:
    - the corrected slope bound for `abs` (M1);
    - the `sign`-flip flag (M2).
  - It reads only conditions RBT-91 already ran and published. **No candidate condition was run.**
- **`power.py` → `power.txt`.** Stdlib only. It reads no data.
- **Timings only, not committed.**
  - `structural_rate.py --n 2000`: 4,000 lineages in 44.6 CPU-s.
  - `--background 4000`: about 12 ms per background lineage.
  - RBT-112's `baseline.py` for seed 801: 65 CPU-s, and it reproduces the committed `baseline-w32-801.txt` byte for byte.
  - 19 holistic `mutate` steps plus `synthesize`: 10–15 ms per lineage on the two holistic pools of §5.

---

## 0. Summary

1. **The ticket's premise needs two corrections from the merged record.**
   - **The rung.**
     - The 6.8664 in "0 of 84" is a **whole-brain** reading of the installed motif. The motif's own links read
       **12.5236** at the first paying rung (a = 32), 6.2831 at a = 16 and 24.7145 at a = 64 (`ERRATA.md:142`, H41;
       `runs/RBT-72-adversary/probe_rung.txt:2-4`).
     - This design scores links alone against 12.5236 and prints the other three readings. The default operator's 84
       arrivals read 0 at every rung (`decompose_arrivals_baseline.txt:107`).
     - The switch makes "moving off 0" harder, not easier (ADVERSARY N1).
   - **Prior art.**
     - RBT-104's `--link-scale K` has already gone through this exact instrument. It scales the link step, the link
       draws **and the parents' links** together.
     - At K = 8 it moved links-alone ≥ 12.52 to **8 of 84**. It also raised the structureless whole-brain background to
       2.18% at ≥ 6.28 on 3,998 lineages, against about 0.26% (`runs/RBT-104/PREREGISTRATION.md:127-130`;
       `runs/RBT-104/drift-reach-k8.txt:105-117`).
     - So what remains untested is a change that grows **the circuit relative to its host**. A uniform scale cannot
       do that, because it scales both (`runs/RBT-104/PREREGISTRATION.md:148-153`).
2. **The mechanism, measured on RBT-91's own arrivals** (§1).
   - The widening did reach the magnitude. At `weight_sigma` 4.0 the four links' product clears 12.52 in **42 of 66**
     arrivals (`_4.0.txt:92`), and every one of them reads 0 as is (`_4.0.txt:89`).
   - **Link magnitude together with the bias offsets** takes it back. The interneuron's resting output v·f(b_k)
     saturates the drive Effectors, and the Effector biases add to that.
     - Zeroing both biases recovers 24 of the 57 non-`sign` arrivals (`_4.0.txt:91`).
     - Zeroing either alone recovers 3 or none (`_4.0.txt:90`; the `tE` column).
     - This is RBT-104's resting-drive mechanism (ADVERSARY N2).
   - The transfer-function draw matters too:
     - `sign` and `differentiate` are deaf at the probe;
     - `abs` is attenuated, at slope sech²(b_k).
   - At the default step no bias treatment can help: the links' product never exceeds 3.68 (`_baseline.txt:115`).
3. **Bounds decide four candidates before they run** (§2.2).
   - Under a change that moves only biases (or adds nothing to the links), a lineage's links and structure are those of
     a committed twin. Its links-alone response is then at most |product| × max f′, among probes not flagged for the
     `sign` artefact.
   - **A0** (bias decoupling alone at the default link step) is bounded at 0 at every rung.
   - **P1** (the decoupled link step at 1.6) is bounded at ≤ 2 at a = 32.
   - **P4** (fan step) and **P5** (differencing-unit event) have expected counts of at most 2.96 and 0.01 by the
     adversary's arithmetic (ADVERSARY M3).
   - All four run as **checks** with their bounds or ceilings printed. None is in the tested family.
4. **The registered family is two candidates on the Pioneer, Holm at 0.05 (m = 2).**
   - **P2**: the link step at 4.0 with the bias steps left at 0.4. It is bounded at ≤ 29 (`_4.0.txt:95`).
   - **P3**: P2 plus a bias reset. It shares P2's links and arrival set (§2.1, S2), so it is also bounded at ≤ 29.
   - Each verdict is PASS, MOVES-WITH-BACKGROUND or NULL (§4).
   - The background clause is one non-inferiority rule for every candidate (§4).
   - §6.4 shows the rule can return each verdict on measurements already merged.
5. **The holistic fauna** (§5).
   - The structural census on the same lineage protocol now has two arms:
     - (a) the global differencing route;
     - (b) the **per-instance (Braitenberg) route**: a duplicated sensor-bearing node, each instance with its own
       nose → Effector loop (ADVERSARY M4).
   - The functional `steer.py` stage (H2) uses the registered W1 battery built from the released RBT-113 O1 hosts. A
     registered fallback battery screened on committed hosts covers the case where that build fails.
   - There is **no holistic links-alone rung** (§5.1).
   - Duplication is no longer "cut". The existing operator already duplicates parts, and arm (b) measures what that
     proposes.
6. **Costs and gating.**
   - About 15–18 CPU-h runnable after the ruling.
   - H2 up to about 62 CPU-h.
   - RBT-113's selection response is about 12 CPU-h per carried candidate and covers both faunas.
   - Nothing needs an ecology run, and nothing merges while RBT-129 is live.
   - *Pointer (F9, post-registration):* the code PR #541 merges before the RBT-129 Stage-2a launch, per
     `runs/RBT-129/coordinator/OWNER-DECISIONS-2026-10-04.md` item 6.

---

## 1. The mechanism RBT-91 named, measured factor by factor

RBT-91's decision names three things (`docs/rbt-91-weight-scale-decision.md:45-48, 242-245`):
- `weight_sigma` drives both the link-weight step and the unit-bias step (`rabbitstew/genetics.py:134-146`);
- biases have no reset and no clip, so `sd(b) = 0.2·√depth` and `sech²(b)` collapses;
- widening inflates the recurrent background, not the circuit (decision `:28-43`).

**The response being decomposed.** The predicate unit's links-alone response (`runs/RBT-91/structural_rate.py:143-163`)
is a chain:

`a = (u_L − u_R)/2 · f′(b_k) · mean_E[v_E · sech²(b_E + v_E·f(b_k))]`

- f is the unit's transfer function; `brain.py:78-93` lists the seven.
- The two drive Effectors are `tanh` (`brain.py:54`).
- The predicate requires v_L and v_R of the same sign (`structural_rate.py:96-98`).
- So `|a| ≤ |(u_L − u_R)/2 · (v_L + v_R)/2| · max f′`. Call the first factor the **link product**.

`decompose_arrivals.py` edits one phenotype at a time and re-reads the response:
- `tanh`: the unit's function set to tanh;
- `b_k=0`: its bias set to 0;
- `b_E=0`: the drive Effectors' biases set to 0;
- their pairs, and all three ("unit slope").

These are bounds on what a bias or function change could buy **the arrivals that exist**. None of them is an operator.

| RBT-91 condition | arrivals | as is, ≥ a32 | tanh + b_k=0 | b_k=0 + b_E=0 (non-`sign`) | unit slope (= link product) | slope bound ≥ a32 (§2.2) | \|b_k\| median | max\|b_E\| median |
|---|---|---|---|---|---|---|---|---|
| `weight_sigma` 0.4 (default) | 84 | 0 | 0 | 0 of 72 | **0** (max 3.68) | **0** | 0.76 | 1.26 |
| 1.6 | 63 | 0 | 1 of 55 | 2 of 55 | 2 | **2** | 2.59 | 3.44 |
| 4.0 | 66 | 0 | 3 of 57 | 24 of 57 | **42** | **29** | 6.41 | 9.48 |

Sources: `decompose_arrivals_baseline.txt:107-115`, `_1.6.txt:86-94` and `_4.0.txt:89-97`. The a = 16 and a = 64 columns
are printed beside these lines. The `sign`-flip flag (§3, M2) fires on **none** of the as-is probes (`_baseline.txt:91`,
`_1.6.txt:70`, `_4.0.txt:73`).

1. **At the default step, magnitude binds absolutely.** The largest link product among the 84 is 3.68, below the null
   rung of 6.28, so no bias or function change can lift a default-step arrival to any own-link rung. This is RBT-91's
   "magnitude is the barrier that binds" (decision `:52-55`), with a proof attached.
2. **At 4.0 the links get there, and the resting drive takes it away.**
   - In 42 of 66 arrivals the link product clears a = 32; as is, 0 do.
   - Zeroing both biases recovers 24 of 57. Fixing the interneuron alone (tanh, b_k = 0) recovers 3, and tanh with
     b_E = 0 recovers 0.
   - The output link multiplies the interneuron's resting output f(b_k), so a large v pushes the Effector into
     saturation unless b_k is near 0 (RBT-104, `runs/RBT-104/PREREGISTRATION.md:136-146`). A walked Effector bias adds
     to it (RBT-121 audit B finding 1, `runs/RBT-121/ga/AUDIT.md:90-100`).
   - So the mechanism is **link magnitude × bias offset**, not the walk alone (ADVERSARY N2).
3. **The transfer-function draw.** `random_neuron` draws the function uniformly from seven (`rabbitstew/genotype.py:596-598`;
   vocabulary `genotype.py:71`). At the probe:
   - **`sign`** has zero slope off its flip window;
   - **`differentiate`** is 0 once settled;
   - **`abs`** (`tanh|x|`, `brain.py:85`) has slope sign(b_k)·sech²(b_k), so it is attenuated, not deaf.

   r1 called `abs` deaf; that was wrong (ADVERSARY M1). `sign` and `differentiate` are 19 of the 84 default arrivals,
   and `abs` is 6 (`_baseline.txt:92`).
4. **The widening also made the background.** RBT-91's structureless background rose from 0.26% to 1.64% (decision
   `:30-32`). That rise belongs to the links: biases only lower slopes. A link-only widening (P2) is therefore expected
   to inflate the background **at least as much** as the coupled one did.

---

## 2. Candidate switches

Every switch is a `MutationConfig` field, off by default.

**Shared requirements.**
- Off, the operator is byte for byte as it is now: no extra random number is drawn, and this is tested (I7).
- **Separate streams (S2).** A switch that needs extra random numbers draws them from an auxiliary generator.
  - The mutation functions gain an optional `aux_rng` argument. With `aux_rng=None` they fall back to the main `rng`,
    so any other caller is defined.
  - The assay passes, for lineage i, `aux_rng = default_rng(SeedSequence([MASTER_SEED, crc32(label), 19, i, 134]))`.
  - The main stream then stays draw for draw B0's. A bias reset still makes, and discards, the main stream's step draw.
- Steps use the RBT-112/124 convention `N(0,1) × S`, so the main stream is unchanged at any S (`genetics.py:59-75`).
- Implementation stays on this branch until RBT-129 releases `rabbitstew/`. *(F9: #541 merges before the Stage-2a
  launch, per `runs/RBT-129/coordinator/OWNER-DECISIONS-2026-10-04.md` item 6.)*

### 2.1 The registered family (Pioneer, `mutate_controller`)

**P2: `link_sigma = 4.0`.**
- **Switch.** The link step is N(0,1) × 4.0. Every bias step stays N(0, 0.4). New links are still N(0, 1).
- **Mechanism.** Magnitude, with the bias walk decoupled from it.
- **Its twin.**
  - Its links and structure are those of RBT-91's σ = 4.0 lineages, and its biases are B0's.
  - Its arrival set is `RBT-91-alone-4.0.txt`'s 66, and it is bounded at ≤ 29 at a = 32 (`_4.0.txt:95`).
- **Available today on the Pioneer without touching `rabbitstew/`.**
  - It equals `weight_sigma 4.0, global_bias_sigma 0.4, effector_bias_sigma 0.4`.
  - That holds because the designed parents carry only global neurons and segment Effectors: W4b-801 has 49 global
    neurons and 14 Effectors, P-801 393 and 120 (measured).
  - `mutate_controller` adds neurons only to the global brain (`genetics.py:389-391`).
  - The new field is needed for the holistic fauna, and its equality to this composition is a byte-identity test (I7).

**P3: P2 + `bias_reset_rate = 0.2`.**
- **Switch.** A perturbed non-sensor bias is redrawn from its birth law N(0, 0.5) with probability 0.2, instead of
  stepped. The coin and the redraw come from `aux_rng`.
- **Mechanism.** The resting-drive saturation (§1, point 2): b_k and b_E far from 0.
- **Its twin.** Its links and structure are P2's, so its arrival set is the same 66 and it is bounded at ≤ 29. Its
  biases are B0's except where reset.

**Why each value.**
- **P2 at 4.0.**
  - It is RBT-91's post-hoc widening, so P2's matched null (RBT-91 coupled σ = 4.0: 0 of 66, background 1.64%) has
    the same links. P2 against it is the direct test of "the coupling takes the gain".
  - 1.6 is P1 and is decided (§2.2).
  - **P2 is a determinate computation from committed data, not a sample (S4).** Its count is fixed by RBT-91's σ = 4.0
    lineages and B0's biases. §10's figure for it is a **credence**, not a probability of an outcome. The no-peek is
    a pledge (§11, risk 7), so the readout computes P2 first, from the registered SHA, and prints that ordering.
- **P3's reset rate of 0.2.**
  - With reset probability ρ, the stationary bias variance is about 0.16/ρ. At 0.02 (the link reset rate) that gives
    sd ≈ 2.8, which is useless. At 0.2 it gives sd ≈ 0.9, keeping the median sech² above 0.4.
  - P3 resets Effector biases too, because b_E is the larger single factor. The host's throttle lives in b_E
    (`AUDIT.md:97-98`), so P3's costs (§8) are expected to be the largest.

### 2.2 Decided by bounds or ceilings: run as checks, outside the family

**The slope bound.** Take a lineage whose link weights and structure are its committed twin's. Then, among probes
without a `sign` flip:

`|a_links-alone| ≤ |product| × max f′`

The values of max f′ at the probe (SETTLE = 12 ticks, `structural_rate.py:58`) are:

| function | max f′ | why |
|---|---|---|
| tanh, sin, relu | 1 | |
| integrate | 1.436 | 2(1 − 0.9¹²), `brain.py:90-91` |
| **abs** | **1** | sech²(b_k) at b_k, `brain.py:85`; r1's 0 was wrong (M1) |
| differentiate | 0 | settled |
| sign | 0 | off its flip window; a flip is flagged and never counted (§3) |

Printed as `SLOPE BOUND` in `decompose_arrivals.py`. Control I3 checks every unflagged probe against it, and the
committed arrivals now give **0 violations** in all three conditions (`_baseline.txt:114`, `_1.6.txt:93`,
`_4.0.txt:96`).

**The four checks.**

| id | switch | bound or ceiling at a = 32 | source |
|---|---|---|---|
| **A0** | `global_bias_sigma = 0, effector_bias_sigma = 0`, links at default (existing switches) | **0** at every own-link rung. "Decouple the bias step / a bias reset" cannot move the primary at the default link step, whatever it does to the biases. | `_baseline.txt:113` |
| **P1** | `link_sigma = 1.6` (RBT-91's pre-registered widening, decoupled) | **≤ 2** | `_1.6.txt:92` |
| **P4** | `fan_rate = 0.2, fan_sigma = 0.75`: after all main-stream draws, each Neuron with probability 0.2 has all its in-links or all its out-links (a fair coin) multiplied by `exp(N(0, 0.75))` across every brain; all draws from `aux_rng` | expected k **≤ 2.96** even at unit downstream slope | ADVERSARY M3, `design-adversary/p4_ceiling.txt` |
| **P5** | `pair_event_rate = 0.005`: an event adds a global tanh neuron (bias N(0, 0.5)) with in-links from the left and right wheel food noses of opposite sign and out-links to both drive Effectors of the same sign, magnitudes \|N(0,1)\| × `link_scale`, signs from fair coins; all draws from `aux_rng` | expected k **≈ 0.01** | ADVERSARY M3, `design-adversary/p5_ceiling.txt` |

**RBT-134 C1 (coordinator, pre-data):** P4 fan runs after the weight draws, not after all main-stream draws; stream pairing unaffected.

**What else each check carries.**
- **P4 is not circuit-wise.** At fan_rate 0.2 on each of the 4–12 global neurons, every neuron-touching link gets a
  log-normal multiplier with sd 1.0–1.46. It is a whole-brain widening, and its background is reported as such.
- **P5's event respects `max_units_per_brain` (12, `genetics.py:103`)** (S9). It is refused when the global brain is
  full, and the refusal count is printed. Global brains hold 4–9 units (ADVERSARY S9).
- **P5's twin.** It is a twin of B0 only up to its first event. An added unit changes the range of later index draws.

**Bound violations VOID the instrument.**
- **Every check must hold its bound or ceiling.** A0 must read 0 and P1 ≤ 2. For P4 and P5, k ≥ 6 is a ceiling
  violation and is reported as a ceiling failure, a finding about the arithmetic. It is not a family rejection.
- The values of P4 and P5 are kept, not re-valued. Their role is now the both-ways statement (§10):
  - P5 prices "structure supply alone" (the event multiplies arrivals by about 200×);
  - P4 prices "a multiplicative circuit step at a modest size".
  - Re-valuing them into the family would have needed new values chosen to make them pass, which is the very thing
    a pre-registration should not do. ADVERSARY M3 accepted either route; the coordinator ruled this one.

### 2.3 Cut, kept, with reasons

- **Duplication of a sensor-bearing part (holistic): not cut. Measured by arm (b) of the H-predicate (§5.2).**
  - Through the **global brain**, a duplicated nose cannot difference. A global unit's link from a local unit is
    summed over every instance of the node (`rabbitstew/synthesis.py:323-332`), and mirroring flips no brain sign
    (`synthesis.py:113-121`; `_synthesize_brains` never reads `mirrored`).
  - **Through the instances' own local brains, it can (ADVERSARY M4).** Local links resolve per instance
    (`synthesis.py:302-321`). Each instance carries its own nose → Effector loop, so the body does the differencing,
    as in a Braitenberg vehicle.
  - The **existing** holistic operator already duplicates: `recursive_limit_rate` 0.05 and `add_connection_rate` 0.1
    (`genetics.py:90, 94, 236, 261`). So no new duplication switch is registered. Arm (b) counts what drift proposes
    by that route under B0 and every condition.
  - A dedicated duplication switch is a follow-up only if arm (b) arrivals exist and H2 finds them steering.
- **The holistic version of P5 (add two noses and a differencing unit): deferred.** Laterality on a holistic body is a
  phenotype property (`planters.py:220-237`). An operator that must read the phenotype to place sensors is an encoding
  change, and the Pioneer P5 is priced at ≈ 0.
- **`link_scale` (RBT-104) is not re-registered.** It is measured, and it is the calibration case of §6.4.
- **Restricting the vocabulary to odd-slope functions is not a candidate.** The function is an encoding choice
  (`genotype.py:596-598`). The function share is reported per condition as a covariate.
- **Mirror-sign synthesis** (mirrored instances entering global sums with opposite sign) is an encoding change. It is
  named as a possible follow-up only.

---

## 3. The assay, Pioneer (designed body)

**The protocol is RBT-91's, unchanged.**
- 19 `mutate_controller` mutations from committed parents.
- Two pools, `W4b-801-bests` and `P-801-final60`, at 100,000 lineages each: **200,000 per condition**.
- `add = 0.15`, `rem = 0.1`, `MASTER_SEED 20260912`.
- Lineage i's main generator is `SeedSequence([MASTER_SEED, crc32(label), 19, i])` (`structural_rate.py:199-203`;
  `runs/RBT-78/reconcile.py:45, 51-54`). Its auxiliary generator is §2's.
- Everything is **imported** from `runs/RBT-91/structural_rate.py`, as RBT-104's `drift_reach.py` does
  (`runs/RBT-104/drift_reach.py:1-12`). The one change is the condition's `MutationConfig` (`dataclasses.replace`) and
  the `aux_rng`.
- Every condition is **paired with B0, lineage by lineage**.

**The script.** `runs/RBT-134/assay.py`, written after the ruling. Per condition it prints:

1. **Structure.** The arrival count per pool and **per parent** (N4: W4b-801 has 7 parents, so lineages cluster). The
   predicate is unchanged (`structural_rate.py:76-100`).
2. **The primary.**
   - Every arrival's links-alone |a| against 6.2831, **12.5236 (primary)** and 24.7145, plus 6.8664 for continuity.
   - **Several predicate units (S8).** |a| is the **maximum over the lineage's predicate units**. `units[0]` is printed
     beside it for continuity with `structural_rate.py:210`.
   - The count k at a = 32, with Wilson intervals per 200,000 lineages and per arrival.
3. **The `sign` artefact (M2).**
   - Every links-alone probe is checked with `sign_flip` (`decompose_arrivals.py`): does any `sign` unit's settled
     output differ between the ±drive runs? Inside its flip window (|b_k| < the unit's net probe input, up to about
     0.075 at σ 4.0; `design-adversary/sign_probe.txt`) the probe reads about 1/drive (60–94) whatever the gain.
   - A flagged arrival is printed and **not counted** in k.
   - Flagged arrivals are excluded from I3's bound check and listed.
   - Verified on the adversary's three windows: the flag fires at b_k = 0, 0.001 and 0.016, and not at 0.08 or 0.5. The
     reading is 0 outside.
4. **The decomposition columns of §1 for every arrival, and the slope bound.**
5. **Background.**
   - The whole-brain |a| (`small_signal_a`, `:103-129`) of the **first 20,000 lineages per pool (40,000)**, split
     structureless/structured, at 6.8664 and 24.7145.
   - The whole-brain probe of each lineage is `sign`-flip-checked over **all** its `sign` units. The registered clause
     (§4) uses the **unflagged** structureless lineages. The all-lineage and flagged-included rates are printed beside
     it.
   - B0 must reproduce RBT-91's **26 of 9,996** (flags included) and **22 of 9,990 unflagged** (6 lineages flagged,
     4 of them hits; `design-adversary/fc_bg_flip.txt`, r3 FC-M1) on the first 5,000 per pool.
   - One task per 5,000 lineages, so it parallelises.
   - **Reading (N5).** The whole-brain probe is strongly drive-dependent on background hits (for example 8.56 at drive
     0.01 against 126.31 at 0.001). It is a registered rung reading, not a small-signal gain (cf. H36).
6. **Re-signing per robot at the reference probe.**
   - It covers arrivals with own-link |a| ≥ 6.2831, **capped at 400 per condition by lineage index** (S7).
   - The heading probe is RBT-91's reference probe, 16 seeds × 15 s, with an UNDETERMINED band of ±15°
     (`runs/RBT-91/resign_arrivals.py:86-114, 195-213`).
   - The sign is taken **on the motif's own links** (`ERRATA.md:141`).
   - Output: compass / anti / undetermined counts.
7. **The sham predicate.** The same predicate with the wheel `agent` sensors in place of `food` (both pools carry
   both, on the same parts). Instrument control I5.
8. **The transfer-function census of the predicate units**, a covariate.

---

## 4. Registered questions and decision rule, per candidate (P2, P3)

**Primary.**
- *Does the count k move off the default operator's 0?*
- k is the number of lineages, out of 200,000, that carry the structure, have no `sign`-flip flag, and whose own links
  read max |a| ≥ 12.5236.
- B0's count on the same seeds is 0: `RBT-91-alone-baseline.txt`, and `runs/RBT-104/drift-reach-k1.txt` at K = 1.
- **The test.** Under H0 the candidate's per-lineage rate equals B0's. Conditional on the k + 0 discordant pairs, the
  candidate's share is Binomial(k, ½), so the one-sided p is 0.5^k. This is McNemar, and every condition is paired.
- **Holm over m = 2:** k ≥ 6 for the first step, then k ≥ 5 (`power.txt`).
- **The count is unconditional**, per 200,000. A per-arrival fraction would reward reducing arrivals. It is printed
  beside the count and answers the ticket's "off 0 of 84" literally (P2 and P3 share the 66).

**Background clause, the same rule for every condition (S1).**
- *Does the structureless background stay where it is?*
- The measure is the rate of **unflagged** structureless lineages with whole-brain |a| ≥ 6.8664 among the 40,000.
- **HOLDS** iff the **one-sided 95% upper bound on the ratio candidate/B0 is ≤ 2**. The bound is the Katz log interval
  on the two counts. It ignores the pairing, which only widens it, and it is the same interval for every condition.
- Power (`power.txt`):
  - P(HOLDS) is 0.998 when unchanged, 0.95 at 1.25×, 0.67 at 1.5× and 0.05 at 2×;
  - RBT-91's 6.3× fails with certainty.
- The margin is the stated quantity, so it is not inert, and noisier conditions do not hold more easily.

**Verdict per candidate.**

| primary (Holm) | background | verdict | reading |
|---|---|---|---|
| rejects | HOLDS | **PASS** | the operator proposes circuits whose own gain pays, without pumping whole-brain gain |
| rejects | fails | **MOVES-WITH-BACKGROUND** | a gain pump, not a circuit proposer: RBT-91's reading of the widening, and RBT-104's of `link_scale` |
| does not reject | either | **NULL** (background reported) | k with its Wilson upper bound per 200,000 and per arrival |

**The compass count is reported, not tested.**
- A drift proposal's sign is a coin (decision `:103-112`). On own links the measured share is 30 of 58 = 51.7%
  (`ERRATA.md:141`), so the compass count is about Binomial(k, ½).
- Testing it would halve power without adding anything about the operator.
- The ticket's "re-signed per robot at the reference probe" is met as a registered secondary.

---

## 5. The assay, holistic fauna

### 5.1 Why not links alone, and why not `steer.py` on 200,000 lineages

- **There is no holistic links-alone rung.**
  - The probe needs a drive-Effector pair and a steering axis, and `drive_effector_units` is for "Pioneer-shaped bodies
    only" (`rabbitstew/fixed.py:218-235`).
  - The only holistic rung on record is G8(c)'s planted total gain, a = 6 split over its output links
    (`runs/RBT-116/planters.py:86-88`). That is a plant parameter, not a small-signal reading.
- **`steer.py` is the body-general functional instrument.**
  - It compares intact and decoy seasons with a trajectory veto (`runs/RBT-116/steer.py:631-702`).
  - A full call is up to 104 seasons, about 37 core-s. A stage-1 stop is about 3 core-s
    (`runs/RBT-116/PREREGISTRATION.md:956-970`).
  - On 200,000 lineages that would be 170 to 2,000 CPU-h per condition. So it runs on the **structural arrivals** and
    on a matched structureless sample: structure first, function on the carriers, as for the Pioneer.

### 5.2 Stage H1 (runnable after the ruling): the structural census, two arms

**Pools.**
- (a) `runs/RBT-19/P-801/holistic/final`, 60 parents. 2 of 60 synthesise a food sensor (measured).
  `mirror false` and `neighbour_links false` (`runs/RBT-19/P-801/config.json:153-154, 172-173`).
- (b) RBT-113's C-config holistic founders, seeds 1–4, from `initial_population`, as audit B draws them
  (`runs/RBT-121/ga/parity.py:26-31`). That is 160 founders, 37 with a food sensor. The config's vocabulary has
  `neighbour_links False` and `mirror_rate 0.0` (measured).
- 100,000 lineages per pool and 19 holistic `mutate` steps. The SeedSequence form is the same, keyed by pool label,
  with §2's `aux_rng`.

**H-predicate, arm G (the global differencing route).**
- A global non-sensor unit k whose summed in-links come from `food` sensors on **two distinct Nodes, each with exactly
  one instance** (`ph.node_instances`; the reason is §2.3), with opposite signs, and which has at least one out-link
  to an Effector.

**H-predicate, arm I (the local, body-differencing route; ADVERSARY M4, widened in r3 by FC-S1).**
- **≥ 2 parts**, each carrying a `food` sensor joined to an Effector **on the same part** by a local path. The parts
  may be **instances of one Node** (sub-count I-dup: the duplicated build) or **distinct Nodes** (sub-count I-dist).
  Both sub-counts are printed, along with their union (arm I).
- **The local path (FC-N3).** It is any directed path within that part's own local brain, from the `food` sensor to
  the Effector, through any number of the brain's local neurons. Every link on it has nonzero summed weight. The
  depth is not limited: a local brain holds at most `max_units_per_brain` = 12 units (`genetics.py:103`), so the search
  is finite.
- A duplicated Node's instances each carry their own nose → Effector loop (`synthesis.py:302-321`).
- With `neighbour_links` off in both pools, crossed (contralateral) local wiring cannot arise. Arm I counts the
  uncrossed vehicle and leaves its sign and laterality to H2.

**What both arms leave out, deliberately.**
- **Laterality** is checked by neither arm. It needs a season (`planters.py:220-237`), and the functional stage
  adjudicates it. Both arms over-count on purpose.

**Conditions.** B0, A0′, P1, P2, P3 and P4.
- `link_sigma`, `bias_reset_rate` and `fan_*` bind `mutate` because `mutate_weights` reads them from the config, as
  `effector_bias_sigma` does (`genetics.py:143-144`).
- `global_bias_sigma` does not bind the holistic fauna (`genetics.py:64-66`). Holistic P1/P2 need the new field, and
  holistic A0′ is `effector_bias_sigma = 0` alone.
- Holistic P5 is deferred (§2.3).

**Output.**
- Per arm and per condition: arrival counts with Wilson intervals.
- The share of children with any food sensor, with food sensors on two or more single-instance Nodes, and with a
  multi-instance food-bearing Node. Arm I's sub-counts I-dup and I-dist are printed separately.

**H1 rule (per arm).**
- If B0 and every condition have **0 arrivals in 200,000** on an arm, that arm's verdict is **STRUCTURE-BOUND**: "no
  operator in this set proposes the holistic <arm> structure at depth 19 from these pools".
- H2 is not run for that arm, and the reason is printed.
- The verdict names its arm, and no claim is made about a route neither arm covers.

### 5.3 Stage H2 (gated on H1 arrivals): the functional call

**Battery.**
- **Registered battery.** The registered W1 battery, built exactly as RBT-116's gate builds it:
  - G8(a)/G8(c) plants on RBT-113 O1 U-line finals (`planters.py:7, 86, 100-103`);
  - W1's 16 screen hosts (`steer.py:721`, `W1_SCREEN_KEY`);
  - `screen_draws` with W1's admissible rule (`steer.py:748-777`, `SCREEN_ANY`).
  - The coordinator released `ckpt/rbt-113-O1` read-only for this purpose. It will be fetched only by the H2 session,
    narrowly, with `git fetch -q origin +refs/heads/ckpt/rbt-113-O1:refs/remotes/origin/ckpt/rbt-113-O1`.
- **Registered fallback (S5).** It is used only if the registered battery cannot be built: missing hosts, a failed
  screen, or `ThetaRefused` on the pool.
  - W1 draws screened by the same `screen_draws` rule on **committed** hosts: RBT-19 P-801 holistic finals and
    RBT-113 C founders that carry a food sensor.
  - Labelled "not the registered battery; within-ticket comparison only, not comparable across tickets".
  - All conditions are read on the same draws, which is all a within-ticket comparison needs.
- **If the fallback screen also fails (FC-N2),** H2 is **unmeasured**. The report says so, names which screen failed
  and why, and gives the holistic answer as H1's structural census alone. No other battery is substituted after the
  ruling.

**Calls.**
- Call every H1 arrival with `steer.py` at W1, up to 400 per arm and condition, subsampled by lineage index if there are
  more.
- Call each STEERS arrival again with its circuit knocked out:
  - arm G: the predicate unit's out-links zeroed;
  - arm I: every qualifying food → Effector local path zeroed, in every carrying part's brain.
- **Circuit-owned STEERS** = STEERS intact and NONE knocked out. This is the holistic analogue of "links alone".

**Background.** A matched sample of 400 structureless lineages per condition is called, and their STEERS rate is the
holistic background.

**Rule.**
- An exact paired count test against B0's circuit-owned STEERS, per arm.
- The background clause as in §4: the ratio upper bound ≤ 2 by Katz, on the 400.
- A separate Holm family over the conditions and arms that reach H2.

**Detection floor.** About 1/133 per arrival at 400 calls (one-sided 95%, zero events). `steer.py`'s confirmed
sensitivity is below 1 (`runs/RBT-116/STEER_NOTES.md:44-58`), so an H2 NULL is an upper bound.

---

## 6. Multiplicity, and the calibration of the rule

### 6.1 The families

- **Pioneer primary:** P2 and P3, Holm at family-wise 0.05: thresholds 0.025 and 0.05, so k ≥ 6 and k ≥ 5
  (`power.txt`).
- **The background clause is the same for both and is not corrected.** It can only turn a rejection into
  MOVES-WITH-BACKGROUND, never into PASS, and an intersection–union conjunction needs no correction.
- **Holistic H2:** a separate Holm family, if run.
- **Not tested:** B0, A0, P1, P4, P5, C+ and the costs of §8. These are controls, checks with bounds, or descriptive.

### 6.2 Why m = 2

A0, P1, P4 and P5 are decided by bounds or priced ceilings from merged data and arithmetic. Spending a test on an
answered question only weakens the others (ADVERSARY M3, ruled).

### 6.3 What is fixed now

- The values in §2.
- The rung 12.5236 and the background rung 6.8664.
- The ×2 non-inferiority margin.
- The `sign`-flip rule.
- The n, and the streams.

**No condition is re-run at another value after seeing data.** A follow-up value is a new pre-registration.

### 6.4 Calibration: the rule can return each verdict, on merged measurements (S3: rung and n stated per row)

| case | k at a = 32 | background, at the rung and n it was measured | the rule says |
|---|---|---|---|
| default (RBT-91 / RBT-104 K = 1) | 0 | 0.26% at ≥ 6.8664, n 9,996 (decision `:30`); 22 of 9,990 = 0.22% unflagged (`fc_bg_flip.txt`) | NULL (the baseline) |
| RBT-91 coupled `weight_sigma 4.0` | 0 of 66 (`_4.0.txt:89`) | 1.64% at ≥ 6.8664, n 9,994 (decision `:32`); 151 of 9,967 unflagged (`design-adversary/fc_bg_flip.txt`) | **NULL** |
| RBT-104 `link_scale 8` | 8 (`drift-reach-k8.txt:107`) | 2.18% at ≥ 6.28 and 2.05% at ≥ 12.52, n 3,998 (`:113-114`); not measured at 6.8664; the ratio at either rung is ≈ 8× | **MOVES-WITH-BACKGROUND** at either rung |
| **C+** (pipeline positive control, run with B0) | must be ≥ 6 | must HOLD | **PASS** |

**C+.** It is P5 with its event's link magnitudes × 16 (the installed output w at the paying rung,
`probe_rung.txt:3`) and bias 0.
- It must PASS. If it does not, the instrument is VOID (I4).
- **What C+ does and does not show (N6).** It shows the pipeline can say PASS. It does **not** show that the background
  clause can be passed by a real operator, because C+'s structureless lineages are mostly event-free default lineages.

---

## 7. Power at the planned n (`power.py` → `power.txt`)

**Primary.**
- With N = 200,000 and a first Holm step at k ≥ 6, power is 80% at a per-lineage rate of 4.0 × 10⁻⁵ and 95% at
  5.3 × 10⁻⁵. Against an 84-arrival denominator that is 9.4% and 12.5%.
- RBT-104's `link_scale 8` reached 9.5% (8 of 84), where power is about 0.81.
- P2 and P3 are bounded at ≤ 29 (of 66 arrivals), so the family can clear the threshold. Whether it does is the bias
  question.
- A candidate delivering less than about 2 per 200,000 is undetectable at this n. Its Wilson upper bound is reported.

**Background.**
- At 40,000 per condition with B0's 22 of 9,990 (unflagged) rate, P(HOLDS) is:

| true ratio | P(HOLDS) |
|---|---|
| 1.0× | 0.998 |
| 1.25× | 0.95 |
| 1.5× | 0.67 |
| 2× | 0.05 |

- The same rule and interval apply for every condition.

---

## 8. What a change costs elsewhere

Each cost is measured for P2, P3, A0, P1, P4 and P5. None enters the primary verdict.

**E1. Structural erosion per child (RBT-121 audit B, `runs/RBT-121/ga/parity.py`).**
- **Default** (`parity.txt:1-2`):

| fauna | link survival per child | children losing any link | route loss among carriers |
|---|---|---|---|
| holistic | 0.9162 | 48.1% | 8.98% |
| designed | 0.9839 | 31.0% | 0.00% |

- **Wrapping.** It is wrapped with `replace(cfg.mutation, …)`, as `runs/RBT-124/bias_walk_s0.py` does. The wrapper is a
  new script under `runs/RBT-134/` that also passes `aux_rng`.
- **It is blind to weight operators by construction.** With separate streams it must equal the default **exactly**
  under P1, P2, P3 and P4: a stream-identity check (I2).
- P5 adds links and never removes them.
- The holistic `mutate` under the new fields must likewise reproduce the default exactly.

**E2. Functional erosion: RBT-112's erasure rate u(8).**
- **Measure.** On RBT-106's planted w = 32 founders: 10 seeds × 30 founders × 20 lineages, `u = 1 − f(8)^(1/8)` on
  pay32 (`runs/RBT-112/erasure.py:1-6`).
- **Default and Z.** u(8) = **0.282** at the default and **0.089** at `global_bias_sigma 0` (`runs/RBT-112/erasure.txt:25`).
- It is generalised from RBT-112's `baseline.py` (`:1-14`). The default must reproduce the committed table byte for
  byte, which it does for seed 801 (measured).
- **Reading.** u(8) above 0.5 is reported as "proposes but cannot keep". It is not a veto: the erasure is not what stops
  selection holding the compass (`ERRATA.md:125`, H65).
- The designed body only. E1's route loss is the holistic proxy (N8).

**E3. The RBT-113 selection response (S6: now defined).**
- **Which candidate is carried.** Each PASS. If there is no PASS, the **strongest MOVES-WITH-BACKGROUND**: the largest
  k, ties broken by the smaller background ratio. If both P2 and P3 are NULL, E3 is not run.
- **Faunas.** Every RBT-113 run carries both faunas in every arm (`runs/RBT-113/PREREGISTRATION.md:98-103, 122-135`). A
  switch that binds holistic `mutate` (P2 and P3 via `link_sigma` and `bias_reset_rate`) is therefore measured on both
  faunas in the same 4 arms.
  - Holistic salt 0 pairs seed for seed with O1–O4's holistic lines.
  - **No extra arms**, so the cost stays 12 CPU-h per candidate (`PREREGISTRATION.md:302-306`).
- **Measure.** `b_div` in σ0 units against the frozen reference: σ0 is 0.7545 for the designed body and 0.2212 for the
  holistic body (`runs/RBT-113/sigma0_reference.json:2-3`). Paired against O1–O4 over 12 seeds.
- **Verdicts per fauna:**

RBT-113's operator rule, verbatim in precedence (`runs/RBT-113/PREREGISTRATION.md:242-244`; r3, FC-N1). The
first matching row wins:

| verdict | condition on the 95% t CI of the mean paired difference |
|---|---|
| **RAISES** | CI excludes 0 above and the sign-flip p < 0.05 |
| **LOWERS** | CI excludes 0 below and the sign-flip p < 0.05 |
| **NO CHANGE** | CI inside ±0.05 σ0 (RBT-113's `EQUIV_OP`; `REPORT.md:51`) |
| **INCONCLUSIVE** | otherwise |

So a CI of [+0.01, +0.04] σ0 reads RAISES, as it would in RBT-113. The report prints whether a RAISES or LOWERS CI also
lies inside ±0.05 σ0. That flag is descriptive and does not change the verdict.

- **Power.** P(detect +0.2 h2) is 0.53 (`runs/RBT-113/power.txt:37`). This is stated, not fixed.
- **Gated** on RBT-129 releasing `rabbitstew/`. It needs:
  - `evolve` flags: `evolve` has `--global-bias-sigma` (`rabbitstew/cli.py:594`) but no `--link-sigma`;
  - a new operator case in `runs/RBT-113/world.py` and `run_arm.sh`;
  - a fresh `prelaunch.py` PASS;
  - readout prefix logic.
- **Reusing O1–O4.** They are reused if one O line reproduces byte for byte on the new tree. Otherwise O is re-run
  (another 12 CPU-h).

---

## 9. Matched nulls and instrument controls (any failure VOIDs the stage it guards)

| id | control | requirement |
|---|---|---|
| **B0** | the default operator, re-run by `assay.py` | arrival list identical to `RBT-91-alone-baseline.txt` line for line; background on the first 5,000 per pool reproduces **26 of 9,996** (all) and **22 of 9,990** (unflagged; `design-adversary/fc_bg_flip.txt`) |
| **I1** | pairing | every condition uses B0's main-stream seeds and §2's `aux_rng`; P2's links are RBT-91 σ = 4.0's and its biases B0's; P3's links are P2's |
| **I2** | stream identity | E1 identical to the default under P1–P4 (both faunas); P2's and P3's arrival sets equal `RBT-91-alone-4.0.txt`'s 66; P1's equals `-1.6.txt`'s 63; A0's equals B0's 84 |
| **I3** | bounds | no unflagged probe exceeds \|product\| × max f′ (§2.2 table, `abs` = 1); A0's k = 0 at every own-link rung; P1's k ≤ 2; P2's and P3's k ≤ 29 |
| **I4** | positive control C+ | PASS |
| **I5** | sham (`agent`) predicate | its arrival count lies within the 99% binomial range of the `food` predicate's, in every condition |
| **I6** | the `sign` artefact | no `sign`-flipped probe is counted in k or in the registered background; all are printed |
| **I7** | byte identity when off | each new field at its default (and `aux_rng=None`) is byte-identical to the current operator on a fixed 1,000-lineage stream; `link_sigma = S` equals §2.1's composition on the Pioneer; full `pytest` passes in a clean `.[dev]` venv without scipy |
| **I8** | holistic H2 | a no-food-sensor body reads NONE (`steer.py`'s I1, `runs/RBT-116/PREREGISTRATION.md:754-755`) |

**Matched nulls.**
- **P2's** matched null is RBT-91's coupled σ = 4.0 run (same links): 0 of 66, background 1.64%.
- **P3's** matched null is P2 (same links, same main stream). P3 against P2 isolates the reset.
- **Every condition's** matched null is B0.
- **The background is the matched null for "circuit, not whole brain".** The sham cannot be one, because the operator
  does not know which sensor is food.

---

## 10. Predictions, both ways (fixed now)

**What the numbers are.**
- P2 is a determinate computation from committed data (§2.1, S4). Its figure is my **credence** about a number that is
  already fixed.
- The other figures are credences about sampled outcomes.

| id | prediction | credence | if wrong, it means |
|---|---|---|---|
| A0 | k = 0 (bound) | 1.0 (proof) | the probe or the stream convention is not as documented: VOID |
| P1 | k ≤ 2 (bound); background above B0's, about RBT-91's coupled 1.41% or higher | 1.0 / 0.7 | — / that biases, not links, carried RBT-91's background |
| P4 | k ≤ 2 (ceiling 2.96); background up | 0.95 | the adversary's ceiling arithmetic is wrong |
| P5 | k ≤ 1 (ceiling 0.01) with arrivals up about 200× | 0.99 | structure supply binds at the tail, against decision `:66-69` |
| **P2** | **NULL**: k < 6, with background ≥ B0 × 2 | 0.55 | if it moves, default-size biases leave enough sub-saturating b_k for wide links to pay; the resting drive binds less than RBT-104 found |
| **P3** | **MOVES-WITH-BACKGROUND**: k ≥ 6, background fails | 0.45 | if PASS, resetting biases also tames recurrence, the first operator to buy circuit gain without whole-brain gain; if NULL, the reset's N(0, 0.5) leaves f(b_k) too large against v ≈ 4.5 |
| holistic H1 | arm G near 0; arm I non-zero under B0 (duplication is common: ≥ 2 food-sensor parts in about 14% of B0 children, pricing run) | 0.6 | — |
| **family** | **no PASS** | 0.65 | — |

**If neither P2 nor P3 PASSes** (scoped, M3), the result is:

> "At depth 19, on these pools, a link step decoupled from the bias step at 4.0 — with the default bias walk, or with
> biases reset to N(0, 0.5) at rate 0.2 — does not make drift propose routed motifs whose own links reach the a = 32
> rung without raising the structureless background above 2×."

- The report separates "all NULL" (the slopes bind even with wide links) from "moves only with background" (circuit
  gain comes only as whole-brain gain).
- It says which, and for these two switches at these values only.
- A0, P1, P4 and P5 add their bounded or priced statements beside it. Together they say that, at their values, bias
  treatments at the default step, a 1.6 widening, a fan step at sd 0.75 and the motif-shape event cannot move the count.
- **Nothing here is a claim about step distributions in general** (r1's "no step distribution separates the two" is
  withdrawn).

**If one PASSes,** the operator, not the encoding, was withholding circuit magnitude at this depth. The candidate goes
to E3 and then to an ecology design of its own, which this ticket does not schedule.

---

## 11. Risks

1. **The probe's operating point is conventional.** Links alone reads the Effector's slope at b_E with other inputs
   silenced. `assay.py` prints, descriptively, the circuit's response with the Effectors held at their whole-brain
   resting input. The registered rung uses the same convention (`probe_rung.txt:3`).
2. **One value per switch.** A NULL is worded "at this value".
3. **The rung comes from one parent.** It was read on one P-801 parent's b_E. W4b's own-link rung differs. The number is
   used as ruled (H41).
4. **Depth 19 is fixed by the mandate.**
5. **P5 makes many lineages structured,** so the structureless background is a selected subset (about 91%). The
   all-lineage rate is printed beside it.
6. **Lineages cluster by parent** (W4b has 7). Per-parent counts are printed (N4). Holm is valid under any dependence.
7. **No peeking at P1/P2.** P1 and P2 are computable today from RBT-91's committed lineages.
   - **That has not been done and must not be done before the ruling.** Only the bound (the link products) has been
     read, and the adversary verified it and did not compute P2 either.
   - The readout computes P2 first, from the registered SHA.
8. **The holistic stage may end at H1.** If an arm is STRUCTURE-BOUND, H2 is not run for it.
9. **CPU contention with RBT-129.** About 18 CPU-h of short jobs, run on a host without RBT-129 lanes, from a pinned
   branch SHA.
10. **`steer.py`'s confirmed sensitivity is below 1**, so an H2 NULL is an upper bound.
11. **The `sign` window is per unit and per probe.** It is detected by output flip, not by a threshold on b_k, so it is
    exact for the probe as run. A `sign` unit flipping in only one of the two whole-brain runs is still flagged.

---

## 12. Costs (CPU-h)

| item | basis | CPU-h |
|---|---|---|
| Pioneer assay, per condition | 200,000 × 11.2 ms + 40,000 background × 12 ms + probes (consistent with ADVERSARY N7) | about 0.8 |
| conditions B0, C+, A0, P1, P2, P3, P4, P5 (8) | ×1.5 margin | **about 10** |
| re-signing, capped at 400 per condition (S7) | 16 × 15 s × 0.35 s per robot (`runs/RBT-113/PREREGISTRATION.md:302`), at most 8 × 400 | at most about 5 |
| E1 (both faunas, 7 operators) | about 10 s each (`runs/RBT-121/ga/AUDIT.md:376-383`) | < 0.1 |
| E2 (u(8), 10 seeds, 6 operators plus the default check) | 65 CPU-s per seed (measured) | about 1.3 |
| holistic H1 (6 conditions × 200,000, both arms in one pass) | 12.5 ms per lineage (measured) | about 4.2 |
| **runnable after the ruling, in total** | | **about 15–21** |
| W1 battery build (H2, from O1 hosts) | planting + the draw screen (64–96 pool draws × 16 hosts, intact, about 0.35 s per season), a small part of RBT-116's whole gate line of about 12–14 (`runs/RBT-116/PREREGISTRATION.md:973`); no W1 battery has yet been built (`:230`) | at most about 2 |
| holistic H2 (gated on H1 arrivals) | at most (400 arrivals × 2 calls × 37 s + 400 structureless × up to 37 s) per arm and condition | at most about 62 per arm |
| E3 (gated, per carried candidate, both faunas) | 4 arms × 3.0 | 12 (24 if O must be re-run) |

---

## 13. Order of work

1. **Ruling on r2.** The adversary fix-checks, then the coordinator and owner rule. No assay runs before the ruling.
2. **Code, on this branch only, not merged.**
   - `rabbitstew/genetics.py` gains the fields `link_sigma`, `bias_reset_rate`, `fan_rate`/`fan_sigma` and
     `pair_event_rate`, plus an optional `aux_rng`. All are default-off.
   - Tests for I7.
   - `runs/RBT-134/assay.py`, the E1 and E2 wrappers and the H1 census.
   - The full `pytest` in a clean `.[dev]` venv without scipy.
   - Runs execute from the pinned branch SHA. Nothing touches `scripts/` or `runs/RBT-129/`.
3. **Controls:** B0, C+ and A0, then P1, P4 and P5 as checks. I1–I7 must pass.
4. **The family.** P2 first, as a determinate computation (S4), then P3. Then the readout and verdicts (§4).
5. **Costs and census:** E1, E2 and holistic H1.
6. **H2,** if H1 has arrivals. Fetch `ckpt/rbt-113-O1` narrowly, read-only, build the W1 battery, or fall back (§5.3),
   then call.
7. **E3** for the carried candidate, after RBT-129 releases `rabbitstew/`.

---

## 14. What the fix-check should attack first

1. `sign_flip` as the M2 rule: does it catch every artefact in both the links-alone and the whole-brain probes?
2. The `aux_rng` stream design (S2): is P3 really P2's twin in links?
3. The non-inferiority background rule (S1) and its power.
4. Arm I of the H-predicate (M4): is "a local path within the Node's brain" the right structural net?
5. The scoped both-ways statement (§10).

---

## R. Revision log, r1 → r2 (against ADVERSARY.md and the coordinator's rulings)

**MUSTs.**

| item | r2 change |
|---|---|
| **M1** | max f′(`abs`) = 1 (sech²(b_k) at the bias) in `decompose_arrivals.py`; outputs regenerated. 0 violations of the corrected bound in all three conditions (`_*.txt`, "bound violations"). P2's bound is ≤ 29 (was 25). A0's 0 and P1's ≤ 2 unchanged. "25 deaf" restated in §1.3. |
| **M2** | The `sign` artefact is defined by mechanism: `sign_flip` flags a `sign` unit whose settled output differs between ±drive. It applies in the primary (not counted), in the background (registered on unflagged lineages) and in I3. It replaces "\|b_k\| < 1e-9". Verified on the adversary's three windows (§3.3). B0 reproduces 20 of 9,996 unflagged (wrong target, corrected in r3 to 22 of 9,990: FC-M1). |
| **M3** | P4 and P5 moved to checks with their ceilings (2.96, 0.01). Family is P2 and P3, Holm m = 2 (k ≥ 6, 5). §10 is scoped to the two switches at their values. "All NULL" is separated from "moves only with background". "No step distribution separates the two" is withdrawn. |
| **M4** | H-predicate arm I (per-instance Braitenberg route) added. The duplication cut is withdrawn: the existing operator duplicates and arm I measures it. STRUCTURE-BOUND is per arm and names it. |

**SHOULDs.**

| item | r2 change |
|---|---|
| **S1** | Non-inferiority: HOLDS iff the one-sided 95% Katz upper bound on candidate/B0 is ≤ 2. Same test and n for all. Power in `power.txt`. |
| **S2** | `aux_rng` for every extra draw. Main stream draw for draw B0's. McNemar throughout. P3 = P2's links + resets. E1 is an identity check for P1–P4. |
| **S3** | Calibration rows state their rung and n. |
| **S4** | P2 recorded as a determinate computation. Its figure is a credence. The readout computes P2 first. |
| **S5** | H2 uses the registered W1 battery from the released O1 hosts, with a registered fallback on committed hosts. |
| **S6** | E3: carried candidate defined; verdict set RAISES / LOWERS / NO CHANGE / INCONCLUSIVE; both faunas in the same arms at no extra cost. |
| **S7** | Re-signing capped at 400 per condition. Cost re-priced. |
| **S8** | max \|a\| over predicate units, with units[0] printed. |
| **S9** | P5's event respects `max_units_per_brain`. Refusals counted. |

**r2 → r3 (fix-check of r2, `ADVERSARY.md` "## Fix-check (r2 678681a)"; nothing else changed).**

| item | r3 change |
|---|---|
| **FC-M1** | B0's targets are **26 of 9,996** (all) and **22 of 9,990** (unflagged, under r2's own `sign_flip` rule). The σ 4.0 calibration row is **151 of 9,967**. `power.py`'s `P0_BG` = 22/9,990, `power.txt` is regenerated, and §4 and §7 power figures are updated. The citation is now `design-adversary/fc_bg_flip.txt`. |
| **FC-S1** | Arm I widened to ≥ 2 parts (instances of one Node or distinct Nodes), with sub-counts I-dup and I-dist printed. |
| **FC-N1** | E3's verdicts follow RBT-113's precedence verbatim (PREREG:242-244). A within-margin flag is printed, descriptive only. |
| **FC-N2** | If the fallback screen also fails, H2 is unmeasured and reported as such. |
| **FC-N3** | Arm I's local path is any directed local path, with no depth limit (finite: at most 12 units). |

**NOTEs (r1 → r2).**

| item | r2 change |
|---|---|
| **N1** | Adopted. |
| **N2** | "Bias walk takes it back" changed to "link magnitude × bias offset (resting drive)". |
| **N3** | Adopted. |
| **N4** | Per-parent counts added. |
| **N5** | The background is read as a rung reading. |
| **N6** | C+'s scope stated. |
| **N7** | Adopted. |
| **N8** | Holistic E2 gap stated. |
