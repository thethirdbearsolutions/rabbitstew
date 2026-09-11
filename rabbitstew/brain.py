"""Runtime neural networks.

Every Brain in a phenotype (one per Part instance plus the global Brain) is
folded into a single dense network per robot: activation vector ``a``,
weight matrix ``W`` and bias ``b``.  All non-sensor units update
synchronously, ``a <- tanh(W a + b)``, using the previous step's activations;
sensor units are overwritten with their environmental readings each step.
Effector outputs lie in ``[-1, 1]`` and are summed per driven degree of
freedom.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .synthesis import Phenotype


@dataclass
class SensorSpec:
    unit: int  #: index into the activation vector
    part: int  #: Part whose Segment the sensor sits on
    source: str
    axis: int


class RuntimeBrain:
    def __init__(self, phenotype: Phenotype):
        self.phenotype = phenotype
        n = len(phenotype.units)
        self.n = n
        self.W = np.zeros((n, n))
        self.bias = np.zeros(n)
        self.is_sensor = np.zeros(n, dtype=bool)
        self.sensors: list[SensorSpec] = []
        self.effectors: dict[tuple[int, int], list[int]] = {}  # (part, dof) -> unit indices
        for i, ui in enumerate(phenotype.units):
            u = ui.unit
            if u.kind == "sensor":
                self.is_sensor[i] = True
                self.sensors.append(SensorSpec(i, ui.part, u.source, u.axis))
            else:
                self.bias[i] = u.bias
                if u.kind == "effector" and ui.part is not None:
                    part = phenotype.parts[ui.part]
                    if part.parent is not None and part.joint_type.ndof > 0:
                        dof = u.dof % part.joint_type.ndof
                        self.effectors.setdefault((ui.part, dof), []).append(i)
        for src, dst, w in phenotype.links:
            self.W[dst, src] += w
        self.activation = np.zeros(n)

    def reset(self) -> None:
        self.activation[:] = 0.0

    def step(self, sensor_values: np.ndarray) -> None:
        """Advance the network one tick given readings aligned with :attr:`sensors`."""
        if self.n == 0:
            return
        new = np.tanh(self.W @ self.activation + self.bias)
        if self.sensors:
            idx = [s.unit for s in self.sensors]
            new[idx] = sensor_values
        self.activation = new

    def effector_output(self, part: int, dof: int) -> float:
        units = self.effectors.get((part, dof))
        if not units:
            return 0.0
        return float(np.clip(self.activation[units].sum(), -1.0, 1.0))

    def outputs(self) -> dict[tuple[int, int], float]:
        return {key: self.effector_output(*key) for key in self.effectors}
