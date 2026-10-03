"""RBT-131 audit, step 1: every ckpt/* snapshot on the remote, final/ against state.json.

    python runs/RBT-131/sweep_checkpoints.py [LABEL ...] > runs/RBT-131/sweep_checkpoints.txt

For each checkpoint branch (scripts/durable.sh's snapshots), fetch it into a throwaway bare repository, list the
tarball, count ``<kind>/final/NNN.json`` per kind, read ``state.json``'s living population per kind and the
config's resume record (``platform.json`` resumes, if any), per run directory (an arena snapshot nests several; an arena
run's population is its ``population_size``, since its state.json keeps no member list).  A row whose final/ holds more files than the state's
population is a snapshot where final/ carries dead members.  Reads only; nothing is run.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

REMOTE = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True).stdout.strip()
MEMBER = re.compile(r"^(.+)/([^/]+)/final/(\d+)\.json$")


def branches():
    out = subprocess.run(["git", "ls-remote", "origin", "refs/heads/ckpt/*"], capture_output=True, text=True, check=True).stdout
    return sorted(l.split()[1][len("refs/heads/"):] for l in out.splitlines())


def one(branch):
    tmp = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "init", "-q", "--bare", tmp], check=True)
        subprocess.run(["git", "-C", tmp, "fetch", "-q", "--depth", "1", REMOTE, f"+refs/heads/{branch}:refs/heads/x"], check=True)
        names = subprocess.run(["git", "-C", tmp, "ls-tree", "--name-only", "x"], capture_output=True, text=True, check=True).stdout.split()
        manifest = subprocess.run(["git", "-C", tmp, "show", "x:MANIFEST"], capture_output=True, text=True).stdout.splitlines()
        blob = b"".join(subprocess.run(["git", "-C", tmp, "cat-file", "blob", f"x:{p}"], capture_output=True, check=True).stdout
                        for p in sorted(n for n in names if n.startswith("run.tar.gz.part")))
    finally:
        shutil.rmtree(tmp)
    return rows_of(branch, manifest, blob)


def rows_of(branch, manifest, blob):
    """One row per run directory in the snapshot (an arena checkpoint can nest several: ``B1/1/C/...``)."""
    runs = {}  # run dir -> {"final": {kind: n}, "state": ..., "config": ..., "platform": ...}
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for m in tar.getmembers():
            hit = MEMBER.match(m.name)
            if hit:
                r = runs.setdefault(hit.group(1), {})
                r.setdefault("final", {})[hit.group(2)] = r.get("final", {}).get(hit.group(2), 0) + 1
                continue
            base = os.path.basename(m.name)
            if base in ("state.json", "config.json", "platform.json") and m.isfile():
                runs.setdefault(os.path.dirname(m.name), {})[base] = json.load(tar.extractfile(m))
    out = []
    for d, r in sorted(runs.items()):
        if "final" not in r and "state.json" not in r:
            continue
        cfg, state, plat = r.get("config.json") or {}, r.get("state.json"), r.get("platform.json")
        eco = "ecology" in cfg
        living = {}
        if state is not None and eco:
            living = {k: len(v) for k, v in state.get("populations", {}).items()}
        elif cfg:  # an arena run: its population is population_size in every generation (state.json keeps no member list)
            living = {k: int(cfg.get("population_size", 0)) for k in r.get("final", {})}
        final = r.get("final", {})
        resumes = len(plat["resumes"]) if isinstance(plat, dict) and isinstance(plat.get("resumes"), list) else None
        out.append({"branch": branch, "run": d, "progress": manifest[1] if len(manifest) > 1 else "?", "ecology": eco,
                    "final": final, "living": living, "resumes": resumes,
                    "stale": {k: final[k] - living.get(k, 0) for k in final if final[k] != living.get(k, 0)}})
    return out


def main():
    rows = []
    for b in (["ckpt/" + x for x in sys.argv[1:]] or branches()):
        try:
            rs = one(b)
        except Exception as e:  # noqa: BLE001 -- a broken snapshot is reported, not fatal
            rs = [{"branch": b, "error": repr(e)}]
        for r in rs:
            rows.append(r)
            print(json.dumps(r), flush=True)
    bad = [r for r in rows if r.get("stale")]
    print(f"# {len({r['branch'] for r in rows})} checkpoints, {len(rows)} run directories; {sum(1 for r in rows if 'error' in r)} unreadable; "
          f"{sum(1 for r in rows if r.get('final'))} with a final/; {len(bad)} whose final/ differs from state.json's population")
    for r in bad:
        print(f"# STALE {r['branch']} {r.get('run')}: final {r['final']} living {r['living']}")


if __name__ == "__main__":
    main()
