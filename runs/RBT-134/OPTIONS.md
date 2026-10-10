# RBT-134: options for the owner after the control-gate ESCALATE

**Status.** Lane A stopped at the control gate. The diagnosis registered in `GATE-FAILURE.md` r2, run on the owner's
approval, returned **C+-BG**. That is an ESCALATE category. Under r2:

- no control re-run follows;
- no r4 change to the background clause is allowed;
- the Pioneer stage stands **VOID** as registered.

The diagnosis then stopped, as the GO required. So the sham check (I5) was never given a category. P1–P5 never ran, and
the family remains unseen by anyone.

**Numbers.** This note quotes only two, each marked **[number]**, because the decision turns on them. The full working
is on `claude/rbt134-diagnosis` (no PR).

## 1. What C+-BG means, in plain words

C+ is the positive control. It plants the paying motif directly through a "pair event": a new unit wired from the two
food noses to the two wheel Effectors, with links about 16× normal size. To PASS, it had to do two things.

**1. The instrument must detect the planted motif at the paying rung.** It did, overwhelmingly. Thousands of C+
lineages carried a motif reading at or above a = 32 **[number: k in the thousands, against the 6 required]**. So the
pipeline can see a paying motif when one is there.

**2. The background clause must hold.** Among lineages that do *not* carry the motif, C+'s whole-brain gain must not run
more than 2× above B0's, judged on a one-sided 95% upper bound. It did not hold: the upper bound of the ratio was about
3.2 **[number: Katz upper bound 3.244, against a limit of 2]**. The pair event raised gain outside the motif as well as
inside it.

**The likely mechanism.** This is a hypothesis, not established, because establishing it would mean regenerating C+
lineages, which r2 did not permit. A lineage counts as "structureless" when it fails the predicate *now*. Later mutations
can break a planted motif by removing one link or flipping one sign, while leaving a large-weight unit wired between the
noses and the Effectors. That remnant carries large whole-brain gain into the background count.

DESIGN.md's N6 expected C+'s background to be mostly event-free default lineages. That is still true of most lineages,
but a modest number of high-gain remnants is enough to move a background rate of a few tenths of a percent (B0's
committed rate, DESIGN §6.4).

**Why this matters beyond C+.** If the mechanism is right, the background clause penalises the **remnants of a working
motif** as though they were whole-brain gain. Any operator that really does make large circuit gains would then risk
failing the clause too. That would make the clause hard to pass for exactly the candidates it was meant to certify. The
current instrument therefore cannot show that a real candidate can PASS.

## 2. The options

| | option | cost | what it would tell us | what it would not |
|---|---|---|---|---|
| **(a)** | **Close RBT-134 as VOID and write it up** | writing only; 0 CPU-h | A methodological result: the registered Pioneer instrument cannot certify a PASS, because its positive control fails the background clause. It also gives the C+-BG mechanism as a hypothesis, and the open sham question (I5). | Anything about whether the operator switches make drift propose paying compasses: P1–P5 never ran. |
| **(b)** | **A new pre-registration, RBT-134b**, with a redesigned positive control and/or background clause | design and adversary rounds (agent-days); about 1 CPU-h to settle I5 (§2.c3); up to about 5 CPU-h of held-out validation; about 10 CPU-h for lane A, plus up to 5 for re-signing (DESIGN §12); about 20 CPU-h in all | If the new controls pass, a registered verdict on P2 and P3 under a clause that separates motif remnants from whole-brain gain. | Nothing if the redesign fails its own controls. There is also a forking-path risk, discussed below. |
| **(c1)** | **Settle I5 now**, by finishing the registered diagnosis's two B0 regenerations (I5-2, I5-3) | about 1 CPU-h; already registered in r2 §4 and approved, and stopped only by the ESCALATE rule; B0 lineages only | Whether the sham's departure from the food count comes from parent asymmetry (I5-A), noise (I5-B), or a code fault (I5-C). The diagnosis saw the departure: B0's sham count is well below its food count **[direction only]**. | Nothing about the operators. |
| **(c2)** | **Run the family now, descriptively**: P1–P5 under the current scripts, with no registered verdict | about 6 CPU-h, plus up to 5 for re-signing | P2's and P3's k counts: whether wide links make paying motifs at all, which is the first half of the question. | It cannot give a registered PASS, and it **spends the family's blindness**: any later RBT-134b would be designed knowing P2's and P3's outcomes. **Not recommended**, unless the owner prefers a descriptive answer now to a registered test later. |

**On (b): how blind it can still be.**

- **Still blind:** every family and check condition (P1–P5). Nobody has seen them, so a redesign of the clause stays
  blind to the outcome it will judge.
- **Not blind:** the designer of this note has seen the control numbers (C+'s k and background, and the sham counts).
- **Mitigations:**
  1. RBT-134b's controls are designed in a fresh session that has never read `claude/rbt134-diagnosis`. This session
     would act only as a reviewer.
  2. Every new control is validated on held-out seeds (as in r2 §3.4, e.g. `MASTER_SEED 20261011`) before
     registration.
  3. The family keeps its registered seed, so P2 stays paired with RBT-91's committed σ = 4.0 lineages.
- **Directions such a design could take (a sketch, not a proposal):**
  - **Remnant-proof background.** Measure whole-brain gain with every unit that has in-links from both food noses
    silenced, or exclude such "partial-motif" lineages from the background.
  - **A remnant-free positive control.** Run the event only at the last mutation step, so that nothing can break it.
  - **A separate negative control for the clause itself.** For example, a whole-brain-only widening that must fail it.

**My recommendation.** Do **(c1)** first. It is cheap and already approved, and it completes the account of the gate.
Then choose between (a) and (b). I would choose **(b)** if the owner still wants the operator question answered, since
the family is untouched. I would choose **(a)** if RBT-134's budget is better spent elsewhere. I recommend against
(c2).

## 3. Lane B (E1, E2, H1): read now, or keep sealed?

**They are separate instruments.** They are not guarded by I4 or I5, which are the Pioneer assay's controls, so the
Pioneer VOID does not invalidate them.

- E1 (structural erosion) is tied into I2's stream-identity check.
- E1 and E2 each carry their own B0 reproduction token in lane B's RELAY: `E1-B0-equals-parity.txt` and
  `E2-B0-equals-RBT-112-tables`.
- H1 has its own registered rule, STRUCTURE-BOUND per arm (DESIGN §5.2).

If lane B's tokens are YES, its outputs are valid as measured.

**But reading them is not neutral.** Their non-B0 rows are data on P1–P5:

- E1 and E2 show how much each switch erodes.
- **H1 counts arrivals per condition on the holistic fauna.** That is a sibling of the primary question.

**So it depends on the choice above:**

- **Under (a):** lane B can be unsealed and reported as independent, descriptive results: the costs of switches whose
  benefit was never established, and the holistic census.
- **Under (b):** keep lane B sealed until RBT-134b is registered. Reading H1 in particular, or even E1 and E2, before
  then would let operator outcomes inform the redesign. That is the one blindness (b) still has. After registration,
  lane B can be read as pre-registered (H1's rule) or descriptive (E1, E2) results.
- **Until the owner chooses:** keep it sealed. Nothing is lost by waiting, since the outputs are committed.
