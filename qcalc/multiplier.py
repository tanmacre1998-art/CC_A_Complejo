"""Multiplicador cuántico basado en la QFT.

    |a>_n |b>_m |0>_{n+m}  ->  |a>_n |b>_m |a*b>_{n+m}

Idea (multiplicación "desplazar y sumar", como a mano):

    a * b = sum_j b_j * (a << j) = sum_{i,j} a_i b_j 2^(i+j)

El registro de salida se pasa al espacio de Fourier y, para cada par de bits
(a_i, b_j), se suma 2^(i+j) aplicando una fase controlada por AMBOS bits
(compuerta de fase doblemente controlada). Al final se aplica la QFT inversa.
Es el esquema de Ruiz-Pérez y García-Escartín (2017).
"""

from math import pi

from qiskit import QuantumCircuit, QuantumRegister

from .qft import fourier_index, iqft, qft


def qft_multiplier(n: int, m: int | None = None) -> QuantumCircuit:
    """Circuito que multiplica un número de n bits por uno de m bits."""
    m = n if m is None else m
    L = n + m  # el producto de n y m bits cabe en n+m bits
    a = QuantumRegister(n, "a")
    b = QuantumRegister(m, "b")
    out = QuantumRegister(L, "out")
    qc = QuantumCircuit(a, b, out, name=f"Mult({n}x{m})")

    qc.compose(qft(L, do_swaps=False), out, inplace=True)
    qc.barrier()
    for j in range(m):          # bit j de b
        for i in range(n):      # bit i de a
            for k in range(L):  # qubit lógico k de la salida
                if i + j + k < L:
                    angle = 2 * pi * 2 ** (i + j + k) / 2 ** L
                    target = out[fourier_index(k, L, do_swaps=False)]
                    qc.mcp(angle, [a[i], b[j]], target)
        qc.barrier()
    qc.compose(iqft(L, do_swaps=False), out, inplace=True)
    return qc
