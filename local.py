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
    # 1. Calculamos el vector ordenado por la sumatoria de distancias
    sumatorios_ciudad = [(i, sum(D[i])) for i in range(len(D))]
    sumatorios_ciudad.sort(key=lambda x: x[1])

    # Se elige de forma aleatoria una entre las k primeras ciudades más prometedoras
    limite_k_ini = min(k, len(sumatorios_ciudad)) #quitaria esta linea por pura redundancia
    indice_elegido = rdm.randint(0, limite_k_ini - 1)
    ciudad_comienzo = sumatorios_ciudad[indice_elegido][0]

    # Inicializacion de variables necesarias para la busqueda
    solucion = [ciudad_comienzo]
    visitados = [False] * len(D)
    visitados[ciudad_comienzo] = True
    ciudad_actual = ciudad_comienzo
    coste_sol = 0

    n = 1
    while n < len(D):
        # Recogemos todas las ciudades no visitadas con su distancia a la ciudad_actual
        candidatos = []
        for j in range(len(D)):
            if not visitados[j]:
                candidatos.append((j, D[ciudad_actual][j]))

        # Ordenamos los candidatos de menor a mayor distancia
        candidatos.sort(key=lambda x: x[1])

        # Tomamos como maximo las k mejores ciudades mas cercanas
        limite_k = min(k, len(candidatos)) #esta linea igual la quitaba por redundancia
        idx_aleatorio = rdm.randint(0, limite_k - 1)
        ciudad_elegida, distancia_elegida = candidatos[idx_aleatorio]

        # Aplicamos el movimiento
        solucion.append(ciudad_elegida)
        visitados[ciudad_elegida] = True
        coste_sol += distancia_elegida
        ciudad_actual = ciudad_elegida

        n += 1

    coste_sol += D[ciudad_actual][ciudad_comienzo]  # Cierre del ciclo volviendo al inicio
    return solucion, coste_sol
