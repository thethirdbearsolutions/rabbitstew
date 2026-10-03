"""Adversary: census founding at the 36 Stage-1 points, per census seed (holistic H, designed D alive at 59 before refill)."""
import json, os
S = os.environ.get('DATA', 'data') + '/0'
def alive(pt, s, k):
    h = json.load(open(f'{S}/{pt}/{s}/S/history.json'))['history']
    e = [x for x in h if x['season'] == 59 and x['population'] == k]
    return bool(e) and e[0]['alive'] - e[0]['births'] > 0
pts = [f"{c}-{p}-{L}-G" for c in ("c0", "c1", "c2") for p in ("p010", "p030", "p080") for L in ("U", "HP", "PW")] + \
      [f"c1-{p}-{L}-L" for p in ("p010", "p030", "p080") for L in ("U", "HP", "PW")]
n1 = 0; dd = 0; rows = []
for pt in pts:
    st = {s: (alive(pt, s, 'holistic'), alive(pt, s, 'conventional')) for s in (129001, 129002, 129003)}
    v1 = st[129001][0] and st[129001][1]; n1 += v1
    dlost = sum(not d for _, d in st.values()); dd += dlost > 0
    rows.append(f"  {pt:14s} " + "  ".join(f"{s % 1000}:{'H' if h else '-'}{'D' if d else '-'}" for s, (h, d) in st.items()) + f"   129001 valid@59: {'yes' if v1 else 'NO'}")
print("\n".join(rows))
print(f"Stage-1 points where 129001 has both faunas at 59: {n1} of 36; points where the designed fauna died on >= 1 census seed: {dd}")
