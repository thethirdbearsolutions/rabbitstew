# RBT-129 Stage 2a: host0-lane0 INCOMPLETE (a reported deviation)

*Ruled by the owner's proxy on 2026-10-05 (~19:41 UTC) and relayed by the coordinator (`session_017eUHGNdTSsoVFAtLaJWehF`).
**COORDINATOR-EXPOSED** (see `DISCLOSURE-2026-10-02.md`). Recorded by the Stage-2 plan author. This is a record only.
It changes no code, no lane file, no launch pin and no quarantine or ruling list.*

## The event

`S2A/host0-lane0` refuses deterministically, with exit 4, at its job 2:

    REFUSED: S2A/c1-p018-PW-L/129001/S60CMP: runs/RBT-129/stage2a/c1-p018-PW-L/129001/S is at season 38, not 60: the comparison runs before S resumes

## The diagnosis: a tooling gap in `s60_compare`, not a crash

- **The order is right.** The unit's jobs are, in the emitted order:
  1. `S60` (a fresh S to season 60);
  2. `S60CMP`;
  3. `ckpt60`;
  4. `S` (a resume from 60 to 300);
  5. `M`;
  6. `N`.

  No job resumes S from 38 to 60.
- **Job 1 finished with S at season 38.** A fresh S60 earns its done-marker only when the ecology exits 0. A run that is killed resumes to season 60, and a crash stops the lane. In the code, the one path to a finished S60 below season 60 is the ecology's exit-0 stop when every population is empty: pre-merge extinction, a registered outcome (DESIGN M2).
- **That outcome is probable and undetermined.** It is an inference from the refusal's text and the code. Nothing was read to confirm it.
- **`s2lanes.s60_compare` has no branch for that case.** It requires season 60 and refuses with exit 4. The `ckpt60` job does have a branch for that case: it writes `EXTINCT.txt` and skips the unit's later jobs. But it runs after `S60CMP`.
- Every later job of the unit needs a saved S60CMP IDENTICAL (`require_identical`), so the lane cannot pass the unit.

**What the diagnosis read.** It read only code (`s2lanes.py`, `launch/stages.py`, `stage2/s2readout.py`, `STAGE2-PLAN.md`) and the lane file `runs/RBT-129/lanes/S2A/host0-lane0.jsonl`. It read no run directory, run log, EPA log, durable log, receipt or ckpt content. It made no narrow fetch of anything but the base ref.

## The 19 unrun jobs

host0-lane0 holds 21 jobs. The lane stops at job 2, so jobs 3–21 do not run:

| unit | jobs not run |
|---|---|
| `c1-p018-PW-L/129001` (the stuck unit's remaining 4) | 3 `ckpt60`, 4 `S`, 5 `M`, 6 `N` |
| `c05-p030-U-G/129001` (never started) | 7 `S60`, 8 `S60CMP`, 9 `ckpt60`, 10 `S` |
| `c15-p030-U-G/129001` (never started) | 11 `S60`, 12 `S60CMP`, 13 `ckpt60`, 14 `S` |
| `c1-p018-U-L/129001` (never started) | 15 `S60`, 16 `S60CMP`, 17 `ckpt60`, 18 `S` |
| `c1-p018-U-G/129005` (never started) | 19 `S60`, 20 `ckpt60`, 21 `S` |

## The ruling

- Stage 2a closes with host0-lane0 **INCOMPLETE**, as a reported deviation.
- There is **no post-data re-pin** of the driver (`s2lanes.py` and `lanes/S2A/launch.txt` stay as launched).
- There is **no quarantine or exclusion** of `c1-p018-PW-L/129001`, and no `QUARANTINE:`, `CRASHED:` or `INCOMPLETE:` line is added for it.
- **P-1 comes before 2b.** P-1 is the `s60_compare` fix: accept an S below its seasons only when every population in its `state.json` is empty (the `ckpt60` job's own test), and compare it as it stands. It goes through the normal pre-data adversary path, under the 2b pin.
- **A separate pre-data amendment is proposed, not decided.** It would complete these 19 jobs under the new blob, with the readout showing the driver blob per run. It follows the normal adversary path, and the owner decides it with the 2b GO ask. If it is judged unsound, it is dropped and the ask says so.
