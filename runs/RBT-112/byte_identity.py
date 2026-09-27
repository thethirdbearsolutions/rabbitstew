"""RBT-112 step 2: does --global-bias-sigma leave the run alone when unset, and freeze only global biases at 0?

Throwaway short runs (not arms), made by byte_identity.sh with RBT-104's short_run.sh (RBT-90 part 2's command):

Check 1 (the default against the committed part 2).  `p2-SEED` (10 seasons, no flag) must pass RBT-104's
  `byte_identity.default`, imported: seasons.txt rows byte-identical to the committed runs/RBT-90/forage-SEED rows,
  and config.json equal outside seasons/generations/workers (so global_bias_sigma is not written).  Seeds 801 and 4.
Check 2 (the default against a committed seeded run).  `S1U-801` (20 seasons, RBT-104's w = 1 founders) must write
  seasons.txt byte-identical to RBT-106's committed runs/RBT-106/side/S1U-801/seasons.txt.
Check 3 (the default against the code before the flag, genome for genome).  `HU-801` (20 seasons, RBT-106's w = 32
  founders: HU's founders and command) on this branch against `HUold-801`, the same command on c872e80's code
  (the code RBT-106's arms run): seasons.txt, lineage.jsonl, config.json and every genome both faunas saved at
  birth, byte for byte.
Check 4 (S = 0 does what it says, and only that).  `HU0-801` (the same, --global-bias-sigma 0) against `HU-801`:
  * config.json differs in exactly one field, mutation.global_bias_sigma (absent -> 0.0);
  * the founders of both faunas, and the holistic fauna's seasons.txt rows, are byte-identical (the flag draws no
    number and touches no holistic genome);
  * in HU0-801 no designed-body child carries a global-unit bias that neither parent carried, beyond at most one
    unit the operator added at that birth (a new unit is born with its own drawn bias).  In HU-801, the default,
    this count is printed for contrast: there the global biases step at every birth.

Usage: byte_identity.py SCRATCH_RUNS_DIR   > byte_identity.txt
"""
import collections
import glob
import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt104_byte_identity", os.path.join(_ROOT, "runs", "RBT-104", "byte_identity.py"))
bi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bi)


def flat(d, p=""):
    out = {}
    for k, v in d.items():
        out.update(flat(v, p + k + ".") if isinstance(v, dict) else {p + k: v})
    return out


def genomes(run, kind):
    return {os.path.basename(p): open(p, "rb").read() for p in glob.glob(os.path.join(run, kind, "genomes", "*.json"))}


def check3(new, old):
    print("\n# Check 3: HU-801 on this branch (flag unset) against HU-801 on c872e80's code, 20 seasons")
    ok = True
    for f in ("seasons.txt", "lineage.jsonl"):
        same = open(os.path.join(new, f), "rb").read() == open(os.path.join(old, f), "rb").read()
        print(f"  {f}: {'BYTE-IDENTICAL' if same else 'DIFFERENT'}")
        ok &= same
    cn, co = json.load(open(os.path.join(new, "config.json"))), json.load(open(os.path.join(old, "config.json")))
    # the c872e80 run is launched from its worktree, so it records the (same) founders by absolute path
    pn, po = (os.path.realpath(os.path.join(_ROOT, c["ecology"]["seed_conventional"])) for c in (cn, co))
    cn["ecology"]["seed_conventional"] = co["ecology"]["seed_conventional"] = None
    same = bi.strip(cn) == bi.strip(co) and "global_bias_sigma" not in cn["mutation"] and pn == po
    print(f"  config.json: equal outside {sorted(bi.VOLATILE)} (founders' path compared resolved: {pn == po}), "
          f"global_bias_sigma not written: {'YES' if same else 'NO'}")
    ok &= same
    for kind in ("holistic", "conventional"):
        a, b = genomes(new, kind), genomes(old, kind)
        same = a == b
        print(f"  {kind} genomes saved at birth: {len(a)} here, {len(b)} there, {'all byte-identical' if same else 'DIFFERENT'}")
        ok &= same
    print(f"default against the pre-flag code, genome for genome: {'SAME RUN' if ok else 'NOT THE SAME RUN'}")
    return ok


def global_biases(g):
    gb = g.get("global_brain") or {}
    return [u.get("bias", 0.0) for u in gb.get("units", []) if u.get("kind") != "sensor"]


def novel_biases(run):
    """(births, births with a global bias carried by neither parent beyond one added unit)."""
    gd = os.path.join(run, "conventional", "genomes")
    G = {os.path.basename(p)[:-5]: json.load(open(p)) for p in glob.glob(os.path.join(gd, "*.json"))}
    births = bad = 0
    for name, g in G.items():
        ps = g.get("parents") or []
        if not ps:
            continue
        births += 1
        pool = collections.Counter()
        for p in ps:
            pool.update(global_biases(G[p]))
        extra = collections.Counter(global_biases(g)) - pool
        bad += sum(extra.values()) > 1
    return births, bad


def check4(zero, default):
    print("\n# Check 4: HU-801 at --global-bias-sigma 0 against HU-801 at the default, 20 seasons")
    ok = True
    cz, cd = flat(json.load(open(os.path.join(zero, "config.json")))), flat(json.load(open(os.path.join(default, "config.json"))))
    diff = sorted(k for k in set(cz) | set(cd) if cz.get(k, "<absent>") != cd.get(k, "<absent>"))
    shown = ", ".join("%s: %r -> %r" % (k, cd.get(k, "<absent>"), cz.get(k, "<absent>")) for k in diff)
    print(f"  config.json fields that differ: {shown}")
    ok &= diff == ["mutation.global_bias_sigma"] and cz["mutation.global_bias_sigma"] == 0.0
    for kind in ("holistic", "conventional"):
        a, b = genomes(zero, kind), genomes(default, kind)
        fz = {n: v for n, v in a.items() if not json.loads(v).get("parents")}
        fd = {n: v for n, v in b.items() if not json.loads(v).get("parents")}
        same = fz == fd and len(fz) == 60
        print(f"  {kind} founders: {len(fz)} and {len(fd)}, {'byte-identical' if same else 'DIFFERENT'}")
        ok &= same
    rz, rd = bi.rows(os.path.join(zero, "seasons.txt")), bi.rows(os.path.join(default, "seasons.txt"))
    pi = rz[0].split("\t").index("population")
    hz = [r for r in rz[1:] if r.split("\t")[pi] == "holistic"]
    hd = [r for r in rd[1:] if r.split("\t")[pi] == "holistic"]
    print(f"  holistic seasons.txt rows: {'BYTE-IDENTICAL' if hz == hd else 'DIFFERENT'} ({len(hz)} rows)")
    ok &= hz == hd
    cz_rows = [r for r in rz[1:] if r.split("\t")[pi] == "conventional"]
    cd_rows = [r for r in rd[1:] if r.split("\t")[pi] == "conventional"]
    first = next((i for i, (x, y) in enumerate(zip(cz_rows, cd_rows)) if x != y), None)
    print(f"  designed-body seasons.txt rows: first differing season {first} (the operator differs from the first birth on)")
    bz, nz = novel_biases(zero)
    bd, nd = novel_biases(default)
    print(f"  designed-body births with a global bias neither parent carried (beyond one added unit): "
          f"S = 0 {nz} of {bz}; default {nd} of {bd}")
    ok &= nz == 0 and nd > 0
    print(f"S = 0 freezes the designed body's global biases and nothing else checked here: {'YES' if ok else 'NO'}")
    return ok


def main():
    d = sys.argv[1]
    ok = True
    print("# RBT-112 byte identity of --global-bias-sigma (throwaway short runs; x86_64)\n")
    print(open(os.path.join(d, "HU-801", "platform.txt")).read().strip() if os.path.exists(os.path.join(d, "HU-801", "platform.txt")) else "")
    for seed in (801, 4):
        print(f"\n# Check 1, seed {seed} (RBT-104's byte_identity.default, imported; its header names --link-scale, the check is the same)")
        ok &= bi.default(os.path.join(d, f"p2-{seed}"), seed) == 0
    print("\n# Check 2: the default, seeded (RBT-104's w = 1 founders), against RBT-106's committed side/S1U-801")
    bi.measure.summarise(os.path.join(d, "S1U-801"))
    mine = bi.rows(os.path.join(d, "S1U-801", "seasons.txt"))
    ref = bi.rows(os.path.join(_ROOT, "runs", "RBT-106", "side", "S1U-801", "seasons.txt"))
    print(f"  seasons.txt: {len(mine) - 1} rows against the committed {len(ref) - 1}: {'BYTE-IDENTICAL' if mine == ref else 'DIFFERENT'}")
    ok &= mine == ref
    for r in ("HU-801", "HUold-801", "HU0-801"):
        bi.measure.summarise(os.path.join(d, r))
    ok &= check3(os.path.join(d, "HU-801"), os.path.join(d, "HUold-801"))
    ok &= check4(os.path.join(d, "HU0-801"), os.path.join(d, "HU-801"))
    print(f"\nBYTE IDENTITY: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
