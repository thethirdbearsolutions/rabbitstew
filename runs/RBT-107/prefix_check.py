"""RBT-107 gate V-EXT: an extended arm must reproduce its committed source arm before season 600, from committed tables.

    python runs/RBT-107/prefix_check.py EXTENDED_DIR SOURCE_DIR [LAST]      (LAST defaults to 600)

1. seasons.txt: every row with season < LAST, on the five columns every source table carries (alive, births, deaths,
   mean_lifetime_score, best_lifetime_score), compared as text.  RBT-90's tables lack mean_age/max_age; RBT-92's
   readout compares fields for the same reason.
2. lineage-last.txt: every source row of an individual last seen before LAST - 1 (it died before the extension)
   is identical in the extended table; every source row last seen at LAST - 1 (alive at the join) has an extended row
   with the same name, parents and birth season (generation - age), last seen at or after LAST - 1.
3. bodysig.txt and wiring.txt, when the source committed them: every row of an individual born before LAST is identical.
Prints PASS or FAIL per part, then V-EXT PASS/FAIL; exit 1 on FAIL.
"""
import csv
import os
import sys

COLS = ("alive", "births", "deaths", "mean_lifetime_score", "best_lifetime_score")


def tsv(path):
    return list(csv.DictReader(open(path), delimiter="\t"))


def main(ext, src, last=600):
    ok = True

    def verdict(name, bad, n):
        nonlocal ok
        ok &= not bad
        print(f"{name}: {'PASS' if not bad else 'FAIL'} ({n} rows compared, {len(bad)} differ)" + (f"; first: {bad[0]}" if bad else ""))

    s_src = {(r["season"], r["population"]): r for r in tsv(os.path.join(src, "seasons.txt")) if int(r["season"]) < last}
    s_ext = {(r["season"], r["population"]): r for r in tsv(os.path.join(ext, "seasons.txt"))}
    bad = [k for k, r in s_src.items() if k not in s_ext or any(r[c] != s_ext[k][c] for c in COLS)]
    verdict(f"seasons.txt [0, {last})", bad, len(s_src))
    top = max(int(s) for s, _ in s_ext)
    print(f"extended seasons.txt runs to season {top}")

    l_ext = {(r["population"], r["name"]): r for r in tsv(os.path.join(ext, "lineage-last.txt"))}
    bad, n = [], 0
    for r in tsv(os.path.join(src, "lineage-last.txt")):
        n += 1
        k, e = (r["population"], r["name"]), l_ext.get((r["population"], r["name"]))
        if int(r["generation"]) < last - 1:
            if e != r:
                bad.append(k)
        elif (e is None or e["parents"] != r["parents"] or int(e["generation"]) < last - 1
              or int(e["generation"]) - int(e["age"]) != int(r["generation"]) - int(r["age"])):
            bad.append(k)
    verdict("lineage-last.txt (dead before the join identical; alive at the join continued)", bad, n)

    for name in ("bodysig.txt", "wiring.txt"):
        if not os.path.exists(os.path.join(src, name)):
            print(f"{name}: not committed at the source; skipped")
            continue
        e = {(r["population"], r["name"]): r for r in tsv(os.path.join(ext, name))} if os.path.exists(os.path.join(ext, name)) else {}
        rows = [r for r in tsv(os.path.join(src, name)) if int(r["born"]) < last]
        verdict(f"{name} (born before {last})", [(r["population"], r["name"]) for r in rows if e.get((r["population"], r["name"])) != r], len(rows))
    print(f"V-EXT {'PASS' if ok else 'FAIL'}: {ext} against {src}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 600))
