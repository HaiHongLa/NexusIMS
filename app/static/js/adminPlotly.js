fetch('/map-data')
  .then(response => response.json())
  .then(mapData => {
    // Calculate the average latitude and longitude
    var sumLat = mapData.lat.reduce((a, b) => a + b, 0);
    var sumLon = mapData.lon.reduce((a, b) => a + b, 0);
    var avgLat = sumLat / mapData.lat.length;
    var avgLon = sumLon / mapData.lon.length;

    // Convert data into Plotly-compatible format
    var data = [{
        type: 'scattermapbox',
        lat: mapData.lat,
        lon: mapData.lon,
        mode: 'markers',
        marker: {
            size: 14,
            color: 'rgb(255, 0, 0)',
            opacity: 0.7
        },
        text: mapData.text
    }];

    // Define layout for the map
    var layout = {
        mapbox: {
            style: 'open-street-map',
            center: { lat: avgLat, lon: avgLon }, // Set the center dynamically
            zoom: 3.5
        },
        margin: { l: 0, r: 0, b: 0, t: 0 },
        // width: 800,
        // height: 600
    };

    // Plot the map
    Plotly.newPlot('map', data, layout);
  })
  .catch(error => {
    console.error('Error fetching map data:', error);
  });
