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

## Mutants (`mutants.py` → `mutants.txt`): 40 of 40 killed

These include the brief's five:
- g0 from the wrong seeds (×2) or the wrong faunas (×2);
- the slot-freeing rule dropped;
- salts not carried to M/N (the job's salts, the lane check, the fork's source check);
- M/N emitted where `stage1-emit`'s screen gate refuses, or against a Stage-1 launch record at other salts;
- the census resume at a salt other than 0 (ckpt60's salts not checked; M/N forked from the census S);
- after the #500 ruling: both K-SALT conditions, K-SALT read after the extinct short-circuit, the run-lane fork check
  (the call, the admitted list, the arm settings, the source), the forks line, and the g0 fauna filter.

## Rulings (#500, comment 5889288621; adversary #501)

1. **N eligibility. DATA-INFORMED, added to T5 item 2.** N is drawn only from the M-admitted points, and N slots
   freed by exclusions pass down the census ranking among those points. So c1-p010-PW-L, not the designed-FF
   c1-p030-PW-L, takes the third N slot when every seed is valid. The code comment and the gate table say so.
2. **No rescale by r = 1.53.** §4.1 fixes the thresholds, T5 was adopted after r was known, and the units differ.
   That leaves **10 M-eligible and 7 N-eligible points**. The gate table records this.
3. **Anchors** take no slot. The fallback at W118-a and W118-c forks from those points' own Stage-1 ckpt60, and W118-b
   from F5, through a separate command. That command is not part of L1.
4. **Validity.** `alive > 0` at 59 is kept. The README's earlier premise was wrong: booked and before-refill
   extinction cannot differ. Breeders are the season's survivors, and a parent cannot die in the season it breeds, so
   births > 0 implies alive − births > 0. Across the 8,584 census history rows the two differ 0 times.
   `test_booked_and_before_refill_extinction_agree_in_the_ecology` tests this.
5. **A K-SALT VOID fails the whole emission closed.** K-SALT is now read **before** the extinct short-circuit, so a
   VOID on an extinct unit is refused too.
6. **N is priced at 240 seasons.** The disclosure's N was 102.6 arm-seasons an arm (0.57 core-h at 20 core-s). This
   emitter prices N 2.34× higher, offset by M having 10 eligible points instead of 12. The bound is **174 / 326**,
   +3 / +6 over 171 / 320. The larger figure goes to the owner. The gate table has this line.
7. **The printed valid-seed counts** reveal PARTIAL status at M-eligible points before the Stage-1 readout. They are
   the gate's registered input, not a peek. The gate table notes this, and the readout should note that the counts
   were seen at emission.

**Also fixed (the ruling's SHOULDs):**
- `run-lane` holds M/N forks to `lanes/1-MN/launch.txt`'s `forks` line, and checks each fork's arm settings and its
  Stage-1 ckpt60 source (`check_lane_forks`).
- A g0 fauna-filter test is added.
- Both K-SALT conditions are tested: required at 129001 at (1, 0), and not required where t ≥ 1.

## Reproduce

```
python3 runs/RBT-129/launch/stages.py mn-rank            # restores the census runs from their branches where missing
python3 runs/RBT-129/mn-emitter/mutants.py <venv python> > runs/RBT-129/mn-emitter/mutants.txt
python -m pytest tests/test_rbt129_mn.py -q
```
