var lat = mymap.getCenter();
	
var textToSave = String(lat);

var hiddenElement = document.createElement('a');

hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave);
hiddenElement.target = '_blank';
hiddenElement.download = 'FOLDERNAME';
hiddenElement.click();