// GPS LOCATION...
console.log('gps enabled')
let latitude = 0
let longitude = 0

if ('geolocation' in navigator) {
	const options = {
		enableHighAccuracy: true,
		timeout: 10000,
		maximumAge: 1000,
	}
	navigator.geolocation.watchPosition(onSuccess, onError)
} else {
	console.log('No Location obtained')
}

function onSuccess(position) {
	latitude = position.coords.latitude
	longitude = position.coords.longitude
}
function onError() {
	alert('Failed to get location: this info is required')
}

timer = setInterval(sendRequest, 20000)

function sendRequest() {
	const xhttp = new XMLHttpRequest()
	xhttp.open(
		'GET',
		''.concat(
			`https://10.0.0.56:80/routs/update_drivers_location/`,
			latitude,
			'/',
			longitude
		),
		true
	)
	xhttp.send()
}
