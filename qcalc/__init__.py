"""qcalc - Calculadora cuántica (suma y multiplicación) implementada en Qiskit."""

from .adders import cuccaro_adder, draper_adder, phase_add
from .calculator import (QuantumCalculator, Result, build_addition,
                         build_multiplication, circuit_metrics)
from .multiplier import qft_multiplier
from .qft import iqft, qft

__all__ = [
    "QuantumCalculator", "Result", "build_addition", "build_multiplication",
    "circuit_metrics", "cuccaro_adder", "draper_adder", "phase_add",
    "qft_multiplier", "qft", "iqft",
]
__version__ = "1.0.0"
