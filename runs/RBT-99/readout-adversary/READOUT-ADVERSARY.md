# RBT-99 readout adversary: PR #185 (`results/RBT-99-design` at `b5783ed`)

I attacked the RBT-99 readout for challenge C2 (dearer work, 0.03 → 0.08 per kJ). The designer's files are not
edited. Every income number below comes from committed tables, read through `readout.py`'s own parser on the arm
set that `readout.sh` assembles. The one exception is `probe_price.py`, which reads pre-onset baseline bulk
restored from `ckpt/rbt-90-SEED`, only rows with generation < T, as README rule 6 allows. No new arm was run.

| probe | file |
|---|---|
| round trip and seven perturbations (fresh worktrees of `b5783ed`, no bulk) | `probe_rederive.sh` → `probe_rederive.txt` |
| inputs, arithmetic, extinction coding, null, class rule, A/A, recovery, guards, lag, scoring | `probe_readout.py` → `probe_readout.txt` |
| `price.txt` re-derived from pre-T bulk, window sensitivity | `probe_price.py` → `probe_price.txt` |

## The verdict of this review

- **Class A is computed correctly and follows the pre-registered rule. It stands.**
- **This is not C1's problem.** In RBT-92 only the lead's level carried the class. Here the paired event contrast
  resolves, and by the rule's letter it classifies A too: +0.371 [+0.162, +0.581], 10/10 positive.
- **But the paired effect is arithmetic of the two bodies' gaits, not a difference in adaptation.**
  - Each body's own price (0.05 × its pre-onset kJ) predicts a paired effect of **+0.689**. The observed effect is
    **+0.371**, about 54% of that.
  - Net of its own price, **the designed body recovered more absolute income than the co-evolved body**:
    +0.524 against +0.207, a difference of −0.318 [−0.498, −0.138].
  - As a share of its price, the designed body recovered less: 55% against 79%. That per-seed difference is
    unresolved.
  - The data attribute the paired effect to the pre-onset kJ gap, which is C2's claim ("one body's cheapness").
    They do not attribute it to a difference in response.
- **Five findings must change the report before it merges: F2, F3, F4, F6 and F7.**
  - F2 and F3 are wording about arithmetic.
  - F4 and F6 are the 18:45 ruling's programme requirements, not yet applied.
  - F7 is recovery time.
  - F12's L row is a one-line change under the same ruling.
- **Nothing here needs a new run.** The class need not wait for RBT-105 (F9).

## Findings

### F1 NONE: re-derivation, inputs, and dropped seeds

Evidence: `probe_rederive.txt` and `probe_readout.txt` P1.

**Round trip.**
- A fresh worktree of `b5783ed` holds 0 untracked files and 0 bulk-shaped files under `runs/RBT-99`, `RBT-92`
  and `RBT-90`.
- In it, `readout.sh` and `score.py` reproduce `readout.txt` (sha256 `8aae84e0…`) and `score.txt`
  (`b4ce79e1…`) **byte for byte**.

**Perturbations**, each in its own fresh worktree:

| # | cell | what moved |
|---|---|---|
| 1 | base (`RBT-90/forage-2`, s482, designed +1.0) | seed 2's base R-body +0.0177 → +0.0077; base mean +0.1481 → +0.1471; designed R-shift on seed 2 −0.813 → −0.823, and its C2 net. 7 lines. |
| 2 | verdict (`shift-806`, recovery window, holistic −0.5) | shift mean +0.519 → +0.469; r 0.183 → 0.162; class still A |
| 3 | null (`cull-805`, s459, designed +0.5) | only R-body(cull), R-null and R-cull for seed 805 |
| 4 | RBT-92's `cull20-7` (linked by `readout.sh`) | only the cull20 lines. **The linked arms are read.** |
| 5 | `price.txt` (801 designed +0.1) | two C2-block lines only. **No `readout.py` line moves.** |
| 6 | `shift-806/` deleted | `readout.sh` prints "not read", "seeds read: 9/10" and exits 0; `score.py` crashes |
| 7 | `cull-k-3.txt` edited to 40 | V1 FAIL, exit 1 |

On perturbation 6: the missing arm is printed, not silent, but it is not a hard failure. That is the same
suggestion RBT-92's adversary made.

**Inputs.**
- **30 arm directories were read**: 10 shift and 10 cull from `runs/RBT-99`, and 10 cull20 from `runs/RBT-92`.
  The 10 RBT-90 baselines were read as well.
- Each `config.json` carries the right seed, `shift_at = T` and `work-cost=0.08`, the cull-k string, or
  `holistic=20,conventional=20`.
- `events.txt` has the shift from T to the end, or exactly min(k, alive) culled at T and nowhere else.
- Every table runs from season 0 to 599.
- **V0 holds on raw text** for every pre-T row of all 20 RBT-99 arms. The first difference is exactly at T.
- On the three co-evolved k = 0 seeds (804, 4, 7), the cull arm's co-evolved fauna is byte-identical to the base
  through season 599.
- **No seed was dropped or substituted.**

### F2 MUST-FIX (wording): the paired effect is the price of a costlier gait; the data do not attribute any of it to a difference in adaptation

Evidence: `probe_readout.txt` P2 and P4.

**The arithmetic.** Income is gain − work_cost × kJ. At an unchanged gait the shift removes exactly 0.05 × kJ from
every robot, and by T+60 every robot alive was born after T (P9: 0 pre-T robots alive at T+60 on every seed and
fauna). So:
- an unchanged population's recovery R-shift is −price;
- two unchanged populations' paired R-shift is price(designed) − price(co-evolved).

| | all ten | 7 designed-surviving (post hoc) |
|---|---|---|
| price, co-evolved / designed | 0.261 / 0.950 | 0.254 / 0.918 |
| **arithmetic paired prediction** | **+0.689** [+0.627, +0.751] | +0.664 |
| **observed paired** (R-body shift − base) | **+0.371** [+0.162, +0.581] | +0.205 [+0.114, +0.296] |
| observed / arithmetic, per seed | 0.52 [0.24, 0.79] | 0.30 [0.18, 0.42] |
| **net** (R-shift + price), co-evolved | +0.207 [+0.151, +0.262] | +0.197 |
| **net**, designed | **+0.524** [+0.362, +0.687] | **+0.656** [+0.569, +0.742] |
| net co-evolved − net designed (= observed − arithmetic) | **−0.318 [−0.498, −0.138]**, 2/10 positive | **−0.458 [−0.516, −0.401]**, 0/7 |
| share of price recovered, co-evolved / designed | 0.79 / 0.55 | 0.78 / 0.71 |
| share difference, per seed | +0.29 [−0.02, +0.61], unresolved | +0.17 [−0.18, +0.53], unresolved |

**What the data can attribute:**
- **All of the paired effect, and more, to the kJ gap.** The designed gait costs 3.6× the co-evolved gait's kJ
  (19.0 against 5.2). That gap is fixed before T (P10).
- **The survival of the co-evolved fauna, to the same gap.** Its unchanged-gait income at 0.08 would be +0.53 to
  +1.00, above basal on 10/10 seeds.
- **The designed fauna's survival on 7/10 seeds, to its response.** Its unchanged-gait income at 0.08 is −0.14 to
  +0.09: below basal on 10/10 seeds and below 0 on 9/10. By arithmetic alone it would be bankrupt everywhere. It
  was bankrupt by D on 4/10 seeds and extinct on 3.

**What the data cannot attribute:**
- **A better response by the co-evolved body.**
  - In absolute income, the non-arithmetic part of the paired effect resolves in the designed body's favour.
  - In share of price, it favours the co-evolved body, but unresolved.
  - Neither scale was registered.
  - The designed net is inflated by survivor-conditioning on the surviving seeds and pinned by extinction on the
    other three (F3).
  - So neither body can be said to have "adapted better".

**The null gives no leverage on this.** A random cull carries no price.
- A cull of 27–43 designed robots moved designed income by −0.018 [−0.083, +0.047] (P4).
- So designed R-null (−0.388) is its R-shift. Net of price it is +0.566 [+0.409, +0.722].
- The report's "the shift did far more to designed income than an impulse cull" is true because of the price,
  and says nothing about turnover.

**Required** in the headline, §2/§3 and the ticket summary:
- Replace "most of the verdict is the designed body's collapse" (and the coordinator's interim "dearer work took
  far more from the designed body") with the arithmetic.
- I propose:

> The designed gait costs 3.6 times the co-evolved gait's kJ, so the price alone takes 0.95 per season from the
> designed body and 0.26 from the co-evolved one. Two unchanged populations would have diverged by +0.69; the observed
> divergence is +0.37 [+0.16, +0.58], 10/10. Net of its own price, each body recovered part of the loss: the
> co-evolved body +0.21 (79% of its price), the designed body +0.52 (55%), and more in absolute terms (difference
> −0.32 [−0.50, −0.14]). The paired effect is therefore the co-evolved body's cheapness before the event, which is
> C2's claim. It is not a difference in how the two bodies responded. At an unchanged gait the designed fauna would
> earn below basal on every seed; it stayed solvent on 6/10 seeds only by turnover (3.9–6.7× its baseline's deaths)
> and went extinct on 3.

- In §3, say that designed R-null is the price, not turnover.

### F3 MUST-FIX (wording): "the co-evolved body paid back about 80% of its price" is valid arithmetic, but it is read on one body only

Evidence: P2, P9 and P10.

**The 80% itself holds up:**
- 0.207 / 0.261 = 0.790 (`score.txt`).
- There is no lifetime-mean lag. No robot born before T is alive at T+60 on any seed, so the recovery window is
  priced wholly at 0.08.
- The price barely moves with the window: 0.260–0.264 for windows of 20 to 100 pre-T seasons (P10's
  `probe_price.txt` §3).
- With the pre-registered probe's kJ (`adversary/kj_baseline.txt`, committed 13:21), the share is 0.793.

**Caveats it needs:**
- **The base's own kJ after T is not measured.** Before T it drifts by up to 0.09 in price terms: on seed 2, over
  150 seasons of `kj_baseline.txt`'s earlier window. Elsewhere it drifts by ≤ 0.03. So the 80% carries roughly
  ±0.05 from that drift alone.
- **The per-seed share runs from 0.30 to 1.63.** The co-evolved per-seed R-shift has RMS 0.106, which is the
  A/A-like spread (F9).
- **"Paid back" implies a response whose mechanism is unknown.** The report says so.

**The asymmetry is the must-fix.**
- The report reads the co-evolved net and declines to read the designed net ("survival-conditioned", §3).
- The co-evolved net is a survivors' lifetime mean too, with transient deaths at 0.96–1.93× base.
- **"The designed body failed to pay back" is a different claim, and it is false** in absolute terms (+0.524
  against +0.207). In relative terms it is unresolved.

**Required:** print both bodies' nets side by side, each with its conditioning caveat.
- Designed: survivor-conditioned on 7 seeds, extinction-pinned on 3.
- Co-evolved: low turnover, base kJ drift unmeasured.
- Do not let the co-evolved 80% stand alone as the finding about the event.

### F4 MUST-FIX (18:45 ruling, programme item 1): report the class on the no-event baseline and on placebo onsets

Evidence: P5.

| arm, window | R-body | r | positive | class |
|---|---|---|---|---|
| base (no event), recovery | +0.148 | 0.097 | 9/10 | **A** |
| base, before | +0.158 | 0.078 | 9/10 | **A** |
| cull20, recovery | +0.191 | 0.108 | 8/10 | **A** |
| cull, recovery | +0.435 | 0.326 | 9/10 | A (3 seeds: designed extinct by the cull) |
| **shift, recovery (verdict)** | **+0.519** | **0.183** | **10/10** | **A** |
| **shift − base, paired** | **+0.371** | 0.210 | 10/10 | **A by the rule's letter** |
| shift − base, paired, 7 surviving | +0.205 | 0.091 | 7/7 | A |
| shift − cull, paired, 7 uncapped | +0.315 | 0.154 | 7/7 | A |
| cull20 − base, paired | +0.043 | 0.074 | 6/10 | B |

- **Placebo onsets on the base alone** (T' = T−200 to T+40): **A on 23/25**. The base and T are RBT-92's byte for
  byte, so this is RBT-92's result by construction.
- The report gives base +0.148 but never says the rule returns A there.

**Required:** one sentence in the headline and in §5:
- The rule returns A on the no-event baseline and on 23/25 placebo onsets.
- Unlike C1, the paired event contrast also classifies A, so here the event did move the contrast.
- That movement is the arithmetic of F2.

### F5 CAVEAT: extinction coded as 0, and the 7-seed subset is post hoc

Evidence: P3.

**The three extinct seeds carry 61% of the summed paired effect.** They are the top three: 806 +0.912, 2 +0.819
and 807 +0.542. The other seven run from +0.057 to +0.294.

**The 0 coding does not inflate the effect relative to arithmetic.**
- Coding extinct seasons at the unchanged-gait income (base designed − price, about −0.14 to −0.02 on those seeds)
  instead of 0 gives **+0.382** [+0.154, +0.609], against +0.371.
- The 0 is, if anything, generous to the designed body.
- What lifts those seeds is extinction itself, which the price predicts.

**The subset is post hoc.** "Seeds where the designed fauna never reached 0" is defined on the outcome. The
pre-registration names no such subset; its only partition is D's test. The alternatives agree:

| subset | paired effect | positive |
|---|---|---|
| **7 designed-surviving** | +0.205 [+0.114, +0.296] | 7/7 |
| **6 non-D** (the registered partition, also outcome-defined) | +0.215 [+0.105, +0.324] | 6/6 |
| **5 neither extinct nor capped** | +0.206 [+0.064, +0.347] | 5/5 |

The shift R-body classifies A on the 7 (+0.407, 7/7) and on the 6 (+0.423, 6/6).

**Required:** label the 7-seed figures "post hoc, outcome-defined". Nothing else changes.

### F6 MUST-FIX (18:45 ruling, programme item 1): the paired contrast against the registered random-cull null is not reported

Evidence: P4.

The ruling makes "the paired event − base contrast against the random-cull null" the readout that speaks to the
event. Paired R-body (shift − cull), recovery:

| seeds | value | positive |
|---|---|---|
| **7 uncapped** (option (a) as registered: capped seeds n/a) | **+0.315 [+0.161, +0.469]** | **7/7** |
| 5 uncapped and not extinct | +0.228 [+0.118, +0.337] | 5/5 |
| all ten, capped seeds read as-is | +0.085 [−0.219, +0.389] | 7/10 |

- **The paired effect resolves against the registered null** on the registered n = 7.
- On the three capped seeds (806, 1, 3) the null is extinction, so shift − cull is negative there (−0.07, −0.59,
  −0.70). Including them drowns the contrast. The registered option (a) excludes them correctly.
- Two of the seven (807, 2) are extinct in the shift arm.
- Against the null, observed minus arithmetic is −0.376 [−0.481, −0.272] (F2's conclusion, again).

**Required:** print this line, with its n = 7 and the capped-seed note, beside the shift − base line.

### F7 MUST-FIX (factual, RBT-92 F4 carried): "returned to the control's band within 180 seasons: 9/10" counts three d = 0 artifacts

Evidence: P7.

**Three of the nine co-evolved recoveries are d = 0 artifacts.**
- Seeds 806, 807 and 2 return d = 0. They first leave the 2-SD band at **T+29, T+31 and T+52**, after the
  [T, T+20) hold was already met.
- Seed 1 (d = 3) leaves at T+2.
- Six seeds show a real exit and re-entry: 801, 804, 805, 1, 4 and 7, with d from 3 to 177.

**The designed "none on 10/10" is the price.** The designed price is 6.1–8.8 × h on every seed, so an unchanged
gait can never re-enter the band. The co-evolved price is 0.8–2.5 × h.

**Required:**
- Drop the ticket summary's recovery table as a finding, and in §4 say what the 18:45 ruling says: no recovery
  claim from the registered rule.
- If the numbers are kept: co-evolved "left and re-entered on 6/10; d = 0 on 3/10 (806, 807, 2) because
  divergence reached h only at T+29 or later; none on 1/10". Designed: "none on 10/10, as its price (6–9 h)
  predicts".

### F8 CAVEAT: "holds up": the wording is right; print the null number beside it

Evidence: P8.

**The wording is right.**
- Co-evolved R-shift −0.055 [−0.123, +0.013] against −r = −0.183.
- The report calls it "an unresolved loss, not a demonstrated absence of one". It claims no absence.

**It is robust to the bar.** It holds at the level r, at its own paired r (0.068) and at the pre-registered 0.077.
- The level r (0.183) is 2.4× the expectation *because the designed collapse varies between seeds*. The
  comparator's collapse loosened the co-evolved body's bar, but the result does not depend on it.

**Against the registered null, the co-evolved loss resolves:** −0.074 [−0.117, −0.031], 1/10 positive. The report
prints this only in the turnover-guard paragraph.

**Required:** the headline "holds up" line carries both numbers, as RBT-92's F3 ruling required for its designed
cost.
- The designed body does not hold up by any bar (−0.426).
- Its unchanged-gait R-shift would have been −0.95.

### F9 CAVEAT: the A/A-like spread and the sign guard

Evidence: P6.

**A/A-like per-seed RMS, recovery window:**

| sample | RMS |
|---|---|
| co-evolved cull − base, k 1–3 | 0.086 |
| co-evolved cull − base, all k > 0 | 0.079 |
| cull20 − base per fauna | 0.077 |
| R-body cull20 − base | 0.108 (mean +0.043) |

- **Co-evolved R-shift per seed has RMS 0.106, the A/A size.** No per-seed co-evolved response can be read alone,
  and that includes the per-seed 80% shares.
- Paired per-seed values below one A/A unit: 801 at +0.057 and 804 at +0.108.

**The sign guard has a 2-seed margin** (10/10 against 8), unlike C1's zero. Jittering per-seed values by
N(0, s) for s = 0.05–0.11 leaves class A in ≥ 99.4% of draws, for both the shift R-body and the paired contrast.

**RBT-105 cannot move the class or the paired sign.** Its recovery-window RMS should be read against 0.08–0.11 as
a post-hoc check on the per-seed tables, as for RBT-92.

### F10 CAVEAT: the turnover guard

Evidence: P8.

- It is scored on **n = 7** (co-evolved k = 20, 1, 2, 2, 3, 1, 10).
- R-null = −0.084 [−0.136, −0.033], which resolves.
- The guard prints YES because |−0.084| < the level r, 0.183. That r is set by the designed body's between-seed
  spread. The co-evolved R-null's own paired r is 0.043.
- The report already says YES "is not a finding of equivalence". **Required:** add "(n = 7; r is inflated by the
  comparator's spread)" wherever YES appears, including the ticket summary.

### F11 NONE: the `price.txt` deviation

Evidence: `probe_price.txt` and P10.

- **`price.py` on the ten restored RBT-90 baselines reproduces `price.txt` byte for byte.**
- It reads only lineage rows with T − 40 ≤ generation < T. That is exactly Amendment 1's window, committed at
  13:38 before any arm existed.
- Those seasons are byte-identical across arms (V0).
- **It could not have been tuned:**
  - The pre-T window choice moves the paired arithmetic prediction only from +0.681 to +0.700 (windows of 20 to
    100 seasons).
  - The pre-registered probe's kJ (committed 13:21) gives +0.692, with shares 0.793 and 0.555.
- **`price.txt` enters no `readout.py` line** (F1, perturbation 5). The report states the deviation correctly.

### F12 CAVEAT, with one required line: the scoring of the predictions

Evidence: P11.

- **Brier 0.2010 re-computed** over the 12 rows. Every HIT/MISS matches `PREREGISTRATION.md` §10 as amended by
  Amendments 1–2.
- **Required (the 18:45 ruling, F8's line):** "L(T+160) shift − cull within ±0.10: HIT (0.5)" becomes **"not
  scored (UNVALIDATED, V3)"** in `score.txt`'s printout, §6 and the ticket summary. It is outside the Brier already.
- **"Co-evolved survives 10/10" (0.85) and "designed transient deaths ≥ 2 × base" (0.8) were set by the pre-onset
  kJ.**
  - The co-evolved unchanged-gait income is +0.53 to +1.00, above basal on every seed. The pre-registration's F4
    said as much.
  - The designed unchanged-gait income is below 0 on 9/10 seeds.
  - They should read "right, but set by the pre-onset kJ".
- **The misses are owned honestly**, including the co-evolved net (+0.207 against +0.03) and the extinction count.
  So is falsifier (i), fired and scored against the original design.

---
_Generated by [Claude Code](https://claude.ai/code)_
