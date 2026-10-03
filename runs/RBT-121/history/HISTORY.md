# RBT-121 audit D: the history of what the record walked back

**Auditor D (history)**, for the RBT-121 design pass. Auditors A–C audit the code; this file audits the **record**.

It catalogues every claim in the programme's record that was later deflated, reversed or shown to be an artefact. It then says what each incident teaches a fair experiment in this simulator.

**Read-only.** No file under `rabbitstew/`, `tests/`, `scripts/` or any scored path was changed. This file is the only addition.

**Tree audited:** `152e2df` (the head of `claude/new-session-4cao7d` at 2026-09-27 20:30 UTC).

## What was read

- **Papers:**
  - the follow-up paper;
  - papers 3–10, with `docs/paper-9/` and `docs/paper-10/` (their re-derivations and paper adversaries);
  - the 2026-09-27 progress report.
- **Design notes:**
  - `sims-budget-run`, `experiment-5-competence`, `founder-diversity`, `foraging-world`, `persistent-world`, `held-out-challenges` and `rbt-91-weight-scale-decision`;
  - the root `README.md`;
  - `docs/lab-*.txt` and `docs/runs/*`.
- **Runs:**
  - every `REPORT.md`, `ADVERSARY*.md` and `RECHECK.md` under `runs/`: 74 files, 15,336 lines;
  - the READOUT, PREREGISTRATION and README files beside them;
  - `runs/sim-audit/CHAOTIC-DOC.md`, `runs/compass-gain/` and `runs/compass-spike/`.
- **Chaotic:**
  - RBT-121 and the doc *Origins: the 2005 Rabbitstew proposal…*;
  - the ruling threads of RBT-8, 30, 38–40, 61–64, 66, 68, 76, 77, 79, 81, 82, 86, 87, 93, 98, 111, 113, 117 and 120.
  - `issue_view` returns only a ticket's newest 20 comments. RBT-113 has 24, so its four oldest comments, including the 15:15 design-adversary ruling, were **not** visible. That ruling is cited here from `runs/RBT-113/design-adversary/ADVERSARY.md` and `PREREGISTRATION.md` instead.
- **Code, for the "in code today" column:**
  - `rabbitstew/cli.py`, `world.py`, `simulation.py`, `synthesis.py`, `ecology.py`, `evolution.py`, `genetics.py` and `analysis.py`;
  - all 439 committed `config.json` files under `runs/`.

**Citation format.** Citations are `path:line` at `152e2df`; for tickets they are the ticket and the comment's UTC timestamp. `→` separates where a claim was made from where it was corrected. Paths starting `runs/` or `docs/` are relative to the repo root. "P7" and similar abbreviations mean `docs/paper-7-five-instruments.md` and its siblings.

**Class codes:**

| code | class |
|---|---|
| **PHYS** | physics or body-model allowance |
| **ECON** | economy or world allowance |
| **OP** | operator or GA artefact |
| **INSTR** | instrument or measurement artefact |
| **STAT** | statistical or registration issue; *(record)* marks evidence-retention and provenance failures |
| **WORD** | overclaiming in wording |

**"In code today" vocabulary:**

| label | meaning |
|---|---|
| **on (unconditional)** | the fix is in code and cannot be turned off |
| **on by default** | the fix is in code and is the default |
| **flag, off by default** | the fix exists only behind an opt-in flag |
| **protocol only** | a written rule, with no code to enforce it |
| **wording only** | the fix was a rewording, with no code or rule change |
| **never fixed** | the fix was proposed or owed and does not exist |
| **n/a** | the incident needed no code fix: a reading was withdrawn, or the error was in a one-off analysis script |

---

## 1. The incident table

There are 76 rows, in roughly chronological order.

**Dates:**

| incidents | when |
|---|---|
| the arena era | before 2026-09-12 |
| RBT-5 to RBT-40 | 09-12 |
| RBT-45 to RBT-87 | 09-13/14 and 09-19 |
| RBT-88 to RBT-105 | 09-19 to 09-26 |
| RBT-106 to RBT-120 | 09-26/27 |

**Where the first draft of each row came from.** Six parallel readers each took one slice of the record, and one read the tickets. The coordinating author spot-checked every load-bearing row against its file and line, and wrote the "in code today" column from the code directly.

### 1a. The arena and the GA runs (the follow-up paper, papers 3 and 4)

| # | date / ticket | what was claimed | what it turned out to be | how it was caught | the fix | in code today | class | cite |
|---|---|---|---|---|---|---|---|---|
| H1 | arena, follow-up paper | One 50-generation seed "crossed parity at generation 18" (214 of 468 champion bouts). | A **weight-class mismatch**. Holistic champions weighed 30–90 kg against the Pioneer's 15.34. Fitness correlated 0.41 with mass and 0.04 with connected units or effectors. A champion with **no driven effector** won its bout. At equal mass: 0.31 → 0.21, 113 of 936. | Replaying 50 best-against-best bouts and correlating with body descriptors; then an equal-mass control. | `--mass-budget 15.34` (`SynthesisConfig.mass_budget`). | **Flag, off by default:** `default=None` at `cli.py:431,462,571`; `synthesis.py:39,277-283`. All 439 committed `config.json` set 15.34. `inspect` never applies it and prints unscaled mass (`cli.py:88-104`; `runs/RBT-12/REPORT.md:5`): never fixed. | PHYS | `docs/followup-paper.md:45-47`; P7:119-126 |
| H2 | arena, follow-up paper | A published matrix: a flat-ground parity band; 1218/1836 wins with 180 climbs on the plateau; 1744/1836 with 1085 crossings on rails. | The **spawn drop**. Bodies were lifted by their bounding spheres, and the drop became momentum. The flat champion is a 13.5 kg motorless sphere that rolls 1.84 m. From rest, every champion gains −0.25 to −0.07 m. | The solo toolkit, measuring from rest. | A 1 s passive settle; velocities zeroed; re-centred on the spawn. | **On by default:** `SimConfig.settle_time = 1.0` (`simulation.py:72,161-187`); every committed config has 1.0. | PHYS | `docs/followup-paper.md:51-55`; P7:128-140 |
| H3 | arena, follow-up paper | Holistic against designed, as the proposal posed it. | Confounded: the fixed body's controller topology was frozen while the holistic one evolved. | Design review. | `--conventional-topology`. | **Flag, off by default under `evolve`** (`cli.py:467`); on by default under `ecology` (`cli.py:579`). All committed configs set it. | OP | `docs/followup-paper.md:13,27` |
| H4 | arena, paper-201 | Flat-ground holistic win, 1079 of 2550 bouts. | The opponent was broken: the wheeled controller moved 0.5 m alone. | Solo toolkit. | Protocol: measure both sides alone. | Protocol only. | INSTR | `docs/followup-paper.md:72,76` |
| H5 | arena | Holistic wins on the plateau and rails. | Shows only that wheels cannot cross them. | Author. | Kept only as where the spawn artefact showed. | Wording only. | WORD | `docs/followup-paper.md:37,135` |
| H6 | paper 3 | Condition C yield heritability 0.74. | Pooling across the solo and competitive phases. Within phase it is 0.41/0.09 and 0.12/0.05. | Author re-analysis. | `heritability --window`. | **Flag, off by default** (`cli.py:533`). | STAT | `docs/paper-3-let-the-furniture-stop-me.md:106,137` |
| H7 | paper 3 → RBT-11 | Population-20 solo-score heritability 0.35–0.41; the standard tool's 0.31 under `--survival`. | Not reproduced at the Sims budget (0.08–0.11). Under `--survival` each survivor is **re-logged every generation**: "survivors, not inheritance". | RBT-11's newborn-only estimator. | RBT-44 (newborn-only pairing). | **Never fixed:** RBT-44 is in backlog; `realised_heritability` is unchanged (`analysis.py:926`). | OP / INSTR | `runs/RBT-11/REPORT.md:59,61`; `docs/paper-4-designed-quadrupeds-and-evolved-lumps.md:139` |
| H8 | RBT-5 → RBT-11 | "Selection at this budget is real and strong": 2 founders against 102 expected under noise. | `--founder-model` models tournament selection with two elites. It "says nothing about drift versus selection" under survival or lexicase. | RBT-11. | None for GA runs. | **Never fixed:** `cli.py:275-277` refuses the flag only for ecology runs, so survival and lexicase GA runs still get the tournament null. | STAT | `runs/RBT-5/REPORT.md:60-64,171-178` → `runs/RBT-11/REPORT.md:70` |
| H9 | paper 4 | Best-of-generation reached about 0.4 within 30 generations. | Winner's curse: 0.01–0.09 on twelve fresh draws. | Fresh-draw re-evaluation (`scripts/eval_fresh.py`). | `--draws 4`, `--heading-curriculum 100`, fresh-draw reporting. | **Flags, off by default:** `--draws 1`, `--heading-curriculum 0` (`cli.py:471,477`). Fresh-draw reporting is protocol only. | STAT | P4:19-23,150,163-165 |
| H10 | paper 3 → RBT-9 | "One steerer in four seeds" / "one seed of two". | One in eight. The stale sentences remain in paper 3. | RBT-9's four extra seeds. | Wording. | Wording only (P3:98,108 still stale). | WORD | P3:93-98,108; `runs/RBT-9/REPORT.md:33` |
| H11 | RBT-12 → RBT-37 | The seed-403 winner is a "rolling" box and sphere on a ball joint. | **It flails:** a sphere on a crank the length of its radius, spun at 3.4 rev/s against the ground, dragging a box lying on its side. Seed 404 found the same crank. | Replay plus `rolling.json`. | "The search designed a crank." A contact-artefact test was **explicitly not done**. | **Never fixed / never tested.** | PHYS | `runs/RBT-12/REPORT.md:34-35` → `runs/RBT-37/REPORT.md:5-20,77` |
| H12 | paper 4, 403 lab | The load-bearing sensor is "target-vertical". | It is unit 21, **"opponent z"**. In solo evaluation, opponent sensors are pointed at the target (`opponent_proxy=True`), so a second target oracle exists that no competitive bout offers. | This audit (docs lab against paper text). | None. | **On by construction:** `simulation.py:701`; `analysis.py:433`. It affects the target task (`paper` and `rich` brains), not foraging's `agent` smell (`simulation.py:270-272`). | PHYS / INSTR | P4:135; `docs/lab-cap-403.txt:25,41` |
| H13 | RBT-37 | Extension of seed 404 to 400 generations. | `--resume` with the original `--locomotion-phase 200` silently switched to competitive bouts at generation 200. | Author. | Config edited by hand. | **Never fixed:** no guard (`--locomotion-phase` default 0, `cli.py:472`). | OP | `runs/RBT-37/REPORT.md:55` |
| H14 | paper 3 → RBT-8 | A relative living cost and a paired challenge as the ecology's economy. | Both self-extinguish: energy is conserved, so nobody gets far enough above average to breed. | Paper 3's runs. | An absolute living cost of 0.05, calibrated by `scripts/calibrate_cost.py`. The delegate's first pick, 0.25, failed calibration. The old economies are retired and warn. | **On by default:** `ecology.py:99,126-187`. | ECON | P3:141; RBT-8 2026-09-12T16:51:30, 17:00:30 |

### 1b. The ecology and the world fan-out (RBT-10 to RBT-40, paper 5, paper 6)

| # | date / ticket | what was claimed | what it turned out to be | how it was caught | the fix | in code today | class | cite |
|---|---|---|---|---|---|---|---|---|
| H15 | RBT-30 (paper 6) | Density-table means over founder draws. | An exploding robot was **billed the actuator work its diverging integrator ran up**: 1.5×10⁹ kJ for one founder in sixty (8×10⁶ on re-run). | Paper 6's density ladder. | An exploded robot forfeits the season: no items, no work. | **On (unconditional):** `simulation.py:514-527`; `ecology.py:295-304`. **But** RBT-71's seeds 801–806 were pinned to `f3aa69d`, before the forfeit. RBT-19's P-801 log holds 97 QACC warnings its report never mentions. | PHYS → ECON | P6:293-300; RBT-30 2026-09-12T19:04:28; `runs/RBT-71/REPORT.md:80-87`; `runs/RBT-19/P-801.log` |
| H16 | RBT-19 | The persistent world keeps the clearance rule. | Food spots cannot move, so robots spawned on food and **ate 15% of all items on the first tick**: a free lunch for standing still. | Author measurement. | `clear_spawn_layout`: the roomiest of 128 redraws. "The only [choice] in the build that could move a number." | **On, persistent worlds only** (`simulation.py:712-751`). | ECON | `runs/RBT-19/REPORT.md:60-70` |
| H17 | RBT-18, RBT-21 | "A lump's budget never depended on the work cost"; the informative ceiling is about 0.1 per kJ. | False for the tail. At 0.15 and 0.08 per kJ, random founders' work budgets "decide the outcome before evolution starts". The ceiling is below 0.08, because realised arena yield (0.385) is below solo yield (0.50). | RBT-21 replication. | Standing rule: no demographic prediction from solo yield. | Protocol only. `--work-cost` defaults to **0.0** (`cli.py:62`); runs set 0.03. | ECON | `runs/RBT-18/REPORT.md:7,30`; `runs/RBT-21/REPORT.md:12-16,195-206` |
| H18 | RBT-16 → RBT-23 | 24 items with no regrowth chosen for "the same expected yield as baseline"; the depletion effects that followed. | A denser first pass. Every demographic difference "reverses or disappears" at 12 items. | RBT-23. | Rerun at baseline density. | n/a | ECON | `runs/RBT-16/REPORT.md:182-190` → `runs/RBT-23/REPORT.md:89-97,213-218` |
| H19 | RBT-15, RBT-20 | Long seasons with "economy per unit simulated time unchanged". | Season length is entangled with the spawn reset of the standing crop: food per second falls to about 40%. | RBT-20. | None: `--duration` cannot isolate it. | **Never fixed.** | ECON | `runs/RBT-15/REPORT.md:76`; `runs/RBT-20/REPORT.md:64-84,100` |
| H20 | RBT-13, RBT-22 → sim-audit | The smell squash `i/(1+i)` is "a real design error" that saturates at 3 m decay. | Refuted three times out of three. It is strictly monotone and destroys no directional information; removing it makes the mower worse (1.516 → 1.288). | `sim-audit` independent refutations. | `--smell {sum,mean,log}` was added for the "error". | **Flag, off by default** (`--smell sum`, `cli.py:61`). The fix was itself reversed. | INSTR | `runs/RBT-22/REPORT.md:18-20` → `runs/sim-audit/CHAOTIC-DOC.md:182-188` |
| H21 | RBT-13, RBT-22, paper 6 → RBT-39 | The **blind-mow floor** 2 × eat_radius × density (0.297 items/m) is the null; "only a yield below it is damning". | A point-robot rate. Body width and own gait put the honest null at 0.70–1.67× the floor, so it bounds nothing in either direction. RBT-22 g300, called "damning", is above its own null. | RBT-39's trajectory-preserving null, with a planted positive control. | `rabbitstew/forage_null.py`; rule: beat your own trajectory null, with a positive control at the n in use. | Tool present; rule protocol only. | INSTR | `runs/RBT-22/REPORT.md:112-114`; P6:35-46 → `runs/RBT-39/REPORT.md:52-118` |
| H22 | RBT-38 (fan-out) | 15 nose-dependence claims at 8–16 seeds: 57%, 74%, 27%, 88% and so on. | At 64 paired seeds, **10 of 15 die** and **every effect that moved, moved down** (27% → +2%, 74% → 35%, 57% → 29%). This is champion selection on a small probe. | Re-read with a verdict rule posted first. | `rabbitstew/paired.py`; `scripts/paired_lesion.py`; rule: 64 paired seeds, per-seed list, zero-count veto. | Tool present; rule protocol only. | STAT | `runs/RBT-38/REPORT.md:27-53`; P6:67-94; RBT-38 2026-09-14T02:14:03 |
| H23 | RBT-28 | The g300 lump "loses half its yield" without its nose; "every subsystem is a handicap"; the mower's 3.12 items; four of five arms converged. | 0.00 ± 0.17 at 64 draws; the handicap reading was withdrawn; 2.03 ± 0.22 (3.12 is outside the interval; the 12-draw rule "could not fail"). The five arms share one founding population, P(≥ 4 of 5) = 0.17. | RBT-28 §7 adversary. | `forage_lab.py` prints the resolvable effect and "CANNOT TEST". | Script only. | STAT | `runs/RBT-28/REPORT.md:92-129,180-233`; `docs/runs/RBT-28-adversary-n64.txt:4`; `docs/runs/RBT-28-adversary-founders.txt:7,14` |
| H24 | RBT-28 | Items per metre from `forage_lab.py`. | It sampled the path every tenth tick, overstating by up to 1.17×. | Adversary. | Sample every tick, with a pinning test. | n/a (script fixed) | INSTR | `runs/RBT-28/REPORT.md:158-164` |
| H25 | RBT-71, RBT-82 | Neutral-control yield heritability 0.52 / 0.60, the strand's headline control; the persistent world's 0.246. | Not on any branch, so unverifiable. Checkable neutrals read about 0 (−0.13 to +0.15). `realised_heritability` reads a **shared season effect** as inheritance (+0.43 at w = 1). The neutral *wheeled* control clears the bar, so "heritable" certifies a measurement, not selection. | RBT-82 synthetic null; RBT-71 adversary. | Docs mark the figures unverified; quote a drift baseline beside every heritability. | **Never fixed in code** (`analysis.py:926`). The share was never measured on the persistent arm, yet 0.246 is still quoted (P5:189,220,414; P6:171) against `docs/foraging-world.md:325`. | STAT / INSTR | `runs/RBT-82/season_effect.txt:1-10`; `docs/foraging-world.md:309-325`; P5:198-205 |
| H26 | RBT-17; paper 4 | "The evolved bodies out-eat the designed one on a fraction of its energy." | Fails at eight robots per arena (the bests reverse). At population level it is **parity, not reversal**. | RBT-17; the held-out-challenges design. | Wording. | Wording only. | WORD / ECON | `runs/RBT-17/REPORT.md:119`; P4:36-47; `docs/held-out-challenges.md:92-97` |
| H27 | RBT-10, RBT-71 (paper 5) | 801 overtakes and climbs to +1.63; the lead holds 450–566 of 600 seasons; a 60 → 7 bottleneck; cheap blind mowing on the free arm. | The climb "does not reproduce anywhere". 450–566 was the two most favourable replicates. The bottleneck is the extreme case. The cheapness was the work-cost coefficient plus drift. | RBT-10 replicates; RBT-71 fresh seeds and adversary. | Wording. | Wording only. | STAT / WORD | P5:137-158,233-240; `runs/RBT-10/REPORT.md:269-280`; `runs/RBT-71/REPORT.md:143-147` |

### 1c. The compass strand: the instruments paper 7 is about (RBT-45 to RBT-97)

| # | date / ticket | what was claimed | what it turned out to be | how it was caught | the fix | in code today | class | cite |
|---|---|---|---|---|---|---|---|---|
| H28 | compass-spike, RBT-61 | "A bolted-on compass earns nothing"; crossed = uncrossed. Backed by 14,336 bouts, a held-out split, a bootstrap and 64 paired seeds. | **Transposed drive.** The Pioneer's wheel hinge axes are antiparallel (dot product −1.0000), so the effector *sum* steers. The spike installed a smell-gated pirouette. Wired correctly: **+0.897 items (+59%)**. | The owner's physics prior ("Braitenberg vehicles demonstrably work"); a 20-agent audit; `sim-audit/verify_independent.py`. | `steering_throttle()`, `drive_commands()`, `tests/test_pioneer_drive.py`. The geometry is deliberately unchanged. | **Helpers and test on;** the convention is still a trap. `runs/compass-spike/REPORT.md` has **no erratum**. | PHYS → INSTR | `runs/compass-spike/REPORT.md:50-64` → `runs/sim-audit/CHAOTIC-DOC.md:14-22,93-111`; P7:282-321; `rabbitstew/fixed.py:188,206` |
| H29 | RBT-45 | "The crossed pairing — the only one that steers" arrives in 1.3% of lineages; re-aim RBT-42's operator at it. | On this body the crossed pair **is** the pirouette (−1.502 items). | H28. | Recommendation withdrawn. | Wording only. Still quoted unqualified at P6:128,210,215,400 and `docs/foraging-world.md:226`. | INSTR | `runs/RBT-45/REPORT.md:143-144` → `runs/sim-audit/CHAOTIC-DOC.md:113-130`; P8:657 |
| H30 | compass-gain → RBT-63 | "The structural precondition for a Braitenberg compass is present in 7–17% … the bottleneck is not that the circuit is never proposed." | `sensor_influence` sums `abs(w)` and clips at 3.0, so a compass and its twin both read (2.0, 2.0). Reversed by its author 5 h later. | Author, with a signed measure. | `signed_influence` added beside it. | **On (both emitted):** `analysis.py:144,169,187,677-678`. `signed_influence` still defaults to **depth 4**, the divergent sum of H31. | INSTR | `runs/compass-gain/SUPERSEDED-FINDING.md`; P7:257-280; RBT-63 2026-09-13T13:24:12 |
| H31 | RBT-45 §7 → RBT-78/81 | "Drift proposes a paying motif in 0.70% of realistic lineages." The "gradient-dominant" filter \|a\| > \|c\|. | A **depth-4 truncation of a divergent series** (ρ 1.565–4.92 on all 14 bests). An information-free agent-smell pair clears at the same rate. The filter is algebraically the sign test s₁·s₂ < 0. It was re-read three times in one night. | Linear algebra over committed files; RBT-78 adversary (200,000 pairs). | `steering_terms(ph, depth=1)`. | **On by default** (`analysis.py:247`). The filter survives in `runs/RBT-78/reconcile.py:237,282,297`. | INSTR | P7:421-474; `runs/RBT-78/REPORT.md:82-95`; P8:116-120,660,663 |
| H32 | RBT-87 | The depth-1 `a` is the calibrated quantity. | It reads **exactly 0** on the only compass motif the encoding can write (routed through a global unit, because the wheels are siblings, `genotype.py:496`). | Round-trip tests. | Docstring scope note plus tests. | Default unchanged (on). | INSTR | RBT-87 2026-09-19T14:21:55; P5:301-303 |
| H33 | RBT-58 | The pre-registered compass criterion was met (t −3.60): "by the letter … this is a compass". | **A throttle:** 0.406 items per fresh cell against 0.416 by chance. Both legs of the criterion are satisfiable by mobility alone. | An off-pipeline density × area null. | Pre-register an argument that the rule can fail. | Protocol only. | INSTR / STAT | `runs/RBT-58/REPORT.md:22-55`; P7:174-192 |
| H34 | RBT-58 → RBT-39 | The replacement rule, items per new cell; the null detects "7% of the crop". | The per-cell rule overstates by 1.67–1.91× (numerator: any geom; denominator: centre-of-mass cells), so it is "a test a wide body passes for being wide". The 7% was extrapolated below every measured point; measured, it is 1–4 items (8.3–16.7%). | RBT-39 and its adversary. | Rule withdrawn; sweep in whole items. | Protocol only. | INSTR / STAT | `runs/RBT-39/REPORT.md:120-195`; `docs/runs/RBT-39-adversary.txt:1-11` |
| H35 | RBT-69, E8, E9 | "The +0.897 is real and it is not chemotaxis: anti-chemotactic." Then: the compass "does not replicate" on P-801 (−1.154, −0.549); then: "the world explains it". | Bearing was measured against chassis yaw on a **reverse-driving** population. **Direction of travel is a free population parameter:** the same weights are a compass on one population and an anti-compass on another. | Geometry; `scripts/travel_direction.py`; an independent re-implementation. | Rule: measure the direction of travel first, and state the generation. | **Protocol only.** It is still stale at source: `docs/runs/RBT-69-compass-replication.md:120-121` (+5.1°, six of seven). P7's abstract gives −1.154 where −0.549 is the split figure (P7:38 against P7:333,390). | PHYS (free body parameter) / INSTR | P7:338-372,484-544; RBT-64 2026-09-13 20:47:40 |
| H36 | RBT-77 | Direction flips within lineages stop a compass accumulating (filed urgent). | The trace conflated lateral champions (0 of 9 changes ancestor → descendant). Acquisition binds, not sign. | Pedigree check; the author's own race. | Closed as refuted. The race numbers still rest on depth-4 (P8:700-708). | n/a | STAT | RBT-77 2026-09-13T21:34:23, 22:31:25; P7:412-419 |
| H37 | RBT-66 | The brake / throttle / sweep-modulator taxonomy of nose circuits. | The free-running lesion that built it **fails a positive control, 2 of 4**, putting both steering circuits on the throttle axis. "Chassis nose alone" is false for the brake. "Tick 2 agrees" was a silent tick. The probe loses magnitude to the Effector `tanh` (up to 24×). | A frozen-trajectory probe with a positive control (4/4, 16/16). | `runs/RBT-66/axis_lesion.py`; relabels. | Script only. Paper 6 not updated (P6:112-118 against `docs/foraging-world.md:282`). | INSTR | `runs/RBT-66/REPORT.md:11-31,54-147,173-208` |
| H38 | RBT-65 → RBT-79/80 | The drift arm retains the seeded motif 30 of 30, as well as selection does. | The champion is the wrong witness: `best_lifetime_score` selects foragers even under drift, against a mutation-only floor of about 58%. RBT-80 then read NO VERDICT, and its seeded arm's lead was already present at season 0. | RBT-79; P8 adversary. | `Ecology(trait=…)` population carriage (RBT-27 telemetry). | **Opt-in, no CLI flag** (by design). The discriminating control is **never run** (P8:767-774). | INSTR / STAT | RBT-79 2026-09-14T02:31:56; `README.md:442-452`; P8:280-296 |
| H39 | RBT-59 → RBT-60 | Arms vary "search pressure" over 600 seasons; recommendation: shorten `max_age` to buy generations. | 600 seasons is about 18–24 reproductions (slot-limited births). `--max-age 15` bought 3.4× the depth and "a worse population": heritability 0.51 → 0.25, and yield fell. | First-parent chain depth; RBT-60's pre-registered arm. | Rule: declare the expected realised depth. | Protocol only. | OP / ECON | `runs/RBT-59/REPORT.md:30-39,76-88` → `runs/RBT-60/REPORT.md:106-124`; P7:217-255 |
| H40 | compass-gain, RBT-62, RBT-91 | P(paying direct motif) ≈ 10⁻⁷⁷; a link reaches 16 at depth ≈ 6,500 (σ(d) law); "thirty times too small"; widening `weight_sigma` supplies magnitude; RBT-91 "magnitude is not far away" (92% of the rung). | The direct motif cannot be written. The walk is stationary (rms about 3) because of the reset. The 92% was the **whole brain** (the motif's own links read +0.0036) and an anti-compass. Widening walks the bias (no reset) and pumps recurrence. The decision went A → B → A. | Re-derivation; RBT-91 census and adversary. | `--global-bias-sigma` (RBT-112), `--link-scale` (RBT-104). | **Flags, off by default** (`cli.py:558-559`, `genetics.py:66,131-132`). Stale at source: `docs/rbt-91-weight-scale-decision.md:202-203`. The σ(d) law is still in P5:303-305. | OP / INSTR | `runs/compass-gain/REPORT.md:88-91`; P8:383-401,614-669; `docs/rbt-91-weight-scale-decision.md:20-67,174,223-245` |
| H41 | RBT-91 | 35 compasses against 48 anti-compasses (42.2%); the paying rung 6.87 "realised against realised". | The re-signing read the whole brain and counted zeros as anti: the motif's own links give 30/28 (51.7%). 6.8664 is a whole-brain reading hard-coded in `structural_rate.py`. Three of four arrivals share one parent. | P8 adversary round 1 (F3, F4); RBT-91 adversary. | Links-alone column. | n/a. **Printing 6.8664 in a readout is still owed** (P8:760). | INSTR / STAT | P8:349-423,668-669; `runs/RBT-91/adversary_rate.py:4-25` |
| H42 | RBT-67 | +59% is the prize; a pre-registered turnover at a = 96 or 128 (confidence 0.60). | A floor: still rising at a = 384 (+148%). Twelve exploded bouts inflated path metres and made the items-per-metre dips. | The ladder extension. | Wording ("a floor"). | Wording only. | WORD | `runs/RBT-67/REPORT.md:90-108,144-155`; P8:183-193 |
| H43 | RBT-97 | Premise: "a correctly wired compass may not pay on these populations", resting on RBT-69's negatives. "12 of 12 robots pay." The gait verdict. | The negatives were the W4b sign installed on forward drivers. Only 6 of 12 are resolved at a = 32. `mechanism.py` tested motif − phantom instead of the phantom's own interval, so the falsifying GAIT verdict could not fire. The static decoy never depleted. g500's gain is sign-independent. | RBT-97 adversary rounds 1 and 2, with synthetic arms. | Code fix at `8713a0d`; rotated, depleting decoy. | n/a (run script). Stale at source: `docs/rbt-91-weight-scale-decision.md:80-87,260-265`. g500 is **open**. | INSTR / WORD | `runs/RBT-97/ADVERSARY.md:40-136`; `ADVERSARY-round2.md:26-163`; P8:510-581 |
| H44 | RBT-68, 86, 98 | Findings under `runs/` are auditable. | `runs/` was gitignored, so the reversed compass-gain finding lived only on disk. The allowlist admitted evidence by file extension ("by luck"). 177 claim-bearing files sat on unmerged branches. | RBT-63's audit could not reach its target. | `runs/**` allowlist; "commit by role" (`runs/README.md`); PR #73 ported the stragglers. | **On** (`.gitignore`). Per-generation genotypes are still excluded; RBT-113's runners needed `git add -f`. | STAT (record) | RBT-68 2026-09-13T14:16:16; RBT-86 2026-09-19T15:23:20; RBT-98 2026-09-26T12:38:04 |
| H45 | RBT-76, P7 | Every control in the vocabulary is negative. | Both false negatives (RBT-45's factor of two; RBT-61) passed noise-defending rules. `tests/test_analysis.py:24` passes under any sign or scale. `drive_straight_genotype` is a fixture in 6 test files and asserted in none. | RBT-76. | Six mechanisms: positive controls, manipulation checks, round-trip tests, asserted conventions, cross-ticket disagreement as blocking, a named adversary. | Mostly protocol. The round trips and the drive convention are in tests (PR #6). `README.md:523`: "smell model and world constants … consumed everywhere and asserted nowhere." | INSTR | RBT-76 2026-09-14T02:16:08; `README.md:505-531` |

### 1d. The arena A/A, founders and the held-out challenges (RBT-74 to RBT-105, paper 9)

| # | date / ticket | what was claimed | what it turned out to be | how it was caught | the fix | in code today | class | cite |
|---|---|---|---|---|---|---|---|---|
| H46 | RBT-74 | Morphological protection, paired by seed: +0.064. | One RNG stream fed both populations and the terrain, so **pairing by seed paired only the founders**. The paired SE (0.073) was worse than the unpaired (0.063). Opponent composition (a wheeled runaway) predicts +0.066. Rerun as RBT-85: −0.049. | The author's runaway split; the tp6zdu adversary. | Per-population streams, `spawn_streams()`. | **On (unconditional):** `evolution.py:580-600`. Pre-RBT-85 checkpoints are refused (`evolution.py:669`). `--protect-morphology` is default 0 (`cli.py:483`). | STAT / INSTR | `runs/RBT-74/REPORT.md:8,110-154` → `runs/RBT-85/REPORT.md:9-18`; `docs/runs/RBT-74-adversary.txt:5-33` |
| H47 | RBT-85 → RBT-96/108 | A 2 SE criterion; "could not see an effect inside ±0.074"; the arena's ±0.10 rule; predicted A/A RMS 0.040. | With four differences 2 SE is an 86% interval. The A/A RMS is **0.128** (3× the prediction), h = 0.178, and the ±0.10 rule is unsound at n = 4. At n = 16, h = 0.159, with a post hoc salt offset of +0.073 (p 0.0055) that is still **undecided**. | RBT-96 and RBT-108 A/A arms; adversaries. | Read against h, or use ≥ 9 seeds. | Protocol only. **RBT-111, which decides the offset, is parked.** | STAT | `runs/RBT-85/REPORT.md:33-37`; `runs/RBT-96/REPORT.md:56-95`; `runs/RBT-108/REPORT.md:63-92`; P9:780-837 |
| H48 | RBT-96 | `tests/test_rng_streams.py` pins salt 0; "a seed is an artifact of its platform". | The test compared `spawn_streams` with itself (a mutant passed 259/259). Cross-platform divergence is shown only for ARM against x86: 0 of 250 rows reproduce, and seed 201 is a runaway on one platform and a driver on the other. | Adversary F7, F9. | `tests/test_salt0_golden.py`; recommendation to record platform, CPU, MuJoCo and numpy in `config.json`. | Golden test **on**. The platform record is **never implemented** in `rabbitstew/`. | INSTR / PHYS | `runs/RBT-96/adversary/ADVERSARY.md:123-135`; `runs/RBT-96/REPORT.md:115-132,178` |
| H49 | RBT-84, RBT-90 | Oscillator drive is "a founding-population property"; median depth in [15, 26] is "a property of the search"; C "drive is an effector" FALSIFIED; "no champion beats its own gait". | Fate reverses in 5 of 14 replicates from identical founders (RBT-105). The depth band holds under a random-parentage null 98% of the time: it is **demography**. C is undecided (t +0.59). Champion paths are **layout-blind**, so the gait null holds by construction. | RBT-90 part-2 adversary; RBT-105. | Relabelled. | Wording only. | ECON / INSTR / WORD | `runs/RBT-90/PART2-VERDICT.md:15-16`; `runs/RBT-90/adversary-part2/ADVERSARY.md:50-88`; `runs/RBT-84/REPORT.md:218-242,309-312`; `runs/RBT-105/REPORT.md:42-47` |
| H50 | RBT-93, RBT-95 | Resumes and `--shift` work as documented. | Resume re-appended the restart generation. `--shift terrain=flat` left the terrain stream one draw behind, so start seeds were unpaired. `--shift food.regrow_delay=45` was accepted and did nothing. The stream tests ran at `birth_threshold=100`, so they exercised nothing. | RBT-93; RBT-95 adversary. | Truncate on resume; draw every season; refuse the shift. | **On (unconditional):** `evolution.py:679`; `ecology.py:406-408`. | INSTR | `docs/runs/RBT-95-adversary-shift.txt:3-15`; `runs/RBT-95/adversary_streams.py:3-5`; RBT-93 2026-09-19T16:04:43 |
| H51 | RBT-92 (C1) | "Class A, co-evolved wins … survives the shift and keeps its lead." | Class A returns A with **no event**: on the no-event base and on 23 of 25 placebo onsets. It measures the lead's level. The four "placebo replications" are one computation. | Readout adversary F2; paper-9 adversary F12/F29. | Report the class on the base and on placebo onsets. | Protocol only. | INSTR / WORD | `runs/RBT-92/REPORT.md:3-27` → `runs/RBT-92/readout-adversary/READOUT-ADVERSARY.md:62-119`; P9:228-239 |
| H52 | RBT-92, RBT-99 | "It never left the band on 6 seeds"; "recovered on 9/10". | A **d = 0 artefact:** a lifetime-mean axis (lag-1 autocorrelation 0.69) meets a 20-season hold before any divergence shows. Every seed leaves the band. | Readout adversary F4 (RBT-92), F7 (RBT-99). | Recovery registered but never read. | **Never fixed** (no valid hold rule). | INSTR | `runs/RBT-92/readout-adversary/READOUT-ADVERSARY.md:140-186`; P9:216,739 |
| H53 | RBT-92 on | "Both survive"; carriage L validated against a random cull. | **Survival is uninformative:** slots refill within the season and `alive` is recorded at season end, so alive = 60 in every season of all 37 runs. V3 (L's validation) fails by design for the same reason. | Readout adversary F2, F8. | "UNVALIDATED means unread." | **Never fixed:** it is how the ecology books births (an ECON allowance). The whole-lineage cull is not built. | ECON → INSTR | P9:213-215,699-701,740-741; `runs/RBT-92/REPORT.md:52-69` |
| H54 | RBT-99 (C2) | "Most of the verdict is the designed body's collapse"; the co-evolved body "paid back about 80%". | **Price arithmetic:** a 3.6× kJ gap predicts +0.689 against +0.371 observed. Net of price, the designed body recovered **more**. | Readout adversary F2, F3. | "Arithmetic first." | Protocol only. | ECON / WORD | `runs/RBT-99/readout-adversary/READOUT-ADVERSARY.md:74-165` → `runs/RBT-99/REPORT.md:18-43`; P9:326-342 |
| H55 | RBT-100 (C3) | "Arithmetic, and nothing beyond it"; the designed body's budget was "exceeded". | An unchanged designed fauna is insolvent, so the prediction is a **bracket** (+0.12 to +0.32). Class-D language was used for an A verdict. The printed `verdict_text` is false on 7 seeds. | Readout adversary F2, F4, F6. | The bracket; wording. | Wording only. `verdict_text` is **not patched** (`runs/RBT-100/REPORT.md:10`). | ECON / WORD | `runs/RBT-100/readout-adversary/READOUT-ADVERSARY.md:81-252`; P9:401-424 |
| H56 | RBT-101 (C4) | "The obstacles were about twice the tax on wheels … no response beyond the unchanged-gait arithmetic", from a registered solo probe. | In the arena, unchanged gaits predict −0.63 to −0.81. The clutter was a **4–7× tax on wheels**, so the co-evolved income lead in the default random-terrain economy was **bought wholly by the clutter**. | Readout adversary F2 (`probe_arena.py`, `probe_refund.py`). | "Arithmetic in the axis's own setting." | Protocol only. `ecology` defaults to `--terrain random` (`cli.py:572`). | PHYS / ECON | `runs/RBT-101/readout-adversary/READOUT-ADVERSARY.md:87-195` → `runs/RBT-101/REPORT.md:16-26`; P9:457-478 |
| H57 | RBT-101 → RBT-110, RBT-107 | "The first resolved non-arithmetic effects in phase 2" (+0.27, C4-specific); "the pattern grows with depth". | Equally large on the old terrain (new − old +0.024); 73% of it is the cull20 turnover null; net +0.07, NOT DECIDED. "Grows with depth" rests on seed 801. The H-REP designed decline is not supported at T + 800. | RBT-110 readout adversary F3; C4null; RBT-107 H1. | Read the old world too; only new − old is a response. | Protocol only. | INSTR / WORD | `runs/RBT-110/C4null/READOUT.md:47-87`; P9:62-79,609-648; `runs/RBT-107/h1/REPORT.md:17-43` |
| H58 | RBT-107 H-REP | The analyst's per-fauna DES "changes no scored rule". | It was switched after the data existed and moved SUPPORTED → NOT SUPPORTED (IUT p 0.0171 → 0.0427). The docstring and code se disagree at n = 19. Seed 29 (co-evolved fauna extinct) decides it. | hrep readout adversary F1, F2, F4. | Reverted to registered; "fragile". | n/a | STAT | `runs/RBT-107/hrep/REPORT.md:7-9,28-66`; `runs/RBT-107/hrep/adversary/ADVERSARY.md:3-132` |
| H59 | RBT-89 on | Pre-registered noise r = 0.077; the A/A 0.077 used as the paired scale; sign guards. | The realised r was 0.104–0.183, so class B was unreachable. The paired scale is 0.091–0.123. The 8/10 guards replicate as a coin flip. | Adversaries across RBT-92, 99, 100, 101. | Jitter the guard; use the paired scale. | Protocol only. | STAT | `runs/RBT-89/window_sd.py:4-8`; `runs/RBT-92/REPORT.md:84-88`; P9:268-277,747-754 |
| H60 | RBT-105 | "History decides the fate"; A/A 0.132 is "a one-directional bound". | R1 licenses only q > 0.1; the founders' ICC is 0.72. The spread does not grow, so it is not a bound. | Readout adversary F3, F8. | Wording. | Wording only. The `aa_spread.txt` header still reads "UPPER BOUND". | WORD / STAT | `runs/RBT-105/readout-adversary/READOUT-ADVERSARY.md:129-163,236-287`; P9:846-865 |

### 1e. Paper 10's strand (RBT-102 to RBT-112)

| # | date / ticket | what was claimed | what it turned out to be | how it was caught | the fix | in code today | class | cite |
|---|---|---|---|---|---|---|---|---|
| H61 | RBT-102 | "The routed motif's structure is not carried at all", read as an answer about selection. | A matched drift null reads zero 81% of the time. The p_u used the wrong parents (5.5× off). About 184,000 genomes are needed. | Adversary `replay_null.py`. | "Not informative about selection." | n/a | STAT | `runs/RBT-102/adversary/ADVERSARY.md:70-148` → `runs/RBT-102/REPORT.md:7-20,130-141` |
| H62 | RBT-103 | Worlds "on flat"; P-801 "dense, patchy, regrowing"; the size gap follows density or regrowth; "pays on 8 of 10". | Terrain is random everywhere and P-801 does not regrow within a bout. The world control ran with no pre-posted attribution rule (exploratory). 8/10 sits on the bar. | Adversary F3–F5. | Errata list. | Wording only. Commit messages `c42e4f7` and `935bcbf` stay wrong. | ECON / WORD / STAT | `runs/RBT-103/REPORT.md:15-91` |
| H63 | RBT-104 | "The evolved hosts mask an installed compass"; a bias gate. | **VOID by design.** The install control never applied the arm's `--link-scale 8`, so a default-scale compass is invisible in a ×8 host (drive saturated on 91–96% of ticks). A pre-arm check flagged as F8 was not run. | Readout adversary F1–F4. | Every per-arm control is run on the arm's own founders and shown able to pass. | Protocol only. `--link-scale` is default 1.0. The question is unanswered. | INSTR / OP | `runs/RBT-104/REPORT.md:38-60`; `runs/RBT-104/readout-adversary/READOUT-ADVERSARY.md:11-152`; P10:243-271 |
| H64 | RBT-106 | The HELD null's false-positive rate is 6.0%; the patchy world is "harder"; `--food-patches 3` changes only the prize: "the size of the prize decided". | Crossover hands over the mate's whole global brain: 15.0%. RBT-103's world was two fields (`regrow_delay 45` silently switches on persistent arenas). The one flag also **raised births (10/10), income and depth**. Kinesis passes the decoy (26 of 70 unselected bodies). | Design adversary `null_xover.py`; h-adversary H8; paper-10 adversary R2-F1. | `held.py` scores planted-rooted k; COMPASS requires FD attribution; the ruled sentence. | Scripts only. The registered label "the larger prize held…" stays. | ECON / OP | `runs/RBT-106/adversary/ADVERSARY.md:105-160,236-293`; `runs/RBT-106/PREREGISTRATION.md:35-51`; `runs/RBT-106/h-adversary/ADVERSARY.md:221-242`; P10:347-365 |
| H65 | RBT-112 | "The operator is not the stall"; the treatment is "the planted unit's bias walk". | `--global-bias-sigma 0` freezes **all** global biases, host included, and raised income +0.160 (SE-Z failed). Under S = 0 the best lines do carry and use the compass (5 COMPASS lines against 0). | Readout adversary A3; paper-10 adversary F3, F4. | Gloss; "host and planted". | **Flag, off by default** (`cli.py:487,559`). The registered `readout.txt` keeps the bare label. | OP / WORD | `runs/RBT-112/READOUT.md:25-64`; `runs/RBT-112/readout-adversary/ADVERSARY.md:33-43,154-203`; P10:436-468 |
| H66 | RBT-112 → paper 10 → progress report | HP's HELD on 9 of 10 implies s ≈ 0.39; "selection outran the erasure"; "2–3% survives 16 generations"; "about 2 in 10,000". | The recursion's HELD fires below the balance point (s 0.089 gives about 2 of 10), so no s was estimated. 16-generation persistence is 1.3%. 2.17e-4 is the count rule's size. | Paper-10 adversary F6. This audit found the progress report residue. | Paper fixed. | **Not fixed in the published progress report** (`docs/progress-reports/2026-09-27/index.html:279,290,292`). By rule, corrections go in report 2 (`docs/progress-reports/README.md:12`). | WORD | P10:506-511; `docs/paper-10/adversary/PAPER-ADVERSARY.md:120-133` |
| H67 | RBT-112 | The pre-launch HELD "positive control". | Arithmetic reachability at k = n, not passability. | Readout adversary. | Programme rule (12:20): a modelled or simulated positive at a stated s. | Protocol only. | INSTR | `runs/RBT-112/readout-adversary/ADVERSARY.md:47,111-130`; P10:565-570 |

### 1f. Today: RBT-113, RBT-117, RBT-120

| # | date / ticket | what was claimed | what it turned out to be | how it was caught | the fix | in code today | class | cite |
|---|---|---|---|---|---|---|---|---|
| H68 | RBT-113 | The holistic down line's work rose "fiftyfold", and b_down ≈ 2 × b_up is read as a response to selection. | **A motor-capacity allowance.** 45.9× the founders' work is real, full-throttle actuation (dt-converged, 94% torque work, no explosions). It is bought by growing Σgear about 10×, 98% of it on ball joints: Σgear/(4 × mass) is 3.66 against the Pioneer's 1.76, so the work ceiling is about 2×. Gear = `motor_strength` × the **heavier** connected mass, **per driven DOF** (up to 3 on a ball joint), and nothing caps it. | Readout adversary `probe_work.py`, `probe_gear.py`. | Wording (M3, S2); S4 → RBT-120. | **Never fixed:** `world.py:202-223` unchanged; RBT-120 is `todo`; no gear or power budget exists. | PHYS | `runs/RBT-113/readout-adversary/ADVERSARY.md:78-101,184,220-238`; `probe_gear.txt:1-9`; `runs/RBT-113/REPORT.md:93-109`; RBT-120 |
| H69 | RBT-117 | **HOLISTIC RESPONDS MORE**, d +0.77 [+0.40, +1.13], p 0.0015. The registered prediction was the opposite (d ≈ −2.8). | **Entirely H68.** The up half is a tie (+0.107, p 0.53). Food alone favours the designed body (−0.419). With the D line's work capped at the designed body's: −0.022 (p 0.86). The power model was an unbounded Gaussian: the designed body hit a floor at 95% of its fixed motor ceiling while the holistic body escaped through gear. It is not evidence for reason (b): the holistic founders were the *less* variable. | Readout adversary `rederive.py`. | M1: the mechanism sentence must accompany the verdict. | Wording only, and in REPORT.md only. **`runs/RBT-117/compare.txt:37,44` prints the bare verdict.** | PHYS / STAT | `runs/RBT-113/REPORT.md:124-136,197-208`; ruling RBT-113 2026-09-27T19:49:36 |
| H70 | RBT-113 (design, then readout) | The up line "learns to eat, and its food rises 20-fold"; "a real gain in foraging". | **Coverage.** Blind variants eat 0.913 and decoy variants 0.934, against 0.854 intact. 61% of U-line members carry no food sensor. Ground covered rises about 6×, items per cell about 1.4×. It is "the blind mower (paper 6) evolving from random founders under imposed selection". | Readout adversary `probe_food.py`. | M2: "learns to move, and eats by covering ground". | **Never fixed in the world:** eating is any geom within `eat_radius` 0.35 m (`simulation.py:465-475`), and eaten food regrows instantly at a fresh random spot by default (`FoodConfig.regrow=True`, `regrow_delay=0.0`). | ECON / WORD | `runs/RBT-113/design-adversary/ADVERSARY.md:65-66`; `runs/RBT-113/PREREGISTRATION.md:341-344` → `runs/RBT-113/readout-adversary/probe_food.txt:1-13`; `REPORT.md:84-91` |
| H71 | RBT-113 N1 | (Nothing claimed.) | **Contact penetrations of 0.27–0.57 m** (holistic U 271 mm; designed founders 416 mm; designed U 573 mm, with one exploded member at 12,069 m/s). | Readout adversary note. | None: "worth a look for overlapping geoms at build time". | **Never fixed; no ticket** (only RBT-121 names it). | PHYS | `runs/RBT-113/readout-adversary/ADVERSARY.md:242-244`; `probe_work.txt:6,13,34,41` |
| H72 | RBT-113 design | Net yield reports what responded; the controls pass; RESPONDS is the finding; "median work is 4 kJ". | Net yield hid a work response (D1). Two controls could not fail (D3). RESPONDS was near-certain by construction (D5). The figure was 4 J. `--line` without `--truncation` is silently ignored. | Design adversary D1, D3, D5, D10. | Endpoint `decompose.py`; §7.6/7.7 can-fail tests; headline reworded. | Scripts only. The `--line` warning was **declined** ("would touch `rabbitstew/`"): never fixed. | INSTR / STAT | `runs/RBT-113/design-adversary/ADVERSARY.md:48-228`; `controls_can_fail.txt:5,10` |
| H73 | RBT-113 readout | "Responded in both directions, on every seed"; the D line's "food stayed where it was". | b_up is negative on designed seeds 8 (default) and 8 and 9 (Z), and on holistic Z4. The D line eats about 2× the control. | Readout adversary M4, N2. | Amendment `7f5a704`. | Wording only. | WORD | `runs/RBT-113/readout-adversary/ADVERSARY.md:188-195` → `runs/RBT-113/REPORT.md:96,172-175` |

### 1g. Wording and propagation residue (corrected in one place, standing in another)

These are not new incidents. Each is a correction that exists in one document while the superseded text still stands in another. A future reader quoting the second document gets the old claim.

| # | superseded text still standing | corrected at |
|---|---|---|
| H74 | P7:309-312 and `runs/sim-audit/CHAOTIC-DOC.md:166` still give the taxis-specific **+0.723 (+48%)**, from a phantom +0.163 with no script. | P8:226-231,724-725; `runs/RBT-72/rederive.txt:17-18` |
| H75 | P5:189,220,414 and P6:171 quote heritability **0.246**; P6 and `docs/foraging-world.md:226` quote the **1.3%** crossed rate; P6:112-118 says "chassis nose alone"; P5:303-305 gives the **σ(d) law**; `docs/rbt-91-weight-scale-decision.md:54,80-87,202-203,260-275` keeps withdrawn and stale text. | `docs/foraging-world.md:282,325`; H29, H37, H40 |
| H76 | Registered outputs keep bare labels: `runs/RBT-117/compare.txt` ("HOLISTIC RESPONDS MORE", H69); `runs/RBT-112/readout.txt` ("the operator is not the stall", H65); `runs/RBT-100` `verdict_text` (H55); `runs/RBT-105/aa_spread.txt` ("UPPER BOUND", H60). | By rule, registered code is not edited after the readout. Nothing flags these files at the point of reading. |

---

## 2. Classification

### 2a. Counts

Each incident is counted under its **primary** class, the first one listed in its row. H74–H76 are propagation residue and are not counted.

| class | primary count | incidents |
|---|---|---|
| **INSTR** (instrument or measurement) | 23 | H4, H20, H21, H24, H29–H34, H37, H38, H41, H43, H45, H48, H50–H52, H57, H63, H67, H72 |
| **STAT** (statistical or registration, including record) | 14 | H6, H8, H9, H22, H23, H25, H27, H36, H44, H46, H47, H58, H59, H61 |
| **ECON** (economy or world) | 12 | H14, H16–H19, H49, H53–H55, H62, H64, H70 |
| **PHYS** (physics or body model) | 11 | H1, H2, H11, H12, H15, H28, H35, H56, H68, H69, H71 |
| **WORD** (overclaiming in wording) | 7 primary; a **secondary** class in about 25 more | H5, H10, H26, H42, H60, H66, H73 |
| **OP** (operator or GA) | 6 | H3, H7, H13, H39, H40, H65 |
| total | 73 | |

**The spine of the record is instruments.** Paper 7 counts 6 of its 9 incidents as "projection instruments" (P7:550), and P8 counts 10 of 14. **Physics and economy allowances are fewer, but each decided a headline:**
- the arena result (H1, H2);
- the C4 lead (H56);
- RBT-117 (H68, H69);
- "foraging" three times over: papers 5–6, RBT-113 and RBT-106 (H70, H21, H64).

### 2b. Paper 7's instruments, placed

Paper 7, *Five instruments, five wrong readings*, catalogues nine incidents (P7:550: "six of the nine… E1–E5 and E8") and adds a tenth, the 0.70% rate, in its limitations (P7:903-914).

| P7 incident | here |
|---|---|
| A1, the weight class | H1 |
| A2, the spawn drop | H2 |
| E1, unpaired SE on paired lesions | H22 |
| E2, the throttle passing the compass criterion | H33, H34 |
| E3, seasons as the unit of search | H39 |
| E4, `sensor_influence` | H30 |
| E5, the transposed drive | H28, H29 |
| E8, chassis yaw in the positive control | H35 |
| E9, direction of travel as a free parameter | H35 |
| the tenth: the depth-4 rate | H31 |

**Paper 7's own count is inconsistent.** P7:48 says "six of those eight", while P7:568 says "Eight of the nine"; the title says five. This audit takes §4's "six of nine" as the paper's claim.

---

## 3. The patterns

### P1. Evolution finds the model's allowance before the task

This is the proposal's reason (a) in its perverse form. It has happened at least six times, and **in every case the score could not see it**:

| incident | the allowance |
|---|---|
| H1 | mass |
| H2 | potential energy at spawn |
| H11 | a crank flail through ground contact |
| H68 | gear per driven DOF keyed to the heavier mass |
| H70, H21 | coverage paid as foraging |
| H56 | a clutter tax the wheeled body pays and the lump does not |

Each was caught only by **measuring the body away from the score**: alone, from rest, lesioned, blind or decoy-fed, with work decomposed, or with a gear audit.

**None was caught by a design review before the run.** H68 had been live in `world.py` since the arena era. `README.md:125-126` documents "gear scales with the larger connected mass" as a feature, and nobody ever discussed it as an allowance.

### P2. Fixed as a flag, not as structure

Nearly every simulator-level fix landed opt-in, and "byte-identical when off" is the house rule (RBT-120's own spec repeats it):

| fix | default |
|---|---|
| `--mass-budget` | None (H1) |
| `--conventional-topology` under `evolve` (H3) | off |
| `--draws` / `--heading-curriculum` (H9) | off |
| `--smell` (H20) | `sum` |
| `--global-bias-sigma`, `--link-scale` (H40, H65) | off |
| `clear_spawn_layout` (H16) | persistent worlds only |
| population carriage (H38) | Python-only opt-in |

**Only four fixes became structural:**
- the settle (H2);
- the exploder forfeit (H15);
- per-population RNG streams (H46);
- the resume and shift guards (H50).

**Every committed run since the arena sets the mass budget by hand** (439/439 configs). So the discipline lives in the run scripts, not the simulator: a new script that forgets `--mass-budget` silently reopens H1.

**Protocol-only fixes dominate the instrument class:**
- the 64-paired-seed rule (H22);
- trajectory nulls (H21);
- the direction of travel (H35);
- "arithmetic first" (H54);
- placebo onsets (H51);
- "shown able to pass" (H63, H67);
- the bracket (H55).

They are in `README.md:505-531` and the papers. **None is asserted by code or a test.**

### P3. Instruments that could not fail

This is the most common single mechanism. Each of the following could return only one answer, or returned its answer regardless of the truth:

| incident | the instrument |
|---|---|
| H33 | a criterion satisfiable by mobility alone |
| H21 | a point-robot floor |
| H30 | an absolute, clipped sum |
| H31 | a sign test named "gradient-dominant" |
| H32 | a depth-1 term that is zero on the only writable motif |
| H37 | a free-running lesion |
| H43 | a gait branch that could not fire |
| H49 | layout-blind paths |
| H51 | class A with no event |
| H52 | a d = 0 hold |
| H53 | `alive` under same-season refill |
| H61 | zero carriers under drift |
| H63 | an install control at the wrong scale |
| H67 | reachability dressed as passability |
| H72 | D3's controls |

**Adversaries caught almost all of them, and mostly after the data.** The positive-control rule (RBT-76) is the right response, but it is enforced only by adversaries.

### P4. One flag, several channels

"Change one parameter" repeatedly changed more than one causal channel:

| incident | what the flag also moved |
|---|---|
| H64 | `--food-patches 3` also raised births, income and depth; `regrow_delay` silently switched to persistent arenas |
| H65 | `--global-bias-sigma 0` froze the host's biases too |
| H63 | `--link-scale 8` also saturated the host |
| H19 | `--duration` also changed the spawn reset |
| H17 | the work-cost coefficient decided viability before evolution started |

**Every world or operator manipulation needs a side-effect check** (income, births, depth, saturation) registered beside it, as RBT-112's SE-Z was. SE-Z is the one that caught it.

### P5. Small n reads high, and one seed carries claims

- **Everything re-read at larger n moved down** (H22, H23, H27; RBT-19's 58%).
- **Single seeds carried claims:**

  | seed | carried |
  |---|---|
  | 801 | "grows with depth" (H57) |
  | 29 | H-REP (H58) |
  | 201 | the A/A RMS (H47) |
  | 805 | the only COMPASS line (H64) and the only RBT-112 HELD |
  | 3 | RBT-107's "nearly blind" |

- **Noise was under-predicted three times over:** A/A RMS 0.040 against 0.128; r 0.077 against 0.104–0.183; null RMS 0.13 against 0.20–0.27. Power models ignored floors and ceilings (H69).

### P6. Corrections do not propagate

The house style appends a correction and keeps the original, which is right for a record. But downstream documents keep quoting the superseded figure (H74–H76):
- registered outputs keep bare labels;
- the published progress report carries a withdrawn reading (H66);
- `compass-spike/REPORT.md` has no erratum at all.

### P7. The record can lose its evidence

- `runs/` was gitignored (H44), and admission to git went by extension.
- Evidence was stranded on unmerged branches, and lineages were never committed (RBT-80; 801's neutral control).
- Cross-platform divergence (H48) means a seed is not a full description of a run.
- **The platform is still not recorded in `config.json`.**

### What an adversary caught that the design should have prevented

The adversary process worked. Nearly every row above has an adversary or self-retraction in its "caught" column. But the following were **knowable before any arm ran**, from the code or from a ten-minute pre-arm check:

1. **The motor-capacity allowance (H68).** `world.py:202` is one line. A pre-registration that printed Σgear/mass per line (now RBT-120's reporting rule) would have exposed it at generation 0. Its consequence, H69, is a registered confirmatory verdict that has to travel with a sentence that neutralises it.
2. **Coverage as foraging (H70).** Papers 5 and 6 had already named the blind mower. RBT-113's pre-registration still said "learns to eat" (`PREREGISTRATION.md:341-344`) with no blind or decoy arm registered.
3. **RBT-104's VOID (H63).** Design-adversary F8 flagged it, and the registration still priced P(VOID) at 0.15 (`runs/RBT-104/adversary/ADVERSARY.md:237-250`).
4. **Survival pinned at capacity (H53).** Same-season refill is how `ecology.py` books births. The V3 validation was designed against a column that could not move.
5. **The shared RNG stream (H46).** "Pairing by seed" was asserted without a test that the pair shared anything but founders.
6. **The patchy flag's side effects (H64).** Births and income are printed by every run; nobody registered them as side effects of the world change.
7. **The transposed drive (H28).** It was invisible at the interface. The fix, `drive_commands()` plus a test that the axes are antiparallel, is the model for making a convention structural.

---

## 4. Candidate rules for a fair experiment

Each rule is traced to the incidents that motivate it. Rules marked **[code]** can be enforced by the simulator or a test. Rules marked **[protocol]** need a registration field and an adversary check.

**R1 [code]. Budget every capacity an evolving body can grow, not only mass.**
- Cap, or at least print, Σgear, Σgear/mass, the actuated DOF count and the free-spin work ceiling per line. Treat sensor count, joint limits and damping the same way.
- The designed body's values must sit inside the budget, unchanged.
- *Motivated by:* H1, H68, H69, and RBT-120's own audit list.

**R2 [code]. Make the fairness defaults the defaults.**
- A run that pits evolved against designed bodies should refuse to start without a mass budget and a motor budget. Alternatively, `evolve` and `ecology` should default to them, with an explicit `--no-…` escape.
- The byte-identical-when-off convention is right for reproducing old runs. It is wrong as the default for new registrations.
- *Motivated by:* H1 (439/439 set it by hand), H3, H9, P2.

**R3 [code/protocol]. Behaviour must be shown by a manipulation the allowance cannot pass.**
- Any "foraging" or "perception" claim registers **blind, decoy and lesion arms**, with a positive control that the instrument can detect at the n in use.
- "Learns to eat" requires the intact − blind difference, not the yield.
- *Motivated by:* H21, H33, H34, H37, H70, H64 (kinesis passes the decoy).

**R4 [code]. The world must make perception pay more than coverage, and show it.**
- Before a world is used for a perception claim, register a **census**: random and blind bodies against sensing bodies, a density × eat-radius × path check, and the ratio of items per cell to cells covered.
- The habitability calibrator (RBT-32 to RBT-36) was specified for exactly this and never built.
- *Motivated by:* H70, H21, H17, H19, papers 5–6.

**R5 [protocol]. Decompose every endpoint into its currencies.**
- Report food and work, or income and price, separately. State the unchanged-population arithmetic (the price, the insolvency bracket, the clutter tax) **in the setting the axis is read in**, before reading any response.
- *Motivated by:* H54, H55, H56, H68, H72 (D1).

**R6 [protocol]. A single-flag manipulation registers its side effects.**
- Income, births, depth, host saturation and fauna solvency are printed for the treatment against the control, as RBT-112's SE-Z was. A side effect that moves demotes the verdict's sentence to "not the only difference".
- *Motivated by:* H64, H65, H63, H19.

**R7 [protocol, with a code hook]. Every control must be shown able to fail, on the arm's own founders, before launch.**
- A modelled or simulated positive at a stated effect, not arithmetic reachability.
- Placebo onsets and no-event bases for any class rule.
- *Motivated by:* H51, H52, H53, H61, H63, H67, H72 (D3), H43.

**R8 [protocol]. Nulls are matched: same parents, same operator and crossover, same demography.**
- A drift or turnover null (cull20) beside every event effect; the old world beside the new; a trajectory-preserving null beside every rate.
- *Motivated by:* H21, H25, H57, H61, H64 (crossover), H49 (random-parentage depth).

**R9 [protocol]. Measure the body away from the score before reading the score.**
- Alone, from rest, on fresh draws, and with the population's free parameters (direction of travel, drive sign) measured and stated first.
- *Motivated by:* H1, H2, H4, H9, H11, H35.

**R10 [protocol]. Power at the realised n, from a model bounded by each body's floor and ceiling.**
- Noise from an A/A of the same design, not a prediction.
- No verdict from a count sitting on its bar; say what one influential seed does.
- *Motivated by:* H47, H59, H69, H57 (seed 801), H58 (seed 29), H62, H22.

**R11 [protocol]. No change to a scored rule after data exist.**
- Where a rule was changed, the registered form is scored and the change is printed as a sensitivity.
- The readout prints the registered-code output **with** any ruled caveat attached, so a bare label cannot be quoted.
- *Motivated by:* H58, H62 (RBT-103's world control), H76.

**R12 [code]. Assert conventions and instruments in tests.**
- Drive axes (as `tests/test_pioneer_drive.py` does); the smell model and world constants (`README.md:523`); gear and mass per body class; the eat rule.
- A derived metric ships with a round trip and a positive control (`steering_terms`, `signed_influence` at depth 1, not 4).
- *Motivated by:* H28, H30–H32, H45, H20.

**R13 [code]. Record what a replay needs.**
- Platform, CPU, MuJoCo and numpy versions in `config.json`.
- Genomes at birth (already on by default in the ecology).
- Commit by role.
- *Motivated by:* H44, H48, H25 (801's neutral control never committed).

**R14 [protocol]. Wording is bounded by the scored result.**
- Registered labels are always quoted with their ruled gloss.
- Counts ("8 of 10", "12 of 12") are quoted with intervals.
- "First", "every", "wholly" and "the prize decided" need their own evidence.
- *Motivated by:* H42, H43, H57, H64–H66, H73, H74–H76.

**R15 [code]. Guard silent no-ops and silent mode switches.**
- `--line` without `--truncation`; `--resume` crossing `--locomotion-phase`; `--founder-model` under survival or lexicase; a shift of a field fixed at construction (now guarded).
- *Motivated by:* H8, H13, H50, H72.

---

## 5. Open risks

### 5a. Fixes that exist only behind flags, or not at all, that current experiments may not set

| risk | status in code at `152e2df` | who is exposed |
|---|---|---|
| **Motor capacity (H68)** | **Never fixed.** `world.py:202-223`: gear = 4.0 × the heavier mass per driven DOF, up to 3 per ball joint, not bounded by `--mass-budget`. RBT-120 is `todo`. | Every holistic-against-designed comparison: RBT-116, RBT-118, any re-read of RBT-117; also any holistic "work" or "locomotion" result since the arena. |
| **Coverage paid as foraging (H70)** | **Never fixed.** Any geom within 0.35 m eats (`simulation.py:465-475`); instant regrowth at a fresh random spot is the default. | Every foraging-yield claim: paper 5's "an economy with no fitness function evolved locomotion" stands as *locomotion*; any "foraging" or "perception" reading of yield; RBT-113 b_up. |
| **Contact penetration (H71)** | **Never examined**; no ticket. 0.27–0.57 m in low-work groups, one exploded designed member. | Unknown. It may interact with H11 (the crank flail through ground contact, whose contact-artefact test was never run). |
| **Mass budget (H1)** | **Flag, off by default** (`cli.py:431,462,571`); set by hand in 439/439 configs. `inspect` ignores it. | Any new run script that omits it. |
| `--conventional-topology` under `evolve` (H3) | **Flag, off by default** (`cli.py:467`); on under `ecology`. | New arena runs. |
| Fresh-draw evaluation, `--draws`, `--heading-curriculum` (H9) | **Flags, off by default.** | GA fitness read at face value. |
| Opponent sensors as target oracle in solo evaluation (H12) | **On by construction** (`simulation.py:701`). | Solo target-task results (paper 4's labs), and whatever `run_solo` evaluates under the `paper` or `rich` brains. |
| `--founder-model` under survival or lexicase (H8) | **Never guarded** (`cli.py:275-277`). | GA drift-versus-selection claims. |
| Survivor re-logging in heritability (H7) | **Never fixed** (RBT-44). | GA heritability under `--survival`. |
| Shared-season inflation of heritability (H25) | **Never fixed in code.** The persistent-world share is never measured. | Paper 5's heritability range, and the 0.246 still quoted. |
| Survival and carriage under same-season refill (H53) | **Never fixed.** | Every challenge readout's "survives" and carriage L. |
| Direction of travel (H35) | **Protocol only.** | Any installed-circuit or compass claim on the Pioneer; undefined on holistic bodies (`docs/founder-diversity.md:46-57`), which matters for RBT-116. |
| `signed_influence` defaults to depth 4 (H30, H31) | **On, divergent default** (`analysis.py:187`), emitted in standard output (`analysis.py:678`). | Anyone reading `analysis.json`'s `signed_influence` as a gain. |
| Platform record (H48) | **Never implemented.** | Cross-machine replication of any seed. |
| `--line` without `--truncation` (H72) | **Silently ignored.** | Future selection-response arms. |

### 5b. Past results to re-read under today's knowledge

1. **RBT-117's verdict** (HOLISTIC RESPONDS MORE) has to be re-run under a motor budget before it can count toward reason (b). RBT-120's optional re-run (4 arms, about 2 h) is the cheapest decisive step.
2. **RBT-113's holistic b_down and b_div**, and any holistic "work" figure. The holistic b_up is coverage (H70), so the benchmark's holistic number means "can learn to move", not "can learn to forage".
3. **Paper 5's headline.** "The evolved bodies out-ate the designed one" rests on yield in a world where coverage is foraging (H70), plus a work-cost coefficient that decided viability (H17), and it reverses in crowds (H26). The blind-mower reading is already the paper's; what needs re-reading is **any sentence that credits the holistic lead to more than cheaper coverage**.
4. **The C1–C3 baseline co-evolved lead** (paper 9) was bought wholly by clutter on random terrain (H56). Since `ecology` defaults to random terrain, **every ecology comparison of the two faunas on random terrain carries a wheel tax**. RBT-118's ecological head-to-head must pick its terrain knowing that.
5. **The motor allowance in older holistic results.** Every holistic body since the arena ran under the same gear rule. The arena's final "fixed body wins every seed" is unaffected in direction: the allowance favours the holistic side, and it still lost. But **any holistic-favourable result is suspect** until Σgear/mass is printed: RBT-107's paired half, RBT-110's C4 residual (already NOT DECIDED), and the C1–C3 residuals.
6. **Seed 403's crank flail (H11)** and the N1 penetrations (H71) together raise the possibility of a contact exploit in the holistic locomotion record. **The test RBT-37 declined should be run** before any holistic locomotion result is used as evidence of a body-specific strategy.
7. **RBT-71's seeds 801–806** ran before the exploder forfeit (H15). They are a different economy from today's head.
8. **The progress report of 2026-09-27** carries H66's withdrawn reading. Report 2 (RBT-119) must correct it, and must carry the RBT-117 mechanism sentence if it reports RBT-117 (RBT-119 item 6).
9. **RBT-111** (the arena salt offset) is parked. Arena verdicts should keep citing h = 0.159 with the offset open (H47).

---

*Auditor D, RBT-121. Read-only: nothing under `rabbitstew/`, `tests/`, `scripts/` or any scored file was changed.*
