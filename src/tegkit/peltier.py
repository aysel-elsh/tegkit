"""Running a module the other way round: as a Peltier cooler (TEC).

Same constant-property model as :class:`tegkit.TEGModule`. All temperatures in
kelvin; ``t_cold`` is the side being cooled.
"""

from __future__ import annotations

import math

from .module import TEGModule

__all__ = [
    "cooling_power",
    "input_power",
    "cop",
    "max_cooling_current",
    "max_cooling_power",
    "max_delta_t",
    "max_delta_t_at_hot",
    "optimal_cop_current",
    "max_cop",
]


def cooling_power(m: TEGModule, current: float, t_hot: float, t_cold: float) -> float:
    """Heat pumped from the cold side (W): ``S*I*Tc - I**2*R/2 - K*dT``."""
    dt = t_hot - t_cold
    return m.seebeck * current * t_cold - 0.5 * current**2 * m.resistance - m.thermal_conductance * dt


def input_power(m: TEGModule, current: float, t_hot: float, t_cold: float) -> float:
    """Electrical power the module draws (W): ``S*I*dT + I**2*R``."""
    return m.seebeck * current * (t_hot - t_cold) + current**2 * m.resistance


def cop(m: TEGModule, current: float, t_hot: float, t_cold: float) -> float:
    """Coefficient of performance Qc / P_in (0 if nothing is drawn)."""
    p = input_power(m, current, t_hot, t_cold)
    return cooling_power(m, current, t_hot, t_cold) / p if p > 0 else 0.0


def max_cooling_current(m: TEGModule, t_cold: float) -> float:
    """Current that maximises cooling power (A): ``S*Tc/R``."""
    return m.seebeck * t_cold / m.resistance


def max_cooling_power(m: TEGModule, t_hot: float, t_cold: float) -> float:
    """Largest heat the module can pump at this dT (W)."""
    return cooling_power(m, max_cooling_current(m, t_cold), t_hot, t_cold)


def max_delta_t(m: TEGModule, t_cold: float) -> float:
    """Largest dT reachable with no heat load (K): ``Z*Tc**2/2``."""
    return 0.5 * m.figure_of_merit() * t_cold**2


def max_delta_t_at_hot(m: TEGModule, t_hot: float) -> float:
    """Largest dT with no heat load when the *hot* side is held at ``t_hot``
    (how datasheets quote dTmax). Solves ``Th - Tc = Z*Tc**2/2`` for Tc."""
    z = m.figure_of_merit()
    t_cold = (math.sqrt(1.0 + 2.0 * z * t_hot) - 1.0) / z
    return t_hot - t_cold


def _root(m: TEGModule, t_hot: float, t_cold: float) -> float:
    return math.sqrt(1.0 + m.zt(t_hot, t_cold))


def optimal_cop_current(m: TEGModule, t_hot: float, t_cold: float) -> float:
    """Current that maximises COP (A): ``S*dT / (R*(sqrt(1+ZTm) - 1))``."""
    dt = t_hot - t_cold
    if dt <= 0:
        raise ValueError("t_hot must be greater than t_cold")
    return m.seebeck * dt / (m.resistance * (_root(m, t_hot, t_cold) - 1.0))


def max_cop(m: TEGModule, t_hot: float, t_cold: float) -> float:
    """Ideal maximum COP: ``(Tc/dT) * (sqrt(1+ZTm) - Th/Tc) / (sqrt(1+ZTm) + 1)``."""
    dt = t_hot - t_cold
    if dt <= 0:
        raise ValueError("t_hot must be greater than t_cold")
    r = _root(m, t_hot, t_cold)
    return (t_cold / dt) * (r - t_hot / t_cold) / (r + 1.0)
