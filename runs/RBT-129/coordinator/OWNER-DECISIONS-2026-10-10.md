# Owner decisions, 2026-10-10 (~01:45 UTC)

*Given first-hand by the owner in the coordinator session `session_017eUHGNdTSsoVFAtLaJWehF`, in reply to the
coordinator's check-ins. Recorded by the coordinator.*

1. **S-scan cost: "OK up to 1,150"** (core-h).
   - The adversary's re-estimate is ~560–1,150 core-h, likely near the top (#562 review, MINOR 2). That is above the
     ~600–800 quoted in `OWNER-DECISIONS-2026-10-04.md` item 1.
   - The cap is 1,150 core-h. The coordinator stops the scan and comes back to the owner if it is on course to exceed it.
   - `GO-ID-SSCAN: RBT129-SSCAN-GO-1` is opened on this approval (`../s-corruption-scan/LOCKS.md`).
2. **P-1: "approve P-1".**
   - P-1 is the `s60_compare` extinction branch and the launch.txt re-pin required by ruling A′ (see
     `OWNER-DECISIONS-2026-10-05.md` item 2). It must land before 2b emits `lanes/S2B`.
   - The adversary nits deferred from #558 ride with it.
   - While the SSCAN lanes are live, NOTE 17 applies: P-1 may not change anything the SSCAN lanes pin.
3. **Permissions and the S2B timebox: "Do both or even more permissive"** (about 12:45Z).
   - Merged as #570 (`37878780`): the repo's `.claude/settings.json` allow-list, and RUNNER-S2B's 110-min
     `timeout` per lane run.
   - The owner then committed `CLAUDE.md` (`210035a8`) personally. It gives the coordinator's messages the owner's
     authority for routine running. It does not cover denials or registered research decisions.
4. **S2B runners: "go 6 9" and "launch 3 4"** (about 13:45Z). The held v2 runners for hosts 6 and 9 were released
   to build and launch their lanes, and new timeboxed v2 runners were launched for hosts 3 and 4. The old runners for
   those hosts stay idle.
5. **RBT-134: "approve RBT-134 diagnosis"** (about 16:45Z).
   - This approves the read-only control diagnosis registered in `runs/RBT-134/GATE-FAILURE.md` r2 (#571,
     `479684bb`). Its decision table was fixed before any control output is read.
   - The diagnosis relays category tokens only. Any r4 amendment and any re-run come back through review.
6. **RBT-134 after the ESCALATE: "Follow your recommendations"** (17:22:51Z).
   - The owner gave this first-hand in the RBT-134 designer session, `session_013wkZLpeTRYVr9H5a645wCk`. The
     coordinator verified it in that session's transcript.
   - It applies to `runs/RBT-134/OPTIONS.md` (#574, `453297b2`), whose recommendation is: "(c1) first, if the
     owner gives the go … then choose between (a) and (b)". On that reading:
     - **(c1) GO.** Finish the r2 §4 B0 regenerations (I5-2, I5-3), about 1 CPU-h. The result is descriptive only:
       no r4 follows an ESCALATE. Only the category tokens are relayed.
     - **(c2) is not chosen**, since OPTIONS recommends against it.
     - **(a) or (b) is PENDING.** OPTIONS makes it depend on whether the owner still wants the operator question
       answered, and the coordinator is asking the owner directly.
       - In the meantime, a fresh blind session drafts RBT-134b's controls. This is the coordinator's step, not
         the owner's: it uses no compute, and nothing is registered or run unless the owner chooses (b).
       - The coordinator has added a blindness condition: the drafting session never reads
         `claude/rbt134-diagnosis`, `OPTIONS.md` or the #574 figures.
     - **The #574 departure from r2 §4.3** (quoting the flagged C+ figures and the sham direction) is *taken as
       accepted* under this decision. That is the coordinator's reading, and it is being confirmed with the owner.
     - **Lane B stays sealed** until the owner chooses.
7. **RBT-134 (a) or (b): "134b", "accept quoting", and a cost cap of "30 CPU-h, with trims"** (about 19:45Z).
   - The owner gave these first-hand in the coordinator session `session_017eUHGNdTSsoVFAtLaJWehF`.
     - The owner first typed "134b, cap N CPU-h" and "accept quoting".
     - The coordinator asked for the value of N. The owner chose "30 CPU-h, with trims (Recommended)".
   - **(b) RBT-134b is chosen**, and (a), closing RBT-134 as VOID, is not. This settles the choice left PENDING in item 6.
   - The 134b design is PR #576. Before any run:
     - its review fixes land;
     - it is re-reviewed;
     - it comes back to the owner.
     The held-out validation needs an owner GO, and so does the registered run.
   - **Cost cap: 30 CPU-h for RBT-134b in total**, covering validation, the registered run and any re-signing. The cap
     adopts the #576 reviewer's trims B1 (i)–(iv):
     - (i) no lane B re-run;
     - (ii) C− runs on its background block only;
     - (iii) no C− swap;
     - (iv) at MASTER_SEED, the diagnosis's EXACT swap for B0 is cited rather than re-run.
     If the run is on course to exceed 30 CPU-h, for example because the C+ ladder climbs, the coordinator stops and comes back to the owner.
   - **"accept quoting"** confirms the coordinator's reading in item 6: #574's departure from GATE-FAILURE r2 §4.3
     (quoting the flagged C+ figures and the sham direction) is accepted.
   - **Lane B stays sealed.** The coordinator reads trim (i) as meaning that lane B's committed E1, E2 and H1 outputs
     are read as they stand, and only after RBT-134b registers. DESIGN-134b must state the exact unseal point.

---
_Generated by [Claude Code](https://claude.ai/code)_
