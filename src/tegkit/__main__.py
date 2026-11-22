"""Command line: ``python -m tegkit --seebeck 0.05 --resistance 2 --conductance 0.5 --dt 40``."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .array import TEGArray
from .curves import iv_curve, max_power_point
from .module import TEGModule


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tegkit", description="Thermoelectric generator calculator")
    p.add_argument("--seebeck", type=float, required=True, help="module Seebeck coefficient, V/K")
    p.add_argument("--resistance", type=float, required=True, help="internal resistance, ohm")
    p.add_argument("--conductance", type=float, required=True, help="thermal conductance, W/K")
    p.add_argument("--dt", type=float, required=True, help="temperature difference across the module, K")
    p.add_argument("--series", type=int, default=1, help="modules in series (default 1)")
    p.add_argument("--parallel", type=int, default=1, help="parallel strings (default 1)")
    p.add_argument("--points", type=int, default=0, help="also print an I-V table with this many points")
    p.add_argument("--version", action="version", version=f"tegkit {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        module = TEGModule(args.seebeck, args.resistance, args.conductance)
        source = TEGArray(module, args.series, args.parallel)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    mpp = max_power_point(source, args.dt)
    print(f"Array:           {args.series}S{args.parallel}P ({source.count} modules)")
    print(f"Open-circuit V:  {source.open_circuit_voltage(args.dt):.3f} V")
    print(f"Matched load:    {source.matched_load():.3f} ohm")
    print(f"Max power:       {mpp.power:.3f} W at {mpp.voltage:.3f} V, {mpp.current:.3f} A")

    if args.points:
        print()
        print(f"{'I (A)':>10} {'V (V)':>10} {'P (W)':>10}")
        for pt in iv_curve(source, args.dt, args.points):
            print(f"{pt.current:10.3f} {pt.voltage:10.3f} {pt.power:10.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
