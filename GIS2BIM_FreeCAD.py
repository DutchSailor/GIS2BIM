## GIS2BIM within FreeCAD

import GIS2BIM_Lib
import urllib.request
import urllib
import xml.etree.ElementTree as ET
import json
import Draft
import Part

def GIS2BIM_FreeCAD_ImportImage(fileLocation,width,height,scale):
	App.activeDocument().addObject('Image::ImagePlane','ImagePlane')
	App.activeDocument().ImagePlane.ImageFile = fileLocation
	App.activeDocument().ImagePlane.XSize = width*scale
	App.activeDocument().ImagePlane.YSize = height*scale
	App.activeDocument().ImagePlane.Placement = App.Placement(App.Vector(0.000000,0.000000,0.000000),App.Rotation(0.000000,0.000000,0.000000,1.000000))

def GIS2BIM_FreeCAD_3DBuildings(curves3DBAG,heightData3DBAG):
	for i,j,k in zip(curves3DBAG,heightData3DBAG[1],heightData3DBAG[2]):
		pointlist = []
		for curve in i:
			pointlist.append(FreeCAD.Vector(curve[0], curve[1], float(j)*1000))
		a = Draft.makeWire(pointlist, closed=True)
		face = Part.Face(a)
		solid = face.extrude(Base.Vector(0,0,float(k)*1000))
		return solid

def GIS2BIM_FreeCAD_CurvesFromWFS(serverName,boundingBoxString,xPathString,dx,dy,scale,DecimalNumbers,XYZCountDimensions,closedValue):
	curves = GIS2BIM_Lib.GIS2BIM_PointsFromWFS(serverName,boundingBoxString,xPathString,dx,dy,scale,DecimalNumbers,XYZCountDimensions)
	for i in curves:
    	pointlist = []
    	for j in i:
	    	pointlist.append(FreeCAD.Vector(j[0], j[1], 0))
		a = Draft.makeWire(pointlist, closed=closedValue)
	return a

def GIS2BIM_FreeCAD_PlaceText(textData,fontSize):
	for i, j, k in zip(textData[0], textData[1], textData[2]):
    	ZAxis = FreeCAD.Vector(0, 0, 1)
    	p1 = FreeCAD.Vector(i[0][0], i[0][1], 0)
    	Place1 = FreeCAD.Placement(p1, FreeCAD.Rotation(ZAxis, -float(j)))
    	Text1 = Draft.make_text(k, point=p1)
    	Text1.ViewObject.FontSize = fontSize
    	Text1.Placement = Place1
	return Text1

#Get Rdx/Rdy
a = GIS2BIM_Lib.GIS2BIM_GetLocationDataNetherlands("dordrecht","Lange%20Geldersekade","2")
width = 500
height = 500
Rdx = float(a[0])
Rdy = float(a[1])

Rdx = 102857.637
Rdy = 425331.936
Bbox = GIS2BIM_Lib.GIS2BIM_CreateBoundingBox(Rdx,Rdy,width,height,2)

fileLocationWMS = 'C:\\TEMP\\test8.jpg'

# Import Aerialphoto in view
GIS2BIM_WMSRequest(DutchGEOLuchtfoto2019WMS,Bbox,fileLocationWMS)
ImageAerialPhoto = GIS2BIM_WMSRequest(fileLocationWMS,width,height,1000)

#Create 3D Building
curves3DBAG = GIS2BIM_Lib.GIS2BIM_PointsFromWFS(GIS2BIM_Lib.DutchGEOBAG3D,Bbox,GIS2BIM_Lib.xPath3DBag3,-Rdx,-Rdy,1000,3,3)
heightData3DBAG = GIS2BIM_Lib.GIS2BIM_DataFromWFS(GIS2BIM_Lib.DutchGEOBAG3D,Bbox,GIS2BIM_Lib.xPath3DBag3,GIS2BIM_Lib.xPathStrings3DBag,-Rdx,-Rdy,1000,3,3)
3DSolids = GIS2BIM_FreeCAD_3DBuildings(curves3DBAG,heightData3DBAG)

#Create Cadastral Parcels 2D
CadastralParcerCurves = GIS2BIM_FreeCAD_CurvesFromWFS(GIS2BIM_Lib.DutchGEOCadastreServerRequest1,Bbox,GIS2BIM_Lib.xPathCadastre1,-Rdx,-Rdy,1000,3,2,False)

#Create Building outline 2D
BAGBuildingCurves = GIS2BIM_FreeCAD_CurvesFromWFS(GIS2BIM_Lib.DutchGEOBAG,Bbox,GIS2BIM_Lib.xPathCadastre1,-Rdx,-Rdy,1000,3,2,True)

#Create Ruimtelijke plannen outline 2D
RuimtelijkePlannenBouwvlakCurves = GIS2BIM_FreeCAD_CurvesFromWFS(GIS2BIM_Lib.DutchGEORuimtelijkeplannenBouwvlakServerRequest,Bbox,GIS2BIM_Lib.xPathRuimtelijkePlannen,-Rdx,-Rdy,1000,3,2,True)

#Create Textdata Cadastral Parcels
textDataCadastralParcels = GIS2BIM_Lib.GIS2BIM_DataFromWFS(GIS2BIM_Lib.DutchGEOCadastreServerRequest2,Bbox,GIS2BIM_Lib.xPathCadastre2,GIS2BIM_Lib.xPathStringsCadastreTextAngle,-Rdx,-Rdy,1000,3,2)
textDataOpenbareRuimtenaam = GIS2BIM_Lib.GIS2BIM_DataFromWFS(GIS2BIM_Lib.DutchGEOCadastreServerRequest3,Bbox,GIS2BIM_Lib.xPathCadastre2,GIS2BIM_Lib.xPathStringsCadastreTextAngle,-Rdx,-Rdy,1000,3,2)

placeTextCadastralParcels = GIS2BIM_FreeCAD_PlaceText(textDataCadastralParcels,200)
placeTextOpenbareRuimteNaam = GIS2BIM_FreeCAD_PlaceText(textDataOpenbareRuimtenaam,200)

FreeCAD.ActiveDocument.recompute()

