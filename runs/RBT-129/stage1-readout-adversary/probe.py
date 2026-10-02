import importlib.util, os, sys, math, inspect
R = sys.argv[1]
spec = importlib.util.spec_from_file_location("sr", f"{R}/runs/RBT-129/stage1-readout/stage1_readout.py")
sr = importlib.util.module_from_spec(spec); spec.loader.exec_module(sr)
sys.path.insert(0, f"{R}/runs/RBT-129"); import power
print("power.resolvable signature:", inspect.signature(power.resolvable))
# a stub with power.resolvable's real return shape: (rows, passes)
stub = lambda lo, hi, rule, n, reps=1500: ([(0.9, 0.1, 0.0, 0.0, False), (0.9, 0.1, 0.0, 0.0, False)], False)
print("P1 resolving() with a stub that FAILS at both bounds (real return shape):", sr.resolving(True, True, [0.9, 1.1, 1.0], 8, stub))
# C1 candidates
c = sr.c1_candidates(f"{R}/runs/RBT-129/stageP0-readout/stageP0_readout.txt")
stage1 = set(sr.STAGE1_POINTS)
mids = {m for _, _, m, _ in sr.ra_pairs()}
print("P2 C1 candidates", len(c), c)
print("   not an R-A midpoint of any Stage-1 pair:", [x for x in c if x not in mids])
# K2 per point at one run: the size bar is evaluable
print("P3 k2_per_point single run y'=0.40:", sr.k2_per_point({"a": [0.40]}))
# pooled null df summed over kinds vs per kind
runs = {("p%d" % i, k): [0.1, -0.1, 0.05, 0.0] for i in range(4) for k in ("holistic",)}
runs.update({("p%d" % i, "conventional"): [0.1, -0.1] for i in range(1)})
print("P4 pooled_null df (holistic 4 points x 4 runs, designed 1 point x 2):", sr.pooled_null(runs)[1], "-> callable", sr.contingent_callable(sr.pooled_null(runs)[1]), "(per-kind df 12 and 1)")
# body_call when n == 0 (all seeds K-SALT VOID) / tie
print("P5 thresholds(0)", sr.thresholds(0))
# verdict 5 with EARNS-TIE everywhere but one EARNS-H
pts = {f"x{i}": {"body": "NOT RUN", "income": "EARNS-TIE", "lever": None, "vd": False, "m_arm": False} for i in range(20)}
pts["h"] = {"body": "NOT RUN", "income": "EARNS-H", "lever": None, "vd": False, "m_arm": False}
pts["s1"] = {"body": "EXCLUDED-H", "income": "UNDECIDED", "lever": None, "vd": False, "m_arm": False}
pts["s2"] = {"body": "PARTIAL-D", "income": "UNDECIDED", "lever": None, "vd": False, "m_arm": False}
print("P6 verdicts (20 EARNS-TIE, 1 EARNS-H, 2 survival-D, T1 not rejected):", sr.verdicts(pts, False, lambda p: False))
# EARNS at an uninhabitable point excluded from counting sets
pts2 = {"a": {"body": "NOT RUN", "income": "EARNS-H"}, "b": {"body": "NOT RUN", "income": "EARNS-H"},
        "c": {"body": "PARTIAL-D", "income": "EARNS-D"}, "d": {"body": "EXCLUDED-H", "income": "EARNS-D"}}
for v in pts2.values(): v.update(lever=None, vd=False, m_arm=False)
print("P7 verdicts (2 EARNS-H habitable; 2 EARNS-D at PARTIAL-D / EXCLUDED-H; T1 rejects):", sr.verdicts(pts2, True, lambda p: False))
# assemble with a crashed M seed that also has N: the N read is skipped
src = inspect.getsource(sr.assemble_point)
print("P8 crashed-M `continue` precedes the N read:", src.index("continue  # CRASHED") < src.index("if j in n_seeds"))
# rb_select: anchors eligible
st = {"c1-p030-U-L": {"body": "RBT-118 (not available)", "income": {"t": 1.0, "n": 8, "call": "UNDECIDED"}}}
print("P9 anchor eligible for R-B:", sr.rb_select(st))
# quarantine through a symlink
import tempfile
d = tempfile.mkdtemp(); q = os.path.join(d, sr.QUARANTINED_DIR); os.makedirs(q); os.symlink(q, os.path.join(d, "alias"))
try:
    sr.refuse_quarantined(path=os.path.join(d, "alias"), root=d); print("P10 symlink alias to the quarantined dir: NOT refused")
except sr.QuarantineRefusal:
    print("P10 symlink alias refused")
for lab in ("remotes/origin/ckpt/" + sr.QUARANTINED_LABEL, " ckpt/" + sr.QUARANTINED_LABEL + " ", "ckpt/" + sr.QUARANTINED_LABEL + ".tar", sr.QUARANTINED_LABEL.replace("-M", "-m")):
    try:
        sr.refuse_quarantined(label=lab); print("P11 label NOT refused:", repr(lab))
    except sr.QuarantineRefusal:
        print("P11 refused:", repr(lab))
# t-dist accuracy vs known values
print("P12 t_ppf(0.975, 1)", sr.t_ppf(0.975, 1), "(12.7062)", "t_sf(2.0,7)", sr.t_sf(2.0, 7), "(0.04281)")
