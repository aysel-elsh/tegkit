import math

import pytest

from tegkit import TEGArray, TEGModule, c_to_k, k_to_c


@pytest.fixture
def mod():
    # Roughly a common 40 mm Bi2Te3 module
    return TEGModule(seebeck=0.05, resistance=2.0, thermal_conductance=0.5)


def test_open_circuit_voltage(mod):
    assert mod.open_circuit_voltage(40) == pytest.approx(2.0)


def test_max_power_at_matched_load(mod):
    dt = 40
    p_match = mod.power(dt, mod.resistance)
    assert p_match == pytest.approx(mod.max_power(dt))
    for r in (0.5, 1.0, 3.0, 8.0):
        assert mod.power(dt, r) < p_match


def test_load_voltage_half_voc_at_match(mod):
    assert mod.load_voltage(40, mod.resistance) == pytest.approx(mod.open_circuit_voltage(40) / 2)


def test_from_measurements_roundtrip(mod):
    dt = 30
    voc = mod.open_circuit_voltage(dt)
    isc = mod.current(dt, 0)
    m2 = TEGModule.from_measurements(voc, isc, dt, mod.thermal_conductance)
    assert m2.seebeck == pytest.approx(mod.seebeck)
    assert m2.resistance == pytest.approx(mod.resistance)


def test_from_datasheet_roundtrip(mod):
    dt = 50
    m2 = TEGModule.from_datasheet(
        mod.max_power(dt), mod.load_voltage(dt, mod.resistance), dt, mod.thermal_conductance
    )
    assert m2.seebeck == pytest.approx(mod.seebeck)
    assert m2.resistance == pytest.approx(mod.resistance)


def test_efficiency_below_carnot(mod):
    th, tc = c_to_k(120), c_to_k(25)
    carnot = 1 - tc / th
    eta = mod.efficiency(th, tc, mod.resistance)
    assert 0 < eta < carnot
    assert mod.max_efficiency(th, tc) < carnot


def test_optimal_load_gives_max_efficiency(mod):
    th, tc = c_to_k(120), c_to_k(25)
    r_opt = mod.optimal_efficiency_load(th, tc)
    eta_opt = mod.efficiency(th, tc, r_opt)
    assert eta_opt == pytest.approx(mod.max_efficiency(th, tc), rel=1e-9)
    assert mod.efficiency(th, tc, r_opt * 0.8) < eta_opt
    assert mod.efficiency(th, tc, r_opt * 1.2) < eta_opt


def test_zt_definition(mod):
    th, tc = 400.0, 300.0
    assert mod.zt(th, tc) == pytest.approx(0.05**2 / (2.0 * 0.5) * 350)


def test_module_delta_t_divider(mod):
    # module thermal resistance is 2 K/W; add 1 K/W each side -> half the dT
    assert mod.module_delta_t(80, 1.0, 1.0) == pytest.approx(40)
    assert mod.module_delta_t(80) == pytest.approx(80)


def test_array_scaling(mod):
    arr = TEGArray(mod, series=4, parallel=2)
    dt = 40
    assert arr.count == 8
    assert arr.open_circuit_voltage(dt) == pytest.approx(4 * mod.open_circuit_voltage(dt))
    assert arr.max_power(dt) == pytest.approx(8 * mod.max_power(dt))
    assert arr.matched_load() == pytest.approx(mod.resistance * 2)


@pytest.mark.parametrize("kwargs", [
    dict(seebeck=0, resistance=1, thermal_conductance=1),
    dict(seebeck=1, resistance=-1, thermal_conductance=1),
    dict(seebeck=1, resistance=1, thermal_conductance=0),
])
def test_rejects_bad_parameters(kwargs):
    with pytest.raises(ValueError):
        TEGModule(**kwargs)


def test_bad_array():
    with pytest.raises(ValueError):
        TEGArray(TEGModule(0.05, 2, 0.5), series=0)


def test_units_roundtrip():
    assert k_to_c(c_to_k(37.5)) == pytest.approx(37.5)
    assert math.isclose(c_to_k(0), 273.15)
