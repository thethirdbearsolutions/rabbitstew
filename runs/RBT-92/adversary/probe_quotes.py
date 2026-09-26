"""RBT-92 adversary probe F: are Amendment 1's quotations of docs/held-out-challenges.md verbatim?

Every '>' block of PREREGISTRATION.md at PR #76's head (a3658f9) is whitespace-normalised and looked
up in the doc; a block that is not found prints each of its lines and whether that line is found.

    git show a3658f9:runs/RBT-92/PREREGISTRATION.md > /tmp/p.md
    python runs/RBT-92/adversary/probe_quotes.py /tmp/p.md > runs/RBT-92/adversary/probe_quotes.txt
"""
import re
import sys

P = open(sys.argv[1]).read()
D = open("docs/held-out-challenges.md").read()
norm = lambda s: " ".join(s.split())
dn = norm(D)
print(__doc__.split("\n\n")[0])
for q in re.findall(r"((?:^> ?.*\n)+)", P, re.M):
    body = [l[2:] if l.startswith("> ") else l[1:] for l in q.splitlines()]
    ok = norm("\n".join(body)) in dn
    print(f"block of {len(body)} lines, first: {body[0][:70]!r}: verbatim {ok}")
    if not ok:
        seen = set()
        for l in body:
            if norm(l) and (norm(l) not in dn or l in seen):
                print(f"   line {'not in the doc' if norm(l) not in dn else 'repeated'}: {l!r}")
            seen.add(l)
