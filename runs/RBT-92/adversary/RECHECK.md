# RBT-92 adversary re-check (the one re-check), on integration `d2aa6e0`

Read against amendment 3 (PR #104 `8151d9b`), PR #76 (`d2aa6e0`, which also carries the protocol §9 E1/E2 split), the senior reviewer's 14:20 read, the coordinator's 14:20 and 14:35 rulings, and RBT-101's 14:15 request. `pytest`: 280 passed.

**Verdict: BLOCK, on two one-line items.** Everything round 1 classed launch-blocking is resolved. Both residuals are mechanical; once they are fixed and `smoke.txt` is re-committed, the verdict becomes **CLEAR-WITH-CAVEATS** with no further round from me.

## Residuals that block

1. **`readout.py` crashes at the VERDICT on every real arm.**
   - The new REMAINDER GROUPS loop, `for r in tsv(gp)` at `readout.py:492`, rebinds `r`, which holds the resolvable effect size computed at line 402. Every later use gets a CSV row dict instead: the verdict line (567), `classify(n, m, r, …)` (570), the equivalence form (572) and the turnover guard.
   - It fires whenever the shift arm has `groups.txt`, which is every arm now that `run_arm.sh` writes it (F5).
   - `smoke.sh` does not catch it. The copy committed on the head shows exit 0 and 155 lines, but it is stale: re-run on this head it exits 1 with `TypeError: unsupported format string passed to dict.__format__` (`recheck_smoke_head.txt`).
   - `recheck_readout_n6.sh` runs the readout to the classifier at n = 6, on throwaway data read for nothing. It gives exit 1 on the head and exit 0 with a class printed after the one-word rename in `recheck_readout_r_shadow.patch` (`r` → `row`, lines 492–493) (`recheck_readout_n6.txt`).
   - **Fix:** apply the rename, re-commit `smoke.txt`, and add a test that runs `main()` at n ≥ 6 with a `groups.txt` present, so the classifier is reached. RBT-99, RBT-100 and RBT-101 share this file.
   - Strictly, this blocks the readout, not the arms. But the pre-registered instrument has to run end to end before launch, and the fix is free now.
2. **RBT-101's cull20 `wiring.txt` line is not in `run_arm.sh`'s post-run step.**
   - RBT-101's designer asked (14:15) for `python runs/RBT-101/wiring.py runs/RBT-92/cull20-SEED` beside `tables.py` for cull20 only, written from the genomes while the bulk exists. The coordinator asked me to check it.
   - It is absent: `grep wiring runs/RBT-92/` finds nothing outside `adversary/`, and the post-run step runs `tables.py` alone.
   - Without it, C4's re-wiring null cannot be recomputed once a cull20 container is gone. The ckpt snapshots do keep the genomes, but restoring them costs a session per seed.
   - **Fix:** `[ "$ARM" = cull20 ] && python "$HERE/../RBT-101/wiring.py" "$OUT" >> "$OUT/run.log" 2>&1` after the `tables.py` line, plus the matching line in §13's resumed-arm note.

## Round 1, finding by finding

| finding | status |
|---|---|
| F1 onset read post-onset deaths | **Resolved** (amendment 2's [280, 340) rule; range corrected to [340, 399]; the drift FLAG is printed). |
| F3 B and S had no range | **Resolved: dropped.** L is the carriage instrument, for both faunas; the B prediction is withdrawn. |
| F4a extinct fauna skipped | **Resolved** (income 0 from extinction; test). |
| F4b E mislabelled a co-evolved collapse | **Resolved** in the protocol (`docs/held-out-challenges.md` §9 E1/E2, `f871128`) and in `classify()` (E1 > D > E2 > A > C > B > F; test). E2 prints with the falsifier. D and E2 cannot both reach ⌈0.8n⌉ on one set of seeds, so the order between them is moot. |
| F5 remainder group | **Resolved:** `tables.py` writes `groups.txt` and `run_arm.sh` runs `tables.py` post-run, and the readout prints the share. That section is where residual 1 lives. |
| F2 V3 | **Resolved as a caveat:** renamed a manipulation check; the prediction is withdrawn. |
| F6 near-empty null | **Resolved as a caveat:** k per seed; 0/0 named; the guard and the R-null prediction are scored on co-evolved k > 0 only, with the count printed; cull20 income is the turnover reference. |
| F8 equivalence | **Resolved:** \|mean\| + r printed beside the class (it will read correctly once residual 1 is fixed). |
| F10 recovery | **Resolved:** the paired form, against the control, is primary; the P-form is secondary with the base's floor; the three predictions are restated and "base 0 on 10/10" withdrawn. |
| §8 sentence | **Corrected** in `onset.py`. |
| duplicated §14 line | **Removed.** |

## Caveats to carry into the report

- F2: V3 is a manipulation check.
- F6: k ≈ 0 means the null is close to the control. Say which seeds had k = 0.
- F10: the P-form recovery is read against its floor.
- Carriage is lineage carriage (L) only; "survives" or "is sorted", never "acquired".
- One seed (9902, T = 150) is the only evidence for F6's mechanism.
