import math
from collections import deque
import random


def calcular_coste(ruta, D):
    coste = 0.0
    n = len(ruta)
    for i in range(n):
        coste += D[ruta[i]][ruta[(i + 1) % n]]
    return coste

def greedy_aleatorio(D, rdm = None, k = None, f_log= None):
    # Formato: lista de tuplas (id_ciudad, suma_distancias)
    vector_ordenado = [(i, sum(D[i])) for i in range(len(D))]
    vector_ordenado.sort(key=lambda x: x[1])  # Orden ascendente por sumatoria

    ciudades_disponibles = [ciudad for ciudad, _ in vector_ordenado]
    solucion = []

    # Construcción: en cada paso se elige al azar una entre las K primeras del vector
    while len(ciudades_disponibles) > 0:
        limite_k = min(k, len(ciudades_disponibles))
        idx_aleatorio = rdm.randint(0, limite_k - 1)

        ciudad_elegida = ciudades_disponibles.pop(idx_aleatorio)
        solucion.append(ciudad_elegida)
    coste_sol = calcular_coste(solucion, D)

    if f_log:
        f_log.write(
            f"[Greedy Aleatorio (K={k})] Solucion Construida || Coste: {coste_sol:.2f} || Solucion: {solucion}\n")
    return solucion, coste_sol