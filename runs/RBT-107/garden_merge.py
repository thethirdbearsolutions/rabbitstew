"""RBT-107: merge garden parts run on disjoint world ranges into one population file (the mean over all their worlds).

    python runs/RBT-107/garden_merge.py OUT.txt PART.txt [PART.txt ...]

Each part is garden.py's output for the same population (same label, seed, kind, season, the same individuals in the
same order) on its own world range, named in its '#' header ("J=... worlds=A..B"; the design stage's 8-world files carry
no range and are worlds 0..7).  Means are weighted by each part's J; exploder counts are summed.  The ranges must be
disjoint.  The parts stay committed beside the merged file: the split-half (worlds 0..15 against 16..31) is read from them.
"""
import re
import sys


def read(path):
    head = [l for l in open(path) if l.startswith("#")]
    m = re.search(r"J=(\d+)(?: worlds=(\d+)\.\.(\d+))?", head[0])
    J = int(m.group(1))
    lo, hi = (int(m.group(2)), int(m.group(3))) if m.group(2) else (0, J - 1)
    rows = [l.rstrip("\n").split("\t") for l in open(path) if l.strip() and not l.startswith("#")]
    return J, (lo, hi), head[0].strip(), rows


def main(out, parts):
    ps = [read(p) for p in parts]
    ranges = sorted(r for _, r, _, _ in ps)
    for (a0, a1), (b0, b1) in zip(ranges, ranges[1:]):
        if b0 <= a1:
            sys.exit(f"overlapping world ranges {ranges}")
    keys = [tuple(r[:5]) for r in ps[0][3]]
    for _, _, _, rows in ps[1:]:
        if [tuple(r[:5]) for r in rows] != keys:
            sys.exit("parts hold different populations")
    Jt = sum(J for J, _, _, _ in ps)
    with open(out, "w") as f:
        f.write(f"# garden MERGED J={Jt} from parts {', '.join(f'{r[0]}..{r[1]}' for r in ranges)}: "
                + " | ".join(h[2:] for _, _, h, _ in ps) + "\n")
        for i, k in enumerate(keys):
            means = [sum(J * float(rows[i][c]) for J, _, _, rows in ps) / Jt for c in range(5, 11)]
            expl = [sum(int(rows[i][c]) for _, _, _, rows in ps) for c in (11, 12)]
            f.write("\t".join(list(k) + [f"{x:.4f}" for x in means] + [str(x) for x in expl]) + "\n")
    print(f"merged {len(parts)} parts, J={Jt}, {len(keys)} individuals -> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
