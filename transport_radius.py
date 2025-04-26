import httpx
import lxml.html
from shapely.geometry import Point
from shapely import wkt
import pandas as pd
import json

def get_l_stations():
    """
    Uses the L stations API
    """
    stations_text = httpx.get("https://data.cityofchicago.org/resource/8pix-ypme.json")
    stations = json.loads(stations_text.text)
    df = pd.DataFrame(stations)
    df["geolocation"] = df["location"].apply(create_shapely_point)
    return df

def create_shapely_point(location):
    """
    Assumes the location is a dict with 'latitude' and 'longitude'
    """
    lat = location.get('latitude')
    long = location.get('longitude')
    if lat is not None and long is not None:
        return Point(long, lat)
    return None
    
def get_l_stations_in_radius(circle):
    """
    Given a Shapely buffer 'circle', return the L stations that fall within the 
    buffer
    """
    stations = get_l_stations()
    return stations[stations['geolocation'].apply(lambda geom: circle.contains(geom))]

def get_cta_bus_stops():
    df = pd.read_csv("data/cta_bus_stops.csv")
    df['geolocation'] = df['the_geom'].apply(wkt.loads)
    return df

def get_cta_bus_stops_in_radius(circle):
    stops = get_cta_bus_stops()
    return stops[stops['geolocation'].apply(lambda geom: circle.contains(geom))]

def find_transport_within_radius(point, radius):
    circle = point.buffer(radius)

