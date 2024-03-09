from packages.GIS2BIM.GIS2BIM_NL import *
from packages.GIS2BIM.GIS2BIM import *
from project.fileformat import *
from packages.GIS2BIM.GIS2BIM_NL_helpers import *
import requests
import xml.etree.ElementTree as ET

#Download CityJSON Files of 3D Basisvoorziening

#SETTINGS
GISProject = BuildingPy("test")
tempfolder = "C:/TEMP/GIS/"
lst = NL_GetLocationData(NLPDOKServerURL,"Dordrecht", "werf van schouten", "501")
Bboxwidth = 500 #m

#BOUNDINGBOX
RdX = lst[0]
RdY = lst[1]
GISBbox = GisRectBoundingBox().Create(RdX,RdY,Bboxwidth,Bboxwidth,0)

#CITYJSON DOWNLOAD
folderBAG3D = tempfolder + "BAG3D/"
CreateDirectory(folderBAG3D)

res = BAG3DDownload(GISBbox.boundingBoxString,folderBAG3D)
