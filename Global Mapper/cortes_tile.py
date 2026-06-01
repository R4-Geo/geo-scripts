import os
import glob
from pathlib import Path
import globalmapper

# Configuración inicial
COMUNA_SHAPE = r"C:\Users\Raster4\Desktop\Scripts\Global Mapper\AOI\ARAUCO_OTA_78.shp"
LAS_FILE = r"C:\Users\Raster4\Desktop\Scripts\Global Mapper\NP\ARAUCO_2_NP.las"
OUTPUT_DIR = r"C:\Users\Raster4\Desktop\Scripts\Global Mapper\NP\ESQUEMA_TILE"
MAX_FILE_SIZE_MB = 999

# Cargar archivos
globalmapper.LoadLayerList(COMUNA_SHAPE, 0)
globalmapper.LoadLayerList(LAS_FILE, 0)

# Obtener capas cargadas
layers = globalmapper.GetLoadedLayerList()
shape_layer = layers[0]['layer']  # Referencia correcta a la capa

# Obtener la cantidad de features para aplicar el buffer a todas
feature_count = globalmapper.GetFeatureCount(shape_layer)
feature_indices = list(range(feature_count))  # Todos los features

# Aplicar buffer de 5 metros
buffer_layer = globalmapper.CreateBufferArea(
    aFeatureLayer=shape_layer,
    aFeatureClassType="AREA",
    aFeatureIndex=feature_indices,
    aBufferDistance=5,
    aBufferLayer="Buffer_5m"
)

# Dividir por atributo 'ID'
split_layers = globalmapper.SplitLayer(buffer_layer, "ID")

for split_layer in split_layers:
    features = globalmapper.GetFeatureList(split_layer)
    if not features:
        continue

    id_value = globalmapper.GetFeatureAttrValue(features[0], "ID")
    name = f"ESQUEMA_TILE_AGI_{id_value}"

    # Renombrar capa
    globalmapper.SetLayerName(split_layer, name)

    # Crear BBOX
    bbox = globalmapper.GenerateFeatureBoundingBox(split_layer)
    width, height = bbox['width'], bbox['height']

    # Verificar tamaño del archivo LAS
    las_file_size_mb = os.path.getsize(LAS_FILE) / (1024 * 1024)
    export_path = os.path.join(OUTPUT_DIR, f"{Path(LAS_FILE).stem}_{id_value}.las")

    if las_file_size_mb <= MAX_FILE_SIZE_MB:
        globalmapper.ExportLidar(LAS_FILE, export_path, tiles=split_layer)
    else:
        rows, cols = (2, 1) if height > width else (1, 2)
        globalmapper.SubdivideFeature(split_layer, rows, cols)
        globalmapper.ExportLidar(LAS_FILE, export_path, tiles=split_layer)

        # Verificar tamaño de tiles exportados
        exported_tiles = glob.glob(os.path.join(OUTPUT_DIR, f"{Path(LAS_FILE).stem}_{id_value}_*.las"))
        for tile in exported_tiles:
            tile_size_mb = os.path.getsize(tile) / (1024 * 1024)
            if tile_size_mb > MAX_FILE_SIZE_MB:
                os.remove(tile)
                rows += 1 if height > width else 0
                cols += 1 if width >= height else 0
                globalmapper.SubdivideFeature(split_layer, rows, cols)
                globalmapper.ExportLidar(LAS_FILE, export_path, tiles=split_layer)

print("✅ Proceso finalizado.")
