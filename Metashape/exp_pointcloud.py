"""
===============================================================================
Script Name: exp_pointcloud.py
Description: Exporta la Nube de Puntos de cada chunk en formato LAS.

Author:      Daniel Labraña Trujillo
Date:        2025-03-14
Version:     1.0

Requirements: 
    - Metashape

Usage:
    1. Abrir Metashape y cargar un proyecto
    2. Copiar y pegar el script en la ventana de consola de Metashape
    3. Presionar Enter para ejecutar el script

Notes:
    - El script exporta la Nube de Puntos de cada chunk en formato LAS
    - La Nube de Puntos se exporta en la carpeta "NP" dentro de la carpeta del proyecto
    - La carpeta "NP" se crea si no existe
    - El script asigna el mismo CRS que el chunk a la Nube de Puntos
    - El script exporta solo las clases 0 y 2 (Created[Never Classified] y Ground)
    - El script exporta color, normales, clasificación y confianza de los puntos
    - El script no recorta la nube de puntos al límite del chunk
    - El script exporta en formato binario
    
===============================================================================
"""

import Metashape
import os

# Obtiene el documento activo
doc = Metashape.app.document

# Obtiene la carpeta del proyecto o usa el directorio actual si el proyecto no se ha guardado
project_folder = os.path.dirname(doc.path) if doc.path else os.getcwd()

# Crea una carpeta "NP" dentro de la carpeta del proyecto
pointcloud_folder = os.path.join(project_folder, "NP")
if not os.path.exists(pointcloud_folder):
    os.makedirs(pointcloud_folder)

# Recorre cada chunk y exporta su Nube de Puntos en formato LAS dentro de la carpeta NP
for chunk in doc.chunks:
    pointcloud_filename = os.path.join(pointcloud_folder, f"{chunk.label}.las")
    
    chunk.exportPointCloud(
        path=pointcloud_filename,
        source_data=Metashape.DataSource.PointCloudData,  # Exporta Nube de Puntos
        crs=chunk.crs,                                    # Asigna el mismo CRS que el chunk
        classes=[0, 2],                                   # Exporta solo las clases 0 y 2 (Created[Never Classified] y Ground)
        binary=True,                                      # Exporta en formato binario
        save_point_color=True,                            # Exporta color de los puntos
        save_point_normal=True,                           # Exporta normales de los puntos
        save_point_classification=True,                   # Exporta clasificación de los puntos
        save_point_confidence=True,                       # Exporta confianza de los puntos
        clip_to_boundary=False,                           # No recorta la nube de puntos al límite del chunk
        format=Metashape.PointCloudFormatLAS,             # Formato de la nube de puntos en LAS
    )
    
    print(f"Nube de Puntos del chunk '{chunk.label}' exportado a:\n {pointcloud_filename}")
