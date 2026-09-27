"""RBT-107 readout.py: the print-only seed-set sensitivity beside H1 (post-H-REP note; coordinator 06:02) leaves the scored
confirmatory() path byte-identical, on synthetic contrasts with one seed's co-evolved fauna extinct (as seed 29's is)."""
import importlib.util
import pathlib
import random

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEEDS = list(range(11, 31))
EXTINCT = 29  # co-evolved fauna extinct: UNREAD for that fauna, so the common set is n = 19 and DES per fauna is n = 20


@pytest.fixture()
def ro():
    spec = importlib.util.spec_from_file_location("rbt107_readout_test", ROOT / "runs" / "RBT-107" / "readout.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _fake_contrasts(sm, seed, kind, d, part=None):
    if kind == "holistic" and seed == EXTINCT:
        return None
    r = random.Random(f"{seed}-{kind}-{d}")
    mu = -0.2 if kind == "conventional" else 0.05
    if seed == EXTINCT:
        mu = 0.3  # the extra seed pulls DES the other way, so the two seed sets differ
    sb = mu + r.gauss(0, 0.15)
    return dict(SB=sb, SN=sb + r.gauss(0, 0.08), NB=r.gauss(0, 0.1), I=r.gauss(0, 0.1), IN=r.gauss(0, 0.1),
                RSB=r.gauss(0, 0.1), REF=0.8 + r.gauss(0, 0.05))


def _run(ro, monkeypatch, capsys, stub):
    monkeypatch.setattr(ro, "contrasts", _fake_contrasts)
    if stub:
        monkeypatch.setattr(ro, "h1_sensitivity", lambda *a, **k: None)
        monkeypatch.setattr(ro, "halt_sensitivity", lambda *a, **k: None)
    ro.confirmatory(ro.Sample("FRESH", SEEDS, True))
    return capsys.readouterr().out.splitlines()


def test_scored_lines_are_unchanged_by_the_sensitivity(ro, monkeypatch, capsys):
    full = _run(ro, monkeypatch, capsys, stub=False)
    scored_only = _run(ro, monkeypatch, capsys, stub=True)  # the stub stays patched for the rest of the test
    assert [l for l in full if "sensitivity (not scored)" not in l] == scored_only
    assert any("sensitivity (not scored)" in l for l in full)


def test_scored_h1_is_on_the_common_set_and_the_sensitivity_on_the_designed_complete_seeds(ro, monkeypatch, capsys):
    full = _run(ro, monkeypatch, capsys, stub=False)
    h1_scored = [l for l in full if (l.strip().startswith("H1-DES designed ") or l.strip().startswith("H1-PAIR paired "))
                 and "sensitivity" not in l]
    assert len(h1_scored) == 4 and all("n=19" in l for l in h1_scored)
    sens = [l for l in full if "H1-DES designed [per fauna, sensitivity (not scored)]" in l]
    assert len(sens) == 2 and all("n=20" in l for l in sens)
    assert any("extra seeds [29]" in l for l in full)
    verdict = [l for l in full if l.startswith("  H1 (IUT, Holm")]
    assert len(verdict) == 1 and "sensitivity" not in verdict[0]
    assert any(l.startswith("  H-ALT outcome FRESH:") for l in full)
    assert any("H-ALT increment on the common set" in l and "n=19" in l for l in full)
