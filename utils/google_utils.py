from dotenv import load_dotenv
import os
import googlemaps

def create_googlemaps_object():
    # Load environment variables from .env
    load_dotenv()

    try:
        GOOGLE_KEY = os.environ["GOOGLE_KEY"]
    except KeyError:
        raise Exception(
            "Make sure that you have set the API Key environment variable as described in the README."
        )
    
    return googlemaps.Client(key=GOOGLE_KEY)

def address_to_location(googlemap_object, address):
    google_address = googlemap_object.geocode(address)
    if google_address:
        location = google_address[0]["geometry"]["location"]
        return [location["lat"], location["lng"]]
    else:
        return -1, -1
    