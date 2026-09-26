# RBT-103 adversary probes

Every row here was run through the author's committed harness, `runs/RBT-103/routed_populations.py`,
unchanged, at 64 paired seeds, a = 32 and 64, with the committed body rule. The exception is
`prefix_routed_populations.py`, which is that harness as committed at 1be81c3, before the 15:02 fix.
The genomes came from `scripts/durable.sh restore runs/RBT-90/forage-S rbt-90-S`, followed by
`git checkout -- runs/RBT-90` (README rule 6: tables are never read from a checkpoint).
`run_probes.sh` and `run_probes2.sh` launch everything. `recount.py` and `world_matrix.py` print
the two summary tables.

| file | what |
|---|---|
| `repro-P801-control.txt`, `repro-seed-805.txt`, `repro-seed-1.txt` | reproductions from scratch: identical to the committed readouts |
| `prefix-seed-807.txt` | seed 807 under the pre-15:02 harness: identical |
| `recount.txt` | 8/10 and t(9) re-derived, plus the pre-fix-readback counterfactual |
| `xworld-seed-S-in-p801.txt` | each of the ten RBT-90 populations' bodies in P-801's world (the missing cell) |
| `seedblock9000-*.txt` | P-801's world move on a fresh seed block |
| `w4b-*.txt` | the W4b move, seed-matched both ways, plus W4b in P-801's world |
| `world-P801-in-*.txt`, `worlds/` | P-801 bodies in worlds that change one food factor at a time |
| `world_matrix.txt` | the whole world control as one table |

Everything in the world matrix is **exploratory**: it was chosen by the adversary after reading
the author's report.
