GLOBAL_MAPPER_SCRIPT VERSION=1.00

// -----------------------------------------------------------------------
// 1. Configuración de Variables
// -----------------------------------------------------------------------
DEFINE_VAR NAME="OUT_DIR" VALUE="RUTA CARPETA"

// Ruta EXACTA del archivo que YA TIENES CARGADO en Global Mapper.
// Se usa solo para identificar la capa, no para importarla de nuevo.
DEFINE_VAR NAME="SHAPE_INPUT" VALUE="ruta shape.shp"

// Variable de atributo (opcional)
DEFINE_VAR NAME="ATTR_NAME" VALUE="" 

// -----------------------------------------------------------------------
// 2. (PASO OMITIDO) Carga de Datos
// -----------------------------------------------------------------------

// COMENTAMOS O BORRAMOS ESTA LÍNEA PARA EVITAR DUPLICADOS:
// IMPORT FILENAME="%SHAPE_INPUT%"

// -----------------------------------------------------------------------
// 3. Exportación
// -----------------------------------------------------------------------

// Global Mapper buscará en las capas abiertas una que coincida con SHAPE_INPUT
// y usará sus polígonos para recortar lo que se ve en pantalla.

EXPORT_RASTER FILENAME="%OUT_DIR%_Nro.tif" TYPE=GEOTIFF \
    SPATIAL_RES=0.5,0.5 \
    COMPRESSION=LZW \
    NUM_BANDS=3 \
    BG_TRANSPARENT=NO \
    ADD_OVERVIEW_LAYERS=YES \
    GEN_WORLD_FILE=YES \
    POLYGON_CROP_FILE="%SHAPE_INPUT%" \
    POLYGON_CROP_USE_EACH=YES \
    POLYGON_CROP_BBOX_ONLY=NO \
    POLYGON_CROP_NAME_ATTR="%ATTR_NAME%" \
    FORCE_SQUARE_PIXELS=YES

// -----------------------------------------------------------------------
// Fin
// -----------------------------------------------------------------------
LOG_MESSAGE "Exportación finalizada sin duplicados."
PLAY_SOUND
