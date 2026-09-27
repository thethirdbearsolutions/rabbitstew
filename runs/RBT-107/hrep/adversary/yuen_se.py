"""RBT-107 H-REP readout adversary: Yuen's standard error, three conventions, on every scored component.

    python runs/RBT-107/hrep/adversary/yuen_se.py [HREP_DIR]      (stdlib only; uses rederive.py's parser and t cdf)

stats107.yuen's docstring says se = s_w / ((1 - 2 trim) sqrt n); its code uses s_w / ((h / n) sqrt n), h = n - 2g.  They
agree when 0.2 n is an integer (n = 20) and differ at n = 19 (h/n = 13/19 = 0.684 against 0.6).  Yuen's (1974) own form,
sqrt((n - 1) s_w^2 / (h (h - 1))), is printed as the third.  df = h - 1 in all three.  stats107's self-checks test the
trimmed mean and df only, never the se.  Also prints stats107.yuen itself for comparison (imported only here).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import rederive as R  # noqa: E402
import stats107 as S  # noqa: E402


def main():
    C = {s: {k: R.contrasts(s, k) for k in (R.CO, R.DE)} for s in R.SEEDS}
    both = [s for s in R.SEEDS if C[s][R.CO] and C[s][R.DE]]
    sets = {
        "DES A_SB (<0) per-fauna n=20": [-C[s][R.DE]["SB"] for s in R.SEEDS],
        "DES A_SN (<0) per-fauna n=20": [-C[s][R.DE]["SN"] for s in R.SEEDS],
        "DES A_SB (<0) common n=19": [-C[s][R.DE]["SB"] for s in both],
        "DES A_SN (<0) common n=19": [-C[s][R.DE]["SN"] for s in both],
        "PAIR P (>0) n=19": [C[s][R.CO]["SB"] - C[s][R.DE]["SB"] for s in both],
        "PAIR P_N (>0) n=19": [C[s][R.CO]["SN"] - C[s][R.DE]["SN"] for s in both],
    }
    for k, x in sets.items():
        n = len(x)
        g = int(math.floor(0.2 * n))
        s = sorted(x)
        h = n - 2 * g
        tm = sum(s[g:n - g]) / h
        w = [min(max(v, s[g]), s[n - g - 1]) for v in s]
        wm = sum(w) / n
        sw = math.sqrt(sum((v - wm) ** 2 for v in w) / (n - 1))
        forms = (("stats107 code h/n", sw / ((h / n) * math.sqrt(n))),
                 ("docstring (1-2*0.2)", sw / (0.6 * math.sqrt(n))),
                 ("Yuen 1974", sw * math.sqrt((n - 1) / (h * (h - 1)))))
        print(f"{k}: " + " | ".join(f"{f} p {R.t_sf(tm / se, h - 1):.4f}" for f, se in forms)
              + f" | stats107.yuen p {S.yuen(x)[3]:.4f}")


if __name__ == "__main__":
    main()
