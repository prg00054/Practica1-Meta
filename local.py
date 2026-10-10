import math

# algoritmo greedy
def greedy(D, rdm = None):
    #primero tenemos que calcular la ciudad por la que comenzaremos
    solucion = [(i, sum(D[i])) for i in range(len(D))] #i, numero ciudad; sumatorio distancias
    solucion.sort(key=lambda x: x[1]) #ordena por sumatoria

    #inicializacion de variables necesarias para la busqueda
    coste_sol = 0
    n = len(solucion)
    for i in range(n):
        if i != n-1:
            coste_sol += D[solucion[i][0]][solucion[i+1][0]]
        else:
            coste_sol += D[solucion[0][0]][solucion[n-1][0]] #esto para asegurar que sabemos la distancia de vuelta al punto de origen
    return solucion, coste_sol


def greedy_aleatorio(D, rdm = None, k = None):
    # 1. Calculamos el vector ordenado por la sumatoria de distancias al resto
    # Formato: lista de tuplas (id_ciudad, suma_distancias)
    vector_ordenado = [(i, sum(D[i])) for i in range(len(D))]
    vector_ordenado.sort(key=lambda x: x[1])  # Orden ascendente por sumatoria

    # Extraemos solo los identificadores de las ciudades en orden
    ciudades_disponibles = [ciudad for ciudad, _ in vector_ordenado]
    solucion = []

    # 2. Construcción: en cada paso se elige al azar una entre las K primeras del vector
    while len(ciudades_disponibles) > 0:
        limite_k = min(k, len(ciudades_disponibles))
        idx_aleatorio = rdm.randint(0, limite_k - 1)

        # Obtenemos la ciudad elegida y la eliminamos del vector disponible
        ciudad_elegida = ciudades_disponibles.pop(idx_aleatorio)
        solucion.append(ciudad_elegida)

    # 3. Cálculo del coste total del ciclo hamiltoniano resultante
    coste_sol = calcular_coste(solucion, D)

    return solucion, coste_sol


def calcular_coste(ruta, D):
    coste = 0.0
    n = len(ruta)
    for i in range(n):
        coste += D[ruta[i]][ruta[(i + 1) % n]]
    return coste


def operador_2opt(i,solucion,D,n,dlb,evals_restantes):
    evals = 0
    ciudad_i = solucion[i]
    # necesitamos los arcos de las ciudades que van antes y despues
    ant_ciudad_i = solucion[i - 1]
    post_ciudad_i = solucion[(i + 1) % n]

    for j in range(i + 1, n):
        if evals >= evals_restantes:
            break
        evals += 1

        ciudad_j = solucion[j]
        ant_ciudad_j = solucion[(j-1) % n]
        post_ciudad_j = solucion[(j+1) % n]

        #caso en el que las ciudades estan separadas
        if j != i + 1 and not (i==0 and j == n-1):
            arcos_viejos = (D[ant_ciudad_i][ciudad_i] + D[ciudad_i][post_ciudad_i] +
                            D[ant_ciudad_j][ciudad_j] + D[ciudad_j][post_ciudad_j])
            arcos_nuevos = (D[ant_ciudad_i][ciudad_j] + D[ciudad_j][post_ciudad_i] +
                            D[ant_ciudad_j][ciudad_i] + D[ciudad_i][post_ciudad_j])
            delta = arcos_nuevos - arcos_viejos

        else:
            # caso en el que las ciudades estan adyacentes
            if j == i+1:
                arcos_viejos = D[ant_ciudad_i][ciudad_i] + D[ciudad_j][post_ciudad_j]
                arcos_nuevos = D[ant_ciudad_i][ciudad_j] + D[ciudad_i][post_ciudad_j]
                delta = arcos_nuevos - arcos_viejos
            else:
                # si las ciudades son adyacentes y son la primera y la ultima
                arcos_viejos = D[ant_ciudad_j][ciudad_j] + D[ciudad_i][post_ciudad_i]
                arcos_nuevos = D[ant_ciudad_j][ciudad_i] + D[ciudad_j][post_ciudad_i]
                delta = arcos_nuevos - arcos_viejos

            #si encontramos mejora
        if delta < -0.0001:
            solucion[i], solucion[j] = solucion[j], solucion[i]
            dlb[ciudad_i] = 0
            dlb[ciudad_j] = 0
            return True, delta, evals
    return False,0,evals

def busqueda_local_primer_mejor(D, rdm, k=None,it=None):
    n = len(D)
    # Generamos una solucion inicial aleatoria basada en la semilla
    solucion, coste_sol = greedy_aleatorio(D,rdm,k) #esto crea una lista de n elementos

    # Don't Look Bits (DLB)
    dlb = [0] * n
    evals = 0
    hay_mejora_global = True

    while hay_mejora_global and (it is None or evals < it):
        hay_mejora_global = False

        for i in range(n):
            if it is not None and evals >= it:
                break
            ciudad = solucion[i]

            if dlb[ciudad] == 1:
                continue

            restantes = (it - evals) if it is not None else n

            mejora_Local, delta, usadas = operador_2opt(i,solucion,D,n,dlb,restantes)
            evals += usadas

            if mejora_Local:
                coste_sol += delta
                hay_mejora_global = True
            else:
                dlb[ciudad] = 1
    return solucion, coste_sol
