//----------------------- defines ---------------------------------------------

// LINK LIMITS
var GOOD_LINK_PDR       = 80;
var MEDIUM_LINK_PDR     = 50;

// LINK COLOR
var GOOD_LINK_COLOR     = "#66ff4c"     // green
var MEDIUM_LINK_COLOR   = "#ff950e"     // orange
var BAD_LINK_COLOR      = "#ff0515"     // red

var map;
var infoWindow;
var sites = [];
var markers = [];
var lines = [];
var markerCluster = null;
var api_url = "https://api.github.com/repos/openwsn-berkeley/mercator/contents/datasets/processed";
var raw_url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/";

//----------------------- init ------------------------------------------------

function initMap() {
  var agde = {lat: 43.28248, lng: 3.51217};

  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 3,
    center: agde,
    mapTypeId: 'satellite',
    tilt: 0
  });

  infoWindow = new google.maps.InfoWindow();
  getSites();
}

//----------------------- helpers ---------------------------------------------

function getSites() {
    $.getJSON(api_url + "?ref=data",
      function(data) {
        $.each( data, function( key, val ) {
          site = val["name"];
          sites.push(site);
          getSiteMeta(site);
        })
    })
}

function getSiteMeta(site) {
  $.getJSON(raw_url + "data/metas/" + site +  ".json",
    function(data) {
    if (data["latitude"] != null) {
      var site_coordinates = {lat: parseFloat(data["latitude"]), lng: parseFloat(data["longitude"])};
      markers.push(addMarker(site_coordinates, site, site));
      $.each(data["nodes"], function (key, val) {
        if (val["archi"] == "m3:at86rf231") {
          node_coordinates = new google.maps.LatLng({
            lat: site_coordinates["lat"] + 0.00005 * parseFloat(val["x"]),
            lng: site_coordinates["lng"] + 0.00005 * parseFloat(val["y"])
          });
          markers.push(addMarker(node_coordinates, val, site))
        }
      });
      refreshMarkerCluster();
    }
  })
}

function getExperiments(site) {
  $.getJSON(api_url + "/" + site +  "?ref=data",
    function(data) {
      var items = [];
      $.each(data, function (key, experiment) {
        items.push( "<option id='" + experiment["name"] + "'>" + experiment["name"] + "</option>" );
      });
      $("#side_pane #experiment_list" ).html(
        "<select onchange='getExperimentInfos(\"" + site + "\", this.value)'>" + items.join( "" ) + "</select>"
      );
    }
  )
}

function getExperimentInfos(site, experiment) {
  clearLines();
  $.getJSON(raw_url + "data/datasets/processed/" + site + "/" + experiment + "/info.json",
    function(data) {
      $("#side_pane #experiment_info").html("<pre>" + JSON.stringify(data["global"], null, 2) + "</pre>");
      $.each(data["paths"], function (key, path) {
        node1 = getMarker(site, path[0]["src"]);
        node2 = getMarker(site, path[0]["dst"]);
        if (node1 != "undefined" && node2 != "undefined"){
          lineCoordinates = [
            node1.getPosition(),
            node2.getPosition()
          ];
          addLine(lineCoordinates, path)
        }
      });
    }
  )
}

function getMarker(site, mac){
  for (var i=0; i<markers.length; i++){
    if (markers[i]["site"] == site && markers[i]["meta"]["mac"] == mac){
      return markers[i]
    }
  }
}

function refreshMarkerCluster(){
  if (markerCluster){
    markerCluster.clearMarkers();
    markerCluster.addMarkers(markers)
  } else {
    var mcOptions = {gridSize: 25, maxZoom: 10, imagePath: 'static/markerclusterer/m', averageCenter: false};
    markerCluster = new MarkerClusterer(map, markers, mcOptions);
  }
  google.maps.event.addListener(markerCluster, 'clusterclick', function(cluster) {
    coords = cluster.getMarkers()[0].getPosition();
    if (cluster.getCenter().equals(coords)){
      $("#side_pane #site_name p").html(cluster.getMarkers()[0].meta);
      getExperiments(cluster.getMarkers()[0].meta);
    } else {
      $("#side_pane #site_name p").html("");
    }
  });
}

// calculates distance between two points in meters
function calcDistance(p1, p2) {
  return (google.maps.geometry.spherical.computeDistanceBetween(p1, p2)).toFixed(2);
}

function addMarker(latLng, jsonNode, site) {
  var marker = new google.maps.Marker({
    position: latLng,
    map: map,
    meta: jsonNode,
    site: site,
    icon: {
        path: google.maps.SymbolPath.CIRCLE,
        scale: 4,
        strokeWeight: 2,
        fillColor: "#ff5050",
        fillOpacity: 1
    }
  });
  google.maps.event.addListener(marker, 'click', (function (marker) {
    return function () {
      var content = "<pre>" + JSON.stringify(marker.meta, null, 2) + "</pre>";
      infoWindow.setContent(content);
      infoWindow.open(map, marker);
    }
  })(marker));
  return marker;
}

function addLine(lineCoordinates, jsonPath) {
  var avgPDR = (jsonPath[0]["PDR"] + jsonPath[1]["PDR"])/2;
  var line = new google.maps.Polyline({
    path: lineCoordinates,
    geodesic: true,
    strokeColor: getLinkColor(avgPDR),
    strokeWeight: 3
  });
  line.setMap(map);
  lines.push(line);
  google.maps.event.addListener(line, 'click', (function (line) {
    return function (event) {
      var content = "<pre>" + JSON.stringify(jsonPath, null, 2) + "</pre>";
      infoWindow.setPosition(event.latLng);
      infoWindow.setContent(content);
      infoWindow.open(map, line);
    }
  })(line));
  return line;
}

function clearLines(){
    for (var i=0; i<lines.length; i++){
        lines[i].setMap(null);
    }
}

function getLinkColor(pdr){
  if (pdr >= GOOD_LINK_PDR)
    return GOOD_LINK_COLOR;
  else if (pdr > MEDIUM_LINK_PDR && pdr < GOOD_LINK_PDR)
    return MEDIUM_LINK_COLOR;
  else
    return BAD_LINK_COLOR;
}
