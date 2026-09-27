"""RBT-120 control K2 at full size (PREREGISTRATION.md §9 item 1): the designed body is untouched by the budget in a
real arm's configuration, not only in the tiny test.

    k2_check.py OUT_DIR [SEED] [LINE] [GENERATIONS]  > controls/k2_full_population.txt

Runs one line of an O arm (RBT-113's command line) and of a B arm (the same plus --motor-budget 1.77) at full
population (40 + 40) and draws (2), for a few generations, and compares every conventional lineage row (and the
holistic rows, which should differ once a founder over the budget is scaled).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world as W  # noqa: E402


def rows(d, kind):
    return [r for r in map(json.loads, open(os.path.join(d, "lineage.jsonl"))) if r["population"] == kind]


def main(argv):
    out = argv[0]
    seed = int(argv[1]) if len(argv) > 1 else 5
    line = argv[2] if len(argv) > 2 else "D"
    G = int(argv[3]) if len(argv) > 3 else 3
    runs = {}
    for tag, cmd in (("O", W.W113.command), ("B", W.command)):
        d = os.path.join(out, tag)
        c = cmd(line, "", seed, d, workers="4", generations=G)
        subprocess.run([sys.executable] + c[1:], check=True, stdout=subprocess.DEVNULL)  # c[0] is "python"
        runs[tag] = d
    print(f"# RBT-120 K2 at full size: line {line}, seed {seed}, {G} generations, population 40 + 40, 2 draws; O = RBT-113's command, B = + --motor-budget {W.MOTOR_BUDGET}")
    for kind in ("conventional", "holistic"):
        o, b = rows(runs["O"], kind), rows(runs["B"], kind)
        same = sum(x == y for x, y in zip(o, b))
        first = next((x["generation"] for x, y in zip(o, b) if x != y), None)
        print(f"{kind:12s} rows {len(o)} vs {len(b)}; identical {same}; first differing generation {first}")
    ok = rows(runs["O"], "conventional") == rows(runs["B"], "conventional")
    print("K2 FULL SIZE: PASS (every designed-body row identical)" if ok else "K2 FULL SIZE: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
