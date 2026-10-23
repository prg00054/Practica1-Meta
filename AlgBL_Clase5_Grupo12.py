import math
from collections import deque
import random
import AlgGREA_Clase5_Grupo12



def calcular_coste(ruta, D):
    coste = 0.0
    n = len(ruta)
    for i in range(n):
        coste += D[ruta[i]][ruta[(i + 1) % n]]
    return coste


def operador_2opt(i, solucion, D, n):
    """Prueba intercambiar la ciudad de la posicion i con TODAS las demas
    posiciones (j<i y j>i). Primer mejor: aplica el primero que mejora."""
    for j in range(n):
        if j == i:
            continue
        a, b = (i, j) if i < j else (j, i)
        delta = delta_intercambio(solucion, D, n, a, b)
        if delta < -0.0001:
            ci, cj = solucion[a], solucion[b]
            solucion[a], solucion[b] = cj, ci
            return True, delta, ci, cj
    return False, 0, None, None

def delta_intercambio(solucion, D, n, i, j):
    """Variacion de coste al intercambiar las ciudades de las posiciones i<j."""
    ciudad_i = solucion[i]
    ciudad_j = solucion[j]
    ant_i = solucion[i - 1]
    post_i = solucion[(i + 1) % n]
    ant_j = solucion[j - 1]
    post_j = solucion[(j + 1) % n]

    # caso en el que las ciudades estan separadas
    if j != i + 1 and not (i == 0 and j == n - 1):
        viejos = D[ant_i][ciudad_i] + D[ciudad_i][post_i] + D[ant_j][ciudad_j] + D[ciudad_j][post_j]
        nuevos = D[ant_i][ciudad_j] + D[ciudad_j][post_i] + D[ant_j][ciudad_i] + D[ciudad_i][post_j]
        # caso en el que las ciudades estan adyacentes
    elif j == i + 1:
        viejos = D[ant_i][ciudad_i] + D[ciudad_j][post_j]
        nuevos = D[ant_i][ciudad_j] + D[ciudad_i][post_j]
        # si las ciudades son adyacentes y son la primera y la ultima
    else:
        viejos = D[ant_j][ciudad_j] + D[ciudad_i][post_i]
        nuevos = D[ant_j][ciudad_i] + D[ciudad_j][post_i]
    return nuevos - viejos


def busqueda_local_primer_mejor(D, rdm, k=None, it=None, f_log=None):
    n = len(D)
    solucion, coste_sol = AlgGREA_Clase5_Grupo12.greedy_aleatorio(D, rdm, k)

    dlb = [0] * n
    iteraciones = 0                  # movimientos aplicados
    hay_mejora_global = True

    while hay_mejora_global and (it is None or iteraciones < it):
        hay_mejora_global = False

        for i in range(n):
            if it is not None and iteraciones >= it:
                break
            ciudad = solucion[i]
            if dlb[ciudad] == 1:
                continue

            mejora, delta, ci, cj = operador_2opt(i, solucion, D, n)

            if mejora:
                dlb[ci] = 0
                dlb[cj] = 0
                coste_sol += delta
                iteraciones += 1
                hay_mejora_global = True
                if f_log:
                    f_log.write(f"[Iter {iteraciones}] Intercambio ({ci} <-> {cj}) || Coste: {coste_sol:.2f}\n")
            else:
                dlb[ciudad] = 1
    return solucion, coste_sol