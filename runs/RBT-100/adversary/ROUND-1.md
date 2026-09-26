# RBT-100 adversary round 1: C3's design (scarce food), what is C3-specific

Adversary: session `session_01S5ugw4uRpKFG1khYtu6PvW`, named by the coordinator at 13:10. Scope: what is C3-specific.
The shared RBT-92 instrument is not re-argued except where C3 breaks one of its assumptions. Design read at
integration `698731d` (PR #81 merged), `runs/RBT-100/PREREGISTRATION.md`.

Probes are on `results/RBT-100-adversary` under `runs/RBT-100/adversary/`. Each has its own script, readout
and command. **None is a C3 arm.**
- **P1:** seed 901, which is outside the ten, with the shift at season 100 rather than at a registered T of
  340–400. It ran plain and shift arms to season 159.
- **P2:** random founders at six items for 40 seasons on the head's generator.

The probes test the design's *mechanism* claims. **The predictions in §8 should not be re-tuned from them.**

## Re-derived first (credit where it holds)

- **§2 quotes: verbatim.** Every block quoted from `docs/held-out-challenges.md` was split into 57 sentence chunks, and all 57 appear verbatim in the doc (whitespace normalised). That covers the C3 table row, both claim lines, the expectation, the unperceived statement, class D's rule, and forbidden readings 1–11. The template's field-2 statement (§3) is restated in the same words.
- **"Six items" endpoint: quoted correctly.** `docs/foraging-world.md` l.105 has holistic starved out at 15, designed bottlenecked to 11 by 17 and extinct at 51. It is **one seed (801) on the pre-RBT-95 generator**, and it is the seed whose founders fell furthest at twelve items (60 → 7, against 31–42 on 802/803, same doc l.121). See F5.
- **§3.1 code premise: holds.** `patches = 0` and `regrow_delay = 0` are the defaults and the command sets neither. Food is instant and uniform, and `--shift food-items=6` changes the count only.
- **Byte identity: holds at another seed and onset.** P1 at seed 901, T = 100 (`probe_bytecheck.txt`):
  - `lineage.jsonl`: 11604/11604 rows before T with the same sha256;
  - `cohorts.jsonl`: 200/200;
  - `history.json`: 200/200 identical;
  - `food.items = 6` on 120/120 entries from T.
  I did not re-run `smoke.sh`. Its numbers are withheld by design and the byte check is the part that bears weight.
- **§4's arithmetic: the core holds, measured on an established population.** P1 `probe_read.txt` §2, per individual-season, shift arm, [T, T+20) against [T−20, T):
  - **Holistic:** gross food 0.955 → **0.451** (×0.47); work charge 0.162 → 0.155.
  - **Designed:** gross food 1.319 → **0.640** (×0.49); work charge 0.537 → 0.543.
  - So gross halves and work does not move, as §4 says.
  - **Designed own net per season: +0.097, below basal 0.25.** This is inside §4's range (−0.03 to +0.34) and far below the protocol's 0.4–0.55. §4's correction of §2 (halve the gross, not the net) is right.
  - **Holistic own net: +0.296**, just above basal and a little under §4's 0.35–0.68.
- **Where the design says the income triggers will rarely fire and the floor will carry D (§4), it is right**, and for a stronger reason than it gives (F3).

## Findings

### F1. The energy buffer is not "a little above 3"; it is 10–16 a head. §3.3's mechanism is wrong, and the UNDERSIZED test cannot fire where it is needed. **Must fix before launch.**

**The premise.** §3.3 says "Energy is at most a little above the birth threshold of 3", so a robot δ below basal dies e/δ ≈ 3–30 seasons after T.

**The code says otherwise.** Energy is uncapped. A breeder breeds only into a free slot (`ecology.py:498–507`), and at capacity slots open only through deaths, about 1.5 a season. So an established robot earning about +0.6 above basal banks almost all of it.

**Measured.** P1 at T−1, over robots that survive the season:
- holistic mean **10.7** (median 9.0, q75 16.2);
- designed mean **16.0** (median 12.0, q75 24.6).

RBT-19's committed `P-801/history.json` (a persistent world, same economy) gives about **27** (holistic) and **18** (designed) a head across seasons 100–550.

**What the shift then does** (P1 `probe_read.txt` §3–5):

| | T+0 | T+10 | T+20 | T+30 | T+40 | T+45 | T+50 | T+55 |
|---|---|---|---|---|---|---|---|---|
| designed alive, shift (base 60 throughout) | 60 | 60 | 60 | 60 | 59 | 58 | 53 | **44** |
| designed stored energy a head, shift | 14.8 | 10.4 | 5.3 | 3.5 | 1.5 | 1.2 | 1.5 | 1.6 |
| holistic alive, shift | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 |

- **The alive count does not move for about 40 seasons.** The residents live off the hoard, and they keep breeding into every slot a death frees.
- **Almost all the excess death is their newborns.** These start at energy 1 and starve before reaching 3. In the designed shift arm, deaths over [T, T+60) were **267 starved newborns (born ≥ T)**, 21 starved residents and 28 aged out. The plain arm had 31, 5 and 49.
- **Excess deaths:**
  - designed 26 / 143 / 314 over [T, +10) / [T, +30) / [T, +60);
  - holistic 9 / 42 / 73.
- **The births deficit is negative:** −292 designed, −73 holistic. The shift arm breeds *more*, into slots its starving young keep freeing.
- **The alive deficit at T+30 is 0 on both faunas.**

**Consequences:**
1. **The UNDERSIZED test cannot fire.** It fires when the alive deficit at T+30 exceeds 2 × k + 2, and here the deficit was 0 against k = 26 (designed) and 9 (holistic). It printed **"not undersized"** on the arm where the impulse null is least like the shift.
2. **Most exposed claim 3 is scored on that test.** It is "falsified if UNDERSIZED prints for neither fauna", so P1's pattern would score it as falsified while the null is badly mis-shaped. The instrument would give a wrong answer on a claim it was built to test.
3. **The collapse comes at T+40 to T+60, not "3 to 30 seasons after T".** It starts when the hoard is spent, at about 0.4 a head a season (14.8 → 3.5 over 30 seasons: own net 0.10 against basal 0.25, plus the birth cost of the young it keeps breeding). At registered T (340–400) the hoard may be larger (RBT-19: about 18 designed a head), so the collapse lands at or after the opening of the recovery window, and the designed minimum alive most likely falls inside [T+60, T+160).

**Fix, before launch** (a pre-registered test, no C3 data yet):
- Either restate UNDERSIZED on the quantity the shift actually moves, or drop it as a decision device.
- My proposal:
  - declare C3's turnover guard **not interpretable a priori**, for the reason §3.3 already gives: the income loss is density arithmetic, not turnover;
  - keep NULL as printed diagnostics only;
  - extend the alive deficit to T+40, T+60 and T+100;
  - split excess deaths into born < T and born ≥ T;
  - rescore claim 3 on something the arm can show. For example: "k is mostly newborn churn: excess deaths of individuals born ≥ T exceed those born < T over [T, T+30), on ≥ ⌈0.8n⌉/n seeds and faunas".
- **Rewrite §3.3's mechanism text.**

### F2. k counts newborn churn, so the cull removes k *hoarders* from a full population. The null is the wrong shape, not merely undersized. **Report caveat** (and state it in the pre-registration).

`cull_k.py`'s k is the excess deaths over [T, T+10). Under C3 those are mostly the hoarders' starving young.

**The cull arm does something different.** It removes k individuals at random at T. Most of them are established residents carrying 10–16 energy, taken from a population that refills within a few seasons from other hoarders' births.

So the shift and its null differ in who dies, not only in how many. The shift keeps every resident and starves the young, where the cull removes residents and lets young survive. The design's "undersized" framing (§3.3) assumes the two differ only in size.

- **The null is still the protocol's**, and k's rule must not change (the design is right on that).
- **But R-null for C3 is not "a same-size cull".** The report should say what it is: a random impulse on residents, against a starvation of recruits.
- **k itself:** P1 gives K1 = 9 and K2 = 26 (n = 1, T = 100), inside the §8 ranges (0–12, 0–30).

### F3. The axis is a lifetime mean over the living. Under C3 it lags the population's own income by about 0.3 in the transient, and it is survivor-conditioned in recovery. D-by-income is close to unreachable. **Report caveat, plus a cheap build before launch.**

**Transient.** `mean_lifetime_score` is `score_sum / evals` per living individual, and at T the residents carry up to 59 seasons of twelve-item earnings.

| P1, designed, shift arm | T+10 | T+20 | T+30 | [T+40, T+60) |
|---|---|---|---|---|
| axis (lifetime mean over the living) | 0.514 | 0.373 | 0.415 | 0.36–0.39 |
| the season's own net | 0.097 (mean over [T, T+20)) | | | 0.266 |

- **The transient income trigger (mean < 0.25 over [T, T+60)) cannot see a fauna earning 0.1 a season** while its residents live off pre-T earnings.
- **In recovery everyone alive was born after T, but the living mean excludes the starved young.** In P1 those are 267 designed newborns in 60 seasons.
- The design saw survivor-conditioning (§4) and predicted "D through the floor" for that reason. **Credit.** The effect is stronger than §4 says: the income triggers are close to structurally blind under a budget shift.
- **That is the shared axis, and I do not ask for the class rule to change.** But D's own words are "below its basal cost", and C3 is the challenge where that matters.

**Build before launch.** The committed tables (`tables.py`) carry neither stored energy nor the season's own gain, and `history.json` and `lineage.jsonl` are bulk. So a C3 table is needed, written from bulk per arm and committed, with per season and fauna:
- `total_energy / alive`;
- mean `last_score` (the season's own net) over everyone who ran the season, the young who then starved included;
- gross food and work charge.

Then the readout can print, beside the class, **"own net below basal in the recovery window: k/n seeds"** per fauna. `probe_read.py` §2 and §5 already do this from bulk. It is cheap and must exist before any arm's bulk is gone; `ckpt/*` does keep the bulk, but the readout is meant to run from committed files.

### F4. §3.4's wave phase: the echo lands across the whole recovery window, not at its opening. **Report caveat; fix the text before launch.**

- The designed collapse starts at about T+40 (F1). Whoever refills after it is born at about T+40 to T+100, and ages out at about **T+100 to T+160**. That is the whole recovery window, not "T+60 to T+90".
- ECHO's count still reads what it reads. But **"the recovery window contains the shift's own echo" should be expected, not 0.25** (§8). The prediction is the designer's to keep and be scored on; I only flag that its mechanism text is wrong.
- A designed fauna below about 20 alive cannot reach the 20/60 peak at all (§3.4 says this). **Credit.**

### F5. "Where random founders could not" rests on one seed on the old generator, and the established population arrives with about 4–5 times the founders' energy. **Must fix before launch** (cheap), or drop the contrast from any sentence.

**The question C3 poses** (protocol §2, ticket) is "whether an established population holds where random founders could not".

**The founders' side is one number:** seed 801, pre-RBT-95 generator. The founding population a seed founds changed with RBT-95 (Resumption guide). 801 was also the seed whose founders fell furthest at twelve items.

**Two things confound the contrast:**
1. **Founders start at energy 3.** An established fauna at T carries 10–16 a head (F1), and that hoard, not income, carries it through the first about 40 seasons. That part of any "held" is bought with pre-T energy.
2. **At registered T the contrast needs a founders endpoint at six items on the same seeds and head.**

**Fix:**
- **(a) A founders-at-six arm per seed:** `--food-items 6` from season 0 for 40–60 seasons, no event. That is about ten short arms (P2 is the template).
- **(b) State the survival sentence on the recovery window only**, where every living robot was born after T at energy 1, so the hoard is spent. The CLASS D lines already split the windows. **Credit.** The sentence about holding should cite only [T+60, T+160) alive and own net.

**P2 is running now** on seeds 801, 1, 901 and 804. Its result is posted as an addendum.

### F6. The readout's verdict text does not carry C3's claim line or its D sentence. **Must fix before the readout runs** (cheap; do it in the answer PR).

- The pre-registration quotes everything correctly. But `runs/RBT-100/readout.py` prints RBT-92's verdict block unchanged:
  - class C reads **"the designed body wins after the shift"**, not the owner's falsifier, "the designed body wins on the held-out challenge";
  - on class D the only sentence printed is "does not hold up (a class-A result would read: outlasts, not holds up)". The protocol's D sentence, **"outlasts a bankrupt comparator"**, is never printed;
  - the C3 claim line ("survivorship at a boundary, here the bootstrap line for food; whether an established population holds where random founders could not. Not the owner's contest claim.") and the unperceived statement are not printed.
- **Proposal:** part 2 prints, after the class:
  - the C3 claim line and the unperceived statement, verbatim;
  - the class-D sentence chosen by the rule ("outlasts a bankrupt comparator" unless co-evolved R-shift ≥ −r);
  - forbidden readings 12 and 13;
  - the owner's falsifier wording.
- This is a text change in C3's own file and touches no RBT-92 code.

## Does the readout answer "does an evolved population survive the bootstrap line random founders don't"?

**Partly.**
- **Survival:** the CLASS D lines give the co-evolved fauna's min alive, extinction and window means per seed. That answers "survives".
- **Holding at the line:** "holds at the bootstrap line" needs:
  - the own-net line (F3), because the lifetime-mean axis cannot say whether a population is paying its way;
  - the founders' endpoint on the same seeds and head (F5);
  - a recovery-window-only reading (F5b).

With those three, the readout answers the question. Without them it answers "the hoard lasted" in the transient and "the survivors earned" in recovery.

**P1's one data point** (n = 1, T = 100, not a registered arm):
- the holistic fauna held at 60 through T+59, on own net +0.30 → +0.41;
- the designed fauna had begun to fall (44 at T+55).

## Verdicts

| | finding | verdict |
|---|---|---|
| F1 | buffer 10–16 not ≈ 3; alive deficit 0 at T+30; UNDERSIZED cannot fire; claim 3 mis-scored | **must fix before launch** |
| F2 | k is newborn churn; cull removes residents; the null is the wrong shape | report caveat, stated in the pre-registration |
| F3 | lifetime-mean axis lags own net by about 0.3 in the transient; D-by-income near blind | report caveat, **own-net and energy table built before launch** |
| F4 | echo spans the whole recovery window | report caveat; fix §3.4's text |
| F5 | founders' endpoint is n = 1 on the old generator; the hoard confounds the contrast | **must fix before launch** (founders-at-six arms, or drop the contrast) |
| F6 | readout omits the C3 claim line, the D sentence and the owner's falsifier wording | **must fix before the readout** (text only) |

**Credit, plainly:**
- the quotes are verbatim;
- the code premise and byte identity reproduce at another seed and onset;
- §4's density arithmetic reproduces on an established population to within 2–6% on gross food, with work unmoved;
- the designer saw survivor-conditioning and the floor route before any data.

The design's class-D prediction is made for the right reason, the designed body's work bill against halved gross. What is wrong is the timing mechanism, and the one test (UNDERSIZED) that depends on it.

