"""tegkit: small, dependency-free toolkit for modelling thermoelectric generators."""

from .array import TEGArray
from .module import TEGModule
from .units import c_to_k, k_to_c

__all__ = ["TEGModule", "TEGArray", "c_to_k", "k_to_c"]
__version__ = "0.1.0"
