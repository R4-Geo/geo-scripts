import arcpy
import numpy as np
import os


def analizar_elevaciones_simple(fc_poligonos_entrada, path_raster_dtm, fc_salida,
                                distancia_buffer_metros, umbral_plataforma_metros):
    """
    Analiza la elevación de polígonos en relación con un anillo circundante.
    Clasifica como 'Plataforma' si la media interna es mayor que la mínima del anillo 
    más un umbral.
    Todas las capas de entrada deben estar en el mismo CRS proyectado con unidades en metros.
    """
    temp_layer_agua_nombre = None  # Inicializar para el bloque finally
    try:
        arcpy.AddMessage("Iniciando análisis de elevación simplificado (v2 corregido)...")
        arcpy.CheckOutExtension("Spatial")

        # --- Configuración del Entorno ---
        dtm_raster = arcpy.Raster(path_raster_dtm)
        arcpy.env.overwriteOutput = True

        # --- Preparar Feature Class de Salida ---
        # output_dir = os.path.dirname(fc_salida) # No se usa directamente
        # output_name = os.path.basename(fc_salida) # No se usa directamente
        arcpy.management.CopyFeatures(fc_poligonos_entrada, fc_salida)

        campos_a_anadir = {
            "MeanElevIn": "DOUBLE",
            "MinElevRg": "DOUBLE",
            "MaxElevRg": "DOUBLE",
            "Clasif": "TEXT"
        }

        for campo, tipo in campos_a_anadir.items():
            if not arcpy.ListFields(fc_salida, campo):
                arcpy.management.AddField(fc_salida, campo, tipo, field_length=50 if tipo == "TEXT" else None)
            else:
                arcpy.AddWarning(f"El campo '{campo}' ya existe en la salida.")

        oid_field_name = arcpy.Describe(fc_poligonos_entrada).OIDFieldName

        temp_layer_agua_nombre = "temp_current_polygon_layer_v2"  # Nombre único
        arcpy.management.MakeFeatureLayer(fc_poligonos_entrada, temp_layer_agua_nombre)

        campos_actualizacion = list(campos_a_anadir.keys())
        # El OIDFieldName para la capa de salida podría ser diferente si es un nuevo FC,
        # pero CopyFeatures usualmente lo preserva para shapefiles.
        # Para ser robusto, podríamos obtener el OID de fc_salida.
        oid_field_salida = arcpy.Describe(fc_salida).OIDFieldName

        with arcpy.da.UpdateCursor(fc_salida, [oid_field_salida] + campos_actualizacion) as cursor_salida:
            for row_salida in cursor_salida:
                oid = row_salida[0]
                # No necesitamos la geometría de row_salida[1] aquí si seleccionamos por OID de la capa original
                feature_id_str = f"OID_{oid}"
                arcpy.AddMessage(f"Procesando polígono {feature_id_str}...")

                # Inicializar valores para la fila actual
                mean_elev_in = np.nan
                min_elev_ring = np.nan
                max_elev_ring = np.nan
                clasificacion = "Error_Desconocido"  # Estado por defecto

                expression = f"{oid_field_name} = {oid}"  # Usar OID de la capa de entrada original
                arcpy.management.SelectLayerByAttribute(temp_layer_agua_nombre, "NEW_SELECTION", expression)

                # Verificar si la selección es válida (1 feature seleccionado)
                count_seleccion = int(arcpy.management.GetCount(temp_layer_agua_nombre)[0])
                if count_seleccion != 1:
                    arcpy.AddWarning(
                        f"  {feature_id_str}: No se pudo seleccionar un único polígono (encontrados: {count_seleccion}). Omitiendo.")
                    clasificacion = "Error_Seleccion_Poligono"
                    # Llenar fila con error y continuar
                    row_salida[1] = clasificacion  # Clasif es el primer campo después del OID en campos_actualizacion
                    row_salida[2] = None
                    row_salida[3] = None
                    row_salida[4] = None
                    cursor_salida.updateRow(row_salida)
                    continue

                current_polygon_fc_ref = temp_layer_agua_nombre

                temp_buffer_fc = f"in_memory/temp_buffer_{oid}"
                temp_anillo_fc = f"in_memory/temp_anillo_{oid}"

                raster_interno = None
                raster_anillo = None

                try:
                    try:
                        raster_interno = arcpy.sa.ExtractByMask(dtm_raster, current_polygon_fc_ref)
                        if raster_interno is not None:
                            array_interno = arcpy.RasterToNumPyArray(raster_interno, nodata_to_value=np.nan)
                            mean_elev_in = np.nanmean(array_interno)
                        else:
                            arcpy.AddWarning(
                                f"  {feature_id_str}: ExtractByMask para polígono interno no produjo ráster.")
                            mean_elev_in = np.nan  # Asegurar que sea NaN
                    except Exception as e_int:
                        arcpy.AddWarning(f"  {feature_id_str}: Error en ExtractByMask (interno) o NumPy: {e_int}")
                        mean_elev_in = np.nan
                    finally:
                        if raster_interno is not None:
                            try:
                                arcpy.management.Delete(raster_interno)
                            except:
                                pass

                    if np.isnan(mean_elev_in):  # Si no se pudo calcular la media interna, no continuar
                        clasificacion = "Error_Media_Interna"
                        raise Exception("No se pudo calcular la media de elevación interna.")

                    arcpy.analysis.Buffer(current_polygon_fc_ref, temp_buffer_fc, f"{distancia_buffer_metros} Meters",
                                          "FULL", "ROUND", "NONE")
                    arcpy.analysis.Erase(temp_buffer_fc, current_polygon_fc_ref, temp_anillo_fc)

                    count_anillo = int(arcpy.management.GetCount(temp_anillo_fc)[0])
                    if count_anillo == 0:
                        arcpy.AddWarning(f"  {feature_id_str}: Anillo resultante de Erase está vacío.")
                        min_elev_ring, max_elev_ring = np.nan, np.nan
                        clasificacion = "Error_Anillo_Vacio"
                    else:
                        try:
                            raster_anillo = arcpy.sa.ExtractByMask(dtm_raster, temp_anillo_fc)
                            if raster_anillo is not None:
                                array_anillo = arcpy.RasterToNumPyArray(raster_anillo, nodata_to_value=np.nan)
                                min_elev_ring = np.nanmin(array_anillo)
                                max_elev_ring = np.nanmax(array_anillo)
                            else:
                                arcpy.AddWarning(f"  {feature_id_str}: ExtractByMask para anillo no produjo ráster.")
                                min_elev_ring, max_elev_ring = np.nan, np.nan
                        except Exception as e_anillo_stats:
                            arcpy.AddWarning(
                                f"  {feature_id_str}: Error en ExtractByMask (anillo) o NumPy: {e_anillo_stats}")
                            min_elev_ring, max_elev_ring = np.nan, np.nan
                        finally:
                            if raster_anillo is not None:
                                try:
                                    arcpy.management.Delete(raster_anillo)
                                except:
                                    pass

                    if np.isnan(
                            min_elev_ring) and clasificacion == "Error_Desconocido":  # Si no se pudo calcular la mínima del anillo
                        clasificacion = "Error_Min_Anillo"
                        # No continuar con la clasificación si min_elev_ring es NaN y no hay otro error
                        if estado_actual_poligono == "No_Procesado":  # 'estado_actual_poligono' no se usa en esta versión, usar 'clasificacion'
                            raise Exception("No se pudo calcular la mínima elevación del anillo.")

                    # Clasificación (solo si no hay errores previos y tenemos los datos necesarios)
                    if clasificacion == "Error_Desconocido":  # Procede solo si no hay errores previos de procesamiento
                        if not np.isnan(mean_elev_in) and not np.isnan(min_elev_ring):
                            if mean_elev_in > (min_elev_ring + umbral_plataforma_metros):
                                clasificacion = "Plataforma"
                            else:
                                clasificacion = "OK"
                        else:  # Si mean_elev_in o min_elev_ring es NaN (y no era un error de anillo vacío)
                            clasificacion = "Datos_Insuficientes"

                except Exception as e_proc:
                    arcpy.AddWarning(f"  Error general procesando {feature_id_str}: {e_proc}")
                    if clasificacion == "Error_Desconocido": clasificacion = "Error_Procesamiento"
                    mean_elev_in, min_elev_ring, max_elev_ring = np.nan, np.nan, np.nan  # Asegurar nulos en error

                finally:
                    for temp_fc in [temp_buffer_fc, temp_anillo_fc]:
                        if arcpy.Exists(temp_fc):
                            try:
                                arcpy.management.Delete(temp_fc)
                            except:
                                pass
                    arcpy.management.SelectLayerByAttribute(temp_layer_agua_nombre, "CLEAR_SELECTION")

                # Actualizar la fila en la feature class de salida
                # Los índices ahora son relativos a campos_actualizacion
                # OID es row_salida[0]
                # campos_actualizacion = ["MeanElevIn", "MinElevRg", "MaxElevRg", "Clasif"]
                # row_salida[1] = MeanElevIn, row_salida[2] = MinElevRg, etc.
                # No, el cursor es [oid_field_salida] + campos_actualizacion
                # Entonces, Clasif está en row_salida[4] si campos_actualizacion tiene 4 elementos.
                # Mejor usar los nombres de los campos para encontrar el índice.

                idx_clasif = campos_actualizacion.index("Clasif") + 1  # +1 porque el OID está en el índice 0 del cursor
                idx_mean_in = campos_actualizacion.index("MeanElevIn") + 1
                idx_min_rg = campos_actualizacion.index("MinElevRg") + 1
                idx_max_rg = campos_actualizacion.index("MaxElevRg") + 1

                row_salida[idx_clasif] = clasificacion
                row_salida[idx_mean_in] = None if np.isnan(mean_elev_in) else float(mean_elev_in)
                row_salida[idx_min_rg] = None if np.isnan(min_elev_ring) else float(min_elev_ring)
                row_salida[idx_max_rg] = None if np.isnan(max_elev_ring) else float(max_elev_ring)
                cursor_salida.updateRow(row_salida)

        arcpy.AddMessage("Análisis simplificado (v2 corregido) completado.")

    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
    except Exception as e:
        arcpy.AddError(f"Error no controlado: {str(e)}")
    finally:
        # Eliminar la capa temporal si fue creada
        if temp_layer_agua_nombre is not None and arcpy.Exists(temp_layer_agua_nombre):
            try:
                arcpy.management.Delete(temp_layer_agua_nombre)
            except Exception as e_del_layer:
                arcpy.AddWarning(f"No se pudo eliminar la capa temporal '{temp_layer_agua_nombre}': {e_del_layer}")

        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckInExtension("Spatial")


# --- Ejemplo de Uso ---
if __name__ == '__main__':
    fc_poligonos_entrada_main = r"archivo.shp"
    path_dtm_entrada_main = r"archivo.tif"
    fc_salida_main = r"archivo.shp"

    distancia_buffer = 20.0
    umbral_plataforma = 0.3

    output_dir_general_main = os.path.dirname(fc_salida_main)
    if not os.path.exists(output_dir_general_main):
        os.makedirs(output_dir_general_main)

    analizar_elevaciones_simple(
        fc_poligonos_entrada_main,
        path_dtm_entrada_main,
        fc_salida_main,
        distancia_buffer,
        umbral_plataforma
    )
    arcpy.AddMessage(f"Proceso finalizado. Resultados en: {fc_salida_main}")

