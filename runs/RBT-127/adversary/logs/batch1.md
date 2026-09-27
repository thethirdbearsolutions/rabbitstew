### ERRATA.md line 57 — section 1. Papers / Paper 5 (`docs/paper-5-the-blind-forager.md`)
| P5:244 | "holds at the four-robot baseline and reverses at eight" | As above. (H26) | `docs/held-out-challenges.md:97` | 2026-09-19 |

### ERRATA.md line 59 — section 1. Papers / Paper 5 (`docs/paper-5-the-blind-forager.md`)
| P5:456 | "Miconi, T. (2011). The evolution of foraging in an open-ended simulation environment. EPIA 2011" | **E1:** Baptista, T. & Costa, E. (2011), *Progress in Artificial Intelligence* (EPIA 2011), LNCS: 125–137. | REVIEW:578; CHECK:81 | 2026-09-27 |

### ERRATA.md line 58 — section 1. Papers / Paper 5 (`docs/paper-5-the-blind-forager.md`)
| P5:45 | "(Miconi, 2011; Utimula, 2025)" as "open-ended foraging with no explicit fitness" | **E1:** the EPIA 2011 paper (doi:10.1007/978-3-642-24769-9_10) is by **Tiago Baptista & Ernesto Costa**, not Miconi. P5:46-47 (Miconi & Channon 2006; Miconi 2008) are Miconi's and stand. **E4:** Utimula (2025) is about reproduction and development of 3-D cell creatures, not foraging; P5:69-70 describes it correctly. | REVIEW:578, 581; CHECK:81, 84 (#404, #406) | 2026-09-27 |

### ERRATA.md line 81 — section 1. Papers / Paper 6 (`docs/paper-6-the-cow-is-the-correct-answer.md`)
| P6:171 | "halved yield heritability from 0.51 to 0.246" | As at P5:189. (H25, H75) | `docs/foraging-world.md:325` | 2026-09-14 |

### ERRATA.md line 123 — section 3. Registered outputs / None
| `runs/RBT-112/readout.txt:40` | "VERDICT Z: FALSIFIED … did not let selection hold the compass; **the operator is not the stall**" | `--global-bias-sigma 0` froze **all** global biases, host and planted, and SE-Z failed (income +0.160). Read it as "the bias walk is not what stops selection holding the compass" (s < about 0.1), not "the operator is irrelevant". Under S = 0 the best lines do carry and use the compass (5 COMPASS lines against 0). (H65) | `runs/RBT-112/READOUT.md:29-40`; `runs/RBT-112/readout-adversary/ADVERSARY.md:33-43, 154-203`; P10:436-448 | 2026-09-27 |

### ERRATA.md line 125 — section 3. Registered outputs / None
| `runs/RBT-105/aa_spread.txt:4` | "this spread is therefore an **UPPER BOUND** on a challenge arm's own A/A spread" | The spread does not grow with time since divergence (time-matched 0.109). It is "a comparator of scale … not a bound in either direction, and not a null for any event". (H60) | `runs/RBT-105/readout-adversary/READOUT-ADVERSARY.md:236-287`; P9:846-858; `runs/RBT-105/REPORT.md:12` | 2026-09-26 |

### ERRATA.md line 151 — section 4. Run reports and analysis files / None
| `runs/RBT-45/REPORT.md:143-144` (also :8-10, 266-268, 320-324) | CROSSED is "the circuit that steers up a gradient", "the only one that steers"; re-aim RBT-42's operator "at the crossed pairing" | As at P6:126-128. The recommendation is withdrawn. (H29) | `runs/sim-audit/CHAOTIC-DOC.md:113-116`; P8:628-629, 657 | 2026-09-13 |

### ERRATA.md line 171 — section 4. Run reports and analysis files / None
| `runs/RBT-22/REPORT.md:3, 20` | "found that the i/(1+i) squash saturates"; "Normalising recovers most of what the saturation cost" | As at P6:154. (H20) | `runs/sim-audit/CHAOTIC-DOC.md:182-188` | 2026-09-13 |

### ERRATA.md line 177 — section 4. Run reports and analysis files / None
| `runs/RBT-113/PREREGISTRATION.md:341-344` (the phrase at :343) | "the up line **learns to eat**" | **"Learns to move, and eats by covering ground."** Blind variants eat 0.913 and decoy variants 0.934, against 0.854 intact. 61% of up-line members carry no food sensor, and ground covered rises about 6×. It is the blind mower of paper 6, evolving from random founders under imposed selection. (H70) | `runs/RBT-113/readout-adversary/ADVERSARY.md:214` (M2); `runs/RBT-113/REPORT.md:84, 179` (#393, #394) | 2026-09-27 |

### ERRATA.md line 153 — section 4. Run reports and analysis files / None
| `runs/RBT-59/REPORT.md:77-78, 84-86` | "`max_age` 15 would buy **four times the search depth**" (recommended) | "The lever works and the recommendation was wrong": `--max-age 15` bought 3.4× the depth and a worse population (heritability 0.51 → 0.25; yield fell). (H39) | `runs/RBT-60/REPORT.md:106-114` | 2026-09-13 |

### ERRATA.md line 191 — section 5. Design notes and other docs / None
| `docs/foraging-world.md:288` | "a summed smell squashed by i/(1+i) saturates at long range" | As at P6:154. (H20) | `runs/sim-audit/CHAOTIC-DOC.md:182-188` | 2026-09-13 |

### ERRATA.md line 207 — section 6. Commit messages / None
| `c42e4f7` | "RBT-90's world is 12 items on random terrain; P-801's is 26 in three patches on **flat**." | Terrain is random in every world. P-801 does not regrow within a bout, and RBT-90 regrows instantly. The world control was exploratory, with no pre-posted attribution rule. | `runs/RBT-103/REPORT.md:43-53, 192-206` | 2026-09-26 |

