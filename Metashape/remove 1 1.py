import PhotoScan, os

chunk = PhotoScan.app.document.chunk
print("start")
paths = set()
photos = list()
for camera in list(chunk.cameras):
      if camera.photo.path in paths:
             photos.append(camera)
      else:
             paths.add(camera.photo.path)

chunk.remove(photos)
print("finished. %d duplicates removed" % len(photos))