"""RBT-98 item 4: files a REPORT cites that exist on no branch at all.

For each REPORT.md on the audited branches (audit.py's BRANCHES), pull out every token that
names a file (a word ending in a known extension), resolve it against every remote-tracking
branch, and print where it lives. A cited file found on no branch is a lost artifact.

Resolution, most specific first: the token as a repository path; the token relative to the
REPORT's own directory; then any path on any branch that ends in "/" + token (a bare name
such as `probe.txt` matches any `.../probe.txt`, so a bare-name hit is weaker evidence and
is marked "suffix"). Needs every branch fetched (blob-less is enough):

    git fetch --filter=blob:none origin '+refs/heads/*:refs/remotes/origin/*'
    python runs/RBT-98/citations.py > runs/RBT-98/citations.txt
"""
import os
import re
import subprocess

from audit import BRANCHES, git

EXT = r"(?:txt|py|sh|json|jsonl|md|log|csv|html|gz|npz|traj|TXT)"
TOKEN = re.compile(r"(?<![\w./-])([\w.\-/*{}]+\." + EXT + r")(?![\w])")
INTEGRATION = "origin/claude/new-session-4cao7d"


def refs():
    out = git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin")
    return [r for r in out.split() if r != "origin/HEAD" and not r.startswith("origin/ckpt/")]


def main():
    trees = {r: set(git("ls-tree", "-r", "--name-only", r).splitlines()) for r in refs()}
    everywhere = {}
    for r, paths in trees.items():
        for p in paths:
            everywhere.setdefault(p, []).append(r)
    seen = set()
    for br in BRANCHES:
        ref = "origin/" + br
        reports = [p for p in trees[ref] if p.endswith("REPORT.md")
                   and git("diff", "--name-only", git("merge-base", INTEGRATION, ref).strip(),
                           ref, "--", p).strip()]
        for rep in reports:
            if (rep, git("rev-parse", f"{ref}:{rep}").strip()) in seen:
                continue
            seen.add((rep, git("rev-parse", f"{ref}:{rep}").strip()))
            text = git("show", f"{ref}:{rep}")
            base = os.path.dirname(rep)
            for tok in sorted(set(TOKEN.findall(text))):
                if any(c in tok for c in "*{}") or tok.startswith(("http", "www.")):
                    print(f"{br}\t{rep}\t{tok}\tpattern\t-")
                    continue
                hit, how = None, None
                for cand in (tok.lstrip("./"), os.path.normpath(os.path.join(base, tok))):
                    if cand in everywhere:
                        hit, how = cand, "path"
                        break
                if hit is None:
                    suf = [p for p in everywhere if p.endswith("/" + tok) or p == tok]
                    near = [p for p in suf if p.startswith(base + "/")]
                    if suf:
                        hit, how = (near or sorted(suf))[0], "suffix" if not near else "path"
                if hit is None:
                    print(f"{br}\t{rep}\t{tok}\tLOST\t-")
                    continue
                on = everywhere[hit]
                where = "integration" if INTEGRATION in on else on[0].replace("origin/", "")
                print(f"{br}\t{rep}\t{tok}\t{how}\t{hit} @ {where}")


if __name__ == "__main__":
    main()
