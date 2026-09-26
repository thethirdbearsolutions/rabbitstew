"""RBT-72 adversary: re-derive paper 8's prize numbers (§2.1, §2.3) from RBT-67's
per-seed JSON by independent code, and the per-robot re-signing that RBT-97 §1 reports."""
import json, math, statistics as st

T6 = 2.446912  # t(0.975, 6)
T4 = 2.776445  # t(0.975, 4)
def tci(xs, t):
    m = st.mean(xs); h = t * st.stdev(xs) / math.sqrt(len(xs)); return m, m - h, m + h

a = json.load(open("docs/artifacts/RBT-67/seedset_anchor.json"))
base = st.mean(a["baseline"].values()); d = a["per_robot_delta_64"]
m, lo, hi = tci(d, T6)
print(f"anchor (seeds 9000+): baseline {base:.4f}; a=64 mean {st.mean(d):.4f} = {st.mean(d)/base:+.1%}; "
      f"t-CI [{lo:.3f}, {hi:.3f}] vs file {a['delta_64'][1:]}; improved {sum(x>0 for x in d)}/7")

def robots(path):
    j = json.load(open(path)); out = {}
    for c in j["cells"]:
        for r in c.get("robots", []):
            out.setdefault(r["gen"], {})[c["a"]] = (r["items"], sum(r["diffs"]) / len(r["diffs"]))
    return j, out

w, wr = robots("docs/artifacts/RBT-67/w4b.json")
b0 = st.mean(v[0.0][0] for v in wr.values())
print(f"\nW4b ladder (seeds 7000+), baseline {b0:.4f}")
for A in w["ladder_a"]:
    ds = [wr[g][A][1] for g in sorted(wr)]
    m, lo, hi = tci(ds, T6)
    print(f"  a={A:>5.0f}: {m:+.4f} [{lo:+.3f}, {hi:+.3f}] {sum(x>0 for x in ds)}/7  ({m/b0:+.1%})")

p, pr = robots("docs/artifacts/RBT-67/p801.json")
fwd, bwd = [0, 200, 300, 500, 590], [100, 400]
bf = st.mean(pr[g][0.0][0] for g in fwd)
print(f"\nP-801 ladder, own (population) sign; forward-five baseline {bf:.4f}, all-seven {st.mean(pr[g][0.0][0] for g in pr):.4f}")
neg = 0; tot = 0
for A in p["ladder_a"]:
    f = [pr[g][A][1] for g in fwd]; bk = [pr[g][A][1] for g in bwd]
    m, lo, hi = tci(f, T4)
    if A >= 64: neg += sum(x < 0 for x in bk); tot += 2
    print(f"  a={A:>5.0f}: fwd5 {m:+.4f} [{lo:+.3f}, {hi:+.3f}] {sum(x>0 for x in f)}/5 ({m/bf:+.1%}); bwd2 {st.mean(bk):+.4f} ({sum(x<0 for x in bk)}/2 negative)")
print(f"  backward two negative at a>=64: {neg}/{tot}")

print("\nRBT-97 §1 per-robot re-signing (12 correctly signed = 7 W4b + 5 P-801 forward):")
for A in p["ladder_a"]:
    ds = [wr[g][A][1] for g in sorted(wr)] + [pr[g][A][1] for g in fwd]
    anti = [pr[g][A][1] for g in bwd]
    m, lo, hi = tci(ds, 2.200985)
    print(f"  a={A:>5.0f}: compass n=12 {m:+.3f} [{lo:+.3f}, {hi:+.3f}] {sum(x>0 for x in ds)}/12; anti n=2 {st.mean(anti):+.3f} {sum(x>0 for x in anti)}/2 better")
