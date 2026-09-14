import sys
import pandas as pd
import random

# =====================================================================
# 1. Carga de Parametros
# =====================================================================

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


# Ejecucion y visualizacion de parametros
ruta_params = f"{ruta_proyecto}/parametros.txt"
semillas, algoritmos, datasets = leer_parametros(ruta_params)

# Presentacion elegante de los parametros
print("\033[1mPARAMETROS CARGADOS CORRECTAMENTE\033[0m")
summary = pd.DataFrame({
    'Parametro': ['Semillas', 'Algoritmos', 'Datasets'],
    'Valores': [str(semillas), ", ".join(algoritmos), ", ".join(datasets)]
})
display(summary)


# =====================================================================
# 2. Lectura de Datasets
# =====================================================================

def leer_dataset(nombre_dataset):
    # Aqui configuras como se lee tu fichero especifico (CSV, TXT, ARFF...)
    ruta_dataset = f"{ruta_proyecto}/datos/{nombre_dataset}.tsp"

    # Para la plantilla, simplemente devolvemos un texto simulado
    print(f"  [+] Cargando datos del dataset: {nombre_dataset}...")
    return f"Datos_cargados_de_{nombre_dataset}"


# =====================================================================
# 3. Ejecucion de la Experimentacion
# =====================================================================

import time

print(f"\033[1mINICIANDO EXPERIMENTACION\033[0m\n" + "=" * 30)

for dataset in datasets:
    print(f"\n\033[1;34mDATASET: {dataset}\033[0m")
    print("-" * 15)
    datos = leer_dataset(dataset)

    for semilla in semillas:
        rdm = random.Random(semilla)
        for algoritmo in algoritmos:
            print(f"  > {algoritmo:12} | Semilla: {semilla:6}", end="")

            inicio = time.time()
            # --- Logica del algoritmo ---
            solucion, coste = mis_algoritmos(algoritmo, datos, rdm)
            #time.sleep(0.05)
            # -----------------------------
            fin = time.time()

            print(f" | Sol: {solucion} | Coste: {coste} | Tiempo: {fin-inicio:.4f}s")

print("\n" + "=" * 30 + "\n\033[1mPROCESO FINALIZADO\033[0m")


def mis_algoritmos(algoritmo, datos, rdm):
    algoritmos = {
        'local': local.ejecutar,
        'evolutivo': evolutivo.ejecutar
    }
    if algoritmo not in algoritmos:
        raise ValueError(f"Algoritmo desconocido: {algoritmo}")

    return algoritmos[algoritmo](datos, rdm)