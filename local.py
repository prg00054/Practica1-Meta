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


