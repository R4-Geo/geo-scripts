"""
===============================================================================
Script Name: Coordenadas_Extremas.pyt

Description: Esta herramienta de ArcGIS Pro calcula las coordenadas extremas 
             (norte, sur, este, oeste) de una feature class mediante la creación
             de un minimum bounding geometry (envelope). Las coordenadas son 
             proyectadas automáticamente a WGS84 (EPSG:4326) y redondeadas a 
             6 decimales para su uso en sistemas de referencia geográficos.

Author:      Daniel Labraña Trujillo
Date:        2025-01-09
Version:     1.0

Requirements: 
    - ArcGIS Pro
    - arcpy

Usage:
    Esta herramienta se utiliza dentro de ArcGIS Pro como un script de herramienta 
    personalizado. Se puede agregar a un toolbox y ejecutarse proporcionando los 
    siguientes parámetros:
    
    1. Agrega este script a un Toolbox en ArcGIS Pro.
    2. Configura los parámetros de la herramienta:
       - **Código EPSG**: El código EPSG del sistema de coordenadas de entrada 
         (ejemplo: 32719 para UTM Zone 19S)
       - **Feature Class de entrada**: La feature class para la cual se calcularán 
         las coordenadas extremas
       - **Archivo de texto de salida** (opcional): Ruta donde se guardarán las 
         coordenadas en formato texto
    3. La herramienta creará un envelope temporal, calculará sus coordenadas 
       extremas en WGS84 y las mostrará en la ventana de resultados y/o las 
       guardará en un archivo de texto.

Notes:
    - Las coordenadas se redondean a 6 decimales para mantener la precisión 
      adecuada en coordenadas geográficas
    - La herramienta proyecta automáticamente los datos al sistema WGS84 (EPSG:4326)
    - Las coordenadas se presentan en el siguiente formato:
        * OESTE (LON_MIN)
        * ESTE (LON_MAX)
        * NORTE (LAT_MAX)
        * SUR (LAT_MIN)
    
===============================================================================
"""
import arcpy
import os

arcpy.SetLogHistory(False)
arcpy.SetLogMetadata(False)

class Toolbox(object):
    def __init__(self):
        """Define el toolbox (el nombre del toolbox es el nombre del archivo .pyt)."""
        self.label = "Coordenadas Extremas"
        self.alias = "CoordenadasExtremas"
        self.tools = [EnvelopeCoordinates]

class EnvelopeCoordinates(object):
    def __init__(self):
        """Define la herramienta."""
        self.label = "Obtener Coordenadas Extremas"
        self.description = "Crea un envelope (minimum bounding geometry) y calcula sus coordenadas extremas en WGS84"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define los parámetros de la herramienta."""
        # Parámetro 1: Código EPSG
        param_epsg = arcpy.Parameter(
            displayName="Código EPSG del sistema de coordenadas de entrada",
            name="input_epsg",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param_epsg.value = "32719"  # Valor por defecto

        # Parámetro 2: Feature Class de entrada
        param_input = arcpy.Parameter(
            displayName="Feature Class de entrada",
            name="input_fc",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        # Parámetro 3: Archivo de salida (opcional)
        param_output = arcpy.Parameter(
            displayName="Archivo de texto de salida (opcional)",
            name="output_txt",
            datatype="DEFile",
            parameterType="Optional",
            direction="Output")
        param_output.filter.list = ["txt"]

        params = [param_epsg, param_input, param_output]
        return params

    def isLicensed(self):
        """Verifica si la herramienta tiene licencia para ejecutarse."""
        return True

    def updateParameters(self, parameters):
        """Modifica los valores y propiedades de los parámetros."""
        return

    def updateMessages(self, parameters):
        """Modifica los mensajes de validación de los parámetros."""
        return

    def execute(self, parameters, messages):
        """Código fuente de la herramienta."""
        try:
            # Obtener los valores de los parámetros
            input_epsg = parameters[0].valueAsText
            input_fc = parameters[1].valueAsText
            output_txt = parameters[2].valueAsText

            # Crear las referencias espaciales
            input_sr = arcpy.SpatialReference(int(input_epsg))
            output_sr = arcpy.SpatialReference(4326)  # WGS84

            # Verificar que la feature class existe
            if not arcpy.Exists(input_fc):
                arcpy.AddError(f"La feature class {input_fc} no existe")
                return

            # Crear una feature class temporal para el envelope
            workspace = arcpy.env.scratchGDB
            temp_envelope = os.path.join(workspace, "temp_envelope")

            # Crear el minimum bounding geometry (envelope)
            arcpy.AddMessage("Creando envelope...")
            arcpy.MinimumBoundingGeometry_management(
                input_fc,
                temp_envelope,
                "ENVELOPE",
                "ALL",
                None,
                "MBG_FIELDS"
            )

            # Obtener las coordenadas del envelope
            with arcpy.da.SearchCursor(temp_envelope, ["SHAPE@"]) as cursor:
                for row in cursor:
                    # Obtener la geometría y proyectarla
                    geom = row[0]
                    if geom.spatialReference.factoryCode != 4326:
                        geom = geom.projectAs(output_sr)

                    # Obtener el extent
                    extent = geom.extent
                    coords = {
                        "OESTE (LON_MIN)": round(extent.XMin, 6),
                        "ESTE (LON_MAX)": round(extent.XMax, 6),
                        "NORTE (LAT_MAX)": round(extent.YMax, 6),
                        "SUR (LAT_MIN)": round(extent.YMin, 6)
                    }

                    # Mostrar las coordenadas en la ventana de resultados
                    arcpy.AddMessage("\nCoordenadas en WGS84 (geográficas decimales):")
                    for name, value in coords.items():
                        arcpy.AddMessage(f"{name}: {value}")

                    # Si se especificó archivo de salida, guardar las coordenadas
                    if output_txt:
                        with open(output_txt, 'w') as f:
                            f.write("Coordenadas en WGS84 (geográficas decimales)\n")
                            for name, value in coords.items():
                                f.write(f"{name}: {value}\n")
                        arcpy.AddMessage(f"\nCoordenadas guardadas en: {output_txt}")

                    break  # Solo procesamos la primera geometría

            # Limpiar - eliminar feature class temporal
            arcpy.Delete_management(temp_envelope)

            # Eliminar archivo .xml generado automáticamente (si existe)
            xml_file = output_txt + ".xml"
            if os.path.exists(xml_file):
                os.remove(xml_file)
                arcpy.AddMessage(f"Archivo auxiliar eliminado: {xml_file}")


        except Exception as e:
            arcpy.AddError(f"Error: {str(e)}")
            # Asegurarse de limpiar el temporal en caso de error
            if arcpy.Exists(temp_envelope):
                arcpy.Delete_management(temp_envelope)

    def postExecute(self, parameters):
        """Este método se ejecuta después de que los outputs son procesados."""
        return
    
