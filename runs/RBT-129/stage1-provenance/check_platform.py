#!/usr/bin/env python3
"""RBT-129 Stage-1 MuJoCo provenance check (crash ruling, runs/RBT-129/mn-crash/RULING.md item 7).

Reads ONLY each run's platform.json.  For every in-scope ckpt branch, one at a time:
  - fetch it --depth=1 into a throwaway bare repository;
  - concatenate its run.tar.gz.part* blobs in sorted order, in memory, as scripts/durable.sh restore does;
  - walk the tar stream by member NAME only; extractfile() is called on the shallowest member whose name ends in
    platform.json and on nothing else; no member name is printed or stored;
  - delete the throwaway repository.
Never reads MANIFEST, never writes a tarball to disk.

In scope: ckpt/rbt-129-stage1-* minus -record, -unit and the quarantined branch (which is never fetched), plus
ckpt/rbt-129-stage0-*-129001-S for each Stage-1 point (the adopted census runs).

Two outputs (coordinator no-peek ruling, 2026-10-02):
  RAW_TSV     every scanned branch, every field.  SEALED for the readout's integrity section: write it OUTSIDE the
              repository; never commit or push it.
  PUBLIC_TSV  what the PR carries.  No -ckpt60 row (which of those copies lacks platform.json is sealed), and the
              resumes column reduced to whether every resume entry is at REQUIRED, so the number of resumes per run
              is not published.

Usage: check_platform.py SCRATCH_DIR RAW_TSV PUBLIC_TSV
       check_platform.py --redact RAW_TSV PUBLIC_TSV      (rebuild the public table from a raw one, no fetch)
"""

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile

REQUIRED = "3.14.0"
QUARANTINE = "rbt-129-stage1-c2-p030-U-G-129001-M"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def git(*args, cwd=None, binary=False):
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=True)
    return out.stdout if binary else out.stdout.decode()


def labels():
    url = git("remote", "get-url", "origin", cwd=REPO).strip()
    refs = [l.split("\t")[1] for l in git("ls-remote", url, "refs/heads/ckpt/rbt-129-stage*", cwd=REPO).splitlines()]
    names = sorted(r[len("refs/heads/ckpt/"):] for r in refs)
    s1 = [n for n in names if n.startswith("rbt-129-stage1-") and not n.endswith("-record") and "-unit" not in n
          and n != QUARANTINE]
    points = sorted({re.match(r"rbt-129-stage1-(.+?)-1290\d\d-", n).group(1) for n in s1})
    s0 = [n for n in names if n.startswith("rbt-129-stage0-") and n.endswith("-129001-S")]
    s0 = [n for n in s0 if re.match(r"rbt-129-stage0-(.+)-129001-S$", n).group(1) in points]
    expected_s0 = {"rbt-129-stage0-%s-129001-S" % p for p in points}
    return url, s1, s0, sorted(expected_s0 - set(s0)), points


def platform_of(url, label, scratch):
    """The parsed platform.json of one branch, or a string saying why there is none."""
    assert label != QUARANTINE
    repo = os.path.join(scratch, "fetch")
    shutil.rmtree(repo, ignore_errors=True)
    try:
        git("init", "-q", "--bare", repo)
        git("fetch", "-q", "--depth=1", url, "refs/heads/ckpt/%s:refs/heads/x" % label, cwd=repo)
        parts = sorted(n for n in git("ls-tree", "--name-only", "x", cwd=repo).splitlines()
                       if n.startswith("run.tar.gz.part"))
        if not parts:
            return "NO-PARTS"
        blob = b"".join(git("cat-file", "blob", "x:" + p, cwd=repo, binary=True) for p in parts)
    finally:
        shutil.rmtree(repo, ignore_errors=True)
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        cands = []
        for m in tf.getmembers():  # names only; no content is read here
            n = m.name[2:] if m.name.startswith("./") else m.name
            if m.isfile() and (n == "platform.json" or n.endswith("/platform.json")):
                cands.append((n.count("/"), m))
        if not cands:
            return "MISSING"
        cands.sort(key=lambda c: c[0])
        if len(cands) > 1 and cands[0][0] == cands[1][0]:
            return "AMBIGUOUS"
        rec = json.load(tf.extractfile(cands[0][1]))
        return rec, len(cands)


def redact(raw, public):
    """The public table: no -ckpt60 rows; resumes reduced to "all REQUIRED" or the offending versions."""
    with open(raw) as f, open(public, "w") as g:
        g.write("branch\tmujoco\tresumes_mujoco\tnumpy\tpython\tsha\n")
        for line in list(f)[1:]:
            b, mj, res, npv, py, sha = line.rstrip("\n").split("\t")
            if b.endswith("-ckpt60"):
                continue
            if mj not in ("MISSING", "NO-PARTS", "AMBIGUOUS"):
                odd = sorted({v for v in res.split(",") if v and v != REQUIRED})
                res = ("not " + REQUIRED + ": " + ",".join(odd)) if odd else "all " + REQUIRED
            g.write("\t".join((b, mj, res, npv, py, sha)) + "\n")


def main():
    if sys.argv[1] == "--redact":
        return redact(sys.argv[2], sys.argv[3])
    scratch, raw, public = sys.argv[1], sys.argv[2], sys.argv[3]
    assert not os.path.abspath(raw).startswith(REPO + os.sep), "the raw table is sealed: write it outside the repository"
    url, s1, s0, missing_s0, points = labels()
    print("points=%d stage1=%d stage0=%d missing_stage0=%s" % (len(points), len(s1), len(s0), missing_s0))
    with open(raw, "w") as f:
        f.write("branch\tmujoco\tresumes_mujoco\tnumpy\tpython\tsha\n")
        for label in s1 + s0:
            r = platform_of(url, label, scratch)
            if isinstance(r, str):
                f.write("%s\t%s\t\t\t\t\n" % (label, r))
                continue
            rec, n = r
            res = [str(x.get("mujoco")) for x in rec.get("resumes", [])]
            f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (label, rec.get("mujoco"), ",".join(res), rec.get("numpy"),
                                                  rec.get("python"), rec.get("git_sha")))
            f.flush()
    redact(raw, public)
    print("done; raw (sealed) and public tables written")  # no per-branch output: the raw table is sealed


if __name__ == "__main__":
    main()
