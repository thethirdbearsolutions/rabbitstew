"""Rabbitstew: a robot simulator with variable morphologies.

Robotic Artificial Brain/Body-Intertwined Simulation Toolkit and Evolution
Workshop.  The package implements the design described in Ethan G. Jucovy's
2005 proposal *Rabbitstew: A Robot Simulator with Variable Morphologies*:

* :mod:`rabbitstew.genotype` -- directed-graph robot genotypes (Nodes,
  Connections, Segments, Brains).
* :mod:`rabbitstew.synthesis` -- breadth-first expansion of a genotype into a
  phenotype, honouring the size-ratio and recursive limits.
* :mod:`rabbitstew.world` / :mod:`rabbitstew.simulation` -- physical
  instantiation of phenotypes in MuJoCo and the two-robot competitive bout.
* :mod:`rabbitstew.brain` -- the runtime neural networks.
* :mod:`rabbitstew.trajectory` / :mod:`rabbitstew.visualizer` -- the decoupled
  trajectory data file and its replay visualizer.
* :mod:`rabbitstew.fixed` -- the human-designed, Pioneer-style fixed body.
* :mod:`rabbitstew.genetics` / :mod:`rabbitstew.evolution` -- mutation,
  crossover and the holistic-versus-conventional evolution experiment.
"""

from .genotype import (
    Brain,
    Connection,
    Effector,
    Genotype,
    JointType,
    Link,
    Neuron,
    Node,
    Segment,
    Sensor,
    Shape,
    UnitRef,
    random_genotype,
)
from .synthesis import SynthesisConfig, synthesize
from .simulation import SimConfig, Simulation, BoutResult, run_bout

__all__ = [
    "Brain",
    "Connection",
    "Effector",
    "Genotype",
    "JointType",
    "Link",
    "Neuron",
    "Node",
    "Segment",
    "Sensor",
    "Shape",
    "UnitRef",
    "random_genotype",
    "SynthesisConfig",
    "synthesize",
    "SimConfig",
    "Simulation",
    "BoutResult",
    "run_bout",
]

__version__ = "0.1.0"
