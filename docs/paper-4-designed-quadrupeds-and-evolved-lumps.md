# Designed Quadrupeds and Evolved Lumps

*Fourth paper in the Rabbitstew series. Placeholder: the GA capacity tests. Filled when the solo and re-evolution runs complete.*

## Questions

1. With the opponent removed and fitness set to reaching and holding a goal on random terrain, does the search find locomotion at all, and how fast?
2. Is a hand-designed quadruped, driven by controller evolution alone, easier or harder to make walk than a body the search designs for itself?
3. Does a controller re-evolved from scratch on an evolved champion's body match the native controller, or was the native pair co-adapted?

## Runs

- `solo/cap-401`, `solo/cap-402`: both populations on solo time-at-target fitness for 200 generations, random terrain, random starts, rich brains, equal mass, the designed body a quadruped with position servos, joint-angle and contact sensors on every segment, two oscillators and eight hidden neurons.
- `reevolve/rich201-body`: fresh controllers evolved for 60 generations on the body of the rich-brain random-terrain champion of seed 201, same solo task.

## Results

(pending)
