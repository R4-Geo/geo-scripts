# Guía: Extraer datos de grifos desde SIG Bomberos de Chile

## Objetivo
Descargar las coordenadas de los grifos de la comuna de Los Ángeles, Bío Bío desde https://sig.bomberos.cl/

===

## Método 1: Interceptar peticiones

### Paso 1: Preparar la consola
1. Abrir https://sig.bomberos.cl/ en Chrome/Edge/Firefox
2. Presionar **F12** para abrir DevTools
3. Ir a la pestaña **Console**

### Paso 2: Ejecutar el interceptor
1. Abrir el archivo `interceptar_peticiones_grifos.js`
2. Copiar TODO el contenido
3. Pegar en la consola y presiona Enter
4. Debería verse: `Interceptor de peticiones activado`

### Paso 3: Activar la capa
1. En el mapa, navegar a **Los Ángeles, Bío Bío**
2. Buscar y **activar la capa "Grifos"**
3. El script automáticamente capturará las peticiones

### Paso 4: Verificar y exportar
- Si encuentra datos, se verá: `Se encontraron X features`
- Los datos estarán en `window.grifosCapturados`
- Aparecerá un diálogo para descargar CSV automáticamente
- O ejecutar manualmente:
  ```javascript
  exportarCSV(window.grifosCapturados)
  // o
  exportarGeoJSON(window.grifosCapturados)
  ```

---

## Método 2: Extraer desde el mapa cargado

Si la capa ya está visible:

### Paso 1
1. Asegurarse de que la capa "Grifos" está activa
2. Abrir la consola (F12)

### Paso 2
1. Copiar el contenido de `extraer_grifos_bomberos.js`
2. Pegarlo en la consola y presionar Enter

### Paso 3
- El script buscará automáticamente los datos en el mapa
- Si los encuentra, mostrará una tabla con los primeros registros
- Descargará automáticamente un CSV

---

## Método 3: Inspección manual de Network

Si los scripts no funcionan:

### Paso 1: Limpiar y preparar
1. Abrir https://sig.bomberos.cl/
2. Abrir DevTools (F12) → pestaña **Network**
3. Marcar la casilla **Preserve log**
4. Filtrar por **Fetch/XHR**

### Paso 2: Activar capa y buscar
1. Navegar a Los Ángeles
2. Activar la capa "Grifos"
3. Buscar en la lista de peticiones URLs que contengan:
   - `geojson`
   - `wfs` o `wms`
   - `features`
   - `query`
   - `geoserver` o `arcgis`

### Paso 3: Inspeccionar respuesta
1. Clic en la petición sospechosa
2. Ir a la pestaña **Response** o **Preview**
3. Si se ve coordenadas/geometrías, se encontraron los datos

### Paso 4: Copiar datos
1. **Opción A**: Clic derecho → Copy response
2. **Opción B**: En la consola ejecutar:
   ```javascript
   copy(await (await fetch('URL_DE_LA_PETICION')).json())
   ```
3. Pegar en un editor de texto y guardar como `.json`

### Paso 5: Convertir a CSV (si es necesario)
Si se obtuvo un GeoJSON, ejecutar en la consola:

```javascript
// Pegar JSON aquí
const data = { /* tu geojson */ };

const features = data.features || data;
const grifos = features.map(f => ({
    lng: f.geometry.coordinates[0],
    lat: f.geometry.coordinates[1],
    ...f.properties
}));

// Convertir a CSV
const keys = Object.keys(grifos[0]);
const csv = [
    keys.join(','),
    ...grifos.map(row => keys.map(k => `"${row[k] || ''}"`).join(','))
].join('\n');

// Descargar
const blob = new Blob([csv], { type: 'text/csv' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'grifos_los_angeles.csv';
a.click();
```

---

## Solución de problemas

### No se capturan peticiones
- ✅ Verificar que la capa esté **realmente activa**
- ✅ Intentar hacer zoom in/out para forzar recarga
- ✅ Recargar la página y ejecutar el interceptor ANTES de activar la capa

### Script no encuentra grifos
- ✅ Los datos podrían cargarse por tiles/chunks
- ✅ Probar hacer más zoom para cargar más detalles
- ✅ Usar el Método 3 (inspección manual)

### Peticiones a dominios externos
Si se encuentran peticiones a servicios como:
- `geoserver.bomberos.cl`
- `arcgis.com`
- `mapserver.algo.cl`

Copiar la URL completa y probar:
```javascript
fetch('URL_COMPLETA')
    .then(r => r.json())
    .then(data => {
        console.log(data);
        window.datosCrudos = data;
    });
```

---

## Formato esperado

### CSV resultante
```csv
id,lat,lng,direccion,tipo,caudal,estado
1,-37.469517,-72.354289,"Av. Principal 123","Público",1000,"Operativo"
```

### GeoJSON resultante
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-72.354289, -37.469517]
      },
      "properties": {
        "id": 1,
        "direccion": "Av. Principal 123",
        "tipo": "Público"
      }
    }
  ]
}
```

---

## Notas legales

- Este método es solo para consulta de datos públicos
- Respetar los términos de servicio del sitio
- No sobrecargar el servidor con peticiones masivas
- Usar los datos de manera responsable

---

## Alternativas

Si nada funciona, considerar:

1. **Contactar a Bomberos de Chile**: Solicitar los datos directamente
2. **SNIT (Sistema Nacional de Información Territorial)**: Podría tener los datos
3. **Municipalidad de Los Ángeles**: Departamento de Emergencias
4. **IDE Chile**: Infraestructura de Datos Espaciales

---

## Conceptos útiles

- **GeoJSON**: Formato estándar para datos geoespaciales
- **WFS**: Web Feature Service - protocolo para compartir features
- **Leaflet**: Biblioteca JavaScript para mapas interactivos
- **Feature**: Un objeto geográfico (punto, línea, polígono)

---

**Creado**: 2026-01-27
**Sitio**: https://sig.bomberos.cl/
**Comuna**: Los Ángeles, Bío Bío
