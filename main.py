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
        lineas = f.readlines()

    for linea in lineas:
        linea = linea.strip()
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


def leer_dataset(nombre_dataset):
    ruta_dataset = f"{ruta_proyecto}/datos/{nombre_dataset}.tsp"

    coordenadas = {}
    dentro_de_coordenadas = False

    with open(ruta_dataset, 'r') as f:
        for linea in f:
            linea = linea.strip()

            if not linea or linea == "EOF":
                continue

            if linea.startswith("NODE_COORD_SECTION"):
                dentro_de_coordenadas = True
                continue

            if not dentro_de_coordenadas:
                continue

            partes = linea.split()
            id_ciudad = int(partes[0])
            x = float(partes[1])
            y = float(partes[2])
            coordenadas[id_ciudad] = (x, y)

    n = len(coordenadas)
    coords_lista = [coordenadas[i] for i in range(1, n + 1)]

    if n <= UMBRAL_MATRIZ_DENSA:
        D = [[0.0] * n for _ in range(n)]
        for i in range(1, n + 1):
            xi, yi = coordenadas[i]
            for j in range(i + 1, n + 1):
                xj, yj = coordenadas[j]
                dist = math.sqrt((xj - xi) ** 2 + (yj - yi) ** 2)
                D[i - 1][j - 1] = dist
                D[j - 1][i - 1] = dist
    else:
        D = MatrizDistanciasPerezosa(coords_lista)

    print(f"  [+] Cargando datos del dataset: {nombre_dataset}... ({n} ciudades)")

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
