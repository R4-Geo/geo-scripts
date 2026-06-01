# -*- coding: utf-8 -*-
import arcpy
import os
from collections import defaultdict

class Toolbox(object):
    def __init__(self):
        """Define la caja de herramientas (tooltbox) y sus propiedades"""
        self.label = "Herramientas de Unificación de GDB"
        self.alias = "UnificarGDBs"

        # Listado de herramientas de la caja
        self.tools = [UnificarGDBs]

class UnificarGDBs(object):
    def __init__(self):
        """Define la herramienta y sus propiedades"""
        self.label = "Unificar Múltiples GDBs"
        self.description = (
            "Unifica el contenido de múltiples Geodatabases de Archivo (.gdb) en una "
            "sola GDB de salida. La herramienta fusiona feature classes con el mismo "
            "nombre, preserva la estructura de datasets y copia los metadatos "
            "del primer feature class de origen encontrado."
        )
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define la interfaz de usuario de la herramienta (parámetros)"""
        
        # Parámetro 0: GDBs de origen (MODIFICADO)
        param_origen = arcpy.Parameter(
            displayName="Geodatabases de Origen",
            name="in_gdbs",
            datatype="DEWorkspace", # Cambio de DEFolder a DEWorkspace
            parameterType="Required",
            direction="Input",
            multiValue=True # Permite seleccionar múltiples GDBs
        )
        param_origen.filter.list = ["FileGDB"] # Filtro para mostrar solo File GDBs

        # Parámetro 1: GDB de salida
        param_salida = arcpy.Parameter(
            displayName="Geodatabase de Salida",
            name="out_gdb",
            datatype="DEFile",
            parameterType="Required",
            direction="Output"
        )
        param_salida.filter.list = ["gdb"]

        params = [param_origen, param_salida]
        return params

    def isLicensed(self):
        """Establece si la herramienta está licenciada para correr"""
        return True

    def updateParameters(self, parameters):
        """Modifica los parámetros en respuesta a la entrada del usuario"""
        return

    def updateMessages(self, parameters):
        """Modifica mensajes en respuesta a la entrada del usuario"""
        return

    def execute(self, parameters, messages):
        """El código principal de la herramienta"""
        
        source_gdbs_text = parameters[0].valueAsText
        output_gdb_path = parameters[1].valueAsText

        # --- Estructura para agrupar feature classes ---
        fc_structure = defaultdict(lambda: defaultdict(list))

        try:
            # --- 1. Crear la GDB de salida ---
            output_folder, output_gdb_name = os.path.split(output_gdb_path)
            if not arcpy.Exists(output_gdb_path):
                arcpy.CreateFileGDB_management(output_folder, output_gdb_name)
                messages.addMessage(f"Geodatabase de salida creada en: {output_gdb_path}")
            else:
                messages.addWarning("La Geodatabase de salida ya existe. Se agregarán o reemplazarán contenidos.")

            # --- 2. Recopilar todos los feature classes de las GDBs de origen (LÓGICA SIMPLIFICADA) ---
            messages.addMessage("Fase 1: Recopilando información de las GDBs de origen...")
            
            # Convierte el texto de las GDBs de origen a una lista, quitando comillas
            source_gdbs = [gdb.strip("'") for gdb in source_gdbs_text.split(';')]

            if not source_gdbs or not source_gdbs[0]:
                messages.addError("No se especificaron GDBs de origen. El proceso se detendrá.")
                return

            messages.addMessage(f"Se procesarán {len(source_gdbs)} GDBs.")

            for gdb in source_gdbs:
                messages.addMessage(f"  Procesando: {os.path.basename(gdb)}")
                arcpy.env.workspace = gdb

                # Feature classes dentro de datasets
                datasets = arcpy.ListDatasets("", "Feature")
                for ds_name in datasets:
                    for fc_name in arcpy.ListFeatureClasses(feature_dataset=ds_name):
                        fc_path = os.path.join(gdb, ds_name, fc_name)
                        fc_structure[ds_name][fc_name].append(fc_path)
                
                # Feature classes fuera de datasets (standalone)
                for fc_name in arcpy.ListFeatureClasses():
                    # Asegurarse de que no esté en un dataset ya procesado
                    is_in_dataset = False
                    for ds_name in datasets:
                        if arcpy.Exists(os.path.join(gdb, ds_name, fc_name)):
                           is_in_dataset = True
                           break
                    if not is_in_dataset:
                        fc_path = os.path.join(gdb, fc_name)
                        fc_structure['standalone'][fc_name].append(fc_path)

            # --- 3. Procesar la estructura recopilada y crear la GDB de salida ---
            messages.addMessage("\nFase 2: Unificando datos en la GDB de salida...")
            
            arcpy.env.workspace = output_gdb_path

            for ds_name, fcs_in_ds in fc_structure.items():
                output_ds_path = ""
                # Crear dataset si no es 'standalone' y no existe
                if ds_name != 'standalone':
                    output_ds_path = os.path.join(output_gdb_path, ds_name)
                    if not arcpy.Exists(output_ds_path):
                        # Usar la referencia espacial del primer FC como plantilla
                        template_fc = list(fcs_in_ds.values())[0][0]
                        spatial_ref = arcpy.Describe(template_fc).spatialReference
                        arcpy.CreateFeatureDataset_management(output_gdb_path, ds_name, spatial_ref)
                        messages.addMessage(f"Dataset '{ds_name}' creado.")
                
                # Procesar cada grupo de feature classes
                for fc_name, fc_paths in fcs_in_ds.items():
                    output_fc_path = os.path.join(output_ds_path if ds_name != 'standalone' else output_gdb_path, fc_name)
                    
                    if len(fc_paths) > 1:
                        # Fusionar (Merge)
                        messages.addMessage(f"  Fusionando {len(fc_paths)} feature classes en '{os.path.join(ds_name, fc_name)}'...")
                        arcpy.Merge_management(fc_paths, output_fc_path)
                    else:
                        # Copiar
                        messages.addMessage(f"  Copiando feature class '{os.path.join(ds_name, fc_name)}'...")
                        arcpy.Copy_management(fc_paths[0], output_fc_path)

                    # --- 4. Copiar metadatos ---
                    try:
                        source_metadata_fc = fc_paths[0]
                        if arcpy.Exists(source_metadata_fc):
                            importer = arcpy.metadata.Metadata(source_metadata_fc)
                            target_metadata = arcpy.metadata.Metadata(output_fc_path)
                            target_metadata.copy(importer)
                            target_metadata.save()
                            messages.addMessage("    -> Metadatos copiados exitosamente.")
                    except Exception as meta_ex:
                        messages.addWarning(f"    -> No se pudieron copiar los metadatos para {fc_name}. Error: {meta_ex}")

            messages.addMessage("\n¡Proceso de unificación completado exitosamente!")

        except arcpy.ExecuteError:
            messages.addError(arcpy.GetMessages(2))
        except Exception as e:
            messages.addError(str(e))

        return