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
  5. flushes each forked pool worker's horizon histogram when the worker exits;
  6. records the exit codes of a broken pool's workers (``pool_broken``), for run-lane's ``exit`` line;
then runs ``rabbitstew.cli`` in this process, unchanged.  Nothing here touches a simulated value: the season marker
and the platform record are written beside the run, and ``platform.json`` and the log are outside every byte
comparison (``stages.K1_SKIP``, ``EPA_SKIP``).

The log's lines (``read_log`` parses them):
  {"start": UTC, "unit", "attempt", "workers", "pid", "argv", "build": BUILD_ID, "libmujoco_sha256",
   "bindings_sha256", "python"}                                                            one per start
  {"season": s, "pid": ...}                                                                as season s begins
  {"event": "near"|"overflow", "unit", "attempt", "pid", "seq", "nedges": n, "cap": 24, "epa_iteration": k, "nverts",
   "nfaces", "geom1", "type1", "geom2", "type2", "step": mj_step within the bout, "time": bout time, "process_steps"}
                                                                                           EPA horizon >= 17, or > 24
  {"hist": {"n": count, ...}, "epa_iterations", "overflows", "process_steps", "unit", "attempt", "pid", "seq"}
                                                                                           a process's histogram
  {"pool_broken": {"attempt", "workers": {pid: exitcode}}, "pid"}                          a pool worker died
  {"exit": {"attempt", "code", "signal", "native"}}            run-lane, after the attempt's process exits (write_exit)
  {"exit": {"attempt": null, "nostart": true, ...}}           the same, for a process that died before its start line
``unit`` is the run's checkpoint label (``unit_id``); ``attempt`` is 1 + the run directory's earlier starts;
``seq`` numbers a process's lines from 1, so (attempt, pid, seq) orders an attempt's events.  The library writes an
overflow line before EPA reads the overflowed arrays, so a fault that follows leaves it (``attested``); if it cannot
write that line whole, it aborts (fail closed: an unattested crash).  A run directory that ``stages._fresh`` deletes
keeps its log beside it as ``epa_overflow.jsonl.prev-<n>``; every reader here reads those first (``log_files``).
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

#: signals that make an attempt's exit NATIVE (a fault inside native code), for the ``exit`` line
NATIVE_SIGNALS = (4, 6, 7, 8, 11)  # SIGILL, SIGABRT, SIGBUS, SIGFPE, SIGSEGV


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


class _Holder(list):
    """A list that can be weakly referenced (register_after_fork keeps a weak reference to its object)."""


#: the library's flush, held here for the forked workers
_FLUSHER = _Holder()


def _arm_flush(_obj) -> None:
    import multiprocessing.util

    multiprocessing.util.Finalize(None, _FLUSHER[0], exitpriority=100)


def unit_id(out: str) -> str:
    """The run's id on every log line: its checkpoint label (``stages._label``: ``rbt-129-<path under runs/RBT-129>``,
    slashes as dashes), or for a directory outside runs/RBT-129 its absolute path."""
    runs = os.path.join(mjbuild.ROOT, "runs", "RBT-129")
    r = os.path.relpath(os.path.abspath(out), runs)
    return os.path.abspath(out) if r.startswith("..") else "rbt-129-" + r.replace(os.sep, "-")


#: a run's earlier logs, kept across ``stages._fresh``'s delete of a run that never finished a season (MINOR 10)
PREV = ".prev-"


def log_files(log: str) -> list:
    """The log and its kept predecessors, oldest first: ``<log>.prev-1``, ``.prev-2``, ..., then ``<log>``."""
    d, name = os.path.split(log)
    prev = []
    if os.path.isdir(d or "."):
        for n in os.listdir(d or "."):
            if n.startswith(name + PREV) and n[len(name + PREV):].isdigit():
                prev.append((int(n[len(name + PREV):]), os.path.join(d, n)))
    return [p for _, p in sorted(prev)] + ([log] if os.path.exists(log) else [])


def keep_log(run_dir: str):
    """Before a run directory is deleted: move its log out of the way; returns a function that puts it back (as the next
    ``.prev-<n>``, with any earlier ones) once the directory is re-created."""
    log = os.path.join(run_dir, mjbuild.EPA_LOG)
    files = log_files(log)
    if not files:
        return lambda: None
    import tempfile
    tmp = tempfile.mkdtemp(prefix="rbt129-epa-")
    moved = []
    for i, f in enumerate(files, 1):
        dst = os.path.join(tmp, f"{mjbuild.EPA_LOG}{PREV}{i}")
        os.replace(f, dst) if os.stat(f).st_dev == os.stat(tmp).st_dev else _copy_remove(f, dst)
        moved.append(dst)

    def restore():
        os.makedirs(run_dir, exist_ok=True)
        for f in moved:
            _copy_remove(f, os.path.join(run_dir, os.path.basename(f)))
        os.rmdir(tmp)
    return restore


def _copy_remove(src: str, dst: str) -> None:
    import shutil
    shutil.copy2(src, dst)
    os.remove(src)


def _lines(log: str):
    """(raw text, parsed record or None) for every line of the log and its predecessors, oldest first."""
    for f in log_files(log):
        for raw in open(f):
            try:
                yield raw, json.loads(raw)
            except ValueError:
                yield raw, None  # a line cut by a kill mid-write


def _records(log: str):
    for _, rec in _lines(log):
        if rec is not None:
            yield rec


def starts(log: str) -> int:
    """How many start lines the log (and its predecessors) holds."""
    return sum(1 for r in _records(log) if "start" in r)


def attempts(log: str) -> int:
    """The attempt number of a new start: 1 + how many starts the run's log already holds (1 for the first; each
    restart or resume of the run directory adds 1).  A container lost before its last snapshot loses that attempt's
    lines with it, so the number is reused by the next start, and no surviving line is ambiguous."""
    return 1 + starts(log)


def current_attempt(log: str):
    """The attempt of the log's latest start line (None if there is none)."""
    last = None
    for r in _records(log):
        if "start" in r:
            last = r.get("attempt")
    return last


def write_exit(run_dir: str, code: int, nostart: bool = False) -> dict:
    """``run-lane``'s line after a continuation's ecology process exits (the Stage-2 plan's fault marker):
    ``{"exit": {"attempt", "code", "signal", "native"}}``.  ``native`` is true when the process died on SIGILL, SIGABRT,
    SIGBUS, SIGFPE or SIGSEGV, or exited non-zero after a pool worker of the same attempt did (the wrapper's
    ``pool_broken`` line).  With ``nostart`` (run-lane counted no new start line: the process died before ``install``),
    the line is ``{"exit": {"attempt": null, "nostart": true, ...}}``, never booked to an earlier attempt; readers take
    it as HELP (MINOR 7).  No season, time or run.log content."""
    log = os.path.join(run_dir, mjbuild.EPA_LOG)
    attempt = None if nostart else current_attempt(log)
    sig = -code if code < 0 else None
    native = sig in NATIVE_SIGNALS
    if not native and code != 0:
        for r in _records(log):
            pb = r.get("pool_broken")
            if pb and pb.get("attempt") == attempt and any(c is not None and c < 0 and -c in NATIVE_SIGNALS
                                                           for c in pb.get("workers", {}).values()):
                native = True
    rec = {"exit": {"attempt": attempt, "code": code, "signal": sig, "native": native}}
    if nostart:
        rec["exit"]["nostart"] = True
    if os.path.isdir(run_dir):
        _line(log, rec)
    return rec


def install(out: str, ident: dict, argv: list) -> str:
    """Steps 2-5 of the module docstring, for a run in ``out``; returns the log's path."""
    import ctypes
    import multiprocessing.util

    from rabbitstew import ecology, provenance

    os.makedirs(out, exist_ok=True)
    log = os.path.abspath(os.path.join(out, mjbuild.EPA_LOG))
    unit, attempt = unit_id(out), attempts(log)
    if len(unit) >= mjbuild.UNIT_MAX:  # the library keeps 127 characters; a longer id could never attest (NOTE 18)
        mjbuild._refuse(f"the run id {unit!r} is {len(unit)} characters; the build's log keeps {mjbuild.UNIT_MAX - 1}", 4)
    workers = next((argv[i + 1] for i, a in enumerate(argv[:-1]) if a == "--workers"), None)
    os.environ["RBT_HZN_LOG"] = log
    os.environ["RBT_HZN_NEAR"] = str(mjbuild.NEAR)
    os.environ["RBT_HZN_UNIT"] = unit
    os.environ["RBT_HZN_ATTEMPT"] = str(attempt)
    _line(log, {"start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "unit": unit, "attempt": attempt,
                "workers": int(workers) if workers and workers.isdigit() else workers, "pid": os.getpid(), "argv": argv,
                "build": ident["build_id"], "libmujoco_sha256": ident["libmujoco_sha256"],
                "bindings_sha256": ident.get("bindings_sha256"), "python": sys.version})

    # a pool worker that dies breaks the pool: record each worker's exit code (negative: the signal) while the pool
    # still knows it, so the attempt's exit line can say whether a worker died natively (CPython 3.11's
    # _ExecutorManagerThread.terminate_broken; if a later CPython lacks it, no line is written and the exit line's
    # ``native`` rests on the parent's own signal alone)
    import concurrent.futures.process as cfp

    broken = getattr(getattr(cfp, "_ExecutorManagerThread", None), "terminate_broken", None)
    if broken is not None and not getattr(broken, "_rbt129", False):
        def terminate_broken(self, cause):
            codes = {str(p.pid): p.exitcode for p in list((getattr(self, "processes", None) or {}).values())}
            _line(log, {"pool_broken": {"attempt": attempt, "workers": codes}, "pid": os.getpid()})
            return broken(self, cause)
        terminate_broken._rbt129 = True
        cfp._ExecutorManagerThread.terminate_broken = terminate_broken

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
    if flush is not None and not _FLUSHER:
        flush.restype = ctypes.c_longlong
        _FLUSHER.append(flush)
        # every process multiprocessing forks from here (the ecology's pool workers) flushes its histogram as it exits:
        # workers leave through os._exit, which skips the library's destructor, but runs multiprocessing's finalizers
        multiprocessing.util.register_after_fork(_FLUSHER, _arm_flush)
    return log


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ident = mjbuild.check_instrumented()
    install(_out_dir(argv), ident, argv)
    from rabbitstew import cli

    return cli.main(["ecology", *argv])


# -- reading a log ------------------------------------------------------------------------------------------------- #

def overflow_records(path: str) -> list:
    """Every overflow line of a log (and its predecessors), in file order (each carries unit, attempt, pid, seq, step)."""
    return [r for r in _records(path) if r.get("event") == "overflow"]


def overflow_before_exit(path: str, unit: str, attempt: int) -> bool:
    """An overflow line of this unit and attempt, logged before that attempt's exit line where it has one (the r1
    test, kept for readers; ``attested`` is the rule's)."""
    for r in _records(path):
        if r.get("event") == "overflow" and r.get("unit") == unit and r.get("attempt") == attempt:
            return True
        ex = r.get("exit")
        if ex and ex.get("attempt") == attempt:
            return False
    return False


def native_exit(path: str, attempt: int):
    """The attempt's exit line's ``native`` (True / False), or None when the log has no exit line for it."""
    out = None
    for r in _records(path):
        ex = r.get("exit")
        if ex and ex.get("attempt") == attempt:
            out = bool(ex.get("native"))
    return out


def attested(path: str, unit: str, attempt: int) -> bool:
    """The crash attestation of one attempt (OVERFLOW-RULE r2 4.2, the adversary's W6; ``native_exit`` folded in,
    MINOR 5): the attempt's exit line says ``native``, and an overflow line of this unit and attempt was written by a
    process that died natively in it (a ``pool_broken`` worker with a fatal signal, or the attempt's own pid when its
    exit carries a fatal signal), after the attempt's last season line and before its exit line.  An overflow the run
    survived seasons earlier does not attest a later fault."""
    recs = list(_records(path))
    start_pid = next((r.get("pid") for r in recs if "start" in r and r.get("attempt") == attempt), None)
    exits = [r["exit"] for r in recs if "exit" in r and r["exit"].get("attempt") == attempt]
    if not exits or not exits[-1].get("native"):
        return False
    fatal = {int(p) for r in recs if "pool_broken" in r and r["pool_broken"].get("attempt") == attempt
             for p, c in r["pool_broken"].get("workers", {}).items() if c is not None and c < 0 and -c in NATIVE_SIGNALS}
    if exits[-1].get("signal") in NATIVE_SIGNALS and start_pid is not None:
        fatal.add(start_pid)
    last_season, cands, done = -1, [], False
    for i, r in enumerate(recs):
        if "season" in r and "event" not in r and r.get("pid") == start_pid and not done:
            last_season = i
        if r.get("event") == "overflow" and r.get("unit") == unit and r.get("attempt") == attempt and not done:
            cands.append((i, r.get("pid")))
        if "exit" in r and r["exit"].get("attempt") == attempt:
            done = True
    return any(i > last_season and pid in fatal for i, pid in cands)


def crash_state(path: str, unit: str):
    """RULING item 5's count, from the log: the run's last two attempts with exit lines are consecutive, both native,
    and one ran at ``workers`` 1.  None, or ``{"attempts": (a, b), "attested": both attested}``."""
    recs = list(_records(path))
    workers = {r.get("attempt"): r.get("workers") for r in recs if "start" in r}
    exits = [r["exit"] for r in recs if "exit" in r and r["exit"].get("attempt") is not None]
    if len(exits) < 2:
        return None
    a, b = exits[-2], exits[-1]
    if not (a.get("native") and b.get("native") and b["attempt"] == a["attempt"] + 1):
        return None
    if 1 not in (workers.get(a["attempt"]), workers.get(b["attempt"])):
        return None
    return {"attempts": (a["attempt"], b["attempt"]),
            "attested": attested(path, unit, a["attempt"]) and attested(path, unit, b["attempt"])}


def _sig(e: dict) -> tuple:
    """An event's identity across attempts: a season re-run after a kill repeats it exactly (the build is deterministic)."""
    return tuple(e.get(k) for k in ("event", "nedges", "epa_iteration", "nverts", "nfaces", "geom1", "geom2", "step",
                                    "time"))


def read_log(path: str) -> dict:
    """A run's EPA log (with its kept predecessors), by season.  A season's events are the UNION over every attempt that
    ran it (MINOR 11: an overflow once logged is never un-seen), a re-run's repeat of the same event counted once.
    Events before any season line of their attempt are kept under season None.  ``unlogged`` lists why the log cannot
    vouch for the run (OVERFLOW-RULE r2 W7, MINOR 9): a process whose histogram ``overflows`` differs from its overflow
    lines, an unreadable line that is not the last of its attempt, an exit line with no start line (``nostart``).
    Returns ``{"starts", "seasons": {season: {"near": [...], "overflow": [...]}}, "near", "overflow", "max_nedges",
    "hist", "epa_iterations", "hist_lines", "bad_lines", "unlogged": [...]}``."""
    seasons, seen, season, bad, unlogged = {}, set(), None, 0, []
    hist, iters, hist_lines, starts_n = {}, 0, 0, 0
    per_pid_lines, per_pid_hist = {}, {}
    pending_bad = False
    for raw, rec in _lines(path):
        if rec is None:
            bad += 1
            if pending_bad:
                unlogged.append("an unreadable line in mid-attempt")
            pending_bad = True
            continue
        if pending_bad and "start" not in rec:
            unlogged.append("an unreadable line in mid-attempt")
        pending_bad = False
        if "start" in rec:
            starts_n += 1
            season = None
        elif "season" in rec and "event" not in rec:
            season = rec["season"]
            seasons.setdefault(season, {"near": [], "overflow": []})
        elif "event" in rec:
            if rec["event"] == "overflow":
                key = (rec.get("attempt"), rec.get("pid"))
                per_pid_lines[key] = per_pid_lines.get(key, 0) + 1
            sig = (season,) + _sig(rec)
            if sig not in seen:
                seen.add(sig)
                seasons.setdefault(season, {"near": [], "overflow": []})[rec["event"]].append(rec)
        elif "hist" in rec:
            hist_lines += 1
            iters += rec.get("epa_iterations", 0)
            key = (rec.get("attempt"), rec.get("pid"))
            per_pid_hist[key] = per_pid_hist.get(key, 0) + rec.get("overflows", 0)
            for k, v in rec["hist"].items():
                hist[int(k)] = hist.get(int(k), 0) + v
        elif "exit" in rec and rec["exit"].get("nostart"):
            unlogged.append("an exit with no start line (nostart)")
    for key, n in per_pid_hist.items():
        if n != per_pid_lines.get(key, 0):
            unlogged.append(f"histogram overflows {n} but {per_pid_lines.get(key, 0)} overflow lines (attempt {key[0]})")
    near = sum(len(v["near"]) for v in seasons.values())
    over = sum(len(v["overflow"]) for v in seasons.values())
    sizes = [e["nedges"] for v in seasons.values() for k in ("near", "overflow") for e in v[k]]
    top = max([n for n in hist if hist[n]] + sizes, default=None)
    return {"starts": starts_n, "seasons": seasons, "near": near, "overflow": over, "max_nedges": top, "hist": hist,
            "epa_iterations": iters, "hist_lines": hist_lines, "bad_lines": bad, "unlogged": unlogged}


if __name__ == "__main__":
    sys.exit(main())
