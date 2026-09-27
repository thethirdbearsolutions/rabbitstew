# Origins

- **[`jucovy-2005-rabbitstew-proposal.pdf`](jucovy-2005-rabbitstew-proposal.pdf).** Ethan G. Jucovy, *Rabbitstew: A Robot Simulator with Variable Morphologies*, 14 December 2005.
  - Swarthmore College CS97 (senior conference) proposal.
  - This is the design the simulator implements. See the README's *Design* and *Departures from the paper* sections.
  - The experiment it proposes sets holistic evolution (body and brain together, from random morphologies) against conventional evolution (weights only, in a fixed Pioneer-style body) in a competitive race to the arena centre.
  - It predicts that holistic evolution loses early and wins eventually.
  - It gives three reasons:
    - body-specific strategies;
    - stronger selection in a more variable population;
    - Conrad's extradimensional bypass.

Related work the proposal leans on most, not copied here:

- **Branen Salmon (2003), *Embodied evolution in a morphologically heterogeneous population of robots*.** Swarthmore CS81 senior seminar project, <https://www.cs.swarthmore.edu/~meeden/cs81/s03/projects/salmon.pdf>.
  - The proposal takes the term "holistic evolution" from it.
  - It argues for holistic evolution combined with *embodied* evolution: selection and reproduction happen between individuals in the task environment, with no central evaluator (Watson, Ficici & Pollack 1999). That is the kind of ecology the programme adopted after the competitive experiment.
- **Karl Sims (1994), *Evolving 3D morphology and behavior by competition*, Artificial Life IV.** The genotype design and the competitive task follow it.
- **Michael Conrad (1990), *The geometry of evolution*, Biosystems 24:61–81.** The extradimensional bypass.
