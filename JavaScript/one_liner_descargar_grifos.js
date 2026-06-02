// ============================================================================
// ONE-LINER: Descargar grifos de Los Ángeles
// Copiar y pegar esta línea completa en la consola del navegador
// ============================================================================

fetch('grifos_2019.json').then(r=>r.json()).then(d=>{window.todosGrifos=d;const g=d.filter(x=>x.lat>=-37.55&&x.lat<=-37.40&&x.lng>=-72.45&&x.lng<=-72.25);console.log(`Encontrados ${g.length} grifos en Los Ángeles`);window.grifosLosAngeles=g;const k=Object.keys(g[0]);const csv=k.join(',')+'\n'+g.map(r=>k.map(c=>`"${(r[c]??'').toString().replace(/"/g,'""')}"`).join(',')).join('\n');const b=new Blob([csv],{type:'text/csv'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='grifos_los_angeles.csv';a.click();console.log('✅ CSV descargado')});


// ============================================================================
// VERSIÓN LEGIBLE (hace lo mismo que el one-liner de arriba)
// ============================================================================

(async function() {
    // Descargar JSON
    const response = await fetch('grifos_2019.json');
    const todosGrifos = await response.json();
    window.todosGrifos = todosGrifos;

    console.log(`Total grifos Chile: ${todosGrifos.length.toLocaleString()}`);

    // Filtrar Los Ángeles (Bío Bío)
    const grifosLosAngeles = todosGrifos.filter(g =>
        g.lat >= -37.55 && g.lat <= -37.40 &&
        g.lng >= -72.45 && g.lng <= -72.25
    );

    console.log(`Grifos en Los Ángeles: ${grifosLosAngeles.length}`);
    window.grifosLosAngeles = grifosLosAngeles;

    // Convertir a CSV
    const keys = Object.keys(grifosLosAngeles[0]);
    const csv = [
        keys.join(','),
        ...grifosLosAngeles.map(row =>
            keys.map(key => `"${(row[key] ?? '').toString().replace(/"/g, '""')}"`).join(',')
        )
    ].join('\n');

    // Descargar
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'grifos_los_angeles.csv';
    link.click();

    console.log('CSV descargado: grifos_los_angeles.csv');
    console.table(grifosLosAngeles.slice(0, 5));
})();


// ============================================================================
// FUNCIONES ÚTILES ADICIONALES
// ============================================================================

// Descargar JSON completo de Chile
function descargarJSONCompleto() {
    const json = JSON.stringify(window.todosGrifos, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'grifos_2019_completo.json';
    a.click();
    console.log('JSON completo descargado');
}

// Exportar como GeoJSON
function exportarGeoJSON(grifos, nombre = 'grifos.geojson') {
    const geojson = {
        type: 'FeatureCollection',
        features: grifos.map(g => ({
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [g.lng, g.lat] },
            properties: { grifoId: g.grifoId, ubicacion: g.ubicacion, modelo: g.modelo, anio: g.anio, diam_grifo: g.diam_grifo, diam_tub: g.diam_tub }
        }))
    };
    const blob = new Blob([JSON.stringify(geojson, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = nombre;
    a.click();
    console.log(`GeoJSON descargado: ${nombre}`);
}

// Buscar grifos en área personalizada
function buscarEnArea(latMin, latMax, lngMin, lngMax) {
    const resultado = window.todosGrifos.filter(g =>
        g.lat >= latMin && g.lat <= latMax &&
        g.lng >= lngMin && g.lng <= lngMax
    );
    console.log(`Encontrados ${resultado.length} grifos en el área`);
    console.table(resultado.slice(0, 10));
    return resultado;
}

// Buscar por texto en ubicación
function buscarPorUbicacion(texto) {
    const resultado = window.todosGrifos.filter(g =>
        g.ubicacion && g.ubicacion.toLowerCase().includes(texto.toLowerCase())
    );
    console.log(`Encontrados ${resultado.length} grifos con "${texto}"`);
    console.table(resultado.slice(0, 10));
    return resultado;
}

// Estadísticas por comuna (aproximado, basado en coordenadas)
function analizarPorRegion() {
    const regiones = {
        'Santiago': { lat: [-33.7, -33.3], lng: [-71.0, -70.5] },
        'Valparaíso': { lat: [-33.2, -32.9], lng: [-71.8, -71.4] },
        'Concepción': { lat: [-36.9, -36.7], lng: [-73.2, -72.9] },
        'Los Ángeles': { lat: [-37.55, -37.40], lng: [-72.45, -72.25] },
        'Temuco': { lat: [-38.8, -38.6], lng: [-72.7, -72.5] },
    };

    Object.entries(regiones).forEach(([nombre, coords]) => {
        const count = window.todosGrifos.filter(g =>
            g.lat >= coords.lat[0] && g.lat <= coords.lat[1] &&
            g.lng >= coords.lng[0] && g.lng <= coords.lng[1]
        ).length;
        console.log(`${nombre}: ${count} grifos`);
    });
}

// Exportar todas las funciones al objeto global
window.descargarJSONCompleto = descargarJSONCompleto;
window.exportarGeoJSON = exportarGeoJSON;
window.buscarEnArea = buscarEnArea;
window.buscarPorUbicacion = buscarPorUbicacion;
window.analizarPorRegion = analizarPorRegion;

console.log('\nFunciones disponibles:');
console.log('• descargarJSONCompleto()');
console.log('• exportarGeoJSON(window.grifosLosAngeles, "nombre.geojson")');
console.log('• buscarEnArea(latMin, latMax, lngMin, lngMax)');
console.log('• buscarPorUbicacion("texto")');
console.log('• analizarPorRegion()');
