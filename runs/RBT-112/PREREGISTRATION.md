# RBT-112 pre-registration: is the operator the stall? Freeze the global biases and ask whether selection then holds a paying compass

*Designer's pre-registration, 2026-09-27. **No arm has been launched.** The only ecology runs made for it
are short throwaway runs (at most 61 seasons, outside the checkout) and byte-identity runs (§8).
**Gating (the ticket):**
- The arm runs only if RBT-106's option H reads that the compass is not held (§7.1).
- It also waits for a fresh adversary on this design and the coordinator's ruling.
- No output of a running RBT-106 or RBT-107 arm was read. The paired control's arms (RBT-106's HU) are
  read only at launch (`certify.sh`) and at readout, once H has read.

Every number below is read from a committed file beside this one, named at the number.*

**The question** (ticket RBT-112, from RBT-104's readout adversary §5.1(i)):
- RBT-106's option H plants a compass that already pays (w = 32, a = 64) in a default host.
- The mutation operator alone erases that paying class at **u ≈ 0.29 per generation**.
- RBT-104 §1.4 and RBT-106 §5.1 blame most of this on the bias walk: the bias step uses `weight_sigma`
  whatever the link scale, and at v = 32 a resting drive v·tanh(b) above ~1 saturates the Effector.
- **If the global biases are frozen, does the erasure fall to the structure's own decay, and does selection
  then hold the paying compass that it loses under the default operator?**

**The design in one paragraph.**
- **One flag, `--global-bias-sigma 0`.** It is tested, byte-identical when unset, keeps the random stream
  and freezes only the global biases (§1–§2).
- **The decisive pre-arm step** (§4, fixed in `DECISION.md` before it ran): the operator-alone baseline at
  S = 0 gives **u = 0.089 against 0.282 by default**. That is ≤ 0.12, so **the arm is worth running**.
- **The arm is HZ = RBT-106's HU + `--global-bias-sigma 0`**, on HU's ten seeds with HU's founders. HU is
  the paired control (§3).
- **HELD** is RBT-106's call. HZ is read against **its own operator's** no-selection table, and each HU
  arm against the default table (§5).
- **The matched null with crossover** is measured, not modelled: 1.5% at S = 0, 1.0% by default (§5.2).
- **Power is re-derived** in four layers (§6.3). It is far below the adversary's rough ≥ 0.95, and depends
  on whether selection keeps planted-rooted lineages alive.
- **The RBT-104 lesson** is made mechanical (§6.6). The per-arm install control, analyse.py's control, the
  frozen-bias F12 print and HELD's reachability were run on the arm's own S = 0 hosts before any arm, and
  `run_arm.sh` refuses to launch without them.

---

## 1. The flag (ticket step 1)

**`--global-bias-sigma S`**, stored as `MutationConfig.global_bias_sigma` (default `None`, meaning `weight_sigma`).
- **Where it acts.** In `genetics.mutate_weights`, a unit of the global brain (owner `None`) takes its bias step
  as `N(0, 1) × S`. Every other unit keeps `N(0, weight_sigma)`.
  - `N(0, 1)` consumes exactly the one standard normal that `N(0, weight_sigma)` consumes, so the random stream
    is unchanged at any S.
  - numpy's `normal(0, σ)` is `0 + σ·z`, so S = `weight_sigma` is bit-identical to the default (tested).
  - At S = 0 the draw is made and multiplied by 0, so only the global biases freeze.
- **What passes it.** Only the designed body's callers: `mutate_controller`, and the ecology's `mutate_weights`
  call without `--conventional-topology`. The holistic operator (`mutate`) ignores it, as it ignores
  `link_scale` (tested).
- **In the config.** `EvolutionConfig.to_dict` writes it only when set, so a default run writes the
  config.json it wrote before, byte for byte. It is wired to the `ecology` CLI.
- **`crossover_rate`** is already exposed on the ecology CLI as `--crossover` (default 0.3). No change was
  made. It applies to both faunas, and 0 skips a random draw, so "crossover 0" is not stream-preserving. No
  arm here uses it.
- **What freezing implies**, all of it the flag's and none of it a side channel:
  - The planted unit's bias is 0 at founding and never steps.
  - `crossover_controller` moves whole global brains, and those are frozen too.
  - A unit the operator adds is born with its drawn bias, and keeps it.
  - **The host's own global units freeze as well.** Host gait cannot use global biases, which is a side
    effect, pre-registered in §6.4 (SE-Z).

## 2. Tests and byte identity (ticket step 2)

**`tests/test_global_bias_sigma.py`** (7 tests):
- The default and S = `weight_sigma` reproduce a verbatim copy of c872e80's `mutate_weights`, draw for draw,
  with the generator state equal afterwards, at K = 1 and 8, on 8 grown genomes.
- **S = 0, over 30-generation `mutate_controller` lineages at K = 1 and 8:**
  - the same topology;
  - every link weight and every segment bias equal to the default lineage's, draw for draw;
  - the stream in the same place;
  - no global bias moved by the weight step.
- S scales the global step exactly.
- `mutate` ignores the flag.
- The config writes it only when set; the CLI parses it; `--crossover` is present.
- The ecology's founders and streams are untouched.

**`byte_identity.py` → `byte_identity.txt`: PASS.** Throwaway runs from `byte_identity.sh`, x86_64, MuJoCo 3.14.0:

| check | runs | result |
|---|---|---|
| 1. The default against the committed part 2 (RBT-104's `byte_identity.default`, imported) | 10 seasons, seeds 801 and 4 | seasons.txt **BYTE-IDENTICAL** to `runs/RBT-90/forage-SEED`; config equal outside seasons/workers, flag not written |
| 2. The default, seeded, against a committed seeded run | 20 seasons, RBT-104's w = 1 founders, 801 | seasons.txt **BYTE-IDENTICAL** to `runs/RBT-106/side/S1U-801` |
| 3. The default against **c872e80's code** (a worktree), HU's founders and command | 20 seasons, 801 | seasons.txt, lineage.jsonl, config, **93 holistic + 177 designed genomes: all byte-identical. SAME RUN** |
| 4. S = 0 against the default, HU's command | 20 seasons, 801 | config differs in **exactly** `mutation.global_bias_sigma`; founders of both faunas and the holistic rows byte-identical; designed births with a global bias neither parent carried: **0 of 89** (default: 60 of 117) |

Check 3 is the one the pair rests on. It shows that the code with the flag unset is the code RBT-106's HU arms
ran, genome for genome. At launch, `certify.sh` repeats this against the HU arms themselves (§7.2).

## 3. The arm (ticket step 4)

| arm | founders | command | role | n |
|---|---|---|---|---|
| **HZ** | RBT-106's w = 32 founders (`founders-w32-SEED`, digests committed) | RBT-106's HU command (its `command.py`, imported) **+ `--global-bias-sigma 0`** | the arm | 10 |
| HU | the same | RBT-106's, unchanged | the paired control: RBT-106's arms, launched at c872e80's code | (10, RBT-106's) |

- **Seeds** are RBT-106's ten: 801, 804, 805, 806, 807, 1, 2, 3, 4 and 7. Depth is 600 seasons.
- **One flag.** `tests/test_rbt112.py` pins HZ's command to HU's token for token, plus the flag.
- **What HZ does at t = 0.** The planted founders are the same as HU's, and the flag acts only at birth. So
  HZ at t = 0 is HU at t = 0 (RBT-106 §3.3: the compass-signed founders earn +1.0 items per bout uniform).
- **The world is uniform**, as HU's is. HZ answers the ticket's question without the prize changing. HP
  (patchy) has no S = 0 twin here: that would be a factorial, and the ticket asks for HU + S = 0.

## 4. The pre-arm operator baseline (ticket step 3): **u = 0.089 at S = 0, against 0.282. WORTH RUNNING**

**The rule was fixed before the run** (`DECISION.md`, committed at `daca7fd` before `baseline.sh` ran):
- **u = 1 − f(8)^(1/8)**, where f(d) is the pooled pay32 fraction at depth d over ten seeds × 600 lineages.
- **u ≤ 0.12:** the arm is worth running.
- **u ≥ 0.20:** stop and report.
- **Between the two:** grey, and the coordinator decides.

**What ran.**
- **Scripts:** `baseline.py` (RBT-106's `baseline.py` with the operator's MutationConfig given
  `global_bias_sigma`) and `baseline.sh`, over ten seeds × 30 planted founders × 20 lineages.
- **Operator:** no selection and no crossover. Each S = 0 lineage is its default twin, draw for draw.
- **Fidelity:** the default run reproduces RBT-106's committed `baseline-w32-SEED.txt` on all ten seeds,
  identical below the header, and byte for byte for 801 and 4.

**Results** (`erasure.py` → `erasure.txt`):

| depth | 0 | 1 | 2 | 4 | 8 | 12 | 16 | 25 | 40 |
|---|---|---|---|---|---|---|---|---|---|
| pay32 persistence, default | 0.997 | 0.708 | 0.492 | 0.250 | 0.071 | 0.023 | 0.013 | 0.005 | 0.002 |
| **pay32 persistence, S = 0** | 0.997 | **0.917** | **0.830** | **0.696** | **0.474** | **0.332** | **0.245** | **0.127** | **0.058** |
| structure with sign, default | 1.000 | 0.917 | 0.826 | 0.671 | 0.442 | 0.283 | 0.191 | 0.104 | 0.042 |
| structure with sign, S = 0 | 1.000 | 0.935 | 0.868 | 0.762 | 0.573 | 0.424 | 0.325 | 0.186 | 0.094 |
| own-links median, default / S = 0 | 26.6 / 26.6 | 22.7 / 25.3 | 10.2 / 23.8 | 0 / 20.6 | 0 / 10.8 | 0 / 0 | … | | |

- **u(d) at depths 1, 2, 4, 8 and 16:**
  - default 0.292, 0.298, 0.293, **0.282**, 0.239;
  - **S = 0: 0.083, 0.089, 0.087, 0.089, 0.084.**
- **Per seed**, u(8) at S = 0 runs from 0.083 to 0.096. The t(9) interval is +0.089 [+0.086, +0.092]. Paired
  against the default it is −0.193 [−0.201, −0.185].
- **All three u(1), u(4) and u(8) fall in the same band.**
- **The structure's own decay** (with sign) at S = 0 is 0.067 per generation, against 0.097 by default.
- **So the bias walk is about two thirds of the erasure: 0.282 → 0.089.**
  - The rest, 0.089, is close to the structure's own decay (0.067 at S = 0; the ticket's "0.07–0.08").
  - It comes from the links: removal, resets and the walk of the own-link gain below the rung. At S = 0
    the own-link median falls from 26.6 to 10.8 by depth 8, and to 0 by depth 12.
- **Decision (DECISION.md): u ≤ 0.12. The arm is worth running**, subject to the gating in §7.1.

Two readings that the decision does not rest on:
- The w = 32 structure decays faster by default (0.097) than the ticket's w = 1 figure (0.07–0.08). The
  bias walk also takes the structure's sign or predicate with it.
- f(0) = 0.9967, not 1: a few founder lineages read just under the pay32 rung at founding (RBT-106
  §5.2). It is the same in both arms.

## 5. The null for "held" (the matched null, including crossover)

### 5.1 The call, and each arm against its own operator

**HELD** is RBT-106's amended call (§10.2), unchanged: **k_planted > B** at both 300 and 599.
- B is the 95th percentile of Binomial(n, μ), where μ is the mean of the operator-alone table at each
  planted-rooted genome's own depth.
- **The table is the arm's own operator's.** `held.py` here is RBT-106's `held.py`, imported. For an arm
  whose config records `global_bias_sigma = 0`, it reads `baseline/baseline-w32-S0-SEED.txt`; every HU arm is
  read by RBT-106's files against the default table. Any other S is refused.
- **Why its own table.** "Held" means *selection keeps more than the operator alone leaves*. Freezing the
  biases raises what the operator alone leaves, from 0.013 to 0.245 at depth 16. So a larger raw carrier
  share in HZ than in HU is expected with no selection at all.
  - The raw share is printed (`readout.py`) and is not the test.
  - The HZ bar is higher in carriage: B at depth 16 with n = 40 needs k_planted ≥ 15, against 3 for HU.

### 5.2 How often HELD fires with nothing selecting the compass: measured

`null_xover_s0.py` runs the RBT-106 adversary's `null_xover.py`, imported:
- part 2's ten real 600-season genealogies (restored from `ckpt/rbt-90-SEED`);
- the w = 32 founders planted at part 2's founders;
- the ecology's own designed-body operator, **`crossover_controller` at the recorded mates, then
  `mutate_controller`**;
- 20 replicates per seed;
- HELD scored as amended.

At S = 0 the operator gets `global_bias_sigma = 0`, and μ comes from the S = 0 table. The default run
reproduces the adversary's committed `xnull-w32-SEED.txt` on all ten seeds, identical below the header.

| operator | HELD at 150 | at 300 | at 599 | **at 300 and 599 (the arm-level call)** | bare-rooted share of k |
|---|---|---|---|---|---|
| default, crossover (RBT-106's H null) | 17/200 | 10/200 | 7/200 | **2/200 = 1.0%** | 336/1066 |
| **S = 0, crossover (HZ's null)** | 10/200 | 15/200 | 13/200 | **3/200 = 1.5%** | 2003/5481 |
| default, mutation only | 31/200 | 18/200 | 8/200 | 2/200 | 0 |
| S = 0, mutation only | 50/200 | 46/200 | 48/200 | **26/200 = 13%** | 0 |

**What this says:**
- **HZ's false-positive rate is 1.5% per seed** under its own operator.
  - P(#HELD(HZ) ≥ 5 of 10 | no selection) = 1.8 × 10⁻⁷.
  - P(#HELD(HZ) ≤ 1 | no selection) = 0.991.
- **Crossover carries the S = 0 null.** Without it the rate is 13%, because frozen compasses persist in
  whole clades, and clades overdisperse k against a table built from independent lineages. With it, a
  bare mate's global brain replaces the planted one in about 15% of births, and 37% of k is bare-rooted
  (not scored).
  - The arm runs at crossover 0.3, the ecology's default. So 1.5% is the matched rate.
  - **A reader of HZ must know it is the crossover-inclusive null that makes the call clean.** The
    mutation-only null would call 13% of unselected seeds HELD.
- **No futility gate** (§7.1). At 150 the S = 0 null reads HELD in 5.0% per seed.

## 6. Readouts, verdicts, power and predictions (ticket step 4)

### 6.1 The readouts, per arm, as RBT-106 reads HU

`postrun.sh HZ SEED` produces the following, using RBT-106's instruments unchanged:
- `seasons.txt`;
- `rbt102.txt` (RBT-102's `analyse.py` and its 40-of-40 positive control);
- `held-300.txt` and `held-599.txt` (§5.1);
- `function-uniform.txt` (RBT-104's `function.py`) and `function-patchy.txt` (RBT-106's `cross_world.py`);
- `function-pc.txt` (the install control, `--install 32`, at the hosts' own scale);
- **`resting.txt` (F12).**

**F12's resting-drive print** (`resting.py`; coordinator 01:52 on RBT-106). For each champion (the bests at
300, 350, …, 590), beside its install-control F, it prints:
- whether the champion carries the routed structure;
- the predicate unit's own-link |a| and whether it pays (≥ 12.52);
- its bias b and transfer function;
- its output weights v_L and v_R onto the drive Effectors;
- the resting drive max|v|·|f(b)|, and the nominal |32·tanh(b)|.

Run with `--frozen` on HZ, it also flags any paying carrier whose planted-unit bias is not 0 as a
**FAULT**. By construction there can be none, and an HZ arm with a fault is unusable, because the flag
did not do what it says. `postrun.sh HU SEED` makes the same print for RBT-106's HU arms (restored
outside the checkout), without `--frozen`.

**So F12's masking route is closed in HZ by construction**, since the planted unit's b stays 0. In HU it is
open, and the readout names it: an arm whose install control fails while its champions carry a planted unit
with resting drive > 1 is printed as "F12's route", not as "the host masks a compass".
- In the 20-season HU-801 and HZ-801 byte-identity runs, both champions at gens 0 and 10 carry the planted
  unit at b = 0.0000, resting drive 0.
- In HZ this is so by construction. In HU, selection had not yet let a drifted carrier become best.

### 6.2 The verdict (`readout.py`; thresholds in code, printed beside the verdict)

**Usable** means:
- viable (no extinction; reached season 599; ≥ 30 alive on average in the window);
- on x86_64;
- both positive controls passing (analyse.py's, and the install control reading FOOD-DEPENDENT);
- the code certified: HU's tree is c872e80's; HZ's launch commit names a `cross-ticket-<commit>.txt` reading
  SAME RUN on HU-801 and HU-4;
- for HZ, no frozen-bias fault.

A pair is usable if both arms are. **VOID** if fewer than 7 paired seeds are usable.

**Pair Z: HU (the default operator) against HZ (S = 0).** Each HELD is against its own operator's table.
- **SUPPORTED:** #HELD(HZ) ≥ 5 **and** #HELD(HZ) − #HELD(HU) ≥ 3. *The operator was the stall: with the global
  biases frozen, selection held the paying compass that the default operator's arm lost.*
- **FALSIFIED:** #HELD(HZ) ≤ 1. *Freezing the global biases cut the erasure to near the structure's own
  (0.282 → 0.089), and selection still did not hold the compass.* In plain terms, the operator is not the
  stall, or not the whole of it. The worded limit is §6.5's: this also reads "selection's advantage on the
  compass is below ~0.1 per generation".
- **NOT DECIDED** otherwise.

**Reported beside the verdict, not in it:**
- the paired log-excess log((k + 1)/(nμ + 1)) at 599, HZ − HU;
- the paired raw carrier share k_planted/n at 599, which the operator alone raises;
- k_bare;
- the side effects (window income and alive, HZ − HU);
- F12's print per arm.

**Function** (reported, RBT-106 §10.4's COMPASS count, patchy-scored; uniform beside it):
- **FUNCTION FOLLOWS:** HZ COMPASS lines ≥ 3 **and** the paired F(HZ) − F(HU) t(n − 1) interval above 0.
- **DOES NOT FOLLOW:** ≤ 1 and that interval not above 0.
- **UNDECIDED** otherwise.
- The primary-only ("food-dependent", any smell use) count and the compass-lesion gain are printed.

**Why ≥ 5 and a gap of 3, and not RBT-106's log-excess condition.**
- The arm runs only if HU is not held, so #HELD(HU) is known to be small at launch (§7.1). Then ≥ 5 is
  what binds, and its null rate is 1.8 × 10⁻⁷ (§5.2).
- The log-excess compares each arm's excess over a *different* table: over the S = 0 table, HZ's excess is
  harder to earn. As a condition it would cost power and add nothing to a null this clean.
- `tests/test_rbt112.py` pins the rules.

### 6.3 Power, re-derived (`power.py` → `power.txt`)

The adversary's rough figures were **≥ 0.95** for ≥ 5 of 10 primary FD "if H holds under S = 0", and 0.6–0.8
on ATTRIBUTION. Both assume that **every** seed holds the compass at balance 1 − u/s ≈ 0.84. Re-derived
here from committed numbers only, in four layers:
- **Layer 0** is the measured null (§5.2).
- **Layer 1: P(HELD on a seed | s).**
  - The mutation–selection recursion x' = x(1 + s)(1 − u)/(1 + sx), with u from §4.
  - The planted-rooted n and depth at 300 and 599 from part 2's real genealogies (`genealogy.txt`).
  - k ~ BetaBinomial(n, x, ρ), with ρ = 0.10 fitted to layer 0's S = 0 rate. The default rate cannot be
    fitted at any ρ: the real null's excess comes from clades the model does not have.
  - B from the operator's own table.
- **Layer 2** is the verdict over ten seeds (Poisson-binomial).
- **Layer 3** is function per line: seven bodies, each carrying with probability p. A carrier's (gain,
  decoy) comes from the committed a = 64 install rows; the zero veto uses the committed zero fractions.

**The genealogy decides much of the power.** In part 2's genealogy no planted-rooted genome is alive at 599 on
seeds 807, 2 and 3 (807 from season 300), and n is 6–11 on 7, 801 and 805. Under that genealogy those seeds
cannot read HELD. Selection on a paying compass should keep planted roots alive (H0's gate, in the patchy world, saw n = 41 and 48 at
season 150 on seeds 4 and 801, against the uniform genealogy's 40 and 25), so the scenario "n = 40 on every seed" is printed beside it. The
truth lies between the two.

| s (per generation) | q_U (HU) genealogy / n = 40 | **q_Z (HZ)** genealogy / n = 40 | P(#HELD(HU) ≤ 1) genealogy / n = 40 | **P(SUPPORTED \| #HELD(HU) ≤ 2)** genealogy / n = 40 | P(FALSIFIED) genealogy / n = 40 |
|---|---|---|---|---|---|
| 0 | 0.001 / 0.002 | 0.016 / 0.033 | 1.00 / 1.00 | 0.000 / 0.000 | 0.99 / 0.96 |
| 0.089 | 0.004 / 0.011 | 0.114 / 0.215 | 1.00 / 1.00 | 0.001 / 0.042 | 0.68 / 0.33 |
| 0.15 | 0.013 / 0.032 | 0.216 / 0.406 | 0.99 / 0.96 | 0.017 / 0.380 | 0.28 / 0.04 |
| **0.20** | 0.030 / 0.069 | **0.288 / 0.540** | 0.97 / 0.85 | **0.071 / 0.719** | 0.11 / 0.005 |
| **0.25** | 0.063 / 0.134 | **0.344 / 0.641** | 0.88 / 0.61 | **0.167 / 0.898** | 0.04 / 0.001 |
| **0.30** | 0.115 / 0.233 | **0.387 / 0.715** | 0.68 / 0.29 | **0.284 / 0.965** | 0.015 / 0.000 |
| 0.50 | 0.386 / 0.718 | 0.483 / 0.862 | 0.02 / 0.00 | 0.663 / 0.999 | 0.001 / 0.000 |

(ρ = 0.10; ρ = 0 and 0.6 are in `power.txt`. At n = 7 usable, SUPPORTED's power roughly halves.)

**What the arm can and cannot say:**
- **The informative window is s ≈ 0.15–0.3.** There, the gating premise (HU not held) is likely, and freezing
  the biases moves q from ≈ 0.01–0.2 to ≈ 0.2–0.7.
  - Below it (s ≲ 0.1), neither operator lets selection hold, and **FALSIFIED fires with probability
    0.3–0.7** even though the bias walk *is* two thirds of the erasure. FALSIFIED therefore means "not the
    operator alone: selection's advantage is below ~0.1 per generation, or planted roots die out". It does
    not mean "the bias walk is harmless" (§6.5).
  - Above it (s ≳ 0.4), HU would already be held and the arm would not run.
- **SUPPORTED's power inside the window: 0.07–0.28 on the genealogy's n, 0.72–0.97 at n = 40.** It is
  honestly moderate, and it depends on whether selection keeps planted roots alive. The adversary's ≥ 0.95
  held only with every seed holding.
- **Function** (layer 3, patchy-scored):
  - Per line, P(primary FD) is 0.97 and P(COMPASS) 0.90 at p = 6/7. Both fall steeply below p = 4/7 (0.57
    and 0.38).
  - **Uniform-scored, P(COMPASS) saturates at 0.55–0.62**, because the installed compass's decoy retains
    24.1% there, against the 25% cutoff (`runs/RBT-104/function-controls-801.txt`). This is the adversary's
    "0.6–0.8 on ATTRIBUTION". It is why the COMPASS count is patchy-scored, as RBT-106 §10.4 counts it.
  - Over ten seeds at s = 0.2–0.3, **P(≥ 3 COMPASS lines)** is 0.04–0.28 (genealogy, champions carrying
    at the window share x) to 0.94–0.995 (n = 40, champions enriched to 6/7).
  - **P(≥ 5 primary FD)**, the adversary's figure, is 0.003–0.28 to 0.70–0.95.
  - **At the adversary's own premise** (every seed holds, p = 6/7) it is 1.000, confirmed.

### 6.4 Predictions and confidences (fixed before any arm; conditional on the arm running, i.e. on HU not held)

| # | prediction | confidence |
|---|---|---|
| **Z-0** | Verdict: SUPPORTED 0.25, FALSIFIED 0.35, NOT DECIDED 0.33, VOID 0.07 | — |
| Z-1 | #HELD(HZ) ≥ #HELD(HU) + 1 (any lift at all) | 0.70 |
| Z-2 | Function: FUNCTION FOLLOWS | 0.20 |
| Z-3 | Every HZ champion that carries a paying planted unit reads b = 0 and resting drive 0 (F12's route closed; no FAULT) | 0.99 |
| Z-4 | HZ's paired raw carrier share at 599 exceeds HU's, t interval above 0 (expected even without selection) | 0.80 |
| **SE-Z** | Side effect: window income HZ − HU, t interval includes 0 (freezing the host's global biases costs no measurable gait) | 0.65 |
| SE-Z2 | No HZ arm goes extinct; 10 of 10 viable | 0.90 |

**Where Z-0 comes from.**
- The arm runs only if HU fails, which by the model puts s ≲ 0.3.
- Over that range, the genealogy's n makes SUPPORTED unlikely and FALSIFIED likely at small s. n = 40
  makes SUPPORTED likely at s ≥ 0.2.
- I put about equal weight on "selection keeps planted roots alive" and "it does not", and on s below
  and inside the window.
- VOID is 0.07, above RBT-106's 0.05. The install control passed on the arm's own hosts (§6.6), but an
  unusable seed now also includes a frozen-bias fault.

### 6.5 The falsifiers, in plain words

*SUPPORTED.* We planted a compass that already pays in ten populations, twice: once under the ordinary
mutation operator (RBT-106's HU), and once with one change, the global units' biases never mutating (HZ).
- Under the ordinary operator the compass was lost. It was not held above what mutation alone leaves.
- If, with the biases frozen, it is held above what *that* operator alone leaves in at least five of ten
  populations, and in at least three more than under the ordinary operator, then **the operator's bias walk
  was what stopped selection holding a paying trait**.

*FALSIFIED.* If, with the biases frozen, it is held in at most one population, then **the bias walk was not
what stopped it**, although it is two thirds of the erasure. With the walk gone, selection still did not keep
the compass above the operator's own residual erasure (0.089 per generation, near the structure's own decay).
- Either selection's advantage for this compass in a real population is below about 0.1 per generation, or
  the planted lineages die out for reasons that have nothing to do with the compass (in part 2's own
  genealogy, 3 of 10 seeds lose every planted root by season 599).
- The report must say which of the two the data show: `held.py` prints n and the number of distinct
  planted roots at each reading.

*Scope.* One uniform world (RBT-90 part 2's), planted w = 32 founders, the default link reach, 600 seasons, and
the ecology's crossover at 0.3. Freezing the global biases also freezes the host's global biases (SE-Z).

### 6.6 The RBT-104 lesson: every per-arm control run on the arm's own hosts before any arm

**Programme rule** (RBT-104 ruling, 01:52): run the per-arm install control and the gate on the arm's own
founders before launch, and report the pass rate. A control that cannot pass by construction is fixed before
any arm.

**Here** (`prelaunch.sh` → `controls/`). HZ smoke runs of 61 seasons on seeds 801 and 4 are the arm's own
S = 0 hosts, and they are not arms. The readout's own instruments run on the bests at 0, 10, …, 60: seven
bodies, the readout's n and t(6).

| control, as the readout runs it | seed 801 | seed 4 | pass rate |
|---|---|---|---|
| (a) analyse.py's positive control (window 30–59) | PASSED, 40/40 | PASSED, 40/40 | 2/2 |
| **(b) the install control**, `function.py --install 32` (the usability control), the line | **FOOD-DEPENDENT**, F +1.766 [+1.210, +2.321]; attribution FOOD-DEPENDENT (decoy retains 10.2%) | **FOOD-DEPENDENT**, F +1.471 [+1.038, +1.904]; attribution UNRESOLVED (decoy retains 30.7%) | **lines 2/2; bodies 14/14 with F > 0** (+0.92 to +2.45) |
| (c) F12, `resting.py --frozen` | 7 of 7 champions carry the paying planted unit at b = 0, resting drive 0; faults 0 | 5 of 7 carry it at b = 0, resting drive 0 (2 bests at 20 and 30 carry no structure); faults 0 | 0 faults |
| (d) HELD reachable (k_planted = n > B) at n = 20, depths 2–40 | all ten seeds' S = 0 tables | | YES |

**PRELAUNCH: PASS** (`controls/prelaunch.txt`, on `rabbitstew/` tree `81e9f0a`).

What (b) says for the readout:
- **The control passes on the arm's own hosts.** Unlike RBT-104's S8, it does not fail by construction. Its
  per-body transmission is healthy: F from +0.92 to +2.45, above RBT-104's S1 installs (+0.39 to +1.13).
- **Seed 4's attribution reads UNRESOLVED in the uniform world, with the decoy retaining 30.7%.** This is the
  uniform-world attribution weakness that §6.3 predicts (P(COMPASS) saturates at 0.55–0.62 uniform-scored).
  - It does not affect usability. Usability needs the control's *primary* call, as RBT-106 has it.
  - It is why the COMPASS count is patchy-scored. The patchy install control on part 2's 801 retains
    2.1% (RBT-106 §6.1).
- The HZ smoke champions carry the planted unit at the paying rung in 12 of 14 bests through season 60.
  This is not a result: it is 61 seasons on two seeds, not an arm, and nothing is read from it.

The refusal paths of `run_arm.sh` were exercised (`controls/launcher-refusals.txt`): unknown arm → 2; no
certification → 6; a stand-in certification with no pre-launch record → 7; an uncommitted edit in
`rabbitstew/` → 5. Nothing was launched.

**By construction:**
- **The install control** installs the a = 64 motif at the hosts' own scale (K = 1), which is the S1 case:
  9 of 10 pass in RBT-104. The HZ host's planted unit rests at b = 0, so the route F12 found cannot mask it.
  The adversary's b = 0 probe gave +1.77 and +1.05, above the bare hosts' +0.67 and +0.83.
- **HELD** can fire at every depth ≥ 2 with 20 planted-rooted genomes, on every seed (table (d) in
  `controls/prelaunch.txt`). It cannot fire at depths 0–1, where the operator alone keeps ≥ 92% of lineages
  paying. No reading is taken there: the window's depth is 8–22 in the genealogy.
- **`run_arm.sh` refuses to launch** unless `controls/prelaunch.txt` reads `PRELAUNCH: PASS` (exit 7), and
  unless the launch commit is certified against HU (exit 6).

## 7. Gating, waves, cost

### 7.1 Gating, and why there is no futility gate

- **The arm launches only if RBT-106's option H reads the compass not held:** FALSIFIED-b, or NOT DECIDED with
  #HELD(HU) ≤ 2.
  - At #HELD(HU) ≥ 3, SUPPORTED would need #HELD(HZ) ≥ 6, and the uniform prize is not failing. The
    coordinator decides.
  - If H reads HELD or FALSIFIED-a, the ticket closes as not needed.
- **It also waits for the fresh adversary on this design and the coordinator's ruling.**
- **No season-150 futility gate.**
  - At S = 0 the null CONTINUEs 5.0% per seed at 150.
  - The arm is one wave of 5 sessions, so a gate would save at most 4 sessions.
  - Under the hypothesis the arm tests, the paying class decays slowly (0.089), so an early reading
    carries little information.

### 7.2 Launch procedure, waves and cost (`waves.txt`)

1. **`certify.sh`** at the launch commit re-runs RBT-106's HU command for 20 seasons with the flag unset, for
   HU-801 and HU-4. It compares each run with RBT-106's arm, restored from `ckpt/rbt-106-HU-SEED`, using
   the RBT-106 adversary's `cross_ticket.py`, and writes `cross-ticket-<commit12>.txt`. It must read SAME
   RUN on both (`run_arm.sh` exit 6).
2. **`controls/prelaunch.txt`** must read PASS (exit 7). Re-run `prelaunch.sh` if `rabbitstew/` has changed
   since this design.
3. **One wave, 5 sessions:** (801, 4), (804, 805), (806, 807), (1, 2) and (3, 7).
   - Two arms per session at WORKERS=2, each with its own `durable.sh every 20` loop.
   - `postrun.sh HZ SEED` runs after season 599, then the final save (README rules 1, 3 and 6).
   - Checkpoint labels are `rbt-112-HZ-SEED`, named on the ticket at launch.
4. **F12 on the control:** `postrun.sh HU SEED` for the ten seeds (restore and print, no ecology).
5. **Readout:** `readout.py > readout.txt` once all ten HZ PRs are merged.

**Cost.**
- Per session: about 51 min of ecology (5.1 s per arm-season, two side by side) plus about 40–80 min of
  post-run (function.py in two worlds, the install control, held.py twice, and resting.py). **About
  1.5–2.2 h per session, so 7.5–11 session-hours** for the wave.
- Certification is two 20-season runs, about 10 min. The ten HU F12 prints take about 1 min each.

## 8. What was run for this design (all x86_64, MuJoCo 3.14.0, numpy 2.4.6)

1. **The flag and its tests**: `tests/test_global_bias_sigma.py`, 7 tests.
2. **Byte identity** (`byte_identity.sh`, `byte_identity.py`, `byte_identity.txt`): 10-season part-2 runs on
   801 and 4, and 20-season runs on 801 (S1U, HU at this code, HU at c872e80's code, and HU at S = 0). **PASS.**
3. **The baseline** (`DECISION.md` first; then `baseline.py`, `baseline.sh`, `baseline/`, `erasure.py`,
   `erasure.txt`): ten seeds × 600 lineages × depths 0–40, default and S = 0.
4. **The matched null** (`null_xover_s0.py`, `null.sh`, `null/`): ten real genealogies × 20 replicates, default
   and S = 0, with and without crossover.
5. **Genealogy** (`genealogy.py`, `genealogy.txt`) and **power** (`power.py`, `power.txt`).
6. **Pre-launch controls** (`prelaunch.sh`, `prelaunch.py`, `controls/`): two 61-season HZ smoke runs.
7. **Tests** (`tests/test_rbt112.py`, 9). The launcher's refusals are in `controls/launcher-refusals.txt`. The full suite, in a clean `pip install -e '.[dev]'` venv with no
   scipy: **358 passed**.

## 9. Files

| file | role |
|---|---|
| `PREREGISTRATION.md`, `DECISION.md` | this; step 3's rule, committed before the baseline ran |
| `baseline.py`, `baseline.sh`, `baseline/`, `erasure.py`, `erasure.txt` | §4 |
| `byte_identity.sh`, `byte_identity.py`, `byte_identity.txt` | §2 |
| `null_xover_s0.py`, `null.sh`, `null/` | §5.2 |
| `held.py` | §5.1: RBT-106's held.py against the arm's own operator's table |
| `resting.py` | §6.1: F12's resting-drive print |
| `genealogy.py`, `genealogy.txt`, `power.py`, `power.txt` | §6.3 |
| `prelaunch.sh`, `prelaunch.py`, `controls/` | §6.6 |
| `command.py`, `run_arm.sh`, `certify.sh`, `postrun.sh`, `waves.txt` | §7 |
| `readout.py` | §6.2 |
| `rabbitstew/genetics.py`, `evolution.py`, `ecology.py`, `cli.py` | §1: the flag |
| `tests/test_global_bias_sigma.py`, `tests/test_rbt112.py` | §2 and the scripts |
