# NombreDelArchivo.pyt
import arcpy

class Toolbox(object):
    def __init__(self):
        """Define la clase Toolbox y la información asociada."""
        self.label = "Mi Toolbox Personalizada"
        self.alias = "miToolbox"

        # Lista de herramientas incluidas en la toolbox
        self.tools = [MiHerramienta]

class MiHerramienta(object):
    def __init__(self):
        """Define la clase de la herramienta."""
        self.label = "Procesar Edificaciones"
        self.description = "Esta herramienta procesa datos de edificaciones utilizando las entradas proporcionadas."
        self.canRunInBackground = False # O True 

    def getParameterInfo(self):
        """Define los parámetros de la herramienta."""
        
        # Parámetro 0: Esqueleto de Edificación (Feature Class de entrada)
        param0 = arcpy.Parameter(
            displayName="Capa de Esqueleto de Edificación",
            name="fc_esqueleto",
            datatype="DEFeatureClass", # Data Element Feature Class
            parameterType="Required", # Requerido
            direction="Input")
        # Aquí puedes agregar filtros para tipos de geometría, etc.
        # param0.filter.list = ["Polygon", "Polyline"] # Ejemplo

        # Parámetro 1: Predio (Feature Class de entrada)
        param1 = arcpy.Parameter(
            displayName="Capa de Predios",
            name="fc_predio",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        # Parámetro 2: Puntos de Edificación (Feature Class de entrada)
        param2 = arcpy.Parameter(
            displayName="Puntos para Identificar Edificaciones",
            name="fc_puntos_edificacion",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        # param2.filter.list = ["Point"] # Ejemplo de filtro por tipo de geometría

        # Parámetro 3: Geodatabase de Destino (Workspace de salida)
        param3 = arcpy.Parameter(
            displayName="Geodatabase de Destino",
            name="gdb_destino",
            datatype="DEWorkspace", # Data Element Workspace
            parameterType="Required",
            direction="Input")
        param3.filter.list = ["Local Database"] # Para GDBs locales (FileGDB, PersonalGDB)
        
        # Parámetro 4: Nombre del Feature Class de Salida (String para el nombre)
        param4 = arcpy.Parameter(
            displayName="Nombre del Feature Class de Edificaciones Resultante",
            name="fc_edificacion_salida_nombre",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param4.value = "Edificacion_Procesada" # Valor por defecto

        params = [param0, param1, param2, param3, param4]
        return params

    def isLicensed(self):
        """Establece si la herramienta tiene licencia para ejecutarse."""
        return True

    def updateParameters(self, parameters):
        """Modifica los parámetros de la herramienta basándose en los valores de otros parámetros."""
        # Ejemplo de validación simple: Verificar si la GDB de destino existe
        if parameters[3].valueAsText:
            if not arcpy.Exists(parameters[3].valueAsText) or not parameters[3].valueAsText.lower().endswith(".gdb"):
                parameters[3].setErrorMessage("La Geodatabase de destino no existe o no es una File Geodatabase (.gdb).")
        
        # Validación para los Feature Classes de entrada (existencia)
        for i in range(3): # Itera sobre los primeros 3 parámetros (fc_esqueleto, fc_predio, fc_puntos_edificacion)
            if parameters[i].valueAsText:
                if not arcpy.Exists(parameters[i].valueAsText):
                    parameters[i].setErrorMessage(f"El Feature Class '{parameters[i].displayName}' no existe.")
            elif parameters[i].parameterType == "Required" and not parameters[i].valueAsText:
                 parameters[i].setErrorMessage(f"El parámetro '{parameters[i].displayName}' es requerido.")


        return

    def updateMessages(self, parameters):
        """Modifica los mensajes de la herramienta basándose en los valores de los parámetros."""
        # Similar a updateParameters, pero se enfoca en los mensajes informativos o de error.
        # Esta función se llama con más frecuencia que updateParameters.
        
        # Ejemplo: Verificar si el Feature Class de puntos realmente contiene puntos
        if parameters[2].valueAsText and arcpy.Exists(parameters[2].valueAsText):
            desc = arcpy.Describe(parameters[2].valueAsText)
            if desc.shapeType != "Point":
                parameters[2].setErrorMessage("La capa de Puntos de Edificación debe ser de tipo Punto.")
        return

    def execute(self, parameters, messages):
        """El código principal de la herramienta."""
        
        # Obtener los valores de los parámetros
        fc_Esqueleto = parameters[0].valueAsText
        fc_Predio = parameters[1].valueAsText
        fc_Puntos_Edificacion = parameters[2].valueAsText
        gdb_destino = parameters[3].valueAsText
        fc_edificacion_salida_nombre = parameters[4].valueAsText
        
        messages.addMessage("Iniciando proceso de creación de edificaciones...")

        #-----------------
        #  PROCESAMIENTO
        #-----------------

        # FEATURE TO POLYGON (de entidad a polígono para crear los polígonos de edificación)
        fc_Edificacion_path = f"{gdb_destino}/{fc_edificacion_salida_nombre}"
        
        try:
            messages.addMessage(f"Creando polígonos de edificación en: {fc_Edificacion_path}")
            arcpy.FeatureToPolygon_management(
                in_features=[fc_Esqueleto, fc_Predio], 
                out_feature_class=fc_Edificacion_path, 
                cluster_tolerance="", 
                attributes="ATTRIBUTES", 
                label_features="" # Dejar vacío si no hay puntos de etiqueta o usar fc_Puntos_Edificacion si aplica
            )
            messages.addMessage("Polígonos de edificación creados.")

            # ELIMINAR POLÍGONOS QUE NO SON EDIFICACIONES
            messages.addMessage("Seleccionando y eliminando polígonos que no son edificaciones...")
            # Crear una capa temporal para la selección
            arcpy.MakeFeatureLayer_management(fc_Edificacion_path, "fc_Edificacion_Layer_temp")
            
            # Process: Select Layer By Location
            arcpy.SelectLayerByLocation_management(
                in_layer="fc_Edificacion_Layer_temp", 
                overlap_type="CONTAINS", 
                select_features=fc_Puntos_Edificacion, 
                search_distance="", 
                selection_type="NEW_SELECTION", 
                invert_selection_effect="INVERT" # Importante: INVERT para seleccionar los que NO contienen puntos
            )
            
            # Contar cuántos se van a eliminar (opcional, para mensajes)
            count_to_delete = int(arcpy.GetCount_management("fc_Edificacion_Layer_temp")[0])
            if count_to_delete > 0:
                messages.addMessage(f"Eliminando {count_to_delete} polígonos...")
                # Process: Delete Features
                arcpy.DeleteFeatures_management("fc_Edificacion_Layer_temp")
                messages.addMessage("Polígonos no deseados eliminados.")
            else:
                messages.addMessage("No se encontraron polígonos para eliminar según los criterios.")
            
            # Eliminar la capa temporal
            arcpy.Delete_management("fc_Edificacion_Layer_temp")

            messages.addMessage("Proceso completado exitosamente.")

        except arcpy.ExecuteError:
            messages.addError(arcpy.GetMessages(2))
            arcpy.AddError("Error durante la ejecución de la herramienta.")
        except Exception as e:
            messages.addError(f"Ocurrió un error no controlado: {str(e)}")
            
        return

    def postExecute(self, parameters):
        """Este método se llama después de que se ejecuta la herramienta."""
        return