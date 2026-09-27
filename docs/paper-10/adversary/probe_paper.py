"""Paper 10 adversary, round 1: print-only probes on committed files (no simulation, no ecology run).

Run from the repository root:

    python docs/paper-10/adversary/probe_paper.py > docs/paper-10/adversary/probe_paper.txt

Each section is cited by letter in PAPER-ADVERSARY.md.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SEEDS = [801, 4, 804, 805, 806, 807, 1, 2, 3, 7]


def read(rel):
    return (ROOT / rel).read_text()


def rows(rel, arms):
    out = {}
    for ln in read(rel).splitlines():
        m = re.match(r"\| (\d+) \| (\w+) \|", ln)
        if m and m.group(2) in arms:
            out[(int(m.group(1)), m.group(2))] = [c.strip() for c in ln.strip("|").split("|")]
    return out


def kpl(cell):
    m = re.match(r"(\d+)\((\d+)\)/(\d+)/(\d+)", cell)
    return tuple(int(x) for x in m.groups())


print("Paper 10 adversary, round 1: probes on committed files")
print()

# A ------------------------------------------------------------------------------------------
print("A. The holistic claim (abstract l.29-31): what committed evidence is there?")
rep = read("runs/RBT-103/REPORT.md").splitlines()
for i, ln in enumerate(rep, 1):
    if "holistic" in ln:
        print(f"  runs/RBT-103/REPORT.md:{i}: {ln.strip()}")
for rel in ("runs/RBT-103/routed_populations.py",):
    for i, ln in enumerate(read(rel).splitlines(), 1):
        if "holistic" in ln:
            print(f"  {rel}:{i}: {ln.strip()}")
outs = sorted(p for p in (ROOT / "runs/RBT-103").rglob("*.txt"))
plan = [(p, ln.strip()) for p in outs for ln in p.read_text().splitlines() if "## Body plan" in ln or "CANNOT CARRY" in ln]
print(f"  committed RBT-103 .txt outputs with a body-plan line: {len(plan)}")
for p, ln in plan:
    print(f"    {p.relative_to(ROOT)}: {ln}")
print(f"  of which report a body that CANNOT CARRY the circuit: {sum(1 for _, ln in plan if 'CANNOT' in ln or not ln.endswith('7 of 7 bests can carry the circuit'))}")
print("  (no committed file names the holistic champions checked or how many there were)")
print()

# B ------------------------------------------------------------------------------------------
print("B. HU (uniform, default operator), per seed: k_planted/n/B at 300 and 599, and champions carrying a paying planted unit")
z = rows("runs/RBT-112/readout.txt", ("HU", "HZ"))
print("  | seed | HU held 300 k/n/B | above B at 300 | HU held 599 k/n/B | n = 0 at 599 | HU champions carrying (F12, of 7) |")
above300, lost599, carry = [], [], []
for s in SEEDS:
    r = z[(s, "HU")]
    a = kpl(r[9])
    b = kpl(r[10].split(",")[0])
    c = int(r[15].split("/")[0])
    if a[0] > a[3]:
        above300.append(s)
    if b[2] == 0:
        lost599.append(s)
    if c:
        carry.append(s)
    print(f"  | {s} | {a[0]}/{a[2]}/{a[3]} | {a[0] > a[3]} | {b[0]}/{b[2]}/{b[3]} | {b[2] == 0} | {c} |")
print(f"  HU seeds above B at 300: {above300}; HU seeds with n = 0 at 599: {lost599}; HU seeds with a carrying champion: {carry}")
print(f"  HU seeds above B at 300 whose planted-rooted living are gone by 599: {[s for s in above300 if s in lost599]}")
print()

# C ------------------------------------------------------------------------------------------
print("C. The 'ruled' HU sentence in the abstract and A3: 'Under the default operator they do neither'")
print(f"  HU COMPASS lines: {sum(1 for s in SEEDS if 'FOOD-DEPENDENT' in z[(s, 'HU')][13])}; HU champions carrying: "
      f"{sum(int(z[(s, 'HU')][15].split('/')[0]) for s in SEEDS)}/70 on seeds {carry}")
print()

# D ------------------------------------------------------------------------------------------
print("D. HP (patchy, default operator): the planted-rooted paying share k_planted / n at 300 and 599 (H-readout.txt)")
print("   HELD means k_planted > B at both readings; it does not mean the share rose. Founding: every planted-rooted genome pays.")
hp = rows("runs/RBT-106/H-readout.txt", ("HP",))
for s in SEEDS:
    r = hp[(s, "HP")]
    a = kpl(r[11])
    b = kpl(r[12].split(",")[0])
    print(f"  HP-{s}: 300 {a[0]}/{a[2]} = {a[0] / a[2]:.2f} (B {a[3]}); 599 {b[0]}/{b[2]} = {b[0] / b[2]:.2f} (B {b[3]}); HELD {r[13]}")
print()

# E ------------------------------------------------------------------------------------------
print("E. RBT-112 A1: the own-genealogy S = 0 null's 95th percentile against B, per HZ arm (readout-adversary/ADVERSARY.md table)")
for ln in read("runs/RBT-112/readout-adversary/ADVERSARY.md").splitlines():
    m = re.match(r"\| \**(\d+)\** \| (\d+) / (\d+) \| (\d+) / (\d+) \|", ln)
    if m:
        s, b3, p3, b5, p5 = (int(x) for x in m.groups())
        below = [lab for lab, b, p in (("300", b3, p3), ("599", b5, p5)) if p < b]
        print(f"  HZ-{s}: B/null95 at 300 {b3}/{p3}, at 599 {b5}/{p5}; null 95th pct below B at: {below or 'none'}")
print()

# F ------------------------------------------------------------------------------------------
print("F. P1-805: a COMPASS line from the sub-paying (w = 1, a = 2) planted founders (P1-readout.txt)")
p1 = rows("runs/RBT-106/P1-readout.txt", ("P1", "S1"))
r = p1[(805, "P1")]
print(f"  P1-805: F uniform {r[14]}; F patchy, attribution {r[15]}; lesion gain {r[16]}")
print(f"  S1-805 (its pair; install control failed): F patchy, attribution {p1[(805, 'S1')][15]}")
