# Saved census (ckpt branch) vs a clean re-run from season 0 at the PR head: counts/indices only.
import sys, os, json
sys.path.insert(0, "/tmp/claude-0/wt/pr/runs/RBT-129/launch")
import stages
saved, rerun = "/tmp/claude-0/census/S", "/tmp/claude-0/rerun/S"
v, lines = stages.k1_compare(saved, rerun)
print("k1_compare(saved, rerun):", v, "|", lines[0] if lines else "", "|", [l for l in lines if "DIFFERS" in l or "only" in l][:6])
a, b = stages.output_files(saved), stages.output_files(rerun)
same = sum(1 for k in a if k in b and open(a[k], "rb").read() == open(b[k], "rb").read())
print(f"files: saved {len(a)}, rerun {len(b)}, byte-identical {same}; differing: {sorted(k for k in a if k in b and open(a[k],'rb').read()!=open(b[k],'rb').read())}; only saved {sorted(set(a)-set(b))[:5]}; only rerun {sorted(set(b)-set(a))[:5]}")
for name in ("lineage.jsonl", "cohorts.jsonl"):
    S = [l for l in open(os.path.join(saved, name)) if l.strip()]
    R = [l for l in open(os.path.join(rerun, name)) if l.strip()]
    seen, ded = set(), []
    for l in S:
        if l not in seen:
            seen.add(l); ded.append(l)
    print(f"{name}: saved {len(S)}, rerun {len(R)}, saved de-duplicated (first occurrence) {len(ded)}; de-dup == rerun (order too): {ded == R}; "
          f"lines only in saved {len(set(S)-set(R))}, only in rerun {len(set(R)-set(S))}")
for kind in ("conventional", "holistic"):
    v, l = stages.half_compare(rerun, saved, kind)
    print("half_compare(rerun, saved,", kind, "):", v, "| dropped note:", "dropped" in l[0], [x for x in l[1:]])
