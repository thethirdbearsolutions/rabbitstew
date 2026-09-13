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

## Why this exists (RBT-68)

`runs/compass-gain/` held a superseded finding about a Braitenberg compass and
`steering_gain.py`, a working signed path sum. RBT-63 was filed because the finding was
wrong, and it pointed at both files: one as the error to audit, one as the code to reuse.

Neither was in the repository. `runs/` was ignored wholesale, so the run existed only on its
author's disk. The audit RBT-63 asked for could cover the repository and nothing else — and
the places where the defective measure had actually produced wrong conclusions were exactly
the places that were out of reach. The replacement had to be written from the ticket's prose
instead of lifted from the working code that already existed.

That is the same failure as RBT-64 one level up: the knowledge existed, it just was not
anywhere the person who needed it could look.
