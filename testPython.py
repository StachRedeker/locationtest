import streamlit as st
import streamlit.components.v1 as components

st.title("Get Geolocation on Android")

st.markdown(
    """
    This example uses a custom HTML/JavaScript snippet to request your location.
    Make sure you are visiting this page over HTTPS and that location services are enabled.
    """
)

# Embed HTML/JavaScript that uses the browser's geolocation API.
html_code = """
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      body { font-family: Arial, sans-serif; }
      #location { margin-top: 20px; font-size: 16px; }
      button { padding: 10px 20px; font-size: 16px; }
    </style>
  </head>
  <body>
    <button onclick="getLocation()">Get Location</button>
    <p id="location">Location will appear here...</p>
    <script>
      function getLocation() {
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(showPosition, showError);
        } else {
          document.getElementById("location").innerText = "Geolocation is not supported by this browser.";
        }
      }
      
      function showPosition(position) {
        document.getElementById("location").innerHTML = "Latitude: " + position.coords.latitude +
        "<br>Longitude: " + position.coords.longitude;
      }
      
      function showError(error) {
        switch(error.code) {
          case error.PERMISSION_DENIED:
            document.getElementById("location").innerText = "User denied the request for Geolocation.";
            break;
          case error.POSITION_UNAVAILABLE:
            document.getElementById("location").innerText = "Location information is unavailable.";
            break;
          case error.TIMEOUT:
            document.getElementById("location").innerText = "The request to get user location timed out.";
            break;
          case error.UNKNOWN_ERROR:
            document.getElementById("location").innerText = "An unknown error occurred.";
            break;
        }
      }
    </script>
  </body>
</html>
"""

components.html(html_code, height=300)
