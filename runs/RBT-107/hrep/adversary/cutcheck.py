"""RBT-107 H-REP readout adversary: independent check that a cut copy holds nothing after LAST.

    python runs/RBT-107/hrep/adversary/cutcheck.py RUN_COPY LAST

Reads the three files hrep_cut.py cuts and checks every row's season key is <= LAST (lineage.jsonl 'generation', which
RBT-92's tables.py treats as the observation season: born = generation - age; cohorts.jsonl 'season'; history.json
entries' 'season'), and that no derived table from the snapshot survived.  Prints only counts and PASS/FAIL, never a
value from a row.  It also lists any OTHER file in the copy that could carry a season (a *.jsonl or *.txt not cut),
since garden.py and tables.py must read nothing past LAST.
"""
import json
import os
import sys


def main(run, last):
    bad = []
    for fn, key in (("lineage.jsonl", "generation"), ("cohorts.jsonl", "season")):
        p = os.path.join(run, fn)
        if os.path.exists(p):
            n = over = 0
            for line in open(p):
                if line.strip():
                    n += 1
                    over += int(json.loads(line).get(key, 0)) > last
            if over:
                bad.append(f"{fn}: {over} of {n} rows past {last}")
    h = json.load(open(os.path.join(run, "history.json")))
    over = sum(int(e["season"]) > last for e in h["history"])
    if over:
        bad.append(f"history.json: {over} entries past {last}")
    left = [f for f in ("seasons.txt", "lineage-last.txt", "bodysig.txt", "events.txt", "groups.txt", "wiring.txt", "vpost.txt")
            if os.path.exists(os.path.join(run, f))]
    if left:
        bad.append(f"stale tables left: {left}")
    other = sorted(f for f in os.listdir(run) if (f.endswith(".jsonl") or f.endswith(".txt") or f.endswith(".json"))
                   and f not in ("lineage.jsonl", "cohorts.jsonl", "history.json"))
    print(f"{os.path.basename(run)} cut <= {last}: {'PASS' if not bad else 'FAIL ' + '; '.join(bad)}; other top-level files not cut: {other}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
