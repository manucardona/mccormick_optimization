import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime
from utils.google_utils import create_googlemaps_object, address_to_location

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("McCormick Optimizer 🚇"),
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
])

@app.callback(
    Output('route-stops', 'children'),
    Output('disruptions', 'children'),
    Input('get-route', 'n_clicks'),
    State('start-address', 'value'),
    State('end-address', 'value'),
    State('travel-date', 'date')
)
def suggest_route(n_clicks, start_address, end_address, travel_date):
    if n_clicks is None or not start_address or not end_address:
        return [], []

    # Step 1: Convert addresses to lat, lon
    start_lat, start_lon = address_to_location(start_address)
    end_lat, end_lon = address_to_location(end_address)

    # Step 2: Call your transit routing function here
    route_data = get_transit_route(start_lat, start_lon, end_lat, end_lon, GOOGLE_API_KEY)

    # Step 3: Extract stops
    stops = extract_stops(route_data)

    # Step 4: Cross-match with events dataset (optional for now)
    disruptions = check_disruptions(stops, travel_date)

    stop_list = [html.Li(stop["name"]) for stop in stops]
    disruption_list = [html.Li(disruption) for disruption in disruptions]

    return stop_list, disruption_list
