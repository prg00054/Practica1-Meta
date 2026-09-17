import math

# algoritmo greedy
def greedy(D,semilla):
    #primero tenemos que calcular la ciudad por la que comenzaremos
    sumatorios_ciudad = [(i, sum(D[i])) for i in range(len(D))]
    sumatorios_ciudad.sort(key=lambda x: x[1])
    ciudad_comienzo = sumatorios_ciudad[0][0]

    #inicializacion de variables necesarias para la busqueda
    solucion = [ciudad_comienzo]
    visitados = [False] * len(D)
    visitados[ciudad_comienzo] = True
    ciudad_actual = ciudad_comienzo
    coste_sol = 0

    n = 1
    while n < len(D): #este while es para que se ejecute tantas veces como ciudades sin visitar
        min_dist = math.inf
        indice_min = -1
        for j in range(len(D)):
            #aplicar la logica de coger el menor e ir rotando de ciudad en ciudad


        n += 1
    coste_sol += D[ciudad_actual][ciudad_comienzo] #esto para asegurar que sabemos la distancia de vuelta al punto de origen( se puede debatir si dejarla o no)
    return solucion, coste_sol


