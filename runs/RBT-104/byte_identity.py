"""RBT-104: does --link-scale leave the run alone at its default, and act only where it should?

Check 1 (default, the ticket's byte-identity requirement).  A short run of RBT-90 part 2's exact
command (`short_run.sh`, no --link-scale) must write
  * a `seasons.txt` whose rows are byte-identical to the first rows of the committed
    `runs/RBT-90/forage-SEED/seasons.txt` (both faunas, every column, full float repr), and
  * a `config.json` equal to the committed one in every field but seasons/generations and workers
    (the three a short run on another core count changes, and the ones RBT-102 already names).
The committed arm ran on the code before the flag existed, so this is the flag at its default
against the code without it.

Check 2 (raised, the flag's reach).  A short run with --link-scale K must write
  * holistic rows byte-identical to the default run's (the flag is the designed body's only, it
    draws no random number, and RBT-95's streams keep the holistic side paired), and
  * designed-body founders (saved at birth) that are the default run's founders with every link
    weight exactly K times larger and every unit, biases included, unchanged.

Usage:
  byte_identity.py default RUN_DIR SEED
  byte_identity.py raised  RUN_DIR DEFAULT_RUN_DIR
"""
import glob
import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ccs = importlib.util.spec_from_file_location("rbt104_configcmp", os.path.join(_HERE, "configcmp.py"))
_cc = importlib.util.module_from_spec(_ccs)
_ccs.loader.exec_module(_cc)
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("measure", os.path.join(_ROOT, "runs", "RBT-71", "measure.py"))
measure = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(measure)

VOLATILE = {"seasons", "generations", "workers"}


def rows(path):
    return open(path).read().splitlines()


def strip(d):
    if isinstance(d, dict):
        return {k: strip(v) for k, v in d.items() if k not in VOLATILE}
    return d


def default(run, seed):
    measure.summarise(run)
    mine = rows(f"{run}/seasons.txt")
    ref = rows(os.path.join(_ROOT, "runs", "RBT-90", f"forage-{seed}", "seasons.txt"))
    n = len(mine) - 1
    same = mine == ref[: len(mine)]
    print(f"# RBT-104 check 1: --link-scale at its default against RBT-90 part 2, seed {seed}\n")
    print(f"seasons.txt: {n} rows ({n // 2} seasons x 2 faunas) of the committed {len(ref) - 1}: "
          + ("BYTE-IDENTICAL" if same else "DIFFERENT"))
    if not same:
        for i, (a, b) in enumerate(zip(mine, ref)):
            if a != b:
                print(f"  first difference, line {i}:\n    here      {a}\n    committed {b}")
                break
    c_mine = json.load(open(f"{run}/config.json"))
    c_ref = json.load(open(os.path.join(_ROOT, "runs", "RBT-90", f"forage-{seed}", "config.json")))
    extra = _cc.added_at_default(c_mine, c_ref)
    cfg_same = strip(c_mine) == strip(c_ref)
    print(f"config.json: equal to the committed one outside {sorted(VOLATILE)}: {'YES' if cfg_same else 'NO'}; "
          f"'link_scale' written: {'link_scale' in c_mine['mutation']}"
          + (f"; fields added since by other tickets, at their defaults: {extra}" if extra else ""))
    return 0 if same and cfg_same else 1


def _genome(run, kind, name):
    return json.load(open(os.path.join(run, kind, "genomes", f"{name}.json")))


def raised(run, base):
    measure.summarise(run)
    measure.summarise(base)
    mine, ref = rows(f"{run}/seasons.txt"), rows(f"{base}/seasons.txt")
    pi = mine[0].split("\t").index("population")
    k = json.load(open(f"{run}/config.json"))["mutation"].get("link_scale")
    print(f"# RBT-104 check 2: --link-scale {k} against the default, same seed, same seasons\n")
    hol = [r for r in mine[1:] if r.split("\t")[pi] == "holistic"]
    hol0 = [r for r in ref[1:] if r.split("\t")[pi] == "holistic"]
    m = min(len(hol), len(hol0))  # runs of unequal length: compare the seasons both have (adversary F1 nit)
    hol, hol0 = hol[:m], hol0[:m]
    ok_h = hol == hol0
    print(f"holistic seasons.txt rows: {len(hol)}, " + ("BYTE-IDENTICAL to the default run" if ok_h else "DIFFERENT"))
    names = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(base, "conventional", "genomes", "c0-*.json")))
    bad = 0
    for n in names:
        a, b = _genome(base, "conventional", n), _genome(run, "conventional", n)
        la = [l for _, br in _brains(a) for l in br["links"]]
        lb = [l for _, br in _brains(b) for l in br["links"]]
        same_topology = [(l["src"], l["dst"]) for l in la] == [(l["src"], l["dst"]) for l in lb]
        scaled = same_topology and all(y["weight"] == k * x["weight"] for x, y in zip(la, lb))
        ua = [u for _, br in _brains(a) for u in br["units"]]
        ub = [u for _, br in _brains(b) for u in br["units"]]
        bad += not (scaled and ua == ub)
    ok_f = bad == 0 and len(names) > 0
    print(f"designed-body founders: {len(names) - bad} of {len(names)} are the default founder with every link "
          f"weight times {k} and every unit (biases included) unchanged: " + ("YES" if ok_f else "NO"))
    return 0 if ok_h and ok_f else 1


def _brains(d):
    out = [(None, d["global_brain"])] if d.get("global_brain") else []
    return out + [(i, n["segment"]["brain"]) for i, n in enumerate(d["nodes"])]


if __name__ == "__main__":
    mode = sys.argv[1]
    sys.exit(default(sys.argv[2], sys.argv[3]) if mode == "default" else raised(sys.argv[2], sys.argv[3]))
