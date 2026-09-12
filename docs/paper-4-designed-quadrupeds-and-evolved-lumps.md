# Designed Quadrupeds and Evolved Lumps

*Fourth paper in the Rabbitstew series. Placeholder: the GA capacity tests. Filled when the solo and re-evolution runs complete.*

## Questions

1. With the opponent removed and fitness set to reaching and holding a goal on random terrain, does the search find locomotion at all, and how fast?
2. Is a hand-designed quadruped, driven by controller evolution alone, easier or harder to make walk than a body the search designs for itself?
3. Does a controller re-evolved from scratch on an evolved champion's body match the native controller, or was the native pair co-adapted?

## Runs

- `solo/cap-401`, `solo/cap-402`: both populations on solo time-at-target fitness for 200 generations, random terrain, random starts, rich brains, equal mass, the designed body a quadruped with position servos, joint-angle and contact sensors on every segment, two oscillators and eight hidden neurons.
- `reevolve/rich201-body`: fresh controllers evolved for 60 generations on the body of the rich-brain random-terrain champion of seed 201, same solo task.

## Interim findings (to be superseded by the final runs)

**The first capacity runs found nothing, and looked as if they had.** Under solo fitness with start headings drawn up to 135° off the goal and two draws per generation, the reported best-of-generation score climbed to about 0.4 within thirty generations in both seeds. Re-evaluated on twelve fresh draws, the same champions scored 0.01 to 0.09 at every generation, for the evolved bodies and for the quadruped alike. The reported curve was a winner's curse: the best of twenty members on two draws is whoever the layout favoured, and with new draws every generation nothing accumulated. A body that only moves forward gains nothing on average when it may face away from the goal, so the progress term averaged to zero and selection had no signal. The steering requirement bit before locomotion existed.

Two changes follow, both now in the simulator: a heading curriculum, under which starts face the goal at first and the offset widens over the first hundred generations, and four draws per generation instead of two. The capacity runs were restarted with both. Every capability number in this series is now reported on fresh, fixed draws, never on the training draws.

**The competitive champion's body is bad at competence with any brain.** On twenty fresh solo draws the rich-brain random-terrain champion scores 0.02 with its native brain and 0.07 with a controller re-evolved on its body for sixty generations, while a random body evolved for the same sixty generations under solo fitness scores 0.30. Whatever competition selected for, it was not the ability to reach and hold a goal, and the body it produced is not a good substrate for learning that ability afterwards.

## What the evolved brains do: situated, local, and never coordinated

Nine holistic bests, one per run, were evaluated on eight fresh terrain and start draws intact and under four lesions: environmental sensors blanked, oscillators blanked, the global brain silenced, the local brains silenced (effectors keep their bias). Progress is metres towards the goal; time at target is the fraction of the bout within the target radius.

| Best | Units (global/local, parts) | Reflex arcs | Env-driven effectors | Intact | No env sensors | No global | No local |
|---|---|---|---|---|---|---|---|
| A-301 final (steers) | 32 (12/20, 2) | 1 | 1 of 3 | +0.81 m, 0.46 | +0.08, 0.00 | +0.81, 0.46 | +0.08, 0.00 |
| A-302 final | 59 (11/48, 5) | 0 | 0 of 4 | +0.03, 0.00 | same | same | same |
| C-301 gen 60, end of solo phase | 50 (6/44, 4) | 8 | 6 of 6 | +0.70, 0.35 | +0.27, 0.00 | +0.70, 0.35 | +0.27, 0.00 |
| C-301 gen 100, competitive | 59 (7/52, 4) | 4 | 4 of 4 | +0.16, 0.00 | same | same | same |
| cap-401 gen 25, solo curriculum | 10 (3/7, 2) | 6 | 2 of 2 | +0.47, 0.08 | +0.17, 0.03 | +0.47, 0.08 | +0.07, 0.00 |
| cap-402 gen 25, solo curriculum | 42 (4/38, 9) | 6 | 4 of 5 | +0.11, 0.00 | +0.11, 0.00 | +0.18, 0.06 | +0.19, 0.01 |
| random/rich-201 final (competitive) | 159 (11/148, 14) | 13 | 14 of 24 | +0.43, 0.00 | +0.52, 0.03 | +0.02, 0.00 | +0.83, 0.88 |
| random/paper-201 final (paper brain) | 69 (11/58, 6) | 2 | 0 of 16 | +0.89, 0.18 | same | same | same |
| flat/rich-202 final (competitive) | 170 (9/161, 16) | 0 | 0 of 38 | +0.55, 0.00 | +0.55, 0.00 | +0.00, 0.00 | +0.00, 0.00 |

**Situated behaviour appeared only where the task demanded it.** The three bests whose score depends on their sensors (A-301, C-301 at the end of its solo phase, cap-401) are the three evolved under a solo goal at a random bearing. Their competence is closed-loop: blank the environmental sensors and each becomes a lump. The champions of the competitive runs are open-loop. The paper-brain champion drives sixteen effectors on constant bias and no lesion changes anything; the flat-ground rich-brain champion has thirty-eight live effectors, none reads a sensor, and silencing either brain kills it only because its constant drive passes through neurons. The random-terrain rich-brain champion is the perverse case: it carries fourteen sensor-driven effectors and thirteen reflex arcs, and silencing all of its local brains raises its fresh-draw time at target from 0.00 to 0.88. Under the old task, its sensing was actively harmful to competence and selection never noticed.

**The work is always local, and the central brain is always inert.** In every best whose brain matters, silencing the global brain changes nothing, and silencing the local brains removes the behaviour. The one exception is the random-terrain champion, whose global brain supplies the constant drive that its local brains then disrupt. Sims' global brain, in this encoding, evolved into a passenger in all nine runs. The competent controllers are reflex arcs: a sensor in a segment wired to a torque effector in the same segment through zero to two neurons. A-301's whole competence is one such arc, from the target direction's vertical component in the second part's own frame to a torque in that part; because the part rolls as the body moves, the local frame turns a bearing into a signal, which is an embodied trick no designer wrote. C-301 at generation 60 is the most distributed: eight arcs across four parts, all six live effectors sensor-driven, and forty generations of competition later the arcs are still in the genome and the behaviour is gone.

**No evolved brain has a single link between two parts.** Across all nine bests the count of links joining the local brains of different parts is zero. This is partly the encoding: as written, a local brain may read its own units and the global brain's, and only the global brain may read every part, so coordination between parts can only route through the global brain, which never evolved to do it. Sims' segments could also read their parent's and children's neurons directly, which is how his creatures propagated waves down chains without a hub. Where our creatures coordinate parts at all, they do it through the body, by physics, which is Braitenberg's downhill synthesis and also its ceiling: no evolved controller here holds state, uses proprioception (joint angle and velocity are in the vocabulary and their measured influence is zero in every best), or meets Beer's bar of behaviour that depends on sensorimotor history. Neighbour links are being added to the encoding as an option so that the next runs can express distributed control the way Sims' could.

## Results

(capacity runs v2 with the heading curriculum, in progress)

**Seed 401 at generation 40 of 200.** Fresh-draw time at target on twelve draws the run never saw, at the full heading range although the curriculum has only reached forty percent of it: the evolved population's best rose from 0.00 through 0.09 at generation 30 to 0.16 at 40; the designed quadruped's best, with controller evolution alone, went 0.00, 0.04, 0.09, 0.00, 0.06. Early and one seed, but at this point the lump is ahead of the designed body on the solo task, and the quadruped's curve is the noisy one.

**Seed 402 at generation 40 of 200** is the mirror image: the evolved best's fresh-draw time at target is 0.00, 0.01, 0.00, 0.00, 0.02 and the designed quadruped's 0.04, 0.09, 0.07, 0.04, 0.14. As in condition A's two seeds, whether the holistic search has a foothold by generation forty is a coin the run flips once; the designed body's controller evolution climbs slowly in both. The runs continue to 200.

**Seed 401 at generation 100, the curriculum fully open.** Fresh-draw time at target at generations 0, 20, 40, 60, 80, 100: evolved best 0.00, 0.00, 0.16, 0.29, 0.16, 0.22; designed quadruped's best 0.00, 0.09, 0.04, 0.02, 0.06, 0.02. Where the evolved search found its foothold, the lump holds the goal five to ten times as long as the designed quadruped whose controller evolved under the same budget. The quadruped's curve never rose above 0.09 in either seed so far: a designed body with the right number of legs is not the easier start when its gait has to be found by a genetic algorithm with heritability near zero, which is the finding this paper was named for. Seed 402 at generation 100 is again the mirror image: evolved best 0.00, 0.00, 0.02, 0.00, 0.00, 0.05; designed quadruped's best 0.04, 0.07, 0.14, 0.13, 0.13, 0.10. Across the two seeds at the half-way mark it is one each, and the two curves say different things. The quadruped's controller evolution climbs to about 0.1 to 0.15 in both seeds and stops there; the evolved search either finds a body that reaches 0.2 to 0.3 or finds nothing at all. The designed body is the safer start and the lower ceiling, at this budget and this heritability.

**Seed 401 complete.** The evolved best's fresh-draw time at target kept climbing through the second half: 0.26, 0.25, 0.42, 0.45, 0.50 at generations 120, 140, 160, 180, 199. The designed quadruped's went 0.08, 0.13, 0.10, 0.02, 0.00. Realised heritability under the solo score was 0.44 then 0.30 for the evolved population over the two halves and 0.30 then 0.17 for the quadruped's controller. On this seed the lump ends within a hair of A-301's champion (0.54), the best solo competence any evolved robot in the series has reached, and the designed body with the right number of legs ends at zero. Seed 402 finishes next.

**What the seed-401 lump is, by lesion (eight fresh draws).** Two parts, 33 units (11 global, 22 local), two reflex arcs, one sensor-driven effector of two live. Intact it makes 0.82 m of progress and holds the target 0.43 of the bout; with its environmental sensors blanked, 0.00 and 0.00; with its local brains silenced, the same; with its oscillator blanked, unchanged. Silencing the global brain costs it a little, 0.82 to 0.78 m and 0.43 to 0.36, the first evolved controller in the series whose global brain does anything measurable at all. It is still a Braitenberg-class reflex in one segment, closed-loop on a target-direction sensor, with a small central contribution and no proprioception, and it climbed from 0.22 to 0.50 over a hundred generations by refining that reflex rather than by adding to it.
