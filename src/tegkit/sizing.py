"""Quick sizing helpers: how many modules, and how good a heat sink."""

from __future__ import annotations

import math

from .array import TEGArray
from .module import TEGModule

__all__ = ["modules_for_power", "suggest_array", "required_cold_side_resistance"]


def modules_for_power(m: TEGModule, delta_t: float, target_power: float) -> int:
    """Smallest number of identical modules whose matched-load power reaches
    ``target_power`` (W) at module temperature difference ``delta_t`` (K)."""
    if target_power <= 0:
        raise ValueError("target_power must be positive")
    p = m.max_power(delta_t)
    if p <= 0:
        raise ValueError("module produces no power at this delta_t")
    return max(1, math.ceil(target_power / p - 1e-12))


def suggest_array(
    m: TEGModule, delta_t: float, target_power: float, target_voltage: float
) -> TEGArray:
    """Series/parallel layout that meets both a power and a matched-load
    voltage target. Modules in series set the voltage (Voc/2 each at matched
    load); parallel strings make up the remaining power."""
    if target_voltage <= 0:
        raise ValueError("target_voltage must be positive")
    v_each = m.open_circuit_voltage(delta_t) / 2.0
    if v_each <= 0:
        raise ValueError("module produces no voltage at this delta_t")
    series = max(1, math.ceil(target_voltage / v_each - 1e-12))
    total = max(series, modules_for_power(m, delta_t, target_power))
    parallel = math.ceil(total / series)
    return TEGArray(m, series=series, parallel=parallel)


def required_cold_side_resistance(
    m: TEGModule,
    source_delta_t: float,
    target_module_delta_t: float,
    hot_side_resistance: float = 0.0,
) -> float:
    """Largest cold-side thermal resistance (K/W, heat sink plus interface)
    that still leaves ``target_module_delta_t`` across the module.

    Inverts :meth:`TEGModule.module_delta_t`. Raises ``ValueError`` if the
    target can't be reached even with a perfect heat sink.
    """
    if not 0 < target_module_delta_t <= source_delta_t:
        raise ValueError("target_module_delta_t must be in (0, source_delta_t]")
    r_module = 1.0 / m.thermal_conductance
    r_cold = r_module * source_delta_t / target_module_delta_t - r_module - hot_side_resistance
    if r_cold < 0:
        raise ValueError("target is unreachable with this hot-side resistance")
    return r_cold
