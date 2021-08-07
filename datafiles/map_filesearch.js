mymap.setView([51LAT, 4LONG] , 16);
marker1.setLatLng([51LAT, 4LONG]);

function updateBoundingbox(center) {
	boundsW = center.toBounds(boundingboxwidth);
	boundsH = center.toBounds(boundingboxheight);	
	bounds = [[boundsH.getSouth(),boundsW.getWest()],[boundsH.getNorth(),boundsW.getEast()]];
	rect.setBounds(bounds);
}

var center = L.latLng([51LAT, 4LONG]);
updateBoundingbox(center)

var textToSave = "LatLng(51LAT, 4LONG)"
var hiddenElement = document.createElement('a')
hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave)
hiddenElement.target = '_blank'
hiddenElement.download = 'FOLDERNAME'
hiddenElement.click()
