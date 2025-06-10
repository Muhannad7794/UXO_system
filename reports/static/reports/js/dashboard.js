document.addEventListener('DOMContentLoaded', function () {
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
        return;
    }

    // --- Global Variables ---
    let map;
    const uxoPointsLayer = L.layerGroup();
    const hotzonesLayer = L.layerGroup();
    let heatmapLayer;

    // --- NEW: Helper function to determine pin color based on danger score ---
    function getPinColor(score) {
        if (score > 0.9) return '#d32f2f'; // Dark Red
        if (score > 0.8) return '#f44336'; // Red
        if (score > 0.7) return '#ff9800'; // Orange
        if (score > 0.6) return '#ffc107'; // Amber
        if (score > 0.4) return '#cddc39'; // Lime
        if (score > 0.2) return '#4caf50'; // Green
        return '#2196f3'; // Blue
    }

    // --- Map Initialization ---
    function initMap() {
        map = L.map('map').setView([35.0, 38.0], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        uxoPointsLayer.addTo(map);
    }

    // --- Layer Control Setup ---
    function addLayerControl() {
        const overlayMaps = {
            "UXO Records": uxoPointsLayer,
            "Hot Zones": hotzonesLayer,
            "Risk Heatmap": heatmapLayer
        };
        L.control.layers(null, overlayMaps, { collapsed: false }).addTo(map);
    }

    // --- Data Loading Functions (Now with better styling) ---
    function loadUxoPoints(url) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                uxoPointsLayer.clearLayers();
                L.geoJSON(data, {
                    // NEW: Use pointToLayer to create custom circle markers
                    pointToLayer: function (feature, latlng) {
                        return L.circleMarker(latlng, {
                            radius: 6,
                            fillColor: getPinColor(feature.properties.danger_score),
                            color: '#000',
                            weight: 1,
                            opacity: 1,
                            fillOpacity: 0.8
                        });
                    },
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
                    // UPDATED: More granular styling for polygons
                    style: function(feature) {
                        const score = feature.properties.avg_danger_score;
                        let color = '#4caf50'; // Green
                        if (score > 0.5) color = '#cddc39'; // Lime
                        if (score > 0.6) color = '#ffc107'; // Amber
                        if (score > 0.7) color = '#ff9800'; // Orange
                        if (score > 0.8) color = '#f44336'; // Red
                        return { color: color, weight: 3, opacity: 0.9, fillOpacity: 0.2 };
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
                // UPDATED: Configure the heatmap layer for better visualization
                heatmapLayer = L.heatLayer(data, {
                    radius: 20,
                    blur: 25,
                    maxZoom: 11,
                    // Custom color gradient
                    gradient: {
                        0.2: 'blue',
                        0.4: 'lime',
                        0.6: 'yellow',
                        0.8: 'orange',
                        1.0: 'red'
                    }
                });
                addLayerControl();
            })
            .catch(error => console.error('Error fetching heatmap data:', error));
    }

    // --- Event listener for the filter form (no changes needed here) ---
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
        loadUxoPoints(apiUrl);
    });

    // --- Initial Setup ---
    initMap();
    loadUxoPoints('/api/v1/records/all_records/');
    loadHotzones();
    loadHeatmap();
});