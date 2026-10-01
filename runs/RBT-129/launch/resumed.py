#!/usr/bin/env python3
"""Which Stage-1 runs were ever resumed, from their checkpoint branches' provenance only (the K-SALT VOID of
1/c1-p010-PW-G/129003; fix/RBT-129-resume-lineage).

    python runs/RBT-129/launch/resumed.py [--lanes runs/RBT-129/lanes/1] [--sources] [--json]

For every run directory a Stage-1 lane names (``dir`` of fresh / adopt / snapshot / resume jobs), the directory's
``ckpt/<label>`` branch is fetched and three files are read out of its tarball, nothing else: ``config.json`` (the
seasons target), ``platform.json`` (one record per ``Ecology.resume``, RBT-127) and ``command.txt`` (one line per
ecology command the lane ran: a fresh run, or ``--resume --seasons N``).  No outcome file (history, lineage, cohorts,
state, run.log) of a Stage-1 run is opened.

A resume to the target already in force (a resume line whose ``--seasons`` equals the previous line's) continued a
killed attempt: ``killed``.  A resume to a new target (S60 to 300) is the design's: ``planned``.  An adopted S60 and its
ckpt60 copy the census directory whole (``fork_config``), so their records start with the census's own.  The season a
resume restarted from is not on record in these files.

A resume is where a run can have been written twice (an orphaned attempt still running beside it), not proof that it
was, nor is its absence proof of a single writer: at 830450e a lane restarted beside an orphan still in season 0 wipes
the directory and starts afresh, leaving a double write with no resume record (#504 S5).  ``--check-runs`` (the
coordinator's leave, 2026-10-01) therefore checks every checkpointed Stage-1 run's lineage.jsonl and cohorts.jsonl for
the signature, resumed or not, structurally (see ``written_twice``); it holds up to each run's latest snapshot.  ``--sources`` adds the census directories the lanes adopt from or K-SALT compares against (Stage 0 / P, not
Stage 1) and, for those only, counts rows of lineage.jsonl and cohorts.jsonl repeated byte for byte and steps back in
their season column, which two writers leave (counts only; no field but the season is parsed).
"""

import argparse
import glob
import io
import json
import os
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUNS))
REMOTE = os.environ.get("DURABLE_REMOTE", "origin")
RUN_JOBS = ("fresh", "adopt", "snapshot", "resume")
PROVENANCE = ("config.json", "platform.json", "command.txt")


def label(d: str) -> str:
    """stages.py's ``_label``: ``rbt-129-<path under runs/RBT-129>`` with slashes turned to dashes."""
    rel = os.path.relpath(os.path.join(ROOT, d), RUNS)
    return "rbt-129-" + rel.replace(os.sep, "-")


def lane_dirs(lanes: str) -> tuple:
    """(Stage-1 run directories, census source directories), in lane order, each once."""
    runs, sources = [], []
    for path in sorted(glob.glob(os.path.join(lanes, "*.jsonl"))):
        for line in open(path):
            if not line.strip():
                continue
            j = json.loads(line)
            if j["job"] in RUN_JOBS and j["dir"] not in runs:
                runs.append(j["dir"])
            src = j.get("ref") if j["job"] == "ksalt" else j.get("src") if j["job"] == "adopt" else None
            if src and src not in sources:
                sources.append(src)
    return runs, sources


def git(*a, **kw):
    return subprocess.run(["git", *a], cwd=ROOT, check=True, capture_output=True, **kw).stdout


def fetch(labels: list) -> set:
    """Fetch the branches that exist; returns their labels."""
    have = set()
    for line in git("ls-remote", REMOTE, "refs/heads/ckpt/rbt-129-*", text=True).splitlines():
        have.add(line.split("refs/heads/ckpt/", 1)[1])
    want = [x for x in labels if x in have]
    for i in range(0, len(want), 40):
        git("fetch", "-q", REMOTE, *[f"+refs/heads/ckpt/{x}:refs/remotes/{REMOTE}/ckpt/{x}" for x in want[i:i + 40]])
    return set(want)


def members(lab: str, names: tuple) -> dict:
    """The named files of the run directory in ``ckpt/<lab>``'s tarball (by base name, top level only)."""
    ref = f"{REMOTE}/ckpt/{lab}"
    top = git("show", f"{ref}:MANIFEST", text=True).splitlines()[0]
    parts = sorted(p for p in git("ls-tree", "--name-only", ref, text=True).split() if p.startswith("run.tar.gz.part"))
    blob = b"".join(git("cat-file", "blob", f"{ref}:{p}") for p in parts)
    out = {}
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for name in names:
            try:
                f = tar.extractfile(f"{top}/{name}")
            except KeyError:
                continue
            if f is not None:
                out[name] = f.read().decode()
    return out


def commands(text: str) -> list:
    """Each ecology command as ("fresh" | "resume", seasons target)."""
    out = []
    for line in (text or "").splitlines():
        if " ecology " not in f" {line} ":
            continue
        a = line.split()
        n = int(a[a.index("--seasons") + 1]) if "--seasons" in a else None
        out.append(("resume" if "--resume" in a else "fresh", n))
    return out


def classify(cmds: list) -> list:
    """Each resume as "killed" (same target as the command before it) or "planned" (a new target)."""
    kinds = []
    for (prev, pn), (kind, n) in zip(cmds, cmds[1:]):
        if kind == "resume":
            kinds.append("killed" if n == pn else "planned")
    return kinds


def written_twice(lab: str) -> dict:
    """lineage.jsonl and cohorts.jsonl, structurally: rows repeated byte for byte (one writer never repeats a row: a
    lineage row names one member in one season, a cohort row one cohort in one season), the seasons they fall in, steps
    back in the season column, and lines that are not JSON (a torn write anywhere but at the end).  Counts and season
    indices only; no field but the season is parsed."""
    got = members(lab, ("lineage.jsonl", "cohorts.jsonl"))
    out = {}
    for name, key in (("lineage.jsonl", "generation"), ("cohorts.jsonl", "season")):
        lines = [line for line in got.get(name, "").splitlines() if line.strip()]
        seasons, torn, seen, rep = [], 0, set(), set()
        for line in lines:
            try:
                g = json.loads(line)[key]
            except ValueError:
                torn += 1
                continue
            seasons.append(g)
            if line in seen:
                rep.add(g)
            seen.add(line)
        out[name] = {"repeated": len(lines) - len(set(lines)), "repeated_seasons": sorted(rep),
                     "steps_back": sum(1 for a, b in zip(seasons, seasons[1:]) if b < a), "torn": torn}
    return out


def double_written(rec: dict) -> bool:
    return any(v["repeated"] or v["steps_back"] or v["torn"] for v in rec.get("twice", {}).values())


def report(d: str, lab: str, got: set, sources: bool = False, check: bool = False) -> dict:
    rec = {"dir": d, "branch": f"ckpt/{lab}"}
    if lab not in got:
        rec["status"] = "no checkpoint"
        return rec
    files = members(lab, PROVENANCE)
    plat = json.loads(files["platform.json"]) if "platform.json" in files else {}
    cmds = commands(files.get("command.txt"))
    kinds = classify(cmds)
    rec.update(status="ok", seasons=json.loads(files["config.json"])["ecology"]["seasons"] if "config.json" in files else None,
               resumes=len(plat.get("resumes", [])), resume_utc=[r.get("written_utc") for r in plat.get("resumes", [])],
               commands=[f"{k} {n}" for k, n in cmds], killed=kinds.count("killed"), planned=kinds.count("planned"))
    if sources or check:
        rec["twice"] = written_twice(lab)
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--lanes", default=os.path.join(RUNS, "lanes", "1"))
    ap.add_argument("--sources", action="store_true", help="also the census directories adopted or compared against")
    ap.add_argument("--check-runs", action="store_true", help="also check every checkpointed Stage-1 run's lineage.jsonl and cohorts.jsonl"
                    " for a double write (structure only: repeated rows, their seasons, steps back, torn lines; no values)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    runs, srcs = lane_dirs(a.lanes)
    got = fetch([label(d) for d in runs + (srcs if a.sources else [])])
    rows = [report(d, label(d), got, check=a.check_runs) for d in runs]
    srows = [report(d, label(d), got, sources=True) for d in srcs] if a.sources else []
    if a.json:
        json.dump({"runs": rows, "sources": srows}, sys.stdout, indent=1)
        print()
        return 0
    for title, rs in (("Stage-1 run directories", rows), ("census sources", srows)):
        if not rs:
            continue
        ok = [r for r in rs if r["status"] == "ok"]
        hit = [r for r in ok if r["resumes"]]
        print(f"# {title}: {len(rs)} in the lanes, {len(ok)} with a checkpoint, {len(hit)} ever resumed"
              f" ({sum(1 for r in hit if r['killed'])} after a kill)")
        for r in hit:
            extra = "".join(f"; {n}: {v['repeated']} rows repeated (seasons {v['repeated_seasons'] or '-'}), {v['steps_back']} steps back,"
                            f" {v['torn']} torn" for n, v in r.get("twice", {}).items())
            print(f"{r['dir']}: resumes {r['resumes']} (killed {r['killed']}, planned {r['planned']}) at"
                  f" {', '.join(x or '?' for x in r['resume_utc'])}; commands: {'; '.join(r['commands'])}{extra}")
        checked = [r for r in ok if "twice" in r]
        bad = [r for r in checked if double_written(r)]
        if checked:
            print(f"# {len(checked)} checked for a double write ({sum(1 for r in checked if r['resumes'])} with a resume record,"
                  f" {sum(1 for r in checked if not r['resumes'])} without); {len(bad)} written twice: " + (", ".join(r["dir"] for r in bad) or "none"))
            for r in bad:
                if not r["resumes"]:
                    print(f"{r['dir']}: no resume record; " + "; ".join(f"{n}: {v['repeated']} rows repeated (seasons {v['repeated_seasons'] or '-'}),"
                                                                      f" {v['steps_back']} steps back, {v['torn']} torn" for n, v in r["twice"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
