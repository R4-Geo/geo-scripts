import globalmapper as gm

#Import terrain layer
err, terrain = gm.LoadLayer("C:/Basics_of_Python_in_GM/Lesson 5/Data/terrain.tif", gm.GM_LoadFlags_UseDefaultLoadOpts)

TerrainInfo = gm.GetLayerInfo(terrain)
DataType = TerrainInfo.mHasRasterData

print("The type of data in this layer is (0 for raster, 1 for elevation)", DataType)

#Generate contours
contour_param = gm.GM_ContourParams_t()
contour_param.mSize = 390198832
contour_param.mDesc = "GENERATED CONTOURS"
contour_param.mContourInterval = 5
contour_param.mIntervalInFeet = False
contour_param.mGenerateAreas = False
contour_param.mGenerateSpotElevs = False
contour_param.mNumberOnlyLabels = False
contour_param.mShowProgress = True
contour_param.mDisableSmoothing = False
contour_param.mCreateFromAbove = False
contour_param.mSingleLevelOnly = False
contour_param.mXSpacing = 10
contour_param.mYSpacing = 10
contour_param.mSimpThreshold = 1
contour_param.mCreateNonOverlappingAreas = True
bounds_rect = gm.GM_Rectangle_t()
bounds_rect.mMinX = 698469.139800
bounds_rect.mMaxX = 710929.139800
bounds_rect.mMinY = 4703338.306085
bounds_rect.mMaxY = 4712748.306085
contour_param.mContourBounds = bounds_rect
layer = gm.FindLoadedLayer("terrain.tif")
# make sure that the layer is loaded successfully
err, elev_grid_layer = gm.GenerateContours(layer, contour_param)

#Export flags and options for creating the DXF file.
script_setup = (
    "EXPORT_VECTOR EXPORT_LAYER=\"GENERATED CONTOURS\" "
    "FILENAME=\"C:/Basics_of_Python_in_GM/Lesson 5/Results/Lesson 5.dxf\" "
    "TYPE=\"DXF\" EXPORT_DXF_LABELS=\"ATTRS\" DXF_TEXT_SIZE=\"1\" "
    "EXPORT_ELEV=\"NO\" LAYER_ATTR=\"<Feature Description>\" "
    "VERSION=\"R15 (AutoCAD 2000)\" ALLOW_LONG_LABELS=\"NO\" "
    "EXPORT_SINGLE_ELEV_2D=\"NO\" EXPORT_ATTRS=\"NO\" "
    "EXPORT_BINARY_DXF=\"NO\" EXPORT_ECEF=\"NO\" GEN_PRJ_FILE=\"NO\" "
    "EMBED_PROJECTION=\"YES\""
)

err = gm.RunScript(script_setup, gm.GM_LoadFlags_UseDefaultLoadOpts, 0)