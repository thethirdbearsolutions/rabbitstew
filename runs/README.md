# Run directories: what is kept, and why

A run directory holds two very different kinds of thing, and they have different fates in
git.

**The evidence is tracked.** The small text files that *constitute* a finding — the report
that states it, the scripts that produced it, the readouts they printed, and the `config.json`
they ran under — are committed by default. They are kilobytes, and they are the only reason
anybody else can re-derive, re-read or re-audit the result later.

**The bulk is ignored.** Per-generation genotype dumps, `history.json`, `lineage.jsonl`,
`analysis.json`, `.traj` files, logs: output, not argument. Regenerable from the tracked
half, and not worth versioning.

The split is mechanical, in the repository's `.gitignore`:

```
runs/**
!runs/**/          # so git descends into run directories at all
!runs/**/*.md      # reports and findings
!runs/**/*.py      # the scripts that produced them
!runs/**/*.sh      # and the shell scripts that launched or extracted them (RBT-86)
!runs/**/*.txt     # readouts
!runs/**/config.json
```

Nothing already committed is affected by this — `.gitignore` never untracks a tracked file —
so `runs/RBT-19`'s genotype corpus stays where it is.

One deliberate side effect. These patterns are anchored to the repository root; the bare
`runs/` they replace had no slash, so git matched it at *any* depth and quietly ignored
`docs/runs/` too — the curated directory whose contents are meant to be committed, and whose
existing files got there by `git add -f`. Those no longer need forcing.

## The rule

**If a claim rests on it, commit it.** A finding whose script lives only on the machine that
produced it is not a finding anyone else can check, and these machines are reclaimed.

The allowlist above is the mechanism, not the rule. It admits files by extension, so a table
that backs a claim is committed if it happens to be called `.txt` and silently dropped if it
was written as `.csv` or `.json` — with the author reasonably believing the policy had been
followed (RBT-86, found twice in one morning). What a run owes is therefore stated by **role**,
and the files are named so that the mechanism admits them:

- **Configs, always.** `config.json` for every arm.
- **Scripts that produce a committed readout, whatever language.** The Python that computes it
  and the shell that launched the arms or extracted the numbers are the same kind of thing:
  part of the argument. RBT-66's `extract.sh` and `run_champions.sh` had to be force-added
  because `*.sh` was not on the allowlist, while RBT-38's identical-purpose `extract.sh` is
  tracked only because it predates it. `*.sh` is on the allowlist now; it cannot admit bulk.
- **For an ecology arm, two tables are the argument and are committed**, whatever format they
  would naturally have taken:
  1. **The per-season summary** — one row per season and fauna (population): alive, births,
     deaths, mean and best of whatever the run scores on. Every figure and every duration
     clause is computed from this. Written as `seasons.txt`.
  2. **One row per individual at its last observation** — population, name, generation, age,
     evaluations, score, parents. Heritability, founder survival and descent depth are computed
     from this. Written as `lineage-last.txt`.
- **Bulk stays out.** Per-season re-logging (`history.json`), genome dumps, raw lineage
  (`lineage.jsonl`), `.traj` files, logs. Regenerable, and not the argument. The `.gitignore`
  patterns are unchanged: adding `*.csv` or `*.json` to the allowlist would admit the bulk.

Both tables are text and about 100–150 kB per 600-season run. Whether a run has met this is
checkable: in a worktree that has never held the bulk, run the arm's analysis script and diff
against the committed readout; then perturb one cell of one committed table and confirm the
readout moves, so that the agreement is a derivation and not a replay.

Worked examples. **RBT-71** (`runs/RBT-71/`): `measure.py` reads the bulk when present, falls
back to `seasons.txt` and `lineage-last.txt` when absent, asserts the two agree when both
exist, and `--summarise` writes the pair from a run's bulk; `adversary.py` item 1 is the
worktree-and-perturb check. **RBT-80** (`docs/artifacts/RBT-80-series.txt`): the per-season
series of all nine arms, committed so that the yield table — the ticket's headline — can be
re-derived from the checkout alone.

## Why this exists (RBT-68)

`runs/compass-gain/` held a superseded finding about a Braitenberg compass and
`steering_gain.py`, a working signed path sum (since RBT-81 it reports the depth-1 term: the
path sum diverges on these brains). RBT-63 was filed because the finding was
wrong, and it pointed at both files: one as the error to audit, one as the code to reuse.

Neither was in the repository. `runs/` was ignored wholesale, so the run existed only on its
author's disk. The audit RBT-63 asked for could cover the repository and nothing else — and
the places where the defective measure had actually produced wrong conclusions were exactly
the places that were out of reach. The replacement had to be written from the ticket's prose
instead of lifted from the working code that already existed.

That is the same failure as RBT-64 one level up: the knowledge existed, it just was not
anywhere the person who needed it could look.

## Ecology runs made before RBT-95 do not reproduce from their configs

RBT-95 gave the ecology one RNG stream per fauna and one for the terrain (mirroring RBT-85's arena
streams), so that two runs at one seed differing on one fauna's side are a pair. Every ecology run
made before that drew founders, ages, groupings, breeding and worlds from a single generator, and
**re-running its `config.json` on the current code gives a different run**. Those runs are not lost:
their record is what RBT-27 put on disk, every genome at birth and every season's cohorts, and
`runs/RBT-84/reproducible.py` check 1 reads the founders from there rather than regenerating them.
A claim about a pre-RBT-95 ecology run is re-derived from its committed summaries and its saved
genomes, never from its seed.

## Do not pipe a long-running readout through `grep` (RBT-84)

`forage_lab.py` and the other lab scripts flush every row as they finish it, so a run in progress can
be watched with `tail`. **A pipe undoes that.** `grep` block-buffers when its stdout is a file rather
than a terminal, so

```
python3 scripts/forage_lab.py … | grep -v WARNING > out.txt      # WRONG: out.txt stays empty for minutes
python3 scripts/forage_lab.py … > out.txt 2>/dev/null            # right
```

leaves the output file empty for minutes at a time no matter how fast the modes are completing.

This has now cost two people on one day. RBT-84's delegate read the empty file, concluded the modes
were not finishing, reported a cost of 4–5 hours for a table that takes 40 minutes, and then killed
the job 2 modes from the end; RBT-84's adversary hit the same buffer watching their own probe. Use
`grep --line-buffered` if a filter is genuinely needed, or redirect and filter afterwards.

**The general rule, which is the reusable part:** before reporting that something did not happen,
verify the channel that would have shown it.
