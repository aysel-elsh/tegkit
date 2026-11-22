"""Tiny unit helpers."""

ZERO_C_IN_K = 273.15


def c_to_k(celsius: float) -> float:
    """Degrees Celsius to kelvin."""
    return celsius + ZERO_C_IN_K


def k_to_c(kelvin: float) -> float:
    """Kelvin to degrees Celsius."""
    return kelvin - ZERO_C_IN_K
