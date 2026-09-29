# RBT-129 L1: the gated M/N emitter (DESIGN §5.2 as amended by AMENDMENT-FOUNDING T5)

Launch condition **L1** (`founding-screen-adversary/ADVERSARY.md`; #495 ruling, open question 2): the emitter must be
written, adversaried and merged before any Stage-1 S60 result is read. This directory records it. The code is in
`launch/stages.py` (section "Stage 1's M and N: the gated emitter"). Its tests are in `tests/test_rbt129_mn.py`.

Nothing here launches anything. `mn-rank` reads the census only. `mn-emit` writes lane files only.

## What the gate reads, and why it must wait for S60

T5 needs Stage-1 S state. These are the sentences it rests on:

> At a gated point, M is forked only on seeds valid at the merge (both faunas alive at season 59 in S).
>
> **DATA-INFORMED (ruling item 6):** a point where M runs on no seed frees its slot for the next point in the ranking.

§5.2 item 2 as T5 amends it gives N "the same seed rule as M". So which points get M and N, and on which seeds, depends
on Stage 1's S at season 59. M and N are therefore emitted by a separate command, `mn-emit`, as fork jobs from each
chain's `ckpt60`. It runs after the S60s exist. The ranking itself reads no Stage-1 data (§5.2 item 1: "Points are
ranked by census g0, lowest first").

**The gate's inputs, all of them:**

| input | source | when |
|---|---|---|
| census g0 per Stage-1 point | `stage0/<point>/<seed>/S` for 129001–129003: `lineage.jsonl` (every row except cull and merge-null, generations 30–59, both faunas pooled), `config.json`'s price; + 0.35 | now (pre-data) |
| the designed fauna's census FOUNDING-FAIL (C2) | the same runs' `history.json`: designed extinct at 59 before refill on ≥ 2 of 3 seeds | now |
| cross-check of both | the committed `stageP0-readout/stageP0_readout.txt` (g0 to 3 decimals, and the designed FOUNDING-FAIL list); any difference is refused | now |
| the anchors | `blocks.ANCHORS` (§5.2 item 3) | now |
| salts (s_j, t_j) | `screen_gate` (the gate `stage1-emit` uses), and `lanes/1/launch.txt`'s `salts` line, which must match it | after Stage F |
| the seed rule | each M-eligible point's `stage1/<point>/<seed>/ckpt60/history.json`: both faunas' `alive` at season 59 > 0, or the unit's `EXTINCT.txt` (not valid) | after S60 |
| provenance checks (not gate inputs) | `ckpt60/config.json` must be the S60 config at the screened salts (for 129001 at (0, 0) that is the adopted census config); where the chain has a K-SALT (F7), its `KSALT.txt` must read PASS | after S60 |

The gate reads no other Stage-1 figure. It reads the S60 of only the M-eligible points. It refuses (exit 8) until
every one of those S60s is done.

## The ranking, now (`mn_rank.txt`)

`python3 runs/RBT-129/launch/stages.py mn-rank` was run with the 108 census runs of the 36 Stage-1 points restored from
their `ckpt/` branches. Every g0 and every designed FOUNDING-FAIL flag matched the committed readout.

- **M-eligible: 10 points.** In rank order: c0-p080-PW-G, c0-p030-PW-G, c2-p010-PW-G, c1-p010-PW-L, c1-p010-PW-G,
  c0-p010-PW-G, c1-p080-HP-L, c1-p080-U-L, c1-p080-HP-G, c2-p030-U-G.
- **N-eligible: 7 points**, the first 7 of those.
- **Excluded:**
  - the anchor c1-p030-PW-G (g0 0.434);
  - designed FOUNDING-FAIL at c1-p030-PW-L, c1-p080-U-G, c2-p080-U-G and c2-p080-HP-G;
  - no census g0 at c1-p080-PW-G, c1-p080-PW-L, c2-p030-PW-G and c2-p080-PW-G.
- **Upper bound, every seed valid:** 80 M + 32 N arms = **174 / 326 core-h** at 23.35 / 43.72 core-s. The disclosed
  figure is **171 / 320**.
- `mn-emit` prints the actual total beside the lanes, in `lanes/1-MN/gate_table.txt`.

## Mutants (`mutants.py` → `mutants.txt`): 31 of 31 killed

These include the brief's five:
- g0 from the wrong seeds (×2) or the wrong faunas (×2);
- the slot-freeing rule dropped;
- salts not carried to M/N (the job's salts, the lane check, the fork's source check);
- M/N emitted where `stage1-emit`'s screen gate refuses, or against a Stage-1 launch record at other salts;
- the census resume at a salt other than 0 (ckpt60's salts not checked; M/N forked from the census S).

## Open questions for the coordinator

1. **N and the slot-freeing rule.** N takes the M-admitted points with g0 ≤ 0.8, in rank order, up to 4, on M's seeds.
   So a point with no valid seed also frees its N slot. T5 states the freeing rule only for M. The alternative reading
   is that N's 4 slots go to the 4 lowest-g0 points whatever their validity. At Stage 1 this is the only place the
   rule bites: M has 10 eligible points for 12 slots, so M never fills; N has 7 for 4.
2. **The anchors.** c1-p030-PW-G would rank 2nd. It is excluded under §5.2 item 3 ("The sweep does not re-run them")
   and takes no slot. If RBT-118 declines the salts (T7), is the sweep's own anchor M/N at c1-p030-PW-G forked from
   Stage-1 S, or only from the §9.1 fallback? This emitter does not do either.
3. **The threshold rescale.** §5.2 says that if the pilot finds the real drift far from the replica's, "the gate's
   thresholds are rescaled by the same ratio before Stage 1". The readout measured r = 1.53. T5 and the 171 / 320 figure
   use the unscaled 1.0 / 0.8, and so does this emitter. Neither the direction nor the trigger ("far") is registered.
4. **"Valid at the merge".** The emitter uses history.json's season-59 `alive` > 0 for both faunas. This is the
   readout's `yprime` count, and the one the pilot's null SD used. The founding criterion (F2) counts before refill
   instead. The two differ only when a fauna's every survivor dies in season 59 after breeding.
5. **K-SALT not PASS.** If any M-eligible chain's K-SALT is VOID or missing, `mn-emit` refuses the whole emission. It
   does not drop the seed. F7 says a VOID "voids the point for the seed" and re-opens the stream claim, and this reads
   that as the coordinator's call.
6. **Pricing.** The disclosed 171 / 320 prices N at 0.57 core-h an arm at 20 core-s (`founding_expect.py`). The gate
   table prices N at the full 240 seasons, like M. The upper bound 174 / 326 is on that basis.
7. **No-peek.** The gate table prints each admitted point's count of valid seeds at the merge, which is a season-59
   survival count. It is what the gate reads; nothing else is printed.

## Reproduce

```
python3 runs/RBT-129/launch/stages.py mn-rank            # restores the census runs from their branches where missing
python3 runs/RBT-129/mn-emitter/mutants.py <venv python> > runs/RBT-129/mn-emitter/mutants.txt
python -m pytest tests/test_rbt129_mn.py -q
```
