"""Physical instantiation of phenotypes in MuJoCo.

For every :class:`~rabbitstew.synthesis.Part` up to three MuJoCo objects are
created: a body (mass properties), a geom (spatial extent, collision) and,
for all Parts but the root, a joint to the parent body.  Fixed joints are
expressed by welding the child body to its parent (a body with no joint).
Effectors drive joint-space motors whose gear is proportional to the larger
of the two connected masses.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

import mujoco
import numpy as np

from . import quat
from .genotype import JointType, Shape
from .synthesis import Phenotype

# Quaternion rotating a MuJoCo cylinder (length along Z) so its length lies along local X.
_CYL_QUAT = quat.from_axis_angle((0, 1, 0), np.pi / 2)


@dataclass
class Spawn:
    """Where and how a robot is placed in the world."""

    position: tuple = (0.0, 0.0, 0.0)  #: x, y of the root; z is a ground offset added to the computed lift
    yaw: float = 0.0
    static: bool = False  #: weld the root to the world (walls, blocks)


@dataclass
class RobotIndex:
    """MuJoCo ids for one instantiated robot."""

    phenotype: Phenotype
    spawn: Spawn
    root_body: int = -1
    bodies: list = field(default_factory=list)  #: body id per Part
    geoms: list = field(default_factory=list)  #: geom id per Part
    joints: list = field(default_factory=list)  #: joint id per Part (-1 when none)
    actuators: dict = field(default_factory=dict)  #: (part index, dof) -> actuator id
    root_qpos_adr: int = -1  #: qpos address of the root free joint (-1 when static)


@dataclass
class WorldConfig:
    timestep: float = 0.005
    gravity: float = -9.81
    motor_strength: float = 4.0  #: gear (N m per kg, or N per kg for sliders) times the larger connected mass
    joint_damping: float = 0.05  #: damping as a fraction of the actuator gear
    joint_armature: float = 0.005
    friction: float = 1.0
    ground_clearance: float = 0.01
    arena_radius: float = 0.0  #: > 0 adds a circular fence of static boxes at this radius


def _fmt(values) -> str:
    return " ".join(f"{float(v):.6g}" for v in np.atleast_1d(values))


def _geom_attrs(part) -> dict:
    if part.shape == Shape.BOX:
        return {"type": "box", "size": _fmt(np.asarray(part.dims) / 2.0)}
    if part.shape == Shape.SPHERE:
        return {"type": "sphere", "size": _fmt([part.dims[0]])}
    return {"type": "cylinder", "size": _fmt([part.dims[0], part.dims[1] / 2.0]), "quat": _fmt(_CYL_QUAT)}


def build_xml(phenotypes: list[Phenotype], spawns: list[Spawn], config: WorldConfig, lifts: Optional[list] = None) -> str:
    """Return the MJCF document for the given robots.

    ``lifts`` are per-robot vertical offsets (computed by :func:`build_model`)
    added to the root position so every robot starts resting on the ground.
    """
    if lifts is None:
        lifts = [0.0] * len(phenotypes)
    root = ET.Element("mujoco", model="rabbitstew")
    ET.SubElement(root, "compiler", angle="radian", autolimits="true")
    ET.SubElement(root, "option", timestep=f"{config.timestep:g}", gravity=f"0 0 {config.gravity:g}")
    default = ET.SubElement(root, "default")
    ET.SubElement(default, "geom", friction=f"{config.friction:g} 0.005 0.0001", condim="3", solref="0.01 1", solimp="0.9 0.95 0.001")
    ET.SubElement(default, "joint", armature=f"{config.joint_armature:g}")
    ET.SubElement(default, "motor", ctrllimited="true", ctrlrange="-1 1")
    world = ET.SubElement(root, "worldbody")
    ET.SubElement(world, "geom", name="floor", type="plane", size="0 0 1", rgba="0.85 0.85 0.8 1")
    ET.SubElement(world, "light", pos="0 0 4", dir="0 0 -1", diffuse="0.8 0.8 0.8")
    if config.arena_radius > 0:
        n = 24
        for k in range(n):
            ang = 2 * np.pi * k / n
            seg = 2 * np.pi * config.arena_radius / n
            ET.SubElement(
                world,
                "geom",
                name=f"fence{k}",
                type="box",
                size=f"0.05 {seg / 2:.4g} 0.3",
                pos=_fmt([config.arena_radius * np.cos(ang), config.arena_radius * np.sin(ang), 0.3]),
                quat=_fmt(quat.yaw(ang)),
                rgba="0.5 0.5 0.5 0.5",
            )
    actuators = ET.SubElement(root, "actuator")

    for ri, (ph, spawn) in enumerate(zip(phenotypes, spawns)):
        elems: dict[int, ET.Element] = {}
        for part in ph.parts:
            name = f"r{ri}_p{part.index}"
            if part.parent is None:
                pos = np.array([spawn.position[0], spawn.position[1], spawn.position[2] + lifts[ri]])
                body = ET.SubElement(world, "body", name=name, pos=_fmt(pos), quat=_fmt(quat.yaw(spawn.yaw)))
                if not spawn.static:
                    ET.SubElement(body, "freejoint", name=f"r{ri}_root")
            else:
                parent_el = elems[part.parent]
                body = ET.SubElement(parent_el, "body", name=name, pos=_fmt(part.attach_pos), quat=_fmt(part.rel_quat))
                parent_part = ph.parts[part.parent]
                gear = config.motor_strength * max(part.mass, parent_part.mass)
                damping = config.joint_damping * gear
                jname = f"r{ri}_j{part.index}"
                if part.joint_type == JointType.HINGE:
                    attrs = {"name": jname, "type": "hinge", "axis": _fmt(part.joint_axis), "damping": f"{damping:g}"}
                    if part.joint_range is not None:
                        attrs["range"] = _fmt(part.joint_range)
                    ET.SubElement(body, "joint", **attrs)
                    ET.SubElement(actuators, "motor", name=f"r{ri}_a{part.index}_0", joint=jname, gear=f"{gear:g}")
                elif part.joint_type == JointType.SLIDER:
                    attrs = {"name": jname, "type": "slide", "axis": _fmt(part.joint_axis), "damping": f"{damping:g}"}
                    if part.joint_range is not None:
                        attrs["range"] = _fmt(part.joint_range)
                    ET.SubElement(body, "joint", **attrs)
                    ET.SubElement(actuators, "motor", name=f"r{ri}_a{part.index}_0", joint=jname, gear=f"{gear:g}")
                elif part.joint_type == JointType.BALL:
                    ET.SubElement(body, "joint", name=jname, type="ball", damping=f"{damping:g}")
                    for dof in range(3):
                        g = [0.0, 0.0, 0.0]
                        g[dof] = gear
                        ET.SubElement(actuators, "motor", name=f"r{ri}_a{part.index}_{dof}", joint=jname, gear=_fmt(g))
                # FIXED: no joint, the body is welded to its parent.
            geom_attrs = _geom_attrs(part)
            geom_attrs.update(
                name=f"r{ri}_g{part.index}",
                pos=_fmt([part.geom_offset, 0.0, 0.0]),
                mass=f"{part.mass:g}",
                rgba=_robot_color(ri, part.depth),
            )
            ET.SubElement(body, "geom", **geom_attrs)
            elems[part.index] = body
    return ET.tostring(root, encoding="unicode")


def _robot_color(ri: int, depth: int) -> str:
    palette = [(0.85, 0.3, 0.25), (0.25, 0.45, 0.85), (0.3, 0.7, 0.35), (0.85, 0.65, 0.2), (0.6, 0.35, 0.75)]
    r, g, b = palette[ri % len(palette)]
    f = max(0.55, 1.0 - 0.12 * depth)
    return f"{r * f:.3f} {g * f:.3f} {b * f:.3f} 1"


def build_model(phenotypes: list[Phenotype], spawns: list[Spawn], config: Optional[WorldConfig] = None):
    """Compile a MuJoCo model for the robots and return ``(model, data, [RobotIndex])``.

    The model is compiled twice: once to measure how far each robot must be
    lifted so that no part starts below the ground, then again with the
    corrected root positions.
    """
    if config is None:
        config = WorldConfig()
    if len(spawns) != len(phenotypes):
        raise ValueError("one Spawn per phenotype is required")
    xml = build_xml(phenotypes, spawns, config)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    lifts = []
    for ri, ph in enumerate(phenotypes):
        lowest = min(
            float(data.geom_xpos[model.geom(f"r{ri}_g{p.index}").id][2] - model.geom_rbound[model.geom(f"r{ri}_g{p.index}").id])
            for p in ph.parts
        )
        lifts.append(config.ground_clearance - lowest)
    xml = build_xml(phenotypes, spawns, config, lifts)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    indices = []
    for ri, (ph, spawn) in enumerate(zip(phenotypes, spawns)):
        idx = RobotIndex(phenotype=ph, spawn=spawn)
        for p in ph.parts:
            idx.bodies.append(model.body(f"r{ri}_p{p.index}").id)
            idx.geoms.append(model.geom(f"r{ri}_g{p.index}").id)
            if p.parent is not None and p.joint_type != JointType.FIXED:
                idx.joints.append(model.joint(f"r{ri}_j{p.index}").id)
            else:
                idx.joints.append(-1)
            for dof in range(p.joint_type.ndof if p.parent is not None else 0):
                idx.actuators[(p.index, dof)] = model.actuator(f"r{ri}_a{p.index}_{dof}").id
        idx.root_body = idx.bodies[0]
        if not spawn.static:
            idx.root_qpos_adr = int(model.jnt_qposadr[model.joint(f"r{ri}_root").id])
        indices.append(idx)
    mujoco.mj_forward(model, data)
    return model, data, indices
