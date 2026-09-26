"""RBT-110 readout adversary: does the simulated split track what the ecology itself recorded near T + 110?

C1's cross-check correlated the simulated paired TOTAL at T + 110 with the recovery R-body from the committed tables
and got r = +0.22 (C4: +0.80).  R-body is a window mean of mean_lifetime_score over [T+60, T+160): a lifetime-mean
axis (lag-1 autocorrelation 0.69, paper 9 lesson 4), not the per-bout gain of the population alive at T + 110.
This probe builds the like-for-like observed quantity from restored bulk (README rule 6): each robot's recorded
gain in the season it played (lineage.jsonl last_score at its generation), averaged over the fauna, in
    (i)  the single season T + 110 (the simulated population, one recorded start seed and terrain)
    (ii) the window [T + 100, T + 120) (21 seasons; neighbouring populations, many draws)
for the shift arm (on its own, new world) and the baseline (old world), so
    observed TOTAL = recorded gain(shift arm) - recorded gain(baseline)       per fauna, then paired,
the recorded counterpart of the split's TOTAL = gain(shift pop, new) - gain(base pop, old).
It prints both beside the analysts' simulated TOTAL (parsed from each committed split.txt) and their per-seed
correlation, and the same against R-body (C1's cross-check).

    python runs/RBT-110/readout-adversary/probe_observed.py BULK > runs/RBT-110/readout-adversary/probe_observed.txt
"""
import json
import os
import statistics as st
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-92"))
os.chdir(ROOT)
import readout as R  # noqa: E402

SEEDS, KINDS, TS = R.SEEDS, R.KINDS, R.onsets()
SHIFT = {"C1": "s92", "C2": "s99", "C3": "s100", "C4null": "s101"}
TABLE = {"C1": "runs/RBT-92/shift-{s}", "C2": "runs/RBT-99/shift-{s}", "C3": "runs/RBT-100/shift-{s}",
         "C4null": "runs/RBT-101/shift-{s}"}


def recorded(run, lo, hi):
    """mean recorded gain per (fauna, season) for seasons in [lo, hi)"""
    acc = {}
    last = int(json.load(open(f"{run}/state.json"))["season"])
    for line in open(f"{run}/lineage.jsonl"):
        x = json.loads(line)
        g = x["generation"]
        if lo <= g < hi and g < last and "food" in x and x.get("last_score") is not None:
            acc.setdefault((x["population"], g), []).append(x["last_score"])
    return {k: st.fmean(v) for k, v in acc.items()}


def paired_total(sh, ba, seasons):
    out = []
    for k in KINDS:
        v = [sh[(k, s)] - ba[(k, s)] for s in seasons if (k, s) in sh and (k, s) in ba]
        if not v:
            return None
        out.append(st.fmean(v))
    return out[0] - out[1]  # holistic - conventional


def sim_total(part):
    L = subprocess.run(["git", "show", f"origin/results/RBT-110-{part}:runs/RBT-110/{part}/split.txt"],
                       capture_output=True, text=True, check=True).stdout.splitlines()
    if part == "C4null":
        i = next(j for j, x in enumerate(L) if x.startswith("REPRODUCTION"))
        j = next(j for j in range(i, len(L)) if "TOTAL (simulated event - base)" in L[j])
        blob = L[j]
    else:
        sec = {"C1": "==== T + 110 ", "C2": "=== T + 110", "C3": "=== r = 110 "}[part]
        i = next(j for j, x in enumerate(L) if x.startswith(sec))
        i = next(j for j in range(i, len(L)) if L[j].startswith("paired"))
        j = next(j for j in range(i, len(L)) if L[j].strip().startswith("TOTAL"))
        blob = L[j] if "per seed [" in L[j] else L[j + 1]
    toks = blob.split("per seed [")[1].split("]")[0].split(",")
    return [None if t.strip().split(":")[-1].strip() in ("n/a", "n/c") else float(t.strip().split(":")[-1]) for t in toks]


def corr(a, b):
    idx = [i for i in range(len(a)) if a[i] is not None and b[i] is not None]
    return st.correlation([a[i] for i in idx], [b[i] for i in idx]), len(idx), idx


def main(bulk):
    print(__doc__.split("\n\n")[0])
    print()
    for part in SHIFT:
        sim = sim_total(part)
        one, win, rb = [], [], []
        for s in SEEDS:
            T = TS[s]
            sh = recorded(f"{bulk}/{SHIFT[part]}-{s}", T + 100, T + 120)
            ba = recorded(f"{bulk}/base-{s}", T + 100, T + 120)
            one.append(paired_total(sh, ba, [T + 110]))
            win.append(paired_total(sh, ba, range(T + 100, T + 120)))
            rb.append(R.rbody(R.Arm(TABLE[part].format(s=s)), T + 60, T + 160)
                      - R.rbody(R.Arm(f"runs/RBT-90/forage-{s}"), T + 60, T + 160))
        print(f"{part}: paired TOTAL per seed ({' '.join(map(str, SEEDS))})")
        for lab, v in (("simulated at T+110 (analyst's split.txt)", sim), ("recorded, season T+110", one),
                       ("recorded, window [T+100, T+120)", win), ("R-body, [T+60, T+160) (tables)", rb)):
            vv = [x for x in v if x is not None]
            print(f"   {lab:42s} mean {st.fmean(vv):+.3f} sd {st.stdev(vv):.3f}  [" +
                  ", ".join("  .   " if x is None else f"{x:+.3f}" for x in v) + "]")
        for lab, v in (("recorded T+110", one), ("recorded window", win), ("R-body", rb)):
            c, n, _ = corr(sim, v)
            print(f"   r(simulated, {lab}) = {c:+.2f}  (n {n})")
        c, n, _ = corr(win, rb)
        print(f"   r(recorded window, R-body) = {c:+.2f}  (n {n})")
        print()


if __name__ == "__main__":
    main(sys.argv[1])
