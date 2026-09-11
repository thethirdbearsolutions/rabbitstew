"""The trajectory data file shared by the simulator and the visualizer.

At the start of a simulation the specification of every body unit is written
out: a shape code followed by the unit's absolute dimensions (one number for
a sphere, two for a cylinder, three for a box).  Every ``n`` control ticks the
state of the simulation is appended: a position vector and an orientation
quaternion ``(w, x, y, z)`` for every unit, in the same order as the header,
i.e. seven floating-point numbers per unit per frame.

Conventions: box extents are along the unit's local X, Y, Z; a cylinder's
length runs along its local Z (MuJoCo's convention); positions are the
centres of the shapes.

File layout (plain text)::

    rabbitstew-trajectory 1
    dt <seconds between frames>
    robots <units in robot 0> <units in robot 1> ...
    scenery <count>                        (optional: static terrain)
    <shape> <dims...> x y z qw qx qy qz    (one line per scenery shape)
    units <total units>
    <shape> <dim> [<dim> [<dim>]]         (one line per unit)
    frames
    x y z qw qx qy qz  x y z qw qx qy qz ...   (one line per frame)
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .genotype import Shape

FORMAT_LINE = "rabbitstew-trajectory 1"


@dataclass
class UnitSpec:
    shape: Shape
    dims: tuple


@dataclass
class SceneryItem:
    shape: Shape
    dims: tuple
    pos: tuple
    quat: tuple = (1.0, 0.0, 0.0, 0.0)


@dataclass
class Trajectory:
    dt: float
    units: list = field(default_factory=list)  #: list[UnitSpec]
    robots: list = field(default_factory=list)  #: number of units per robot
    frames: list = field(default_factory=list)  #: each an (n_units, 7) array
    scenery: list = field(default_factory=list)  #: list[SceneryItem], static terrain

    @property
    def n_frames(self) -> int:
        return len(self.frames)

    @property
    def duration(self) -> float:
        return self.dt * max(0, self.n_frames - 1)

    def as_array(self) -> np.ndarray:
        if not self.frames:
            return np.zeros((0, len(self.units), 7))
        return np.stack(self.frames)

    def robot_of_unit(self, unit: int) -> int:
        total = 0
        for i, n in enumerate(self.robots):
            total += n
            if unit < total:
                return i
        return max(0, len(self.robots) - 1)

    # -- I/O ---------------------------------------------------------------- #
    def write(self, path) -> None:
        with open(path, "w") as f:
            f.write(FORMAT_LINE + "\n")
            f.write(f"dt {self.dt:.9g}\n")
            f.write("robots " + " ".join(str(int(n)) for n in self.robots) + "\n")
            if self.scenery:
                f.write(f"scenery {len(self.scenery)}\n")
                for sc in self.scenery:
                    f.write(f"{int(sc.shape)} " + " ".join(f"{d:.9g}" for d in sc.dims) + " " + " ".join(f"{v:.9g}" for v in list(sc.pos) + list(sc.quat)) + "\n")
            f.write(f"units {len(self.units)}\n")
            for u in self.units:
                f.write(f"{int(u.shape)} " + " ".join(f"{d:.9g}" for d in u.dims) + "\n")
            f.write("frames\n")
            for fr in self.frames:
                f.write(" ".join(f"{v:.7g}" for v in np.asarray(fr).reshape(-1)) + "\n")

    @staticmethod
    def read(path) -> "Trajectory":
        with open(path) as f:
            lines = [ln.strip() for ln in f]
        if not lines or lines[0] != FORMAT_LINE:
            raise ValueError("not a rabbitstew trajectory file")
        dt = 0.0
        robots: list[int] = []
        units: list[UnitSpec] = []
        scen: list[SceneryItem] = []
        i = 1
        n_units = None
        while i < len(lines):
            ln = lines[i]
            i += 1
            if not ln:
                continue
            if ln.startswith("dt "):
                dt = float(ln.split()[1])
            elif ln.startswith("robots"):
                robots = [int(x) for x in ln.split()[1:]]
            elif ln.startswith("scenery "):
                for _ in range(int(ln.split()[1])):
                    parts = lines[i].split()
                    i += 1
                    shape = Shape(int(parts[0]))
                    nd = shape.ndims
                    vals = [float(x) for x in parts[1:]]
                    scen.append(SceneryItem(shape, tuple(vals[:nd]), tuple(vals[nd : nd + 3]), tuple(vals[nd + 3 : nd + 7])))
            elif ln.startswith("units "):
                n_units = int(ln.split()[1])
                for _ in range(n_units):
                    parts = lines[i].split()
                    i += 1
                    units.append(UnitSpec(Shape(int(parts[0])), tuple(float(x) for x in parts[1:])))
            elif ln == "frames":
                break
            else:
                raise ValueError(f"unexpected header line {ln!r}")
        if n_units is None:
            raise ValueError("trajectory file has no units section")
        frames = []
        for ln in lines[i:]:
            if not ln:
                continue
            vals = np.array([float(x) for x in ln.split()])
            frames.append(vals.reshape(n_units, 7))
        return Trajectory(dt=dt, units=units, robots=robots or [n_units], frames=frames, scenery=scen)
