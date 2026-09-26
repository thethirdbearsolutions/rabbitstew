# RBT-90 part 2: the verdict, after the adversary

This is the coordinator's ruling of 2026-09-26, about 16:45 UTC.

- **Derivation:** `part2-readout.txt` (PR #118). It is unchanged, and re-derives byte for byte.
- **Adversary:** `adversary-part2/ADVERSARY.md` (PR #141). It re-derived every count from the restored bulk, and **no count changes**.
- **This file** fixes the words the programme may use for each regularity. Where the adversary showed that a pre-registered label claims more than its test can carry, the label is corrected here, and the count stands.

## The ten-seed regularities, final wording

| regularity (pre-registered) | count | final verdict and wording |
|---|---|---|
| no champion beats its own gait | 10/10 | **Holds, and it is entailed by a stronger fact:** *no champion's path responds to the food layout (10/10).* On every seed and every probed spawn, the path is identical tick for tick under two layouts (max difference 0.00e+00 m). The gait row therefore holds by construction and adds nothing beyond the layout-blindness (F1). |
| drive is not an oscillator | 10/10 | **Holds structurally:** *no champion carries an oscillator with a path to a live effector (10/10).* The `no_osc` lesion is a no-op on all ten, which is why every t is `nan`, and at n = 64 it lacks the power to contradict (F2). |
| holistic median depth in [15, 26] | 10/10 | **Relabelled: a property of this economy's demography, not of the search.** A random-parentage null lands inside the interval in 98% of replicates, and the designed fauna is inside on 10/10 (F3). |
| oscillator drive discarded / acquired | 5 / 5 | **The counts hold and are cleanly bimodal. The gloss is withdrawn.** It is *not* shown to be a founding-population property. The fate tracks which founder line won the run (3/5 against 0/5), and seed 4 acquired its oscillators entirely de novo. Wording: *"varies across runs; one run per founding population cannot separate founders from history"* (F4). |
| champion's drive kind is an effector | 5 hold, 5 unresolved | **Not decided at ten seeds.** Unchanged (F5). On 806 and 807 no sensor at all reaches a live effector: those champions are open-loop. |

The descent seam (F6): no scored regularity reads `descent.txt`, and this is confirmed by perturbation. The supplement stands as reported.

## What the programme may now say

- **Across ten diverse founding populations, the evolved champions are open-loop foragers.**
  - Their movement does not respond to where the food is, on 10/10.
  - None carries a live oscillator driving an effector, on 10/10.
  - Two have no sensor-to-effector path at all.
  - Foraging income comes from how they move, not from sensing where to go.
  - This is the strongest regularity the sweep produced, and it is the population-scale counterpart of strand 3's finding: a compass would pay (RBT-97, RBT-103), but the magnitude it needs is not reached (paper 8; causal test RBT-104).
- **Depth is set by the economy's mortality regime.** It cannot be read as evidence about selection.
- **Whether oscillator use belongs to the founding population or to the run's history is open.** The decisive test is a replicate run from the same founders with a different breeding stream (RBT-95's per-fauna streams), on the seeds nearest the boundary. It is filed as a follow-up.

## Caveat carried forward

All ten champions were read on one shared block of real layouts (F1). Per-draw differences correlate across champions (mean r +0.131). So "10/10" on the gait row is not ten independent readings. This does not affect the layout-blindness finding, which is exact per champion.
