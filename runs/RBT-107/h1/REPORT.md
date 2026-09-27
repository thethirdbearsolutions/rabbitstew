# RBT-107 H1: the scored read at T + 800 (~21 events) on fresh seeds 11–30

This is H1 as registered: §5.5, as amended by A2.1, A2.2, A2.8 and A2.9, plus the post-H-REP note.
- **Scoring:** the registered `readout.py confirmatory()` scores it, unchanged. The seed-set sensitivities from #345
  are printed beside it and are not scored.
- **When:** it was run once, after the coordinator's 08:45 note: all 60 fresh arms merged, and V-POST PASS at 1200/1200.
- **The full output:**
  - `readout.txt` (`python runs/RBT-107/readout.py`);
  - `power.txt` (`h1_power.py`), the power at the usable n;
  - `posthoc.txt` (`h1_posthoc.py`), post hoc lines.

## The result

| line | verdict | p | n |
|---|---|---|---|
| **H1-DES** (designed A_SB < 0 AND A_SN < 0) | **NOT SUPPORTED** | IUT p 0.1987 | 19 |
| **H1-PAIR** (P > 0 AND P_N > 0) | **NOT SUPPORTED** | IUT p 0.1828 | 19 |
| **H-ALT** (re-adaptation) | **NOT DECIDED** | increment Yuen p 0.4425 (> 0), MDE on the realised null 0.209 | 20 |
| §5.3 designed | **NOT SEEN** | resolution (two-interval, realised null) 0.209 | 20 |
| §5.3 co-evolved | **NOT SEEN** | resolution 0.217 | 19 |

- **A2.9:** both H1 lines read "not supported". I is GENERAL on both: designed +0.039 [−0.076, +0.154], paired
  −0.035 [−0.159, +0.088].
- **The ticket's question: can adaptation after a challenge be seen at ~20 events?** On C4, with this instrument, it was
  not seen:
  - no ADAPTED verdict on either fauna;
  - no OVERSHOOTS;
  - no H1 line supported.
- **The H-REP designed decline at T + 110 (SUPPORTED, fragile) is not supported at T + 800.**
  - Its point estimate is about the same size: designed A_SB is −0.114 at T + 110 and −0.126 at T + 800, over all 20
    seeds.
  - Its intervals widen: −0.126 [−0.283, +0.031]. The realised T + 800 null RMS is 0.27 per fauna, against the
    modelled T + 110 null of about 0.13 designed.
  - H-ALT's increment is +0.013 (n = 20), so the data say neither "deepens" nor "reverses".

## The scored lines (verbatim from `readout.txt`)

```
    H1-DES designed against base (< 0): n=19 trimmed mean -0.079; Yuen p = 0.1987 (PRIMARY); t p = 0.0908; Wilcoxon p = 0.1660; component p used = 0.1987
    H1-DES designed net of the null (< 0): n=19 trimmed mean -0.120; Yuen p = 0.1224 (PRIMARY); t p = 0.1196; Wilcoxon p = 0.0978; component p used = 0.1224
    H1-PAIR paired against base (> 0): n=19 trimmed mean +0.087; Yuen p = 0.1828 (PRIMARY); t p = 0.0736; Wilcoxon p = 0.1868; component p used = 0.1828
    H1-PAIR paired net of the null (> 0): n=19 trimmed mean +0.198; Yuen p = 0.0345 (PRIMARY); t p = 0.0375; Wilcoxon p = 0.0399; component p used = 0.0345
  H1 (IUT, Holm at alpha 0.05 over DES and PAIR): H1-DES NOT SUPPORTED (IUT p 0.1987); H1-PAIR NOT SUPPORTED (IUT p 0.1828)
    H1-DES specialisation (designed): I +0.039 [-0.076, +0.154] 9/19 positive; I - I_N +0.013 [-0.115, +0.141] 10/19 positive; I is GENERAL; reading: not supported
    H1-PAIR specialisation (paired): I -0.035 [-0.159, +0.088] 10/19 positive; I - I_N -0.011 [-0.137, +0.114] 10/19 positive; I is GENERAL; reading: not supported
  sensitivity (not scored), per fauna: H1-DES designed on the designed-complete seeds, n = 20 (extra seeds [29])
    H1-DES designed [per fauna, sensitivity (not scored)] against base (< 0): n=20 trimmed mean -0.103; Yuen p = 0.1662 (PRIMARY); t p = 0.0550; Wilcoxon p = 0.1012; component p used = 0.1662
    H1-DES designed [per fauna, sensitivity (not scored)] net of the null (< 0): n=20 trimmed mean -0.137; Yuen p = 0.0871 (PRIMARY); t p = 0.0930; Wilcoxon p = 0.0825; component p used = 0.0871
    sensitivity (not scored): with the scored PAIR p, Holm would give H1-DES NOT SUPPORTED (IUT p 0.1662); PAIR's per-fauna set is the scored set
  H-ALT increment A_SB^des(T+800) - A_SB^des(T+110) (> 0): n=20 trimmed mean +0.013; Yuen p = 0.4425 (PRIMARY); t p = 0.5550; Wilcoxon p = 0.4636
  H-ALT outcome FRESH: NOT DECIDED (MDE on the realised null 0.209)
  sensitivity (not scored), H-ALT increment on the common set (> 0): n=19 trimmed mean +0.039; Yuen p = 0.3266 (PRIMARY); t p = 0.3417; Wilcoxon p = 0.3113
  sensitivity (not scored), H-ALT increment on the common set (< 0): n=19 trimmed mean +0.039; Yuen p = 0.6734 (PRIMARY); t p = 0.6583; Wilcoxon p = 0.7026
```

**The trajectory, secondary, printed.** Read points T + 110, 400 and 600; each read point on its own seeds.

```
  d=110 designed A_SB -0.114 [-0.231, +0.003] 7/20 positive | designed A_SN -0.112 [-0.202, -0.022] 5/20 positive | paired P +0.082 [-0.062, +0.227] 14/19 positive | paired P_N +0.101 [-0.020, +0.223] 12/19 positive (P: +0.7 to +0.9 paired A/A units)
  d=400 designed A_SB -0.087 [-0.226, +0.053] 7/20 positive | designed A_SN -0.117 [-0.238, +0.004] 6/20 positive | paired P -0.013 [-0.169, +0.144] 10/19 positive | paired P_N +0.044 [-0.112, +0.199] 12/19 positive (P: -0.1 to -0.1 paired A/A units)
  d=600 designed A_SB -0.107 [-0.247, +0.034] 8/20 positive | designed A_SN -0.082 [-0.218, +0.053] 8/20 positive | paired P +0.012 [-0.174, +0.197] 11/19 positive | paired P_N +0.028 [-0.136, +0.191] 11/19 positive (P: +0.1 to +0.1 paired A/A units)
  d=800 designed A_SB -0.126 [-0.283, +0.031] 8/20 positive | designed A_SN -0.104 [-0.264, +0.055] 7/20 positive | paired P +0.152 [-0.059, +0.362] 9/19 positive | paired P_N +0.174 [-0.020, +0.368] 13/19 positive (P: +1.4 to +1.7 paired A/A units)
```

## The absent verdict: power at the usable n

H1-DES and H1-PAIR are both absent. The common set is **n = 19**, not the planned 20, because seed 29's co-evolved
fauna has been extinct since season 27 in all three arms.

**(a) The registered model at n = 19** (`iut_power.py`'s own model and T + 800 targets). At n = 20 it reproduces A2.8.3's
table (0.90 / 0.91 measured).

```
  MEASURED     T+800 n=19 F2-NOT-TURNOVER  EMPIRICAL DES-IUT 0.91  PAIR-IUT 0.91  Holm DES 0.88  Holm PAIR 0.88
  MEASURED     T+800 n=19 F2-NOT-TURNOVER  GAUSS     DES-IUT 0.93  PAIR-IUT 0.94  Holm DES 0.91  Holm PAIR 0.92
  MEASURED     T+800 n=19 C4NULL-SPLIT     EMPIRICAL DES-IUT 0.89  PAIR-IUT 0.25  Holm DES 0.80  Holm PAIR 0.25
  MEASURED     T+800 n=19 C4NULL-SPLIT     GAUSS     DES-IUT 0.90  PAIR-IUT 0.23  Holm DES 0.80  Holm PAIR 0.23
  MEASURED     T+800 n=19 HALF-SIZE        EMPIRICAL DES-IUT 0.32  PAIR-IUT 0.40  Holm DES 0.26  Holm PAIR 0.29
  MEASURED     T+800 n=19 HALF-SIZE        GAUSS     DES-IUT 0.33  PAIR-IUT 0.36  Holm DES 0.26  Holm PAIR 0.27
  CONSERVATIVE T+800 n=19 F2-NOT-TURNOVER  EMPIRICAL DES-IUT 0.92  PAIR-IUT 0.65  Holm DES 0.85  Holm PAIR 0.64
  CONSERVATIVE T+800 n=19 F2-NOT-TURNOVER  GAUSS     DES-IUT 0.91  PAIR-IUT 0.43  Holm DES 0.85  Holm PAIR 0.42
  CONSERVATIVE T+800 n=19 C4NULL-SPLIT     EMPIRICAL DES-IUT 0.89  PAIR-IUT 0.14  Holm DES 0.80  Holm PAIR 0.14
  CONSERVATIVE T+800 n=19 C4NULL-SPLIT     GAUSS     DES-IUT 0.90  PAIR-IUT 0.10  Holm DES 0.81  Holm PAIR 0.10
  CONSERVATIVE T+800 n=19 HALF-SIZE        EMPIRICAL DES-IUT 0.33  PAIR-IUT 0.18  Holm DES 0.24  Holm PAIR 0.14
  CONSERVATIVE T+800 n=19 HALF-SIZE        GAUSS     DES-IUT 0.32  PAIR-IUT 0.11  Holm DES 0.22  Holm PAIR 0.08
```

**(b) The realised T + 800 null** (cull20 − base on the scored common set) and the IUT on a Gaussian model of it:

```
  holistic     null A_NB (cull20 - base) at T+800: -0.031 [-0.168, +0.106] 9/19 positive; RMS 0.279 (n 19)
  conventional null A_NB (cull20 - base) at T+800: -0.009 [-0.142, +0.124] 8/19 positive; RMS 0.269 (n 19)
  REALISED-NULL GAUSS n=19 F2-NOT-TURNOVER  DES-IUT 0.89  PAIR-IUT 0.75  Holm DES 0.83  Holm PAIR 0.72
  REALISED-NULL GAUSS n=19 HALF-SIZE        DES-IUT 0.30  PAIR-IUT 0.21  Holm DES 0.22  Holm PAIR 0.16
  REALISED-NULL GAUSS n=19 NULL             DES-IUT 0.01  PAIR-IUT 0.01  Holm DES 0.00  Holm PAIR 0.01
  IUT MDE (80%, Holm) for H1-DES at n=19 on the realised null: 1.0 x RBT-101 F2's sizes (designed A_SB -0.220, paired P +0.270)
  IUT MDE (80%, Holm) for H1-PAIR at n=19 on the realised null: 1.1 x RBT-101 F2's sizes (designed A_SB -0.242, paired P +0.297)
```

**What the absent verdict excludes:**
- At n = 19 on the realised null, the scored IUT had **0.83 (DES) and 0.72 (PAIR)** power at RBT-101 F2's sizes:
  designed −0.22, paired +0.27, none of it turnover.
- Its 80% MDE is **1.0× (DES) and 1.1× (PAIR) F2's sizes**.
- **So H1's absence argues against an F2-sized effect persisting at T + 800 beyond turnover. It says little about an
  effect half that size:** the power there is 0.22 and 0.16.
- Under RBT-110's C4null split, the registered model gave H1-PAIR 0.23 at n = 19 (0.10–0.25 across targets), as
  A2.8.3 said before any arm.

## §10's predictions, scored against `readout.txt`

| prediction | registered | observed | scored |
|---|---|---|---|
| designed verdict at T + 800 | NOT SEEN 0.60 (ADAPTED 0.30, MALADAPTED 0.10) | NOT SEEN | hit |
| co-evolved verdict at T + 800 | NOT SEEN 0.85 | NOT SEEN | hit |
| designed A_SB at T + 800 | **+0.15** (−0.10 to +0.40), 0.6 | **−0.126** [−0.283, +0.031] | **miss** (outside the range, other sign) |
| co-evolved A_SB at T + 800 | +0.05 (−0.30 to +0.40), 0.6 | +0.046 | hit |
| designed I at T + 800 | +0.05 (−0.15 to +0.25), 0.6 | +0.031 | hit |
| income, secondary | FLAT on both, 0.75 / 0.85 | FLAT on both | hit |
| DEPTH: median few-births depth at T + 800 ≥ 15 in S | ~22, 0.9 | 20.6 co-evolved (n = 19), 21.3 designed | hit |
| null A_NB at T + 800 covers 0 | 0.8 / 0.85 | −0.031 [−0.168, +0.106]; −0.021 [−0.150, +0.107] | hit |
| every V-EXT gate passes on the 34 continuations | 0.9 | **not scorable**: the old-seed continuations were never run (OLD is UNREAD) | — |
| "neither fauna returns ADAPTED, SPECIFIC" (most exposed, 0.80) | | neither does | hit |

- **The falsifier did not fire:** there is no ADAPTED verdict on either fauna.
- §6's "positive control" condition is moot: Amendment 2 (F7) relabelled §6 as a post hoc C2 result.
- **The exclusion §10 promised:** there is no flat-ground designed response in A_SB and A_SN larger than about **0.21**
  income per bout at ~21 events. That is the realised two-interval resolution, about 0.28 |Δ0| (Δ0 designed +0.742),
  tighter than the 0.45 |Δ0| forecast. For the co-evolved fauna the resolution is 0.217, about 1.5 Δ0: as forecast, not
  a statement worth much.

## Gates (all PASS on FRESH)

- **V-POST** on all 60 arms, and **V0** (shift and cull20 against base before T) on all 20 seeds: PASS.
- **V-G** (garden populations complete, by name): PASS.
- **DEPTH:** no DEPTH SHORT.
- **OLD sample: UNREAD.**
  - The ten old seeds' 34 continuations to 1200 ("persistence", A2.2) were never launched. No arm, table or
    checkpoint exists.
  - `readout.py` prints OLD's gates as MISSING, "ALL GATES OLD: FAIL: nothing of this sample below enters a
    sentence", and every OLD line as UNREAD.
  - That is the registered behaviour. Nothing in this report reads OLD, except the Z10 OLD line, which comes from
    RBT-101's committed seasons.

## Printed, not scored

- **Z10:** paired −0.636 [−0.729, −0.543]. The garden's Δ0 is designed +0.742 and co-evolved +0.145. The Δ0 level
  carries a common-world error, which cancels in every contrast.
- **§7 income:** FLAT (not resolved) on both faunas. The designed residual level net of Z10 over [T+700, T+800) is
  −0.135 [−0.278, +0.009].
- **Sorting against novelty at T + 800:**
  - designed sorting part −0.127 [−0.227, −0.028], novelty part +0.001;
  - co-evolved −0.063 / +0.109.
  - These are approximate: ancestry shares.
- **A1.6's selection differential** is printed per arm and read point in `readout.txt`. It is diagnostic and names no
  mechanism.
- **Split-half measurement sd** of a seed's A_SB at J = 32, T + 800: 0.070 co-evolved and 0.130 designed.
- **Nulls:** RBT-105's depth-matched A/A RMS is 0.159, and `aa_spread.txt` is quoted verbatim.

## POST HOC (not registered tests; they enter no verdict; `posthoc.txt`)

**1. A2.9 point 3, the "general" reading, recorded before H-REP as a hypothesis to watch.** The designed fauna's
RESPONSE on the old, random ground, net of the cull null (G_S^random − G_N^random):

| read point | designed, vs base | designed, net of the null | co-evolved, net of the null |
|---|---|---|---|
| T + 110 | −0.085 [−0.142, −0.028] 5/20 | −0.067 [−0.120, −0.015] 5/20 | −0.038 [−0.128, +0.053] |
| T + 400 | −0.102 [−0.159, −0.046] 3/20 | −0.096 [−0.131, −0.061] 3/20 | −0.058 [−0.144, +0.028] |
| T + 600 | −0.127 [−0.186, −0.068] 2/20 | −0.111 [−0.182, −0.040] 5/20 | −0.048 [−0.127, +0.031] |
| T + 800 | −0.157 [−0.224, −0.090] 3/20 | −0.116 [−0.178, −0.055] 4/20 | +0.075 [−0.065, +0.215] |

- **What it shows:**
  - The designed population that lived through flat ground is worse **on the terrain it no longer faces**, relative to
    base and to cull20.
  - The deficit is resolved at every read point, and it grows with depth.
  - On flat ground the same populations' A_SB and A_SN are not resolved at T + 800.
- **What it suggests, as a hypothesis to test and not a finding:** the designed fauna's post-C4 change is a loss of
  old-terrain competence (the "general" reading of A2.9), not a gain on flat ground.
- **Caveats:**
  - It is post hoc, printed on the same data, unadjusted, with t intervals, and it was chosen for display after the
    registration named it.
  - The registered test of it would need a fresh registration.

**2. The per-seed table at T + 800** is in `posthoc.txt`.

**3. The per-fauna H1-DES** (n = 20) is #345's labelled sensitivity. It gives IUT p 0.1662: NOT SUPPORTED either way.
H-ALT's increment on the common set (n = 19) is +0.039, and resolved in neither direction.

## Provenance

- **Where the T + 800 (and T + 400, T + 600, c0) populations come from.** They are **restored copies of each arm's
  checkpoint (`ckpt/rbt-107-fresh-ARM-SEED`, each at 1200/1200), cut to season 1160 = T + 800** before any table was
  written. This is the coordinator's cut discipline: `hrep/hrep_cut.py`, then RBT-92 `tables.py`. `h1/h1_run.sh` does
  it; `h1/source/ARM-SEED.txt` names each checkpoint and the season it was restored at.
- **The units and labels are `garden_run.sh readout`'s, verbatim.**
  - c0 at T − 1 from the base, and base, shift and cull20 at T + 800, 400 and 600, for both faunas.
  - J = 32, as halves 0..15 and 16..31, merged into `garden/readout/`, the path the registered `readout.py` reads.
- **T + 110 and Z10 are H-REP's committed files, copied, not re-run.** H-ALT's increment and the trajectory therefore
  use exactly the numbers H-REP was scored on.
  - `d110_reuse_check.txt`: seed 11 base designed, worlds 0..15, re-gardened from the H1 copy, cut to 1160. Its 60 data
    rows are **byte-identical** to H-REP's committed part.
  - The H-REP lines in `readout.txt` reproduce the merged H-REP verdict exactly (0.0171 / 0.0782).
- **The hashes in `source.txt` are not durable** (H-REP adversary F10). `durable.sh` force-pushes one commit per save.
  The restored season, 1200, is the durable part.
- **Compute:**
  - seven shards (`h1/h1_shard.sh K 7`): shard 0 in this session, and shards 1–6 in six sessions tagged `hive-0926`,
    `rbt`, `rbt-107`, `garden`, each archived once its output was merged.
  - Shard 2 was slow (5 h 10 min). As a hedge I started its seeds locally in reverse order. Shard 2 pushed first, and
    the local partial output was discarded, not mixed.
  - The merged files equal shard 2's commit: the diff against it shows additions only (the other seeds).

## Faults found at run time, and fixes

1. **`depth.py measures()`: an extinct fauna.**
   - Seed 29's co-evolved fauna has nobody alive at T − 1. The C0 founder set was empty, and `statistics.median` raised,
     stopping the readout in the DEPTH section.
   - The fix: `measures()` returns no measures when C0 is empty. The caller already skips an empty result, so the seed
     is absent from DEPTH for that fauna (A1.2's UNREAD).
   - A test is added (`tests/test_rbt107_readout.py`).
   - **It changes no scored number.** DEPTH is a printed gate line. Its co-evolved median is over 19 seeds, and no
     DEPTH SHORT is triggered either way.
2. **No other code changed.**
   - `readout.py` is integration's, which includes #345's print-only sensitivity.
   - `garden.py` and `garden_merge.py` are unchanged since H-REP. The extinct seed 29 co-evolved gardens merge as
     header-only files, as at H-REP.
   - The garden route adds only the scripts `h1/h1_run.sh` and `h1/h1_shard.sh`, and the print-only `h1/h1_power.py` and
     `h1/h1_posthoc.py`.

## What this does and does not say

- **It does say:**
  - On 19 fresh C4 seeds, at ~21 reproduction events, neither registered H1 hypothesis is supported, and neither fauna
    reads ADAPTED on §5.3.
  - H-ALT is NOT DECIDED.
  - Adaptation to flat ground was **not seen**, and designed effects larger than about 0.21 income per bout are
    excluded on A_SB/A_SN.
- **It does not say:**
  - That there is no response. Effects half of F2's size had power 0.16–0.22.
  - That the H-REP designed decline reversed. The increment is +0.013, not resolved.
- **The post hoc old-terrain deficit** is the one resolved, growing pattern in these data. It is post hoc. It is
  printed so that a later registration can test it, not as a finding.

## Suite

The full suite passes in a clean `pip install -e '.[dev]'` venv without scipy: **365 passed**.
