# RBT-122 citation check: PR #404, `docs/prior-art/REVIEW.md` at 6513164

*Citation adversary, 2026-09-27, 20:45–21:30 UTC. I wrote only this file and `logs/`. Line numbers refer to `REVIEW.md` at 6513164.*

## Verdict: **ACCURATE-WITH-FIXES**

- **No phantom citations.** All 106 DOIs in the review resolve on Crossref. For every one, the authors, year, venue and pages agree with the review, with one exception: the review leaves some page and volume fields blank, and Crossref fills them (F8).
- **The six arXiv IDs from 2025–2026 exist** and match their titles and authors.
- **Every quotation I could reach is verbatim:** those from Sims 1994a, Lehman et al. 2020, Taylor & Massey 2001, Cheney 2013, Mertan & Cheney and Song et al.
- **Fix one error before RBT-120 cites the review.** It attributes a *per-joint* actuator cap to Sims. Sims's cap is **per effector, i.e. per degree of freedom** (F1).
- **One of the review's own errata is itself wrong.** E2 says Cheney et al. 2016 "proposes nothing". I reached the full text, which the reviewer could not, and its closing section proposes protecting morphological innovations and reports initial results (F2).
- **The novelty claims need hedging.** Three are stated as absolutes, and one directly relevant paper is missing from §1 (F3).
- **Four smaller fixes** are listed as F4–F7.

**How the evidence was gathered.**
- **Tools.** Crossref (`logs/crossref-all-dois.txt`), PubMed E-utilities (`logs/pubmed-abstracts.txt`, `logs/sample-pubmed.txt`), arXiv abstract pages (`logs/arxiv-recent.txt`, `logs/sample-arxiv.txt`, `logs/novelty-neighbours-arxiv.txt`), and author or publisher PDFs, with the excerpts I relied on in `logs/fulltext-excerpts.txt`.
- **Blocked hosts.** These were unreachable from the container, and I did not guess at their content:
  - 403: `direct.mit.edu`, `pnas.org`, `royalsocietypublishing.org`, `sciencedirect.com`;
  - `channon.net`: no connection;
  - `export.arxiv.org`: 406;
  - Europe PMC full text: 500;
  - `pmc.ncbi.nlm.nih.gov`: a JavaScript challenge page;
  - OpenAlex: 429 on the first try.
- **Where I used abstracts instead.** In those cases I used the PubMed abstract or an author copy, and say so below.

---

## Errors, with corrections

| # | line | the review says | the source says | fix | severity |
|---|---|---|---|---|---|
| **F1** | 401 (§4.2 table), 638–639 (§10.3.1) | Sims caps strength "by cross-sectional area … **per joint**, with forces clamped"; "Sims's rule is the principled one: … **per joint rather than per DOF**" | Sims 1994a §3.3 (author PDF, karlsims.com/papers/siggraph94.pdf): "**Each effector controls a degree of freedom of a joint.** … Each effector is given a maximum-strength proportional to the maximum cross sectional area of the two parts it joins. Effector forces are scaled by these strengths and not permitted to exceed them." The cap is per effector, which means per DOF. A spherical (3-DOF) Sims joint has three effectors, each at the full cap. That is the same ×3 allowance per ball joint that the review lists as our open exploit. | Credit Sims for the **area scaling and the clamp** only. Present "per joint rather than per DOF" (the joint-level `actuatorfrcrange`) as **the programme's own addition**, going beyond Sims. Also: "∝ mass^⅔ at fixed density" holds only for geometrically similar parts. Sims uses the *maximum* cross-section of the two parts joined, which a long, thin part does not scale that way. Say "≈ mass^⅔ for isometric parts". | **High**: RBT-120's design will cite it |
| **F2** | 560 (§8 E2) | Cheney et al. 2016 "diagnoses premature convergence and proposes nothing"; MIP is 2018's | The full text (Bongard lab copy, meclab.w3.uvm.edu/papers/2016_ALife_Cheney.pdf) says: "diversity maintenance would do best to focus on **protection of diversity within morphologies**", and "results employing a multi-timescale model, in which morphological mutations are given time to re-adapt their controllers … shows an improved ability for optimization … This is exactly the type of diversity maintenance that focuses on **protecting innovations to the morphology** specifically". The abstract adds: "early findings from our future work point in that direction". The 2018 paper names the method (MIP) and tests it. | Rewrite E2: "P7:780–782 credits the 2016 paper with *proposing MIP*. The 2016 paper proposes protecting morphological innovations as future work, with preliminary results. The named, tested method is Cheney et al. 2018. Cite both, and cite 2018 for the mechanism." Severity **Low**. `README.md`:269–271, which cites both papers, is correct as it stands. The cited range should be P7:780–782, not 781–783. | Medium: the erratum is itself an error |
| **F3** | 50 (§0.1) | "**Nobody has compared** open-ended body evolution against a strong hand-designed body at matched compute across tasks." | This is not falsified as literally worded, but close neighbours exist, and one is absent from §1. **Pagliuca & Nolfi, "The dynamic of body and brain co-evolution", *Adaptive Behavior* 30(3): 245–255 (online 2021), doi:10.1177/1059712321994685** (Crossref; arXiv:2011.11440 abstract): "robots with co-adapted body and control traits **outperform robots with fixed hand-designed morphologies**". **RoboMoRe** (Fang et al. 2025, arXiv:2506.00276) "significantly outperforms **human-engineered designs** … across **eight different tasks**". That one is LLM-driven rather than evolutionary, and matched compute is not stated. **Evolution Gym** (already in §1.3) claims the same across a multi-task benchmark. | Say "**not found in a directed search**: no study we found pairs open-ended body evolution with a strong hand-designed body at *explicitly matched* compute across tasks". Add Pagliuca & Nolfi to §1.2/§1.4 as another evolved-vs-hand-designed comparison with a parametric or bauplan-constrained body. | Medium |
| F3b | 68 (§0.5), 526 (§6) | The bypass "has been tested directly in an evolved robot **once**"; "**Tested once**, mixed" | Line 497 correctly says "the only direct test … **found**". An independent search (below) found no other test. But §9 itself lists Paul (2005, *Adaptive Behavior*) as an unread lead, and its citation context calls morphology "an extra-dimensional bypass". | Say "once, as far as a directed search found (Paul 2005 not yet read)". | Low–medium |
| F4 | 387 (§4.2) | Taylor & Massey's fixes include "use force-limited velocity-constraint actuators" | Their text: "we used orientation based proportional-derivative (PD) actuators". FLVCs appear only in a footnote: "New types of actuators **are now available** … ‘force limited velocity constraints’ (FLVCs) … ideal for modeling realistic virtual muscle responses" (tim-taylor.com/papers/taylor2001recent.pdf). | "…and they point to newly available force-limited velocity-constraint actuators (MathEngine) and dashpots (Havok) as more stable effectors." | Low |
| F5 | 502 (§6 table) | 3 radii genes "**beat** control-only evolution" | "variable morphology populations **tend to outperform** fixed morphology populations" (Fig. 4a). No statistical test is reported. Also, the Fig. 3 caption says "30 independent evolutionary runs" for the mass-block sets, where Table 2 and the text say 20. That inconsistency is in the source; the review's 20 follows Table 2 and is right. | "outperformed on average (no significance test reported)". | Low |
| F6 | 467–469 (§5) | Covert et al. 2013: "complex functions need rewarded intermediates, and deleterious mutations serve as stepping stones" | "Complex functions evolved by building on simpler functions … provided that these were also selectively favoured" is **Lenski et al. 2003** (PubMed 12736677). Covert et al. 2013 (PubMed 23918358) is the knock-out of deleterious mutations. | Attach the first clause to Lenski 2003. | Low |
| F7 | 20–23; 115; §8 numbering | "**Four** load-bearing claims were checked a second time", but three are listed. Cheney 2013 "(§4.3)" points to the reality-gap section; the charging proposal is in §10.3. Log `6-errata-gap.md` numbers the errata differently from §8: log E2 = Utimula, E3 = MIP, E4 = Mertan; §8 E2 = MIP, E3 = Mertan, E4 = Utimula. | — | Fix the count and the cross-reference, and add a mapping note between the log's numbers and §8's. | Editorial |
| F8 | 591 (§9), 101 | Kriegman article number, De Carlo volume and the full Bongard 2015 author list are "not seen" | Crossref: Kriegman *Sci. Rep.* **8: 13934** ✓. De Carlo *Evol. Intell.* **17(3): 1733–1749** (print 2024; online 2023-07-03). Bongard et al. 2015: Bongard, Bernatskiy, Livingston K., Livingston N., **Long J., Smith M.**, GECCO '15: **129–136**. Jakobi et al. 1995: 704–720 ✓. | Move these out of §9 and complete the entries. | Completion |

**No error found** in anything else I checked (below).

---

## 1. The load-bearing entries

Key to the "record" column:
- **CR**: Crossref record matches the authors, year, venue and pages.
- **PM**: PubMed abstract read.
- **FT**: full text read by me.

| entry | record | summary faithful? | notes |
|---|---|---|---|
| **Sims 1994a**, SIGGRAPH '94: 15–22, doi:10.1145/192161.192167 | CR ✓; author PDF ✓ (FT) | All three quotations are **verbatim**. The PDF ligature "ﬁrst" is the only difference. | Energy-leak ✓, actuator ✓, settle ✓ (it applies "for land environments"), time-step ✓. Discarding bodies for persistent interpenetration or too many parts ✓. **Per-joint gloss wrong: F1.** Sims uses adaptive Runge-Kutta-Fehlberg integration, which supports §4.1's "a better integrator" row. |
| **Sims 1994b** | CR ✓: *Artificial Life* 1(4): 353–372, doi:10.1162/artl.1994.1.4.353. The author PDF footer reads "Artificial Life IV Proceedings … MIT Press, 1994, pp28-39" ✓ | — | §8's handling of the 28–39 pages is correct. |
| **Conrad 1990**, *BioSystems* 24(1): 61–81 | CR ✓, PM 2224072 | ✓ against the abstract (peak-to-peak variation against stability; redundancy and weak interactions) | "Added dimensions turn isolated peaks into ridges" is the full-text bypass argument, which Bongard & Paul attribute to it. ScienceDirect was blocked, so I did not re-read the full text. |
| **Bongard & Paul 2001**, ECAL 2001, LNCS 2159: 401–412 | CR ✓; author PDF ✓ (FT, decoded) | ✓: population 300, 300 generations, 60 synapses; Table 2 gives genomes 60/63/60/68 and runs 30/30/20/20; "Only two of the 20 populations achieve stable locomotion in both cases"; no convergence of shape (centre-of-mass spread 0.52–0.57); one lineage event (15.03 → 23.17, suppressed 20.87); "the arbitrary inclusion of morphological parameters does not always yield better results" | "Beat" should be softened (F5). |
| **Watson, Ficici & Pollack 1999**, CEC 1999: 335–342 | CR ✓. The Crossref author field misspells "S.G. Ficiei"; the review spells it correctly. | The summary at line 200 rests on the **2002 RAS** paper. Its abstract (Brandeis page) reads: "eight robots … Controllers evolved by EE outperform a hand-designed controller in a simple application" ✓ | The 1999 full text was not read (IEEE). The EWLR-8 entry (pp. 14–22) matches the Brandeis page ✓. |
| **Cheney et al. 2018** *JRSI* 15(143): 20170937 | CR ✓, PM 29899155 | ✓: the abstract introduces "morphological innovation protection" | The fixed-morphology baseline is correctly held in §9. |
| **Mertan & Cheney 2026**, doi:10.1162/ARTL.a.476 | CR ✓: *Artificial Life*, issued and online **2026-09-04**, pp. 1–20, no volume yet | The arXiv v2 abstract (revised 2026-08-12, "accepted for publication in Artificial Life") supports E3's reading word for word | "Published 2026-09-04" ✓. |
| **Lehman et al. 2020**, *ALife* 26(2): 274–306 | CR ✓, PM 32271631, arXiv FT ✓ | The table quotations are verbatim: relax-potential-energy, the VoxCAD fix, "first few tenths of a second", "impossibly-strong grasshoppers", "adopt an adversarial mindset". Krcah's pole is "found only by watching": "observing the creatures' behaviors directly revealed …" ✓ | — |
| **Bredeche, Haasdijk & Prieto 2018**, *Front. Robot. AI* 5: 12 | CR ✓ | ✓: the abstract gives "a shift from … a parallel search method within small robot collectives (fewer than 10 robots) to … online distributed learning … in swarm-like collectives". The discussion treats evolving morphologies as a future prospect (Frontiers full text), which is consistent with line 226. | — |
| **Taylor & Massey 2001**, *ALife* 7(1): 77–87 | CR ✓, PM 11461690, author PDF (FT) | The quotations are verbatim, and "4 to 10" parts ✓. Their table characterises Lipson & Pollack's physics as quasi-static ✓ | **FLVC overstated: F4.** |
| **Krčah 2008**, ICES 2008, LNCS: 153–164 | CR ✓ (no volume in the record; it is LNCS 5216) | **Not re-checked.** Springer's full text is paywalled. The §3.3 "Validity testing" quotation rests on the review's own reading. | Treat it as the reviewer's reading, unconfirmed by a second person. |
| **Auerbach & Bongard 2014**, *PLoS CB* 10(1): e1003399 | CR ✓, PM, FT ✓ | "**Only** when complexity carried a cost" ✓. The full text says that without a cost, the icy environments "do not reflect a consistent relationship between environment and evolved morphological complexity". | "A capacity that costs nothing will be bought" is the review's inference, and is labelled as "For RBT-120/121". Acceptable. |
| **Cheney et al. 2013**, GECCO: 167–174 | CR ✓; author PDF (FT) | ✓: penalties multiply fitness by (1 − penalty/max); "analogous to the cost of expending energy to contract muscles" verbatim | Cross-reference slip: F7. |
| **Mühlenbein & Schlierkamp-Voosen 1993** I and "Science of breeding" | CR ✓ for both: *Evol. Comp.* 1(1): 25–49 and 1(4): 335–360 | Not re-read; MIT Press was blocked, and neither paper is in PubMed. The summary matches the papers' well-known content (the breeder's response equation R = h²S in the BGA). | Record-level only from me. |
| **Bedau et al. 1997**, ECAL97: 125–134 | Bedau's publication page ✓ (authors, title, editors, pages, MIT Press) | The "first neutral shadow" claim is attributed to Channon 2024, and correctly labelled "per Channon (2024)". | — |
| **Channon 2006**, *GPEM* 7(3): 253–281 | CR ✓ | Not re-read. The log relies on an S2 abstract. | — |
| **Channon 2024**, *ALife* 30(3): 345–355 | CR ✓, PM 38635908 | The abstract is consistent. The "random selection should be employed in the shadow" quotation comes from the author's copy on channon.net, which **I could not reach**, so it is unconfirmed by a second person. | — |
| **Williams & Lenton 2007**, *PNAS* 104(21): 8918–8923 | CR ✓, PM 17517642 | Consistent with the abstract (artificial ecosystem selection in an individual-based simulation). The High/Low/Random lines and the "no numerical h²" point come from the log's full-text reading. I could not re-open it: pnas.org returned 403, PMC served a JS challenge and Europe PMC returned 500. | Log 5 cites PMC1885603. |
| **Nygaard et al. 2021**, *NMI* 3(5): 410–419 | CR ✓ | ✓ against the Nature abstract: in situ morphological adaptation chosen from a learned model on sensed terrain, "most energy-efficient morphologies", "substantial performance improvements over a non-adaptive approach" | — |

---

## 2. Errata E1–E7 (§8), against the sources and our files at 152e2df

| # | our file at the cited lines | the source | verdict |
|---|---|---|---|
| E1 | P5:45 "(Miconi, 2011 …)", P5:456 and RBT-71 `citations-check.txt`:6 all attribute EPIA 2011 / doi:10.1007/978-3-642-24769-9_10 to Miconi ✓ | Crossref: **Tiago Baptista; Ernesto Costa**, "The Evolution of Foraging in an Open-Ended Simulation Environment", LNCS *Progress in Artificial Intelligence*: 125–137 | **Confirmed.** P5:46–47 (Miconi & Channon 2006; Miconi 2008) are genuinely Miconi's and are unaffected. |
| E2 | P7:780–782 (the review says 781–783) | See F2: the 2016 full text does propose protecting morphological innovations, as future work with initial results | **The erratum itself needs correcting (F2).** |
| E3 | P5:58–60 and P7:785–786 as quoted ✓ | arXiv:2508.17464 v2 abstract: "eliminates promising morphologies. **On the other hand**, … useful goal-switching, yielding morphology-controller pairs whose performance cannot be reached …" | **Confirmed**, and the suggested wording is faithful. |
| E4 | P5:45 groups Utimula with "open-ended foraging" ✓ | PubMed 39898762: reproduction and development of 3-D cell creatures; no foraging | **Confirmed.** Note that the PubMed and Crossref dates read "2024 Feb 25" for vol. 31(1) (online 2025-02-25); 2025 is the conventional year. |
| E5 | P5:57, P5:453 and P7:783–785 say "2025"/"accepted" ✓ | Crossref: published online 2026-09-04, doi:10.1162/ARTL.a.476 | **Confirmed.** |
| E6 | P5:450 has no volume, P5:461 no pages or DOI, P5:463 no DOI ✓ | Crossref: *GPEM* 17(4): 359–390 ✓; Chromaria 793–800, doi:10.7551/978-0-262-32621-6-ch128 ✓; Utimula doi:10.1162/artl_a_00466 ✓ | **Confirmed.** |
| E7 | P5:56–57 "this programme has never run it" ✓ | `runs/RBT-74/REPORT.md` lines 3, 7–16 and 215–219: `--protect-morphology 4`, verdict null, superseded by RBT-85; a body change costs 0.05–0.13 of bout score; −0.001 to −0.013 recovered | **Confirmed.** |

---

## 3. Random sample of 15 further entries

- **Method.** I listed every bold-headed bullet with a year or "et al." in §§1–7 (103 entries), removed the load-bearing list (leaving 87), and drew 15 with `random.seed(122); random.sample(pool, 15)` in Python 3.11. The script and its output are in `logs/sample-and-search.md`.

| line | entry | record | summary |
|---|---|---|---|
| 122 | Mertan & Cheney 2025, arXiv:2504.06523 | arXiv ✓ ("Accepted at GECCO 2025 … full paper") | ✓: "body mutations … break the robots' fragile brain-body co-adaptation"; Pollination "increases the success of body mutations" |
| 139 | Jelisavcic et al. 2019, *Front. Robot. AI* 6: 9 | CR ✓, PM 33501026 | Consistent with the abstract. "Especially under tight learning budgets" and "rose with body similarity" are not in the abstract; I did not re-read the full text. |
| 170 | Huang et al. 2024, CompetEvo, arXiv:2405.18300 | arXiv ✓ | ✓: "compared to fixed-morph agents … obtain advantages in combat scenarios" |
| 222 | Montanier et al. 2016, *Front. Robot. AI* 3: 38 | CR ✓ (article 38 from the DOI suffix) | ✓: "a very sparse communication network is required"; "population size (the larger the better)" |
| 230 | Soros & Stanley 2014, ALIFE 14: 793–800 | CR ✓ | Not re-read. The four conditions are standard, and log 2 has an S2 abstract. |
| 241 | Lehman & Stanley 2011, *Evol. Comp.* 19(2): 189–223 | CR ✓ | (no summary given) |
| 270 | Beer & Gallagher 1992, *Adapt. Behav.* 1(1): 91–122 | CR ✓ | Not re-read. |
| 291 | Liese, Polani & Uthmann 2001, *ALife* 7(2): 99–124 | CR ✓, PM 11580876 | ✓: "balance between sensor costs and agent performance … reflects the emission spectrum … help the agents significantly" |
| 367 | Krakovna et al. 2020, DeepMind blog | not re-fetched | The quotation is unchecked by me. It is a blog, so low stakes. |
| 370 | Amodei et al. 2016, arXiv:1606.06565 | arXiv ✓ (six authors as listed) | Reward hacking ✓. Trip wires are in the body text, which I did not re-read. |
| 412 | Koos, Mouret & Doncieux 2013, *IEEE TEC* 17(1): 122–145 | CR ✓ | The quotation was not re-checked (IEEE). |
| 455 | De Carlo et al. 2023 | CR ✓: **17(3): 1733–1749** (F8) | ✓ against the arXiv:2110.11187 abstract: heritability used to compare direct and indirect encodings. The arXiv version adds a sixth author, G. Meynen, who is not in the journal record; the review follows the journal. |
| 466 | Lenski et al. 2003, *Nature* 423: 139–144 | CR ✓, PM | (no summary; see F6) |
| 467 | Covert et al. 2013, *PNAS* 110(34): E3171–E3178 | PM ✓ (the pages come from PubMed; Crossref has none) | **F6** |
| 519 | Wu et al. 2016, *eLife* 5: e16965 | CR ✓, PM | ✓: "20^4 = 160,000 variants"; indirect paths "involving gain and subsequent loss of mutations" |

**Result.** All 15 records are correct. One summary merges two papers (F6). None fabricates a claim.

---

## 4. §9 UNVERIFIED items used in the body

I searched the body (§§0–8 and §10) for each §9 item: Balakrishnan & Honavar 1996, Mark et al. 1998, Paul & Bongard 2001 (IROS), Cheney 2018's fixed baseline, Clark & Amodei, Tobin, Matsushita, Paul 2005 and Inden & Jost.
- **None is cited as fact.**
- **Peng et al. appears in the body** (line 415), flagged there with "venue is unverified". That is acceptable.
- **The 1996 Balakrishnan paper** is mentioned only to say that it is unverified (line 296).
- **Clean.**

---

## 5. Claims of novelty

- **The search.** An independent search on 2026-09-27, covering 2023–2026: WebSearch, arXiv abstract pages and a Crossref `query.bibliographic`, with the queries listed in `logs/sample-and-search.md`. It is not systematic.

| claim | line | phrasing | closest hits | verdict |
|---|---|---|---|---|
| Nobody has compared evolved bodies with a strong hand-designed body at matched compute across tasks | 50 | **absolute** | Pagliuca & Nolfi 2021/22 (omitted from the review); RoboMoRe 2025 (8 tasks, LLM); Evolution Gym; "Co-design is powerful and not free" (Zhang et al. 2025, arXiv:2510.08368: control-only "often matches or exceeds co-design" when the baseline body is adequate, in reaching tasks only) | Partial neighbours only, but **hedge it** (F3). Zhang et al. 2025 is also worth a line in §1.4, since it is a recent "the fixed body is often enough" result. |
| Nobody has done it in a fitness-free economy | 50 | absolute | Bejjani et al. 2025: fitness-free, but only weights and colour evolve and there are no evolved bodies | No counterexample. Hedge it anyway; line 615 already says "still unoccupied (§7)", with §7's search caveat. |
| The combination (divergent lines, realised h², drift lines, two body classes) | 67, 479 | "was not found" ✓ | De Carlo 2023 (regression h² only) | No counterexample; the phrasing is correct. |
| Bongard & Paul is the only direct bypass test | 68, 497, 526 | 497 says "found" ✓; 68 and 526 are **absolute** | Nothing else found. Paul (2004) "Evolution of embodied intelligence" (Springer LNCS) and Paul (2005) come from the same group, and neither was read. | Hedge 68 and 526 (F3b). |
| Nothing catalogues measurement bugs | 618 | "We found nothing" ✓ | Kůdela 2023 (arXiv:2301.01984: centre-bias benchmark flaws); the CEC 2022 EA4Eig bug analysis; RL-evaluation work (Henderson et al. 2018; Agarwal et al. 2021). None is a catalogue of measurement-side bugs in ALife or EC. | The phrasing is fine. "No dedicated catalogue" would be more precise. |
| None of the §1.4 comparisons measured bodies apart from the score or removed the allowances | 186, 614 | absolute about the works listed | — | Fine as a statement about the works listed. Add "that we found" at 614. |

---

## 6. Could a reader mistake a known result for the programme's claim?

§10.2 credits prior work properly, and §3's "known result, not a new one" is exemplary. Three things to tighten:
1. **F1 runs the other way.** The review credits *Sims* with the per-joint idea, which is the programme's own. That matters for RBT-120's design document: say "Sims's area rule, applied per joint (our choice)".
2. **Line 400, "We re-derived it independently" (the settle protocol), and line 656, "arrived at independently".** Independence cannot be verified from the record, and a reader might take it as a priority claim. Suggested wording: "our protocol matches Sims's; it was written without reference to it". Or drop the sentence.
3. **Line 130, "an independent replication of the premise".** This is fine as it stands. RBT-74 measured the cost of a body change on our substrate, and the review credits Cheney for the premise.

---

## 7. What I could not check myself

- **Full texts not re-read**, because of paywalls or blocked hosts: Krčah 2008, Williams & Lenton 2007, Channon 2006 and 2024, Mühlenbein 1993, Watson 1999, Jelisavcic 2019, Koos 2013 and the Krakovna blog.
- **Where the review says it read those texts in full**, I found nothing inconsistent in the abstracts. Those readings are single-reviewer.
