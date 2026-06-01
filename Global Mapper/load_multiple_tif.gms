import os
import gm  # Modulo de Global Mapper

def load_tif_files(base_dir):
    """
    Recorre recursivamente el directorio base en busqueda de archivos TIF y los carga en Global Mapper.
    """
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(('.tif', '.tiff')):
                file_path = os.path.join(root, file)
                # Cargar el archivo TIF en Global Mapper
                gm.LoadLayer(file_path)
                print("Archivo cargado:", file_path)

if __name__ == '__main__':
    # Directorio base donde se buscaran los archivos TIF (modifica esta ruta segun tu entorno)
    base_directory = r"C:\Ruta\A\Carpeta\Principal"
    load_tif_files(base_directory)
