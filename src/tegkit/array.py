"""Series/parallel arrays of identical TEG modules."""

from __future__ import annotations

from dataclasses import dataclass

from .module import TEGModule

__all__ = ["TEGArray"]


@dataclass(frozen=True)
class TEGArray:
    """``series`` modules per string, ``parallel`` strings, all identical and
    all seeing the same temperature difference. Both counts must be positive integers.
    """

    module: TEGModule
    series: int = 1
    parallel: int = 1

    def __post_init__(self) -> None:
        for name, count in (("series", self.series), ("parallel", self.parallel)):
            if isinstance(count, bool) or not isinstance(count, int) or count < 1:
                raise ValueError(f"{name} must be an integer >= 1")

    @property
    def count(self) -> int:
        return self.series * self.parallel

    def as_module(self) -> TEGModule:
        """Equivalent single module (Thevenin source plus total conductance)."""
        m = self.module
        return TEGModule(
            seebeck=m.seebeck * self.series,
            resistance=m.resistance * self.series / self.parallel,
            thermal_conductance=m.thermal_conductance * self.count,
            name=f"{self.series}S{self.parallel}P {m.name}".strip(),
        )

    def open_circuit_voltage(self, delta_t: float) -> float:
        return self.as_module().open_circuit_voltage(delta_t)

    def power(self, delta_t: float, load_resistance: float) -> float:
        return self.as_module().power(delta_t, load_resistance)

    def max_power(self, delta_t: float) -> float:
        return self.as_module().max_power(delta_t)

    def matched_load(self) -> float:
        """Load resistance (ohm) for maximum power."""
        return self.as_module().resistance
