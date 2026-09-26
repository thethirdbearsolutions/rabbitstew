"""RBT-72 adversary: paper 8 §2.2 table from RBT-67's manipulation JSON, per-robot means
recomputed, and the population it was run on (the abstract applies it to both)."""
import json, statistics as st, math
d = json.load(open("docs/artifacts/RBT-67/manipulation_384.json"))
print("population:", d["population"])
for k, v in d["summary"].items():
    pr = v["per_robot"]; m = st.mean(pr)
    h = 2.446912 * st.stdev(pr) / math.sqrt(len(pr)) if len(set(pr)) > 1 else 0
    print(f"{k:>14}: per-robot mean {m:+.4f} (t-CI [{m-h:+.3f}, {m+h:+.3f}], {sum(x>0 for x in pr)}/7 up); "
          f"bearing {v['bearing_grad']:.3f}; centroid {v['centroid_d']:.2f}")
