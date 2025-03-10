function get_delegations(chosen, dest, default_value){
	if ($('#zipcode').val() != "") $('#zipcode').val('');
	if(!chosen){
		$(dest).prop('disabled', 'disabled');
		$(dest).find('option').not(':first').remove().val('');
		$(dest).selectpicker("refresh");
		var dest = '#city';
		$(dest).prop('disabled', 'disabled');
		$(dest).find('option').not(':first').remove().val('');
		$(dest).selectpicker("refresh");
		return;
	}else{
		$('#city').prop('disabled', 'disabled');
		$('#city').find('option').not(':first').remove().val('');
		$('#city').selectpicker("refresh");
	}
	$(dest).prop('disabled', false);
	$.ajax({
		url: "/delegations",
		type: "get", //send it through get method
		data: {	"state": chosen},
		success: function(response) {
			//Do Something
			$(dest).find('option').not(':first').remove().val('');
			for( var delgation of response['data']['delegations']){
				$(dest).append(`<option value="${delgation['id']}">${delgation['name']}</option>`);
			}
			$(dest).selectpicker("refresh");
		},
		error: function(xhr) {
		//Do Something to handle error
		}
	});
}

function get_cities(chosen, dest, default_value){
	if ($('#zipcode').val() != "") $('#zipcode').val('');
	if(!chosen){
		$(dest).prop('disabled', 'disabled');
		$(dest).find('option').not(':first').remove().val('');
		$(dest).selectpicker("refresh");
		return;
	}
	city_data = {'': ''};
	$(dest).prop('disabled', false);
	$.ajax({
		url: "/cities",
		type: "get", //send it through get method
		data: {	"delegation": chosen},
		success: function(response) {
			//Do Something
			$(dest).find('option').not(':first').remove().val('');
			for( var city of response['data']['cities']){
				$(dest).append(`<option value="${city['id']}">${city['name']}</option>`);
				city_data[city['id']] = city;
			}
			$(dest).selectpicker("refresh");
		},
		error: function(xhr) {
		//Do Something to handle error
		}
	});
}

function onCityChange(id){
	$('#zipcode').val(city_data[id]['zipcode']);
}

function cancelMarkerFromMap(map, marker){
	if(marker){
		map.removeLayer(marker);
	}
	$('#geolat').val("");
	$('#geolong').val("");
}

function setLocationMap(marker){
	$('#geolat').val(marker.getLatLng()['lat']);
	$('#geolong').val(marker.getLatLng()['lng']);
	$('#GeoModal').modal('hide');
	return true;
}
