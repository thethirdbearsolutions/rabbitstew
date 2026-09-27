"""RBT-107 H-REP readout adversary: the gates, re-checked from the committed files with an independent parser.

    python runs/RBT-107/hrep/adversary/gates.py [HREP_DIR]       (stdlib only)

NO-PEEK  every committed table under HREP_DIR/tables stops at 470: seasons.txt's last season, lineage-last.txt's last
         observation (its 'generation' column: RBT-92 tables.py reads born = generation - age), events.txt's seasons;
         every garden file and part names season 470 in its header and rows; z10 files name no season.  Prints only
         maxima and counts.
V0       seasons 0..359: base, shift and cull20 identical on alive, births, deaths, mean_lifetime_score,
         best_lifetime_score, both faunas, all 20 seeds (prefix_check.py's five columns).
V-G      each merged garden population is, by name, the fauna alive at the end of season 470 as lineage-last.txt gives it
         (born = generation - age <= 470 <= generation; a culled row's generation is T - 1, as RBT-92's Arm reads it),
         and its size equals seasons.txt's alive at 470; both halves (parts) hold the same names in the same order.
"""
import os
import sys

HREP = sys.argv[1] if len(sys.argv) > 1 else os.path.join("runs", "RBT-107", "hrep")
SEEDS = range(11, 31)
ARMS = ("base", "shift", "cull20")
KINDS = ("holistic", "conventional")
COLS = ("alive", "births", "deaths", "mean_lifetime_score", "best_lifetime_score")
READ, T = 470, 360


def tsv(p):
    lines = [l.rstrip("\n").split("\t") for l in open(p) if l.strip()]
    return [dict(zip(lines[0], r)) for r in lines[1:]]


def garden_names(p):
    head = [l for l in open(p) if l.startswith("#")]
    rows = [l.rstrip("\n").split("\t") for l in open(p) if l.strip() and not l.startswith("#")]
    assert all(int(r[3]) == READ for r in rows), p
    assert all(f"season {READ}" in h for h in head), p
    return [r[4] for r in rows]


def main():
    fails = []
    maxima = {"seasons.txt": -1, "lineage-last.txt": -1, "events.txt": -1}
    seasons, alive_sets = {}, {}
    for s in SEEDS:
        for a in ARMS:
            d = os.path.join(HREP, "tables", f"{a}-{s}")
            rows = tsv(os.path.join(d, "seasons.txt"))
            maxima["seasons.txt"] = max(maxima["seasons.txt"], max(int(r["season"]) for r in rows))
            seasons[(a, s)] = {(int(r["season"]), r["population"]): r for r in rows}
            ev = tsv(os.path.join(d, "events.txt"))
            if ev:
                maxima["events.txt"] = max(maxima["events.txt"], max(int(r["season"]) for r in ev))
            culled = {n for r in ev if r["kind"] == "cull" for n in r["names"].split(",") if n}
            lin = tsv(os.path.join(d, "lineage-last.txt"))
            maxima["lineage-last.txt"] = max(maxima["lineage-last.txt"], max(int(r["generation"]) for r in lin))
            for k in KINDS:
                al = set()
                for r in lin:
                    if r["population"] != k:
                        continue
                    g, age = int(r["generation"]), int(r["age"])
                    if r["name"] in culled:
                        g -= 1
                    if g - age <= READ <= g:
                        al.add(r["name"])
                alive_sets[(a, s, k)] = al
    for f, m in maxima.items():
        print(f"NO-PEEK {f}: last season in any committed table = {m}")
        if m > READ:
            fails.append(f"NO-PEEK {f}")
    nz = 0
    for f in os.listdir(os.path.join(HREP, "garden")):
        if f.startswith("z10"):
            nz += 1
            for line in open(os.path.join(HREP, "garden", f)):
                if "season" in line:
                    fails.append(f"z10 file {f} names a season")
    print(f"NO-PEEK z10: {nz} files, rows are (seed, fauna, Z10, n_pairs) only")
    # V0
    bad0 = []
    for s in SEEDS:
        for a in ("shift", "cull20"):
            for t in range(T):
                for k in KINDS:
                    B, X = seasons[("base", s)].get((t, k)), seasons[(a, s)].get((t, k))
                    if B is None or X is None or any(B[c] != X[c] for c in COLS):
                        bad0.append((a, s, t, k))
    print(f"V0 seasons 0..{T - 1}, {len(COLS)} columns, both faunas, 20 seeds x 2 arms vs base: "
          f"{'PASS' if not bad0 else 'FAIL ' + str(bad0[:5])}")
    fails += ["V0"] if bad0 else []
    # V-G
    badg, sizes = [], {}
    for s in SEEDS:
        for a in ARMS:
            for k in KINDS:
                lab = f"fresh-{a}-{s}-{k}-d110"
                names = garden_names(os.path.join(HREP, "garden", f"{lab}.txt"))
                p0 = garden_names(os.path.join(HREP, "garden", "parts", f"{lab}.w00-15.txt"))
                p1 = garden_names(os.path.join(HREP, "garden", "parts", f"{lab}.w16-31.txt"))
                al = alive_sets[(a, s, k)]
                n_seasons = int(seasons[(a, s)].get((READ, k), {"alive": "0"})["alive"])
                sizes[(a, s, k)] = len(names)
                if set(names) != al or len(names) != len(al) or len(names) != n_seasons or names != p0 or names != p1:
                    badg.append(f"{lab}: garden {len(names)} lineage {len(al)} seasons.txt {n_seasons}")
    print(f"V-G 120 populations (names = lineage-last alive at {READ} = seasons.txt alive; parts agree): "
          f"{'PASS' if not badg else 'FAIL ' + str(badg)}")
    fails += ["V-G"] if badg else []
    ext = sorted({(s, k) for (a, s, k), n in sizes.items() if n == 0})
    print(f"  populations of size 0: {ext}")
    for (s, k) in ext:
        last_alive = max(t for (t, kk), r in seasons[('base', s)].items() if kk == k and int(r['alive']) > 0)
        same = all(max(t for (t, kk), r in seasons[(a, s)].items() if kk == k and int(r['alive']) > 0) == last_alive for a in ARMS)
        print(f"  seed {s} {k}: last season with alive > 0 is {last_alive} in base; identical in all three arms: {same}")
    print(f"ALL GATES: {'PASS' if not fails else 'FAIL ' + str(fails)}")


if __name__ == "__main__":
    main()
