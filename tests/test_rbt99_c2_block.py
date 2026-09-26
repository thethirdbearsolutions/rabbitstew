"""RBT-99's C2 block (Amendment 1, answering the adversary's F4-F7): the price beside R-shift, turnover
against the baseline, the null note and the framing, from committed tables only; an extinct fauna earns 0."""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEAD = "season\tpopulation\talive\tbirths\tdeaths\tmean_lifetime_score\tbest_lifetime_score"


def _seasons(d, conv_income, conv_deaths, conv_alive=lambda s: 60, hol_income=lambda s: 1.0):
    d.mkdir(parents=True)
    rows = [HEAD]
    for s in range(30):
        rows.append(f"{s}\tholistic\t60\t2\t2\t{hol_income(s)}\t2")
        rows.append(f"{s}\tconventional\t{conv_alive(s)}\t{conv_deaths(s)}\t{conv_deaths(s)}\t{conv_income(s)}\t2")
    (d / "seasons.txt").write_text("\n".join(rows) + "\n")


def test_c2_block(tmp_path, monkeypatch, capsys):
    _seasons(tmp_path / "base" / "forage-1", lambda s: 0.9, lambda s: 2)
    # shift at 10: holistic drops to 0.8; designed churns (8 deaths a season) until 15, then is extinct and earns 0
    _seasons(tmp_path / "arms" / "shift-1", lambda s: 0.9 if s < 10 else 0.5, lambda s: 2 if s < 10 else 8,
             conv_alive=lambda s: 0 if s >= 15 else 60, hol_income=lambda s: 1.0 if s < 10 else 0.8)
    (tmp_path / "onset.txt").write_text("seed\tT\n1\t10\n")
    (tmp_path / "price.txt").write_text("header line\nseed\tfauna\tT\twindow\trows\tkJ\tprice\n"
                                        "1\tholistic\t10\t0-9\t100\t4.000\t0.2000\n1\tconventional\t10\t0-9\t100\t20.000\t1.0000\n")
    for k, v in {"RBT92_WINDOWS": "5,3,4,3,2", "RBT92_SEEDS": "1", "RBT92_BASE_DIR": str(tmp_path / "base"),
                 "RBT99_ARM_DIR": str(tmp_path / "arms"), "RBT92_ONSET": str(tmp_path / "onset.txt"),
                 "RBT99_PRICE": str(tmp_path / "price.txt")}.items():
        monkeypatch.setenv(k, v)
    spec = importlib.util.spec_from_file_location("c2_block", ROOT / "runs" / "RBT-99" / "c2_block.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.main()
    out = capsys.readouterr().out
    # recovery [13, 17): holistic 0.8 - 1.0 = -0.2, net of a 0.2 price = 0; designed 0.5 - 0.9 on 13-14, extinct (0) - 0.9 on 15-16: -0.65
    assert "holistic R-shift -0.200 price -0.200 net +0.000" in out
    assert "conventional R-shift -0.650 price -1.000 net +0.350" in out
    # transient [10, 13): designed deaths 24 against 6: ratio 4, flagged
    assert "conventional transient: deaths   24 vs    6" in out and "ratio 4.00   >= 2x base" in out
    assert "designed deaths in the shift arm over [T, T+10) 80 (k's window) and over [T+10, T+3) 0" in out
    assert "one body's cheapness, not two bodies'" in out
    assert "the designed body wins on the held-out challenge" in out
