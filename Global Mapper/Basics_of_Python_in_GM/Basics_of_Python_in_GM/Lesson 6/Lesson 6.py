import globalmapper as gm
 
#Importing the point cloud layer.
err, layer = gm.LoadLayer("C:/Basics_of_Python_in_GM/Lesson 6/Data/Forsyth_Park.laz", gm.GM_LoadFlags_UseDefaultLoadOpts)

#Set the projection to UTM 17N (WGS 84).
error, utm17n_proj = gm.LoadProjectionFromEPSGCode(32617)
gm.SetProjection(utm17n_proj)

lidar_thin_opts = gm.GM_LidarSpatialThinSetup_t()
lidar_thin_opts.mLayerDesc = "Forsyth_Park.laz (Thinned)"
lidar_thin_opts.mMedianPercentile = 50
lidar_thin_opts.mNthCount = 0
lidar_thin_opts.mResMult = 2
lidar_thin_opts.mElevResMult = 1
lidar_thin_opts.mKeepAllReturns = False
lidar_thin_opts.mCreateNewCloud = True
lidar_thin_opts.mThinAlg = 3
lidar_thin_opts.mHideProgress = False

err = gm.LidarThin(layer, lidar_thin_opts, 0)

#Classify ground in the thinned layer via Automatic Point Cloud Analysis.
ground_classify_layers = []
ground_classify_layers.append( gm.FindLoadedLayer("Forsyth_Park.laz (Thinned)") )
ground_opts = gm.GM_ClassifyGroundSetup_t()
ground_opts.mFlags = 1
ground_opts.mResMult = -2
ground_opts.mCurvature = 0.30000001
ground_opts.mDeltaHeightMaxM = 10
ground_opts.mMaxWindowSizeM = 100
ground_opts.mSlopeDeg = 7.5
err = gm.LidarClassifyGround(ground_classify_layers, ground_opts, 0)

# Classify Buildings and Vegetation in the thinned layer via Automatic Point Cloud Analysis
graph_classify_layers = []
graph_classify_layers.append( gm.FindLoadedLayer("Forsyth_Park.laz (Thinned)") )

build_veg_opts = gm.GM_ClassifyBuildingVegSetup_t()
build_veg_opts.mGridBinSizeUnits = gm.GM_LidarResMult_Spacings
build_veg_opts.mMeanGridBinMult = 3
build_veg_opts.mMinHeightAboveGround = 3
graph_opts = gm.GM_ClassifyGraphSetup_t()
graph_opts.mTypes = 6
graph_opts.mFlags = 1
graph_opts.mBuildingVegOpts = build_veg_opts
err = gm.LidarClassifyGraph(graph_classify_layers, graph_opts, 0)

#Export classified point cloud to LAZ.
script_setup = (
    "EXPORT_VECTOR EXPORT_LAYER=\"Forsyth_Park.laz (Thinned)\" "
    "FILENAME=\"C:/Basics_of_Python_in_GM/Lesson 6/Results/Lesson_Six.laz\" "
    "TYPE=\"LAZ\" ELEV_UNITS=\"METERS\" VERT_CS_CODE=\"5703\" VERT_CITATION=\"\" "
    "FILE_SOURCE_ID=\"0\" GLOBAL_ENCODING=\"0\" SYSTEM_ID=\"\" GEN_SOFTWARE=\"\" "
    "INC_COLOR=\"NO\" NO_PROJ_HEADER=\"NO\" FLIGHT_DATE=\"2024-06-13T13:01:03Z\"")

err = gm.RunScript(script_setup, gm.GM_LoadFlags_UseDefaultLoadOpts, 0)



