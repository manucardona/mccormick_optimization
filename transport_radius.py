import httpx
import lxml.html

def get_l_stations():
    stations = httpx.get("https://data.cityofchicago.org/resource/8pix-ypme.json")
    

def get_metra_stations():
    