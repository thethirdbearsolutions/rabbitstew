# RBT-92 adversary round 1, addendum: the round against the current head

The coordinator's 13:46 note ("the design moved under you") was delivered to me after the 13:55 post, so round 1 was written against `292d6c5`. This addendum reads the current integration head `a16a859`, which carries PR #87: amendments 1–2 and the shared V1 cap fix.

Re-derived on it:
- `pytest`: 273 passed;
- `onset_rules_dryrun.py`: byte-identical to its committed readout;
- `smoke.sh 801 9901`: exit 0, V0–V2 PASS on 2/2, and the 0/0 path exercised (`rederive_smoke_head.txt`).

| finding | status on the head |
|---|---|
| **F1** onset reads post-onset control deaths | **Resolved.** `onset.py` reads only [280, 340) (`tot(t, t+10)` for t ≤ 330), before every T it can return. It lands in the trough: holistic deaths over [T, T+10) are 10, 2 and 4 on RBT-71, against 12, 4 and 6 for the 12:42 rule and 28, 20 and 16 for the [T−20, T) ruling. That is better than my proposed fix, which had the same aim. The references it prints are unselected. Credit. |
| **F4a** extinct fauna dropped from R-body, the guard and R-shift | **Resolved.** `Arm` sets income to 0 from extinction on, and `rbody` and the contrasts no longer skip. It is pinned by `tests/test_rbt92_readout.py` (survivors' +0.6 against the truth −0.15). |
| **F4b** class E reads a co-evolved collapse beside a thriving designed fauna as "both fail" | **Open.** Amendment 2 says a co-evolved extinction "reads as C or E by the rules as written". The E branch (`readout.py`, the `ez` test and `cls = "E. both fail"`) still fires on co-evolved income < 0.25 alone, and is checked before C. Still must fix before launch: split E1/E2 and report E2 with the falsifier. |
| **F3** body digest changes on 436/511 births; B and S floor at 0 | **Open.** Nothing touches `body_structure` or B/S. Still must fix before launch. |
| **F5** remainder group | **Open.** Not a launch blocker. |
| **F6** null channel near empty | **Partly addressed.** Amendment 2 item 6 handles k = 0/0 (the null is the baseline; R-null = R-shift, said). The scoring of the R-null prediction on k > 0 seeds only is still asked. |
| **F8** equivalence form beside B | **Partly addressed.** `BMIN = 8` makes B unreachable below eight seeds, which is right. The |mean| + r < 0.10 line is still asked. |
| **F2**, **F10**, the §8 sentence | **Open** (caveats). `onset.py`'s docstring still says "has no solution on a selected arm" (probe D). |
| V0 now also compares `lineage-last.txt` rows with generation < T − 1 | **New, and correct.** The cut matches the measured "a death in season s is a last row at s − 1" (probe A: 1200/1200). |

**New, small:** `runs/RBT-92/smoke.txt` on the head is stale. It records `readout.py exit status: 1` with V0 FAIL on every arm, which is the superseded < T cut. The current code gives exit 0 and V0–V2 PASS (`rederive_smoke_head.txt`). **Re-commit it** so the file matches the code.

**Must fix before launch, on the current head: F3 and F4b.** F1 and F4a are done.
