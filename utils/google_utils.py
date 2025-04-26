def create_googlemaps_object():
    import googlemaps
    return googlemaps.Client(key="GOOGLE_KEY")

def address_to_location(googlemap_object, address):
    location = googlemap_object.geocode(address)[0]["geometry"]["location"]
    return [location["lat"], location["lng"]]