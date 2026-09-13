<!--
PENDING. Post this verbatim as a comment on RBT-45 (mcp__Chaotic__issue_comment) when the
Chaotic connector is re-authorized. It is the only RBT-45 material not yet posted: everything
through "Correction 3" (comment 68ab190c) is already up. Do not post it twice - check for a
comment newer than 68ab190c mentioning motif.py before posting.
-->

# Correction 3, part two: the recount against the motif that actually pays

Commit `bf9d9e8`, `runs/RBT-45/motif.py`. This is the step my last comment named as the cheapest decisive one, and it needed no simulation. `reach.py` is still untouched, so `cells.json` reproduces byte-for-byte.

## What was recounted

The published grid measured the operator's reach against a 2-link "crossed" pattern which, on this body, is a spinner. This recounts the **same drift process** against the quantity that decides whether a robot actually steers:

> **k** = the **signed** coefficient on `(n₁ − n₂)` arriving at the steering axis `e₁ + e₂`, summed over every path of up to four links, with **no per-link clamp**.

That fixes all three defects in the original classifier at once: it counts the 4-link motif rather than the 2-link one, it is signed rather than `abs(w)`, and it is unclamped. The audit's dose-response sets the scale — |k| = 16 is inert (+0.054, CI straddling zero), 32 gives +0.246 items, 64 gives +0.897.

## What the evolved population carries

| | |
|---|---|
| final population, n = 60 | median \|k\| **0.000**, max \|k\| **1.415**, **0 of 60** above 16 |

## What drift proposes (2000 lineages per cell)

| add_link_rate | mutations | correct-sign k ≥ 16 | k ≥ 32 | k ≥ 64 |
|---|---|---|---|---|
| 0.15 (default) | **19 — realistic depth** | **2.95%** | 1.45% | 0.70% |
| 0.15 | 23 | 3.25% | 1.60% | 0.70% |
| 0.15 | 50 | 7.65% | 4.15% | 1.90% |
| 0.15 | 200 | 16.45% | 11.15% | 7.00% |
| 0.3 | 20 | 6.35% | 3.50% | 0.95% |
| 0.6 | 20 | 16.25% | 9.35% | 3.80% |
| 1.0 | 20 | 27.05% | 17.25% | 9.05% |
| 1.0 | 50 | 44.10% | 39.75% | 32.40% |

**Caveat stated up front:** this is a linearisation. Gain routed through neurons is attenuated by `tanh` — the audit measured per-effector gains of 0.407 and 0.197 on the shipped robots — so these fractions are a **permissive upper bound** on reachability, exact only for direct nose→effector links.

## The puzzle sharpens rather than resolves

Selection had access to a circuit worth **+59% yield**. Drift proposes the enabling gain in about **3% of realistic lineages**. The final population carries **none of it**.

Rough hazard arithmetic — roughly 0.0016 per birth across 1364 birth events — suggests the motif probably *did* appear once or twice over the 600 seasons and failed to establish. That is a different failure from "never proposed", and a more interesting one. It is not yet tested, and this recount cannot test it.

So the standing explanation for six hundred seasons of blind mowers is no longer "the world does not reward sensing" (it does, richly) nor "the search never proposes the wiring" (measured against a circuit that cannot work). It is now a claim about the search that is testable, cheap, and untested.

## What I would run next, for the coordinator

1. **The co-adaptation run.** Seed from gen 590 with the 4-link motif installed at k = 32 and let selection run a few hundred seasons. Does it *keep* it? Given ~3% proposal against 0/60 carriage, the live hypothesis is that it arrives and is lost — either to drift before it pays, or because a partially-formed version costs more than it earns. Nothing else distinguishes those.
2. **Fix the axis convention at the interface**, which I would rank above more science: a named accessor for the steering and throttle channels plus one test asserting the two wheel hinge axes are antiparallel. That would have made every error in this thread impossible, against a demonstrated four-incident history.
3. **Bound the prize** — one sweep past k = 64, about five minutes, since every positive sat at the top of its range.
4. **Do not spend RBT-42 yet.** Widening to `add_link_rate` 1.0 does lift correct-sign k ≥ 16 from 2.95% to 27%, so it works mechanically — but running it before the co-adaptation question risks discovering that the operator proposes the motif fine and selection discards it anyway.

A full write-up of the audit and everything it invalidates is staged as an RBT project document (`runs/sim-audit/CHAOTIC-DOC.md`), posted separately.

Issue stays `in_review`. I have not closed it and none of this is review.
