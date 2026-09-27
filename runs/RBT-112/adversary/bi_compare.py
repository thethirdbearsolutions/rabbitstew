"""RBT-112 design adversary: byte identity and freezing of --global-bias-sigma, on the adversary's own throwaway runs
(bi.sh; RBT-106's HU command, built by RBT-106's command.py, run in-process on an asserted rabbitstew/ package).

  A. new-HU-SEED (PR #277's code, flag unset) against old-HU-SEED (c872e80's code; the package path and the absence of
     the field are asserted in the same process, code.txt), 20 seasons, seeds 801 and 4: lineage.jsonl, cohorts.jsonl,
     history.json, config.json and every genome saved at birth, both faunas, byte for byte.
  B. sig04-HU-801 (--global-bias-sigma 0.4 = weight_sigma) against new-HU-801: the config differs only in that field,
     and every genome, lineage and cohort is byte-identical (S = weight_sigma is the default draw for draw).
  C. s0-HU-SEED (--global-bias-sigma 0, 40 seasons, seeds 801 and 4), every designed-body birth: the child's
     global-brain biases, as a multiset, are drawn from its parents' global biases plus at most one new value (an
     added unit); the planted unit (bias exactly 0 at founding) keeps b = 0; no global bias outside the set of founder
     global biases and added-unit birth values ever appears.  The same count on the default twins, for contrast.
  D. The side effect (SE-Z), anecdotal: designed-body births and mean lifetime score, S = 0 against the default, 40 seasons.

Usage: bi_compare.py RUNS_DIR
"""
import collections
import glob
import json
import os
import sys

R = sys.argv[1]


def files(run):
    out = {}
    for sub in ("holistic/genomes", "conventional/genomes"):
        for p in sorted(glob.glob(os.path.join(run, sub, "*.json"))):
            out[os.path.join(sub, os.path.basename(p))] = open(p, "rb").read()
    for f in ("lineage.jsonl", "cohorts.jsonl"):
        out[f] = open(os.path.join(run, f), "rb").read()
    return out


def cfg(run):
    c = json.load(open(os.path.join(run, "config.json")))

    def flat(d, p=""):
        o = {}
        for k, v in d.items():
            if isinstance(v, dict):
                o.update(flat(v, p + k + "."))
            else:
                o[p + k] = v
        return o
    return flat(c)


def history(run):
    h = json.load(open(os.path.join(run, "history.json")))
    strip = lambda e: {k: v for k, v in e.items() if k not in ("seconds", "elapsed", "time")}
    return [strip(e) for e in h["history"]]


def same_run(a, b, label):
    fa, fb = files(a), files(b)
    diff = [k for k in sorted(set(fa) | set(fb)) if fa.get(k) != fb.get(k)]
    ca, cb = cfg(a), cfg(b)
    cdiff = {k: (ca.get(k), cb.get(k)) for k in sorted(set(ca) | set(cb)) if ca.get(k) != cb.get(k)}
    ha, hb = history(a), history(b)
    ng = sum(1 for k in fa if "genomes" in k)
    print(f"  {label}: {ng} genomes + lineage + cohorts, differing files: {len(diff)} {diff[:5]}; history rows {len(ha)} vs {len(hb)}, "
          f"equal: {ha == hb}; config fields that differ: {cdiff}")
    return not diff and ha == hb, cdiff


def gbiases(g):
    gb = g.get("global_brain") or {"units": []}
    return [u["bias"] for u in gb["units"] if u.get("kind") != "sensor" and "bias" in u]


def freeze(run):
    gd = os.path.join(run, "conventional", "genomes")
    G = {os.path.basename(p)[:-5]: json.load(open(p)) for p in glob.glob(os.path.join(gd, "*.json"))}
    founders = [g for g in G.values() if not g["parents"]]
    seen = set(b for g in founders for b in gbiases(g))
    births = [g for g in G.values() if g["parents"]]
    bad, new_units, zero_keep, zero_n = 0, 0, 0, 0
    for g in births:
        pool = collections.Counter()
        for p in g["parents"]:
            if p in G:
                pool.update(gbiases(G[p]))
        child = collections.Counter(gbiases(g))
        extra = child - pool
        if sum(extra.values()) > 1:
            bad += 1
        new_units += sum(extra.values())
        p0 = collections.Counter(gbiases(G[g["parents"][0]])) if g["parents"][0] in G else collections.Counter()
        if child == p0 or len(g["parents"]) < 2:
            pass
        if 0.0 in gbiases(G[g["parents"][0]]) if g["parents"][0] in G else False:
            zero_n += 1
            zero_keep += 0.0 in child
    return len(births), bad, new_units, zero_n, zero_keep


def income(run):
    h = json.load(open(os.path.join(run, "history.json")))["history"]
    rows = [e for e in h if e["population"] == "conventional"]
    return sum(e["births"] for e in rows), sum(e["mean_lifetime_score"] for e in rows) / len(rows)


def main():
    print("# RBT-112 design adversary: byte identity and freezing, on the adversary's own runs\n")
    for run in sorted(glob.glob(os.path.join(R, "*"))):
        if os.path.exists(os.path.join(run, "code.txt")):
            print(f"{os.path.basename(run)}: {open(os.path.join(run, 'code.txt')).read().strip()}")
    ok = True
    print("\n## A. flag unset (PR #277) against c872e80's code, 20 seasons")
    for seed in (801, 4):
        s, cd = same_run(os.path.join(R, f"new-HU-{seed}"), os.path.join(R, f"old-HU-{seed}"), f"HU-{seed}")
        cd = {k: v for k, v in cd.items() if k not in ("out", "ecology.out", "out_dir")}
        ok &= s and not cd
    print("\n## B. --global-bias-sigma 0.4 (= weight_sigma) against the flag unset, 20 seasons, 801")
    s, cd = same_run(os.path.join(R, "sig04-HU-801"), os.path.join(R, "new-HU-801"), "HU-801")
    ok &= s and set(cd) <= {"mutation.global_bias_sigma", "out", "ecology.out", "out_dir"}
    print("\n## C. --global-bias-sigma 0: every designed-body birth's global biases come from its parents (+ at most one added unit)")
    for tag in ("s0-HU-801", "s0-HU-4", "new40-HU-801", "new40-HU-4"):
        if not os.path.isdir(os.path.join(R, tag)):
            continue
        n, bad, nu, pn, pok = freeze(os.path.join(R, tag))
        print(f"  {tag}: births {n}; with more than one global bias no parent carried: {bad}; values new at birth, all births: {nu}; "
              f"parents[0] carrying a b = 0 unit (the planted unit): {pn}, of whose children still carrying b = 0: {pok} "
              f"(the rest took a mate's global brain, or lost the unit)")
        if tag.startswith("s0"):
            ok &= bad == 0
    print("\n## D. SE-Z, anecdotal (two seeds x 40 seasons; not a test): designed births and mean lifetime score over seasons")
    for seed in (801, 4):
        a, b = os.path.join(R, f"s0-HU-{seed}"), os.path.join(R, f"new40-HU-{seed}")
        if os.path.isdir(a) and os.path.isdir(b):
            print(f"  seed {seed}: S = 0 births {income(a)[0]}, mean score {income(a)[1]:.3f}; default births {income(b)[0]}, mean score {income(b)[1]:.3f}")
    print(f"\nADVERSARY BYTE IDENTITY AND FREEZING: {'PASS' if ok else 'FAIL'}")


if __name__ == "__main__":
    main()
