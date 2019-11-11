import clr
clr.AddReference('ProtoGeometry')
clr.AddReference("System.Drawing")
clr.AddReference("System")
from System import Drawing
from System.Drawing import Image
from System.Drawing import Bitmap
from System.Drawing import Graphics
from System.Drawing.Imaging import ImageFormat
from System.Net import WebRequest
from System.IO import Path
#from os import listdir
import sys
sys.path.append("C:\Program Files (x86)\IronPython 2.7\Lib")

from Autodesk.DesignScript.Geometry import *
#The inputs to this node will be stored as a list in the IN variables.

import math
from math import *
import itertools
from itertools import islice

dataEnteringNode = IN

Zoomlevels = IN[0]
Rdx = IN[1]
Rdy = IN[2]
BoundingboxWidths = IN[3]
Layers = IN[4]

Zoomleveldata = {0:3440.640,
1:1720.320,
2:860.160,
3:430.080,
4:215.040,
5:107.520,
6:53.720,
7:26.880,
8:13.440,
9:6.720,
10:3.360,
11:1.680,
12:0.840,
13:0.420,
14:0.210,
15:0.105,
16:0.0575}

PixelWidth =256
Xcorner=-285401.92
Ycorner=903402.0

Resolutions = []
for i in Zoomlevels:
	Resolutions.append(Zoomleveldata[i])

TileColumns = []
TileRows = []
DeltaX = []
DeltaY= []

for i in Resolutions:
	a = PixelWidth*i
	#TileColumns.append(Rdx-Xcorner)
	#TileRows.append(a)
	TileY = (Ycorner-Rdy)/a
	TileX = (Rdx-Xcorner)/a
	TileYRound = int(TileY)
	TileXRound = int(TileX)
	TilePercentageY = TileX-TileXRound
	TilePercentageX = TileY-TileYRound
	DeltaYM = TilePercentageY*PixelWidth*i
	DeltaXM = TilePercentageX*PixelWidth*i
	
	TileRows.append(TileYRound)
	TileColumns.append(TileXRound)
	DeltaY.append(DeltaYM)
	DeltaX.append(DeltaXM)

UniqueTileColumns = []
UniqueTileRows = []
TileColumns2 = []
TileRows2 = []

for i,j,k,l in zip(TileColumns, TileRows, BoundingboxWidths, Resolutions):
	TileWidth=PixelWidth*l
	c = math.ceil(k/TileWidth)
	b = math.ceil(c/2)*2
	UniqueTileColumns.append(range(int((i-b/2)), 1+int(i+b/2)))
	UniqueTileRows.append(range((int(j-b/2)), 1+int(j+b/2)))


for i in UniqueTileColumns:
	#de list:
	a = []
	
	counter = len(i)
	
	for j in i: #elke unieke tile
		a.append(i)
	flatA= []
	
	for sublist in a:
		for item in sublist:
			flatA.append(item)
	TileColumns2.append(flatA)
	
	counter=0

for i in UniqueTileRows:
	#de list:
	a = []
	
	counter = len(i)
	for j in i: #elke unieke tile
		a.append([int(j)]*counter)
	flatA= []
	
	for sublist in a:
		for item in sublist:
			flatA.append(item)
	TileRows2.append(flatA)
	
	counter=0

TotalTileWidth = []

for i, j in zip(Resolutions,UniqueTileColumns):
	a = len(j)*PixelWidth*i
	TotalTileWidth.append(a)

string1 = "http://geodata.nationaalgeoregister.nl/tiles/service/wmts?&request=GetTile&VERSION=1.0.0&LAYER="
string3 = "&STYLE=default&TILEMATRIXSET=EPSG:28992&TILEMATRIX=EPSG:28992:"
string34 = "&TILEROW="
string5 = "&TILECOL="
string7 = "&FORMAT=image/png8";

urlList = []

for i,j,k,z in zip(TileColumns2,TileRows2,Layers,Zoomlevels):
	a = []
	for l,m in zip(i,j):
		b = string1 + str(k) + string3 + str(z) + string34 + str(m) + string5 + str(l) + string7
		a.append(b)
	urlList.append(a)

bitmaps2 = []


for i in urlList:
	bitmaps = []
	for j in i:
		request = WebRequest.Create(j)
		request.Accept = "text/html"
		request.UserAgent = "Mozilla/5.0"
		response = request.GetResponse()
		bitmaps.append(Image.FromStream(response.GetResponseStream()))
	bitmaps2.append(bitmaps)

combinedBitmaps = []
for a,b,c in zip(bitmaps2,UniqueTileColumns,UniqueTileRows):
	TotalWidth = len(b)*PixelWidth
	TotalHeight = len(c)*PixelWidth
	img = Bitmap(TotalWidth,TotalHeight)
	g = Graphics.FromImage(img)
	LPx = []
	n = 0
	for l in j:
		LPx.append(n*PixelWidth)
		n=n+1
	
	LPy = []
	n = 0
	for i in c:
		LPy.append(n*PixelWidth)
		n=n+1

	LPx2=[]
	n=len(LPy)
	for i in LPx:
		LPx2.append([i]*n)

	LPx3=[]
	for sublist in LPx2:
		for item in sublist:
			LPx3.append(item)

	LPy2=[]
	for i in LPx:
		LPy2.append(LPy)

	LPy3=[]
	for sublist in LPy2:
		for item in sublist:
			LPy3.append(item)
        
	LPy4=reversed(LPy3)

	for m,n,o in zip(a,LPy3,LPx3):
		g.DrawImage(m,n,o)
	combinedBitmaps.append(img)

	#else:
	#	for i,j,k in zip(bitmaps,LPx3,LPy4):
	#		g.DrawImage(i,j,k)
	
combinedBitmaps
#Assign your output to the OUT variable.
OUT = combinedBitmaps