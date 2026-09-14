"""Does forage_lab.py return the same numbers on a re-run of the same best?

Background, and the reason this exists: the first g590 attempt was killed at 26 of 34 modes on a
progress check of mine that did not match the row format (report section 7.4). The table was re-run
from scratch. Comparing the rows the two attempts share is a free determinism check on the
instrument -- the bout seeds are fixed (8000 + s) and the null layouts are drawn from the world's own
food seed, so every row SHOULD come back identical.

PROVENANCE LIMIT, stated because it changes what a match means: I relaunched to the same path without
saving the partial, so the original bytes are gone. `lab_g590.killed-partial.txt` is transcribed from
the tool-output rendering of that file, which is a faithful cat but not the file. A match therefore
establishes that the printed numbers agree to the precision printed -- NOT bit-identity of the files.

usage: determinism_check.py [OLD] [NEW]
"""
import re
import sys

OLD = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-84/lab_g590.killed-partial.txt"
NEW = sys.argv[2] if len(sys.argv) > 2 else "runs/RBT-84/lab_g590.txt"
# The second field must start a number: the completed table also carries a prose line
# "intact against its own gait: ..." which a looser pattern matches as an `intact` row and
# then overwrites the real one with -- a false DIVERGENCE this check reported on its first run.
ROW = re.compile(r"^(intact|no_\w+|lesion:\d+)\s+([-+.\d].*?)\s*$")


def rows(path):
    out = {}
    for line in open(path):
        if line.startswith("#"):
            continue
        m = ROW.match(line.rstrip("\n"))
        if m:
            # the trailing unit description is commentary; compare the numeric columns only
            out[m.group(1)] = tuple(m.group(2).split()[:10])
    return out


a, b = rows(OLD), rows(NEW)
shared = [k for k in a if k in b]
agree = [k for k in shared if a[k] == b[k]]
print(f"old: {OLD}  ({len(a)} rows)")
print(f"new: {NEW}  ({len(b)} rows)")
print(f"rows in both: {len(shared)}   agreeing on every printed column: {len(agree)}")
for k in shared:
    if a[k] != b[k]:
        print(f"  DIFFER {k}\n    old {' '.join(a[k])}\n    new {' '.join(b[k])}")
if len(b) < len(a):
    print(f"  (the new table is still being written: {len(a) - len(shared)} of the old rows not yet reached)")
print("VERDICT:", "IDENTICAL on every shared row" if len(agree) == len(shared) and shared
      else "DIVERGENCE -- see above" if shared else "no shared rows")
