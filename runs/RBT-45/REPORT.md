# RBT-45 — Is a two-nose pairing ever proposed?

Measured with no world, no selection, no simulation. `Simulation` is not imported
anywhere in this package; nothing is ever kept for being better than anything else.

**The short answer.** The operator proposes a two-nose pairing readily — about one
lineage in eleven at the depth a real 600-season run actually reaches — so the
ticket's arithmetic is right and "the operator almost never proposes the wiring"
is wrong. But that is the *uncrossed* pairing. The **crossed** pairing, the one a
Braitenberg compass needs, arrives in 1.3% of realistic lineages, and the run's
observed zero is entirely consistent with that. So neither of the ticket's two
possibilities is what the measurement shows: the coordinator's third neighbour is.
Three further things came out that contradict the package, in §6.

> **Two corrections to this report, made by me after posting it (§5a, §6.5).** The
> `neighbour_links` lever I suggested in §5 does not do what I said — measured, it
> *halves* the pairing rate rather than helping. And the error bars I quoted were
> binomial on n = 2000 when the lineages are clustered on 60 parents; the honest
> ones are about 2.8× wider. Neither changes the verdict in §5; both change numbers
> that other tickets were about to be built on.

---

## 1. Setup confirmation

| | |
|---|---|
| Commit | `d66602a`, identical to `origin/claude/new-session-4cao7d` |
| Test suite | `./v/bin/pytest -q` → **159 passed in 43.96s**, all green before any work |
| Parent population | `runs/RBT-23/W4b-801/conventional/final/`, 60 genotypes, via `analysis._parent_pool` |
| Secondary population | the same run's 60 `holistic` genotypes |
| Operators | `mutate_controller` (conventional) and `mutate` (holistic), config from the run's own `config.json` |
| Master seed | **20260912**. Every lineage's generator is `default_rng(SeedSequence([20260912, crc32(cell_id), lineage_index]))`, so a cell reproduces independently of worker scheduling |
| Cost | 53 cells × 2000 lineages, 919s on 4 workers |

**Reproducibility was checked, not assumed.** The whole grid was run twice, in
separate invocations, and the two `cells.json` agree on every count in all 53
cells (`pair_count`, `half_count`, `chassis_count`, `uncrossed_count`,
`crossed_count`, `mean_links`, `mean_food_wired`): zero differing fields. The
first run's output is kept as `cells_prethreshold.json`.

**The readout was checked against the library.** `PAIR`/`HALF`/`CHASSIS` use
`analysis.sensor_influence`'s own quantity. For the crossed/uncrossed split I
needed the same sum decomposed per effector, which the library does not expose, so
`reach.py` rebuilds it — same matrix, same 3.0 clamp, same depth 4, same `live`
effector set — and asserts at startup that summing it back over effectors
reproduces `sensor_influence` unit for unit on 20 phenotypes. No library code was
changed.

**Definitions.** `wired(s)` = that sensor's influence > 0. On the Pioneer the
three `food` sensors are unit 8 (part 0, chassis) and units 12 and 16 (parts 1 and
2, the two drive wheels); indices are found from the phenotype each time, not
hardcoded. `PAIR` = both wheel noses wired. `HALF` = exactly one. `CHASSIS` = the
part-0 nose wired. `uncrossed` = each wheel nose reaches *its own* wheel's
effector; `crossed` = each reaches *the other's*. For the holistic side, where
there is no chassis and no designated left and right wheel, `PAIR` is read as
"food sensors on two or more distinct parts are wired", `CHASSIS` as "a food
sensor on the root part is wired", and crossed/uncrossed is undefined and not
reported.

---

## 2. The grid (conventional, 2000 lineages per cell, `remove_link_rate` 0.1)

Rows marked `*` are the two extra depths the real run actually reaches (§4); they
were run at the default rate only, so the rest of those rows is blank by design.

### PAIR — both wheel noses wired

| k | add=0.0 | add=0.15 | add=0.3 | add=0.6 | add=1.0 |
|---|---|---|---|---|---|
| 1 | 0.000 | 0.004 | 0.006 | 0.018 | 0.034 |
| 2 | 0.000 | 0.009 | 0.024 | 0.040 | 0.081 |
| 5 | 0.000 | 0.021 | 0.063 | 0.128 | 0.273 |
| 10 | 0.000 | 0.049 | 0.117 | 0.312 | 0.562 |
| **19** * | . | **0.091** | . | . | . |
| 20 | 0.000 | 0.107 | 0.278 | 0.571 | 0.835 |
| **23** * | . | **0.122** | . | . | . |
| 50 | 0.000 | 0.222 | 0.570 | 0.920 | 0.993 |
| 100 | 0.000 | 0.358 | 0.822 | 0.989 | 1.000 |
| 200 | 0.000 | 0.491 | 0.965 | 1.000 | 1.000 |

The `add=0.0` control is flat at 0.000 at every depth, which is what the parents
carry (§ parent baseline below). The control behaves.

### HALF — exactly one wheel nose wired

| k | add=0.0 | add=0.15 | add=0.3 | add=0.6 | add=1.0 |
|---|---|---|---|---|---|
| 1 | 0.213 | 0.237 | 0.262 | 0.302 | 0.368 |
| 2 | 0.208 | 0.253 | 0.279 | 0.367 | 0.443 |
| 5 | 0.196 | 0.315 | 0.357 | 0.485 | 0.503 |
| 10 | 0.179 | 0.357 | 0.468 | 0.484 | 0.372 |
| **19** * | . | **0.438** | . | . | . |
| 20 | 0.138 | 0.431 | 0.478 | 0.372 | 0.159 |
| **23** * | . | **0.429** | . | . | . |
| 50 | 0.040 | 0.477 | 0.368 | 0.077 | 0.007 |
| 100 | 0.002 | 0.483 | 0.170 | 0.011 | 0.000 |
| 200 | 0.000 | 0.404 | 0.035 | 0.001 | 0.000 |

HALF is non-monotonic in `add_link_rate` because it is a transit state: at high
rates lineages pass through it into PAIR. At `add=1.0, k=200`, HALF is 0.000 and
PAIR is 1.000 — everything has gone all the way through.

### CHASSIS — the reference sensor

| k | add=0.0 | add=0.15 | add=0.3 | add=0.6 | add=1.0 |
|---|---|---|---|---|---|
| 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 5 | 0.999 | 1.000 | 1.000 | 1.000 | 1.000 |
| 10 | 0.995 | 0.998 | 1.000 | 1.000 | 0.999 |
| **19** * | . | **0.993** | . | . | . |
| 20 | 0.955 | 0.991 | 0.999 | 1.000 | 0.999 |
| **23** * | . | **0.991** | . | . | . |
| 50 | 0.576 | 0.968 | 0.983 | 0.990 | 0.993 |
| 100 | 0.056 | 0.875 | 0.948 | 0.974 | 0.981 |
| 200 | 0.000 | 0.672 | 0.837 | 0.948 | 0.977 |

CHASSIS is 1.000 in the parents and stays at or above 0.99 through realistic
depth, so the measurement is reading the quantity it is meant to read. Its decay
at large `k` is the diagnostic in §6.3.

### The crossed / uncrossed split (the coordinator's addition)

**UNCROSSED** — each wheel nose reaches its own wheel:

| k | add=0.0 | add=0.15 | add=0.3 | add=0.6 | add=1.0 |
|---|---|---|---|---|---|
| 1 | 0.000 | 0.004 | 0.006 | 0.018 | 0.034 |
| 2 | 0.000 | 0.009 | 0.024 | 0.038 | 0.080 |
| 5 | 0.000 | 0.021 | 0.062 | 0.125 | 0.270 |
| 10 | 0.000 | 0.047 | 0.115 | 0.309 | 0.555 |
| **19** * | . | **0.088** | . | . | . |
| 20 | 0.000 | 0.103 | 0.274 | 0.567 | 0.833 |
| **23** * | . | **0.119** | . | . | . |
| 50 | 0.000 | 0.208 | 0.562 | 0.919 | 0.993 |
| 100 | 0.000 | 0.330 | 0.816 | 0.989 | 1.000 |
| 200 | 0.000 | 0.451 | 0.963 | 1.000 | 1.000 |

**CROSSED** — each wheel nose reaches the *other* wheel, which is the circuit that
steers up a gradient:

| k | add=0.0 | add=0.15 | add=0.3 | add=0.6 | add=1.0 |
|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.001 | 0.000 | 0.002 |
| 2 | 0.000 | 0.001 | 0.001 | 0.003 | 0.012 |
| 5 | 0.000 | 0.001 | 0.008 | 0.018 | 0.064 |
| 10 | 0.000 | 0.007 | 0.019 | 0.079 | 0.221 |
| **19** * | . | **0.013** | . | . | . |
| 20 | 0.000 | 0.013 | 0.062 | 0.242 | 0.525 |
| **23** * | . | **0.027** | . | . | . |
| 50 | 0.000 | 0.048 | 0.216 | 0.650 | 0.897 |
| 100 | 0.000 | 0.086 | 0.460 | 0.863 | 0.983 |
| 200 | 0.000 | 0.147 | 0.693 | 0.956 | 0.992 |

**PAIR is almost entirely uncrossed at every realistic depth.** At the default
operator and k=19, PAIR 0.091 splits into uncrossed 0.088 and crossed 0.013 (the
two overlap: a lineage can hold both). The coordinator's mechanism is exactly
right. `_link_sources(child, owner)` with `vocab.neighbour_links = False` — and it
is `False` in this run's config — gives a wheel's local brain only its own four
units plus the global brain's neurons (eight in a typical parent) as sources.
Nose 1 → effector 1 is one draw among twelve in one brain; nose 1 → effector 2 has no direct route at all and must
go through the global brain, which is a second draw in a second brain. The factor
of seven between uncrossed and crossed at realistic depth is that extra brain.

### Parent populations before any mutation (k = 0)

| population | n | PAIR | HALF | CHASSIS | mean food sensors wired | mean links |
|---|---|---|---|---|---|---|
| conventional | 60 | 0.000 | **0.217** | 1.000 | 1.217 | 112.2 |
| holistic | 60 | 0.000 | 0.017 | 0.000 | 0.017 | 42.8 |

### Holistic (secondary; `add=0.15`, `rem=0.1`)

| k | PAIR | HALF | CHASSIS | mean food sensors wired | mean links |
|---|---|---|---|---|---|
| 1 | 0.004 | 0.018 | 0.000 | 0.025 | 41.8 |
| 2 | 0.007 | 0.014 | 0.000 | 0.032 | 40.8 |
| 5 | 0.014 | 0.015 | 0.001 | 0.048 | 38.7 |
| 10 | 0.022 | 0.010 | 0.001 | 0.076 | 34.9 |
| 20 | 0.030 | 0.018 | 0.004 | 0.106 | 30.1 |
| 50 | 0.042 | 0.020 | 0.004 | 0.151 | 23.1 |
| 100 | 0.044 | 0.028 | 0.007 | 0.159 | 20.9 |
| 200 | 0.050 | 0.025 | 0.007 | 0.180 | 21.3 |

The holistic side is a different problem and the numbers should not be read
against the conventional ones. Its parents mostly carry **no expressed food sensor
at all** (mean food sensors wired 0.017; RBT-19 and RBT-23 both reported the
evolved lumps dropping the nose), so the operator has to grow the sensor before it
can wire it, and `mutate` is also rearranging the body under it. PAIR saturates
around 0.05 by k≈50 and stops climbing, unlike the conventional side which is
still rising at k=200.

---

## 3. The removal sweep (conventional, `add=0.15`, k = 50)

| remove_link_rate | PAIR | HALF | CHASSIS | uncrossed | crossed | mean links |
|---|---|---|---|---|---|---|
| 0.0 | 0.378 | 0.468 | 0.985 | 0.369 | 0.079 | 90.7 |
| 0.05 | 0.311 | 0.499 | 0.983 | 0.301 | 0.073 | 86.1 |
| 0.1 (default) | 0.222 | 0.477 | 0.968 | 0.208 | 0.048 | 78.4 |
| 0.2 | 0.104 | 0.399 | 0.786 | 0.074 | 0.012 | 67.4 |

Removal matters, but it is not the thing suppressing the pairing. Turning removal
off entirely only lifts PAIR at k=50 from 0.222 to 0.378 — a factor of 1.7, where
`add_link_rate` over the same span moves it from 0.222 to 0.993, a factor of 4.5.
This is the crux the ticket asked for and it answers "proposed", not "pruned":
even with *zero* pruning, drift at k=50 holds a pairing in only 38% of lineages,
because proposal is the slow step at these rates and depths.

---

## 4. Lineage depth in the real run, and the sentence this package exists to produce

`analysis.read_lineage` on `runs/RBT-23/W4b-801/lineage.jsonl`. The file holds
36000 conventional records, which are per-season snapshots of 1422 distinct
individuals; `read_lineage` keys by name and keeps each individual's last record,
so `generation == 599` picks out exactly the 60 alive at the end. All parent
references resolve; no chain stops short of a founder. `ecology._breed` applies
exactly one `mutate_controller` per reproduction event and sets
`parents[0]` to the individual the child was copied from, so depth along the chain
of first parents *is* the number of mutations that lineage underwent.

**Conventional, individuals alive at season 599 (n = 60):**

| statistic | value |
|---|---|
| **median depth** | **19** |
| **maximum depth** | **23** |
| mean | 18.8 |
| minimum | 16 |
| interquartile range | 17 – 20 |
| longest path to a founder over all ancestral routes (crossover included) | median 23, max 27 |
| shortest path to a founder over all ancestral routes | median 15, max 18 |

Holistic, for reference: median 23, max 26 (first-parent), longest-path max 31.

> **At the default operator, a conventional lineage of the realistic depth D = 19
> holds a two-nose pairing with probability p = 0.094 ± 0.008, of which
> 0.090 ± 0.008 is the uncrossed pairing and only 0.011 ± 0.002 is the crossed
> pairing a Braitenberg compass needs; at the deepest lineage in the run, D = 23,
> those become 0.113 ± 0.009, 0.108 ± 0.009 and 0.020 ± 0.003.**

Those are pooled over 10 000 lineages (five independent replicates of 2000) with a
*cluster* standard error that resamples parents rather than lineages — see §6.5,
which is why the single-cell numbers in the grid above (0.091, 0.088, 0.013 at
k = 19) carry a wider interval than their binomial `_se` fields claim.

**Six hundred seasons is nineteen mutations.** That single fact reconciles the
ticket's arithmetic with the observed zero, and it is the most consequential number
in this package. The hand calculation in §1 of the ticket computes an
*equilibrium* occupancy and is essentially right — measured PAIR is 0.491 at
k=200 and still climbing, so the true equilibrium is above the "about a third" the
arithmetic predicted. It is simply never approached. A real lineage is cut off an
order of magnitude short of it, at the point on the curve where PAIR is still
9%.

---

## 5. Which possibility is true

**Neither of the two possibilities as filed. The measurement shows the
coordinator's third neighbour: the uncrossed pairing is proposed regularly and
the crossed pairing — the only one that steers — is not.**

Taking them one at a time:

**Possibility 1 ("the arithmetic is wrong, the operator almost never proposes the
wiring") is false for the pairing as the ticket defines it, and true for the
crossed circuit.** At the default operator and realistic depth, 9.1% of lineages
hold both wheel noses wired, 182 of 2000. That is not "almost never" and the
ticket's arithmetic is vindicated. But 1.3% hold the crossed pairing, 26 of 2000,
and against that number the run's zero is unremarkable.

**Possibility 2 ("proposed regularly, and selection removes it") has its premise
confirmed but its conclusion unsupported by this measurement.** The run's zero is
not statistically below the drift prediction once the 60 saved genotypes are
counted as the number of lineages they actually are. They are not 60. Through the
full ancestry including crossover they descend from **11 distinct founders**, and
along first-parent chains they collapse to 23 distinct ancestors 5 reproduction
events back, 22 at 10 back, and 9 at 19 back (`coalescence.py`).

P(zero) is given two ways. *Homogeneous* gives every lineage the pooled p, which is
what I originally reported. *Heterogeneous* lets each lineage draw its parent first,
which is what the real run does — and since propensity varies sharply by parent
(§6.5: 21 of 60 parents never produce a crossed pairing at k = 19), by Jensen this
can only raise P(zero). The heterogeneous column is the honest one.

| metric | k | p | P(zero in 60) | P(zero in 22) | P(zero in 11) |
|---|---|---|---|---|---|
| | | | homog / **heterog** | homog / **heterog** | homog / **heterog** |
| PAIR | 19 | 0.0935 | 0.003 / **0.035** | 0.115 / **0.213** | 0.340 / **0.414** |
| PAIR | 23 | 0.1134 | 0.001 / **0.010** | 0.071 / **0.137** | 0.266 / **0.333** |
| UNCROSSED | 19 | 0.0900 | 0.004 / **0.042** | 0.126 / **0.229** | 0.354 / **0.430** |
| CROSSED | 19 | 0.0105 | 0.531 / **0.651** | 0.793 / **0.820** | 0.890 / **0.898** |
| CROSSED | 23 | 0.0195 | 0.307 / **0.491** | 0.648 / **0.709** | 0.805 / **0.825** |

At the effective lineage count the run actually has, observing no pairing at
season 599 carries p ≈ 0.21 to 0.41 for the uncrossed one and p ≈ 0.82 to 0.90 for
the crossed one. **Neither is evidence of selection removing anything**, and
accounting for parent heterogeneity makes that conclusion stronger, not weaker: even
the most generous reading, treating all 60 saved genotypes as 60 independent
lineages, puts P(zero) for the uncrossed pairing at 0.042 rather than the 0.004 I
first reported. A single
600-season run on one seed does not have the resolution to detect a per-lineage
effect of this size; it would need several independent runs, or a direct
before-and-after on the intermediate, to say that selection is doing the work.

*Per the coordinator's scope note, I have not gone on to test whether the
intermediate is harmful — that needs the world.*

**What this means for RBT-42.** Not misdirected, but aimed as filed at a target
that does not need it. Widening `add_link_rate` to get *any* two noses wired is
unnecessary; the operator already does that in about one realistic lineage in
eleven, and turning removal off entirely buys less than doubling the add rate
does. Widening it to get the **crossed** circuit proposed is a different matter
and the numbers for it are strong: at k≈20, crossed goes 0.013 → 0.062 → 0.242 →
0.525 across `add_link_rate` 0.15 → 0.3 → 0.6 → 1.0, a factor of forty. If RBT-42
proceeds it should be re-aimed at the crossed pairing and should say so in its
success criterion, because a widened operator that produces uncrossed pairs at 80%
and crossed ones at 5% would look like a success on the ticket's current wording
and be one on nothing that steers.

### 5a. Correction: the `neighbour_links` lever I proposed is wrong, and would hurt

The first version of this report suggested `vocab.neighbour_links` as a cheaper
lever than RBT-42's, on the reasoning that it "puts the crossed link one draw away
instead of two". **That is false, and I should have read `Genotype.neighbours`
before writing it rather than after.** On the Pioneer the two wheels are *siblings*,
both children of the chassis:

```
neighbours of node 0 (chassis) = [1, 2, 3]
neighbours of node 1 (wheel)   = [0]
neighbours of node 2 (wheel)   = [0]
```

A wheel's neighbours are the chassis and nothing else, so the flag never gives one
wheel's brain sight of the other wheel's units. The crossed path still routes
through the global brain: two draws in two brains, exactly as before. What the flag
*does* do is enlarge each wheel's candidate source pool from 12 to 22, which dilutes
the chance of drawing that wheel's own nose. Measured (`neighbour.py`,
`neighbour.json`; 2000 lineages per cell, same discipline):

| neighbour_links | add | k | wheel sources | PAIR | uncrossed | crossed | CHASSIS | links |
|---|---|---|---|---|---|---|---|---|
| False | 0.15 | 19 | 12.1 | 0.1030 | 0.0985 | 0.0175 | 0.995 | 96.8 |
| **True** | 0.15 | 19 | 22.1 | **0.0525** | **0.0495** | **0.0130** | 0.996 | 96.0 |
| False | 0.15 | 50 | 12.8 | 0.2375 | 0.2240 | 0.0440 | 0.961 | 77.4 |
| **True** | 0.15 | 50 | 22.9 | **0.1330** | **0.1195** | **0.0310** | 0.966 | 78.2 |
| False | 0.6 | 19 | 12.1 | 0.5640 | 0.5570 | 0.2380 | 1.000 | 120.3 |
| **True** | 0.6 | 19 | 22.1 | **0.3590** | **0.3450** | **0.1675** | 1.000 | 120.2 |
| False | 0.6 | 50 | 13.0 | 0.9150 | 0.9140 | 0.6500 | 0.990 | 137.4 |
| **True** | 0.6 | 50 | 22.9 | **0.7830** | **0.7760** | **0.5470** | 1.000 | 139.0 |

Turning the flag on roughly **halves** the pairing rate at realistic depth and
lowers the crossed rate at every cell but one (k = 23, where the two are within
noise). Mean link count is unchanged, so this is not fewer links — it is the same
links spread over a wider target set. The ratio tracks the dilution: 12/22 = 0.55
against a measured uncrossed ratio of 0.0495/0.0985 = 0.50.

**So: do not turn this flag on to chase a compass.** It is a lever in the wrong
direction. If a cheap structural lever for the crossed circuit exists, it would have
to be one that makes the two wheels visible to each other — which, on this body,
`neighbour_links` is not, because siblings are not neighbours.

---

## 6. What contradicts the ticket

### 6.1 "The static influence of both wheel noses was exactly 0.0 in every sampled best" is not true of RBT-23

It is true for *both at once* — PAIR is 0.000 in all 120 genotypes RBT-23 saved —
but it is false for the wheel noses individually, and the intermediate the entire
cliff argument is about turns out to be common and long-lived
(`evolved_wiring.py`, `evolved_wiring.json`):

| sample | n | PAIR | HALF | CHASSIS |
|---|---|---|---|---|
| bests, one every 10 seasons | 60 | 0.000 | **0.167** | 1.000 |
| final population | 60 | 0.000 | **0.217** | 1.000 |

Ten of the sixty sampled bests carry one wheel nose wired, at seasons 190, 210,
230, 310, 360, 390, 410, 550, 560 and **590**. The season-590 best — the one the
fan-out table reports on — has part-2 nose influence **0.219**, not 0.0. Season 560
reads 1.415. `docs/foraging-world.md` says of this arm "the wheel noses had
influence 0.0 for six hundred seasons"; on the saved genotypes that is wrong, and
I would rather state it flatly than reconcile it.

**This was not a new measurement.** RBT-23's own committed readout already has it.
`runs/RBT-23/wiring_590.txt`, written by that delegate, ends with:

```
=== conventional g590: parts 5 units 26 links 116 ...
   unit  8 part 0 food     influence 352.7811
   unit 12 part 1 food     influence 0.0
   unit 16 part 2 food     influence 0.219
```

and the same file's g300 block shows `unit 13 part 1 agent influence 0.5732`, a
wheel-mounted *agent* sensor wired too. The "0.0 for six hundred seasons" summary
was drawn from a file that contradicts it; the number was recorded and then
rounded away in prose. I would suggest the fan-out table's RBT-23 row and the
§"Why sensing did not evolve" sentence be corrected to "the wheel noses were never
*both* wired, and where one was, at influence below 1.5 against a chassis nose
above 200", which is what both that file and this package measure.

Two caveats that cut in opposite directions, both of which belong with the claim.
The influences are *tiny*: 0.219 and 1.415 against a chassis nose at 200–500 in the
same genotype, so these are wired in the `> 0` sense and nowhere near being read.
And on the other side: **a half-pairing is evidently not lethal.** It sits in a
fifth of the population and in a sixth of the bests, and it keeps reappearing over
four hundred seasons. Possibility 2's mechanism — "a random-weight link into a
wheel disrupts a finely tuned gait and the work cost charges for it" — predicts
that the intermediate should be scarce. At the strength these links actually
arrive at, it is not scarce, and it is not obviously being charged for either.

### 6.2 The pairing arrives far weaker than the chassis nose, and `> 0` flatters it

The `> 0` test is the ticket's, and it is the right one for comparability with the
evolved runs, but the magnitudes behind it change the reading. At k=19 and the
default rate, the pairing's strength — the weaker of the two wheel noses'
influence — has quartiles **0.37 / 0.96 / 2.38** when it is present, against a mean
chassis-nose influence of **487** in the very same genotypes. Re-reading the same
cell at stricter thresholds:

| k | PAIR > 0 | > 0.1 | > 1 | > 10 |
|---|---|---|---|---|
| 19 | 0.092 | 0.087 | 0.044 | 0.011 |
| 23 | 0.123 | 0.119 | 0.065 | 0.015 |
| 50 | 0.222 | 0.211 | 0.147 | 0.038 |
| 200 | 0.491 | 0.482 | 0.399 | 0.172 |

At the default operator and realistic depth, a pairing that is within two orders
of magnitude of the chassis nose arrives in about 1% of lineages, not 9%. Whether
"proposed" should mean "present in the graph" or "present at a strength selection
could act on" is a question this ticket does not settle and I have not answered
it; both columns are reported so the coordinator can choose.

### 6.3 The default operator is net link-destroying, so "equilibrium" is not a genotype selection would hold

Drift at the default rates takes the mean genotype link count from the evolved
**112.2** down to **96.8** at k=19, **78.4** at k=50, and **47.3** at k=200; over the
same span CHASSIS falls from 1.000 to 0.672 and the chassis-nose wiring that every
evolved Pioneer depends on is gone in a third of lineages. At `add_link_rate` 0.0
the genotype is down to 13.9 links and CHASSIS is 0.000 by k=200 — the controller
is gone.

Two consequences. The high-`k` cells are measuring the pairing rate in genotypes
that have been substantially dismantled, so they should not be read as "what a
long-lived lineage would look like"; the realistic-depth rows are the ones to
quote. And the evolved population carries **more than twice** the links the
operator's own stationary distribution would hold, which means selection in this
ecology is spending real effort holding links *in* — a fact that belongs in any
discussion of "the cost of exploration", because the operator is already pushing
downhill in link count while the ticket's framing assumes it pushes up.

### 6.4 A note on what the drift baseline is, and is not

The lineages here start from the run's *final* genotypes, not from its season-0
founders, because that is the population the ticket specifies and the one whose
zero is being explained. So p = 0.091 at k=19 is "what 19 mutations of drift do to
the run's endpoint genotypes", used as a proxy for "what 19 mutations did along a
real lineage". The two are not identical: the endpoint genotypes are converged and
carry 112 links where the founders carried fewer, and HALF is already 0.217 in
them, which is most of why PAIR appears at all by k=1 (0.004 ≈ 0.217 × 0.0125, one
further draw completing an existing half-pairing, rather than 0.0125² ≈ 0.00016 for
two links in one mutation). Starting from founders would give a different, probably
lower, number. I did not run that arm; it was not asked for and it would change
the parent population the ticket fixed.

### 6.5 Correction: my error bars were too small, by a factor of about 2.8

`reach.py` reports a `_se` field per metric, computed as `sqrt(p(1-p)/n)` with
n = 2000. **That is the wrong error bar for this design and I should not have
quoted it.** The 2000 lineages in a cell are not 2000 independent draws: every cell
cycles the same 60 parents about 33 times each, and the propensity to acquire a
pairing depends strongly on which parent a lineage started from — a crossed path
completes in a single draw if the parent's global brain already reaches both
effectors, and not at all if it does not.

I found this by accident: `neighbour.py` re-measured two cells that were already in
the published grid, under different seeds, and seven of eight metrics agreed within
1.2 binomial SE while `crossed` at k = 23 sat 2.9 SE apart. That is the kind of
outlier that is either a bug or a bad error bar, so I measured which
(`variance.py`, `variance.json`): five independent replicates of 2000 lineages at
each of three depths, with the parent index recorded, and a **cluster bootstrap that
resamples parents rather than lineages**.

| k | metric | p | binomial SE (quoted) | cluster SE (honest) | design effect | parents that never hit |
|---|---|---|---|---|---|---|
| 19 | PAIR | 0.0935 | 0.0065 | **0.0179** | 7.6 | 0/60 |
| 19 | uncrossed | 0.0900 | 0.0064 | **0.0177** | 7.7 | 0/60 |
| 19 | crossed | 0.0105 | 0.0023 | **0.0036** | 2.5 | **21/60** |
| 19 | HALF | 0.4357 | 0.0111 | **0.0315** | 8.1 | 0/60 |
| 23 | crossed | 0.0195 | 0.0031 | **0.0061** | 3.9 | **8/60** |
| 50 | PAIR | 0.2270 | 0.0094 | **0.0188** | 4.0 | 0/60 |
| 50 | crossed | 0.0430 | 0.0045 | **0.0064** | 2.0 | 0/60 |

(SEs restated for a single 2000-lineage cell. Full table for all five metrics at all
three depths in `variance.json`.)

**Design effects run from 2 to 9.** Every `_se` in `cells.json` should be multiplied
by roughly 2 to 3 before being used for anything. With the honest interval the
k = 23 `crossed` outlier falls to 1.5 SE and is unremarkable, so the grid is sound —
it was the error bar that was wrong, not the measurement.

Three consequences worth carrying forward:

1. **The verdict in §5 is unaffected and in fact strengthened.** Wider intervals and
   parent heterogeneity both raise P(zero), which was already the basis for saying
   the run's zero is not evidence of removal.
2. **The crossed rate is still robustly non-zero**, which is what RBT-46's B1 leans
   on: 0.0105 ± 0.0036 at k = 19 is about three cluster-SEs clear of zero, and 39 of
   60 parents produce at least one. That claim survives the correction.
3. **This is not specific to my package.** Any measurement on this project that
   cycles a fixed parent pool and quotes a binomial error bar is understating it the
   same way — `analysis.mutation_heritability` has the same shape. I have not audited
   anything but my own numbers, and I am not claiming any other result is wrong; I am
   saying the error term deserves the same check. It is a cheap one: record the
   parent index and bootstrap over parents.

---

## 7. Files

| file | what it is |
|---|---|
| `reach.py` | the whole measurement: grid, readout, lineage depth. `--smoke` runs a tiny version |
| `cells.json` | the raw per-cell output, 53 cells |
| `cells_prethreshold.json` | the first, independent run of the same grid — the reproducibility check |
| `evolved_wiring.py` / `evolved_wiring.json` | what RBT-23's own 60 bests and 60 final genotypes carry (§6.1) |
| `coalescence.py` / `coalescence.json` | how few independent lineages the 60 final genotypes are (§5) |
| `tables.py` / `tables.txt` | the tables above, rendered from `cells.json` |
| `stats.py` / `stats.txt` | the drift-versus-observed comparison in §5 |
| `neighbour.py` / `neighbour.json` | the `neighbour_links` lever, measured and refuted (§5a) |
| `variance.py` / `variance.json` | the cluster-bootstrap audit of my own error bars (§6.5) |
| `reach.log` | the run log |

To reproduce, from the repo root with the venv and `runs/RBT-23` in place:

```
./v/bin/python runs/RBT-45/reach.py --n 2000 --workers 4 --chunk 50   # ~15 min
./v/bin/python runs/RBT-45/evolved_wiring.py
./v/bin/python runs/RBT-45/coalescence.py
./v/bin/python runs/RBT-45/tables.py runs/RBT-45/cells.json
./v/bin/python runs/RBT-45/stats.py
./v/bin/python runs/RBT-45/neighbour.py --n 2000 --workers 4   # ~2 min  (§5a)
./v/bin/python runs/RBT-45/variance.py --reps 5 --n 2000       # ~2 min  (§6.5)
```

`reach.py` is unchanged since the first posting, so `cells.json` still reproduces
byte-for-byte; `neighbour.py` and `variance.py` import its readout rather than
editing it, and use a separate cell-id namespace so their seeds differ.
