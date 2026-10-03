# RBT-129 Stage 1 readout (S arm, and the gated M and N forks): READOUT-STAGE1

*Go: `RBT129-S1-READOUT-GO-1` (`GO-RBT129-S1-READOUT-GO-1.md`, merged in #516 at
`fe3a602975fcbbd2732620589d3ccd96acc4feb7`). Plan: `READOUT-PLAN.md` (merged in #512). Script: `stage1_readout.py`, run as
committed. No line of the script, plan, rules, thresholds or definitions was changed. Every number below is copied from
a line of `stage1_readout.txt` (cited `Lnnn`) or `integrity.txt` (cited `I-n`). No statistic in this report was
computed outside the script.*

*Commits on `claude/rbt129-stage1-readout`, in order:*
1. *`integrity.txt`: `0f5aee12b4dfecc5fb4294cc67ba4705da5bb07f`, committed and pushed before `readout` ran;*
2. *`stage1_readout.txt`: `e129dccf497d83af1b2afbf18f6690aa7b5cf827`, committed and pushed before this report was
   written;*
3. *`READOUT-STAGE1.md`: this file.*

**Claim label, on every call, table and map below:** *"among holistic and designed stream draws (founders and their
early history) that establish at W118-b"*. Every share-layer line is read *"under the committed rule"* (L1–L2).
**Every Stage-1 call, M1/M4 count, Holm decision and the §8 evaluation is PROVISIONAL** (plan §5, §9). The sweep answers
which body *earns* more, and where. It does not answer which body *persists*.

## 1. Headline: M1 call table and M4 area shares (PROVISIONAL)

*Among holistic and designed stream draws (founders and their early history) that establish at W118-b. Provisional.*

| layout | body calls (count, area share) | income calls | line |
|---|---|---|---|
| G (27) | EXCLUDED-D 2 (0.07), EXCLUDED-H 4 (0.15), NEITHER 5 (0.19), NOT RUN 11 (0.41), PARTIAL-D 4 (0.15), PARTIAL-H 1 (0.04) | EARNS-D 6, NOT TESTED 11, UNDECIDED 10 | L376 |
| L (9) | EXCLUDED-H 1 (0.11), NEITHER 2 (0.22), NOT RUN 3 (0.33), PARTIAL-D 1 (0.11), PARTIAL-H 1 (0.11), RBT-118 (not available) 1 (0.11) | EARNS-H 2, NOT TESTED 2, UNDECIDED 5 | L377 |

- No share WIN, TIE, CONTINGENT, SATURATED or UNDECIDED body call occurs, as plan §0 worked out in advance. The share
  families are empty (L309).
- No EARNS-TIE occurs (L376–L377).
- LEVER: not evaluated. VARIANCE-DRIVEN: not reachable, because there is no share WIN.
- **Provisional §8 (§8 below):** **EARNINGS DEPEND** (L423), *among holistic and designed stream draws (founders and
  their early history) that establish at W118-b; provisional: Stage-1 calls only; not a verdict.*

## 2. Integrity

`integrity.txt` reads **INTEGRITY PASS** under go `RBT129-S1-READOUT-GO-1` (I-1, I-15). Verdicts, as printed:

| § | verdict | line |
|---|---|---|
| 2.5 | local refs naming the quarantined unit: 0 | I-2 |
| 2.1 | branches: 973 of 973 expected labels have a branch | I-3 |
| 2.1 | the quarantined branch `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M`: listed by ls-remote (name only; never read) | I-4 |
| 2.2 | done-markers: 973 present (extinct-pre-merge skips included, not split out); missing S-arm 0, M/N 0, other 0 | I-5 |
| 2.4 | `CRASHED: 1/c2-p030-U-G/129001/M (native SIGSEGV in libmujoco 3.14.0, projectOriginPlane under mjc_ccd), x4` | I-6 |
| 2.4 | crash bookkeeping: PASS | I-7 |
| 2.3 | resume audit: 720 of 721 directories clean; 1 accepted under the listed double-write signature (`runs/RBT-129/stage0/c1-p010-PW-G/129003/S`) | I-8, I-9 |
| 2.6 | MuJoCo 3.14.0: PASS, on every S, every ckpt60 copied from a live S, and every M/N, at top level and on every resume. Each ckpt60 without `platform.json` is an extinct-pre-merge snapshot, verified by `EXTINCT.txt` and its marker | I-10 |
| 2.7 | K-SALT: 72 of 72 PASS (unit record's `KSALT.txt`) | I-11 |
| 2.7 | the known case `1/c1-p010-PW-G/129003/KSALT`: record PASS, ksalt dir VOID, marker VOID | I-12 |
| 2.7 | the gate's valid-at-merge counts against `gate_table.txt`: PASS | I-13 |
| 2.7 | K1: pilot PASS at `c1-p030-U-L`, `c0-p030-U-L`; UNTESTABLE at `c1-p030-PW-G`, `c2-p030-PW-G`; never tested on PW terrain; no Stage-1 point is VOID by K1 | I-14 |

- **K-SALT known case.** The ksalt directory and its marker still read VOID. The unit record reads PASS under the O-1
  ruling (`RULINGS-CITED.md`; record `b00fc6af02fcf6d67dc7b257340e98e70f992a5a`), with the superseded VOID kept. This
  is the disagreement plan §2.7 anticipated, and the record reads `KSALT PASS` as that section requires. No
  `KSALT-VOID:` line is ruled, so n = 8 at every point.
- **CRASHED and disclosure** (`mn-crash/RULING.md` r3).
  - The host1 runner displayed 0 per-season lines (`INTEGRITY-host1.md`).
  - The coordinator saw job names, exit codes, dmesg lines, faulthandler frames, and attempt start and crash times.
  - The second-host reproduction (`REPRO-host7.md`) reads REPRODUCED. Its scratch directories were deleted unread.
  - The gate table's valid-seed counts were seen at emission.
  - Nothing about how far the crashed unit got is reported anywhere here.
- **Quarantine.** The quarantined branch was never fetched, restored, checked out or read by this session. Every fetch
  was the script's own narrow `fetch_label`; no bare `git fetch`, `git pull` or `git fetch --all` was run. Before and
  after the run, no local ref named the unit (I-2).
- **Coordinator disclosure** (`coordinator/DISCLOSURE-2026-10-02.md`). It stands as written. It does not touch this
  run, which only executed the committed script.
- **Provenance, relayed, not read** (coordinator FYI to this session, 2026-10-02 22:48 UTC):
  - #513 was squash-merged into `claude/new-session-4cao7d` at `02f7d47`.
  - It reports all physics runs at MuJoCo 3.14.0.
  - It also reports a third checkout sha, `716e2d3c8aaa4a8c31a1f3a95e514ff9b67e44a0`, on 26 census runs.
  - **Recorded here as provenance only, not as an outcome.** This session did not read #513 or `stage1-provenance/`,
    and the script reads neither (plan §2.6). The script's own 2.6 check is the integrity verdict (I-10).
  - That message also carried an aggregate count of physics runs. It reached this session while integrity was
    running, before any outcome output existed. No call, rule or number here depends on it.
- **Exclusions** (L622): none beyond K-SALT VOID (none ruled), validity (plan §3.1) and CRASHED. Nothing was
  winsorised or re-weighted.

## 3. The per-point table

*Among holistic and designed stream draws (founders and their early history) that establish at W118-b. Every call is
provisional.*
- **Columns.** n share and n income are "valid of n" (plan §3.1). x̄ is Flow(H) − Flow(D) over 240–299 in S.
- **BH.** The script prints the BH outcome through the call: EARNS-X means BH-significant in the EARNS family (q =
  0.10, K = 23 points tested, L309) with |x̄| ≥ 0.10. No separate adjusted p is printed.
- **MARGINAL** is printed on EARNS calls only (plan §4.3).
- **The table** reproduces the script's per-point header lines field by field (a text-only reformat; see Observations).

| line | point | body call | n share | n income | x̄ | SD | t | p | TOST p | income call (BH via call) | M | N | y′ (descr.) | M g0 (census conv.) | census g0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L6 | `c0-p010-U-G` | NOT RUN | 7/8 | 7/8 | -0.386 | 0.260 | -3.92 | 0.0078 | 0.9733 | EARNS-D MARGINAL | -- | 0 | -- | -- (--) | 1.426 |
| L14 | `c0-p010-HP-G` | NOT RUN | 7/8 | 6/8 | -0.817 | 0.958 | -2.09 | 0.0911 | 0.9255 | UNDECIDED | -- | 0 | -- | -- (--) | 1.795 |
| L22 | `c0-p010-PW-G` | EXCLUDED-H | 1/8 | 1/8 | -0.025 | -- | -- | -- | -- | NOT TESTED | 1 of 1 | 0 | -0.500 | 0.764 (0.734) | 0.666 |
| L31 | `c0-p030-U-G` | NOT RUN | 7/8 | 7/8 | -0.596 | 0.257 | -6.14 | 0.0009 | 0.9981 | EARNS-D MARGINAL | -- | 0 | -- | -- (--) | 1.454 |
| L39 | `c0-p030-HP-G` | NOT RUN | 7/8 | 7/8 | -1.331 | 0.528 | -6.67 | 0.0005 | 0.9995 | EARNS-D MARGINAL | -- | 0 | -- | -- (--) | 1.904 |
| L47 | `c0-p030-PW-G` | EXCLUDED-H | 2/8 | 1/8 | +0.180 | -- | -- | -- | -- | NOT TESTED | 2 of 2 | 2 | -0.167 | 0.472 (0.447) | 0.458 |
| L57 | `c0-p080-U-G` | NOT RUN | 7/8 | 7/8 | -0.877 | 0.229 | -10.14 | 0.0001 | 0.9999 | EARNS-D MARGINAL | -- | 0 | -- | -- (--) | 1.541 |
| L65 | `c0-p080-HP-G` | NOT RUN | 7/8 | 7/8 | -1.653 | 0.399 | -10.95 | 0.0000 | 1.0000 | EARNS-D MARGINAL | -- | 0 | -- | -- (--) | 2.293 |
| L73 | `c0-p080-PW-G` | NEITHER | 0/8 | 0/8 | -- | -- | -- | -- | -- | NOT TESTED | -- | 0 | -- | -- (--) | 0.329 |
| L81 | `c1-p010-U-G` | NOT RUN | 7/8 | 6/8 | -0.092 | 0.306 | -0.74 | 0.4949 | 0.3302 | UNDECIDED | -- | 0 | -- | -- (--) | 1.181 |
| L89 | `c1-p010-HP-G` | NOT RUN | 6/8 | 6/8 | -0.288 | 0.339 | -2.08 | 0.0916 | 0.8182 | UNDECIDED | -- | 0 | -- | -- (--) | 1.487 |
| L97 | `c1-p010-PW-G` | EXCLUDED-H | 1/8 | 1/8 | +0.191 | -- | -- | -- | -- | NOT TESTED | 1 of 1 | 1 | +0.487 | 0.726 (0.698) | 0.554 |
| L107 | `c1-p030-U-G` | NOT RUN | 8/8 | 7/8 | -0.186 | 0.373 | -1.32 | 0.2354 | 0.5965 | UNDECIDED | -- | 0 | -- | -- (--) | 1.059 |
| L115 | `c1-p030-HP-G` | PARTIAL-D | 5/8 | 5/8 | -0.596 | 0.217 | -6.14 | 0.0036 | 0.9950 | EARNS-D MARGINAL | -- | 0 | -- | -- (--) | 1.239 |
| L123 | `c1-p030-PW-G` | NEITHER | 0/8 | 0/8 | -- | -- | -- | -- | -- | NOT TESTED | -- | 0 | -- | -- (--) | 0.434 |
| L131 | `c1-p080-U-G` | PARTIAL-H | 3/8 | 2/8 | +0.271 | 0.071 | +5.40 | 0.1166 | 0.8749 | UNDECIDED | -- | 0 | -- | -- (--) | 0.857 |
| L139 | `c1-p080-HP-G` | PARTIAL-D | 5/8 | 5/8 | -0.197 | 0.292 | -1.51 | 0.2059 | 0.6308 | UNDECIDED | 5 of 5 | 0 | +0.319 | 1.332 (1.279) | 0.934 |
| L148 | `c1-p080-PW-G` | NEITHER | 0/8 | 0/8 | -- | -- | -- | -- | -- | NOT TESTED | -- | 0 | -- | -- (--) | -- |
| L156 | `c2-p010-U-G` | PARTIAL-D | 5/8 | 5/8 | +0.182 | 0.162 | +2.51 | 0.0657 | 0.6611 | UNDECIDED | -- | 0 | -- | -- (--) | 1.113 |
| L164 | `c2-p010-HP-G` | NOT RUN | 7/8 | 7/8 | -0.268 | 0.400 | -1.77 | 0.1265 | 0.7681 | UNDECIDED | -- | 0 | -- | -- (--) | 1.387 |
| L172 | `c2-p010-PW-G` | EXCLUDED-H | 2/8 | 0/8 | -- | -- | -- | -- | -- | NOT TESTED | 2 of 2 | 2 | +0.061 | 0.631 (0.601) | 0.535 |
| L182 | `c2-p030-U-G` | NOT RUN | 8/8 | 6/8 | +0.096 | 0.114 | +2.07 | 0.0936 | 0.1490 | UNDECIDED | 7 of 8 (1 CRASHED) | 0 | -0.176 | 1.058 (1.036) | 0.938 |
| L191 | `c2-p030-HP-G` | PARTIAL-D | 5/8 | 5/8 | -0.190 | 0.251 | -1.69 | 0.1660 | 0.6293 | UNDECIDED | -- | 0 | -- | -- (--) | 1.325 |
| L199 | `c2-p030-PW-G` | NEITHER | 0/8 | 0/8 | -- | -- | -- | -- | -- | NOT TESTED | -- | 0 | -- | -- (--) | -- |
| L207 | `c2-p080-U-G` | EXCLUDED-D | 0/8 | 0/8 | -- | -- | -- | -- | -- | NOT TESTED | -- | 0 | -- | -- (--) | 0.936 |
| L215 | `c2-p080-HP-G` | EXCLUDED-D | 1/8 | 0/8 | -- | -- | -- | -- | -- | NOT TESTED | -- | 0 | -- | -- (--) | 1.003 |
| L223 | `c2-p080-PW-G` | NEITHER | 0/8 | 0/8 | -- | -- | -- | -- | -- | NOT TESTED | -- | 0 | -- | -- (--) | -- |
| L231 | `c1-p010-U-L` | NOT RUN | 7/8 | 7/8 | +0.001 | 0.199 | +0.01 | 0.9930 | 0.0472 | UNDECIDED | -- | 0 | -- | -- (--) | 1.204 |
| L239 | `c1-p010-HP-L` | NOT RUN | 6/8 | 6/8 | -0.079 | 0.361 | -0.54 | 0.6147 | 0.3256 | UNDECIDED | -- | 0 | -- | -- (--) | 1.331 |
| L247 | `c1-p010-PW-L` | EXCLUDED-H | 2/8 | 2/8 | +0.182 | 0.011 | +23.91 | 0.0266 | 0.9261 | EARNS-H MARGINAL | 2 of 2 | 2 | +0.082 | 0.620 (0.590) | 0.543 |
| L257 | `c1-p030-U-L` | RBT-118 (not available) | 8/8 | 8/8 | -0.003 | 0.287 | -0.03 | 0.9771 | 0.0952 | UNDECIDED | -- | 0 | -- | -- (--) | 1.060 |
| L265 | `c1-p030-HP-L` | NOT RUN | 7/8 | 6/8 | +0.166 | 0.375 | +1.08 | 0.3285 | 0.5391 | UNDECIDED | -- | 0 | -- | -- (--) | 1.170 |
| L273 | `c1-p030-PW-L` | NEITHER | 0/8 | 0/8 | -- | -- | -- | -- | -- | NOT TESTED | -- | 0 | -- | -- (--) | 0.525 |
| L281 | `c1-p080-U-L` | PARTIAL-H | 5/8 | 5/8 | +0.256 | 0.195 | +2.93 | 0.0429 | 0.8538 | UNDECIDED | 5 of 5 | 0 | +0.345 | 1.096 (1.070) | 0.818 |
| L290 | `c1-p080-HP-L` | PARTIAL-D | 5/8 | 3/8 | +0.254 | 0.083 | +5.32 | 0.0335 | 0.9194 | EARNS-H MARGINAL | 5 of 5 | 0 | +0.198 | 1.231 (1.189) | 0.680 |
| L299 | `c1-p080-PW-L` | NEITHER | 0/8 | 0/8 | -- | -- | -- | -- | -- | NOT TESTED | -- | 0 | -- | -- (--) | -- |

**n at the merge per seed** (n_H / n_D at season 59, from ckpt60 or S; plan §3.3):

| line | point | merge counts (H/D) per seed |
|---|---|---|
| L7 | `c0-p010-U-G` | 129001:60/60 129002:60/60 129003:60/60 129004:60/60 129005:60/60 129006:60/60 129007:0/60 129008:60/60 |
| L15 | `c0-p010-HP-G` | 129001:60/60 129002:60/60 129003:6/60 129004:60/60 129005:60/60 129006:60/60 129007:0/60 129008:60/60 |
| L23 | `c0-p010-PW-G` | 129001:0/60 129002:0/60 129003:0/60 129004:0/60 129005:60/60 129006:0/60 129007:0/60 129008:0/60 |
| L32 | `c0-p030-U-G` | 129001:60/60 129002:60/60 129003:49/60 129004:12/60 129005:60/60 129006:60/60 129007:0/60 129008:60/60 |
| L40 | `c0-p030-HP-G` | 129001:60/60 129002:60/60 129003:9/60 129004:60/60 129005:60/60 129006:31/60 129007:0/60 129008:60/60 |
| L48 | `c0-p030-PW-G` | 129001:3/42 129002:0/47 129003:0/59 129004:0/39 129005:22/60 129006:0/36 129007:0/60 129008:0/55 |
| L58 | `c0-p080-U-G` | 129001:60/60 129002:60/60 129003:60/60 129004:60/60 129005:60/60 129006:60/60 129007:0/60 129008:60/60 |
| L66 | `c0-p080-HP-G` | 129001:60/60 129002:60/60 129003:20/60 129004:60/60 129005:60/60 129006:60/60 129007:0/60 129008:60/60 |
| L74 | `c0-p080-PW-G` | 129001:0/9 129002:0/0 129003:0/12 129004:0/0 129005:37/0 129006:0/21 129007:0/0 129008:0/7 |
| L82 | `c1-p010-U-G` | 129001:60/60 129002:60/60 129003:16/60 129004:60/60 129005:60/60 129006:0/60 129007:3/60 129008:60/60 |
| L90 | `c1-p010-HP-G` | 129001:60/60 129002:60/60 129003:31/60 129004:60/60 129005:60/60 129006:0/60 129007:0/60 129008:60/60 |
| L98 | `c1-p010-PW-G` | 129001:0/60 129002:0/60 129003:0/60 129004:0/60 129005:60/57 129006:0/58 129007:0/60 129008:0/60 |
| L108 | `c1-p030-U-G` | 129001:60/60 129002:60/60 129003:1/60 129004:60/60 129005:60/60 129006:60/60 129007:3/60 129008:60/60 |
| L116 | `c1-p030-HP-G` | 129001:60/60 129002:60/60 129003:0/60 129004:0/60 129005:60/60 129006:60/60 129007:0/60 129008:60/60 |
| L124 | `c1-p030-PW-G` | 129001:0/0 129002:0/26 129003:0/22 129004:0/10 129005:28/0 129006:0/7 129007:0/0 129008:0/0 |
| L132 | `c1-p080-U-G` | 129001:60/60 129002:3/0 129003:10/0 129004:0/60 129005:60/60 129006:0/60 129007:5/60 129008:60/0 |
| L140 | `c1-p080-HP-G` | 129001:60/60 129002:60/60 129003:0/59 129004:0/60 129005:60/60 129006:60/60 129007:0/60 129008:14/60 |
| L149 | `c1-p080-PW-G` | 129001:0/0 129002:0/0 129003:0/0 129004:0/0 129005:13/0 129006:0/0 129007:0/0 129008:0/0 |
| L157 | `c2-p010-U-G` | 129001:60/60 129002:60/60 129003:0/60 129004:60/60 129005:60/60 129006:0/60 129007:0/60 129008:60/60 |
| L165 | `c2-p010-HP-G` | 129001:60/60 129002:60/60 129003:21/60 129004:60/60 129005:60/60 129006:3/60 129007:0/60 129008:60/60 |
| L173 | `c2-p010-PW-G` | 129001:0/0 129002:1/29 129003:0/5 129004:0/47 129005:60/11 129006:0/0 129007:0/38 129008:0/48 |
| L183 | `c2-p030-U-G` | 129001:60/60 129002:60/60 129003:9/60 129004:60/60 129005:60/60 129006:60/60 129007:1/60 129008:60/60 |
| L192 | `c2-p030-HP-G` | 129001:60/60 129002:60/60 129003:0/60 129004:6/60 129005:60/60 129006:0/60 129007:0/60 129008:2/60 |
| L200 | `c2-p030-PW-G` | 129001:0/0 129002:0/0 129003:0/0 129004:0/0 129005:60/0 129006:0/0 129007:0/0 129008:0/0 |
| L208 | `c2-p080-U-G` | 129001:60/0 129002:60/0 129003:5/0 129004:0/8 129005:60/0 129006:1/0 129007:5/0 129008:3/0 |
| L216 | `c2-p080-HP-G` | 129001:60/0 129002:60/0 129003:0/0 129004:60/16 129005:60/0 129006:0/20 129007:0/28 129008:0/48 |
| L224 | `c2-p080-PW-G` | 129001:0/0 129002:0/0 129003:0/0 129004:0/0 129005:0/0 129006:0/0 129007:0/0 129008:0/0 |
| L232 | `c1-p010-U-L` | 129001:60/60 129002:60/60 129003:0/60 129004:60/60 129005:60/60 129006:31/60 129007:60/60 129008:60/60 |
| L240 | `c1-p010-HP-L` | 129001:60/60 129002:60/60 129003:7/60 129004:60/60 129005:60/60 129006:0/60 129007:0/60 129008:60/60 |
| L248 | `c1-p010-PW-L` | 129001:10/46 129002:0/37 129003:0/44 129004:0/34 129005:49/57 129006:0/37 129007:0/57 129008:0/46 |
| L258 | `c1-p030-U-L` | 129001:60/60 129002:60/60 129003:7/60 129004:60/60 129005:60/60 129006:60/60 129007:60/60 129008:60/60 |
| L266 | `c1-p030-HP-L` | 129001:60/60 129002:60/60 129003:60/60 129004:10/60 129005:60/60 129006:60/60 129007:0/60 129008:60/60 |
| L274 | `c1-p030-PW-L` | 129001:18/0 129002:0/0 129003:0/0 129004:0/0 129005:0/1 129006:0/0 129007:0/0 129008:0/0 |
| L282 | `c1-p080-U-L` | 129001:60/41 129002:60/0 129003:5/24 129004:60/60 129005:60/60 129006:15/0 129007:0/1 129008:60/60 |
| L291 | `c1-p080-HP-L` | 129001:60/1 129002:60/7 129003:11/58 129004:0/60 129005:60/60 129006:23/0 129007:0/26 129008:60/60 |
| L300 | `c1-p080-PW-L` | 129001:0/0 129002:0/0 129003:0/0 129004:0/0 129005:0/0 129006:0/0 129007:0/0 129008:0/0 |

**Per-seed detail.** Per-birth income (both readings), flow variants (last_score, survivors, p0), and the S lines per
fauna are printed under each point, at L7–L306:
- the S lines give alive at 299, births and deaths (starved and aged) in 240–299, extinct seeds and their seasons,
  `mean_lifetime_score`, and food, work and path per member-season;
- the share-of-the-living variant and the N runs' y′ appear where M or N ran.

## 4. The share layer

*Under the committed rule; among holistic and designed stream draws (founders and their early history) that establish
at W118-b; provisional.*

- **What is NOT RUN, and why.** N ran at 4 points only, under the gate (`lanes/1-MN/gate_table.txt`): `c0-p030-PW-G`,
  `c1-p010-PW-G`, `c2-p010-PW-G` and `c1-p010-PW-L`.
  - At every other point with no N arm, the share call is **NOT RUN** (14 points: 11 G, 3 L; L376–L377).
  - The anchor `c1-p030-U-L` reads **RBT-118 (not available)** (L257). `c1-p030-PW-G`, the other Stage-1 anchor, is
    settled as NEITHER by §6.1 item 1 first (L123).
  - All 4 N points are settled by §6.1 item 1 (EXCLUDED-H; L47, L97, L172, L247), so they enter no share family. The
    share WIN/TIE/CONTINGENT families hold 0 points (L309; O-22).
- **K2** (L311–L315):
  - Pooled over the 7 N runs: **FAIL**, so "the share layer is VOID for the stage" (mean −0.125, t −1.13, p 0.3007).
  - Per point, all four FAIL: `c0-p030-PW-G` (2 runs, mean +0.173), `c1-p010-PW-G` (1 run, −0.231), `c1-p010-PW-L`
    (2 runs, −0.193) and `c2-p010-PW-G` (2 runs, −0.301).
  - By plan §2.8, at Stage 1 this **changes no call**: every N point is settled by item 1 before VOID (item 3), and
    there is no other share call.
- **The N runs' y′** (descriptive):
  - `c0-p030-PW-G`: 129001 −0.067, 129005 +0.412 (L56);
  - `c1-p010-PW-G`: 129005 −0.231 (L106);
  - `c2-p010-PW-G`: 129002 −0.561, 129005 −0.041 (L181);
  - `c1-p010-PW-L`: 129001 −0.179, 129005 −0.207 (L256).
- **CONTINGENT's df.** The holistic-null pool gives σ̂² 0.0576 at df 2. The conventional-null pool gives σ̂² "--" at
  df 0. CONTINGENT is **not callable** (df 2 < 12) (L316–L318).
- **RESOLVING** at the 4 N points: False at each (L319–L322). This is descriptive, because each body call is already
  settled.
- **Every point is labelled PW.** K1 was never tested on PW terrain (O-2; I-14). That qualifies all four N points and
  every PW M row. Nothing is VOIDed for it.
- **y′ at M points without N** (descriptive; never tested; ruling item 4(a)):
  - `c1-p080-HP-G` +0.319 (L139);
  - `c2-p030-U-G` −0.176 at **M 7 of 8 (1 CRASHED)** (L182, L334);
  - `c1-p080-U-L` +0.345 (L281);
  - `c1-p080-HP-L` +0.198 (L290);
  - `c0-p010-PW-G` −0.500 (L22). `c0-p010-PW-G` has an M arm and no N.
- **The bound under arbitrary missingness** at `c2-p030-U-G`, on the 8-seed mean y′: **[−0.216, −0.091]**, with s₀
  0.500 from 129001's ckpt60, under the empty-world convention of plan §3.3 (L335). Income flow has no logical bound,
  and no min/max-of-7 substitute is printed (L336).

## 5. The one-world column and the interference table

*Among holistic and designed stream draws (founders and their early history) that establish at W118-b. Descriptive.*
Interference is M − S per fauna, with S paired on the M arm's completed seeds (L324–L333).

| point | M n | M flow H | M flow D | interference H (n) | interference D (n) | line |
|---|---|---|---|---|---|---|
| `c0-p010-PW-G` | 1 of 1 | -- | +0.415 | -- (0) | +0.019 (1) | L325 |
| `c0-p030-PW-G` | 2 of 2 | -- | +0.110 | -- (0) | -0.008 (1) | L326 |
| `c1-p010-PW-G` | 1 of 1 | +0.374 | -- | -0.014 (1) | -- (0) | L327 |
| `c1-p080-HP-G` | 5 of 5 | +0.788 | +1.738 | -0.116 (5) | +0.636 (5) | L328 |
| `c2-p010-PW-G` | 2 of 2 | +0.348 | +0.204 | -- (0) | -- (0) | L329 |
| `c2-p030-U-G` | 7 of 8 (1 CRASHED) | +0.746 | +0.679 | -0.007 (5) | -0.003 (5) | L330 |
| `c1-p010-PW-L` | 2 of 2 | +0.363 | +0.221 | -0.011 (1) | +0.022 (2) | L331 |
| `c1-p080-U-L` | 5 of 5 | +0.825 | +0.527 | +0.012 (4) | +0.018 (2) | L332 |
| `c1-p080-HP-L` | 5 of 5 | +0.842 | +0.522 | -0.101 (3) | -0.053 (1) | L333 |

M6 concordance: **no decided share call** (L379).

## 6. M2 / T1–T3, the share model, M3 and M7

*Among holistic and designed stream draws (founders and their early history) that establish at W118-b. The
coefficients are final values (plan §6, NOTE 10). Holm is provisional, with T4 pending.*

**M2, income (registered Stage-1 fit)** (L402–L413):
- **The fit.** 15 habitable points, 100 seeds.
- **Support rule.** Dropped term: **L = PW** (no habitable PW point). Status: **TESTABLE**.
- **Coefficients**, with 95% Wald CIs, coded c − 1 and log(p/0.03) (O-21):

  | term | estimate [95% CI] |
  |---|---|
  | intercept | +0.1303 [−0.1325, +0.3932] |
  | c | +0.5022 [+0.2800, +0.7243] |
  | log p | −0.0925 [−0.3222, +0.1372] |
  | L = HP | −0.3379 [−0.5849, −0.0909] |
  | s = G | −0.3874 [−0.6580, −0.1168] |
  | c × log p | +0.2322 [−0.0435, +0.5080] |

- **The tests, Holm at α = 0.05 with T4 NOT MEASURED at p = 1** ("T1–T3 Holm with T4 pending"):
  - **T1** (Wald χ²): stat 69.704, p 1.181e-13, **REJECTED**;
  - **T2** (clutter, z): stat 4.431, p 9.393e-06, **REJECTED**;
  - **T3** (log price, z): stat −0.789, p 0.43, not rejected.
- **T1 state for §8: rejects** (L413).

**The share model** (secondary; descriptive at Stage 1). It uses points with an M arm, with census g0 as a covariate,
and the CRASHED point at n = 7. Status TESTABLE, nothing dropped. Share Wald T1, net of g0 and outside Holm: χ² 2.056,
df 6, p 0.9145 (L414).

**M3 break-evens** (per-row OLS of x on p, Fieller 95%) (L415–L420):

| row (c, L, s) | p* | Fieller 95% |
|---|---|---|
| (0, HP, G) | −0.0794 | bounded [−4.0249, −0.0164] |
| (0, U, G) | −0.0519 | bounded [−0.1730, −0.0162] |
| (1, HP, L) | 0.0165 | whole line |
| (1, U, G) | −0.0095 | whole line |
| (1, U, L) | 0.0137 | whole line |

No M3 interval lies inside [0.01, 0.08], so no single call is corroborated by M3 for a counting set (§9).

**M7, the monotonicity of x̄** (L380–L401):
- The only row with more than one sign change is **price row c1 U L, 2 sign changes [+0.001 −0.003 +0.256]** (L385).
- Rows with exactly one sign change:
  - price c1 U G (L384);
  - price c1 HP L (L387);
  - clutter p010 U G (L393);
  - clutter p030 U G (L396);
  - clutter p080 U G (L399).
- PW rows have gaps ("--"), as printed.

**Cross-point correlation of x:** mean 0.262, max 1.000, over 202 pairs (L310). The mean is ≤ 0.3, so no BY column is
triggered.

## 7. The R-A and R-B lists

**R-A** (≤ 16; the G block first, then L; L428–L441). Fewer than 16 G pairs fire, so L pairs refine (NOTE 12). Every
pair is on the income layer, because no point is RESOLVING.

| midpoint | source | pair | sign | calls | \|Δt\| | line |
|---|---|---|---|---|---|---|
| `c05-p080-U-G` | R-A | c0-p080-U-G / c1-p080-U-G | True | True | 15.537 | L429 |
| `c15-p010-U-G` | R-A | c1-p010-U-G / c2-p010-U-G | True | False | 3.250 | L430 |
| `c1-p053-U-G` | R-A | c1-p030-U-G / c1-p080-U-G | True | False | 6.717 | L431 |
| `c15-p030-U-G` | R-A | c1-p030-U-G / c2-p030-U-G | True | False | 3.386 | L432 |
| `c1-p018-U-L` | R-A | c1-p010-U-L / c1-p030-U-L | True | False | 0.039 | L433 |
| `c1-p018-HP-L` | R-A | c1-p010-HP-L / c1-p030-HP-L | True | False | 1.619 | L434 |
| `c1-p018-PW-L` | R-A | c1-p010-PW-L / c1-p030-PW-L | False | True | -- | L435 |
| `c1-p053-U-L` | R-A | c1-p030-U-L / c1-p080-U-L | True | False | 2.957 | L436 |
| `c0-p018-HP-G` | C1 | c0-p010-HP-G / c0-p030-HP-G | False | False | 4.585 | L437 |
| `c1-p018-U-G` | C1 | c1-p010-U-G / c1-p030-U-G | False | False | 0.583 | L438 |
| `c2-p053-HP-G` | C1 | c2-p030-HP-G / c2-p080-HP-G | False | False | -- | L439 |
| `c05-p030-U-G` | C1 | c0-p030-U-G / c1-p030-U-G | False | False | 4.820 | L440 |

**Selected (12), in rank order** (L441): `c05-p080-U-G`, `c1-p053-U-G`, `c05-p030-U-G`, `c0-p018-HP-G`,
`c15-p030-U-G`, `c15-p010-U-G`, `c1-p018-U-G`, `c2-p053-HP-G`, `c1-p053-U-L`, `c1-p018-HP-L`, `c1-p018-U-L`,
`c1-p018-PW-L`.

The 7 C1 candidates (O-23) are all included. `c1-p018-PW-L`, `c1-p053-U-G` and `c15-p030-U-G` were already selected by
R-A.

**R-B** (COORD-RULING-512 R4, **DATA-INFORMED**): **9 points**. S arms 140 / 262 core-h. **Needs its own owner GO; no
spending is authorized** (L442). Ranked by conditional power on the income t (L443–L451):

| rank | point | CP |
|---|---|---|
| 1 | `c0-p010-HP-G` | 0.807 |
| 2 | `c1-p010-HP-G` | 0.806 |
| 3 | `c2-p030-U-G` | 0.800 |
| 4 | `c2-p010-HP-G` | 0.652 |
| 5 | `c1-p030-U-G` | 0.376 |
| 6 | `c1-p030-HP-L` | 0.253 |
| 7 | `c1-p010-U-G` | 0.097 |
| 8 | `c1-p010-HP-L` | 0.046 |
| 9 | `c1-p010-U-L` | 0.006 |

- **The literal list** (body call UNDECIDED or CONTINGENT; not the registered reading) is **empty** (L452).
- The anchor `c1-p030-U-L` is excluded (R4 (ii)).
- If `c2-p030-U-G` is extended, 129001's M stays CRASHED at 15 of 16 (ruling item 2).

## 8. The provisional §8 evaluation

**PROVISIONAL: Stage-1 calls only; not a verdict** (COORD-RULING-512 R1 + R2 + R3) (L422–L426):

- **Registered reading: EARNINGS DEPEND** (L423). *Among holistic and designed stream draws (founders and their early
  history) that establish at W118-b; earns, not persists; provisional.*
  - **T1 rejects** (Holm; L410, L413).
  - **EARNS-D forms a counting set.** There are 6 EARNS-D calls: `c0-p010-U-G`, `c0-p030-U-G`, `c0-p030-HP-G`,
    `c0-p080-U-G`, `c0-p080-HP-G` and `c1-p030-HP-G` (L6, L31, L39, L57, L65, L115).
  - **EARNS-H forms a counting set.** There are 2 EARNS-H calls: `c1-p010-PW-L` (L247) and `c1-p080-HP-L` (L290).
  - Under **R1**, both EARNS-H calls count, although their points are not habitable: `c1-p010-PW-L` is EXCLUDED-H and
    `c1-p080-HP-L` is PARTIAL-D.
- **NON-REGISTERED, descriptive only** (EARNS at habitable points only): **DEPENDS ONLY THROUGH HABITABILITY (D)**
  (L424). This line decides nothing (R1).
- **NON-REGISTERED, descriptive only** (verdict 5 ignoring EARNS-TIE): EARNINGS DEPEND (L425). No EARNS-TIE occurs at
  Stage 1, so R2 is not engaged.
- **Not measured or not evaluated.** Perception verdicts are NOT MEASURED. LEVER is not evaluated, and every EARNS
  call is counted with that caveat (L426).
- **MARGINAL** is on all 8 EARNS calls (L6, L31, L39, L57, L65, L115, L247, L290).

**How far the plan's calls allow this to be read.**
- The registered provisional headline rests on the two EARNS-H calls. Both are at non-habitable points, with small
  income n: 2 of 8 at `c1-p010-PW-L` and 3 of 8 at `c1-p080-HP-L`.
- Under the non-registered habitable-only reading the headline would differ (L424). The plan ruled that reading out
  (R1).
- §8 reads the final map. The final BH over all points after Stage 2 (with R-B's combined p-values) can change these
  calls.

## 9. Founding beside the census, the census layer at unrun points, and the §12 scorecard

**Founding beside the census** (AMENDMENT-FOUNDING T3; L454–L490). The census's FOUNDING-FAIL flags (unscreened) are
printed beside the Stage-1 founding (screened), i.e. the seeds alive at 59:

```
## founding beside the census (AMENDMENT-FOUNDING T3): census FOUNDING-FAIL (unscreened) | Stage 1 alive at 59 (screened)
  c0-p010-U-G    census FF H yes D no | Stage 1 H alive at 59 on 7 of 8, D on 8 of 8
  c0-p010-HP-G   census FF H yes D no | Stage 1 H alive at 59 on 7 of 8, D on 8 of 8
  c0-p010-PW-G   census FF H yes D no | Stage 1 H alive at 59 on 1 of 8, D on 8 of 8
  c0-p030-U-G    census FF H yes D no | Stage 1 H alive at 59 on 7 of 8, D on 8 of 8
  c0-p030-HP-G   census FF H yes D no | Stage 1 H alive at 59 on 7 of 8, D on 8 of 8
  c0-p030-PW-G   census FF H yes D no | Stage 1 H alive at 59 on 2 of 8, D on 8 of 8
  c0-p080-U-G    census FF H yes D no | Stage 1 H alive at 59 on 7 of 8, D on 8 of 8
  c0-p080-HP-G   census FF H yes D no | Stage 1 H alive at 59 on 7 of 8, D on 8 of 8
  c0-p080-PW-G   census FF H yes D no | Stage 1 H alive at 59 on 1 of 8, D on 4 of 8
  c1-p010-U-G    census FF H yes D no | Stage 1 H alive at 59 on 7 of 8, D on 8 of 8
  c1-p010-HP-G   census FF H yes D no | Stage 1 H alive at 59 on 6 of 8, D on 8 of 8
  c1-p010-PW-G   census FF H yes D no | Stage 1 H alive at 59 on 1 of 8, D on 8 of 8
  c1-p030-U-G    census FF H yes D no | Stage 1 H alive at 59 on 8 of 8, D on 8 of 8
  c1-p030-HP-G   census FF H yes D no | Stage 1 H alive at 59 on 5 of 8, D on 8 of 8
  c1-p030-PW-G   census FF H yes D no | Stage 1 H alive at 59 on 1 of 8, D on 4 of 8
  c1-p080-U-G    census FF H yes D yes | Stage 1 H alive at 59 on 6 of 8, D on 5 of 8
  c1-p080-HP-G   census FF H yes D no | Stage 1 H alive at 59 on 5 of 8, D on 8 of 8
  c1-p080-PW-G   census FF H yes D yes | Stage 1 H alive at 59 on 1 of 8, D on 0 of 8
  c2-p010-U-G    census FF H yes D no | Stage 1 H alive at 59 on 5 of 8, D on 8 of 8
  c2-p010-HP-G   census FF H yes D no | Stage 1 H alive at 59 on 7 of 8, D on 8 of 8
  c2-p010-PW-G   census FF H yes D no | Stage 1 H alive at 59 on 2 of 8, D on 6 of 8
  c2-p030-U-G    census FF H yes D no | Stage 1 H alive at 59 on 8 of 8, D on 8 of 8
  c2-p030-HP-G   census FF H yes D no | Stage 1 H alive at 59 on 5 of 8, D on 8 of 8
  c2-p030-PW-G   census FF H yes D yes | Stage 1 H alive at 59 on 1 of 8, D on 0 of 8
  c2-p080-U-G    census FF H yes D yes | Stage 1 H alive at 59 on 7 of 8, D on 1 of 8
  c2-p080-HP-G   census FF H yes D yes | Stage 1 H alive at 59 on 4 of 8, D on 4 of 8
  c2-p080-PW-G   census FF H yes D yes | Stage 1 H alive at 59 on 0 of 8, D on 0 of 8
  c1-p010-U-L    census FF H yes D no | Stage 1 H alive at 59 on 7 of 8, D on 8 of 8
  c1-p010-HP-L   census FF H yes D no | Stage 1 H alive at 59 on 6 of 8, D on 8 of 8
  c1-p010-PW-L   census FF H yes D no | Stage 1 H alive at 59 on 2 of 8, D on 8 of 8
  c1-p030-U-L    census FF H yes D no | Stage 1 H alive at 59 on 8 of 8, D on 8 of 8
  c1-p030-HP-L   census FF H yes D no | Stage 1 H alive at 59 on 7 of 8, D on 8 of 8
  c1-p030-PW-L   census FF H yes D yes | Stage 1 H alive at 59 on 1 of 8, D on 1 of 8
  c1-p080-U-L    census FF H yes D no | Stage 1 H alive at 59 on 7 of 8, D on 6 of 8
  c1-p080-HP-L   census FF H yes D no | Stage 1 H alive at 59 on 6 of 8, D on 7 of 8
  c1-p080-PW-L   census FF H yes D yes | Stage 1 H alive at 59 on 0 of 8, D on 0 of 8
```

**Census layer at the 114 points never run at Stage 1** (L491–L605). It gives FOUNDING-FAIL per fauna, saturation over
30–59 and census g0, read from the committed census readout. It is the only habitability proxy there, with its
60-season limit. Not reproduced here; see `stage1_readout.txt` L492–L605.

**§12 scorecard** (provisional where §8 is) (L607–L620):

| prediction | reading | line |
|---|---|---|
| T2 (clutter) > 0 | AS PREDICTED (z +4.43) | L608 |
| T3 (price) > 0 | NOT SHOWN (z −0.79) | L609 |
| M3 p* > 0.018 at c = 1, rows (1, HP, L), (1, U, G), (1, U, L) | NOT SHOWN (Fieller whole line), each | L610–L612 |
| M3 p* > 0.053 at c = 0, row (0, HP, G) | OPPOSITE (p* −0.0794 [−4.0249, −0.0164]) | L613 |
| M3 p* > 0.053 at c = 0, row (0, U, G) | OPPOSITE (p* −0.0519 [−0.1730, −0.0162]) | L614 |
| EARNS-D on flat ground at p ≤ 0.03 | AS PREDICTED (3 EARNS-D, 0 EARNS-H of 6 points) | L615 |
| EARNS-H at c ≥ 1, p ≥ 0.03 | NOT SHOWN (1 EARNS-H, 1 EARNS-D of 18 points) | L616 |
| share NOT RUN or SATURATED at most points, RESOLVING at 0–2 | NOT SHOWN (15 of 36; RESOLVING 0) | L617 |
| EXCLUDED-D or PARTIAL-H at some p = 0.08, c ≥ 1 point | AS PREDICTED (`c1-p080-U-G`, `c2-p080-U-G`, `c2-p080-HP-G`, `c1-p080-U-L`) | L618 |
| perception (item 4), retention (item 6) | NOT MEASURED | L619 |
| the framing, EARNINGS DEPEND (item 5) | AS PREDICTED (provisional: EARNINGS DEPEND) | L620 |

## 10. The regime table (every S and M arm)

Columns: regime.py window-local saturation / viability / alive, as means over seeds, per 60-season window. `h` is
holistic, `c` is conventional, and the number is the window start. Descriptive. Copied verbatim from L338–L373:

```
## regime (regime.py; window-local saturation / viability / alive, mean over seeds; descriptive)
  c0-p010-U-G S (n 7): h0: 4.57/0.99/51.3  h60: 3.91/1.41/60.0  h120: 4.19/1.91/60.0  h180: 4.11/1.55/60.0  h240: 3.76/-0.96/60.0  c0: 4.12/2.57/60.0  c60: 4.52/3.54/60.0  c120: 4.80/3.48/60.0  c180: 4.97/3.77/60.0  c240: 5.06/-1.49/60.0
  c0-p010-HP-G S (n 6): h0: 5.62/0.89/53.7  h60: 5.22/1.38/60.0  h120: 5.64/1.29/60.0  h180: 5.20/1.73/60.0  h240: 5.82/-0.97/60.0  c0: 6.63/3.68/60.0  c60: 7.56/3.67/60.0  c120: 7.90/4.40/60.0  c180: 8.35/4.64/60.0  c240: 8.77/-1.61/60.0
  c0-p010-PW-G S (n 1): h0: 3.98/-0.68/50.9  h60: 1.82/-0.73/60.0  h120: 2.26/-0.75/60.0  h180: 2.10/-0.69/60.0  h240: 1.75/-0.98/60.0  c0: 2.87/-1.06/59.9  c60: 1.80/-1.04/60.0  c120: 2.03/-1.11/60.0  c180: 1.83/-0.98/60.0  c240: 1.79/-1.47/60.0
  c0-p010-PW-G M (n 1): h0: 3.98/-0.72/50.9  h60: 0.94/-0.89/35.4  h120: 0.62/-1.02/5.2  h180: 0.92/-1.20/1.4  h240: --/--/--  c0: 2.87/-1.02/59.9  c60: 2.21/-1.00/84.6  c120: 2.08/-1.02/114.8  c180: 1.74/-0.95/119.6  c240: 2.00/-1.46/120.0
  c0-p030-U-G S (n 7): h0: 3.81/0.01/42.0  h60: 2.74/0.39/56.9  h120: 2.84/0.65/60.0  h180: 3.07/0.71/60.0  h240: 3.14/-0.97/60.0  c0: 4.47/1.33/60.0  c60: 5.13/2.26/60.0  c120: 5.48/3.05/60.0  c180: 5.40/2.92/60.0  c240: 5.26/-2.47/60.0
  c0-p030-HP-G S (n 7): h0: 5.32/-0.03/41.2  h60: 4.47/0.35/53.0  h120: 4.58/0.50/56.5  h180: 4.10/0.60/60.0  h240: 4.08/-1.04/60.0  c0: 7.26/1.30/60.0  c60: 8.23/2.38/60.0  c120: 9.13/3.22/60.0  c180: 9.64/3.59/60.0  c240: 9.29/-2.71/60.0
  c0-p030-PW-G S (n 1): h0: 6.25/-0.87/30.3  h60: 4.69/-0.86/53.4  h120: 2.78/-0.85/60.0  h180: 2.51/-0.89/60.0  h240: 2.45/-1.01/60.0  c0: 6.11/-2.19/37.3  c60: 6.27/-2.13/53.0  c120: 4.18/-2.04/59.4  c180: 4.79/-2.18/57.3  c240: 6.12/-2.46/50.5
  c0-p030-PW-G M (n 2): h0: 5.55/-0.87/22.9  h60: 2.69/-1.15/10.1  h120: --/--/--  h180: --/--/--  h240: --/--/--  c0: 6.03/-2.28/38.0  c60: 5.84/-2.40/98.0  c120: 5.74/-2.51/98.8  c180: 5.93/-2.41/101.1  c240: 5.90/-2.69/97.5
  c0-p080-U-G S (n 7): h0: 3.77/0.35/47.4  h60: 2.84/0.52/60.0  h120: 2.86/0.71/60.0  h180: 3.08/0.70/60.0  h240: 3.05/-1.00/60.0  c0: 5.27/-1.42/58.5  c60: 5.56/-0.50/60.0  c120: 6.18/0.02/60.0  c180: 6.47/0.97/60.0  c240: 6.52/-4.31/60.0
  c0-p080-HP-G S (n 7): h0: 5.06/0.15/46.9  h60: 4.25/0.32/56.6  h120: 3.88/0.62/60.0  h180: 4.70/0.86/60.0  h240: 4.46/-1.15/60.0  c0: 9.21/-2.64/57.8  c60: 9.77/-1.54/60.0  c120: 10.35/-1.14/60.0  c180: 10.82/-0.00/60.0  c240: 11.09/-6.10/60.0
  c1-p010-U-G S (n 6): h0: 3.73/0.38/46.1  h60: 3.39/0.64/53.7  h120: 2.91/0.97/59.6  h180: 2.96/1.18/60.0  h240: 3.25/-0.93/60.0  c0: 2.82/1.44/60.0  c60: 2.93/1.73/60.0  c120: 3.14/1.75/60.0  c180: 3.27/2.13/60.0  c240: 3.32/-1.30/60.0
  c1-p010-HP-G S (n 6): h0: 5.47/0.44/47.0  h60: 4.01/0.66/59.5  h120: 4.01/0.78/60.0  h180: 4.37/1.08/60.0  h240: 4.34/-0.96/60.0  c0: 4.12/1.10/60.0  c60: 4.18/1.22/60.0  c120: 4.69/1.87/60.0  c180: 4.84/2.06/60.0  c240: 5.03/-1.52/60.0
  c1-p010-PW-G S (n 1): h0: 3.39/-0.71/53.4  h60: 2.03/-0.70/60.0  h120: 1.71/-0.58/60.0  h180: 1.63/-0.66/60.0  h240: 1.81/-0.92/60.0  c0: 5.13/-1.26/44.3  c60: 5.64/-1.28/55.6  c120: 5.09/-1.34/56.5  c180: 5.65/-1.37/53.6  c240: 5.61/-1.55/48.4
  c1-p010-PW-G M (n 1): h0: 3.39/-0.69/53.4  h60: 2.26/-0.63/96.5  h120: 1.75/-0.66/111.7  h180: 1.88/-0.66/119.7  h240: 1.77/-0.94/120.0  c0: 5.13/-1.25/44.3  c60: 2.03/-1.39/23.4  c120: 1.00/-1.31/8.3  c180: -1.03/-0.99/1.7  c240: --/--/--
  c1-p030-U-G S (n 7): h0: 3.50/0.22/44.9  h60: 3.18/0.49/52.4  h120: 3.38/0.67/52.0  h180: 3.34/0.56/52.0  h240: 3.14/-1.00/51.6  c0: 2.95/0.03/60.0  c60: 3.00/0.34/60.0  c120: 2.98/0.38/60.0  c180: 3.21/0.76/60.0  c240: 3.20/-2.23/60.0
  c1-p030-HP-G S (n 5): h0: 4.79/0.19/46.5  h60: 3.70/0.31/60.0  h120: 3.61/0.36/60.0  h180: 3.85/0.57/60.0  h240: 3.65/-1.01/60.0  c0: 4.79/-0.40/60.0  c60: 5.08/-0.05/60.0  c120: 5.48/0.17/60.0  c180: 5.79/0.43/60.0  c240: 5.95/-2.93/60.0
  c1-p080-U-G S (n 2): h0: 3.56/0.00/52.3  h60: 3.04/0.39/60.0  h120: 3.14/0.92/60.0  h180: 3.13/1.02/60.0  h240: 3.54/-0.99/60.0  c0: 3.46/-3.23/47.0  c60: 2.29/-2.58/60.0  c120: 2.59/-2.20/60.0  c180: 2.81/-2.37/60.0  c240: 2.82/-3.71/60.0
  c1-p080-HP-G S (n 5): h0: 5.32/-0.43/37.0  h60: 3.83/-0.28/55.3  h120: 3.27/-0.07/60.0  h180: 3.31/-0.01/60.0  h240: 3.66/-1.07/60.0  c0: 6.68/-4.31/44.3  c60: 4.98/-3.84/60.0  c120: 5.10/-3.71/60.0  c180: 5.44/-3.42/60.0  c240: 4.80/-5.23/60.0
  c1-p080-HP-G M (n 5): h0: 5.32/-0.40/37.0  h60: 3.35/-0.15/52.7  h120: 3.08/-0.23/74.9  h180: 3.25/-0.04/86.9  h240: 3.13/-1.13/90.8  c0: 6.68/-4.32/44.3  c60: 4.80/-3.89/67.2  c120: 4.68/-3.67/45.1  c180: 5.43/-3.53/33.1  c240: 7.14/-6.43/29.6
  c2-p010-U-G S (n 5): h0: 3.60/0.48/54.2  h60: 3.32/0.79/60.0  h120: 3.21/1.11/60.0  h180: 3.43/1.23/60.0  h240: 3.30/-0.97/60.0  c0: 2.27/0.97/60.0  c60: 2.33/1.17/60.0  c120: 2.41/1.20/60.0  c180: 2.44/1.02/60.0  c240: 2.35/-1.35/60.0
  c2-p010-HP-G S (n 7): h0: 5.10/0.13/42.8  h60: 4.21/0.41/53.8  h120: 3.50/0.56/60.0  h180: 3.66/0.63/60.0  h240: 3.56/-0.98/60.0  c0: 3.53/0.44/60.0  c60: 3.49/0.92/60.0  c120: 3.79/1.13/60.0  c180: 4.19/1.19/60.0  c240: 4.51/-1.50/60.0
  c2-p010-PW-G M (n 2): h0: 4.23/-0.79/32.9  h60: 2.28/-0.71/57.6  h120: 2.11/-0.74/120.0  h180: 1.78/-0.64/120.0  h240: 1.69/-0.94/120.0  c0: 5.25/-1.29/25.3  c60: 4.19/-1.36/20.5  c120: 5.93/-1.31/62.1  c180: 5.60/-1.33/93.3  c240: 5.71/-1.48/96.6
  c2-p030-U-G S (n 6): h0: 3.39/0.17/48.7  h60: 2.83/0.32/60.0  h120: 2.54/0.32/60.0  h180: 2.58/0.47/60.0  h240: 2.60/-0.99/60.0  c0: 2.15/-0.74/60.0  c60: 2.02/-0.45/60.0  c120: 2.07/-0.37/60.0  c180: 2.08/-0.26/60.0  c240: 2.14/-2.21/60.0
  c2-p030-U-G M (n 7): h0: 3.50/-0.06/38.9  h60: 2.44/-0.02/46.7  h120: 2.85/0.43/53.7  h180: 2.66/0.51/43.9  h240: 2.63/-0.94/34.1  c0: 2.14/-0.76/60.0  c60: 2.03/-0.32/73.1  c120: 2.10/-0.20/81.7  c180: 2.23/-0.04/88.6  c240: 2.20/-2.10/95.6
  c2-p030-HP-G S (n 5): h0: 4.86/-0.24/34.1  h60: 4.31/0.45/47.2  h120: 3.44/0.48/60.0  h180: 3.49/0.32/60.0  h240: 3.75/-1.03/60.0  c0: 4.07/-1.11/60.0  c60: 3.54/-0.97/60.0  c120: 4.15/-0.74/60.0  c180: 4.06/-0.54/60.0  c240: 4.46/-2.68/60.0
  c1-p010-U-L S (n 7): h0: 3.86/0.51/47.5  h60: 3.11/0.83/59.8  h120: 3.20/1.00/60.0  h180: 3.27/1.14/60.0  h240: 3.41/-0.96/60.0  c0: 2.77/1.38/60.0  c60: 2.87/1.67/60.0  c120: 3.02/2.01/60.0  c180: 3.13/1.89/60.0  c240: 3.20/-1.35/60.0
  c1-p010-HP-L S (n 6): h0: 4.91/0.32/45.3  h60: 4.49/0.60/56.9  h120: 4.27/0.83/60.0  h180: 4.26/1.06/60.0  h240: 4.26/-0.99/60.0  c0: 4.02/1.12/60.0  c60: 3.98/1.33/60.0  c120: 4.23/1.41/60.0  c180: 4.25/1.27/60.0  c240: 4.17/-1.53/60.0
  c1-p010-PW-L S (n 2): h0: 5.56/-0.76/27.4  h60: 4.58/-0.75/40.0  h120: 3.82/-0.78/53.5  h180: 2.10/-0.72/60.0  h240: 2.03/-0.94/60.0  c0: 5.41/-1.18/48.6  c60: 5.16/-1.19/54.1  c120: 5.54/-1.16/54.6  c180: 4.52/-1.17/58.6  c240: 5.34/-1.26/53.4
  c1-p010-PW-L M (n 2): h0: 5.56/-0.78/27.4  h60: 4.50/-0.87/29.8  h120: 3.26/-0.77/59.6  h180: 3.07/-0.72/76.4  h240: 2.23/-0.95/96.3  c0: 5.41/-1.17/48.6  c60: 5.04/-1.21/86.9  c120: 3.38/-1.10/90.2  c180: 2.80/-1.13/81.8  c240: 2.45/-1.29/71.8
  c1-p030-U-L S (n 8): h0: 3.65/0.19/44.7  h60: 3.13/0.40/54.9  h120: 2.81/0.56/59.9  h180: 2.83/0.74/60.0  h240: 2.90/-1.00/60.0  c0: 2.54/-0.10/60.0  c60: 2.55/0.08/60.0  c120: 2.69/0.38/60.0  c180: 2.80/0.39/60.0  c240: 2.72/-2.27/60.0
  c1-p030-HP-L S (n 6): h0: 5.22/-0.11/48.1  h60: 3.60/0.21/60.0  h120: 4.14/0.82/60.0  h180: 4.24/0.78/60.0  h240: 4.49/-1.09/60.0  c0: 3.72/-1.13/60.0  c60: 3.89/-0.74/60.0  c120: 4.16/-0.47/60.0  c180: 4.05/-0.48/60.0  c240: 3.71/-2.62/60.0
  c1-p080-U-L S (n 5): h0: 3.31/0.04/45.6  h60: 3.16/0.35/50.8  h120: 2.67/0.18/58.3  h180: 2.46/0.35/60.0  h240: 2.48/-1.10/60.0  c0: 4.33/-3.00/31.3  c60: 3.22/-2.81/55.6  c120: 1.83/-2.59/60.0  c180: 1.86/-2.47/60.0  c240: 1.82/-3.58/60.0
  c1-p080-U-L M (n 5): h0: 3.31/0.04/45.6  h60: 3.00/0.33/68.9  h120: 2.90/0.57/109.2  h180: 2.75/0.72/118.8  h240: 2.84/-1.09/119.8  c0: 4.33/-3.06/31.3  c60: 2.37/-2.72/35.7  c120: 1.55/-2.50/32.3  c180: 1.83/-2.48/31.8  c240: 1.53/-3.30/60.5
  c1-p080-HP-L S (n 3): h0: 5.09/-0.05/45.8  h60: 4.84/0.03/41.8  h120: 4.52/-0.02/46.2  h180: 3.19/0.09/60.0  h240: 3.28/-1.19/60.0  c0: 5.82/-4.34/40.5  c60: 2.68/-3.49/59.9  c120: 2.78/-2.89/60.0  c180: 2.63/-2.76/60.0  c240: 2.70/-3.56/60.0
  c1-p080-HP-L M (n 5): h0: 5.07/-0.13/45.6  h60: 3.32/-0.17/82.8  h120: 3.41/0.13/94.8  h180: 3.33/0.21/96.5  h240: 3.46/-1.05/96.7  c0: 5.78/-4.57/30.9  c60: 2.00/-4.25/35.5  c120: 2.06/-3.79/42.0  c180: 1.43/-3.70/39.4  c240: 2.76/-4.21/116.4
```

## 11. OPEN items and how they were applied; exclusions

Every OPEN item was resolved before data (plan §11), and the script applies each one as committed. None was
re-resolved here.

| id | applied as | where it shows |
|---|---|---|
| O-1 | K-SALT record PASS at `c1-p010-PW-G/129003` (ruled); superseded VOID noted | I-12 |
| O-2 | K1 never tested on PW: qualification printed, nothing VOID | I-14; §4 above |
| O-3 | flow = evaluated rows (starved and aged included), food − p · kJ; variants printed | the flow variants under each point (e.g. L9–L11) |
| O-4 | y′ as registered; the living-share variant printed | e.g. L30, L147, L190 |
| O-5 | MARGINAL on net_per_birth + 0.25 < 0.25; the other reading printed | the per-birth lines (e.g. L8) |
| O-6 | within-member SD | not reachable (no share WIN) |
| O-7 | VOID seed removed from n | no VOID seed is ruled |
| O-8 | PARTIAL survivor by majority of invalid seeds | PARTIAL-H/-D calls, e.g. L131, L290 |
| O-9 | per-kind pooled null, holistic-null pin | L316–L318 |
| O-10 | anchor reads RBT-118 (not available); does not block | L257 |
| O-11 | income tested at ≥ 2 income-valid seeds at every point; §8 counts every EARNS (R1) | L309; L423 |
| O-12 | K2 pooled: \|mean\| < 0.05 and t not rejected | L311 |
| O-13 | Wald χ²/z on the GLS covariance | L410–L412 |
| O-14 | per-row OLS of x on p, Fieller | L415–L420 |
| O-15 | R-A (b) on the pair's layer | L428–L440 |
| O-16 | "smell G first" as a block order | L428, L441 |
| O-17 | every sign change on a listed C1 row | L437–L440 |
| O-18 | R-B eligibility at NOT RUN points (R4, DATA-INFORMED) | L442–L452 |
| O-19 | CP at α = 0.05, inverse normal of the t p-value | L443–L451 |
| O-20 | (a) pooled across kinds; (b) EARNS-TIE fails verdict 5 (R2) | L423–L425 |
| O-21 | c − 1, log(p/0.03) coding | L404–L409 |
| O-22 | settled N points enter no share family | L309 |
| O-23 | the Stage-1 flanking pair; 7 candidates | L437–L441 |

**Exclusions** (plan §3.2): none beyond K-SALT VOID (none ruled), validity (plan §3.1) and CRASHED. Nothing was
winsorised or re-weighted (L622). No §3.2 cross-check mismatch and no empty flow was raised: the script would have
stopped with HELP, and it exited 0.

## Observations outside the plan (descriptive, not registered)

*None of these changes any call. They are offered for the adversary.*

1. **The readout test file is not fully green at the go commit.** `tests/test_rbt129_stage1_readout.py` at
   `fe3a602975fcbbd2732620589d3ccd96acc4feb7`: 89 passed, 2 failed.
   - The two failing tests (`test_ruled_ksalt_void_go_ids_and_the_readout_input`, `test_a_pending_go_id_is_refused`)
     assert that the repository's `RULINGS-CITED.md` still carries `GO-ID-PENDING:`. The go commit
     `d11b814bb24077f0837dd75461eaf1d3c8e0b446` renamed that tag to `GO-ID:`.
   - On the go's parent (`14f3c67`) the same file passes, 91 of 91.
   - So the failures are the lock opening, not a script defect. The tests were not changed.
2. **The per-birth income for H sits near zero at every point**, from −0.048 to +0.020 (e.g. L8, L292). D's is
   negative at every point (e.g. L8, L59). So MARGINAL is set on every EARNS call (§8 above).
   - In the regime table, the 240 window's viability is negative for both faunas at every point and arm, while the
     earlier windows are mostly positive (L339–L373).
   - The 240–299 window is the run's last, so its complete-life measures may be shaped by the end of the run. The
     plan's definition counts censored lives (§3.5).
   - Whether MARGINAL here reads the economy or the window is a question for the adversary. The definition was applied
     as committed.
3. **The anchor in M1.** M1/M4 (L377) prints "RBT-118 (not available)" at `c1-p030-U-L` as its own category. Plan §4.2
   item 8 says M4 counts it under NOT RUN, with that note. The scorecard's "15 of 36" (L617) does count it with NOT
   RUN. Presentation only; no call changes.
4. **The share model.** Plan §6 and ruling NOTE 3 expected the secondary share model to be not identifiable at Stage 1.
   The script reports it TESTABLE with nothing dropped, at p 0.9145 (L414). It is descriptive and outside Holm either
   way.
5. **Both EARNS-H calls are at points where H does not persist.** `c1-p010-PW-L` is EXCLUDED-H, with H extinct by 299
   on 6 seeds (L253). `c1-p080-HP-L` is PARTIAL-D (L290). Each was tested on 2 and 3 income-valid seeds. This is what
   separates the registered headline (L423) from the non-registered habitable-only line (L424).
6. **How the per-point table was produced.** The §3 table and the merge-count table were produced by a text-only
   reformat of the script's header lines. It does field extraction and no arithmetic, and it is not committed. Every
   other table was transcribed by hand from the cited lines.
