import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import folium_static
import pandas as pd
import datetime
import hashlib
import os
import base64
from cryptography.fernet import Fernet

def authenticate():
    """Secure authentication with username and password."""
    try:
        users_df = pd.read_csv("users.csv")
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return None, False, None
    
    username = st.text_input("Enter username:")
    password = st.text_input("Enter password:", type="password")
    
    if not username or not password:
        return None, False, None
    
    hashed_username = hashlib.sha256(username.encode()).hexdigest()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    if any((users_df["username"] == hashed_username) & (users_df["password"] == hashed_password)):
        return hashed_username, True, password
    else:
        st.error("Incorrect username or password.")
        return None, False, None

def load_points():
    """Loads points from points.csv and returns as a DataFrame."""
    try:
        df = pd.read_csv("points.csv")
        df["available_from"] = pd.to_datetime(df["available_from"])
        df["available_to"] = pd.to_datetime(df["available_to"])
        return df
    except Exception as e:
        st.error(f"Error loading points: {e}")
        return pd.DataFrame()

def save_user_location(username, password, lat, lon):
    """Encrypts and saves user location to a file hashed with the username."""
    file_path = f"data/{username}.csv"
    os.makedirs("data", exist_ok=True)
    key = hashlib.sha256((username + password).encode()).digest()
    encrypted_data = base64.urlsafe_b64encode(f"{lat},{lon},{datetime.datetime.utcnow()}".encode()).decode()
    with open(file_path, "a") as f:
        f.write(encrypted_data + "\n")

def load_user_locations(username, password):
    """Loads and decrypts user locations from a file."""
    file_path = f"data/{username}.csv"
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=["lat", "lon", "timestamp"])
    
    decrypted_data = []
    with open(file_path, "r") as f:
        for line in f:
            try:
                decrypted_line = base64.urlsafe_b64decode(line.strip()).decode()
                lat, lon, timestamp = decrypted_line.split(",")
                decrypted_data.append([float(lat), float(lon), timestamp])
            except:
                continue
    
    return pd.DataFrame(decrypted_data, columns=["lat", "lon", "timestamp"])

def plot_location(lat, lon, show_radii):
    """Creates a Folium map centered on the given latitude and longitude, adding points from CSV."""
    m = folium.Map(location=[lat, lon], zoom_start=12, control_scale=True)
    folium.Marker([lat, lon], popup="Your Location", tooltip="You are here", icon=folium.Icon(color='blue')).add_to(m)
    
    df = load_points()
    if not df.empty:
        current_date = datetime.datetime.utcnow()
        for _, row in df.iterrows():
            r_lat, r_lon, radius_km, available_from, available_to, pointer_text = row
            is_active = available_from <= current_date <= available_to
            color = "green" if is_active else "gray"
            
            if show_radii and is_active:
                folium.Circle(
                    location=[r_lat, r_lon],
                    radius=radius_km * 1000,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.3
                ).add_to(m)
            
            popup_text = f"{pointer_text}<br>Radius: {radius_km:.2f} km" if is_active else f"{pointer_text}<br>Available from: {available_from.date()} to {available_to.date()}"
            folium.Marker([r_lat, r_lon], popup=popup_text, tooltip=pointer_text, icon=folium.Icon(color=color)).add_to(m)
    
    return m

st.title("User Location on Map")

username, authenticated, password = authenticate()
if authenticated and password:
    show_radii = st.checkbox("Show Radii", value=True)
    loc = None  # Ensure loc is always defined
    
    if st.checkbox("Check my location"):
        loc = get_geolocation()
        st.write(f"Your coordinates are {loc}")
        if loc and "coords" in loc:
            lat, lon = loc["coords"]["latitude"], loc["coords"]["longitude"]
            folium_static(plot_location(lat, lon, show_radii), width=700, height=500)
            
            if st.button("Save My Location"):
                save_user_location(username, password, lat, lon)
                st.success("Location saved successfully.")
    
    with st.expander("Show Saved Locations"):
        saved_df = load_user_locations(username, password)
        if not saved_df.empty:
            m_saved = folium.Map(location=[52.215808, 6.848512], zoom_start=12)
            for _, row in saved_df.iterrows():
                folium.Marker([row["lat"], row["lon"]], popup=row["timestamp"], icon=folium.Icon(color='blue')).add_to(m_saved)
            folium_static(m_saved, width=700, height=500)
        else:
            st.write("No saved locations found.")
    
    if st.button("Save My Current Location"):
        if loc and "coords" in loc:
            lat, lon = loc["coords"]["latitude"], loc["coords"]["longitude"]
            save_user_location(username, password, lat, lon)
            st.success("Current location saved successfully.")