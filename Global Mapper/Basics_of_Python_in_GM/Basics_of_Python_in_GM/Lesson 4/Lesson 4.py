import globalmapper as gm

# NOTE: Import Buffer Data
err, layerTrails = gm.LoadLayer("C:/Basics_of_Python_in_GM/Lesson 4/Data/GRSM_TRAILS.zip", gm.GM_LoadFlags_UseDefaultLoadOpts)
err, layer = gm.LoadLayer("C:/Basics_of_Python_in_GM/Lesson 4/Data/Boundaries.kmz", gm.GM_LoadFlags_UseDefaultLoadOpts)

# NOTE: Select Swain County & Create a buffer of 0.5 miles.
# Creating buffer area.
LayerToAddBuffer = layer 
TypeOfBufferToAdd = gm.GM_FeatureClass_Area  #Area Point Line.
LayerFeature = 6  #Select Swain County.
RadiusOfBuffer = 800  #Size is tracked in meters so the current radius is set to roughly half a mile.
projection = gm.GM_Projection_t()  #Pointer / Reference to the Global Mapper projection class.
buffer_layer = gm.CreateCustomVectorLayer("Buffer", projection)  #New layer for the buffer.

gm.CreateBufferArea(LayerToAddBuffer, TypeOfBufferToAdd, LayerFeature, RadiusOfBuffer, buffer_layer)

#Crop Terrain from Buffer.
err, output, outputCount = gm.RunScript("IMPORT FILENAME=\"C:/Basics_of_Python_in_GM/Lesson 4/Data/Terrain.gmg\" TYPE=\"GLOBAL_MAPPER_GRID\" POLYGON_CROP_FILE=\"Buffer\"", 0x0, 0x0)

#Use the layer handles to close the layers.
err = gm.CloseLayer(layerTrails)
err = gm.CloseLayer(layer)
err = gm.CloseLayer(buffer_layer)

#Export as a Global Mapper package.
err = gm.ExportPackage("C:/Basics_of_Python_in_GM/Lesson 4/Results/Lesson 4.gmp", None, None, 0.0, gm.GM_ExportPackage_HideProgress)

