import arcpy
import os

# Entradas
cutlines = r"D:\RASTER4\1193 SURVEY CONTROL SYSTEM\Orthoengine\vector_cutlines.shp"  # Shapefile con polígonos
campo_match = "ImageSourc"  # Campo que contiene el nombre del raster sin extensión
carpeta_rasters = r"D:\RASTER4\1193 SURVEY CONTROL SYSTEM\Export_Pansharpen\Mosaicos_Trazado_Sur"  # Carpeta con los .tif originales
carpeta_salida = r"D:\RASTER4\1193 SURVEY CONTROL SYSTEM\Export_Pansharpen\Mosaicos_Trazado_Sur\Recortados"  # Carpeta de salida

# Asegurarse de que las extensiones estén activadas
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# Leer los valores únicos del shapefile
with arcpy.da.SearchCursor(cutlines, [campo_match, "SHAPE@"]) as cursor:
    for row in cursor:
        nombre_raster = row[0]
        geometria = row[1]

        ruta_raster = os.path.join(carpeta_rasters, nombre_raster + ".tif")
        salida_raster = os.path.join(carpeta_salida, nombre_raster + "_recortado.tif")

        if os.path.exists(ruta_raster):
            print(f"Cortando {ruta_raster} con su polígono asociado...")

            # Crear un feature layer temporal con solo este polígono
            where_clause = f"{campo_match} = '{nombre_raster}'"
            arcpy.MakeFeatureLayer_management(cutlines, "corte_temp", where_clause)

            # Ejecutar el clip (ExtractByMask)
            out_extract = arcpy.sa.ExtractByMask(ruta_raster, "corte_temp")
            out_extract.save(salida_raster)

            # Eliminar capa temporal
            arcpy.Delete_management("corte_temp")

        else:
            print(f"Raster no encontrado: {ruta_raster}")

print("Proceso de recorte completado.")