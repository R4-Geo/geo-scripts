# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Script_CapasAutomaticas.py
# Fecha Edicion: 28/02/2022
# Version: 2.0
# Descripcion: construye aceras, manzana predial, manzanas, linea de edificacion y cierre
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
    expiry_date = "2023-03-11"
    if today_date == expiry_date:
       messagebox.showerror("Error","El código expiro")
       quit()
    
    elif today_date > expiry_date:
        messagebox.showerror("Error","El código expiro")
        quit()
                        
program_expired()

#-------------------------------------------------------
# Argumentos del script

fc_Predio = arcpy.GetParameterAsText(0)

fc_Vialidad = arcpy.GetParameterAsText(1)

fc_Edificacion = arcpy.GetParameterAsText(2)

gdb_destino = arcpy.GetParameterAsText(3)

# Variables locales:

# Espacio de trabajo
# Set Geoprocessing environments
arcpy.env.workspace = ""

#-----------------
#  PROCESAMIENTO
#-----------------

# DISOLVER PREDIOS (CREA MANZANA PREDIAL)
# Process: Dissolve
fc_manzana_predial1 = arcpy.Dissolve_management(fc_Predio, gdb_destino+"/manzana_predial", "", "", "MULTI_PART", "DISSOLVE_LINES")

#SEPARAR MANZANA PREDIAL
# Process: Multipart To Singlepart 
fc_manzana_predial = arcpy.management.MultipartToSinglepart(fc_manzana_predial1, gdb_destino+"/manzanapredial")

#Eliminar fc_manzana_predial1
# Process: Delete 
Delete_Succeeded = arcpy.management.Delete([fc_manzana_predial1], "")[0]


# FEATURE TO POLYGON (de entidad a poligono para crear las soleras)
# Process: Feature To Polygon
fc_Acera = arcpy.FeatureToPolygon_management([fc_manzana_predial, fc_Vialidad], gdb_destino+"/Acera", "", "ATTRIBUTES", "")


# DISOLVER ACERAS PARA OBTENER MANZANAS 
# Process: Dissolve
fc_manzanas = arcpy.Dissolve_management(fc_Acera, gdb_destino+"/manzanas", "", "", "MULTI_PART", "DISSOLVE_LINES")

# SEPARAR POLIGONOS
# Process: Multipart To Singlepart 
fc_manzana = arcpy.management.MultipartToSinglepart(fc_manzanas, gdb_destino+"/manzana")

# ELIMINAR MANZANAS QUE NO SON
# Process: Select Layer By Location
fc_manzana_Layer, Output_Layer_Names, Count = arcpy.SelectLayerByLocation_management([fc_manzana], "INTERSECT", fc_manzana_predial, "", "NEW_SELECTION", "INVERT")

# Process: Delete Features
fc_manzana_Layer_2_ = arcpy.DeleteFeatures_management(fc_manzana_Layer)


# Eliminar fc_manzanas
# Process: Delete 
Delete_Succeeded = arcpy.management.Delete([fc_manzanas], "")[0]

                                                                                    
# ELIMINAR ACERAS QUE NO SON
# Process: Select Layer By Location
fc_Acera_Layer, Output_Layer_Names, Count = arcpy.SelectLayerByLocation_management([fc_Acera], "WITHIN", fc_manzana_predial, "", "NEW_SELECTION", "NOT_INVERT")

# Process: Delete Features
fc_Acera_Layer_2_ = arcpy.DeleteFeatures_management(fc_Acera_Layer)


# PASAR MANZANA PREDIAL A LINEA
# Process: Feature To Line 
fc_manzana_predial_linea = arcpy.management.FeatureToLine([fc_manzana_predial], gdb_destino+"/manzana_predial_linea", cluster_tolerance="", attributes="ATTRIBUTES")


# CREAR LINEA DE CIERRE
# Process: Erase 
fc_cierre1 = arcpy.analysis.Erase(fc_manzana_predial_linea, fc_Edificacion, gdb_destino+"/cierre1", cluster_tolerance="")


# SEPARAR LINEAS DE CIERRE
# Process: Multipart To Singlepart 
fc_cierre = arcpy.management.MultipartToSinglepart(fc_cierre1, gdb_destino+"/cierre")

                                  
# Eliminar fc_cierre1
# Process: Delete 
Delete_Succeeded = arcpy.management.Delete([fc_cierre1], "")[0]
                                  

#CREAR LINEA DE EDIFICACIÓN
# Process: Erase                                   
fc_linea_edi = arcpy.analysis.Erase(fc_manzana_predial_linea, fc_cierre, gdb_destino+"/linea_edi", cluster_tolerance="")

# SEPARAR LINEAS DE CIERRE
# Process: Multipart To Singlepart 
fc_linea_de_edificacion = arcpy.management.MultipartToSinglepart(fc_linea_edi, gdb_destino+"/linea_de_edificacion")


# Eliminar fc_linea_edi
# Process: Delete 
Delete_Succeeded = arcpy.management.Delete([fc_linea_edi], "")[0]

# Eliminar fc_manzana_predial_linea
# Process: Delete 
Delete_Succeeded = arcpy.management.Delete([fc_manzana_predial_linea], "")[0]


