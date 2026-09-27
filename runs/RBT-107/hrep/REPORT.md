# RBT-107 H-REP: the registered replication of RBT-101 F2 at T + 110, fresh seeds 11–30

H-REP is §5.5's interim look, as registered in Amendment 2 (A2.1, A2.2), A2.8 (IUT, Holm) and A2.9 (interpretation).
It was run once, for all 20 fresh seeds, in one pass, after the coordinator's 03:17 note that every fresh arm had a
checkpoint at season 472 or later. The full output is `readout.txt` (`python runs/RBT-107/hrep/hrep_readout.py`).

**Amended per the coordinator's 05:50 ruling on the readout adversary (#341): F1 upheld.** The registered pre-data seed
set is the one scored. The first version of this report (`e2f5a15`) read both lines NOT SUPPORTED on a seed set chosen
after the data existed (F4, below).

## The scored lines

| hypothesis | verdict | IUT p | n | A2.9 reading |
|---|---|---|---|---|
| **H-REP-DES** (designed A_SB < 0 AND A_SN < 0) | **SUPPORTED** | 0.0171 (≤ Holm's 0.025) | 19 | **general, not flat-specific** |
| **H-REP-PAIR** (P > 0 AND P_N > 0) | **NOT SUPPORTED** | 0.0782 | 19 | not supported |

- **The size to quote (A2.8.3)** for H-REP-DES is the net-of-null trimmed mean: **−0.125**. Against base it is −0.141.
- **What it says:** on 19 fresh seeds, the designed fauna's post-C4 garden gain contrast replicates RBT-101 F2's designed half
  in sign, against base and net of the cull null, at the registered bar.
- **What it does not say:**
  - That this is adaptation to, or a response to, flat ground. I = −0.044 [−0.119, +0.032] is GENERAL, which matches
    RBT-110's finding that C4's pattern is population-general.
  - That the paired half replicates. It does not: P fails its against-base half. The Yuen p of 0.0482 is in the band,
    and the exact Wilcoxon backstop is 0.0782.
  - That RBT-101 F2's full pattern holds. It does not, because the paired interval contains 0.

**The DES verdict is fragile. It rests on two registered choices, each of which moves it:**

| reading | DES IUT p | DES verdict |
|---|---|---|
| **scored:** the registered common seed set (n = 19), `stats107.yuen` as coded | **0.0171** | **SUPPORTED** |
| F1, post-data, not scored: DES per fauna (n = 20, seed 29 included) | 0.0427 | NOT SUPPORTED |
| F2, not scored: the common set with the docstring's approximate se, s_w / ((1 − 2γ)√n) | 0.0291 | NOT SUPPORTED |
| F2, not scored: the common set with Yuen's 1974 se, √((n−1)s_w² / (h(h−1))) | 0.0181 | SUPPORTED |

- **F13.** Seed 29 is the seed that separates the two seed sets.
  - Its co-evolved fauna is extinct from season 27 in all three arms, so its designed fauna evolved alone for 330
    seasons before the onset.
  - Its designed A_SB (+0.342) and A_SN (+0.291) are among the highest of the 20.
  - The registration has no rule about such a seed. This is printed, not acted on.
- **PAIR is NOT SUPPORTED under every reading**, including all three se conventions (IUT p 0.0782, 0.0698 and 0.0501).

## F4 disclosure: the first version of this PR changed a scored rule after the data existed

- **The rule that was registered before any data:**
  - The registered `readout.py confirmatory()` scores DES and PAIR on one common seed set: the seeds with all four
    contrasts in both faunas. It was committed in `f53b1e8` (A2.8, 22:42, before any arm) and kept in `6828154` (A2.9,
    before any read).
  - My own first `hrep_readout.py` (`56b1c7e`, 03:26, before any garden output) used the same line.
- **What I changed, and when:**
  - At 05:20, in `a7bf4d2`, the same commit that carried the data, I switched DES to "its own complete seeds" (n = 20).
  - The per-seed garden files were already on disk when I did this. REPORT.md then said the change "changes no scored
    rule".
- **That was wrong.** It changed the scored seed set, and with it the DES verdict: IUT p **0.0171 → 0.0427**, SUPPORTED
  → NOT SUPPORTED. This amendment restores the registered set, so the scored DES IUT p goes **0.0427 → 0.0171**, NOT
  SUPPORTED → SUPPORTED.
  - The change moved the result away from support, so it was not a search for a positive finding.
  - But under A2.8.4 a post-data change is not scored.
- **The adversary's F1 is upheld** (ruling 05:50). The scored lines are on the registered common set. The per-fauna
  line is printed beneath them as "post-data sensitivity (not scored)".

## The registered verdict lines (verbatim from `readout.txt`)

```
  holistic     UNREAD (A1.2, extinct at season 470): 29 (base, shift, cull20 extinct)
  conventional UNREAD (A1.2, extinct at season 470): none
  SCORED seed set (registered, common): n = 19 seeds with all four contrasts in both faunas
  designed A_SB -0.138 [-0.250, -0.026] 6/19 positive | designed A_SN -0.133 [-0.216, -0.050] 4/19 positive
  paired P +0.082 [-0.062, +0.227] 14/19 positive | paired P_N +0.101 [-0.020, +0.223] 12/19 positive
    H-REP-DES designed against base (< 0): n=19 trimmed mean -0.141; Yuen p = 0.0171 (PRIMARY); t p = 0.0094; Wilcoxon p = 0.0102; component p used = 0.0171
    H-REP-DES designed net of the null (< 0): n=19 trimmed mean -0.125; Yuen p = 0.0025 (PRIMARY); t p = 0.0017; Wilcoxon p = 0.0010; component p used = 0.0025
    H-REP-PAIR paired against base (> 0): n=19 trimmed mean +0.116; Yuen p = 0.0482 (PRIMARY); t p = 0.1235; Wilcoxon p = 0.0782; component p used = 0.0782
    H-REP-PAIR paired net of the null (> 0): n=19 trimmed mean +0.109; Yuen p = 0.0209 (PRIMARY); t p = 0.0482; Wilcoxon p = 0.0364; component p used = 0.0209
  H-REP (IUT, Holm at alpha 0.05 over DES and PAIR): H-REP-DES SUPPORTED (IUT p 0.0171); H-REP-PAIR NOT SUPPORTED (IUT p 0.0782)
    H-REP-DES specialisation (designed): I -0.044 [-0.119, +0.032] 9/19 positive; I - I_N -0.058 [-0.101, -0.016] 5/19 positive; I is GENERAL; reading: general, not flat-specific
    H-REP-PAIR specialisation (paired): I +0.048 [-0.036, +0.131] 14/19 positive; I - I_N +0.065 [+0.003, +0.127] 13/19 positive; I is GENERAL; reading: not supported
    A2.8.3 size to quote, H-REP-DES: net-of-null trimmed mean -0.125
```

Printed directly beneath them in `readout.txt`, **not scored**:

```
  post-data sensitivity (not scored), adversary F1: DES per fauna (A1.2's 'UNREAD for that fauna'), n = 20
    H-REP-DES designed [per fauna, not scored] against base (< 0): n=20 trimmed mean -0.122; Yuen p = 0.0427 (PRIMARY); t p = 0.0282; Wilcoxon p = 0.0266; component p used = 0.0427
    H-REP-DES designed [per fauna, not scored] net of the null (< 0): n=20 trimmed mean -0.113; Yuen p = 0.0054 (PRIMARY); t p = 0.0089; Wilcoxon p = 0.0060; component p used = 0.0054
    with PAIR's p, Holm would give H-REP-DES NOT SUPPORTED (IUT p 0.0427) [not scored]
  post-data sensitivity (not scored), adversary F2: the Yuen se convention on the scored seed set (component p's, band rule as scored_p; IUT p = max; Holm over DES and PAIR)
    coded s_w sqrt n / h (the registered object)     DES IUT p 0.0171 SUPPORTED; PAIR IUT p 0.0782 NOT SUPPORTED
    docstring-approx s_w / ((1 - 2 trim) sqrt n)     DES IUT p 0.0291 NOT SUPPORTED; PAIR IUT p 0.0698 NOT SUPPORTED
    Yuen 1974 sqrt((n-1) s_w^2 / (h (h-1)))          DES IUT p 0.0181 SUPPORTED; PAIR IUT p 0.0501 NOT SUPPORTED
  F13 (not scored): seed 29's co-evolved fauna is extinct from season 27 in all three arms, so its designed fauna evolved alone; it is the seed that separates the two seed sets
```

## Gates (all PASS)

- **COMPLETENESS:** 60/60 arms' cut tables and 120/120 garden populations, J = 32 each.
- **NO-PEEK:** the last season in any cut table is 470.
- **V0:** seasons 0..359 are identical across base, shift and cull20 on the five shared `seasons.txt` columns, on all
  20 seeds.
- **V-G:** every garden population is exactly the fauna alive at the end of season 470, by name.
  - This includes seed 29's co-evolved fauna: an empty file, with 0 alive.

## The arithmetic (Z10, seasons 360..369, paired by name)

| fauna | Z10 [95% t] | seeds positive |
|---|---|---|
| co-evolved | +0.192 [+0.153, +0.230] | 19/19 |
| designed | +0.827 [+0.761, +0.892] | 20/20 |
| paired | −0.636 [−0.729, −0.543] | 0/19 |

The paired Z10 is the arithmetic for an unchanged pair. It is the same as the old seeds': −0.630 (RBT-101) and
−0.621 at J = 32 (Δ0).

## Printed, not scored (on the scored common set, n = 19, unless stated)

- **Designed RESPONSE_random** (G_S^random − G_B^random): −0.094 [−0.151, −0.037], 4/19.
- **POST HOC, A2.9 point 3, not a registered test and entering no verdict:** designed RESPONSE_random net of the null
  (G_S^random − G_N^random) is −0.074 [−0.127, −0.021], 4/19.
  - This is the direction A2.9 point 3 recorded as the one to watch, the "general" reading. The designed population
    that lived through flat ground is worse on the terrain it no longer faced, relative to base and to cull20.
  - That matches RBT-110's adversary on C4 at T + 110 (−0.151 [−0.282, −0.019]).
  - It is printed with a t interval, on the one set of data, unadjusted.
- **Designed REFUND** (G_B^flat − G_B^random): +0.780, 19/19. Flat ground is a boon to an unchanged population, as A1.2
  predicted.
- **Per fauna, each on its own complete seeds:**
  - co-evolved (n 19): A_SB −0.056, A_SN −0.031, null A_NB −0.024;
  - designed (n 20): A_SB −0.114, A_SN −0.112, null A_NB −0.002.
- **Paired P in paired A/A units:** +0.7 to +0.9.
- **Split-half measurement sd** of one seed's A_SB at J = 32, worlds 0..15 against 16..31: 0.054 co-evolved and 0.095
  designed.
- **Per seed:** in `readout.txt`.

## Provenance: where the T + 110 populations come from

**The T + 110 populations come from restored copies of each arm's checkpoint, not from `fresh_seed.sh`'s artefact.**
This is the route registered in A2.2 (`garden_run.sh hrep`: "restores copies of base, shift and cull20; it never
touches a running directory; it writes their tables, runs the garden at T + 110").

`hrep/hrep_run.sh SEED` does the following for each arm:
1. It restores `ckpt/rbt-107-fresh-ARM-SEED` into a scratch directory, and requires the checkpoint to be at season 472
   or later.
2. **It cuts the copy to season ≤ 470 before anything is read** (`hrep/hrep_cut.py`). This drops every lineage, cohort
   and history row after 470, and deletes stale derived tables.
3. It writes RBT-92's tables on the cut copy, and copies `seasons.txt`, `lineage-last.txt` and `events.txt` to
   `hrep/tables/ARM-SEED/`.
4. It runs `garden.py` at season 470 for both faunas on worlds 0..15 and 16..31, and merges them to J = 32.
5. It runs `z10.py`.

The cut is an addition to `garden_run.sh hrep`. It is what makes the no-peek rule mechanical: no file under `hrep/`
holds a season after 470. The population alive at 470 is the same whether or not the later seasons are present,
because `alive_at` reads birth and death up to the season.

- **Each arm's `source.txt`** names the checkpoint and the season it was restored at.
  - The hash printed is the checkpoint branch's head when the source line was written.
  - For seed 11, whose tables were written later (see below), that head may be a later commit than the one restored.
    The restored season in the same line is the one read.
  - **The hashes are not durable** (adversary F10). `durable.sh` force-pushes one parentless commit per save, so a
    recorded commit can disappear: `ckpt/rbt-107-fresh-base-11` was recorded as `88e8a226` and is now `a7dbc03`.
    Provenance rests on the restored season and on re-cut identity. The adversary re-cut seeds 11, 25 and 29 from their
    `ckpt/` branches, and the tables were byte-identical (F9).
- **No-peek on T + 800 holds.**
  - Nothing from season ≥ 471 of any arm was written, printed or read here.
  - The only fact about later seasons in this report is each checkpoint's season number, in the provenance lines.

**Compute.**
- The seeds were split into seven shards (`hrep/hrep_shard.sh K 7`):
  - shard 0 ran in this session;
  - shards 1–6 ran in six sessions tagged `hive-0926`, `rbt`, `rbt-107`, `garden`.
- Each shard pushed only `hrep/garden` and `hrep/tables` to `results/RBT-107-hrep-sK`. Those were merged here, and every
  shard session was archived once its output was in.
- Shard 4 (seeds 15, 22, 29) failed in its session. It was re-run from clean in this session (below).

## Faults found at run time, and their fixes (1, 2 and 4 are implementation; **3 changed a scored rule and is reverted**)

1. **`garden.py base_sim`.**
   - The fault: it read the sim config from `runs/RBT-90/forage-SEED`, and the fresh seeds have none.
   - The fix: it now falls back to the arm's own `config.json` "sim", after asserting that this equals seed 801's
     RBT-90 sim. Otherwise it exits.
   - Check: an old-seed garden (`c0-801-holistic`) re-ran byte-identical to its committed file.
2. **`garden_merge.py`: shard 4's AttributeError.**
   - The cause: seed 29's co-evolved fauna went extinct at **season 27**, identically in all three arms, long before
     the onset at 360.
   - For an extinct fauna, `garden.py` writes a header-only "nobody alive (extinct)" file, and the merge's header
     regex expected a J.
   - The fix: when every part is that header, the merged file is the header. `readout.py`'s `garden()` reads it as an
     empty population, and A1.2 codes that seed as UNREAD for that fauna.
   - Parts that disagree on extinction are an error.
   - No arm was skipped and no input is missing. All nine of shard 4's checkpoints restored at season ≥ 472.
3. **`hrep_readout.py`: the seed set. This changed a scored rule, and it is reverted** (F4 above; ruling 05:50).
   - The registered code and my own first draft score DES and PAIR on the common set of seeds with all four contrasts
     (n = 19).
   - At 05:20 (`a7bf4d2`), with the per-seed garden files on disk, I switched DES to its own complete seeds (n = 20).
     The first version of this report called that "A1.2's rule applied per fauna" and said no fault changed a scored
     rule.
   - It moved the DES IUT p from 0.0171 to 0.0427, and the verdict from SUPPORTED to NOT SUPPORTED.
   - The readout now scores on the registered common set. The per-fauna DES is printed beneath it as "post-data
     sensitivity (not scored)".
4. **`hrep_run.sh`: tables with a reused scratch copy.**
   - The fault: the table copy sat inside the "not yet restored" branch. Seed 11's scratch copies, already cut to 470
     in a smoke test whose tables had been deleted, were reused without their tables being copied.
   - The fix: the tables are now written whenever they are missing. Seed 11's were regenerated from its cut copies:
     every table ends at 470, and its Z10 re-ran byte-identical.
   - Editing the script while shard 0 ran broke that run's final Z10 step for seed 25, because bash reads scripts
     incrementally. Seed 25's gardens were complete; its Z10 was re-run alone.

## What this does and does not say

- **H-REP is an interim look (A2.8.4).** Nothing in §5.5 changes because of it: the statistics, forms, α, Holm family,
  read points, seed set, and the H1 and H-ALT outcomes and their meanings all stay as registered. H1 at T + 800 is the
  scored test.
- **The PREREGISTRATION now has a post-H-REP note (interpretation only, not scoring).** H1-DES and H1-PAIR use
  `confirmatory()`'s common set unchanged, and H-ALT's increment uses its registered designed-only seeds. The H1
  readout prints the other seed set beside each line, as labelled sensitivity.
- **The designed half replicates in sign at the registered bar. It is a population difference, not a response to flat
  ground.**
  - I is GENERAL.
  - The post hoc RESPONSE_random net of the null is negative too: the designed population that lived through flat
    ground is worse on the terrain it no longer faced.
  - It is fragile: see the table at the top.
- **The paired effect against base is not established.**
  - A2.8.3 warned that under RBT-110's C4null truth, most of a paired effect against base would be turnover.
  - Here P_N (+0.109) is not smaller than P (+0.116), trimmed. The fresh seeds do not show RBT-110's C4null split, in
    which turnover made +0.20 of +0.27.
  - That is a description, not a test.
- **`stats107.yuen`'s se** is the registered object as coded (s_w·√n / h). Its docstring gave the (1 − 2γ)
  approximation, which differs at n = 19. The docstring is corrected to the code, and an se self-check at n = 19 is
  added. The code is unchanged (F2).
- **Seed 29 will be UNREAD for the co-evolved fauna at every read point,** T + 800 included. Its co-evolved fauna died
  at season 27. H1-PAIR and the common set will therefore be read on at most 19 seeds. A2.8.3's power figures were
  computed for n = 20.
- The ten old seeds' T + 110 lines, "persistence on the discovery seeds" (A2.1), are RBT-101's own read and are not
  re-run here.
