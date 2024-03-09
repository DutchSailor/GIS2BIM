from packages.GIS2BIM.GIS2BIM_NL import *
from packages.GIS2BIM.GIS2BIM import *
from project.fileformat import *
from packages.GIS2BIM.GIS2BIM_NL_helpers import *

#Download CityJSON Files of 3D Basisvoorziening

#SETTINGS
GISProject = BuildingPy("test")
tempfolder = "C:/TEMP/GIS/"
lst = NL_GetLocationData(NLPDOKServerURL,"Dordrecht", "lange geldersekade", "2")
Bboxwidth = 200 #m

#BOUNDINGBOX
RdX = lst[0]
RdY = lst[1]
GISBbox = GisRectBoundingBox().Create(RdX,RdY,Bboxwidth,Bboxwidth,0)

kaartbladenres = kaartbladenBbox(GISBbox)
print(kaartbladenres)

#CITYJSON DOWNLOAD
folderCityJSON = tempfolder + "cityJSON/"
CreateDirectory(folderCityJSON)
for i in kaartbladenres:
    downloadlink = NLPDOKKadasterBasisvoorziening3DCityJSONVolledig + i[0] + "_2020_volledig.zip"
    print(downloadlink)
    downloadUnzip(downloadlink, folderCityJSON + i[0] +".zip", folderCityJSON)
