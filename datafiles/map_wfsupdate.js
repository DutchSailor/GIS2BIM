mymap.removeLayer(wfsGroup)
var url = 'URL'
var wfsGroup = new L.LayerGroup();
wfsGroup.addTo(mymap);

$.getJSON(url, function(data) {
	$.each(data.features, function(index, geometry) {
		wfsCurves = L.geoJson(geometry),
		wfsGroup.addLayer(wfsCurves)
	});
});
