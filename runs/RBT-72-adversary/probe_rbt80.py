"""RBT-72 adversary: paper 8 §2.4 [S1] from RBT-80's committed series, by own parser."""
import re
rows = []
sec = None
for line in open("docs/artifacts/RBT-80-series.txt"):
    if line.startswith("## "): sec = line
    if sec and "mean_lifetime_score" in sec and re.match(r"^\s+\d+\s", line):
        rows.append([float(x) for x in line.split()])
print(f"seasons parsed: {len(rows)} ({int(rows[0][0])}..{int(rows[-1][0])})")
for s, (i, j, k) in zip("ABC", ((1, 2, 3), (4, 5, 6), (7, 8, 9))):
    m = lambda c, rr=rows: sum(r[c] for r in rr) / len(rr)
    pl = [r for r in rows if 250 <= r[0] <= 299]
    print(f"seed {s}: seeded-control over all seasons {m(i)-m(j):+.3f}; plateau 250-299 {m(i,pl)-m(j,pl):+.3f}; "
          f"seeded-drift all {m(i)-m(k):+.3f}")
