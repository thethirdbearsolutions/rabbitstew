# READOUT-STAGE1: corrections adopted by the coordinator (COORD-RULING-517 C2)

*These annotations govern the reading of `READOUT-STAGE1.md` wherever the two differ.*
- *Source: the run adversary's MINOR 1–5 (`../stage1-readout-run-adversary/ADVERSARY.md`).*
- *No call, Holm decision or §8 line changes.*
- *Numbers are copied from `stage1_readout.txt` (`Lnnn`). None was computed here.*

## A1. §1 headline: how fragile the EARNS-H side is (MINOR 4)

The headline **EARNINGS DEPEND** (L423) is correct under R1. **It rests on an H counting set of exactly 2 EARNS-H calls, both at non-habitable points:**

| point | call | n | detail | line |
|---|---|---|---|---|
| `c1-p010-PW-L` | EXCLUDED-H | 2 | t +23.91 on df 1, p 0.0266 | L247 |
| `c1-p080-HP-L` | PARTIAL-D | 3 | p 0.0335 | L290 |

- `c1-p080-HP-L` passes BH by 0.0013: the 8th smallest p is 0.0335, against a threshold of 0.0348.
- There is no EARNS-H at any of the 15 habitable points. Under the non-registered habitable-only reading, the line reads DEPENDS ONLY THROUGH HABITABILITY (D) (L424).
- The final BH after Stage 2 can change this headline.

## A2. §1 table: the anchor belongs under NOT RUN (MINOR 5)

Plan §4.2 item 8 counts the anchor under NOT RUN. Read the L row's body calls with the anchor's own category, `RBT-118 (not available) 1 (0.11)`, merged into NOT RUN:

> **NOT RUN 4 (0.44)**, including the anchor `c1-p030-U-L` (RBT-118, not available).

The scorecard (L617) already counts it that way.

## A3. §8 and the observations: MARGINAL is a censoring artifact at Stage 1 (MINOR 3)

- MARGINAL is set on all 8 EARNS calls by construction.
- `scripts/regime.py:175` averages per-birth income over **complete** lives only. In the last window (240–299), the complete lives are mostly those that died early, so per-birth income is biased towards short, low-gain lives.
  - H per-birth income lies between −0.048 and +0.020 at every point.
  - The 240-window viability is about −1 everywhere.
- **MARGINAL at Stage 1 therefore carries no information about the economy.** The calls count, flagged, as DESIGN §6.1 requires.
- The report's Observation 2 should be read with this mechanism, not as an open question.

## A4. Observation 4: the share Wald's scope (MINOR 2)

- The secondary share model (L414: TESTABLE, χ² 2.056, df 6, p 0.9145) was fitted on **every completed M seed at all 9 M points**.
- Only one of those points, `c2-p030-U-G`, is habitable.
- Under the habitable scope that ruling NOTE 3 assumed, it would be NOT TESTABLE. **It must not be read as a world-model result.** It is descriptive and outside Holm.

## A5. §9 scorecard, item 2 (MINOR 1)

- The scripted line stands: **NOT SHOWN (15 of 36; RESOLVING 0)** (L617). It counts body calls of NOT RUN, SATURATED or anchor.
- Under plan §0's reading, where a point with no N arm counts as share NOT RUN, the same prediction reads **AS PREDICTED (32 of 36 not run; RESOLVING 0)**.
- The two readings differ. The scorecard is descriptive and changes no call. The Stage-2 plan must pin which reading applies (COORD-RULING-517 C3).

## A6. Small prose fixes (NOTE 13)

- §4: "Every point is labelled PW" should read **"every N point"**.
- The R-A pair `c1-p018-U-L` is selected on clause (a) by a sign difference that is noise: x̄ +0.001 against −0.003 (L433). The selection conforms to the plan; it carries no information beyond that.

## A7. Integrity: silent EPA overflow is not ruled out (COORD-RULING-520 D2)

- The one CRASHED unit is a MuJoCo 3.14.0 EPA horizon overflow (#520, #521).
- A non-crashing overflow is mechanically possible. Silent corruption of another Stage-1 run is therefore **not ruled out** outside the scanned coverage: 0 overflows in 30 M units × 3 seasons (#520), and in 528 S plus 240 M unit-seasons (#521), with near misses at horizon 17–23 in both arms.
- The integrity verdict (I-1, I-15) stands as scripted. This annotation qualifies it.
- **The owner-approved M/N silent-corruption scan has reported** (`mn-corruption-scan/scan_report.txt`, #544 → `f38df13`; counts only, per COORD-RULING-527):
  - **37 of 37** Stage-1 M and N forks (M 30, N 7) replayed on the instrumented build v3 are **IDENTICAL** to their stored branches and **CLEAN** over **seasons 60–299**: no overflow logged, complete logs. None is named DIFFER, NO-REFERENCE, OVERFLOWED or UNLOGGED.
  - Excluded: `c2-p030-U-G/129001/M` (the CRASHED unit; quarantined).
  - **Still UNSCANNED:** the S60 phase upstream of every M and N (S's seasons 0–59), and the S arms. Silent corruption there is **not ruled out**.
  - Whether to scan S (~600–800 core-h) is the owner's decision (OWNER-DECISIONS-2026-10-03 item 1).
- **The owner decided to run the S scan** (`../coordinator/OWNER-DECISIONS-2026-10-09.md` item 1, settling
  OWNER-DECISIONS-2026-10-04 item 1). It replays all 288 Stage-1 S chains from season 0 on the instrumented build. Each
  chain gets two byte-for-byte comparisons against its stored branches: ckpt60 (the S60 phase, seasons 0–59, upstream of
  every M and N) and S (seasons 0–299). Code, lanes and lock: `../s-corruption-scan/` and `../lanes/SSCAN/`.
  - **Its result is recorded here when it reports** (`s-corruption-scan/scan_report.txt`), as counts only, with the
    M/N scan's states: CLEAN (seasons 0–59) or CLEAN (seasons 0–299), OVERFLOWED, UNLOGGED; verdicts IDENTICAL,
    DIFFER, NO-REFERENCE.
  - **Until then** the S arms and the S60 phase stay **UNSCANNED**, as above.

---
_Generated by [Claude Code](https://claude.ai/code)_
