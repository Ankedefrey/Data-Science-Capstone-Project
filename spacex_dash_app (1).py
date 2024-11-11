# Import required libraries
from dash import dcc, html, Input, Output
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
# Empty dict
launch_sites = []
# Dict for "All Sites"
launch_sites.append({'label': 'All Sites', 'value': 'All Sites'})
# Loop through unique launch site names if there is
for site in spacex_df["Launch Site"].value_counts().index:
    launch_sites.append({'label': site, 'value': site})
    # Note to self: label - user see ; value - Dash use
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', options = launch_sites, value = 'All Sites', placeholder = "Select a Launch Site here", searchable = True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                # Line break
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min = 0, max = 10000, step = 1000, value = [min_payload, max_payload],
                                                marks={ 0: {'label': '0 (Kg)'}, 2500: {'label': '2500 (Kg)'}, 5000: {'label': '5000 (Kg)'}, 7500: {'label': '7500 (Kg)'}, 10000: {'label': '10000 (Kg)'}}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
# check if ALL sites were selected or just a specific launch site was selected
def select(input_site):
    if input_site == 'All Sites':
        aggregated_df = spacex_df.groupby('Launch Site')["class"].sum().reset_index()
        fig = px.pie(aggregated_df, values='class', names='Launch Site', title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == input_site]
        success_counts = filtered_df['class'].value_counts().rename({0: 'Failure', 1: 'Success'}).reset_index()
        success_counts.columns = ['Outcome', 'Count']
        fig = px.pie(success_counts, values='Count', names='Outcome', title=f'Total Success Launches for {input_site}')
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback( Output(component_id='success-payload-scatter-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'), Input(component_id='payload-slider', component_property='value') 
)
def scatter(input_site, payload_range):
    # Filter data based on selected site and payload range
    filtered_df = spacex_df if input_site == 'All Sites' else spacex_df[spacex_df["Launch Site"] == input_site]
    payload_filtered_df = filtered_df[(filtered_df["Payload Mass (kg)"] >= payload_range[0]) &
                                      (filtered_df["Payload Mass (kg)"] <= payload_range[1])]
    
    fig = px.scatter(payload_filtered_df, x="Payload Mass (kg)", y="class", 
                     color="Booster Version Category",
                     title=f"Payload vs. Outcome for {'All Sites' if input_site == 'All Sites' else input_site}")
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8053)
