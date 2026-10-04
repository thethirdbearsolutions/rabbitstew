# Coordinator ruling RBT129-RB-HELP-1: an R-B arm-seed that overflowed in its S60 phase and then failed non-natively

*Coordinator: `session_017eUHGNdTSsoVFAtLaJWehF`. Ruled 2026-10-04 ~00:50 UTC, with the **owner's explicit approval** ("ok", in response to the coordinator's recommendation). **COORDINATOR-EXPOSED** (see `DISCLOSURE-2026-10-02.md`). It was ruled before any outcome of this arm-seed, or of any R-B arm-seed, was read. It changes nothing in `continuations/OVERFLOW-RULE.md` (`RBT129-OVERFLOW-RULE-1`). It decides one case the rule does not name.*

## The event (as relayed by runner `RB/host8`, `session_019NBW3xvp34KpgwN8oxNjvP`, about 00:35Z)

1. `EPA OVERFLOW: RB/c2-p010-HP-G/129014/S60: 1 logged`. That is an overflow in the S60 phase of seed 129014 at point `c2-p010-HP-G`.
2. The following S job, `rbt-129-rb-c2-p010-HP-G-129014-S`, then failed **twice in a row** with `ecology exited 1`: a non-native exit, with no broken pool. The runner stopped `host8-lane1` after one restart, as instructed.
3. **No diagnosis was taken.** A coordinator request for a filtered traceback (exception class and frames only) was **blocked** by the session's permission classifier as weakening no-peek. It was not worked around. No run log, EPA log or run-directory content of this unit has been read by anyone.

## Why the rule does not settle it

- §4.1 counts as a crash only native exits (`crash_state`). A repeated exit 1 is not a crash under the rule.
- §4.6 lists the HELP states, and a non-native repeated failure is not among them. Its default would read an incomplete HELP arm-seed as CRASHED (unattested), and §4.3 would then stop the R-B hive.
- That default exists because an unattested crash may hide an **unlogged** overflow. Here the overflow is logged, at this arm-seed, before the failure. Under FC-2, post-overflow behaviour is undefined and is not evidence about anything.

## Ruling

- **H1. State.** `RB/c2-p010-HP-G/129014/S` is **OVERFLOWED** (§3.1, from the logged line alone) **and INCOMPLETE**. Its seasons after 60 do not exist. R-B has no M or N arm at this point, so nothing else propagates.
  - **In the readout**, its income-layer value is **missing**, so the point's n is one lower (15 of 16).
  - It enters the primary analysis only as such: it is in no M1 or M4 category, mean, table or figure.
  - It is listed among the OVERFLOWED arm-seeds with the note "incomplete: non-native failure after a logged overflow (RBT129-RB-HELP-1)".
  - Where §3.3's logical bound exists, it is printed as for a CRASHED seed.
- **H2. The ceiling (conservative).** The event **counts as one crash event** toward §4.4's ceiling, exactly as an attested crash would. A second such or attested event at `c2-p010-HP-G`, or a third across GO-1 and Stage 2, stops launches.
- **H3. No re-run.** The arm-seed is never resumed, re-run, restored or substituted, on any build (`RULING.md` item 2). Its branches and records are kept and never read, except by the readout's integrity counts.
- **H4. Tripwire.** Every R-B runner is now told: **any** further non-native job failure stops that lane at once, with no restart, and wakes the coordinator. **A second non-native failure at any other unit pauses R-B** for a proper diagnosis, because it would point to a tooling defect rather than to post-overflow fallout.
- **H5. The rest of `host8-lane1`.** Its remaining jobs run without this unit, by a mechanism the tooling author proposes and the coordinator reviews. That mechanism must not change anything the other live lanes pin.
- **H6. Disclosure.** This ruling, the blocked diagnostic and the owner's approval go into the next progress report and the R-B readout's integrity section.

## Also recorded (NOTE): an accidental scratch start by the drivers adversary

During the review of #533, the adversary (`session_01HSrytBaaQZ5ebri12t1bot`) started `S2A/c1-p018-PW-L/129001/S60` by mistake, in a scratch clone against a **local fake origin** with `NO_DURABLE=1`.
- It killed the run after about 2 minutes.
- Nothing was read: only the runner's start line and a directory name were seen.
- Nothing was saved or pushed. The run directory, the lock file and the whole scratch clone are deleted (#534, `e351a08`).
- It has no effect on any registered unit. Stage 2a has not been launched, and GO-ID-2A is PENDING.

## Clarification C1 (2026-10-04 ~03:05 UTC, COORDINATOR-EXPOSED): H3 governs the §3.3 bound

Raised by the #535 fix-check 3 (finding 3), on synthetic fixtures. No outcome of this unit, or of any R-B unit, has been read.

- H1's "where §3.3's logical bound exists, it is printed as for a CRASHED seed" is **subordinate to H3 and FC-2**.
- This unit's only checkpoint, `ckpt60`, was written by the S60 phase that logged the overflow. It is post-overflow state, which is not evidence under FC-2. H3 bars restoring or reading it beyond the integrity counts.
- **Therefore:**
  - The readout does **not** restore `ckpt60`, or any dependent, of an `INCOMPLETE:` unit.
  - Its §3.3 bound is the uninformative one: every completion is enumerated, as with `v=None`.
  - The integrity counts are unchanged.
- **Effect:** at most the body word at `c2-p010-HP-G`. Under H1 the unit's income-layer value stays missing (n 15 of 16).

---
_Generated by [Claude Code](https://claude.ai/code)_
