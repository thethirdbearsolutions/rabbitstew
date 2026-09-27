"""RBT-113 design-adversary probe: can each per-arm control FAIL?  (The design shows them passing only.)

Takes one real arm (U/, D/, C/ of one seed), copies it, applies one corruption at a time and runs readout.py's
own `controls()` plus its manipulation check, printing whether the corruption is caught.

    controls_can_fail.py ARM_DIR
"""
import copy
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.environ.get("RBT113", "runs/RBT-113"))
import readout as ro  # noqa: E402


def load(arm):
    cfgs, runs = {}, {}
    for L in ro.LINES:
        cfgs[L], runs[L] = ro.read_run(os.path.join(arm, L))
    return cfgs, runs


def verdict(arm, cfgs, runs):
    G = cfgs["U"]["generations"]
    bad = ro.controls(arm, cfgs, runs, G)
    for f in ro.FAUNAE:
        ser = {}
        for L in ro.LINES:
            m, S, _, _ = ro.line_series(runs[L][f]) if len({r["generation"] for r in runs[L][f]}) == G else (None, None, None, None)
            if m is None:
                break
            ser[L] = (m, S)
        else:
            st = ro.arm_stats(ser)
            if not st["S_U"] - st["S_D"] > 0:
                bad.append(f"{f}: manipulation check")
    return bad


def main(arm):
    cfgs0, runs0 = load(arm)
    G = cfgs0["U"]["generations"]
    print(f"# controls_can_fail on {arm} (G = {G})")
    print(f"  unmodified: {'PASS' if not verdict(arm, cfgs0, runs0) else 'FAIL ' + str(verdict(arm, cfgs0, runs0))}")

    def case(name, fn, armname=arm):
        c, r = copy.deepcopy(cfgs0), copy.deepcopy(runs0)
        fn(c, r)
        bad = verdict(armname, c, r)
        print(f"  {name:62s} {'CAUGHT' if bad else 'MISSED'}  {bad[:1]}")

    def u_parent_from_bottom(c, r):  # an up-line child whose parent is the worst of its generation
        rows = r["U"]["holistic"]
        g3 = [x for x in rows if x["generation"] == 3]
        worst = min(g3, key=lambda x: x["fitness"])["name"]
        kids = [x for x in rows if x["generation"] == 4]
        swap = kids[0]["parents"][0]  # rename one real parent to the worst member, everywhere: k unchanged
        for x in kids:
            x["parents"] = [worst if q == swap else q for q in x["parents"]]
    case("1/3 U child bred from the bottom (holistic, gen 3)", u_parent_from_bottom)

    def d_parent_from_top(c, r):
        rows = r["D"]["conventional"]
        g2 = [x for x in rows if x["generation"] == 2]
        best = max(g2, key=lambda x: x["fitness"])["name"]
        kids = [x for x in rows if x["generation"] == 3]
        swap = kids[0]["parents"][0]
        for x in kids:
            x["parents"] = [best if q == swap else q for q in x["parents"]]
    case("3 D child bred from the top (designed body, gen 2)", d_parent_from_top)

    def c_too_many_parents(c, r):  # the control breeds from more than k (a weaker drift than U and D)
        rows = r["C"]["holistic"]
        g1 = [x["name"] for x in rows if x["generation"] == 1]
        for i, x in enumerate([x for x in rows if x["generation"] == 2]):
            x["parents"] = [g1[i % len(g1)]]
    case("3 C bred from every member (no drift match)", c_too_many_parents)

    def c_is_selected(c, r):  # the control silently truncates up: every parent a top-k member
        rows = r["C"]["holistic"]
        for t in range(G - 1):
            gen = sorted([x for x in rows if x["generation"] == t], key=lambda x: -x["fitness"])[:10]
            for i, x in enumerate([x for x in rows if x["generation"] == t + 1]):
                x["parents"] = [gen[i % len(gen)]["name"]]
    case("3 C bred from the top k every generation (a selected 'control')", c_is_selected)

    def wrong_line(c, r):
        c["D"]["line"] = "up"
    case("1 D config says line up", wrong_line)

    def wrong_operator(c, r):
        for L in ro.LINES:
            c[L]["mutation"]["global_bias_sigma"] = 0.0
    case("1 default arm run with --global-bias-sigma 0", wrong_operator)

    def gen0_differs(c, r):
        r["C"]["holistic"][0]["fitness"] += 0.5
    case("2 generation 0 differs on C", gen0_differs)

    def missing_gen(c, r):
        r["D"]["conventional"] = [x for x in r["D"]["conventional"] if x["generation"] != G - 1]
    case("5 D missing its last generation", missing_gen)

    def worlds_differ(c, r):  # not a lineage field: the readout cannot see a world mismatch after generation 0
        pass
    print(f"  {'2 worlds differ between lines after generation 0':62s} NOT CHECKED (readout reads no history.json)")

    case("4 U and D replaced by the control line's lineage", lambda c, r: [r.__setitem__(L, copy.deepcopy(r["C"])) for L in ("U", "D")])


if __name__ == "__main__":
    main(sys.argv[1])
