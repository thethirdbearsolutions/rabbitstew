# RBT-104 readout adversary: PR #256 (`results/RBT-104-readout`, head `0634a84`)

*Fresh session, dispatched by the coordinator on 2026-09-27. I did not design or run RBT-104. I read the
ticket (all rulings; 23:05, 23:15, 00:00, 00:25), `PREREGISTRATION.md` (§1.4, §2, §4.2, §5, §6.1, §6.5 and
Amendments 1–3), the design adversary's reports under `adversary/`, `runs/README.md`, and PR #256.
**Every number I computed that the registration did not name is POST HOC**, labelled so at each place. No
registered rule is changed, and no arm is added. Every probe runs `runs/RBT-104/function.py` or `peek.py`
unchanged, on checkpoints restored with `scripts/durable.sh restore` into scratch, or on synthetic hosts
written to scratch. Nothing was written into an arm directory.*

## Verdict on the readout

**The scored verdict, VOID, is read correctly from the registered rules, and the fidelity chain is clean.**
But **the VOID is a design artefact of the install control's scale, not a finding about S8 hosts.**
- The registered control installs the a = 64 motif at the **default** reach (input ±1, output 32). The
  host's ×8 does not apply to it.
- In a ×8 host the drive Effectors sit at |x| ≈ 14–27 and are saturated on 91–96% of ticks. Only 2–8% of
  the installed compass's effect reaches them, against 36–53% in S1 hosts.
- **A known-passing host fails the control once it is put at ×8:** three S1 hosts that pass, with every
  link ×8, fail 3 of 3.
- **The same control built at the arm's own reach (every motif link ×8) passes on 5 of 5 of the S8 hosts
  that failed it, and on 3 of 3 synthetic S8 hosts.** F is +1.2 to +2.3, above the S1 hosts' own
  registered readings.

So the registered control could not pass on an S8 host except by margin-of-noise: the two S8 "passes" have
transmission of 4% and 8%. The report's reading of the VOID ("the evolved hosts mask an installed
compass", "§1.4's bias gate, seen in evolved brains", "the scale that lifts the compass's own gain also
saturates the host") needs rewriting before the coordinator rules. **VOID stands as the scored verdict.**
What it says is narrower than the report states:

> *A compass built at the default scale is invisible in a host built at ×8.*

That was knowable before any arm (F2).

## Findings

| F# | severity | finding |
|---|---|---|
| F1 | **MUST-FIX** (report wording; the verdict stands) | The install control fails by construction on K = 8 hosts. It is installed at default reach (±1, 32) into hosts whose Effector drive is ×8. Scaled S1 hosts fail it 3/3, and the arm-reach control passes on 5/5 failing S8 hosts and 3/3 synthetic ones. REPORT must say the VOID measures the control's scale, not masking of a compass at the arm's reach. |
| F2 | CAVEAT | P(VOID) = 0.15 was inconsistent with §2's founding measurement (whole-brain 0.0025 against own links 46.0). The registration flagged the gap (§4.2 limit 1, adversary F8), and a ten-minute pre-arm check (F1's group B) would have put P(VOID) near 1. |
| F3 | **MUST-FIX** | P1's −0.609 is not a fair new − old for "600 seasons of selection under ×8". The same scaling applied to a fixed S1 host costs −0.66 (−0.59, −0.59, −0.79). So the contrast is the instantaneous effect of the link scale, not of the evolved S8 hosts. "§1.4's bias gate" is the wrong mechanism, because the installed unit has bias 0. |
| F4 | **MUST-FIX** | "The scale that lifts the compass's own gain also saturates the host" does not follow. A compass scaled with the host pays in every S8 host tried. What the arms and probes show is that a **uniform** scale leaves the compass-to-host ratio unchanged, so it cannot supply relative magnitude. The planted founding geometry (±8, 8) is masked, 3/3. |
| F5 | CAVEAT | The two usable S8 arms (807, 4) pass on low transmission (T 0.037, 0.077). 807 passes by +0.011 at its lower bound. |
| F6 | NONE | `readout.py`, `peek.py` and `function.py` are blob-identical at `3f2878e`, `2524ae6` and `0634a84`. `peek-a3-*` is committed (`42e19ef`, 00:29:02) before `readout.txt` (`0634a84`, 00:30:57). `regen_a3.sh` runs integration's `peek.py`. |
| F7 | CAVEAT | The runner-made `peek-a3-*` on S8-1, S8-2 and S8-805 came from **the pre-registration's own §5 step 3**, as amended at `2524ae6`, which tells runners to produce them. That conflicts with the 23:15 ruling. They differ from the regenerated files only in the header path. |
| F8 | NONE | I regenerated 16 window readings on 8 S8 seeds from `ckpt/rbt-104-S8-SEED`. They are identical to the committed ones below the header, and the runner-added `baseline-{3,806,7}.txt` equal `baseline106` pay64 at depths 0–30. |
| F9 | NONE | An independent re-derivation (not importing `readout.py`) reproduces every scored count: S8 2/10 usable (807, 4), S1 9/10 (805's control reads +0.306 [−0.067, +0.678]), primary FD S1 [804, 2], S8 [], compass-FD 0/0, held 0 of the usable seeds and 0 of 10, income, births 10/10, and VOID. `readout.py` and `posthoc.py` re-run byte-identically. |
| F10 | CAVEAT | P3's single-season null rate can be computed from the committed null (0.035 per reading): 0.70 expected against 5 observed of 20, P ≈ 0.0002 with the cells as measured, 0.053 with each 0/20 cell at its upper bound. The report should carry it. No sentence should rest on it. |
| F11 | CAVEAT | Strand 3: this VOID says nothing for or against "magnitude is the cause". The cheapest decisive test is already in flight (RBT-106 HU). A bias-held-near-zero flag does not address the masking seen here. See §5. |
| F12 | CAVEAT (to RBT-106) | Option H has no scale masking: it is K = 1, and its control is at its own scale. It has its own route through the planted w = 32 unit's bias. At b = 0 the control passes 2/2, at b = 0.1 1/2, and at b = 0.3 0/2. But carriers at b ≥ 0.1 lose most of their gait (base 0.01–0.29 against 1.2–1.6), so a champion is unlikely to be one. RBT-106's readout should print each champion's planted-unit resting drive beside its control. |

---

## 1. Is the install control faithful, and could it pass on an S8 host? (F1–F5)

### 1.1 The code path

- `function.py --install 32` calls `install(g, 32, 1, sign)`. That calls RBT-97's `routed.install(g, 32)`:
  a new global `tanh` unit, bias 0, fed by the two wheel noses at **±1**, feeding both drive Effectors at
  **32**. The input links are then multiplied by `s = 1`.
- **Nothing reads the run's `link_scale`.** `function.py` prints it and never applies it. So the motif is
  installed at the default reach in both arms, while the host it is installed into has every link ×8
  (`genetics.scale_links` at founding, and ×8 draws after).
- This is faithful to the registration. §4.2 names `function.py --install 32` "in every arm", and its limit
  1 says the K = 8 geometry control ran only on K = 1 hosts, "the per-arm install control is the guard".
  **The control is as registered. What it measures on an S8 host is the problem.**

### 1.2 Mechanism: the host's drive on the Effectors (`sat_probe.py` → `sat_probe.txt`, POST HOC)

The probe runs the install-control body (the champion plus the a = 64 motif) on real smell, 4 seeds × 7
bests per host. Before every tick it splits each drive Effector's pre-activation into the host's part
x_host and the compass's part c. **T** is the share of the compass's effect on the Effector's output,
against an idle Effector.

| hosts | median \|x_host\| | P(\|x_host\| > 2) | E[sech² x_host] | T |
|---|---|---|---|---|
| S1 (801, 4, 806, 805, 1, 7) | 1.44–2.21 | 0.31–0.55 | 0.22–0.37 | **0.36–0.53** |
| S8 (807, 4, 801, 805, 806, 3, 1, 7) | 13.8–27.5 | 0.91–0.96 | 0.021–0.054 | **0.037–0.077** |
| **S1 hosts ×8** (801, 4, 806), synthetic | 13.0–22.1 | 0.92–0.96 | 0.023–0.033 | **0.039–0.064** |
| S8 hosts ÷8 (801, 3, 806, 805, 1), synthetic | 2.1–3.4 | 0.52–0.78 | 0.12–0.25 | 0.23–0.44 |

- The compass term is the same size in every host (median |c| 0.65–1.39).
- **An S1 host put at ×8 is indistinguishable from an evolved S8 host.** So the saturation is the link
  scale's, present from founding, and 600 seasons of selection did not move it. An S8 host ÷8 comes most
  of the way back.
- The least transmissive S1 host, S1-805 (P(sat) 0.552), is the one S1 arm that fails the control.
- The two S8 hosts that pass have T = 0.037 (807) and 0.077 (4), no better than those that fail. Their
  passes are not evidence that those hosts let a compass through (F5). S8-807's interval clears zero by
  0.011.

### 1.3 Behaviour: the control on hosts known to pass, and at the arm's reach (`probes.sh` → `probes/`, POST HOC)

Every line is `function.py` unchanged. The table is `probes/SUMMARY.txt` (`summarise.sh`).

**Reproductions from the checkpoints** (group R) match the committed `function-pc.txt` to the digit:
- S8-801 +0.188 [−0.046, +0.421];
- S1-801 +0.674 [+0.234, +1.114];
- S1-805 +0.306 [−0.067, +0.678].

**B: synthetic S8 hosts, the registered control.** These are passing S1 hosts with every link ×8
(`make_host.py`, the flag's own founder transform).

| host | registered control on the S1 host (committed) | the same host ×8 | Δ |
|---|---|---|---|
| S1-801 | +0.674 [+0.234, +1.114] FD | +0.083 [−0.276, +0.442] **fail** | −0.591 |
| S1-4 | +0.621 [+0.367, +0.874] FD | +0.027 [−0.286, +0.340] **fail** | −0.594 |
| S1-806 | +0.830 [+0.452, +1.209] FD | +0.042 [−0.221, +0.305] **fail** | −0.788 |

**D and E: the control at the arm's reach.** This is the registered motif with every link ×8, input ±8 and
output 256 (`--install 256,8`), exactly what `--link-scale 8` does to any founder link.

| host | registered control (±1, 32) | at the arm's reach (±8, 256) |
|---|---|---|
| S8-801 | +0.188 fail | **+1.688 [+0.800, +2.575] FD** |
| S8-3 | +0.121 fail | **+1.382 [+0.336, +2.428] FD** |
| S8-806 | +0.150 fail | **+2.085 [+1.215, +2.955] FD, compass FD** |
| S8-805 | −0.016 fail | **+1.935 [+1.447, +2.424] FD, compass FD** |
| S8-1 | +0.092 fail | **+1.725 [+0.798, +2.653] FD, compass FD** |
| S1-801 ×8 (synthetic) | +0.083 fail | **+2.306 [+1.682, +2.929] FD, compass FD** |
| S1-4 ×8 | +0.027 fail | **+1.493 [+0.576, +2.411] FD, compass FD** |
| S1-806 ×8 | +0.042 fail | **+1.214 [+0.182, +2.245] FD, compass FD** |

**G: the planted founding geometry** (±8, 8; a = 128), on failing S8 hosts: S8-801 +0.074, S8-3 +0.158
and S8-806 +0.138, all **not** FD.

**C: the registered control on S8 hosts ÷8.** S8-801 +0.154, S8-3 +0.272, S8-806 +0.587, S8-805 **+0.464
FD** and S8-1 +0.603 (lower bound −0.005). F rises on 4 of 5. Only one clears, but the rescale also
damages the gaits: the lesioned bases fall to 0.82–1.17 from 1.27–1.48.

### 1.4 What this means

- **The control, as implemented, fails by construction on a K = 8 host.** A host that is known to let an
  a = 64 compass through at K = 1 stops doing so at the moment its links are scaled (B, 3/3). The failure
  is not a property of what selection built.
- **An S8 host carrying a working compass *at its own scale* would still fail this control.** The same
  hosts pass it 8 of 8 when the motif is built at ×8 (D, E). So "8 of 10 S8 arms fail" is the expected
  reading whatever S8 evolved, and VOID was near certain from the moment the control was fixed at
  (±1, 32).
- **What the registration anticipated (F2).**
  - §2 measured, at founding, the planted compass's whole-brain response at median **0.0025** against its
    own links' **46.0**, with only 2 of 30 reaching the rung. It also named the per-arm install control as
    the guard.
  - §3.2 measured that the planted compass does not steer at t = 0 on all ten seeds.
  - §4.2's first limit and the design adversary's F8 said outright that the guard had never been run on a
    K = 8 host: "the VOID probability is unmeasured on K = 8 hosts".
  - The founders *are* K = 8 hosts, so group B's ten minutes, or the control on the ×8 founders, was
    available before any arm. Given §2's 0.0025, a prior of **P(VOID) = 0.15** (and 0.10 before Amendment
    3) assumed that 600 seasons would desaturate the hosts. The founding measurement gave no reason to
    expect that, and the arms show it did not happen (S8 drive 14–27, as in S1 ×8).
  - The honest prior was "VOID unless selection desaturates the host", which is much higher than 0.15.
- **The verdict stands under the registered rule**, and I propose no change to it. The REPORT's
  paragraphs under "Why VOID", P1 and "What this does to strand 3" should be reworded as in F3 and F4.

## 2. Fidelity (F6–F8)

- **`readout.py` unchanged.** Its blob is `d69ce770` at `3f2878e`, at `2524ae6` and at the PR head `0634a84`.
  `peek.py` (`336c23bc`) and `function.py` (`ec89672b`) are also identical across all three.
- **Order.** `42e19ef` (00:29:02 UTC) commits the 20 `peek-a3-*` files, and `0634a84` (00:30:57) commits
  `readout.txt`.
  - Commit order cannot prove execution order.
  - It does not need to: the window readings are a deterministic function of the checkpoint, and I
    regenerated them (below). `readout.py` also re-runs byte-identically on the PR tree, as does
    `posthoc.py`.
- **`regen_a3.sh`** runs `runs/RBT-104/peek.py` from the checkout, which is integration's (the blob
  above). It writes a file only if the WINDOW line carries `k_bare`, and otherwise leaves it missing, so
  the reading is NOT READ, never F-b. Correct.
- **The runner-made `peek-a3-*` on S8-1 (`33d158e`), S8-2 (`4dd65de`) and S8-805 (`95710d4`)** were made
  because **`PREREGISTRATION.md` §5 step 3, as amended at `2524ae6`, instructs the runner** to make them:
  "S8 only, with Amendment 3's `peek.py` from integration: … → `peek-a3-300.txt` …". Runners 1d, 1e and 1a
  followed the pre-registration's text. The coordinator's 23:15 ruling (the designer writes them, not the
  runners) contradicts that text, and the text was never reconciled (F7). **No effect:** `42e19ef` replaces
  all three pairs, and the diff is the header's path line only. Every verdict line is identical.
- **Regenerated by me** (`regen_diff.txt`). Restored from `ckpt/rbt-104-S8-{801,805,3,806,1,4,7,807}`, run
  with the checkout's `peek.py` at 300 and 599: **16 of 16 are identical to the committed files below the
  header line** (F8). Seeds 804 and 2 were not restored.
- **Runner-added baselines.** `peek.py` reads `baseline-SEED.txt` before `baseline106/`. The committed
  `baseline-3.txt`, `baseline-806.txt` and `baseline-7.txt` equal `baseline106/baseline-w1-k8-SEED.txt`'s
  pay64 fraction string for string at depths 0–30 (as do 801 and 4). **Harmless.** The 00:00 ruling
  checked only seed 3.

## 3. Re-derivation (F9): `rederive.py` → `rederive.txt`

This is independent code with its own parsers. It does not import `readout.py`.
- **Usable:** S8 **2/10** (807, 4); S1 **9/10**.
  - **S1-805 fails** because its install control reads +0.306 [−0.067, +0.678]. It is the S1 host with the
    most saturated Effectors (§1.2), and the reading reproduces from its checkpoint (group R).
  - All 20 arms are viable, and readout (a)'s control passes 20/20.
- **Primary FD on usable seeds:** S1 [804, 2], S8 []. **Compass-FD:** S1 [], S8 [].
- **Held** (k_planted > B at both 300 and 599): **0 of the usable S8 seeds, and 0 of 10** post hoc.
- **Side effects:** income S8 − S1 = +0.052 [−0.011, +0.115]; S8 had more births than S1 on 10/10 seeds.
- **F(S8 − S1)** on the seeds usable in both (807, 4): +0.115 [−2.248, +2.478].
- **P1**, re-derived: −0.609 [−0.804, −0.414].
- **VERDICT: VOID** (2 < 7), the first rule that applies.

## 4. The POST HOC section (F3, F4, F10)

- **P1 (F3).** The numbers are right, and it is labelled POST HOC. But it is not a fair "new − old" for the
  claim attached to it.
  - The S1 and S8 hosts differ in 600 seasons of separate history, as well as in reach.
  - Group B separates the two. Scaling a fixed S1 host costs **−0.591, −0.594 and −0.788** (mean −0.66),
    as much as or more than the evolved S8 − S1 contrast on the same seeds (−0.486, −0.074 and −0.680).
  - So the whole of P1 is the link scale's instantaneous effect on a compass built at the old scale.
  - **"§1.4's bias gate, seen in evolved brains" is the wrong mechanism.** The installed unit's bias is 0.
    What gates it is the host's own ×8 drive on the Effectors (§1.2).
  - **"After 600 seasons of selection, those hosts still mostly mask it"** implies selection might have
    been expected to unmask a default-scale compass. It had no such compass to select for.
  - Suggested wording: *"the installed a = 64 motif, at default scale, is masked in ×8 hosts. The same
    motif at the arm's scale is not (adversary D/E)."*
- **P2.** The numbers and labels are right. Its caveat, that the controls say an S8 zero is not a reading,
  is right and should now say why (§1).
- **P3 (F10).** The single-season null rate on k_planted can be computed from the committed Amendment 3
  tables (`p3_null.py` → `p3_null.txt`, reusing `null_rates.py`'s parser).
  - It is 0.035 per reading, so 0.70 of 20 are expected against **5** observed.
  - P(≥ 5 | null) is **0.0002** with each seed-season cell as measured. It is **0.053** if each 0/20 cell is
    set to its one-sided 95% upper bound (0.119).
  - The two seasons of a seed are not independent, and the null rests on 20 replicates per seed.
  - So it is suggestive that selection held planted payers above the operator transiently. None held at
    both seasons. **It must not carry a sentence.** The report is right to say "not read", and should
    print this number beside it.
- **P4.** The numbers are right. Its gloss ("its host did not let it through, the pattern of F-m") inherits
  F1: the whole-brain rung (13.35) is the K = 1 host's reading of a K = 1 install.
- **The strand-3 sentence (F4).** *"'Magnitude' cannot be supplied by a uniform link scale in this body,
  because the scale that lifts the compass's own gain also saturates the host."*
  - The first half follows, from §1.4's founding measurements and from G. The planted geometry is masked
    in ×8 hosts, 3/3.
  - **The "because" does not follow.** A compass scaled *with* the host pays strongly in every S8 host tried
    (D and E, 8/8), and more than a = 64 pays in S1 hosts.
  - What the probes show is that a **uniform** scale moves the compass and the host together. The host's
    Effector drive rises ×8, so the compass must rise too, relative to it. The ×8 buys no ratio: output
    256 is to an N(0, 8) link what 32 is to an N(0, 1) link.
  - Suggested wording: *"a uniform link scale cannot supply the compass's magnitude relative to its host,
    because it scales both. At ×8, the paying geometry is (±8, 256), as far out in the operator's own
    units as (±1, 32) is at ×1."*
  - This is a correction to §1.4's reading as well as to the report's.

## 5. Consequences for strand 3 (F11)

**What the VOID says.** Nothing, either way, about whether selection keeps a compass once its magnitude
is within reach. The instrument could not see a default-scale compass in the hosts the flag makes (§1).

**What it does not say.** It does not say that S8 hosts mask compasses in general. A compass at the arm's
scale pays in all of them. It does not say that selection failed to hold a compass: the (a) readings are
0 held, with a transient single-season excess (P3). And it does not say that link reach was too short.

**What RBT-104 plus these probes do support (POST HOC).** Uniform link reach is not a magnitude knob in
this body, because it scales the host too. The quantity that matters is the compass's drive relative to
the host's drive on the same Effectors. That is closer to the programme's "magnitude withholds it" than
the report's wording, and it names the right variable.

### 5.1 The two tests the report names, designed and costed

**(i) The interneuron bias held near zero.**
- **Flag.** `--global-bias-sigma S` (`MutationConfig.global_bias_sigma`, default None, meaning
  `weight_sigma`). In `genetics.mutate_weights`, a unit's bias step uses S when the brain is the global
  one (owner `None`). At S = 0 the draw is still made and multiplied by 0, so the random stream is
  unchanged and only global biases freeze.
- **Needs:** one test that every draw is unchanged at the default, a byte-identity run like §7's check 1,
  and a test that S = 0 freezes only global biases.
- **What it addresses.** The operator's erasure of the paying class (§6.0: u ≈ 0.25/generation at K = 8,
  u ≈ 0.29 for RBT-106's w = 32 at K = 1, "the bias gate").
- **It does not address the masking this VOID is made of.** The installed unit's bias was already 0 (§1).
  So **in S8 it is not decisive.** It belongs to RBT-106's H geometry, a paying compass in a default host.
- **Cheapest step, before any arm.** Re-run the operator-alone baseline (`runs/RBT-106/baseline.py`, w = 32,
  K = 1) with S = 0. That takes minutes and no arm.
  - If u falls from about 0.29 to about the structure's own decay (about 0.07–0.08, §6.0), the bias gate is
    confirmed as the whole of the erasure. Then an arm is worth running.
  - That arm is **HU + `--global-bias-sigma 0`**, 10 seeds, with RBT-106's HU as the paired control:
    5 sessions at about 1.3–2.2 h, so **about 7–11 session-hours**.
  - **Power (rough, POST HOC).** With u ≈ 0.08 and s ≈ 0.5, mutation–selection keeps about 1 − u/s ≈ 0.84
    of lines. The primary per-line power on a working compass is 0.96–1.00 at p ≥ 0.86 (§6.3). So the
    primary FD count is ≥ 5 of 10 with probability > 0.95 if H is true. On the ATTRIBUTION call (d_c ≈ 0.5),
    about 0.6–0.8.
  - I have not run this, and I state it as an estimate.

**(ii) A desaturated host.**
- **Flag.** `--global-link-scale K`: scale only the links with a global-unit endpoint (`UnitRef.node is
  None` at src or dst), at founding and in the operator's draws. The host's segment-local links stay at
  K = 1.
- **Code.** `scale_links` and `mutate_weights` take a per-link factor. The add-link draw in
  `mutate_controller` uses the factor for the new link's endpoints. Tests and byte identity are as above.
- **Caveat.** Host global units that already feed the Effectors are scaled too, so the host is only partly
  desaturated. Before any arm, run `sat_probe.py` on ×K founders built this way.
- **Why it is no cheaper than (i), and not needed first.** A paying compass in a K = 1 host is exactly what
  RBT-106's option H plants (w = 32, K = 1, pays at t = 0: RBT-106 §3.3, H − U compass-signed +1.0 uniform).
  **Option H already is the desaturated-host test, and it is in flight.**

**Recommendation.** **Run neither before RBT-106's H reads.**
- HU answers the question directly: does selection, in the uniform world, hold a compass at paying
  magnitude in a host that does not mask it? HP adds the prize.
- If H reads FALSIFIED-b (the compass is not held), then (i)'s pre-arm baseline decides whether the bias
  gate is the reason, and (i)'s arm follows.
- **Paper 10 can be written now on RBT-104 only as "VOID, and the instrument could not see"**, with §1's
  probes as POST HOC.
  - It should **not** state that uniform-reach hosts mask compasses (they mask default-scale ones), or
    that magnitude was tested.
  - Its strand-3 conclusion should wait for RBT-106 H.

### 5.2 Does RBT-106's H share the masking risk? (F12)

- **By construction, no.** H is K = 1. Its per-arm control (`function.py --install 32`) is at its hosts'
  own scale, which is the S1 case: 9 of 10 pass, and T is 0.36–0.53. Its planted founders pay at t = 0 in
  both worlds (whole-brain median 11.9, RBT-106 §5.1).
- **But H has its own route to masking.** The planted unit has v = 32. RBT-106 §5.1 measures its bias gate:
  "a resting drive v·tanh(b) above ~1 saturates the Effector". A champion that carries a planted unit whose
  bias has walked therefore puts a constant drive of 32·tanh(b) on the same Effectors the install control
  feeds. That can mask the control on that champion, as the ×8 host does here.
- **Group H probe** (`make_host.py --plant 32,b` on passing S1 hosts, the unit signed as the control
  would sign it, then the registered control on top; POST HOC):

  | host | b = 0 | b = 0.1 | b = 0.3 |
  |---|---|---|---|
  | S1-801 | +1.770 [+1.606, +1.934] FD (base 1.63) | +0.174 [−0.313, +0.662] **fail** (base 0.26) | −0.002, VETOED (base 0.01) |
  | S1-806 | +1.054 [+0.327, +1.781] FD (base 1.24) | +1.297 [+0.516, +2.077] FD (base 0.29) | −0.004, VETOED (base 0.02) |

  Here "base" is the mean lesioned income, which is the host's gait without any compass input.
- **Reading.**
  - The route is real. A planted unit at b = 0.3 masks the control completely, and at b = 0.1 it masks it
    on one host of two.
  - But **the same drift cripples the host's gait**: its base falls from 1.2–1.6 to 0.26–0.29 at b = 0.1,
    and to about 0 at b = 0.3. Selection should purge such carriers, and a population's *best* is unlikely
    to be one.
  - So this is a CAVEAT for RBT-106, not a design artefact like F1. RBT-106's readout should print, per
    champion, whether it carries the planted unit and that unit's resting drive |32·tanh(b)| beside the
    install control. An H arm that fails its control while its champions carry a drifted planted unit is
    then legible as this route, not as "the host masks a compass".
- **H's control reads high when the champion carries an intact planted compass** (b = 0: +1.77 and +1.05,
  above the bare hosts' +0.67 and +0.83), because the two compasses add. That is harmless for a control
  that must only pass.

## 6. Scripts and outputs, by role

| file | role |
|---|---|
| `make_host.py` | POST HOC: a synthetic host in scratch (links ×FACTOR; optionally a planted w = 32 unit at a given bias) |
| `probes.sh` | POST HOC: `function.py` unchanged, on restored checkpoints and synthetic hosts; groups R, B, C, D, E, G, H. (The run of R–G ended with a harmless shell parse error, because the script was appended while running. H was run separately.) |
| `probes/*.txt`, `summarise.sh`, `probes/SUMMARY.txt` | the probes' outputs, one line each in SUMMARY |
| `sat_probe.py` → `sat_probe.txt` | POST HOC: drive-Effector operating point and transmission, 22 hosts |
| `rederive.py` → `rederive.txt` | independent re-derivation of the scored counts |
| `p3_null.py` → `p3_null.txt` | POST HOC: P3's single-season null rate |
| `regen_diff.txt` | 16 window readings regenerated from 8 checkpoints, diffed against `42e19ef` |

**Suite:** 325 passed, in a clean `pip install -e '.[dev]'` venv with no scipy, on this branch (cut from `origin/claude/new-session-4cao7d` at `d04a3ef`). The branch adds files under `runs/RBT-104/readout-adversary/` only.

Checkpoints were restored into scratch with `scripts/durable.sh restore DIR rbt-104-ARM-SEED`, for S1-{801,
4, 806, 805, 1, 7} and S8-{801, 805, 3, 1, 4, 806, 807, 7}. The platform is x86_64 with MuJoCo 3.14.0,
the same as the arms, and the reproductions match to the digit.
