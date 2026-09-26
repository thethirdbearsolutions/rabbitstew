"""RBT-98: the per-branch table, from rows.txt (audit.py) and citations.txt (citations.py).

    python runs/RBT-98/table.py > docs/artifacts/RBT-98-stranded.txt
"""
import collections
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROLES = ["report", "readout", "script", "config", "seasons", "lineage-last", "bulk", "infra"]
CLAIM = {"report", "readout", "script", "config", "seasons", "lineage-last"}
TICKET = {
    "claude/wonderful-dirac-crq8aa": "RBT-14", "results/RBT-14": "RBT-14",
    "results/RBT-18": "RBT-18", "results/RBT-15": "RBT-15", "results/RBT-16": "RBT-16",
    "claude/rbt-20-mtqdsp": "RBT-20", "results/RBT-13": "RBT-13",
    "claude/dazzling-shannon-qq5zd1": "RBT-9", "claude/wizardly-johnson-4c9hvn": "RBT-17",
    "results/RBT-21": "RBT-21", "feature/RBT-28": "RBT-28",
    "claude/rbt-lowest-unclaimed-ticket-fe8mzt": "RBT-5",
    "claude/rbt-lowest-unclaimed-ticket-cylx3s": "RBT-2", "results/RBT-22": "RBT-22",
    "results/baseline-801": "(baseline)", "claude/determined-shannon-2zb8jp": "RBT-10",
    "claude/rbt-lowest-unclaimed-ticket-55orfd": "RBT-23",
    "claude/dazzling-lamport-y47veb": "RBT-11", "results/RBT-12": "RBT-12+37",
    "claude/busy-mendel-rdhs94": "RBT-12+37",
}
ALIASES = [
    ("claude/beautiful-galileo-pqrpl5", "results/RBT-15 (56df288)"),
    ("claude/stoic-pasteur-k8i8sg", "results/RBT-13 (d56be52)"),
    ("claude/clever-heisenberg-wf95xu", "results/RBT-18 (fcc40a7)"),
    ("claude/eager-meitner-95d7zl", "results/RBT-16 (3a35f46)"),
    ("claude/rbt-lowest-unclaimed-ticket-f7ovpw", "results/RBT-21 (9cbd061)"),
    ("claude/rbt-lowest-unclaimed-ticket-9oyh8a", "feature/RBT-28 (62726ed)"),
]
# Claim-bearing files whose path exists on integration with different content, judged by
# reading both sides: integration carries the change in a later form, so nothing is ported.
SUPERSEDED = {
    ("feature/RBT-28", "scripts/forage_lab.py"):
        "adopted and extended on integration (12ed2d5, then RBT-39's gait null)",
    ("feature/RBT-28", "tests/test_foraging.py"):
        "both tests live on as tests/test_forage_lab.py (refuses a non-food run; end to end)",
    ("claude/rbt-lowest-unclaimed-ticket-cylx3s", "docs/persistent-world.md"):
        "the 'about half the spots empty' correction is on integration (lines 214-215, 235-237)",
}


def main():
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(HERE, "rows.txt"))]
    by = collections.OrderedDict()
    for br, head, role, status, path, where, dest in rows:
        by.setdefault(br, []).append((head, role, status, path, where, dest))
    heads = {}
    out = []
    w = out.append
    w("RBT-98: stranded evidence on the unmerged 09-12 wave branches, audited against")
    w("integration claude/new-session-4cao7d @ 3b89700 (2026-09-26). Re-derive with")
    w("runs/RBT-98/audit.py > rows.txt; table.py writes this file from rows.txt and citations.txt.")
    w("")
    w("Files = what the branch adds or changes relative to its merge-base with integration, by")
    w("role (runs/README.md). ported = claim-bearing, absent from integration, now on")
    w("results/RBT-98 byte for byte. present = the same content already on integration (same")
    w("path, or another path: listed below). superseded = the path is on integration in a later")
    w("form. archive-only = after this port the branch holds nothing claim-bearing that")
    w("integration lacks: only bulk, .gitignore edits, or superseded files.")
    w("")
    hdr = (f"{'branch':44s} {'head':7s} {'ticket':9s} " + " ".join(f"{r[:6]:>6s}" for r in ROLES)
           + f" {'ported':>6s} {'presnt':>6s} {'supsd':>5s}  archive-only")
    w(hdr)
    w("-" * len(hdr))
    tot = collections.Counter()
    for br, fs in by.items():
        head = fs[0][0]
        c = collections.Counter(f[1] for f in fs)
        ported = sum(1 for f in fs if f[5] != "-")
        present = sum(1 for f in fs if f[1] in CLAIM and f[2].startswith("present"))
        sup = sum(1 for f in fs if (br, f[3]) in SUPERSEDED)
        unexplained = [f for f in fs if f[1] in CLAIM and f[2] == "diverged"
                       and (br, f[3]) not in SUPERSEDED]
        assert not unexplained, unexplained
        dup = heads.get(head)
        heads.setdefault(head, br)
        arch = "yes" if c["bulk"] else "yes (no bulk; superseded only)"
        if dup:
            arch += f"; same commit as {dup}"
        w(f"{br:44s} {head:7s} {TICKET[br]:9s} " + " ".join(f"{c[r]:6d}" for r in ROLES)
          + f" {ported:6d} {present:6d} {sup:5d}  {arch}")
        if not dup:
            tot.update(c)
            tot["ported"] += ported
            tot["present"] += present
            tot["sup"] += sup
    w("-" * len(hdr))
    w(f"{'total (each commit once)':44s} {'':7s} {'':9s} "
      + " ".join(f"{tot[r]:6d}" for r in ROLES)
      + f" {tot['ported']:6d} {tot['present']:6d} {tot['sup']:5d}")
    w("")
    w("Roles, as applied. report: *.md. config: config.json. seasons: the per-season summary,")
    w("here the `rabbitstew history` dumps (history*.txt; no branch has a seasons.txt).")
    w("lineage-last: none on any branch. script: *.py, *.sh. readout: other *.txt, a .json at the")
    w("top of a run directory, and a .log that is not the run log of the arm directory beside it")
    w("(by role, not extension, RBT-86). bulk: genotype dumps, history.json, lineage.jsonl(.gz),")
    w("state/analysis/descriptors/fresh_eval.json, run logs, the RBT-37 replay .html.")
    w("A readout the allowlist does not admit under its own name (.json, .log) is ported byte for")
    w("byte as NAME.txt, e.g. runs/RBT-11/situated.json -> runs/RBT-11/situated.json.txt.")
    w("")
    w("Claim-bearing content already on integration under another path:")
    seen = set()
    for br, fs in by.items():
        for head, role, status, path, where, dest in fs:
            if role in CLAIM and status == "present-elsewhere" and (path, where) not in seen:
                seen.add((path, where))
                w(f"  {path:48s} = {where}   ({br})")
    w("")
    w("Superseded (path on integration, later content; not ported):")
    for (br, path), why in SUPERSEDED.items():
        w(f"  {path:32s} {br}: {why}")
    w("")
    w("Aliases. Every branch on the remote was swept with git cherry against integration. Six")
    w("more 09-12 branch names carry unmerged patches; each is the same commit as a listed branch,")
    w("so its row above is theirs too (prune them together):")
    for alias, same in ALIASES:
        w(f"  {alias:44s} = {same}")
    w("The only other branches with unmerged patches are 09-26 work in flight (RBT-90 part 2,")
    w("RBT-92, RBT-96, RBT-97), outside this audit.")
    w("")
    w("Not claim-bearing, not ported: every branch's .gitignore edit (integration's allowlist")
    w("supersedes them all).")
    w("")
    w("Lost artifacts (item 4): files a REPORT cites that exist on no branch at all")
    cites = [l.rstrip("\n").split("\t") for l in open(os.path.join(HERE, "citations.txt"))]
    lost = [c for c in cites if c[3] == "LOST"]
    w(f"  {len(cites)} file citations in {len({c[1] for c in cites})} REPORTs, resolved against all"
      f" 105 branches: {sum(c[3] == 'path' for c in cites)} by path,"
      f" {sum(c[3] == 'suffix' for c in cites)} by bare name,"
      f" {sum(c[3] == 'pattern' for c in cites)} are globs, {len(lost)} unresolved.")
    w("  None of the unresolved is a lost artifact; each is notation or a file the REPORT says")
    w("  it did not keep:")
    notes = {
        "holistic/best_gen0000-0030.json": "a range; best_gen0000..0030 are on the branch",
        "holistic/best_gen0000-0020.json": "a range; best_gen0000..0020 are on the branch",
        ".history.txt": "`<run>.history.txt` template; four are on the branch",
        ".probe.txt": "`<run>.probe.txt` template; four are on the branch",
        "analysis.html": "the REPORT says 'analysis.html is not committed'",
    }
    for c in lost:
        w(f"  {c[1]:24s} {c[2]:34s} {notes[c[2]]}")
    w("  So the result is: no lost artifacts among what the 09-12 REPORTs cite. Two bare-name")
    w("  citations (RBT-9 analysis.json, state.json) resolve only to other tickets' files; the")
    w("  REPORT itself says there was no analysis.json and the state.json checkpoints were omitted.")
    w("")
    w("What pruning would lose. No branch here carries a lineage-last.txt, and none a seasons.txt;")
    w("the history*.txt dumps are the per-season tables. Any lineage-based claim in these REPORTs")
    w("(heritability, founders, descent) can be re-derived only from lineage.jsonl in the bulk,")
    w("whose every blob exists only in these branches' commits, under the names above and their")
    w("aliases (RBT-11's as lineage.jsonl.gz). Pruning an archive-only branch, with its aliases,")
    w("is safe for everything ported here, and final for that re-derivation.")
    print("\n".join(out))


if __name__ == "__main__":
    main()
