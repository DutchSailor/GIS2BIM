import GIS2BIM_Lib
import urllib
import urllib.request
import xml.etree.ElementTree as ET
import json

Rdx = 104857.637
Rdy = 425331.936
width = 500
boundingBoxString = GIS2BIM_Lib.GIS2BIM_CreateBoundingBox(Rdx,Rdy,width,width,2)

fileLocation = 'C:\\TEMP\\test4.jpg'

serverName = GIS2BIM_Lib.DutchGEOLuchtfoto2019WMS

# perform a WMS OGC webrequest( Web Map Service). This is loading images.
myrequesturl = serverName + boundingBoxString
#resource = urllib.request.urlopen(myrequesturl)
#output = open(fileLocation, "wb")
#output.write(resource.read())
#output.close()


stringPart1 = "http://epsg.io/trans?&s_srs="
SourceSRS = "28992"
stringPart3 = "&t_srs="
TargetSRS = "4326"
stringPart4 = "&x="
XCoordinate = str(Rdx)
stringPart6 = "&y="
YCoordinate = str(Rdy)
stringPart7 = "&format=xml&trans=1"

requesturl = stringPart1 + SourceSRS + stringPart3 + TargetSRS + stringPart4 + XCoordinate + stringPart6 + YCoordinate + stringPart7

from urllib.request import urlopen
import json

file = urllib.request.urlopen(requesturl)
#data = json.loads(urlopen(requesturl).read().decode("utf-8"))
#urlFile = urllib.request.urlopen(requesturl)
#jsonList = json.load(urlFile)

#response = json.loads(requests.get(requesturl).text)
#data = json.loads(response.read())

#data = json.loads(webrequestresult)

print(file)
#wmsLuchtfoto = GIS2BIM_Lib.GIS2BIM_WMSRequest(GIS2BIM_Lib.DutchGEOLuchtfoto2019WMS,boundingBoxString,fileLocation):


## GIS2BIM Library

## Webserverdata
DutchGEO_PDOKServerURL = "http://geodata.nationaalgeoregister.nl/locatieserver/v3/free?wt=json&rows=1&q="

DutchGEOCadastreServerRequest1 = "http://geodata.nationaalgeoregister.nl/kadastralekaart/wfs/v4_0?service=WFS&version=2.0.0&request=GetFeature&typeName=perceel&bbox="
#For curves of Cadastral Parcels

DutchGEOCadastreServerRequest2 = "http://geodata.nationaalgeoregister.nl/kadastralekaart/wfs/v4_0?service=WFS&version=2.0.0&request=GetFeature&typeName=kadastralekaartv4:nummeraanduidingreeks&bbox="
#For 'nummeraanduidingreeks' of Cadastral Parcels

DutchGEOCadastreServerRequest3 = "http://geodata.nationaalgeoregister.nl/kadastralekaart/wfs/v4_0?service=WFS&version=2.0.0&request=GetFeature&typeName=kadastralekaartv4:openbareruimtenaam&bbox="
#For 'openbareruimtenaam' of Cadastral Parcels

DutchGEOBAG = "http://geodata.nationaalgeoregister.nl/bag/wfs/v1_1?service=wfs&version=2.0.0&request=GetFeature&typeName=bag:pand&bbox="
#Building Contour of BAG

DutchGEOBAG3D = "http://3dbag.bk.tudelft.nl/data/wfs?&request=GetFeature&typeName=BAG3D:pand3d&outputFormat=GML3&bbox="
#3D Buildings of BAG

DutchGEOLuchtfoto2019WMS = "http://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?&request=GetMap&VERSION=1.3.0&STYLES=&layers=2019_ortho25&width=3000&height=3000&format=image/png&crs=EPSG:28992&bbox="

DutchGEORuimtelijkeplannenBouwvlakServerRequest = "http://afnemers.ruimtelijkeplannen.nl/afnemers/services?&service=WFS&version=1.1.0&request=GetFeature&typeName=app:Bouwvlak&bbox="


xPathCadastre1 = ".//{http://www.opengis.net/gml/3.2}posList"
xPathCadastre2 = ".//{http://www.opengis.net/gml/3.2}pos"
xPathStringsCadastreTextAngle = [".//{http://kadastralekaartv4.geonovum.nl}hoek", ".//{http://kadastralekaartv4.geonovum.nl}tekst"]


xPathRuimtelijkePlannen = ".//{http://www.opengis.net/gml}posList"
xPathStrings3DBag = [".//{3dbag}ground-0.50", ".//{3dbag}roof-0.50"]
xPath3DBag3 = ".//{http://www.opengis.net/gml}posList"

#Xpath for several Cadastral Servers

import urllib.request
import xml.etree.ElementTree as ET
import json

def GIS2BIM_GML_poslistData(tree, xPathString,dx,dy,scale,DecimalNumbers,XYZCountDimensions):
#group X and Y Coordinates of polylines
    posLists = tree.findall(xPathString)
    xyPosList = []
    for posList in posLists:
        dataPosList = posList.text
        coordSplit = dataPosList.split()
        x = 0
        coordSplitXY = []
        for j in range(0, int(len(coordSplit) / XYZCountDimensions)):
            xy_coord = (round((float(coordSplit[x])+dx)*scale,DecimalNumbers), round((float(coordSplit[x+1])+dy)*scale,DecimalNumbers))
            coordSplitXY.append(xy_coord)
            x +=XYZCountDimensions
        xyPosList.append(coordSplitXY)
    return xyPosList

def GIS2BIM_CreateBoundingBox(CoordinateX,CoordinateY,BoxWidth,BoxHeight,DecimalNumbers):
#Create Boundingboxstring for use in webrequests.
    XLeft = round(CoordinateX-0.5*BoxWidth,DecimalNumbers)
    XRight = round(CoordinateX+0.5*BoxWidth,DecimalNumbers)
    YBottom = round(CoordinateY-0.5*BoxHeight,DecimalNumbers)
    YTop = round(CoordinateY+0.5*BoxHeight,DecimalNumbers)
    boundingBoxString1 = str(XLeft) + "," + str(YBottom) + "," + str(XRight) + "," + str(YTop)
    return boundingBoxString1

def GIS2BIM_GetLocationDataNetherlands(City,Streetname,Housenumber):
# Use PDOK location server to get X & Y data
    PDOKServer = DutchGEO_PDOKServerURL
    requestURL =  PDOKServer + City +"%20and%20" + Streetname + "%20and%20" + Housenumber
    urlFile = urllib.request.urlopen(requestURL)
    jsonList = json.load(urlFile)
    jsonList = jsonList["response"]["docs"]
    jsonList1 = jsonList[0]
    RD = jsonList1['centroide_rd']
    RD = RD.replace("("," ").replace(")"," ")
    RD = RD.split()
    RDx = RD[1]
    RDy = RD[2]
    return RDx,RDy, requestURL

def GIS2BIM_PointsFromWFS(serverName,boundingBoxString,xPathString,dx,dy,scale,DecimalNumbers,XYZCountDimensions):
# group X and Y Coordinates
    myrequesturl = serverName + boundingBoxString
    urlFile = urllib.request.urlopen(myrequesturl)
    tree = ET.parse(urlFile)
    xyPosList = GIS2BIM_GML_poslistData(tree,xPathString,dx,dy,scale,DecimalNumbers,XYZCountDimensions)
    return xyPosList

def GIS2BIM_DataFromWFS(serverName,boundingBoxString,xPathStringCoord,xPathStrings,dx,dy,scale,DecimalNumbers,XYZCountDimensions):
# group textdata from WFS
    myrequesturl = serverName + boundingBoxString
    urlFile = urllib.request.urlopen(myrequesturl)
    tree = ET.parse(urlFile)
    xyPosList = GIS2BIM_GML_poslistData(tree,xPathStringCoord,dx,dy,scale,DecimalNumbers,XYZCountDimensions)
    xPathResults = []
    for xPathString in xPathStrings:
        a = tree.findall(xPathString)
        xPathResulttemp2 = []
        for xPathResult in a:
            xPathResulttemp2.append(xPathResult.text)
        xPathResults.append(xPathResulttemp2)
    xPathResults.insert(0,xyPosList)
    return xPathResults

## GIS2BIM Library

import urllib.request
import xml.etree.ElementTree as ET
import json
import Draft
import Part

a = GIS2BIM_GetLocationDataNetherlands("dordrecht","Lange%20Geldersekade","2")
width = 1000
height = 400
Rdx = float(a[0])
Rdy = float(a[1])

Rdx = 104857.637
Rdy = 425331.936
Bbox = GIS2BIM_CreateBoundingBox(Rdx,Rdy,width,height,2)

fileLocationWMS = 'C:\\TEMP\\test7.jpg'
curvesCadastralParcels = GIS2BIM_PointsFromWFS(DutchGEOCadastreServerRequest1,Bbox,xPathCadastre1,-Rdx,-Rdy,1000,3,2)
curvesBuildings = GIS2BIM_PointsFromWFS(DutchGEOBAG,Bbox,xPathCadastre1,-Rdx,-Rdy,1000,3,2)
curves3DBAG = GIS2BIM_PointsFromWFS(DutchGEOBAG3D,Bbox,xPath3DBag3,-Rdx,-Rdy,1000,3,3)

curvesRuimtelijkePlannen = GIS2BIM_PointsFromWFS(DutchGEORuimtelijkeplannenBouwvlakServerRequest,Bbox,xPathRuimtelijkePlannen,-Rdx,-Rdy,1000,3,2)
textDataCadastralParcels = GIS2BIM_DataFromWFS(DutchGEOCadastreServerRequest2,Bbox,xPathCadastre2,xPathStringsCadastreTextAngle,-Rdx,-Rdy,1000,3,2)
textDataOpenbareRuimtenaam = GIS2BIM_DataFromWFS(DutchGEOCadastreServerRequest3,Bbox,xPathCadastre2,xPathStringsCadastreTextAngle,-Rdx,-Rdy,1000,3,2)
heightData3DBAG = GIS2BIM_DataFromWFS(DutchGEOBAG3D,Bbox,xPath3DBag3,xPathStrings3DBag,-Rdx,-Rdy,1000,3,3)

def GIS2BIM_WMSRequest(serverName,boundingBoxString,fileLocation):
    # perform a WMS OGC webrequest( Web Map Service). This is loading images.
    myrequestURL = serverName + boundingBoxString
    resource = urllib.request.urlopen(myrequestURL)
    output1 = open(fileLocation, "wb")
    output1.write(resource.read())
    output1.close()
    return fileLocation, resource

#GIS2BIM_WMSRequest(DutchGEOLuchtfoto2019WMS,Bbox,fileLocationWMS)

#App.activeDocument().addObject('Image::ImagePlane','ImagePlane')
#App.activeDocument().ImagePlane.ImageFile = fileLocationWMS
#App.activeDocument().ImagePlane.XSize = width*1000
#App.activeDocument().ImagePlane.YSize = height*1000
#App.activeDocument().ImagePlane.Placement = App.Placement(App.Vector(0.000000,0.000000,0.000000),App.Rotation(0.000000,0.000000,0.000000,1.000000))

#Import 3D Buildings BAG
def GIS2BIM_FreeCAD_3DBuildings(curves3DBAG,heightData3DBAG):
	for i,j,k in zip(curves3DBAG,heightData3DBAG[1],heightData3DBAG[2]):
		pointlist = []
		for curve in i:
			pointlist.append(FreeCAD.Vector(curve[0], curve[1], float(j)*1000))
		a = Draft.makeWire(pointlist, closed=True)
		face = Part.Face(a)
		solid = face.extrude(Base.Vector(0,0,float(k)*1000))
		return solid

#test = GIS2BIM_FreeCAD_3DBuildings(curves3DBAG,heightData3DBAG)


for i in curvesCadastralParcels:
	pointlist = []
	for j in i:
		pointlist.append(FreeCAD.Vector(j[0], j[1], 0))
	a = Draft.makeWire(pointlist, closed=False)

for i, j, k in zip(textDataCadastralParcels[0], textDataCadastralParcels[1], textDataCadastralParcels[2]):
    ZAxis = FreeCAD.Vector(0, 0, 1)
    p1 = FreeCAD.Vector(i[0][0], i[0][1], 0)
    Place1 = FreeCAD.Placement(p1, FreeCAD.Rotation(ZAxis, -float(j)))
    Text1 = Draft.make_text(k, point=p1)
    Text1.ViewObject.FontSize = 150
    Text1.Placement = Place1

for i, j, k in zip(textDataOpenbareRuimtenaam[0], textDataOpenbareRuimtenaam[1], textDataOpenbareRuimtenaam[2]):
    ZAxis = FreeCAD.Vector(0, 0, 1)
    p1 = FreeCAD.Vector(i[0][0], i[0][1], 0)
    Place1 = FreeCAD.Placement(p1, FreeCAD.Rotation(ZAxis, -float(j)))
    Text1 = Draft.make_text(k.upper(), point=p1)
    Text1.ViewObject.FontSize = 150
    Text1.Placement = Place1

FreeCAD.ActiveDocument.recompute()
