import pytest

from tegkit import TEGArray, TEGModule, c_to_k
from tegkit import peltier
from tegkit.__main__ import main
from tegkit.curves import as_module, iv_curve, max_power_point
from tegkit.sizing import modules_for_power, required_cold_side_resistance, suggest_array


@pytest.fixture
def mod():
    return TEGModule(seebeck=0.05, resistance=2.0, thermal_conductance=0.5)


# ---------------------------------------------------------------- curves
def test_iv_curve_endpoints(mod):
    curve = iv_curve(mod, 40, points=11)
    assert len(curve) == 11
    assert curve[0].current == 0 and curve[0].voltage == pytest.approx(2.0)
    assert curve[-1].voltage == pytest.approx(0, abs=1e-12)
    assert curve[-1].current == pytest.approx(1.0)


def test_mpp_matches_max_power(mod):
    mpp = max_power_point(mod, 40)
    assert mpp.power == pytest.approx(mod.max_power(40))
    assert max(p.power for p in iv_curve(mod, 40, 101)) == pytest.approx(mpp.power)


def test_curves_accept_arrays(mod):
    arr = TEGArray(mod, 3, 2)
    assert max_power_point(arr, 40).power == pytest.approx(6 * mod.max_power(40))


def test_as_module_rejects_other_types():
    with pytest.raises(TypeError):
        as_module("not a module")


def test_iv_curve_needs_two_points(mod):
    with pytest.raises(ValueError):
        iv_curve(mod, 40, points=1)


# ---------------------------------------------------------------- peltier
def test_peltier_max_cooling_current_is_peak(mod):
    th, tc = 300.0, 290.0
    i_max = peltier.max_cooling_current(mod, tc)
    q = peltier.cooling_power(mod, i_max, th, tc)
    assert q == pytest.approx(peltier.max_cooling_power(mod, th, tc))
    assert peltier.cooling_power(mod, 0.9 * i_max, th, tc) < q
    assert peltier.cooling_power(mod, 1.1 * i_max, th, tc) < q


def test_peltier_max_delta_t_gives_zero_cooling(mod):
    tc = 280.0
    th = tc + peltier.max_delta_t(mod, tc)
    q = peltier.cooling_power(mod, peltier.max_cooling_current(mod, tc), th, tc)
    assert q == pytest.approx(0, abs=1e-9)


def test_peltier_max_delta_t_at_hot_consistent(mod):
    th = 300.0
    dt = peltier.max_delta_t_at_hot(mod, th)
    assert 0 < dt < th
    assert peltier.max_delta_t(mod, th - dt) == pytest.approx(dt)


def test_peltier_optimal_cop(mod):
    th, tc = 305.0, 290.0
    i_opt = peltier.optimal_cop_current(mod, th, tc)
    best = peltier.cop(mod, i_opt, th, tc)
    assert best == pytest.approx(peltier.max_cop(mod, th, tc), rel=1e-9)
    assert peltier.cop(mod, 0.8 * i_opt, th, tc) < best
    assert peltier.cop(mod, 1.2 * i_opt, th, tc) < best
    assert best < tc / (th - tc)  # below Carnot


def test_peltier_energy_balance(mod):
    th, tc, i = 310.0, 290.0, 1.5
    qc = peltier.cooling_power(mod, i, th, tc)
    p = peltier.input_power(mod, i, th, tc)
    qh = mod.seebeck * i * th + 0.5 * i**2 * mod.resistance - mod.thermal_conductance * (th - tc)
    assert qh == pytest.approx(qc + p)


def test_peltier_rejects_inverted_temps(mod):
    with pytest.raises(ValueError):
        peltier.max_cop(mod, 290, 300)


# ---------------------------------------------------------------- sizing
def test_modules_for_power(mod):
    p1 = mod.max_power(40)
    assert modules_for_power(mod, 40, p1) == 1
    assert modules_for_power(mod, 40, 2.5 * p1) == 3


def test_suggest_array_meets_targets(mod):
    arr = suggest_array(mod, 40, target_power=5.0, target_voltage=5.0)
    assert arr.open_circuit_voltage(40) / 2 >= 5.0
    assert arr.max_power(40) >= 5.0


def test_required_cold_side_resistance_roundtrip(mod):
    r_c = required_cold_side_resistance(mod, 80, 40, hot_side_resistance=0.5)
    assert mod.module_delta_t(80, 0.5, r_c) == pytest.approx(40)


def test_required_cold_side_resistance_unreachable(mod):
    with pytest.raises(ValueError):
        required_cold_side_resistance(mod, 80, 70, hot_side_resistance=5.0)


# ---------------------------------------------------------------- cli
def test_cli_runs(capsys):
    code = main(["--seebeck", "0.05", "--resistance", "2", "--conductance", "0.5",
                 "--dt", "40", "--series", "2", "--points", "3"])
    out = capsys.readouterr().out
    assert code == 0
    assert "2S1P" in out and "Max power" in out and "I (A)" in out


def test_cli_bad_input(capsys):
    assert main(["--seebeck", "0", "--resistance", "2", "--conductance", "0.5", "--dt", "40"]) == 2
