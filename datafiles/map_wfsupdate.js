mymap.removeLayer(wfsGroup)
var url = 'https://geodata.nationaalgeoregister.nl/bag/wfs/v1_1?';
var params = 'REQUEST&';
params += 'VERSION&';
params += 'SERVICE&';
params += 'TYPENAME&';
params += 'OUTPUT&';
params += 'SRS&';
params += 'BBOX';
//params += 'bbox=104600,425116,105000,425516';
var wfsGroup = new L.LayerGroup();
wfsGroup.addTo(mymap);

$.getJSON(url + params, function(data) {
	$.each(data.features, function(index, geometry) {
		wfsCurves = L.geoJson(geometry),
		wfsGroup.addLayer(wfsCurves)
	});
});
