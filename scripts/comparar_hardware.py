"""Compara la calculadora en tres situaciones:

  1. simulación ideal (sin ruido),
  2. simulación con el ruido calibrado de computadores reales de IBM
     (los "fake backends" de Qiskit guardan los errores medidos en esos equipos),
  3. (opcional) un computador cuántico REAL de IBM, usando su cuenta gratuita.

Uso:
    python scripts/comparar_hardware.py            # 1 y 2 (no necesita cuenta)
    python scripts/comparar_hardware.py --real     # además 3 (necesita cuenta de IBM Quantum)

Para --real, una sola vez antes hay que guardar la clave (API key) de IBM Quantum:
    from qiskit_ibm_runtime import QiskitRuntimeService
    QiskitRuntimeService.save_account(token="SU_API_KEY", set_as_default=True)
"""

import argparse
import json
import os
import sys
import warnings

warnings.filterwarnings("ignore")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from qiskit import transpile
from qiskit_aer import AerSimulator

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from qcalc import build_addition, build_multiplication  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
SHOTS = 4000

# Operaciones pequeñas: en hardware real los circuitos grandes ya no funcionan
CASOS = [
    ("3 + 2 (QFT)", lambda: build_addition(3, 2, "qft", n=2)[0], 5),
    ("3 + 2 (Cuccaro)", lambda: build_addition(3, 2, "ripple", n=2)[0], 5),
    ("5 + 3 (QFT)", lambda: build_addition(5, 3, "qft", n=3)[0], 8),
    ("5 + 3 (Cuccaro)", lambda: build_addition(5, 3, "ripple", n=3)[0], 8),
    ("2 × 3", lambda: build_multiplication(2, 3, 2, 2)[0], 6),
    ("3 × 3", lambda: build_multiplication(3, 3, 2, 2)[0], 9),
]


def contar(counts: dict) -> dict:
    return {int(k.replace(" ", ""), 2): v for k, v in counts.items()}


def compuertas_2q(circ) -> int:
    return sum(v for k, v in circ.count_ops().items() if k in ("cx", "cz", "ecr"))


def correr_simulado(backend_fake, nombre):
    sim = AerSimulator.from_backend(backend_fake, seed_simulator=7)
    filas = []
    for etiqueta, hacer, esperado in CASOS:
        t = transpile(hacer(), backend_fake, optimization_level=3, seed_transpiler=7)
        counts = contar(sim.run(t, shots=SHOTS).result().get_counts())
        p = counts.get(esperado, 0) / SHOTS
        mas_frecuente = max(counts, key=counts.get)
        filas.append({"operacion": etiqueta, "esperado": esperado, "p_correcto": p,
                      "mas_frecuente": mas_frecuente, "compuertas_2q": compuertas_2q(t),
                      "profundidad": t.depth()})
        print(f"  {nombre:<14} {etiqueta:<16} P(correcto)={p:.3f}  más frecuente={mas_frecuente:<3}"
              f" compuertas de 2 qubits={compuertas_2q(t)}")
    return filas


def correr_real():
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False)
    print(f"\n  Computador real elegido: {backend.name} ({backend.num_qubits} qubits). Enviando el trabajo...")
    circuitos = [transpile(hacer(), backend, optimization_level=3, seed_transpiler=7) for _, hacer, _ in CASOS]
    job = SamplerV2(mode=backend).run(circuitos, shots=SHOTS)
    print(f"  Trabajo {job.job_id()} en cola. Puede tardar varios minutos (u horas si hay mucha fila)...")
    resultado = job.result()
    filas = []
    for (etiqueta, _, esperado), circ, res in zip(CASOS, circuitos, resultado):
        counts = contar(res.data.res.get_counts())
        p = counts.get(esperado, 0) / SHOTS
        mas_frecuente = max(counts, key=counts.get)
        filas.append({"operacion": etiqueta, "esperado": esperado, "p_correcto": p,
                      "mas_frecuente": mas_frecuente, "compuertas_2q": compuertas_2q(circ),
                      "profundidad": circ.depth()})
        print(f"  {backend.name:<14} {etiqueta:<16} P(correcto)={p:.3f}  más frecuente={mas_frecuente}")
    return backend.name, filas


def graficar(series: dict, archivo: str):
    colores = ["#257de0", "#f47230", "#00b894", "#6a4ce2"]
    etiquetas = [c[0] for c in CASOS]
    k = len(series)
    ancho = 0.8 / k
    fig, ax = plt.subplots(figsize=(9, 4.4))
    for idx, (nombre, filas) in enumerate(series.items()):
        xs = [i + (idx - (k - 1) / 2) * ancho for i in range(len(etiquetas))]
        ys = [f["p_correcto"] for f in filas]
        ax.bar(xs, ys, width=ancho * 0.92, color=colores[idx % len(colores)], label=nombre)
    ax.axhline(0.5, color="#999999", lw=1, ls="--")
    ax.set_xticks(range(len(etiquetas)), etiquetas, fontsize=9)
    ax.set_ylabel("Probabilidad de resultado correcto")
    ax.set_ylim(0, 1.22)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.legend(frameon=False, fontsize=9, loc="upper left", ncol=k)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Ideal vs. ruido de computadores reales de IBM", loc="left")
    fig.tight_layout()
    fig.savefig(archivo, dpi=150)
    print(f"\n  Gráfica guardada en {archivo}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--real", action="store_true", help="también correr en un computador cuántico real de IBM")
    args = p.parse_args()

    from qiskit_ibm_runtime.fake_provider import FakeBrisbane, FakeFez

    series = {}
    print("Simulación ideal:")
    ideal = AerSimulator(seed_simulator=7)
    filas = []
    for etiqueta, hacer, esperado in CASOS:
        counts = contar(ideal.run(transpile(hacer(), ideal), shots=SHOTS).result().get_counts())
        filas.append({"operacion": etiqueta, "esperado": esperado, "p_correcto": counts.get(esperado, 0) / SHOTS})
    print("  " + ", ".join(f"{f['operacion']}: {f['p_correcto']:.2f}" for f in filas))
    series["Ideal"] = filas

    print("\nCon el ruido calibrado de computadores de IBM:")
    series["Ruido de ibm_fez (Heron)"] = correr_simulado(FakeFez(), "ibm_fez")
    series["Ruido de ibm_brisbane (Eagle)"] = correr_simulado(FakeBrisbane(), "ibm_brisbane")

    if args.real:
        nombre, filas = correr_real()
        series[f"REAL: {nombre}"] = filas

    os.makedirs(os.path.join(ROOT, "resultados"), exist_ok=True)
    sufijo = "_real" if args.real else ""
    json.dump(series, open(os.path.join(ROOT, "resultados", f"hardware{sufijo}.json"), "w"),
              indent=2, ensure_ascii=False)
    graficar(series, os.path.join(ROOT, "figuras", f"hardware{sufijo}.png"))


if __name__ == "__main__":
    main()
