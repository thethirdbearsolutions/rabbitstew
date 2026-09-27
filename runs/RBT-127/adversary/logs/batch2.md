### ERRATA.md line 42 — section 1. Papers / Paper 3 (`docs/paper-3-let-the-furniture-stop-me.md`)
| P3:108 | "as one seed of two did under condition A" | As above. (H10) | `runs/RBT-9/REPORT.md:33` | 2026-09-12 |

### ERRATA.md line 94 — section 1. Papers / Paper 7 (`docs/paper-7-five-instruments.md`)
| P7:784-785 | *Evolutionary Brain-Body Co-Optimization …* "(2025)", with no authors | **E5:** Mertan & Cheney, *Artificial Life*, published online 2026-09-04, doi:10.1162/ARTL.a.476. Cite it as 2026 and name the authors. | REVIEW:582; CHECK:85 | 2026-09-27 |

### ERRATA.md line 60 — section 1. Papers / Paper 5 (`docs/paper-5-the-blind-forager.md`)
| P5:56-57 | "morphological innovation protection … this programme has never run it" | **E7:** it has, as RBT-74 (`--protect-morphology 4`). The paired verdict was null at four seeds and superseded by RBT-85. The within-run finding stands: a body change costs 0.05–0.13 of bout score, and four controller-only rounds recover none of it. | REVIEW:584; CHECK:87 | 2026-09-27 |

### ERRATA.md line 111 — section 2. Published progress reports / Report 1 (`docs/progress-reports/2026-09-27/index.html`)
| `…/2026-09-27/index.html:292` | "In the world where the compass pays more, **selection outran the erasure**" | **Withdrawn.** HELD fires *below* the balance point, so HP's 9 of 10 does not imply any selection strength. "No s was estimated for HP." | P10:506-511; `docs/paper-10/adversary/PAPER-ADVERSARY.md:120-133` (F6); report 2 draft, PR #398 (pending) | 2026-09-27 |

### ERRATA.md line 132 — section 3. Registered outputs / None
| `runs/RBT-90/part2-readout.txt:54` (the label also at :28) | depth in [15, 26]: "A PROPERTY OF THE SEARCH" | "A property of this economy's **demography**, not of the search": a random-parentage null lands inside the interval 98% of the time. (H49) | `runs/RBT-90/PART2-VERDICT.md:15` | 2026-09-26 |

### ERRATA.md line 136 — section 3. Registered outputs / None
| `runs/RBT-102/aggregate.txt:3` | "drift reference … upper bound p_u = 0.0520%" | p_u used the wrong (evolved) parents. The matched drift rate is 0.0076%, about 5.5× lower, and zero is the modal drift outcome (81%). The verdict does not move. (H61) | `runs/RBT-102/REPORT.md:132-137`; `runs/RBT-102/adversary/ADVERSARY.md:70-148` | 2026-09-26 |

### ERRATA.md line 173 — section 4. Run reports and analysis files / None
| `runs/RBT-23/REPORT.md:83` | "s590 only, and weakly (1.38 → 1.00, −28 %)" | **Dies and is vetoed:** 36 of 64 seeds unmoved. (H22) | `runs/RBT-38/REPORT.md:42` | 2026-09-12 |

### ERRATA.md line 166 — section 4. Run reports and analysis files / None
| `runs/RBT-17/REPORT.md:54` | bests "lose a third and 58% of their solo yield" | The 590 best survives at 35%, not 58%. (H22) | `runs/RBT-38/REPORT.md:30` | 2026-09-12 |

### ERRATA.md line 148 — section 4. Run reports and analysis files / None
| `runs/compass-spike/REPORT.md:50, 102, 106-110` | "Result: nothing, at any setting"; "a bolted-on compass earns nothing" | **Transposed drive.** The Pioneer's wheel hinge axes are antiparallel, so the spike installed a smell-gated pirouette. Wired correctly, the compass earns **+0.897 items (+59%, 7 of 7)**. The finding is "withdrawn, not amended". The report has **no erratum**. (H28) | `runs/sim-audit/CHAOTIC-DOC.md:14-22, 93-111`; P7:282-321 | 2026-09-13 |

### ERRATA.md line 197 — section 5. Design notes and other docs / None
| `docs/rbt-91-weight-scale-decision.md:260-275` | item 1: "first paying rung … did not replicate … negative at every magnitude"; item 3: "**n = 4** … Re-signing … has not been done … roughly half … anti-compasses" | Item 1 as at :80-87. Item 3: the same document later measured 84 in 200,000 and re-signed all 84 (:26-33, :89-101), and P8 re-reads that as 30/28, 51.7%. Item 2 (:266-268, n = 4) is weakened, not withdrawn: :61-62 says it was nearer two independent draws. (H43, H75) | P8:349-370, 508-523, 668 | 2026-09-26 |

### ERRATA.md line 192 — section 5. Design notes and other docs / None
| `docs/runs/RBT-69-compass-replication.md:119-121` | "drive **forward** (pooled travel azimuth minus body yaw +5.1°, six of seven within ±10°)" | An independent re-implementation measures +12.0°, R = 0.430: five forward and two backward. Direction of travel is a free population parameter. Measure it first. (H35) | P7:396-400 | 2026-09-14 |

### ERRATA.md line 216 — section 7. Withdrawn before publication (noted for completeness) / None
| RBT-118 prior, first draft of `runs/RBT-118/prior/ANALYSIS.md:96` and the RBT-118 post (not in the current tree) | "In income, the pattern is 'behind early, ahead late'. That is the 2005 proposal's **two-phase shape**." | Withdrawn before merge. The early deficit is random founders that cannot move, set against working bodies (seasons 0–10, 30 of 30). The late lead is a work-price lead on **random terrain**. It reverses below a median 0.018 per kJ, and on flat ground on 21 of 29 histories. The faunas never compete, so this is **not** a test of the 2005 prediction. The merged ANALYSIS.md carries the replacement. | `runs/RBT-118/prior-adversary/ADVERSARY.md:51, 212-222` (MUST-FIX 1); PR #399, #402 | 2026-09-27 |

