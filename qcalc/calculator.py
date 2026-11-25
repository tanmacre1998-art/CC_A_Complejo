"""Calculadora cuántica: arma el circuito completo, lo simula y lee el resultado.

Ejemplo
-------
>>> from qcalc import QuantumCalculator
>>> calc = QuantumCalculator()
>>> calc.add(5, 3).value
8
>>> calc.multiply(6, 7).value
42
>>> calc.evaluate("12 + 9").value
21
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from qiskit import ClassicalRegister, QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from .adders import cuccaro_adder, draper_adder
from .multiplier import qft_multiplier

BASIS_GATES = ["cx", "rz", "sx", "x"]  # base nativa típica de hardware IBM


# ---------------------------------------------------------------------------
# Métricas de recursos
# ---------------------------------------------------------------------------

def circuit_metrics(core: QuantumCircuit) -> dict:
    """Recursos del circuito aritmético (sin preparación ni medición),
    descompuesto a la base nativa {CX, RZ, SX, X}."""
    t = transpile(core, basis_gates=BASIS_GATES, optimization_level=1, seed_transpiler=7)
    ops = dict(t.count_ops())
    ops.pop("barrier", None)
    return {
        "qubits": t.num_qubits,
        "profundidad": t.depth(lambda instr: instr.operation.name != "barrier"),
        "cx": ops.get("cx", 0),
        "compuertas_1q": sum(v for k, v in ops.items() if k != "cx"),
        "compuertas_total": sum(ops.values()),
    }


# ---------------------------------------------------------------------------
# Construcción de circuitos completos
# ---------------------------------------------------------------------------

def _load(qc: QuantumCircuit, register, value: int) -> None:
    """Codifica un entero clásico en un registro aplicando X donde hay un 1."""
    for i in range(len(register)):
        if (value >> i) & 1:
            qc.x(register[i])


def build_addition(a: int, b: int, method: str = "qft", n: int | None = None):
    """Devuelve (circuito completo, circuito núcleo) para a + b."""
    n = n or max(a.bit_length(), b.bit_length(), 1)
    if method == "qft":
        core = draper_adder(n)
        ra, rb = core.qregs
        qc = QuantumCircuit(*core.qregs, ClassicalRegister(n + 1, "res"))
        _load(qc, ra, a)
        _load(qc, rb, b)
        qc.barrier()
        qc.compose(core, inplace=True)
        qc.barrier()
        qc.measure(rb, qc.cregs[0])
    elif method == "ripple":
        core = cuccaro_adder(n)
        _cin, ra, rb, cout = core.qregs
        qc = QuantumCircuit(*core.qregs, ClassicalRegister(n + 1, "res"))
        _load(qc, ra, a)
        _load(qc, rb, b)
        qc.barrier()
        qc.compose(core, inplace=True)
        qc.barrier()
        qc.measure(list(rb) + [cout[0]], qc.cregs[0])  # bit n = acarreo
    else:
        raise ValueError("method debe ser 'qft' o 'ripple'")
    return qc, core


def build_multiplication(a: int, b: int, n: int | None = None, m: int | None = None):
    """Devuelve (circuito completo, circuito núcleo) para a * b."""
    n = n or max(a.bit_length(), 1)
    m = m or max(b.bit_length(), 1)
    core = qft_multiplier(n, m)
    ra, rb, out = core.qregs
    qc = QuantumCircuit(*core.qregs, ClassicalRegister(n + m, "res"))
    _load(qc, ra, a)
    _load(qc, rb, b)
    qc.barrier()
    qc.compose(core, inplace=True)
    qc.barrier()
    qc.measure(out, qc.cregs[0])
    return qc, core


# ---------------------------------------------------------------------------
# Calculadora
# ---------------------------------------------------------------------------

@dataclass
class Result:
    operation: str
    a: int
    b: int
    value: int                 # resultado más frecuente en las mediciones
    expected: int              # resultado clásico, para comparar
    counts: dict               # {entero: veces medido}
    shots: int
    circuit: QuantumCircuit = field(repr=False)
    metrics: dict = field(default_factory=dict)

    @property
    def correct(self) -> bool:
        return self.value == self.expected

    @property
    def success_probability(self) -> float:
        """Fracción de mediciones que dieron el resultado correcto."""
        return self.counts.get(self.expected, 0) / self.shots

    def __str__(self) -> str:
        sym = "+" if self.operation.startswith("suma") else "×"
        mark = "✔" if self.correct else "✘"
        return (f"{self.a} {sym} {self.b} = {self.value}  {mark}  "
                f"(binario {self.value:b}, P(correcto)={self.success_probability:.3f}, "
                f"{self.metrics.get('qubits')} qubits, profundidad {self.metrics.get('profundidad')})")


class QuantumCalculator:
    """Calculadora que suma y multiplica enteros no negativos con circuitos cuánticos.

    Parámetros
    ----------
    shots : número de repeticiones del circuito en el simulador.
    noise_model : modelo de ruido de qiskit-aer (None = simulación ideal).
    seed : semilla del simulador, para resultados reproducibles.
    """

    MAX_QUBITS = 28  # límite razonable para simular en un computador normal

    def __init__(self, shots: int = 1024, noise_model=None, seed: int | None = 1234):
        self.shots = shots
        self.backend = AerSimulator(noise_model=noise_model, seed_simulator=seed)

    def _run(self, qc: QuantumCircuit) -> dict:
        if qc.num_qubits > self.MAX_QUBITS:
            raise ValueError(f"El circuito necesita {qc.num_qubits} qubits; "
                             f"el máximo configurado es {self.MAX_QUBITS}.")
        compiled = transpile(qc, self.backend, optimization_level=0)
        raw = self.backend.run(compiled, shots=self.shots).result().get_counts()
        return {int(bits.replace(" ", ""), 2): c for bits, c in raw.items()}

    def _finish(self, op, a, b, expected, qc, core) -> Result:
        counts = self._run(qc)
        value = max(counts, key=counts.get)
        return Result(op, a, b, value, expected, counts, self.shots, qc, circuit_metrics(core))

    @staticmethod
    def _check(*values):
        for v in values:
            if not isinstance(v, int) or v < 0:
                raise ValueError("Solo se admiten enteros no negativos.")

    def add(self, a: int, b: int, method: str = "qft") -> Result:
        """Suma a + b. ``method`` = 'qft' (Draper) o 'ripple' (Cuccaro)."""
        self._check(a, b)
        qc, core = build_addition(a, b, method)
        name = "suma (QFT)" if method == "qft" else "suma (ripple-carry)"
        return self._finish(name, a, b, a + b, qc, core)

    def multiply(self, a: int, b: int) -> Result:
        """Multiplica a × b con el multiplicador QFT."""
        self._check(a, b)
        qc, core = build_multiplication(a, b)
        return self._finish("multiplicación (QFT)", a, b, a * b, qc, core)

    def evaluate(self, expression: str, method: str = "qft") -> Result:
        """Evalúa una expresión simple como '7 + 5' o '6 * 3' (también 'x')."""
        match = re.fullmatch(r"\s*(\d+)\s*([+*xX×])\s*(\d+)\s*", expression)
        if not match:
            raise ValueError("Formato esperado: 'a + b' o 'a * b' con enteros no negativos.")
        a, op, b = int(match[1]), match[2], int(match[3])
        return self.add(a, b, method) if op == "+" else self.multiply(a, b)
