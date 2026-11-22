"""Lumped-parameter model of a single thermoelectric generator (TEG) module.

The model is the standard textbook one (see e.g. Rowe, *CRC Handbook of
Thermoelectrics*): a module is described by an effective Seebeck coefficient
``S`` (V/K), an internal electrical resistance ``R`` (ohm) and a thermal
conductance ``K`` (W/K). Temperature dependence of S, R and K is ignored.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = ["TEGModule"]


def _check_positive(name: str, value: float) -> None:
    if not value > 0:
        raise ValueError(f"{name} must be positive, got {value!r}")


@dataclass(frozen=True)
class TEGModule:
    """A single thermoelectric module.

    Parameters
    ----------
    seebeck:
        Effective module Seebeck coefficient in V/K (all couples combined).
    resistance:
        Internal electrical resistance in ohm.
    thermal_conductance:
        Module thermal conductance in W/K (hot face to cold face).
    name:
        Optional label, e.g. the part number.
    """

    seebeck: float
    resistance: float
    thermal_conductance: float
    name: str = ""

    def __post_init__(self) -> None:
        _check_positive("seebeck", self.seebeck)
        _check_positive("resistance", self.resistance)
        _check_positive("thermal_conductance", self.thermal_conductance)

    # ------------------------------------------------------------------ #
    # Constructors
    # ------------------------------------------------------------------ #
    @classmethod
    def from_measurements(
        cls,
        open_circuit_voltage: float,
        short_circuit_current: float,
        delta_t: float,
        thermal_conductance: float,
        name: str = "",
    ) -> "TEGModule":
        """Build a module from a bench measurement at a known face-to-face
        temperature difference ``delta_t`` (K).

        ``S = Voc / dT`` and ``R = Voc / Isc``.
        """
        _check_positive("open_circuit_voltage", open_circuit_voltage)
        _check_positive("short_circuit_current", short_circuit_current)
        _check_positive("delta_t", delta_t)
        return cls(
            seebeck=open_circuit_voltage / delta_t,
            resistance=open_circuit_voltage / short_circuit_current,
            thermal_conductance=thermal_conductance,
            name=name,
        )

    @classmethod
    def from_datasheet(
        cls,
        matched_power: float,
        matched_voltage: float,
        delta_t: float,
        thermal_conductance: float,
        name: str = "",
    ) -> "TEGModule":
        """Build a module from the matched-load point most datasheets list.

        At matched load the load voltage is half the open-circuit voltage and
        ``P = Voc**2 / (4 R)``.
        """
        _check_positive("matched_power", matched_power)
        _check_positive("matched_voltage", matched_voltage)
        _check_positive("delta_t", delta_t)
        voc = 2.0 * matched_voltage
        return cls(
            seebeck=voc / delta_t,
            resistance=voc**2 / (4.0 * matched_power),
            thermal_conductance=thermal_conductance,
            name=name,
        )

    @classmethod
    def from_tec_datasheet(
        cls,
        i_max: float,
        v_max: float,
        delta_t_max: float,
        t_hot: float,
        name: str = "",
    ) -> "TEGModule":
        """Build a module from the four numbers every Peltier (TEC) datasheet
        lists: Imax (A), Vmax (V) and dTmax (K) at hot-side temperature
        ``t_hot`` (kelvin).

        Uses the standard inversion of the constant-property model::

            S = Vmax / Th
            R = (Vmax / Imax) * (Th - dTmax) / Th
            K = Imax * Vmax * (Th - dTmax) / (2 * Th * dTmax)
        """
        for label, value in (("i_max", i_max), ("v_max", v_max), ("delta_t_max", delta_t_max), ("t_hot", t_hot)):
            _check_positive(label, value)
        if delta_t_max >= t_hot:
            raise ValueError("delta_t_max must be smaller than t_hot")
        t_cold = t_hot - delta_t_max
        return cls(
            seebeck=v_max / t_hot,
            resistance=(v_max / i_max) * t_cold / t_hot,
            thermal_conductance=i_max * v_max * t_cold / (2.0 * t_hot * delta_t_max),
            name=name,
        )

    # ------------------------------------------------------------------ #
    # Electrical behaviour
    # ------------------------------------------------------------------ #
    def open_circuit_voltage(self, delta_t: float) -> float:
        """Open-circuit voltage (V) for a face-to-face difference ``delta_t`` (K)."""
        return self.seebeck * delta_t

    def current(self, delta_t: float, load_resistance: float) -> float:
        """Current (A) into a resistive load (ohm)."""
        if load_resistance < 0:
            raise ValueError("load_resistance must be >= 0")
        return self.open_circuit_voltage(delta_t) / (self.resistance + load_resistance)

    def load_voltage(self, delta_t: float, load_resistance: float) -> float:
        """Voltage (V) across a resistive load."""
        return self.current(delta_t, load_resistance) * load_resistance

    def power(self, delta_t: float, load_resistance: float) -> float:
        """Power (W) delivered to a resistive load."""
        i = self.current(delta_t, load_resistance)
        return i * i * load_resistance

    def max_power(self, delta_t: float) -> float:
        """Maximum power (W), reached when the load equals the internal resistance."""
        voc = self.open_circuit_voltage(delta_t)
        return voc * voc / (4.0 * self.resistance)

    # ------------------------------------------------------------------ #
    # Thermal behaviour and efficiency
    # ------------------------------------------------------------------ #
    def heat_in(self, t_hot: float, t_cold: float, load_resistance: float) -> float:
        """Heat (W) absorbed at the hot face, including Peltier and Joule terms.

        ``Qh = S*I*Th + K*dT - I**2*R/2`` with temperatures in kelvin.
        """
        _check_positive("t_hot", t_hot)
        dt = t_hot - t_cold
        i = self.current(dt, load_resistance)
        return self.seebeck * i * t_hot + self.thermal_conductance * dt - 0.5 * i * i * self.resistance

    def efficiency(self, t_hot: float, t_cold: float, load_resistance: float) -> float:
        """Conversion efficiency P / Qh (0..1). Temperatures in kelvin."""
        dt = t_hot - t_cold
        q = self.heat_in(t_hot, t_cold, load_resistance)
        return self.power(dt, load_resistance) / q if q > 0 else 0.0

    def figure_of_merit(self) -> float:
        """Device figure of merit Z = S**2 / (R*K) in 1/K."""
        return self.seebeck**2 / (self.resistance * self.thermal_conductance)

    def zt(self, t_hot: float, t_cold: float) -> float:
        """Dimensionless ZT evaluated at the mean temperature (kelvin)."""
        return self.figure_of_merit() * (t_hot + t_cold) / 2.0

    def max_efficiency(self, t_hot: float, t_cold: float) -> float:
        """Ideal maximum efficiency for this module's ZT (kelvin inputs).

        ``eta = (dT/Th) * (sqrt(1+ZT) - 1) / (sqrt(1+ZT) + Tc/Th)``
        """
        _check_positive("t_hot", t_hot)
        _check_positive("t_cold", t_cold)
        if t_hot <= t_cold:
            return 0.0
        m = math.sqrt(1.0 + self.zt(t_hot, t_cold))
        return (t_hot - t_cold) / t_hot * (m - 1.0) / (m + t_cold / t_hot)

    def optimal_efficiency_load(self, t_hot: float, t_cold: float) -> float:
        """Load resistance (ohm) that maximises efficiency: R * sqrt(1+ZT)."""
        return self.resistance * math.sqrt(1.0 + self.zt(t_hot, t_cold))

    # ------------------------------------------------------------------ #
    # Thermal contact
    # ------------------------------------------------------------------ #
    def module_delta_t(
        self,
        source_delta_t: float,
        hot_side_resistance: float = 0.0,
        cold_side_resistance: float = 0.0,
    ) -> float:
        """Temperature difference (K) that actually appears across the module.

        Treats the hot-side and cold-side thermal resistances (K/W, e.g. heat
        exchanger plus interface material) as a series divider with the
        module's own thermal resistance ``1/K``. Peltier and Joule effects are
        neglected, so this is the open-circuit estimate.
        """
        if hot_side_resistance < 0 or cold_side_resistance < 0:
            raise ValueError("thermal resistances must be >= 0")
        r_module = 1.0 / self.thermal_conductance
        return source_delta_t * r_module / (r_module + hot_side_resistance + cold_side_resistance)
