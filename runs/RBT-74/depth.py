"""Realised search depth of the arena arms (RBT-74; method from RBT-59's depth.py, adapted).

For every member alive at the last generation of a run, walk the first-parent chain back to
generation 0 through lineage.jsonl.  In the arena GA every member has a parent in the previous
generation, so the chain length is the generation count by construction; what varies is what
the steps *are*:

* mutation events   -- steps that are not elite copies (a child differs from its parent by at
                       least one operator application);
* body-change events -- steps where the body-plan hash changes (holistic only; the conventional
                       body is fixed by assertion);
* controller-only events -- mutation events that kept the body plan (readaptation children of
                       the protected arm, and the ~1% of free-slot children the full operator
                       happens to leave bodily unchanged);
* elite copies      -- steps with no mutation.

Runs written before RBT-74 have no `body`/`birth` fields; elite copies are then detected by an
unchanged genotype hash where genotypes are saved, otherwise reported as unknown.

    python runs/RBT-74/depth.py runs/RBT-74/base-201 runs/RBT-74/prot-201 ...

No simulation.  File analysis only.
"""
import json
import os
import statistics as st
import sys
from collections import defaultdict


def load(run):
    lin = defaultdict(dict)  # population -> name -> last record
    with open(os.path.join(run, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            lin[r["population"]][r["name"]] = r
    return lin


def chain_stats(records):
    last = max(r["generation"] for r in records.values())
    alive = [r for r in records.values() if r["generation"] == last]
    rows, founders = [], set()
    for r in alive:
        steps = muts = body = ctrl = elites = 0
        cur, seen = r, set()
        while cur["parents"] and cur["parents"][0] in records and cur["name"] not in seen:
            seen.add(cur["name"])
            par = records[cur["parents"][0]]
            steps += 1
            birth = cur.get("birth")
            if birth in ("elite", "survivor"):
                elites += 1
            else:
                muts += 1
                if "body" in cur and "body" in par:
                    if cur["body"] != par["body"]:
                        body += 1
                    else:
                        ctrl += 1
            cur = par
        founders.add(cur["name"])
        rows.append(dict(name=r["name"], steps=steps, mutations=muts, body_changes=body, controller_only=ctrl, elite_copies=elites))
    return last, alive, rows, founders


def summarise(run, kind, last, alive, rows, founders):
    med = lambda k: st.median(x[k] for x in rows)
    rng = lambda k: (min(x[k] for x in rows), max(x[k] for x in rows))
    return dict(run=os.path.basename(os.path.normpath(run)), population=kind, last_generation=last, alive=len(alive), founders=len(founders),
                steps_median=med("steps"), mutations_median=med("mutations"), mutations_range=rng("mutations"),
                body_changes_median=med("body_changes"), body_changes_range=rng("body_changes"),
                controller_only_median=med("controller_only"), elite_copies_median=med("elite_copies"), members=rows)


def main(runs):
    out = []
    hdr = f"{'run':10} {'pop':12} {'last':>4} {'alive':>5} {'fnd':>3} {'steps':>5} {'mut med':>7} {'mut range':>9} {'body med':>8} {'body range':>10} {'ctrl med':>8} {'elite med':>9}"
    print(hdr)
    print("-" * len(hdr))
    for run in runs:
        lin = load(run)
        for kind in ("holistic", "conventional"):
            if kind not in lin:
                continue
            last, alive, rows, founders = chain_stats(lin[kind])
            s = summarise(run, kind, last, alive, rows, founders)
            out.append(s)
            print(f"{s['run']:10} {kind:12} {last:4d} {len(alive):5d} {len(founders):3d} {s['steps_median']:5.0f} {s['mutations_median']:7.0f} {str(s['mutations_range']):>9} {s['body_changes_median']:8.0f} {str(s['body_changes_range']):>10} {s['controller_only_median']:8.0f} {s['elite_copies_median']:9.0f}")
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "depth.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    main(sys.argv[1:] or sorted(d for d in (os.path.join("runs/RBT-74", x) for x in os.listdir("runs/RBT-74")) if os.path.isdir(d) and os.path.exists(os.path.join(d, "lineage.jsonl"))))
