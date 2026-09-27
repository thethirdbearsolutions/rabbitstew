### ERRATA.md line 43 — section 1. Papers / Paper 3 (`docs/paper-3-let-the-furniture-stop-me.md`)
| P3:104 | "the same ancestry-only noise model predicts about 102, so there selection, not drift, thinned the ancestry" | `--founder-model` models tournament selection with two elites. It "says nothing about drift versus selection" under survival or lexicase. (H8) | `runs/RBT-11/REPORT.md:70` | 2026-09-12 |

### ERRATA.md line 93 — section 1. Papers / Paper 7 (`docs/paper-7-five-instruments.md`)
| P7:781-783 | Cheney, Bongard, SunSpiral & Lipson (2016) "propose morphological innovation protection" | **E2, as corrected by CHECK F2:** the 2016 paper proposes protecting morphological innovations *as future work, with initial results*. The named, tested method (MIP) is Cheney et al. 2018, *J. R. Soc. Interface* 15: 20170937. Cite both, and cite 2018 for the mechanism. The first version of E2 wrongly said the 2016 paper "proposes nothing". **Lines:** the claim is at :781-783 (:780 is blank). REVIEW:579 and CHECK F2 give 780-782; REVIEW's first version had it right. | REVIEW:579 (as amended); CHECK:33 (F2), :82 (#404, #406) | 2026-09-27 |

### ERRATA.md line 64 — section 1. Papers / Paper 5 (`docs/paper-5-the-blind-forager.md`)
| P5:220 | "to 0.246, because patch luck is within-season variance" | As above. (H25, H75) | `docs/foraging-world.md:325` | 2026-09-14 |

### ERRATA.md line 72 — section 1. Papers / Paper 5 (`docs/paper-5-the-blind-forager.md`)
| P5:463 | Utimula (2025), with no DOI | **E6:** doi:10.1162/artl_a_00466. | REVIEW:583; CHECK:86 | 2026-09-27 |

### ERRATA.md line 110 — section 2. Published progress reports / Report 1 (`docs/progress-reports/2026-09-27/index.html`)
| `…/2026-09-27/index.html:290` | "only **2–3%** survives 16 generations of mutation alone" | **1.3%.** The working compass's persistence at depth 16 under the default operator is 0.0127. | P10:410; report 2 draft, PR #398 (pending) | 2026-09-27 |

### ERRATA.md line 131 — section 3. Registered outputs / None
| `runs/RBT-90/part2-readout.txt:49` | "SPLITS: a founding-population property" | The gloss is withdrawn: fate "varies across runs; one run per founding population cannot separate founders from history". RBT-105 then found fate reverses in 5 of 14 replicates from identical founders. (H49) | `runs/RBT-90/PART2-VERDICT.md:16`; `runs/RBT-105/REPORT.md:47` | 2026-09-26 |

### ERRATA.md line 128 — section 3. Registered outputs / None
| `runs/RBT-104/readout.txt:58` | "VOID … the side effect, not link-weight reach, is what was measured" | **VOID by design.** The install control never applied the arm's `--link-scale 8`, and "a compass built at the default scale is invisible in a host built at ×8". The question is unanswered. "Hosts mask" is withdrawn. (H63) | `runs/RBT-104/readout-adversary/READOUT-ADVERSARY.md:13-30`; `runs/RBT-104/REPORT.md:36-60`; P10:243-271 | 2026-09-27 |

### ERRATA.md line 150 — section 4. Run reports and analysis files / None
| `runs/sim-audit/CHAOTIC-DOC.md:214, 234, 247-249` | "drift reaches a gain that earns anything measurable (a ≥ 32) in **0.70%** of lineages" | 0.70% is a depth-4 truncation of a divergent series (ρ 1.565–4.92), and an information-free sensor pair clears it at the same rate. The direct motif arrives 0 of 10,000. (H31) | P7:421-430, 469-474; `runs/RBT-78/REPORT.md:91-99`; P8:116-120, 660 (W4) | 2026-09-14 |

### ERRATA.md line 159 — section 4. Run reports and analysis files / None
| `runs/RBT-91/resign_arrivals.py:239-242` | "Against the first paying rung (6.8664)" | :241-242 flag the gains as whole-brain, but not the 42.2% classifier. As in §3. (H41) | P8:349-356, 669 | 2026-09-26 |

### ERRATA.md line 163 — section 4. Run reports and analysis files / None
| `runs/RBT-13/REPORT.md:90` | "A 57% cut, at about two standard errors" | At 64 paired seeds: 29%, t = +2.15. **Dies** under the 64-seed rule. (H22) | `runs/RBT-38/REPORT.md:37` | 2026-09-12 |

### ERRATA.md line 195 — section 5. Design notes and other docs / None
| `docs/rbt-91-weight-scale-decision.md:80-87` | "the compass does not pay on these populations at all … RBT-69 … negative at every magnitude" | RBT-69's negatives were the W4b sign installed on mostly forward-driving robots, which makes an anti-compass. Correctly signed, **12 of 12** robots pay from a = 32 (6 of 12 resolved). RBT-97 withdrew the premise. (H43, H75) | P8:508-523; `runs/RBT-97/ADVERSARY.md:153` | 2026-09-26 |

### ERRATA.md line 208 — section 6. Commit messages / None
| `935bcbf` | "P-801 in its own world (26 items, 3 patches, **flat**)"; gains "+0.507 to +1.324" | As above. The gain size follows food patchiness, not density or regrowth (exploratory). | `runs/RBT-103/REPORT.md:43-53, 83-91, 204-206` | 2026-09-26 |

