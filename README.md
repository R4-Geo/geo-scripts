# 🌍 geo-scripts

Colección de scripts y herramientas para **SIG, fotogrametría y geomática**, organizados por software y lenguaje de programación. Reúne automatizaciones desarrolladas para flujos de trabajo de cartografía, procesamiento de nubes de puntos, generación de modelos digitales y extracción de datos geoespaciales.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![ArcGIS](https://img.shields.io/badge/ArcGIS-ArcPy-2C7AC3?logo=arcgis&logoColor=white)
![QGIS](https://img.shields.io/badge/QGIS-PyQGIS-589632?logo=qgis&logoColor=white)
![AutoCAD](https://img.shields.io/badge/AutoCAD-LISP-E51050?logo=autodesk&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📁 Estructura del repositorio

| Carpeta | Software / Lenguaje | Contenido |
|---|---|---|
| **`ArcGIS (ArcPy)/`** | ArcGIS Pro · ArcPy | Toolboxes `.pyt`/`.atbx` y scripts: contador de entidades, tiling de cartografía, corte de ráster por campo, herramientas de edificaciones, coordenadas extremas y conversión de herramientas QGIS↔ArcPy. |
| **`QGIS/`** | QGIS · PyQGIS · GDAL | Cálculo de densidad de nubes de puntos LAS/LAZ y verificación de sistemas de referencia (CRS SIRGAS). |
| **`Metashape/`** | Agisoft Metashape | Exportación de DEM, ortomosaicos, nubes de puntos y referencias; selección y limpieza de cámaras. Incluye los scripts oficiales de ejemplo. |
| **`Global Mapper/`** | Global Mapper | Scripts `.gms` y Python: generación de DHM, carga múltiple de TIF, tiling y exportación de basemaps. |
| **`AutoCAD (LISP)/`** | AutoCAD · AutoLISP/VLX | Rutinas: aplanar cotas a 0, importar shapefiles e imágenes satelitales, JOIN, reticulado y exportación de tablas. |
| **`JavaScript/`** | JavaScript (navegador) | Extracción de datos geográficos desde la web interceptando peticiones de red (grifos de bomberos, puntos de reciclaje). |
| **`Contabilizar imágenes capturadas/`** | Python | Conteo de imágenes capturadas en campañas de vuelo con dron. |
| **`Python/`** | Python | Utilidades generales (cálculo de tiempo de vuelo y otras). |

---

## 🚀 Uso

Cada carpeta agrupa scripts por entorno de ejecución:

- **ArcPy / QGIS / Metashape / Global Mapper** → ejecutar dentro del intérprete de Python del software correspondiente.
- **AutoCAD (LISP)** → cargar las rutinas con `APPLOAD` en AutoCAD.
- **JavaScript** → ejecutar en la consola de DevTools del navegador.

Revisa la cabecera de cada script para ver requisitos, autor y descripción detallada.

---

## 📦 Datos

Por su tamaño, los **datos de muestra** (`.las`, `.tif`, geodatabases `.gdb`, archivos comprimidos) **no se incluyen** en el repositorio (ver `.gitignore`). Los scripts esperan que proporciones tus propias capas de entrada.

---

## 📄 Licencia

Distribuido bajo licencia **MIT**. Consulta el archivo [`LICENSE`](LICENSE).

---

**Autor:** Daniel Labraña Trujillo
