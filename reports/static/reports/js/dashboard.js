document.addEventListener('DOMContentLoaded', function () {
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
        return;
    }

    // --- Global Variables ---
    let map;
    // We create separate Layer Groups to hold each type of data
    const uxoPointsLayer = L.layerGroup();
    const hotzonesLayer = L.layerGroup();
    let heatmapLayer; // This will be created by the Leaflet.heat plugin

    // --- Initialize the map ---
    function initMap() {
        map = L.map('map').setView([35.0, 38.0], 6);
        const osmTileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // Add the UXO points layer to the map by default
        uxoPointsLayer.addTo(map);
    }

    // --- Function to add the layer switcher UI to the map ---
    function addLayerControl() {
        const overlayMaps = {
            "UXO Records": uxoPointsLayer,
            "Hot Zones": hotzonesLayer,
            "Risk Heatmap": heatmapLayer
        };
        // This Leaflet function automatically builds the UI control
        L.control.layers(null, overlayMaps, { collapsed: false }).addTo(map);
    }

    // --- Functions to load data for each layer ---
    function loadUxoPoints(url) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                uxoPointsLayer.clearLayers(); // Clear old points before adding new ones
                L.geoJSON(data, {
                    onEachFeature: function (feature, layer) {
                        if (feature.properties) {
                            const popupContent = `<strong>Type:</strong> ${feature.properties.ordnance_type}<br><strong>Score:</strong> ${feature.properties.danger_score.toFixed(2)}`;
                            layer.bindPopup(popupContent);
                        }
                    }
                }).addTo(uxoPointsLayer);
            })
            .catch(error => console.error('Error fetching UXO points:', error));
    }

    function loadHotzones() {
        fetch('/api/v1/reports/geospatial/hotzones/')
            .then(response => response.json())
            .then(data => {
                hotzonesLayer.clearLayers();
                L.geoJSON(data.features, {
                    style: function(feature) {
                        // Style the polygons based on their average danger score
                        const score = feature.properties.avg_danger_score;
                        let color = '#4CAF50'; // Green
                        if (score > 0.6) color = '#FFC107'; // Yellow
                        if (score > 0.8) color = '#F44336'; // Red
                        return { color: color, weight: 2, opacity: 0.8 };
                    },
                    onEachFeature: function (feature, layer) {
                        const props = feature.properties;
                        const popupContent = `<strong>Hot Zone</strong><br>Contains: ${props.record_count} records<br>Avg Score: ${props.avg_danger_score.toFixed(2)}`;
                        layer.bindPopup(popupContent);
                    }
                }).addTo(hotzonesLayer);
            })
            .catch(error => console.error('Error fetching hot zones:', error));
    }

    function loadHeatmap() {
        fetch('/api/v1/reports/geospatial/heatmap/')
            .then(response => response.json())
            .then(data => {
                // The API returns points as [lat, lng, intensity]
                // L.heatLayer expects this format.
                heatmapLayer = L.heatLayer(data, { radius: 25 });
                
                // After the heatmap layer is created, we can add the layer control
                addLayerControl();
            })
            .catch(error => console.error('Error fetching heatmap data:', error));
    }

    // --- Event listener for the filter form ---
    const filterForm = document.getElementById('filter-form');
    filterForm.addEventListener('change', function () {
        const formData = new FormData(filterForm);
        const params = new URLSearchParams();
        for (const [key, value] of formData.entries()) {
            if (value) {
                params.append(key, value);
            }
        }
        const apiUrl = `/api/v1/records/all_records/?${params.toString()}`;
        // When filters change, only update the UXO points layer
        loadUxoPoints(apiUrl);
    });

    // --- Initial Setup ---
    initMap();
    loadUxoPoints('/api/v1/records/all_records/'); // Load initial points
    loadHotzones(); // Load hot zones
    loadHeatmap();  // Load heatmap data and create the layer control
});