"""
Este script selecciona las imágenes duplicadas
"""

import PhotoScan, os

chunk = PhotoScan.app.document.chunk
step = PhotoScan.app.getInt("Specify the selection step:" ,2)
index = 1
for camera in chunk.cameras:
      if not (index % step):
            camera.selected = True
      else:
            camera.selected = False
      index += 1
