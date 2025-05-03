import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import json
from datetime import datetime
import folium
import polyline
import os
from shapely.geometry import Point
from utils.google_utils import create_googlemaps_object, address_to_location
from utils.route_utils import get_transit_route
from utils.transport_radius import create_buffer
from pyproj import Transformer

MAP_FILE = "assets/map.html"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create initial empty map if not exist
if not os.path.exists(MAP_FILE):
    fmap = folium.Map(location=[41.8781, -87.6298], zoom_start=12)  # Chicago
    fmap.save(MAP_FILE)

app.layout = dbc.Container([
    html.H1("smooth_navigator 🚇"),
    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Label("Starting Address:"),
            dcc.Input(id='start-address', type='text', placeholder='Enter start address', style={"width": "100%"}),
        ]),
        dbc.Col([
            html.Label("Ending Address:"),
            dcc.Input(id='end-address', type='text', placeholder='Enter end address', style={"width": "100%"}),
        ]),
        dbc.Col([
            html.Label("Travel Date:"),
            dcc.DatePickerSingle(
                id='travel-date',
                min_date_allowed=datetime(datetime.today().year, 1, 1),
                max_date_allowed=datetime(datetime.today().year, 12, 31),
                initial_visible_month=datetime.today()
            )
        ]),
    ], className="mb-4"),

    dbc.Button("Get Route", id='get-route', color='primary', className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.H4("Route Stops:"),
            html.Ul(id='route-stops')
        ]),
        dbc.Col([
            html.H4("Potential Disruptions:"),
            html.Ul(id='disruptions')
        ])
    ]),

    dbc.Row([
        dbc.Col([
            html.H4("Map:"),
            html.Iframe(id='map', src='/assets/map.html', width='100%', height='600')
        ])
    ]),
])

@app.callback(
    Output('route-stops', 'children'),
    Output('disruptions', 'children'),
    Output('map', 'src'),
    Input('get-route', 'n_clicks'),
    State('start-address', 'value'),
    State('end-address', 'value'),
    State('travel-date', 'date')
)
def suggest_route(n_clicks, start_address, end_address, travel_date):
    if n_clicks is None or not start_address or not end_address:
        return [], [], '/assets/map.html'

    g_object = create_googlemaps_object()
    start_lat, start_lon = address_to_location(g_object, start_address)
    end_lat, end_lon = address_to_location(g_object, end_address)

    route_data = get_transit_route(start_lat, start_lon, end_lat, end_lon)
    route_points = route_data

    with open("data/choose_chicago_events.json", "r") as f:
        events_data = json.load(f)

    event_buffers = []
    disruptions_list = []

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

    for event in events_data:
        address = event["location"]
        lat, lon = address_to_location(g_object, address)

        if lat != -1:
            x, y = transformer.transform(lon, lat)
            event_point_proj = Point(x, y)
            event_buffer = event_point_proj.buffer(500)
            event_buffers.append((event["event_name"], (lat, lon), event_buffer))

    fmap = folium.Map(location=[start_lat, start_lon], zoom_start=13)
    folium.PolyLine(route_points, color="blue", weight=5).add_to(fmap)

    for event_name, (lat, lon), event_buffer in event_buffers:
        folium.Circle(
            location=[lat, lon],
            radius=500,
            color='red',
            fill=True,
            fill_opacity=0.25,
            popup=event_name
        ).add_to(fmap)

        for rlat, rlon in route_points:
            rx, ry = transformer.transform(rlon, rlat)
            if event_buffer.contains(Point(rx, ry)):
                disruptions_list.append(event_name)
                break

    fmap.save(MAP_FILE)

    route_stops = [
        html.Li(f"{start_address}"),
        html.Li(f"{end_address}")
    ]
    disruptions_html = [html.Li(d) for d in disruptions_list]
    map_src = f"/assets/map.html?reload={n_clicks}"

    return route_stops, disruptions_html, map_src

if __name__ == "__main__":
    app.run(debug=True, port=8052)
