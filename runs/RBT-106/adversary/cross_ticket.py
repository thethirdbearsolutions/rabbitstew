"""RBT-106 design adversary, item 2: is RBT-106's S1 (the launcher P1 is paired against) the arm RBT-104
is actually running, byte for byte, on the code RBT-106 will run?

P1 is compared with RBT-104's S1 arms, launched from RBT-104's own `run_arm.sh` on integration at
c872e80.  RBT-106 will launch later from its own `run_arm.sh`/`command.py`, with its founders under
`runs/RBT-106/founders-w1-SEED`.  A token-for-token test of the command (tests/test_rbt106.py) does not
show the RUN is the same: code, founders' path, platform and streams all enter.  This probe runs
RBT-106's S1 command for a few seasons (SEASONS=20, as command.py builds it) and compares it with the
first seasons of RBT-104's live S1 arm on the same seed, restored from its checkpoint
(`scripts/durable.sh restore ... rbt-104-S1-SEED`).  Only the first 20 seasons of RBT-104's arm are read
(seasons.txt rows and lineage.jsonl records with generation < 20): no window, no readout.

Compared:
  seasons.txt   RBT-71 measure.summarise on both; the short run's rows against the same rows of RBT-104's
  lineage.jsonl  every record with generation < N, as parsed JSON, in file order
  config.json   equal outside seasons/generations/workers (and the founders' path, if written)
  platform.txt  both

Usage: cross_ticket.py SHORT_RUN RBT104_RUN
"""
import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
_spec = importlib.util.spec_from_file_location("measure", os.path.join(_ROOT, "runs", "RBT-71", "measure.py"))
measure = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(measure)
VOLATILE = {"seasons", "generations", "workers"}


def flat(d, p=""):
    out = {}
    for k, v in d.items():
        out.update(flat(v, p + k + ".") if isinstance(v, dict) else {p + k: v})
    return out


def lineage(run, n):
    out = []
    for line in open(os.path.join(run, "lineage.jsonl")):
        r = json.loads(line)
        if r.get("generation", 0) < n:
            out.append(r)
    return out


def main(short, ref):
    measure.summarise(short)
    measure.summarise(ref)
    mine = open(os.path.join(short, "seasons.txt")).read().splitlines()
    theirs = open(os.path.join(ref, "seasons.txt")).read().splitlines()
    n_seasons = (len(mine) - 1) // 2
    same = mine == theirs[: len(mine)]
    print(f"# RBT-106 adversary cross_ticket: {os.path.basename(short)} (RBT-106's S1 command) against RBT-104's live {os.path.basename(ref)}")
    print(f"seasons.txt: {len(mine) - 1} rows ({n_seasons} seasons x 2 faunas) against RBT-104's first {len(mine) - 1}: "
          + ("BYTE-IDENTICAL" if same else "DIFFERENT"))
    if not same:
        for i, (a, b) in enumerate(zip(mine, theirs)):
            if a != b:
                print(f"  first difference, line {i}:\n    RBT-106 {a}\n    RBT-104 {b}")
                break
    la, lb = lineage(short, n_seasons), lineage(ref, n_seasons)
    print(f"lineage.jsonl, records with generation < {n_seasons}: {len(la)} here, {len(lb)} RBT-104's: "
          + ("IDENTICAL" if la == lb else "DIFFERENT"))
    ca, cb = flat(json.load(open(os.path.join(short, "config.json")))), flat(json.load(open(os.path.join(ref, "config.json"))))
    diff = sorted(k for k in set(ca) | set(cb) if k.split(".")[-1] not in VOLATILE and ca.get(k, "<absent>") != cb.get(k, "<absent>"))
    # the founders' directory is a path, not a parameter: both launchers check the same digest before loading
    paths = [k for k in diff if k == "ecology.seed_conventional"]
    diff = [k for k in diff if k not in paths]
    for k in paths:
        print(f"config.json {k}: {ca.get(k)!r} here, {cb.get(k)!r} RBT-104's (the founders' path; the digests "
              f"are checked by both launchers and the runs are compared directly below/above; tolerated)")
    print(f"config.json, outside {sorted(VOLATILE)}: " + ("EQUAL" if not diff else "differs in " + ", ".join(
        f"{k} ({ca.get(k, '<absent>')!r} here, {cb.get(k, '<absent>')!r} RBT-104's)" for k in diff)))
    for d, who in ((short, "RBT-106 short run"), (ref, "RBT-104 arm")):
        p = os.path.join(d, "platform.txt")
        print(f"platform, {who}: " + (open(p).read().strip() if os.path.exists(p) else "(not written by this launcher path)"))
    ok = same and la == lb and not diff
    print(f"\nCROSS-TICKET {os.path.basename(ref)}: {'SAME RUN (prefix)' if ok else 'NOT THE SAME RUN'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/")))
