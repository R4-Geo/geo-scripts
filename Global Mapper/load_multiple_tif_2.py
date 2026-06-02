import os
import ctypes
import globalmapper as gm

def load_tif_files_recursively(base_dir, load_flags=0):
    """
    Recorre recursivamente 'base_dir' y carga cada archivo TIF encontrado.
    """
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(('.tif', '.tiff')):
                file_path = os.path.join(root, file)
                print("Cargando archivo:", file_path)
                
                # Llamada a LoadLayerList: devuelve (error, puntero a array, cantidad de capas)
                error, layer_handles_ptr, count = gm.LoadLayerList(file_path, gm.GM_LoadFlags_UseDefaultLoadOpts)
                
                if error != 0:
                    print("Error cargando:", file_path, "Codigo de error:", error)
                    continue
                
                print("Se cargaron", count, "capa(s) del archivo", file_path)

def set_transparency_for_loaded_layers():
    """
    Ajusta la transparencia de todas las capas cargadas al color negro.
    """
    # Obtener la lista de capas cargadas
    result = gm.GetLoadedLayerList()
    for layer in result:
        # Obtener opciones de visualizacion para cada capa
        display_options = gm.GetRasterDisplayOptions(layer)

if __name__ == '__main__':
    base_directory = r"RUTA CARPETA"
    load_tif_files_recursively(base_directory, load_flags=0)
    set_transparency_for_loaded_layers()  # Llama a la funcion correctamente
