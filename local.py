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


def busqueda_local_primer_mejor(D, rdm, k=None):
    n = len(D)

    # 1. Solución inicial aleatoria basada en la semilla
    solucion = list(range(n)) #esto crea una lista de n elementos
    rdm.shuffle(solucion) #esto cambia aleatoriamente soluciones
    coste_sol = calcular_coste(solucion, D)

    # 2. Inicialización de Don't Look Bits (DLB): todos a 0 (prometedores)
    dlb = [0] * n
    hay_mejora_global = True

    while hay_mejora_global:
        hay_mejora_global = False

        for i in range(n):
            if dlb[i] == 1:
                continue #ya hemos mirado esa opcion y no es prometedora, asi que pasamos

            mejora_Local = False

            for j in range(i+2,n):
                if i == 0 and j == n-1: #aqui tenemos el caso que intercambiemos la primera y ultima ciudad
                    continue

                #extraemos las 4 ciudades involucradas en el cambio: A->B->...->C->D
                ciudad_A = solucion[i]
                ciudad_B = solucion[i+1]
                ciudad_C = solucion[j]
                ciudad_D = solucion[(j+1) % n]

                #Aqui calculamos la diferencia en el coste que tenemos al intercambiar
                delta = (D[ciudad_A][ciudad_C] + D[ciudad_B][ciudad_D]) - (D[ciudad_A][ciudad_B] + D[ciudad_C][ciudad_D])

                if delta < -0.0001:
                    solucion[i+1 : j+1] = solucion[i+1 : j+1][::-1]
                    coste_sol += delta
                    dlb[ciudad_A] = 0
                    dlb[ciudad_B] = 0
                    dlb[ciudad_C] = 0
                    dlb[ciudad_D] = 0

                    hay_mejora_global = True
                    mejora_Local = True

                    break #estamos con el primero el mejor asi que cortamos

            if not mejora_Local:
                dlb[i] = 1
    return solucion, coste_sol
