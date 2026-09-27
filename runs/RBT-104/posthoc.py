"""RBT-104 readout: POST HOC descriptions. None of these enters the verdict; each is labelled POST HOC.

Reads only the committed per-arm readouts (function.txt, function-pc.txt, peek-a3-*.txt, rbt102.txt)
through readout.py's own parsers, and prints:
  P1  the install control (a = 64 motif on each arm's own bests) read as S8 - S1 on the same seed:
      the same install in the new host against the old one (lesson 8's clause: only new - old is a
      response to the change);
  P2  the primary F, S8 - S1, on all ten seeds, usable or not;
  P3  the Amendment 3 window readings on all ten S8 seeds, usable or not: held at both, above at one;
  P4  paying carriers on own links against paying in host, per S8 arm.
"""
import importlib.util
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("rbt104_readout", os.path.join(HERE, "readout.py"))
ro = importlib.util.module_from_spec(_s)
_s.loader.exec_module(ro)
R = lambda *p: os.path.join(HERE, *p)


def main():
    seeds = ro.SEEDS
    print("# RBT-104 readout: POST HOC descriptions (not verdict-bearing)\n")
    pc = {(a, s): ro.function(R(f"{a}-{s}", "function-pc.txt")) for a in ("S1", "S8") for s in seeds}
    fb = {(a, s): ro.function(R(f"{a}-{s}", "function.txt")) for a in ("S1", "S8") for s in seeds}
    print("## P1 (POST HOC). The installed a = 64 motif, at DEFAULT scale (+-1, 32), on S8's own bests against S1's, same seed")
    print("   (readout adversary F1/F3: this is the link scale's instantaneous effect on a default-scale compass; a fixed S1 host")
    print("    scaled x8 costs about the same, -0.66; the same motif at the arm's scale (+-8, 256) passes on S8 hosts)\n")
    print("| seed | S1 host F | S8 host F | S8 - S1 |")
    print("|---|---|---|---|")
    d = []
    for s in seeds:
        x, y = pc[("S1", s)], pc[("S8", s)]
        d.append(y["F"] - x["F"])
        print(f"| {s} | {ro.fmt(x['F'], x['lo'], x['hi'])} {x['verdict']} | {ro.fmt(y['F'], y['lo'], y['hi'])} {y['verdict']} | {d[-1]:+.3f} |")
    print(f"\n  installed-motif F, S8 host - S1 host, t(9): {ro.fmt(*ro.t_int(d))}; FOOD-DEPENDENT on S1 hosts "
          f"{sum(pc[('S1', s)]['fd'] for s in seeds)}/10, on S8 hosts {sum(pc[('S8', s)]['fd'] for s in seeds)}/10")
    print("\n## P2 (POST HOC). The evolved champions' primary F, S8 - S1, all ten seeds (usable or not)\n")
    e = [fb[("S8", s)]["F"] - fb[("S1", s)]["F"] for s in seeds]
    print(f"  F(S8) - F(S1), t(9): {ro.fmt(*ro.t_int(e))}; primary FD: S1 {sum(fb[('S1', s)]['fd'] for s in seeds)}/10 "
          f"{[s for s in seeds if fb[('S1', s)]['fd']]}, S8 {sum(fb[('S8', s)]['fd'] for s in seeds)}/10; compass-FD (ATTRIBUTION): "
          f"S1 {sum(fb[('S1', s)]['compass_fd'] for s in seeds)}/10, S8 {sum(fb[('S8', s)]['compass_fd'] for s in seeds)}/10")
    print("\n## P3 (POST HOC). Amendment 3 window readings on all ten S8 seeds, usable or not\n")
    both = one = 0
    for s in seeds:
        w3, w5 = ro.peek(R(f"S8-{s}", "peek-a3-300.txt")), ro.peek(R(f"S8-{s}", "peek-a3-599.txt"))
        both += w3["above"] and w5["above"]
        one += w3["above"] + w5["above"]
        print(f"  S8-{s}: 300 k_planted {w3['k']} / n {w3['n']} / B {w3['B']} (k_bare {w3['k_bare']}); "
              f"599 k_planted {w5['k']} / n {w5['n']} / B {w5['B']} (k_bare {w5['k_bare']})")
    print(f"\n  held at both 300 and 599: {both}/10 seeds (full-operator null per seed 0.005); "
          f"readings above B at a single season: {one}/20; NOT READ. Null single-season rate on k_planted 0.035 per reading "
          f"(readout adversary F10, readout-adversary/p3_null.txt): 0.70 expected of 20, P(>= {one} | null) 0.0002-0.053")
    print("\n## P4 (POST HOC). S8 window carriers: paying on own links against paying in host\n")
    for s in seeds:
        a = ro.rbt102(R(f"S8-{s}", "rbt102.txt"))
        print(f"  S8-{s}: distinct window carriers {a['window_carriers']}, paying on own links {a['paying_own']}, paying in host {a['paying_host']}")


if __name__ == "__main__":
    main()
