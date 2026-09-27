"""RBT-107 H1: POST HOC lines, printed and not scored (none is a registered test; none enters a verdict).

    python runs/RBT-107/h1/h1_posthoc.py > runs/RBT-107/h1/posthoc.txt

1. A2.9 point 3 ("a hypothesis to watch", recorded before H-REP was read): the designed RESPONSE_random net of the null,
   G_S^random - G_N^random, at every read point, beside RESPONSE_random against base (G_S^random - G_B^random), t intervals,
   on each fauna's own complete seeds.  The registered readout prints RESPONSE_random against base only.
2. The per-seed table at T + 800 (designed A_SB, designed A_SN, paired P, paired P_N), UNREAD where a fauna is extinct.
"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rbt107_readout_ph", os.path.join(os.path.dirname(HERE), "readout.py"))
RO = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RO)


def main():
    print(__doc__.split("\n\n")[0])
    sm = RO.Sample("FRESH", RO.FRESH_SEEDS, True)
    print("\n== 1. A2.9 point 3 (POST HOC): RESPONSE_random against base and net of the null, per read point")
    for k in RO.KINDS:
        for d in (110, 400, 600, 800):
            rb, rn = [], []
            for s in sm.seeds:
                g = {a: RO.G(RO.garden(sm.label(a, s, k, d))) for a in ("shift", "base", "cull20")}
                if all(g.values()):
                    rb.append(g["shift"][1] - g["base"][1])
                    rn.append(g["shift"][1] - g["cull20"][1])
            print(f"  {k:12s} d={d:>3} n={len(rb)} RESPONSE_random vs base {RO.fmt(rb)} | net of the null {RO.fmt(rn)}")
    print(f"\n== 2. per seed at T+{RO.DSTAR} (designed A_SB, designed A_SN, paired P, paired P_N)")
    d = RO.DSTAR
    t = [RO.table(sm, "conventional", d, "SB"), RO.table(sm, "conventional", d, "SN"),
         RO.paired(sm, d, "SB"), RO.paired(sm, d, "SN")]
    for s in sm.seeds:
        print(f"    seed {s:>2}: " + " ".join(f"{x[s]:+.3f}" if s in x else "UNREAD" for x in t))


if __name__ == "__main__":
    main()
