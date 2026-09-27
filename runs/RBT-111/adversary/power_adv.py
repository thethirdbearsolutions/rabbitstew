"""RBT-111 design adversary: size and power of the registered test and of the within-seed permutation
alternative, re-derived independently (own code; it imports nothing from runs/RBT-111/).

Outcome model, the designer's and the RBT-108 adversary's: y = e + offset per run, e iid per run.
  N62  normal sd 0.062;  N81  normal sd 0.081;  T  normal sd 0.040 + 0.25 w.p. 1/16  (the three registered models)
  T8   normal sd 0.030 + 0.30 w.p. 1/8   (a STRESS model, not registered: a heavier one-sided discovery tail)
Scenarios: null; salt0 delta (y_s0 -= delta, expect "salt0"); salt1 delta (y_s1 += delta, expect "keys").
Tests, both exact enumerations, both via meet in the middle (independent of the designer's 2^16 matrix):
  SF   the registered test: sign-flip on c0 and on c12 (2^16), Holm at 0.05, then the reading table
  PERM c0 by the within-seed permutation test (3^16 labellings of the s0 label; perm.py), c12 by sign-flip, Holm, table

    python runs/RBT-111/adversary/power_adv.py [TRIALS] [SEEDS]      (default 10000, 16; numpy default_rng(20260927))
"""
import sys
import numpy as np

TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
N = int(sys.argv[2]) if len(sys.argv) > 2 else 16
TOL = 1e-12
MODELS = {"N62": (0.062, 0.0, 0.0), "N81": (0.081, 0.0, 0.0), "T": (0.040, 1 / 16, 0.25), "T8*": (0.030, 1 / 8, 0.30)}
SCEN = [("null", 0.0), ("salt0", 0.05), ("salt0", 0.082), ("salt1", 0.05), ("salt1", 0.082)]
H = N // 2


def signed_half_sums(x):  # x (T, m) -> (T, 2^m), every signed sum
    m = x.shape[1]
    S = 1 - 2 * ((np.arange(2 ** m)[:, None] >> np.arange(m)[None, :]) & 1)
    return x @ S.T


def sign_flip(x):  # x (T, N) -> exact two-sided p, meet in the middle by broadcasting (2^8 x 2^8)
    obs = np.abs(x.sum(1))[:, None, None]
    a, b = signed_half_sums(x[:, :H])[:, :, None], signed_half_sums(x[:, H:])[:, None, :]
    return (np.abs(a + b) >= obs - TOL).mean(axis=(1, 2))


IDX = [np.array(np.unravel_index(np.arange(3 ** m), (3,) * m)).T for m in (H, N - H)]  # (3^m, m) label choices


def perm_c0(y):  # y (T, N, 3) -> exact two-sided p over the 3^N choices of which run is labelled s0
    ch = np.stack([(y[..., 1] + y[..., 2]) / 2 - y[..., 0], (y[..., 0] + y[..., 2]) / 2 - y[..., 1],
                   (y[..., 0] + y[..., 1]) / 2 - y[..., 2]], axis=-1)  # (T, N, 3)
    obs = np.abs(ch[..., 0].sum(1))
    out = np.empty(len(y))
    for t in range(len(y)):
        L = ch[t, np.arange(H)[None, :], IDX[0]].sum(1)
        R = np.sort(ch[t, H + np.arange(N - H)[None, :], IDX[1]].sum(1))
        hi = len(R) - np.searchsorted(R, obs[t] - TOL - L, "left")
        lo = np.searchsorted(R, -obs[t] + TOL - L, "right")
        out[t] = (hi + lo).sum() / 3 ** N if obs[t] > TOL else 1.0
    return out


def holm2(p1, p2, a=0.05):
    first1 = p1 <= p2
    r_small = np.minimum(p1, p2) <= a / 2
    r_large = r_small & (np.maximum(p1, p2) <= a)
    return np.where(first1, r_small, r_large), np.where(first1, r_large, r_small)


def reading(r0, r12):
    return np.where(r12, "keys", np.where(r0, "salt0", "chance"))


def main():
    rng = np.random.default_rng(20260927)
    print(f"RBT-111 design adversary power: {TRIALS} trials per cell, n = {N} seeds x 3 salts, default_rng(20260927), fresh draws per cell")
    print("SF = registered (sign-flip c0 and c12, Holm); PERM = c0 by within-seed 3^n permutation, c12 sign-flip, Holm")
    print("columns: raw = unadjusted P(p <= 0.05); Holm = P(rejected inside Holm); '+/-' = raw rejections split by the sign of mean c0;")
    print("         read = P(reading = the scenario's expected reading); read=salt0 = P(reading = salt0): false 'salt0' under null and salt1\n")
    hdr = f"{'scenario':12} {'model':5} | {'SF raw c0':>9} {'(+ / -)':>13} {'SF Holm c0':>10} {'SF read':>7} | {'PERM raw c0':>11} {'(+ / -)':>13} {'PERM Holm c0':>12} {'PERM read':>9} | {'raw c12':>7} {'Holm c12 SF/PERM':>16} | read=salt0 SF/PERM"
    print(hdr)
    for kind, delta in SCEN:
        for model, (sd, pd, jump) in MODELS.items():
            y = rng.normal(0, sd, (TRIALS, N, 3))
            if pd:
                y += jump * (rng.random((TRIALS, N, 3)) < pd)
            if kind == "salt0":
                y[..., 0] -= delta
            elif kind == "salt1":
                y[..., 1] += delta
            c0 = (y[..., 1] + y[..., 2]) / 2 - y[..., 0]
            c12 = y[..., 2] - y[..., 1]
            p_sf = np.concatenate([sign_flip(c0[i:i + 500]) for i in range(0, TRIALS, 500)])
            p12 = np.concatenate([sign_flip(c12[i:i + 500]) for i in range(0, TRIALS, 500)])
            p_pm = perm_c0(y)
            pos = c0.mean(1) > 0
            want = {"null": "chance", "salt0": "salt0", "salt1": "keys"}[kind]
            row = f"{kind + (f' {delta:.3f}' if delta else ''):12} {model:5} |"
            res = {}
            for name, p0 in (("SF", p_sf), ("PERM", p_pm)):
                r0, r12 = holm2(p0, p12)
                rd = reading(r0, r12)
                raw = p0 <= 0.05
                res[name] = (raw.mean(), (raw & pos).mean(), (raw & ~pos).mean(), r0.mean(), (rd == want).mean(), r12.mean(), (rd == "salt0").mean())
            s, q = res["SF"], res["PERM"]
            row += f" {s[0]:9.4f} {s[1]:6.4f}/{s[2]:6.4f} {s[3]:10.4f} {s[4]:7.4f} | {q[0]:11.4f} {q[1]:6.4f}/{q[2]:6.4f} {q[3]:12.4f} {q[4]:9.4f} | {(p12 <= 0.05).mean():7.4f} {s[5]:7.4f}/{q[5]:.4f}"
            row += f" | {s[6]:.4f}/{q[6]:.4f}"
            print(row, flush=True)
    print(f"\nMonte Carlo SE: <= {0.5 / TRIALS ** 0.5:.4f} for any share; at 0.05, {np.sqrt(0.05 * 0.95 / TRIALS):.4f}.  T8* is a stress model, not registered.")


if __name__ == "__main__":
    main()
