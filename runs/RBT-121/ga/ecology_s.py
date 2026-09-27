"""RBT-121 audit B, probe 4: what selection coefficient the ecology's economy gives a small heritable gain.

    python runs/RBT-121/ga/ecology_s.py > runs/RBT-121/ga/ecology_s.txt

A synthetic population run through a transcription of `Ecology.step`'s economy (ecology.py:476-548): energy += gain -
living cost; death at energy <= 0 or age >= max_age; breeders are everyone at or above the birth threshold, SHUFFLED,
and breed in that order while a slot is free, paying birth_cost into the child.  Defaults are EcologyConfig's
(capacity 60, cost 0.05, threshold 3, birth cost 1, initial 2, max age 60).  Each individual's season gain is
mu + delta (carriers) + N(0, sigma); sigma 1.16 is probe 3's member x draw SD of net yield.  A carrier's child is a
carrier unless erosion u removes it.  Output: the carrier share after 150 seasons from 10%, and the per-season s
fitted from the log-odds, for the shipped order ("shuffled") and for the proposed fix ("richest first").
"""
import numpy as np


def run(delta, order, rng, mu=0.25, sigma=1.16, u=0.0, seasons=150, cap=60, cost=0.05, thr=3.0, bc=1.0, e0=2.0, max_age=60):
    n = cap
    E = np.full(n, e0); A = rng.integers(0, max_age, n); C = np.zeros(n, bool); C[: n // 10] = True
    share = []
    for _ in range(seasons):
        E = E + mu + delta * C + rng.normal(0, sigma, len(E)) - cost
        A = A + 1
        ok = (E > 0) & (A < max_age)
        E, A, C = E[ok], A[ok], C[ok]
        br = np.flatnonzero(E >= thr)
        br = rng.permutation(br) if order == "shuffled" else br[np.argsort(-E[br], kind="stable")]
        free = cap - len(E)
        kids = br[: max(0, free)]
        E[kids] -= bc
        kc = C[kids] & (rng.random(len(kids)) >= u)
        E = np.concatenate([E, np.full(len(kids), bc)]); A = np.concatenate([A, np.zeros(len(kids), int)]); C = np.concatenate([C, kc])
        share.append(C.mean() if len(C) else np.nan)
    return np.array(share)


def fit_s(share):
    t = np.arange(len(share)); p = np.clip(share, 1e-3, 1 - 1e-3)
    ok = (share > 0.02) & (share < 0.98)
    ok[:5] = False
    if ok.sum() < 5:
        return float("nan")
    return float(np.polyfit(t[ok], np.log(p[ok] / (1 - p[ok])), 1)[0])


def main():
    rng = np.random.default_rng(12104)
    print("# per-season gain mu 0.25 + delta, member x season noise sigma 1.16; 200 replicate populations each; start share 10%")
    for u in (0.0, 0.15):
        for delta in (0.0, 0.02, 0.05, 0.1, 0.2):
            cells = []
            for order in ("shuffled", "richest first"):
                S = np.array([run(delta, order, rng, u=u) for _ in range(200)])
                fin = S[:, -1]
                s = np.nanmedian([fit_s(x) for x in S])
                cells.append(f"{order:13s} share at 150: {np.nanmean(fin) * 100:5.1f}% (lost {np.mean(fin == 0) * 100:3.0f}%), s/season {s:+.4f}")
            print(f"erosion u {u:.2f}  delta +{delta:<4}  " + "  |  ".join(cells))


if __name__ == "__main__":
    main()
