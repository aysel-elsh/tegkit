"""Size a small TEG array and print its power curve."""

from tegkit import TEGArray, TEGModule, c_to_k

# Matched-load point read off a generic 40 mm module datasheet:
# 2.5 W at 2.1 V with 80 K across the faces; ~0.45 W/K thermal conductance.
module = TEGModule.from_datasheet(
    matched_power=2.5, matched_voltage=2.1, delta_t=80, thermal_conductance=0.45, name="generic-40mm"
)

# Only part of the source temperature difference reaches the module
# once heat-sink and interface resistances are included.
dt = module.module_delta_t(source_delta_t=60, hot_side_resistance=0.3, cold_side_resistance=0.5)
print(f"Module sees {dt:.1f} K of the 60 K available")

array = TEGArray(module, series=4, parallel=2)
r_match = array.matched_load()
print(f"Matched load: {r_match:.2f} ohm -> {array.max_power(dt):.2f} W")

for r in (0.5, 1, 2, 4, 8, 16):
    print(f"  R = {r:>4} ohm : {array.power(dt, r):6.2f} W")

th, tc = c_to_k(25 + dt), c_to_k(25)
print(f"Max efficiency of one module: {module.max_efficiency(th, tc) * 100:.2f} %")
