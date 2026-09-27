# RBT-107 H-REP: the registered replication of RBT-101 F2 at T + 110, fresh seeds 11–30

H-REP is §5.5's interim look, as registered in Amendment 2 (A2.1, A2.2), A2.8 (IUT, Holm) and A2.9 (interpretation).
It was run once, for all 20 fresh seeds, in one pass, after the coordinator's 03:17 note that every fresh arm had a
checkpoint at season 472 or later. The full output is `readout.txt` (`python runs/RBT-107/hrep/hrep_readout.py`).

## The result

**Neither registered H-REP hypothesis is SUPPORTED.**

- **H-REP-DES fails only at Holm.**
  - Both of its IUT halves pass on their own:
    - designed A_SB < 0, Yuen p 0.0427. This is in the (0.04, 0.05] band, and the Wilcoxon backstop passes at 0.0266.
    - designed A_SN < 0, Yuen p 0.0054.
  - The IUT p is 0.0427.
  - Holm over DES and PAIR needs the smaller p to be ≤ 0.025, and 0.0427 is not. So neither is rejected.
- **H-REP-PAIR fails in its against-base half.**
  - P > 0 has Yuen p 0.0482, inside the band. The exact Wilcoxon p is 0.0782, so the component does not count.
  - The net-of-null half, P_N > 0, has p 0.0209.
- **RBT-101 F2's full pattern does not hold** on the fresh seeds. That pattern is: designed flat below 0, designed
  random below 0, and paired above 0, on t intervals.

What the numbers show (point estimates and t intervals; `readout.txt` has the full lines):

| quantity | estimate [95% t] | seeds positive |
|---|---|---|
| designed A_SB | −0.114 [−0.231, +0.003] | 7/20 |
| designed A_SN | −0.112 [−0.202, −0.022] | 5/20 |
| paired P | +0.082 [−0.062, +0.227] | 14/19 |
| paired P_N | +0.101 [−0.020, +0.223] | 12/19 |

- The estimates have the signs RBT-101 F2 found, and they are about half its size. F2 found designed −0.22 and paired
  +0.27.
- Against base, neither the designed nor the paired interval excludes 0.
- **Holm is part of the registered rule** (A2.1, A2.8.2), so the DES line reads NOT SUPPORTED. Nothing below treats the
  unadjusted DES halves as a finding.

## The registered verdict lines (verbatim from `readout.txt`)

```
== H-REP (T + 110 = season 470): §5.5 as amended by A2.8 (IUT) and A2.9 (interpretation), fresh seeds 11-30
  holistic     UNREAD (A1.2, extinct at season 470): 29 (base, shift, cull20 extinct)
  conventional UNREAD (A1.2, extinct at season 470): none
  DES n = 20 seeds (designed A_SB and A_SN); PAIR n = 19 seeds (both faunas)
  designed A_SB -0.114 [-0.231, +0.003] 7/20 positive | designed A_SN -0.112 [-0.202, -0.022] 5/20 positive
  paired P +0.082 [-0.062, +0.227] 14/19 positive | paired P_N +0.101 [-0.020, +0.223] 12/19 positive
    H-REP-DES designed against base (< 0): n=20 trimmed mean -0.122; Yuen p = 0.0427 (PRIMARY); t p = 0.0282; Wilcoxon p = 0.0266; component p used = 0.0427
    H-REP-DES designed net of the null (< 0): n=20 trimmed mean -0.113; Yuen p = 0.0054 (PRIMARY); t p = 0.0089; Wilcoxon p = 0.0060; component p used = 0.0054
    H-REP-PAIR paired against base (> 0): n=19 trimmed mean +0.116; Yuen p = 0.0482 (PRIMARY); t p = 0.1235; Wilcoxon p = 0.0782; component p used = 0.0782
    H-REP-PAIR paired net of the null (> 0): n=19 trimmed mean +0.109; Yuen p = 0.0209 (PRIMARY); t p = 0.0482; Wilcoxon p = 0.0364; component p used = 0.0209
  H-REP (IUT, Holm at alpha 0.05 over DES and PAIR): H-REP-DES NOT SUPPORTED (IUT p 0.0427); H-REP-PAIR NOT SUPPORTED (IUT p 0.0782)
    H-REP-DES specialisation (designed): I -0.029 [-0.106, +0.049] 10/20 positive; I - I_N -0.044 [-0.094, +0.005] 6/20 positive; I is GENERAL; reading: not supported
    H-REP-PAIR specialisation (paired): I +0.048 [-0.036, +0.131] 14/19 positive; I - I_N +0.065 [+0.003, +0.127] 13/19 positive; I is GENERAL; reading: not supported
```

**A2.9.**
- I and I − I_N are printed beside both lines.
- Neither hypothesis is SUPPORTED, so the "general, not flat-specific" label is not used.
- Both specialisations read GENERAL: I's interval contains 0 for DES and for PAIR.

**A2.8.3.** P_N's trimmed mean is +0.109. A2.8 names it as the size to quote if PAIR were SUPPORTED. PAIR is not
SUPPORTED, and the figure is given only for completeness.

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

## Printed, not scored

- **Designed RESPONSE_random** (G_S^random − G_B^random): −0.085 [−0.142, −0.028], 5/20.
- **POST HOC, A2.9 point 3, not a registered test and entering no verdict:** designed RESPONSE_random net of the null
  (G_S^random − G_N^random) is −0.067 [−0.120, −0.015], 5/20.
  - This is the direction A2.9 point 3 recorded as the one to watch, the "general" reading. The designed population
    that lived through flat ground is worse on the terrain it no longer faced, relative to base and to cull20.
  - That matches RBT-110's adversary on C4 at T + 110 (−0.151 [−0.282, −0.019]).
  - It is printed with a t interval, on the one set of data, unadjusted.
- **Designed REFUND** (G_B^flat − G_B^random): +0.777, 20/20. Flat ground is a boon to an unchanged population, as A1.2
  predicted.
- **Per fauna:**
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

## Faults found at run time, and their fixes (all implementation; none changes a scored rule)

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
3. **`hrep_readout.py`: each hypothesis on its own complete seeds.**
   - The first draft took the seeds that had all four contrasts in both faunas. That would have dropped seed 29 from
     DES too, although its designed fauna is alive.
   - The readout now scores DES on the 20 seeds with the designed A_SB and A_SN, and PAIR on the 19 with both faunas.
     It lists the UNREAD seeds.
   - This is A1.2's rule applied per fauna. It was fixed after the per-seed outputs existed, but before any H-REP
     line was printed.
4. **`hrep_run.sh`: tables with a reused scratch copy.**
   - The fault: the table copy sat inside the "not yet restored" branch. Seed 11's scratch copies, already cut to 470
     in a smoke test whose tables had been deleted, were reused without their tables being copied.
   - The fix: the tables are now written whenever they are missing. Seed 11's were regenerated from its cut copies:
     every table ends at 470, and its Z10 re-ran byte-identical.
   - Editing the script while shard 0 ran broke that run's final Z10 step for seed 25, because bash reads scripts
     incrementally. Seed 25's gardens were complete; its Z10 was re-run alone.

## What this does and does not say

- **H-REP is an interim look (A2.8.4).** Nothing in §5.5 changes because of it: the statistics, forms, α, Holm family,
  read points, the H1 and H-ALT outcomes and their meanings all stay as registered. H1 at T + 800 is the scored test.
- **The designed decline is not established at T + 110.**
  - Both of its forms point below 0, and the net-of-null form's interval excludes 0.
  - The registered family did not reject it. The report does not call it replicated.
- **The paired effect against base is not established.**
  - A2.8.3 warned that under RBT-110's C4null truth, most of a paired effect against base would be turnover.
  - Here P_N (+0.109) is not smaller than P (+0.116), trimmed. The fresh seeds do not show RBT-110's C4null split, in
    which turnover made +0.20 of +0.27.
  - That is a description, not a test.
- **Seed 29 will be UNREAD for the co-evolved fauna at every read point,** T + 800 included. Its co-evolved fauna died
  at season 27. H1-PAIR will therefore be read on at most 19 seeds. A2.8.3's power figures were computed for n = 20.
- The ten old seeds' T + 110 lines, "persistence on the discovery seeds" (A2.1), are RBT-101's own read and are not
  re-run here.
