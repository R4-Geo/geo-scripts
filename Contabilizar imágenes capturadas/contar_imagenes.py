import os
import csv

def contar_imagenes_trinity(ruta_trinity):
    """
    Contabiliza las imágenes de la plataforma TRINITY a partir de archivos .csv.
    Ignora la primera fila (header) de cada archivo.

    Args:
        ruta_trinity (str): Ruta a la carpeta con los logs de TRINITY.

    Returns:
        int: Número total de imágenes.
    """
    total_imagenes = 0
    if not os.path.isdir(ruta_trinity):
        print(f"Error: La ruta para TRINITY no existe: {ruta_trinity}")
        return 0
        
    for archivo in os.listdir(ruta_trinity):
        if archivo.lower().endswith('.csv'):
            try:
                with open(os.path.join(ruta_trinity, archivo), 'r', encoding='utf-8') as f:
                    # Omitimos la primera línea (header)
                    next(f) 
                    # Contamos las líneas restantes
                    total_imagenes += sum(1 for line in f)
            except Exception as e:
                print(f"No se pudo procesar el archivo {archivo}: {e}")
    return total_imagenes

def contar_imagenes_mavic3(ruta_mavic):
    """
    Contabiliza las imágenes de la plataforma MAVIC 3 a partir de archivos .MRK.
    Estos archivos no tienen header.

    Args:
        ruta_mavic (str): Ruta a la carpeta con los logs de MAVIC 3.

    Returns:
        int: Número total de imágenes.
    """
    total_imagenes = 0
    if not os.path.isdir(ruta_mavic):
        print(f"Error: La ruta para MAVIC_3 no existe: {ruta_mavic}")
        return 0
        
    for archivo in os.listdir(ruta_mavic):
        if archivo.lower().endswith('.mrk'):
            try:
                with open(os.path.join(ruta_mavic, archivo), 'r', encoding='utf-8') as f:
                    # No hay header, contamos todas las líneas
                    total_imagenes += sum(1 for line in f)
            except Exception as e:
                print(f"No se pudo procesar el archivo {archivo}: {e}")
    return total_imagenes

def contar_imagenes_evo(ruta_evo):
    """
    Contabiliza las imágenes de la plataforma EVO a partir de archivos .csv y .txt.
    Ignora la primera fila (header) de cada archivo.

    Args:
        ruta_evo (str): Ruta a la carpeta con los logs de EVO.

    Returns:
        int: Número total de imágenes.
    """
    total_imagenes = 0
    if not os.path.isdir(ruta_evo):
        print(f"Error: La ruta para EVO no existe: {ruta_evo}")
        return 0
        
    for archivo in os.listdir(ruta_evo):
        if archivo.lower().endswith(('.csv', '.txt')):
            try:
                with open(os.path.join(ruta_evo, archivo), 'r', encoding='utf-8') as f:
                    # Omitimos la primera línea (header)
                    next(f)
                    # Contamos las líneas restantes
                    total_imagenes += sum(1 for line in f)
            except StopIteration:
                # Archivo vacío o con solo una línea de header
                pass
            except Exception as e:
                print(f"No se pudo procesar el archivo {archivo}: {e}")
    return total_imagenes

def main():
    """
    Función principal que define las rutas y ejecuta el conteo para cada plataforma.
    """
    # --- CONFIGURACIÓN DE RUTAS ---
    ruta_base = r"Ruta Carpeta base"
    
    ruta_trinity = os.path.join(ruta_base, "TRINITY")
    ruta_mavic3 = os.path.join(ruta_base, "MAVIC_3")
    ruta_evo = os.path.join(ruta_base, "EVO")

    # --- EJECUCIÓN DEL CONTEO ---
    print("Iniciando el conteo de imágenes por plataforma...")
    
    total_trinity = contar_imagenes_trinity(ruta_trinity)
    total_mavic3 = contar_imagenes_mavic3(ruta_mavic3)
    total_evo = contar_imagenes_evo(ruta_evo)
    
    # --- PRESENTACIÓN DE RESULTADOS ---
    print("\n" + "="*40)
    print("         RESULTADOS FINALES         ")
    print("="*40)
    print(f" dron TRINITY:  {total_trinity} imágenes")
    print(f" ️ dron MAVIC 3: {total_mavic3} imágenes")
    print(f" dron EVO:      {total_evo} imágenes")
    print("="*40)
    
    total_general = total_trinity + total_mavic3 + total_evo
    print(f"\nIMÁGENES TOTALES (todas las plataformas): {total_general}")

if __name__ == "__main__":
    main()
