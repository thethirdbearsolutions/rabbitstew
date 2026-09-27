"""RBT-126: run scripts/regime.py over the committed ecology corpus and write runs/RBT-126/regime/*.

Sources, per ticket:
  RBT-19   runs/RBT-19/P-801/lineage.jsonl (committed)
  RBT-90, 99, 100, 101, 104, 105, 106, 107, 112   the full lineage.jsonl restored from each run's checkpoint branch
           (origin ckpt/rbt-<n>-<arm>: MANIFEST + run.tar.gz.part*, extracted by fetch_ck.sh), with the
           checkpoint's config.json (identical to the committed one on all 201 runs).  RBT-104 (S1, S8) is beyond the ticket's list: its S1 arms are paper 10's
           uniform w=1 comparator (runs/RBT-106/S1-*).  RBT-80 has no committed lineage and no checkpoint branch.

Windows: the standard blocks 0-49, 50-149, 150-299, 300-449, 450-599 (and 600-899, 900-1199 for RBT-107's 1200
seasons), plus each ticket's own headline windows (onset-relative ones use the seed's T from runs/RBT-92/onset.txt,
or T = 360 for RBT-107).

python3 runs/RBT-126/corpus.py CK_DIR    (CK_DIR holds rbt-<n>-<arm>/<arm dir>/lineage.jsonl)
"""
import glob, importlib.util, json, os, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("regime", ROOT / "scripts" / "regime.py")
rg = importlib.util.module_from_spec(spec); spec.loader.exec_module(rg)

STD = ((0, 49), (50, 149), (150, 299), (300, 449), (450, 599))
ONSET = {int(l.split("\t")[0]): int(l.split("\t")[1]) for l in open(ROOT / "runs/RBT-92/onset.txt") if l[0].isdigit()}


def headline_windows(ticket, arm, seed):
    """(label, lo, hi) for the windows each ticket's headline was read in."""
    if ticket in (99, 100, 101) or (ticket == 90):
        T = ONSET.get(seed)
        if T is None:
            return []
        w = [("before [T-100,T)", T - 100, T - 1), ("transient [T,T+60)", T, T + 59),
             ("recovery [T+60,T+160)", T + 60, T + 159)]
        return w + ([("season-590 champions: 500-599", 500, 599)] if ticket == 90 else [])
    if ticket == 107:
        T = 360
        return [("before [T-100,T)", T - 100, T - 1), ("to H-REP [T,T+110)", T, T + 109),
                ("to H1 [T+110,T+800)", T + 110, T + 799), ("H1 tail [T+700,T+800)", T + 700, T + 799)]
    if ticket in (104, 106, 112):
        return [("to 300 [0,300)", 0, 299), ("window income [300,600)", 300, 599)]
    if ticket == 105:
        return [("A/A [60,160)", 60, 159), ("R2 [300,600)", 300, 599)]
    if ticket == 19:
        return [("0-99", 0, 99), ("100-299", 100, 299), ("300-499", 300, 499), ("500-599", 500, 599)]
    return []


def runs(ck):
    yield 19, "P-801", 801, str(ROOT / "runs/RBT-19/P-801")
    for d in sorted(glob.glob(os.path.join(ck, "rbt-*"))):
        m = re.match(r"rbt-(\d+)-(.*)$", os.path.basename(d))
        t, arm = int(m.group(1)), m.group(2)
        if not os.path.exists(os.path.join(d, "DONE")):
            continue  # still being extracted
        inner = [x for x in glob.glob(os.path.join(d, "*")) if os.path.isdir(x)]
        if not inner or not os.path.exists(os.path.join(inner[0], "lineage.jsonl")):
            continue
        seed = int(re.findall(r"(\d+)", arm.replace("b0", "").replace("b1", "").replace("b2", ""))[-1]) if re.findall(r"\d+", arm) else None
        if t == 105:
            seed = int(arm.split("-")[0])
        yield t, arm, seed, inner[0]


def main(ck):
    out = HERE / "regime"
    out.mkdir(exist_ok=True)
    allres = []
    texts = {}
    for t, arm, seed, d in runs(ck):
        # the committed config beats the checkpoint's copy only if the checkpoint lacks one
        if not os.path.exists(os.path.join(d, "config.json")):
            continue
        last = rg.read_lineage(d)[1]
        std = STD + (((600, 899), (900, 1199)) if last >= 1000 else ())
        hw = headline_windows(t, arm, seed)
        res = rg.regime(d, std + tuple((lo, hi) for _, lo, hi in hw))
        res.update(ticket=t, arm=arm, seed=seed, headline=hw)
        res["run"] = f"RBT-{t}/{arm}"
        allres.append(res)
        texts.setdefault(t, []).append(rg.render(res, {(lo, hi) for _, lo, hi in hw}))
        print(f"RBT-{t} {arm}: last season {last}", flush=True)
    for t, tx in texts.items():
        (out / f"RBT-{t}.txt").write_text(f"# scripts/regime.py on RBT-{t}'s restored lineages (runs/RBT-126/corpus.py)\n\n" + "\n\n".join(tx) + "\n")
    with open(out / "corpus.json", "w") as f:  # untracked (runs/** keeps only text): the input of build_regime_md.py
        json.dump(allres, f)


if __name__ == "__main__":
    main(sys.argv[1])
