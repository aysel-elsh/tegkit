"""Operating curves: I-V, power and the maximum power point."""

from __future__ import annotations

from typing import NamedTuple, Union

from .array import TEGArray
from .module import TEGModule

__all__ = ["OperatingPoint", "iv_curve", "max_power_point", "as_module"]

Source = Union[TEGModule, TEGArray]


class OperatingPoint(NamedTuple):
    current: float  # A
    voltage: float  # V
    power: float  # W


def as_module(source: Source) -> TEGModule:
    """Return a single equivalent :class:`TEGModule` for a module or array."""
    if isinstance(source, TEGArray):
        return source.as_module()
    if isinstance(source, TEGModule):
        return source
    raise TypeError(f"expected TEGModule or TEGArray, got {type(source).__name__}")


def iv_curve(source: Source, delta_t: float, points: int = 21) -> list[OperatingPoint]:
    """Sweep current from 0 (open circuit) to short circuit.

    The generator is a Thevenin source, so ``V = Voc - I*R`` is a straight line
    and power is a parabola peaking at half the short-circuit current.
    """
    if points < 2:
        raise ValueError("points must be >= 2")
    m = as_module(source)
    voc = m.open_circuit_voltage(delta_t)
    isc = voc / m.resistance
    curve = []
    for k in range(points):
        i = isc * k / (points - 1)
        v = voc - i * m.resistance
        curve.append(OperatingPoint(i, v, i * v))
    return curve


def max_power_point(source: Source, delta_t: float) -> OperatingPoint:
    """Current, voltage and power at the maximum power point (I = Isc/2)."""
    m = as_module(source)
    voc = m.open_circuit_voltage(delta_t)
    i = voc / (2.0 * m.resistance)
    return OperatingPoint(i, voc / 2.0, voc * i / 2.0)
