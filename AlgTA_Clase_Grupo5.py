import math
from collections import deque
import random
import AlgGREA_Clase_Grupo5


def calcular_coste(ruta, D):
    coste = 0.0
    n = len(ruta)
    for i in range(n):
        coste += D[ruta[i]][ruta[(i + 1) % n]]
    return coste

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


def actualizar_frecuencias(solucion, frec):
    """Memoria a largo plazo: suma 1 a cada arco (ciudad-ciudad) de la solucion.
    frec[a][b] se guarda como diccionario disperso (valido para n grande)."""
    n = len(solucion)
    for k in range(n):
        a = solucion[k]
        b = solucion[(k + 1) % n]
        frec[a][b] = frec[a].get(b, 0) + 1
        frec[b][a] = frec[b].get(a, 0) + 1


def mas_visitados(frec, n, rdm):
    """Intensificacion: construye una solucion siguiendo los arcos mas frecuentes."""
    sinvisitar = set(range(n))
    actual = rdm.randint(0, n - 1)
    sol = [actual]
    sinvisitar.discard(actual)
    while sinvisitar:
        mejor, mejor_f = None, -1
        for vecino, f in frec[actual].items():
            if vecino in sinvisitar and f > mejor_f:
                mejor, mejor_f = vecino, f
        if mejor is None:  # ningun arco memorizado libre: ciudad al azar
            mejor = rdm.choice(tuple(sinvisitar))
        sol.append(mejor)
        sinvisitar.discard(mejor)
        actual = mejor
    return sol


def menos_visitados(frec, n, rdm, muestra=10):
    """Diversificacion: construye una solucion con arcos poco frecuentes.
    En cada paso se muestrean 'muestra' ciudades libres y se elige la menos frecuente."""
    libres = list(range(n))
    pos = rdm.randint(0, n - 1)
    actual = libres[pos]
    libres[pos] = libres[-1]
    libres.pop()
    sol = [actual]
    while libres:
        mejor_pos, mejor_f = None, None
        for _ in range(min(muestra, len(libres))):
            p = rdm.randint(0, len(libres) - 1)
            f = frec[actual].get(libres[p], 0)
            if mejor_f is None or f < mejor_f:
                mejor_pos, mejor_f = p, f
                if f == 0:
                    break
        actual = libres[mejor_pos]
        libres[mejor_pos] = libres[-1]
        libres.pop()
        sol.append(actual)
    return sol


def busqueda_tabu(D, rdm, k=None, it=None, tenencia=10, empeora=0.05, oscila=0.5, f_log=None):
    n = len(D)
    solucion, coste = AlgGREA_Clase_Grupo5.greedy_aleatorio(D, rdm, k)
    solucion = list(solucion)

    mejor_global = solucion[:]
    mejor_coste_global = coste
    mejor_coste_momento = coste

    dlb = [0] * n
    iteracion = 0
    num_empeora = 0
    inicio = rdm.randint(0, n - 1)

    limite_estancamiento = int(it * empeora) if it is not None else 200

    # MCP: cola de los ultimos 'tenencia' movimientos (ciudades + posiciones) + contador para consulta O(1)
    cola_tabu = deque()
    en_tabu = {}

    # MLP: frecuencia de arcos
    frec = [dict() for _ in range(n)]
    actualizar_frecuencias(solucion, frec)

    while it is None or iteracion < it:
        mov = None
        peor = None
        mejor_peor = math.inf

        for cont in range(n):
            if mov is not None:
                break
            i = (inicio + cont) % n
            if dlb[i] == 1:
                continue
            mejora_local = False

            for j in range(i + 1, n):
                a, b = solucion[i], solucion[j]
                if (en_tabu.get(('c', min(a, b), max(a, b)), 0) > 0
                        or en_tabu.get(('p', i, j), 0) > 0):
                    continue            # movimiento tabu (ciudades o posiciones): descartado (sin aspiracion)

                delta = delta_intercambio(solucion, D, n, i, j)

                if delta < -0.0001:
                    mov = (i, j, delta)
                    inicio = (i + 1) % n
                    mejora_local = True
                    break
                if delta < mejor_peor:
                    mejor_peor = delta
                    peor = (i, j, delta)

            if not mejora_local:
                dlb[i] = 1

        if mov is None:
            mov = peor

        if mov is None:
            cola_tabu.clear()
            en_tabu.clear()
            dlb = [0] * n
            iteracion += 1
            if f_log:
                f_log.write(f"[Iter {iteracion}] Vecindario bloqueado -> reseteo de lista tabu\n")
            continue

        i, j, delta = mov
        a, b = solucion[i], solucion[j]          # ciudades antes del intercambio
        solucion[i], solucion[j] = b, a
        coste += delta

        if f_log:
            f_log.write(f"[Iter {iteracion}] Intercambio ({a} <-> {b}) || Coste: {coste:.2f}\n")

        if coste < mejor_coste_global - 1e-9:
            mejor_coste_global = coste
            mejor_global = solucion[:]

        if coste < mejor_coste_momento - 1e-9:
            mejor_coste_momento = coste
            num_empeora = 0
        else:
            num_empeora += 1

        actualizar_frecuencias(solucion, frec)

        # por cada movimiento se guardan dos valores: el par de ciudades y el par de posiciones
        claves = (('c', min(a, b), max(a, b)), ('p', i, j))
        cola_tabu.append(claves)
        for clave in claves:
            en_tabu[clave] = en_tabu.get(clave, 0) + 1
        if len(cola_tabu) > tenencia:
            for vieja in cola_tabu.popleft():
                en_tabu[vieja] -= 1

        dlb = [0] * n
        iteracion += 1

        if num_empeora >= limite_estancamiento and (it is None or iteracion < it):
            num_empeora = 0
            if rdm.random() < oscila:
                solucion = mas_visitados(frec, n, rdm)
                tipo_osc = "Intensificacion"
            else:
                solucion = menos_visitados(frec, n, rdm)
                tipo_osc = "Diversificacion"

            coste = calcular_coste(solucion, D)
            mejor_coste_momento = coste
            if f_log:
                f_log.write(f"[Iter {iteracion}] ESTANCAMIENTO -> {tipo_osc} || Nuevo Coste: {coste:.2f}\n")

            if coste < mejor_coste_global:
                mejor_coste_global = coste
                mejor_global = solucion[:]

            cola_tabu.clear()
            en_tabu.clear()
            dlb = [0] * n
            inicio = rdm.randint(0, n - 1)

    return mejor_global, calcular_coste(mejor_global, D)