"""RBT-132 design adversary: mutants of the code RBT-132 ADDS (steer.py's per-point parts, planters.py,
probe_members.py), against tests/test_rbt132.py and tests/test_rbt116_steer.py.  rbt132_mutants.py re-ran RBT-116's own
kill-sets, which cover W1; nothing yet asked whether RBT-132's own tests kill faults in RBT-132's own code.

    python runs/RBT-116/design-adversary/rbt132_new_mutants.py TREE [WORKERS] > runs/RBT-116/design-adversary/rbt132_new_mutants.txt

Each mutant is one textual fault in one file, run in a hard-linked private copy of TREE (the mutated file is rewritten,
never edited through the link).  Fixture tests only: no RBT-129 or RBT-116 point, pool season, host or arm is run.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

S, P, Q = "runs/RBT-116/steer.py", "runs/RBT-116/planters.py", "runs/RBT-116/probe_members.py"
TESTS = ["tests/test_rbt132.py", "tests/test_rbt116_steer.py"]
MUTANTS = [
    (S, "CONTROL (no fault: must SURVIVE)", "N_BATTERY = N_STAGE1 + N_STAGE2 + N_CONFIRM", "N_BATTERY = N_STAGE1 + N_STAGE2 + N_CONFIRM"),
    # steer.py: the per-point additions
    (S, "tau-ignores-point", 'return REGISTERED_POINTS[point]["smell_tau"]', "return SMELL_TAU"),
    (S, "L-point-channel-allowed", ' or REGISTERED_POINTS[point]["smell_contrast"] <= 0)', ")"),
    (S, "G-rows-tau-1", '"smell_tau": 2.0, "eat_from": "root",\n', '"smell_tau": 1.0, "eat_from": "root",\n'),
    (S, "screen-default-season-W1", 'if season is run_season and world != "W1":', "if False:"),
    (S, "_job-ignores-point", 'season = run_season if point == "W1" else point_season(point)', "season = run_season"),
    (S, "cli-drops-world-in-tasks", "battery.to_dict(), a.world) for p in a.genomes]", "battery.to_dict()) for p in a.genomes]"),
    (S, "cli-channel-check-at-W1", "    assert_registered_channel(cfg, a.world)\n", "    assert_registered_channel(cfg)\n"),
    (S, "cli-fair-check-dropped", "    assert_fair_config(raw, a.world)\n", ""),
    (S, "fair-check-off", 'if point in FAIR_POINTS and raw.get("fairness") != "fair":', "if False:"),
    (S, "pool-keys-shifted", "enumerate(RBT129_POINTS, start=1)", "enumerate(RBT129_POINTS, start=2)"),
    # planters.py
    (P, "host-perm-no-fauna-term", 'list(HOSTS_KEY) + [0 if kind == "conventional" else 1]', "list(HOSTS_KEY)"),
    (P, "host-seeds-1-only", "HOST_SEEDS = (1, 2, 3)", "HOST_SEEDS = (1,)"),
    (P, "compass-probes-need-not-agree", "if backs[0] is None or backs[0] != backs[1]:", "if backs[0] is None:"),
    (P, "compass-sign-inverted", "return +1.0 if backs[0] == routed.mech.rs.PUBLISHED_IS_BACKWARD else -1.0", "return -1.0 if backs[0] == routed.mech.rs.PUBLISHED_IS_BACKWARD else +1.0"),
    (P, "rung-a-8", "W_RUNG = 3.0", "W_RUNG = 4.0"),
    (P, "motors-off-keeps-bias", "node.segment.brain.units[i].bias = 0.0", "pass"),
    (P, "motors-off-keeps-links", "if not (l.dst.index in effs and l.dst.node in (None, nd))]", "]"),
    (P, "b-signed-not-abs", 'gb.units.append(Neuron(bias=0.0, func="abs"))', 'gb.units.append(Neuron(bias=0.0, func="tanh"))'),
    (P, "b-no-threshold", "gb.units.append(Neuron(bias=-q, func=\"relu\"))", "gb.units.append(Neuron(bias=0.0, func=\"relu\"))"),
    (P, "b-nose-on-root", "gb.links.append(Link(UnitRef(LEFT, nose), UnitRef(None, mag), k))", "gb.links.append(Link(UnitRef(0, nose), UnitRef(None, mag), k))"),
    (P, "c-multi-instance-noses", "if len(parts) == 1]", "]"),
    (P, "c-straddling-effectors-wired", "if np.all(s > 0) or np.all(s < 0):", "if True:"),
    (P, "c-noses-same-sign", "for nd, s in ((layout[\"left\"], +1.0), (layout[\"right\"], -1.0)):", "for nd, s in ((layout[\"left\"], +1.0), (layout[\"right\"], +1.0)):"),
    (P, "c-w-doubled", "sign * side * w))", "sign * side * 2 * w))"),
    (P, "tune-argmin", "best = int(np.argmax([f for _, f in table]))", "best = int(np.argmin([f for _, f in table]))"),
    (P, "tune-on-draws-5-8", "tune_draws = pool[:N_TUNE]", "tune_draws = pool[N_TUNE:2 * N_TUNE]"),
    (P, "k3-lbdT-ignored", 's2.get("lbdT", -1) > 0', "True"),
    (P, "k3-veto-ignored", 'and s2.get("c3") and', "and"),
    (P, "k3-threshold-3", "len(a) + len(c) >= 4", "len(a) + len(c) >= 3"),
    (P, "k4-b-excluded", 'for key in ("b", "d", "e", "motors-off")', 'for key in ("d", "e", "motors-off")'),
    (P, "planted-calls-at-W1", "steer.call_genome(gd, SimConfig.from_dict(cfg_d), steer.Battery.from_dict(bat_d), steer.point_season(point))",
     "steer.call_genome(gd, SimConfig.from_dict(cfg_d), steer.Battery.from_dict(bat_d))"),
    (P, "planted-fair-check-dropped", "    steer.assert_fair_config(raw, point)\n    season = steer.point_season(point)", "    season = steer.point_season(point)"),
    (P, "planted-screen-hosts-a-only", 'steer.screen_draws(plants["a"] + plants["c"], cfg, point, season)', 'steer.screen_draws(plants["a"], cfg, point, season)'),
    (P, "planted-no-refusal-when-short", "    if short:\n", "    if False:\n"),
    (P, "power-line-legacy-everywhere", 'if steer.REGISTERED_POINTS[point]["smell_contrast"] > 0 else table["legacy"]', 'if False else table["legacy"]'),
    # probe_members.py
    (Q, "members-with-replacement", "N_PROBE, replace=False)", "N_PROBE, replace=True)"),
    (Q, "founders-any-season", 'if row["season"] != 0:', "if False:"),
    (Q, "missing-below-1", "if len(chosen) < N_MIN:", "if len(chosen) < 1:"),
    (Q, "f-on-stage1", "for d in bat.stage2[:N_F]]", "for d in bat.stage1[:N_F]]"),
    (Q, "f-on-4-draws", "N_PROBE, N_MIN, N_F = 20, 5, 8", "N_PROBE, N_MIN, N_F = 20, 5, 4"),
    (Q, "probe-at-W1", "    season = steer.point_season(point)\n    f = [", "    season = steer.run_season\n    f = ["),
    (Q, "probe-fair-check-dropped", "    steer.assert_fair_config(raw, point)\n    bat =", "    bat ="),
    (Q, "rng-offset", "np.random.default_rng(int(rng))", "np.random.default_rng(int(rng) + 1)"),
]


def run(tree, path, name, old, new):
    src = open(os.path.join(tree, path)).read()
    if src.count(old) != 1:
        return name, f"BAD-MUTANT ({src.count(old)} anchors)", ""
    tmp = tempfile.mkdtemp(prefix="mut132-")
    for p in sorted(set(os.listdir(tree)) - {".git"}):
        subprocess.run(["cp", "-al", os.path.join(tree, p), os.path.join(tmp, p)], check=True)
    dst = os.path.join(tmp, path)
    os.unlink(dst)  # break the hard link before writing
    open(dst, "w").write(src.replace(old, new))
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider"] + TESTS,
                       cwd=tmp, capture_output=True, text=True, timeout=3600)
    shutil.rmtree(tmp, ignore_errors=True)
    failed = [l for l in r.stdout.splitlines() if l.startswith("FAILED") or l.startswith("ERROR")]
    return name, ("KILLED" if r.returncode else "SURVIVED"), (failed[0].split(" - ")[0] if failed else r.stdout.strip().splitlines()[-1])


if __name__ == "__main__":
    tree = os.path.abspath(sys.argv[1])
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    with ThreadPoolExecutor(w) as ex:
        res = list(ex.map(lambda m: (m[0],) + run(tree, *m), MUTANTS))
    print(f"# rbt132_new_mutants.py: {len(MUTANTS)} mutants of RBT-132's added code, against {' + '.join(TESTS)}")
    for path, name, verdict, why in res:
        print(f"{verdict:9s} {os.path.basename(path):17s} {name:34s} {why}")
    ctrl, muts = res[0], res[1:]
    print(f"# control: {ctrl[2]} (the unmutated copy {'passes: the harness is sound' if ctrl[2] == 'SURVIVED' else 'FAILS: the harness is broken'})")
    print(f"# killed {sum(r[2] == 'KILLED' for r in muts)} / {len(muts)}; survivors: " + ", ".join(r[1] for r in muts if r[2] != "KILLED"))
