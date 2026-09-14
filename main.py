import sys
import math
import time
import random
import pandas as pd

#import local
#import evolutivo

# =====================================================================
# 1. Carga de Parametros
# =====================================================================
# Fichero parametros.txt con formato:
#   Semillas: 1, 3, 8
#   Algoritmos: Greedy, GreedyAleatorio
#   Datasets: a280, ch130, pr144, u1060, d18512

def leer_parametros(ruta_fichero):
    semillas, algoritmos, datasets = [], [], []

    with open(ruta_fichero, 'r') as f:
        lineas = f.readlines() #readlines lo que hace es devolver una lista donde cada elemento es una linea

    for linea in lineas:
        linea = linea.strip() #strip elimina espacios en blanco
        if not linea or ':' not in linea: continue

        partes = linea.split(':', 1)
        etiqueta = partes[0].strip().lower()
        valores = [v.strip() for v in partes[1].split(',')]

        if 'semilla' in etiqueta: semillas = [int(v) for v in valores]
        elif 'algoritmo' in etiqueta: algoritmos = valores
        elif 'dataset' in etiqueta: datasets = valores

    return semillas, algoritmos, datasets


# =====================================================================
# 2. Lectura de Datasets
# =====================================================================
# Ficheros en formato TSPLIB (.tsp) con cabecera + NODE_COORD_SECTION.
#
# Para instancias muy grandes (p.ej. d18512, 18512 ciudades) una matriz
# de distancias densa n*n no cabe en memoria (~340 millones de celdas).
# Por eso, a partir de UMBRAL_MATRIZ_DENSA ciudades, se usa una matriz
# "perezosa" que calcula cada distancia al vuelo a partir de las
# coordenadas, pero se sigue pudiendo indexar igual: D[i][j].

UMBRAL_MATRIZ_DENSA = 2000  # por debajo -> matriz densa; por encima -> perezosa


class MatrizDistanciasPerezosa:
    """Se comporta como D[i][j] sin almacenar los n*n valores."""
    def __init__(self, coords):
        self.coords = coords
        self.n = len(coords)

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        return _FilaPerezosa(self, i)


class _FilaPerezosa:
    def __init__(self, matriz, i):
        self.matriz = matriz
        self.i = i

    def __getitem__(self, j):
        xi, yi = self.matriz.coords[self.i]
        xj, yj = self.matriz.coords[j]
        return math.sqrt((xj - xi) ** 2 + (yj - yi) ** 2)


#Los parámetros de esta funcion son las coordenadas x e y de dos puntos distintos
def distanciaEuclidea(x1:int,y1:int,x2:int,y2:int):
    return math.sqrt( (x2-x1)**2 +  (y2-y1)**2)

def leer_dataset(nombre_dataset):
    ruta_dataset = f"{ruta_proyecto}/datos/{nombre_dataset}.tsp"

    dimension = 0
    lista_coord = []
    leyendo_cord = False  # esta variable me sirve como un flag para saber si estoy procesando las coordenadas

    with open(ruta_dataset, 'r') as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue

            if linea.find("DIMENSION") == 0:
                pos = linea.find(":") #busco la posicion donde está `:` para pegar el corte
                dimension = int(linea[pos + 1:].strip())

            elif linea.find("NODE_COORD_SECTION") == 0:
                leyendo_cord = True

            elif linea.find("EOF") == 0:
                leyendo_cord = False

            elif leyendo_cord:
                partes = linea.split()
                # con esta funcion divido en partes la linea por espacios de forma que asi saco el nº de ciudad y las coordenadas
                # id_ciudad = partes[0]
                x = float(partes[1])
                y = float(partes[2])
                lista_coord.append((x, y))

    if dimension <= UMBRAL_MATRIZ_DENSA:
        distancias = [[0.0 for _ in range(dimension)] for _ in range(dimension)]
        for i in range(dimension):
            for j in range(i + 1, dimension):
                    distancias[i][j] = distancias[j][i] = distanciaEuclidea(lista_coord[i][0], lista_coord[i][1],
                                                                            lista_coord[j][0], lista_coord[j][1])
    else:
        D = MatrizDistanciasPerezosa(lista_coord)

    print(f"  [+] Cargando datos del dataset: {nombre_dataset}... ({dimension} ciudades)")

    return D

# =====================================================================
# 3. Ejecucion de la Experimentacion
# =====================================================================
def mis_algoritmos(algoritmo, datos, rdm):
    algoritmos = {
        'greedy': local.greedy,
        'greedyaleatorio': local.greedy_aleatorio,
        'evolutivo': evolutivo.ejecutar
    }

    clave = algoritmo.strip().lower().replace(" ", "")
    if clave not in algoritmos:
        raise ValueError(f"Algoritmo desconocido: {algoritmo}")

    return algoritmos[clave](datos, rdm)


# Ejecucion y visualizacion de parametros
ruta_proyecto = "."  # <-- ajustar a la ruta real del proyecto
ruta_params = f"{ruta_proyecto}/parametros.txt"
semillas, algoritmos, datasets = leer_parametros(ruta_params)

#Voy a poner el trozo este por aqui que era al final lo que queria poner pero puede no vaya justo aquí
for _ in range(len(datasets)):
    D = leer_dataset(datasets[_]) #aqui ya cargo la matriz de distancias segun los datasets
    sumatorios_ciudad = [(fila,sum(fila)) for fila in D]
sumatorios_ciudad.sort(key = lambda x: x[1])
ciudad_comienzo = sumatorios_ciudad[0][0]


print("\033[1mPARAMETROS CARGADOS CORRECTAMENTE\033[0m")
summary = pd.DataFrame({
    'Parametro': ['Semillas', 'Algoritmos', 'Datasets'],
    'Valores': [str(semillas), ", ".join(algoritmos), ", ".join(datasets)]
})
print(summary)

print(f"\033[1mINICIANDO EXPERIMENTACION\033[0m\n" + "=" * 30)

for dataset in datasets:
    print(f"\n\033[1;34mDATASET: {dataset}\033[0m")
    print("-" * 15)
    datos = leer_dataset(dataset)

    for semilla in semillas:
        rdm = random.Random(semilla)
        for algoritmo in algoritmos:
            print(f"  > {algoritmo:16} | Semilla: {semilla:6}", end="")

            inicio = time.time()
            solucion, coste = mis_algoritmos(algoritmo, datos, rdm)
            fin = time.time()

            print(f" | Coste: {coste:12.2f} | Tiempo: {fin-inicio:.4f}s")

print("\n" + "=" * 30 + "\n\033[1mPROCESO FINALIZADO\033[0m")
