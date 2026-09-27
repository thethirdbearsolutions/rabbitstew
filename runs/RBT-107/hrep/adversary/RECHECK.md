# RBT-107 H-REP re-check: #338 amended to `7b35fbc`, per the coordinator's 05:50 ruling

**Result: all four items PASS.** Two small CAVEATs, neither a MUST-FIX. No-peek holds: nothing after season 470 was
read.

## 1. `hrep_readout.py`: PASS

- **The scored line is the registered one.** The seed set is `readout.py confirmatory()`'s line verbatim (seeds with all
  four contrasts in both faunas), n = 19 for both lines.
- **The verdict:**
  - H-REP-DES is SUPPORTED, IUT p 0.0171, "general, not flat-specific".
  - H-REP-PAIR is NOT SUPPORTED, IUT p 0.0782.
  - Both match my independent `rederive.py` (COMMON rows) to 4 decimals, including the A2.9 I and I − I_N lines.
  - The A2.8.3 size is −0.125, which is the Yuen trimmed mean of the n = 19 A_SN (my −0.1253).
- **The per-fauna DES** (n = 20, 0.0427) prints beneath as "post-data sensitivity (not scored)".
- **The F2 sensitivities print too:** 0.0171 / 0.0291 / 0.0181 for DES and 0.0782 / 0.0698 / 0.0501 for PAIR. These
  equal my `yuen_se.txt` after the band rule is applied.
- **`readout.txt` regenerates byte-identically** from the committed files (`cmp`, clean venv).
- **The printed-not-scored lines** (RESPONSE_random, REFUND, split-half) now use the common set too. That is consistent,
  and none of them is scored.

## 2. `REPORT.md`: PASS

- The scored lines and the verdict table are at the top.
- The F4 disclosure is there:
  - the timing (`f53b1e8` and `6828154` registered, `56b1c7e` pre-data draft, `a7bf4d2` post-data switch with the
    garden files on disk);
  - 0.0427 → 0.0171;
  - "that was wrong".
- The fragility table (F1, F2 docstring, F2 Yuen 1974) and F13 are stated plainly.
- The report states that PAIR fails under every reading.
- **CAVEAT (wording):** "the designed fauna's post-C4 income contrast" should read "garden gain contrast". A_SB is a
  common-garden gain, not the ecology's income.

## 3. `stats107.py`: PASS

- The diff since `e2f5a15` touches only the module docstring and adds one self-check (the se at n = 19).
- `tcdf`, `t_test`, `yuen`, `wilcoxon` and `holm` are unchanged. The self-checks pass.
- I checked the new self-check's constant by hand: winsorized s_w² = 398/18 = 22.111.
- `readout.txt` is identical, so the code's behaviour is identical.

## 4. The post-H-REP note in PREREGISTRATION: PASS

- It is appended after A2.9 and labelled interpretation only.
- It pins what the registered code already does:
  - the common set for H1;
  - the designed-only seeds for H-ALT's increment (`inc = d8[s] − d1[s] for s in d8 if s in d1`);
  - H-ALT on the IUT's H1-DES;
  - Yuen as coded.
- It changes no statistic, α, Holm family, read point or outcome.
- `runs/RBT-107/readout.py` is untouched: its diff against `e2f5a15` is empty.
- **CAVEAT:** note point 2 says "the H1 readout prints the other seed set beside each H1 line", but `readout.py` does
  not print it yet. Add that print-only sensitivity to `readout.py` before T + 800 is read. It must not touch
  `confirmatory()`'s scored path. The alternative is to reword the note as "will print".

## Suite

- #338's head `7b35fbc` merged with #341 (`5fa0e2a`, a local merge only), in a clean `pip install -e '.[dev]'` venv
  with no scipy: **361 passed**.
- The same merge re-runs `rederive.py` unchanged.
