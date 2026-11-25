"""Pruebas exhaustivas: se comprueban TODAS las combinaciones de entradas
pequeñas usando el vector de estado exacto (sin muestreo)."""

import itertools

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Operator, Statevector

from qcalc import QuantumCalculator, cuccaro_adder, draper_adder, qft, qft_multiplier


def basis_index(values_and_widths):
    """Índice del estado base |..., v2, v1, v0> (registro 0 en los bits bajos)."""
    idx, shift = 0, 0
    for value, width in values_and_widths:
        idx |= value << shift
        shift += width
    return idx


def evolve(circuit: QuantumCircuit, index: int) -> int:
    """Aplica el circuito a un estado base y devuelve el estado base de salida
    (comprobando que la salida es un estado base con probabilidad 1)."""
    sv = Statevector.from_int(index, 2 ** circuit.num_qubits).evolve(circuit)
    probs = sv.probabilities()
    out = int(np.argmax(probs))
    assert probs[out] == pytest.approx(1.0, abs=1e-9)
    return out


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_qft_igual_a_la_de_qiskit(n):
    assert Operator(qft(n)).equiv(Operator(QFTGate(n)))


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_draper_exhaustivo(n):
    qc = draper_adder(n)
    for a, b in itertools.product(range(2 ** n), repeat=2):
        out = evolve(qc, basis_index([(a, n), (b, n + 1)]))
        assert out & (2 ** n - 1) == a, "a debe quedar intacto"
        assert out >> n == a + b


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_cuccaro_exhaustivo(n):
    qc = cuccaro_adder(n)
    for a, b in itertools.product(range(2 ** n), repeat=2):
        out = evolve(qc, basis_index([(0, 1), (a, n), (b, n), (0, 1)]))
        cin = out & 1
        a_out = (out >> 1) & (2 ** n - 1)
        s = (out >> (n + 1)) & (2 ** n - 1)
        carry = out >> (2 * n + 1)
        assert cin == 0 and a_out == a
        assert s + (carry << n) == a + b


@pytest.mark.parametrize("n,m", [(1, 1), (2, 2), (3, 2), (2, 3), (3, 3)])
def test_multiplicador_exhaustivo(n, m):
    qc = qft_multiplier(n, m)
    for a in range(2 ** n):
        for b in range(2 ** m):
            out = evolve(qc, basis_index([(a, n), (b, m), (0, n + m)]))
            assert out & (2 ** n - 1) == a
            assert (out >> n) & (2 ** m - 1) == b
            assert out >> (n + m) == a * b


def test_calculadora_de_punta_a_punta():
    calc = QuantumCalculator(shots=64)
    assert calc.add(13, 29).value == 42
    assert calc.add(13, 29, method="ripple").value == 42
    assert calc.multiply(11, 13).value == 143
    assert calc.evaluate("7 x 6").value == 42
    assert calc.evaluate("0 + 0").value == 0


def test_entradas_invalidas():
    calc = QuantumCalculator()
    with pytest.raises(ValueError):
        calc.add(-1, 2)
    with pytest.raises(ValueError):
        calc.evaluate("2 - 1")
