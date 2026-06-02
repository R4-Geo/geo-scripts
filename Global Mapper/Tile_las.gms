GLOBAL_MAPPER_SCRIPT VERSION=1.00

// ===========================
// Definir variables
// ===========================
DEFINE_VAR NAME="COMUNA_SHAPE" VALUE="ruta.shp"
DEFINE_VAR NAME="LAS_FOLDER" VALUE="CARPETA CON ARCHIVOS LAS"  // Carpeta con archivos LAS
DEFINE_VAR NAME="OUTPUT_DIR" VALUE="CARPETA CON SALIDA LAS" // Carpeta salida Tiles LAS
DEFINE_VAR NAME="MAX_FILE_SIZE_MB" VALUE="999"

// ===========================
// Paso 1: Cargar shapes
// ===========================
IMPORT FILENAME="%COMUNA_SHAPE%"

// ===========================
// Paso 2: Crear buffer de 5 metros
// ===========================
EDIT_VECTOR FILENAME="%COMUNA_SHAPE%" BUFFER_DIST=5 NEW_LAYER_NAME="Buffer_5m"

LAYER_LOOP_START FILENAME="*" VAR_NAME_PREFIX="HIDE"
    SET_LAYER_OPTIONS FILENAME="%HIDE_FNAME_W_DIR%" HIDDEN=YES
	SET_LAYER_OPTIONS FILENAME="Buffer_5m" HIDDEN=NO
LAYER_LOOP_END

EXPORT_VECTOR FILENAME="RUTA SHAPE.shp" SPLIT_BY_ATTR=YES FILENAME_ATTR="ID" TYPE=SHAPEFILE
UNLOAD_ALL

IMPORT_DIR_TREE DIRECTORY="CARPETA DE IMPORTACION" TYPE=SHAPEFILE

LAYER_LOOP_START
    GENERATE_LAYER_BOUNDS FILENAME="CARPETA DESTINO / %LAYER_FNAME_W_DIR%"
LAYER_LOOP_END

// IMPORT_DIR_TREE DIRECTORY="%LAS_FOLDER%" TYPE="LIDAR_LAS"  // Carga todos los archivos LAS de la carpeta
// ===========================
// Paso 3: Asignar nombre a cada feature y crear nuevas capas según el campo "Name"
// ===========================
// Iterador: recorre los valores de 1 al X, asumiendo que esos son los IDs a procesar //
// EXPORT_VECTOR FILENAME="CARPETA DESTINO/%COMUNA_SHAPE%_buffer_id_%CURRENT_ID%.shp" SPLIT_BY_ATTR="ID" TYPE=SHAPE 


//VAR_LOOP_START VAL_START=1 VAL_STOP=7 VAL_STEP=1 VAR_NAME="CURRENT_ID"  

    // Exporta el feature cuyo campo ID es igual al valor actual del iterador  
 //   EXPORT_VECTOR FILENAME="CARPETA DESTINO/%COMUNA_SHAPE%_buffer_id_%CURRENT_ID%.shp" SPLIT_BY_ATTR="ID" TYPE=SHAPE 
//VAR_LOOP_END

// ===========================
// Paso 4: Genera un BBOX rectangular alrededor del polígono de cada área de interés
// ===========================
// Iterador: recorre cada vector exportado (por ejemplo, con ID de 1 a 50) 
//VAR_LOOP_START VAL_START=1 VAL_STOP=7 VAL_STEP=1 VAR_NAME="CURRENT_ID" 

    // Para cada vector, genera el bounding box rectangular 
  //  GENERATE_LAYER_BOUNDS INPUT_FILENAME="CARPETA ORIGEN\%COMUNA_SHAPE%_buffer_id_%CURRENT_ID%.shp"
  //  OUTPUT_FILENAME="CARPETA DESTINO\%COMUNA_SHAPE%_bbox_%CURRENT_ID%.shp" METHOD=BBOX

//VAR_LOOP_END

###### SELECT - Select all features in Select Layer(s) with digitizer tool
