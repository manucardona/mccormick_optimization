import requests
import os
from dotenv import load_dotenv
import os
import polyline

def get_transit_route(start_lat, start_lon, end_lat, end_lon):
    # Load environment variables from .env
    load_dotenv()

    try:
        GOOGLE_KEY = os.environ["GOOGLE_KEY"]
    except KeyError:
        raise Exception(
            "Make sure that you have set the API Key environment variable as described in the README."
        )

    url = (
        f"https://maps.googleapis.com/maps/api/directions/json"
        f"?origin={start_lat},{start_lon}"
        f"&destination={end_lat},{end_lon}"
        f"&mode=transit"
        f"&key={GOOGLE_KEY}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        route_data = response.json()
        encoded_polyline = route_data["routes"][0]["overview_polyline"]["points"]
        
        # Decode the polyline into list of (lat, lon)
        points = polyline.decode(encoded_polyline)
        return points
    else:
        print("Error:", response.status_code, response.text)
        return None