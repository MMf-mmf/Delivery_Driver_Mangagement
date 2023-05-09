const scheduleId = document.getElementById('schedule_id').value
let lat = parseFloat(document.currentScript.getAttribute('drivers_latitude'))
let lng = parseFloat(document.currentScript.getAttribute('drivers_longitude'))
let map
let marker

function initMap() {
	map = new google.maps.Map(document.getElementById('map'), {
		zoom: 13,
		center: { lat: lat, lng: lng },
	})

	marker = new google.maps.Marker({
		position: { lat: lat, lng: lng },
		map: map,
		title: 'Flakos car',
	})
}

timer = setInterval(sendRequest, 120000) // 2 min

function sendRequest() {
	const xhttp = new XMLHttpRequest()
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.response)
			if (
				lat.toString().substring(0, 8) == response.lat.substring(0, 8) &&
				lng.toString().substring(0, 8) == response.lon.substring(0, 8)
			) {
				// console.log('lat, lon did not change')
			} else {
				// console.log('lat lon changed')
				lat = parseFloat(response.lat.replaceAll(' ', ''))
				lng = parseFloat(response.lon.replaceAll(' ', ''))
				let location = new google.maps.LatLng(lat, lng)
				map.setCenter(location)
				marker.setPosition(location)
			}
		}
	}
	xhttp.open(
		'GET',
		''.concat(
			`https://10.0.0.56:80/routs/current_drivers_location_on_schedule/`,
			scheduleId
		),
		true
	)
	response = xhttp.send()
}

window.initMap = initMap
