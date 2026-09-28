# RBT-125 world gate: readout of the τ cell, §C, the committed layouts and §B

*This is the follow-up to #430 (§A, merged), per the coordinator's ruling of 01:31 UTC. The rules are
`REGISTRATION.md` with amendments 1 and 2. The parts are added as they finish. They all come from the same launch
as §A: the worktree pinned at c591a75, started at 23:01:31, with the parity result in `launch.txt`.*

## τ = 1 s sensitivity (PW-G2.5-tau1; descriptive)

The cell is PW at G = 2.5 with `smell_tau` = 1 s, the value in RBT-116's draft. All 10 of 10 populations are
readable, and 70 of 70 bodies are signed.

| quantity | t(9) 95% |
|---|---|
| prize at a = 6 | +0.812 [+0.414, +1.210] |
| motif − decoy | +0.930 [+0.563, +1.297] (the decoy retains −14%) |
| τ1 − PW-G0, paired (the channel's contribution) | +0.687 [+0.296, +1.078] |
| **τ1 − τ2 (PW-G2.5), paired** | **+0.199 [+0.064, +0.333]** |

- The base income is 1.052, and 2822 of 4480 pairs tie.
- **At this rung, τ = 1 s pays the installed compass more than the registered τ = 2 s,** and the interval excludes 0.
- **This is descriptive, and it does not change the registered transform.**
  - The 22:28 ruling kept τ = 2 s and had RBT-116 amended to match.
  - Whether to move τ is the coordinator's call. It would need a new registration, because this cell was run as a
    sensitivity check, not as a comparison.
- **A plausible mechanism**, consistent with the saturation table below: a shorter baseline tracks the noses' mean
  faster, so the common temporal term is smaller, and less of each nose's tanh range is spent on it.
  - The median |c| is 0.27 at τ = 1 s, against 0.37 at τ = 2 s.
  - The median |c_L − c_R| is 0.35 against 0.29.

## §C, saturation (`saturation.txt`)

This is the registered readout: the median and p90 of |c| over every food nose and every tick. It uses the §A bodies
(70 designed bests × 2 seasons, seeds 7000 and 7001), as they are, with no motif.

| cell | median \|c\| | p90 \|c\| | share \|c\| > 0.9 | median \|c_L − c_R\| | p90 \|c_L − c_R\| |
|---|---|---|---|---|---|
| PW-G2.5 | 0.368 | 0.862 | 0.077 | 0.292 | 0.529 |
| PW-G10 | 0.887 | 1.000 | 0.486 | 0.325 | 1.505 |
| PW-G2.5-tau1 | 0.270 | 0.703 | 0.024 | 0.349 | 0.549 |
| HP-G2.5 | 0.384 | 0.933 | 0.127 | 0.255 | 0.631 |
| HP-G10 | 0.923 | 1.000 | 0.530 | 0.248 | 1.579 |
| U-G2.5 | 0.398 | 0.923 | 0.116 | 0.326 | 0.677 |
| U-G10 | 0.916 | 1.000 | 0.526 | 0.353 | 1.697 |

- **G = 10 saturates the individual noses on real bodies.**
  - About half of all readings exceed 0.9, and the median is about 0.9 in every layout. This confirms adversary §6b
    (median 0.56–0.64 and p90 0.93–0.95 there) and puts it higher.
  - The wheel difference |c_L − c_R| is still graded at the median (0.25–0.35), but its p90 reaches 1.5–1.7, close
    to the maximum of 2.
- **At G = 2.5, the median |c| is about 0.37–0.40, and 8–13% of readings exceed 0.9.** It sits mostly in the graded
  range.
- Together with §A (G10 not worse than G2.5 at a = 6), this says the G = 10 cost, if there is one, lies in the step
  path and in the evolved wiring the nose feeds. It does not lie in an installed compass's prize. §B tests the step
  path.

## §C, the R6 side effects (`side_effects.txt`)

*Running. The seasons are solo, so births and realised depth are out of scope (amendment 1, A1.7).*

## §A, the committed layouts (HP and U at G ∈ {2.5, 10}, then G = 0)

*Pending. These run after §C.*

## §B: a nose step against a +25% speed step (descriptive; expected TIED, UNRESOLVED)

*Pending. It runs last, at 128 seeds per host.*

## Output timestamps (UTC, gate worktree)

- `saturation.txt` 2026-09-28 01:52:53Z
- `prize/PW-G2.5-tau1-1.txt` 2026-09-28 01:35:07Z
- `prize/PW-G2.5-tau1-2.txt` 2026-09-28 01:38:55Z
- `prize/PW-G2.5-tau1-3.txt` 2026-09-28 01:42:49Z
- `prize/PW-G2.5-tau1-4.txt` 2026-09-28 01:46:44Z
- `prize/PW-G2.5-tau1-7.txt` 2026-09-28 01:50:32Z
- `prize/PW-G2.5-tau1-801.txt` 2026-09-28 01:15:46Z
- `prize/PW-G2.5-tau1-804.txt` 2026-09-28 01:19:40Z
- `prize/PW-G2.5-tau1-805.txt` 2026-09-28 01:23:29Z
- `prize/PW-G2.5-tau1-806.txt` 2026-09-28 01:27:19Z
- `prize/PW-G2.5-tau1-807.txt` 2026-09-28 01:31:10Z
