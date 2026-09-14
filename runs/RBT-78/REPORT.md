# RBT-78: the direct route and the path route, on one denominator

`runs/RBT-78/reconcile.py`, readout `docs/runs/RBT-78-reconcile.txt`. The script also writes
`runs/RBT-78/reconcile.json`, which RBT-68's rule correctly classes as bulk and leaves untracked —
it is derived, and the committed readout carries every number quoted here.
10,000 drift lineages (2 pools × 5,000), 19 mutations each, `add=0.15 rem=0.1`, master seed
20260912 — RBT-45's, so the drift process is the same one. No world, no selection, no
simulation, no library changes.

## The one sentence, for papers 5 and 7

> RBT-62 and RBT-45 are both correct and count different routes — a **direct** four-link motif
> never arrives (0 of 10,000 lineages, max `|a| = 3.3`, consistent with RBT-62's 10⁻⁷⁷), and
> RBT-45's 0.70% is a depth-4 path sum carried essentially entirely by indirect routes through
> the global brain (median indirect share **1.000**) — **but that path quantity is not a compass
> arrival rate**: an information-free control sensor pair clears the same thresholds at
> 50–100% of the food noses' rate, the magnitude grows geometrically with depth, and the rate
> that could actually mean "drift proposed a compass" is **0.06–0.12%** at `a ≥ 32` and
> **0.00–0.02%** at the `a ≥ 64` that pays +0.897 items.

## Verdict on the reconciliation: it holds, and it is not the whole story

**P1 (pre-registered, confidence 0.85) — confirmed.** The direct route never arrives.

| pool | direct max &#124;a&#124; | direct `a≥16` | direct `a≥32` | direct `a≥64` |
|---|---|---|---|---|
| W4b-801 bests | 3.232 | **0.00%** | **0.00%** | **0.00%** |
| P-801 final 60 | 3.333 | **0.00%** | **0.00%** | **0.00%** |

Not one lineage in ten thousand gets a direct-link `|a|` even a fifth of the way to the inert
boundary. RBT-62's figure is not merely defensible, it is if anything conservative about how
unreachable the direct route is.

**P2 (confidence 0.75) — confirmed, more strongly than predicted.** I predicted a median
indirect share above 80%; it is **1.000** in both pools, with 100% of clearing lineages
majority-indirect. Median `|direct component|` among lineages clearing `|a| ≥ 16` is 0.197 and
0.344 — the direct term contributes essentially nothing. (Shares slightly exceeding 1.0, to
1.083, are lineages where direct and indirect carry opposite signs.)

**RBT-45's rate reproduces.** Signed `a ≥ 32`: **0.44%** (W4b bests) and **0.36%** (P-801 final
60) against its reported 0.70%, on the same cell and seed. Signed `a ≥ 64`: 0.02% both, against
its 0.05%. Same order on both available pools — the first independent reproduction of that
number, and it survives.

## P3 (confidence 0.5) — confirmed, and it is the finding that matters

I flagged that the path quantity might be measuring network gain rather than compass arrival.
Two tests, both decisive.

**Control: the same maths on a sensor pair with no food gradient.** The `agent` smell sensors
sit on the same two wheel parts as the food noses, so the computation is structurally identical
and points at a pathway that has nothing to do with food.

**The raw comparison is confounded and I corrected it.** I flagged in the first version of this
report that I had not checked whether the mutation operator treats the two pairs alike. It does
not: the evolved parents already carry more food-nose wiring, so the food pathway has any
outgoing link in **69.5%** of lineages against the agent pair's **52.8%** (W4b) and 59.6% against
52.9% (P-801). Part of the raw gap was simply that.

Conditioning on the pathway being wired at all — the matched comparison:

| pool | | `|a|≥16` | `|a|≥32` | `|a|≥64` |
|---|---|---|---|---|
| W4b-801 bests | food noses | 3.71% | 1.09% | 0.14% |
| | **agent control** | **3.63%** | **1.02%** | **0.19%** |
| P-801 final 60 | food noses | 3.29% | 1.04% | 0.20% |
| | **agent control** | **2.42%** | **0.45%** | **0.19%** |

On **the ticket's own population the control is indistinguishable from the food pathway at every
threshold**, and slightly *higher* at `|a| ≥ 64`. On P-801 the food pathway keeps an advantage at
`|a| ≥ 32` (1.04% against 0.45%) but none at `|a| ≥ 64` (0.20% against 0.19%).

This is a stronger result than the raw comparison, not a weaker one: once the wiring rate is
matched, the path statistic is largely — on W4b entirely — indifferent to which sensor pair it
is pointed at.

**Where the magnitude comes from.** Max `|a|` by path depth: **3.2 → 7.2 → 31.5 → 91.8**
(W4b) and **3.3 → 10.4 → 30.3 → 115.6** (P-801), roughly ×2.8 per link. The global brain is
fully recurrent, so `M⁴` grows geometrically for reasons that have no nose in them. The large
values are manufactured by depth.

**The rate that could mean a compass.** Requiring correct sign, magnitude, *and* the gradient
term beating the common-mode term in the same individual (`a ≥ t` and `|a| > |c|` — the
distinction `steering_gain.py` exists to draw):

| pool | `a≥16` | `a≥32` | `a≥64` |
|---|---|---|---|
| W4b-801 bests | 0.28% | **0.12%** | **0.00%** |
| P-801 final 60 | 0.22% | **0.06%** | **0.02%** |

Against RBT-45's headline 0.70%, that is **6–12× lower** at `a ≥ 32`, and at the `a ≥ 64` that
actually buys +0.897 items it rounds to zero. Only 24/129 and 21/98 of the clearing lineages are
gradient-dominant at all; the other ~80% are pirouettes with a gradient term attached.

`motif.py` already calls its own thresholds "a permissive upper bound on reachability" and
reports a `_dominant` column. This quantifies how permissive: about an order of magnitude, and
the headline 0.70% quoted downstream is the permissive number, not the dominant one.

## Calibration (rule III), run before anything was measured

Five round-trips, all passing, printed at the head of every run:

```
antisymmetric w=1  -> a=2.0  c=0.0     (expect a=2,  c=0)
antisymmetric w=8  -> a=16.0 c=0.0     (expect a=16, c=0)
antisymmetric w=32 -> a=64.0 c=0.0     (expect a=64, c=0)
single wired nose  -> |a|=5.0 = |c|=5.0
indirect 2-link    -> direct a=0.0, path a=15.0   (expect 0 and 15)
```

The last one is the instrument for this ticket's actual question: it shows DIRECT blind to an
indirect route and PATH seeing it, on an input whose answer is known by construction. The motif
is built through `fixed.drive_commands()` rather than by hand, with an assertion that it still
puts a pure steering term on both effectors.

**Rule II arrows.** Frame: n/a, file analysis only — stated, not skipped. Calibrate: yes, above,
and first, because P1 predicted a null. Manipulation check: n/a, nothing installed in a world.
Effect: the tables above.

## A third convention difference, not in the ticket

`motif.py` thresholds on **signed** `a >= t`; `steering_gain.py` reports `|a|`. The two differ
by about 2× by symmetry. Both are reported here so the numbers are directly comparable to either
source table; the signed column is the one to compare against RBT-45's.

## Deviations from the package, and why

**The requested pool does not exist.** `runs/RBT-23/W4b-801` is committed on no branch. Both
`motif.py` and `reach.py` hard-code it and call `_parent_pool`, so **neither can be run as
written from a fresh checkout** — RBT-68's failure mode, blocking its own reconciliation ticket.
Regenerating the final 60 needs a 600-season run, which this package forbids. So:

- **Pool A** — the 7 W4b-801 bests committed on PR #5, copied to this branch (`config.json` and
  the seven genotypes only, 200K, byte-identical to #5 so the merge is clean) so that this
  result is reproducible standalone, per rule V.
- **Pool B** — `runs/RBT-19/P-801/conventional/final/`, a genuine final 60 on the integration
  branch. Right shape, wrong run.

Neither is the requested pool; both give the same answer on every question here, which is the
main reason I am willing to report rather than hold. If the real final 60 surfaces, the run is
one command.

## What I would attack if I were the adversary

- **The control was confounded and is now matched.** The two pairs are *not* wired at the same
  rate (69.5% against 52.8%), which I flagged as unchecked and then checked; the matched
  comparison above is the one to read, and it strengthens the conclusion. What remains unchecked
  is whether "has at least one outgoing link" is the right matching variable — number of links,
  or their weight, might matter more.
- **`|a| > |c|` is itself a summary** and could be collapsing something, exactly as this
  programme keeps discovering. It is the criterion `steering_gain.py` already uses, which makes
  it consistent, not necessarily right.
- **Everything here is a linearisation.** tanh only attenuates, so all of it is an upper bound,
  and the gap between a path-sum `a` and a realised steering gain is not measured here at all.
- **Two pools, neither the requested one.** The agreement between them is reassuring, not
  conclusive.

## Reproduce

```
python runs/RBT-78/reconcile.py --n 5000 --workers 4     # ~30 s
```
