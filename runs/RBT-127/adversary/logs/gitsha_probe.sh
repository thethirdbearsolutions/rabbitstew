#!/usr/bin/env bash
# RBT-127 adversary: where does provenance._git() get its sha?  Run from the scratch dir; $VENV is a venv
# with numpy+mujoco and PR #411 installed editable; $PR is a checkout of 4a3ce85.
set -x
OTHER=$(mktemp -d); git -C $OTHER init -q; git -C $OTHER -c user.email=a@b -c user.name=x commit -q --allow-empty -m other
git -C $OTHER rev-parse HEAD
python3 -m venv $OTHER/venv; $OTHER/venv/bin/pip install -q --no-deps $PR
SP=$($VENV/bin/python -c 'import numpy,os;print(os.path.dirname(os.path.dirname(numpy.__file__)))')
# A: non-editable install into a venv inside an unrelated git checkout  -> that checkout's sha
cd / && $OTHER/venv/bin/python -c "import sys; sys.path.append('$SP'); import rabbitstew.provenance as m; r=m.platform_record(); print('A', r['git_sha'], r['git_dirty'])"
# C: no git on PATH -> None
cd / && PATH=/nonexistent $VENV/bin/python -c "from rabbitstew.provenance import platform_record as p; r=p(); print('C', r['git_sha'], r['git_dirty'])"
# D: GIT_DIR inherited from the environment -> the other repo's sha
cd / && GIT_DIR=$OTHER/.git $VENV/bin/python -c "from rabbitstew.provenance import platform_record as p; r=p(); print('D', r['git_sha'], r['git_dirty'])"
# E: editable checkout -> the checkout's sha
cd / && $VENV/bin/python -c "from rabbitstew.provenance import platform_record as p; r=p(); print('E', r['git_sha'], r['git_dirty'])"; git -C $PR rev-parse HEAD
# F: git status takes index.lock when stat data is stale
touch $PR/rabbitstew/__init__.py; strace -f -e trace=openat,rename git -C $PR/rabbitstew status --porcelain --untracked-files=no 2>&1 | grep index.lock
