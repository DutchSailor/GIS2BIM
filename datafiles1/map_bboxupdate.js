boundingboxwidth = WBBOX
boundingboxheight = HBBOX;
var center = marker1.getLatLng();
boundsW = center.toBounds(boundingboxwidth);
boundsH = center.toBounds(boundingboxheight);	
bounds = [[boundsH.getSouth(),boundsW.getWest()],[boundsH.getNorth(),boundsW.getEast()]]
rect.setBounds(bounds)
