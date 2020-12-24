from PyFlow.Core.Common import *
from PyFlow.Core import FunctionLibraryBase
from PyFlow.Core import IMPLEMENT_NODE

import math
import random
import GIS2BIM_Lib

class DemoLib(FunctionLibraryBase):
    '''doc string for DemoLib'''

    def __init__(self, packageName):
        super(DemoLib, self).__init__(packageName)

    @staticmethod
    @IMPLEMENT_NODE(returns=None, nodeType=NodeTypes.Callable, meta={NodeMeta.CATEGORY: 'DemoLib', NodeMeta.KEYWORDS: []})
    # Return a random integer N such that a <= N <= b
    def demoLibGreet(word=('StringPin', "Greet!")):
        """Docstrings are in **rst** format!"""
        print(word)

    @staticmethod
    @IMPLEMENT_NODE(returns=('StringPin', "empty"), meta={NodeMeta.CATEGORY: 'coordinates', NodeMeta.KEYWORDS: []})
    def GIS2BIM_CreateBoundingBox(CoordinateX=('FloatPin', 0.0), CoordinateY=('FloatPin', 0.0), BoxWidth=('FloatPin', 0.0), BoxHeight=('FloatPin', 0.0), DecimalNumbers=('IntPin', 0)):
        '''Create boundingboxstring for webrequests based on coordinates and dimensions.'''
        boundingBoxString1 = GIS2BIM_CreateBoundingBox(CoordinateX, CoordinateY, BoxWidth, BoxHeight, DecimalNumbers)
        return boundingBoxString1
		
    @staticmethod
    @IMPLEMENT_NODE(returns=('StringPin', "empty"), meta={NodeMeta.CATEGORY: 'DutchGEO', NodeMeta.KEYWORDS: []})
    def GIS2BIM_GetLocationDataNetherlands(City=('StringPin', "Dordrecht"), StreetName=('StringPin', "LangeGeldersekade"), HouseNumber=('StringPin', "2")):
        '''Gives locationdata based on an address in the Netherlands.'''
        PDOKServer = "http://geodata.nationaalgeoregister.nl/locatieserver/v3/free?wt=json&rows=1&q="
        import urllib.request
        import json
        requesturl =  PDOKServer + City +" and " + StreetName + " and " + HouseNumber
        urlFile = urllib.request.urlopen(requesturl)
        jsonList = json.load(urlFile)
        jsonList = jsonList["response"]["docs"]
        jsonList1 = jsonList[0]
        RD = jsonList1['centroide_rd']
        RD = RD.replace("("," ").replace(")"," ")
        RD = RD.split()
        RDx = float(RD[1])
        RDy = float(RD[2])
        return RDx

#    @staticmethod
#    @IMPLEMENT_NODE(returns=('StringPin', "empty"), meta={NodeMeta.CATEGORY: 'DutchGEO', NodeMeta.KEYWORDS: []})

#    def GIS2BIM_PointsFromWFS(serverName=('StringPin', ""), boundingBoxString=('StringPin', ""), xPathString=('StringPin', ""), dx=('FloatPin', 0.0), dy=('FloatPin', 0.0), scale=('FloatPin', 1.0), DecimalNumbers=('FloatPin', 1000)):
#        '''Gives locationdata based on an address in the Netherlands.'''
#
#        curvesCadastralParcels = GIS2BIM_PointsFromWFS(DutchGEOCadastreServerRequest1, Bbox, xPathCadastre1, -Rdx, -Rdy,
                                                       1000, 1)