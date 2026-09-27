# RBT-127 adversary: PR #411 (head `4a3ce85`, base `dc57055`)

**Verdict: MERGE AFTER FIXES.** The code is sound and every golden and byte-identity test holds. One code MUST remains: `platform.json` is git-ignored, so the record never reaches committed evidence. The errata index is complete, and 30 of the 36 sampled rows are right on location and substance. Six rows misquote, overstate or mislocate a correction, and four of those six are ruled glosses on registered labels, which R14 says must be quoted exactly. All the fixes are text edits, plus one `.gitignore` line; none touches `rabbitstew/`.

Logs are in `logs/`:
- `sample.py` and `sample.txt`: the sampling method and the drawn rows;
- `batch{0,1,2}.md`: the rows as drawn;
- `gitsha_probe.sh` and `gitsha_probe.txt`: the git-sha and index-lock probes;
- `suite_*.txt`: the test runs.

---

## 1. Code

### 1.1 Tests

- **PR head `4a3ce85`, clean venv:** Python 3.11.15, mujoco 3.14.0, numpy 2.4.6, pytest 9.1.1. **scipy is not installed** (`ModuleNotFoundError`). Result: **403 passed** in 249 s (`logs/suite_head_4a3ce85.txt`).
- **Base `dc57055`, same setup:** **398 passed** (`logs/suite_base_dc57055.txt`). The difference, 403 − 398 = 5, is exactly the 5 new tests in `tests/test_platform_record.py`. No existing test changed outcome.
- **The goldens pass unchanged:**
  - `tests/test_rbt113.py`, which holds sha256 digests of `config.json`, `history.json` and `state.json`;
  - `tests/test_salt0_golden.py`.

  `config.json` gains no key. The platform record is a sibling file, which is the right call.

### 1.2 Does `platform.json` break a reader? No.

I swept `rabbitstew/`, `scripts/`, every script under `runs/`, `tests/`, and both RBT-120 branches (`results/RBT-120-design` 343cff5 and `-design-adversary` f8d296c). Every reader that lists, globs or counts files falls into one of these groups:
- it reads a subdirectory (`KIND/final`, `KIND/genomes`, `champions_gen*`, `best_gen*`);
- it reads files it names;
- it takes the whole directory as-is.

**Where each kind of reader stands:**
- **Genotype loaders.** The only root-level `*.json` genotype glob is `ecology.population_files` (`ecology.py:819`). The PR excludes `platform.json` there, and a test covers it. No other loader can pick it up. *(Pre-existing and out of scope: `state.json` is not excluded there either. A real run never reaches that branch.)*
- **Resume and byte-identity checks** compare named files only, so the new timestamp and `resumes` list are never compared. This covers:
  - `tests/test_ecology_switches.py:98-99`;
  - `tests/test_rng_streams.py`;
  - `runs/RBT-107/fork_check.sh` and `extend_check.sh`;
  - `runs/RBT-104/byte_identity.py`, `runs/RBT-112/byte_identity.py` and `runs/RBT-112/adversary/bi_compare.py`;
  - `runs/RBT-96/adversary/item4.sh`;
  - the roundtrip, smoke and rederive scripts in RBT-92/96/99/100/101.
- **`scripts/durable.sh`.**
  - `save` tars the whole directory, so `platform.json` rides along.
  - `restore` guards only on `state.json` and restores with `cp -a`.
  - The MANIFEST is built from the tar parts and `progress()` reads only `config.json` and `state.json`.

  So restore is unaffected. Restoring a pre-PR checkpoint and then resuming creates `{"resumes": [...]}`, which `read_platform` handles.
- **No-peek, trial-merge and file-count checks.** I found **no "tm" or trial-merge script** on either RBT-120 branch. RBT-120's runner inherits RBT-113 RUNNER §4's evidence step: an allowlisted `install` loop, then "38 files (+ any resumes.txt), nothing else". It never copies `platform.json`, so the count is unchanged. `runs/RBT-106/p1-adversary/nopeek_check.py` guards the paths a script opens, not directory listings. The RBT-120 `run_arm.sh` writes its own arm-level `platform.txt`, a different name, so there is no clash.
- **Cosmetic only.** `runs/RBT-107/hrep/adversary/cutcheck.py:36` prints the run root's other top-level files. On a new run the list would gain `platform.json`. That changes a printed line, not a PASS/FAIL.

### 1.3 The git sha: safe everywhere, but sometimes wrong (`logs/gitsha_probe.txt`)

**Where it behaves:**
- **No network is involved.** It runs only `rev-parse` and `status`.
- **No git binary** on the PATH gives `None`/`None` (probe C).
- **Outside a checkout**, with a non-editable install, it gives `None`/`None`.
- **A timeout** raises `TimeoutExpired`, which the broad `except` catches.

**Where it goes wrong:**
- **Wrong sha from a surrounding repo (probe A).** A non-editable `pip install` into a venv that sits inside an unrelated git checkout records **that checkout's HEAD** (`025bf20…`, the probe's throwaway repo). The same happens with the common `.venv/` inside the rabbitstew checkout itself: the recorded sha is the checkout's current HEAD, not the commit that was installed. The code runs `git -C <package dir>`, and `site-packages` is inside the outer work tree.
- **Inherited `GIT_DIR` (probe D).** If the environment sets `GIT_DIR`, it silently wins and records the other repo's sha.
- **Index lock (probe F).** `git status` takes `.git/index.lock` and rewrites the index whenever stat data is stale (seen in strace). A `git add` or `git commit` in the same checkout at that instant, which this programme does routinely while launching arms, fails with "index.lock exists". The window is small but real.

### 1.4 `record_resume`

It writes only `platform.json`, which no golden test pins. `config.json` is still rewritten exactly as before. The write is not atomic: a torn file reads as `None`, and the next resume would then replace the original record with `{"resumes": [...]}`. That is a nit.

---

## 2. Errata

### 2.1 Method

`logs/sample.py` parses every data row of the seven numbered tables in `ERRATA.md` at `4a3ce85`, skipping header rows: 104 rows in all. It then calls `random.seed(127)` once and walks the strata in sorted order. From each stratum it takes `min(n, max(2, round(32·n/104)))` rows with `random.sample`, which gives **36 rows**:

| table | rows | sampled |
|---|---|---|
| Papers | 35 | 11 |
| Published reports | 4 | 2 |
| Registered outputs | 19 | 6 |
| Run reports | 31 | 10 |
| Docs | 12 | 4 |
| Commit messages | 2 | 2 |
| Withdrawn | 1 | 1 |

I split the 36 into three batches for independent checks. Each row was checked on:
- (a) whether file:line at the PR head shows the quoted text;
- (b) whether the cited source makes the correction, and whether the figures match;
- (c) whether the row claims more than the source;
- (d) for a registered label, whether its ruled gloss is quoted exactly;
- (e) whether HISTORY agrees.

I re-checked every MUST below myself, against the files.

I also checked by hand the two H76 labels the sample missed:
- RBT-117 `compare.txt:46`: the quoted text is at :46;
- RBT-100 `readout.txt:413`: the text matches `readout.py:230`.

The two commit rows (c42e4f7 and 935bcbf) are outside the shallow clone, so they were read through the GitHub API.

**Result:**
- **Clean:** 18 rows. Every quoted "what it says" is at the cited line in all 36, with the exceptions listed below.
- **SHOULD only:** 12 rows.
- **MUST:** 6 rows.

### 2.2 MUST (fix before merge)

**M1. `.gitignore` drops the platform record** (code, not errata). `runs/**` whitelists only `*.md`, `*.py`, `*.sh`, `*.txt` and `config.json`, and `git check-ignore -v runs/X/platform.json` hits `.gitignore:14`. So `platform.json` never enters a results PR, which defeats R13: a replay reads committed evidence. The file survives only in `ckpt/*` tarballs.

- **Fix:** add `!runs/**/platform.json` to `.gitignore`, and add `platform.json` to the evidence allowlist in RUNNER-style install loops going forward. Or state plainly that the record is bulk, not evidence.
- **Timing:** this touches no file under `rabbitstew/`, so it does not move the pinned launch tree.

**M2. ERRATA:123, RBT-112 `readout.txt:40`: the ruled gloss is truncated inside quotation marks.**
- **Row:** "the bias walk is not what stops selection holding the compass".
- **Ruling:** `runs/RBT-112/READOUT.md:35-36` and P10:62 read "The bias walk is not what stops selection holding the compass **in the population**."
- The scope phrase is dropped with no ellipsis, on a registered label (R14).

**M3. ERRATA:131, RBT-90 `part2-readout.txt:49` "SPLITS": it gives a gloss that has itself been replaced.**
- The row quotes PART2-VERDICT:16: "one run per founding population cannot separate founders from history".
- `runs/RBT-105/REPORT.md:45` says: "This replaces RBT-90 part 2's *'one run per founding population cannot separate founders from history'*."
- The adopted wording is REPORT:42-43: "Oscillator fate is **not fixed by the founding population** … reversed the fate in 5 of 14 **decided** replicates … on 3 of 8 founding populations … **The founders shift the late oscillator birth rate**."
- The row's citation `RBT-105/REPORT.md:47` should be :42-45. :47 is about the first version's withdrawn phrases. The row also drops "decided".

**M4. ERRATA:128, RBT-104 `readout.txt:58` "VOID": the ruled wording is missing.**
- The row leads with HISTORY's summary, "**VOID by design**".
- The ruling reads "VOID, and the instrument could not see" (`runs/RBT-104/readout-adversary/READOUT-ADVERSARY.md:292`; P10:258-259).
- Section 3's own rule is to quote the ruled gloss.
- Also, "Hosts mask" is withdrawn at `runs/RBT-104/REPORT.md:170-171`, which is outside the cited :36-60.

**M5. ERRATA:111, report 1 `index.html:292`: overclaim.**
- The row says "HP's 9 of 10 does not imply **any** selection strength".
- The cited sources say less. P10:510 says "does not **by itself** imply s **of that order**" (≈ 0.39), and F6 (PAPER-ADVERSARY:127) says "does not imply s ≈ 0.39".
- Use the source's wording. Also cite HISTORY H66 (:165), which names :279, :290 and :292.

**M6. ERRATA:197, `docs/rbt-91-weight-scale-decision.md:260-275`: misattributed quotation and understatement.**
- **Wrong item.** "item 3: '**n = 4** … Re-signing …'" puts item 2's heading (:266) inside item 3's quotation. Item 3 is :269-275.
- **Understated.** "Item 2 … is weakened, not withdrawn" misses that item 2's "92% figure is the maximum of four draws" is withdrawn:
  - the same document at :97-98 says the arrival "an earlier version of this document reported as '92% …'" turned out to steer the wrong way;
  - P8:666 (W10) withdraws the "92% of the first paying rung".

**M7. ERRATA:132, RBT-90 `part2-readout.txt:54` has a wrong second location.** It says "(the label also at :28)", but :28 is the pre-registered rule text ("holds on >= 8 of 10, a property of the search; …"), not a label. The label's other occurrences are :34 (row 133's own location) and :44. *(M2–M7 are the six failing rows: 111, 123, 128, 131, 132, 197.)*

### 2.3 SHOULD

**Uncited sources or ranges that miss the figures**
- **ERRATA:177 (RBT-113 "learns to eat").**
  - The 3-decimal figures 0.913 / 0.934 / 0.854 come from `runs/RBT-113/readout-adversary/probe_food.txt`, which the row does not cite. The cited sources round them to 0.91 / 0.93 / 0.85.
  - "It is the blind mower of paper 6, evolving from random founders under imposed selection" is in neither cited source. Its only home is HISTORY:174 (H70), which quotes it. Cite HISTORY:174 and `probe_food.txt`.
  - M2's quotation is recapitalised ("Learns…").
- **ERRATA:153 (RBT-59).** The 3.4×, 0.51 → 0.25 and "worse" figures are at `runs/RBT-60/REPORT.md:27, 49, 65`, outside the cited :106-114.
- **ERRATA:207 (c42e4f7).** "Terrain is random in every world" is at RBT-103 REPORT:41, and "exploratory, with no pre-posted attribution rule" is at :55-59. Both are outside the cited 43-53 and 192-206.
- **ERRATA:150 (CHAOTIC-DOC 0.70%).**
  - "ρ 1.565–4.92" is at P7:435, outside the cited range.
  - CHAOTIC-DOC repeats 0.70% at :285 and :323, and the row does not list either.

**Wording**
- **ERRATA:136 (RBT-102 aggregate).**
  - The "5.5×" is against 0.042%, not the p_u = 0.0520% the row sets it beside; that would be about 6.8×.
  - The ruled headline "not informative about selection at this n" (REPORT:7) is missing, so "The verdict does not move" stands alone.
- **ERRATA:208 (935bcbf).** "+0.507 to +1.324" is quoted as if superseded, but no source corrects the numbers, only the terrain word and the attribution.

**Off-by-one spans**
- **ERRATA:60 (E7).** The quoted text starts at P5:55, so the span is 55-57. It inherits REVIEW's 56-57.
- **ERRATA:192 (RBT-69).** The quoted text is at :120-121, which is also H35's citation. "Direction of travel is a free population parameter. Measure it first" comes from HISTORY H35, not from the cited P7:396-400.
- **ERRATA:58 (E1/E4).** The quoted phrase spans P5:44-45.

**Dates**
- **ERRATA:163 and the other RBT-38-sourced rows (166-173).** These are dated 2026-09-12, while H22 cites RBT-38 at 2026-09-14T02:14. GitHub shows RBT-38 REPORT commits on 09-12, so 09-12 is defensible, but HISTORY contradicts itself. Say which one you took.

**Small omissions**
- **ERRATA:94 (E5 in P7).** It drops REVIEW's "adding arXiv:2508.17464, 2025".
- **ERRATA:216.** The bold in the quotation sits on different words from the draft `d5e60a8:96`.

**Code**
- **S-code-1.** Make `_git` trust only the package's own checkout.
  - Pass an environment without `GIT_DIR` and `GIT_WORK_TREE`.
  - Record the sha only if `git -C here ls-files --error-unmatch provenance.py` succeeds; otherwise record `None`.
  - Consider adding the installed distribution's `direct_url.json` commit when one is present.
- **S-code-2.** Use `git --no-optional-locks status …` so the dirty check never takes `index.lock`.
- **S-code-3 (nit).** Write `platform.json` through a temp file and `os.replace`, as `state.json` is written.

### 2.4 Checked and correct (examples)

- E2 as corrected by F2 (ERRATA:93):
  - P7:780 is blank and the claim is at :781-783;
  - REVIEW's first version (`6513164`) had 781-783 and "proposes nothing", as the row says.
- The index.html:290 correction to 1.3% (P10:410, 0.0127).
- P5:456 E1 (authors, venue and pages).
- P5:463 E6 (the DOI).
- RBT-105 `aa_spread.txt:4` (the permitted citation, :281, quoted with a fair ellipsis).
- The compass-spike row (no erratum in the file; CHAOTIC-DOC:14-22).
- The RBT-118 withdrawn two-phase row: the draft `d5e60a8:96` has the sentence, and every figure is at prior-adversary :51 and :212-222.

---

## 3. Coverage

Every required item is present.

| item | ERRATA rows |
|---|---|
| **H74:** +0.723 | P7:309-312 (:91), CHAOTIC-DOC:166 (:149) |
| **H75:** 0.246 | P5:189, 220, 414; P6:171; foraging-world:152 |
| **H75:** 1.3% | P6:126-128, 209-210, 213-215, 399-400; foraging-world:225-226 |
| **H75:** "chassis nose alone" | P6:112-118 |
| **H75:** the σ(d) law | P5:303-305 |
| **H75:** rbt-91 decision note | :54, :80-87, :202-203, :260-275 (and :36 etc.) |
| **H76:** bare labels | RBT-117 `compare.txt` (:46; HISTORY's :37,44 corrected, which is right), RBT-112 `readout.txt`, RBT-100 `verdict_text`, RBT-105 `aa_spread.txt` |
| **H66:** report 1's readings | index.html :279, :290, :292, plus :251 |
| **E1–E7** (E2 per F2) | E1 at P5:45 and :456; E2 at P7:781-783; E3 at P5:58-60 and P7:786-787; E4 at P5:45; E5 at P5:57, :453 and P7:784-785; E6 at P5:450, :461, :463; E7 at P5:56-57 |
| **RBT-113's "learns to eat"** | PREREG:343; design-adversary:65-66. The only other occurrences are in the readout adversary, quoting it for replacement, and in HISTORY. |
| **RBT-118 "two-phase"** | Section 7 |

On H66, the pointer to report 2 is PR #398, still a draft; the row says so.

**Coverage note:** "a real gain in foraging" (H70) survives only as quotation in the adversary and HISTORY, so its omission is right.

---

## Summary of required changes

- **MUST:**
  - M1: `.gitignore` whitelists `platform.json`;
  - M2: row 123, restore "in the population";
  - M3: row 131, give RBT-105's adopted wording, fix `:47`→`:42-45`, "decided";
  - M4: row 128, quote "VOID, and the instrument could not see", cite REPORT:170-171;
  - M5: row 111, "does not by itself imply s of that order", cite H66;
  - M6: row 197, move "n = 4" to item 2 and say item 2's 92% is withdrawn;
  - M7: row 132, drop ":28" (or say :34, :44).
- **SHOULD:** S-code-1 to S-code-3, plus the errata items in §2.3.
- **Merge timing:** unchanged. Hold until after the RBT-120 arms launch, as ruled. The MUST fixes add no change under `rabbitstew/`.
