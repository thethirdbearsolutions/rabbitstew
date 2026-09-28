"""RBT-131 audit, step 1: every ckpt/* snapshot on the remote, final/ against state.json.

    python runs/RBT-131/sweep_checkpoints.py > runs/RBT-131/sweep_checkpoints.txt

For each checkpoint branch (scripts/durable.sh's snapshots), fetch it into a throwaway bare repository, list the
tarball, count ``<kind>/final/NNN.json`` per kind, read ``state.json``'s living population per kind and the
config's resume record (``platform.json`` resumes, if any).  A row whose final/ holds more files than the state's
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
MEMBER = re.compile(r"^[^/]+/([^/]+)/final/(\d+)\.json$")


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
    final, state, config, plat = {}, None, None, None
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for m in tar.getmembers():
            hit = MEMBER.match(m.name)
            if hit:
                final[hit.group(1)] = final.get(hit.group(1), 0) + 1
            elif re.match(r"^[^/]+/state\.json$", m.name):
                state = json.load(tar.extractfile(m))
            elif re.match(r"^[^/]+/config\.json$", m.name):
                config = json.load(tar.extractfile(m))
            elif re.match(r"^[^/]+/platform\.json$", m.name):
                plat = json.load(tar.extractfile(m))
    living = {}
    if state is not None:
        for k, v in state.get("populations", {}).items():
            living[k] = len(v["members"] if isinstance(v, dict) else v)
    eco = (config or {}).get("ecology")
    resumes = len(plat.get("resumes", [])) if isinstance(plat, dict) and isinstance(plat.get("resumes"), list) else None
    return {"branch": branch, "progress": manifest[1] if len(manifest) > 1 else "?", "ecology": eco is not None,
            "final": final, "living": living, "resumes": resumes,
            "stale": {k: final[k] - living.get(k, 0) for k in final if final[k] != living.get(k, 0)}}


def main():
    rows = []
    for b in branches():
        try:
            r = one(b)
        except Exception as e:  # noqa: BLE001 -- a broken snapshot is reported, not fatal
            r = {"branch": b, "error": repr(e)}
        rows.append(r)
        print(json.dumps(r), flush=True)
    bad = [r for r in rows if r.get("stale")]
    print(f"# {len(rows)} checkpoints; {sum(1 for r in rows if 'error' in r)} unreadable; "
          f"{sum(1 for r in rows if r.get('final'))} with a final/; {len(bad)} whose final/ differs from state.json's population")
    for r in bad:
        print(f"# STALE {r['branch']}: final {r['final']} living {r['living']}")


if __name__ == "__main__":
    main()
