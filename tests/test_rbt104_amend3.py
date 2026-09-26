"""RBT-104 Amendment 3: HELD rests on k_planted (k_bare reported), and 'compass' needs the ATTRIBUTION."""
import importlib.util
import os

_p = os.path.join(os.path.dirname(__file__), "..", "runs", "RBT-104", "readout.py")
_s = importlib.util.spec_from_file_location("rbt104_readout", _p)
ro = importlib.util.module_from_spec(_s)
_s.loader.exec_module(ro)


def test_window_reading_holds_on_k_planted_and_reports_k_bare(tmp_path):
    f = tmp_path / "peek-300.txt"
    f.write_text("WINDOW seed 801 season 300: k = 5, n = 30, B = 6 -> AT OR BELOW NO-SELECTION; k_bare = 9 (reported, not counted)\n")
    r = ro.peek(str(f))
    assert r["k"] == 5 and r["k_bare"] == 9 and r["B"] == 6
    assert r["above"] is False  # 5 planted-rooted hits <= B, whatever k_bare is


def test_compass_needs_the_attribution(tmp_path):
    f = tmp_path / "function.txt"
    f.write_text("LINE S8-801: FOOD-DEPENDENT  F +0.500 [+0.100, +0.900]  compass UNRESOLVED at this n  bodies 7\n")
    r = ro.function(str(f))
    assert r["fd"] is True and r["compass_fd"] is False
    f.write_text("LINE S8-801: FOOD-DEPENDENT  F +0.500 [+0.100, +0.900]  compass FOOD-DEPENDENT  bodies 7\n")
    assert ro.function(str(f))["compass_fd"] is True


def test_null_rates_readout_reproduces():
    import subprocess
    import sys
    here = os.path.join(os.path.dirname(__file__), "..", "runs", "RBT-104")
    out = subprocess.run([sys.executable, os.path.join(here, "null_rates.py")], capture_output=True, text=True).stdout
    assert out == open(os.path.join(here, "null_rates.txt")).read()


def test_a_pre_amendment_window_reading_is_refused(tmp_path):
    f = tmp_path / "peek-300.txt"
    f.write_text("WINDOW seed 801 season 300: k = 12, n = 30, B = 6 -> HELD ABOVE NO-SELECTION\n")
    assert ro.peek(str(f)) is None


def _w(k, B, kb=0):
    return dict(k=k, n=30, B=B, above=k > B, text="", k_bare=kb)


def test_a_missing_window_reading_never_reads_as_f_b():
    usable = [801, 4, 804]
    # 801 and 4 not held; 804's 599 reading missing -> not F-b, NOT READ
    windows = {801: (_w(1, 5), _w(0, 3)), 4: (_w(2, 6), _w(1, 3)), 804: (_w(2, 6), None)}
    br = ro.falsified_branch(usable, windows, inhost=[])
    assert "NOT READ" in br and "F-b" not in br.split(":")[0]
    windows[804] = None, None
    assert "NOT READ" in ro.falsified_branch(usable, windows, inhost=[])
    del windows[804]
    assert "NOT READ" in ro.falsified_branch(usable, windows, inhost=[])
    # every usable seed has both readings -> the branch is read
    windows[804] = (_w(2, 6), _w(1, 3))
    assert ro.falsified_branch(usable, windows, inhost=[]).startswith("(F-b)")


def test_readout_reads_only_the_amendment3_window_names():
    assert ro.WINDOW_FILES == ("peek-a3-300.txt", "peek-a3-599.txt")
    src = open(_p).read()
    assert '"peek-300.txt"' not in src and '"peek-599.txt"' not in src
