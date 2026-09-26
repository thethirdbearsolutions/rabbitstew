#!/usr/bin/env bash
# Keep a long run alive across a reclaimed container: snapshot its whole directory to a
# checkpoint branch on the remote, and restore it in a fresh session to continue with --resume.
#
#   scripts/durable.sh save    RUN_DIR [LABEL]          one snapshot now
#   scripts/durable.sh every   MINUTES RUN_DIR [LABEL]  a snapshot every MINUTES until the run's
#                                                        state.json reaches its config's seasons
#                                                        (or generations), then a final one;
#                                                        with DURABLE_WATCH_PID set, also stops
#                                                        (after a last save) when that process exits
#   scripts/durable.sh restore RUN_DIR [LABEL]          unpack the latest snapshot into RUN_DIR
#   scripts/durable.sh status  RUN_DIR [LABEL]          what the remote holds, without fetching it
#
# LABEL defaults to RUN_DIR with slashes turned into dashes; the branch is ckpt/LABEL. Each save
# replaces the branch with one parentless commit (force-push), so a checkpoint branch never grows
# a history and the working tree, index and current branch are never touched (plumbing only).
# The tarball is split into 90 MB parts to stay under GitHub's 100 MB file limit.
#
# Why (the "lost runs" failure): cloud sessions go idle, their containers are reclaimed, and a
# run's bulk (state.json, lineage.jsonl, genomes/) goes with them. The ecology and the arena both
# resume byte for byte from their directory (RBT-93, RBT-95); this makes the directory outlive
# the machine. A snapshot taken mid-season is consistent: state.json is replaced atomically after
# each season and --resume cuts the logs back to it. Checkpoint branches are bulk, not evidence:
# the evidence still goes on a results branch and a PR per runs/README.md. Cloud sessions
# cannot delete remote branches (the git proxy answers 403), so stale ckpt/* branches are left
# for the owner to prune once a run's evidence is merged.
set -euo pipefail

REMOTE="${DURABLE_REMOTE:-origin}"
PART_SIZE="${DURABLE_PART_SIZE:-90m}"

die() { echo "durable: $*" >&2; exit 1; }
label_of() { local l="${2:-}"; [ -n "$l" ] || l="$(echo "${1%/}" | tr '/' '-')"; echo "$l"; }

progress() {  # "<done>/<target>" from state.json and config.json, or "?" when either is missing
    python3 - "$1" <<'EOF'
import json, os, sys
d = sys.argv[1]
try:
    cfg = json.load(open(os.path.join(d, "config.json")))
    st = json.load(open(os.path.join(d, "state.json")))
except Exception:
    print("?"); sys.exit(0)
if "ecology" in cfg:
    print(f"{int(st['season'])}/{cfg['ecology']['seasons']}")  # seasons completed
else:
    gens = [p.get("generation") for p in st.get("populations", {}).values()]
    print(f"{min(gens) if gens and None not in gens else '?'}/{cfg.get('generations', '?')}")
EOF
}

save() {
    local dir="${1%/}" label; label="$(label_of "$@")"
    [ -d "$dir" ] || die "no run directory $dir"
    local tmp; tmp="$(mktemp -d)"
    # a file replaced mid-read (state.json, the logs) makes tar exit 1; the snapshot is still usable
    tar -C "$(dirname "$dir")" --warning=no-file-changed -czf "$tmp/run.tar.gz" "$(basename "$dir")" || [ $? -eq 1 ]
    (cd "$tmp" && split -b "$PART_SIZE" -d -a 3 run.tar.gz run.tar.gz.part && rm run.tar.gz)
    local entries="" f
    for f in "$tmp"/run.tar.gz.part*; do
        entries+="100644 blob $(git hash-object -w "$f")"$'\t'"$(basename "$f")"$'\n'
    done
    local prog; prog="$(progress "$dir")"
    printf '%s\n' "$(basename "$dir")" "$prog" "$(date -u +%FT%TZ)" > "$tmp/MANIFEST"
    entries+="100644 blob $(git hash-object -w "$tmp/MANIFEST")"$'\t'"MANIFEST"$'\n'
    local tree commit size
    tree="$(printf '%s' "$entries" | git mktree)"
    commit="$(git commit-tree "$tree" -m "ckpt/$label: $dir at $prog")"
    size="$(du -sh "$tmp" | cut -f1)"
    rm -rf "$tmp"
    local i
    for i in 0 1 2 3 4; do
        if git push -q -f "$REMOTE" "$commit:refs/heads/ckpt/$label" 2>/dev/null; then
            echo "durable: saved $dir at $prog to $REMOTE ckpt/$label ($size, ${commit:0:7})"; return 0
        fi
        sleep $((2 ** (i + 1)))
    done
    die "push of ckpt/$label failed five times"
}

restore() {
    local dir="${1%/}" label; label="$(label_of "$@")"
    [ ! -e "$dir/state.json" ] || die "$dir already holds a state.json; move it aside first"
    git fetch -q "$REMOTE" "+refs/heads/ckpt/$label:refs/remotes/$REMOTE/ckpt/$label" || die "no ckpt/$label on $REMOTE"
    local tmp ref="$REMOTE/ckpt/$label"; tmp="$(mktemp -d)"
    git show "$ref:MANIFEST" > "$tmp/MANIFEST"
    local name; name="$(head -1 "$tmp/MANIFEST")"
    local part
    for part in $(git ls-tree --name-only "$ref" | grep '^run.tar.gz.part' | sort); do
        git cat-file blob "$ref:$part" >> "$tmp/run.tar.gz"
    done
    mkdir -p "$tmp/x" "$(dirname "$dir")"
    tar -C "$tmp/x" -xzf "$tmp/run.tar.gz"
    mkdir -p "$dir"
    cp -a "$tmp/x/$name/." "$dir/"
    rm -rf "$tmp"
    echo "durable: restored $dir at $(progress "$dir") from $REMOTE ckpt/$label; continue it with --resume --out $dir"
}

status() {
    local label; label="$(label_of "$@")"
    git ls-remote --exit-code "$REMOTE" "refs/heads/ckpt/$label" >/dev/null 2>&1 || { echo "durable: no ckpt/$label on $REMOTE"; return 1; }
    git fetch -q "$REMOTE" "+refs/heads/ckpt/$label:refs/remotes/$REMOTE/ckpt/$label"
    echo "durable: ckpt/$label: $(git log -1 --format='%s (%cr)' "$REMOTE/ckpt/$label")"
}

every() {
    local minutes="$1"; shift
    local dir="${1%/}"
    [[ "$minutes" =~ ^[0-9]+$ ]] && [ "$minutes" -ge 1 ] || die "every: MINUTES must be a positive integer"
    while :; do
        sleep "$((minutes * 60))"
        [ -e "$dir/state.json" ] || { echo "durable: $dir has no state.json yet"; continue; }
        save "$@" || echo "durable: save failed; will retry in $minutes min" >&2
        local p; p="$(progress "$dir")"
        if [ "${p%%/*}" = "${p##*/}" ]; then echo "durable: $dir complete ($p)"; return 0; fi
        if [ -n "${DURABLE_WATCH_PID:-}" ] && ! kill -0 "$DURABLE_WATCH_PID" 2>/dev/null; then
            save "$@" || true; echo "durable: process $DURABLE_WATCH_PID has exited; final snapshot taken ($(progress "$dir"))"; return 0
        fi
    done
}

cmd="${1:-}"; shift || true
case "$cmd" in
    save|restore|status) [ $# -ge 1 ] || die "usage: $cmd RUN_DIR [LABEL]"; "$cmd" "$@" ;;
    every) [ $# -ge 2 ] || die "usage: every MINUTES RUN_DIR [LABEL]"; every "$@" ;;
    *) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 2 ;;
esac
