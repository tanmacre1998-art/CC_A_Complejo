# Circuitos listos para el IBM Quantum Composer

Abran el archivo de la operación con el Bloc de notas, copien todo, péguenlo en el editor OpenQASM del Composer y denle **Set up and run**.
En el histograma de IBM, la barra correcta es la de la columna **Barra en IBM**.

## Sumas (sumador de Cuccaro, números de 0 a 7) → carpeta `sumas/`

| Operación | Archivo | Resultado | Barra en IBM |
|---|---|---|---|
| 0 + 0 | `sumas/0mas0.qasm` | 0 | `0000` |
| 0 + 1 | `sumas/0mas1.qasm` | 1 | `0001` |
| 0 + 2 | `sumas/0mas2.qasm` | 2 | `0010` |
| 0 + 3 | `sumas/0mas3.qasm` | 3 | `0011` |
| 0 + 4 | `sumas/0mas4.qasm` | 4 | `0100` |
| 0 + 5 | `sumas/0mas5.qasm` | 5 | `0101` |
| 0 + 6 | `sumas/0mas6.qasm` | 6 | `0110` |
| 0 + 7 | `sumas/0mas7.qasm` | 7 | `0111` |
| 1 + 0 | `sumas/1mas0.qasm` | 1 | `0001` |
| 1 + 1 | `sumas/1mas1.qasm` | 2 | `0010` |
| 1 + 2 | `sumas/1mas2.qasm` | 3 | `0011` |
| 1 + 3 | `sumas/1mas3.qasm` | 4 | `0100` |
| 1 + 4 | `sumas/1mas4.qasm` | 5 | `0101` |
| 1 + 5 | `sumas/1mas5.qasm` | 6 | `0110` |
| 1 + 6 | `sumas/1mas6.qasm` | 7 | `0111` |
| 1 + 7 | `sumas/1mas7.qasm` | 8 | `1000` |
| 2 + 0 | `sumas/2mas0.qasm` | 2 | `0010` |
| 2 + 1 | `sumas/2mas1.qasm` | 3 | `0011` |
| 2 + 2 | `sumas/2mas2.qasm` | 4 | `0100` |
| 2 + 3 | `sumas/2mas3.qasm` | 5 | `0101` |
| 2 + 4 | `sumas/2mas4.qasm` | 6 | `0110` |
| 2 + 5 | `sumas/2mas5.qasm` | 7 | `0111` |
| 2 + 6 | `sumas/2mas6.qasm` | 8 | `1000` |
| 2 + 7 | `sumas/2mas7.qasm` | 9 | `1001` |
| 3 + 0 | `sumas/3mas0.qasm` | 3 | `0011` |
| 3 + 1 | `sumas/3mas1.qasm` | 4 | `0100` |
| 3 + 2 | `sumas/3mas2.qasm` | 5 | `0101` |
| 3 + 3 | `sumas/3mas3.qasm` | 6 | `0110` |
| 3 + 4 | `sumas/3mas4.qasm` | 7 | `0111` |
| 3 + 5 | `sumas/3mas5.qasm` | 8 | `1000` |
| 3 + 6 | `sumas/3mas6.qasm` | 9 | `1001` |
| 3 + 7 | `sumas/3mas7.qasm` | 10 | `1010` |
| 4 + 0 | `sumas/4mas0.qasm` | 4 | `0100` |
| 4 + 1 | `sumas/4mas1.qasm` | 5 | `0101` |
| 4 + 2 | `sumas/4mas2.qasm` | 6 | `0110` |
| 4 + 3 | `sumas/4mas3.qasm` | 7 | `0111` |
| 4 + 4 | `sumas/4mas4.qasm` | 8 | `1000` |
| 4 + 5 | `sumas/4mas5.qasm` | 9 | `1001` |
| 4 + 6 | `sumas/4mas6.qasm` | 10 | `1010` |
| 4 + 7 | `sumas/4mas7.qasm` | 11 | `1011` |
| 5 + 0 | `sumas/5mas0.qasm` | 5 | `0101` |
| 5 + 1 | `sumas/5mas1.qasm` | 6 | `0110` |
| 5 + 2 | `sumas/5mas2.qasm` | 7 | `0111` |
| 5 + 3 | `sumas/5mas3.qasm` | 8 | `1000` |
| 5 + 4 | `sumas/5mas4.qasm` | 9 | `1001` |
| 5 + 5 | `sumas/5mas5.qasm` | 10 | `1010` |
| 5 + 6 | `sumas/5mas6.qasm` | 11 | `1011` |
| 5 + 7 | `sumas/5mas7.qasm` | 12 | `1100` |
| 6 + 0 | `sumas/6mas0.qasm` | 6 | `0110` |
| 6 + 1 | `sumas/6mas1.qasm` | 7 | `0111` |
| 6 + 2 | `sumas/6mas2.qasm` | 8 | `1000` |
| 6 + 3 | `sumas/6mas3.qasm` | 9 | `1001` |
| 6 + 4 | `sumas/6mas4.qasm` | 10 | `1010` |
| 6 + 5 | `sumas/6mas5.qasm` | 11 | `1011` |
| 6 + 6 | `sumas/6mas6.qasm` | 12 | `1100` |
| 6 + 7 | `sumas/6mas7.qasm` | 13 | `1101` |
| 7 + 0 | `sumas/7mas0.qasm` | 7 | `0111` |
| 7 + 1 | `sumas/7mas1.qasm` | 8 | `1000` |
| 7 + 2 | `sumas/7mas2.qasm` | 9 | `1001` |
| 7 + 3 | `sumas/7mas3.qasm` | 10 | `1010` |
| 7 + 4 | `sumas/7mas4.qasm` | 11 | `1011` |
| 7 + 5 | `sumas/7mas5.qasm` | 12 | `1100` |
| 7 + 6 | `sumas/7mas6.qasm` | 13 | `1101` |
| 7 + 7 | `sumas/7mas7.qasm` | 14 | `1110` |

## Multiplicaciones (números de 0 a 3) → carpeta `multiplicaciones/`

| Operación | Archivo | Resultado | Barra en IBM |
|---|---|---|---|
| 0 × 0 | `multiplicaciones/0por0.qasm` | 0 | `0000` |
| 0 × 1 | `multiplicaciones/0por1.qasm` | 0 | `0000` |
| 0 × 2 | `multiplicaciones/0por2.qasm` | 0 | `0000` |
| 0 × 3 | `multiplicaciones/0por3.qasm` | 0 | `0000` |
| 1 × 0 | `multiplicaciones/1por0.qasm` | 0 | `0000` |
| 1 × 1 | `multiplicaciones/1por1.qasm` | 1 | `0001` |
| 1 × 2 | `multiplicaciones/1por2.qasm` | 2 | `0010` |
| 1 × 3 | `multiplicaciones/1por3.qasm` | 3 | `0011` |
| 2 × 0 | `multiplicaciones/2por0.qasm` | 0 | `0000` |
| 2 × 1 | `multiplicaciones/2por1.qasm` | 2 | `0010` |
| 2 × 2 | `multiplicaciones/2por2.qasm` | 4 | `0100` |
| 2 × 3 | `multiplicaciones/2por3.qasm` | 6 | `0110` |
| 3 × 0 | `multiplicaciones/3por0.qasm` | 0 | `0000` |
| 3 × 1 | `multiplicaciones/3por1.qasm` | 3 | `0011` |
| 3 × 2 | `multiplicaciones/3por2.qasm` | 6 | `0110` |
| 3 × 3 | `multiplicaciones/3por3.qasm` | 9 | `1001` |

Las multiplicaciones tienen muchas más compuertas que las sumas, así que en el computador real salen con bastante más ruido.
