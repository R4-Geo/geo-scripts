# -*- coding: utf-8 -*-
import arcpy
import os
from arcpy import metadata as md

# Función auxiliar para crear nombres válidos para carpetas y archivos
def clean_name(name):
    name = str(name).replace(' ', '_').replace('-', '_')
    return "".join(c for c in name if c.isalnum() or c == '_')

class Toolbox(object):
    def __init__(self):
        """Define el nombre y alias de la caja de herramientas (Toolbox)"""
        self.label = "Herramientas de Geoproceso Territorial"
        self.alias = "GeoTerritorial"
        self.tools = [CorteGDBporComuna]

class CorteGDBporComuna(object):
    def __init__(self):
        """Define las propiedades de la herramienta"""
        self.label = "Cortar Capas por Comuna"
        self.description = (
            "Recorta features de una GDB, Shapefile o Feature Class de entrada según los límites de cada comuna. "
            "Para cada comuna, crea una File Geodatabase (.gdb) separada, copia los metadatos relevantes "
            "(de GDB, Dataset y Feature Class) y opcionalmente exporta los resultados a Shapefiles. "
            "Esta herramienta omite cualquier feature class dentro de un dataset llamado 'Limites'."
        )
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define la interfaz de usuario de la herramienta (los parámetros)"""
        params = []
        # (Esta sección no cambia, los parámetros para el usuario son los mismos)
        param_in_source = arcpy.Parameter(
            displayName="Entrada (GDB, Carpeta con Shapefiles, o Feature Class)",
            name="in_source",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )
        params.append(param_in_source)
        param_comunas = arcpy.Parameter(
            displayName="Capa de Polígonos de Comunas",
            name="comuna_fc",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input"
        )
        param_comunas.filter.list = ["Polygon"]
        params.append(param_comunas)
        param_name_field = arcpy.Parameter(
            displayName="Campo con Nombre de Comuna",
            name="name_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        param_name_field.parameterDependencies = [param_comunas.name]
        param_name_field.filter.list = ['Text']
        params.append(param_name_field)
        param_out_folder = arcpy.Parameter(
            displayName="Carpeta de Salida Principal",
            name="out_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Output"
        )
        params.append(param_out_folder)
        param_export_shp = arcpy.Parameter(
            displayName="Exportar resultados a Shapefiles (adicional a la GDB)",
            name="export_shp",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input"
        )
        param_export_shp.value = True
        params.append(param_export_shp)
        return params

    def execute(self, parameters, messages):
        """Aquí se ejecuta la lógica del script con los parámetros que el usuario ingresó"""
        in_source_path = parameters[0].valueAsText
        comuna_fc = parameters[1].valueAsText
        name_field = parameters[2].valueAsText
        out_folder = parameters[3].valueAsText
        export_shp = parameters[4].value

        arcpy.env.overwriteOutput = True
        messages.addMessage(f"Proceso iniciado. Exportar a SHP: {'Sí' if export_shp else 'No'}")

        desc_source = arcpy.Describe(in_source_path)
        is_gdb = desc_source.dataType == "Workspace" and in_source_path.lower().endswith(".gdb")
        is_folder = desc_source.dataType == "Workspace" and not is_gdb
        is_fc = desc_source.dataType == "FeatureClass"

        if not is_gdb and not is_folder and not is_fc:
             messages.addErrorMessage("La entrada debe ser una File Geodatabase (.gdb), una carpeta (conteniendo Shapefiles) o un Feature Class.")
             raise arcpy.ExecuteError("Tipo de entrada no soportado.")

        if not os.path.isdir(out_folder):
            os.makedirs(out_folder)

        src_gdb_md = None
        if is_gdb:
            try:
                src_gdb_md = md.Metadata(in_source_path)
            except Exception as e:
                messages.addWarningMessage(f"No se pudo leer la metadata de la GDB origen '{in_source_path}'. Error: {e}")

        comuna_layer = "comunas_layer_for_clipping"
        if arcpy.Exists(comuna_layer):
            arcpy.Delete_management(comuna_layer)
        arcpy.MakeFeatureLayer_management(comuna_fc, comuna_layer)

        comuna_names = sorted(list(set(row[0] for row in arcpy.da.SearchCursor(comuna_fc, [name_field]) if row[0])))
        if not comuna_names:
             messages.addErrorMessage(f"No se encontraron valores en el campo '{name_field}'.")
             arcpy.Delete_management(comuna_layer)
             return
        messages.addMessage(f"Se procesarán {len(comuna_names)} comunas únicas.")

        for comuna_name_raw in comuna_names:
            comuna_name_clean = clean_name(comuna_name_raw)
            if not comuna_name_clean:
                messages.addWarningMessage(f"Nombre de comuna '{comuna_name_raw}' inválido, se omitirá.")
                continue

            messages.addMessage(f"\n--- Procesando Comuna: {comuna_name_raw} ---")
            comuna_folder = os.path.join(out_folder, comuna_name_clean)
            if not os.path.isdir(comuna_folder):
                os.makedirs(comuna_folder)

            out_gdb_name = f"{comuna_name_clean}.gdb"
            out_gdb_path = os.path.join(comuna_folder, out_gdb_name)
            if not arcpy.Exists(out_gdb_path):
                arcpy.CreateFileGDB_management(comuna_folder, out_gdb_name)
                if src_gdb_md:
                    try:
                        tgt_gdb_md = md.Metadata(out_gdb_path)
                        tgt_gdb_md.copy(src_gdb_md)
                        tgt_gdb_md.save()
                    except Exception:
                        messages.addWarningMessage(f"No se pudo copiar metadata a la GDB {out_gdb_path}.")

            # Prepara el nombre de la comuna escapando caracteres especiales para SQL
            prepared_name = str(comuna_name_raw).replace('\\', '\\\\').replace("'", "''")
            where_clause = f"{arcpy.AddFieldDelimiters(comuna_fc, name_field)} = '{prepared_name}'"
            arcpy.SelectLayerByAttribute_management(comuna_layer, "NEW_SELECTION", where_clause)

            if int(arcpy.GetCount_management(comuna_layer).getOutput(0)) == 0:
                messages.addWarningMessage(f"No se encontraron geometrías para '{comuna_name_raw}'.")
                continue

            datasets_to_process = []
            features_to_process = {}

            if is_gdb or is_folder:
                arcpy.env.workspace = in_source_path
                if is_gdb:
                    datasets_to_process.extend(arcpy.ListDatasets(feature_type='Feature') or [''])
                else:
                    datasets_to_process.append('')
                for ds in datasets_to_process:
                    fcs_in_ds = arcpy.ListFeatureClasses(feature_dataset=ds if ds else None)
                    if fcs_in_ds:
                        features_to_process[ds] = [os.path.join(in_source_path, ds, fc) if ds else os.path.join(in_source_path, fc) for fc in fcs_in_ds]
            elif is_fc:
                 datasets_to_process.append('')
                 features_to_process[''] = [in_source_path]

            if not features_to_process:
                 messages.addWarningMessage(f"No se encontraron Feature Classes en la entrada: {in_source_path}")
                 continue

            for ds_name in datasets_to_process:
                # <-- NUEVO: Inicio de la regla de exclusión
                # Comprueba si el nombre del dataset (en minúsculas) es "limites"
                if ds_name.lower() == "limites":
                    messages.addMessage(f"Omitiendo el dataset '{ds_name}' y todos sus contenidos según la regla de exclusión.")
                    continue # Salta al siguiente dataset sin procesar este
                # <-- NUEVO: Fin de la regla de exclusión

                if ds_name not in features_to_process: continue
                
                out_ds_path = None
                if ds_name and is_gdb:
                    src_ds_path = os.path.join(in_source_path, ds_name)
                    out_ds_path = os.path.join(out_gdb_path, ds_name)
                    if not arcpy.Exists(out_ds_path):
                        sr = arcpy.Describe(src_ds_path).spatialReference
                        arcpy.CreateFeatureDataset_management(out_gdb_path, ds_name, sr)
                        try:
                            src_ds_md = md.Metadata(src_ds_path)
                            tgt_ds_md = md.Metadata(out_ds_path)
                            tgt_ds_md.copy(src_ds_md)
                            tgt_ds_md.save()
                        except Exception:
                            messages.addWarningMessage(f"No se pudo copiar metadata al dataset {out_ds_path}.")

                shp_folder_path = None
                if export_shp:
                    shp_folder_path = os.path.join(comuna_folder, ds_name) if ds_name else comuna_folder
                    if not os.path.isdir(shp_folder_path): os.makedirs(shp_folder_path)

                for in_fc_path in features_to_process[ds_name]:
                    fc_name = arcpy.Describe(in_fc_path).baseName
                    messages.addMessage(f"  Procesando Feature Class: {fc_name}")
                    out_fc_gdb_path = os.path.join(out_ds_path or out_gdb_path, fc_name)
                    try:
                        arcpy.Clip_analysis(in_fc_path, comuna_layer, out_fc_gdb_path)
                        if int(arcpy.GetCount_management(out_fc_gdb_path).getOutput(0)) == 0:
                            messages.addWarningMessage(f"    El resultado del clip para {fc_name} está vacío. Se omite.")
                            arcpy.Delete_management(out_fc_gdb_path)
                            continue

                        try:
                            src_fc_md = md.Metadata(in_fc_path)
                            tgt_fc_md = md.Metadata(out_fc_gdb_path)
                            tgt_fc_md.copy(src_fc_md)
                            tgt_fc_md.save()
                        except Exception:
                            messages.addWarningMessage(f"    No se pudo copiar metadata a {out_fc_gdb_path}.")

                        if export_shp and shp_folder_path:
                            shp_name_base = fc_name[:9]
                            shp_out_path = os.path.join(shp_folder_path, f"{shp_name_base}.shp")
                            arcpy.CopyFeatures_management(out_fc_gdb_path, shp_out_path)
                            try:
                                src_md_for_shp = md.Metadata(out_fc_gdb_path)
                                tgt_shp_md = md.Metadata(shp_out_path)
                                tgt_shp_md.copy(src_md_for_shp)
                                tgt_shp_md.save()
                            except Exception:
                                messages.addWarningMessage(f"    No se pudo copiar metadata al Shapefile {shp_out_path}.")
                    except arcpy.ExecuteError:
                        messages.addErrorMessage(f"  Error al procesar el Feature Class {fc_name}: {arcpy.GetMessages(2)}")
                    except Exception as e:
                        messages.addErrorMessage(f"  Error inesperado procesando {fc_name}: {e}")

            arcpy.SelectLayerByAttribute_management(comuna_layer, "CLEAR_SELECTION")

        arcpy.Delete_management(comuna_layer)
        messages.addMessage("\nProceso completado.")