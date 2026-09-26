# RBT-92 adversary: confirmation after the re-check (not a new round), integration `a8169e1`

**CLEAR-WITH-CAVEATS.** Both residuals from the 14:32 re-check are fixed:

- **Residual 1 (`readout.py` `r` shadowing): fixed.** Line 492 now reads `for row in tsv(gp)`.
  - `recheck_readout_n6.sh` exits 0 through the classifier at n = 6.
  - `smoke.sh 801 9901` output is identical to the committed `smoke.txt`.
  - A test through the classifier at n = 6 with `groups.txt` present was added (PR #115).
  - `pytest`: 284 passed.
- **Residual 2 (the cull20 `wiring.py` post-run line): fixed.** `run_arm.sh` line 65 is `if [ "$ARM" = cull20 ]; then python "$HERE/../RBT-101/wiring.py" …`, and the resumed-arm note names both post-run lines (PRs #114, #115).
- **Step 0:** `python runs/RBT-92/onset.py` reproduces the committed `onset.txt` byte for byte. T = 361, 358, 359, 365, 360, 382, 382, 352, 355, 354 for seeds 801, 804, 805, 806, 807, 1, 2, 3, 4, 7.

**Caveats carried into the report:**
- V3 is a manipulation check (F2).
- k ≈ 0 means the null is close to the control: name the k = 0 seeds (F6).
- The P-form recovery is read against its floor (F10).
- Carriage is lineage only (L).
- F6's mechanism rests on one probe seed.
- **New, minor:** seed 806's wave window is [330, 340), at the upper edge of the rule's search range [280, 330]. Its peak may lie past 340, where the rule does not look, so its T = 365 may sit closer to the wave than half a period. The printed drift FLAG is the guard: read 806's FLAG line before its transient is interpreted. This is a caveat, not a re-pick.
