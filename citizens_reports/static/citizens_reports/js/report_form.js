// This function runs once the entire page is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Check if the report map container element exists on the page
    const reportMapContainer = document.getElementById('report-map');
    if (!reportMapContainer) {
        return; // If there's no map container, do nothing
    }

    // Initialize the map and set its view
    const reportMap = L.map('report-map').setView([35.0, 38.0], 6);

    // Add the map background tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(reportMap);

    let marker = null; // Variable to hold the user's location pin
    const locationInput = document.getElementById('location-input'); // The hidden input field

    // Listen for clicks on the map
    reportMap.on('click', function(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        // Update the hidden input field with the coordinates
        locationInput.value = `${lat},${lng}`;

        // If a marker already exists, move it. Otherwise, create a new one.
        if (marker) {
            marker.setLatLng(e.latlng);
        } else {
            marker = L.marker(e.latlng).addTo(reportMap);
        }

        // Add a popup to the marker
        marker.bindPopup("Your selected location.").openPopup();
    });
});