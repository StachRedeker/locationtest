# -*- coding: utf-8 -*-
import streamlit as st
import folium
from streamlit_folium import st_folium
import random
import math
import requests

st.title("User Location and a Random 10km Marker")

st.markdown(
    """
    This app shows your location on an OpenStreetMap, along with a randomly generated
    point exactly 10 km away.
    """
)

# -----------------------------------------------------------------------------
# 1. Try to get the user's geolocation automatically using streamlit-geolocation.
# -----------------------------------------------------------------------------
location = None
try:
    from streamlit_geolocation import st_geolocation

    # st_geolocation will prompt the browser for your location.
    location = st_geolocation(label="Click to allow geolocation")
except ImportError:
    st.info("Automatic geolocation via streamlit-geolocation is not available.")

# -----------------------------------------------------------------------------
# 2. If no location from the geolocation component, try IP-based geolocation.
# -----------------------------------------------------------------------------
if location is None or not location:
    st.info("Attempting IP-based geolocation...")
    try:
        response = requests.get("http://ip-api.com/json/")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                location = {"latitude": data["lat"], "longitude": data["lon"]}
                st.success(
                    f"IP-based geolocation found: Latitude: {data['lat']:.6f}, "
                    f"Longitude: {data['lon']:.6f}"
                )
            else:
                st.error("IP-based geolocation failed: " + data.get("message", "Unknown error"))
        else:
            st.error("IP-based geolocation failed with status code: " + str(response.status_code))
    except Exception as e:
        st.error("Error during IP-based geolocation: " + str(e))

# -----------------------------------------------------------------------------
# 3. Fallback: manual coordinate entry if neither method worked.
# -----------------------------------------------------------------------------
if location is not None:
    lat = location["latitude"]
    lon = location["longitude"]
else:
    lat = st.number_input("Enter your latitude:", value=0.0, format="%.6f")
    lon = st.number_input("Enter your longitude:", value=0.0, format="%.6f")
    if lat == 0.0 and lon == 0.0:
        st.warning("Please enter your location above to see the map.")

# -----------------------------------------------------------------------------
# 4. Proceed only if a valid location is available.
# -----------------------------------------------------------------------------
if not (lat == 0.0 and lon == 0.0):
    
    # -----------------------------------------------------
    # Function: Compute a random point exactly 10 km away.
    # -----------------------------------------------------
    def get_random_point(origin_lat, origin_lon, distance_km=10):
        """
        Given an origin (in degrees) and a distance in kilometers,
        compute a destination point exactly that distance away in a random direction.
        """
        # Earth's radius (in km)
        R = 6371.0

        # Convert coordinates from degrees to radians.
        lat_rad = math.radians(origin_lat)
        lon_rad = math.radians(origin_lon)

        # Pick a random bearing (angle in radians)
        bearing = random.uniform(0, 2 * math.pi)

        # Angular distance in radians
        angular_distance = distance_km / R

        # Destination point (using the spherical Earth projected formula)
        dest_lat = math.asin(
            math.sin(lat_rad) * math.cos(angular_distance) +
            math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing)
        )
        dest_lon = lon_rad + math.atan2(
            math.sin(bearing) * math.sin(angular_distance) * math.cos(lat_rad),
            math.cos(angular_distance) - math.sin(lat_rad) * math.sin(dest_lat)
        )

        return math.degrees(dest_lat), math.degrees(dest_lon)

    # -----------------------------------------------------------------------------
    # 5. Use Streamlit session_state to generate the random point only once.
    # -----------------------------------------------------------------------------
    if "user_location" not in st.session_state or st.session_state.user_location != (lat, lon):
        st.session_state.user_location = (lat, lon)
        st.session_state.random_lat, st.session_state.random_lon = get_random_point(lat, lon, 10)
    
    # Provide a button to regenerate the random point manually.
    if st.button("Regenerate Random Point"):
        st.session_state.random_lat, st.session_state.random_lon = get_random_point(lat, lon, 10)
    
    random_lat = st.session_state.random_lat
    random_lon = st.session_state.random_lon

    st.info(
        f"Random point 10 km away: Latitude: {random_lat:.6f}, "
        f"Longitude: {random_lon:.6f}"
    )

    # -----------------------------------------------------------------------------
    # 6. Create and display a Folium map with markers for both points.
    # -----------------------------------------------------------------------------
    m = folium.Map(location=[lat, lon], zoom_start=12)

    # Marker for the user's location (blue marker).
    folium.Marker(
        location=[lat, lon],
        popup="Your Location",
        icon=folium.Icon(color="blue", icon="user")
    ).add_to(m)

    # Marker for the random point (red marker).
    folium.Marker(
        location=[random_lat, random_lon],
        popup="Random 10km Point",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    st_folium(m, width=700, height=500)
