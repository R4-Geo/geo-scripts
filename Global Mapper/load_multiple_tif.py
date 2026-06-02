import os
import ctypes
import globalmapper as gm

def load_tif_files_recursively(base_dir, load_flags=0):
    """
    Recorre recursivamente 'base_dir' y carga cada archivo TIF encontrado.
    Devuelve una lista con todos los handles de las capas cargadas.
    """
    all_handles = []  # Lista para almacenar los handles de todas las capas cargadas
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(('.tif', '.tiff')):
                file_path = os.path.join(root, file)
                print("Cargando archivo:", file_path)
                # Llamada a LoadLayerList: devuelve (error, puntero a array, cantidad de capas)
                error, layer_handles_ptr, count = gm.LoadLayerList(file_path, load_flags)
                if error != 0:
                    print("Error cargando:", file_path, "Codigo de error:", error)
                    continue
                print("Se cargaron", count, "capa(s) del archivo", file_path)
                
                # Convertir layer_handles_ptr a un objeto c_void_p segun su tipo
                try:
                    if isinstance(layer_handles_ptr, int):
                        pointer_val = ctypes.c_void_p(layer_handles_ptr)
                    else:
                        pointer_val = layer_handles_ptr
                except Exception as e:
                    print("Error al convertir layer_handles_ptr:", e)
                    continue

                # Crear un arreglo de uint32 de tamano 'count'
                ArrayType = ctypes.c_uint32 * count
                try:
                    layer_handle_array = ctypes.cast(pointer_val, ctypes.POINTER(ArrayType)).contents
                except Exception as e:
                    print("Error al castear el puntero:", e)
                    continue
                
                # Agregar cada handle a la lista
                for i in range(count):
                    handle = layer_handle_array[i]
                    all_handles.append(handle)
                    print("Handle de capa:", handle)

    return all_handles

def set_layer_transparency(layer_handle, transparency):
    """
    Establece la transparencia de una capa raster especifica.
    :param layer_handle: Handle de la capa.
    :param transparency: Valor de transparencia (0-100), donde 0 es completamente opaco y 100 es completamente transparente.
    """
    # Obtener las opciones actuales de visualizacion de la capa
    err, opts = gm.GetRasterDisplayOptions(layer_handle)
    if err != 0:
        print(f"Error al obtener opciones de visualizacion para la capa {layer_handle}. Codigo de error: {err}")
        return
    
    # Establecer la nueva transparencia
    opts.mTransparent = bool

    # Aplicar las opciones modificadas a la capa
    err = gm.SetRasterDisplayOptions(layer_handle, opts)
    if err != 0:
        print(f"Error al establecer opciones de visualizacion para la capa {layer_handle}. Codigo de error: {err}")

if __name__ == '__main__':
    # Directorio base donde se buscaran los archivos TIF (incluye subcarpetas)
    base_directory = r"RUTA CARPETA"
    handles = load_tif_files_recursively(base_directory, load_flags=0)
    print(f"Total de handles de capas cargadas: {len(handles)}")

    # Aplicar transparencia a cada capa cargada
    transparencia_deseada = True  # Valor de transparencia deseado (True - False)
    for handle in handles:
        set_layer_transparency(handle, transparencia_deseada)

    # Cerrar cada capa para liberar recursos
    for handle in handles:
        gm.CloseLayer(handle)
