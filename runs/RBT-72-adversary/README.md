# RBT-72 adversary probes (paper 8)

Independent re-derivations of paper 8's headline numbers from the committed files, by code
not shared with `runs/RBT-72/rederive.py`. No simulation except `probe_rung.py`, which runs the
committed small-signal probe on one installed genotype (about a second).
Run from the repo root with `PYTHONPATH=$PWD`.

| probe | readout | what it checks |
|---|---|---|
| `probe_prize.py` | `probe_prize.txt` | +0.897 / 1.516 / +59%; W4b ladder to +1.875; P-801 forward five +1.009 / +3.206 / +8.094 on 2.688; backward two 12/12 negative; RBT-97 §1's 12/12 and 2/2 table; t-intervals beside the committed bootstrap ones |
| `probe_phantom.py` | `probe_phantom.txt` | §2.2's manipulation table, per-robot, and the population it was run on (W4b only) |
| `probe_alone.py` | `probe_alone.txt` | §4.2's links-alone table (84/63/66, 0 reaching the rung, maxima, background 0.26% to 1.64%), and whether the whole-brain column is background (Fisher) |
| `probe_resign.py` | `probe_resign.txt` | §3.4's 35/48/1, 42.2% [32.1, 52.9], z −1.43: what quantity it signs, how zeros are classed, the motif's own links re-signed; §6.1's "below 1e-5" bound |
| `probe_rung.py` | `probe_rung.txt` | the paying rung 6.8664 (hard-coded in `runs/RBT-91/structural_rate.py`, printed by no readout) measured on the same install, whole brain and links alone |
| `probe_rbt80.py` | `probe_rbt80.txt` | §2.4's seeded − control yields +0.432 / +0.371 / +0.373, the plateau and the season-0 gap |

## Round 2 (re-check of PR #82)

| probe | readout | what it checks |
|---|---|---|
| `genotype_motif_rerun.py` | `genotype_motif_rerun.txt` | `scripts/genotype_motif.py` with one line changed: `RUN` pointed at the committed copy of the run (`docs/artifacts/RBT-23-W4b-801`), because `runs/RBT-23/W4b-801` is not on the branch. 2,240 bouts, 2 m 44 s on four cores. The numbers are byte-identical to `docs/artifacts/RBT-23-W4b-801/genotype_motif.txt` (paper 8 G1, G2). The one extra line is a MuJoCo instability warning on stderr from one bout. |
