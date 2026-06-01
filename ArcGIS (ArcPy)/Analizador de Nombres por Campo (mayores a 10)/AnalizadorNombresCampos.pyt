import arcpy

class Toolbox(object):
    def __init__(self):
        """Define la clase del toolbox (la caja de herramientas)."""
        self.label = "Análisis de Nombres de Campos"
        self.alias = "AnalisisCampos"

        # Lista de herramientas que contiene el toolbox
        self.tools = [BuscarNombresCamposLargos]

class BuscarNombresCamposLargos(object):
    def __init__(self):
        """Define la clase de la herramienta."""
        self.label = "Buscar Nombres de Campos Largos (>10 caracteres)"
        self.description = "Lee todos los feature classes dentro de cada feature dataset de una GDB y reporta los campos cuyos nombres tengan más de 10 caracteres."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define los parámetros que la herramienta aceptará."""
        param0 = arcpy.Parameter(
            displayName="Geodatabase de Entrada",
            name="in_gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        
        param0.filter.list = ["File Geodatabase", "Personal Geodatabase", "SDE Geodatabase"]

        params = [param0]
        return params

    def isLicensed(self):
        """Establece las licencias necesarias. No se requiere ninguna especial."""
        return True

    def updateParameters(self, parameters):
        """Modifica los parámetros si es necesario. No se usa aquí."""
        return

    def updateMessages(self, parameters):
        """Modifica los mensajes de validación. No se usa aquí."""
        return

    def execute(self, parameters, messages):
        """El código principal que se ejecuta cuando la herramienta es utilizada."""
        in_gdb = parameters[0].valueAsText

        # Establecer el espacio de trabajo en la GDB de entrada
        arcpy.env.workspace = in_gdb
        arcpy.AddMessage(f"Analizando la geodatabase: {in_gdb}\n")

        # --- Lógica principal ---
        
        encontrados = False # Bandera para saber si se encontró algún campo largo

        try:
            # 1. Listar todos los Feature Datasets
            feature_datasets = arcpy.ListDatasets("", "Feature")

            if not feature_datasets:
                arcpy.AddWarning("No se encontraron Feature Datasets en esta geodatabase.")

            for fd in feature_datasets:
                arcpy.AddMessage(f"--- Feature Dataset: {fd} ---")
                
                # 2. Listar Feature Classes dentro de cada Feature Dataset
                # La ruta completa del dataset es necesaria para listar sus contenidos
                fcs_in_fd = arcpy.ListFeatureClasses(feature_dataset=fd)

                if not fcs_in_fd:
                    arcpy.AddMessage("  No contiene Feature Classes.")
                    continue

                for fc in fcs_in_fd:
                    # 3. Listar los campos de cada Feature Class
                    try:
                        fields = arcpy.ListFields(fc)
                        campos_largos_fc = []

                        for field in fields:
                            # 4. Verificar la longitud del nombre del campo
                            if len(field.name) > 10:
                                campos_largos_fc.append(field.name)
                                encontrados = True
                        
                        if campos_largos_fc:
                            arcpy.AddMessage(f"  -> Feature Class: {fc}")
                            for nombre_campo in campos_largos_fc:
                                arcpy.AddMessage(f"     - Campo encontrado: '{nombre_campo}' (Longitud: {len(nombre_campo)})")
                        
                    except Exception as e_field:
                        arcpy.AddWarning(f"No se pudo leer los campos para el Feature Class: {fc}. Error: {e_field}")
                
                arcpy.AddMessage("-" * (len(fd) + 24) + "\n")

            if not encontrados:
                arcpy.AddMessage("Análisis finalizado: No se encontraron campos con nombres de más de 10 caracteres.")
            else:
                 arcpy.AddMessage("Análisis finalizado.")


        except arcpy.ExecuteError:
            messages.addErrorMessage(arcpy.GetMessages(2))
        except Exception as e:
            messages.addErrorMessage(str(e))
            
        return