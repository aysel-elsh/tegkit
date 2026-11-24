"""tegkit: small, dependency-free toolkit for modelling thermoelectric generators."""

from . import peltier, presets
from .array import TEGArray
from .curves import OperatingPoint, iv_curve, max_power_point
from .module import TEGModule
from .sizing import modules_for_power, required_cold_side_resistance, suggest_array
from .units import c_to_k, k_to_c

__all__ = [
    "TEGModule",
    "TEGArray",
    "OperatingPoint",
    "iv_curve",
    "max_power_point",
    "modules_for_power",
    "suggest_array",
    "required_cold_side_resistance",
    "peltier",
    "presets",
    "c_to_k",
    "k_to_c",
]
__version__ = "0.3.1"
