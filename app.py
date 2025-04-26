import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import json
from datetime import datetime
import folium
import polyline
import os
from shapely.geometry import Polygon, Point
from utils.google_utils import create_googlemaps_object, address_to_location
from utils.route_utils import get_transit_route
from utils.transport_radius import create_buffer

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
                min_date_allowed=datetime.today(),
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

    # Step 1: Convert addresses to lat, lon
    g_object = create_googlemaps_object()
    start_lat, start_lon = address_to_location(g_object, start_address)
    end_lat, end_lon = address_to_location(g_object, end_address)

    # Step 2: Get route
    route_data = get_transit_route(start_lat, start_lon, end_lat, end_lon)

    # Decode the polyline
    #encoded_polyline = route_data["routes"][0]["overview_polyline"]["points"]
    route_points = route_data

    # Step 3: Load events and create buffers
    with open("data/choose_chicago_events.json", "r") as f:
        events_data = json.load(f)

    event_buffers = []
    disruptions_list = []

    for event in events_data:
        address = event["location"]
        lat, lon = address_to_location(g_object, address)
        if lat != -1:
            event_buffer = Point(lon, lat).buffer(500)
            #event_buffer = create_buffer(lat, lon, 500)  # 500 meter buffer
            for point in route_data:
                if event_buffer.contains(Point(point[1], point[0])):
                    event_buffers.append((event["event_name"], event_buffer))
                    break

    # Step 4: Create a Folium map
    fmap = folium.Map(location=[start_lat, start_lon], zoom_start=13)

    # Add route polyline
    folium.PolyLine(route_points, color="blue", weight=5).add_to(fmap)

    # Step 5: Add event buffers to the map
    for event_name, event_buffer in event_buffers:
        # Add as CircleMarker around event center
        center = list(event_buffer.centroid.coords)[0]
        folium.Circle(
            location=[center[1], center[0]],
            radius=500,
            color='red',
            fill=True,
            fill_opacity=0.4,
            popup=event_name
        ).add_to(fmap)

        # Step 6: Check for disruptions
        for lat, lon in route_points:
            if event_buffer.contains(Point(lon, lat)):
                disruptions_list.append(event_name)
                break  # No need to check more points for this event

    # Save the map
    fmap.save(MAP_FILE)

    # Build route stop list
    route_stops = [
        html.Li(f"{start_address}"),
        html.Li(f"{end_address}")
    ]
    disruptions_html = [html.Li(d) for d in disruptions_list]

    # Force reload map by modifying src URL slightly (cache buster)
    map_src = f"/assets/map.html?reload={n_clicks}"

    return route_stops, disruptions_html, map_src

if __name__ == "__main__":
    app.run(debug=True, port=8052)
