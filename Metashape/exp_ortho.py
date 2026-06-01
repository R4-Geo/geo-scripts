"""
===============================================================================
Script Name: exp_ortho.py
Description: Exporta los ortomosaicos de cada chunk del proyecto

Author:      Daniel Labraña Trujillo
Date:        2025-03-14
Version:     1.0

Requirements: 
    - Metashape

Usage:
    1. Abre Metashape y carga un proyecto
    2. Copia y pega el script en la ventana de consola de Metashape
    3. Presiona Enter para ejecutar el script

Notes:
    - El script exporta los ortomosaicos de cada chunk en formato TIFF
    - El script exporta en la carpeta definida por el usuario
    - El script asigna el mismo CRS que el chunk al ortomosaico
    - El script asigna el fondo blanco por defecto
    - El script pregunta por el tamaño del pixel
    - El script pregunta por la generación de overviews (pirámides)
    - El script pregunta por el recorte al área o límite definido
    - El script pregunta por guardar el canal alfa
    - El script pregunta por generar el archivo world (TFW)
    
===============================================================================
"""

import Metashape
import os

# Solicita al usuario los parámetros mediante diálogos
ortho_folder = Metashape.app.getExistingDirectory("Ingrese carpeta de salida")
pixel_size = Metashape.app.getFloat("Ingrese el tamaño del pixel (m):", 0.05)
jpeg_quality = Metashape.app.getInt("Ingrese la calidad JPEG (0-100):", 90)
generate_overviews = Metashape.app.getBool("¿Generar TIFF overviews?")
clip_to_boundary = Metashape.app.getBool("¿Recortar al área o límite definido?")
save_alpha = Metashape.app.getBool("¿Guardar canal alfa?")
save_world = Metashape.app.getBool("¿Generar archivo world?")

# Obtiene el documento activo
doc = Metashape.app.document

# Configura la compresión para TIFF:
compression = Metashape.ImageCompression()
compression.tiff_big       = True
compression.tiff_compression = Metashape.ImageCompression.TiffCompressionJPEG
compression.jpeg_quality   = jpeg_quality
compression.tiff_overviews = generate_overviews

# Recorre cada chunk y exporta su ortomosaico con los parámetros especificados
for chunk in doc.chunks:
    ortho_filename = os.path.join(ortho_folder, f"{chunk.label}.tif")
    
    chunk.exportRaster(
        path=ortho_filename,
        image_format=Metashape.ImageFormatTIFF,         # Exporta en TIFF
        image_compression=compression,                  # Usa la configuración de compresión definida
        resolution_x=pixel_size,                        # Tamaño del pixel en X (m)
        resolution_y=pixel_size,                        # Tamaño del pixel en Y (m)
        white_background=True,                          # Fondo blanco
        clip_to_boundary=clip_to_boundary,              # No recorta al límite del chunk
        source_data=Metashape.DataSource.OrthomosaicData, # Exporta ortomosaico
        save_alpha=save_alpha,                          # Guarda canal alfa según lo especificado
        save_world=save_world                           # No genera archivo world (opcional)
    )
    
    print(f"Ortomosaico del chunk '{chunk.label}' exportado a:\n {ortho_filename}")
