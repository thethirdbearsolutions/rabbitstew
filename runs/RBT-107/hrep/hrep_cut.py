"""RBT-107 H-REP no-peek (coordinator 03:17: "nothing from season >= 471 of any arm enters or is printed").

    python runs/RBT-107/hrep/hrep_cut.py RUN_COPY LAST        (LAST = 470 = T + 110)

Cuts a RESTORED COPY of an arm (never a live run directory) back to the end of season LAST, before any table is written:
lineage.jsonl keeps rows with generation <= LAST, cohorts.jsonl rows with season <= LAST, history.json entries with
season <= LAST.  Then RBT-92's tables.py writes seasons.txt and lineage-last.txt from what is left, so every table read
for H-REP stops at LAST.  The T + 110 population is unchanged by the cut: garden.py takes "alive at the end of season
470" (RBT-92's Arm.alive_at: born <= 470 <= last seen), and an individual alive at 470 is last seen at >= 470 in both the
cut and the uncut lineage.  Genomes at birth (KIND/genomes/NAME.json) are read only for that population.
"""
import json
import os
import sys


def cut_jsonl(path, key, last):
    if not os.path.exists(path):
        return 0
    keep, dropped = [], 0
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if int(r.get(key, 0)) <= last:
                keep.append(line if line.endswith("\n") else line + "\n")
            else:
                dropped += 1
    with open(path, "w") as f:
        f.writelines(keep)
    return dropped


def main(run, last):
    a = cut_jsonl(os.path.join(run, "lineage.jsonl"), "generation", last)
    b = cut_jsonl(os.path.join(run, "cohorts.jsonl"), "season", last)
    hp = os.path.join(run, "history.json")
    h = json.load(open(hp))
    n0 = len(h["history"])
    h["history"] = [e for e in h["history"] if int(e["season"]) <= last]
    json.dump(h, open(hp, "w"))
    for stale in ("seasons.txt", "lineage-last.txt", "bodysig.txt", "events.txt", "groups.txt", "wiring.txt", "vpost.txt"):
        p = os.path.join(run, stale)
        if os.path.exists(p):
            os.remove(p)  # the snapshot's own tables may run past LAST: never read them
    print(f"cut {run} to season <= {last}: dropped {a} lineage rows, {b} cohort rows, {n0 - len(h['history'])} history entries")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
