# RBT-129 designed PAYS legs: readout plan (pre-data)

*Written and committed before any output of either leg was opened. No `ckpt/rbt-129-stage0-pays-*` branch had been
fetched or read when this commit was pushed; its commit timestamp is the audit trail. The legs ran from `29ab80b`
(`runs/RBT-129/lanes/pays-prize/` and `pays-steps/`). The inputs read so far are the registered and ruled texts cited
below, the pinned tools' source at `29ab80b`, and the cells' `worlds/config/<id>/config.json` at `29ab80b` (inputs,
not outputs).*

## 1. The rule being read (verbatim)

DESIGN §6.3, "The world layer PAYS, per fauna":

> at that cell, the fauna's nose step pays at least comparably to a speed step, and its planted prize (designed:
> RBT-106's at a = 6; holistic: the G8(c) plant at a = 6) has a lower bound > 0. A point takes PAYS from its (L, s, c)
> cell.

For the designed fauna, per cell: "the fauna's nose step pays at least comparably to a speed step, and its planted
prize (designed: RBT-106's at a = 6) has a lower bound > 0".

DESIGN §5.1 names the instruments: "RBT-125's world-gate harness: a nose step against a +25% speed step on real
designed hosts, and RBT-106's prize at a = 6", "under the sweep's own block (`--fair` and the ruled eating rule)".

## 2. "At least comparably": operationalised from registered and ruled text only

**Designed nose step "pays at least comparably" at a cell ⇔ the registered §B line reads NOSE LEADS or COMPARABLE.**

| element | fixed by | text |
|---|---|---|
| the labels and their order | RBT-125 `gate/REGISTRATION.md`, amendment 1, A1.4 (supersedes §B's original COMPARABLE) | NOSE LEADS: 95% lower bound of (nose − speed) > 0; SPEED LEADS: 95% upper bound < 0; COMPARABLE: "equivalence: two one-sided t tests at 5%, i.e. the 90% interval inside ±δ, with δ = 0.10 items per season"; TIED, UNRESOLVED otherwise. Implemented as `reading()` in `steps.py` at `29ab80b` (blob `4834838`), tested in that order |
| "at least comparably" = COMPARABLE or NOSE LEADS | RBT-125 `readout-adversary/ADVERSARY-PASS2.md` §3 ("For RBT-129's PAYS rule (COMPARABLE or NOSE)"); RBT-116 `design-adversary/ADVERSARY-RBT132.md` S7(b) ("The R4 test (COMPARABLE or NOSE) matches RBT-121 R4's text … It is not 'beats'"); RBT-125 `gate/READOUT-BC.md` §B scope, as amended under the coordinator's ruling ("The sweep's PAYS rule uses the same labels (COMPARABLE, NOSE LEADS) on its own legs") | — |
| the line | RBT-125 REGISTRATION §B ("The w 3 → 3.4 step … is the registered line. The first nose and w 1 → 1.4 are reported beside it") and A1.4 ("**The per-unit comparison is the registered line.** The raw comparison is printed beside it") | the `STEP <cell> \| nose step w 3 -> 3.4 \| … \| vs per-unit speed (n k): m [lo, hi] READING` field |
| per-unit speed | A1.4 | per host, (items of speed@w3 − items of w3) × 0.25 ÷ (r − 1); hosts with r < 1.10 leave the line and are counted |
| the world | DESIGN §5.1 | each cell's own `worlds/config/<id>`; at s = G that is G = 2.5, τ = 2 s; at s = L the legacy reading. The line is read in each cell's own world; RBT-125's "at G = 2.5" names the gate's world, not a condition on these cells |

**Consequences fixed now:**
- SPEED LEADS and TIED, UNRESOLVED do **not** pay at least comparably.
- A line printed `NOT READABLE` (fewer than 2 hosts at r ≥ 1.10), a missing `STEP` row, or a crash: the steps
  condition is **not met**, reported as NOT READABLE, never as a negative finding about the world.
- The raw-speed comparison and the w1 and first-nose lines are printed beside, and are descriptive. They never decide
  the call.
- The nose step's own sign is **not** a condition of the registered rule (NOSE LEADS is a difference). See §4 for what
  is printed beside it instead.
- A1.4's power statement stands: "The expected reading is TIED, UNRESOLVED, unless one step leads by about 0.17 or
  more." No COMPARABLE is expected anywhere; that would be a power result, not evidence that the steps differ
  (ADVERSARY-PASS2 §2).

I judge the registered text to fix "comparably" without ambiguity, so this plan proceeds without a pre-data ruling.

## 3. The prize's lower bound

**The prize condition at a cell ⇔ the RBT-106 prize at a = 6 has a t(9) 95% lower bound > 0 over all ten
populations.**

| element | fixed by |
|---|---|
| the statistic | RBT-125 REGISTRATION §A ("per population, the mean over its signed bodies of (motif − base) items per season. Across populations, the mean with a Student t(n − 1) 95% interval"); computed as `prize_readout.py`'s `prize()` and `t_int()` |
| the per-population inputs | each `prize/<seed>.txt`'s per-body lines `g<gen> ±1 <base> \| <delta>` (the lines `prize_readout.read()` parses), in a file that carries its `ROW` |
| all ten | A1.2: "PASS is read over all 10 populations … A population with no readable ROW counts as prize 0". Missing populations are listed |
| the lower bound | the lower end of the two-sided t(9) 95% interval, as §A's PASS rule reads it ("the prize's t lower bound is > 0") |

- **The decoy is not part of the PAYS rule**, whose text names only the prize's lower bound. At the six PW cells,
  which ran `--decoy 3` (LEGS.md, L-2), (motif − decoy) with its t(9) interval is printed beside the prize as
  descriptive. A PAYS call with a (motif − decoy) lower bound ≤ 0 is flagged "not shown food-dependent", as RBT-125's
  readout did for HP and U; the flag does not change the call.
- **At U and HP no decoy ran** (by the registered harness), so a prize there is not shown to be food-dependent
  (READOUT-BC, S2 of pass 1).

## 4. Printed beside every nose-vs-speed reading (coordinator's pre-data note, 08:10, from the RBT-125 ruling)

**Every nose-vs-speed reading prints the speed step's own payoff beside it**, because under the channel the speed
step collapses (sech² approach gating), and a NOSE LEADS can then mean a failing speed step rather than a strong
nose.

Per cell, beside the registered reading:
- the nose step w 3 → 3.4, items, mean [t 95%] over signed hosts (from the `steps` table);
- **the per-unit speed step at w3, mean [t 95%]** over the hosts that enter it, and its n (from the realised-speed
  block);
- the raw speed step at w3, items and net;
- the realised r at w3, its range, and how many hosts leave at r < 1.10;
- the w1 and first-nose readings.

Any NOSE LEADS whose per-unit speed step has an upper 95% bound < 0, or whose nose step has a 95% lower bound ≤ 0, is
flagged **"lead carried by the speed step"** in the table. The flag is descriptive and does not change the call.

## 5. The host caveat (RBT-125 harness adversary, #443, S3)

Both host sets evolved before the fairness set (without `effector_bias_sigma = 0`): RBT-90 part 2's bests (prize) and
RBT-113 O1's finals (steps). They carry whatever resting-throttle bias the walk left. **Every PAYS figure is stated
with that caveat**: it measures an installed compass and the steps on bodies whose resting drive `--fair` would not
have let evolve.

## 6. The procedure, in order

0. This plan, committed and pushed before any leg output is fetched.
1. **Integrity (before any number is read).** A failure is a HELP wake, and nothing further is read.
   - Fetch the 36 `ckpt/rbt-129-stage0-pays-<cell>-{prize,steps}` branches **only**. No Stage P branch, and no
     Stage 0 census branch (`ckpt/rbt-129-stage0-<point>` without `pays`), is fetched or read.
   - **Complete:** per leg, every cell in its `launch.txt` `cells` line. Prize: 10 files per cell (one per RBT-90
     population), each promoted only with a `ROW` line. Steps: one output per cell with its three `STEP <cell>` rows.
     Counted against `launch.txt`.
   - **Flags:** each output names its world. Prize: the `WORLD CONTROL: … world from runs/RBT-129/worlds/config/<id>`
     header. Steps: `# fairness: 'fair'` and the food block in its header. Each named config at `29ab80b` must have
     `fairness == "fair"`, `food.eat_from == "root"` and `food.eat_rule == "surface"`, and the steps header's food block
     must equal it.
   - **Blobs:** every `tool:` line of both `launch.txt` files, plus `runs/RBT-97/mechanism.py` and
     `runs/RBT-97/resign_rbt67.py` (DESIGN §12, the RBT-132 amendment's "Also recorded here"), equal
     `git rev-parse 29ab80b:<path>`. Where a branch records its commit or blobs, they are checked against `29ab80b`
     too.
2. **Per cell** (18 = L ∈ {U, HP, PW} × s ∈ {L, G} × c ∈ {0, 1, 2}, p = 0.03): prize with t(9) CI and the > 0 call;
   the registered steps line, its reading, and §4's prints; **designed PAYS = both conditions**. An 18-row table.
   Marginals over L, s and c: counts of PAYS, of each condition, and of each reading, and the mean prize and mean
   (nose − speed). The marginals are descriptive.
3. **Holistic PAYS and the holistic nose step: NOT RUN (blocked; LEGS.md B1–B4).** The PAYS layer is designed-fauna
   only for now, and the headline says so.
4. **Descriptive comparison, no verdicts:** RBT-125's gate cells under the committed eating rule, without `--fair`
   (§A prize at U/HP/PW × G2.5/G0; §B at PW-G2.5 and PW-G0), set beside the matching cells here (c = 0 is the
   closest clutter; the gate ran RBT-90's random terrain, so no cell is an exact match). Differences are printed, not
   tested.
5. **Robustness:** leave-one-out lower bounds for each PAYS call, as the RBT-125 pass-2 adversary did.
   - Prize: leave one population out (t(8)); the minimum and maximum lower bound.
   - Steps: leave one host out of the registered per-unit line, recomputed from the per-host table (`w3`, `w3.4`,
     `speed@w3`, `r@w3`, printed at 3 decimals), with `steps.py`'s `reading()` applied to each; the readings reached.
     A first check reproduces the full-sample `STEP` interval from the per-host table to within the rounding.
   - **A call that flips** under any single omission (either condition) is flagged FRAGILE, with the omission that
     flips it.
6. **Multiplicity.** DESIGN registers PAYS per cell with no family correction, so none is applied. The count of
   calls is stated beside the headline (18 cells, 2 conditions each).

## 7. Deliverables

`runs/RBT-129/legs-readout/`: this plan; `legs_readout.py` (reads the branches, prints every number); its text
outputs; `READOUT-LEGS.md` with the headline first. Every number in the readout is traceable to a line of the script's
output.
