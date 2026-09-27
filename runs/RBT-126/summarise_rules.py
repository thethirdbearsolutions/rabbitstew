"""RBT-126: the breeding-rule tables in BREEDING-RULES.md, from depth*.txt, invasion*.txt and retention*.txt."""
import collections, pathlib, re
HERE = pathlib.Path(__file__).resolve().parent
num = r"([-\d.na]+)"
D, I, R = {}, collections.defaultdict(dict), collections.defaultdict(dict)
for f in sorted(HERE.glob("depth*.txt")):
    for l in f.read_text().splitlines():
        m = re.match(rf"(\S+)\s+g0 {num} \| parents\s+{num}±\S+ \| age\s+{num}±\S+ \| gen/season {num}±\S+ \| births\s+{num} \| eligible {num} \| alive\s+{num}", l)
        if m:
            D[(m[1], float(m[2]))] = tuple(float(x) for x in m.groups()[2:])
for f in sorted(HERE.glob("invasion*.txt")):
    for l in f.read_text().splitlines():
        m = re.match(rf"(\S+)\s+g0 {num} x{num} \| share {num}±\S+ \| fix {num}", l)
        if m:
            I[(m[1], float(m[2]))][float(m[3])] = (float(m[4]), float(m[5]))
for f in sorted(HERE.glob("retention*.txt")):
    for l in f.read_text().splitlines():
        m = re.match(rf"(\S+)\s+gn {num} \| carriage {num}±{num}", l)
        if m:
            R[m[1]][float(m[2])] = (float(m[3]), float(m[4]))
rules = list(dict.fromkeys(r for r, _ in D))
G = sorted({g for _, g in D})
print("### Depth (neutral population, seasons 200-400): generations per season, and ratio to shuffle at the same g0 (collapse: fewer than 50 of 60 alive on average)\n")
print("| rule | " + " | ".join(f"g0 {g}" for g in G) + " |")
print("|---|" + "---|" * len(G))
for r in rules:
    cells = []
    for g in G:
        d, s = D.get((r, g)), D.get(("shuffle", g))
        if not d or d[5] < 50 or d[2] != d[2]:
            cells.append("collapse" if d and d[5] < 50 else "-"); continue
        cells.append(f"{d[2]:.4f} ({d[2]/s[2]:.2f}×)")
    print(f"| {r} | " + " | ".join(cells) + " |")
for idx, name in ((0, "distinct parents in 200 seasons"), (1, "mean age at breeding")):
    print(f"\n### {name}\n")
    print("| rule | " + " | ".join(f"g0 {g}" for g in G) + " |")
    print("|---|" + "---|" * len(G))
    for r in rules:
        print(f"| {r} | " + " | ".join(("collapse" if D[(r, g)][5] < 50 else f"{D[(r, g)][idx]:.0f}" if idx == 0 else f"{D[(r, g)][idx]:.1f}") if (r, g) in D else "-" for g in G) + " |")
for mult in (1.25, 2.0):
    print(f"\n### Invasion: ×{mult} mutant, 6 of 60, 400 seasons: mean share / fixation (neutral share 0.10)\n")
    print("| rule | " + " | ".join(f"g0 {g}" for g in G) + " |")
    print("|---|" + "---|" * len(G))
    for r in rules:
        print(f"| {r} | " + " | ".join((f"{I[(r, g)][mult][0]:.2f} / {I[(r, g)][mult][1]:.2f}" if mult in I.get((r, g), {}) else "-") for g in G) + " |")
print("\n### Retention at RBT-80's numbers: carriage at season 300 (±SE); in brackets, minus the rule's own neutral floor (gn = 1.05)\n")
GN = sorted({g for r in R.values() for g in r})
print("| rule | " + " | ".join(f"gn {g}" for g in GN) + " |")
print("|---|" + "---|" * len(GN))
for r in list(dict.fromkeys(rules + list(R))):
    if r not in R: continue
    fl = R[r].get(1.05, (float("nan"),))[0]
    print(f"| {r} | " + " | ".join(f"{R[r][g][0]:.3f}±{R[r][g][1]:.3f} ({R[r][g][0]-fl:+.2f})" if g in R[r] else "-" for g in GN) + " |")
