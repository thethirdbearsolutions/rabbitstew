import re, sys, importlib.util
sys.path.insert(0, "runs/RBT-129/stage2-plan")
import stage2_readout as s2
sr = s2.sr
pts = {}
for l in open("runs/RBT-129/stage1-readout/stage1_readout.txt"):
    m = re.match(r"  (c\d+-p\d+-\w+-[GL])\s+(.+?)\s{2,}share [^|]*\|[^|]*\| (\S+) [^|]*\| M (\S+)", l)
    if m and "|" in l and "x̄" in l:
        pid, body, inc, marm = m.groups()
        pts[pid] = {"body": body.strip(), "income": inc, "m_arm": marm != "--", "lever": False, "vd": False, "resolving": False}
assert len(pts) == 36, len(pts)
no = lambda p: False
def run(label, mod):
    P = {k: dict(v) for k, v in pts.items()}
    for k, v in mod.items(): P[k]["income"] = v
    reg = sr.verdicts(P, "rejects", no)
    lit = sr.verdicts(P, "rejects", no) if False else None
    v5lit = s2.verdict5_literal(P, no)
    hab = sr.verdicts(P, "rejects", no, earns_habitable_only=True)
    print(f"{label:58s} registered: {reg} | literal-v5 line: {v5lit or '(fails)'} | hab-only: {hab}")
run("Stage 1 as printed (EARNS-H at PW-L, HP-L)", {})
run("c1-p080-HP-L drops to UNDECIDED (1 EARNS-H left)", {"c1-p080-HP-L": "UNDECIDED"})
run("c1-p010-PW-L drops (1 EARNS-H left)", {"c1-p010-PW-L": "UNDECIDED"})
run("both EARNS-H drop", {"c1-p080-HP-L": "UNDECIDED", "c1-p010-PW-L": "UNDECIDED"})
run("1 EARNS-H left + one EARNS-TIE appears", {"c1-p080-HP-L": "UNDECIDED", "c1-p010-U-L": "EARNS-TIE"})
