#!/usr/bin/env python3
"""
Script para procesar grifos_2019.json y filtrar por Los Ángeles
Uso: python procesar_grifos.py grifos_2019.json
"""

import json
import csv
import sys
from pathlib import Path

def cargar_grifos(archivo_json):
    """Carga el archivo JSON de grifos"""
    print(f"📂 Cargando {archivo_json}...")
    with open(archivo_json, 'r', encoding='utf-8') as f:
        grifos = json.load(f)
    print(f"Cargados {len(grifos):,} grifos")
    return grifos

def filtrar_por_coordenadas(grifos, lat_min, lat_max, lng_min, lng_max):
    """Filtra grifos por bounding box"""
    filtrados = [
        g for g in grifos
        if lat_min <= g['lat'] <= lat_max and lng_min <= g['lng'] <= lng_max
    ]
    return filtrados

def filtrar_por_ubicacion(grifos, texto):
    """Filtra grifos por texto en ubicación"""
    texto_lower = texto.lower()
    filtrados = [
        g for g in grifos
        if g.get('ubicacion') and texto_lower in g['ubicacion'].lower()
    ]
    return filtrados

def exportar_csv(grifos, archivo_salida):
    """Exporta grifos a CSV"""
    if not grifos:
        print("No hay grifos para exportar")
        return

    print(f"💾 Exportando a {archivo_salida}...")

    # Obtener todas las claves
    keys = list(grifos[0].keys())

    with open(archivo_salida, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(grifos)

    print(f"CSV exportado: {archivo_salida} ({len(grifos):,} registros)")

def exportar_geojson(grifos, archivo_salida):
    """Exporta grifos a GeoJSON"""
    if not grifos:
        print("No hay grifos para exportar")
        return

    print(f"Exportando a {archivo_salida}...")

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [g['lng'], g['lat']]
                },
                "properties": {k: v for k, v in g.items() if k not in ['lat', 'lng']}
            }
            for g in grifos
        ]
    }

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    print(f"GeoJSON exportado: {archivo_salida} ({len(grifos):,} features)")

def mostrar_estadisticas(grifos):
    """Muestra estadísticas de los grifos"""
    print("\nESTADÍSTICAS:")
    print(f"Total de grifos: {len(grifos):,}")

    if not grifos:
        return

    # Estadísticas por modelo
    modelos = {}
    for g in grifos:
        modelo = g.get('modelo', 'Sin modelo')
        modelos[modelo] = modelos.get(modelo, 0) + 1

    print("\nGrifos por modelo:")
    for modelo, cantidad in sorted(modelos.items(), key=lambda x: x[1], reverse=True):
        print(f"  {modelo}: {cantidad:,}")

    # Estadísticas por año
    anios = [g.get('anio') for g in grifos if g.get('anio')]
    if anios:
        print(f"\nAño más antiguo: {min(anios)}")
        print(f"Año más reciente: {max(anios)}")

    # Diámetros
    diametros = [g.get('diam_grifo') for g in grifos if g.get('diam_grifo')]
    if diametros:
        print(f"\n🔧 Diámetros de grifo: {sorted(set(diametros))}")

def main():
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("Uso: python procesar_grifos.py <archivo_json>")
        print("\nEjemplo:")
        print("  python procesar_grifos.py grifos_2019.json")
        sys.exit(1)

    archivo_entrada = sys.argv[1]

    # Verificar que existe
    if not Path(archivo_entrada).exists():
        print(f"El archivo no existe: {archivo_entrada}")
        sys.exit(1)

    # Cargar datos
    grifos = cargar_grifos(archivo_entrada)

    # Mostrar muestra
    print("\nPrimeros 3 grifos:")
    for i, g in enumerate(grifos[:3], 1):
        print(f"\n{i}. Grifo #{g.get('grifoId')}")
        for k, v in g.items():
            print(f"   {k}: {v}")

    # FILTRAR LOS ÁNGELES
    print("\n" + "="*60)
    print("FILTRANDO GRIFOS DE LOS ÁNGELES, BÍO BÍO")
    print("="*60)

    # Coordenadas de Los Ángeles
    # Centro aproximado: -37.47, -72.35
    LOS_ANGELES_BBOX = {
        'lat_min': -37.55,
        'lat_max': -37.40,
        'lng_min': -72.45,
        'lng_max': -72.25
    }

    grifos_los_angeles = filtrar_por_coordenadas(
        grifos,
        LOS_ANGELES_BBOX['lat_min'],
        LOS_ANGELES_BBOX['lat_max'],
        LOS_ANGELES_BBOX['lng_min'],
        LOS_ANGELES_BBOX['lng_max']
    )

    print(f"Encontrados {len(grifos_los_angeles):,} grifos en Los Ángeles")

    if grifos_los_angeles:
        # Mostrar estadísticas
        mostrar_estadisticas(grifos_los_angeles)

        # Exportar
        print("\n" + "="*60)
        print("EXPORTANDO DATOS")
        print("="*60)

        exportar_csv(grifos_los_angeles, 'grifos_los_angeles.csv')
        exportar_geojson(grifos_los_angeles, 'grifos_los_angeles.geojson')

        # También exportar todos los grifos de Chile
        print("\n¿Quieres exportar TODOS los grifos de Chile? (79,000+)")
        respuesta = input("Escribe 'si' para exportar: ").strip().lower()

        if respuesta in ['si', 'sí', 's', 'yes', 'y']:
            exportar_csv(grifos, 'grifos_chile_completo.csv')
            exportar_geojson(grifos, 'grifos_chile_completo.geojson')
    else:
        print("No se encontraron grifos en las coordenadas especificadas")
        print("\nIntenta ajustar las coordenadas en el script")

    print("\nProceso completado")

if __name__ == '__main__':
    main()
