"""Ready-made modules built from public manufacturer datasheets.

Each preset keeps the raw datasheet numbers it was derived from, so anyone can
check the conversion. Real parts vary (datasheets typically quote about
+-10%), and the constant-property model is a first-pass approximation.

Known bias for TEC presets: deriving S, R, K from Imax/Vmax/dTmax reproduces
dTmax exactly but gives Qmax about 15-20% high and R about 10% low compared
with the datasheet, because the model ignores contact resistance and Thomson
heat. ``tests/test_presets.py`` pins this range.

>>> from tegkit import presets
>>> m = presets.get("TEC1-12706")
>>> presets.names()
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .module import TEGModule
from .units import c_to_k

__all__ = ["Preset", "get", "info", "names"]


@dataclass(frozen=True)
class Preset:
    name: str
    kind: str  # "TEC" (Peltier cooler) or "TEG" (generator)
    manufacturer: str
    source: str
    conditions: str
    datasheet: dict = field(default_factory=dict)
    module: TEGModule | None = None


def _tec(name, manufacturer, source, i_max, v_max, dt_max, th_c, extra=None):
    data = {"Imax_A": i_max, "Vmax_V": v_max, "dTmax_K": dt_max, "Th_C": th_c, **(extra or {})}
    m = TEGModule.from_tec_datasheet(i_max, v_max, dt_max, c_to_k(th_c), name=name)
    return Preset(name, "TEC", manufacturer, source, f"Th = {th_c} C", data, m)


def _teg_marlow_tg12_4() -> Preset:
    # Datasheet row: Th = 230 C, Tc = 50 C
    voc, i_sc, r_th = 9.45, 1.71, 2.21
    dt = 230 - 50
    m = TEGModule(seebeck=voc / dt, resistance=voc / i_sc, thermal_conductance=1.0 / r_th, name="TG12-4")
    return Preset(
        "TG12-4",
        "TEG",
        "Marlow Industries (Coherent)",
        "https://www.coherent.com/resources/datasheet/materials/single-stage-thermoelectric-generator-tg12-4-ds.pdf",
        "Th = 230 C, Tc = 50 C",
        {"Voc_V": voc, "Isc_A": i_sc, "Rth_K_per_W": r_th, "P_opt_W": 4.05, "R_load_opt_eta_ohm": 6.83,
         "Th_C": 230, "Tc_C": 50},
        m,
    )


def _teg_tecteg_teg2_126ldt() -> Preset:
    # Datasheet: Th = 200 C, Tc = 30 C; matched-load point plus heat flow.
    voc, r_match, q_h = 8.6, 6.0, 52.0
    th, tc = c_to_k(200), c_to_k(30)
    dt = th - tc
    s = voc / dt
    i = voc / (2 * r_match)
    # Qh = S*I*Th + K*dT - I^2*R/2  ->  solve for K
    k = (q_h - s * i * th + 0.5 * i * i * r_match) / dt
    m = TEGModule(seebeck=s, resistance=r_match, thermal_conductance=k, name="TEG2-126LDT")
    return Preset(
        "TEG2-126LDT",
        "TEG",
        "TECTEG MFR",
        "https://thermoelectric-generator.com/wp-content/uploads/2026/05/TEG2-126LDT-Spec.-sheet.1.1.pdf",
        "Th = 200 C, Tc = 30 C",
        {"Voc_V": voc, "R_matched_ohm": r_match, "V_matched_V": 4.3, "I_matched_A": 0.7, "P_matched_W": 3.0,
         "Qh_W": q_h, "Th_C": 200, "Tc_C": 30},
        m,
    )


_PRESETS: dict[str, Preset] = {
    p.name: p
    for p in (
        _tec("TEC1-12706", "HB Corporation (Hebei I.T.)", "https://digsys.upc.edu/csd/DEE/chamber/TEC1-12706.pdf",
             6.4, 14.4, 66, 25, {"Qmax_W": 50, "R_ohm": 1.98}),
        _tec("TEC-40-36-127", "Wakefield Thermal",
             "https://wakefieldthermal.com/content/data_sheets/December2025/ThermoElectricCoolersCatalog.pdf",
             6.0, 15.4, 68, 27, {"Qmax_W": 51.4, "R_ohm": 2.17}),
        _tec("TEC-30-36-71", "Wakefield Thermal",
             "https://wakefieldthermal.com/content/data_sheets/December2025/ThermoElectricCoolersCatalog.pdf",
             6.0, 8.6, 68, 27, {"Qmax_W": 28.7, "R_ohm": 1.24}),
        _teg_marlow_tg12_4(),
        _teg_tecteg_teg2_126ldt(),
    )
}


def names() -> list[str]:
    """All preset names."""
    return sorted(_PRESETS)


def info(name: str) -> Preset:
    """Full preset record: source URL, test conditions and raw datasheet values."""
    try:
        return _PRESETS[name]
    except KeyError:
        raise KeyError(f"unknown preset {name!r}; choose from {names()}") from None


def get(name: str) -> TEGModule:
    """The :class:`TEGModule` for a preset."""
    return info(name).module
