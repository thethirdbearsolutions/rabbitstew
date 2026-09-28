# RBT-131: the fix, and the audit of results that may have read dead members from `final/`

**The audit's verdict: no committed result moves.** I found no number under `runs/` or `docs/` that was computed from
the `final/` of a **resumed or forked** ecology run whose population then shrank. For every candidate, at least one of
the three conditions fails, and in almost every case the first one does: the result never reads `final/`. So there
was nothing to re-read from `state.json`, and no erratum is needed.

## 1. The fix (`rabbitstew/ecology.py`, `Ecology._save_populations`)

**What changed.** Before writing `<kind>/final/`, the method now removes the member files it writes there (`NNN.json`,
all digits). Anything else in `final/` is left alone.

**Why fresh runs are unaffected.** A fresh run has no `final/` when it ends, so the removal finds nothing and the bytes
are unchanged:
- `tests/test_rbt131.py::test_a_fresh_run_writes_final_byte_for_byte_as_before` checks the sha256 of every `final/`
  file of a run with a mid-run cull. The digests were recorded on the pre-fix code, 01f113d.
- `fresh_identity.py` runs four test-sized fresh ecologies on the pre-fix checkout and on this branch: plain, cull,
  breeding with deaths, and merge-null, where a fauna goes to zero at the merge. It compares every file except
  `platform.json`, which records the checkout's sha. The outputs are `fresh_identity_prefix_01f113d.txt` and
  `fresh_identity_fixed.txt`, 133 files each, identical, 31 of them under `final/`.
- The golden-digest tests (RBT-113, RBT-120, RBT-125, RBT-126, RBT-130) pass in the full suite; see §5.

**The two tests that fail before the fix and pass after it.** The pre-fix run is `test_rbt131_prefix.txt`, the fixed
run `test_rbt131_fixed.txt`.
- *Resume.* A run with a cull at season 2 is stopped at season 2, before the cull, so `final/` holds 6 + 6 members. It
  is then resumed to season 4, through the cull. `final/` must hold exactly `state.json`'s population, in order, and
  be byte-identical to the `final/` of a straight run to season 4. Before the fix, 3 stale files remain (6 files for 3
  living).
- *Fork.* A finished run is copied, as `runs/RBT-107/fork.py` does, a cull is written into its config, and it is
  resumed. The same check applies, plus: a non-member file put in `final/` survives the fix.

**Not changed:** `Evolution._save_populations` (arena runs, `rabbitstew/evolution.py`). It never clears `final/`
either, but an arena population is `population_size` every generation. Each write therefore overwrites the same
`000..N-1`, and `Experiment.resume` cannot change the size. It would become the same bug only if a resume or fork
lowered `population_size`, and no committed run does that (RBT-37's extension keeps 20; see §3). Kept out to keep
the fix minimal. It is a one-line port if the coordinator wants it.

## 2. How the audit was done

1. **Every checkpoint snapshot on the remote** (`sweep_checkpoints.py` → `sweep_checkpoints.txt`). For each of the
   277 `ckpt/*` branches (scripts/durable.sh snapshots of run directories), the script fetches it into a throwaway
   repository and counts `<kind>/final/NNN.json` in the tarball. It compares that count with the length of
   `state.json`'s population per kind. A snapshot whose `final/` holds more files than its living population carries
   dead members. **Result.**
- **277 checkpoints, 385 run directories, 0 unreadable. None has a `final/` that differs from its living population.**
  An arena snapshot, such as RBT-113 O / Z or RBT-120 B, nests several run directories. Its `state.json` keeps no
  member list, so those runs are compared against `population_size`.
- 362 run directories have a `final/`. Of the 23 without one:
  - 11 are unfinished snapshots, where `final/` is not written yet: RBT-92 shift / cull20 and RBT-99 / RBT-101 arms
    at seasons 473 to 599 of 600.
  - 12 are the arena parent directories, whose nested runs are counted separately.
- No snapshot's `platform.json` records a resume.
- So no checkpointed run carries dead members in `final/`, and no committed result could have read them from a
  restored checkpoint.
2. **Every committed reader of `final/`** (`final_readers.txt`): a `git grep` of `runs/`, `scripts/` and `docs/` code
   for `final/` paths and for `final/` readers. The readers searched for are `population_files`, `load_population`,
   `_parent_pool`, `--from-run`, `seed_from`, and `rabbitstew levers`, `motors`, `synergy` and `analyze`. There are
   86 lines, all in the tickets listed in §3.
3. **Every ticket's committed results**, traced from the number back to its script and inputs. This covers RBT-5 to
   RBT-130, `HIVE-0926`, `baseline-801`, `compass-*`, `sim-audit`, `docs/`, `scripts/` and `ERRATA.md`. For each I
   asked three questions: does it read `final/`? Was that run resumed or forked after a *finished* segment? Did the
   population shrink? A resume of a run killed mid-way cannot leave stale files, because `final/` is written only
   when a run ends.

Some structural facts narrow the risk:
- The stale files are always the *highest-numbered* ones: the living are rewritten as `000..n-1`.
- So `load_population` (founders from `--from-run` / `seed_from` / `--seed-*`) picks up the dead only when the slot
  count exceeds the living count.
- `mutation_heritability` reads `state.json` first, so it is unaffected unless the fauna is extinct.

## 3. The candidates

| Ticket | Result | Reads `final/`? | Resumed / forked after a finished segment? | Shrank? | Verdict |
|---|---|---|---|---|---|
| RBT-130 | `clutter_census.txt`; `adversary/probe_fork.txt`, `probe_census.txt`; `tests/test_rbt130*` | No. The census is geometry only. The fork probe and tests compare `lineage.jsonl`, `cohorts.jsonl` and `history.json` (`probe_fork.py:26`) | Yes. `probe_fork` forks by copytree and resumes | A merge-null can shrink a fauna | **Not affected**: `final/` is not read |
| RBT-126 | depth / invasion / retention / screen / drift_gate / verify_*, REGIME.md, BREEDING-RULES.md | No. It uses the replica plus `lineage.jsonl` restored by `fetch_ck.sh:13`, which extracts only lineage, seasons, config and event | The corpus includes rbt-107 arms | n/a | **Not affected**: lineage only |
| RBT-129 | `power*.txt`, `prior_regime.txt`; design-adversary `probe_launch_cli.txt` | `prior_regime` takes its inputs from RBT-118 `prior/levers.py`, which reads `genomes/`. `probe_launch_cli` hashes every file of a run resumed after finishing, `final/` included | Yes (the probe) | Possibly | **Not affected**. The probe compares two code trees that both carry the bug, so its identity claim holds. The launcher itself clears `final/` (`stages._clear_final`), which is why the sweep is safe |
| RBT-80 | `docs/artifacts/RBT-80-*` (within-arm +1.144 / +0.415 / +0.499; crossover floor 0.989), cited in paper-5 and paper-8 | No. `scripts/rbt80_*.py` and `crossover_floor.py` load `conventional/genomes/<name>.json` for the names alive in `lineage.jsonl`. Founders come from `best_gen*` through `founders/` | No resume on record | No: alive is 60 in every sampled season | **Not affected** |
| RBT-118 step 1 | `prior/ANALYSIS.md`, `levers.tsv/.txt`, levers-flat, relate, terrain, pool, phases, survey | No. `prior/levers.py:143-153` takes the living from `lineage.jsonl` and loads `<kind>/genomes/<name>.json`; the rest read seasons, config or lineage | It reads RBT-107 and RBT-105 checkpoints | n/a | **Not affected** |
| RBT-107 | garden income, H1 / H-REP, depth, stats107, vpost, z10; `fork_check`, `extend_check`, `ckpt_replay` | No. `garden.py:90` and the probes load `genomes/` for the population in `lineage-last.txt`; hrep cuts lineage, cohorts and history. `fork_check.sh:37-38` and `extend_check.sh:41-43` exclude `*/final/*`. PREREGISTRATION.md:92: nothing in RBT-107 reads `final/` | Arms run fresh from season 0 (`fresh_seed.sh:13-15`, "no fork") and were resumed only mid-run. `fork.py` / extend were used in throwaway checks only | Throwaway only. `extend_check.txt` records the bug itself: 35 / 4 / 4 stale files | **Not affected** |
| RBT-112 | READOUT / DECISION; `HZ-*/{freeze,held,function*,rbt102,resting}.txt` | No: `freeze.txt`, `resting.txt`, `best_gen*`, lineage and `genomes/`. Founders are RBT-106's generated founders, with digests | Mid-run resume only (RUNNER.md:88-91) | n/a | **Not affected** |
| RBT-113 | REPORT §3 food/work split (`readout.txt:180-186`), `decompose.*`, adversary probes | **Yes**: `decompose.py:83` and `probe_{work,gear,food}.py` | Arena (`evolve`) runs, population 40. `run_arm.sh` resumes only unfinished lines | No. The population is fixed, and `decompose.py:85-86` asserts n = 40 of generation 23 | **Not affected**: not an ecology run |
| RBT-120, 121, 124, 116, 117, 125 (`gate/steps.py`) | motors / levers / budget / options / counterfactual / apportion; noise, physics probes; sample / passive / wheels; steer_real; compare | **Yes**, the `final/` of RBT-113 O / Z and RBT-120 B1-B4 | Arena runs, population 40; finished runs skipped; no `resumes.txt` | No | **Not affected**: arena, fixed size |
| RBT-102 to 106, 108, 110, 111, 127, 128 | readouts, carriage, world matrix, split probes | No: lineage, `genomes/`, `best_gen*`, seasons, history, state. RBT-111 runs `analyze`, but its readout uses none of the final-diversity output | Mid-run resumes only (RBT-102 seed 3 at season 207; RBT-105 `RESUME=1`) | n/a | **Not affected** |
| RBT-90, 92, 95, 99, 100, 101 | shift / cull / cull20 arms; tables, own_table, wiring; RBT-95 P5 extension | No: history, lineage, `genomes/`, cohorts. RBT-95's `adversary_streams.py` P5 extends a finished run but compares lineage, cohorts, history and config only | Arms start at season 0 (not forks of RBT-90); mid-arm resumes only | n/a | **Not affected** |
| RBT-17, 22, 45; RBT-67 / 78 / 81 / 91 / 97 (the P-801 final60 pool); compass-gain | lesion, nosed bests, reach / wiring, reconcile / truncation / drive spec / arrivals, steering gain | **Yes**: the `final/` of W5-801, W1b-801, W4b-801, P-801, A30-801 and A15-801 | No. Each ran once from season 0, or was relaunched from scratch (A15). The committed `P-801.log` has 600 season lines, 0-599, no repeats | P-801 ends at alive 60 / 60, matching the committed 60 + 60 files | **Not affected**: never resumed after finishing |
| RBT-5, 9, 11, 12, 37, 74, 85, 96, 111 | arena analyze / synergy | Yes (arena) | RBT-37 extends RBT-12's cap-404 from generation 200 to 400 | No: `population_size` stays 20 in the config diff | **Not affected**: arena, fixed size |
| RBT-10, 13-16, 18, 20, 21, 23, 60, 65, 71, 84, baseline-801, HIVE-0926, compass-spike, sim-audit, docs/, ERRATA.md | ecology readouts and probes | No, or the W-series `final/` is empty (extinct), or runs were relaunched fresh. RBT-65 seeds from `best_gen*`. The docs cite `--from-run` / `final/` only for arena runs | Relaunches from scratch only | n/a | **Not affected** |

**Re-read from the living population:** none needed, because no row meets all three conditions. No number moves.

## 4. Latent exposure, for the record

These change no published number:
- RBT-107's throwaway fork and extend directories (35 / 4 / 4
  stale files, not committed as data). Their `final/` includes dead members. A future `levers`, `motors`,
  `--from-run` or `analyze` pointed at a restored snapshot would sample them; with the fix, a further resume
  rewrites `final/` cleanly. To read one of these snapshots, take the population from `state.json` (as
  `analysis._parent_pool` does) or clear `final/` first.
- `runs/RBT-129/design-adversary/probe_launch_cli.txt` ("29 files, 1 differ") hashed stale `final/` files in both
  trees. Its code-identity conclusion stands.
- `Evolution._save_populations`: see §1.

## 5. Files and suite

- `sweep_checkpoints.py` / `.txt`: the checkpoint sweep.
- `final_readers.txt`: the reader grep.
- `fresh_identity.py`, `fresh_identity_prefix_01f113d.txt`, `fresh_identity_fixed.txt`: fresh-run identity.
- `test_rbt131_prefix.txt`, `test_rbt131_fixed.txt`: the new test before and after the fix.
- `suite.txt`: the full suite, in a clean `.[dev]` venv without scipy. 632 passed, 1 skipped, 0 failed (6 min 43 s, x86_64, so the golden-digest tests ran). The one skip is `tests/test_rbt125_harness.py:170`, `importorskip("scipy.stats")`, as intended without scipy.
