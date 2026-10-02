"""Fix-check probes on #512 at eaab9c8: single functions of the plan's script on synthetic values, plus registered inputs
(gate table, census readout).  Run: python3 probe2.py <worktree at eaab9c8>.  Reads no Stage-1 output."""
import importlib.util, os, sys, math, json, tempfile, io, contextlib
R = sys.argv[1]
spec = importlib.util.spec_from_file_location("sr", f"{R}/runs/RBT-129/stage1-readout/stage1_readout.py")
sr = importlib.util.module_from_spec(spec); spec.loader.exec_module(sr)
H, D = sr.H, sr.D
# MUST 1
stub = lambda lo, hi, rule, n, reps=1500: ([(0.9, 0.1, 0.0, 0.0, False)] * 2, False)
print("Q1 resolving() with power.resolvable's shape, failing at both bounds:", sr.resolving(True, True, [0.9, 1.1, 1.0], 8, stub)[0])
with contextlib.redirect_stdout(io.StringIO()):
    res, scale = sr.scaled_resolvable()
print("Q2 scaled_resolvable y_scale:", scale)
# SHOULD 1, 2
runs = {("p%d" % i, H): [0.1, -0.1, 0.05, 0.0] for i in range(4)}; runs[("p0", D)] = [0.1, -0.1]
print("Q3 pooled_null per kind:", {k: v[1] for k, v in sr.pooled_null(runs).items()}, "kind used:", sr.CONTINGENT_KIND)
print("Q4 k2_per_point single run 0.40 / 0.10:", sr.k2_per_point({"a": [0.40], "b": [0.10]}))
# MUST 4 (R1, R2)
def P(b, i): return {"body": b, "income": i, "lever": None, "vd": False, "m_arm": False, "resolving": False}
p6 = {f"x{i}": P("NOT RUN", "EARNS-TIE") for i in range(20)}; p6["h"] = P("NOT RUN", "EARNS-H")
p6["s1"] = P("EXCLUDED-H", "UNDECIDED"); p6["s2"] = P("PARTIAL-D", "UNDECIDED")
print("Q5 (old P6) registered:", sr.verdicts(p6, "does not reject", lambda p: False), "| non-registered v5:", sr.verdicts(p6, "does not reject", lambda p: False, v5_ignores_tie=True))
p7 = {"a": P("NOT RUN", "EARNS-H"), "b": P("NOT RUN", "EARNS-H"), "c": P("PARTIAL-D", "EARNS-D"), "d": P("EXCLUDED-H", "EARNS-D")}
print("Q6 (old P7) registered:", sr.verdicts(p7, "rejects", lambda p: False), "| habitable-only:", sr.verdicts(p7, "rejects", lambda p: False, earns_habitable_only=True))
p8 = {"a": P("NOT RUN", "UNDECIDED"), "b": P("NOT RUN", "EARNS-TIE")}
print("Q7 T1 NOT TESTABLE, nothing reached:", sr.verdicts(p8, "NOT TESTABLE", lambda p: False))
p9 = {f"h{i}": P("NOT RUN", "EARNS-H") for i in range(4)}; p9.update({f"o{i}": P("NOT RUN", "UNDECIDED") for i in range(4)})
print("Q8 T1 NOT TESTABLE, verdict 3 reachable:", sr.verdicts(p9, "NOT TESTABLE", lambda p: False))
# MUST 3 (R3)
import numpy as np
rng = np.random.default_rng(1)
pts_noPW = [f"c{c}-p{p}-{L}-G" for c in "012" for p in ("010", "030", "080") for L in ("U", "HP")]
m = sr.world_model([(p, float(rng.normal())) for p in pts_noPW for _ in range(5)])
print("Q9 no PW, no L-smell habitable:", m["status"], "dropped", m["dropped"], "P", m.get("P"), "T1 df", m["T1"][1] if m["T1"] else None)
diag = ["c0-p010-U-G", "c1-p030-U-G", "c2-p080-U-G", "c0-p010-HP-G", "c1-p030-HP-G", "c2-p080-HP-G"]
m = sr.world_model([(p, float(rng.normal())) for p in diag for _ in range(5)])
print("Q10 c and log p collinear (diagonal habitable points):", m["status"], "|", m.get("why"))
inter = ["c0-p010-U-G", "c0-p030-U-G", "c1-p010-U-G", "c1-p030-HP-G", "c2-p080-HP-G", "c2-p010-U-G", "c1-p080-U-G"]
m = sr.world_model([(p, float(rng.normal())) for p in inter for _ in range(5)])
print("Q11 a 7-point design:", m["status"], "dropped", m["dropped"], "P", m.get("P"), "|", m.get("why"))
m = sr.world_model([])
print("Q12 no habitable seed:", m["status"], m.get("why"), "| holm ps:", sr.map_holm(m)[1], "| t1:", sr.t1_state(m, set()))
# NOTE 7: go ids
print("Q13 go_ids at head:", sr.go_ids())
with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
    f.write("GO-ID:\nGO-ID: R-77\n")
print("Q14 go_ids with an empty GO-ID line:", sr.go_ids(f.name), "-> '--go \" \"' strip ''; in set:", "" in sr.go_ids(f.name))
# O-23
c = sr.c1_candidates(f"{R}/runs/RBT-129/stageP0-readout/stageP0_readout.txt")
mids = {m for _, _, m, _ in sr.ra_pairs()}
print("Q15 C1 candidates", len(c), "; with a Stage-1 flanking pair:", [x for x in c if x in mids], "; without:", len([x for x in c if x not in mids]))
# stage-2 combination sanity
x1 = list(rng.normal(0.0, 0.05, 8)); x2 = list(rng.normal(0.0, 0.05, 8))
print("Q16 stage2 call at a true 0, SD 0.05:", sr.stage2_income_call(x1, x2, lambda p: p < 0.05, lambda p: p < 0.05))
x1 = list(rng.normal(0.5, 0.1, 8)); x2 = list(rng.normal(0.5, 0.1, 8))
print("Q17 stage2 call at +0.5:", sr.stage2_income_call(x1, x2, lambda p: p < 0.05, lambda p: p < 0.05))
# quarantine forms
for lab in ("remotes/origin/ckpt/" + sr.QUARANTINED_LABEL, "ckpt/" + sr.QUARANTINED_LABEL + ".tar",
            "FETCH_HEAD " + sr.QUARANTINED_LABEL, "x-" + sr.QUARANTINED_LABEL, sr.QUARANTINED_LABEL + "0"):
    try:
        sr.refuse_quarantined(label=lab); print("Q18 NOT refused:", repr(lab))
    except sr.QuarantineRefusal:
        print("Q18 refused:", repr(lab))
d = tempfile.mkdtemp(); q = os.path.join(d, sr.QUARANTINED_DIR); os.makedirs(q); os.symlink(q, os.path.join(d, "alias"))
try:
    sr.refuse_quarantined(path=os.path.join(d, "alias"), root=d); print("Q19 symlink alias NOT refused")
except sr.QuarantineRefusal:
    print("Q19 symlink alias refused")
# provenance shape: extra key / relative-path form
prov_ok = {"runs/RBT-129/stage1/c0-p010-U-G/129001/S": "PASS"}
print("Q20 provenance read: integrity uses key = repo-relative run dir; values compared verbatim to 'PASS'/'FAIL'")
