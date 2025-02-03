# -*- coding: utf-8 -*-
import streamlit as st
import folium
from streamlit_folium import st_folium
import random
import math

st.title("User Location and a Random 10km Marker")

st.markdown(
    """
    This app shows your location on an OpenStreetMap, along with a randomly generated
    point exactly 10 km away.
    """
)

# -------------------------------------------------------------------
# Try to get the user's geolocation automatically using streamlit-geolocation.
# If not available or the user denies permission, allow manual input.
# -------------------------------------------------------------------
location = None
try:
    from streamlit_geolocation import st_geolocation

    # st_geolocation will prompt the browser for your location.
    location = st_geolocation(label="Click to allow geolocation")
except ImportError:
    st.info("Automatic geolocation is not available. "
            "Please enter your coordinates manually below.")

if location is not None:
    lat = location["latitude"]
    lon = location["longitude"]
    st.success(f"Location found: Latitude: {lat:.6f}, Longitude: {lon:.6f}")
else:
    lat = st.number_input("Enter your latitude:", value=0.0, format="%.6f")
    lon = st.number_input("Enter your longitude:", value=0.0, format="%.6f")
    if lat == 0.0 and lon == 0.0:
        st.warning("Please enter your location above to see the map.")

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

# Only proceed if a valid location is provided
if not (lat == 0.0 and lon == 0.0):
    # Use session state to avoid regenerating the random point on every run.
    if "user_location" not in st.session_state or st.session_state.user_location != (lat, lon):
        st.session_state.user_location = (lat, lon)
        st.session_state.random_lat, st.session_state.random_lon = get_random_point(lat, lon, 10)
    
    # Optional: Provide a button to regenerate the random point manually.
    if st.button("Regenerate Random Point"):
        st.session_state.random_lat, st.session_state.random_lon = get_random_point(lat, lon, 10)
    
    random_lat = st.session_state.random_lat
    random_lon = st.session_state.random_lon

    st.info(
        f"Random point 10 km away: Latitude: {random_lat:.6f}, "
        f"Longitude: {random_lon:.6f}"
    )

    # -----------------------------------------
    # Create a Folium map with the two markers.
    # -----------------------------------------
    # Center the map on the user's location.
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

    # Display the map in the Streamlit app.
    st_folium(m, width=700, height=500)
