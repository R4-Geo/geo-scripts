#The following code demonstrates how to generate a DEM and extract building footprints from lidar data. 

#Import the global mapper library as shorthand GM
import globalmapper as gm

#Import the point cloud that was classified in Lesson 6
err, array_ptr, array_size = gm.LoadLayerList("C:\Basics_of_Python_in_GM\Lesson 6\Results\Lesson_Six.laz", gm.GM_LoadFlags_UseDefaultLoadOpts)

#Use RunScript to use the Global Mapper Scripting command GENERATE_ELEV_GRID
script = """
GENERATE_ELEV_GRID \
    FILENAME="Lesson_Six.laz" \
    LIDAR_FILTER="NONE,2" \
    GRID_ALG=BIN_MIN \
    SPATIAL_RES_METERS=1.0 \
    LAYER_DESC="Ground Points Elevation Grid"\
	NO_DATA_DIST_MULT = 10
"""
err_code, layer_handles, num_handles = gm.RunScript(script, gm.GM_LoadFlags_UseDefaultLoadOpts, 0)

elevation_flags = 1048576
elevation_layer = gm.FindLoadedLayer("Ground Points Elevation Grid")
# make sure that the layer is loaded successfully
bounds_rect = gm.GM_Rectangle_t()
bounds_rect.mMinX = 490108.693554
bounds_rect.mMaxX = 491257.693554
bounds_rect.mMinY = 3546996.950810
bounds_rect.mMaxY = 3548135.950810
err = gm.ExportElevation("C:\\Basics_of_Python_in_GM\\Lesson 7\\Results\\lesson_7.tif", gm.GM_Export_ElevGeoTIFF, elevation_layer, bounds_rect, 1149, 1139, elevation_flags, gm.GM_ElevUnit_Meters)
 
lidar_extract_opts = gm.GM_LidarExtractSetup_t() 
lidar_extract_opts.mTypes = 1
lidar_extract_layers = [] 
lidar_extract_layers.append( gm.FindLoadedLayer("Lesson_Six.laz") )
err, output_layer = gm.LidarExtractFeatures(lidar_extract_layers, lidar_extract_opts) 


vector_flags = 37
vector_layer = gm.FindLoadedLayer("Building Footprints")
layer_info = gm.GetLayerInfo(vector_layer)
err = gm.ExportVector("C:/Basics_of_Python_in_GM/Lesson 7/Results/ShapeFile.shp", gm.GM_Export_Shapefile, vector_layer, layer_info.mGlobalRect, vector_flags, 0)

