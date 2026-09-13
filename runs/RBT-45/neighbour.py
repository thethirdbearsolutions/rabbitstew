"""RBT-45 follow-up: does `vocab.neighbour_links` help the crossed pairing?

My RBT-45 report suggested, without measuring it, that turning this flag on
"puts the crossed link one draw away instead of two".  Reading `Genotype.neighbours`
says otherwise: the Pioneer's two wheels are *siblings*, both children of the
chassis, so neighbours(wheel) = [chassis] and a wheel's brain never gains the other
wheel's units.  The crossed path still routes through the global brain.  What the
flag does instead is enlarge each wheel's source pool from 12 to 22, which should
*dilute* the chance of drawing that wheel's own nose and push the uncrossed rate down.

This script measures both, on the same no-world, no-selection discipline as reach.py.
It imports reach.py rather than editing it, so the published grid in cells.json still
reproduces byte-for-byte; the cell-id namespace here is separate, so the seeds differ.

Usage:  python runs/RBT-45/neighbour.py [--n 2000] [--workers 4]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import zlib
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import reach  # the validated readout: same sensor_influence decomposition
from rabbitstew.genetics import _link_sources, mutate_controller
from rabbitstew.synthesis import synthesize

MASTER_SEED = reach.MASTER_SEED
K_VALUES = (19, 23, 50)
ADD_RATES = (0.15, 0.6)
NEIGHBOUR = (False, True)


def wheel_source_count(g, vocab):
    """Candidate sources the operator draws from for a link into a wheel's brain."""
    out = {}
    for owner in (1, 2):
        out[owner] = len(_link_sources(g, owner, vocab))
    return out


def cell_id(cell):
    return f"nbr|{cell['kind']}|add{cell['add']}|nb{int(cell['nbr'])}|k{cell['k']}"


def run_chunk(task):
    cell, lo, hi = task
    cfg = reach.config()
    pool = reach.parents(cell["kind"])
    vocab = replace(cfg.mutation.vocab, neighbour_links=cell["nbr"])
    mcfg = replace(cfg.mutation, add_link_rate=cell["add"], remove_link_rate=0.1, vocab=vocab)
    cid = cell_id(cell)
    rows = []
    for i in range(lo, hi):
        rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, zlib.crc32(cid.encode()), i]))
        g = pool[i % len(pool)]
        for _ in range(cell["k"]):
            g = mutate_controller(g, rng, mcfg)
        r = reach.measure_conventional(synthesize(g, cfg.sim.synthesis))
        r["sources"] = sum(wheel_source_count(g, vocab).values()) / 2.0
        rows.append(r)
    return cid, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--chunk", type=int, default=50)
    args = ap.parse_args()

    cfg = reach.config()
    g0 = reach.parents("conventional")[0]
    base = {
        "wheels_are_neighbours": bool(2 in g0.neighbours(1)),
        "neighbours_of_wheel_1": g0.neighbours(1),
        "neighbours_of_wheel_2": g0.neighbours(2),
        "sources_off": wheel_source_count(g0, replace(cfg.mutation.vocab, neighbour_links=False)),
        "sources_on": wheel_source_count(g0, replace(cfg.mutation.vocab, neighbour_links=True)),
    }
    print(json.dumps(base), flush=True)

    cells = [
        {"kind": "conventional", "add": a, "nbr": nb, "k": k, "n": args.n}
        for nb in NEIGHBOUR
        for a in ADD_RATES
        for k in K_VALUES
    ]
    by_id = {cell_id(c): c for c in cells}
    tasks = [(c, lo, min(lo + args.chunk, c["n"])) for c in cells for lo in range(0, c["n"], args.chunk)]
    print(f"{len(cells)} cells, {len(tasks)} chunks, n={args.n}", flush=True)

    t0 = time.time()
    collected = {cid: [] for cid in by_id}
    with Pool(args.workers) as p:
        for cid, rows in p.imap_unordered(run_chunk, tasks, chunksize=1):
            collected[cid].extend(rows)

    results = []
    for cid, cell in by_id.items():
        rows = collected[cid]
        s = reach.summarise({**cell, "rem": 0.1}, rows)
        s["neighbour_links"] = cell["nbr"]
        s["mean_wheel_sources"] = round(float(np.mean([r["sources"] for r in rows])), 2)
        results.append(s)
    results.sort(key=lambda r: (r["neighbour_links"], r["add_link_rate"], r["k"]))

    payload = {"master_seed": MASTER_SEED, "n_per_cell": args.n, "body": base,
               "cells": results, "seconds": round(time.time() - t0, 1)}
    with open("runs/RBT-45/neighbour.json", "w") as f:
        json.dump(payload, f, indent=1)

    print("\n| neighbour_links | add | k | wheel sources | PAIR | uncrossed | crossed | CHASSIS | links |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in results:
        print(f"| {r['neighbour_links']} | {r['add_link_rate']} | {r['k']} | {r['mean_wheel_sources']} | "
              f"{r['pair']:.4f} | {r['uncrossed']:.4f} | {r['crossed']:.4f} | {r['chassis']:.4f} | {r['mean_links']:.1f} |")
    print(f"\nwrote runs/RBT-45/neighbour.json in {payload['seconds']}s")


if __name__ == "__main__":
    main()
