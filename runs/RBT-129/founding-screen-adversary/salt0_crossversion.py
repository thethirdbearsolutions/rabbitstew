"""Adversary (RBT-129c, #495): salt 0 is byte-identical to the base tree, for both faunas and every stage.

Runs tiny ecologies (never a sweep world) with the BASE tree (fbfdac3, before #495) and the HEAD tree (#495), and
compares every output file byte for byte (config.json, state.json, history.json, lineage.jsonl, cohorts, genomes,
final/, ...; only run.log, command.txt and platform.json are skipped).  Arms, each at seed 7 and 129002:

  S      two faunas, seasons 0-4                         (the census / Stage-1 S shape)
  H1     holistic alone (--only-fauna), 0-4              (the screen's salt-0 attempt)
  D1     designed alone, 0-4
  R      two faunas to 2, then --resume to 4             (a killed and resumed S)
  M      S's season-2 state forked with the merge set    (the pilot / Stage-1 M arm)
  N      the same with merge_null                        (the N arm)

HEAD runs each arm twice: with no salt flag, and with --holistic-stream-salt 0 --designed-stream-salt 0 given
explicitly (what stages.screen_argv passes for salt 0).  BASE has no salt flag on `ecology`.

    python3 salt0_crossversion.py --base /path/to/base/checkout --head /path/to/head/checkout > salt0_crossversion.txt
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

TINY = ["--capacity", "4", "--challenge", "foraging", "--group-size", "2", "--brain-model", "foraging", "--food-items", "4",
        "--duration", "0.4", "--terrain", "flat", "--conventional-topology", "--score", "food", "--living-cost", "0.05",
        "--initial-energy", "2", "--birth-threshold", "0.5", "--birth-cost", "0.2", "--max-age", "6",
        "--eat-from", "root", "--eat-rule", "surface", "--fair", "--sweep-log"]
SKIP = ("run.log", "command.txt", "platform.json")
SALT0 = ["--holistic-stream-salt", "0", "--designed-stream-salt", "0"]


def eco(tree, argv, out):
    env = {**os.environ, "PYTHONPATH": tree}
    r = subprocess.run([sys.executable, "-m", "rabbitstew.cli", "ecology", *argv, "--workers", "1", "--out", out],
                       cwd=tree, env=env, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"{tree}: {argv}: exit {r.returncode}\n{r.stderr[-2000:]}")


def fork(src, dst, settings, tree, seasons):
    shutil.copytree(src, dst)
    p = os.path.join(dst, "config.json")
    c = json.load(open(p))
    c["ecology"].update(settings)
    json.dump(c, open(p, "w"), indent=2)
    eco(tree, ["--resume", "--seasons", str(seasons)], dst)


def arms(tree, root, extra, seed):
    base = TINY + ["--seed", str(seed)]
    out = {}
    d = os.path.join(root, "S"); eco(tree, base + extra + ["--seasons", "4"], d); out["S"] = d
    d = os.path.join(root, "H1"); eco(tree, base + extra + ["--only-fauna", "holistic", "--seasons", "4"], d); out["H1"] = d
    d = os.path.join(root, "D1"); eco(tree, base + extra + ["--only-fauna", "conventional", "--seasons", "4"], d); out["D1"] = d
    d = os.path.join(root, "R"); eco(tree, base + extra + ["--seasons", "2"], d); eco(tree, ["--resume", "--seasons", "4"], d); out["R"] = d
    c = os.path.join(root, "ckpt"); eco(tree, base + extra + ["--seasons", "2"], c)
    fork(c, os.path.join(root, "M"), {"merge_after": 2, "pooled_capacity": 8}, tree, 5); out["M"] = os.path.join(root, "M")
    fork(c, os.path.join(root, "N"), {"merge_after": 2, "pooled_capacity": 8, "merge_null": "holistic"}, tree, 5); out["N"] = os.path.join(root, "N")
    return out


def files(d):
    out = {}
    for b, _, fs in os.walk(d):
        for n in fs:
            if n not in SKIP:
                out[os.path.relpath(os.path.join(b, n), d)] = os.path.join(b, n)
    return out


def compare(a, b):
    fa, fb = files(a), files(b)
    diff = sorted(set(fa) ^ set(fb)) + [n for n in sorted(set(fa) & set(fb)) if open(fa[n], "rb").read() != open(fb[n], "rb").read()]
    return len(set(fa) & set(fb)), diff


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="salt0x-")
    bad = 0
    print("# salt-0 cross-version byte-identity (adversary, RBT-129c #495): BASE fbfdac3 against HEAD, tiny worlds")
    for seed in (7, 129002):
        ref = arms(a.base, os.path.join(tmp, f"base-{seed}"), [], seed)
        for tag, extra in (("head, no flag", []), ("head, explicit salt 0 flags", SALT0)):
            got = arms(a.head, os.path.join(tmp, f"head-{seed}-{len(extra)}"), extra, seed)
            for arm in ref:
                n, diff = compare(ref[arm], got[arm])
                bad += bool(diff)
                print(f"seed {seed:6d}  {arm:2s}  {tag:28s}  {n:4d} files  {'IDENTICAL' if not diff else 'DIFFERS: ' + ', '.join(diff[:6])}")
    shutil.rmtree(tmp)
    print(f"\n{'PASS' if not bad else 'FAIL'}: {bad} arm(s) differ")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
