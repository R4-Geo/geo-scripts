"""
===============================================================================
Script Name: Conversion_QGIS_Arcpy_tools.pyt

Description: Este script es una herramienta de ArcGIS Pro que convierte datos 
             geoespaciales de un archivo Geodatabase (GDB) a formatos Shapefile 
             (SHP) y KML, asegurando compatibilidad con QGIS y aplicaciones que 
             utilizan KML. Redondea todos los valores decimales a dos cifras y 
             realiza un recorte por Área de Interés (AOI) para cada capa, 
             organizando los resultados por directorio.

Author:      Leonel G. Rivero
Date:        2024-08-13
Version:     1.0

Requirements: 
    - ArcGIS Pro
    - arcpy

Usage:
    Esta herramienta se utiliza dentro de ArcGIS Pro como un script de herramienta 
    personalizado. Se puede agregar a un toolbox y ejecutarse proporcionando los 
    parámetros de entrada y salida correspondientes:
    
    1. Agrega este script a un Toolbox en ArcGIS Pro.
    2. Configura los parámetros de la herramienta:
       - **Archivo GDB de Entrada**: La ruta completa al archivo Geodatabase que contiene los datos a convertir.
       - **Carpeta de Destino para SHP y KML**: La carpeta donde se guardarán los archivos convertidos en formato SHP y KML.
       - **Archivo AOI (Área de Interés)**: La ruta al archivo Shapefile o GDB que define el área de interés para recortar los datos.
       - **Nombre del Campo de Zonas**: El nombre del campo dentro del AOI que agrupa las zonas específicas a procesar.
    3. Ejecuta la herramienta desde el entorno de ArcGIS Pro, asegurándote de que todos los parámetros estén correctamente configurados.

Notes:
    - Asegúrate de tener ArcGIS Pro y las licencias necesarias.
    - La conversión y procesamiento pueden variar en tiempo dependiendo del tamaño de los datos.
    - Verifica que los datos convertidos mantengan la integridad espacial y de atributos.
    - Los resultados se organizan en directorios por tipo de salida.
    
===============================================================================
"""
import arcpy
from arcpy import env
from pathlib import Path
from arcgis import GIS
import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
import sys
import traceback
from osgeo import ogr
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import json
from arcgis.features import FeatureSet



general_name = 'Export data QGIS Arcpy'
workspace = Path(__file__).parents[0]

## ===== FUNCIONES =========

def rename_logs(old_file_name):
    
    tiempo = pd.Timestamp.today().strftime("%d-%m-%Y %H-%M-%S")   
    name_general_old = Path(old_file_name).stem
    old_folder = f'{str(Path(old_file_name).parents[0])}\\Old\\{name_general_old}'
    new_file_name = f'{old_folder}\\{name_general_old}-{tiempo}.log'

    if not os.path.exists(old_folder):
        os.makedirs(old_folder) 

    if os.path.exists(old_file_name):
        os.rename(old_file_name, new_file_name)	
    
def obtener_horas_inicio_fin(archivo_logs):
    with open(archivo_logs, 'r') as f:
        lineas = f.readlines()
    hora_inicio = None
    hora_fin = None
    for linea in reversed(lineas):
        if ' - START - ' in linea and hora_inicio is None:
            hora_inicio = linea.split(' - ')[1]
            hora_inicio = datetime.strptime(hora_inicio, '%d/%m/%Y, %H:%M:%S')

        if 'END' in linea and hora_fin is None:
            hora_fin = linea.split(' - ')[1]
            hora_fin = datetime.strptime(hora_fin, '%d/%m/%Y, %H:%M:%S')
        if hora_inicio is not None and hora_fin is not None:
            break
    return hora_fin - hora_inicio

def write(text_F,tipo_p,etapa,pCadena):
    text_file = open(text_F,'a')
    tiempo = datetime.now().strftime("%d/%m/%Y, %H:%M:%S - ")
    if tipo_p == 'RESUMEN':
        text_file.write(f'{etapa}\n{pCadena}\n')
        arcpy.AddMessage(f'{etapa}\n{pCadena}\n')
    elif tipo_p == 'WARNING':
        text_file.write(f'{etapa}\n{pCadena}\n')
        arcpy.AddWarning(f'{etapa}\n{pCadena}\n')
    elif tipo_p == 'ERROR - ':
        text_file.write(f'{tipo_p}{tiempo}{etapa}{pCadena}\n')
        arcpy.AddError(f'{tipo_p}{tiempo}{etapa}{pCadena}')
    else:
        text_file.write(f'{tipo_p}{tiempo}{etapa}{pCadena}\n')
        arcpy.AddMessage(f'{tipo_p}{tiempo}{etapa}{pCadena}')
    text_file.close()

class Logfile(object):
    def __init__(self,file_name,overwrite=False):
        workspace = str(Path(__file__).parents[0])
        self.file_name = f'{workspace}\\Logs\\{file_name}.log'
        folder = str(Path(self.file_name).parents[0])
        if overwrite:
            rename_logs(self.file_name)
           
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        text_file = open(self.file_name,'a')
        h = (75*"=")+"\n"
        h2 = (75*"=")
        print(h2)
        text_file.write(h)        
    def start_script(self,pCadena):
        tipo = 'INFO - '
        etapa = 'START - '
        write(self.file_name,tipo,etapa,pCadena)
    def start_funtion(self,pCadena):
        tipo = 'INFO - '
        etapa = 'FUNCTION - '
        write(self.file_name,tipo,etapa,pCadena)
    def start(self,pCadena):
        tipo = 'INFO - '
        etapa = '  START - '
        write(self.file_name,tipo,etapa,pCadena)
    def end(self,pCadena):
        tipo = 'INFO - '
        etapa = '  END   - '
        write(self.file_name,tipo,etapa,pCadena)
    def close(self,pCadena):
        tipo = 'INFO - '
        etapa = 'CLOSING - '
        timer = obtener_horas_inicio_fin(self.file_name)
        t = f'{pCadena}, Duracion: {timer}'
        write(self.file_name,tipo,etapa,t)
    def error(self,pCadena):
        tipo = 'ERROR - '
        etapa = '  EXECUTION - '
        write(self.file_name,tipo,etapa,pCadena)        
    def info(self,pCadena):
        tipo = 'INFO - '
        etapa = '  EXECUTION - '
        write(self.file_name,tipo,etapa,pCadena)
    def resumen(self,pCadena):
        tipo = 'RESUMEN'
        etapa = '*'*75
        write(self.file_name,tipo,etapa,f'{pCadena}\n{etapa}')
    def warning(self,pCadena):
        tipo = 'WARNING'
        etapa = '*'*75
        write(self.file_name,tipo,etapa,f'{pCadena}\n{etapa}')
                 
def capturaError(e,name,logs):
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    logs.error(name)
    logs.error(str(e))	
    logs.error(str(tbinfo))

# ### Exportar a QGIS

def CreatFolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

def update_2_decimales(fc,logs):
    try:
        # Define los nombres de los campos que quieres excluir
        exclude_fields = ["Shape_Length", "Shape_Area"]

        # Obtén la lista de campos de la feature class
        fields = arcpy.ListFields(fc)

        # Filtra los campos de tipo float (Double), excluyendo los especificados
        float_fields = [field.name for field in fields if field.type == "Double" and field.name not in exclude_fields]
        if float_fields:
            ## Se crea un dataframe
            data = [row for row in arcpy.da.SearchCursor(fc, float_fields)]
            df = pd.DataFrame(data, columns=float_fields)
            # Redondear todos los valores a dos decimales
            # df = df.round(2)
            # Convertir el DataFrame de vuelta a una lista de listas para la actualización
            data_rounded = df.values.tolist()
            # Actualizar los valores en la geodatabase
            cursor = arcpy.da.UpdateCursor(fc, float_fields)
            for i, row in enumerate(cursor):
                cursor.updateRow(data_rounded[i])
            del cursor
    except Exception as e:
        capturaError(e,general_name,logs)

def truncate_to_two_decimals(value):
    return round(value, 2)

def process_feature_class(input_fc, output_fc,logs):
    try:
        # Se Crear un nuevo Feature Class
        sr = arcpy.Describe(input_fc).spatialReference
        geometry_type = arcpy.Describe(input_fc).shapeType

        arcpy.CreateFeatureclass_management(f'{Path(output_fc).parents[0]}',
                                            f'{Path(output_fc).name}', 
                                            geometry_type, 
                                            "",
                                            "DISABLED", 
                                            "DISABLED", 
                                            sr
                                            )

        # Se Agregan campos al nuevo Feature Class
        fields = arcpy.ListFields(input_fc)
        field_names = [field.name for field in fields \
                    if field.type not in ['Geometry', 'OID'] and \
                        not field.name in ['OBJECTID']]
        
        for field in fields:
            if field.type not in ['Geometry', 'OID']\
                        and not field.name in ['OBJECTID']:
                arcpy.AddField_management(output_fc,
                                        field.name, 
                                        field.type, 
                                        field_precision=2 if field.type in ['Double', 'Single'] else None)
        
        # Insertar filas en el nuevo Feature Class con valores truncados
        field_names.append('SHAPE@')
        with arcpy.da.SearchCursor(input_fc, field_names) as search_cursor, \
            arcpy.da.InsertCursor(output_fc, field_names) as insert_cursor:
            for row in search_cursor:
                new_row = [truncate_to_two_decimals(val) if isinstance(val, (float, int)) else val for val in row]
                insert_cursor.insertRow(new_row)
    except Exception as e:
        capturaError(e,general_name,logs)

def export_to_geopackage(input_gdb, output_gpkg,logs):
    try:
        arcpy.env.workspace = input_gdb
        feature_classes = arcpy.ListFeatureClasses()
        
        for fc in feature_classes:
            output_fc = f'{output_gpkg}\\{Path(fc).name}'
            process_feature_class(fc, output_fc,logs)
    except Exception as e:
        capturaError(e,general_name,logs)
 
def CrearArchivotxt(folder,name):
    contenido = "NO EXISTEN DATOS PARA MOSTRAR EN ESTA AGI"
    # Nombre del archivo
    nombre_archivo =fr'{folder}\{contenido}.txt'
    contenido = f'{contenido}: {name}\n'
    # Crear y escribir en el archivo
    with open(nombre_archivo, "a") as archivo:
        archivo.write(contenido)
    return nombre_archivo


def es_shapefile(path):
    # Definir el patrón regex para un archivo .shp
    pattern = r'.*\.shp$'
    # Verificar si el archivo existe y si el nombre cumple con el patrón
    if re.match(pattern, path, re.IGNORECASE):
        return True
    else:
        return False
   

def Export(sdf,out_fc,in_fc):
    ## Se crea el array del esquema de campos
    shapefile = es_shapefile(out_fc)
    
    # Crea el array del esquema de campos
    fields_add = [
        [
            c.name[:10] if shapefile else c.name, 
            'Text' if c.type == 'String' else c.type,
            None, 
            c.length if c.type == 'String' else None
        ]
        for c in arcpy.ListFields(in_fc)
    ]
    
    fields_add = [c for c in fields_add if c[0] in sdf.columns]
    ## Se crea el featureclass
    descfc = arcpy.Describe(in_fc)
    geometryType = descfc.shapeType
    crs = descfc.spatialReference.factoryCode 
    arcpy.CreateFeatureclass_management(f'{Path(out_fc).parents[0]}',
                                        f'{Path(out_fc).name}',
                                        geometryType,
                                        spatial_reference=crs)
    ## Se agregan los campos
    arcpy.AddFields_management(out_fc,fields_add)
    ## Se insertan los datos
    shape_column = sdf.filter(regex='(?i)^shape$').columns[0]
    cols = [c for c in sdf.columns if c not in shape_column]
    fields = ['SHAPE@']  + cols
    with arcpy.da.InsertCursor(out_fc, fields) as cursor_insert:
        for i, row in sdf.iterrows():
            # Obtener la geometría como un objeto JSON y convertirla a una geometría de arcpy
            geom_json = row[shape_column]  # Ajusta según el nombre del campo de geometría
            geom = arcpy.AsShape(geom_json, True)
            # Crear una lista con los valores de los campos, comenzando con la geometría
            field_values = [geom] + [row[field] for field in sdf.columns if field not in shape_column]
            cursor_insert.insertRow(field_values)
            
def areas(x):
    return x.area

def perimetro(x):
    return x.length

def conversionkml(fc,output_kmz):
    layer_name = f'{Path(fc).stem}'
    arcpy.MakeFeatureLayer_management(fc, layer_name)
    # Guardar la capa temporal como archivo .lyr
    layer_file =  fr"{workspace}\{layer_name}.lyrx"
    arcpy.SaveToLayerFile_management(layer_name, layer_file, "ABSOLUTE")[0]
    arcpy.conversion.LayerToKML(
        layer=layer_file,
        out_kmz_file=output_kmz,
        layer_output_scale=0,
        is_composite="NO_COMPOSITE",
        image_size=1024,
        dpi_of_client=96,
        ignore_zvalue="CLAMPED_TO_GROUND"
    )
    arcpy.Delete_management(layer_file)

def ExportQgis(parameters):
    try:
        logs = Logfile(general_name)
        logs.start_script(general_name)
        env.overwriteOutput = True
    
        gdb = r'{}'.format(parameters[0].value)
        folder_out = r'{}'.format(parameters[1].value)
        aoi = r'{}'.format(parameters[2].value)
        field_clip = r'{}'.format(parameters[3].value)

        name = 'Exportando datos'
        logs.start(name)
        ## Se actualiza a dos decimales todas las capas
        env.workspace = gdb
        features = arcpy.ListFeatureClasses()
        feature_export = []
        logs.info(f'Actualizando decimales en feature class gdb --> {Path(gdb).name}')
        for f in features:
            fc = rf'{gdb}\{f}'
            feature_export.append(fc)
            # update_2_decimales(fc,logs)
            # logs.info(f'Actualizando decimales --> {f}')
        ## Se recorren todas la zonas
        def _nameZona(x):
            if isinstance(x, (int, float)):
                x = int(x)
                return f'Zona {x}'
            else:
                return x

        aois = sorted([[_nameZona(c[0]),int(c[0]),c[1]] for c in arcpy.da.SearchCursor(aoi,[field_clip]+['Comuna'])])
        logs.info(f'Se procesaran --> {len(aois)} AOIS')
        
        ## Se recorren las zonas para cortar las areas  
        for _namezona,zona,_comuna in aois:
            env.outputZFlag = "Enabled"
            _comuna = _comuna.replace('_',' ')
            _name = f'Procesando --> {_namezona}'
            ## Se crea el folder resultado de la zona
            folder_salida = CreatFolder(rf'{folder_out}\PLANIMETRIA {_comuna}\{_namezona}\PLANIMETRIA')
            _name = f'Procesando --> {_namezona}'
            _namezona = f'{_comuna} {_namezona}'
            
            logs.start(_name)
            ## Se crea la gdb de salida
            n = _namezona.replace(' ','_')
            folder_gdb = CreatFolder(rf'{folder_salida}\Geodatabase')
            _gdb = rf'{folder_gdb}\{n}.gdb'
            if not os.path.exists(_gdb):
                arcpy.CreateFileGDB_management(folder_gdb,Path(_gdb).name,'9.2')
            else:
                arcpy.Delete_management(_gdb)
                arcpy.CreateFileGDB_management(folder_gdb,Path(_gdb).name,'9.2')
            ## Se realiza el clip
            folder_output_dict = {
            'Camino pavimentado':'Calles, caminos, senderos y Huellas',
            'Camino tierra':'Calles, caminos, senderos y Huellas',
            'Construcciones': 'Construcciones',
            'Curvas de nivel 50cm':'Curvas de nivel',
            'Deslindes prediales': 'Deslindes Prediales',
            'Eje vial':'Calles, caminos, senderos y Huellas',
            'Piscina':'Piscina',
            'Postacion':'Postacion',
            }
            ## Se extre la zona
            zona_aoi = arcpy.Select_analysis(aoi,'in_memory/tempzona',f"{field_clip} = {zona}")[0]
            ## Se realiza el clip
            for c in feature_export:
                _name_clip = str(Path(c).name).replace("_",' ')
                try:
                    _name_folder_output = folder_output_dict[_name_clip]
                except:
                    _name_folder_output = _name_clip
                logs.info(f'Exportando --> {_name_clip} --> {_namezona}')
                ## Se realiza el clip 
                env.outputZFlag = "Disabled"
                clip = arcpy.Clip_analysis(c,zona_aoi,'in_memory/temp')[0]
                
                count = int(arcpy.GetCount_management(clip)[0])
                _foldertxt = CreatFolder(rf'{folder_salida}\{_name_folder_output}')
                if count:
                    ## Se crea le folder resultado shape
                    _folder_shape = CreatFolder(rf'{folder_salida}\{_name_folder_output}\SHP')
                    ## Se crea el folder kmz
                    _folder_kmz = CreatFolder(rf'{folder_salida}\{_name_folder_output}\KMZ')
                    ## Se consulta el tipo de geometria
                    tipo = arcpy.Describe(c).shapeType
                    ## Se explota el multi part
                    clip2 = arcpy.MultipartToSinglepart_management(clip, 'in_memory/temp2')[0]
                    sdf = pd.DataFrame.spatial.from_featureclass(clip2)
                    del sdf['OBJECTID']
                    
                    if not sdf.empty:
                        if 'Shape_Length' in sdf.columns:
                            del sdf['Shape_Length']
                        if 'Shape_Area' in sdf.columns:
                            del sdf['Shape_Area']
                        if 'M2' in sdf.columns:
                            sdf['M2'] = sdf['SHAPE'].apply(lambda x : areas(x))
                        if 'SHAPE_Le_1' in sdf.columns:
                            del sdf['SHAPE_Le_1']
           
                        if _name_clip == 'Deslindes prediales':
                            try:
                                sdf = sdf[sdf['M2'] > 30]
                            except:
                                sdf['M2'] = sdf['SHAPE'].apply(lambda x : areas(x))
                                sdf = sdf[sdf['M2'] > 30]
                                del sdf['M2']
                        if tipo == 'Polyline':
                            sdf['longitud'] = sdf['SHAPE'].apply(lambda x : perimetro(x))
                            sdf = sdf[sdf['longitud']>=10]
                            del sdf['longitud']
                            
                        if 'ORIG_FID' in sdf.columns:
                            del sdf['ORIG_FID']
                            
                        if 'Id' in sdf.columns:
                            del sdf['Id']
                            
                        ## Se exporta a gdb
                        fc_export = fr'{_gdb}\{Path(c).name}'
                        Export(sdf,fc_export,c)

                        
                        ## Se exporta a shape
                        # Redondear todos los campos numéricos a 2 decimales sin ceros adicionales
                        if tipo != 'Point':
                            sdf['Shape_Leng'] = sdf['SHAPE'].apply(lambda x : perimetro(x))
                        if tipo == 'Polygon':
                            sdf['Shape_Area'] = sdf['SHAPE'].apply(lambda x : areas(x))
                          
                        shape_export = fr'{_folder_shape}\{_name_clip}.shp'
                        # Reducir el nombre de todas las columnas a 10 caracteres
                        sdf.columns = sdf.columns.map(lambda x: x[:10])
                        Export(sdf,shape_export,c)
                        cols_ = [c.name for c in arcpy.ListFields(shape_export)]
                        if 'SHAPE_Le_1' in cols_:
                            arcpy.DeleteField_management(shape_export,'SHAPE_Le_1')
                            
                        # # Convertir la capa a KMZ
                        output_kmz = fr'{_folder_kmz}\{_name_clip}.kmz'
                        conversionkml(shape_export,output_kmz)
                        
                else:
                    txt_file = CrearArchivotxt(_foldertxt,f'{Path(c).name}')
                    msg = f'La capa {Path(c).name} quedo fuera de la zona\n Se crea el txt --> {txt_file}'
                    logs.warning(msg)
            
            # Crear un nuevo GeoPackage
            ## Se exporta a QGIS *.gpkg
            # logs.info('Exportando datos a QGIS geopackage ')
            # folder_geopackage = CreatFolder(rf'{folder_salida}\Geopackage')
            # output_gpkg =rf'{folder_geopackage}\{n}.gpkg'
            # # Asegurarse de que el GeoPackage no exista antes de crear uno nuevo
            # if os.path.exists(output_gpkg):
            #     os.remove(output_gpkg)
            # driver = ogr.GetDriverByName("GPKG")
            # driver.CreateDataSource(output_gpkg)
            # export_to_geopackage(_gdb, output_gpkg,logs)
            
            logs.end(_name)
        logs.end(name)
        logs.close(general_name)
    except Exception as e:
        capturaError(e,general_name,logs)
    
   
# # ============ Parametros tools ==========================

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [QGIS_Export]
        
class QGIS_Export(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Export Datos QGIS"
        self.description = "Export Datos QGIS"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Primer parametro
        gdb_param = arcpy.Parameter(
                            displayName='GDB',
                            name= 'GDB',
                            datatype= 'DEWorkspace',
                            direction= 'input')
        # Segundo parametro
        folder = arcpy.Parameter(
                    displayName='Folder Resultado',
                    name= 'FolderResult',
                    datatype= 'DEFolder',
                    direction= 'input')
        
        aoi= arcpy.Parameter(
            displayName="Seleccione AOI",
            name="input_layer",
            datatype=["GPFeatureLayer", "DEFeatureClass"],
            parameterType="Required",
            direction="Input"
        )

        # Parámetro 2: Campo de la capa
        field = arcpy.Parameter(
            displayName="Campo de zonas",
            name="field_name",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )
        # La dependencia asegura que el segundo parámetro se actualice en función del primero
        field.parameterDependencies = [aoi.name]
        parameters = [gdb_param,folder,aoi,field]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        # Obtén el valor de la capa seleccionada
        input_layer = parameters[2].valueAsText

        # Lista todos los campos de la capa
        field_list = [field.name for field in arcpy.ListFields(input_layer)]

        # Actualiza los valores del parámetro de campos
        parameters[3].filter.list = field_list
       
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        ExportQgis(parameters)
        return

