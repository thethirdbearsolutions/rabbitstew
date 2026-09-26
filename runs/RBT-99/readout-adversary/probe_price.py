"""RBT-99 readout adversary: price.txt re-derived from the baselines' pre-onset bulk, and its window sensitivity.

README rule 6 allows pre-T bulk: the RBT-90 part 2 baselines restored with
`scripts/durable.sh restore BULKDIR/forage-SEED rbt-90-SEED`.  Only lineage.jsonl rows with generation < T are read
(asserted below); no table and no post-T row is read from a checkpoint.

  1  runs/RBT-99/price.py BULKDIR, diffed against the committed price.txt
  2  every row price.py's window can read has generation < T, and the window is exactly Amendment 1's [T-40, T)
  3  the price and the paired arithmetic prediction under other pre-T windows ([T-20, T), [T-60, T), [T-100, T)):
     could the window have been tuned toward the headline?

    python runs/RBT-99/readout-adversary/probe_price.py BULKDIR > runs/RBT-99/readout-adversary/probe_price.txt
"""
import json
import os
import statistics as st
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
BULK = sys.argv[1]
KINDS = ("holistic", "conventional")
T_OF = {int(l.split("\t")[0]): int(l.split("\t")[1]) for l in open("runs/RBT-92/onset.txt")
        if l.split("\t")[0].lstrip("-").isdigit() and l.split("\t")[1].strip().isdigit()}

print("RBT-99 readout adversary: price.txt re-derived from pre-onset bulk (README rule 6)")
out = subprocess.run([sys.executable, "runs/RBT-99/price.py", BULK], capture_output=True, text=True).stdout
same = out == open("runs/RBT-99/price.txt").read()
print(f"1  price.py on the restored baselines: {'byte-identical to the committed price.txt' if same else 'DIFFERS from price.txt'}")
if not same:
    print(out)

print("2  rows in each seed's lineage.jsonl, by relation to T (price.py filters T-40 <= generation < T):")
kj = {}
for seed, T in T_OF.items():
    n_pre = 0
    rows = {k: [] for k in KINDS}
    for line in open(os.path.join(BULK, f"forage-{seed}", "lineage.jsonl")):
        r = json.loads(line)
        g = r["generation"]
        if g >= T:
            continue  # post-T bulk: never read (rule 6)
        n_pre += 1
        if "work" in r and r.get("death") != "cull":
            rows[r["population"]].append((g, r["work"] / 1000))
    assert all(g < T for k in KINDS for g, _ in rows[k])
    kj[seed] = rows
    print(f"   {seed:>4} T={T}: pre-T rows read {n_pre}; generations read {min(g for g, _ in rows['holistic'])}.."
          f"{max(g for k in KINDS for g, _ in rows[k])} (< T)")

print("3  window sensitivity (all pre-T): mean price per fauna over seeds, and the paired arithmetic prediction")
print("   window      price hol  price con  arith paired (con - hol)  min..max per seed")
for W in (20, 40, 60, 100):
    ph, pc, ap = [], [], []
    for seed, T in T_OF.items():
        h = 0.05 * st.fmean(v for g, v in kj[seed]["holistic"] if T - W <= g < T)
        c = 0.05 * st.fmean(v for g, v in kj[seed]["conventional"] if T - W <= g < T)
        ph.append(h)
        pc.append(c)
        ap.append(c - h)
    tag = "  <- Amendment 1's window, price.txt" if W == 40 else ""
    print(f"   [T-{W:>3}, T)  {st.fmean(ph):9.4f}  {st.fmean(pc):9.4f}  {st.fmean(ap):+24.4f}  {min(ap):+.3f}..{max(ap):+.3f}{tag}")
