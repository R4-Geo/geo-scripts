;; Función principal para llamar desde Civil 3D
(defun C:ImportarShpDetallado ()
  (arxload "acedfdo.arx") ; <-- AÑADIR ESTA LÍNEA, CARGA LAS FUNCIONES FDO
  (vl-load-com) ; Carga de funciones ActiveX

  ;; --- LISTA DE ARCHIVOS SHP ---
  (setq lista-shp
    (list
      '("C:\\RASTER4_DANIEL\\SECTRA\\2da ENTREGA\\DWG\\SHP PRUEBA LISP\\ZONA_DE_RECICLAJE.shp" "02.22 - ZONA_DE_RECICLAJE" "ZONA_DE_RECICLAJE")
      '("C:\\RASTER4_DANIEL\\SECTRA\\2da ENTREGA\\DWG\\SHP PRUEBA LISP\\AREA_VERDE.shp" "09.03 - AREA_VERDE" nil)
      '("C:\\RASTER4_DANIEL\\SECTRA\\2da ENTREGA\\DWG\\SHP PRUEBA LISP\\EJE_VIAL.shp" "10.12 - EJE_VIAL" nil)
    )
  )

  ;; Procesa cada elemento de la lista
  (foreach shp-info lista-shp
    (setq shp-path (nth 0 shp-info))
    (setq target-layer (nth 1 shp-info))
    (setq point-block (nth 2 shp-info))

    (princ (strcat "\nProcesando: " (vl-filename-base shp-path)))

    ;; 1. Crear capa de destino si no existe
    (if (not (tblsearch "LAYER" target-layer))
      (command "-LAYER" "N" target-layer "")
    )
    
    (setq conn (ade_fdo_connect "OSGeo.SHP.3.8"))
    (if conn
      (progn
        (ade_fdo_connectstring conn (strcat "File=" shp-path))
        (ade_fdo_open conn)
        
        (setq schemas (ade_fdo_getschemanames conn))
        (setq classes (ade_fdo_getclassnames conn (car schemas)))
        
        ;; 2. Configurar opciones de importación
        (setq import-options (list
            (list "Layer" target-layer)
            (list "CreateTable" 1) 
          )
        )

        ;; 3. Lógica CORREGIDA para el bloque de puntos
        (if point-block
          (if (tblsearch "BLOCK" point-block)
            ;; Si el bloque existe, lo añade a las opciones
            (setq import-options (append import-options (list (list "PointId" point-block))))
            ;; Si no existe, muestra una advertencia
            (princ (strcat "\nADVERTENCIA: El bloque '" point-block "' no existe y no será utilizado."))
          )
        )
        
        (setq options (ade_fdo_impoptions import-options))
        
        ;; 4. Importar las entidades
        (ade_fdo_import conn (car schemas) (car classes) options)
        
        (ade_fdo_close conn)
        (ade_fdo_disconnect conn)
        (princ " ... ¡Importado!")
      )
      (princ " ... Error de conexión FDO.")
    )
  )
  (princ "\n--- Proceso finalizado. ---")
  (princ)
)