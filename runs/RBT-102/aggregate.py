"""RBT-102: the pre-registered verdict across the ten RBT-90 part-2 arms (runs/RBT-102/PREREG.md).

    python runs/RBT-102/aggregate.py runs/RBT-102/arm-*.txt

Reads the SUMMARY line of each arm readout written by analyse.py. Every number is re-derivable
from those committed readouts.
"""
import json
import math
import sys

T9 = 2.262157                     # two-sided 95% t, 9 degrees of freedom
DRIFT_K, DRIFT_N = 84, 200_000    # RBT-91 structural arrivals, weight_sigma 0.4


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    arms = []
    for path in sys.argv[1:]:
        line = [l for l in open(path) if l.startswith("SUMMARY ")][-1]
        arms.append((path, json.loads(line[len("SUMMARY "):])))
    arms.sort(key=lambda x: x[1]["seed"])
    dl, dh = wilson(DRIFT_K, DRIFT_N)
    print("# RBT-102 verdict across the RBT-90 part-2 arms\n")
    print(f"drift reference (RBT-91, weight_sigma 0.4): {DRIFT_K} of {DRIFT_N} = {100 * DRIFT_K / DRIFT_N:.3f}% "
          f"[{100 * dl:.4f}, {100 * dh:.4f}] (Wilson 95%); upper bound p_u = {100 * dh:.4f}%\n")
    print("| seed | positive control | X (window carriage) | window depth | seasons with a carrier | founders carrying | births | carriers born | de novo | depth 17-21 births (carriers) | window carriers | compass | ANTI | undetermined |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for _, s in arms:
        print(f"| {s['seed']} | {s['pc_detected']}/{s['pc_total']}{' PASS' if s['pc_pass'] else ' FAIL'} | "
              f"{100 * s['X']:.4f}% | {s['window_depth']:.1f} | {s['seasons_any']}/{s['n_seasons']} | "
              f"{s['founder_carriers']}/{s['founders']} | {s['births']} | {s['carriers_born']} | {s['de_novo']} | "
              f"{s['depth_matched']} ({s['depth_matched_carriers']}) | {s['window_carriers']} | {s['compass']} | "
              f"**{s['anti']}** | {s['undetermined']} |")
    n = len(arms)
    X = [s["X"] for _, s in arms]
    m = sum(X) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in X) / (n - 1)) if n > 1 else float("nan")
    hw = T9 * sd / math.sqrt(n) if n == 10 else float("nan")
    L, U = m - hw, m + hw
    print(f"\n## Carriage verdict (pre-registered rule; requires all ten arms and every positive control passing)\n")
    print(f"  arms read: {n}; positive controls passing: {sum(s['pc_pass'] for _, s in arms)} of {n}")
    print(f"  mean X = {100 * m:.4f}%, SD {100 * sd:.4f}%, t(9) 95% CI [{100 * L:.4f}%, {100 * U:.4f}%]")
    print(f"  arms with X > p_u: {sum(1 for x in X if x > dh)} of {n}")
    if n != 10 or not all(s["pc_pass"] for _, s in arms):
        verdict = "NO VERDICT (fewer than ten arms, or a positive control failed)"
    elif L > dh:
        verdict = "HELD ABOVE DRIFT"
    elif U <= dh:
        verdict = "NOT HELD"
    else:
        verdict = "UNRESOLVED"
    print(f"  VERDICT: **{verdict}**")
    births = sum(s["births"] for _, s in arms)
    dn = sum(s["de_novo"] for _, s in arms)
    dm = sum(s["depth_matched"] for _, s in arms)
    dmc = sum(s["depth_matched_carriers"] for _, s in arms)
    ml, mh = wilson(dmc, dm)
    print(f"\n## Births, pooled (secondary)\n")
    print(f"  de novo arrivals {dn} in {births} births ({100 * dn / births:.4f}% per birth)" if births else "  no births")
    print(f"  births at depth 17-21 carrying: {dmc} of {dm}" + (f" = {100 * dmc / dm:.4f}% [{100 * ml:.4f}, {100 * mh:.4f}]" if dm else ""))
    c = sum(s["compass"] for _, s in arms)
    a = sum(s["anti"] for _, s in arms)
    u = sum(s["undetermined"] for _, s in arms)
    print(f"\n## Signing, pooled over distinct window carriers (the inversion count is primary)\n")
    print(f"  compasses {c}, **ANTI-COMPASSES {a}**, undetermined {u}")
    if c + a:
        lo, hi = wilson(c, c + a)
        print(f"  compass fraction of resolved carriers {100 * c / (c + a):.1f}% [{100 * lo:.1f}, {100 * hi:.1f}] (Wilson 95%);"
              f" null 50% by sign symmetry; RBT-91's drift arrivals 42.2% [32.1, 52.9]")
    print(f"  links-alone |a| >= paying rung: {sum(s['alone_reaches_rung'] for _, s in arms)}")


if __name__ == "__main__":
    main()
