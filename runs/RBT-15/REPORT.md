# RBT-15 — W3, long seasons: 60 s seasons at 6 items, basal cost 1.0 (seed 801)

**Outcome: both populations went extinct within six seasons. The wheeled side died out at season 4, the holistic side at season 6, and the run ended on its own ("everyone died"). No tuning, no flag changes; the run is `runs/RBT-15/W3-801`, config as specified (`--duration 60 --food-items 6 --living-cost 1.0`, work cost 0.03, initial energy 3, birth at 3, birth cost 1, capacity 60, groups of four, random terrain and starts, seed 801, 3 workers).** Wall time was under three minutes, so nothing was stopped early.

The pre-registered readout (heritability, founders at season 599, probes at 100/300/590) is mostly unmeasurable: there were 15 births in total, no child was ever evaluated five times, and the only saved bests are the season-0 ones. Everything below is what the run can say.

## 1. Ecology readout (`rabbitstew history`)

| season | holistic alive | births | deaths | mean lifetime score | wheeled alive | births | deaths | mean lifetime score |
|---|---|---|---|---|---|---|---|---|
| 0 | 55 | 0 | 5 | −0.03 | 40 | 5 | 25 | −0.49 |
| 1 | 53 | 0 | 2 | +0.02 | 16 | 4 | 28 | +0.88 |
| 2 | 6 | 0 | 47 | +0.29 | 7 | 1 | 10 | +0.88 |
| 3 | 2 | 1 | 5 | +0.60 | 1 | 0 | 6 | +0.93 |
| 4 | 1 | 0 | 1 | +0.90 | 0 | 0 | 1 | extinct |
| 5 | 1 | 0 | 0 | +0.70 | | | | |
| 6 | 0 | 0 | 1 | extinct | | | | |

"Lifetime score" is the ecology's per-season score, food eaten minus 0.03 per kJ of work, averaged over an individual's evaluations; the basal cost of 1.0 per season comes off on top of it. Seasons 11, 20, 32, 60, 100 … 599 do not exist.

**Bottleneck.** As the ticket anticipated, founders start with 3 energy against a basal cost of 1.0, so a founder that nets nothing is dead after its third season. That is season 2 in the run's zero-based numbering (the baseline's season-11 cliff is the same event at 12 seasons of 0.25): 47 of 53 holistic founders starved together at season 2. Of the 55 holistic founders evaluated at season 0, 4% ate anything at all (median season score 0.00, best 0.97), and not one covered the basal cost of 1.0. The six that came through the cliff had eaten once or twice by luck; the best of them (h0-59, mean +0.92 a season, still net −0.08 after basal) died at season 3, the last one (h0-52, one season of +4.70 among five of about −0.3) bred once at season 3 and starved at season 6; its child died in its first season. There was no recovery, no season at which holistic mean gain exceeded wheeled while both were alive, and no first season of positive net budget for any lineage.

**The wheeled side died faster, of the work cost.** A random-weight Pioneer spends roughly four times the actuator work it spent in a 15 s season, about 2 energy per 60 s at 0.03 per kJ, so a season with fewer than three items eaten is a loss before the basal cost. At season 0 the wheeled founders' net-of-work score had mean −0.55 and median −1.12; 29% were positive and 14% covered the basal cost. 25 died at season 0 and 28 at season 1. The ten wheeled births were all to founders with one or two good seasons (c0-2: +3.16, +2.89, then −0.95; c0-57: +3.73 then −1.49; ce65, a child, +5.58 then −1.55). A newborn Pioneer starts with 1 energy and must net +0 in its first 60 s, i.e. eat about three items, or die: four of the five children evaluated did. The last Pioneer (c0-7, mean +0.93) died at season 4.

Deaths at seasons 0 and 1 also include founders that started near the 60-season age limit (ages are staggered over 0–59 at season 0); one holistic death at season 3 was by age.

## 2. Founders at the last season with survivors

```
holistic     last season 5  {'founders': 1, 'of': 1}   ['h0-52']
conventional last season 3  {'founders': 1, 'of': 1}   ['c0-7']
```
Trivially one of one on each side: the last individual alive was itself a founder. `<kind>/final/` is empty because both populations were empty at the end.

## 3. Yield heritability (the point of the arm)

Pearson r between a child's lifetime mean yield and its parents' mean, evals ≥ 5 on both sides (`runs/RBT-15/heritability.py`):

```
holistic     evals>=5: n=0 children, r=None   (individuals with >=5 evals: 1 of 56)
conventional evals>=5: n=0 children, r=None   (individuals with >=5 evals: 0 of 45)
```
With the threshold dropped to one evaluation there are 2 wheeled parent–child pairs and 0 holistic; the repo's `realised_heritability` (no threshold, children with zero evaluations counted at fitness 0) gives r = −0.11 over n = 10 wheeled children, which is noise from ten first-season deaths. **The pre-registered comparison against the baseline 0.51 cannot be made: heritability is undefined in this arm because there were no lineages.**

## 4. Probes (`scripts/forage_probe.py runs/RBT-15/W3-801 0,100,300,590 8`, 60 s trials alone in the arena)

Only the season-0 bests exist (bests are saved every ten seasons).

```
holistic     g  0 parts  4 units  29 sensors ['oscillator', 'up']
     intact: food 0.00 disp 0.34 path 6.9 work 1.8kJ  no_food: food 0.00 disp 0.34 path 6.9 work 1.8kJ  no_env: food 0.00 disp 0.22 path 3.5 work 0.8kJ  no_local: food 0.12 disp 0.76 path 5.0 work 1.8kJ
conventional g  0 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 1.00 disp 4.45 path 33.8 work 64.4kJ  no_food: food 1.00 disp 3.86 path 16.4 work 46.3kJ  no_env: food 0.62 disp 2.12 path 22.5 work 56.0kJ  no_local: food 0.62 disp 2.12 path 22.5 work 56.0kJ
```

- **Holistic best at season 0 (h0-49, 4 parts, 29 units, sensors: oscillator and `up`; no nose):** eats nothing alone on 8 seeds intact, with its noses blanked (it has none) or with every environmental sensor blanked; no sensor matters. Silencing its local brains lets it eat 0.12 items on a longer walk. Its season-0 score of +0.97 was one item in a shared arena and not a repeatable behaviour.
- **Pioneer best at season 0 (c0-57, noses on chassis and both wheels, 24 units, fully global tanh controller):** eats 1.00 items alone in 60 s over a 34 m path on 64 kJ (work cost 1.93 energy, so net −0.93 before and −1.93 after the basal cost, which is the wheeled extinction in one line); with its noses blanked it still eats 1.00 on a shorter 16 m path, so the food sensors do not matter (0% change), while blanking every environmental sensor drops it to 0.62 (−38%, above the 25% mark): what it depends on is orientation, velocity and contact holding a driving gait, not smell. `no_food` does not halve its yield, so no wiring is reported beyond the note that its three food sensors sit on the chassis and both wheels (segments 0, 1, 2) and feed a fully global six-tanh controller (centralisation 1.0) that ignores them.

## 5. Against the baseline

| | baseline forage-801 (12 items, 15 s, basal 0.25) | this arm W3-801 (6 items, 60 s, basal 1.0) |
|---|---|---|
| holistic bottleneck | 60 → 7 at season 11, back to 60 by 32 | 60 → 6 at season 2, 2 at 3, 1 at 4–5, extinct at 6 |
| wheeled | 16 of 60 survive the founding, full thereafter | 60 → 40 → 16 → 7 → 1 → 0 at season 4 |
| holistic mean gain, seasons 100 / 300 / 500 / 599 | +1.02 / +1.19 / +1.63 / +1.41 | — (extinct) |
| wheeled mean gain, same seasons | +0.96 / +1.03 / +0.94 / +0.95 | — (extinct) |
| first season holistic mean gain > wheeled | 83 | never |
| holistic founders in the final ancestry | 1 of 60 | 1 of 1 (the last survivor) |
| yield heritability, holistic / wheeled | 0.51 / 0.24–0.39 | undefined (0 / 0 children with ≥5 evaluations) |
| sensor lesions on holistic bests | none changes yield | none changes yield (season 0 only; it eats nothing anyway) |
| chemotaxis anywhere | no | no |
| seasons run / simulated time | 600 / 2.5 h | 7 / 7 min |

## Does this variant give sensing a slope?

No, and it cannot say anything about the noise hypothesis, because the world it specifies does not bootstrap. Heritability first: the baseline's 0.51 was measured over hundreds of parent–child pairs with five or more evaluations each; this arm produced no such pair at all, so the pre-registered prediction (heritability above 0.51) is neither confirmed nor refuted. It is unmeasured. The reason is stated plainly, and it contradicts the arm's premise rather than the docs: the ticket scales the basal cost by four so that "the economy per unit of simulated time is unchanged", and it is, which means this arm is the six-item economy the docs already recorded as non-bootstrapping ("Six items": holistic starved out at season 15, wheeled bottlenecked to 11 and went extinct at 51). Quadrupling the season length does not change the yield-per-cost ratio that killed that arm; it only changes how many selection and birth events fit into the same simulated time, and there were fewer here. In simulated time the holistic extinction (6 seasons, 360 s) matches the 15 s six-item arm (15 seasons, 225 s), and the wheeled extinction came sooner (240 s against 765 s), because at 60 s a Pioneer's per-season work cost is about 2 energy, a newborn with 1 energy must eat about three items in its first season or die, and the season-to-season swing of ±3 in yield on six items (c0-2: +3.16, +2.89, −0.95) is the Poisson noise this arm was meant to shrink, undiminished as a fraction of the fixed cost. Halving the per-season noise relative to its mean does not help when the mean is below the cost line. If the question "does a longer season give sensing a slope?" is still worth asking, it has to be asked at a density where a random population lives at all: the docs place that between six and twelve items under this economy. A W3 at 12 items, 60 s and basal 1.0 (keeping food density at the baseline and changing only the season length) would isolate the season-length variable; this run confounded it with the density that the six-item arm had already shown to be fatal.

## Files

`runs/RBT-15/`: `W3-801/config.json`, `W3-801/history.json`, `W3-801/lineage.jsonl`, `W3-801/holistic/best_gen0000.json`, `W3-801/conventional/best_gen0000.json`, `W3-801.log`, `probe.txt`, `heritability.py`, `REPORT.md`. No `final/` populations (both empty), no `.traj`/`.html`.
