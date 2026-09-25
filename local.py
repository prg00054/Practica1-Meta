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
