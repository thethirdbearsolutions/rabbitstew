# RBT-125 readout adversary, pass 2: #436 at 28f374a (§B, the pass-1 closure, and the verdict on #436)

*This is the coordinator's task of 08:02 UTC. The gate finished at 08:00:14Z, with exit 0. §B was re-derived from the
committed `steps/PW-*.txt` with my own code (`recompute_B.py`), in a clean `pip install -e ".[dev]"` venv with no
scipy: the t quantiles are hard-coded. Nothing was run on hosts.*

## Verdict on #436: **CONFIRMED WITH CAVEATS**

| item | count |
|---|---|
| MUST | 1: a §B sentence that over-reads a descriptive cell |
| SHOULD | 3 |
| NIT | 3 |

Every number in #436 that I checked reproduces:
- §A's layouts (pass 1);
- §C and τ = 1 s (#445, #448);
- §B here, to the rounding of the per-host table.

## 1. The pass-1 findings (#458): all closed

| #458 item | status in 28f374a |
|---|---|
| M1: ranking read from point estimates | **closed.** The table gives HP − PW, HP − U, and PW − U as "(unresolved)". The legacy ranking is "not resolved"; "scales with the layout" is labelled *conjecture* |
| S1: U base-income drop | **closed.** −0.113 [−0.213, −0.013] and −0.142 [−0.259, −0.025], stated as resolved |
| S1: U's absolute channel contribution | **closed.** An absolute-income table for all three layouts |
| S2: HP and U without a decoy | **closed.** "not shown to be food-dependent. Only PW's is" |
| S3: U-G0 as audit C's second failed prediction | **closed**, with a citation to AUDIT L451 |
| S4: the stale §C sentence | **closed.** The corpus and founder `surface` rows "reproduce to the digit … the minimal guard did not bind" |
| NIT: "not detectably worse" | **closed** |
| NIT: merge integration | **open again.** 28f374a does not contain integration's head (3d7e8be), but merges clean |

## 2. §B, re-derived (`recompute_B.py` / `.txt`)

**The line and interval are exactly the registered ones** (amendment A1.4):
- the w 3 → 3.4 nose step, minus the per-unit speed step at w3;
- per-unit = (speed@w3 − w3) × 0.25 ÷ (r − 1), over hosts with r ≥ 1.10;
- paired per host, t(n − 1) at 95%;
- read by: NOSE LEADS if the 95% lower bound > 0; SPEED LEADS if the upper bound < 0; COMPARABLE if the 90% interval is
  inside ±0.10; TIED otherwise.

`reading()` in c591a75's `steps.py` implements that order. The copy that ran is the pinned c591a75 one. The head's
`steps.py` later gained reuse flags and a scipy-free t quantile, but its registered defaults and path are unchanged
(NIT 2).

**My figures** (per-host means are read at 3 decimals, so the last digit can differ):

| cell | nose − per-unit speed, w3 line | reading | readout |
|---|---|---|---|
| PW-G2.5 | +0.316 [+0.032, +0.600], n 13 | NOSE LEADS | +0.317 [+0.032, +0.602], NOSE LEADS |
| PW-G10 | +0.243 [−0.076, +0.563], n 13 | TIED | same |
| PW-G0 | −0.266 [−0.413, −0.119], n 13 | SPEED LEADS | same |

The w1 and first-nose lines, and the raw-speed lines, also reproduce, and so does every reading.

### Was the +25% speed step delivered?

On average, partly: the realised speed ratio at w3 is 1.20 at G2.5 (range 0.82–1.46), 1.20 at G10 and 1.24 at G0. The
per-unit rescaling corrects for this per host, as registered. That multiplies a host's speed step by up to 2.19 at
G2.5, which adds noise.

### Why is n 13 on the registered line?

Exactly the registered exclusion, and it is counted:
- G2.5: 15 hosts signed; 2 leave at w3 for r < 1.10: O1/3/023 (r 0.993) and O1/3/031 (r 0.816).
- G10: 023 (1.075) and O1/3/028 (1.022) leave.
- G0: 14 are signed (O1/3/028 UNDETERMINED), and O1/2/008 (1.051) leaves.

Nothing else is dropped. The other arms' exclusions are listed in `recompute_B.txt`.

### Are "NOSE LEADS" and "no COMPARABLE anywhere" consistent with the rule?

**Yes.**
- LEADS is tested before COMPARABLE, but no line would have met COMPARABLE anyway. Every line's 90% half-width is
  0.11–0.29, and to fit inside ±0.10 it would need a half-width under 0.10 around a mean near 0. That is the power
  statement's own prediction.
- "No COMPARABLE anywhere" is therefore a power result. It is not evidence that the steps differ.

### How robust is the NOSE LEADS?

**Fragile.**
- Leaving one host out of the 13 gives lower bounds from **−0.021** to +0.098. At least one host's removal turns the
  reading into TIED.
- The raw-speed comparison is sturdier: +0.324 [+0.091, +0.558].
- It is one descriptive line among 18 printed readings (3 cells × 3 steps × raw / per-unit). §B is registered as
  descriptive with no multiplicity control. See SHOULD 1.

### What drives the G pattern?

**The speed step, more than the nose step.**

| | G2.5 | G10 | G0 |
|---|---|---|---|
| nose step w3 → 3.4 | +0.247 | +0.173 | −0.060 |
| per-unit speed step at w3 | **−0.074** | −0.020 | **+0.214** |

- Under the channel, +25% speed does not pay a host that already carries a compass at a = 6. Under legacy smell, it
  pays +0.21.
- **This is what the channel's approach gating predicts.** The three noses share one baseline, so faster motion along
  the gradient multiplies L − R by about sech²(G·c) (`runs/RBT-125/adversary/probe_motion.txt`: 30% of static at G2.5
  and 0.5 m/s). A faster steerer loses steering signal. A.8 of the amendment already states this mechanism.
- The readout's own conjecture (overshooting 0.4 m patches) is possible. The gating mechanism is documented and
  predicts the sign, and it should be named first. SHOULD 2.
- **G10:** the installed compass pays more (+2.0 against +0.82, unpaired), and the next nose step less (+0.17 against
  +0.25). That is consistent with saturation (the saturation table: G10 median |c| 0.89) and with stronger gating.
  Both are descriptive.

### Is G0's SPEED LEADS the expected legacy calibration?

**Yes, and it says something about these hosts.**
- Under legacy smell, the installed a = 6 compass barely pays on the RBT-113 hosts: +0.048 [−0.056, +0.151], against
  +0.125 on §A's RBT-90 bests.
- So the nose steps are ≈ 0 or negative, while speed pays.
- This is consistent with audit C's un-centred "gain 1" probe (nose steps +4% / +7%) and with the R4 premise that the
  legacy world pays speed over noses. It was not a registered prediction.

## 3. What §B licenses (it is descriptive under the registration)

**For RBT-121 R4 ("a nose step pays at least comparably to a speed step, along the path"):**
- **Licensed:** at G = 2.5, on 15 RBT-113 O1 hosts carrying an installed a = 6 compass, the next one-σ nose step paid
  more than a realised +25% speed step at the same base. The reading is fragile to one host, and it is descriptive.
- **Not licensed:** that R4 holds *along the path*. The path's early steps, the first nose and w 1 → 1.4, read TIED at
  every G, with 90% intervals of ±0.12 to ±0.29 around −0.11 to +0.10. So the comparison is unresolved exactly where
  evolution starts. The readout says this correctly ("a statement about the step path from a working compass, not
  from none").

**For RBT-129's PAYS rule (COMPARABLE or NOSE):**
- §B licenses nothing for RBT-129's cells. RBT-129's legs run their own `steps.py` per PAYS cell.
- RBT-125's G2.5 NOSE LEADS is on a different world (PW at c591a75), with different hosts, at the w3 rung. It should
  not be cited as a PAYS precedent.
- The readout does not claim it is one. It should say so explicitly, since the sweep's rule uses the same labels (NIT 1).

## MUST

**M1.** The §B finding "**So the channel flips the R4 comparison on real hosts at this rung.** That is the audit's
kinematic claim (`probe_gprop.txt`: 'every step ties speed'), seen on real bodies. At the w3 rung it is stronger than a
tie" over-reads. It has three problems:
- **"Flips" is a G2.5 − G0 contrast that was neither registered nor computed.** The two cells are read separately.
  One is SPEED LEADS and the other NOSE LEADS on a fragile line; nothing tests their difference.
- **It is not the audit's claim seen on real bodies.**
  - The audit's kinematic PW-G2.5 pattern was **every** step (first nose +0.18, k1 → 1.4 +0.19, k2 → 2.4 +0.17)
    *tying a speed step that paid* (+0.17).
  - On real hosts, the early steps are unresolved, and the speed step at w3 does **not** pay under the channel (−0.07).
  - The w3 lead comes mostly from speed collapsing, not from a nose step of the audit's size meeting a paying speed
    step.
- **Fix:** replace it with the separate readings, for example "under G = 2.5 the registered line reads NOSE LEADS
  (fragile to one host); under G0 it reads SPEED LEADS; the difference was not tested". Add the speed-step collapse
  under the channel, and give approach gating as its documented candidate mechanism.

## SHOULD

1. **State the fragility and the multiplicity** beside the NOSE LEADS: leave-one-host-out lower bounds span −0.021 to
   +0.098, and it is 1 of 18 printed readings in a descriptive section.
2. **Name approach gating** (A1.8, sech²) as the documented candidate for "speed at this rung hurts", before the
   overshoot conjecture. Point out that G0, which has no gating, is where speed pays.
3. **Add the RBT-113-host calibration.** The installed a = 6 compass barely pays under legacy smell on these hosts
   (+0.048 [−0.056, +0.151]), unlike §A's RBT-90 bests (+0.125). This is why G0's nose steps are ≈ 0; it is a
   property of the hosts, not only of the channel.

## NIT

1. Say in §B's scope that RBT-129's PAYS rule uses the same labels on its own legs, and that §B is not a PAYS
   precedent.
2. Say that §B ran with c591a75's pinned `steps.py`. The head's copy has reuse flags and a scipy-free t, with the
   registered defaults unchanged.
3. Merge integration (3d7e8be) into the branch before merging; it merges clean. "Far more (+2.0 against +0.82)" for
   G10's installed compass is unpaired; "more" is enough.

## Files

| file | what it holds |
|---|---|
| `recompute_B.py` / `.txt` | §B from the committed per-host tables, with hard-coded t quantiles: every line and reading, the exclusions per arm, the realised r, the 90% half-widths, and the leave-one-host-out bounds of the w3 line |
