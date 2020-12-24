## GIS2BIM Library

import GIS2BIM_Lib
import urllib.request
import xml.etree.ElementTree as ET
import json

a = GIS2BIM_Lib.GIS2BIM_GetLocationDataNetherlands("dordrecht","Lange%20Geldersekade","2")
width = 500
Rdx = float(a[0])
Rdy = float(a[1])

Rdx = 104857.637
Rdy = 425331.936
Bbox = GIS2BIM_Lib.GIS2BIM_CreateBoundingBox(Rdx,Rdy,width,width,2)

curvesCadastralParcels = GIS2BIM_Lib.GIS2BIM_PointsFromWFS(GIS2BIM_Lib.DutchGEOCadastreServerRequest1,Bbox,GIS2BIM_Lib.xPathCadastre1,-Rdx,-Rdy,1000,3,2)
curvesBuildings = GIS2BIM_Lib.GIS2BIM_PointsFromWFS(GIS2BIM_Lib.DutchGEOBAG,Bbox,GIS2BIM_Lib.xPathCadastre1,-Rdx,-Rdy,1000,3,2)
curves3DBAG = GIS2BIM_Lib.GIS2BIM_PointsFromWFS(GIS2BIM_Lib.DutchGEOBAG3D,Bbox,GIS2BIM_Lib.xPath3DBag3,-Rdx,-Rdy,1000,3,3)


curvesRuimtelijkePlannen = GIS2BIM_Lib.GIS2BIM_PointsFromWFS(GIS2BIM_Lib.DutchGEORuimtelijkeplannenBouwvlakServerRequest,Bbox,GIS2BIM_Lib.xPathRuimtelijkePlannen,-Rdx,-Rdy,1000,3,2)
textDataCadastralParcels = GIS2BIM_Lib.GIS2BIM_DataFromWFS(GIS2BIM_Lib.DutchGEOCadastreServerRequest2,Bbox,GIS2BIM_Lib.xPathCadastre2,GIS2BIM_Lib.xPathStringsCadastreTextAngle,-Rdx,-Rdy,1000,3,2)
textDataOpenbareRuimtenaam = GIS2BIM_Lib.GIS2BIM_DataFromWFS(GIS2BIM_Lib.DutchGEOCadastreServerRequest3,Bbox,GIS2BIM_Lib.xPathCadastre2,GIS2BIM_Lib.xPathStringsCadastreTextAngle,-Rdx,-Rdy,1000,3,2)
heightData3DBAG = GIS2BIM_Lib.GIS2BIM_DataFromWFS(GIS2BIM_Lib.DutchGEOBAG3D,Bbox,GIS2BIM_Lib.xPath3DBag3,GIS2BIM_Lib.xPathStrings3DBag,-Rdx,-Rdy,1000,3,3)


#test = GIS2BIM_Lib.GIS2BIM_PointsFromWFS(GIS2BIM_Lib.DutchGEOBAG3D,Bbox,GIS2BIM_Lib.xPath3DBag3,0,0,1,3,3)
import Draft
import Part

for i,j,k in zip(curves3DBAG,heightData3DBAG[1],heightData3DBAG[2]):
	pointlist = []
	for curve in i:
		pointlist.append(FreeCAD.Vector(curve[0], curve[1], float(j)*1000))
	a = Draft.makeWire(pointlist, closed=True)
    face = Part.Face(a)
    solid = face.extrude(Base.Vector(0,0,float(k)*1000))

for i in curvesCadastralParcels:
    pointlist = []
    for j in i:
	    pointlist.append(FreeCAD.Vector(j[0], j[1], 0))
	a = Draft.makeWire(pointlist, closed=False)

for i in curvesBuildings:
	pointlist = []
	for j in i:
		pointlist.append(FreeCAD.Vector(j[0], j[1], 0))
	a = Draft.makeWire(pointlist, closed=True)

for i in curvesRuimtelijkePlannen:
	pointlist = []
	for j in i:
		pointlist.append(FreeCAD.Vector(j[0], j[1], 0))
	a = Draft.makeWire(pointlist, closed=True)
	
for i, j, k in zip(textDataCadastralParcels[0], textDataCadastralParcels[1], textDataCadastralParcels[2]):
    ZAxis = FreeCAD.Vector(0, 0, 1)
    p1 = FreeCAD.Vector(i[0][0], i[0][1], 0)
    Place1 = FreeCAD.Placement(p1, FreeCAD.Rotation(ZAxis, -float(j)))
    Text1 = Draft.makeText(k, point=p1)
    Text1.ViewObject.FontSize = 1000
    Text1.Placement = Place1

for i, j, k in zip(textDataOpenbareRuimtenaam[0], textDataOpenbareRuimtenaam[1], textDataOpenbareRuimtenaam[2]):
    ZAxis = FreeCAD.Vector(0, 0, 1)
    p1 = FreeCAD.Vector(i[0][0], i[0][1], 0)
    Place1 = FreeCAD.Placement(p1, FreeCAD.Rotation(ZAxis, -float(j)))
    Text1 = Draft.makeText(k.upper(), point=p1)
    Text1.ViewObject.FontSize = 1000
    Text1.Placement = Place1

for i,j,k in zip(curves3DBAG,heightData3DBAG[1],heightData3DBAG[2]):
	pointlist = []
	for curve in i:
		pointlist.append(FreeCAD.Vector(curve[0], curve[1], float(j)*1000))
	extrudeAlong = FreeCAD.Vector(0,0,float(k)*1000)
	pointlist.append(pointlist[0])
	a = Part.makePolygon(pointlist)
	face = Part.Face(a)
	solid = face.extrude(extrudeAlong)
	Part.show(solid)

FreeCAD.ActiveDocument.recompute()

'''