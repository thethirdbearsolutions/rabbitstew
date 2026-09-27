# RBT-112 design adversary: re-check of F7, F11 and F14 on #277 `23232ef`

*2026-09-27, about 03:50 UTC. Only the three MUST-FIXes were re-checked, as the coordinator asked. No arm was
launched, and no RBT-106 or RBT-107 arm output was read. The probes feed `gate.py` and `readout.py` synthetic
text, built from RBT-106 `readout.py`'s own print formats (l. 157, 160, 199 and 234).*

**Verdict: all three MUST-FIXes are RESOLVED.**
- The suite passes at `23232ef`: **360 passed**, in a clean `.[dev]` venv with no scipy.
- `power.py` reproduces the committed `power.txt` byte for byte.
- I found one new CAVEAT (R1), which is a one-line fix, and one NONE (R2).

| # | what was asked | what is there | check | status |
|---|---|---|---|---|
| F7 | SUPPORTED = #HELD(HZ) − #HELD(HU) ≥ 3 | `readout.py`: `SUPPORT_GAP = 3`; the "≥ 5" floor is removed; SUPPORTED is tested before FALSIFIED (the two are disjoint) | `recheck_probe.txt`: nU 0 / nZ 3 → SUPPORTED; 2/5 → SUPPORTED; 2/4 → NOT DECIDED. `power.txt` P(SUPPORTED \| gate) at s = 0.15/0.2/0.25/0.3 is 0.337/0.534/0.617/0.626, the same as my `power_alt.txt` gap column. The null is 3.7e-4 (7.7e-3 at the upper bound) | **RESOLVED** |
| F11 | a gate pinned to RBT-106's H readout, every label covered | `gate.py`: WAIT (NOT READ, or no VERDICT line); LAUNCH iff not VOID and nU ≤ 2, whatever the label; CLOSE iff nU ≥ 3; VOID → HU arms alone (≥ 7 counted, ≤ 2 HELD; the install control is not required); an ambiguous file → re-run RBT-106's `readout.py`, then HU alone. §7.1's old text is withdrawn | the regexes match RBT-106's printed header, `HELD:` line and `VERDICT H:` line (`readout.py` identical on integration). All labels × nU probed: SUPPORTED nU 0 and 2 → LAUNCH; FALSIFIED-b nU 0 → LAUNCH, 3 and 4 → CLOSE; NOT DECIDED 2 → LAUNCH, 3 → CLOSE; FALSIFIED-a → CLOSE; VOID → the HU-alone branch; NOT READ → WAIT; a duplicated `HELD` line → AMBIGUOUS | **RESOLVED** |
| F14 | FALSIFIED split by whether the planted roots survived | FALSIFIED = #HZ ≤ 1 and #LOST ≤ 2; FALSIFIED-ROOTS = #HZ ≤ 1 and #LOST ≥ 3; LOST = held.py's n = 0 at 300 or at 599; n and the class printed per seed | probes: lost 2 → FALSIFIED, lost 3 → FALSIFIED-ROOTS; `lost()` is True for n = 0 at either season | **RESOLVED** |

**R1 (CAVEAT, new; one line).** A usable HZ seed with a **missing** `held-300.txt` or `held-599.txt` reads
HELD = False and LOST = False. It is therefore counted as NOT HELD, and pushes toward FALSIFIED.
- The docstring says the opposite: "a missing file … leaves the rule it feeds; it is never read as a null".
- This behaviour predates the amendment, but F14 now makes FALSIFIED's count matter.
- **Fix:** add `r["held300"] and r["held599"]` to `usable`, or drop such seeds from the counts.

**R2 (NONE).** `power.py`'s module docstring (l. 24–26) still describes the old "≥ 5" rule. The code and
`power.txt` use the gap rule. The docstring is stale text only.

## Files

| file | role |
|---|---|
| `recheck_probe.py` → `recheck_probe.txt` | `gate.py`'s `parse` and `decide`, and `readout.py`'s `verdict` and `lost`, probed with synthetic inputs |
