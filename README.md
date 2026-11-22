# tegkit

Small, dependency-free Python toolkit for modelling **thermoelectric generators (TEGs)**: the little ceramic modules that turn a temperature difference into electricity.

Use it to answer the usual first questions fast:
- How much power will this module give me at this ΔT?
- What load should I use: max power or max efficiency?
- How much ΔT do I actually lose to my heat sinks?
- What do 4 in series × 2 in parallel give me?

```bash
pip install tegkit
```

## Quick start

```python
from tegkit import TEGModule, TEGArray, c_to_k

# From the matched-load point on a datasheet
m = TEGModule.from_datasheet(matched_power=2.5, matched_voltage=2.1,
                             delta_t=80, thermal_conductance=0.45)

dt = m.module_delta_t(source_delta_t=60, hot_side_resistance=0.3, cold_side_resistance=0.5)
arr = TEGArray(m, series=4, parallel=2)

print(arr.max_power(dt), "W at", arr.matched_load(), "ohm")
print(m.max_efficiency(c_to_k(85), c_to_k(25)))
```

Or straight from a bench test: `TEGModule.from_measurements(voc, isc, delta_t, thermal_conductance)`.

## What's inside

| Function | What it gives you |
|---|---|
| `open_circuit_voltage`, `current`, `load_voltage`, `power` | Electrical behaviour into a resistive load |
| `max_power` | Matched-load power, `Voc² / 4R` |
| `heat_in`, `efficiency` | Hot-side heat flow (Fourier + Peltier + Joule) and P/Qh |
| `figure_of_merit`, `zt`, `max_efficiency`, `optimal_efficiency_load` | Z, ZT and the ideal efficiency limit |
| `module_delta_t` | ΔT left after heat-sink / interface thermal resistances |
| `TEGArray` | Series/parallel arrays of identical modules |
| `iv_curve`, `max_power_point` | I-V / power sweep and the maximum power point |
| `modules_for_power`, `suggest_array` | How many modules, and in what series/parallel layout |
| `required_cold_side_resistance` | How good your heat sink must be to keep a target ΔT |
| `tegkit.peltier` | Cooler mode: cooling power, COP, max ΔT, optimal current |

## Real-module presets

```python
from tegkit import presets
presets.names()        # ['TEC-30-36-71', 'TEC-40-36-127', 'TEC1-12706', 'TEG2-126LDT', 'TG12-4']
m = presets.get("TG12-4")
presets.info("TG12-4").source   # datasheet URL + the raw numbers used
```

Every preset is derived from a public datasheet, and the tests check it reproduces that datasheet's own numbers. Or build your own from any Peltier datasheet with `TEGModule.from_tec_datasheet(i_max, v_max, delta_t_max, t_hot)`.

**Adding a preset is a great first PR**: cite the datasheet and add a test.

## Command line

```bash
tegkit --seebeck 0.05 --resistance 2 --conductance 0.5 --dt 40 --series 4 --parallel 2 --points 5
```

prints open-circuit voltage, matched load, max power and an I-V table.

## Model and limits

Constant-property, lumped model (S, R, K don't change with temperature). It's the standard first-pass model from the thermoelectrics literature, good for sizing and teaching and not a replacement for FEM or measured curves. Contributions that add temperature-dependent properties are very welcome.

## Run the tests

```bash
pip install -e '.[dev]'
pytest
```

## Contributing

New here? Look for issues labelled **good first issue**, and read [CONTRIBUTING.md](CONTRIBUTING.md). Physics corrections, real datasheet presets and examples are all great first PRs.

## License

MIT. See [LICENSE](LICENSE).

Made by [Aysel Elshenawy](https://github.com/aysel-elsh), EE student at FAU.
