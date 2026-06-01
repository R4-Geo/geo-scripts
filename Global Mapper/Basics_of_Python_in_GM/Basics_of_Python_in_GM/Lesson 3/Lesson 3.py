import globalmapper as gm
import os
import tkinter.filedialog
from tkinter import *

root = Tk()     
input_dir = tkinter.filedialog.askdirectory(title='Select Input Directory')
root.destroy() 

root = Tk()     
export_dir = tkinter.filedialog.askdirectory(title='Select Output Directory') 
root.destroy()  

root = Tk()     
ext = tkinter.simpledialog.askstring(title='File Mask',prompt='File Extension')
root.destroy()  

error, spcs_proj = gm.LoadProjectionFromEPSGCode(6483)
gm.SetProjection(spcs_proj)

for filename in os.listdir(input_dir):
    file_path = os.path.join(input_dir, filename)
    if os.path.isfile(file_path):
        if file_path.endswith(ext):
            error, loaded_layer = gm.LoadLayer(file_path, gm.GM_LoadFlags_UseDefaultLoadOpts)
            name = os.path.splitext(os.path.basename(file_path))[0]
            print(name)
            bounds = gm.GetLayerInfo(loaded_layer).mGlobalRect
            print(bounds)
            pixel_x = round(gm.GetLayerInfo(loaded_layer).mPixelSizeX)
            pixel_y = round(gm.GetLayerInfo(loaded_layer).mPixelSizeY)
            print(pixel_x,' ',pixel_y)
            error, layer_width = gm.CalcDistance(bounds.mMaxX, bounds.mMaxY, bounds.mMinX, bounds.mMaxY, 0)  #Get the total width of the data in meters
            error, layer_height = gm.CalcDistance(bounds.mMaxX, bounds.mMaxY, bounds.mMaxX, bounds.mMinY, 0)  #Ditto for height
            width = round(layer_width / pixel_x)      #We are using the pixel_resolution variable for spacing
            height = round(layer_height / pixel_y) 
            print(width,height)
            export_path = os.path.join(export_dir,name+'.tif')
            print(export_path)
            err = gm.ExportRaster(export_path, gm.GM_Export_GeoTIFF, loaded_layer, bounds, width, height, 0x0)

