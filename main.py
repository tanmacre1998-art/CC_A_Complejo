"""Calculadora cuántica interactiva en la terminal.

Uso:
    python main.py                 # modo interactivo
    python main.py "25 * 13"       # una sola operación
    python main.py "25 + 13" --ripple --dibujar
"""

import argparse

from qcalc import QuantumCalculator


def show(calc, expr, method, draw):
    r = calc.evaluate(expr, method=method)
    print(f"\n  {r}")
    print(f"  Operación: {r.operation} | recursos: {r.metrics}")
    if draw:
        print(r.circuit.draw("text", fold=120))


def main():
    p = argparse.ArgumentParser(description="Calculadora cuántica (suma y multiplicación) con Qiskit")
    p.add_argument("expresion", nargs="?", help="por ejemplo '7 + 5' o '6 * 3'")
    p.add_argument("--ripple", action="store_true", help="sumar con el sumador de Cuccaro en vez de la QFT")
    p.add_argument("--dibujar", action="store_true", help="mostrar el circuito en texto")
    p.add_argument("--shots", type=int, default=1024)
    args = p.parse_args()

    calc = QuantumCalculator(shots=args.shots)
    method = "ripple" if args.ripple else "qft"

    if args.expresion:
        show(calc, args.expresion, method, args.dibujar)
        return

    print("Calculadora cuántica — escribe 'a + b' o 'a * b' (enteros >= 0). 'salir' para terminar.")
    while True:
        try:
            expr = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if expr.lower() in {"salir", "exit", "q"}:
            break
        try:
            show(calc, expr, method, args.dibujar)
        except ValueError as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    main()
