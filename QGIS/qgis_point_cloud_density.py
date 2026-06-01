"""
===============================================================================
Idioma: Español
Nombre del Script: qgis_point_cloud_density.py
Descripción:     Calcula la densidad de puntos para una capa de nube de puntos
                 (LAS/LAZ) seleccionada en QGIS. Muestra el recuento total
                 de puntos, el área del extent y la densidad de puntos por
                 unidad de área del SRC de la capa.
                 Advierte si el SRC no está definido o no es adecuado.

Autor:           Daniel Labraña Trujillo
Fecha:           2025-05-29
Versión:         1.1

Requisitos:
    - QGIS 3.x
    - Una capa de nube de puntos (.LAS, .LAZ) cargada en el proyecto.

Uso:
    1. Abre QGIS y carga tu capa de nube de puntos.
    2. Asegúrate de que la capa de nube de puntos deseada esté SELECCIONADA
       en el Panel de Capas.
    3. Abre la Consola de Python de QGIS (Complementos -> Consola de Python).
    4. Haz clic en el botón 'Mostrar editor' (icono de libreta).
    5. Copia y pega este script completo en la ventana del editor.
    6. Haz clic en el botón 'Ejecutar script' (icono de reproducción verde).
    7. Los resultados se imprimirán en la consola y se mostrarán en una
       barra de mensajes en QGIS. Revisa también el panel de 'Mensajes de Registro'.

Notas:
    - El script obtiene el recuento total de puntos directamente del proveedor
      de datos de la capa.
    - Calcula el área basándose en el 'extent' (extensión) de la capa.
    - Verifica la validez y las unidades del Sistema de Coordenadas de
      Referencia (SRC) de la capa.
    - Si el SRC no está definido o usa unidades angulares (grados), la
      densidad calculada podría no ser cartográficamente significativa y se
      mostrará una advertencia.
    - Es crucial que la capa tenga un SRC proyectado con unidades lineales
      (metros, pies, etc.) para una interpretación correcta de la densidad.
===============================================================================
"""

# Import necessary QGIS modules
from qgis.core import QgsPointCloudLayer, QgsMessageLog, Qgis

# Get the currently active layer in QGIS interface
# Ensure the desired LAS/LAZ layer is selected in the Layers Panel
layer = iface.activeLayer()

# Check if a layer is actually selected
if not layer:
    message = "No layer selected. Please select a point cloud layer in the Layers Panel."
    iface.messageBar().pushMessage("Error", message, level=Qgis.Critical, duration=5)
    QgsMessageLog.logMessage(message, 'PointDensityScript', level=Qgis.Critical)
    print(message)
# Check if the selected layer is a Point Cloud layer
elif isinstance(layer, QgsPointCloudLayer):
    try:
        # Access the data provider for the layer
        provider = layer.dataProvider()

        # Get the total number of points from the provider
        # This is generally more accurate for the full count than sampledPointsCount()
        point_count = provider.pointCount()

        # Get the extent of the layer
        extent = layer.extent()

        # Get the Coordinate Reference System (CRS) of the layer
        crs = layer.crs()
        crs_authid = crs.authid()
        crs_units = crs.mapUnits() # Get the units of the CRS

        # Print CRS information for verification
        print(f"Layer Name: {layer.name()}")
        print(f"Layer CRS: {crs_authid}")
        print(f"CRS Units: {QgsUnitTypes.encodeUnit(crs_units)}") # Prints human-readable unit

        # Calculate the area of the extent
        # It's crucial to ensure the CRS units are appropriate (e.g., meters) for area calculation
        area = extent.width() * extent.height()

        # Initialize density
        density_per_unit_area = 0

        # Avoid division by zero if the area is zero (e.g., if the layer has no extent or is invalid)
        if area > 0:
            density_per_unit_area = point_count / area
        else:
            print("Warning: Layer extent area is zero. Cannot calculate density.")
            QgsMessageLog.logMessage(f"Layer '{layer.name()}' has zero extent area.", 'PointDensityScript', level=Qgis.Warning)


        # Output the results
        print(f"Total Points (from provider): {point_count}")
        # Determine the unit string based on CRS
        unit_str = QgsUnitTypes.encodeUnit(crs_units).lower() # e.g., "meters", "feet"
        if not unit_str: # Fallback if unit is unknown
            unit_str = "units"

        print(f"Extent Area: {area:.2f} square {unit_str}")
        print(f"Point Density: {density_per_unit_area:.4f} points/square {unit_str}")

        # Display results in QGIS message bar for better visibility
        iface.messageBar().pushMessage(
            "Point Cloud Density",
            f"Layer: {layer.name()}\n"
            f"Total Points: {point_count}\n"
            f"Extent Area: {area:.2f} sq {unit_str}\n"
            f"Density: {density_per_unit_area:.4f} points/sq {unit_str}",
            level=Qgis.Info,
            duration=10 # Show message for 10 seconds
        )

    except Exception as e:
        error_message = f"An error occurred: {e}"
        iface.messageBar().pushMessage("Error", error_message, level=Qgis.Critical, duration=5)
        QgsMessageLog.logMessage(error_message, 'PointDensityScript', level=Qgis.Critical)
        print(error_message)

else:
    message = "The selected layer is not a Point Cloud layer. Please select a valid .LAS or .LAZ file."
    iface.messageBar().pushMessage("Error", message, level=Qgis.Critical, duration=5)
    QgsMessageLog.logMessage(message, 'PointDensityScript', level=Qgis.Critical)
    print(message)
