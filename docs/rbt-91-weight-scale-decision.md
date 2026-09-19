# RBT-91: the weight-scale ceiling — decision

**Decision: option A. The operator is left as it is, and the held-out challenge protocol must
state that challenges are unperceived.**

The ceiling is the mutation operator's own stationary distribution, and it is neither a clamp
nor selection. `genetics.mutate_weights` applies **no bound to `link.weight` at all** — a
touched weight is redrawn from `N(0, 1)` with probability 0.02 or takes an `N(0, 0.4)` step
otherwise, and neither branch clips, while `freq` and `dims` are clipped in the same file, so
the absence is deliberate. Selection is not holding the weights down either: over the 8,884
links on the 120 committed bests the largest `|weight|` is **4.606** and none reaches 8, and
running those same genotypes forward under `mutate_weights` alone, with nothing selecting, gives
max 4.7 at depth 10 and 5.0 at depth 20 — the runs' realised depth — with **0.00% at or above 8
either way**. What binds is the step against the reset: with `P(step) = 0.245` and
`P(reset) = 0.005` per weight per mutation, the walk equilibrates at a variance of
`1 + σ²·P(step)/P(reset) = 8.84`, rms **2.94**, and the measured asymptote agrees (rms 2.938
after 20,000 mutations, against 2.97 predicted). **That is a ceiling no amount of running
removes**: at infinite time only **1.96%** of weights reach 8, **0.03%** reach 16 and **0.00%**
reach 32, where a compass is **null** at `a = 16` (+0.054, CI spanning zero) and first **pays**
at `a = 32` (+0.246), with the prize still rising at `a = 384` (RBT-67, RBT-69). Since the routed
motif puts `a = 2w` on the steering axis (RBT-87), the first paying rung needs two coordinated
links at **`|w| ≥ 16`** — about `1 × 10⁻⁷` before signs even at the asymptote, and only *given* a
structure drift proposes 0 times in 10,000 (RBT-78). Option B is declined because widening the
scale changes magnitude and not correlation, so it addresses the smaller of the two barriers;
the larger one is structural and a wider scale does not touch it. Saying this plainly is also
what the programme owes itself — *"the robots cannot perceive the disruption under the current
operator; say so or change it, never both silently."*

## The numbers

| quantity | value |
|---|---|
| clamp on `link.weight` | **none** (`freq` and `dims` are clipped; weights are not) |
| operator | `weight_rate` 0.25, `weight_sigma` 0.4, `weight_reset_rate` 0.02 |
| per weight per mutation | `P(step)` 0.245, `P(reset)` 0.005 |
| committed bests (120 genotypes, 8,884 links) | max \|w\| **4.606**, p99 2.94, 0.00% ≥ 8 |
| drift only, depth 10 / 20 (the realised depth) | max **4.745 / 5.008**, 0.00% ≥ 8 |
| drift only, depth 500 | max 15.18, 1.92% ≥ 8, 0.00% ≥ 16 |
| operator asymptote (20,000 mutations) | rms **2.938**, 1.96% ≥ 8, **0.03% ≥ 16**, **0.00% ≥ 32** |
| predicted asymptote | variance 8.84, rms 2.97 |
| first paying rung (RBT-69: null at `a = 16`, pays at `a = 32`) | two coordinated links at **\|w\| ≥ 16**, i.e. the 0.03% column |

Readout: `docs/artifacts/RBT-91-weight-census.txt`; script `runs/RBT-91/weight_census.py`.

## What this decision does and does not say

It does **not** say a compass is unreachable in principle, and it does not close option B. It
says that the barrier is two barriers, that widening the weight scale removes only the smaller,
and that the programme should not pay for a substrate change and a positive control until it has
a reason to believe the structural barrier moves too.

**Corrected 2026-09-19, by the RBT-89 delegate's §3.** An earlier version of this document said a
compass "pays from `a = 16`", inherited from the ticket's "perception pays at 16–32" without being
checked against RBT-69's own table (+0.054 at `w = 8`, +0.246 at `w = 16`, +0.897 at `w = 32`,
with `a = 2w`). `a = 16` is the null; `a = 32` is the first paying rung. **The decision is
unchanged and better supported**: the requirement moves from `|w| ≥ 8`, which 1.96% of weights
reach at the asymptote, to `|w| ≥ 16`, which 0.03% reach.

**What would reopen it.** Evidence that the routed motif's *structure* is proposed at a rate
above zero under some operator — RBT-78's instrument on one denominator, measured on the routed
motif rather than the direct one it was built for. If that rate is non-zero and the only thing
missing is magnitude, option B becomes the right call and its positive control becomes worth
running. That measurement is not this ticket's and is not assumed here.

**One caveat against this decision, stated rather than buried.** The drift null runs
`mutate_weights` from *already-evolved* genotypes, so it inherits their weight distribution; a
lineage founded differently could sit elsewhere. The asymptote argument does not depend on the
starting point — that is why it carries the decision — but the depth-10 and depth-20 rows do.

## Consequence for the held-out challenge protocol (RBT-89)

"Robust against novel challenges" means **survivorship of standing morphology and gait through
a shift**, not adaptation during it. The protocol should say so in those words, and its
pre-registered axis and falsifier should be written so that neither can be read as a claim about
perception. This is faithful to Gould, whose events select on what is already there; it is a
narrower claim than the owner's goal states, and the narrowing is real and should be visible
rather than absorbed.
