import math
from collections import deque
import random

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


def calcular_coste(ruta, D):
    coste = 0.0
    n = len(ruta)
    for i in range(n):
        coste += D[ruta[i]][ruta[(i + 1) % n]]
    return coste


def operador_2opt(i, solucion, D, n, dlb, evals_restantes):
    evals = 0
    ciudad_i = solucion[i]

    for j in range(i + 1, n):
        if evals >= evals_restantes:
            break
        evals += 1

        delta = delta_intercambio(solucion, D, n, i, j)

        if delta < -0.0001:
            ciudad_j = solucion[j]
            solucion[i], solucion[j] = ciudad_j, ciudad_i
            dlb[ciudad_i] = 0
            dlb[ciudad_j] = 0
            return True, delta, evals
    return False, 0, evals

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

# =====================================================================
# BUSQUEDA TABU (sobre primer mejor, con memoria a corto y largo plazo)
# =====================================================================


def busqueda_local_primer_mejor(D, rdm, k=None, it=None, f_log=None):
    n = len(D)
    solucion, coste_sol = greedy_aleatorio(D, rdm, k)

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

            mejora, delta, _ = operador_2opt(i, solucion, D, n, dlb, n)

            if mejora:
                coste_sol += delta
                iteraciones += 1
                hay_mejora_global = True
                if f_log:
                    f_log.write(f"[Iter {iteraciones}] 2-opt || Coste: {coste_sol:.2f}\n")
            else:
                dlb[ciudad] = 1
    return solucion, coste_sol



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
    solucion, coste = greedy_aleatorio(D, rdm, k)
    solucion = list(solucion)

    mejor_global = solucion[:]
    mejor_coste_global = coste
    mejor_coste_momento = coste

    dlb = [0] * n
    iteracion = 0
    num_empeora = 0
    inicio = rdm.randint(0, n - 1)

    limite_estancamiento = int(it * empeora) if it is not None else 200

    # MCP: cola de los ultimos 'tenencia' movimientos + contador para consulta O(1)
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
                if en_tabu.get((min(a, b), max(a, b)), 0) > 0:
                    continue            # movimiento tabu: descartado (sin aspiracion)

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

        clave = (min(a, b), max(a, b))
        cola_tabu.append(clave)
        en_tabu[clave] = en_tabu.get(clave, 0) + 1
        if len(cola_tabu) > tenencia:
            vieja = cola_tabu.popleft()
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