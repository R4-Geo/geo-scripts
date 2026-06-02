// MÉTODO SIMPLE: Para cuando ya copiamos el JSON manualmente
//
// PASO 1: En Network, clic derecho en "grifos_2019.json" → Copy → Copy response
// PASO 2: Ejecutar:  window.todosGrifos = [PEGAR AQUÍ EL JSON]
// PASO 3: Ejecutar este script

(function() {
    if (!window.todosGrifos) {
        console.error('Primero debes cargar los datos en window.todosGrifos');
        console.log('\nPASOS:');
        console.log('1. En Network → clic derecho en "grifos_2019.json"');
        console.log('2. Copy → Copy response');
        console.log('3. En consola: window.todosGrifos = [PEGA_AQUÍ]');
        console.log('4. Ejecuta este script nuevamente');
        return;
    }

    console.log(`Cargados ${window.todosGrifos.length.toLocaleString()} grifos`);

    // Función para exportar a CSV
    function exportarCSV(datos, nombreArchivo = 'grifos.csv') {
        const keys = Object.keys(datos[0]);
        let csv = keys.join(',') + '\n';
        datos.forEach(item => {
            const row = keys.map(key => `"${(item[key] ?? '').toString().replace(/"/g, '""')}"`);
            csv += row.join(',') + '\n';
        });
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = nombreArchivo;
        a.click();
        console.log(`Descargado: ${nombreArchivo}`);
    }

    // Función para exportar a GeoJSON
    function exportarGeoJSON(datos, nombreArchivo = 'grifos.geojson') {
        const geojson = {
            type: 'FeatureCollection',
            features: datos.map(g => ({
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [g.lng, g.lat] },
                properties: { ...g, lat: undefined, lng: undefined }
            }))
        };
        const blob = new Blob([JSON.stringify(geojson, null, 2)], { type: 'application/json' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = nombreArchivo;
        a.click();
        console.log(`Descargado: ${nombreArchivo}`);
    }

    // FILTRAR LOS ÁNGELES
    // Coordenadas aproximadas: -37.47, -72.35
    const grifosLosAngeles = window.todosGrifos.filter(g =>
        g.lat >= -37.55 && g.lat <= -37.40 &&
        g.lng >= -72.45 && g.lng <= -72.25
    );

    console.log(`Encontrados ${grifosLosAngeles.length} grifos en Los Ángeles`);
    console.table(grifosLosAngeles.slice(0, 5));

    window.grifosLosAngeles = grifosLosAngeles;

    // Exponer funciones
    window.exportarCSV = exportarCSV;
    window.exportarGeoJSON = exportarGeoJSON;

    // Ofrecer descarga
    if (confirm(`¿Descargar ${grifosLosAngeles.length} grifos de Los Ángeles como CSV?`)) {
        exportarCSV(grifosLosAngeles, 'grifos_los_angeles.csv');
    }

    console.log('\nCOMANDOS:');
    console.log('exportarCSV(grifosLosAngeles, "grifos_los_angeles.csv")');
    console.log('exportarGeoJSON(grifosLosAngeles, "grifos_los_angeles.geojson")');
    console.log('exportarCSV(todosGrifos, "grifos_chile_completo.csv")');
})();
