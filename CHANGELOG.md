# Changelog

## 0.2.0 (2026-11-22)

- **Curves:** `iv_curve` and `max_power_point` for modules and arrays.
- **Peltier mode:** new `tegkit.peltier` module covering cooling power, input power, COP, max cooling current/power, max ΔT (cold- or hot-side referenced), and optimal-COP current.
- **Sizing:** `modules_for_power`, `suggest_array` and `required_cold_side_resistance`.
- **Command line:** `tegkit --seebeck ... --dt ...` (or `python -m tegkit`).
- Requires Python 3.10+.

## 0.1.0 (2026-11-22)

- First release: `TEGModule` (power, efficiency, ZT, contact-resistance divider), `TEGArray`, unit helpers.
