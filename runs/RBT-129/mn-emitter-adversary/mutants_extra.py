"""L1 adversary: mutants of PR #500's gate that its mutants.py does not try.  Each edits the PR head's
``runs/RBT-129/launch/stages.py`` in place, runs the PR's ``tests/test_rbt129_mn.py`` (and, second, that file plus
this directory's ``test_adversary.py``), and restores the file.

    PR500=/tmp/pr500 python3 mutants_extra.py <venv python> > mutants_extra.txt
"""
import os
import subprocess
import sys

PR = os.environ["PR500"]
PY = sys.argv[1] if len(sys.argv) > 1 else sys.executable
PATH = os.path.join(PR, "runs", "RBT-129", "launch", "stages.py")
HERE = os.path.dirname(os.path.abspath(__file__))

MUTANTS = [
    ("K-SALT not required at 129001 when s >= 1, t = 0 (F7 covers it; stage1_units runs it)",
     "if j in CENSUS_SEEDS and salts[0] >= 1 and salts[1] == 0 and", "if j in (2, 3) and salts[0] >= 1 and salts[1] == 0 and"),
    ("K-SALT required also where t >= 1 (no K-SALT runs there: mn-emit never emits)",
     "if j in CENSUS_SEEDS and salts[0] >= 1 and salts[1] == 0 and", "if j in CENSUS_SEEDS and salts[0] >= 1 and"),
    ("an extinct unit not short-circuited (it then waits on a ckpt60 that is never taken)",
     "    if extinct_season(unit) is not None:\n        return False  # both faunas extinct before the merge: not valid",
     "    if extinct_season(unit) is not None and False:\n        return False"),
    ("valid at the merge read before refill (alive - births), F2's count",
     'e["season"] == SCREEN_SEASON and e["alive"] > 0 for e in hist', 'e["season"] == SCREEN_SEASON and e["alive"] - e["births"] > 0 for e in hist'),
    ("--fair/--eat against Stage 1's launch record not compared",
     '        if (a.fair, a.eat) != (launch["fair"], launch["eat"]):', '        if False:'),
    ("g0 fauna filter dropped (every population pooled)",
     'if r.get("death") in ("cull", "merge-null") or r["population"] not in G0_FAUNAS:', 'if r.get("death") in ("cull", "merge-null"):'),
    ("N slots not freed (a point with no valid seed holds its N slot; M's is still freed): OQ1's other reading",
     '''            elif not r["seeds"]:
                r["why"] = "M on no seed: slot freed (T5, DATA-INFORMED)"''',
     '''            elif not r["seeds"]:
                r["why"] = "M on no seed: slot freed (T5, DATA-INFORMED)"; n_used += 1 if r["n_ok"] else 0'''),
    ("the M slot counted before the seed rule (a point with no valid seed uses a slot)",
     '''            elif not r["seeds"]:
                r["why"] = "M on no seed: slot freed (T5, DATA-INFORMED)"''',
     '''            elif not r["seeds"]:
                r["why"] = "M on no seed: slot freed (T5, DATA-INFORMED)"; m_used += 1'''),
]


def run(tests):
    p = subprocess.run([PY, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", *tests], cwd=PR, capture_output=True,
                       text=True, env={**os.environ, "PR500": PR})
    return p.returncode


def main():
    orig = open(PATH).read()
    own = ["tests/test_rbt129_mn.py"]
    both = own + [os.path.join(HERE, "test_adversary.py")]
    print("# extra mutants of stages.py at PR #500's head: PR tests / PR tests + test_adversary.py")
    try:
        for name, a, b in MUTANTS:
            assert orig.count(a) == 1, name
            open(PATH, "w").write(orig.replace(a, b))
            r1, r2 = run(own), run(both)
            print(f"  {'KILLED  ' if r1 else 'SURVIVED'}  {'KILLED  ' if r2 else 'SURVIVED'}  {name}")
    finally:
        open(PATH, "w").write(orig)


main()
