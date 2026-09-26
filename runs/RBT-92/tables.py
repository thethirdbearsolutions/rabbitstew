"""RBT-92: what one finished arm owes the repository, written from its bulk.

    python runs/RBT-92/tables.py ARM_DIR [--bodysig-only [--to DIR]]

  seasons.txt       RBT-71's summarise() columns plus mean_age and max_age (RBT-89 section 8's build
                    item) and, for a fauna that died out, alive = 0 rows to the run's last season
                    (RBT-89 section 13's build item), so extinction is readable from the table
  lineage-last.txt  RBT-71's summarise(), unchanged: one row per individual at its last observation
  bodysig.txt       one row per individual: population, name, born season, and a 12-hex digest of its
                    BODY STRUCTURE from its genome at birth (see body_structure below); the carriage
                    readout (readout.py) traces descent on lineage-last.txt and compares these digests
  groups.txt        one row per season and fauna: the sizes of that season's arena groups, from cohorts.jsonl
                    (C1 owes "which robots the remainder group held", RBT-89 section 2; adversary F5)
  events.txt        the event as the run recorded it: every "death: cull" lineage row counted by fauna
                    and season with the culled names, and the seasons whose history entries carry
                    "shift" or "culled"

--bodysig-only writes bodysig.txt alone, for a baseline arm (RBT-90 part 2) whose seasons.txt and
lineage-last.txt are already committed by its own pass and must not be rewritten; --to DIR writes
it there instead (runs/RBT-92/base-SEED for a baseline, where readout.py looks for it).

body_structure(g) is rabbitstew.genetics.body_signature with every continuous value dropped: the root,
each node's segment shape, each connection's child index, joint type, recursive limit, motor mode and
mirror flag, and each node's non-neuron units (kind, source, axis, dof).  It is the body a designer
would draw, and it survives the weight, dims, position, orientation, scale and axis-angle mutations
that change body_signature in almost every child.  The designed (conventional) fauna's body is fixed,
so its digest is one value throughout; the carriage readout reads the holistic fauna.
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
KINDS = ("holistic", "conventional")
EXTRA = ("mean_age", "max_age")


def _measure():
    spec = importlib.util.spec_from_file_location("measure", ROOT / "runs" / "RBT-71" / "measure.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def body_structure(g):
    sig = [g.root]
    for node in g.nodes:
        seg = node.segment
        sig.append(int(seg.shape))
        sig.append(tuple((c.child, int(c.joint_type), c.recursive_limit, c.motor, c.mirror) for c in node.connections))
        sig.append(tuple((u.kind, getattr(u, "source", None), getattr(u, "axis", None), getattr(u, "dof", None))
                         for u in seg.brain.units if u.kind != "neuron"))
    return hashlib.sha256(repr(tuple(sig)).encode()).hexdigest()[:12]


def write_seasons(run):
    m = _measure()
    hist = json.load(open(f"{run}/history.json"))["history"]
    last = max(h["season"] for h in hist)
    keys = m.SEASON_KEYS + EXTRA
    seen = {(h["season"], h["population"]) for h in hist}
    rows = list(hist)
    for kind in KINDS:
        s_last = max((h["season"] for h in hist if h["population"] == kind), default=-1)
        for s in range(s_last + 1, last + 1):
            if (s, kind) not in seen:
                rows.append({"season": s, "population": kind, "alive": 0, "births": 0, "deaths": 0,
                             "mean_lifetime_score": 0.0, "best_lifetime_score": 0.0, "mean_age": 0.0, "max_age": 0})
    rows.sort(key=lambda h: (h["season"], KINDS.index(h["population"])))
    with open(f"{run}/seasons.txt", "w") as f:
        f.write("\t".join(keys) + "\n")
        for h in rows:
            f.write("\t".join(str(h[k]) for k in keys) + "\n")
    # lineage-last.txt exactly as RBT-71 writes it (summarise writes both; restore our seasons.txt after)
    body = open(f"{run}/seasons.txt").read()
    m.summarise(run)
    open(f"{run}/seasons.txt", "w").write(body)


def write_bodysig(run, to=None):
    from rabbitstew.genotype import Genotype
    born, out = {}, []
    with open(f"{run}/lineage.jsonl") as f:
        for line in f:
            r = json.loads(line)
            k = (r["population"], r["name"])
            if k not in born:
                born[k] = r["generation"] - r["age"]
    missing = 0
    for (pop, name), b in born.items():
        p = os.path.join(run, pop, "genomes", f"{name}.json")
        if not os.path.exists(p):
            missing += 1
            out.append((pop, name, b, "-"))
            continue
        out.append((pop, name, b, body_structure(Genotype.load(p))))
    os.makedirs(to or run, exist_ok=True)
    with open(os.path.join(to or run, "bodysig.txt"), "w") as f:
        f.write("population\tname\tborn\tbody\n")
        for r in out:
            f.write("\t".join(map(str, r)) + "\n")
    return missing


def write_events(run):
    culls = {}
    with open(f"{run}/lineage.jsonl") as f:
        for line in f:
            r = json.loads(line)
            if r.get("death") == "cull":
                culls.setdefault((r["population"], r["generation"]), []).append(r["name"])
    hist = json.load(open(f"{run}/history.json"))["history"]
    shift = sorted({h["season"] for h in hist if "shift" in h})
    culled = sorted({h["season"] for h in hist if "culled" in h})
    first = next((h for h in hist if "shift" in h), None)
    with open(f"{run}/events.txt", "w") as f:
        f.write("kind\tpopulation\tseason\tcount\tnames\n")
        for (pop, s), names in sorted(culls.items()):
            f.write(f"cull\t{pop}\t{s}\t{len(names)}\t{','.join(names)}\n")
        if shift:
            f.write(f"shift\t-\t{shift[0]}\t{len(shift)}\t{json.dumps(first['shift'])} on every entry from {shift[0]} to {shift[-1]}\n")
        if culled:
            f.write(f"culled_entries\t-\t{culled[0]}\t{len(culled)}\tseasons {culled}\n")


def write_groups(run):
    path = os.path.join(run, "cohorts.jsonl")
    if not os.path.exists(path):
        return
    with open(path) as f, open(os.path.join(run, "groups.txt"), "w") as out:
        out.write("season\tpopulation\tsizes\tnames_in_groups_below_modal\n")
        for line in f:
            c = json.loads(line)
            sizes = [len(g) for g in c["groups"]]
            modal = max(set(sizes), key=sizes.count) if sizes else 0
            small = [m["name"] for g in c["groups"] if len(g) < modal for m in g]
            out.write(f"{c['season']}\t{c['cohort']}\t{','.join(map(str, sizes))}\t{','.join(small)}\n")


def main(run, bodysig_only=False, to=None):
    if not bodysig_only:
        write_seasons(run)
        write_events(run)
        write_groups(run)
    missing = write_bodysig(run, to)
    print(f"wrote {run}: " + ("bodysig.txt" if bodysig_only else "seasons.txt lineage-last.txt bodysig.txt events.txt groups.txt")
          + (f"  ({missing} genomes missing: body '-')" if missing else ""))


if __name__ == "__main__":
    a = sys.argv[2:]
    main(sys.argv[1], "--bodysig-only" in a, a[a.index("--to") + 1] if "--to" in a else None)
