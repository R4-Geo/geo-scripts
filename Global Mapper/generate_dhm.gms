// =========================== // Solicitar directorios de entrada y salida // =========================== 
DEFINE_VAR NAME="DSM_DIR" 
PROMPT=DIR VALUE="C:\Default\DSM" 
ABORT_ON_CANCEL=YES 
DEFINE_VAR NAME="DTM_DIR" 
PROMPT=DIR VALUE="C:\Default\DTM" 
ABORT_ON_CANCEL=YES 
DEFINE_VAR NAME="OUTPUT_DIR" 
PROMPT=DIR VALUE="C:\Default\Output" 
ABORT_ON_CANCEL=YES

// =========================== // Importar rasters DSM y DTM // =========================== 
IMPORT_DIR_TREE DIRECTORY="%DSM_DIR%" 
FILENAME_MASKS="DSM*" 
TYPE=RASTER 
IMPORT_DIR_TREE 
DIRECTORY="%DTM_DIR%" 
FILENAME_MASKS="DTM*" 
TYPE=RASTER

// =========================== // Generar DHM para cada par DSM/DTM (DHM = DSM - DTM) // =========================== 
LAYER_LOOP_START FILENAME="DSM" 
VAR_NAME_PREFIX="DSM_LAYER" // Derivar el nombre del DTM: se reemplaza "DSM" por "DTM" en el nombre del DSM actual DEFINE_VAR NAME="DTM_FILE" VALUE="%LAYER_FNAME%" REPLACE_STR="DSM=DTM" // Derivar el nombre de salida del DHM: se reemplaza "DSM" por "DHM" DEFINE_VAR NAME="DHM_FILE" VALUE="%LAYER_FNAME%" REPLACE_STR="DSM=DHM"