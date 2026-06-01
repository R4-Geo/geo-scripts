# -*- coding: utf-8 -*-
import arcpy

class Toolbox(object):
    def __init__(self):
        self.label = "Herramientas de Conteo Automatizado"
        self.alias = "ConteoTools"
        self.tools = [SumarEntidadesMultiples]

class SumarEntidadesMultiples(object):
    def __init__(self):
        self.label = "Sumar Total de Objetos (Batch)"
        self.description = "Cuenta la cantidad de registros en múltiples Feature Classes y calcula una suma total."
        self.canRunInBackground = False

    def getParameterInfo(self):
        param0 = arcpy.Parameter(
            displayName="Capas de Entrada (Seleccione una o varias)",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
            multiValue=True
        )
        return [param0]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        try:
            # En lugar de usar .value, usamos .valueAsText para obtener una cadena
            # Ejemplo: "Capa1;Capa2;Capa3"
            raw_input = parameters[0].valueAsText
            
            # Verificamos que no esté vacío
            if not raw_input:
                messages.addErrorMessage("No se seleccionaron capas.")
                return

            # Dividimos la cadena por punto y coma para crear una lista real de Python
            # Esto maneja tanto rutas de archivos como nombres de capas
            capas_entrada = raw_input.split(";")
            
            total_global = 0
            
            messages.addMessage("--- Calculando Entidades ---")

            for capa in capas_entrada:
                # Limpieza: A veces las rutas vienen con comillas simples extra, las quitamos
                capa = capa.replace("'", "")
                
                # GetCount funciona bien con el nombre de la capa o la ruta completa
                resultado = arcpy.management.GetCount(capa)
                cantidad = int(resultado[0])
                
                # Intentamos obtener solo el nombre del archivo para que el mensaje sea limpio
                # Si es una ruta larga, extraemos lo que está después de la última barra
                nombre_visual = str(capa).split("\\")[-1]
                
                messages.addMessage(f"Capa: '{nombre_visual}' -> {cantidad} entidades.")
                
                total_global += cantidad

            messages.addMessage("-" * 30)
            messages.addMessage(f"RESULTADO FINAL: {total_global} objetos en total.")
            messages.addMessage("-" * 30)
            
        except Exception as e:
            messages.addErrorMessage(f"Error en la ejecución: {str(e)}")

        return