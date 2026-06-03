# -*- coding: utf-8 -*-

import processing # Import processing principal
import os
import tempfile
import shutil
from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsProject,
    QgsField,
    QgsFeature,
    QgsVectorFileWriter,
    QgsProcessingException,
    QgsWkbTypes,
    QgsApplication
)
# IMPORTACIÓN CORRECTA PARA TEMP FOLDER:
from qgis.processing import QgsProcessingUtils
from PyQt5.QtCore import QVariant

# --- Configuración de Entradas ---
shapefile_path = r"ruta" # CAMBIAR ESTA RUTA
raster_path = r"ruta"      # CAMBIAR ESTA RUTA
buffer_distance = 20.0
elevation_threshold = 0.3

# --- Crear Directorio Temporal ---
temp_dir = os.path.join(QgsProcessingUtils.tempFolder(), "zonal_analysis_temp")
if os.path.exists(temp_dir):
     shutil.rmtree(temp_dir)
os.makedirs(temp_dir, exist_ok=True)
print(f"Usando directorio temporal: {temp_dir}")

# --- Carga de Capas ---
print("Cargando capas...")
vector_layer = QgsVectorLayer(shapefile_path, "Poligonos Originales", "ogr")
raster_layer = QgsRasterLayer(raster_path, "DEM")

if not vector_layer.isValid():
    print(f"Error: No se pudo cargar la capa vectorial: {shapefile_path}")
    shutil.rmtree(temp_dir) # Limpiar
    exit()
elif not raster_layer.isValid():
    print(f"Error: No se pudo cargar la capa raster: {raster_path}")
    shutil.rmtree(temp_dir) # Limpiar
    exit()
else:
    print("Capas cargadas correctamente.")
    print(f"  CRS Vector: {vector_layer.crs().authid()} | CRS Raster: {raster_layer.crs().authid()}")
    if vector_layer.crs() != raster_layer.crs():
        print("  ADVERTENCIA: Los CRS son diferentes.")

    if not QgsProject.instance().mapLayersByName("Poligonos Originales"):
         QgsProject.instance().addMapLayer(vector_layer)
    if not QgsProject.instance().mapLayersByName("DEM"):
        QgsProject.instance().addMapLayer(raster_layer)

    # --- Preparación de la Capa Vectorial ---
    provider = vector_layer.dataProvider()
    field_name = "Clasificacion"
    class_field_idx = vector_layer.fields().indexFromName(field_name)

    if class_field_idx == -1:
        print(f"Añadiendo campo '{field_name}'...")
        field = QgsField(field_name, QVariant.String, len=20)
        provider.addAttributes([field])
        vector_layer.updateFields()
        class_field_idx = vector_layer.fields().indexFromName(field_name)
        if class_field_idx != -1:
             print(f"Campo '{field_name}' añadido correctamente (Índice: {class_field_idx}).")
        else:
             print(f"ERROR CRÍTICO: No se pudo añadir/encontrar índice del campo '{field_name}'.")
             shutil.rmtree(temp_dir) # Limpiar
             exit()
    else:
        print(f"El campo '{field_name}' ya existe (Índice: {class_field_idx}).")

    # Empezar la edición
    vector_layer.startEditing()
    print("Iniciando procesamiento por polígono...")

    feature_count = vector_layer.featureCount()
    processed_count = 0
    success_count = 0
    error_count = 0

    # --- Iteración y Procesamiento ---
    try: # Envolver el bucle principal en try/finally para asegurar limpieza
        for feature in vector_layer.getFeatures():
            feature_id = feature.id()
            processed_count += 1
            print(f"\nProcesando polígono ID: {feature_id} ({processed_count}/{feature_count})")

            current_classification = "Error_Process" # Default for this feature

            # Definir rutas temporales para esta feature
            temp_poly_path = os.path.join(temp_dir, f'temp_poly_{feature_id}.gpkg')
            buffer_path = os.path.join(temp_dir, f'buffer_{feature_id}.gpkg')
            ring_path = os.path.join(temp_dir, f'ring_{feature_id}.gpkg')

            geom = feature.geometry()
            if not geom or geom.isEmpty() or not geom.isGeosValid():
                print(f"  Advertencia: Geometría inválida/vacía ID {feature_id}. Saltando...")
                current_classification = "Error_Geom"
                if class_field_idx != -1:
                     vector_layer.changeAttributeValue(feature_id, class_field_idx, current_classification)
                error_count += 1
                continue

            # 1. Guardar polígono actual en archivo temporal GPKG
            wkb_type = QgsWkbTypes.displayString(geom.wkbType())
            temp_layer_type = "Polygon"
            if 'MultiPolygon' in wkb_type: temp_layer_type = "MultiPolygon"

            # Crear capa en memoria primero para facilitar la escritura
            temp_mem_layer = QgsVectorLayer(f"{temp_layer_type}?crs={vector_layer.crs().authid()}",
                                             f"temp_mem_{feature_id}", "memory")
            temp_mem_provider = temp_mem_layer.dataProvider()
            # Usar los campos de la capa original para que ZonalStats funcione
            temp_mem_provider.addAttributes(vector_layer.fields())
            temp_mem_layer.updateFields()
            temp_feature_copy = QgsFeature(feature) # Crear copia
            temp_mem_provider.addFeatures([temp_feature_copy])

            # Escribir a GPKG
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "GPKG"
            transform_context = QgsProject.instance().transformContext()
            error_write = QgsVectorFileWriter.writeAsVectorFormatV3(temp_mem_layer,
                                                                    temp_poly_path,
                                                                    transform_context,
                                                                    options)
            del temp_mem_layer # Liberar capa en memoria
            if error_write[0] != QgsVectorFileWriter.NoError:
                 print(f"  Error guardando polígono temporal en {temp_poly_path}: {error_write}. Saltando...")
                 current_classification = "Error_WriteTemp"
                 if class_field_idx != -1:
                     vector_layer.changeAttributeValue(feature_id, class_field_idx, current_classification)
                 error_count += 1
                 continue

            # 2. Zonal Statistics para polígono original (promedio) - Lee y modifica el GPKG
            print(f"  Calculando stats (original) en {os.path.basename(temp_poly_path)}...")
            stats_prefix_orig = 'orig_'
            avg_elev = None
            mean_field_name = stats_prefix_orig + 'mean'
            try:
                result_orig = processing.run("native:zonalstatisticsfb", {
                    'INPUT': temp_poly_path,
                    'INPUT_RASTER': raster_layer,
                    'RASTER_BAND': 1,
                    'COLUMN_PREFIX': stats_prefix_orig,
                    'STATISTICS': [2], # Mean
                    'OUTPUT': 'TEMPORARY_OUTPUT' # Modifica el INPUT GPKG
                })

                # Recargar la capa desde el GPKG modificado para leer el resultado
                temp_poly_layer_updated = QgsVectorLayer(temp_poly_path, f"poly_{feature_id}_stats", "ogr")
                if not temp_poly_layer_updated.isValid():
                     print(f"  Error: No se pudo recargar {temp_poly_path} después de Zonal Stats.")
                else:
                    mean_field_index = temp_poly_layer_updated.fields().indexFromName(mean_field_name)
                    if mean_field_index == -1:
                        print(f"  Advertencia: Zonal Stats (original) no añadió campo '{mean_field_name}' a {os.path.basename(temp_poly_path)}.")
                    else:
                        updated_feat = next(temp_poly_layer_updated.getFeatures())
                        avg_elev = updated_feat.attribute(mean_field_index)
                        if avg_elev is not None: print(f"    -> Elevación promedio: {avg_elev}")
                        else: print(f"    -> Elevación promedio: NULL")
                del temp_poly_layer_updated # Liberar

            except QgsProcessingException as e:
                print(f"  Error en Zonal Statistics (original) para {feature_id}: {e}")

            # 3. Crear Buffer (desde el GPKG temporal, salida a nuevo GPKG)
            print(f"  Creando buffer -> {os.path.basename(buffer_path)}...")
            buffer_layer_ok = False
            try:
                buffer_result = processing.run("native:buffer", {
                    'INPUT': temp_poly_path, # Usa el GPKG como entrada
                    'DISTANCE': buffer_distance,
                    'SEGMENTS': 8, 'OUTPUT': buffer_path # Salida a archivo GPKG
                })
                # Verificar si el archivo de salida existe y tiene contenido
                if os.path.exists(buffer_path):
                    buffer_check_layer = QgsVectorLayer(buffer_path, "buffer_check", "ogr")
                    if buffer_check_layer.isValid() and buffer_check_layer.featureCount() > 0:
                         print("    -> Buffer creado.")
                         buffer_layer_ok = True
                    else: print(f"  Error: Archivo buffer {os.path.basename(buffer_path)} vacío o inválido.")
                    del buffer_check_layer
                else: print(f"  Error: Archivo buffer {os.path.basename(buffer_path)} no fue creado.")
            except QgsProcessingException as e:
                print(f"  Error creando buffer para {feature_id}: {e}")

            # 4. Crear Anillo (Diferencia) (usa GPKG buffer y GPKG poly, salida a nuevo GPKG)
            ring_layer_ok = False
            if buffer_layer_ok:
                print(f"  Creando anillo -> {os.path.basename(ring_path)}...")
                try:
                    difference_result = processing.run("native:difference", {
                        'INPUT': buffer_path,    # GPKG del buffer
                        'OVERLAY': temp_poly_path, # GPKG del polígono original
                        'OUTPUT': ring_path       # Salida a archivo GPKG
                    })
                    # Verificar si el archivo de salida existe y tiene contenido
                    if os.path.exists(ring_path):
                         ring_check_layer = QgsVectorLayer(ring_path, "ring_check", "ogr")
                         if ring_check_layer.isValid() and ring_check_layer.featureCount() > 0:
                             print("    -> Anillo creado.")
                             ring_layer_ok = True
                         else: print(f"  Advertencia: Archivo anillo {os.path.basename(ring_path)} vacío o inválido.")
                         del ring_check_layer
                    else: print(f"  Advertencia: Archivo anillo {os.path.basename(ring_path)} no fue creado.")
                except QgsProcessingException as e:
                    print(f"  Error creando anillo (diferencia) para {feature_id}: {e}")

            # 5. Zonal Statistics para el anillo (lee y modifica el GPKG del anillo)
            min_ring_elev = None
            max_ring_elev = None
            min_field_name = 'ring_min'
            max_field_name = 'ring_max'
            if ring_layer_ok:
                print(f"  Calculando stats (anillo) en {os.path.basename(ring_path)}...")
                stats_prefix_ring = 'ring_'
                try:
                    result_ring = processing.run("native:zonalstatisticsfb", {
                        'INPUT': ring_path,
                        'INPUT_RASTER': raster_layer,
                        'RASTER_BAND': 1,
                        'COLUMN_PREFIX': stats_prefix_ring,
                        'STATISTICS': [6, 7], # Min, Max
                        'OUTPUT': 'TEMPORARY_OUTPUT' # Modifica el INPUT GPKG
                    })

                    # Recargar la capa desde el GPKG modificado
                    temp_ring_layer_updated = QgsVectorLayer(ring_path, f"ring_{feature_id}_stats", "ogr")
                    if not temp_ring_layer_updated.isValid():
                         print(f"  Error: No se pudo recargar {ring_path} después de Zonal Stats.")
                    else:
                        min_field_index = temp_ring_layer_updated.fields().indexFromName(min_field_name)
                        max_field_index = temp_ring_layer_updated.fields().indexFromName(max_field_name)

                        if min_field_index == -1 or max_field_index == -1:
                            print(f"  Advertencia: Zonal Stats (anillo) no añadió campos a {os.path.basename(ring_path)}.")
                        else:
                            updated_ring_feat = next(temp_ring_layer_updated.getFeatures())
                            min_ring_elev = updated_ring_feat.attribute(min_field_index)
                            max_ring_elev = updated_ring_feat.attribute(max_field_index)
                            if min_ring_elev is not None: print(f"    -> Elevación mínima: {min_ring_elev}")
                            else: print(f"    -> Elevación mínima: NULL")
                            if max_ring_elev is not None: print(f"    -> Elevación máxima: {max_ring_elev}")
                            else: print(f"    -> Elevación máxima: NULL")
                    del temp_ring_layer_updated # Liberar

                except QgsProcessingException as e:
                    print(f"  Error en Zonal Statistics (anillo) para {feature_id}: {e}")
                    # Dejar min/max como None

            # 6. Clasificación
            print("  Clasificando...")
            if isinstance(avg_elev, (int, float)) and isinstance(min_ring_elev, (int, float)):
                if avg_elev > (min_ring_elev + elevation_threshold):
                    current_classification = "Plataforma"
                else:
                    current_classification = "OK"
                print(f"    -> Resultado: {current_classification}")
                success_count += 1
            elif not isinstance(avg_elev, (int, float)):
                print(f"    -> No se pudo clasificar: Valor inválido/ausente para elevación promedio ({avg_elev}).")
                current_classification = "Error_Avg"
                error_count += 1
            elif not isinstance(min_ring_elev, (int, float)):
                print(f"    -> No se pudo clasificar: Valor inválido/ausente para elevación mínima anillo ({min_ring_elev}).")
                current_classification = "Error_RingMin"
                error_count += 1
            else:
                print(f"    -> No se pudo clasificar: Condición inesperada.")
                current_classification = "Error_Unknown"
                error_count += 1

            # 7. Actualizar atributo en la capa original
            if class_field_idx != -1:
                vector_layer.changeAttributeValue(feature_id, class_field_idx, current_classification)

        # --- Fin del Bucle ---

    except Exception as e:
         print(f"\nERROR INESPERADO DURANTE EL PROCESAMIENTO DEL BUCLE: {e}")
         print("Intentando guardar cambios parciales y limpiar...")
         # Marcar el error count para reflejar que el bucle se interrumpió
         error_count = feature_count - success_count
         # No podemos continuar el bucle, así que salimos al bloque finally

    finally:
        # --- Finalizar Edición (dentro de finally para intentar guardar) ---
        print(f"\nProcesamiento del bucle terminado. Intentando guardar cambios ({success_count} éxitos, {error_count} errores)...")
        try:
            if vector_layer.isEditable(): # Solo intentar guardar si está en modo edición
                if not vector_layer.commitChanges():
                    print("Error al guardar los cambios:")
                    commit_errors = vector_layer.commitErrors()
                    if commit_errors: print("\n".join(commit_errors))
                    else: print("(No hay detalles de error disponibles)")
                    print("Revirtiendo cambios...")
                    vector_layer.rollBack()
                else:
                    print("Cambios guardados exitosamente.")
            else:
                 print("La capa no estaba en modo edición al finalizar.")
        except Exception as e:
            print(f"Excepción al intentar finalizar edición: {e}")
            if vector_layer.isEditable(): vector_layer.rollBack()

        # --- Limpiar Directorio Temporal ---
        print(f"Limpiando directorio temporal: {temp_dir}")
        try:
             shutil.rmtree(temp_dir)
             print("Directorio temporal eliminado.")
        except Exception as e:
             print(f"Error al eliminar directorio temporal: {e}")

print(f"\n--- Proceso Completado ({success_count} éxitos, {error_count} errores de {feature_count} polígonos) ---")
