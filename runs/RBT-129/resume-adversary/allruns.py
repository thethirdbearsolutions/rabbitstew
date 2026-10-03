# Structural double-write check of EVERY checkpointed Stage-1 run dir (not only resumed ones). Counts only.
import sys, os, json
sys.path.insert(0, "/tmp/claude-0/wt/pr/runs/RBT-129/launch")
import resumed as R
runs, srcs = R.lane_dirs(os.path.join(R.RUNS, "lanes", "1"))
got = R.fetch([R.label(d) for d in runs + srcs])
out = {"runs": [], "sources": []}
for kind, ds in (("runs", runs), ("sources", srcs)):
    for d in ds:
        lab = R.label(d)
        if lab not in got:
            continue
        rec = R.report(d, lab, got, sources=True)
        rec.pop("resume_utc", None)
        out[kind].append(rec)
json.dump(out, open("/tmp/claude-0/allruns.json", "w"), indent=1)
for kind in ("runs", "sources"):
    rs = out[kind]
    bad = [r["dir"] for r in rs if R.double_written(r)]
    print(f"{kind}: {len(rs)} checkpointed, {sum(1 for r in rs if r['resumes'])} with a resume record, "
          f"{sum(1 for r in rs if not r['resumes'])} never resumed; written twice: {len(bad)} {bad}")
