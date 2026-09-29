"""Adversary mutation run for RBT-129c (#495): mutants the implementer did not try.

Each mutant is one exact text replacement in a scratch checkout of the PR head.  It is run against the PR's own tests
(tests/test_rbt129c.py, tests/test_rng_streams.py, tests/test_salt0_golden.py; ``-x``), and, when it survives them,
against this directory's test_founding_screen_adversary.py.  The checkout is restored after each mutant.

    python3 mutants.py /path/to/scratch/checkout/of/71c7d38 > mutants.txt
"""
import os
import subprocess
import sys

S, E = "runs/RBT-129/launch/stages.py", "rabbitstew/evolution.py"
MUTANTS = [
    ("cap 19 redraws (salts 0-19)", S, "SCREEN_SALTS = tuple(range(0, 21))", "SCREEN_SALTS = tuple(range(0, 20))"),
    ("criterion > 30, not >= 30", S, "return alive59 >= SCREEN_CRITERION", "return alive59 > SCREEN_CRITERION"),
    ("criterion read at season 60", S, "SCREEN_SEASON = MERGE - 1", "SCREEN_SEASON = MERGE"),
    ("byte-compare drops season 59 (history)", S, 'e["season"] <= upto]', 'e["season"] < upto]'),
    ("byte-compare ignores lineage.jsonl", S, '(("history.json", ha, hb), ("lineage.jsonl", la, lb))', '(("history.json", ha, hb),)'),
    ("byte-compare's EMPTY guard removed (vacuous pass)", S, "if not ha or not la:", "if False:"),
    ("stop rule 3-of-16 as > 3", S, "if len(all_) >= STOP_ALL:", "if len(all_) > STOP_ALL:"),
    ("stop rule 2-of-8 as > 2", S, "if len(first) >= STOP_FIRST:", "if len(first) > STOP_FIRST:"),
    ("stop rule's first half is seeds 1-7", S, "STOP_ALL, STOP_FIRST, FIRST_HALF = 3, 2, tuple(range(1, 9))", "STOP_ALL, STOP_FIRST, FIRST_HALF = 3, 2, tuple(range(1, 8))"),
    ("capped counts the holistic fauna only", S, 'for (j, _), r in results.items() if r["capped"]', 'for (j, k), r in results.items() if r["capped"] and k == H'),
    ("gate ignores the salt-0 verdicts", S, "    if bad:\n        _refuse(\"the salt-0", "    if False:\n        _refuse(\"the salt-0"),
    ("gate ignores missing records", S, "    if missing:\n        _refuse(f\"the screen is not complete", "    if False:\n        _refuse(f\"the screen is not complete"),
    ("salt-0 compare drops 129004 (pilot)", S, 'SALT0_REF = {1: "stage0", 2: "stage0", 3: "stage0", 4: "stageP"}', 'SALT0_REF = {1: "stage0", 2: "stage0", 3: "stage0"}'),
    ("salt-0 compare of 129004 against stage0 (no such run)", S, '3: "stage0", 4: "stageP"}', '3: "stage0", 4: "stage0"}'),
    ("K-SALT also at t >= 1 (always VOID)", S, "j in CENSUS_SEEDS and s >= 1 and t == 0", "j in CENSUS_SEEDS and s >= 1"),
    ("K-SALT never for 129001 at s >= 1", S, "j in CENSUS_SEEDS and s >= 1 and t == 0", "j in (2, 3) and s >= 1 and t == 0"),
    ("K-SALT compares the holistic half", S, 'verdict, lines = half_compare(job["src"], job["ref"], D)', 'verdict, lines = half_compare(job["src"], job["ref"], H)'),
    ("salt flags swapped", S, 'SALT_FLAG = {H: "--holistic-stream-salt", D: "--designed-stream-salt"}', 'SALT_FLAG = {D: "--holistic-stream-salt", H: "--designed-stream-salt"}'),
    ("salts_argv passes s as t", S, "([SALT_FLAG[D], str(t)] if t else [])", "([SALT_FLAG[D], str(s)] if t else [])"),
    ("fork source at (t_j, s_j)", S, '"extra": salts_argv(*salts[j]), "cost": MERGE}]} for j in range(1, n + 1)]', '"extra": salts_argv(*salts[j][::-1]), "cost": MERGE}]} for j in range(1, n + 1)]'),
    ("fork source for seeds 1..n-1", S, '"extra": salts_argv(*salts[j]), "cost": MERGE}]} for j in range(1, n + 1)]', '"extra": salts_argv(*salts[j]), "cost": MERGE}]} for j in range(1, n)]'),
    ("Stage 1 for seeds 1..n-1", S, "        for j in range(1, n + 1):\n            s, t = salts[j]", "        for j in range(1, n):\n            s, t = salts[j]"),
    ("adopt skips its config check", S, "    if _arm_config(src) != want:", "    if False:"),
    ("check_extra takes any value", S, 'if flag in SALT_FLAG.values() and str(value).isdigit():', 'if flag in SALT_FLAG.values():'),
    ("capped salt 0 counted as accepted (side effects)", S, 'ok = not r["capped"] and a["salt"] == r["salt"]', 'ok = a["salt"] == r["salt"]'),
    ("last season alive ignores refill", S, 'e["alive"] - e["births"] > 0], default=-1)', 'e["alive"] > 0], default=-1)'),
    ("designed salt re-spawns the holistic index", E, "            i = STREAMS.index(kind)\n", "            i = STREAMS.index(HOLISTIC)\n"),
    ("salt key shifted by one, (i, salt + 1)", E, "spawn_key=(i, int(salt)))", "spawn_key=(i, int(salt) + 1))"),
    ("designed salt 0 written to config.json", E, '        if not d["designed_stream_salt"]:\n            del d["designed_stream_salt"]', '        if False:\n            del d["designed_stream_salt"]'),
    ("negative salt accepted by spawn_streams", E, "            if int(salt) < 0:", "            if False:"),
]
PR_TESTS = ["tests/test_rbt129c.py", "tests/test_rng_streams.py", "tests/test_salt0_golden.py"]
MINE = ["runs/RBT-129/founding-screen-adversary/test_founding_screen_adversary.py"]


def run(tree, tests):
    r = subprocess.run([sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", *tests], cwd=tree,
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": tree})
    return r.returncode == 0


def main():
    tree = sys.argv[1]
    print("# RBT-129c (#495) adversary mutants: killed by the PR's tests / by the adversary's tests")
    for name, path, old, new in MUTANTS:
        p = os.path.join(tree, path)
        src = open(p).read()
        if src.count(old) != 1:
            print(f"  NOT APPLIED ({src.count(old)} matches): {name}")
            continue
        open(p, "w").write(src.replace(old, new))
        try:
            pr = run(tree, PR_TESTS)
            mine = run(tree, MINE) if pr else None
        finally:
            open(p, "w").write(src)
        verdict = "killed by PR tests" if not pr else ("SURVIVES the PR tests; killed by adversary tests" if not mine else "SURVIVES both")
        print(f"  {verdict:50s} {name}", flush=True)


if __name__ == "__main__":
    main()
