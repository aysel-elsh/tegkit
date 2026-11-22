"""Use a module as a Peltier cooler: how cold can it get, and at what current?"""

from tegkit import TEGModule, c_to_k, peltier

# Generic 40 mm module (illustrative numbers, not a specific part)
m = TEGModule(seebeck=0.053, resistance=2.1, thermal_conductance=0.48, name="generic-40mm")

t_hot, t_cold = c_to_k(35), c_to_k(15)

print(f"Max dT, hot side at 35 C:  {peltier.max_delta_t_at_hot(m, t_hot):.1f} K")
print(f"Max cooling at 20 K dT:    {peltier.max_cooling_power(m, t_hot, t_cold):.2f} W "
      f"at {peltier.max_cooling_current(m, t_cold):.2f} A")

i_opt = peltier.optimal_cop_current(m, t_hot, t_cold)
print(f"Best COP at 20 K dT:       {peltier.max_cop(m, t_hot, t_cold):.2f} at {i_opt:.2f} A "
      f"({peltier.cooling_power(m, i_opt, t_hot, t_cold):.2f} W pumped)")
