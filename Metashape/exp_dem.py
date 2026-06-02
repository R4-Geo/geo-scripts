"""
===============================================================================
Script Name: exp_dem.py
Description: Exporta el Modelo Digital de Elevación de cada chunk en formato TIFF.

Author:      Daniel Labraña Trujillo
Date:        2025-03-14
Version:     2.0

Requirements: 
    - Metashape

Usage:
    1. Abrir Metashape y cargar un proyecto
    2. Copiar y pegar el script en la ventana de consola de Metashape
    3. Presionar Enter para ejecutar el script

Notes:
    - El script exporta el Modelo Digital de Elevación (DEM) de cada chunk en formato TIFF
    - El DEM se exporta en la carpeta "DEM" dentro de la carpeta del proyecto
    - La carpeta "DEM" se crea si no existe
    - El script asigna el mismo CRS que el chunk al DEM
    - El script exporta el DEM con tamaño de pixel de 0.25 m
    - El script exporta en formato TIFF
    - El script no genera archivo world
    - El script no recorta el DEM al límite del chunk
    - El script asigna el valor -32767 para los datos sin información
    
===============================================================================
"""

import Metashape
import os

# Obtiene el documento activo
doc = Metashape.app.document

# Obtiene la carpeta del proyecto o usa el directorio actual si el proyecto no se ha guardado
project_folder = os.path.dirname(doc.path) if doc.path else os.getcwd()

# Crea una carpeta "DEM" dentro de la carpeta del proyecto
dem_folder = os.path.join(project_folder, "DEM")
if not os.path.exists(dem_folder):
    os.makedirs(dem_folder)

# Recorre cada chunk y exporta su DEM en formato TIFF dentro de la carpeta DEM
for chunk in doc.chunks:
    dem_filename = os.path.join(dem_folder, f"{chunk.label}.tif")
    
    chunk.exportRaster(
        path=dem_filename,
        image_format=Metashape.ImageFormatTIFF,         # Exporta en TIFF
        resolution_x=0.25,                              # Tamaño del pixel en X (m)
        resolution_y=0.25,                              # Tamaño del pixel en Y (m)
        nodata_value=-32767,                             # Valor para datos sin información
        source_data=Metashape.DataSource.ElevationData, # Exporta DEM (Modelo Digital de Elevación)
        save_world=False                                 # Genera archivo world (opcional)
    )
    
    print(f"DEM del chunk '{chunk.label}' exportado a:\n {dem_filename}")
