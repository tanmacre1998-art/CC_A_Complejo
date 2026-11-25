"""Genera todas las figuras y tablas del análisis en ./figuras y ./resultados.

Uso:  python scripts/analisis.py
"""

import json
import os
import random
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from qiskit import ClassicalRegister, QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from qcalc import (QuantumCalculator, build_addition, circuit_metrics,  # noqa: E402
                   cuccaro_adder, draper_adder, qft, qft_multiplier)

ROOT = os.path.join(os.path.dirname(__file__), "..")
FIG = os.path.join(ROOT, "figuras")
RES = os.path.join(ROOT, "resultados")
os.makedirs(FIG, exist_ok=True)
os.makedirs(RES, exist_ok=True)

# Paleta categórica validada (azul, naranja, aguamarina) + tintas de texto
C = {"Draper (QFT)": "#257de0", "Cuccaro (ripple-carry)": "#f47230", "Multiplicador QFT": "#00b894"}
MK = {"Draper (QFT)": "o", "Cuccaro (ripple-carry)": "s", "Multiplicador QFT": "^"}
TEXT, TEXT2, GRID = "#191919", "#666666", "#e6e6e6"
plt.rcParams.update({
    "font.size": 11, "axes.edgecolor": GRID, "axes.labelcolor": TEXT, "text.color": TEXT,
    "xtick.color": TEXT2, "ytick.color": TEXT2, "axes.grid": True, "grid.color": GRID,
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150,
    "lines.linewidth": 2, "lines.markersize": 7, "legend.frameon": False,
})


def label_end(ax, x, y, text, color):
    ax.annotate(text, (x, y), xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=10, color=TEXT)


# ---------------------------------------------------------------------------
# 1. Diagramas de circuitos
# ---------------------------------------------------------------------------
def diagramas():
    style = {"backgroundcolor": "#ffffff"}
    qft(4).draw("mpl", style=style).savefig(f"{FIG}/circuito_qft4.png", bbox_inches="tight")
    draper_adder(3).draw("mpl", style=style, fold=-1).savefig(f"{FIG}/circuito_draper3.png", bbox_inches="tight")
    cuccaro_adder(3).draw("mpl", style=style, fold=-1).savefig(f"{FIG}/circuito_cuccaro3.png", bbox_inches="tight")
    qft_multiplier(2, 2).draw("mpl", style=style, fold=-1).savefig(f"{FIG}/circuito_mult2x2.png", bbox_inches="tight")
    qc, _ = build_addition(5, 3, "qft", n=3)
    qc.draw("mpl", style=style, fold=-1).savefig(f"{FIG}/circuito_completo_5mas3.png", bbox_inches="tight")
    plt.close("all")


# ---------------------------------------------------------------------------
# 2. Recursos vs tamaño
# ---------------------------------------------------------------------------
def recursos():
    data = {"Draper (QFT)": [], "Cuccaro (ripple-carry)": [], "Multiplicador QFT": []}
    for n in range(1, 11):
        data["Draper (QFT)"].append({"n": n, **circuit_metrics(draper_adder(n))})
        data["Cuccaro (ripple-carry)"].append({"n": n, **circuit_metrics(cuccaro_adder(n))})
    for n in range(1, 7):
        data["Multiplicador QFT"].append({"n": n, **circuit_metrics(qft_multiplier(n, n))})
    json.dump(data, open(f"{RES}/recursos.json", "w"), indent=2, ensure_ascii=False)

    for metric, ylabel, fname in [("cx", "Compuertas CNOT", "recursos_cx.png"),
                                  ("profundidad", "Profundidad del circuito", "recursos_profundidad.png"),
                                  ("qubits", "Qubits", "recursos_qubits.png")]:
        fig, ax = plt.subplots(figsize=(7, 4.2))
        for name, rows in data.items():
            xs = [r["n"] for r in rows]
            ys = [r[metric] for r in rows]
            ax.plot(xs, ys, marker=MK[name], color=C[name], label=name,
                    markeredgecolor="white", markeredgewidth=1.5)
            label_end(ax, xs[-1], ys[-1], f"{ys[-1]}", C[name])
        ax.set_xlabel("Bits por operando (n)")
        ax.set_ylabel(ylabel)
        ax.set_xticks(range(1, 11))
        if metric != "qubits":
            ax.set_yscale("log")
        ax.legend(loc="upper left")
        ax.set_title(f"{ylabel} según el tamaño de los números", loc="left", fontsize=12)
        fig.tight_layout()
        fig.savefig(f"{FIG}/{fname}")
        plt.close(fig)
    return data


# ---------------------------------------------------------------------------
# 3. Ruido
# ---------------------------------------------------------------------------
def noise_model(p2):
    nm = NoiseModel()
    if p2 == 0:
        return None
    nm.add_all_qubit_quantum_error(depolarizing_error(p2 / 10, 1), ["sx", "x", "rz"])
    nm.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ["cx"])
    return nm


def success(qc, expected, sim, shots):
    t = transpile(qc, basis_gates=["cx", "rz", "sx", "x"], optimization_level=1, seed_transpiler=7)
    counts = sim.run(t, shots=shots).result().get_counts()
    return sum(c for k, c in counts.items() if int(k.replace(" ", ""), 2) == expected) / shots


def ruido():
    rng = random.Random(42)
    shots, trials = 2000, 6
    p_list = [0, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]
    out = {"p2": p_list, "series": {}}
    cases = {
        "Draper (QFT)": lambda a, b: (build_addition(a, b, "qft", n=4)[0], a + b, 4),
        "Cuccaro (ripple-carry)": lambda a, b: (build_addition(a, b, "ripple", n=4)[0], a + b, 4),
    }
    from qcalc import build_multiplication
    cases["Multiplicador QFT"] = lambda a, b: (build_multiplication(a % 8, b % 8, 3, 3)[0], (a % 8) * (b % 8), 3)
    inputs = [(rng.randrange(16), rng.randrange(16)) for _ in range(trials)]
    for name, make in cases.items():
        vals = []
        for p in p_list:
            sim = AerSimulator(noise_model=noise_model(p), seed_simulator=11)
            vals.append(sum(success(*make(a, b)[:2], sim, shots) for a, b in inputs) / trials)
        out["series"][name] = vals
        print(name, [round(v, 3) for v in vals])
    json.dump(out, open(f"{RES}/ruido.json", "w"), indent=2, ensure_ascii=False)
    plot_ruido(out)
    return out


def plot_ruido(out):
    p_list = out["p2"]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    xs = [p * 100 for p in p_list]
    for name, ys in out["series"].items():
        lab = name + (" (3×3 bits)" if "Mult" in name else " (4 bits)")
        ax.plot(xs, ys, marker=MK[name], color=C[name], label=lab,
                markeredgecolor="white", markeredgewidth=1.5)
    ax.axhline(1 / 32, color=TEXT2, lw=1, ls="--")
    ax.text(0.75, 1 / 32 + 0.015, "adivinar al azar (suma de 4 bits)", ha="left", fontsize=9, color=TEXT2)
    ax.set_xlabel("Error por compuerta CNOT (%)  —  error de 1 qubit = 1/10")
    ax.set_ylabel("Probabilidad de obtener el resultado correcto")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="upper right")
    ax.set_title("Efecto del ruido depolarizante", loc="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(f"{FIG}/ruido.png")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Superposición: sumar b a TODOS los valores de a a la vez
# ---------------------------------------------------------------------------
def superposicion(n=3, b=5, shots=4000):
    core = draper_adder(n)
    ra, rb = core.qregs
    ca, cb = ClassicalRegister(n, "ma"), ClassicalRegister(n + 1, "mb")
    qc = QuantumCircuit(ra, rb, ca, cb)
    qc.h(ra)                       # a = superposición uniforme de 0..2^n-1
    for i in range(n + 1):
        if (b >> i) & 1:
            qc.x(rb[i])
    qc.compose(core, inplace=True)
    qc.measure(ra, ca)
    qc.measure(rb, cb)
    sim = AerSimulator(seed_simulator=3)
    counts = sim.run(transpile(qc, sim), shots=shots).result().get_counts()
    rows = []
    for key, c in counts.items():
        sb, sa = key.split()       # Qiskit imprime el último registro clásico primero
        rows.append((int(sa, 2), int(sb, 2), c))
    rows.sort()
    json.dump([{"a": a, "a_mas_b": s, "cuentas": c} for a, s, c in rows],
              open(f"{RES}/superposicion.json", "w"), indent=2)

    fig, ax = plt.subplots(figsize=(7, 3.8))
    labels = [f"a={a}\n{a}+{b}={s}" for a, s, _ in rows]
    vals = [c / shots for *_, c in rows]
    ax.bar(range(len(rows)), vals, color=C["Draper (QFT)"], width=0.7)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.004, f"{v:.3f}", ha="center", fontsize=9, color=TEXT)
    ax.axhline(1 / 2 ** n, color=TEXT2, lw=1, ls="--")
    ax.set_xticks(range(len(rows)), labels, fontsize=9)
    ax.set_ylabel("Frecuencia medida")
    ax.grid(axis="x", visible=False)
    ax.set_title(f"Una sola ejecución suma {b} a los {2**n} valores de a en superposición",
                 loc="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(f"{FIG}/superposicion.png")
    plt.close(fig)
    return rows


# ---------------------------------------------------------------------------
# 5. Ejemplo de histograma de una operación
# ---------------------------------------------------------------------------
def ejemplos():
    calc = QuantumCalculator(shots=1024)
    ex = []
    for r in [calc.add(320, 150), calc.add(320, 150, "ripple"), calc.multiply(53, 4),
              calc.multiply(15, 15), calc.evaluate("123 * 45")]:
        print(r)
        ex.append({"op": r.operation, "a": r.a, "b": r.b, "valor": r.value,
                   "esperado": r.expected, "p_correcto": r.success_probability, **r.metrics})
    json.dump(ex, open(f"{RES}/ejemplos.json", "w"), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    diagramas()
    print("diagramas ok")
    recursos()
    print("recursos ok")
    ejemplos()
    superposicion()
    print("superposicion ok")
    ruido()
    print("ruido ok")
