import httpx
from shapely.geometry import Point
from shapely import wkt
import pandas as pd
import json
import pyproj
import utm

def get_l_stations():
    """
    Uses the L stations API
    """
    stations_text = httpx.get("https://data.cityofchicago.org/resource/8pix-ypme.json")
    stations = json.loads(stations_text.text)
    df = pd.DataFrame(stations)
    df["geolocation_latlong"] = df["location"].apply(create_shapely_point)
    df["geolocation"] = df["geolocation_latlong"].apply(latlong_to_utm)
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
    
def latlong_to_utm(point):
    """
    From Gemini with the query: 
    I have a pandas dataframe column geolocation which contains Point objects in the lat long format. 
    Give me only the Python code that would convert this column into the appropriate projection for
    using buffers in meters.
    
    Projects a Shapely Point (in lat/lon) to the appropriate UTM zone (Northern Hemisphere) in meters.
    """
    lat, lon = point.y, point.x
    zone_number = utm.from_latlon(lat, lon)[2]
    epsg_code = f"EPSG:326{zone_number}"  # Northern hemisphere
    utm_crs = pyproj.CRS(epsg_code)
    wgs84 = pyproj.CRS("EPSG:4326")
    transformer = pyproj.Transformer.from_crs(wgs84, utm_crs, always_xy=True)
    utm_x, utm_y = transformer.transform(lon, lat)
    return Point(utm_x, utm_y)

def get_l_stations_in_radius(center_lat, center_long, radius):
    """
    Given a Shapely buffer 'circle', return the L stations that fall within the 
    buffer
    """

    center = latlong_to_utm(Point(center_long, center_lat))
    circle = center.buffer(radius)

    stations = get_l_stations()
    return stations[stations['geolocation'].apply(lambda geom: circle.contains(geom))]

def get_cta_bus_stops():
    """
    Downloaded from https://catalog.data.gov/dataset/cta-busstops
    """
    df = pd.read_csv("data/cta_bus_stops.csv")
    df['geolocation_latlong'] = df['the_geom'].apply(wkt.loads)
    df["geolocation"] = df["geolocation_latlong"].apply(latlong_to_utm)
    return df

def get_cta_bus_stops_in_radius(center_lat, center_long, radius):
    """
    Given a Shapely buffer 'circle', return the bus stops that fall within the 
    buffer
    """

    center = latlong_to_utm(Point(center_long, center_lat))
    circle = center.buffer(radius)

    stops = get_cta_bus_stops()
    return stops[stops['geolocation'].apply(lambda geom: circle.contains(geom))]

def get_stations_and_stops_in_radius(center_lat, center_long, radius):
    """
    Gets the L stations and CTA bus stops contained within the circle centered
    around the point specified
    """    
    stations = get_l_stations_in_radius(center_lat, center_long, radius)
    stops = get_cta_bus_stops_in_radius(center_lat, center_long, radius)

    stations_dict = stations.rename(columns={'location': 'geometry'}).apply(lambda row: {'name': row['name'], 'location': row['geometry']}, axis=1).tolist()
    

def create_buffer(center_lat, center_long, radius):
    """
    Returns a Polygon that is a buffer around the center point specified
    """
    center = latlong_to_utm(Point(center_long, center_lat))
    return center.buffer(radius)