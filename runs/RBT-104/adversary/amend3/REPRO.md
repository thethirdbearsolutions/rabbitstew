# How the Amendment 3 re-check's probes were run

All inputs are either committed or rebuilt from committed recipes. **No RBT-104 arm output was read.**
The only arm information used is branch metadata: commit subjects, times and file names.

## Inputs
- **Founders.** `SCRATCH/fhead` is `runs/RBT-104/seed_founders.py 801 SCRATCH/fhead`. Its SHA256SUMS
  digest is `78493e74…`, which equals `founders-digests.txt`.
- **Part-2 genealogy.** `SCRATCH/p2x/forage-801` is RBT-90 part 2's checkpoint
  (`ckpt/rbt-90-801`, 600/600), extracted from `run.tar.gz.part*`. It holds `lineage.jsonl`
  (71,288 rows) and `conventional/genomes` (1,295 genomes).
- **RBT-106's tree.** `SCRATCH/w106` is a worktree at `85cdee48` (`origin/results/RBT-106-adversary`).

## Probes

**`xnull-801-rerun.txt`: the full-operator null, re-run independently.**

    cd SCRATCH/w106 && PYTHONPATH=. python runs/RBT-106/adversary/null_xover.py \
        SCRATCH/p2x/forage-801 801 1 SCRATCH/fhead --k 8 --reps 20 --procs 4 --seasons 150,300,599

It is identical to `runs/RBT-104/null_xover/xnull-w1-k8-801.txt`, cell for cell. The one difference
is the header's suffix ", deepen x1": the committed tables were written by the script's 22:08
version, `19f6ca24`, before `--deepen` existed.

**`workability.txt`: Amendment 3's `peek.py` window path on a throwaway S8-801 mini-run.** The run is
part 2's command with `--from-conventional SCRATCH/fhead --link-scale 8 --seasons 8`, in scratch.

**`power_a3.txt`: P(SUPPORTED | H) under the attribution requirement, with its spread.** No
simulation.
