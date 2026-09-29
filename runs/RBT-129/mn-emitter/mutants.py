"""L1's mutants: each edits ``runs/RBT-129/launch/stages.py`` in place, runs ``tests/test_rbt129_mn.py``, and restores
the file.  A mutant is KILLED when the tests fail.

    python3 runs/RBT-129/mn-emitter/mutants.py > runs/RBT-129/mn-emitter/mutants.txt
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PATH = os.path.join(ROOT, "runs", "RBT-129", "launch", "stages.py")

MUTANTS = [
    # the five the brief names
    ("g0 from the wrong seeds (129001 only)", "G0_SEEDS = CENSUS_SEEDS", "G0_SEEDS = (1,)"),
    ("g0 from the wrong seeds (129001-129004)", "G0_SEEDS = CENSUS_SEEDS", "G0_SEEDS = (1, 2, 3, 4)"),
    ("g0 from the wrong faunas (designed only)", "G0_FAUNAS = FAUNAS", "G0_FAUNAS = (D,)"),
    ("g0 from the wrong faunas (holistic only)", "G0_FAUNAS = FAUNAS", "G0_FAUNAS = (H,)"),
    ("the slot-freeing rule dropped (a point with no valid seed keeps its slot)",
     '''                r["why"] = "M on no seed: slot freed (T5, DATA-INFORMED)"''',
     '''                r["why"] = "M on no seed"; m_used += 1; n_used += 1 if r["n_ok"] else 0'''),
    ("salts not carried to M/N (the job's salts)", '"salts": list(salts[j]),', '"salts": [0, 0],'),
    ("salts not carried to M/N (the lane check dropped)",
     '''        if j["job"] == "fork" and tuple(j.get("salts", ())) != salts.get(j["seed"]):''',
     '''        if False:'''),
    ("salts not carried to M/N (the fork's source check dropped)",
     '''            if "salts" in job and source_salts(job["src"]) != tuple(job["salts"]):''',
     '''            if False:'''),
    ("M/N emitted where stage1-emit's gate would refuse (screen gate skipped)",
     "    salts = screen_gate(root)\n    path = os.path.join(root, \"lanes\", \"1\", \"launch.txt\")",
     "    salts = {j: (0, 0) for j in SCREEN_SEEDS}\n    path = os.path.join(root, \"lanes\", \"1\", \"launch.txt\")"),
    ("M/N emitted with Stage 1's launch record at other salts",
     '''    if launch.get("salts") != pairs:''', '''    if False:'''),
    ("the census resume used at a salt other than 0 (ckpt60's salts not checked)",
     "    want = blocks.config_dict(argv + salts_argv(*salts), seed=seed(j), seasons=MERGE)",
     "    want = blocks.config_dict(argv, seed=seed(j), seasons=MERGE)"),
    ("the census resume used at a salt other than 0 (M/N forked from the census S)",
     '''            base = {"job": "fork", "src": f"{d}/ckpt60",''',
     '''            base = {"job": "fork", "src": os.path.join(root, "stage0", r["point"], str(seed(j)), "S") if j == RESUME_SEED else f"{d}/ckpt60",'''),
    # the rest of the gate
    ("M threshold 1.0 -> 1.1", "GATE_M_G0, GATE_N_G0 = 1.0, 0.8", "GATE_M_G0, GATE_N_G0 = 1.1, 0.8"),
    ("N threshold 0.8 -> 1.0", "GATE_M_G0, GATE_N_G0 = 1.0, 0.8", "GATE_M_G0, GATE_N_G0 = 1.0, 1.0"),
    ("M slots 12 -> 13", "GATE_M_SLOTS, GATE_N_SLOTS = 12, 4", "GATE_M_SLOTS, GATE_N_SLOTS = 13, 4"),
    ("N slots 4 -> 5", "GATE_M_SLOTS, GATE_N_SLOTS = 12, 4", "GATE_M_SLOTS, GATE_N_SLOTS = 12, 5"),
    ("offset 0.35 -> 0", "G0_OFFSET = 0.35", "G0_OFFSET = 0.0"),
    ("window 30-59 -> 29-59", "G0_WINDOW = (30, 59)", "G0_WINDOW = (29, 59)"),
    ("cull rows kept", 'if r.get("death") in ("cull", "merge-null") or', 'if r.get("death") in ("merge-null",) or'),
    ("the anchors admitted", '        m = not anchor and not ff and g0', '        m = not ff and g0'),
    ("the designed FOUNDING-FAIL dropped", '        m = not anchor and not ff and g0', '        m = not anchor and g0'),
    ("N not limited to g0 <= 0.8", '"n_ok": m and g0 <= GATE_N_G0', '"n_ok": m'),
    ("the seed rule: one fauna alive is enough", "    return all(any(e[\"population\"] == k", "    return any(any(e[\"population\"] == k"),
    ("the seed rule dropped (M on every seed)", '''            r["seeds"] = [j for j in range(1, n + 1) if valid[r["point"]][j]]''',
     '''            r["seeds"] = list(range(1, n + 1))'''),
    ("N on seeds M does not run", '''                    r["n"], n_used = list(r["seeds"]), n_used + 1''',
     '''                    r["n"], n_used = list(range(1, n + 1)), n_used + 1'''),
    ("ranked highest g0 first", '''    return sorted(rows, key=lambda r: (r["g0"] is None,''', '''    return sorted(rows, reverse=True, key=lambda r: (r["g0"] is None,'''),
    ("the readout cross-check dropped", '''            if g == "missing" or (g is None) != (r["g0"] is None) or (g is not None and round(r["g0"], 3) != g):''',
     '''            if False:'''),
    ("K-SALT VOID forked", '''or not open(ks).read().startswith("KSALT PASS")):''', '''and False):'''),
    ("the gate does not wait for every S60", '''    if waiting:\n        _refuse(''', '''    if False:\n        _refuse('''),
    ("null kind swapped", '''"merge_null": null_kind(j)}})''', '''"merge_null": null_kind(j + 1)}})'''),
    # the #500 ruling's fixes
    ("K-SALT not required at 129001 (s >= 1, t = 0)", "    if j in CENSUS_SEEDS and salts[0] >= 1 and salts[1] == 0 and",
     "    if j in CENSUS_SEEDS and j != 1 and salts[0] >= 1 and salts[1] == 0 and"),
    ("K-SALT required where t >= 1", "and salts[0] >= 1 and salts[1] == 0 and (not os.path.exists(ks)",
     "and salts[0] >= 1 and (not os.path.exists(ks)"),
    ("the extinct short-circuit before K-SALT", "    extinct = extinct_season(unit) is not None\n    if not extinct:",
     "    extinct = extinct_season(unit) is not None\n    if extinct:\n        return False\n    if not extinct:"),
    ("run-lane does not hold forks to the admitted list", "    check_lane_forks(jobs, launch)\n    os.makedirs", "    os.makedirs"),
    ("a fork off the admitted list passes", " or name not in admitted or", " or"),
    ("a fork's arm settings not checked", ' or j.get("set") != want', ""),
    ("a fork from outside Stage 1's ckpt60 passes",
     ' or not j["src"].endswith(os.path.join("stage1", parts[1], parts[2], "ckpt60"))', ""),
    ("the g0 fauna filter dropped", ' or r["population"] not in G0_FAUNAS:', ":"),
    ("the forks line not written", ',\n                            "forks": " ".join(mn_fork_names(gate))})', "})"),
    ("an extinct unit counted valid", '''        return False  # both faunas extinct before the merge: not valid''', '''        return True'''),
]


def _no_bytecode() -> None:
    cache = os.path.join(os.path.dirname(PATH), "__pycache__")
    for name in os.listdir(cache) if os.path.isdir(cache) else ():
        if name.startswith("stages."):
            os.remove(os.path.join(cache, name))


def run(venv_python: str) -> int:
    base = open(PATH).read()
    killed = 0
    print(f"# L1 mutants: {len(MUTANTS)} edits of runs/RBT-129/launch/stages.py against tests/test_rbt129_mn.py")
    try:
        for name, old, new in MUTANTS:
            if base.count(old) != 1:
                print(f"  NOT APPLIED ({base.count(old)} matches)  {name}")
                continue
            open(PATH, "w").write(base.replace(old, new))
            _no_bytecode()  # a same-size edit within a second would otherwise load the previous mutant's .pyc
            r = subprocess.run([venv_python, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", "tests/test_rbt129_mn.py"],
                               cwd=ROOT, capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            word = "KILLED  " if r.returncode else "SURVIVED"
            killed += bool(r.returncode)
            first = next((l for l in r.stdout.splitlines() if l.startswith("FAILED")), "").split(" - ")[0]
            print(f"  {word}  {name}" + (f"   ({first.replace('FAILED tests/test_rbt129_mn.py::', 'by ')})" if first else ""))
    finally:
        open(PATH, "w").write(base)
        _no_bytecode()
    print(f"# {killed} of {len(MUTANTS)} killed")
    return 0 if killed == len(MUTANTS) else 1


if __name__ == "__main__":
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else sys.executable))
