# W1 gate check: #484 (head `f0f9fd7`), the proposed amendment to RBT-116 §1.1 ("≥ 1 control reaches")

*2026-09-28, the design adversary. Pre-data: no W1 arm, gate cell, screen or battery has run.*

**Scope.** #484 is docs-only (`W1_GATE_AMENDMENT.md`). It is based on integration `56f8672`.

**The bar is higher here than for #478**, because this amends a registered study.

## Verdict: **ADOPT-WITH**

The rule change is right for W1, for the same reason as at RBT-129's points: "at least half" cannot pass a W1 gate
whose G8(c) controls rarely eat. But the amendment must say three more things before it is registered, or W1's screen
is under-specified:

1. **Which hosts are screened, and how many (N).** The registration is silent on this, and the two rules behave very
   differently as N grows (§1).
2. **W1's table records `ate_by_host`**, as #478 now does at RBT-129's points.
3. **It lands after #478.**
   - The code it relies on (`admissible`, `SCREEN_ANY`, `ate_by_host`) is **not on integration yet**: `steer.py` at
     `56f8672` has none of it.
   - #484's "its implementation already exists" and "merged with #478" are true only of #478's head (`e063f49`).

## (a) Does the #482 reasoning carry over to W1?

**Partly. The failure mechanism carries over; the size of the selection bias depends on N, which W1 has not fixed.**

**Who the screen hosts are.** §1.1 says "the positive-control hosts of G8(a) and G8(c) run every pool draw intact".
- G8 has 4 designed and 4 holistic burn-in-final hosts per unit, **192 in all**, drawn from W1's own arms. They are
  **not** RBT-19 bodies, and not O1's.
- STEER_NOTES says the screen runs "with the G8(a) and G8(c) hosts".
- So the screen hosts **are** G8's plants, and G8 then calls them on the admitted draws.
- The battery is shared by the whole study: G1, G4, G6, G8 and every arm's probes.

**Selection bias.**
- **Luck selection.** Under "≥ ½", draws are admitted where the screen hosts happened to eat, so each G8 plant is read
  partly on its own lucky seasons. That is the #478 mechanism, and its size is about 1/N per host.
  - It is large with the fixture's 12 hosts: ×2.23 on intact eating (`gate_diag.txt`).
  - It is small if all 192 hosts screen.
- **Draw selection.** "≥ ½" also keeps only easy draws, for every body alike.
  - The arms' U and N lines share the battery, so their comparison stays fair.
  - But G8's absolute pass rules (G8(c) at ≥ 20%, G8(b)'s F ≥ 0.25) and the gate's measured SENS and EPS are then
    judged on easy draws. They are optimistic in the direction that makes the study look more powerful than it is.
- **G8(a) is partly protected**, because its bar is relative (0.6 × c_G1, on the same battery).

**The gate failure itself** does not depend on N (`w1_gate_hosts.txt`, exact binomial).
- In the model, half the hosts (the G8(c) plants) never eat, and a typical draw's rate is 0.25.
- "≥ ½" then needs **every** eater to eat. It admits 6% of draws at N = 8, 0.4% at N = 16, and 0 at N ≥ 32.
- **W1's gate fails under the registered rule whatever N is**, unless W1's own G8(c) plants eat far more often than
  the fixture's (0.00) or O1's apparently do.

**But "≥ 1" is not N-free either:**

| N screen hosts | "≥ 1": P(admit a typical draw) | P(admit a near-hopeless draw, p_d 0.02) |
|---|---|---|
| 12 | 0.98 | 0.22 |
| 16 | 1.00 | 0.28 |
| 48 | 1.00 | 0.63 |
| 192 | 1.00 | **0.98** |

- With all 192 G8 hosts screening, "≥ 1" admits nearly every near-hopeless layout. That is exactly what MUST 1 (M2:
  "hopeless layouts") asked the screen to drop.
- W1 has **random terrain**, unlike RBT-129's flat c0 cells, so such draws are more plausible there.
- **Condition 1:** the amendment registers N and the host set.
- I recommend **16 screen hosts: 8 G8(a) and 8 G8(c)**, drawn by a registered `default_rng` from G8's hosts. That
  matches RBT-129's screen, and at N = 16 "≥ 1" still drops about 72% of near-hopeless draws.

## (b) "3 of 48 under ≥ ½", and what "≥ 1" admits: indicative, not a measurement

The figure is `gate_diag.txt` Part 2: 12 fixture controls on 48 fixture draws in W1's block (random terrain, 15 s).
- It admits **3 of 48 (6%) under ≥ ½, and 45 of 48 (94%) under ≥ 1.**
- The controls are 6 G8(a) and 6 G8(c) plants on RBT-19 bodies, not W1's G8 hosts, and N = 12, not W1's.
- It is therefore **indicative** of the mechanism: the six G8(c) controls ate 0.00 at every length and terrain.
- It is **not a measurement** of W1's gate. #484 says so itself.

My own earlier "77%" (FIX-CHECK-476) was a denser W1-*shaped* test fixture, and I have withdrawn it (GATE-CHECK-478 §4).

## (c) Power

- **`power_tau1.txt` models no screen.** `power.py` takes caricature priors (SENS, EPS, u, σ), and its batteries are the
  registered counts. Nothing in it reads a screen table. So the amendment changes **neither `power_tau1.txt` nor n**:
  the battery is still 4 + 16 + 16 from the first admitted draws in pool order.
- **What it does change is the gate's measurements.** "GATE values replace every prior before launch": SENS_C from G1
  and G8(a), SENS_C,H from G8(c) and G8(f), EPS_C from G4.
  - Under "≥ ½", those would be measured on easy draws, where they are inflated. The re-run power would be optimistic.
  - Under "≥ 1" they are measured on essentially the whole pool. **The measured SENS may come out lower, and the
    launch power lower with it.** That is the honest direction, and the amendment should say so.
  - Put plainly: the registered rule would either fail the gate or, with luck, pass it on a battery that flatters it.

## (d) The registered test: is editing it the only registered change, and is it safe?

**It is not the only registered change.** The amendment must also:
- amend **PREREGISTRATION.md §1.1** as a dated pre-data amendment, as Amendments 1–3 were;
- fix STEER_NOTES N20 ("admissible iff 2 × (hosts eating ≥ 1) ≥ hosts");
- state the host set and N (condition 1).

**The test edit itself is safe.**
- `test_screen_admits_by_half_the_hosts_and_assigns_in_pool_order` pins the half rule. #484's edit gives the "bad"
  draws zero eaters instead of one. It keeps 42 of 64 admitted and every pool-order assertion, and adds a one-eater
  assertion at W1. Nothing it checked is lost.
- `test_screen_extends_once_then_fails` is unaffected: its two hosts eat together.
- **No RBT-116 kill-set mutant touches the screen rule** (I grepped `steer_mutants.py` and `steer_mutants2.py` for the
  screen). The re-run should give 16/16 and 24/24 against the edited file. Re-run it and commit it.
- **Identity scripts to update:**
  - my `rbt132_w1_identity_extra.py` compares `screen_draws(W1)` with `ce69f17`, and will then differ, correctly. It
    should compare with the rule set aside, as `rbt132_battery_identity.py` does.
  - `rbt132_478_mutants.py`'s `W1-in-SCREEN_ANY` mutant becomes the registered code, and should be replaced by
    `W1-out-of-SCREEN_ANY`, as #484 says.
- **The end of "no diff against `ce69f17`"** is the real cost. It is acceptable because it is pre-data, dated, and
  confined to one test whose assertions are kept.

## (e) Would a screen with hosts disjoint from the plants be better for W1?

**Only if a threshold above 1 is wanted.**
- Disjoint hosts remove the luck selection on G8's plants entirely, so a stricter rule could be used without biasing
  G8.
- But under "≥ 1" at N = 16, a G8 plant's own season decides a draw only when it is the sole eater. With 8 eaters at
  a rate of 0.5, that happens on about 3% of draws. That residual is negligible.
- A disjoint set costs a registered second host set drawn from the arms' burn-in finals, with its own carrying rule.
- **Not needed with condition 1.**

## Conditions, as fixes

1. **Register the screen's hosts:** 16 (8 G8(a) and 8 G8(c)) by a registered `default_rng` from G8's hosts, with the
   rule "≥ 1 of them eats ≥ 1 item intact". State what it drops: a draw no screened control reaches.
2. **Record `ate_by_host` at W1 too.** #478 keeps W1's table "as registered"; the amendment should switch it on.
3. **Merge order:** #478, then the code of #484. The §1.1 text, N20 and the test edit go in one dated amendment. Then
   re-run the kill-sets and fix the identity scripts, as in (d).
4. **Say it in the amendment:** the gate's measured SENS may fall under "≥ 1", and that is the correction, not a loss.
5. **Optional, the coordinator's call:** register the RBT-116 analogue of #478's S-2 statement (no post-data change to
   G8(c)'s layout, hosts, rung or carrying rule), since W1's G8(c) may also rarely eat.

## Files

In `runs/RBT-116/design-adversary/`: `w1_gate_hosts.py/.txt`, the admission probabilities against N (exact).
