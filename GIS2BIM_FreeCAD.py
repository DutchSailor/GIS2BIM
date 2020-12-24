## GIS2BIM Library

a = GIS2BIM_GetLocationDataNetherlands("dordrecht","Lange%20Geldersekade","2")
width = 500
Rdx = float(a[0])
Rdy = float(a[1])

Rdx = 104857.637
Rdy = 425331.936
Bbox = GIS2BIM_CreateBoundingBox(Rdx,Rdy,width,width,2)

curvesCadastralParcels = GIS2BIM_PointsFromWFS(DutchGEOCadastreServerRequest1,Bbox,xPathCadastre1,-Rdx,-Rdy,1000,1)
curvesBuildings = GIS2BIM_PointsFromWFS(DutchGEOBAG,Bbox,xPathCadastre1,-Rdx,-Rdy,1000,1)
curvesRuimtelijkePlannen = GIS2BIM_PointsFromWFS(DutchGEORuimtelijkeplannenBouwvlakServerRequest,Bbox,xPathRuimtelijkePlannen,-Rdx,-Rdy,1000,1)
textDataCadastralParcels = GIS2BIM_DataFromWFS(DutchGEOCadastreServerRequest2,Bbox,xPathCadastre2,xPathStringsCadastreTextAngle,-Rdx,-Rdy,1000,1)
textDataOpenbareRuimtenaam = GIS2BIM_DataFromWFS(DutchGEOCadastreServerRequest3,Bbox,xPathCadastre2,xPathStringsCadastreTextAngle,-Rdx,-Rdy,1000,1)

import Draft

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

FreeCAD.ActiveDocument.recompute()

