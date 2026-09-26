"""RBT-92's readout when a cull's k exceeds the fauna's alive count (RBT-99 adversary F1, F3).

The switch removes min(k, alive) (ecology.py _cull). V1 must expect that, not k, or one capped seed halts
the shift readout for every seed; and the capped fauna's R-null is n/a, because its null is extinction,
not turnover."""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEAD = "season\tpopulation\talive\tbirths\tdeaths\tmean_lifetime_score\tbest_lifetime_score"
LAST = 20  # seasons 0..19; T = 10; windows 5,3,4,3,2 need T + 10 seasons
T = 10
N = 3      # alive per fauna


def _write_arm(d, culled=(), shift=False):
    """Three founders per fauna alive 0..19; a culled fauna loses all three at the top of season T."""
    d.mkdir(parents=True)
    rows, last = [HEAD], ["population\tname\tgeneration\tage\tevals\tfitness\tparents"]
    for kind, inc, p in (("holistic", 1.0, "h"), ("conventional", 0.4, "c")):
        gone = kind in culled
        for s in range(LAST):
            alive = 0 if gone and s >= T else N
            rows.append(f"{s}\t{kind}\t{alive}\t0\t{N if gone and s == T else 0}\t{inc if alive else 0.0}\t{inc}")
        for i in range(N):
            # a culled row is logged at the top of T and repeats the age of T - 1 (readout.py's V2 note)
            g, a = (T, T - 1) if gone else (LAST - 1, LAST - 1)
            last.append(f"{kind}\t{p}0-{i}\t{g}\t{a}\t{g}\t{inc}\t")
    (d / "seasons.txt").write_text("\n".join(rows) + "\n")
    (d / "lineage-last.txt").write_text("\n".join(last) + "\n")
    ev = ["kind\tpopulation\tseason\tcount\tnames"]
    for kind, p in (("holistic", "h"), ("conventional", "c")):
        if kind in culled:
            ev.append(f"cull\t{kind}\t{T}\t{N}\t{','.join(f'{p}0-{i}' for i in range(N))}")
    if shift:
        ev.append(f"shift\t-\t{T}\t{LAST - T}\tshift")
    (d / "events.txt").write_text("\n".join(ev) + "\n")


def test_a_cull_k_above_alive_passes_v1_and_reads_r_null_na(tmp_path, monkeypatch, capsys):
    base, arms = tmp_path / "base", tmp_path / "arms"
    _write_arm(base / "forage-1")
    _write_arm(arms / "shift-1", shift=True)
    _write_arm(arms / "cull-1", culled=("conventional",))
    _write_arm(arms / "cull20-1", culled=("holistic", "conventional"))
    (arms / "cull-k-1.txt").write_text("cull\tholistic=0,conventional=41\n")  # 41 > 3 alive
    (tmp_path / "onset.txt").write_text(f"seed\tT\n1\t{T}\n")
    for k, v in {"RBT92_WINDOWS": "5,3,4,3,2", "RBT92_SEEDS": "1", "RBT92_BASE_DIR": str(base),
                 "RBT92_ARM_DIR": str(arms), "RBT92_ONSET": str(tmp_path / "onset.txt")}.items():
        monkeypatch.setenv(k, v)
    spec = importlib.util.spec_from_file_location("readout_cap", ROOT / "runs" / "RBT-92" / "readout.py")
    ro = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ro)
    ro.main()
    out = capsys.readouterr().out
    assert "V1 note 1: cull-k conventional=41 >= alive 3" in out
    assert "V0-V2: PASS" in out
    assert "INSTRUMENT FAILED VALIDATION" not in out
    rnull = [l for l in out.splitlines() if l.strip().startswith("R-null") and "conventional" in l]
    assert rnull and all("n/a on [1]" in l for l in rnull)
    # the co-evolved fauna was not capped: its R-null is read
    assert all("n/a" not in l for l in out.splitlines() if l.strip().startswith("R-null") and "holistic" in l)
    # R-cull is still read on the capped fauna, labelled as extinction, not turnover (adversary re-check caveat 1)
    rcull = [l for l in out.splitlines() if l.strip().startswith("R-cull ") and "conventional" in l]
    assert rcull and all("capped on [1]: extinction, not turnover" in l for l in rcull)
