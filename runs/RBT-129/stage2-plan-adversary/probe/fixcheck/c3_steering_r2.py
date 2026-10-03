"""Fix-check: the C3 steering analysis re-run under the r2 pins (stage2_readout.py at 3a8587e), on the public
# Run from a checkout of the plan at 3a8587e (it imports runs/RBT-129/stage2-plan/stage2_readout.py there).
Stage-1 record only (stage1_readout.txt's per-point table)."""
import re, sys
sys.path.insert(0, "runs/RBT-129/stage2-plan")
import stage2_readout as s2
sr = s2.sr
pts = {}
for l in open("runs/RBT-129/stage1-readout/stage1_readout.txt"):
    m = re.match(r"  (c\d+-p\d+-\w+-[GL])\s+(.+?)\s{2,}share [^|]*\|[^|]*\| (\S+) [^|]*\| M (\S+)[^|]*? N (\d+) \|", l)
    if m:
        pid, body, inc, marm, n = m.groups()
        pts[pid] = {"body": body.strip(), "income": inc, "m_arm": marm != "--", "n_ran": int(n) > 0,
                    "lever": False, "vd": False, "resolving": False}
assert len(pts) == 36, len(pts)
no = lambda p: False
print("## C3-2 (v5_mark: registered headline, literal headline, mark); T1 'rejects' (frozen), no M3 corroboration")
for label, mod in [("as printed", {}), ("c1-p080-HP-L drops", {"c1-p080-HP-L": "UNDECIDED"}),
                   ("c1-p010-PW-L drops", {"c1-p010-PW-L": "UNDECIDED"}),
                   ("both EARNS-H drop", {"c1-p080-HP-L": "UNDECIDED", "c1-p010-PW-L": "UNDECIDED"}),
                   ("1 EARNS-H left + 1 EARNS-TIE", {"c1-p080-HP-L": "UNDECIDED", "c1-p010-U-L": "EARNS-TIE"})]:
    P = {k: dict(v) for k, v in pts.items()}
    for k, v in mod.items():
        P[k]["income"] = v
    print(f"  {label:30s}", s2.v5_mark(P, "rejects", no))
sc = s2.scorecard_item2(pts)
print("## C3-3 (registered = pre-data code)"); [print("  " + sc[k]) for k in ("registered", "gated", "n_points")]
print("## C3-4 registered (all M):", s2.share_model_points(pts))
print("   non-registered (habitable):", s2.share_model_points(pts, scope="habitable"))
print("## C3-5 window:", s2.PER_BIRTH_WINDOW)
