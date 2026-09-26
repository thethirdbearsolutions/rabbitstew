# RBT-106 design adversary: re-check of the 22:40 amendment (PR #213 head 4919a4e)

*Re-check, 2026-09-26 ~23:00 UTC. It checks PREREGISTRATION.md §10 and the changed tools against F2, F3,
F5 and F6 of `ADVERSARY.md`. The checks ran in a worktree at 4919a4e. Platform: x86_64, MuJoCo 3.14.0,
numpy 2.4.6. No arm was launched. The one new run was a pair of 21-season HU/HP smoke runs in
scratch.*

**Verdict: all four MUST-FIXes are resolved. The design is CLEAR from the adversary's side.** There are
two small notes and no new MUST-FIX.

| finding | amendment | re-check | status |
|---|---|---|---|
| F2 | `run_arm.sh` writes `commit.txt` and refuses on a dirty `rabbitstew/` (exit 5), or on a tree ≠ c872e80's without a SAME RUN `cross-ticket-<commit>.txt` (exit 6). `postrun.sh S1/S8` certifies RBT-104's arm with `cross_ticket.py` before writing its `commit.txt`. `readout.py` drops pairs on code | Read the diff. All three gate paths are exercised in `controls/f2-gate.txt`. `rabbitstew/` at 4919a4e is still c872e80's. The readout's `commit()` parses both launchers' `commit.txt`. The certification greps the output line `cross_ticket.py` actually prints | **RESOLVED** |
| F3 | `held.py`: HELD iff k_planted > B, with k_bare, mean depth and distinct planted roots printed. `null_rates.py` re-scores my full-operator draws under both rules | `null_rates.py` at 4919a4e reproduces the committed `null_rates.txt` byte for byte. Amended rates: 2.0% (`same`), 0.5% (`pay64`), 1.0% (`pay32`); depth proxy 1.5 / 0.0 / 0.0%. H's gate is 8.5% per seed (0.16 for two seeds). The readout's `held()` regex matches held.py's new line, including `depth = nan`. The cost (transfer by crossover into bare-rooted lineages is not credited) is stated, and is symmetric between worlds | **RESOLVED** |
| F5 | F-0 and F-1 withdrawn and restated from `power_adv.txt` A. The factorial P8 is DEFERRED by the ruling. Order H0, P1, H1 | Read §6.4 and §10.3. The restated figures match `power_adv.txt` | **RESOLVED** |
| F6 | Option (a): a line counts toward EVOLVED / NULL / "function follows" only if its primary call is FD **and** its attribution is `compass: FOOD-DEPENDENT`. The primary-only count and the lesion gain are printed | `readout.function()` at 4919a4e, run on real function.py outputs: the patchy positive control (`controls/function-patchy-801.txt`) gives FD, attribution FOOD-DEPENDENT, **counted**, lesion gain +2.609. All ten bare lines in `bare_patchy/` give not FD, "no compass gain", **not counted**. `tests/test_rbt106.py`: 13 passed | **RESOLVED** |

**Note 1 (NONE, for the record): H's install control in the amended smoke reads False on HU and HP.**
`controls/pipeline-smoke-H-801-amended.txt` shows "pc (a)/(b) True/False" for both H arms, which would
make every H arm "unusable". I re-ran it (`recheck/pc-HU-801-smoke.txt`: a 21-season HU-801 in scratch,
`function.py --install 32` on bests 0, 10, 20).
- **Every body pays under the install:** F per body is +0.94, +2.97 and +2.36.
- **The line fails only through t(2) on three bodies:** +2.089 [−0.501, +4.678].
- The real readout uses seven window bodies, so this is a smoke-test artefact, not a VOID risk for H.
- The planted w = 32 compass does not block a second, travel-signed install.

**Note 2 (CAVEAT, carried): F6(a)'s power on evolved lines is unmeasured.** §10.4 says so, and treats
§6.3's EVOLVED powers as upper bounds. That is the right wording.

No other change was found outside `runs/RBT-106/` and the tests.
