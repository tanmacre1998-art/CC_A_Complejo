"""Sumadores cuánticos.

Se implementan dos sumadores de dos números de n bits, ambos reversibles:

1. ``draper_adder``  - Sumador de Draper (2000), basado en la QFT.
       |a>_n |b>_{n+1}  ->  |a>_n |a+b>_{n+1}
   El registro b tiene un qubit extra (inicialmente 0) para el acarreo final.
   Idea: en el espacio de Fourier, sumar un número equivale a aplicar fases.

2. ``cuccaro_adder`` - Sumador de acarreo en cascada (ripple-carry) de
   Cuccaro, Draper, Kutin y Moulton (2004).
       |0>_cin |a>_n |b>_n |0>_cout  ->  |0>_cin |a>_n |a+b mod 2^n>_n |carry>_cout
   Usa solo compuertas clásicas reversibles (CNOT y Toffoli).
"""

from math import pi

from qiskit import QuantumCircuit, QuantumRegister

from .qft import fourier_index, iqft, qft


# ---------------------------------------------------------------------------
# 1. Sumador de Draper (QFT)
# ---------------------------------------------------------------------------

def phase_add(qc: QuantumCircuit, a, b_fourier, do_swaps: bool = False) -> None:
    """Suma el registro ``a`` al registro ``b_fourier``, que ya está en el
    espacio de Fourier, usando rotaciones de fase controladas.

    El qubit lógico k de b debe acumular la fase  2*pi * a * 2^k / 2^L.
    Escribiendo a = sum_i a_i 2^i, cada bit a_i aporta  2*pi * 2^(i+k) / 2^L,
    que es una compuerta CP controlada por a_i. Si i+k >= L la fase es un
    múltiplo de 2*pi y la compuerta se omite.
    """
    L = len(b_fourier)
    for k in range(L):
        target = b_fourier[fourier_index(k, L, do_swaps)]
        for i in range(len(a)):
            if i + k < L:
                qc.cp(2 * pi * 2 ** (i + k) / 2 ** L, a[i], target)


def draper_adder(n: int) -> QuantumCircuit:
    """Circuito |a>_n |b>_{n+1} -> |a>_n |a+b>_{n+1} con la QFT."""
    a = QuantumRegister(n, "a")
    b = QuantumRegister(n + 1, "b")
    qc = QuantumCircuit(a, b, name=f"Draper({n})")
    qc.compose(qft(n + 1, do_swaps=False), b, inplace=True)
    qc.barrier()
    phase_add(qc, a, b, do_swaps=False)
    qc.barrier()
    qc.compose(iqft(n + 1, do_swaps=False), b, inplace=True)
    return qc


# ---------------------------------------------------------------------------
# 2. Sumador de Cuccaro (ripple-carry)
# ---------------------------------------------------------------------------

def _maj(qc: QuantumCircuit, c, b, a) -> None:
    """Bloque MAJ: deja en ``a`` el acarreo mayoritario de (a, b, c)."""
    qc.cx(a, b)
    qc.cx(a, c)
    qc.ccx(c, b, a)


def _uma(qc: QuantumCircuit, c, b, a) -> None:
    """Bloque UMA (UnMajority and Add): deshace MAJ y deja la suma en ``b``."""
    qc.ccx(c, b, a)
    qc.cx(a, c)
    qc.cx(c, b)


def cuccaro_adder(n: int) -> QuantumCircuit:
    """Circuito |0>|a>|b>|0> -> |0>|a>|a+b mod 2^n>|carry> (Cuccaro et al.)."""
    cin = QuantumRegister(1, "cin")
    a = QuantumRegister(n, "a")
    b = QuantumRegister(n, "b")
    cout = QuantumRegister(1, "cout")
    qc = QuantumCircuit(cin, a, b, cout, name=f"Cuccaro({n})")

    # Ida: propagar el acarreo con bloques MAJ
    _maj(qc, cin[0], b[0], a[0])
    for i in range(1, n):
        _maj(qc, a[i - 1], b[i], a[i])

    # El último acarreo se copia al qubit de salida
    qc.cx(a[n - 1], cout[0])

    # Vuelta: deshacer los acarreos y escribir la suma con bloques UMA
    for i in reversed(range(1, n)):
        _uma(qc, a[i - 1], b[i], a[i])
    _uma(qc, cin[0], b[0], a[0])
    return qc
