# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Script_Edificaciones.py
# Descripción: Construye edificaciones a partir de capas de entrada
# Autor: Raster4 (modificado por Daniel Labraña)
# Fecha de edición: 13/05/2025
# ---------------------------------------------------------------------------

import arcpy
import os
import sys # Importado para sys.exit() en caso de error crítico de validación
from datetime import date

# -------------------------------
# Obtener parámetros del usuario
fc_Esqueleto = arcpy.GetParameterAsText(0)
fc_Predio = arcpy.GetParameterAsText(1)
fc_Puntos_Edificacion = arcpy.GetParameterAsText(2)
gdb_destino = arcpy.GetParameterAsText(3)

# -------------------------------
# Validaciones básicas y mejoradas para gdb_destino

arcpy.AddMessage(f"Validando geodatabase de destino: {gdb_destino}")

if not gdb_destino:
    arcpy.AddError("El parámetro de geodatabase de destino no ha sido proporcionado.")
    sys.exit() # Salir si no hay GDB de destino

if not arcpy.Exists(gdb_destino):
    arcpy.AddError(f"La geodatabase de destino especificada no existe: {gdb_destino}")
    sys.exit() # Salir si la GDB no existe

try:
    desc_gdb = arcpy.Describe(gdb_destino)
    if desc_gdb.dataType != "Workspace":
        arcpy.AddError(f"La ruta de destino '{gdb_destino}' no es un Espacio de Trabajo (Workspace) válido.")
        sys.exit()
    # workspaceType puede ser LocalDatabase (FileGDB, MobileGDB) o RemoteDatabase (Enterprise GDB)
    if desc_gdb.workspaceType not in ["LocalDatabase", "RemoteDatabase"]:
        arcpy.AddError(f"El espacio de trabajo '{gdb_destino}' no es una Geodatabase reconocida (File GDB, Mobile GDB o Enterprise GDB). Tipo detectado: {desc_gdb.workspaceType}")
        sys.exit()
    arcpy.AddMessage(f"Geodatabase de destino '{gdb_destino}' validada como {desc_gdb.workspaceType}.")
except arcpy.ExecuteError as e:
    arcpy.AddError(f"Error de ArcPy al describir la geodatabase de destino: {gdb_destino}. Mensaje: {str(e)}")
    sys.exit()
except Exception as e:
    arcpy.AddError(f"Error inesperado al describir la geodatabase de destino: {gdb_destino}. Error: {str(e)}")
    sys.exit()

output_fc_name = "Edificacion"
output_fc = os.path.join(gdb_destino, output_fc_name)

# Si ya existe la capa de salida, eliminarla
# Esta sección elimina la CLASE DE ENTIDAD 'Edificacion', NO la GEODATABASE.
if arcpy.Exists(output_fc):
    arcpy.AddMessage(f"La capa '{output_fc_name}' ya existe en '{gdb_destino}'. Se eliminará antes de crear una nueva.")
    try:
        arcpy.Delete_management(output_fc)
        arcpy.AddMessage(f"Capa '{output_fc_name}' eliminada exitosamente.")
    except arcpy.ExecuteError as e:
        arcpy.AddError(f"Error de ArcPy al eliminar la capa existente '{output_fc_name}'. Mensaje: {str(e)}")
        sys.exit()
    except Exception as e:
        arcpy.AddError(f"Error inesperado al eliminar la capa existente '{output_fc_name}'. Error: {str(e)}")
        sys.exit()

# -------------------------------
# PROCESAMIENTO

# 1. Crear polígono de edificación
arcpy.AddMessage(f"Creando polígonos de edificación en: {output_fc}")
try:
    # FeatureToPolygon_management devuelve un objeto Result, no la ruta a la capa directamente para MakeFeatureLayer
    # Usamos output_fc que ya tiene la ruta de salida.
    arcpy.FeatureToPolygon_management(
        in_features=[fc_Esqueleto, fc_Predio],
        out_feature_class=output_fc,
        cluster_tolerance="", # Se recomienda especificar una tolerancia o dejarla vacía para usar la predeterminada
        attributes="ATTRIBUTES",
        label_features=""
    )
    arcpy.AddMessage("Polígonos de edificación creados.")
except arcpy.ExecuteError as e:
    arcpy.AddError(f"Error de ArcPy durante FeatureToPolygon. Mensaje: {str(e)}")
    sys.exit()
except Exception as e:
    arcpy.AddError(f"Error inesperado durante FeatureToPolygon. Error: {str(e)}")
    sys.exit()


# 2. Seleccionar y eliminar polígonos que no contienen puntos de edificación
arcpy.AddMessage("Eliminando polígonos sin puntos de edificación...")

# Crear capa temporal de la nueva capa de edificación
layer_name = "edificacion_temp_layer"
try:
    if arcpy.Exists(output_fc): # Asegurarse que la capa base existe antes de crear la capa en memoria
        arcpy.MakeFeatureLayer_management(output_fc, layer_name)
        arcpy.AddMessage(f"Capa temporal '{layer_name}' creada.")

        # Selección por ubicación (INVERT = selecciona los que NO contienen puntos)
        arcpy.SelectLayerByLocation_management(
            in_layer=layer_name,
            overlap_type="CONTAINS",
            select_features=fc_Puntos_Edificacion,
            selection_type="NEW_SELECTION",
            invert_spatial_relationship="INVERT"
        )
        
        # Verificar si hay algo seleccionado para eliminar
        count_selected = int(arcpy.GetCount_management(layer_name)[0])
        if count_selected > 0:
            arcpy.AddMessage(f"Se eliminarán {count_selected} polígonos que no contienen puntos de edificación.")
            arcpy.DeleteFeatures_management(layer_name)
            arcpy.AddMessage("Polígonos no deseados eliminados.")
        else:
            arcpy.AddMessage("No se encontraron polígonos para eliminar (todos contienen puntos de edificación o la capa está vacía).")
        
        # Limpiar la capa temporal (opcional, pero buena práctica)
        arcpy.Delete_management(layer_name)

    else:
        arcpy.AddWarning(f"La capa de salida '{output_fc}' no se encontró después de la creación. Se omite el paso de eliminación de polígonos.")

except arcpy.ExecuteError as e:
    arcpy.AddError(f"Error de ArcPy durante la selección/eliminación de polígonos. Mensaje: {str(e)}")
    # No necesariamente salir, el resultado principal puede estar ya creado.
except Exception as e:
    arcpy.AddError(f"Error inesperado durante la selección/eliminación de polígonos. Error: {str(e)}")

arcpy.AddMessage("Proceso completado exitosamente.")