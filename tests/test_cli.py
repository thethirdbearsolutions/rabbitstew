from rabbitstew.cli import main
from rabbitstew.genotype import Genotype


def test_cli_end_to_end(tmp_path, capsys):
    r = str(tmp_path / "r.json")
    p = str(tmp_path / "p.json")
    assert main(["random", "--seed", "4", "--out", r]) == 0
    assert main(["fixed", "--drive", "--out", p]) == 0
    assert Genotype.load(r).is_valid() and Genotype.load(p).is_valid()
    assert main(["inspect", r]) == 0
    assert "parts from" in capsys.readouterr().out
    traj = str(tmp_path / "bout.traj")
    html = str(tmp_path / "bout.html")
    assert main(["simulate", r, p, "--duration", "0.5", "--out", traj, "--html", html]) == 0
    out = capsys.readouterr().out
    assert "winner" in out
    assert main(["visualize", traj, "--out", str(tmp_path / "again.html")]) == 0
    run = str(tmp_path / "run")
    assert main(["evolve", "--generations", "1", "--population", "3", "--champion-interval", "1", "--champions", "1", "--duration", "0.3", "--out", run]) == 0
    assert main(["history", run + "/history.json"]) == 0
    assert "champion bouts" in capsys.readouterr().out
