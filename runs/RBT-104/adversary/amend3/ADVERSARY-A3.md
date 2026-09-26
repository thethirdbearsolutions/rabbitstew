# RBT-104 design adversary: re-check of Amendment 3 (PR #223, head `2848b06`)

*RBT-104's design adversary, 2026-09-26, about 23:10 UTC. This re-checks **Amendment 3 only**, at the
coordinator's request of 22:55. **No arm output was read.** The only arm information used is branch
metadata: commit subjects, times and file names. Platform: x86_64, MuJoCo 3.14.0. The probes are in
this directory, and `REPRO.md` says how each was run.*

## Verdict: CLEAR once A4 is fixed

The null is faithful and the k_planted/k_bare split is clean. The power statement is correct
arithmetic and needs a wider statement of its range. The regeneration from checkpoints works.

**One MUST-FIX remains, in `readout.py` (A4).** A window reading that is missing or refused is
counted as "not held", so it pushes the verdict towards **F-b**. The coordinator's plan to
regenerate the files under new names would trigger exactly that path.

| # | severity | one line |
|---|---|---|
| A1 | NONE | The null is faithful: unedited, all ten tables identical to `85cdee48`, seed 801 re-run independently cell for cell, criterion and roots the same as `peek.py`'s |
| A2 | CAVEAT | The copied `null_xover.py` cannot run from `runs/RBT-104/`; the tables came from the script's earlier version, with identical numbers |
| A3 | NONE | The k_planted/k_bare split is clean and identical in `peek.py`, the null and `readout.py` |
| A4 | **MUST-FIX** | A missing or refused window reading counts as "not held", which reads F-b; and `readout.py` reads only `peek-{300,599}.txt`, the names of the pre-amendment files |
| A5 | CAVEAT | P(SUPPORTED \| H) ≈ 0.11–0.14 is right at n = 10 as an upper bound. It is ≤ 0.03 at n = 7, and 0.005–0.52 across d_c's own uncertainty |
| A6 | CAVEAT | Timing: consistent, but tight. S8-4's 600-season tables were pushed 4 min 52 s before the amendment; they hold nothing that bears on what it changes |
| A7 | NONE | Workable: a checkpoint holds `lineage.jsonl` and every genome, and Amendment 3's window path runs and parses end to end |

---

### A1. Is the null faithful to the full operator, and applied at every cell's criterion? NONE

**The copy is unedited.**
- `null_xover.py` is byte-identical to `85cdee48:runs/RBT-106/adversary/null_xover.py`.
- All ten `xnull-w1-k8-SEED.txt` tables and all ten `baseline106/baseline-w1-k8-SEED.txt` tables
  are identical to `85cdee48`'s.

**It reproduces independently** (`xnull-801-rerun.txt`). I re-ran the script from RBT-106's tree on
part 2's own 801 genealogy, restored from `ckpt/rbt-90-801`, with the pre-registered founders
(digest `78493e74…`) at 20 replicates. It is identical to the committed table **in every cell**, in
both the full-operator and the mutation-only branches.

**The operator is the ecology's own.**
- A recorded mate gives `crossover_controller` then `mutate_controller`. There are 374 of 1,235
  births with a mate on 801, a share of 0.303.
- One parent gives `mutate_controller` only.
- `link_scale` is 8, and the MutationConfig is part 2's.

**Its criterion is `peek.py`'s.**
- RBT-106's `held.hit(av, s0, "pay64")` is: same sign as the root (either sign when the root is
  bare) and own links ≥ 24.7145.
- It calls RBT-104's `peek.own_links` and `binom_q95`, imported, not copied.
- The root is the founder reached along `parents[0]`, and "planted" means the root carries the
  structure at founding. Both are as in `peek.py`.

**Its baseline μ is RBT-104's.** `baseline106` equals `baseline-{801,4}.txt` at every shared depth
(0–30). The depth caps differ, 40 in the null against 30 in `peek.py`. That is immaterial here:
on 801's genealogy the living genomes' parents[0] depth is at most 7, 12 and 24 at seasons 150, 300
and 599.

**Applied at every cell.**
- HELD, now on k_planted at 300 and 599, is scored from the same tables by `null_rates.py`, which
  re-derives byte for byte.
- The gate is re-read post hoc, and labelled so.
- F-a and F-m are both gated on "held on ≥ 2 seeds", so they inherit HELD's null. P(held on ≥ 2
  of 10 | null) is 0.0011, or 0.020 at the rate's upper bound.
- No other verdict cell reads a no-selection null.

**One approximation is disclosed.** The null runs on part 2's genealogies, bred at K = 1 with no
seed, not on S8's. The amendment says so ("the ten RBT-90 part-2 genealogies"). The depth mismatch
is absorbed by reading μ at each genome's own depth. The clustering of S8's own genealogy is not
modelled; §6.2 already states that this errs towards "held".

### A2. Provenance of the copied null. CAVEAT

- `runs/RBT-104/null_xover/null_xover.py` imports `null_genealogy.py` from its parent directory,
  which is `runs/RBT-104/`. **No such file exists there, so the script fails in place**
  (`FileNotFoundError: …/runs/RBT-104/null_genealogy.py`).
- Only `null_rates.py`'s re-reading of the tables can be re-derived from RBT-104's checkout.
- The committed tables were written by the script's 22:08 version, `19f6ca24`. Their header lacks
  ", deepen x1". Today's script reproduces them exactly, apart from that suffix.

**Fix (one sentence in §6.5):** re-derivation runs from `runs/RBT-106/adversary/` once #222 is
merged, as `REPRO.md` here does. Otherwise, copy its two imports.

### A3. The k_planted/k_bare split. NONE

Every place uses the same partition.
- **In `peek.py`:** a living genome is planted-rooted if its `parents[0]` root carries the
  structure. Its hit is counted in k_planted, and its depth enters n and μ. A bare-rooted hit at
  either sign is counted in k_bare, and enters neither n nor μ.
- **In the null:** identically.
- **In `readout.py`:** `peek()` parses `k` as k_planted and `k_bare` beside it, and `above` is
  `k_planted > B`. `tests/test_rbt104_amend3.py` checks this.

A planted-rooted genome whose unit arrived by crossover from another lineage counts in k_planted,
and the null counts it the same way, so the comparison is like for like.

The gate's post hoc line, "k_planted 12 > B 8; the null gives k_planted > B at 801 in 0 of 20", is
correctly read from the table (gate on k_planted: 801 0/20).

### A4. A missing or refused window reading reads as F-b. MUST-FIX

The problem is in `readout.py` at `2848b06`.
- It reads the window files only as `S8-SEED/peek-300.txt` and `peek-599.txt` (lines 129–130).
- It returns `None` for a pre-amendment file (the new refusal) or an absent one.
- It then builds `held = [s … if usable … and w300 and w599 and both above]` (lines 196–197).
- A seed with no valid reading is therefore **not held**, and "held on ≤ 1 seed" gives **(F-b)**
  (line 232). The MISSING line is printed, but the verdict does not use it.
- That contradicts the file's own rule: "each leaves the rules it feeds, never read as a null".

**It is not hypothetical under the 22:55 plan.**
- The runners commit `peek-{300,599}.txt` in the launch commit's format, which `readout.py`
  refuses by design.
- The designer's regenerated files are to be committed beside them, "named for Amendment 3". A
  name `readout.py` does not read means that, **with a FALSIFIED count, every seed reads "not held"
  and the verdict is F-b by construction.**
- And the launch commit's `peek.py` has no baseline for eight seeds. So those runners' window steps
  may fail outright and leave no file at all, with the same result.

**Fix, both parts:**
- (a) Fix the Amendment 3 filenames now, for example `peek-a3-{300,599}.txt`, and point
  `readout.py` at them.
- (b) If any usable S8 seed lacks a valid Amendment 3 window reading, the FALSIFIED branch reads
  **NOT READ** (the count may still be printed), not F-b.

Add a test that removes one seed's window file and asserts the branch is not F-b.

### A5. Power: correct, and stated too narrowly. CAVEAT

`power_a3.txt` re-derives the amendment's arithmetic. The inputs are q_c = q_H · d_c / d, with
q_H = 0.5, d = 0.82 and d_c = 0.50 (4 of 8 RBT-103 decoy readouts meet the retention rule,
confirmed in `docs/artifacts/RBT-103-decoy-*.txt`). That gives q_c = 0.305, P(≥ 5 of 10) = 0.159,
and **≤ 0.117–0.146 after the S1 condition**. The amendment's 0.11–0.14 is the same figure,
rounded from q = 0.30.

It should also state three things:
- it is an **upper bound**, because the paired-F condition is not included;
- **at the VOID floor, n = 7, it is ≤ 0.023–0.028**;
- d_c is 4/8, with a Wilson 95% interval of [0.215, 0.785]. Over that interval P(SUPPORTED | H)
  runs from **0.004 to 0.52** at n = 10.

The other restated figures are correct from `null_rates.txt` and `power.txt`:
- FALSIFIED's count: 0.011 (0.062 at n = 7);
- F-b: 0.011;
- P(held ≥ 2 | null): 0.0011, or 0.020 at the upper bound;
- the S1 cap: 0.735–0.921.

The coordinator's 22:55 instruction, that a NOT SUPPORTED carries its power figure and does not
read as "no compass", is what these numbers require.

### A6. Committed before any arm output past season 150 was read? Consistent, but tight. CAVEAT

This is from branch metadata only.

| time (UTC) | event |
|---|---|
| 20:59:30, 21:18:53 | the season-150 peeks (S8-4, S8-801) |
| 22:36:11 | the coordinator's comment asking for Amendment 3, items 1–4 |
| **22:38:58** | **`results/RBT-104-S8-4` 4f0225a: `seasons.txt` and `lineage-last.txt` (600 seasons)** |
| 22:43:50, 22:44:05 | Amendment 3's commits 40ea758 and 2848b06 |
| 22:46:50 | `results/RBT-104-S1-801`: its 600-season tables (after the amendment) |

**Before 22:44:05, no window reading, `rbt102.txt` or `function.txt` existed on any RBT-104 branch.**
The only post-150 arm output was S8-4's per-season summary and lineage-last table, pushed 4 min 52 s
earlier. Those hold income, alive counts and parentage. They hold nothing about k_planted, own-link
magnitude or food dependence, which is everything the amendment changes.

The amendment's rule changes follow the coordinator's 22:36 items one for one:
- the full-operator null;
- k_planted separate from k_bare;
- the attribution for "compass";
- power restated.

Its re-stated predictions are a renormalisation for the stricter SUPPORTED. So the claim is
consistent with the record, and the leverage of anything readable at 22:38 on these rules is nil.

**Required, one sentence:** §6.5 should say that S8-4's 600-season tables were on the remote from
22:38:58, and whether they were opened. The 22:44 ticket comment says "no arm output … was read",
but the record shows the output existed.

### A7. Is regeneration from checkpoints workable? NONE

- **The checkpoint holds what `peek.py` needs.** `durable.sh` tars the whole run directory.
  Part 2's 801 checkpoint at 600/600 extracts to `lineage.jsonl` (71,288 rows),
  `conventional/genomes` (1,295 genomes: 60 founders and 1,235 births) and `state.json`.
  `run_arm.sh` (`2848b06`) does not pass `--no-genomes`.
- **The window path runs** (`workability.txt`). I made a throwaway 8-season S8-801 run with the
  pre-registered founders at `--link-scale 8`, and ran Amendment 3's `peek.py` `main()` with its
  window constant moved to season 5.
  - It prints `WINDOW seed 801 season 5: k = 28, n = 31, B = 30 -> AT OR BELOW NO-SELECTION;
    k_bare = 0`. That is the designer's own smoke reading, reproduced.
  - `readout.peek()` parses it, with k_bare present and HELD on k_planted.
  - The launch-format line is refused.
- **It is cheap.** Each reading synthesises about 60 living genomes and their roots, which takes
  seconds.
- **Suite on `2848b06`:** 310 passed. `null_rates.py` re-derives `null_rates.txt`. `readout.py`
  on the branch reads NOT READ, so no arm data is in it.

---

## What clears it
1. **A4:** fixed Amendment 3 window filenames that `readout.py` reads, and missing or refused
   readings giving NOT READ for the FALSIFIED branch, with a test.
2. One sentence each:
   - **A2:** where the null re-derives from;
   - **A5:** the upper bound, the n = 7 figure and the d_c range;
   - **A6:** the S8-4 tables' timestamp and whether they were opened.

## Files (`runs/RBT-104/adversary/amend3/`)
| file | what |
|---|---|
| `ADVERSARY-A3.md` | this report |
| `xnull-801-rerun.txt` | A1: the independent re-run of the full-operator null, seed 801, 20 replicates |
| `workability.py`, `workability.txt` | A7 and A4: the window path, regenerated and parsed, on a throwaway run |
| `power_a3.py`, `power_a3.txt` | A5 |
| `REPRO.md` | inputs and commands |

---

## Addendum, 23:10 UTC: A4 re-checked at `2524ae6`. CLEAR

The designer's fix was checked for A4 only. No arm output was read.
- **The filenames.** `readout.py` reads the window readings only from `S8-SEED/peek-a3-{300,599}.txt`
  (`WINDOW_FILES`). The launch-format names appear nowhere in its source, and a test asserts this.
- **A missing reading is no longer read as F-b.** The FALSIFIED branch is now
  `readout.falsified_branch()`. If any usable S8 seed lacks a valid Amendment 3 reading (the file
  is missing, or the reading is refused for having no `k_bare`), it returns **"branch NOT READ"**,
  never F-b. F-b, F-m and F-a are read only when every usable seed has both readings.
  `test_a_missing_window_reading_never_reads_as_f_b` covers a missing 599 reading, a missing pair,
  an absent key, and the complete case. A `peek.py` run that refuses writes no WINDOW line, so it
  parses as missing, which fails safe.
- **The documents name the files.** The `peek.py` docstring and §5 and §6.5 give the command
  (`peek.py … --season 300 > S8-SEED/peek-a3-300.txt`, and likewise 599) and say the readings
  come from Amendment 3's `peek.py` on integration, regenerable from the checkpoint. A7's probe
  showed that regeneration works.
- **A2, A5 and A6** each have their sentence in §6.5. For A6 the designer states that S8-4's tables
  were not opened, and that no RBT-104 arm branch or checkpoint ref was fetched into the design
  clone.
- **Tests:** `tests/test_rbt104_amend3.py` passes 6 of 6, and the full suite on `2524ae6` passes
  **312**.

**Amendment 3 clears.** Nothing from this re-check is left open.
