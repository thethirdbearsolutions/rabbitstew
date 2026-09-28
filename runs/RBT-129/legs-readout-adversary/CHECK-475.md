# Check of #475 (`steps.py --exclude-exploded`, head b6571bf) against the coordinator's ruling on RBT-129 #467

*This checks #475 for the coordinator (task of 13:52 UTC).
- **Reproduction** ran on the pays-steps inputs already read for #473 (the committed `ckpt/rbt-129-stage0-pays-*` seeds,
  from 125000), with hosts from `ckpt/rbt-113-O1`. It was run only as a diagnostic: nothing ran on the fresh seeds
  (from 126000), and no call was made.
- **Environment:** a clean `.[dev]` venv (numpy only).
- **Tree:** the PR's `rabbitstew/` tree equals 29ab80b's (`b3a29ba`), so the pays legs' inputs reproduce exactly.*

## Verdict: **MERGE**

| item | count |
|---|---|
| MUST | none |
| SHOULD | 1: a registered guard against sub-threshold blow-ups, to be ruled before the fresh-seed readout |
| NIT | 3 |

## 1. Flag off: byte-identical

- **The PR's proof.** `flag_off_repro.txt` re-runs the committed §B cell PW-G2.5 (15 hosts, 128 seeds) and gets a
  sha256 identical to `runs/RBT-125/gate/steps/PW-G2.5.txt`. The PR also has a fixture digest test
  (`test_flag_off_is_byte_identical_to_the_pre_flag_readout`).
- **My reproduction, on a pays-steps output.** I ran the PR's `steps.py`, flag off, on `c2-p030-HP-L` with
  `--config runs/RBT-129/worlds/config/c2-p030-HP-L --hosts-file` for hosts O1/1/016 and O1/1/019, which are the two
  worst r outliers. A host's table row does not depend on the other hosts.
  - **Both rows are byte-identical to the committed `designed.txt` rows**, including r@w3 = **943.448** and **0.006**
    (`check475/c2-p030-HP-L-off.txt`).
- **By code reading,** the flag-off path changes only the unpacking of `bout`'s new sixth field (`exploded`). The
  printed table, steps, r and STEP lines are the old code, unchanged.

## 2. Flag on, against the ruling

| ruling element | in the code (`paired_readout`) | verified by |
|---|---|---|
| a seed exploded in **either** arm of a comparison is dropped from **both**, for items and for path | `pair()`: `keep = ~(boom[hi] \| boom[lo])` on item and net differences; `ratio()`: the same `keep` on both arms' paths | tests (host 0, 1 and 2 cases); my re-runs below |
| it covers speed@w3 vs w3, w3.4 vs w3, the w1 line and the first-nose line (and the installed a = 6 step) | the `steps` dict holds all seven comparisons, and each gets its own pairing | code read |
| r = the ratio of mean path over the remaining paired seeds | `ratio(h, w)` | re-runs: every r equals my #473 explosion-free r (below) |
| a host with > 25% of a comparison's paired seeds exploded leaves the line, and is counted | `too_many(dropped) = dropped > 0.25 × len(SEEDS)`. A per-unit line needs both its nose and its speed comparison under the limit. The count is printed ("n out") | tests; mutants M2, M4, M8 and my M10 |
| exploded counts per host and per arm | the per-host table's last column, and the all-host totals line | re-run output |
| the raw line printed beside, as descriptive | "vs raw speed@w (descriptive, n …)" | re-run output |

**Unchanged** (code read, and the PR's tests and mutants):
- the per-unit formula (× 0.25 ÷ (r − 1));
- the R_MIN = 1.10 exclusion, applied after the explosion step (mutant M7);
- `reading()`, with its labels and order;
- DELTA = 0.10;
- "`len(pu) > 1` or NOT READABLE" (`test_fewer_than_two_hosts_is_not_readable`).

## 3. The explosion test catches the contaminated cases (diagnostic re-runs, flag on)

These are the hosts from #473 §3, re-run under `--exclude-exploded` on the committed pays-steps seeds:

| cell / host | committed r@w3 | #473 explosion-free r | **#475 flag-on r@w3** | exploded seasons (w3, speed@w3) |
|---|---|---|---|---|
| c2-HP-L / 1/016 | **943.448** | 1.266 | **1.266** | 1, 2 |
| c2-HP-L / 1/019 | **0.006** | not re-run | **1.217** | 1, 0 |
| c1-PW-G / 3/009 | **236.826** | 1.238 | **1.238** | 2, 1 |
| c1-PW-G / 1/019 | 0.508 | 1.190 | **1.190** | 1, 1 |
| c2-PW-G / 3/004 | 1.420 (registered: in) | 1.062 | **1.062** (now out at < 1.10) | 1, 3 |
| c2-PW-G / 3/031 | 0.645 (registered: out) | 1.101 | **1.101** (now in) | 3, 0 |

- **Every blow-up that drove r in my #473 cases is caught.** The flag's `sim.exploded` is the same test my diagnostic
  used, and its r reproduces mine to the digit.
- The extreme case's committed row (1/016) was carried by one season whose centre of mass "moved" at 52,340 m/s
  (`probe_r_outlier.txt`). That season is flagged exploded and dropped.

**Mutants.** The PR lists M1–M8, all killed. I re-ran M3 myself (r over every seed): 2 tests fail. I also added two new
ones:
- **M9:** r drops only the speed arm's explosions. It is killed (1 test fails).
- **M10:** the > 25% limit is applied to the nose comparison only. It is killed (1 test fails).

The harness tests pass: 16 passed, and 1 skipped (the pre-existing scipy cross-check, absent in a clean venv).

## 4. Can a partial blow-up below the explosion threshold still dominate r?

**Yes in principle, and it is not bounded by the flag.**
- `exploded` fires only when a body passes `explosion_speed` (200 m/s).
- A season that shakes violently below that speed, or a burst the robot recovers from, adds path without being flagged.
- **The evidence is modest.** On 1/016 (the one host with per-season paths on record), the largest non-exploded seasons
  are 2.2 and 3.8 m/s against a median of 0.37–0.47 m/s: an 8× season. One such season among 128 moves that arm's
  mean path by about 5%. That is enough to move a host across r = 1.10, as with host 3/031 at 1.101.
  - Its ratio of medians (1.277) against its paired-mean r (1.266) shows no domination on that host.
  - It cannot be excluded elsewhere without per-season data, which `steps.py` does not print.

**What a registered guard would look like** (for the coordinator to rule before the fresh-seed readout; it is not
proposed as a re-call of anything):
- **(a) A physical cap on path speed:** treat a season as blown up if its mean centre-of-mass path speed exceeds a
  fixed ceiling above any Pioneer's top speed (for example 3 m/s), and pair-drop it exactly like an explosion.
- **(b) A robust r:** the ratio of the per-host *medians* of the paired per-season path speeds, in place of the ratio
  of means, keeping the 1.10 exclusion.
- Either option is one line in `ratio()`, and should print the count of seasons it removes.
- **Cheapest first step:** print, per host and arm, the maximum non-exploded path speed. That shows on the fresh seeds
  whether (a) or (b) would change anything, without changing the rule.

## SHOULD

1. Before the fresh-seed readout is read, register one sub-threshold guard from §4, or at least print the per-host
   maximum non-exploded path speed. That way a residual partial blow-up is visible rather than silent.

## NIT

1. **The per-host table under the flag is unpaired.** It prints each arm's items over that arm's own non-exploded seeds,
   but the steps and lines use per-comparison pairs. Say so in its header, so no one recomputes a line from the table
   (the committed-table recompute that #467 and #473 used would not reproduce the flag's lines).
2. **With 1 host in a per-unit comparison, the speed-step summary prints `[+nan, +nan]`** (for example, c1-PW-G at w1
   in my two-host run). The reading itself correctly says NOT READABLE. Print "--" as the STEP line does.
3. **Merge integration into the branch before merging.** It is 6 commits behind, but merges clean, with no change to
   `steps.py` or its tests on integration's side.

## Files (`runs/RBT-129/legs-readout-adversary/check475/`)

| file | what it holds |
|---|---|
| `c2-p030-HP-L-off.txt` | flag off, hosts 1/016 and 1/019: rows byte-identical to the committed `designed.txt` |
| `c2-p030-HP-L-on.txt`, `c1-p030-PW-G-on.txt`, `c2-p030-PW-G-on.txt` | flag on, the #473 outlier hosts: per-arm exploded counts, and r over the paired seeds |
| `hosts_*.txt` | the host files used, relative to `ckpt/rbt-113-O1`'s root |

Reproduce, in #475's tree, with `HOSTS_ROOT` extracted from `ckpt/rbt-113-O1`:
`python runs/RBT-125/gate/steps.py HOSTS_ROOT <cell> --config runs/RBT-129/worlds/config/<cell> --hosts-file <file> [--exclude-exploded]`.
