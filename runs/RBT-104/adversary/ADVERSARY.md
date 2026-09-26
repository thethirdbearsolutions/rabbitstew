# RBT-104 design adversary: report on PR #177

*Design adversary for RBT-104, 2026-09-26. It attacks the pre-registration and the flag at PR #177's head,
`ae50050` (`results/RBT-104-design`). It measures and does not tune, and it edits no file of the
designer's. Every probe is under `runs/RBT-104/adversary/` and its readout is committed beside it.
No arm was launched, and every run was a short throwaway: at most 10 seasons and scratch directories only.*

**Platform, for every number below:** `platform.machine()` = `x86_64`, MuJoCo 3.14.0, numpy 2.4.6,
on a four-core cloud container.

## Verdict in one paragraph

The flag is clean. It touches what it claims, K = 1 is byte-identical to RBT-90 part 2 on two seeds,
a K = 8 run resumes byte for byte, and the suite passes on the head and on both trial merges. **The
design is not ready to launch, and all four MUST-FIXes are in the pre-registration's text and
reasoning, not in the code.**
- **F7:** the pre-registration omits two of the coordinator's conditions, matched-null power and
  the t = 0 income cost.
- **F5:** the falsifier's plain words over-claim twice. They say the planted wiring "pays from the
  first season", which the design's own measurements contradict, and they omit the uniform-world
  limit.
- **F6:** a no-selection probe shows that S8's paying magnitude is lost under mutation alone in
  about two generations. So FALSIFIED (F-b) is close to the operator's default outcome, and the
  design must state that before any arm, not discover it after 20 arms.

A redesign is not required. Every MUST-FIX can be fixed in the pre-registration without changing
an arm.

---

## Findings

| # | severity | item | one line |
|---|---|---|---|
| F1 | NONE | 1 flag | Scope as claimed; K = 1 byte-identical to part 2; a K = 8 run resumes byte for byte; suite 295 passed |
| F2 | **MUST-FIX** | 1 merges | #146 merges cleanly and passes, but after it `seed_founders.py` refuses to build S1/S8 founders |
| F3 | NONE | 3 seed | The seed is the same files in S1 and S8; digests reproduce (801, 4); S1/S8 are stream-paired |
| F4 | CAVEAT | 3 seed | t = 0: the seed costs no detectable income in either arm, and **the planted compass is not food-dependent in either arm** |
| F5 | **MUST-FIX** | 2 falsifier | The plain-words falsifier and the F-a label over-claim; it answers "link reach", not "magnitude", and omits the uniform world |
| F6 | **MUST-FIX** | 3, 4 purge | Under the operator alone, S8's paying magnitude is gone in ~2 generations and at window depth 2–3% remain; F-b is the operator's default outcome |
| F7 | **MUST-FIX** | 4, 7 conditions | Coordinator conditions 1 (matched-null power), 2 (t = 0 income) and 3 (platform record) are not in the pre-registration |
| F8 | CAVEAT | 5 controls | Readout (b)'s K = 8 control ran on K = 1 hosts; the one K = 8-host reading we have (t = 0) fails; VOID risk is unmeasured |
| F9 | CAVEAT | 6 cost | U8 carries no verdict; with house packing, the primaries cost ~20 session-hours, not 40–63 |

---

### F1 — The flag. NONE

**Scope, read from the diff:**
- A step's N(0, 0.4) and a reset's N(0, 1) (`mutate_weights`, with `link_scale` passed only from
  `mutate_controller` and from `_breed`) are scaled.
- A new link's N(0, 1) in `mutate_controller` is scaled.
- The designed founders' links are multiplied by K in `Ecology.__init__`, whether drawn or loaded.
- Untouched: unit biases (step N(0, 0.4)), a new neuron's bias (`random_neuron`, N(0, 0.5)), the
  holistic `mutate` (its `mutate_weights` call keeps the default 1.0), and every stream. No draw is
  added.

One nit. `_breed`'s fixed-topology branch (`else:`, designed bodies without
`--conventional-topology`) also passes `link_scale`, which is broader than the pre-registration's
"mutate_controller only". These arms run with `conventional_topology: true` (part 2's
config.json), so it does not reach them. The CLI help should say it.

**Re-run by this adversary** (`short_run.sh`, `byte_identity.py`, unchanged):

| check | result |
|---|---|
| K = 1, seed 801, 10 seasons, against committed `forage-801/seasons.txt` | **BYTE-IDENTICAL**, 20 rows; config equal outside the volatile fields (and RBT-105's null `breed_stream`) |
| K = 1, seed 4, 10 seasons | **BYTE-IDENTICAL**, 20 rows; config equal |
| K = 1, the other eight seeds (804, 805, 806, 807, 1, 2, 3, 7), 2 seasons each | **BYTE-IDENTICAL** on all eight; config equal |
| K = 8, seed 801, 8 seasons: holistic rows against the K = 1 run | **identical**, 8 of 8 |
| K = 8 founders | 60 of 60 are the K = 1 founder, links ×8, units unchanged |
| **K = 8, killed at season 4 and resumed with `--resume` to 8**, against uninterrupted K = 8 | **`seasons.txt` identical**, and `link_scale: 8.0` is restored from config.json. Resume builds a fresh Ecology with `out_dir=None` and then replaces the fauna from `state.json`, so founders are not scaled twice. This matters because every arm runs under `durable.sh`, and the designer did not check it. |
| full suite, PR head | **295 passed** (the pre-registration says 290; integration added tests since) |

Integration (`claude/new-session-4cao7d`, 47210f1, carrying RBT-105's `--breed-stream`) is already
an ancestor of the PR head, so the trial merge is a no-op.

Tooling nit: `byte_identity.py raised` compares holistic rows without truncating to the shorter
run. On runs of unequal length it prints DIFFERENT when the common seasons are identical (it did so
here on 8 against 10 seasons).

### F2 — Trial merge with PR #146 (RBT-96, `--holistic-stream-salt`). MUST-FIX (small)

**The text merges cleanly.** `rabbitstew/{cli,ecology,evolution}.py` merge without a conflict, and the
suite on the merge gives **297 passed** (with `PYTHONPATH` set to the merge worktree; the editable
install otherwise imports the main checkout). Seasons stay byte-identical at K = 1 (seed 801,
3 seasons).

**The semantic conflict.** #146 adds `holistic_stream_salt` to `EvolutionConfig`, and `asdict`
writes it **as 0 in every config.json**.
- `seed_founders.py` and `byte_identity.py` tolerate only fields added *at null*
  (`_extra_nulls`).
- On the merge, `seed_founders.py 801` raises `AssertionError: the founders would not be RBT-90
  part 2's`. `run_arm.sh` therefore cannot build S1/S8 founders: it fails closed, which is good.
- `byte_identity.py default` reads `config.json … NO`.

If #146 merges before wave 1, no primary arm launches. **Fix, either way:**
- have the comparison tolerate an added field at its dataclass default (0, None or False), and name it; or
- make #146 write the salt only when set, as `link_scale` does.

### F3 — The seed is identical across S1 and S8. NONE

- `seed_founders.py` reproduces the committed `SHA256SUMS` digests for **801 and 4**.
- S1 and S8 load the same files. The flag multiplies the loaded links at founding (the `scale_links`
  call is after `load_population`).
- Loading draws no founder or age from the conventional stream in either arm, so **S1 and S8 are
  stream-paired from season 0**.
- (S1 is *not* stream-paired to part 2: part 2 drew its founders and ages. The pre-registration
  does not claim that it is.)
- Which founders (even i), which unit (a new global `tanh`, bias 0), magnitudes (|w| = 1 at K = 1,
  8 at K = 8) and the sign split (i % 4) are pre-registered exactly, and I confirmed them in the code.

### F4 — t = 0: cost and function of the seed (`founders_t0.py`, `founders-t0-801.txt`). CAVEAT

Each of seed 801's 30 planted founders was paired with its own bare twin, at K = 1 and at K = 8.
The scoring is RBT-103's `income_bout` unchanged, in part 2's world, on 16 paired seeds, with real
smell and the rotated decoy. The t is over the 30 founders.

| items per bout | K = 1 (S1) | K = 8 (S8) |
|---|---|---|
| bare founder income | +0.440 [+0.296, +0.583] | +0.621 [+0.452, +0.789] |
| **cost, seeded − bare** | **+0.033 [−0.033, +0.100]** | **−0.090 [−0.263, +0.084]** |
| **the planted compass's food dependence, F(seeded) − F(bare)** | −0.027 [−0.097, +0.043] | **−0.081 [−0.273, +0.111]** |

- **No income cost is detectable in either arm.** Its upper bound in S8 (a 0.26-item loss) is
  about 40% of a bare founder's income, so the S8 seed is not shown to be free.
- **The planted compass does not steer at t = 0 in S8.** Its upper bound, +0.11, is an eighth of
  the uniform-world prize (+0.84). This is the behavioural confirmation of the pre-registration's
  §2 small-signal reading (whole brain 0.0025): the K = 8 host masks it.
- The flag alone moves a bare founder's income by +0.181 [−0.019, +0.381] (U8 − U1). That is not
  significant, but it is the side effect's sign at t = 0.

One seed, 16 bouts per body. It answers the coordinator's condition 2 for 801 only. The designer
should run it on all ten seeds (≈ 5 min each on four cores) and cite it.

### F5 — Does K = 8 test "magnitude"? The falsifier over-claims. MUST-FIX (wording)

**The judgement.** The flag scales link weights only.
- The design's own §1.4 shows that the reachable gain is gated by the interneuron's bias through
  Effector saturation (|v·f(b)| < ~1). No single scale of links or biases removes that gate.
- Scaling biases saturates f(b). A larger K raises the resting drive in proportion.
- So a bias-scale arm or a different K would not rescue the test, and **no extra arm is
  warranted.**

But the conclusion has to narrow to what was manipulated: *uniform link-weight reach at K = 8,
biases unscaled, planted structure, RBT-90's uniform world.* Specifically:

1. The plain words say *"so that the planted wiring is strong enough to pay from the first
   season."* That is **false by the design's own measurement**: whole-brain 0.0025, 2 of 30 over
   the rung (§2). It is also false by F4, where the compass does not steer at t = 0. Replace it
   with what is true: *strong enough on its own links; masked by its host at founding.*
2. *"Missing magnitude is not what stood between…"* must read *"missing **link-weight reach** is
   not…"*. A null cannot speak to magnitude reached by any other route, such as a bias held near
   zero or a desaturated host.
3. **The uniform-world clause the coordinator asked for (17:46) is absent.** The pre-registration
   never says that a null here does not speak to patchy worlds (P-801's +2.27 against +0.84), and
   it never uses +0.84 in its power reasoning (F7).
4. **F-a over-claims.** It fires on **≥ 1** own-link paying carrier on ≥ 1 usable seed.
   - Own-link magnitude is not in-host function: §2 and F4 show a host masking an own-link-paying
     compass completely. So "the compass was present at magnitude and not used" does not follow.
   - One genome among thousands is not "present".
   - F-a should require an in-host reading (the carrier's whole-brain response, or a behavioural
     F on carriers) and a carriage threshold, fixed now.
   - `readout.py`'s FALSIFIED string, "the magnitude was supplied", needs the same narrowing.

### F6 — Can the seed be purged before selection acts? Yes, and at K = 8 the operator does it in two generations (`persistence.py`, `persistence-{801,4}.txt`). MUST-FIX

The probe uses the operator alone, with no selection and no crossover. It runs part 2's own
MutationConfig on each seed's 30 planted founders, 20 lineages each (600 per K), and reads each
lineage with RBT-91's instruments unchanged. Seed 801, with seed 4 in brackets:

| depth (generations) | 0 | 1 | 2 | 4 | 8 | 16 (window) |
|---|---|---|---|---|---|---|
| structure, K = 1 | 100% | 94% (93) | 88% (88) | 78% (78) | 58% (55) | 31% (29) |
| structure, K = 8 | 100% | 94% (94) | 89% (88) | 76% (74) | 55% (58) | 29% (33) |
| **paying (same sign, own links ≥ 24.71), K = 8** | **100%** | **74% (75)** | **54% (56)** | **31% (30)** | **13% (11)** | **2% (3)** |
| own-link median, K = 8 | 46.0 (50.0) | 40.0 (44.4) | 29.1 (31.8) | 2.7 (2.6) | 0 | 0 |
| whole-brain median, K = 8 | 0.0025 (0.0000) | ~0 | ~0 | 0 | 0 | 0 |

**What this means:**
- **The structure's half-life is ~8–10 generations at both K.** So by the window (depth
  14.0–17.5), mutation alone leaves ~30% of planted lineages carrying it, identically in S1 and S8.
- **S8's paying magnitude has a half-life of about two generations**, a loss of u ≈ 0.25 per
  generation. This is consistent with §1.4's gate acting on the planted unit: its bias starts at 0 and
  walks, and at v ≈ 8 one bias step of N(0, 0.4) takes the resting drive past 1. The probe does not
  decompose the loss by cause.
- **Selection has nothing to hold it with at the start.** F4 shows the compass gives no detectable
  benefit at t = 0 in S8. For H to be tested, selection must supply s > u ≈ 0.25 per generation
  *from within the first ~2–4 generations*, on a compass its host is masking.
- Otherwise the S8 window reads ~2–3% paying, and the verdict machine reads **FALSIFIED (F-b)**.
  That outcome is the operator's arithmetic, known before any arm, not a result about selection.

**Required before launch:**
- (a) State this operator-only baseline in the pre-registration.
- (b) Define F-b *relative to it*. "Magnitude could not be held" is informative only if S8's
  window paying fraction is compared with the no-selection 2–3%, and the pre-registration must say
  what excess counts.
- (c) Raise P-2's F-b share, or say why selection is expected to act by generation ~2.
- (d) Say what 20 arms add beyond this table, if the expected answer is F-b.

A cheap option for the coordinator to rule on (judged, not designed): **one or two S8 pilot seeds
to ~150 seasons (~4 generations)**. They would show whether selection holds any paying carriers
past the operator's curve before 20 arms are committed. At the house rate that is about 13 minutes
of arm time each.

### F7 — The coordinator's conditions, as the pre-registration stands. MUST-FIX

**(a) Condition 1: matched-null power** (`power.py`, `power.txt`). The pre-registration gives outcome
confidences (P-1…P-4) but **no P(null outcome | H)** for any verdict. It also uses +0.84 only in
"why P-1 is not higher", never in a power statement. The pieces, from committed per-body values
(`function-controls-801.txt`):

- **Readout (b), per line:**
  - false-positive rate on bare champions: **0.05–0.10** (centred, uncentred);
  - power against the fraction p of the seven window champions carrying a working a = 64 compass:
    p = 0.29 → 0.23, 0.43 → 0.41, 0.57 → 0.62, 0.71 → 0.82, 0.86 → 0.96.
- **The verdict:** with q = P(an S8 line reads food-dependent | H), the FALSIFIED count (≤ 1)
  fires with **P ≥ 0.25 whenever q ≤ ~0.25 at n = 10, or q ≤ ~0.35 at n = 7**.
- **SUPPORTED is capped** before its paired-F condition by S1's false positives:
  P(S1 ≤ 1 of 10) = **0.74–0.92**.
- **The designer must state q under H, and hence P(FALSIFIED | H) and P(SUPPORTED | H).** Given F6,
  q under H depends on selection acting by generation ~2, so P(FALSIFIED | H) is not small unless
  the design argues otherwise.

**(b) Condition 2: the t = 0 income of the seeded founders against the unseeded** is not in the
pre-registration. F4 supplies seed 801. The designer should run and cite all ten.

**(c) Condition 3: the platform** is not recorded anywhere.
- It is missing from the pre-registration, `byte_identity.txt`, `run_arm.sh` and `readout.py`.
- The byte-identity check was on x86 (this container matches), but nothing in the files says so.
- RBT-90 part 2 records no platform either. Byte identity to its seasons on this x86_64 /
  MuJoCo 3.14.0 container (F1: all ten seeds, `platform.txt`) is the evidence that part 2 ran on the
  same class of machine.
- **Required:** each arm writes `platform.machine()` and `mujoco.__version__` beside its config.
  `readout.py` refuses an arm that is not x86_64 / 3.14.0, or at least prints a warning.

### F8 — Positive controls under K = 8. CAVEAT

**Readout (a):**
- The predicate is sign-based, so it passes at any K by construction (40/40).
- The paying-carrier count was exercised on a 6-season S8 run (19 of 51, §7 check 4).
- That is adequate.

**Readout (b):** its K = 8 control ("a = 128 geometry, F +1.379") was run on **part 2's K = 1
hosts**, gens 0–590. It shows the geometry pays in a K = 1 host, not that a K = 8 host can express
it.
- The only K = 8-host behavioural reading so far is F4 at t = 0, and **it fails** (−0.081).
- The per-arm install control at readout is the right guard. But P-4 (VOID) = 0.15 is set without
  any measurement of whether evolved K = 8 hosts desaturate. A 6-season S8 run's bests would give
  a first reading cheaply.

Two smaller points:
- The controls used gens 0–590, while the verdict rule reads 300–590.
- The negative control's zero count is **213/448 = 47.5%**, just under the 50% veto. Bare lines
  will often be *vetoed* rather than read "not food-dependent". Either outcome counts as not
  food-dependent, so it does not change the counts, but the readout should say so.

### F9 — Cost: is every arm needed? CAVEAT

**U8 carries no verdict** (§3.1). It is the literal arm and the side-effect arm.
- The primary verdict does not use it, and S8 − S1 already measures the reach's side effect with
  the seed present.
- **Dropping U8 loses no power that the verdict uses.** Its S-2…S-4 side-effect predictions would
  go too.
- Reasonable options: U8 on 5 seeds, or U8 as a conditional wave run only if the primaries are
  SUPPORTED or VOID.

**All ten seeds are needed for S1 and S8.** The count rules already sit at the edge at n = 7–10 (F7).

**Session-hours.** The pre-registration's 40–63 assumes one arm per session at 6–10.5 s/season,
and `run_arm.sh` defaults to `WORKERS=1` while its comment says 4. At the house packing (two arms
per session at WORKERS=2, ~5.1 s per arm-season):
- one 600-season arm takes ≈ 51 min;
- **20 primary arms take 10 sessions ≈ 15–20 session-hours in one wave**;
- all 30 take ≈ 25–30 session-hours.

The pre-registration should adopt the packing and fix `run_arm.sh`'s default and comment to match.

---

## What would clear the design

1. **F2:** make the config comparison tolerate an added field at its default, or sequence #146 after launch.
2. **F5:** reword the falsifier and F-a:
   - "link-weight reach", not "magnitude";
   - "masked by its host at founding";
   - the uniform-world clause;
   - F-a with an in-host reading and a carriage threshold.
3. **F6:** put the operator-only persistence baseline in the pre-registration, define F-b against
   it, and revise P-2. The coordinator may also rule on an S8 pilot.
4. **F7:** add:
   - P(FALSIFIED | H) and P(SUPPORTED | H) with a stated q;
   - the t = 0 income on all ten seeds;
   - the platform record in each arm and in the readout.

The CAVEATs (F4, F8, F9) need a sentence each, and the coordinator's ruling on U8.

## Files (all under `runs/RBT-104/adversary/`)

| file | what |
|---|---|
| `ADVERSARY.md` | this report |
| `persistence.py`, `persistence-801.txt`, `persistence-4.txt` | F6 |
| `founders_t0.py`, `founders-t0-801.txt` | F4 |
| `power.py`, `power.txt` | F7(a) |
| `platform.txt` | F1 and F7(c): the byte-identity re-runs, the resume check and the #146 merge, with the machine |
