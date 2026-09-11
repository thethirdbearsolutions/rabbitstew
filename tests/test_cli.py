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
    gallery = str(tmp_path / "gallery.html")
    assert main(["gallery", run, "--out", gallery]) == 0
    text = open(gallery).read()
    assert "RabbitstewReplay" in text and '"entries":[' in text and "champions_gen" not in text
    assert (tmp_path / "run" / "holistic" / "champions_gen0000" / "0.json").exists()
    report = str(tmp_path / "report.html")
    assert main(["report", run, run, "--out", report]) == 0
    text = open(report).read()
    assert '"multi":true' in text and '"mean_curve":[' in text and "best_units" in text
    cmp = str(tmp_path / "compare.html")
    assert main(["compare", f"a={run}", f"b={run},{run}", "--out", cmp]) == 0
    text = open(cmp).read()
    assert '"conditions":[' in text and '"name":"b"' in text
