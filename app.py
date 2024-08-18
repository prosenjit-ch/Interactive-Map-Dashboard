import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import requests
import time


st.markdown(
    """
    <style>
    /* Adjust padding for .st-emotion-cache-gh2jqd */
    @media (min-width: 576px) {
        .st-emotion-cache-gh2jqd {
            padding-left: 0rem;
            padding-right: 0rem;
        }
    }

    .st-emotion-cache-13ln4jf {
    width: 100%;
    padding: 0rem 0rem 0rem;
    max-width: 64rem;
}
    .st-emotion-cache-12fmjuu {
    position: fixed;
    top: 0px;
    left: 0px;
    right: 0px;
    height: 3.75rem;
    background: rgb(255, 255, 255);
    outline: none;
    z-index: 999990;
    display: none;
}
    .st-emotion-cache-6qob1r {
    position: relative;
    height: 100%;
    width: 100%;
    overflow: overlay;
    background-color: #00cec9;
}

    .st-emotion-cache-1mi2ry5 {
    display: flex;
    -webkit-box-pack: justify;
    justify-content: space-between;
    -webkit-box-align: start;
    align-items: start;
    padding: 0rem 0rem 0rem;
}

    .custom-text {
        background-color: #81ecec;
        color: black;
        padding: 1rem; /* Adjust padding to 2rem */
        border-radius: 10px;
        box-sizing: border-box; /* Ensures padding is included in element's total width and height */
    }
 
    .st-emotion-cache-128wn4a {
    width: 1024px;
    position: relative;
    display: flex;
    flex: 0 0 0%;
    flex-direction: column;
    gap: 0rem;
}
    </style>
    """,
    unsafe_allow_html=True
)

INITIAL_LOCATION = [23.8103, 90.4125]  



st.sidebar.title("Selected Location")

m = folium.Map(location=INITIAL_LOCATION, zoom_start=12, tiles="OpenStreetMap")

sidebar_placeholder = st.sidebar.empty()
sidebar_placeholder.markdown('<div class="custom-text">Select an area on the map to see details here.</div>', unsafe_allow_html=True)

def add_rectangle(bounds):
    southwest_lng, southwest_lat = bounds[0]
    northeast_lng, northeast_lat = bounds[1]
    folium.Rectangle(bounds=bounds, color="blue", fill=True, fill_opacity=0.2).add_to(m)
    center_lat = (southwest_lat + northeast_lat) / 2
    center_lng = (southwest_lng + northeast_lng) / 2


    osm_url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={center_lat}&lon={center_lng}&addressdetails=1"

    def fetch_location(url, retries=3, delay=2):
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; GeoAPI/1.0; +http://yourwebsite.com)"
        }
        for i in range(retries):
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Attempt {i + 1}: Failed with status code {response.status_code}. Retrying in {delay} seconds...")
                    time.sleep(delay)
            except requests.exceptions.RequestException as e:
                print(f"Attempt {i + 1}: Request failed with exception {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
        return None

    data = fetch_location(osm_url)

    if data:
        location_address = data.get('display_name', 'Location not found')
        sidebar_placeholder.markdown(f'<div class="custom-text">{location_address}</div>', unsafe_allow_html=True)
    else:
        sidebar_placeholder.write("Error: Unable to fetch location data after multiple attempts.")



draw_control = folium.plugins.Draw(export=False,
    draw_options={
        'polyline': False,
        'polygon': True,
        'circle': False,
        'rectangle': True,
        'marker': False,
        'circlemarker': False
    })
draw_control.add_to(m)


output = st_folium(m, width="100%", height=608)


if output["all_drawings"]:
    last_drawing = output["all_drawings"][-1]
    if last_drawing["geometry"]["type"] == "Polygon":
        bounds = last_drawing["geometry"]["coordinates"][0]
        southwest_lat, southwest_lng = bounds[0]
        northeast_lat, northeast_lng = bounds[2]
        add_rectangle([[southwest_lat, southwest_lng], [northeast_lat, northeast_lng]])
