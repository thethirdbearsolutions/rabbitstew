# RBT-92 seed rule (committed before any RBT-90 part 2 output is readable)

Committed 2026-09-26 12:26 UTC by the RBT-92 designer. At this time the ten RBT-90 part 2 arms
(dispatched ~12:30 UTC per the state doc, ~1 h each) have produced nothing the designer has read, and none is readable
on any branch the designer has fetched.

**Rule: all ten RBT-90 part 2 seeds, no selection.** 801 804 805 806 807 1 2 3 4 7
(`docs/artifacts/RBT-90-part2-seeds.txt`; chosen there by a founders-only rule, before any run).

The only exclusion, applied mechanically per seed and stated in the readout as k/10:

- the seed's population (holistic, or conventional comparator) is extinct at or before the event
  season in its RBT-90 arm, so there is nothing to shift or cull. The shift and cull arms share the
  baseline's prefix byte for byte (verified separately, `runs/RBT-92/shared_baseline_check.txt`), so
  this exclusion is decided by the baseline arm alone and is identical across the three arms.

A seed whose run crashes for an infrastructure reason is re-run (restore + `--resume`), not
excluded. If fewer than six seeds survive the exclusion the epoch is reported as underpowered
(k/10 read, below the six-seed floor of RBT-89) and no verdict is issued.

Nothing about a seed's RBT-90 outcome (income, turnover, diversity at season 600, direction of
travel) enters this rule.
