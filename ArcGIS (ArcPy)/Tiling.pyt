# -*- coding: utf-8 -*-
import arcpy
import os
import random

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Tiling"
        self.alias = "tiling"
        self.tools = [Tool]

class Tool:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tile LAS by Area of Interest"
        self.description = "Cuts LAS files based on an area of interest and generates tiles of specific size."

    def getParameterInfo(self):
        """Define the tool parameters."""
        params = []

        # Param 0: Shapefile del AGI
        ota_shapefile = arcpy.Parameter(
            displayName="Shapefile de la OTA",
            name="ota_shapefile",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input"
        )
        params.append(ota_shapefile)

        # Param 1: Carpeta de entrada LAS
        las_folder_i = arcpy.Parameter(
            displayName="Carpeta de entrada LAS",
            name="las_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )
        params.append(las_folder_i)

        # Param 2: Carpeta de salida LAS
        las_folder_o = arcpy.Parameter(
            displayName="Carpeta de salida LAS",
            name="las_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )
        params.append(las_folder_o)

        # Param 3: Carpeta de salida Buffer
        buffer_o = arcpy.Parameter(
            displayName="Carpeta de Salida Buffer",
            name="buffer_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )
        params.append(buffer_o)

        # Param 4: Carpeta de salida Fishnet
        fishnet_o = arcpy.Parameter(
            displayName="Carpeta de Salida Fishnet",
            name="fishnet_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )
        params.append(fishnet_o)

        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Leer los parámetros
        ota_shapefile = parameters[0].valueAsText
        las_folder_i = parameters[1].valueAsText
        las_folder_o = parameters[2].valueAsText
        buffer_o = parameters[3].valueAsText
        fishnet_o = parameters[4].valueAsText

        # Paso 1: Buffer al AGI
        arcpy.analysis.PairwiseBuffer(
            in_features=r"C:\Users\Raster4\Desktop\Scripts\Python\ArcGIS Pro Pruebas\Prueba Tile LAS\Areas de interes Alhue OTA 68\ALHUE_OTA_68.shp",
            out_feature_class=r"C:\Users\Raster4\Desktop\Scripts\Python\ArcGIS Pro Pruebas\Prueba Tile LAS\Areas de interes Alhue OTA 68\ALHUE_OTA_68_PairwiseBuffer.shp",
            buffer_distance_or_field="5 Meters",
            dissolve_option="NONE",
            dissolve_field=None,
            method="PLANAR",
            max_deviation="0 Meters"
        )

        # Paso 2: Aplicar Split by Attributes por el campo ID
            # Eliminar cualquier variante de 'Id', 'ID' o 'iD" del campo y dejarla solo como "id"
        id_field = [ID, iD, Id, id]
        for field in id_field:
            id_field = id_field.lower()

        arcpy.analysis.SplitByAttributes(
            Input_Table=r"C:\Users\Raster4\Desktop\Scripts\Python\ArcGIS Pro Pruebas\Prueba Tile LAS\Areas de interes Alhue OTA 68\ALHUE_OTA_68_PairwiseBuffer.shp",
            Target_Workspace= # Debe ser en la misma carpeta del buffer, pero el nombre de la carpeta debe llamarse "Split By Attributes"
            Split_Fields="Id"
        )

        # Paso 3: Crear Minimum Bounding Geometry rectangular
        for polygon in {contenido carpeta split by attributes}:
            arcpy.management.MinimumBoundingGeometry(
                in_features= # Debe ser la carpeta resultante del Split By attributes,
                out_feature_class= # Alojado en la memoria del proyecto de ArcGIS Pro,
                geometry_type="ENVELOPE",
                group_option="NONE",
                group_field=None,
                mbg_fields_option="NO_MBG_FIELDS"
            )

        # Determinar la mejor dirección de corte (horizontal o vertical) según la relación de aspecto del AGI
        with arcpy.da.SearchCursor(out_feature_class, ["SHAPE@"]) as cursor:
            for row in cursor:
                extent = row[0].extent
                width = extent.XMax - extent.XMin
                height = extent.YMax - extent.YMin
                extent = ["Vertical", "Horizontal"]
                if width > height:
                    initial_cut_direction = "Vertical"
                elif width == height:
                    initial_cut_direction = random.choice("Vertical", "Horizontal")
                else:
                    initial_cut_direction = "Horizontal"
        
        # Paso 4: Crear Fishnet para los cortes y ajustar en caso de exceder tamaño límite (borra el corte anterior junto al fishnet)
        def create_fishnet(cut_direction):
            x_divisions, y_divisions = (1, 1)
            output_fishnet = r"C:\Users\Raster4\Desktop\Scripts\Python\ArcGIS Pro Pruebas\Prueba Tile LAS\ESQUEMA_TILES"
            
            while True:
                if cut_direction == "Vertical":
                    x_divisions += 1
                else:
                    y_divisions += 1

                #   Create Fishnet
                #   Grid Index Features (este corta los que están vacíos)
                #   Generate Grid From Area

                # Paso 5: Crear tiles de LAS
                las_dataset = "in_memory\\las_dataset"
###########                arcpy.ddd.TileLas(las_folder_i, las_folder_o, {base_name}, {out_las_dataset}, {compute_stats}, {las_version}, {point_format}, {compression}, {las_options}, {tile_feature}, {naming_method}, {file_size}, {tile_width}, {tile_height}, {tile_origin})
                input
                output
                basename
                tile feature class
                naming method
                file size



                # Verificar el tamaño de los tiles
                file_sizes = []
                for i, tile in enumerate(arcpy.da.SearchCursor(output_fishnet, ["SHAPE@"]), start=1):
                output_tile = f"C:\\Users\\Raster4\\Desktop\\Scripts\\Python\\ArcPy\\Archivo Test\\TILES\\tile_{i}.las"
                    arcpy.conversion.LasDatasetToRaster(las_dataset, output_tile, "ELEVATION", "BINNING", "FLOAT", "CELLSIZE", "1")
                    size = os.path.getsize(output_tile)
                    file_sizes.append(size)

                    if size > size_limit_bytes:
                        # Cambiar de orientación si el límite es superado
                        if cut_direction == "Vertical":
                            cut_direction = "Horizontal"
                        else:
                            cut_direction = "Vertical"
                        
                        arcpy.AddMessage(f"Tile {output_tile} exceeds size limit. Recalculating divisions in {cut_direction} direction...")
                        break
                else:
                    return output_fishnet, file_sizes

        # Ejecutar el proceso de corte con la dirección inicial
        output_fishnet, tile_sizes = create_fishnet(initial_cut_direction)
        arcpy.AddMessage(f"Finished creating tiles. Total tiles created: {len(tile_sizes)}")

        return
