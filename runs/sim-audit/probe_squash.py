"""H4: does the squash-over-a-sum destroy the food gradient?

Pure analysis of _intensity() (rabbitstew/simulation.py ~line 484), reproduced standalone and
checked bit-for-bit against the library function.  Current config (runs/RBT-23/W4b-801):
items=12, radius=3.0, decay=1.0, smell="sum", regrow=False, eat_radius=0.35.

Sections
  A  exactness check of the standalone reproduction
  B  how big is S (the raw pile) in a real arena, and how much gradient does the squash eat
  C  differential across the 0.3872 m wheel track vs distance to nearest item, raw vs squashed
  D  mode x decay sweep (sum / mean / log, plus a hypothetical 'nearest'), diff-to-DC ratio
  E  "am I in the disc" test: variance of the field explained by radius-from-centre alone
  F  directional quality: does the gradient point at food, does the track differential sign steer right
"""
from __future__ import annotations

import json
import sys

import numpy as np

sys.path.insert(0, "/home/user/rabbitstew")

from rabbitstew.simulation import FoodConfig, SimConfig, Simulation

TRACK = 0.3872          # wheel-track / nose separation, measured on the season-590 best
DISC = 3.0              # food disc radius
ITEMS = 12
DECAY = 1.0
RNG = np.random.default_rng(20260913)

out: dict = {}


# ---------------------------------------------------------------- standalone reproduction ----
def intensity(points: np.ndarray, sources: np.ndarray, decay: float, mode: str, n_div: int | None = None) -> np.ndarray:
    """Vectorised copy of Simulation._intensity.  points (..., 2), sources (m, 2).

    n_div is the divisor the sim uses for 'mean'/'log': len(sources) INCLUDING parked items
    (the sim parks eaten food at 1e6 but still counts it), so it stays at the arena item count.
    """
    pts = np.atleast_2d(points)
    n = len(sources) if n_div is None else n_div
    if len(sources) == 0:
        return np.zeros(len(pts))
    d = np.linalg.norm(pts[:, None, :] - sources[None, :, :], axis=2)
    total = np.exp(-d / decay).sum(axis=1)
    if mode == "mean":
        i = total / n
        return i / (1.0 + i)
    if mode == "log":
        return np.clip(np.log1p(total) / np.log1p(n), 0.0, 1.0)
    if mode == "nearest":          # NOT in the sim: reference point, nearest source only
        return np.exp(-d.min(axis=1) / decay)
    if mode == "raw":              # NOT in the sim: the unsquashed pile
        return total
    return total / (1.0 + total)


def raw_sum(points: np.ndarray, sources: np.ndarray, decay: float) -> np.ndarray:
    pts = np.atleast_2d(points)
    d = np.linalg.norm(pts[:, None, :] - sources[None, :, :], axis=2)
    return np.exp(-d / decay).sum(axis=1)


def grad_raw(points: np.ndarray, sources: np.ndarray, decay: float) -> np.ndarray:
    """Analytic grad of the raw pile S = sum exp(-d/decay)."""
    pts = np.atleast_2d(points)
    v = pts[:, None, :] - sources[None, :, :]
    d = np.linalg.norm(v, axis=2)
    d = np.maximum(d, 1e-9)
    w = np.exp(-d / decay) / decay / d
    return -(w[:, :, None] * v).sum(axis=1)


def layouts(k: int, items: int) -> np.ndarray:
    """k food layouts of `items` points, uniform in the disc, exactly as _food_spot draws them."""
    r = DISC * np.sqrt(RNG.random((k, items)))
    a = RNG.uniform(0, 2 * np.pi, (k, items))
    return np.stack([r * np.cos(a), r * np.sin(a)], axis=-1)


def robot_points(k: int) -> np.ndarray:
    """Robot positions: uniform in a 3.5 m disc (the bout roams a little outside the food disc)."""
    r = 3.5 * np.sqrt(RNG.random(k))
    a = RNG.uniform(0, 2 * np.pi, k)
    return np.stack([r * np.cos(a), r * np.sin(a)], axis=-1)


# ================================================================== A: exactness ==============
class Shim:
    def __init__(self, cfg):
        self.config = cfg


err = 0.0
for mode in ("sum", "mean", "log"):
    for dec in (0.3, 1.0, 3.0):
        cfg = SimConfig(food=FoodConfig(items=ITEMS, radius=DISC, decay=dec, smell=mode))
        shim = Shim(cfg)
        src = layouts(1, ITEMS)[0]
        pts = robot_points(50)
        ref = np.array([Simulation._intensity(shim, np.array([p[0], p[1], 0.05]), src) for p in pts])
        mine = intensity(pts, src, dec, mode)
        err = max(err, float(np.abs(ref - mine).max()))
out["A_max_abs_error_vs_library"] = err
print(f"[A] standalone reproduction vs Simulation._intensity: max |err| = {err:.3e} over 450 samples, 3 modes x 3 decays")

# ============================================== B: how big is the pile, how much does squash eat
print("\n[B] the raw pile S and what the squash does to the gradient (decay=1.0, sum mode)")
print("    live   mean S   mean I=S/(1+S)   squash gradient factor 1/(1+S)^2   relative-contrast factor")
b_rows = []
NL, NP = 300, 300
for live in (12, 8, 6, 4, 2, 1):
    lays = layouts(NL, live)
    pts = robot_points(NL * NP).reshape(NL, NP, 2)
    S = np.concatenate([raw_sum(pts[i], lays[i], DECAY) for i in range(NL)])
    I = S / (1.0 + S)
    # d|I|/d|S| = 1/(1+S)^2 : how much absolute gradient survives the squash
    gfac = 1.0 / (1.0 + S) ** 2
    # relative contrast (dI/I) / (dS/S) = (1/(1+S)^2)/(1/(1+S)) = 1/(1+S)
    rfac = 1.0 / (1.0 + S)
    b_rows.append(dict(live=live, S=float(S.mean()), I=float(I.mean()),
                       grad_factor=float(gfac.mean()), rel_factor=float(rfac.mean()),
                       S_median=float(np.median(S))))
    print(f"    {live:4d}   {S.mean():6.3f}   {I.mean():9.3f}        {gfac.mean():9.3f}                     {rfac.mean():8.3f}")
out["B_pile_and_squash"] = b_rows
print("    (grad factor = fraction of the ABSOLUTE gradient that survives the squash;")
print("     rel factor  = fraction of the RELATIVE contrast dI/I vs dS/S that survives)")

# ======================================= C: wheel-track differential vs distance to nearest item
print("\n[C] differential across the 0.3872 m track, by distance to nearest live item (decay=1.0)")
NL, NP = 400, 250
lays12 = layouts(NL, ITEMS)
pts = robot_points(NL * NP).reshape(NL, NP, 2)
head = RNG.uniform(0, 2 * np.pi, (NL, NP))
perp = np.stack([-np.sin(head), np.cos(head)], axis=-1)          # left-right axis of the body
nL = pts + (TRACK / 2) * perp
nR = pts - (TRACK / 2) * perp

acc = {k: [] for k in ("d1", "Ic", "dI", "Sc", "dS", "bear_lat", "gang", "Nc", "dN")}
for i in range(NL):
    src = lays12[i]
    d = np.linalg.norm(pts[i][:, None, :] - src[None, :, :], axis=2)
    j = d.argmin(axis=1)
    acc["d1"].append(d.min(axis=1))
    SL, SR, SC = raw_sum(nL[i], src, DECAY), raw_sum(nR[i], src, DECAY), raw_sum(pts[i], src, DECAY)
    acc["Sc"].append(SC)
    acc["dS"].append(SL - SR)
    acc["Ic"].append(SC / (1 + SC))
    acc["dI"].append(SL / (1 + SL) - SR / (1 + SR))
    NL_ = intensity(nL[i], src, DECAY, "nearest")
    NR_ = intensity(nR[i], src, DECAY, "nearest")
    acc["Nc"].append(intensity(pts[i], src, DECAY, "nearest"))
    acc["dN"].append(NL_ - NR_)
    to = src[j] - pts[i]                                          # vector to the nearest item
    to /= np.linalg.norm(to, axis=1, keepdims=True)
    acc["bear_lat"].append((to * perp[i]).sum(axis=1))            # >0 -> nearest item is to the left
    g = grad_raw(pts[i], src, DECAY)
    g /= np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)
    acc["gang"].append(np.degrees(np.arccos(np.clip((g * to).sum(axis=1), -1, 1))))
A = {k: np.concatenate(v) for k, v in acc.items()}

print("    d1 bin      n     I (squashed)   |dI|/I      S (raw)   |dS|/S    nearest-mode |dN|/N")
c_rows = []
for lo, hi in ((0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 2.0), (2.0, 9.0)):
    m = (A["d1"] >= lo) & (A["d1"] < hi)
    if m.sum() < 50:
        continue
    ri = np.abs(A["dI"][m]) / A["Ic"][m]
    rs = np.abs(A["dS"][m]) / A["Sc"][m]
    rn = np.abs(A["dN"][m]) / A["Nc"][m]
    c_rows.append(dict(lo=lo, hi=hi, n=int(m.sum()), I=float(A["Ic"][m].mean()), rel_I=float(ri.mean()),
                       S=float(A["Sc"][m].mean()), rel_S=float(rs.mean()), rel_N=float(rn.mean()),
                       abs_dI=float(np.abs(A["dI"][m]).mean())))
    print(f"    {lo:.1f}-{hi:.1f}  {m.sum():7d}   {A['Ic'][m].mean():8.4f}   {ri.mean():7.4f}   {A['Sc'][m].mean():8.4f}  {rs.mean():7.4f}   {rn.mean():7.4f}")
allI = np.abs(A["dI"]) / A["Ic"]
print(f"    ALL      {len(allI):7d}   {A['Ic'].mean():8.4f}   {allI.mean():7.4f}   {A['Sc'].mean():8.4f}  "
      f"{(np.abs(A['dS']) / A['Sc']).mean():7.4f}   {(np.abs(A['dN']) / A['Nc']).mean():7.4f}")
print(f"    mean |dI| absolute = {np.abs(A['dI']).mean():.4f}, mean I = {A['Ic'].mean():.4f}  "
      f"(sim measured 0.0399 / 0.3283 on a real bout)")
out["C_by_nearest_distance"] = c_rows
out["C_all"] = dict(rel_I=float(allI.mean()), rel_S=float((np.abs(A["dS"]) / A["Sc"]).mean()),
                    rel_N=float((np.abs(A["dN"]) / A["Nc"]).mean()),
                    abs_dI=float(np.abs(A["dI"]).mean()), I=float(A["Ic"].mean()), S=float(A["Sc"].mean()))

# ================================================================ D: mode x decay sweep ========
print("\n[D] mode x decay: mean |differential| / DC across the track, and steering-sign accuracy")
print("    (sign accuracy = P(the higher nose is on the side of the nearest item) -- 0.5 is blind)")
print("    mode      decay   DC value   |dI|/DC    |dI| abs    sign-acc   sign-acc d1<1m   range: I at d1=2m")
d_rows = []
for mode in ("sum", "mean", "log", "nearest"):
    for dec in (0.25, 0.5, 1.0, 2.0, 3.0):
        vc = np.empty(0)
        vd = np.empty(0)
        sgn = np.empty(0)
        d1a = np.empty(0)
        for i in range(0, NL, 2):                      # half the layouts: plenty (50k samples)
            src = lays12[i]
            c = intensity(pts[i], src, dec, mode, n_div=ITEMS)
            l = intensity(nL[i], src, dec, mode, n_div=ITEMS)
            r = intensity(nR[i], src, dec, mode, n_div=ITEMS)
            d = np.linalg.norm(pts[i][:, None, :] - src[None, :, :], axis=2)
            j = d.argmin(axis=1)
            to = src[j] - pts[i]
            to /= np.linalg.norm(to, axis=1, keepdims=True)
            lat = (to * perp[i]).sum(axis=1)
            vc = np.r_[vc, c]
            vd = np.r_[vd, l - r]
            sgn = np.r_[sgn, np.sign(l - r) * np.sign(lat)]
            d1a = np.r_[d1a, d.min(axis=1)]
        rel = np.abs(vd) / np.maximum(vc, 1e-12)
        near = d1a < 1.0
        # detection range: mean field value when the nearest item is ~2 m away
        far = (d1a > 1.8) & (d1a < 2.2)
        d_rows.append(dict(mode=mode, decay=dec, DC=float(vc.mean()), rel=float(rel.mean()),
                           absd=float(np.abs(vd).mean()), sign=float((sgn > 0).mean()),
                           sign_near=float((sgn[near] > 0).mean()), I_at_2m=float(vc[far].mean())))
        tag = mode + ("*" if mode == "nearest" else " ")
        print(f"    {tag:9s} {dec:5.2f}   {vc.mean():8.4f}   {rel.mean():7.4f}   {np.abs(vd).mean():8.5f}    "
              f"{(sgn > 0).mean():6.3f}     {(sgn[near] > 0).mean():6.3f}         {vc[far].mean():8.4f}")
print("    * 'nearest' is NOT a mode the sim supports -- it is the reference ceiling")
out["D_mode_decay"] = d_rows

# ==================================================== E: is it just "am I in the disc"? ========
print("\n[E] is the squashed field just a radial 'am I in the disc' scalar? (sum, decay=1.0, 12 items)")
e_rows = []
for mode, dec in (("sum", 1.0), ("mean", 1.0), ("sum", 0.5), ("sum", 3.0)):
    vals, rads = [], []
    for i in range(0, NL, 2):
        vals.append(intensity(pts[i], lays12[i], dec, mode, n_div=ITEMS))
        rads.append(np.linalg.norm(pts[i], axis=1))
    v = np.concatenate(vals)
    r = np.concatenate(rads)
    # variance of v explained by radius alone (20 radial bins, layout-averaged profile)
    bins = np.clip((r / 3.5 * 20).astype(int), 0, 19)
    prof = np.array([v[bins == b].mean() if (bins == b).sum() else 0.0 for b in range(20)])
    resid = v - prof[bins]
    r2 = 1.0 - resid.var() / v.var()
    inside = r < 2.5
    e_rows.append(dict(mode=mode, decay=dec, r2_radial=float(r2), cv_inside=float(v[inside].std() / v[inside].mean()),
                       mean_in=float(v[inside].mean()), mean_out=float(v[r > 3.2].mean())))
    print(f"    {mode:5s} decay={dec:.1f}: R^2 of a pure radial profile = {r2:.3f} | "
          f"CV inside 2.5 m = {v[inside].std() / v[inside].mean():.3f} | mean in {v[inside].mean():.3f} vs out(>3.2m) {v[r > 3.2].mean():.3f}")
out["E_radial"] = e_rows

# ================================================== F: where does the gradient actually point ===
print("\n[F] direction quality of the raw-sum gradient (decay=1.0, 12 items): angle to the NEAREST item")
for lo, hi in ((0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 9.0)):
    m = (A["d1"] >= lo) & (A["d1"] < hi)
    g = A["gang"][m]
    print(f"    d1 {lo:.1f}-{hi:.1f}: median angle error {np.median(g):5.1f} deg | "
          f"within 45 deg {np.mean(g < 45):.3f} | within 90 deg {np.mean(g < 90):.3f}")
out["F_grad_angle"] = {f"{lo}-{hi}": dict(median=float(np.median(A["gang"][(A['d1'] >= lo) & (A['d1'] < hi)])),
                                          within45=float(np.mean(A["gang"][(A['d1'] >= lo) & (A['d1'] < hi)] < 45)))
                       for lo, hi in ((0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 9.0))}
sgn_all = np.sign(A["dI"]) * np.sign(A["bear_lat"])
print(f"    track-differential sign points at the nearest item: {np.mean(sgn_all > 0):.3f} overall, "
      f"{np.mean(sgn_all[A['d1'] < 1.0] > 0):.3f} when d1<1 m  (squash cannot change a sign)")
out["F_sign"] = dict(all=float(np.mean(sgn_all > 0)), near=float(np.mean(sgn_all[A["d1"] < 1.0] > 0)))

with open("/home/user/rabbitstew/runs/sim-audit/probe_squash.json", "w") as fh:
    json.dump(out, fh, indent=1)
print("\nwrote runs/sim-audit/probe_squash.json")

# ============================ G: match the real bout's operating point (regrow=False depletes) ==
print("\n[G] the real bout ran DEPLETED (regrow=False parks eaten items): diff/DC by live count")
print("    mode   decay  live   DC       |dI|/DC   sign-acc")
g_rows = []
for mode in ("sum", "mean", "log"):
    for live in (12, 6, 4, 2):
        la = layouts(120, live)
        pp = robot_points(120 * 250).reshape(120, 250, 2)
        hh = RNG.uniform(0, 2 * np.pi, (120, 250))
        pe = np.stack([-np.sin(hh), np.cos(hh)], axis=-1)
        vc, vd, sg = [], [], []
        for i in range(120):
            src = la[i]
            c = intensity(pp[i], src, DECAY, mode, n_div=ITEMS)
            l = intensity(pp[i] + (TRACK / 2) * pe[i], src, DECAY, mode, n_div=ITEMS)
            r = intensity(pp[i] - (TRACK / 2) * pe[i], src, DECAY, mode, n_div=ITEMS)
            d = np.linalg.norm(pp[i][:, None, :] - src[None, :, :], axis=2)
            to = src[d.argmin(axis=1)] - pp[i]
            to /= np.linalg.norm(to, axis=1, keepdims=True)
            vc.append(c); vd.append(l - r); sg.append(np.sign(l - r) * np.sign((to * pe[i]).sum(axis=1)))
        vc, vd, sg = np.concatenate(vc), np.concatenate(vd), np.concatenate(sg)
        rel = float((np.abs(vd) / np.maximum(vc, 1e-12)).mean())
        g_rows.append(dict(mode=mode, live=live, DC=float(vc.mean()), rel=rel, sign=float((sg > 0).mean())))
        print(f"    {mode:5s}  {DECAY:.2f}  {live:4d}   {vc.mean():7.4f}  {rel:7.4f}   {(sg > 0).mean():6.3f}")
out["G_depletion"] = g_rows
print("    real bout measured: DC 0.3283, |dI|/DC 0.1215 (0.0399/0.3283) -- compare the sum rows")

# ================== H: what the effector tanh can actually deliver from that differential ======
print("\n[H] post-tanh wheel asymmetry a crossed link can buy (effector out = tanh(w*I), range +-1)")
print("    sweep w; report the w that maximises mean |tanh(w*I_L) - tanh(w*I_R)| and the common drive there")
print("    mode      decay   best w   max wheel differential   common drive tanh(w*DC)")
h_rows = []
ws = np.concatenate([np.arange(0.1, 5.0, 0.1), np.arange(5.0, 40.0, 0.5)])
for mode, dec in (("sum", 1.0), ("mean", 1.0), ("log", 1.0), ("sum", 0.5), ("sum", 0.25), ("nearest", 1.0)):
    L, R, C = [], [], []
    for i in range(0, NL, 4):
        src = lays12[i]
        L.append(intensity(nL[i], src, dec, mode, n_div=ITEMS))
        R.append(intensity(nR[i], src, dec, mode, n_div=ITEMS))
        C.append(intensity(pts[i], src, dec, mode, n_div=ITEMS))
    L, R, C = np.concatenate(L), np.concatenate(R), np.concatenate(C)
    best = max(((float(np.abs(np.tanh(w * L) - np.tanh(w * R)).mean()), float(w)) for w in ws))
    md, bw = best
    h_rows.append(dict(mode=mode, decay=dec, best_w=bw, max_diff=md, common=float(np.tanh(bw * C).mean())))
    print(f"    {mode:9s} {dec:5.2f}   {bw:6.2f}   {md:20.4f}   {np.tanh(bw * C).mean():10.4f}")
out["H_tanh_ceiling"] = h_rows
print("    (a full-speed wheel command is 1.0, so 'max wheel differential' is the steering authority")
print("     the compass can ever have, and 'common drive' is the forward push it forces alongside it)")

with open("/home/user/rabbitstew/runs/sim-audit/probe_squash.json", "w") as fh:
    json.dump(out, fh, indent=1)
print("\nrewrote runs/sim-audit/probe_squash.json")

# ======== I: the spike's own magnitude grid, at the real (depleted) operating point live=4 ======
print("\n[I] what the spike's magnitudes actually did, at the real operating point (sum, decay=1.0,")
print("    live=4 -> DC 0.286, matching the bout's measured 0.328). Wheel command = tanh(w*I).")
la = layouts(200, 4)
pp = robot_points(200 * 250).reshape(200, 250, 2)
hh = RNG.uniform(0, 2 * np.pi, (200, 250))
pe = np.stack([-np.sin(hh), np.cos(hh)], axis=-1)
Lv, Rv = [], []
for i in range(200):
    Lv.append(intensity(pp[i] + (TRACK / 2) * pe[i], la[i], DECAY, "sum"))
    Rv.append(intensity(pp[i] - (TRACK / 2) * pe[i], la[i], DECAY, "sum"))
Lv, Rv = np.concatenate(Lv), np.concatenate(Rv)
print("      w    common drive   crossed-vs-uncrossed wheel-command gap   steering asymmetry")
i_rows = []
for w in (0.5, 1.0, 2.0, 4.0, 8.0):
    com = float(0.5 * (np.tanh(w * Lv) + np.tanh(w * Rv)).mean())
    gap = float(np.abs(np.tanh(w * Lv) - np.tanh(w * Rv)).mean())   # crossed and uncrossed differ by exactly this, doubled
    i_rows.append(dict(w=w, common=com, gap=gap))
    print(f"    {w:5.1f}      {com:8.4f}                 {2 * gap:8.4f}                    {gap / max(com, 1e-9):7.3f}")
out["I_spike_grid"] = i_rows
print("    (the spike found crossed and uncrossed behaviourally identical; the wheel-command gap")
print("     between those two wirings is the middle column, out of a +-1 full-scale command)")

with open("/home/user/rabbitstew/runs/sim-audit/probe_squash.json", "w") as fh:
    json.dump(out, fh, indent=1)

# ======== J: can a co-adapted BIAS rescue it? wheel command = tanh(w*I + b), sweep (w, b) ======
print("\n[J] wheel units carry a bias (brain.py: self.bias[i] = u.bias). Best (w, b) for steering:")
print("    mode    decay  best w   best b   max wheel differential   common drive at that (w,b)")
j_rows = []
for mode, dec, LL, RR in (("sum", 1.0, None, None), ("mean", 1.0, None, None), ("sum", 0.5, None, None)):
    L, R = [], []
    for i in range(0, NL, 4):
        L.append(intensity(nL[i], lays12[i], dec, mode, n_div=ITEMS))
        R.append(intensity(nR[i], lays12[i], dec, mode, n_div=ITEMS))
    L, R = np.concatenate(L), np.concatenate(R)
    best = (0.0, 0.0, 0.0)
    for w in np.arange(0.5, 60.0, 0.5):
        bs = -w * np.quantile(0.5 * (L + R), np.arange(0.1, 0.95, 0.05))
        for b in bs:
            v = float(np.abs(np.tanh(w * L + b) - np.tanh(w * R + b)).mean())
            if v > best[0]:
                best = (v, float(w), float(b))
    v, w, b = best
    com = float(0.5 * (np.tanh(w * L + b) + np.tanh(w * R + b)).mean())
    j_rows.append(dict(mode=mode, decay=dec, w=w, b=b, max_diff=v, common=com))
    print(f"    {mode:6s} {dec:5.2f}  {w:6.1f}   {b:6.2f}   {v:20.4f}   {com:12.4f}")
out["J_bias_rescue"] = j_rows
print("    compare section H (b forced to 0): sum/1.0 ceiling was 0.0318")

with open("/home/user/rabbitstew/runs/sim-audit/probe_squash.json", "w") as fh:
    json.dump(out, fh, indent=1)
