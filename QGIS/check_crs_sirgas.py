import os
from osgeo import gdal, ogr, osr

# Configurar GDAL para que lance excepciones en caso de error
gdal.UseExceptions()

def normalizar_epsg(spatial_ref):
    """
    Intenta extraer el código EPSG de un objeto osr.SpatialReference.
    Retorna el código como entero o None si no se puede determinar.
    """
    if spatial_ref is None:
        return None
    
    # Intentar autodetectar el EPSG si no está explícito en el WKT
    try:
        spatial_ref.AutoIdentifyEPSG()
        code = spatial_ref.GetAuthorityCode(None)
        if code:
            return int(code)
    except Exception:
        pass
    return None

def auditar_proyecciones(directorio_raiz, archivo_salida):
    """
    Itera sobre carpetas buscando SHP y TIF que no sean SIRGAS 2000 (EPSG:4674).
    """
    TARGET_EPSG = 4674
    archivos_incorrectos = []
    
    print(f"Iniciando auditoría en: {directorio_raiz}")
    print(f"Buscando archivos distintos a EPSG:{TARGET_EPSG} (SIRGAS 2000)...")

    for root, dirs, files in os.walk(directorio_raiz):
        for file in files:
            file_path = os.path.join(root, file)
            ext = file.lower().split('.')[-1]
            
            crs_code = -1 # -1 indica no procesado, None indica sin proyección
            es_geoarchivo = False

            try:
                # --- Procesamiento de Vectores (Shapefiles) ---
                if ext == 'shp':
                    es_geoarchivo = True
                    driver = ogr.GetDriverByName('ESRI Shapefile')
                    dataSource = driver.Open(file_path, 0) # 0 significa solo lectura
                    
                    if dataSource is None:
                        print(f"Error al abrir vector: {file}")
                        continue
                        
                    layer = dataSource.GetLayer()
                    spatial_ref = layer.GetSpatialRef()
                    crs_code = normalizar_epsg(spatial_ref)
                    dataSource = None # Cerrar archivo

                # --- Procesamiento de Rústers (GeoTIFF) ---
                elif ext in ['tif', 'tiff']:
                    es_geoarchivo = True
                    ds = gdal.Open(file_path, gdal.GA_ReadOnly)
                    
                    if ds is None:
                        print(f"Error al abrir raster: {file}")
                        continue
                        
                    wkt = ds.GetProjection()
                    if wkt:
                        spatial_ref = osr.SpatialReference()
                        spatial_ref.ImportFromWkt(wkt)
                        crs_code = normalizar_epsg(spatial_ref)
                    else:
                        crs_code = None # No tiene proyección definida
                    ds = None # Cerrar archivo

                # --- Evaluación ---
                if es_geoarchivo:
                    if crs_code is None:
                        archivos_incorrectos.append(f"[SIN CRS] {file_path}")
                    elif crs_code != TARGET_EPSG:
                        archivos_incorrectos.append(f"[EPSG:{crs_code}] {file_path}")

            except Exception as e:
                archivos_incorrectos.append(f"[ERROR DE LECTURA] {file_path} - {str(e)}")

    # --- Escribir Resultados ---
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write(f"REPORTE DE ARCHIVOS NO-SIRGAS 2000 (EPSG:{TARGET_EPSG})\n")
        f.write("="*60 + "\n")
        if not archivos_incorrectos:
            f.write("Todos los archivos analizados están correctamente en SIRGAS 2000.\n")
        else:
            for item in archivos_incorrectos:
                f.write(f"{item}\n")
    
    print(f"\nProceso finalizado. Se encontraron {len(archivos_incorrectos)} archivos fuera de norma.")
    print(f"Reporte guardado en: {archivo_salida}")

# --- Ejecución ---
# Ajusta estas rutas según tu entorno
carpeta_a_auditar = r"E:"
archivo_reporte = r"E:\reporte_crs.txt"

if __name__ == "__main__":
    # Verifica que la carpeta exista antes de correr
    if os.path.exists(carpeta_a_auditar):
        auditar_proyecciones(carpeta_a_auditar, archivo_reporte)
    else:
        print("La ruta especificada no existe.")