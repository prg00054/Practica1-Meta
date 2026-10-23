import math
from collections import deque
import random


def calcular_coste(ruta, D):
    coste = 0.0
    n = len(ruta)
    for i in range(n):
        coste += D[ruta[i]][ruta[(i + 1) % n]]
    return coste

# algoritmo greedy
def greedy(D, f_log= None):
    #primero tenemos que calcular la ciudad por la que comenzaremos
    v_ordenado = [(i, sum(D[i])) for i in range(len(D))] #i, numero ciudad; sumatorio distancias
    v_ordenado.sort(key=lambda x: x[1]) #ordena por sumatoria

    solucion = [ciudad for ciudad, _ in v_ordenado]
    coste_sol = calcular_coste(solucion, D)

    if f_log:
        f_log.write(f"[Greedy] Solucion Construida || Coste: {coste_sol:.2f} || Solucion: {solucion}\n")
    return solucion, coste_sol
