# RBT-129 Stage 1 readout: rulings cited, not read from branches

## F7 K-SALT de-duplication (resolves READOUT-PLAN.md O-1)

- **Ruling.** Coordinator, 2026-10-01 14:35 UTC, a comment on tracker issue RBT-129. It is labelled
  **DATA-INFORMED**. Quoted as the coordinator relayed it:

  > "A K-SALT reference is de-duplicated only when it shows the double-write signature; otherwise the check reads VOID."

- **Why.** It answers resume-adversary M1 (`resume-adversary/ADVERSARY.md`): the changed K-SALT reading had to be
  recorded as a ruling on F7. The signature is the one `stages.double_write` tests: every repeated line occurs exactly
  twice, in one contiguous range of generations, with no step back after de-duplication and a resume on record (#504).
- **Applied.** The coordinator's ruling of 2026-10-02 12:57 re-evaluated `1/c1-p010-PW-G/129003` as **PASS** under the
  merged `half_compare`. The census reference `stage0/c1-p010-PW-G/129003/S` shows the signature: 347 duplicate lines
  over generations 55–59, each written twice, from one resume. The resume adversary's N5 independently confirms this.
- **Record.** `KSALT.txt` on `ckpt/rbt-129-stage1-c1-p010-PW-G-129003-record` at
  `b00fc6af02fcf6d67dc7b257340e98e70f992a5a`. It is the rewritten record, and it keeps the superseded VOID text.
  **Cited, not read**: the plan's author has not fetched or read this branch. The readout reads it at integrity,
  after the go.
