"""RBT-104 (design adversary F2): compare a config.json against a committed one, tolerating fields
that later tickets added AT THEIR DEFAULT VALUES (RBT-105's ecology.breed_stream = null, RBT-96's
holistic_stream_salt = 0, ...).

A field present in `got` but absent from `ref` is tolerated, and named, iff its value equals the
default of the dataclass that owns it in the running code.  Owners: the top level is EvolutionConfig,
`ecology.` EcologyConfig, `mutation.` MutationConfig, `sim.` SimConfig and its nested configs.  An
added field at any other value, or one whose owner cannot be found, is NOT tolerated: the
comparison then fails, which is the safe direction.
"""
import dataclasses

from rabbitstew.ecology import EcologyConfig
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.genetics import MutationConfig
from rabbitstew.simulation import SimConfig


def _default(cls, name):
    for f in dataclasses.fields(cls):
        if f.name == name:
            if f.default is not dataclasses.MISSING:
                return True, f.default
            if f.default_factory is not dataclasses.MISSING:  # type: ignore[misc]
                return True, f.default_factory()  # type: ignore[misc]
    return False, None


def _nested(cls, name):
    for f in dataclasses.fields(cls):
        if f.name == name:
            ok, v = _default(cls, name)
            if ok and dataclasses.is_dataclass(v):
                return type(v)
    return None


OWNERS = {"": EvolutionConfig, "ecology": EcologyConfig, "mutation": MutationConfig, "sim": SimConfig}


def added_at_default(got, ref, path="", cls=None):
    """Drop, in place, fields of `got` absent from `ref` that sit at their dataclass default.
    Returns the dotted names dropped."""
    cls = cls if cls is not None else OWNERS.get(path.rstrip("."))
    out = []
    if not (isinstance(got, dict) and isinstance(ref, dict)):
        return out
    for k in list(got):
        if k not in ref:
            if cls is not None and dataclasses.is_dataclass(cls):
                ok, dv = _default(cls, k)
                if ok and got[k] == (dv.to_dict() if hasattr(dv, "to_dict") else dv):
                    out.append(path + k)
                    del got[k]
        elif isinstance(got[k], dict):
            sub = OWNERS.get(path + k) or (_nested(cls, k) if cls is not None and dataclasses.is_dataclass(cls) else None)
            out += added_at_default(got[k], ref[k], path + k + ".", sub)
    return out
