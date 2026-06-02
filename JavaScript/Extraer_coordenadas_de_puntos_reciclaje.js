// Este código es para extraer los puntos de reciclaje desde un mapa embebido en un visor web


// Código para guardar como CSV
if (typeof markers !== 'undefined' && markers.length > 0) {
  let puntos = [];
  
  // Extraer datos de cada marcador
  markers.forEach((marker, index) => {
    if (marker && marker.getPosition) {
      const posicion = marker.getPosition();
      const titulo = marker.getTitle ? marker.getTitle() : `Punto ${index + 1}`;
      
      puntos.push({
        indice: index,
        titulo: titulo,
        lat: posicion.lat(),
        lng: posicion.lng()
      });
    }
  });
  
  // Crear contenido CSV
  let csvContent = "indice,titulo,lat,lng\n";
  puntos.forEach(punto => {
    csvContent += `${punto.indice},"${punto.titulo}",${punto.lat},${punto.lng}\n`;
  });
  
  // Crear y descargar el archivo
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', 'puntos_limpios_concepcion.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
