// Script para extraer coordenadas de grifos desde el visor SIG Bomberos de Chile
// Ejecutar en la consola del navegador (F12) cuando la capa "Grifos" esté visible

(function() {
    console.log('🔍 Buscando datos de grifos...');

    // Método 1: Buscar en capas de Leaflet
    function extraerDesdeLeaflet() {
        const grifos = [];

        // Buscar el mapa de Leaflet
        if (typeof L === 'undefined') {
            console.error('Leaflet no encontrado');
            return null;
        }

        // Iterar sobre todos los mapas
        const mapas = Object.keys(window).filter(k => window[k] instanceof L.Map);

        mapas.forEach(mapaKey => {
            const mapa = window[mapaKey];

            // Revisar todas las capas
            mapa.eachLayer(function(layer) {
                // Si es una capa GeoJSON o FeatureGroup
                if (layer instanceof L.GeoJSON || layer instanceof L.FeatureGroup) {
                    layer.eachLayer(function(marker) {
                        if (marker.getLatLng) {
                            const latLng = marker.getLatLng();
                            const datos = {
                                lat: latLng.lat,
                                lng: latLng.lng,
                                tipo: 'Grifo'
                            };

                            // Intentar obtener propiedades adicionales
                            if (marker.feature && marker.feature.properties) {
                                Object.assign(datos, marker.feature.properties);
                            }

                            // Obtener datos del popup si existe
                            if (marker.getPopup && marker.getPopup()) {
                                datos.popup = marker.getPopup().getContent();
                            }

                            grifos.push(datos);
                        }
                    });
                }
            });
        });

        return grifos;
    }

    // Método 2: Buscar en variables globales comunes
    function extraerDesdeVariablesGlobales() {
        const posiblesVars = ['grifos', 'features', 'markers', 'data', 'geojson', 'capas'];
        const grifos = [];

        posiblesVars.forEach(varName => {
            if (window[varName]) {
                console.log(`📦 Encontrado: window.${varName}`);
                console.log(window[varName]);
            }
        });

        return grifos;
    }

    // Método 3: Exportar a CSV
    function exportarCSV(datos) {
        if (!datos || datos.length === 0) {
            console.error('No hay datos para exportar');
            return;
        }

        // Obtener todas las claves únicas
        const keys = [...new Set(datos.flatMap(Object.keys))];

        // Crear CSV
        let csv = keys.join(',') + '\n';

        datos.forEach(item => {
            const row = keys.map(key => {
                const value = item[key] || '';
                // Escapar comillas y comas
                return `"${String(value).replace(/"/g, '""')}"`;
            });
            csv += row.join(',') + '\n';
        });

        // Descargar archivo
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'grifos_los_angeles.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        console.log(`CSV descargado con ${datos.length} registros`);
    }

    // Método 4: Exportar a GeoJSON
    function exportarGeoJSON(datos) {
        if (!datos || datos.length === 0) {
            console.error('No hay datos para exportar');
            return;
        }

        const geojson = {
            type: 'FeatureCollection',
            features: datos.map(item => ({
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: [item.lng, item.lat]
                },
                properties: Object.keys(item)
                    .filter(k => k !== 'lat' && k !== 'lng')
                    .reduce((obj, k) => ({ ...obj, [k]: item[k] }), {})
            }))
        };

        const blob = new Blob([JSON.stringify(geojson, null, 2)], { type: 'application/json' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'grifos_los_angeles.geojson');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        console.log(`GeoJSON descargado con ${datos.length} features`);
    }

    // Ejecutar extracción
    console.log('Método 1: Extrayendo desde Leaflet...');
    let grifos = extraerDesdeLeaflet();

    if (!grifos || grifos.length === 0) {
        console.log('Método 2: Buscando en variables globales...');
        extraerDesdeVariablesGlobales();
    }

    // Mostrar resultados
    if (grifos && grifos.length > 0) {
        console.log(`Se encontraron ${grifos.length} grifos`);
        console.table(grifos);

        // Guardar en variable global para acceso manual
        window.grifosExtraidos = grifos;

        console.log('\nComandos disponibles:');
        console.log('  exportarCSV(window.grifosExtraidos)    - Descargar como CSV');
        console.log('  exportarGeoJSON(window.grifosExtraidos) - Descargar como GeoJSON');

        // Preguntar si quiere exportar
        if (confirm(`Se encontraron ${grifos.length} grifos. ¿Descargar como CSV?`)) {
            exportarCSV(grifos);
        }

        return grifos;
    } else {
        console.warn('No se encontraron grifos automáticamente.');
        console.log('\nOpciones alternativas:');
        console.log('1. Verifica que la capa "Grifos" esté activa');
        console.log('2. Revisa la pestaña Network para ver peticiones a APIs');
        console.log('3. Inspecciona manualmente: window, L.map, etc.');
        return null;
    }

    // Exponer funciones globalmente
    window.exportarCSV = exportarCSV;
    window.exportarGeoJSON = exportarGeoJSON;
})();
