"""
===============================================================================
Script Name: copiarpegar.py

Description: Este script de Python copia archivos de una carpeta de origen a una
             carpeta de destino basándose en una lista de IDs proporcionada en
             un archivo Excel. El script verifica si los archivos con los IDs
             correspondientes existen en las carpetas de origen y los copia a
             la carpeta de destino. Al final, se muestra un resumen con la cantidad
             de IDs inspeccionados, la cantidad de fotos copiadas y los IDs que no
             se encontraron en las carpetas de origen.

Author:      Daniel Labraña Trujillo
Date:        2025-01-09
Version:     1.0

Requirements: 
    - Python 3.x
    - pandas
    - shutil
    - os
    - Archivo Excel con los IDs a copiar
    - Carpetas de origen y destino

Usage:
    Este script se ejecuta desde la línea de comandos de Python. Se debe proporcionar
    la ruta del archivo Excel con los IDs a copiar y las carpetas de origen y destino.
    Los archivos con los IDs correspondientes se copiarán de las carpetas de origen
    a la carpeta de destino. Al final, se mostrará un resumen con los resultados.
    Es necesario saber que el script se modifica según cada zona a trabajar, y para eso
    se debe modificar la ruta de las carpetas de origen y destino.

Notes:
    - Asegúrese de tener los módulos necesarios instalados (pandas, shutil, os). y que el
    IDE a utilizar sea compatible con Python 3.x y lo asuma como intérprete.
    - El script asume que los archivos a copiar tienen los IDs en sus nombres.
    - Este script se puede personalizar para adaptarse a diferentes estructuras de carpetas
      o formatos de nombres de archivos.
    - El script no sobrescribirá archivos existentes en la carpeta de destino si tienen el
      mismo nombre que los archivos a copiar.
    - Los archivos duplicados en el Excel se eliminarán manteniendo la primera ocurrencia.
    - Los archivos duplicados en las carpetas de origen no se copiarán más de una vez.
    
===============================================================================
"""

import os
import shutil
import pandas as pd # type: ignore

# Ruta del archivo excel, carpetas de origen y destino
destination_folder = r"CARPETA DESTINO"
excel_file = r"RUTA EXCEL.xlsx"

source_folders = [
    r"CARPETA DE ORIGEN 1",
    r"CARPETA DE ORIGEN 2"
]

# Leer el archivo Excel completo (original)
df1 = pd.read_excel(excel_file)

# Leer el archivo Excel con los parámetros específicos
df2 = pd.read_excel(excel_file, usecols="C", skiprows=3, header=None)

# Análisis detallado de duplicados
col_C_name = df1.columns[2]  # La columna C es el índice 2 (0-based)

# Información detallada sobre el DataFrame
print(f"Total de filas en el Excel original: {len(df1)}")
print(f"Total de IDs únicos: {df1[col_C_name].nunique()}")
print(f"Total de duplicados: {len(df1[df1[col_C_name].duplicated(keep=False)])}")

# Mostrar cantidad de veces que aparece cada ID duplicado
duplicados_count = df1[col_C_name].value_counts()
print("\nIDs que aparecen más de una vez:")
print(duplicados_count[duplicados_count > 1])

# Eliminar duplicados manteniendo la primera ocurrencia
df_sin_duplicados = df1.drop_duplicates(subset=col_C_name, keep='first')
print(f"\nTotal de filas después de eliminar duplicados: {len(df_sin_duplicados)}")

# Guardar el nuevo Excel sin duplicados
output_excel = excel_file.replace('.xlsx', '_sin_duplicados.xlsx')
df_sin_duplicados.to_excel(output_excel, index=False)

# Continuar con el resto del código usando df2 para la copia de archivos
id_values = df2.iloc[:, 0]

# Limpiar los datos para eliminar posibles caracteres invisibles o espacios
id_values = id_values.astype(str).str.strip()

# Verificar duplicados
duplicated_id = id_values[id_values.duplicated(keep=False)]
if not duplicated_id.empty:
    print(f"Hay {len(duplicated_id)} elementos duplicados en el Excel")
    print(duplicated_id)
else:
    print("No se encontraron elementos duplicados en el Excel")

# Contadores de elementos de Excel y Fotos copiadas
inspected_elements = 0
copied_photos = 0
not_copied_ids = [] # Lista para almacenar IDs que no se copiaron

# Iterador sobre los ID presentados en el Excel
for file_id in id_values:
    inspected_elements += 1 # Incrementa el contador de elementos de Excel
    file_id_str = str(file_id) # Transforma la columa ID en tipo String
    found = False # Bandera para verificar si se encontró el archivo correspondiente

    # Iterador para buscar en la carpeta de origen
    for source_folder in source_folders:
        for filename in os.listdir(source_folder):

            # Verificar si el ID de la foto existe en la carpeta
            if file_id_str in filename:
                source_file = os.path.join(source_folder, filename)
                destination_file = os.path.join(destination_folder, filename)

                # Copiar el archivo en la carpeta de destino
                shutil.copy(source_file, destination_file)
                copied_photos += 1 # Incrementa el contador de fotos copiadas
                found = True # Se encontró el archivo correspondiente
                print(f"Archivo {filename} copiado a {destination_folder}")
                break # Si encontramos el archivo, no hace falta seguir buscando en otras carpetas

        if found:
            break # Si se encontró en alguna carpeta, salimos del ciclo

    if not found:
        not_copied_ids.append(file_id_str) # Si no se encontró el archivo, agrega el ID a la lista de archivos no copiados

# Imprimir los resultados finales
print("Archivos copiados y pegados.")
print(f"{inspected_elements} ID inspeccionados en Excel.")
print(f"{copied_photos} fotos copiadas en la carpeta destino.")

# Imprimir los IDs que no se copiaron
if not_copied_ids:
    print(f"Los siguientes {len(not_copied_ids)} IDs no se encontraron en las carpetas de origen:")
    print(not_copied_ids)
else:
    print("Todos los IDs fueron copiados correctamente.")
