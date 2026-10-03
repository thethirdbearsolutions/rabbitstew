"""RBT-129 continuations: run one ecology command on the instrumented MuJoCo, logging every EPA horizon overflow and
near miss to the run's own ``epa_overflow.jsonl`` (owner decision 2, option (c)).

    python runs/RBT-129/launch/epa_ecology.py <rabbitstew ecology arguments, --out DIR included>

``stages.run_lane`` runs every continuation job's ecology through this file instead of ``-m rabbitstew.cli``.  It:
  1. refuses (exit 9) unless this process runs the instrumented build (``mjbuild.check_instrumented``);
  2. points the library's log at ``DIR/epa_overflow.jsonl`` (``RBT_HZN_LOG``, near-miss threshold ``RBT_HZN_NEAR`` 17);
  3. records the build in ``platform.json``: every platform record this process writes (a fresh run's, or the entry a
     resume appends) carries ``mujoco_build`` (``mjbuild.identity()``);
  4. writes a ``{"start": ...}`` line at each start, and a ``{"season": s}`` line as each season begins, so the library's
     event lines (written by whichever process ran the bout) fall under the season they belong to;
  5. flushes each pool worker's horizon histogram when the worker exits;
then runs ``rabbitstew.cli`` in this process, unchanged.  Nothing here touches a simulated value: the season marker
and the platform record are written beside the run, and ``platform.json`` and the log are outside every byte
comparison (``stages.K1_SKIP``, ``EPA_SKIP``).

The log's lines (``read_log`` parses them):
  {"start": UTC, "unit", "attempt", "pid", "argv": [...], "build": BUILD_ID, "libmujoco_sha256"}   one per start
  {"season": s, "pid": ...}                                                                as season s begins
  {"event": "near"|"overflow", "unit", "attempt", "pid", "seq", "nedges": n, "cap": 24, "epa_iteration": k, "nverts",
   "nfaces", "geom1", "type1", "geom2", "type2", "step": mj_step within the bout, "time": bout time, "process_steps"}
                                                                                           EPA horizon >= 17, or > 24
  {"hist": {"n": count, ...}, "epa_iterations", "overflows", "process_steps", "unit", "attempt", "pid", "seq"}
                                                                                           a process's histogram
``unit`` is the run's checkpoint label (``unit_id``); ``attempt`` counts the run directory's earlier starts (0 first);
``seq`` numbers a process's lines from 1, so (attempt, pid, seq) orders an attempt's events.  The library writes an
overflow line before EPA reads the overflowed arrays, so a fault that follows leaves it (``attested``).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import mjbuild  # noqa: E402

if mjbuild.ROOT not in sys.path:  # rabbitstew from the checkout, as ``-m rabbitstew.cli`` run from the root finds it
    sys.path.insert(0, mjbuild.ROOT)

#: the pool's task functions (rabbitstew.evolution), wrapped so that a worker flushes its histogram when it exits
TASKS = ("_bout_task", "_group_task", "_persistent_group_task")


def _out_dir(argv: list) -> str:
    for i, a in enumerate(argv):
        if a == "--out" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--out="):
            return a.split("=", 1)[1]
    mjbuild._refuse("an instrumented ecology run needs --out: its EPA log goes beside the run", 4)


def _line(path: str, rec: dict) -> None:
    data = (json.dumps(rec) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)


def unit_id(out: str) -> str:
    """The run's id on every log line: its checkpoint label (``stages._label``: ``rbt-129-<path under runs/RBT-129>``,
    slashes as dashes), or for a directory outside runs/RBT-129 its absolute path."""
    runs = os.path.join(mjbuild.ROOT, "runs", "RBT-129")
    r = os.path.relpath(os.path.abspath(out), runs)
    return os.path.abspath(out) if r.startswith("..") else "rbt-129-" + r.replace(os.sep, "-")


def attempts(log: str) -> int:
    """The attempt number of a new start: how many starts the run's log already holds (0 for the first)."""
    if not os.path.exists(log):
        return 0
    n = 0
    for raw in open(log):
        try:
            n += "start" in json.loads(raw)
        except ValueError:
            pass
    return n


def install(out: str, ident: dict, argv: list) -> str:
    """Steps 2-5 of the module docstring, for a run in ``out``; returns the log's path."""
    import ctypes
    import multiprocessing.util

    from rabbitstew import ecology, evolution, provenance

    os.makedirs(out, exist_ok=True)
    log = os.path.abspath(os.path.join(out, mjbuild.EPA_LOG))
    unit, attempt = unit_id(out), attempts(log)
    os.environ["RBT_HZN_LOG"] = log
    os.environ["RBT_HZN_NEAR"] = str(mjbuild.NEAR)
    os.environ["RBT_HZN_UNIT"] = unit
    os.environ["RBT_HZN_ATTEMPT"] = str(attempt)
    _line(log, {"start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "unit": unit, "attempt": attempt,
                "pid": os.getpid(), "argv": argv, "build": ident["build_id"], "libmujoco_sha256": ident["libmujoco_sha256"]})

    record = provenance.platform_record
    if not getattr(record, "_rbt129", False):
        def platform_record():
            return {**record(), "mujoco_build": dict(ident)}
        platform_record._rbt129 = True
        provenance.platform_record = platform_record

    step = ecology.Ecology.step
    if not getattr(step, "_rbt129", False):
        def season_step(self):
            _line(log, {"season": self.season, "pid": os.getpid()})
            return step(self)
        season_step._rbt129 = True
        ecology.Ecology.step = season_step

    flush = getattr(ctypes.CDLL(ident["libmujoco_path"]), "rbt_hzn_flush", None)  # None only off the build (tests)
    if flush is not None:
        flush.restype = ctypes.c_longlong
    main, registered = os.getpid(), set()

    def wrap(name):
        task = getattr(evolution, name)

        def run(args):
            pid = os.getpid()
            if flush is not None and pid != main and pid not in registered:  # a forked worker: flush as it exits
                registered.add(pid)
                multiprocessing.util.Finalize(None, flush, exitpriority=100)
            return task(args)
        run.__module__, run.__qualname__, run.__name__ = task.__module__, task.__qualname__, task.__name__
        run._rbt129 = True
        return run

    for name in TASKS:
        if not getattr(getattr(evolution, name), "_rbt129", False):
            setattr(evolution, name, wrap(name))
    return log


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ident = mjbuild.check_instrumented()
    install(_out_dir(argv), ident, argv)
    from rabbitstew import cli

    return cli.main(["ecology", *argv])


# -- reading a log ------------------------------------------------------------------------------------------------- #

def overflow_records(path: str) -> list:
    """Every overflow line of a log, in file order (each carries unit, attempt, pid, seq, step)."""
    out = []
    if os.path.exists(path):
        for raw in open(path):
            try:
                rec = json.loads(raw)
            except ValueError:
                continue
            if rec.get("event") == "overflow":
                out.append(rec)
    return out


def attested(path: str, unit: str, attempt: int) -> bool:
    """The crash attestation (OVERFLOW-RULE 4.2; the Stage-2 plan's definition): the log holds an overflow line of this
    unit and this attempt.  The library writes it before the read that can fault, so a crash leaves it; ordering against
    the abnormal exit is the attempt's: every line of an attempt precedes that attempt's exit."""
    return any(r.get("unit") == unit and r.get("attempt") == attempt for r in overflow_records(path))


def read_log(path: str) -> dict:
    """A run's EPA log, by season.  A season run more than once (a killed run resumed: ``--resume`` cuts the run back
    to its last saved season and runs the rest again) counts from its LAST attempt only.  Events before any season
    line of their attempt (model setup) are kept under season None.  Returns
    ``{"starts": n, "seasons": {season: {"near": [...], "overflow": [...]}}, "near": n, "overflow": n,
    "max_nedges": n or None, "hist": {n: count}, "epa_iterations": n, "hist_lines": n, "bad_lines": n}``; the histogram
    sums every ``hist`` line written (a re-run season counted twice; a killed process's never written)."""
    attempts, cur, season, bad = [], None, None, 0
    hist, iters, hist_lines = {}, 0, 0
    if os.path.exists(path):
        for raw in open(path):
            try:
                rec = json.loads(raw)
            except ValueError:
                bad += 1  # a line cut by a kill mid-write
                continue
            if "start" in rec:
                cur, season = {}, None
                attempts.append(cur)
            elif "season" in rec and "event" not in rec:
                season = rec["season"]
                if cur is not None:
                    cur.setdefault(season, {"near": [], "overflow": []})
            elif "event" in rec:
                if cur is None:
                    cur = {}
                    attempts.append(cur)
                cur.setdefault(season, {"near": [], "overflow": []})[rec["event"]].append(rec)
            elif "hist" in rec:
                hist_lines += 1
                iters += rec.get("epa_iterations", 0)
                for k, v in rec["hist"].items():
                    hist[int(k)] = hist.get(int(k), 0) + v
    seasons = {}
    for a in attempts:  # later attempts replace earlier ones season by season
        seasons.update(a)
    near = sum(len(v["near"]) for v in seasons.values())
    over = sum(len(v["overflow"]) for v in seasons.values())
    sizes = [e["nedges"] for v in seasons.values() for k in ("near", "overflow") for e in v[k]]
    top = max([n for n in hist if hist[n]] + sizes, default=None)
    return {"starts": len(attempts), "seasons": seasons, "near": near, "overflow": over, "max_nedges": top,
            "hist": hist, "epa_iterations": iters, "hist_lines": hist_lines, "bad_lines": bad}


if __name__ == "__main__":
    sys.exit(main())
