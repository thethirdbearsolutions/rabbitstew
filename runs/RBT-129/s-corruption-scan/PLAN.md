# RBT-129 Stage-1 S silent-corruption scan: the plan

*Owner decision: `../coordinator/OWNER-DECISIONS-2026-10-09.md` item 1 (RUN). Modelled on the M/N scan:
`OWNER-DECISIONS-2026-10-03` item 1, COORD-RULING-520 D2, COORD-RULING-527 T5, `stages.py`
`scan-emit` / `scancmp` / `scan-report`, `../mn-corruption-scan/`. Written before any of its data exist.*

## 1. What it scans, and why

- **A7 and OVERFLOW-RULE §6.1 leave two things UNSCANNED:**
  - every Stage-1 S arm;
  - the S60 phase upstream of every Stage-1 M and N (S's seasons 0–59).

  The M/N scan replayed each fork from its stock ckpt60, so it covers seasons 60–299 of M and N only.
- **A non-crashing EPA horizon overflow can corrupt a run silently** (MuJoCo 3.14.0, google-deepmind/mujoco#3646). The
  instrumented build (c) logs every overflow and is byte-identical to stock on any trajectory without one. A replay on
  the build that matches the stored run byte for byte, with no overflow logged, therefore rules out silent corruption
  in the seasons it covers.

## 2. The replay set (pinned by the committed Stage-1 emission)

- **Every unit with an `S` resume job in `lanes/1/*.jsonl`** (`sscan.stage1_s_chains`): **288 S chains**, from 36
  points × seeds 129001–129008. `lanes/1/launch.txt` gives the screened salts.
  - 252 chains were fresh in Stage 1. Their replays use exactly Stage 1's `extra` (checked: 0 mismatches).
  - 36 chains (seed 129001) adopted the census's S 0–59 (F7, salts (0, 0)). Their replay runs those seasons fresh at
    (0, 0), as Stage 2a's O-2 re-simulation does. That also scans the census S60 the adoption carried in.
- **Excluded: none.** The one CRASHED Stage-1 unit is an M arm (`1/c2-p030-U-G/129001/M`, quarantined). Its S is
  replayed, and no scan job reads or fetches its M (`check_lane_sscan`: no job touches a quarantined label).

## 3. The jobs per chain (`sscan.sscan_units`)

| job | kind | what |
|---|---|---|
| `SSCAN/<p>/<s>/S60` | `fresh` | seasons 0–59 on the build, at the seed's salts, into `s-corruption-scan/replay/<p>/<s>/S` |
| `SSCAN/<p>/<s>/ckpt60` | `snapshot` | the season-60 state, as Stage 1 took it. A pre-merge extinction writes `EXTINCT.txt` and the resume is skipped, as in Stage 1 |
| `SSCAN/<p>/<s>/S` | `resume` | S to 300 on the build |
| `SSCAN/<p>/<s>/ckpt60-cmp` | `sscancmp` | the replay's ckpt60 against `ckpt/rbt-129-stage1-<p>-<s>-ckpt60`: **the S60 phase** |
| `SSCAN/<p>/<s>/S-cmp` | `sscancmp` | the replay's S against `ckpt/rbt-129-stage1-<p>-<s>-S`: **seasons 0–299** |

- **The comparison.** Every file is compared byte for byte except logs and provenance: `platform.json`,
  `command.txt`, `run.log`, `durable.log`, `run.lock`, EPA logs, done-markers and `SSCAN.txt`. `config.json` is
  compared **bar `workers`** (`stages._arm_config`), because a fresh run's worker count is the host's. `adopt_census`
  and Stage 2a's `s60cmp` compare it the same way.
- **The jobs are continuations** (the build check, `epa_ecology.py`, the EPA log, `check_not_crashed`), through
  `stages.run_job` unchanged. The only override is `"SSCAN/"` added to `stages.CONTINUATION_PREFIXES` in the scan's own
  process.

## 4. States and verdicts (the M/N scan's, OVERFLOW-RULE §6.1)

- **Verdicts:** IDENTICAL; DIFFER (the differing file *names* only, in `SSCAN.txt` on the replay's branch);
  NO-REFERENCE (the stored run has no done-marker: named, not compared).
- **States**, read from the replay's own EPA log, for the seasons each comparison covers:
  - `ckpt60-cmp`: **CLEAN (seasons 0–59)** / OVERFLOWED / UNLOGGED;
  - `S-cmp`: **CLEAN (seasons 0–299)** / OVERFLOWED / UNLOGGED.

  An overflow logged before an attempt's first season line counts against the phase, conservatively. A pre-merge
  extinction is checked only for the seasons it ran.
- **What a mismatch means** (as for M/N). It is silent corruption, or nondeterminism. An overflow in the replay's log
  marks corruption. A DIFFER with no overflow is nondeterminism, itself an integrity finding.
- Either a DIFFER or an OVERFLOWED unit is a Stage-1 integrity finding. The coordinator rules on it against the accepted
  Stage-1 record (COORD-RULING-517 C1), which this scan does not touch.

## 5. The report and the record

- `sscan.py scan-report` writes `s-corruption-scan/scan_report.txt`. It holds **counts only**: totals of each verdict
  and state, for the S60 phase and for S. A unit is named only when it is DIFFER, NO-REFERENCE, OVERFLOWED or UNLOGGED.
  No EPA figure, season, geom pair, near miss or file name is copied.
- The result is recorded in **READOUT-STAGE1-CORRECTIONS A7** with the same states (a pointer is already there).

## 6. The final readout (`../stage2/s2readout.py`)

- **What `scan_states` does now.** It also reads `lanes/SSCAN` (`s_scan_states`):
  - Each Stage-1 S arm takes its scan state.
  - Each chain's S60-phase state propagates to that seed's Stage-1 M and N, as `stage2_readout.propagate_s60` does for
    continuations. A flagged S60 phase flags them, whatever their own 60–299 scan found.
  - A DIFFER is SCAN-DIFFER, a NO-REFERENCE or an unfinished comparison is UNSCANNED, and each is counted or named.
    None is a HELP.
- **How `stage1_arms` uses those states** under `exclude-known-flagged`:
  - A flagged Stage-1 S seed leaves n and takes its M and N with it, as `arms_for` does for a continuation.
  - A flagged M or N is listed out, as before.
  - Under `include-flagged`, everything is read as observed (the accepted Stage-1 record stands).
- **Does the final have to wait for the S scan?** Not mechanically. An unfinished scan reads UNSCANNED, and the
  integrity lines count it, so the final can run while the scan is incomplete. But the S scan's states feed the
  sensitivity map (`exclude-known-flagged`) for every Stage-1 point. **The author recommends that `GO-ID-FINAL` wait
  for `scan_report.txt`.** That is the coordinator's and the owner's call.
- **What does not change.** `stage2_readout.py` and `stage1_readout.py` (both pinned by blob in `lanes/S2A` and
  `lanes/S2B`). The interim prints no Stage-1 scan line, so it is unchanged too.

## 7. Cost, lanes and gates

- **Cost: ~560–1,150 core-h, likely near the top.** The rates were not measured on build (c), and the figure excludes
  restart rework.
  - The arithmetic: 288 chains × 300 seasons = **86,400 arm-seasons**. At the planning rates of 23.35 / 43.72 core-s
    per arm-season (`stages.MN_CORE_S`) that gives 560 / 1049 core-h.
  - The wall time below implies more: 20 lanes × ~29 h × 2 cores ≈ 1,150 core-h.
  - A pre-merge extinction skips its resume, which lowers all of these.
  - The owner's figure was ~600–800 and may be exceeded (#562 adversary MINOR 2).
- **The lanes.** `sscan.py emit --hosts 10` writes `lanes/SSCAN/`: 20 lanes of 14–15 chains each.
  - Wall time follows the M/N scan's loads (240 seasons ≈ 1.5 h): about 2 h per chain, so roughly 28–30 h per lane at
    `--hosts 10`.
  - Raising `--hosts` at re-emission shortens it proportionally.
- **The gates of `run-lane`**, in order:
  - the host, the build and the pinned trees (`stages.check_host`);
  - the modules (`check_modules`);
  - `sscan.py` by blob, committed (`check_code`);
  - **the scan's GO** on the merged base after a narrow fetch that must succeed (`check_go`, `LOCKS.md`: exit 10 until
    `GO-ID-SSCAN: RBT129-SSCAN-GO-1` is open);
  - the lane file equal to its slice of the emission (`check_emission`);
  - blocks and salts (`stages`);
  - every job an S-scan job writing under the replay tree that touches no quarantined label (`check_lane_sscan`).
- **The overflow rule does not gate the scan.** It produces no continuation data (as M/N).
- **NOTE 17.** `sscan.py` lives outside the pinned trees and imports nothing from Stage 2. The P-1 fix to
  `s2lanes.py`, a 2b launch or a readout change therefore cannot refuse a scan lane, and the scan cannot refuse theirs.
  The lanes pin the launch tree, as every lane does. So **no change to `runs/RBT-129/launch/`, `scripts/` or
  `rabbitstew/` may merge while SSCAN lanes are live**.
- **Shared resources with 2b.** Seed locks (`/tmp/rbt129-locks/seed-<seed>.lock`) are per host. The scan uses seeds
  129001–129008 and 2b(2a) uses 129009–129016, so they never contend even on one host.
- **A scan crash** refuses its lane (exit 4, `check_not_crashed`). It is a Stage-1 integrity finding for the
  coordinator, not counted toward the §4.4 ceiling (rule §6.1).
- **There is no `drop` command.** A crashed chain stops its lane until the coordinator rules, as in the M/N scan.

---
_Generated by [Claude Code](https://claude.ai/code)_
