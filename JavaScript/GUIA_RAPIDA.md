# 🚀 Guía Rápida: Descargar Grifos de Los Ángeles

Ya encontraste el archivo `grifos_2019.json` con **79,191 grifos** de Chile.

---

## ⚡ MÉTODO 1: Script automático (30 segundos)

### Paso 1: Copiar script
Abre el archivo: `descargar_grifos_desde_network.js`

### Paso 2: En el navegador
1. En https://sig.bomberos.cl/, presiona **F12**
2. Ve a la pestaña **Console**
3. **Pega el script completo** y presiona Enter

### Paso 3: ¡Listo!
- El script descarga automáticamente los datos
- Filtra Los Ángeles (aprox. coordenadas: -37.47, -72.35)
- Te pregunta si quieres descargar el CSV
- Archivo descargado: `grifos_los_angeles.csv`

**Comandos disponibles después:**
```javascript
// Ver datos de Los Ángeles
console.table(window.grifosLosAngeles.slice(0, 10))

// Exportar CSV
exportarCSV(window.grifosLosAngeles, "grifos_los_angeles.csv")

// Exportar GeoJSON
exportarGeoJSON(window.grifosLosAngeles, "grifos_los_angeles.geojson")

// Exportar TODOS los grifos de Chile
exportarCSV(window.todosGrifos, "grifos_chile_completo.csv")
```

---

## ⚡ MÉTODO 2: Copy/Paste manual (1 minuto)

### Si el script automático no funciona:

#### Paso 1: Copiar JSON
1. En la pestaña **Network**, encuentra `grifos_2019.json`
2. **Clic derecho** → **Copy** → **Copy response**

#### Paso 2: Cargar en consola
```javascript
// Pegar el JSON copiado aquí:
window.todosGrifos = [PEGA_AQUÍ_EL_JSON]
```

#### Paso 3: Ejecutar procesador
1. Abre: `metodo_simple_copy_paste.js`
2. Copia todo el contenido
3. Pégalo en la consola
4. Presiona Enter
5. ¡Descarga automática!

---

## ⚡ MÉTODO 3: Python (si descargaste el JSON)

### Si ya descargaste `grifos_2019.json` al disco:

```bash
# Navegar a la carpeta
cd D:\RASTER4\Scripts\JavaScript

# Ejecutar script
python procesar_grifos.py grifos_2019.json
```

**El script Python:**
- ✅ Filtra grifos de Los Ángeles automáticamente
- ✅ Exporta CSV y GeoJSON
- ✅ Muestra estadísticas (modelos, años, diámetros)
- ✅ Opción de exportar todos los grifos de Chile

---

## 📊 Estructura de datos

Cada grifo tiene:

```javascript
{
  grifoId: 1,                      // ID único
  ubicacion: "LAS HIGUERAS 0555",  // Dirección
  lng: -70.90958823609252,         // Longitud
  lat: -33.655559227803685,        // Latitud
  anio: 1986,                      // Año instalación
  diam_grifo: 100,                 // Diámetro grifo (mm)
  diam_tub: 110,                   // Diámetro tubería (mm)
  modelo: "GRIFO COLUMNA"          // Tipo de grifo
}
```

---

## 🗺️ Coordenadas de Los Ángeles

El script usa este bounding box:

```
Centro: -37.47, -72.35
Área:
  Latitud:  -37.55 a -37.40  (Sur a Norte)
  Longitud: -72.45 a -72.25  (Oeste a Este)
```

**Ajustar coordenadas si es necesario:**

```javascript
// En la consola:
const grifos = filtrarPorCoordenadas(-37.60, -37.35, -72.50, -72.20)
exportarCSV(grifos, "grifos_area_personalizada.csv")
```

---

## 🎯 Archivos creados

```
D:\RASTER4\Scripts\JavaScript\
├── descargar_grifos_desde_network.js     ⭐ Script automático
├── metodo_simple_copy_paste.js           📋 Método manual
├── procesar_grifos.py                    🐍 Procesador Python
├── GUIA_RAPIDA.md                        📖 Esta guía
└── INSTRUCCIONES_EXTRACCION_GRIFOS.md   📚 Guía completa
```

---

## 💡 Tips

### Ver campos únicos en consola:
```javascript
// Modelos de grifos
const modelos = [...new Set(todosGrifos.map(g => g.modelo))]
console.log(modelos)

// Rango de años
const anios = todosGrifos.map(g => g.anio).filter(a => a)
console.log(`Años: ${Math.min(...anios)} - ${Math.max(...anios)}`)

// Diámetros disponibles
const diametros = [...new Set(todosGrifos.map(g => g.diam_grifo))]
console.log(diametros)
```

### Filtrar por múltiples criterios:
```javascript
// Grifos de Los Ángeles instalados después del 2000
const recientes = grifosLosAngeles.filter(g => g.anio >= 2000)
exportarCSV(recientes, "grifos_los_angeles_recientes.csv")

// Grifos por modelo específico
const columna = todosGrifos.filter(g => g.modelo === "GRIFO COLUMNA")
console.log(`${columna.length} grifos tipo columna`)
```

---

## ❓ Problemas comunes

### "todosGrifos is not defined"
→ Ejecuta primero el script de descarga o carga manual

### "No se encontraron grifos en Los Ángeles"
→ Ajusta las coordenadas del bounding box

### CSV con caracteres raros (ñ, á, etc)
→ Abre en Excel: Datos → Obtener datos externos → CSV → UTF-8

---

## 📞 Datos oficiales

Si necesitas datos actualizados o verificados:
- **Bomberos de Chile**: https://www.bomberos.cl/
- **Municipalidad de Los Ángeles**: www.munilosangeles.cl
- **IDE Chile**: www.ide.cl

---

**Última actualización**: 2026-01-27
**Archivo fuente**: https://sig.bomberos.cl/ → `grifos_2019.json`
**Total grifos Chile**: 79,191
