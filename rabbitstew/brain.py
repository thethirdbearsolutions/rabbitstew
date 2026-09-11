"""Runtime neural networks.

Every Brain in a phenotype (one per Part instance plus the global Brain) is
folded into a single dense network per robot: activation vector ``a``,
weight matrix ``W`` and bias ``b``.  All non-sensor units update
synchronously from the previous tick's activations, ``a <- f(W a + b)``,
where ``f`` is the unit's transfer function; sensor units are overwritten
with their environmental readings each tick.  Effector outputs lie in
``[-1, 1]`` and are summed per driven degree of freedom.

Transfer functions (:data:`rabbitstew.genotype.NEURON_FUNCS`): ``tanh``,
``sin``, ``abs`` (``tanh|x|``), ``relu`` (``tanh max(x, 0)``), ``sign``,
``integrate`` (leaky integrator, ``0.9 a + 0.2 tanh x`` clipped to ±1) and
``differentiate`` (``tanh`` of the change in input since the last tick).
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
    freq: float = 1.0
    phase: float = 0.0


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
        funcs: dict[str, list[int]] = {}
        for i, ui in enumerate(phenotype.units):
            u = ui.unit
            if u.kind == "sensor":
                self.is_sensor[i] = True
                self.sensors.append(SensorSpec(i, ui.part, u.source, u.axis, getattr(u, "freq", 1.0), getattr(u, "phase", 0.0)))
                continue
            self.bias[i] = u.bias
            func = u.func if u.kind == "neuron" else "tanh"
            funcs.setdefault(func, []).append(i)
            if u.kind == "effector" and ui.part is not None:
                part = phenotype.parts[ui.part]
                if part.parent is not None and part.joint_type.ndof > 0:
                    dof = u.dof % part.joint_type.ndof
                    self.effectors.setdefault((ui.part, dof), []).append(i)
        self.funcs = {k: np.array(v, dtype=int) for k, v in funcs.items()}
        for src, dst, w in phenotype.links:
            self.W[dst, src] += w
        self.sensor_idx = np.array([s.unit for s in self.sensors], dtype=int)
        self.activation = np.zeros(n)
        self._prev_input = np.zeros(n)

    def reset(self) -> None:
        self.activation[:] = 0.0
        self._prev_input[:] = 0.0

    def step(self, sensor_values: np.ndarray) -> None:
        """Advance the network one tick given readings aligned with :attr:`sensors`."""
        if self.n == 0:
            return
        x = self.W @ self.activation + self.bias
        new = np.zeros(self.n)
        for func, idx in self.funcs.items():
            xi = x[idx]
            if func == "tanh":
                new[idx] = np.tanh(xi)
            elif func == "sin":
                new[idx] = np.sin(xi)
            elif func == "abs":
                new[idx] = np.tanh(np.abs(xi))
            elif func == "relu":
                new[idx] = np.tanh(np.maximum(xi, 0.0))
            elif func == "sign":
                new[idx] = np.sign(xi)
            elif func == "integrate":
                new[idx] = np.clip(0.9 * self.activation[idx] + 0.2 * np.tanh(xi), -1.0, 1.0)
            elif func == "differentiate":
                new[idx] = np.tanh(xi - self._prev_input[idx])
            else:  # pragma: no cover - validated upstream
                raise ValueError(f"unknown transfer function {func!r}")
        self._prev_input = x
        if len(self.sensor_idx):
            new[self.sensor_idx] = sensor_values
        self.activation = new

    def effector_output(self, part: int, dof: int) -> float:
        units = self.effectors.get((part, dof))
        if not units:
            return 0.0
        return float(np.clip(self.activation[units].sum(), -1.0, 1.0))

    def outputs(self) -> dict[tuple[int, int], float]:
        return {key: self.effector_output(*key) for key in self.effectors}
