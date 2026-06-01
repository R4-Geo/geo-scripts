// Script para interceptar peticiones de red y capturar datos de grifos
// Ejecutar ANTES de activar la capa "Grifos" en el visor

(function() {
    console.log('🎯 Interceptor de peticiones activado');
    console.log('👉 Ahora activa la capa "Grifos" en el mapa\n');

    const peticionesCapturadas = [];

    // Interceptar fetch
    const fetchOriginal = window.fetch;
    window.fetch = function(...args) {
        const url = args[0];

        console.log('📡 Fetch:', url);

        return fetchOriginal.apply(this, args).then(response => {
            // Clonar para no consumir el stream
            const responseClone = response.clone();

            // Verificar si podría contener datos de grifos
            if (url.toString().match(/grifo|feature|geojson|wfs|geoserver|arcgis/i) ||
                response.headers.get('content-type')?.includes('json')) {

                responseClone.json().then(data => {
                    console.log('📦 Datos recibidos de:', url);
                    console.log(data);

                    peticionesCapturadas.push({
                        url: url.toString(),
                        data: data,
                        timestamp: new Date().toISOString()
                    });

                    // Intentar extraer features
                    extraerFeatures(data, url);
                }).catch(err => {
                    // No es JSON, ignorar
                });
            }

            return response;
        });
    };

    // Interceptar XMLHttpRequest
    const xhrOriginal = window.XMLHttpRequest;
    function XMLHttpRequestProxy() {
        const xhr = new xhrOriginal();
        const originalOpen = xhr.open;
        const originalSend = xhr.send;
        let requestURL = '';

        xhr.open = function(method, url) {
            requestURL = url;
            console.log('📡 XHR:', method, url);
            return originalOpen.apply(this, arguments);
        };

        xhr.send = function() {
            const originalOnload = xhr.onload;

            xhr.onload = function() {
                if (xhr.responseType === '' || xhr.responseType === 'text' || xhr.responseType === 'json') {
                    try {
                        const data = JSON.parse(xhr.responseText);

                        if (requestURL.match(/grifo|feature|geojson|wfs|geoserver|arcgis/i)) {
                            console.log('📦 Datos XHR de:', requestURL);
                            console.log(data);

                            peticionesCapturadas.push({
                                url: requestURL,
                                data: data,
                                timestamp: new Date().toISOString()
                            });

                            extraerFeatures(data, requestURL);
                        }
                    } catch (e) {
                        // No es JSON
                    }
                }

                if (originalOnload) {
                    return originalOnload.apply(this, arguments);
                }
            };

            return originalSend.apply(this, arguments);
        };

        return xhr;
    }
    window.XMLHttpRequest = XMLHttpRequestProxy;

    // Función para extraer features de diferentes formatos
    function extraerFeatures(data, source) {
        let features = [];

        // GeoJSON estándar
        if (data.type === 'FeatureCollection' && data.features) {
            features = data.features;
        }
        // Array de features
        else if (Array.isArray(data) && data[0]?.geometry) {
            features = data;
        }
        // ArcGIS REST API format
        else if (data.features && Array.isArray(data.features)) {
            features = data.features.map(f => ({
                type: 'Feature',
                geometry: f.geometry,
                properties: f.attributes || f.properties || {}
            }));
        }
        // WFS GetFeature response
        else if (data.features || data.members) {
            features = data.features || data.members;
        }

        if (features.length > 0) {
            console.log(`✅ Se encontraron ${features.length} features en ${source}`);

            // Convertir a formato simple con lat/lng
            const grifos = features.map((feature, index) => {
                let coords;

                // Extraer coordenadas según el tipo de geometría
                if (feature.geometry) {
                    if (feature.geometry.type === 'Point') {
                        coords = feature.geometry.coordinates;
                    } else if (feature.geometry.x !== undefined) {
                        // ArcGIS format
                        coords = [feature.geometry.x, feature.geometry.y];
                    }
                }

                return {
                    id: feature.id || feature.properties?.id || index,
                    lng: coords?.[0],
                    lat: coords?.[1],
                    ...feature.properties
                };
            });

            console.table(grifos.slice(0, 5)); // Mostrar primeros 5
            console.log(`\n💾 Datos guardados en: window.grifosCapturados`);

            // Guardar en variable global
            window.grifosCapturados = grifos;
            window.peticionesGrifos = peticionesCapturadas;

            // Preguntar si quiere exportar
            if (grifos.length > 0) {
                setTimeout(() => {
                    if (confirm(`Se capturaron ${grifos.length} grifos. ¿Descargar como CSV?`)) {
                        exportarCSV(grifos);
                    }
                }, 500);
            }
        }
    }

    // Función para exportar a CSV
    function exportarCSV(datos) {
        if (!datos || datos.length === 0) {
            console.error('❌ No hay datos para exportar');
            return;
        }

        const keys = [...new Set(datos.flatMap(Object.keys))];
        let csv = keys.join(',') + '\n';

        datos.forEach(item => {
            const row = keys.map(key => {
                const value = item[key] || '';
                return `"${String(value).replace(/"/g, '""')}"`;
            });
            csv += row.join(',') + '\n';
        });

        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `grifos_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        console.log(`✅ CSV descargado con ${datos.length} registros`);
    }

    // Función para exportar a GeoJSON
    function exportarGeoJSON(datos) {
        if (!datos || datos.length === 0) {
            console.error('❌ No hay datos para exportar');
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
        link.setAttribute('download', `grifos_${new Date().toISOString().split('T')[0]}.geojson`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        console.log(`✅ GeoJSON descargado con ${datos.length} features`);
    }

    // Exponer funciones globalmente
    window.exportarCSV = exportarCSV;
    window.exportarGeoJSON = exportarGeoJSON;

    console.log('\n📋 Variables globales disponibles:');
    console.log('  window.grifosCapturados    - Datos de grifos capturados');
    console.log('  window.peticionesGrifos    - Todas las peticiones interceptadas');
    console.log('\n📋 Funciones disponibles:');
    console.log('  exportarCSV(window.grifosCapturados)');
    console.log('  exportarGeoJSON(window.grifosCapturados)');
})();
