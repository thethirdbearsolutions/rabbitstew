# Twenty years on: a verified review of the prior art

*RBT-122, 2026-09-27. This review extends the programme's existing one; it does not replace it.
The existing review is in three places:*
- *paper 5 §0, "Where this sits, and what is and is not new in it", and its "External sources" list;*
- *its verification log, `runs/RBT-71/citations-check.txt` (2026-09-14);*
- *paper 7 §7, "Related work".*

*Their verified entries are reused here without a second check, apart from the corrections in §8. The effort went where they are thin:*
- *the evolution of perception;*
- *simulator exploits, and what others did about them;*
- *evolvability benchmarks;*
- *the extradimensional bypass;*
- *embodied evolution after Watson, Ficici & Pollack;*
- *work since 2025.*

**How the citations were checked.**
- **The bar.** Every reference below was matched against a real record for authors, year, title and venue: a Crossref DOI record, a publisher or proceedings page, arXiv, PubMed, dblp, or the author's own page.
- **The logs.** The six logs in `docs/prior-art/verification/` record, for each entry, which record was used and whether the full text, the abstract or only the record was read. Where a summary below rests on the abstract alone, it says so.
- **Checked twice.** Four load-bearing claims were checked a second time against the primary text:
  - Sims's actuator-strength rule and his settling protocol;
  - the Cheney VoxCAD penetration fix, as reported in Lehman et al.;
  - the Baptista & Costa authorship (§8, E1);
  - the Mertan & Cheney 2026 publication record (§8, E5).
- **Independent citation check.** An adversary then checked the review (PR #406, `docs/prior-art/citation-check/CHECK.md`, verdict ACCURATE-WITH-FIXES). This revision applies its F1–F8 and its §6 items, as the coordinator ruled.
- **What could not be verified** is in §9, and nothing in §9 is cited in the body.
- **Limits.** This is a directed search, not a systematic review. It was done from a container: dblp and the MIT Press pages were intermittently unreachable, and records were confirmed through Crossref or PubMed instead.

**Ticket shorthand.**

| ticket | what it is |
|---|---|
| RBT-113 | the evolvability benchmark |
| RBT-115 | the return to the 2005 question |
| RBT-116 | the extradimensional bypass |
| RBT-117 | the selection-response comparison |
| RBT-118 | the head-to-head in the ecology |
| RBT-119 | progress report 2 |
| RBT-120 | the motor budget |
| RBT-121 | the loophole audit |

---

## 0. The short answers

1. **Has anyone run the 2005 proposal's side-by-side comparison properly?** Partly, and only in narrow settings (§1.4).
   - Controlled comparisons between an evolved or changing body and a fixed one exist, and mostly favour the evolving body:
     - Bongard 2011; Bongard et al. 2015; Ha 2019;
     - Nygaard et al. 2021 (*Nature Machine Intelligence*);
     - Evolution Gym.
   - But in every one of them the body space is small or parametric, or the comparison is a benchmark aside.
   - **Not found in a directed search:** a study pairing open-ended body evolution with a strong hand-designed body at *explicitly matched* compute across tasks, or any such comparison in a fitness-free economy (§7). The nearest neighbours:
     - Pagliuca & Nolfi, co-adapted bodies against fixed hand-designed ones;
     - RoboMoRe, which is LLM-driven, with compute not stated;
     - Evolution Gym.

     A 2025 counterpoint finds that a control-only search on an adequate fixed body often matches co-design (Zhang et al.; §1.4).
   - The careful recent work says the joint search is the problem: co-optimisation reaches pairs a fixed-body search cannot, and then undervalues and discards new bodies (Cheney et al. 2016, 2018; Mertan & Cheney 2024, 2026).
2. **Simulator exploits: what did others do?** Sims (1994) had already fixed three of our four exploits, in one paragraph each (§4.2):
   - an effector-strength cap proportional to cross-sectional area, not mass;
   - a friction-free, force-free settle before scoring;
   - timestep reduction to bound penetration.

   Cheney's group fixed a ground-penetration exploit with contact damping, a minimum body size and a timestep rule. The field's general advice is to budget capacity by a quantity that grows more slowly than mass, to run validity and stability checks, and to measure behaviour directly.
3. **Why is perception hard to evolve?** In others' work it evolved when the reward could not be collected by coverage, and when a minimal version of the sensor already paid (§3).
   - Rewards that coverage cannot collect: a single source, a charger to return to on limited energy, a landmark goal, a category decision.
   - The theory literature says a blind strategy is the correct answer when cues are short-range, targets are sparse and the environment rarely changes. That is paper 6's "the cow is the correct answer", already in the literature.
4. **Evolvability benchmarks.** Each part of RBT-113 has a precedent (§5):
   - up, down and control lines, and realised h² (Falconer & Mackay; Hill & Caballero);
   - R = h²S inside a genetic algorithm (Mühlenbein & Schlierkamp-Voosen 1993);
   - random-selection "shadow" controls (Bedau et al. 1997; Channon 2006, 2024);
   - high, low and random lines in an artificial-life simulation (Williams & Lenton 2007).

   The combination, with two body classes, was not found.
5. **The extradimensional bypass** has been tested directly in an evolved robot once, as far as a directed search found (Paul 2005 not yet read): Bongard & Paul (2001), with mixed results (§6). Three extra morphological genes helped on average; eight did not.

---

## 1. Body–brain co-evolution after Sims

The programme's existing review already covers these, verified in RBT-71 and not repeated here:
- Sims (1994a, b);
- Cheney, Bongard, SunSpiral & Lipson (2016, 2018);
- Mertan & Cheney (2025, now 2026: see §8).

### 1.1 The founding line

- **Lipson, H. & Pollack, J. B. (2000).** Automatic design and manufacture of robotic lifeforms. *Nature* 406: 974–978. [doi:10.1038/35023115](https://doi.org/10.1038/35023115).
  - Bars, linear actuators and neurons were evolved together for locomotion in a "limited universe" simulation, then fabricated automatically, and they worked.
  - Taylor & Massey (2001, §4) list its simulator as quasi-static energy minimisation, a deliberately conservative physics that leaves little dynamic energy to harvest.
  - **For RBT-121:** conservative physics is one of the field's standing answers to exploits.
- **Pollack, J. B., Lipson, H., Hornby, G. S. & Funes, P. (2001).** Three generations of automatically designed robots. *Artificial Life* 7(3): 215–223. [doi:10.1162/106454601753238627](https://doi.org/10.1162/106454601753238627).
  - A position and review paper arguing that body and controller should evolve together. It is the 2005 proposal's reference [7], and the proposal's page range 215–223 is correct.
- **Hornby, G. S. & Pollack, J. B. (2002).** Creating high-level components with a generative representation for body-brain evolution. *Artificial Life* 8(3): 223–246. [PubMed 12537684](https://pubmed.ncbi.nlm.nih.gov/12537684/).
  - GENRE co-evolves body and brain through a generative, reusing encoding. It beat a direct encoding on locomotion, faster and to higher fitness.
  - The comparison is between encodings, not between evolved and fixed bodies. It bears on the 2005 proposal's own caveat about direct encodings, which the follow-up paper §6 repeats.
- **Pfeifer, R. & Bongard, J. (2006).** *How the Body Shapes the Way We Think.* MIT Press. [publisher page](https://mitpress.mit.edu/9780262537421/how-the-body-shapes-the-way-we-think/).
  - The embodied-cognition case: morphology does computational work, so body and brain should be designed together.
  - Background only.

### 1.2 The Bongard, Cheney and Lipson line: controlled comparisons with a fixed body

- **Bongard, J. (2011).** Morphological change in machines accelerates the evolution of robust behavior. *PNAS* 108(4): 1234–1239. [doi:10.1073/pnas.1015390108](https://doi.org/10.1073/pnas.1015390108). Full text read.
  - Phototaxis controllers were evolved for simulated quadrupeds and hexapods, against a **fixed, upright legged body** as the control.
  - Robots whose body changed from legless to legged, within a lifetime and over evolutionary time, found gaits significantly faster, and their gaits were more robust.
  - The change is a scheduled developmental trajectory, not open-ended body search, and the paper does not cite Conrad.
  - **For RBT-116:** a related result ("changing the body makes the control search easier"), but not a bypass test.
- **Bongard, J. C., Bernatskiy, A., Livingston, K., Livingston, N., Long, J. & Smith, M. (2015).** Evolving robot morphology facilitates the evolution of neural modularity and evolvability. *GECCO 2015*: 129–136. [doi:10.1145/2739480.2754750](https://doi.org/10.1145/2739480.2754750). Abstract only. Authors and pages are from Crossref (citation check F8).
  - Simulated grippers were evolved with the body **co-evolving or held fixed**.
  - Modular controllers evolved only when the body co-evolved and fitness also selected for robust behaviour. Evolved-body robots grasped better.
- **Auerbach, J. E. & Bongard, J. C. (2014).** Environmental influence on the evolution of morphological complexity in machines. *PLoS Computational Biology* 10(1): e1003399. [doi:10.1371/journal.pcbi.1003399](https://doi.org/10.1371/journal.pcbi.1003399).
  - Selection for locomotion drove morphological complexity above chance.
  - **Only when complexity carried a cost** did complex environments evolve more complex bodies than simple ones.
  - **For RBT-120/121:** a capacity that costs nothing (our gear) will be bought whether or not it helps the task.
- **Lehman, J. & Stanley, K. O. (2011).** Evolving a diversity of virtual creatures through novelty search and local competition. *GECCO '11*: 211–218. [doi:10.1145/2001576.2001606](https://doi.org/10.1145/2001576.2001606).
  - Creatures "tend to converge to a single morphology because selection therein greedily rewards the morphology that is easiest to exploit".
  - Novelty search with local competition keeps diverse, functional bodies in one run.
  - **For the follow-up paper's founder collapse** (2–6 of 20 founders survive), and for RBT-121 B.
- **Cheney, N., MacCurdy, R., Clune, J. & Lipson, H. (2013).** Unshackling evolution: evolving soft robots with multiple materials and a powerful generative encoding. *GECCO 2013*: 167–174. [doi:10.1145/2463372.2463404](https://doi.org/10.1145/2463372.2463404). Full text read.
  - CPPN-encoded voxel soft robots were evolved under fitness **penalties on voxel count and on the amount of actuated material** ("analogous to the cost of expending energy to contract muscles").
  - Penalties changed body plans without much loss of performance. With an actuation cost, evolution used more passive material.
  - **For RBT-120:** a direct precedent for charging for actuator capacity rather than for actuator use alone (§10.3).
- **Kriegman, S., Cheney, N. & Bongard, J. (2018).** How morphological development can guide evolution. *Scientific Reports* 8: 13934. [doi:10.1038/s41598-018-31868-7](https://doi.org/10.1038/s41598-018-31868-7).
  - With development, evolution favours body plans robust to controller change. Those bodies canalise while controllers keep evolving.
- **Pagliuca, P. & Nolfi, S. (2022).** The dynamic of body and brain co-evolution. *Adaptive Behavior* 30(3): 245–255 (online 2021). [doi:10.1177/1059712321994685](https://doi.org/10.1177/1059712321994685); [arXiv:2011.11440](https://arxiv.org/abs/2011.11440). Abstract only. Added from the citation check (F3).
  - "Robots with co-adapted body and control traits outperform robots with fixed hand-designed morphologies."
  - "The advantage is not due to the selection of better morphologies but rather to the mutual scaffolding process" between body and control traits. They also report that "morphological variations do not necessarily have destructive effects on robot skills".
  - Another evolved-against-hand-designed comparison. The body is parametric or constrained to a bauplan.
  - **For RBT-118:** a positive result whose mechanism, scaffolding, is the opposite of Cheney's "body mutations break controllers".
- **Mertan, A. & Cheney, N. (2024).** Investigating premature convergence in co-optimization of morphology and control in evolved virtual soft robots. *EuroGP 2024*, LNCS 14631: 38–55. [doi:10.1007/978-3-031-56957-9_3](https://doi.org/10.1007/978-3-031-56957-9_3).
  - The reverse comparison: **body-only evolution under a fixed open-loop controller** beat body–brain co-optimisation (all P < 0.005).
  - Bodies found that way, re-paired with trained controllers, beat co-optimised pairs in 3 of 4 settings.
  - Good bodies exist; co-optimisation does not find them.
- **Mertan, A. & Cheney, N. (2025).** Controller distillation reduces fragile brain-body co-adaptation and enables migrations in MAP-Elites. *GECCO 2025.* [arXiv:2504.06523](https://arxiv.org/abs/2504.06523). Abstract only.
  - Body mutations "break the robots' fragile brain-body co-adaptation". Distilled generalist controllers let more body mutations succeed.
- **Song et al. (2026).** Shaping the evolutionary dynamics of robot morphology via adaptive control learning. [arXiv:2608.23100](https://arxiv.org/abs/2608.23100). Preprint, abstract only.
  - Independent support for the same point: "premature fitness evaluation systematically underestimates true potential and biases selection towards fast learners."

**The programme has already run this line's remedy.** RBT-74 put morphological innovation protection on the arena (`--protect-morphology K`).
- The verdict was null at four seeds (superseded on the paired number by RBT-85).
- Its within-run result stands: a body change costs 0.05–0.13 of bout score immediately, and four controller-only rounds recover none of it.
- **Cheney's premise holds on this substrate; the remedy did not act.** That is an independent replication of the premise.

### 1.3 The Eiben group, real-world evolution, and machine-learning co-design

- **Eiben, A. E. & Smith, J. (2015).** From evolutionary computation to the evolution of things. *Nature* 521: 476–482. [doi:10.1038/nature14544](https://doi.org/10.1038/nature14544).
  - A perspective: evolution moving into physical hardware, bodies included. Background.
- **Eiben, A. E., Bredeche, N., Hoogendoorn, M., Stradner, J., Timmis, J., Tyrrell, A. M. & Winfield, A. (2013).** The Triangle of Life: evolving robots in real-time and real-space. *ECAL 2013*: 1056–1063. [doi:10.7551/978-0-262-31709-2-ch157](https://doi.org/10.7551/978-0-262-31709-2-ch157).
  - A framework of birth (morphogenesis), infancy (learning a controller for the new body) and maturity (reproduction).
  - The infant-learning stage is this group's answer to the body–brain mismatch that Cheney names.
- **Jelisavcic, M., Glette, K., Haasdijk, E. & Eiben, A. E. (2019).** Lamarckian evolution of simulated modular robots. *Frontiers in Robotics and AI* 6: 9. [doi:10.3389/frobt.2019.00009](https://doi.org/10.3389/frobt.2019.00009).
  - Offspring inheriting their parents' *learned* controllers gained clearly, especially under tight learning budgets. The gain rose with parent–offspring body similarity.
- **Luo, J., Stuurman, A. C., Tomczak, J. M., Ellers, J. & Eiben, A. E. (2022).** The effects of learning in morphologically evolving robot systems. *Frontiers in Robotics and AI* 9: 797393. [doi:10.3389/frobt.2022.797393](https://doi.org/10.3389/frobt.2022.797393).
  - Infant learning raised performance and changed which bodies evolved. The "learning delta" grew over generations.
  - **For RBT-118:** in this literature, a holistic body without lifetime learning is the handicapped arm. Rabbitstew has no lifetime learning.
- **Nygaard, T. F., Martin, C. P., Torresen, J., Glette, K. & Howard, D. (2021).** Real-world embodied AI through a morphologically adaptive quadruped robot. *Nature Machine Intelligence* 3(5): 410–419. [doi:10.1038/s42256-021-00320-3](https://doi.org/10.1038/s42256-021-00320-3).
  - A real quadruped that changes its leg lengths for the sensed terrain improved substantially on energy efficiency outdoors, over a **fixed-morphology** configuration.
  - The body is chosen from a learned model, not evolved online.
- **Nygaard, T. F., Samuelsen, E. & Glette, K. (2017).** Overcoming initial convergence in multi-objective evolution of robot control and morphology using a two-phase approach. *EvoApplications 2017*, LNCS 10199: 825–836. [doi:10.1007/978-3-319-55849-3_53](https://doi.org/10.1007/978-3-319-55849-3_53).
  - Co-evolution converges early. The fix: evolve both, then freeze the body and re-evolve the controller.
  - **For RBT-118:** a principled "late phase" protocol.
- **Nygaard, T. F., Martin, C. P., Samuelsen, E., Torresen, J. & Glette, K. (2018).** Real-world evolution adapts robot morphology and control to hardware limitations. *GECCO 2018*: 125–132. [doi:10.1145/3205455.3205567](https://doi.org/10.1145/3205455.3205567).
  - With joint torque and speed cut by lowering the supply voltage, evolution adapted both body and control and kept comparable performance at low and moderate speeds.
  - **For RBT-120:** evolution works within an actuator budget set independently of the body.
- **Ha, D. (2019).** Reinforcement learning for improving agent design. *Artificial Life* 25(4): 352–365. [doi:10.1162/artl_a_00301](https://doi.org/10.1162/artl_a_00301).
  - The cleanest head-to-head with a **stock hand-designed body under the same training pipeline.**
  - BipedalWalker: learned body 359 against 347 for the fixed body.
  - BipedalWalkerHardcore: 335 ± 37 against 313 ± 53, solved in about 12 h instead of about 40 h.
  - Only leg dimensions varied; the topology was fixed.
- **Bhatia, J., Jackson, H., Tian, Y., Xu, J. & Matusik, W. (2021).** Evolution Gym: a large-scale benchmark for evolving soft robots. *NeurIPS 34.* [proceedings page](https://proceedings.neurips.cc/paper/2021/hash/118921efba23fc329e6560b27861f0c2-Abstract.html).
  - Thirty-two tasks, with design optimisers paired with PPO. Evolved robots "often grow to resemble existing natural creatures while outperforming hand-designed robots". All methods failed on the hardest tasks.
  - The body lives on a fixed voxel grid, must be connected, and must carry an actuator. The simulator limits spring strain.
  - **For RBT-121:** a hard body budget by construction.
- **Gupta, A., Savarese, S., Ganguli, S. & Fei-Fei, L. (2021).** Embodied intelligence via learning and evolution. *Nature Communications* 12: 5721. [doi:10.1038/s41467-021-25874-z](https://doi.org/10.1038/s41467-021-25874-z).
  - DERL evolves bodies that learn by reinforcement. Complex environments evolved bodies that learn new tasks faster (a "morphological Baldwin effect"), and selected more stable, energy-efficient bodies.
  - No hand-designed baseline in the abstract.
- **Other machine-learning co-design, verified (see log 1).** These are not comparisons with a hand-designed body:
  - Wang, Zhou, Fidler & Ba (2019), *Neural Graph Evolution*, ICLR ([arXiv:1906.05370](https://arxiv.org/abs/1906.05370));
  - Pathak, Lu, Darrell, Isola & Efros (2019), NeurIPS 32 ([arXiv:1902.05546](https://arxiv.org/abs/1902.05546)), which is compared against static baselines;
  - Zhao et al. (2020), *RoboGrammar*, ACM TOG 39(6) ([doi:10.1145/3414685.3417831](https://doi.org/10.1145/3414685.3417831));
  - Yuan et al. (2022), *Transform2Act*, ICLR ([arXiv:2110.03659](https://arxiv.org/abs/2110.03659)).
- **Huang et al. (2024).** CompetEvo: towards morphological evolution from competition. *IJCAI 2024.* [arXiv:2405.18300](https://arxiv.org/abs/2405.18300).
  - Evolving-body agents fight fixed-body agents in one arena and "obtain advantages in combat".
  - This is the 2005 arena configuration, in ranked zero-sum combat. It has none of the follow-up paper's controls (mass, spawn, a measure taken alone).
  - **For RBT-118:** the contrast case.
- **Zhang, Y., Xie, Y., Sun, T. & Iida, F. (2025).** Co-design is powerful and not free. [arXiv:2510.08368](https://arxiv.org/abs/2510.08368). Preprint, abstract only; reaching tasks only.
  - "When the baseline morphology already affords sufficient capability, control-only optimization often matches or exceeds co-design." Co-design helps where the body is poorly matched to the task.
  - **For RBT-115/118:** a recent "a fixed body is often enough" result, consistent with our arena answer.
- **Fang, J., Sun, Y., Ma, C., Lu, Q. & Yao, L. (2025).** RoboMoRe: LLM-based robot co-design via joint optimization of morphology and reward. [arXiv:2506.00276](https://arxiv.org/abs/2506.00276). Preprint, abstract only.
  - LLM-driven co-design of body and reward. The citation check (F3) reports that it "significantly outperforms human-engineered designs" across eight tasks.
  - It is not evolutionary, and matched compute is not stated.

### 1.4 So: has the 2005 comparison been run properly?

**Not in the form the proposal asked for, and not with the follow-up paper's controls.**
- What exists:
  - parametric bodies against their stock design (Ha 2019);
  - scheduled or small morphological spaces against a fixed body (Bongard 2011, 2015; Bongard & Paul 2001);
  - an adaptive real robot against a fixed configuration (Nygaard et al. 2021);
  - co-adapted bodies against fixed hand-designed ones (Pagliuca & Nolfi 2022);
  - a benchmark remark (Evolution Gym), and LLM-driven co-design against human designs (RoboMoRe 2025);
  - an unaudited arena (CompetEvo).

  The evolving body wins or ties in all of them. The counterpoint is Zhang et al. (2025): when the fixed body is already adequate, control-only optimisation often matches or beats co-design.
- **None of the ones we found controls for the allowances the follow-up paper found:** mass, spawn energy, and now motor capacity. None reports the evolving body measured apart from the scoring bout.
- **The Cheney and Mertan line changes the question.** It says the potential advantage of an evolving body is real but the search throws it away. Our arena "no" is consistent with that.
- The two open questions match RBT-118's options:
  - does the answer change when the instrument is an economy rather than a ranked bout?
  - does it change when the body's allowances are budgeted?

---

## 2. Embodied and ecological evolution

The origin papers:

- **Watson, R. A., Ficici, S. G. & Pollack, J. B. (1999).** Embodied evolution: embodying an evolutionary algorithm in a population of robots. *CEC 1999*: 335–342. [doi:10.1109/CEC.1999.781944](https://doi.org/10.1109/CEC.1999.781944).
- **Watson, R. A., Ficici, S. G. & Pollack, J. B. (2002).** Embodied evolution: *distributing* an evolutionary algorithm in a population of robots. *Robotics and Autonomous Systems* 39(1): 1–18. [doi:10.1016/S0921-8890(02)00170-7](https://doi.org/10.1016/S0921-8890(02)00170-7).
  - The algorithm lives in the robots. Each broadcasts genes at a rate set by its own score and accepts genes more readily as its score falls. With eight real robots, evolved controllers beat a hand-designed one on a simple task.
  - Note: each robot still computes a local, task-defined score. **Embodied evolution in this sense is decentralised, not fitness-free.** Rabbitstew's ecology goes further than its named ancestor: no score is computed at all.
- **Ficici, S. G., Watson, R. A. & Pollack, J. B. (1999).** Embodied evolution: a response to challenges in evolutionary robotics. *EWLR-8*: 14–22. [authors' page](http://demo.cs.brandeis.edu/papers/long.html#ewlr8).
  - The companion methodology paper.
- **Salmon, B. (2003).** Embodied evolution in a morphologically heterogeneous population of robots. Swarthmore CS81 project, 19 May 2003. [PDF](https://www.cs.swarthmore.edu/~meeden/cs81/s03/projects/salmon.pdf). Read in full.
  - A **position paper about a work in progress; it reports no results.**
  - It proposes combining holistic evolution (Sims, Hornby & Pollack, Bongard & Paul) with embodied evolution, and predicts three things:
    - stability;
    - fast re-adaptation after environmental change;
    - gradual complexification without staged fitness.
  - Cite it as the idea, not as evidence. RBT-107 is its only test so far (re-adaptation, not seen).

What happened next (the Bredeche, Haasdijk and Eiben line):

- **Bredeche, N. & Montanier, J.-M. (2010).** Environment-driven embodied evolution in a population of autonomous agents. *PPSN XI*, LNCS 6239: 290–299. [doi:10.1007/978-3-642-15871-1_30](https://doi.org/10.1007/978-3-642-15871-1_30).
- **Bredeche, N., Montanier, J.-M., Liu, W. & Winfield, A. F. T. (2012).** Environment-driven distributed evolutionary adaptation in a population of autonomous robotic agents. *Mathematical and Computer Modelling of Dynamical Systems* 18(1): 101–129. [doi:10.1080/13873954.2011.601425](https://doi.org/10.1080/13873954.2011.601425).
  - mEDEA has no task fitness: the algorithm copes with "the implicit fitness function hidden in the environment". Genomes spread by local broadcast.
  - The winners are whatever spreads most, which in practice means moving about and meeting others. It ran on 20 e-pucks.
  - **For papers 5 and 6:** the fitness-free precedent in robotics, and the same finding that implicit selection rewards the cheapest way to keep reproducing.
- **Haasdijk, E., Bredeche, N. & Eiben, A. E. (2014).** Combining environment-driven adaptation and task-driven optimisation in evolutionary robotics. *PLoS ONE* 9(6): e98466. [doi:10.1371/journal.pone.0098466](https://doi.org/10.1371/journal.pone.0098466).
  - MONEE splits selection in two: the environment decides survival and a task score decides parenthood. It gets task behaviour without losing viability.
  - **For RBT-121 C:** the field's standard answer when the world alone does not select for what we want. It is also a warning: adding it makes the ecology no longer fitness-free.
- **Montanier, J.-M., Carrignon, S. & Bredeche, N. (2016).** Behavioral specialization in embodied evolutionary robotics: why so difficult? *Frontiers in Robotics and AI* 3: 38. [doi:10.3389/frobt.2016.00038](https://doi.org/10.3389/frobt.2016.00038).
  - In two-resource foraging, specialisation rarely evolves. It needs sparse interaction and larger populations.
- **Bredeche, N., Haasdijk, E. & Prieto, A. (2018).** Embodied evolution in collective robotics: a review. *Frontiers in Robotics and AI* 5: 12. [doi:10.3389/frobt.2018.00012](https://doi.org/10.3389/frobt.2018.00012).
  - The field review. Embodied evolution shifted from parallel search in small groups to online distributed learning in swarms.
  - **Not one reviewed system evolves bodies in a physics ecology beside a designed body.**

Open-ended evolution, and what makes a world produce more:

- **Soros, L. B. & Stanley, K. O. (2014).** Identifying necessary conditions for open-ended evolution through the artificial life world of Chromaria. *ALIFE 14*: 793–800. [doi:10.7551/978-0-262-32621-6-ch128](https://doi.org/10.7551/978-0-262-32621-6-ch128).
  - Four conditions:
    - a minimal criterion to reproduce;
    - individuals create new opportunities to meet it;
    - individuals decide their own interactions;
    - an uncapped representation.

    Chromaria stagnates without any one of them.
  - **For RBT-121 C:** Rabbitstew meets the first and fourth. It arguably fails the second, since agents do not create opportunities for one another: food is exogenous.
- **Brant, J. C. & Stanley, K. O. (2017).** Minimal criterion coevolution: a new approach to open-ended search. *GECCO '17*: 67–74. [doi:10.1145/3071178.3071186](https://doi.org/10.1145/3071178.3071186).
  - Mazes and solvers coevolve under mutual minimal criteria, and both complexify.
- **Lehman, J. & Stanley, K. O. (2011).** Abandoning objectives: evolution through the search for novelty alone. *Evolutionary Computation* 19(2): 189–223. [doi:10.1162/EVCO_a_00025](https://doi.org/10.1162/EVCO_a_00025).
- **Taylor, T. et al. (2016).** Open-ended evolution: perspectives from the OEE workshop in York. *Artificial Life* 22(3): 408–423. [doi:10.1162/ARTL_a_00210](https://doi.org/10.1162/ARTL_a_00210).
  - Keep observable hallmarks apart from hypothesised mechanisms.
- **Packard, N. et al. (2019).** An overview of open-ended evolution. *Artificial Life* 25(2): 93–103. [doi:10.1162/artl_a_00291](https://doi.org/10.1162/artl_a_00291).
- **Channon, A. (2019).** Maximum individual complexity is indefinitely scalable in Geb. *Artificial Life* 25(2): 134–144. [doi:10.1162/artl_a_00285](https://doi.org/10.1162/artl_a_00285).
  - Complexity grows without bound only when world size and the neuron cap are scaled together, and then only logarithmically.
- **Miras, K. & Eiben, A. E. (2019).** Effects of environmental conditions on evolved robot morphologies and behavior. *GECCO '19*: 125–132. [doi:10.1145/3321707.3321811](https://doi.org/10.1145/3321707.3321811).
  - Environments that look different to people can select for the same bodies.
  - **For RBT-121 C:** "we changed the world" is not evidence that the selection changed. Measure it.
- **Stanton, A. & Channon, A. (2013).** Heterogeneous complexification strategies robustly outperform homogeneous strategies for incremental evolution. *ECAL 2013*: 973–980. [doi:10.7551/978-0-262-31709-2-ch145](https://doi.org/10.7551/978-0-262-31709-2-ch145).
  - Ramping difficulty, or jumping straight to the hard task, loses the gradient. Many difficulties at once do better.
- **Bejjani et al. (2025).** The emergence of complex behavior in large-scale ecological environments. [arXiv:2510.18221](https://arxiv.org/abs/2510.18221). Preprint, abstract only.
  - Agents "have no explicit rewards or learning objectives but instead evolve … according to reproduction, mutation, and selection". It studies scale and population size.
  - No evolved morphology, and no designed body.

**What this literature says, for the programme.** Removing the fitness function does not remove selection. It moves selection into the world, where it is implicit and greedy.
- The winners are whatever lineage persists most cheaply (mEDEA; Lehman & Stanley 2011's "easiest to exploit").
- The blind mower is the expected outcome, not an anomaly.
- The field's two answers, both open to RBT-121 C:
  - give selection a task channel (MONEE), at the cost of fitness-freeness;
  - build a world whose structure makes the behaviour pay (Chromaria's conditions; §3).

---

## 3. The evolution of perception and chemotaxis

- **Braitenberg, V. (1984).** *Vehicles: Experiments in Synthetic Psychology.* MIT Press. [publisher page](https://mitpress.mit.edu/9780262521123/vehicles/).
  - The two-sensor compass. With one sensor, a vehicle can modulate its speed but cannot steer.
  - Paper 8's decomposition (a lone nose is half compass, half pirouette) is the quantitative form of that remark, on the Pioneer.
- **Beer, R. D. & Gallagher, J. C. (1992).** Evolving dynamical neural networks for adaptive behavior. *Adaptive Behavior* 1(1): 91–122. [doi:10.1177/105971239200100105](https://doi.org/10.1177/105971239200100105).
  - Evolved continuous-time recurrent networks produced a **chemotaxis controller that switches strategy with conditions**.
  - Fitness rewarded reaching the source directly.
- **Beer, R. D. (1996).** Toward the evolution of dynamical neural networks for minimally cognitive behavior. *From Animals to Animats 4*: 421–429. [doi:10.7551/mitpress/3118.003.0051](https://doi.org/10.7551/mitpress/3118.003.0051).
- **Beer, R. D. (2003).** The dynamics of active categorical perception in an evolved model agent. *Adaptive Behavior* 11(4): 209–243. [doi:10.1177/1059712303114001](https://doi.org/10.1177/1059712303114001).
  - Minimally cognitive behaviour: an agent with a ray sensor catches circles and avoids diamonds.
  - Perception here is *active*: the agent's scanning movement creates the difference it categorises.
  - The task makes the sensed difference decision-relevant by construction.
- **Izquierdo, E. J. & Lockery, S. R. (2010).** Evolution and analysis of minimal neural circuits for klinotaxis in *C. elegans*. *J. Neuroscience* 30(39): 12908–12917. [doi:10.1523/JNEUROSCI.2606-10.2010](https://doi.org/10.1523/JNEUROSCI.2606-10.2010).
- **Izquierdo, E. J. & Beer, R. D. (2013).** Connecting a connectome to behavior. *PLoS Computational Biology* 9(2): e1002890. [doi:10.1371/journal.pcbi.1002890](https://doi.org/10.1371/journal.pcbi.1002890).
  - Evolved klinotaxis steers up a gradient with **one** chemosensory input. The undulating body samples the gradient over time.
  - **For RBT-116:** a route to chemotaxis that does not cross the Pioneer's two-sensor valley at all. It is exactly the "different route to chemotaxis" the ticket names, and a reason the valley may be a property of the wheeled body.
- **Goldstein, R. A. & Soyer, O. S. (2008).** Evolution of taxis responses in virtual bacteria: non-adaptive dynamics. *PLoS Computational Biology* 4(5): e1000084. [doi:10.1371/journal.pcbi.1000084](https://doi.org/10.1371/journal.pcbi.1000084).
  - Evolved taxis took a simple form under most conditions. *E. coli*-like adaptive sensing evolved only under **stimulus scarcity and fluctuation**.
  - The statistics of the world decide which sensing evolves.
- **Cliff, D., Husbands, P. & Harvey, I. (1993).** Explorations in evolutionary robotics. *Adaptive Behavior* 2(1): 73–110. [doi:10.1177/105971239300200104](https://doi.org/10.1177/105971239300200104).
  - "Robust visually guided control systems evolve from evaluation functions that do not explicitly require monitoring visual input."
  - Vision evolved because the task (reach the room's centre) could not be done well without it.
- **Harvey, I., Husbands, P. & Cliff, D. (1994).** Seeing the light: artificial evolution, real vision. *From Animals to Animats 3*: 392–401. [doi:10.7551/mitpress/3117.003.0058](https://doi.org/10.7551/mitpress/3117.003.0058).
  - **Visual sampling morphology (which pixels to sample) co-evolved with the controller**, on a real camera robot.
  - **For RBT-116:** the precedent for evolving sensor placement, which is the extra dimension a holistic body adds.
- **Liese, A., Polani, D. & Uthmann, T. (2001).** A study of the simulated evolution of the spectral sensitivity of visual agent receptors. *Artificial Life* 7(2): 99–124. [doi:10.1162/106454601753138961](https://doi.org/10.1162/106454601753138961).
  - Receptor sensitivity co-evolved with control **under an explicit sensor cost**. Sensitivities converged on the targets' emission spectrum, and evolving the sensor helped.
  - It sits in the *Artificial Life* special issue on sensor evolution: Dautenhahn, Polani & Uthmann (2001), 7(2): 95–97, [doi:10.1162/106454601753138952](https://doi.org/10.1162/106454601753138952).
- **Balakrishnan, K. & Honavar, V. (2001).** Evolving neuro-controllers and sensors for artificial agents. In Patel, Honavar & Balakrishnan (eds), *Advances in the Evolutionary Synthesis of Intelligent Agents*, MIT Press: 109–152. [doi:10.7551/mitpress/1129.003.0007](https://doi.org/10.7551/mitpress/1129.003.0007).
  - The consolidated version of the 1996 work that the 2005 proposal cites. The record is verified; no abstract was retrieved, so cite it for the fact that sensors and controllers were co-evolved, not for results.
  - The 1996 GP-96 paper itself could not be verified to our bar (§9).
- **Dale, K. & Collett, T. S. (2001).** Using artificial evolution and selection to model insect navigation. *Current Biology* 11(17): 1305–1316. [doi:10.1016/S0960-9822(01)00418-3](https://doi.org/10.1016/S0960-9822(01)00418-3).
  - With a compass and eyes **given**, and fitness for reaching a landmark-defined goal, animats evolved bee-like strategies.
- **Floreano, D. & Mondada, F. (1996).** Evolution of homing navigation in a real mobile robot. *IEEE Trans. SMC-B* 26(3): 396–407. [doi:10.1109/3477.499791](https://doi.org/10.1109/3477.499791).
  - On a real Khepera with a battery that runs down, finding and returning to the charger evolved, through an internal map.
  - **For RBT-121 C:** an energy ecology in which *where* you go matters, not how far. That is the property our foraging world lacks.
- **Tiwary, K. et al. (2025).** What if eye...? Computationally recreating vision evolution. *Science Advances* 11(51). [doi:10.1126/sciadv.ady2888](https://doi.org/10.1126/sciadv.ady2888).
  - Eyes co-evolved with behaviour in embodied agents. Task-specific selection split eye types, and lenses emerged to resolve a light-versus-acuity trade-off.
  - The most direct modern case of perception evolving from scratch, under a task that demands it.
- **Nilsson, D.-E. & Pelger, S. (1994).** A pessimistic estimate of the time required for an eye to evolve. *Proc. R. Soc. B* 256(1345): 53–58. [doi:10.1098/rspb.1994.0048](https://doi.org/10.1098/rspb.1994.0048).
  - An eye evolves fast **if every small step pays**.
  - The compass valley (papers 8 and 10) is the opposite case. That is the precise sense in which it is hard.
- **Viswanathan, G. M. et al. (1999).** Optimizing the success of random searches. *Nature* 401: 911–914. [doi:10.1038/44831](https://doi.org/10.1038/44831).
  - When targets are sparse and detectable only close by, a blind statistical search (a Lévy walk) is optimal.
- **Kussell, E. & Leibler, S. (2005).** Phenotypic diversity, population growth, and information in fluctuating environments. *Science* 309: 2075–2078. [doi:10.1126/science.1114383](https://doi.org/10.1126/science.1114383).
  - Sensing beats blind stochastic switching only when the environment changes often enough to repay the sensor's cost.
- **Stephens, D. W. (1991).** Change, regularity, and value in the evolution of animal learning. *Behavioral Ecology* 2(1): 77–89. [doi:10.1093/beheco/2.1.77](https://doi.org/10.1093/beheco/2.1.77).
  - Tracking the environment is least valuable when the uninformed alternatives already pay about the same. That is about learning; it applies to sensing by analogy.
- **Chaumont, N. & Adami, C. (2016).** Evolution of sustained foraging in three-dimensional environments with physics. *Genetic Programming and Evolvable Machines* 17(4): 359–390. [doi:10.1007/s10710-016-9270-z](https://doi.org/10.1007/s10710-016-9270-z). Verified in RBT-71; details completed here.
  - "Artificially evolving foraging behavior in simulated articulated animals has proved to be a notoriously difficult task."
  - It worked only with an **explicit, staged fitness function** and food positions randomised gradually.
- **The bootstrap problem:**
  - Nelson, Barlow & Doitsidis (2009), *Robotics and Autonomous Systems* 57(4): 345–370, [doi:10.1016/j.robot.2008.09.009](https://doi.org/10.1016/j.robot.2008.09.009);
  - Mouret & Doncieux (2009), *CEC 2009*: 1161–1168, [doi:10.1109/CEC.2009.4983077](https://doi.org/10.1109/CEC.2009.4983077), who use behavioural diversity to cross a zero-gradient start on a light-seeking robot;
  - Silva, Duarte, Correia, Oliveira & Christensen (2016), *Evolutionary Computation* 24(2): 205–236, [doi:10.1162/EVCO_a_00172](https://doi.org/10.1162/EVCO_a_00172).

  When no individual in the population can collect the reward, there is no gradient.
- **Klyubin, A. S., Polani, D. & Nehaniv, C. L. (2005).** Empowerment: a universal agent-centric measure of control. *CEC 2005*: 128–135. [doi:10.1109/CEC.2005.1554676](https://doi.org/10.1109/CEC.2005.1554676).
  - A task-free drive that can make sensor and actuator structure pay when the external reward does not.

**Why perception is hard to evolve, and what made it evolve elsewhere.** Across the verified work, perception evolved when three things held:
1. **The sensed signal was decision-relevant, and coverage could not stand in for it:**
   - a single source (Beer & Gallagher);
   - a goal marked by a landmark (Dale & Collett);
   - a charger to return to before energy runs out (Floreano & Mondada);
   - a category to decide (Beer 2003);
   - a room centre (Cliff et al.).
2. **The minimal version already paid:**
   - one-sensor klinotaxis (Izquierdo);
   - tunable sensitivity under a cost (Liese et al.);
   - graded visual sampling (Harvey et al.);
   - Nilsson & Pelger's premise.
3. **The world varied enough to repay the sensor** (Goldstein & Soyer; Kussell & Leibler).

**Paper 6's world fails 1 and 3 by design:**
- food is dense, immobile, uniform and renewed at once;
- yield is linear in ground swept;
- targets are detectable only close by.

**The Pioneer's compass fails 2 by geometry** (papers 8 and 10).

The theory papers (Viswanathan; Kussell & Leibler; Stephens) make "the cow is the correct answer" a known result, not a new one. **What is new is measuring it inside one simulator**, with lesion and decoy tests on both kinds of body, and a planted compass tested for whether selection holds it (RBT-106, 112).

---

## 4. Simulators gamed by evolution

### 4.1 The catalogues

- **Lehman, J., Clune, J., Misevic, D., et al. (2020).** The surprising creativity of digital evolution: a collection of anecdotes from the evolutionary computation and artificial life research communities. *Artificial Life* 26(2): 274–306. [doi:10.1162/artl_a_00319](https://doi.org/10.1162/artl_a_00319); [arXiv:1803.03453](https://arxiv.org/abs/1803.03453). Full text read. Already cited in paper 7 §7; the anecdotes and their fixes are drawn out here.

  | anecdote | what evolution did | what was done |
  |---|---|---|
  | Sims | tall rigid bodies fell over to convert their initial potential energy into velocity | "allocate time at the beginning of each simulation to relax the potential energy inherent in the creature's initial stance before motion was rewarded" |
  | Sims | swimmers harvested Euler-integration error | a better integrator |
  | Sims | self-collision bugs made "impossibly-strong grasshoppers" | patched |
  | Krcah | "maximum height" was met by towers, then by kick-and-fall somersaults | found only by watching |
  | Cheney et al., VoxCAD | bodies shrank to get a coarser timestep, then penetrated the ground and rode the correction force | "Damping was increased when contacting the ground, the minimum creature size was raised, and the time delta calculation was adjusted to reduce ground penetration" |
  | Cully et al. | scoring started after the first transient | "the first few tenths of a second of the simulation are ignored" |

  - **The authors' advice:** expect the specification to fail, "adopt an adversarial mindset", and visualise solutions regularly.
- **Krakovna, V., Uesato, J., Mikulik, V., Rahtz, M., Everitt, T., Kumar, R., Kenton, Z., Leike, J. & Legg, S. (2020).** Specification gaming: the flip side of AI ingenuity. DeepMind blog, 21 April 2020. [link](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/).
  - "The underlying problem isn't the bug itself but a failure of abstraction that can be exploited by the agent."
  - **For RBT-121:** our four exploits are four abstraction failures, not four bugs. That is the reason for the audit.
- **Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J. & Mané, D. (2016).** Concrete problems in AI safety. [arXiv:1606.06565](https://arxiv.org/abs/1606.06565).
  - Reward hacking and its mitigations: reward capping, multiple rewards, careful engineering, and **trip wires** (monitored vulnerabilities that flag exploitation).
- **Baker, B. et al. (2020).** Emergent tool use from multi-agent autocurricula. *ICLR 2020*. [arXiv:1909.07528](https://arxiv.org/abs/1909.07528).
  - MuJoCo-based agents "box-surfed" because their movement action applied force "regardless of whether they are on the ground or not". The authors call environments free of such exploits an open problem.
  - The RL cousin of RBT-120: **an actuation rule that grants capacity the physics would not.**
- **Manheim, D. & Garrabrant, S. (2018).** Categorizing variants of Goodhart's law. [arXiv:1803.04585](https://arxiv.org/abs/1803.04585).
  - Our exploits are *extremal* Goodhart: pushing into regimes where the proxy stops tracking the goal. That reading is ours, not the paper's.

### 4.2 What the physics-creature literature did, exploit by exploit

- **Sims, K. (1994a).** Evolving virtual creatures. *SIGGRAPH '94*: 15–22. [doi:10.1145/192161.192167](https://doi.org/10.1145/192161.192167); [author PDF](https://www.karlsims.com/papers/siggraph94.pdf). Verified in RBT-71; the quotations below were checked against the author's PDF for this review.
  - "Any bugs that allow energy leaks from non-conservation, or even round-off errors, will inevitably be discovered and exploited by the evolving creatures."
  - **Actuator budget:** "Each effector is given a maximum-strength proportional to the maximum cross sectional area of the two parts it joins. Effector forces are scaled by these strengths and not permitted to exceed them. Since strength scales with area, but mass scales with volume, as in nature, behavior does not always scale uniformly."
  - **Settling:** "it can be necessary to prevent creatures from generating high velocities by simply falling over. This is accomplished by first running the simulation with no friction and no effector forces until the height of the center of mass reaches a stable minimum."
  - **Penetration:** "If necessary, the previous time-step is reduced to keep any new penetrations below a certain tolerance." Creatures with persistent initial interpenetration, or with more than a set number of parts, are discarded.
- **Taylor, T. & Massey, C. (2001).** Recent developments in the evolution of morphologies and controllers for physically simulated creatures. *Artificial Life* 7(1): 77–87. [doi:10.1162/106454601300328034](https://doi.org/10.1162/106454601300328034). Full text read.
  - A re-implementation of Sims on MathEngine, capped at 4–10 parts. "Despite various attempts to limit the magnitude of the forces applied to joints", creatures drove the solver to explode.
  - Fixes: count solver warnings and abort on explosion signatures. They used PD actuators, and point to newly available force-limited velocity-constraint actuators (MathEngine) and dashpots (Havok) as more stable effectors.
  - "No matter which physics engine is used … a certain number of stability checks … will be required."
- **Krčah, P. (2008).** Towards efficient evolutionary design of autonomous robots. *ICES 2008*, LNCS: 153–164. [doi:10.1007/978-3-540-85857-7_14](https://doi.org/10.1007/978-3-540-85857-7_14). Full text read.
  - §3.3, "Validity testing": "robots often exploit properties of the physical simulation to their advantage". Pre-simulation tests reject self-penetration, excessively small parts and excessively many parts. Variation is re-applied until a genotype passes.
- **Lessin, D., Fussell, D. & Miikkulainen, R. (2013).** Open-ended behavioral complexity for evolved virtual creatures. *GECCO '13*: 335–342. [doi:10.1145/2463372.2463411](https://doi.org/10.1145/2463372.2463411).
  - Muscles carry an explicit maximum strength.
- **Cheney et al. (2013):** fitness penalties on voxel count and on actuated material (§1.2).

**Mapped onto our exploits:**

| our exploit | where it bit | the literature's fix | status here |
|---|---|---|---|
| weight class: bodies grew to several times 15 kg | follow-up paper §4.1 | part-count caps (Sims; Taylor & Massey); validity checks (Krčah); body-size penalties (Cheney 2013); a fixed voxel grid (Evolution Gym) | **fixed** by the mass budget |
| spawn drop harvested as momentum | follow-up paper §4.2 | Sims's friction-free, force-free settle to a stable centre-of-mass minimum; Cully's ignored transient | **fixed**. Our protocol (settle passively, zero velocities, re-centre) matches Sims's in substance |
| motor capacity grows with mass per driven DOF, up to 3 per ball joint (gear = 4 × heavier mass) | RBT-113/117 adversary §3 → RBT-120 | Sims scales each effector's maximum strength **by cross-sectional area** (≈ mass^⅔ for isometric parts) and clamps forces at it. **His cap is per effector, i.e. per DOF**: "Each effector controls a degree of freedom of a joint", so a 3-DOF Sims joint also carries three full-strength effectors. Cheney charges for actuated material. Nygaard shows evolution adapts within a fixed torque limit | **open** (RBT-120). Sims's area rule removes the mass-proportional growth, but not the ×3 per ball joint; a per-joint cap would be our own addition (§10.3) |
| contact penetration of 0.27–0.57 m (RBT-113 N1) | RBT-121 A | Sims shrinks the step to hold penetration under a tolerance and discards bodies with persistent interpenetration; Cheney raised ground damping, a minimum body size and a timestep rule; MuJoCo ties resting penetration to `solref`/`solimp` against the timestep | **open** (RBT-121 A) |
| solver explosions | handled: exploded seasons book 0 (RBT-113 adversary §3) | Taylor & Massey abort on warnings and explosion signatures | **fixed**, in the same form |
| coverage paid as "foraging" | papers 5–6; RBT-113 §4 | not a physics exploit: an economy one (§3) | RBT-121 C |

### 4.3 Reality-gap and robustness methods

- **Jakobi, N. (1997).** Evolutionary robotics and the radical envelope-of-noise hypothesis. *Adaptive Behavior* 6(2): 325–368. [doi:10.1177/105971239700600205](https://doi.org/10.1177/105971239700600205).
  - Features the task must not depend on are varied at random, so controllers cannot rely on them. Minimal simulations built this way transferred to real robots.
  - **For RBT-121:** randomise what evolution should not exploit (contact softness, spawn height, friction) and an exploit stops paying reliably.
- **Jakobi, N., Husbands, P. & Harvey, I. (1995).** Noise and the reality gap: the use of simulation in evolutionary robotics. *ECAL 1995*, LNCS: 704–720. [doi:10.1007/3-540-59496-5_337](https://doi.org/10.1007/3-540-59496-5_337). Record only; cited for priority.
- **Koos, S., Mouret, J.-B. & Doncieux, S. (2013).** The transferability approach: crossing the reality gap in evolutionary robotics. *IEEE Trans. Evolutionary Computation* 17(1): 122–145. [doi:10.1109/TEVC.2012.2185849](https://doi.org/10.1109/TEVC.2012.2185849).
  - "The most efficient solutions in simulation often exploit badly modeled phenomena." They add a second objective: estimated agreement between simulation and reality.
  - **For RBT-121:** a simulation-only analogue is to score agreement between the default physics and a conservative configuration (stiffer contacts, a smaller step).
- **Peng, X. B., Andrychowicz, M., Zaremba, W. & Abbeel, P.** Sim-to-real transfer of robotic control with dynamics randomization. [arXiv:1710.06537](https://arxiv.org/abs/1710.06537). The venue is unverified.
  - Randomised dynamics as the RL descendant of Jakobi.
- **Physics engines:**
  - Todorov, E., Erez, T. & Tassa, Y. (2012). MuJoCo: a physics engine for model-based control. *IROS 2012*: 5026–5033. [doi:10.1109/IROS.2012.6386109](https://doi.org/10.1109/IROS.2012.6386109).
  - Erez, T., Tassa, Y. & Todorov, E. (2015). Simulation tools for model-based robotics: comparison of Bullet, Havok, MuJoCo, ODE and PhysX. *ICRA 2015*: 4397–4404. [doi:10.1109/ICRA.2015.7139807](https://doi.org/10.1109/ICRA.2015.7139807).
  - The MuJoCo documentation ([computation](https://mujoco.readthedocs.io/en/stable/computation/index.html), [modeling](https://mujoco.readthedocs.io/en/stable/modeling.html); documentation, not peer-reviewed):
    - the contact model is soft by design, and penetration is set by `solref` and `solimp` against the timestep;
    - `timeconst` should be at least twice the step;
    - the joint-level `actuatorfrcrange` clamps the **total** actuator force on a joint.

---

## 5. Evolvability and selection-response benchmarks (RBT-113, RBT-117)

The quantitative-genetics template:

- **Falconer, D. S. & Mackay, T. F. C. (1996).** *Introduction to Quantitative Genetics*, 4th ed. Longman. ISBN 0-582-24302-5. Library record.
  - R = h²S, realised heritability as cumulative response over cumulative selection differential, and divergent lines with an unselected control. Chapter and page are not verified; cite the book.
- **Hill, W. G. & Caballero, A. (1992).** Artificial selection experiments. *Annual Review of Ecology and Systematics* 23: 287–310. [doi:10.1146/annurev.es.23.110192.001443](https://doi.org/10.1146/annurev.es.23.110192.001443).
  - The conventions for replicate lines, controls and the limits of selection.
- **Houle, D. (1992).** Comparing evolvability and variability of quantitative traits. *Genetics* 130(1): 195–204. [doi:10.1093/genetics/130.1.195](https://doi.org/10.1093/genetics/130.1.195).
  - h² is a poor measure of evolvability for fitness-like traits, because their residual variance is large. Use mean-standardised additive variance.
  - **For RBT-117 directly:** its "responds more per σ0" is variance-standardised, and the two faunas' σ0 differ by a factor of 3.4 (0.221 against 0.754). Houle's point is that a variance-scaled comparison and a mean-scaled one can disagree. Report both.
- **Hansen, T. F. & Houle, D. (2008).** Measuring and comparing evolvability and constraint in multivariate characters. *Journal of Evolutionary Biology* 21(5): 1201–1219. [doi:10.1111/j.1420-9101.2008.01573.x](https://doi.org/10.1111/j.1420-9101.2008.01573.x).
- **Price, G. R. (1970).** Selection and covariance. *Nature* 227: 520–521. [doi:10.1038/227520a0](https://doi.org/10.1038/227520a0).

Carried into evolutionary computation and artificial life:

- **Mühlenbein, H. & Schlierkamp-Voosen, D. (1993).** Predictive models for the breeder genetic algorithm I. *Evolutionary Computation* 1(1): 25–49. [doi:10.1162/evco.1993.1.1.25](https://doi.org/10.1162/evco.1993.1.1.25). Also: The science of breeding and its application to the breeder genetic algorithm. *Evolutionary Computation* 1(4): 335–360. [doi:10.1162/evco.1993.1.4.335](https://doi.org/10.1162/evco.1993.1.4.335).
  - Truncation selection with R = h²S and regression heritability, used to predict and control a genetic algorithm.
  - **This is the precedent for RBT-113's `--truncation` hook and its realised h².**
- **Bedau, M. A., Snyder, E., Brown, C. T. & Packard, N. H. (1997).** A comparison of evolutionary activity in artificial evolving systems and in the biosphere. *ECAL97*: 125–134. [Bedau's publications](https://people.reed.edu/~mab/publications/index.html).
  - Per Channon (2024), the first **neutral shadow**: a copy of the system in which reproducing individuals are chosen at random.
- **Channon, A. (2006).** Unbounded evolutionary dynamics in a system of agents that actively process and transform their environment. *Genetic Programming and Evolvable Machines* 7(3): 253–281. [doi:10.1007/s10710-006-9009-3](https://doi.org/10.1007/s10710-006-9009-3).
- **Channon, A. (2024).** A procedure for testing for Tokyo Type 1 open-ended evolution. *Artificial Life* 30(3): 345–355. [doi:10.1162/artl_a_00430](https://doi.org/10.1162/artl_a_00430).
  - The shadow is run in parallel "except that whenever selection operates in the real system, random selection should be employed in the shadow".
  - This is artificial life's drift control, and conceptually RBT-113's C lines and paper 5's neutral arms. It measures component persistence, not trait response.
- **Williams, H. T. P. & Lenton, T. M. (2007).** Artificial selection of simulated microbial ecosystems. *PNAS* 104(21): 8918–8923. [doi:10.1073/pnas.0610038104](https://doi.org/10.1073/pnas.0610038104). Full text read.
  - High, Low and Random-control lines in an individual-based evolutionary simulation, with heritability inferred from sustained divergence from the control. No numerical h².
  - **The closest precedent for RBT-113's design.**
- **De Carlo, M., Ferrante, E., Zeeuwe, D., Ellers, J. & Eiben, A. E. (2023).** Heritability of morphological and behavioural traits in evolving robots. *Evolutionary Intelligence* 17(3): 1733–1749 (online 2023, print 2024; Crossref, citation check F8). [doi:10.1007/s12065-023-00860-0](https://doi.org/10.1007/s12065-023-00860-0).
  - Parent–offspring regression h² of body and behaviour traits in robots that co-evolve body and brain, used to compare encodings.
  - **The closest robotics precedent for paper 5's h² of foraging yield.** It uses regression, not realised h² from selection lines.
- **Tarapore, D. & Mouret, J.-B. (2015).** Evolvability signatures of generative encodings: beyond standard performance benchmarks. *Information Sciences* 313: 43–61. [doi:10.1016/j.ins.2015.03.046](https://doi.org/10.1016/j.ins.2015.03.046).
  - Distributions of behavioural and fitness change after mutation as an evolvability benchmark. They predicted re-adaptation after damage.
  - **For RBT-121 B:** a cheap operator-level instrument, in the spirit of paper 8's proposal rate.
- **Lehman, J. & Stanley, K. O. (2013).** Evolvability is inevitable: increasing evolvability without the pressure to adapt. *PLoS ONE* 8(4): e62186. [doi:10.1371/journal.pone.0062186](https://doi.org/10.1371/journal.pone.0062186).
  - Evolvability rises under drift alone.
  - **Caution for RBT-113:** control lines hold *directional* response at zero. They do not hold everything else constant.
- **Wagner, G. P. & Altenberg, L. (1996).** Complex adaptations and the evolution of evolvability. *Evolution* 50(3): 967–976. [doi:10.1111/j.1558-5646.1996.tb02339.x](https://doi.org/10.1111/j.1558-5646.1996.tb02339.x).
  - The genotype–phenotype map, not only selection, decides evolvability.
- **Lenski, R. E., Ofria, C., Pennock, R. T. & Adami, C. (2003).** The evolutionary origin of complex features. *Nature* 423: 139–144. [doi:10.1038/nature01568](https://doi.org/10.1038/nature01568).
- **Covert, A. W., Lenski, R. E., Wilke, C. O. & Ofria, C. (2013).** Experiments on the role of deleterious mutations as stepping stones in adaptive evolution. *PNAS* 110(34): E3171–E3178. [doi:10.1073/pnas.1313424110](https://doi.org/10.1073/pnas.1313424110).
  - Avida's counterfactual arms. Lenski et al. 2003: complex functions evolved by building on simpler ones, provided those were also selectively favoured. Covert et al. 2013: knocking out deleterious mutations showed they serve as stepping stones across valleys.
  - **For RBT-116:** valley crossing measured with a knock-out control.
- **Dolson, E. L., Vostinar, A. E., Wiser, M. J. & Ofria, C. (2019).** The MODES toolbox. *Artificial Life* 25(1): 50–73. [doi:10.1162/artl_a_00280](https://doi.org/10.1162/artl_a_00280).

**Reading for RBT-113.** Each part of the benchmark has a precedent:
- up, down and control lines, and realised h² (Falconer & Mackay; Hill & Caballero);
- h² inside a genetic algorithm (Mühlenbein);
- random-selection controls in artificial life (Bedau; Channon);
- high, low and random lines in an artificial-life simulation (Williams & Lenton);
- h² in evolving robots (De Carlo et al.).

**The combination was not found:**
- replicated divergent lines;
- realised h² from cumulative R/S;
- drift lines;
- two body classes compared in one simulator.

Frame it as porting the breeders' protocol, not as inventing one. The RBT-113 adversary's finding, that the holistic down line's response was mostly an unbudgeted motor allowance, is the §4 lesson arriving through the §5 instrument: **a selection-response benchmark measures the model's allowances as well as its evolvability**, unless the allowances are budgeted.

---

## 6. Conrad's extradimensional bypass (RBT-116)

- **Conrad, M. (1990).** The geometry of evolution. *BioSystems* 24(1): 61–81. [doi:10.1016/0303-2647(90)90030-5](https://doi.org/10.1016/0303-2647(90)90030-5).
  - Evolvability needs variation that can carry a structure from peak to peak, together with stability on a peak.
  - Redundancy and many weak interactions reconcile the two. Added dimensions turn isolated peaks into ridges.
- **Conrad, M. (1979).** Bootstrapping on the adaptive landscape. *BioSystems* 11(2–3): 167–182. [doi:10.1016/0303-2647(79)90009-1](https://doi.org/10.1016/0303-2647(79)90009-1).
  - The antecedent: features that make evolution easier can accumulate by hitchhiking.
- **Bongard, J. C. & Paul, C. (2001).** Making evolution an offer it can't refuse: morphology and the extradimensional bypass. *ECAL 2001*, LNCS 2159: 401–412. [doi:10.1007/3-540-44811-X_43](https://doi.org/10.1007/3-540-44811-X_43); [author PDF](https://meclab.w3.uvm.edu/papers/2001_ECAL_Bongard.pdf). Full text read.
  - **The only direct test in evolved robots found.**
  - The setup: a simulated biped, a 60-weight recurrent controller, a population of 300 and 300 generations.

    | extra genes | runs per arm | result |
    | --- | --- | --- |
    | 3 segment radii | 30 against 30 control-only | **outperformed** control-only evolution on average, despite the larger space ("tend to outperform"; no significance test reported) |
    | 8 mass-block genes | 20 against 20 | **no gain**: 2 of 20 runs walked in each condition |

  - The case for a bypass rests on two things: the evolved bodies did not converge on any particular shape, and one dissected lineage event. There was no landscape analysis.
  - Their own conclusion: the *right* morphological parameters help, and arbitrary ones do not.
  - The 2005 proposal cites this paper as support for holistic evolution. The negative half was not mentioned there.
- **Bongard, J. C. & Paul, C. (2000).** Investigating morphological symmetry and locomotive efficiency using virtual embodied evolution. *From Animals to Animats 6*: 420–429. [doi:10.7551/mitpress/3120.003.0045](https://doi.org/10.7551/mitpress/3120.003.0045). Full text read.
  - More symmetric evolved bipeds walked more efficiently. No bypass claim.
- **Gavrilets, S. (1997).** Evolution and speciation on holey adaptive landscapes. *TREE* 12(8): 307–312. [doi:10.1016/S0169-5347(97)01098-7](https://doi.org/10.1016/S0169-5347(97)01098-7).
- **Gavrilets, S. & Gravner, J. (1997).** Percolation on the fitness hypercube and the evolution of reproductive isolation. *J. Theoretical Biology* 184(1): 51–64. [doi:10.1006/jtbi.1996.0242](https://doi.org/10.1006/jtbi.1996.0242).
  - In high dimensions, viable genotypes form connected ridges, and Wright's valley-crossing problem "may be non-existent". This is Conrad's argument, generalised.
- **Huynen, M. A., Stadler, P. F. & Fontana, W. (1996).** Smoothness within ruggedness: the role of neutrality in adaptation. *PNAS* 93(1): 397–401. [doi:10.1073/pnas.93.1.397](https://doi.org/10.1073/pnas.93.1.397).
- **Wagner, A. (2008).** Robustness and evolvability: a paradox resolved. *Proc. R. Soc. B* 275: 91–100. [doi:10.1098/rspb.2007.1137](https://doi.org/10.1098/rspb.2007.1137).
  - Neutral networks let populations drift across genotype space while keeping their phenotype.
- **Weissman, D. B., Desai, M. M., Fisher, D. S. & Feldman, M. W. (2009).** The rate at which asexual populations cross fitness valleys. *Theoretical Population Biology* 75(4): 286–300. [doi:10.1016/j.tpb.2009.02.006](https://doi.org/10.1016/j.tpb.2009.02.006).
  - Large populations cross even wide valleys when the intermediates are near-neutral. Below a threshold population size, crossing becomes rare.
  - **For RBT-116's power:** populations of tens, like RBT-113's 40-member lines and the ecology's arenas, should be expected to sit toward the rare-crossing end unless the intermediate is near-neutral. Paper 8's lone-nose "pirouette" is not near-neutral.
- **Wu, N. C., Dai, L., Olson, C. A., Lloyd-Smith, J. O. & Sun, R. (2016).** Adaptation in protein fitness landscapes is facilitated by indirect paths. *eLife* 5: e16965. [doi:10.7554/eLife.16965](https://doi.org/10.7554/eLife.16965).
  - Across 160,000 GB1 variants, indirect paths (gain a mutation, later lose it) get around sign-epistatic traps. This is bypass-like, measured.
- **Papkou, A., Garcia-Pastor, L., Escudero, J. A. & Wagner, A. (2023).** A rugged yet easily navigable fitness landscape. *Science* 382: eadh3860. [doi:10.1126/science.adh3860](https://doi.org/10.1126/science.adh3860).
  - In DHFR, 514 peaks are mostly reachable directly, and indirect paths play little role (per its citation context).
  - The counter-case: whether a bypass matters depends on the landscape.

**Reading for RBT-116.**
- **Tested once as far as a directed search found, and mixed** (Paul 2005 not yet read). The bypass has been tested in evolved robots once, with a positive result for one parameter set and a null for another. Later robotics work (Cheney 2016, 2018; Mertan & Cheney 2024, 2026) says extra morphological dimensions help only if selection lets the controller catch up with a changed body.
- **What that means for the design:**
  1. Choose the added dimensions for their relevance: sensor placement (Harvey et al. 1994) or a one-sensor klinotaxis route (Izquierdo & Lockery), rather than "the whole body".
  2. Expect the holistic arm's extra dimensions to cost something as well as offer something, and register a clean null as publishable (the ticket already does).
  3. Say whether innovation protection is on, since RBT-74 found the premise holds here but the remedy did not act.
  4. Check the population-size regime against Weissman et al. before powering the test.

---

## 7. The gap probe, refreshed for 2025–2026

- **The question.** RBT-71's probe (2026-09-14) found no paper that places a designed body and co-evolved bodies in the same fitness-free economy and compares realised income. It found none reporting heritability of lifetime yield beside the heritability of a competitive score.
- **The refresh.** 17 fresh queries on 2026-09-27, 20:37–20:40 UTC, plus record fetches. The queries are listed in `verification/6-errata-gap.md`.
- **Nothing found occupies the configuration.** The nearest new neighbours each lack a key element:

  | paper | fitness-free? | evolved bodies? | designed body alongside? |
  |---|---|---|---|
  | Bejjani et al. 2025 | yes | no | no |
  | CompetEvo 2024 | no: ranked combat | yes | yes (fixed body), but in an arena |
  | Mertan & Cheney GECCO 2025; Song et al. 2026 | no: explicit objective | yes | no |
  | Wang et al. 2025, *Embodied co-design for rapidly evolving agents*, a survey of 100+ studies ([arXiv:2512.04770](https://arxiv.org/abs/2512.04770)) | its open-ended section lists only POET-style and developmental work | — | none listed |
  | Finn & Bräunl (2026), *An open and accessible platform for evolving virtual creatures*, *Artificial Life* 32(1): 23–45 ([doi:10.1162/ARTL.a.457](https://doi.org/10.1162/ARTL.a.457)) | a platform paper, no fitness-free economy | yes | no |

- **Limits.** About 2.5 minutes of search wall-clock, with dblp and MIT Press unreachable. It is not systematic. The verdict stands at that weight: **still unoccupied as far as a directed search can see.**

---

## 8. Errata to our own papers

Checked against the source record in each case. The coordinator asked for this section. Line numbers are as of `152e2df`. P5 is `docs/paper-5-the-blind-forager.md` and P7 is `docs/paper-7-five-instruments.md`.

| # | where | what it says | what the source says | severity |
|---|---|---|---|---|
| **E1** | P5:45 ("Miconi, 2011"); P5:456; `runs/RBT-71/citations-check.txt`:6 | "Miconi, T. (2011). The evolution of foraging in an open-ended simulation environment. *EPIA 2011* … doi:10.1007/978-3-642-24769-9_10" | The DOI's own Crossref record: **Tiago Baptista & Ernesto Costa**, *Progress in Artificial Intelligence* (EPIA 2011), LNCS: 125–137. Miconi is not an author. The claim about the paper (foraging evolved with no explicit fitness function) is right; only the attribution is wrong. Checked again for this review against Crossref. | **High**: wrong author |
| **E2** | P7:780–782 | Cheney et al. (2016) "propose morphological innovation protection" | P7:780–782 credits the 2016 paper with *proposing MIP*. The 2016 paper proposes protecting morphological innovations as future work, with preliminary results. The named, tested method is Cheney et al. 2018, *J. R. Soc. Interface* 15: 20170937. Cite both, and cite 2018 for the mechanism. `README.md`:269–271, which cites both, is correct. *(Corrected per citation check F2. The first version of this erratum wrongly said the 2016 paper "proposes nothing".)* | Low |
| **E3** | P5:58–60; P7:786–788 | Co-optimisers "reach morphology-controller pairs that fixed-morphology optimisation cannot, and then discard them" | The abstract of arXiv:2508.17464 gives two separate findings: (a) the search undervalues newly mutated bodies and **eliminates promising morphologies**; (b) "on the other hand", goal-switching yields pairs a controller-only search cannot reach, presented as a *benefit*. The full text does not say the goal-switching pairs are later discarded. The quotation "regularly undervalu[ing] individuals with newly mutated bodies" is accurate. Suggested wording: "reaches pairs a fixed-morphology search cannot, yet regularly undervalues newly mutated bodies and eliminates promising morphologies." | Medium: interpretive |
| **E4** | P5:45 | Utimula (2025) is grouped with "open-ended foraging with no explicit fitness" | Utimula's abstract (PubMed 39898762) is about reproduction and development of 3-D cell creatures, with no mention of foraging. P5:69–70 describes it correctly. | Medium |
| **E5** | P5:57, P5:453; P7:784–785 | Mertan & Cheney (2025), *Artificial Life*, "accepted" | **Published online 2026-09-04**: *Artificial Life*, [doi:10.1162/ARTL.a.476](https://doi.org/10.1162/ARTL.a.476) (Crossref, checked again for this review). Cite it as 2026, adding "arXiv:2508.17464, 2025". P7 should also name the authors. | Low |
| **E6** | P5:450, P5:461, P5:463 | Chaumont & Adami has no volume; Chromaria has no pages or DOI; Utimula has no DOI | Chaumont & Adami: *GPEM* 17(4): 359–390. Chromaria: ALIFE 14: 793–800, doi:10.7551/978-0-262-32621-6-ch128. Utimula: doi:10.1162/artl_a_00466. | Low: incomplete |
| **E7** | P5:56–57 | Morphological innovation protection: "this programme has never run it" | It has: RBT-74 (`runs/RBT-74/REPORT.md`, `--protect-morphology 4`). The paired verdict was null at four seeds, superseded by RBT-85. The within-run finding stands: a body change costs 0.05–0.13 of bout score and four controller-only rounds recover none of it. The sentence is stale, and the premise now has an in-programme replication to cite. | Medium: stale |
| **E8** | `docs/origins/README.md` | (no error) | The Salmon (2003) URL resolves, and the paper is a position paper with no results (§2). Any future text that treats it as evidence would be an error. | Note |

- **Checked and correct:** everything else in P5 §0 and P7 §7, and the 2005 proposal's bibliography where it could be checked.
  - The Pollack et al. (2001) page range 215–223 is right.
  - Sims (1994b) pp. 28–39 in *Artificial Life IV* is confirmed by the author's PDF. Crossref's digital-chapter record gives 26–32; that is the digital edition's pagination.
  - The 1,305,840 figure is right.
  - Geb's "first … to pass" is the author's own claim.
  - Division Blocks' "simulated sun" is right.
- **Adami & Brown (1994).** pp. 377–381 is the conventional citation. Crossref's digital record gives 373–377, which could not be settled against print.

These are corrections for the next revision of each paper. This review changes none of them.

**Numbering against the logs (citation check F7).** `verification/6-errata-gap.md` numbers its findings differently:

| log | §8 |
|---|---|
| E1 | E1 |
| E2 | E4 |
| E3 | E2 |
| E4 | E3 |
| E5 | E5 |
| E6 and E7 | E6 |
| E8 | the page-number notes above |

§8's E7 (RBT-74) and E8 are not in the log.

---

## 9. UNVERIFIED (not cited above)

- **Balakrishnan, K. & Honavar, V. (1996).** "On sensor evolution in robotics", *Genetic Programming 1996*, pp. 455–460 (the 2005 proposal's [1]).
  - Found only in other papers' reference lists; no primary record reached.
  - The 2001 MIT Press chapter (§3) is the verified substitute. A one-page AAAI-96 student abstract by the same authors exists (p. 1378), but its scanned text could not be read.
- **Mark, A., Polani, D. & Uthmann, T. (1998).** "A framework for sensor evolution in a population of Braitenberg vehicle-like agents". The authors, year and title are confirmed; the venue (ALIFE VI) and the pages are not.
- **Paul, C. & Bongard, J. C. (2001).** "The road less travelled: morphology in the optimization of biped robot locomotion", IROS 2001.
  - The record was seen, but the abstract was not read. Its reported "co-evolution beats a fixed body" rests on secondary descriptions.
- **Cheney et al. (2018)'s fixed-morphology baseline.** Not confirmed. Its confirmed comparison is co-optimisation with and without protection.
- **Clark, J. & Amodei, D. (2016).** "Faulty reward functions in the wild" (OpenAI blog). The page returned 403, so the authors and date were not confirmed.
- **Venues.** Peng et al. (dynamics randomisation), cited above by arXiv number only; Tobin et al. (domain randomisation).
- **Content not read:** Jakobi et al. (1995). Its record, pp. 704–720, is confirmed. The citation check (F8) confirmed Kriegman et al. (2018) as *Sci. Rep.* 8: 13934 and De Carlo et al. as *Evolutionary Intelligence* 17(3): 1733–1749 (print 2024). Both are completed in the body.
- **Requested but not found:**
  - a "Stanley et al., CPPN-NEAT and ecological …" paper;
  - "Evolving virtual creatures in open-ended environments";
  - any Avida experiment with up, down and control lines and realised h²;
  - any paper using "morphological bypass";
  - a Lehman paper testing the bypass;
  - a verified simulation paper showing that patchy resources made sensing evolve.

  On the last: the environmental-structure argument in §3 rests on Goldstein & Soyer, Kussell & Leibler, Stephens and Floreano & Mondada instead.
- **Leads not followed up:**
  - Matsushita et al. (2006), *Robotics and Autonomous Systems* 54;
  - Paul (2005), *Adaptive Behavior*, whose citation context calls morphology "an extra-dimensional bypass";
  - Inden & Jost (2013, ECAL), which argues that bypasses may not keep pace with the growth of the search space.

  These are worth a look for RBT-116.

---

## 10. Synthesis

### 10.1 What is genuinely new here

1. **The 2005 comparison, run with an audit.** Others have compared evolving bodies with fixed ones (§1.4). None of those we found measured the bodies apart from the score, found and removed the allowances that decided the comparison (mass, spawn energy, motor capacity), and reported that the designed body then wins. The follow-up paper's contribution is the audit as much as the verdict.
2. **A designed body and co-evolved bodies in one fitness-free economy**, compared on realised income, with the heritability of that income measured beside the heritability of the arena score. Not found in a directed search (§7).
3. **A selection-response benchmark for a physics simulator:** divergent lines, realised h², drift lines, and two body classes, with the decomposition that showed the response was mostly an allowance (§5).
4. **The anatomy of a chemotaxis valley, measured in one body.** Paper 8's prize, proposal rate and magnitude gap, and paper 10's result that a planted compass is held but not spread, with s at 0 to 0.08. The perception literature has the ingredients (§3), but not this decomposition.
5. **Instrument validity as a separate axis** (paper 7): cases where the bug is in the measurement, not the world. We found nothing that catalogues these.

### 10.2 What we are re-deriving

These should be credited, not claimed:
- **Settling before scoring:** Sims 1994, in one sentence.
- **Area-scaled actuator strength, clamped:** Sims 1994. Not re-derived, and not yet adopted. Note that Sims's cap is per effector (per DOF), so the per-joint cap proposed in §10.3 is ours, not his.
- **Stability checks and explosion handling:** Taylor & Massey 2001.
- **"Evolution will find and exploit every leak":** Sims 1994; Lehman et al. 2020; Krakovna et al. 2020.
- **Premature morphological convergence, and its remedy:** Cheney et al. 2016, 2018, and RBT-74's replication of the premise.
- **Implicit, greedy selection in fitness-free worlds:** Bredeche and Montanier's mEDEA; Lehman & Stanley 2011.
- **"The cow is the correct answer":** blind search is optimal when cues are short-range and the world is uniform (Viswanathan et al. 1999; Kussell & Leibler 2005; Stephens 1991).
- **Perception evolves when the world makes it decision-relevant:** Cliff et al. 1993; Floreano & Mondada 1996; Goldstein & Soyer 2008.
- **Realised heritability in an evolutionary algorithm:** Mühlenbein & Schlierkamp-Voosen 1993.
- **Random-selection drift controls:** Bedau et al. 1997; Channon 2006, 2024.

### 10.3 What others' fixes suggest for RBT-120 and RBT-121

These are proposals for the auditors and the design adversary. Each is off by default behind a flag, as RBT-120 requires.

1. **Motor capacity (RBT-120).**
   - **Sims's area rule is the principled precedent:** each effector's maximum strength is proportional to the cross-sectional area of the parts it joins (≈ mass^⅔ for isometric parts, though not for long, thin ones), and forces are clamped at it.
   - **Sims's cap is per effector, i.e. per DOF, so it does not remove the ×3 per ball joint.** Capping **per joint rather than per DOF** is **the programme's own proposal**, going beyond Sims. In RBT-120's design it should read "Sims's area rule, applied per joint (our choice)".
   - **The minimal change in MuJoCo** is a joint-level `actuatorfrcrange`. It clamps the total across a ball joint's three motors, so one joint cannot hold three times the capacity.
   - **Calibration:** the RBT-120 constraint, that the Pioneer's Σgear/mass of 1.76 is unchanged, still fixes the constant.
   - **Cost:** Cheney 2013's actuated-material charge is a second, softer option. It charges capacity where our 0.03/kJ work cost charges use. In the RBT-113 D line, selection was *for* waste, so only a capacity cap bounds it.
2. **Penetration (RBT-121 A).**
   - Stiffen `solref`/`solimp` for the masses involved, keeping `timeconst` at least twice the step.
   - Add a trip wire: maximum penetration per season, logged, with a season voided above a tolerance, as Sims discarded bodies.
   - Consider a minimum part size, as Cheney's fix raised the minimum creature size.
   - Krčah-style pre-simulation checks for self-penetration and tiny parts are cheap.
3. **A budget for every capacity that is not mass** (RBT-120 item 5), as Auerbach & Bongard's "complexity must cost" predicts: sensors, joint limits and damping. Anything free will be bought.
4. **Randomise what must not be exploited** (Jakobi 1997): contact softness, friction and spawn height within plausible ranges, so that exploits stop paying reliably.
5. **Cross-check against conservative physics** (Koos et al. 2013; Lipson & Pollack's quasi-static physics): re-score champions under a stiffer contact model and a smaller timestep. A large drop flags an exploit. This is a trip wire made into an instrument, in the spirit of the analysis toolkit.
6. **Perception (RBT-121 C).** A world where perception pays needs one of:
   - sparse, patchy or moving food;
   - a resource that coverage cannot collect (a single source, or a home to return to on limited energy);
   - enough variation, on the right timescale, to repay a sensor.

   Prefer world structure over a task channel (MONEE) if the ecology is to stay fitness-free. Measure what the new world selects for rather than assume it (Miras & Eiben 2019).
7. **Keep watching.** Lehman et al.'s advice, which matches the follow-up paper's practice: measure champions alone and look at them. Every exploit in our table was found that way, never from the score.

### 10.4 References for progress report 2 (RBT-119)

The origin (Jucovy 2005) and the proposal's own sources are cited in addition to these. Eleven, all verified above:

1. **Sims, K. (1994b).** Evolving 3D morphology and behavior by competition. *Artificial Life* 1(4): 353–372. The genotype and the competitive task.
2. **Sims, K. (1994a).** Evolving virtual creatures. *SIGGRAPH '94*: 15–22. The settle protocol and the actuator-strength rule we are now re-deriving.
3. **Conrad, M. (1990).** The geometry of evolution. *BioSystems* 24: 61–81. The extradimensional bypass.
4. **Bongard, J. C. & Paul, C. (2001).** Making evolution an offer it can't refuse. *ECAL 2001*, LNCS 2159: 401–412. The one direct test of the bypass in robots, and a mixed one.
5. **Watson, R. A., Ficici, S. G. & Pollack, J. B. (1999).** Embodied evolution. *CEC 1999*: 335–342. Embodied evolution.
6. **Salmon, B. (2003).** Swarthmore CS81 project. "Holistic evolution", and the proposal to combine it with embodied evolution.
7. **Braitenberg, V. (1984).** *Vehicles.* MIT Press. The compass.
8. **Cheney, N., Bongard, J., SunSpiral, V. & Lipson, H. (2018).** Scalable co-optimization of morphology and control in embodied machines. *J. R. Soc. Interface* 15: 20170937. Why co-optimisation discards new bodies, and innovation protection.
9. **Mertan, A. & Cheney, N. (2026).** Evolutionary brain-body co-optimization consistently fails to select for morphological potential. *Artificial Life*, doi:10.1162/ARTL.a.476. The same finding, against complete knowledge of the landscape.
10. **Lehman, J., Clune, J., Misevic, D., et al. (2020).** The surprising creativity of digital evolution. *Artificial Life* 26(2): 274–306. Evolution exploiting the simulator.
11. **Bredeche, N., Haasdijk, E. & Prieto, A. (2018).** Embodied evolution in collective robotics: a review. *Frontiers in Robotics and AI* 5: 12. Where embodied evolution went.

**If there is room for a twelfth,** Falconer & Mackay (1996) for realised heritability, when the report explains the RBT-113 benchmark.

**Keep report 1's Braitenberg credit.** Say, as the Origins doc asks, that the compass results are for the fixed body only.
