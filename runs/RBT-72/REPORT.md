# RBT-72: re-derivation behind paper 8

`docs/paper-8-the-prize-the-proposal-rate-and-the-magnitude-gap.md` is the deliverable. This
directory holds the one thing it owes the repository beyond the text: a script that recomputes
every headline number in the paper from the committed file the paper cites for it.

    python runs/RBT-72/rederive.py > runs/RBT-72/rederive.txt

No simulation. Pure file reading and arithmetic; runs in under a second from a checkout that has
never held the bulk. Each row prints the figure recomputed, the figure quoted on the tickets, and
a status: MATCH, MISMATCH, READOUT (a printed readout with no data behind it committed) or PROSE
(only prose is committed). The paper's bracketed tags (P6, R15, M18, ...) are the row ids.

As committed: 100 rows from 33 files; 77 match, 6 do not (four figures, discussed in the paper's
§8), 16 rest on readouts only, 1 on prose only.

Three readouts were also re-run from their own scripts for the paper and are byte-identical to
the committed files: `runs/RBT-91/weight_census.py`, `runs/RBT-78/reconcile.py --n 5000
--workers 4`, and `runs/RBT-91/structural_rate.py --n 100000 --workers 4 --background 5000`
(about nine minutes on four cores).
