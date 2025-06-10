document.addEventListener("DOMContentLoaded", function () {
  // Find all elements with the class 'mini-map'
  const miniMaps = document.querySelectorAll(".mini-map");

  // Loop through each mini-map container
  miniMaps.forEach((mapDiv) => {
    // Get the coordinates from the data attributes we set in the template
    const lat = parseFloat(mapDiv.dataset.lat);
    const lng = parseFloat(mapDiv.dataset.lng);

    // Make sure the coordinates are valid numbers
    if (!isNaN(lat) && !isNaN(lng)) {
      // Initialize the map in this specific div
      const map = L.map(mapDiv.id, {
        scrollWheelZoom: true, // Disable zoom on scroll for a better page experience
        dragging: true, // Disable dragging
        zoomControl: true, // Hide zoom buttons
      }).setView([lat, lng], 8); // Center the map on the pin

      // Add the tile layer
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(
        map
      );

      // Add a single marker for the reported location
      L.marker([lat, lng]).addTo(map);
    }
  });
});
