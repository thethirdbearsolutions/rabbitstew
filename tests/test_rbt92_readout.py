"""RBT-92's readout: an extinct fauna earns 0 in every later season of every window, never skipped
(senior review (a); coordinator ruling 2026-09-26 13:10, item 1), and the onset rule reads nothing at or
after the onset (item 2 / Amendment 2)."""
import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "runs" / "RBT-92" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _arm(tmp_path, seasons, holistic_dies_at=None, stop_rows=False):
    """A synthetic arm: holistic earns 1.0 while alive, conventional 0.4 throughout; lineage-last is one
    founder per fauna spanning its life, so the table is self-consistent."""
    d = tmp_path / "arm"
    d.mkdir()
    rows = ["season\tpopulation\talive\tbirths\tdeaths\tmean_lifetime_score\tbest_lifetime_score"]
    for s in range(seasons):
        dead = holistic_dies_at is not None and s >= holistic_dies_at
        if not (dead and stop_rows):
            rows.append(f"{s}\tholistic\t{0 if dead else 1}\t0\t{1 if s == holistic_dies_at else 0}\t{0.0 if dead else 1.0}\t0")
        rows.append(f"{s}\tconventional\t1\t0\t0\t0.4\t0")
    (d / "seasons.txt").write_text("\n".join(rows) + "\n")
    last_h = (holistic_dies_at - 1) if holistic_dies_at is not None else seasons - 1
    (d / "lineage-last.txt").write_text(
        "population\tname\tgeneration\tage\tevals\tfitness\tparents\n"
        f"holistic\th0-0\t{last_h}\t{last_h}\t1\t1.0\t\n"
        f"conventional\tc0-0\t{seasons - 1}\t{seasons - 1}\t1\t0.4\t\n")
    return d


@pytest.mark.parametrize("stop_rows", [False, True])
def test_an_extinct_fauna_earns_zero_and_is_not_skipped(tmp_path, stop_rows):
    ro = _load("readout")
    arm = ro.Arm(str(_arm(tmp_path, 40, holistic_dies_at=25, stop_rows=stop_rows)))
    # window [20, 40): holistic alive 5 seasons at 1.0 then 15 at 0: mean 0.25; minus conventional 0.4
    assert ro.rbody(arm, 20, 40) == pytest.approx(0.25 - 0.4)
    assert ro.wmean(arm.x["holistic"], 20, 40) == pytest.approx(0.25)
    # the NaN-filtered mean over survivors would have read +0.6; the fix is what separates them
    assert ro.rbody(arm, 20, 40) != pytest.approx(1.0 - 0.4)
    # the round trip still holds through the extinction
    assert arm.check_alive("holistic", 0, 40) == []


def test_a_living_arm_is_unchanged(tmp_path):
    ro = _load("readout")
    arm = ro.Arm(str(_arm(tmp_path, 30)))
    assert ro.rbody(arm, 0, 30) == pytest.approx(0.6)


def test_the_onset_rule_reads_nothing_at_or_after_the_onset(tmp_path, monkeypatch):
    """Perturbing every season >= 340 of the baseline cannot move T; T is always >= 340."""
    import random
    rng = random.Random(0)
    base = tmp_path / "forage-1"
    base.mkdir()
    deaths = {(s, k): rng.randint(0, 6) + (25 if (s - 11) % 60 < 8 and s > 100 else 0)
              for s in range(600) for k in ("holistic", "conventional")}

    def write(ds):
        rows = ["season\tpopulation\talive\tbirths\tdeaths\tmean_lifetime_score\tbest_lifetime_score"]
        rows += [f"{s}\t{k}\t60\t0\t{ds[(s, k)]}\t1.0\t1.0" for s in range(600) for k in ("holistic", "conventional")]
        (base / "seasons.txt").write_text("\n".join(rows) + "\n")

    monkeypatch.setenv("RBT92_BASELINE_DIR", str(tmp_path))
    on = _load("onset")
    write(deaths)
    T0 = on.onset(1)[0]
    assert 340 <= T0 <= 399
    later = {key: (v if key[0] < 340 else rng.randint(0, 60)) for key, v in deaths.items()}
    write(later)
    assert on.onset(1)[0] == T0


def test_a_co_evolved_collapse_beside_a_thriving_comparator_is_E2_not_both_fail():
    """Adversary F4b: RBT-89's E read "co-evolved income < 0.25" alone as "both fail"; the mirror of D is E2."""
    ro = _load("readout")
    # ten seeds, co-evolved bankrupt on 9 and designed on none: E2, reported with the falsifier
    assert ro.classify(10, -0.5, 0.08, 0, 10, e1=0, dz=0, e2=9).startswith("E2.")
    assert "falsifier" in ro.classify(10, -0.5, 0.08, 0, 10, e1=0, dz=0, e2=9).lower()
    # both bankrupt on 8/10: E1
    assert ro.classify(10, 0.0, 0.08, 5, 5, e1=8, dz=1, e2=1).startswith("E1.")
    # designed bankrupt: D, which outranks E2
    assert ro.classify(10, 0.3, 0.08, 10, 0, e1=0, dz=8, e2=0).startswith("D.")
    # B needs n >= 8 and r <= 0.10; at seven seeds a small mean is F
    assert ro.classify(10, 0.02, 0.077, 6, 4, 0, 0, 0).startswith("B.")
    assert ro.classify(7, 0.02, 0.09, 4, 3, 0, 0, 0).startswith("F.")


def _synthetic_epoch(root, seeds=(1, 2, 3, 4, 5, 6), T=10, S=20):
    """Six seeds of four self-consistent arms (one individual per fauna), groups.txt on every arm, so that
    readout.main() passes V0-V2 and reaches the classifier (adversary re-check, residual 1)."""
    import random
    rng = random.Random(7)
    base_dir, arm_dir = root / "base", root / "arms"
    arm_dir.mkdir(parents=True)
    (arm_dir / "onset.txt").write_text("seed\tT\n" + "".join(f"{s}\t{T}\n" for s in seeds))
    head = "season\tpopulation\talive\tbirths\tdeaths\tmean_lifetime_score\tbest_lifetime_score\n"
    lhead = "population\tname\tgeneration\tage\tevals\tfitness\tparents\n"

    def write(d, rows, last, events="", groups=True):
        d.mkdir(parents=True)
        (d / "seasons.txt").write_text(head + "".join(rows))
        (d / "lineage-last.txt").write_text(lhead + last)
        (d / "events.txt").write_text("kind\tpopulation\tseason\tcount\tnames\n" + events)
        if groups:
            (d / "groups.txt").write_text("season\tpopulation\tsizes\tnames_in_groups_below_modal\n" + "".join(
                f"{s}\t{k}\t1\t\n" for s in range(S) for k in ("holistic", "conventional")))

    for seed in seeds:
        xs = {(s, k): round(0.5 + rng.random(), 6) for s in range(S) for k in ("holistic", "conventional")}
        live = "holistic\th0-0\t19\t19\t1\t1.0\t\nconventional\tc0-0\t19\t19\t1\t0.5\t\n"
        base = [f"{s}\t{k}\t1\t0\t0\t{xs[(s, k)]}\t1\n" for s in range(S) for k in ("holistic", "conventional")]
        write(base_dir / f"forage-{seed}", base, live, groups=False)
        shift = [f"{s}\t{k}\t1\t0\t0\t{xs[(s, k)] if s < T else xs[(s, k)] * 0.8}\t1\n"
                 for s in range(S) for k in ("holistic", "conventional")]
        write(arm_dir / f"shift-{seed}", shift, live, events=f"shift\t-\t{T}\t{S - T}\tgroup-size=8\n")
        cull20 = [f"{s}\t{k}\t{1 if s < T else 0}\t0\t{1 if s == T else 0}\t{xs[(s, k)] if s < T else 0.0}\t1\n"
                  for s in range(S) for k in ("holistic", "conventional")]
        culled = f"holistic\th0-0\t{T}\t{T - 1}\t1\t1.0\t\nconventional\tc0-0\t{T}\t{T - 1}\t1\t0.5\t\n"
        write(arm_dir / f"cull20-{seed}", cull20, culled,
              events=f"cull\tholistic\t{T}\t1\th0-0\ncull\tconventional\t{T}\t1\tc0-0\n")
        (arm_dir / f"cull-k-{seed}.txt").write_text("cull\tholistic=0,conventional=0\n")
    return base_dir, arm_dir


def test_the_readout_reaches_a_verdict_at_six_seeds_with_groups_present(tmp_path):
    """smoke.sh at n = 2 never reaches the classifier; this does, with groups.txt on the arms, which is the
    case the r clobber crashed on (adversary re-check residual 1)."""
    import os
    import subprocess
    import sys
    base_dir, arm_dir = _synthetic_epoch(tmp_path)
    env = dict(os.environ, RBT92_WINDOWS="5,3,4,3,2", RBT92_SEEDS="1 2 3 4 5 6", RBT92_BASE_DIR=str(base_dir),
               RBT92_ARM_DIR=str(arm_dir), RBT92_ONSET=str(arm_dir / "onset.txt"))
    out = subprocess.run([sys.executable, str(ROOT / "runs" / "RBT-92" / "readout.py")], env=env,
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-2000:]
    assert "V0-V2: PASS on 6/6" in out.stdout
    assert "REMAINDER GROUPS" in out.stdout
    verdict = [line for line in out.stdout.splitlines() if "CLASS:" in line]
    assert verdict and "NONE" not in verdict[0], verdict
    assert "equivalence form" in out.stdout and "turnover guard" in out.stdout
