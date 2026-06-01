# -*- coding: utf-8 -*-
import arcpy
import os
from arcpy import metadata as md

# --- Funciones Auxiliares ---

def _clean_name(name):
    """
    Limpia un nombre para que sea válido como nombre de carpeta o GDB.
    Reemplaza espacios y guiones por guiones bajos y elimina caracteres no alfanuméricos.
    """
    name = str(name).replace(' ', '_').replace('-', '_')
    return "".join(c for c in name if c.isalnum() or c == '_')

def _get_fcs_to_process(source_path):
    """
    Inspecciona la ruta de entrada y devuelve un diccionario organizado 
    de feature classes a procesar.
    Devuelve: {dataset_name: [fc_path, ...]}
    """
    features_to_process = {}
    desc = arcpy.Describe(source_path)
    is_gdb = desc.dataType == "Workspace" and source_path.lower().endswith(".gdb")
    is_folder = desc.dataType == "Workspace" and not is_gdb
    is_fc = desc.dataType == "FeatureClass"

    if not (is_gdb or is_folder or is_fc):
        raise arcpy.ExecuteError("La entrada debe ser una GDB, una carpeta de Shapefiles o un Feature Class.")

    if is_gdb or is_folder:
        arcpy.env.workspace = source_path
        # Para GDB, lista datasets. Para carpetas, trata todo como si estuviera en la raíz.
        datasets = arcpy.ListDatasets(feature_type='Feature') if is_gdb else ['']
        if not datasets and is_gdb: datasets.append('') # Maneja FCs en la raíz de una GDB

        for ds in datasets:
            fcs_in_ds = arcpy.ListFeatureClasses(feature_dataset=ds if ds else None)
            if fcs_in_ds:
                # Construye la ruta completa para cada feature class
                fc_paths = [os.path.join(source_path, ds, fc) if ds else os.path.join(source_path, fc) for fc in fcs_in_ds]
                features_to_process[ds] = fc_paths
    elif is_fc:
        # Si la entrada es un solo FC, lo pone en una estructura compatible
        features_to_process[''] = [source_path]
        
    return features_to_process

# --- Clases de la Python Toolbox ---

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
            "Recorta features de una GDB, Shapefile o Feature Class según los límites de cada comuna. "
            "Crea una GDB por comuna, copia metadatos y opcionalmente exporta a Shapefiles. "
            "Omite cualquier feature class dentro de un dataset llamado 'Limites'."
        )
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define la interfaz de usuario de la herramienta (parámetros)"""
        params = []
        param_in_source = arcpy.Parameter(displayName="Entrada (GDB, Carpeta con Shapefiles, o Feature Class)", name="in_source", datatype="DEWorkspace", parameterType="Required", direction="Input")
        params.append(param_in_source)
        param_comunas = arcpy.Parameter(displayName="Capa de Polígonos de Comunas", name="comuna_fc", datatype="DEFeatureClass", parameterType="Required", direction="Input")
        param_comunas.filter.list = ["Polygon"]
        params.append(param_comunas)
        param_name_field = arcpy.Parameter(displayName="Campo con Nombre de Comuna", name="name_field", datatype="Field", parameterType="Required", direction="Input")
        param_name_field.parameterDependencies = [param_comunas.name]
        param_name_field.filter.list = ['Text']
        params.append(param_name_field)
        param_out_folder = arcpy.Parameter(displayName="Carpeta de Salida Principal", name="out_folder", datatype="DEFolder", parameterType="Required", direction="Output")
        params.append(param_out_folder)
        param_export_shp = arcpy.Parameter(displayName="Exportar resultados a Shapefiles (adicional a la GDB)", name="export_shp", datatype="GPBoolean", parameterType="Optional", direction="Input")
        param_export_shp.value = True
        params.append(param_export_shp)
        return params

    def execute(self, parameters, messages):
        """Lógica principal de ejecución de la herramienta"""
        in_source_path = parameters[0].valueAsText
        comuna_fc = parameters[1].valueAsText
        name_field = parameters[2].valueAsText
        out_folder = parameters[3].valueAsText
        export_shp = parameters[4].value

        arcpy.env.overwriteOutput = True
        messages.addMessage(f"Proceso iniciado. Exportar a SHP: {'Sí' if export_shp else 'No'}")
        
        # Se crea una capa temporal para la selección de comunas
        comuna_layer = "comunas_layer_for_clipping"
        
        try:
            # --- 1. Preparación de Entradas ---
            features_to_process = _get_fcs_to_process(in_source_path)
            if not features_to_process:
                 messages.addWarningMessage(f"No se encontraron Feature Classes para procesar en: {in_source_path}")
                 return

            if not os.path.isdir(out_folder):
                os.makedirs(out_folder)

            # Obtener metadatos de la GDB origen (si aplica)
            src_gdb_md = None
            if in_source_path.lower().endswith(".gdb"):
                try:
                    src_gdb_md = md.Metadata(in_source_path)
                except Exception:
                    messages.addWarningMessage(f"No se pudo leer la metadata de la GDB origen: '{in_source_path}'.")

            arcpy.MakeFeatureLayer_management(comuna_fc, comuna_layer)

            comuna_names = sorted(list(set(row[0] for row in arcpy.da.SearchCursor(comuna_fc, [name_field]) if row[0])))
            if not comuna_names:
                 messages.addErrorMessage(f"No se encontraron valores en el campo de comunas '{name_field}'.")
                 return
            messages.addMessage(f"Se procesarán {len(comuna_names)} comunas únicas.")

            # --- 2. Bucle principal por cada comuna ---
            for comuna_name_raw in comuna_names:
                comuna_name_clean = _clean_name(comuna_name_raw)
                if not comuna_name_clean:
                    messages.addWarningMessage(f"Nombre de comuna '{comuna_name_raw}' inválido, se omitirá.")
                    continue

                messages.addMessage(f"\n--- Procesando Comuna: {comuna_name_raw} ---")
                
                # --- 2.1. Crear estructura de salida para la comuna ---
                comuna_folder = os.path.join(out_folder, comuna_name_clean)
                os.makedirs(comuna_folder, exist_ok=True)

                out_gdb_name = f"{comuna_name_clean}.gdb"
                out_gdb_path = os.path.join(comuna_folder, out_gdb_name)
                if not arcpy.Exists(out_gdb_path):
                    arcpy.CreateFileGDB_management(comuna_folder, out_gdb_name)
                    if src_gdb_md:
                        try:
                            tgt_gdb_md = md.Metadata(out_gdb_path)
                            tgt_gdb_md.copy(src_gdb_md)
                            tgt_gdb_md.save()
                        except Exception: messages.addWarningMessage(f"No se pudo copiar metadata a la GDB {out_gdb_path}.")

                # --- 2.2. Seleccionar la geometría de la comuna actual ---
                # Prepara el nombre de la comuna escapando caracteres especiales para SQL
                prepared_name = str(comuna_name_raw).replace('\\', '\\\\').replace("'", "''")
                where_clause = f"{arcpy.AddFieldDelimiters(comuna_fc, name_field)} = '{prepared_name}'"
                arcpy.SelectLayerByAttribute_management(comuna_layer, "NEW_SELECTION", where_clause)

                # --- 2.3. Bucle por cada dataset y feature class de entrada ---
                for ds_name, fc_paths in features_to_process.items():
                    if ds_name.lower() == "limites":
                        messages.addMessage(f"Omitiendo el dataset '{ds_name}' por regla de exclusión.")
                        continue
                    
                    # Crear dataset correspondiente en la GDB de salida
                    out_ds_path = None
                    if ds_name:
                        out_ds_path = os.path.join(out_gdb_path, ds_name)
                        if not arcpy.Exists(out_ds_path):
                            sr = arcpy.Describe(os.path.join(in_source_path, ds_name)).spatialReference
                            arcpy.CreateFeatureDataset_management(out_gdb_path, ds_name, sr)

                    for in_fc_path in fc_paths:
                        fc_name = os.path.basename(in_fc_path)
                        messages.addMessage(f"  Procesando: {fc_name}")
                        
                        out_fc_gdb_path = os.path.join(out_ds_path or out_gdb_path, arcpy.Describe(in_fc_path).baseName)
                        
                        try:
                            # --- 2.4. Ejecutar el corte (Clip) y copiar metadatos ---
                            arcpy.Clip_analysis(in_fc_path, comuna_layer, out_fc_gdb_path)
                            
                            if int(arcpy.GetCount_management(out_fc_gdb_path).getOutput(0)) == 0:
                                messages.addWarningMessage("    Resultado del clip vacío. Se omite la capa.")
                                arcpy.Delete_management(out_fc_gdb_path)
                                continue
                            
                            # Copiar metadatos del FC origen al FC destino
                            try:
                                src_fc_md = md.Metadata(in_fc_path)
                                tgt_fc_md = md.Metadata(out_fc_gdb_path)
                                tgt_fc_md.copy(src_fc_md)
                                tgt_fc_md.save()
                            except Exception: messages.addWarningMessage(f"    No se pudo copiar metadata a {out_fc_gdb_path}.")

                            # --- 2.5. Exportar a Shapefile si está activado ---
                            if export_shp:
                                shp_folder_path = os.path.join(comuna_folder, ds_name) if ds_name else comuna_folder
                                os.makedirs(shp_folder_path, exist_ok=True)
                                
                                # Usar ValidateTableName para un nombre de SHP seguro y válido
                                shp_name_base = arcpy.ValidateTableName(arcpy.Describe(in_fc_path).baseName, shp_folder_path)
                                shp_out_path = os.path.join(shp_folder_path, f"{shp_name_base}.shp")
                                
                                arcpy.CopyFeatures_management(out_fc_gdb_path, shp_out_path)

                        except arcpy.ExecuteError:
                            messages.addErrorMessage(f"  Error al procesar {fc_name}: {arcpy.GetMessages(2)}")
                        except Exception as e:
                            messages.addErrorMessage(f"  Error inesperado con {fc_name}: {e}")

            arcpy.SelectLayerByAttribute_management(comuna_layer, "CLEAR_SELECTION")

        finally:
            # --- 3. Limpieza final ---
            # Este bloque se ejecuta SIEMPRE, incluso si hay un error, 
            # asegurando que la capa temporal se elimine.
            if arcpy.Exists(comuna_layer):
                arcpy.Delete_management(comuna_layer)
            messages.addMessage("\nProceso completado.")
