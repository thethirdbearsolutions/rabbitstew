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
    assert 340 <= T0 <= 395
    later = {key: (v if key[0] < 340 else rng.randint(0, 60)) for key, v in deaths.items()}
    write(later)
    assert on.onset(1)[0] == T0
