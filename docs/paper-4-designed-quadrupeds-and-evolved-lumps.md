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

## Results

(pending: capacity runs v2 with the heading curriculum)
