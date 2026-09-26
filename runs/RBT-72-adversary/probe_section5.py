"""RBT-72 adversary, last look at paper 8 §5 (final): re-derive its numbers from the files it
cites, by own parsing and own statistics (t over robots). No simulation."""
import json, math, re, statistics as st

T = {4: 2.776445, 6: 2.446912, 63: 1.998341}
def tci(xs):
    m = st.mean(xs); h = T[len(xs) - 1] * st.stdev(xs) / math.sqrt(len(xs)); return m, m - h, m + h
def fmt(x): return f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]"

# §5.1 routed motif on P-801
rows = re.findall(r"^(g\d+)\s+[+-][\d.]+°\s+[+-]1\s+[\d.]+ \|\s+([+-][\d.]+) \|\s+([+-][\d.]+)$",
                  open("docs/artifacts/RBT-97-routed-p801.txt").read(), re.M)
for j, w in ((1, 16), (2, 32)):
    d = [float(r[j]) for r in rows]
    print(f"§5.1 routed P-801 w={w}: {fmt(tci(d))}, {sum(x > 0 for x in d)}/{len(d)} improved; "
          f"not improved: {[r[0] + ' ' + r[j] for r in rows if float(r[j]) <= 0]}")

# §5.3 / §5.4(1): pooled motif - decoy from per-robot rows
def mech(path):
    out = {}
    for g, a, mo, ph in re.findall(r"^(g\d+)\s+[+-]1\s+(\d+) \|\s+[\d.]+\s+([+-][\d.]+)\s+([+-][\d.]+)", open(path).read(), re.M):
        out.setdefault(int(a), {})[g] = (float(mo), float(ph))
    return out
def rot(pop):
    t = open("runs/RBT-97/adversary_rotated.txt").read().split(f"== {pop}")[1].split("== ")[0]
    out = {}
    for blk in re.split(r"a = (\d+)\s+per robot", t)[1:]:
        pass
    parts = re.split(r"\n\s+a = (\d+)\s+per robot", t)
    for a, body in zip(parts[1::2], parts[2::2]):
        out[int(a)] = {g: (float(m), float(r)) for g, m, r in re.findall(r"(g\d+)\s+motif\s+([+-][\d.]+)\s+rotated\s+([+-][\d.]+)", body)}
    return out
for pop, path in (("p801", "docs/artifacts/RBT-97-p801-mechanism.txt"), ("w4b", "docs/artifacts/RBT-97-w4b-control.txt")):
    M, R = mech(path), rot(pop)
    for a in (64, 384):
        gs = sorted(M[a]); mo = [M[a][g][0] for g in gs]; ph = [M[a][g][1] for g in gs]; ro = [R[a][g][1] for g in gs]
        assert all(abs(R[a][g][0] - M[a][g][0]) < 1e-3 for g in gs)
        print(f"§5.3 {pop} a={a}: motif {fmt(tci(mo))}; motif-static {fmt(tci([x - y for x, y in zip(mo, ph)]))} "
              f"retains {100*st.mean(ph)/st.mean(mo):+.1f}%; motif-rotated {fmt(tci([x - y for x, y in zip(mo, ro)]))} "
              f"retains {100*st.mean(ro)/st.mean(mo):+.1f}%; rotated alone {fmt(tci(ro))}")
        if pop == "p801" and a == 64:
            k = [g for g in gs if g != "g500"]
            print(f"   without g500: rotated retains {100*st.mean(R[a][g][1] for g in k)/st.mean(M[a][g][0] for g in k):+.1f}%")

# §5.2: per-robot 64-seed t-intervals above zero, the 12 correctly signed robots
def robots(path):
    out = {}
    for c in json.load(open(path))["cells"]:
        for r in c.get("robots", []):
            out.setdefault(r["gen"], {})[c["a"]] = r["diffs"]
    return out
w, p = robots("docs/artifacts/RBT-67/w4b.json"), robots("docs/artifacts/RBT-67/p801.json")
twelve = [w[g] for g in sorted(w)] + [p[g] for g in (0, 200, 300, 500, 590)]
for a in (32.0, 64.0):
    lo = [tci(r[a])[1] for r in twelve]
    print(f"§5.2 a={a:.0f}: {sum(x > 0 for x in lo)}/12 robots with own 64-seed t-interval above zero")
print(f"§5.2 pooled a=32: W4b {st.mean(st.mean(w[g][32.0]) for g in w):+.3f}, P-801 fwd {st.mean(st.mean(p[g][32.0]) for g in (0,200,300,500,590)):+.3f}")
