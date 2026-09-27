# RBT-107 H-REP readout adversary (PR #338, head `e2f5a15`)

**Overall verdict: WRONG. The H-REP-DES verdict line moves.**

- **H-REP-DES moves from NOT SUPPORTED to SUPPORTED** under the seed set that was fixed before the data existed.
  - The IUT p is **0.0171**, which is ≤ Holm's first threshold of 0.025.
  - The A2.9 label then reads **"general, not flat-specific"**, because I's interval contains 0.
- **H-REP-PAIR stays NOT SUPPORTED** under every reading (IUT p 0.0782).

Every number #338 prints is arithmetically right, and its gates and no-peek hold. The one wrong thing is the seed set
used for DES:
- #338 scores DES on 20 seeds.
- The registered `readout.py` and #338's own pre-data draft score it on the 19 seeds that have all four contrasts.
- #338 changed the rule after the per-seed outputs existed, and REPORT.md says the change "changes no scored rule".
- The change moves the DES verdict.

A1.2's prose can be read in #338's way, so **the coordinator has to rule** (F1). The case for the pre-data rule is
set out there.

Scripts (stdlib only, no scipy, nothing imported from `readout.py`, `stats107.py` or RBT-92 except where named):
- `rederive.py` → `rederive.txt`: every scored p, from the committed garden files.
- `yuen_se.py` → `yuen_se.txt`: three Yuen standard-error conventions.
- `gates.py` → `gates.txt`: no-peek, V0 and V-G, from the committed tables.
- `spotcheck.sh` and `cutcheck.py` → `spotcheck.txt`: restore, cut and table seeds 11, 25 and 29 from their checkpoint
  branches, and re-garden seed 29's designed fauna in all three arms.

Run them from a checkout of #338's head, e.g. `python runs/RBT-107/hrep/adversary/rederive.py`.

**No-peek.**
- Nothing from season ≥ 471 was read or printed.
- The restored copies were cut to 470 before any table was written.
- `durable.sh restore`'s "restored at season X" line was discarded.
- `runs/RBT-107/fresh/*/` was opened for `config.json` only.

## Findings

| # | finding | class | moves a verdict? |
|---|---|---|---|
| F1 | DES seed set: the pre-data rule (registered `readout.py` and #338's 03:26 draft) gives n = 19 and DES **SUPPORTED**; #338's post-data per-fauna rule gives n = 20 and NOT SUPPORTED | **MUST-FIX** | **yes, H-REP-DES** |
| F2 | `stats107.yuen`: the docstring's se and the code's se differ at n = 19, and the three conventions split the F1 verdict | **MUST-FIX before H1**; CAVEAT on F1 | only under F1's n = 19 |
| F3 | H1 will read the common set (`readout.py confirmatory()`), but H-REP reads per fauna; H-ALT's increment uses the designed seeds only | **MUST-FIX before H1** | H1 not yet read |
| F4 | REPORT.md fix 3 says "none changes a scored rule". It does change one. | **MUST-FIX** (disclosure) | — |
| F5 | PAIR n = 19 is registered under both readings, not a choice. Coding seed 29's extinct fauna as 0 is unregistered, and even so it gives IUT p 0.100. | NONE | no |
| F6 | Band rule: the registration says only "counts only if". Three conventions give the same verdicts. | CAVEAT | no |
| F7 | `garden.py base_sim` fallback | NONE | no |
| F8 | `garden_merge.py` extinct carry | NONE | no |
| F9 | `hrep_run.sh`: seed 11's tables regenerated | NONE | no |
| F10 | `source.txt` hashes are not durable, because checkpoint branches are force-pushed | CAVEAT | no |
| F11 | Cut, no-peek, V0 and V-G | NONE (PASS) | no |
| F12 | A2.8 and A2.9 lines; the post hoc RESPONSE_random is kept out of the verdict | NONE | no |
| F13 | Seed 29's designed fauna lived alone from season 27 on, and it is the seed that decides F1 | CAVEAT | — |

---

### F1 (MUST-FIX): the DES seed set was changed after the data existed, and the change moves the verdict

**What the registration says.**

1. **A1.2 (prose).** "If any arm's fauna is extinct at a read point … That seed reads UNREAD **for that fauna**."
   - This is per fauna.
   - Read literally, DES (a designed-only hypothesis) keeps seed 29. That is #338's reading.
2. **`readout.py confirmatory()`, the registered code.** A2.8 says "`readout.py` implements this: `iut()`, `scored_p()`".
   The line was committed in `f53b1e8` (22:42, A2.8, before any arm) and kept in `6828154` (A2.9, before any read):
   ```
   seeds = [s for s in sm.seeds if all(s in table(sm, k, d, key) for k in KINDS for key in ("SB", "SN"))]
   ```
   - DES and PAIR are **both** scored on the seeds with all four contrasts in both faunas.
   - Seed 29 drops out of DES.
3. **#338's own first draft, `56b1c7e`, 03:26, before any garden output** (`hrep/hrep_readout.py:92`), has the same
   common-set line.
4. **The switch to per fauna came in `a7bf4d2` (05:20).** That commit also carried the data and `readout.txt`.
   - REPORT.md says the switch was made "after the per-seed outputs existed, but before any H-REP line was printed".
   - Seed 29's designed values were readable in the garden files at that point: A_SB +0.342 and A_SN +0.291. They are the
     highest designed A_SB after seed 19 (+0.392) and the highest designed A_SN of all 20 seeds.
   - The switch moved the result toward NOT SUPPORTED, so it is not a search for a positive finding.

**What each rule gives** (`rederive.txt`: independent code, matching `readout.txt` to 4 decimals where they overlap):

| seed set | DES n | A_SB Yuen / Wilcoxon | A_SN Yuen | DES IUT p | PAIR n, IUT p | Holm (min p vs 0.025) |
|---|---|---|---|---|---|---|
| per fauna (#338) | 20 | 0.0427 (in band) / 0.0266 | 0.0054 | 0.0427 | 19, 0.0782 | **neither** |
| **common (registered code, pre-data)** | 19 | 0.0171 / 0.0102 | 0.0025 | **0.0171** | 19, 0.0782 | **DES SUPPORTED**, PAIR not |

- Under the common set, the designed A_SB trimmed mean is −0.141 (t p 0.0094) and A_SN's is −0.125.
- The A2.9 label beside DES would be: I −0.044 [−0.119, +0.032], and I − I_N −0.058 [−0.101, −0.016] (below 0).
- I's interval does not exclude 0, so the specialisation is **GENERAL**. The line would read **"SUPPORTED, general, not
  flat-specific"**.

**Why I take the pre-data rule as the registered one.**
- A2.8.4 says: "Nothing in §5.5 changes after H-REP is read … Any change after H-REP is an amendment labelled
  post-H-REP, and it is not scored."
  - A change to the analysis set made while the garden outputs sat on disk falls under that rule.
  - The only analysis set specified in code before any data existed is the common set, in the registered `readout.py`
    and in #338's own draft.
- A1.2's per-fauna sentence is about which seeds are UNREAD for a fauna.
  - It does not say that the two hypotheses of one Holm family are read on different seed sets.
  - The code that A2.8 names as the implementation reads them on one set.
- The per-fauna reading is a defensible reading of A1.2. It is not what was fixed before the data.

**The fix.**
- The coordinator rules which set is scored.
- `readout.txt` and REPORT.md print both lines, with the ruled one marked scored and the other labelled post-H-REP.
- If the pre-data rule stands, the headline becomes "H-REP-DES SUPPORTED (IUT p 0.0171), general, not flat-specific;
  H-REP-PAIR NOT SUPPORTED (IUT p 0.0782)". A2.8.3's size-to-quote rule applies to DES: its net-of-null trimmed mean is
  −0.125.

### F2 (MUST-FIX before H1; CAVEAT on F1): `stats107.yuen`'s docstring and code disagree on the se

- **The two definitions:**
  - the docstring (and A2.1's description) gives se = s_w / ((1 − 2·trim)·√n);
  - the code uses s_w / ((h/n)·√n), with h = n − 2g.
- **When they differ:** they agree when 0.2n is an integer (n = 20). At **n = 19**, h/n = 13/19 = 0.684 against 0.6.
- **The self-checks do not catch it:** `stats107`'s self-checks test the trimmed mean and df, never the se.

`yuen_se.txt` gives the p under each convention:

| component | code (h/n) | docstring (1 − 2γ) | Yuen 1974 √((n−1)s_w²/(h(h−1))) |
|---|---|---|---|
| DES A_SB, n = 20 | 0.0427 | 0.0427 | 0.0452 |
| DES A_SB, n = 19 (common) | **0.0171** | **0.0291** | 0.0181 |
| DES A_SN, n = 19 | 0.0025 | 0.0055 | 0.0028 |
| PAIR P, n = 19 | 0.0482 | 0.0698 | 0.0501 |
| PAIR P_N, n = 19 | 0.0209 | 0.0344 | 0.0220 |

- **Effect on F1:** under the docstring's convention, the common-set DES IUT p is 0.0291 > 0.025, and DES stays NOT
  SUPPORTED.
  - The registered object is `stats107.yuen` as coded. A2.1 names it, and A2.4 and A2.8's size (5.3–6.3%) and power
    were computed with it.
  - So F1's flip holds under the registered code and under Yuen's own form, but not under the docstring.
- **Effect on PAIR:** none. It fails under all three.
- **Why it matters for H1:** H1-PAIR is n ≤ 19 (seed 29), so the ambiguity is certain to arise at T + 800. It should be
  pinned before T + 800 is read, by correcting the docstring to the code and adding an se self-check at n = 19.

### F3 (MUST-FIX before H1): H1 would be scored on a different seed rule from H-REP's

- `readout.py confirmatory()` (H1 at T + 800) still reads both lines on the common set.
- `hrep_readout.py` reads them per fauna.
- H-ALT's increment (`inc = d8[s] − d1[s]`) is designed-only (n = 20), while H1-DES, which H-ALT's outcomes depend on
  (A2.8.2), would be n = 19.
- Whatever F1's ruling, one rule should cover H-REP, H1 and H-ALT. It should be written into a labelled post-H-REP
  amendment and `readout.py` before any T + 800 garden is read.

### F4 (MUST-FIX): the disclosure

- REPORT.md, "Faults found at run time … (all implementation; none changes a scored rule)", item 3, calls the per-fauna
  rule "A1.2's rule applied per fauna".
- It does not say that the registered code and the pre-data draft used the common set, or that the verdict differs.
- That has to be stated beside the verdict lines, not only in the faults section.

### F5 (NONE): PAIR n = 19 is registered, not a choice

- P = A_SB^co − A_SB^des needs the co-evolved garden, which is empty for seed 29 in all three arms.
  - The fauna's last season with anyone alive is 26 in base, shift and cull20 alike (`gates.txt`).
  - It is empty under both A1.2 and the registered code.
- There is no second way that the registration defines.
- As an unregistered sensitivity, I coded the extinct fauna as earning 0 in every arm (contrasts 0), so P = −A_SB^des.
  - PAIR on n = 20: P +0.061, p 0.100; P_N +0.082, p 0.053; IUT p 0.100.
  - PAIR is not SUPPORTED either way.

### F6 (CAVEAT): which p is used in the band

- A2.8.4 says a Yuen p in (0.04, 0.05] "counts only if the exact Wilcoxon p … is also ≤ 0.05".
- `scored_p` uses max(Yuen, Wilcoxon). Two alternatives:
  - "Yuen if Wilcoxon passes, else 1";
  - "Wilcoxon's p".
- **No verdict depends on the convention,** in either seed set (`rederive.txt`):
  - DES n = 20 is 0.0427 / 0.0427 / 0.0266, all > 0.025;
  - PAIR is 0.0782 / 1 / 0.0782;
  - the common-set DES is not in band.
- **Checks on the comparison and the directions:**
  - 0.0427 against Holm's α/2 = 0.025 is the registered comparison (A2.1, A2.8.2), since Holm over two compares the
    smaller p with α/2.
  - The directions are as registered: DES tests −x ("< 0"), PAIR tests +x ("> 0").
  - The IUT takes the max of the two component ps.

### F7 (NONE): `garden.py base_sim`

- **It can only exit, never change a number.**
  - No fresh seed has an RBT-90 directory.
  - The fallback returns the arm's own `sim` only if it equals `forage-801`'s key for key.
  - Old seeds take the unchanged path.
- **Checks:**
  - All 29 fresh `config.json`s I could reach have a `sim` identical to RBT-90 801's: the 20 committed ones under
    `fresh/`, plus the 9 restored copies.
  - Seed 29's designed gardens were re-run under the fallback: 6 parts × 60 rows, **identical** to the committed rows
    (`spotcheck.txt`).

### F8 (NONE): `garden_merge.py`'s extinct carry

- It triggers only when every part is the header-only "nobody alive" file, and parts that disagree are an error.
- Only seed 29's co-evolved fauna triggers it, in all three arms.
- Its two parts carry the same single header line.
- `readout.py garden()` reads it as `{}`, and `contrasts()` returns None, which makes the seed UNREAD.
- It cannot alter a living population's numbers.

### F9 (NONE): seed 11's regenerated tables

- I restored `ckpt/rbt-107-fresh-{base,shift,cull20}-11` myself, cut to 470 and ran `tables.py`.
- `seasons.txt`, `lineage-last.txt` and `events.txt` are **byte-identical** to the committed ones for all three arms.
- Seeds 25 and 29 are identical too (`spotcheck.txt`).

### F10 (CAVEAT): provenance hashes

- `source.txt` records the checkpoint branch's head when the line was written.
- `durable.sh` force-pushes one parentless commit per save, so the recorded commit can disappear.
  - For example, `ckpt/rbt-107-fresh-base-11` was recorded as `88e8a226` and is now `a7dbc03`.
  - The restored season is the durable part.
- Provenance rests on re-cut identity (F9), not on the hash.

### F11 (NONE): the cut, no-peek and gates

- **The cut.**
  - `hrep_cut.py` cuts `lineage.jsonl` on `generation`, which is the observation season (`tables.py`: born =
    generation − age), and cuts cohorts and history on season. It deletes stale snapshot tables.
  - `cutcheck.py` confirmed, on 9 restored copies, that no row is past 470 and no stale table is left.
  - The only uncut top-level files are `config.json`, `event.txt` and `state.json`. `garden.py` reads the first; the
    third only gives the season number.
- **The population is unchanged by the cut:**
  - `alive_at(470)` needs born ≤ 470 ≤ last seen;
  - anyone alive at 470 is seen at 470 in both the cut and the uncut lineage.
- **Gates** (`gates.txt`, independent parser, from the committed files):
  - NO-PEEK: `seasons.txt` and `lineage-last.txt` end at 470, `events.txt` at 360, and the z10 rows carry no season;
  - V0 PASS: 20 seeds × {shift, cull20} vs base, seasons 0..359, five columns, both faunas;
  - V-G PASS: all 120 populations equal lineage-last's alive set at 470 by name and seasons.txt's alive count, and both
    parts have the same names in the same order.

### F12 (NONE): A2.8 and A2.9

- The IUT forms, directions, the max and Holm over (DES, PAIR) are as registered.
- The paired contrasts are computed as registered:
  - I = (S_f − S_r) − (B_f − B_r);
  - I_N = (N_f − N_r) − (B_f − B_r);
  - the paired I is I^co − I^des.
- The labels are as registered: `specificity()` is direction-aware with t intervals. Both lines read GENERAL (my
  numbers match), and "reading: not supported" is correct for #338's verdicts.
- **The post hoc RESPONSE_random line** (−0.067 [−0.120, −0.015] net of the null) is printed under "PRINTED, NOT
  SCORED", labelled post hoc, and enters no verdict.
- **Under F1's common set,** DES would carry the "general, not flat-specific" label.

### F13 (CAVEAT): seed 29

- Seed 29's designed fauna evolved alone from season 27, in all three arms. It is a one-fauna ecology for 330 seasons
  before the onset.
- It is also the seed that separates the two readings in F1.
- This is not a reason to drop it, since the registration has no such rule. It is a reason the coordinator's F1 ruling
  should be made on the registration's text and timing, not on seed 29's values.

## Question 5: do the garden fixes alter H1 (T + 800)?

**No.** `base_sim` returns the identical config or exits, and the merge change touches only all-extinct parts.

The MUST-FIXes before H1 are elsewhere:
- **F3:** one seed-set rule for H-REP, H1 and H-ALT, written down now.
- **F2:** pin the Yuen se, since n = 19 for H1-PAIR.
- **Seed 29:** its co-evolved fauna is UNREAD at T + 800 (n ≤ 19 for PAIR, as REPORT.md says). A2.8.3's power was for
  n = 20.

## Suite

- #338's head (`e2f5a15`), in a clean `pip install -e '.[dev]'` venv with no scipy: **342 passed**.
- This branch (integration `0ccec0d` plus these files), in a second clean venv with no scipy: **361 passed**.
