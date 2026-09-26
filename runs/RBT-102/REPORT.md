# RBT-102: the routed motif's structure under selection, read without the magnitude gate

Status: **§1 is final. §2 is pending**: the RBT-90 part-2 arms are still running. The
pre-registration is `PREREG.md`, committed before any arm was restored.

## 1. RBT-80's own data: what it can and cannot say (ruling (a))

**RBT-80's genomes and lineage were never committed, by design.** RBT-80's description says
"genomes and lineage stay out", and `.gitignore` keeps `runs/**` out of the repository except
`.md`, `.py`, `.sh`, `.txt` and `config.json`.

On 2026-09-26 all 122 remote branches were checked, `ckpt/*` included. Every branch carries the same
24 RBT-80 files: nine `config.json`, ten `docs/artifacts/RBT-80-*.txt` readouts and five
`scripts/rbt80_*.py`. `git log --all -- 'runs/RBT-80*'` shows only config commits. The W4b-801
founders (`runs/RBT-23/W4b-801`) are not committed anywhere either. RBT-80 ran before RBT-95, so its
arms do not reproduce from their configs. RBT-91's structural predicate therefore cannot be applied
to RBT-80's populations.

**The stated bound from the committed summaries** (`docs/artifacts/RBT-80-seed{A,B,C}-depths.txt`,
every 10th season plus season 299, three seeds, 479 / 462 / 461 control genotypes measured over 31 sampled seasons each):

- **Control arm:** `carr d2` = 0 and `inverted d2` = 0 in **every sampled season of every seed**.
  No living control individual had a depth-2 path gain of |a| ≥ 16 in *either* direction of travel.
- **The median depth-2 gain** of the living control population is ±0.0 in every sampled season of
  every seed. So at least half of every sampled control cohort had zero net depth-2
  nose→Effector gain.

That bounds control-arm structural carriage at **≤ ~0.5 per season**, and no tighter. The bound
cannot be compared with RBT-91's drift proposal rate (0.042%). The question this ticket asks,
whether the structure was carried at sub-paying magnitude, **is not answerable from RBT-80's
committed data**.

Three limits of those columns, for anyone quoting them:
1. Every carrier count is gated at |a| ≥ 16, and the depth-2 gain is a path sum, not RBT-91's
   single-interneuron predicate.
2. Direction was probed at 2 seeds × 3 s, not the 16 × 15 s reference.
3. Only counts and medians are stored; there is no per-individual `a`.

The seeded and drift inversion counts in the same tables restate RBT-80 at the magnitude gate, so
they are not re-tabulated here (ruling).

## 2. RBT-90 part 2's ten arms (ruling (c))

Pending. See `PREREG.md` for the data, the config differences from RBT-80's control arm, the rule
and the prediction.
