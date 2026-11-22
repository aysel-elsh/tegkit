# Changelog

## 0.3.0 (2026-11-22)

- **Presets** from public datasheets: TEC1-12706, Wakefield TEC-40-36-127 and TEC-30-36-71, Marlow TG12-4, and TECTEG TEG2-126LDT. Each one stores its source URL and raw values, and is tested against them.
- `TEGModule.from_tec_datasheet(i_max, v_max, delta_t_max, t_hot)`.
- Documented the model's known bias on TEC datasheets (Qmax about 15-20% high, R about 10% low).

## 0.2.0 (2026-11-22)

- **Curves:** `iv_curve` and `max_power_point` for modules and arrays.
- **Peltier mode:** new `tegkit.peltier` module covering cooling power, input power, COP, max cooling current/power, max ΔT (cold- or hot-side referenced), and optimal-COP current.
- **Sizing:** `modules_for_power`, `suggest_array` and `required_cold_side_resistance`.
- **Command line:** `tegkit --seebeck ... --dt ...` (or `python -m tegkit`).
- Requires Python 3.10+.

## 0.1.0 (2026-11-22)

- First release: `TEGModule` (power, efficiency, ZT, contact-resistance divider), `TEGArray`, unit helpers.
