"""RBT-107 new seeds: the onset T by RBT-92's committed rule, from a base that has played seasons 0..339 only.

    python runs/RBT-107/new_onset.py BASE_DIR SEED          prints "SEED<TAB>T<TAB>..." (T in [340, 399])
    python runs/RBT-107/new_onset.py --validate             the ten old seeds: must reproduce runs/RBT-92/onset.txt

RBT-92's onset.py waits for a finished 600-season arm, but its rule reads deaths over [280, 340) only (its docstring:
"It reads only seasons [280, 340)").  This applies the same rule, by importing onset.py's constants and deaths reader,
to a base stopped at 340, so a new seed's shift and cull20 arms can fork at T - 1 (fork.py).  The printed references
that onset.py adds read seasons >= T and are omitted.  --validate recomputes the ten committed onsets from the RBT-90
tables truncated to [0, 340) and compares them with onset.txt.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
spec = importlib.util.spec_from_file_location("rbt92_onset", os.path.join(ROOT, "runs", "RBT-92", "onset.py"))
O = importlib.util.module_from_spec(spec)
spec.loader.exec_module(O)


def rule(d):
    tot = lambda s0, s1: sum(d.get((t, k), 0) for t in range(s0, s1) for k in O.KINDS)
    p = max(range(O.PLO, O.PHI + 1), key=lambda t: (tot(t, t + 10), t))
    c = p + 5
    return (c + O.PERIOD // 2 if c + O.PERIOD // 2 >= O.LO else c + O.PERIOD + O.PERIOD // 2), p, tot(p, p + 10)


def onset(seasons_txt):
    d, a = O.deaths_alive(seasons_txt)
    d = {k: v for k, v in d.items() if k[0] < O.LO}  # the rule's reach, and nothing past it
    if max(s for s, _ in d) < O.LO - 1:
        raise SystemExit(f"{seasons_txt} ends before season {O.LO - 1}")
    return rule(d)


def main():
    if sys.argv[1] == "--validate":
        ok = True
        committed = {}
        for line in open(os.path.join(ROOT, "runs", "RBT-92", "onset.txt")):
            f = line.split("\t")
            if f[0].isdigit() and f[1].isdigit():
                committed[int(f[0])] = int(f[1])
        for seed, T in committed.items():
            t, p, D = onset(os.path.join(ROOT, "runs", "RBT-90", f"forage-{seed}", "seasons.txt"))
            ok &= t == T
            print(f"{seed}\tT {t} (committed {T})\t{'MATCH' if t == T else 'MISMATCH'}\twave [{p},{p + 10}) deaths {D}")
        print(f"NEW-ONSET VALIDATE {'PASS' if ok else 'FAIL'}: the rule on seasons [0, 340) reproduces onset.txt on {len(committed)} seeds")
        return 0 if ok else 1
    base, seed = sys.argv[1], int(sys.argv[2])
    t, p, D = onset(os.path.join(base, "seasons.txt"))
    print(f"{seed}\t{t}\twave window [{p},{p + 10}) deaths {D}\t(runs/RBT-107/new_onset.py, RBT-92's rule on seasons [0, 340) of {base})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
