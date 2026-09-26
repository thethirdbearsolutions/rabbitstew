"""RBT-72 adversary: what the 35/48/1 re-signing (paper 8 §3.4) actually signs.

runs/RBT-91/resign_arrivals.py signs the WHOLE-BRAIN small-signal response ('raw a'),
and classifies `signed > 0` as COMPASS, else ANTI-COMPASS, so an exact zero is an
anti-compass. This probe joins the committed re-signing table to the committed
links-alone column (same 84 lineages) and recounts, with no simulation."""
import re, math

def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return 100*(c - h), 100*(c + h)

T = re.compile(r"^\| (\S+) #(\d+) \| ([+-][\d.]+) \| (.*?) \| .*?\| (\S+) \| .*\| \**([A-Z-]+)\** \|$")
rs = {}
for line in open("docs/artifacts/RBT-91-resigned-84-reference.txt"):
    m = T.match(line.strip())
    if m:
        rs[(m[1], int(m[2]))] = dict(raw=float(m[3]), drives=m[5], verdict=m[6])
L = re.compile(r"^\s+(\S+) lineage (\d+): \d+ unit\(s\), LINKS ALONE ([+-][\d.]+) .*whole brain ([+-][\d.]+)")
al = {}
for line in open("docs/artifacts/RBT-91-alone-baseline.txt"):
    m = L.match(line)
    if m:
        al[(m[1], int(m[2]))] = (float(m[3]), float(m[4]))
assert set(rs) == set(al), (len(rs), len(al))
print(f"joined {len(rs)} arrivals; whole-brain column equals 'raw a' on all: "
      f"{all(abs(rs[k]['raw'] - al[k][1]) < 5e-5 for k in rs)}")

v = [r["verdict"] for r in rs.values()]
print(f"as committed: COMPASS {v.count('COMPASS')}, ANTI-COMPASS {v.count('ANTI-COMPASS')}, UNDETERMINED {v.count('UNDETERMINED')}")
zeros = [k for k, r in rs.items() if r["verdict"] != "UNDETERMINED" and abs(r["raw"]) < 5e-5]
print(f"resolved arrivals whose whole-brain response prints as 0.0000: {len(zeros)}, all ANTI: "
      f"{all(rs[k]['verdict'] == 'ANTI-COMPASS' for k in zeros)}")
c, a = v.count("COMPASS"), v.count("ANTI-COMPASS") - len(zeros)
print(f"  zeros excluded as unsigned: {c} / {c + a} = {100*c/(c+a):.1f}% {wilson(c, c+a)}")

for thr in (1e-4, 1e-3, 1e-2):
    cc = aa = 0
    for k, r in rs.items():
        if r["verdict"] == "UNDETERMINED": continue
        own = al[k][0]
        if abs(own) < thr: continue
        s = own if r["drives"] == "backward" else -own
        cc += s > 0; aa += s < 0
    print(f"motif's OWN links re-signed by the same direction, |own| >= {thr:g}: compass {cc}, anti {aa}, "
          f"{100*cc/(cc+aa):.1f}% {tuple(round(x,1) for x in wilson(cc, cc+aa))}")
agree = sum(1 for k, r in rs.items() if r["verdict"] != "UNDETERMINED" and abs(al[k][0]) >= 1e-4 and abs(al[k][1]) >= 1e-4 and al[k][0]*al[k][1] > 0)
both = sum(1 for k, r in rs.items() if r["verdict"] != "UNDETERMINED" and abs(al[k][0]) >= 1e-4 and abs(al[k][1]) >= 1e-4)
print(f"own-link sign agrees with whole-brain sign where both are non-zero: {agree}/{both}")

# The committed 42.2% itself, recomputed, and z against 0.5
lo, hi = wilson(35, 83)
print(f"\ncommitted figure recomputed: 35/83 = {100*35/83:.1f}% [{lo:.1f}, {hi:.1f}], z = {(35/83 - 0.5)/math.sqrt(0.25/83):+.2f}")

# Paper 8 §6.1 / §10: 'below one in a hundred thousand lineages is the bound'
cond_hi = wilson(0, 84)[1] / 100
rate = 84 / 200000
rate_hi_deff = rate + 1.959964 * math.sqrt(rate * (1 - rate) / 200000) * 3.0   # RBT-45 design effect 9 -> x3 on the SE
print(f"paper's product: {cond_hi:.4f} x {rate:.5f} x 0.422 = {cond_hi*rate*0.422:.2e}")
print(f"every factor at its own upper end (Wilson 0/84; rate with sqrt(9) design effect {rate_hi_deff:.5f}; sign 52.9%): "
      f"{cond_hi*rate_hi_deff*0.529:.2e}; with own-link sign upper 64.1%: {cond_hi*rate_hi_deff*0.641:.2e}")
