"""RBT-22: reproduce RBT-13's smell_range table for the normalised smell modes.

Signal read by a nose at 0 / 2 / 3 / 4 m from the centre of a 12-item, 3 m disc, and the
slope per metre there, averaged over many random item layouts.  Pure sensor arithmetic --
the same expression Simulation._intensity evaluates -- so no physics is needed.
"""
import numpy as np

ITEMS, RADIUS, EAT = 12, 3.0, 0.35


def signal(mode, decay, point, items):
    d = np.linalg.norm(items - point, axis=1)
    total = float(np.exp(-d / decay).sum())
    n = len(items)
    if mode == "mean":
        i = total / n
        return i / (1.0 + i)
    if mode == "log":
        return float(np.clip(np.log1p(total) / np.log1p(n), 0.0, 1.0))
    return total / (1.0 + total)


def layout(rng):
    ang, rad = rng.uniform(0, 2 * np.pi, ITEMS), RADIUS * np.sqrt(rng.uniform(0, 1, ITEMS))
    return np.stack([rad * np.cos(ang), rad * np.sin(ang)], axis=1)


def table(mode, decay, trials=4000, h=0.05):
    rng = np.random.default_rng(801)
    rs = [0.0, 2.0, 3.0, 4.0]
    sig = {r: [] for r in rs}
    slope = {r: [] for r in rs}
    for _ in range(trials):
        f = layout(rng)
        for r in rs:
            p0, pm, pp = np.array([r, 0.0]), np.array([r - h, 0.0]), np.array([r + h, 0.0])
            sig[r].append(signal(mode, decay, p0, f))
            slope[r].append(abs(signal(mode, decay, pp, f) - signal(mode, decay, pm, f)) / (2 * h))
    return [np.mean(sig[r]) for r in rs], [np.mean(slope[r]) for r in rs]


def disc_span(mode, decay, trials=4000):
    """Signal difference between 0.5 m and 2.5 m from a food item at the centre: what a nose
    crossing the disc actually has to read.  This is the quantity the tests assert on."""
    rng = np.random.default_rng(801)
    out = []
    for _ in range(trials):
        f = layout(rng)
        f[0] = (0.0, 0.0)
        out.append(signal(mode, decay, np.array([0.5, 0.0]), f) - signal(mode, decay, np.array([2.5, 0.0]), f))
    return float(np.mean(out))


arms = [("sum", 1.0, "baseline (RBT-13's 1 m row)"), ("sum", 3.0, "RBT-13's W1 arm"),
        ("mean", 3.0, "W1' candidate"), ("log", 3.0, "W1' candidate")]
print("| smell | decay | signal at 0 / 2 / 3 / 4 m | slope per metre at 0 / 2 / 3 / 4 m | change over one eat radius (0.35 m) at 3 m | 0.5 m vs 2.5 m from an item |")
print("|---|---|---|---|---|---|")
for mode, decay, note in arms:
    s, g = table(mode, decay)
    print(f"| `{mode}` | {decay:g} m | " + " / ".join(f"{v:.2f}" for v in s) + " | "
          + " / ".join(f"{v:.3f}" for v in g) + f" | {g[2]*EAT:.3f} | {disc_span(mode, decay):.3f} |")
print()
for mode, decay, note in arms:
    print(f"{mode} decay {decay:g}: {note}")
