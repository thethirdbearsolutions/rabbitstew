# RBT-106 design adversary: report on PR #213

*Design adversary for RBT-106, 2026-09-26, dispatched by the coordinator (session_01WKXr6PgNkscGhVc7Bzth9k).
It attacks the pre-registration at PR #213's head, `1163d62` (`results/RBT-106-design`). It measures and
does not tune, and it edits no file of the designer's. Every probe is under `runs/RBT-106/adversary/`,
with its readout committed beside it. **No arm was launched.** The throwaway runs were at most 20
seasons, in scratch directories. Two reads touch RBT-104's live arms: the first 20 seasons of S1-801
and S1-4 (seasons rows and lineage records only), restored from their checkpoints for the cross-ticket
check, and nothing later.*

**Platform, for every number below:** `x86_64`, MuJoCo 3.14.0, numpy 2.4.6, on a four-core cloud
container. `rabbitstew/` at the head is byte-identical to c872e80, RBT-104's launch commit.

## Verdict in one paragraph

__VERDICT__

---

## Findings

__TABLE__

---

__BODY__

## Files (all under `runs/RBT-106/adversary/`)

| file | what |
|---|---|
| `ADVERSARY.md` | this report |
| `cross_ticket.py`, `cross_ticket.txt` | F2: RBT-106's S1 command against RBT-104's live S1-801 and S1-4, 20 seasons |
| `one_field_4.txt` | F1: the flag on seed 4 (byte identity at 0; one field at 3; regrow_delay) |
| `null_xover.py` | F3, F4: the designer's null with the ecology's crossover put back (`--deepen M` sets the depth proxy) |
| `null_xover/`, `pool_xnull.py`, `pool_xnull.txt` | F3: ten seeds × three cells × 20 replicates at seasons 150, 300 and 599; the mutation-only branch reproduces the designer's `null/` in 30 of 30 seed-cells |
| `null_xover_deep/`, `pool_xnull_deep.txt` | F4: the same at depth ×2 (K = 1 cells) and ×3 (K = 8) |
| `bare_patchy/`, `pool_bare.py`, `pool_bare.txt` | F6: part 2's bare champions on ten seeds, scored by readout (b) in the patchy world (`cross_world.py`, unchanged) |
| `power_adv.py`, `power_adv.txt` | F5, F7: the designer's `power.factorial` at the q the pre-registration states; the power model with the measured bare-line distribution |
