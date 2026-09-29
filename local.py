import math

# algoritmo greedy
def greedy(D, rdm = None):
    #primero tenemos que calcular la ciudad por la que comenzaremos
    sumatorios_ciudad = [(i, sum(D[i])) for i in range(len(D))] #i, numero ciudad; sumatorio distancias
    sumatorios_ciudad.sort(key=lambda x: x[1]) #ordena por sumatoria
    ciudad_comienzo = sumatorios_ciudad[0][0]

    #inicializacion de variables necesarias para la busqueda
    solucion = [ciudad_comienzo]
    visitados = [False] * len(D)
    visitados[ciudad_comienzo] = True
    ciudad_actual = ciudad_comienzo #fila
    coste_sol = 0

    n = 1
    while n < len(D): #este while es para que se ejecute tantas veces como ciudades sin visitar (para ver la fila)
        min_dist = math.inf
        indice_min = -1
        for j in range(len(D)): #para ver las columnas
            #aplicar la logica de coger el menor e ir rotando de ciudad en ciudad
            if not visitados[j]:
                dist = D[ciudad_actual][j]
                if dist < min_dist:
                    min_dist = dist
                    indice_min = j

        solucion.append(indice_min)
        visitados[indice_min] = True
        coste_sol += min_dist
        ciudad_actual = indice_min

        n += 1
    coste_sol += D[ciudad_actual][ciudad_comienzo] #esto para asegurar que sabemos la distancia de vuelta al punto de origen
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


def operador_2opt(i,solucion,D,n,dlb):
    for j in range(i + 1, n):
        ciudad_i = solucion[i]
        #necesitamos los arcos de las ciudades que van antes y despues
        ant_ciudad_i = solucion[i-1]
        post_ciudad_i = solucion[i+1]

        ciudad_j = solucion[j]
        ant_ciudad_j = solucion[(j-1) % n]
        post_ciudad_j = solucion[(j+1) % n]

        #caso en el que las ciudades estan separadas
        if j != i and not (i==0 and j == n-1):
            arcos_viejos = (D[ant_ciudad_i][ciudad_i] + D[ciudad_i][post_ciudad_i] +
                            D[ant_ciudad_j][ciudad_j] + D[ciudad_j][post_ciudad_j])

            arcos_nuevos = (D[ant_ciudad_i][ciudad_j] + D[ciudad_j][post_ciudad_i] +
                            D[ant_ciudad_j][ciudad_i] + D[ciudad_i][post_ciudad_j])
        delta = arcos_nuevos - arcos_viejos

    else:
        # caso en el que las ciudades estan adyacentes
        if j == i+1:
            arcos_viejos = D[ant_ciudad_i][ciudad_i] + D[ciudad_i][post_ciudad_i]
            arcos_nuevos = D[ant_ciudad_i][ciudad_j] + D[ciudad_j][post_ciudad_i]
        #si encontramos mejora
        if delta < -0.0001:
            solucion[i], solucion[j] = solucion[j], solucion[i]
            dlb[ciudad_i] = 0
            dlb[ciudad_j] = 0

            return True, delta
    return False,0

def busqueda_local_primer_mejor(D, rdm, k=None):
    n = len(D)

    # Generamos una solucion inicial aleatoria basada en la semilla
    solucion = list(range(n)) #esto crea una lista de n elementos
    rdm.shuffle(solucion) #esto cambia aleatoriamente soluciones
    coste_sol = calcular_coste(solucion, D)

    # Don't Look Bits (DLB)
    dlb = [0] * n
    hay_mejora_global = True
    vueltas = 0

    while hay_mejora_global and (k is None or vueltas < k):
        hay_mejora_global = False
        vueltas += 1

        for i in range(n):
            if dlb[i] == 1:
                continue #ya hemos mirado esa opcion y no es prometedora, asi que pasamos

            mejora_Local, delta = operador_2opt(i,solucion,D,n,dlb)

            if mejora_Local:
                coste_sol += delta
                hay_mejora_global = True
            else:
                dlb[i] = 1
    return solucion, coste_sol
