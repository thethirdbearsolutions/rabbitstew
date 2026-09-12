# Designed Quadrupeds and Evolved Lumps

*Fourth paper in the Rabbitstew series. The GA capacity tests: four capacity seeds to 200 generations, the re-evolution control, and the lesion study of nine bests. Every capability number is measured on fresh, fixed draws the run never trained on.*

## Questions

1. With the opponent removed and fitness set to reaching and holding a goal on random terrain, does the search find locomotion at all, and how fast?
2. Is a hand-designed quadruped, driven by controller evolution alone, easier or harder to make walk than a body the search designs for itself?
3. Does a controller re-evolved from scratch on an evolved champion's body match the native controller, or was the native pair co-adapted?

## Runs

- `solo/cap-401`, `solo/cap-402`: both populations on solo time-at-target fitness for 200 generations, random terrain, random starts, rich brains, equal mass, the designed body a quadruped with position servos, joint-angle and contact sensors on every segment, two oscillators and eight hidden neurons.
- `solo/cap-403`, `solo/cap-404`: the same two seeds again at 403 and 404, run by a delegate (Chaotic RBT-12).
- `reevolve/rich201-body`: fresh controllers evolved for 60 generations on the body of the rich-brain random-terrain champion of seed 201, same solo task.

## Why the first capacity runs were discarded (method, not a result)

The findings this section reported as results are superseded by the complete runs below. What survives is the reason the first attempt had to be thrown away, which is the most transferable thing in the paper.

**The first capacity runs found nothing, and looked as if they had.** Under solo fitness with start headings drawn up to 135° off the goal and two draws per generation, the reported best-of-generation score climbed to about 0.4 within thirty generations in both seeds. Re-evaluated on twelve fresh draws, the same champions scored 0.01 to 0.09 at every generation, for the evolved bodies and for the quadruped alike. The reported curve was a winner's curse: the best of twenty members on two draws is whoever the layout favoured, and with new draws every generation nothing accumulated. A body that only moves forward gains nothing on average when it may face away from the goal, so the progress term averaged to zero and selection had no signal. The steering requirement bit before locomotion existed.

Two changes follow, both now in the simulator: a heading curriculum, under which starts face the goal at first and the offset widens over the first hundred generations, and four draws per generation instead of two. The capacity runs were restarted with both. Every capability number in this series is now reported on fresh, fixed draws, never on the training draws.

## The re-evolution control: the competitive pair was not co-adapted

**The competitive champion's body is bad at competence with any brain.** On twenty fresh solo draws the rich-brain random-terrain champion scores 0.02 with its native brain and 0.07 with a controller re-evolved on its body for sixty generations, while a random body evolved for the same sixty generations under solo fitness scores 0.30. Whatever competition selected for, it was not the ability to reach and hold a goal, and the body it produced is not a good substrate for learning that ability afterwards.

## What the foraging world adds, and why it is a fifth paper

The foraging ecology (`docs/foraging-world.md`) replaces the fitness function with an economy: food in a disc,
an eat radius, a work cost and a basal living cost, no ranking, no culling round, and a sensor vocabulary with
no target-direction oracle in it. Two of its results answer this paper's second question from a direction the
capacity runs cannot, and they are folded in here.

**The evolved body is the cheaper mover, by a wide margin, when nothing ranks it.** Across both dense arms at
600 seasons the holistic bests eat 2.1 to 2.5 items a season alone on 2 to 6 kJ, where the Pioneer bests eat
0.9 to 1.6 on 17 to 20 kJ. Locomotion evolved from survival alone, through a founder bottleneck at season 11,
with no fitness function present. That is the same asymmetry the capacity table shows — the designed body is
the safer start and the lower ceiling — arriving by a completely different route, and it is the strongest
version of it in the series, because here the evolved side wins on the designed body's own home ground of
moving efficiently.

**It does not generalise to a crowd.** In the eight-robot arena (Chaotic RBT-17) the wheeled bests out-eat the
holistic bests both alone and in groups, 2.12 against 0.88 alone and 2.34 against 1.14 per robot in eights at
season 590. The cheap-mowing advantage is a property of the four-robot baseline and not of the comparison, so
the sentence above carries that qualifier wherever it is repeated.

**Lifetime yield is heritable where bout outcomes were not.** Parent-child correlation of foraging yield is
0.51 on the holistic side and 0.24 to 0.39 on the wheeled side, against zero for any bout outcome anywhere in
this series and 0.44 to 0.64 for the solo score in the capacity runs that worked. This is the cleanest support
for the diagnosis in the third paper: what a child inherits is its body, its wiring and mostly its behaviour,
so a score that reads behaviour over a lifetime is heritable and a score that reads one zero-sum bout is not.

**Sensing still did not evolve, in six hundred seasons of seven arms.** No population in the foraging family
ever wired a Braitenberg pairing. The one nose-dependent controller found is a Pioneer whose chassis nose
stops it leaving the food disc, a brake rather than a compass. This extends, rather than qualifies, the lesion
finding above: the absence of distributed, sensor-driven control in this encoding survives the removal of the
fitness function, the oracle sensor and the ranking step alike.

**Scope decision: the foraging world and the ecology are the fifth paper, not a section of this one.** Three
reasons. The question differs — this paper asks which body is the easier substrate for a genetic algorithm on
a designed task, and the foraging work asks what a population does when no task is posed at all, which is a
claim about selection rather than about bodies. The evidence is not complete — the world fan-out has four arms
outstanding (Chaotic RBT-19, RBT-21, RBT-22, RBT-23), and the persistent world they lead to (RBT-2, RBT-19) is
the run the whole family was built to justify, so a section written now would have to be rewritten. And the
material is already the length of a paper: seven arms, two complete 600-season dense ecologies, a drift
baseline, a sparse pair, a density series and two banked designs (the interchange, RBT-3, and the range
expansion, RBT-4). The four results above stay here because they bear on this paper's questions; the rest is
paper 5, and `docs/foraging-world.md` is its working draft.

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

Capacity runs v2, with the heading curriculum and four draws per generation. Four seeds, all complete to 200 generations.

**The final lump-vs-quadruped table.** Fresh-draw time at target on twelve start-and-terrain draws the run never
saw, at the full heading range. The lump is the evolved population's best; the quadruped is the designed body's
best, with controller evolution alone under the same budget. Realised heritability is under the solo score, over
the run's first and second hundred generations. Dashes are quantities the run did not report.

| Seed | Lump, gen 200 | Lump peak | Quadruped, gen 200 | Quadruped peak | Heritability, lump | Heritability, quadruped | Foothold |
|---|---|---|---|---|---|---|---|
| 401 | 0.50 | 0.50 (gen 199) | 0.00 | 0.13 (gen 140) | 0.44 / 0.30 | 0.30 / 0.17 | by gen 40 |
| 402 | 0.00 | 0.05 | 0.07 | 0.20 (gen 140) | 0.12 / 0.08 | 0.25 / 0.14 | never |
| 403 | 0.68 | 0.68 (gen 199) | 0.01 | 0.21 | 0.14 / 0.64 | – | gens 140–160 |
| 404 | 0.02 | – | 0.05 | 0.15 | – | – | never |

Read down the columns rather than across the rows. The quadruped's fresh-draw ceiling is 0.13 to 0.21 in every
seed and its final value is 0.00 to 0.07 in every seed: controller evolution on a designed body finds a little
competence everywhere, keeps none of it, and never reaches what the evolved search reaches when the evolved
search works at all. The lump's column is bimodal: 0.50 and 0.68 in two seeds, 0.00 and 0.02 in the other two,
with nothing in between. Heritability tracks the split and not the body — 0.44 and 0.64 in the halves where a
lump was climbing, 0.08 to 0.14 where it was not — so what distinguishes a working capacity run from a failed
one is whether the search found a body whose solo score its children inherit, which the quadruped's fixed body
cannot supply and cannot lack.

**Seed 401 at generation 40 of 200.** Fresh-draw time at target on twelve draws the run never saw, at the full heading range although the curriculum has only reached forty percent of it: the evolved population's best rose from 0.00 through 0.09 at generation 30 to 0.16 at 40; the designed quadruped's best, with controller evolution alone, went 0.00, 0.04, 0.09, 0.00, 0.06. Early and one seed, but at this point the lump is ahead of the designed body on the solo task, and the quadruped's curve is the noisy one.

**Seed 402 at generation 40 of 200** is the mirror image: the evolved best's fresh-draw time at target is 0.00, 0.01, 0.00, 0.00, 0.02 and the designed quadruped's 0.04, 0.09, 0.07, 0.04, 0.14. As in condition A's two seeds, whether the holistic search has a foothold by generation forty is a coin the run flips once; the designed body's controller evolution climbs slowly in both. The runs continue to 200.

**Seed 401 at generation 100, the curriculum fully open.** Fresh-draw time at target at generations 0, 20, 40, 60, 80, 100: evolved best 0.00, 0.00, 0.16, 0.29, 0.16, 0.22; designed quadruped's best 0.00, 0.09, 0.04, 0.02, 0.06, 0.02. Where the evolved search found its foothold, the lump holds the goal five to ten times as long as the designed quadruped whose controller evolved under the same budget. The quadruped's curve never rose above 0.09 in either seed so far: a designed body with the right number of legs is not the easier start when its gait has to be found by a genetic algorithm with heritability near zero, which is the finding this paper was named for. Seed 402 at generation 100 is again the mirror image: evolved best 0.00, 0.00, 0.02, 0.00, 0.00, 0.05; designed quadruped's best 0.04, 0.07, 0.14, 0.13, 0.13, 0.10. Across the two seeds at the half-way mark it is one each, and the two curves say different things. The quadruped's controller evolution climbs to about 0.1 to 0.15 in both seeds and stops there; the evolved search either finds a body that reaches 0.2 to 0.3 or finds nothing at all. The designed body is the safer start and the lower ceiling, at this budget and this heritability.

**Seed 401 complete.** The evolved best's fresh-draw time at target kept climbing through the second half: 0.26, 0.25, 0.42, 0.45, 0.50 at generations 120, 140, 160, 180, 199. The designed quadruped's went 0.08, 0.13, 0.10, 0.02, 0.00. Realised heritability under the solo score was 0.44 then 0.30 for the evolved population over the two halves and 0.30 then 0.17 for the quadruped's controller. On this seed the lump ends within a hair of A-301's champion (0.54), the best solo competence any evolved robot in the series has reached, and the designed body with the right number of legs ends at zero.

**Seed 402 complete.** The evolved best never found a foothold: fresh-draw time at target 0.00 to 0.05 at every checkpoint to generation 199. The designed quadruped's controller climbed to 0.20 at generation 140 and ended at 0.07. Heritability under the solo score was 0.12 then 0.08 for the evolved population and 0.25 then 0.14 for the quadruped's controller.

**The two seeds together.** At generation 200: lump 0.50 against quadruped 0.00 on seed 401; lump 0.00 against quadruped 0.07 (peak 0.20) on seed 402. The designed body is the safer start, since its controller evolution finds a little competence on every seed, and the lower ceiling, since it never found much; the evolved search either finds a body and climbs past anything the designed body reached, or finds nothing at all. **Seeds 403 and 404**, run by a delegate (Chaotic RBT-12), sharpened both halves. Seed 403's lump sat at 0.00 to 0.08 fresh for 140 generations, indistinguishable from a failure, then found its body between generations 140 and 160 (heritability 0.64 in the second half against 0.14 in the first) and ended at 0.68, the highest fresh-draw competence in the series, passing all three steering trials and four of six terrains with a two-part rolling body and a five-link reflex on the target's vertical component and its own up-vector, the same embodied trick as A-301 and 401. Its quadruped peaked at 0.21 and ended at 0.01. Seed 404's lump found nothing (0.02); its quadruped peaked at 0.15 and ended at 0.05. Across four seeds at generation 200 the lump is ahead twice by a wide margin (0.50 and 0.68 against 0.00 and 0.01) and behind twice at noise level; the quadruped's fresh-draw ceiling is 0.21 in any seed, and it does not keep what it finds. So the foothold is not decided by generation fifty, and the sentence gains a clause: the designed body is the safer start, the lower ceiling, and it does not keep what it finds, while the evolved search's foothold can come late as well as early and, when it comes, climbs past anything the designed body reached. One qualifier to the lesion section: seed 404's failing lump carries measurable joint-angle lesion loss on flat ground, so "no proprioceptive influence" holds for every competent best, not every best.

**What the seed-401 lump is, by lesion (eight fresh draws).** Two parts, 33 units (11 global, 22 local), two reflex arcs, one sensor-driven effector of two live. Intact it makes 0.82 m of progress and holds the target 0.43 of the bout; with its environmental sensors blanked, 0.00 and 0.00; with its local brains silenced, the same; with its oscillator blanked, unchanged. Silencing the global brain costs it a little, 0.82 to 0.78 m and 0.43 to 0.36, the first evolved controller in the series whose global brain does anything measurable at all. It is still a Braitenberg-class reflex in one segment, closed-loop on a target-direction sensor, with a small central contribution, and it climbed from 0.22 to 0.50 over a hundred generations by refining that reflex rather than by adding to it.

**The lab (scripts/lab401.py, twelve fresh draws).** The body is a 10.9 kg sphere with a 0.53 m, 4.4 kg cylinder on a ball joint. The steering axis of that joint is driven by the cylinder's own target-bearing sensor (weight +1.50) and its up-vector sensor (−1.28): a bearing term and an attitude term, the first champion in the series whose reflex reads its own orientation. Lesioning the bearing sensor takes time at target from 0.54 to 0.03; lesioning the attitude sensor, to 0.06. The velocity, joint-angle and joint-velocity sensors on both parts are wired to nothing. The global brain has eleven units and no sensor input: four are constants (a sign and two absolute-value units with fixed biases, and a relu that outputs zero) summing into the joint's other axis, whose raw bias of +1.88 they trim to an effective input of +0.83, a torque of 0.68 instead of 0.95; the rest is a chain ending in a local neuron with no outputs. Silencing the global brain leaves the raw torque and costs 0.54 to 0.38 with a longer, costlier path (8.5 m and 14.5 kJ against 6.4 m and 9.5 kJ); silencing it and writing +0.83 into the effector's bias by hand restores 0.48. Lesioning the one constant that carries most of the trim flips the torque's sign and collapses the robot (0.02). So the global brain's contribution is real, and it is a number: evolution used a hub that could have computed as four extra bias parameters on one torque. On the capability trials the lump reaches all three off-heading goals (final distances 0.25, 0.28, 0.09 m) at 0.40 m/s with a straightness of 0.35, and topples on the way; the designed quadruped's final controller reaches none.

**The lab of the seed-403 lump (scripts/lab.py, twelve fresh draws; run by a delegate, labbed here under the standing rule).** Two parts, 35 units, five links. The body is an 11.1 kg box with a 0.135 m, 4.3 kg sphere on a ball joint. Every link that matters is local to the sphere: the sphere's target-vertical sensor drives one joint axis (weight −0.79), its up-vector z drives another (+1.58), and its up-vector y reaches a third effector on the same joint through the one global neuron that does anything (a tanh, −1.45 into the effector); the fifth link is a second global tanh at +0.06, noise. No velocity, joint-angle, joint-velocity or contact sensor on either part is wired to anything, and the food sensor the vocabulary gave it is unlinked. Intact it makes 1.64 m of progress and holds the target 0.65 of the bout, straighter than 401 (0.28 against 0.35 is the same class) and on the same energy (18.9 kJ). Blanking its environmental sensors or silencing its local brains: 0.22 m and 0.02, a lump. Lesioning the target-vertical sensor: 0.14 m and 0.00; the up-vector z sensor: 0.39 m and 0.00; the effector they feed: 0.16 m and 0.02. Silencing the global brain costs 0.65 to 0.40 with a shorter, straighter path (4.9 m at 0.37 against 7.2 m at 0.28), and lesioning the one global tanh that carries the up-y term gives the same 0.47: as in 401, the hub's whole contribution is one number on one torque, here an attitude term routed through a neuron because that is where the mutation landed. Lesioning the up-y sensor itself costs nothing (0.67), so the neuron's input is the part that does not matter and its bias is the part that does. Three champions in the series have now been labbed (A-301, 401, 403), and all three are the same object: a two-part body, a ball joint, a reflex from the target's direction plus the body's own attitude onto one or two joint axes, and a memory or a trim that lives in the effector's own dynamics rather than in any neuron.

## Reproducibility

The capacity runs. Fitness is solo for the whole run, so the locomotion phase is set to the run's length;
champion bouts still run at the checkpoint interval, but as a measurement only, and nothing a bout
returns feeds selection. The designed population's body is the quadruped rather than the Pioneer.

```
rabbitstew evolve --terrain random --mass-budget 15.34 --conventional-topology \
    --random-start --score time_at_target --locomotion-phase 200 \
    --heading-curriculum 100 --draws 4 --fixed-body quadruped --hidden 8 \
    --population 20 --generations 200 --brain-model rich --duration 15 --seed 401 \
    --out runs/cap-401
```

Seeds 402, 403 and 404 differ only in `--seed`. The re-evolution control keeps a champion's body and redraws
its weights, which is what `--fixed-body` does when given a genotype file rather than a name:

```
rabbitstew evolve ... --locomotion-phase 60 --generations 60 \
    --fixed-body runs/random-rich-201/holistic/final/000.json --out runs/reevolve-rich201-body
```

Every number in the results table is a fresh-draw solo score from `scripts/eval_fresh.py RUN 20 12`: twelve
start-and-terrain draws seeded outside the run's own range, at the full heading range whatever the curriculum
has reached, and never a training-draw best. This is the discipline the first capacity runs lacked and the
reason they were discarded. Heritability is `rabbitstew heritability RUN`, windowed to report the two halves
apart. The lesion table is `rabbitstew analyze RUN --lesions final`; the two labbed champions are
`scripts/lab401.py` and `scripts/lab.py`, whose transcripts are `docs/lab-cap-403.txt` and `docs/lab-A-301.txt`.
