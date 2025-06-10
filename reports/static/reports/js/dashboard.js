document.addEventListener('DOMContentLoaded', function () {
    const mapContainer = document.getElementById('map');
    if (!mapContainer) { return; }

    // --- Global Variables ---
    let map;
    const uxoPointsLayer = L.layerGroup();
    const hotzonesLayer = L.layerGroup();
    let heatmapLayer;
    const drawnItems = new L.FeatureGroup(); // Layer group to hold the user-drawn rectangle

    // --- Helper function to get pin color ---
    function getPinColor(score) {
        if (score > 0.9) return '#d32f2f';
        if (score > 0.8) return '#f44336';
        if (score > 0.7) return '#ff9800';
        if (score > 0.6) return '#ffc107';
        if (score > 0.4) return '#cddc39';
        if (score > 0.2) return '#4caf50';
        return '#2196f3';
    }

    // --- Map Initialization ---
    function initMap() {
        map = L.map('map').setView([35.0, 38.0], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        map.addLayer(drawnItems); // Add the layer for drawn items to the map

        // --- NEW: Initialize Leaflet.draw controls ---
        const drawControl = new L.Control.Draw({
            edit: { featureGroup: drawnItems, remove: false },
            draw: {
                polygon: false, polyline: false, circle: false, marker: false, circlemarker: false,
                rectangle: { shapeOptions: { color: '#007bff' } } // Only enable the rectangle tool
            }
        });
        map.addControl(drawControl);

        // --- NEW: Event listener for when a shape is created ---
        map.on(L.Draw.Event.CREATED, function (e) {
            const layer = e.layer;
            drawnItems.clearLayers(); // Clear any previous rectangle
            drawnItems.addLayer(layer); // Add the new rectangle to the map

            const bounds = layer.getBounds();
            const bbox_param = `${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`;
            const apiUrl = `/api/v1/reports/geospatial/within-bbox/?bbox=${bbox_param}`;
            
            console.log("Fetching data for bounding box:", bbox_param);
            loadUxoPoints(apiUrl); // Update the map with data from the new endpoint
        });

        uxoPointsLayer.addTo(map);
    }

    // --- Layer Control Setup ---
    function addLayerControl() {
        const overlayMaps = {
            "UXO Records": uxoPointsLayer, "Hot Zones": hotzonesLayer, "Risk Heatmap": heatmapLayer
        };
        L.control.layers(null, overlayMaps, { collapsed: false }).addTo(map);
    }

    // --- Data Loading Functions (no changes here) ---
    function loadUxoPoints(url) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                uxoPointsLayer.clearLayers();
                L.geoJSON(data.features || data, { // Handle both paginated and direct GeoJSON
                    pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
                        radius: 6, fillColor: getPinColor(feature.properties.danger_score), color: '#000', weight: 1, opacity: 1, fillOpacity: 0.8
                    }),
                    onEachFeature: (feature, layer) => {
                        const props = feature.properties;
                        layer.bindPopup(`<strong>Type:</strong> ${props.ordnance_type}<br><strong>Score:</strong> ${props.danger_score.toFixed(2)}`);
                    }
                }).addTo(uxoPointsLayer);
            }).catch(error => console.error('Error fetching UXO points:', error));
    }

    function loadHotzones() {
        fetch('/api/v1/reports/geospatial/hotzones/')
            .then(response => response.json())
            .then(data => {
                hotzonesLayer.clearLayers();
                L.geoJSON(data.features, {
                    style: feature => ({ color: getPinColor(feature.properties.avg_danger_score), weight: 3, opacity: 0.9, fillOpacity: 0.2 }),
                    onEachFeature: (feature, layer) => {
                        const props = feature.properties;
                        layer.bindPopup(`<strong>Hot Zone</strong><br>Contains: ${props.record_count} records<br>Avg Score: ${props.avg_danger_score.toFixed(2)}`);
                    }
                }).addTo(hotzonesLayer);
            }).catch(error => console.error('Error fetching hot zones:', error));
    }

    function loadHeatmap() {
        fetch('/api/v1/reports/geospatial/heatmap/')
            .then(response => response.json())
            .then(data => {
                heatmapLayer = L.heatLayer(data, {
                    radius: 20, blur: 25, maxZoom: 11,
                    gradient: { 0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 0.8: 'orange', 1.0: 'red' }
                });
                addLayerControl();
            }).catch(error => console.error('Error fetching heatmap data:', error));
    }

    // --- Event Listeners for Filters ---
    const filterForm = document.getElementById('filter-form');
    filterForm.addEventListener('change', () => {
        const params = new URLSearchParams(new FormData(filterForm));
        const apiUrl = `/api/v1/records/all_records/?${params.toString()}`;
        loadUxoPoints(apiUrl);
    });

    // NEW: Event listener for the "Clear Area Filter" button
    document.getElementById('clear-area-filter').addEventListener('click', () => {
        drawnItems.clearLayers(); // Remove the drawn rectangle
        filterForm.reset(); // Optional: reset the other filters too
        loadUxoPoints('/api/v1/records/all_records/'); // Reload all points
    });

    // --- Initial Setup ---
    initMap();
    loadUxoPoints('/api/v1/records/all_records/');
    loadHotzones();
    loadHeatmap();
});