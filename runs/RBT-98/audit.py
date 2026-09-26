"""RBT-98: stranded-evidence audit of the unmerged 09-12 wave branches.

For each branch, list the files it adds or changes relative to its merge-base with
integration, classify each by role (runs/README.md), and say whether integration already
holds it: at the same path with the same content, or with the same content (blob id)
under another path. Only blob ids are compared, so it runs on a blob-less fetch
(`git fetch --filter=blob:none origin BRANCH`) without downloading any bulk.

    python runs/RBT-98/audit.py [--integration origin/claude/new-session-4cao7d] > rows.txt

Prints one line per file: branch, head, role, status, path, the integration path for
content already present, and the path a missing claim-bearing file is ported to. The summary table is docs/artifacts/RBT-98-stranded.txt.
"""
import argparse
import os
import re
import subprocess
import sys

BRANCHES = [
    "claude/wonderful-dirac-crq8aa",  # = results/RBT-14
    "results/RBT-14",
    "results/RBT-18",
    "results/RBT-15",
    "results/RBT-16",
    "claude/rbt-20-mtqdsp",
    "results/RBT-13",
    "claude/dazzling-shannon-qq5zd1",  # RBT-9
    "claude/wizardly-johnson-4c9hvn",  # RBT-17
    "results/RBT-21",
    "feature/RBT-28",
    "claude/rbt-lowest-unclaimed-ticket-fe8mzt",  # RBT-5
    "claude/rbt-lowest-unclaimed-ticket-cylx3s",  # RBT-2
    "results/RBT-22",
    "results/baseline-801",
    "claude/determined-shannon-2zb8jp",  # RBT-10
    "claude/rbt-lowest-unclaimed-ticket-55orfd",  # RBT-23
    "claude/dazzling-lamport-y47veb",  # RBT-11
    "results/RBT-12",  # = claude/busy-mendel-rdhs94 (RBT-37)
    "claude/busy-mendel-rdhs94",
]

# A json that is not a config is bulk unless it sits at the top of a run directory (not
# inside an arm) -- those are single readouts that were written as .json (RBT-86).
BULK_NAMES = {"history.json", "state.json", "analysis.json", "descriptors.json",
              "fresh_eval.json", "MUJOCO_LOG.TXT"}


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def git(*args):
    # From the repository root: ls-tree prints paths relative to the working directory.
    return subprocess.run(["git", *args], check=True, capture_output=True,
                          text=True, cwd=ROOT).stdout


def role(path, dirs):
    """The file's role in runs/README.md's terms; `dirs` is every directory on its branch.

    By role, not by extension (RBT-86): a small .log or top-level .json that holds what an
    analysis script printed is a readout; a .log named after the arm directory beside it is
    that arm's run log, and bulk. A `rabbitstew history` dump (history*.txt) is the
    per-season summary of its day, one row per generation and kind.
    """
    base = os.path.basename(path)
    stem, ext = os.path.splitext(base)
    parts = path.split("/")
    if base == ".gitignore":
        return "infra"
    if base in BULK_NAMES:
        return "bulk"
    if ext == ".md":
        return "report"
    if base == "config.json":
        return "config"
    if base == "seasons.txt" or (ext == ".txt" and "history" in base):
        return "seasons"
    if base == "lineage-last.txt":
        return "lineage-last"
    if ext in (".py", ".sh"):
        return "script"
    if ext == ".txt":
        return "readout"
    if ext == ".log" and parts[0] == "runs":
        run_dir = os.path.join(os.path.dirname(path), stem)
        return "bulk" if run_dir in dirs else "readout"
    if parts[0] == "runs" and len(parts) == 3 and ext == ".json":
        return "readout"  # one result at the top of a run directory, written as .json
    return "bulk"


def port_path(path):
    """Where a ported file goes: its own path when the allowlist admits it, else + '.txt'."""
    ignored = subprocess.run(["git", "check-ignore", "-q", "--no-index", path],
                             cwd=ROOT).returncode == 0
    return path + ".txt" if ignored else path


def tree(ref):
    """path -> blob id, for every blob in ref."""
    out = {}
    for line in git("ls-tree", "-r", ref).splitlines():
        meta, path = line.split("\t", 1)
        out[path] = meta.split()[2]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--integration", default="origin/claude/new-session-4cao7d")
    args = ap.parse_args()
    integ = tree(args.integration)
    by_blob = {}
    for p, b in integ.items():
        by_blob.setdefault(b, []).append(p)
    for br in BRANCHES:
        ref = "origin/" + br
        mb = git("merge-base", args.integration, ref).strip()
        head = git("rev-parse", "--short", ref).strip()
        btree = tree(ref)
        dirs = {os.path.dirname(p) for p in btree}
        dirs |= {os.path.dirname(d) for d in list(dirs)}
        changed = git("diff", "--name-only", "--no-renames", "--diff-filter=AM",
                      mb, ref).splitlines()
        for path in changed:
            blob = btree[path]
            r = role(path, dirs)
            if integ.get(path) == blob:
                status, where = "present", path
            elif blob in by_blob:
                status, where = "present-elsewhere", by_blob[blob][0]
            elif path in integ:
                status, where = "diverged", path
            else:
                status, where = "missing", "-"
            dest = port_path(path) if status == "missing" and r not in ("bulk", "infra") else "-"
            print(f"{br}\t{head}\t{r}\t{status}\t{path}\t{where}\t{dest}")


if __name__ == "__main__":
    sys.exit(main())
