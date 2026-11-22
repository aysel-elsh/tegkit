"""Presets must reproduce the datasheet numbers they were derived from."""

import pytest

from tegkit import TEGModule, c_to_k, peltier, presets


def test_names_and_lookup():
    assert "TEC1-12706" in presets.names()
    assert isinstance(presets.get("TG12-4"), TEGModule)
    with pytest.raises(KeyError):
        presets.get("nope")


@pytest.mark.parametrize("name", ["TEC1-12706", "TEC-40-36-127", "TEC-30-36-71"])
def test_tec_presets_reproduce_datasheet(name):
    p = presets.info(name)
    m, d = p.module, p.datasheet
    th = c_to_k(d["Th_C"])
    # dTmax is exact by construction
    assert peltier.max_delta_t_at_hot(m, th) == pytest.approx(d["dTmax_K"], rel=1e-6)
    # Qmax (at dT = 0) and module resistance are independent checks. The
    # constant-property inversion is known to overestimate Qmax and
    # underestimate R (it ignores contact resistance and Thomson heat), so
    # pin that documented bias instead of pretending it's exact.
    q_ratio = peltier.max_cooling_power(m, th, th) / d["Qmax_W"]
    r_ratio = m.resistance / d["R_ohm"]
    assert 1.0 <= q_ratio <= 1.25, q_ratio
    assert 0.85 <= r_ratio <= 1.0, r_ratio


def test_tg12_4_reproduces_datasheet():
    p = presets.info("TG12-4")
    m, d = p.module, p.datasheet
    th, tc = c_to_k(d["Th_C"]), c_to_k(d["Tc_C"])
    assert m.max_power(th - tc) == pytest.approx(d["P_opt_W"], rel=0.02)
    # independent check: load for best efficiency, R*sqrt(1+ZT)
    assert m.optimal_efficiency_load(th, tc) == pytest.approx(d["R_load_opt_eta_ohm"], rel=0.05)


def test_teg2_126ldt_reproduces_datasheet():
    p = presets.info("TEG2-126LDT")
    m, d = p.module, p.datasheet
    th, tc = c_to_k(d["Th_C"]), c_to_k(d["Tc_C"])
    dt = th - tc
    assert m.open_circuit_voltage(dt) == pytest.approx(d["Voc_V"])
    assert m.max_power(dt) == pytest.approx(d["P_matched_W"], rel=0.05)
    assert m.heat_in(th, tc, d["R_matched_ohm"]) == pytest.approx(d["Qh_W"], rel=1e-6)
    assert 0 < m.thermal_conductance < 1


def test_from_tec_datasheet_rejects_bad_input():
    with pytest.raises(ValueError):
        TEGModule.from_tec_datasheet(6, 15, 400, 300)
    with pytest.raises(ValueError):
        TEGModule.from_tec_datasheet(0, 15, 60, 300)
