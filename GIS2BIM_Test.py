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

