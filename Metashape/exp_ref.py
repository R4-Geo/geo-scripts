"""
===============================================================================
Script Name: exp_ref.py
Description: Exporta las referencias de las cámaras en un proyecto de Metashape

Author:      Daniel Labraña Trujillo
Date:        2025-03-03
Version:     1.0

Requirements: 
    - Metashape

Usage:
    Este script de Metashape exporta las coordenadas de referencia de las cámaras 
    en un proyecto a un archivo de texto. Las coordenadas se presentan en formato 
    de tabla con las siguientes columnas:
    
    - Chunk: Nombre del chunk al que pertenece la cámara
    - Camera: Nombre de la cámara
    - X: Coordenada X de la referencia
    - Y: Coordenada Y de la referencia
    - Z: Coordenada Z de la referencia
    
    Para utilizar este script, simplemente cópialo y pégalo en la ventana de
    consola de Metashape y ejecútalo. El script generará un archivo de texto
    con las coordenadas de referencia de las cámaras en el mismo directorio que el
    proyecto actual.

Notes:
    - Este script se puede utilizar para exportar las coordenadas de referencia
      de las cámaras en un proyecto de Metashape para su posterior análisis o
      procesamiento externo.
    
===============================================================================
"""

import Metashape
import csv
import os

# Obtiene el documento activo
doc = Metashape.app.document

# Obtiene el nombre del proyecto (sin extensión) o usa un nombre por defecto si no se ha guardado
if doc.path:
    project_name = os.path.splitext(os.path.basename(doc.path))[0]
else:
    project_name = "untitled_project"

# Define el directorio de salida (usa el directorio del proyecto o el actual si no se ha guardado)
output_folder = os.path.dirname(doc.path) if doc.path else os.getcwd()
txt_filename = os.path.join(output_folder, f"{project_name}.txt")

with open(txt_filename, mode='w', newline='') as txtfile:
    writer = csv.writer(txtfile, delimiter=';')
    
    # Escribe la cabecera: incluye el nombre del chunk, la cámara y las coordenadas de referencia
    writer.writerow(["Chunk", "Camera", "X", "Y", "Z"])
    
    # Recorre todos los chunks y sus cámaras
    for chunk in doc.chunks:
        for cam in chunk.cameras:
            if cam.reference.enabled and cam.reference.location:
                loc = cam.reference.location
                writer.writerow([chunk.label, cam.label, loc.x, loc.y, loc.z])
            else:
                writer.writerow([chunk.label, cam.label, "", "", ""])

print(f"Exportadas todas las referencias de cámaras en:\n {txt_filename}")
