"""Transformada Cuántica de Fourier (QFT) construida compuerta por compuerta.

Convención de Qiskit (little-endian): el qubit 0 es el bit menos significativo.

La QFT estándar sobre L qubits hace

    |x>  ->  (1/sqrt(2^L)) * sum_y exp(2*pi*i*x*y / 2^L) |y>

que se puede escribir como un producto tensorial: el qubit k del resultado
queda en  (|0> + exp(2*pi*i * x * 2^k / 2^L) |1>) / sqrt(2).

Las compuertas SWAP finales solo invierten el orden de los qubits. En los
sumadores las omitimos (do_swaps=False) para ahorrar compuertas: en ese caso
la "fase del qubit k" queda guardada físicamente en el qubit L-1-k, y los
sumadores tienen en cuenta esa reindexación.
"""

from math import pi

from qiskit import QuantumCircuit


def qft(num_qubits: int, do_swaps: bool = True, name: str = "QFT") -> QuantumCircuit:
    """Devuelve el circuito de la QFT sobre ``num_qubits`` qubits."""
    qc = QuantumCircuit(num_qubits, name=name)
    for j in reversed(range(num_qubits)):
        qc.h(j)
        for k in reversed(range(j)):
            # rotación de fase controlada R_{j-k+1} = diag(1, e^{i*pi/2^(j-k)})
            qc.cp(pi / 2 ** (j - k), k, j)
    if do_swaps:
        for i in range(num_qubits // 2):
            qc.swap(i, num_qubits - 1 - i)
    return qc


def iqft(num_qubits: int, do_swaps: bool = True, name: str = "QFT†") -> QuantumCircuit:
    """Devuelve la QFT inversa (la adjunta de :func:`qft`)."""
    inv = qft(num_qubits, do_swaps=do_swaps).inverse()
    inv.name = name
    return inv


def fourier_index(k: int, num_qubits: int, do_swaps: bool) -> int:
    """Qubit físico que guarda la fase del 'qubit lógico k' en el espacio de Fourier."""
    return k if do_swaps else num_qubits - 1 - k
