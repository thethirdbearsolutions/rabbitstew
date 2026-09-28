# RBT-129 r3 check: PR #412 at `606368a`, against R2-CHECK.md (`d3f5209`)

**Verdict: REGISTER AFTER FIXES.** Two one-line MUST fixes remain. Both are verdict clauses in §8 that reopen a route
through the share layer that the ruling demoted. The coordinator can verify both without another adversary pass.

- **R2-M1, R2-M2 and R2-M3 are closed as ruled.**
- **R2-S1 is closed as ruled.**
- **S-1 to S-6 are closed.**
- **The re-costed budget re-derives**, with small uncosted items listed in §3.

No new probes were needed. The check below uses r3's `power_r3.txt`, `prior_regime.txt`, and this directory's
`probe_retention.txt` and `probe_verdicts.txt`.

## 1. The R2-CHECK items

| item | r3 | status |
|---|---|---|
| **R2-M1** retention | see the five parts below | **closed** |
| **R2-M2** g0 | g0, taken from the census, enters the share model only. The income model is fitted on c, log p, L, s and c × log p, with a random intercept per point (§7.2) | **closed** |
| **R2-M3** opposite-sign sets | ≥ 2 calls, or 1 call corroborated by an M3 break-even whose Fieller interval lies inside [0.01, 0.08]. The rule is applied symmetrically: a dominance verdict tolerates one uncorroborated call for the other fauna (§8) | **closed**. A break-even inside the grid is real dependence under the linear income model, so it is a fair corroboration |
| **R2-S1** share layer demoted | see the five points below | **closed**, except for the two §8 clauses in §2 |
| S-1 | `resolvable()` is run at both bounds (`power_r3.txt` §5′). RESOLVING needs the g0 interval inside [0.5, 0.65] at n 8, or inside [0.5, 0.80] at n 16 | closed |
| S-2 | CONTINGENT is computed at the gated df. It is not callable below df 12. Under shuffle it fires at 0.01–0.03, a false rate ≤ 0.010 (`power_r3.txt` §6b′) | closed |
| S-3 | net income per birth is printed beside the flow; MARGINAL is added | closed |
| S-4 | VARIANCE-DRIVEN is decided by a two-predictor fit | closed |
| S-5 | N is run only where census g0 ≤ 0.8 | closed |
| S-6 | the anchors are taken from RBT-118, with fallback arms at 46 core-h | closed |

**R2-M1, the retention layer, in detail:**
- **Floor and planted negative.** R_marker (the lesioned motif) is both. h = carriage(R_sel) − carriage(R_marker).
- **R_drift** is descriptive only, and depends on `--breed-gate none`, which is no longer a gate.
- **Readout floors.** These are validated on planted genomes (≥ 0.95), random genomes (the false-carriage rate is
  printed) and ablated genomes (must read absent). A failure VOIDs that fauna's layer.
- **Behavioural confirmation.** It is held to K3's bars, and R_marker members must read NONE. That makes it a second
  check able to fail.
- **Operator table.** It prints u_f and births per season per fauna. A cross-fauna reading is allowed only at one
  matched-erosion re-read.
- **Power table.** r3 registers a regime × value power table, and withdraws "not bounded by the saturated band".
  Retention points are ranked by census g0, and points above 1.3 are dropped.

**R2-S1, the share layer's demotion, in detail:**
- M runs at census g0 ≤ 1.0 as the one-world income column.
- N runs only at census g0 ≤ 0.8.
- The anchors are taken from RBT-118, with seeds coordinated.
- DEPENDS and ONE BODY DOMINATES are moved below their income counterparts and marked "not expected to be reachable".
- §1 and §8 say "earns, not persists".

## 2. Does anything in r3 reintroduce a demoted verdict path?

**Yes, in two clauses of §8.**

### R3-M1 (MUST): WORLD-INVARIANT's share route

§8, verdict 6 reads: "EARNS-TIE at ≥ half of the habitable points, **or share TIE at ≥ half of the RESOLVING
points**".

Under shuffle, `prior_regime.txt` expects **0 RESOLVING points at n 8 and 2 at n 16**. N runs at no more than 4 sweep
points. So a **single share TIE at one of two RESOLVING points** satisfies "≥ half". Together with a failure to reject
T1 and the absence of an opposite counting set, one share call would then deliver a falsifying verdict for the whole
map.

That is the share layer deciding the headline, which the ruling demoted.

**Fix:** delete the share route from verdict 6, so that WORLD-INVARIANT runs through EARNS-TIE only. If the share route
is kept at all, give it a floor, for example "at ≥ half of the RESOLVING points **and** at ≥ 6 RESOLVING points". It
then cannot fire under shuffle, and it becomes live if a later rule makes RESOLVING common.

### R3-M2 (MUST): DEPENDS ONLY THROUGH HABITABILITY switches its basis to the share layer

§8, verdict 5 reads: "every decided EARNS call (**or, if there are share WINs, every decided WIN**) favours one fauna
X".

As written, **the existence of one share WIN switches the verdict's basis from income to share.** A map could then
have:
- EARNS calls for both faunas, including a counting set for Y;
- one share WIN for X;
- a set of survival calls for Y.

On the share basis, it reads "only through habitability". On the income basis, it is EARNINGS DEPEND territory,
except that EARNINGS DEPEND ranks first and would catch it only if T1 rejects. If T1 fails to reject, verdict 5 is
reached through the share basis while the income layer shows a ranking reversal.

**Fix:** income is the basis. The clause becomes: "every decided EARNS call favours one fauna X, with no counting set
for the other; **any share WINs must also favour X**". Share WINs can then only veto the verdict, never supply it.

### Checked and not reintroduced

- Verdicts 2 and 4 are share-based. They are below their income counterparts, and marked unreachable. Verdict 4 is
  also bounded by the gate.
- Verdict 1 (EARNINGS DEPEND) and verdict 3 (EARNINGS DOMINATED) are income only, with the R2-M3 sets.
- RBT-118's rule-chosen points now use the income effect (§9.1).
- K2 and CONTINGENT exist only where N does.
- §6.2's "What SATURATED does not mean" still holds. So does §6.4's "UNDECIDED at census g0 > 0.9 … says nothing about
  the bodies".

### SHOULD

**S3-1: SATURATED (not run) is used as evidence in two places.** Most points now read "SATURATED (not run; census
g0 = x)" (§5.2). This label is a gating decision, not a measurement. Two places still read it as a finding:
- **§9.2, W2's criterion** ("PAYS, SATURATED and NONE for both faunas … §6.3's 'pays but the ecology does not select
  it'"). Almost every PAYS point now satisfies "SATURATED" by default, so W2's criterion reduces to "PAYS and NONE".
  Its gloss implies the ecology was measured and failed to select.
- **§6.3's cross-tab row** "PAYS, SATURATED and NONE: … this ecology's births do not spread an edge of δ_i".

Fixes:
- Split the label into SATURATED (measured: M and N ran, and the point is not RESOLVING) and NOT RUN (census g0
  > 0.8).
- The cross-tab row reads "births not measured" at NOT RUN points.
- W2's criterion becomes "PAYS and NONE, with retention UNDECIDED or NOT HELD where it ran". It is ranked as before.

**S3-2: the §0 table still leads with the share verdict.** The row "what falsifies" (line 40) still lists "ONE BODY
DOMINATES or EARNINGS DOMINATED …". Reorder it to income first, to match §8.

## 3. The re-costed budget

**It re-derives** (`prior_regime.txt`, r3 budget, at 20 core-s and probes 0.46).

| stage | arithmetic | total, core-h |
|---|---|---|
| Stage 1 | 36 × 8 × (1.67 + 0.46) = 613; M 12 × 8 × 1.33 = 128; N 4 × 8 × 0.57 = 18; plants 36 × 0.8 = 29 | **787** ✓ |
| 2a | 16 × 8 × 2.13 = 273; M 4 × 8 × 1.33 = 43; N 2 × 8 × 0.57 = 9; plants 13 | **337** ✓ |
| 2b | 20 × 8 × 2.13 = 341; M 6 × 8 × 1.33 = 64; N 2 × 8 × 0.57 = 9 | **414** ✓ |
| retention | 12 × 2 × 8 × 1.67 = 321; validation 12 × 0.3 ≈ 4; the matched-erosion re-read 2 faunas × 2 arms × 8 × 1.67 = 53 | **378** ✓ |
| with the pilot (77) and the census (195) | | **2,186** ✓ |

- At probes 0.83 the total is 2,405. At 25 core-s it is 2,641–2,860.
- The wall time, 55–72 h on 40 cores, follows.
- The stated saving over r2 (2,243–2,931) is modest, as expected: most of the demoted share layer's savings went into
  the retention controls, as ruled.

**Small items not costed (SHOULD):**
- **S3-3: the retention layer's behavioural confirmation.** It probes 20 R_sel and 20 R_marker members per seed at K3's
  bars. That is about 40 × 60–75 solo seasons × 0.35 s, or 0.23–0.29 core-h a seed. Over 12 × 8 seeds, plus the re-read
  point, that is **+25–30 core-h**.
- **S3-4: the anchor fallback.** It is 46 core-h, or 57 at 25 core-s, if RBT-118 does not adopt the seed coordination.
  It is described in §9.1 but not listed in §11.2's "optional" row. Add it there, since §11.1 makes the fallback a
  gate alternative.
- **S3-5, a possible saving.** R_sel and R_marker are "the point's S arm" with one fauna planted, so each runs both
  ecologies. The unplanted fauna in those arms is a duplicate of S. Running only the planted fauna's ecology would
  roughly halve the retention cost, saving about 150 core-h. The saving is about 0.45 of the arm, since the holistic
  bouts cost about 0.85 of the designed.

**Net:** at most +30 core-h uncosted, and an optional −150 core-h. No budget conclusion changes.

## 4. r3's open items

1. **The anchors from RBT-118 as a gate alternative:** yes, the gate is the right place. Also add the 46 core-h
   fallback to §11.2 (S3-4).
2. **R_marker's lesion at L points:** it is moot while retention is registered at G points only. Say so in §6.4.
3. **VARIANCE-DRIVEN's fit has 5 residual df:** it is acceptable as a conservative flag. It is a flag, not a call.
4. **MARGINAL's bar:** keep the living cost, 0.25. Per-birth income includes children who die young, and the flag
   exists to mark where the flow is compressed. A strict bar errs toward flagging, which is the safe direction for a
   flag that does not remove calls.
5. **CONTINGENT callable only with RBT-118's nulls:** acceptable. Under shuffle it fires at 0.01–0.03 in any case, so
   little is lost if it is never callable.

## 5. The list

**MUST**
- **R3-M1:** remove the share-TIE route from WORLD-INVARIANT, or give it a floor of ≥ 6 RESOLVING points.
- **R3-M2:** DEPENDS ONLY THROUGH HABITABILITY is based on income only. Share WINs may only veto it.

**SHOULD**
- **S3-1:** split SATURATED into measured and NOT RUN, in §6.3's cross-tab and in W2's criterion.
- **S3-2:** reorder the §0 table row to income first.
- **S3-3:** cost the retention confirmation probes (+25–30 core-h).
- **S3-4:** list the anchor fallback in §11.2's optional row.
- **S3-5:** optionally, run the retention arms with only the planted fauna's ecology (about −150 core-h).

With R3-M1 and R3-M2 fixed, the design is ready to register once its §11.1 gates are met.

---
_Generated by [Claude Code](https://claude.ai/code)_
