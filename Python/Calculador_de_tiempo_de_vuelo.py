import arcpy

# 1. Definir los rendimientos de cada equipo (minutos por hectárea)
rendimiento_mavic = 30.0 / 80.0     # 0.375 min/ha
rendimiento_trinity = 60.0 / 600.0  # 0.1 min/ha
rendimiento_evocam = 120.0 / 1100.0 # ~0.109 min/ha

# Ventana de vuelo: 10:00 am a 16:00 pm = 6 horas = 360 minutos diarios
# Asumiendo el peor horario de invierno
minutos_por_dia = 6.0 * 60.0

# Rutas de los shapefiles, agregar los que sean necesarios
shapefiles = [
    r"RUTA SHAPE 1.shp",
    r"RUTA SHAPE 2.shp",
    r"RUTA SHAPE 3.shp",
    r"RUTA SHAPE 4.shp"
]

total_general_hectareas = 0
total_general_entidades = 0

arcpy.AddMessage("Iniciando actualización de tablas de atributos...")

for shp in shapefiles:
    try:
        # 2. Definir los campos a agregar: Nombre del campo y su Alias
        # Nota: Los shapefiles tienen un límite de 10 caracteres para el nombre del campo.
        campos_requeridos = {
            "Area_h": "Área (Hectáreas)",
            "T_Mavic_hr": "Hrs Vuelo Mavic 3 Pro",
            "T_Trin_hr": "Hrs Vuelo Trinity Pro",
            "T_Evo_hr": "Hrs Vuelo EVOCAM"
        }
        
        # Obtener lista de campos existentes para no duplicarlos
        campos_existentes = [campo.name for campo in arcpy.ListFields(shp)]
        
        # 3. Agregar los campos si no existen
        for nombre_campo, alias_campo in campos_requeridos.items():
            if nombre_campo not in campos_existentes:
                arcpy.management.AddField(shp, nombre_campo, "DOUBLE", field_alias=alias_campo)
                
        # 4. Calcular el Área Geodésica en Hectáreas primero
        arcpy.management.CalculateGeometryAttributes(
            in_features=shp, 
            geometry_property=[["Area_h", "AREA_GEODESIC"]], 
            area_unit="HECTARES"
        )
        
        area_total_shp = 0.0
        conteo_entidades = 0
        
        # 5. Usar UpdateCursor para calcular y escribir los tiempos por entidad
        # Los tiempos se guardarán en HORAS para facilitar la lectura en la tabla de atributos
        campos_cursor = ["Area_h", "T_Mavic_hr", "T_Trin_hr", "T_Evo_hr"]
        
        with arcpy.da.UpdateCursor(shp, campos_cursor) as cursor:
            for row in cursor:
                area = row[0]
                if area is not None and area > 0:
                    # Fórmula: (Área * Rendimiento) / 60 para convertir minutos a horas
                    hrs_mavic = (area * rendimiento_mavic) / 60.0
                    hrs_trinity = (area * rendimiento_trinity) / 60.0
                    hrs_evocam = (area * rendimiento_evocam) / 60.0
                    
                    # Actualizar los valores en la fila
                    row[1] = hrs_mavic
                    row[2] = hrs_trinity
                    row[3] = hrs_evocam
                    cursor.updateRow(row)
                    
                    # Sumar a los totales globales
                    area_total_shp += area
                    conteo_entidades += 1
                else:
                    # Manejo de geometrías nulas o de área cero
                    row[1] = 0.0
                    row[2] = 0.0
                    row[3] = 0.0
                    cursor.updateRow(row)
                    
        total_general_hectareas += area_total_shp
        total_general_entidades += conteo_entidades
        
        # 6. Imprimir resumen en consola para seguimiento
        nombre_archivo = shp.split("\\")[-1]
        print(f"\n--- Atributos actualizados con éxito en: {nombre_archivo} ---")
        print(f"Entidades procesadas: {conteo_entidades}")
        print(f"Área Total: {area_total_shp:,.2f} hectáreas")
        
    except Exception as e:
        print(f"\nError procesando {shp}: {str(e)}")

# Resumen General
print("\n" + "="*50)
print("PROCESO DE ESCRITURA FINALIZADO")
print("="*50)
print(f"Total de entidades actualizadas: {total_general_entidades}")
print(f"Total de área registrada: {total_general_hectareas:,.2f} hectáreas")
print("="*50)
