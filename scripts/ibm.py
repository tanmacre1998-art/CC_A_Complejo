"""Prepara cualquier suma o multiplicación para correrla en un computador cuántico de IBM.

Uso (desde la carpeta del proyecto):

    py scripts/ibm.py "7 + 6"              # crea qasm/op_7mas6_qft.qasm para pegar en el Composer
    py scripts/ibm.py "7 + 6" --ripple     # lo mismo, con el sumador de Cuccaro
    py scripts/ibm.py "3 * 2"              # multiplicación
    py scripts/ibm.py "7 + 6" --correr     # además lo manda directo a IBM (necesita la API key guardada)

En Colab:  !python scripts/ibm.py "7 + 6"
"""

import argparse
import os
import re
import sys
import warnings

warnings.filterwarnings("ignore")

from qiskit import qasm2, transpile
from qiskit_aer import AerSimulator

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from qcalc import build_addition, build_multiplication  # noqa: E402

RAIZ = os.path.join(os.path.dirname(__file__), "..")


def armar(expr: str, ripple: bool):
    m = re.fullmatch(r"\s*(\d+)\s*([+*xX×])\s*(\d+)\s*", expr)
    if not m:
        sys.exit("Escriban la operación así: \"7 + 6\" o \"3 * 2\" (enteros >= 0).")
    a, op, b = int(m[1]), m[2], int(m[3])
    if op == "+":
        metodo = "ripple" if ripple else "qft"
        qc, _ = build_addition(a, b, metodo)
        esperado, nombre = a + b, f"op_{a}mas{b}_{'cuccaro' if ripple else 'qft'}"
        bases = ["x", "cx", "ccx"] if ripple else ["h", "x", "rz", "cx"]
    else:
        qc, _ = build_multiplication(a, b)
        esperado, nombre = a * b, f"op_{a}por{b}"
        bases = ["h", "x", "rz", "cx"]
    # Se traduce a compuertas sencillas que el Composer de IBM entiende sin problema
    qc = transpile(qc, basis_gates=bases, optimization_level=1, seed_transpiler=1)
    return a, op, b, esperado, nombre, qc


def main():
    p = argparse.ArgumentParser()
    p.add_argument("operacion", help='por ejemplo "7 + 6" o "3 * 2"')
    p.add_argument("--ripple", action="store_true", help="sumar con el sumador de Cuccaro")
    p.add_argument("--correr", action="store_true", help="mandarlo directo a un computador real de IBM")
    p.add_argument("--shots", type=int, default=1024)
    args = p.parse_args()

    a, op, b, esperado, nombre, qc = armar(args.operacion, args.ripple)
    bits = qc.cregs[0].size
    esperado_bin = format(esperado, f"0{bits}b")
    n2 = sum(v for k, v in qc.count_ops().items() if k in ("cx", "ccx"))

    # Verificación rápida en el simulador antes de gastar tiempo de IBM
    sim = AerSimulator()
    counts = sim.run(qc, shots=100).result().get_counts()
    ok = counts.get(esperado_bin, 0) == 100

    ruta = os.path.join(RAIZ, "qasm", f"{nombre}.qasm")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w") as f:
        f.write(qasm2.dumps(qc))

    print(f"\n  Operación: {a} {op} {b} = {esperado}")
    print(f"  En el histograma de IBM busquen la barra: {esperado_bin}")
    print(f"  Qubits: {qc.num_qubits} | compuertas de 2 o 3 qubits: {n2}")
    print(f"  Simulador ideal: {'✔ da ' + str(esperado) if ok else '✘ algo salió mal'}")
    print(f"  Archivo para el Composer: {os.path.relpath(ruta, RAIZ)}")

    if qc.num_qubits > 10 or n2 > 100:
        print("\n  Ojo: es un circuito grande. En un computador real el ruido puede tapar la respuesta.")
        print("  Para que se vea bien en IBM usen números pequeños (sumas de 2-3 bits, multiplicaciones de 2 bits).")

    if not args.correr:
        print("\n  Abran el archivo, copien todo y péguenlo en el editor OpenQASM del Composer.\n")
        return

    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False)
    print(f"\n  Enviando a {backend.name} ({args.shots} mediciones)...")
    circ = transpile(qc, backend, optimization_level=3, seed_transpiler=7)
    job = SamplerV2(mode=backend).run([circ], shots=args.shots)
    print(f"  Trabajo {job.job_id()} en fila (lo pueden ver en Workloads). Esperando resultado...")
    cuentas = job.result()[0].data.res.get_counts()
    total = sum(cuentas.values())
    print(f"\n  Resultado en {backend.name}:")
    for k, v in sorted(cuentas.items(), key=lambda kv: -kv[1])[:6]:
        marca = "  ← correcto" if k == esperado_bin else ""
        print(f"    {k} = {int(k, 2):>4}   {v / total:6.1%}{marca}")
    print(f"\n  P(resultado correcto) = {cuentas.get(esperado_bin, 0) / total:.1%}\n")


if __name__ == "__main__":
    main()
