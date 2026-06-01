// Script para descargar y procesar grifos_2019.json desde la consola
// Ejecutar después de ver el archivo en la pestaña Network

(async function() {
    console.log('🔥 Descargando grifos de Chile...');

    try {
        // Intentar obtener la URL del archivo desde Network
        const performanceEntries = performance.getEntriesByType('resource');
        const grifoURL = performanceEntries.find(e => e.name.includes('grifos_2019.json'));

        let url;
        if (grifoURL) {
            url = grifoURL.name;
            console.log('✅ URL encontrada:', url);
        } else {
            // URL de respaldo (ajustar si es necesario)
            url = 'grifos_2019.json';
            console.log('⚠️ URL no encontrada en Network, usando ruta relativa');
        }

        // Descargar datos
        const response = await fetch(url);
        const grifos = await response.json();

        console.log(`✅ Descargados ${grifos.length.toLocaleString()} grifos`);
        console.table(grifos.slice(0, 3));

        // Guardar en variable global
        window.todosGrifos = grifos;

        // Análisis de columnas
        const columnas = Object.keys(grifos[0]);
        console.log('\n📊 Columnas disponibles:', columnas);

        // Función para filtrar por comuna/ciudad
        window.filtrarPorUbicacion = function(texto) {
            const filtrados = grifos.filter(g =>
                g.ubicacion && g.ubicacion.toLowerCase().includes(texto.toLowerCase())
            );
            console.log(`✅ Encontrados ${filtrados.length} grifos con "${texto}"`);
            return filtrados;
        };

        // Función para filtrar por bounding box (coordenadas)
        window.filtrarPorCoordenadas = function(latMin, latMax, lngMin, lngMax) {
            const filtrados = grifos.filter(g =>
                g.lat >= latMin && g.lat <= latMax &&
                g.lng >= lngMin && g.lng <= lngMax
            );
            console.log(`✅ Encontrados ${filtrados.length} grifos en el área`);
            return filtrados;
        };

        // Función para exportar a CSV
        window.exportarCSV = function(datos, nombreArchivo = 'grifos.csv') {
            if (!datos || datos.length === 0) {
                console.error('❌ No hay datos para exportar');
                return;
            }

            const keys = Object.keys(datos[0]);
            let csv = keys.join(',') + '\n';

            datos.forEach(item => {
                const row = keys.map(key => {
                    const value = item[key] !== null && item[key] !== undefined ? item[key] : '';
                    // Escapar comillas y comas
                    return `"${String(value).replace(/"/g, '""')}"`;
                });
                csv += row.join(',') + '\n';
            });

            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const urlBlob = URL.createObjectURL(blob);
            link.setAttribute('href', urlBlob);
            link.setAttribute('download', nombreArchivo);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            console.log(`✅ CSV descargado: ${nombreArchivo} (${datos.length} registros)`);
        };

        // Función para exportar a GeoJSON
        window.exportarGeoJSON = function(datos, nombreArchivo = 'grifos.geojson') {
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
            const urlBlob = URL.createObjectURL(blob);
            link.setAttribute('href', urlBlob);
            link.setAttribute('download', nombreArchivo);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            console.log(`✅ GeoJSON descargado: ${nombreArchivo} (${datos.length} features)`);
        };

        // COORDENADAS DE LOS ÁNGELES, BÍO BÍO
        // Los Ángeles aproximadamente: lat: -37.47, lng: -72.35
        const losAngelesBbox = {
            latMin: -37.55,  // Sur
            latMax: -37.40,  // Norte
            lngMin: -72.45,  // Oeste
            lngMax: -72.25   // Este
        };

        console.log('\n🎯 FILTRANDO GRIFOS DE LOS ÁNGELES...');
        const grifosLosAngeles = filtrarPorCoordenadas(
            losAngelesBbox.latMin,
            losAngelesBbox.latMax,
            losAngelesBbox.lngMin,
            losAngelesBbox.lngMax
        );

        if (grifosLosAngeles.length > 0) {
            console.log('\n📍 Primeros 5 grifos de Los Ángeles:');
            console.table(grifosLosAngeles.slice(0, 5));

            window.grifosLosAngeles = grifosLosAngeles;

            // Preguntar si quiere descargar
            setTimeout(() => {
                if (confirm(`¿Descargar ${grifosLosAngeles.length} grifos de Los Ángeles como CSV?`)) {
                    exportarCSV(grifosLosAngeles, 'grifos_los_angeles.csv');
                }
            }, 500);
        } else {
            console.warn('⚠️ No se encontraron grifos en las coordenadas de Los Ángeles');
            console.log('💡 Ajusta las coordenadas o usa filtrado por texto');
        }

        // Mostrar ayuda
        console.log('\n\n📋 COMANDOS DISPONIBLES:\n');
        console.log('// Ver todos los grifos descargados');
        console.log('console.table(window.todosGrifos.slice(0, 10))\n');

        console.log('// Filtrar por ubicación (texto)');
        console.log('const resultado = filtrarPorUbicacion("los angeles")');
        console.log('console.table(resultado.slice(0, 10))\n');

        console.log('// Filtrar por coordenadas');
        console.log('const resultado = filtrarPorCoordenadas(-37.55, -37.40, -72.45, -72.25)\n');

        console.log('// Exportar Los Ángeles a CSV');
        console.log('exportarCSV(window.grifosLosAngeles, "grifos_los_angeles.csv")\n');

        console.log('// Exportar Los Ángeles a GeoJSON');
        console.log('exportarGeoJSON(window.grifosLosAngeles, "grifos_los_angeles.geojson")\n');

        console.log('// Exportar TODOS los grifos de Chile');
        console.log('exportarCSV(window.todosGrifos, "grifos_chile_completo.csv")\n');

        console.log('// Estadísticas por modelo');
        console.log('const modelos = {}; todosGrifos.forEach(g => modelos[g.modelo] = (modelos[g.modelo]||0)+1); console.table(modelos)\n');

        return grifosLosAngeles;

    } catch (error) {
        console.error('❌ Error:', error);
        console.log('\n💡 SOLUCIÓN MANUAL:');
        console.log('1. En la pestaña Network, haz clic derecho en "grifos_2019.json"');
        console.log('2. Selecciona "Copy" → "Copy response"');
        console.log('3. En la consola ejecuta:');
        console.log('   window.todosGrifos = [PEGA_AQUÍ]');
        console.log('   // Luego ejecuta este script nuevamente');
    }
})();
