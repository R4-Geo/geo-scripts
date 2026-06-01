# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Script.py
# Fecha: 
# Fecha Edicion: 28/02/2022
# Descripcion: con/struye edificaciones
# Owner: Raster4
# ---------------------------------------------------------------------------

#------------------------
# IMPORTACION DE MODULOS
#------------------------

# Importacion del modulo de arcpy
import arcpy

#------------------------------
from datetime import date
import tkinter as tk
from tkinter import messagebox
#------------------------------

#Funcion de expiracion de codigo
def program_expired():
    today_date = date.today().isoformat()
    expiry_date = "2022-08-31"
    if today_date == expiry_date:
       messagebox.showerror("Error","El código expiro")
       quit()
    
    elif today_date > expiry_date:
        messagebox.showerror("Error","El código expiro")
        quit()
                        
program_expired()

#-------------------------------------------------------
# Argumentos del script

fc_Esqueleto = arcpy.GetParameterAsText(0)

fc_Predio = arcpy.GetParameterAsText(1)

fc_Puntos_Edificacion = arcpy.GetParameterAsText(2)

gdb_destino = arcpy.GetParameterAsText(3)

# Variables locales:

# Espacio de trabajo
# Set Geoprocessing environments
arcpy.env.workspace = ""

#-----------------
#  PROCESAMIENTO
#-----------------

# FEATURE TO POLYGON (de entidad a poligono para crear los poligonos de edificacion)
# Process: Feature To Polygon
fc_Edificacion = arcpy.FeatureToPolygon_management([fc_Esqueleto, fc_Predio], gdb_destino+"/Edificacion", "", "ATTRIBUTES", "")

                                                                                    
# ELIMINAR POLIGONOS QUE NO SON EDIFICACIONES
# Process: Select Layer By Location
fc_Edificacion_Layer, Output_Layer_Names, Count = arcpy.SelectLayerByLocation_management([fc_Edificacion], "CONTAINS", fc_Puntos_Edificacion, "", "NEW_SELECTION", "INVERT")

# Process: Delete Features
fc_Edificacion_Layer_2_ = arcpy.DeleteFeatures_management(fc_Edificacion_Layer)


