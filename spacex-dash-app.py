# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Liste der Startplätze für Dropdown-Optionen
launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = [{'label': 'Alle Startplätze', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',  # Standardwert
        placeholder='Wählen Sie hier einen Startplatz aus',
        searchable=True
    ),

    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2000)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Callback function to update the pie chart based on dropdown selection
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Show all data: Sum successful launches (class = 1) per launch site
        fig = px.pie(
            # Only successful launches
            spacex_df[spacex_df['class'] == 1],
            names='Launch Site',
            title='Overall success rate of all starting positions'
        )
    else:
        # Filter the DataFrame for the selected start page
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]

        # Count successes and failures (class = 1 or 0)
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        success_counts['class'] = success_counts['class'].replace(
            {1: 'Success', 0: 'Failure'})

        # Create the pie chart with custom colors
        fig = px.pie(
            success_counts,
            names='class',
            values='count',
            title=f'Start success rate for starting position {selected_site}',
            # References the column for color matching
            color='class',  
            color_discrete_map={
                'Success': '#2ecc71',   # Green
                'Failure': '#e74c3c'    # Red
            },
            # Define order for legend
            category_orders={'class': ['Success', 'Failure']} 
        )

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range

    # Filter by payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site == 'ALL':
        df_plot = filtered_df
        title = 'Launch success for all sites'
    else:
        df_plot = filtered_df[filtered_df['Launch Site'] == selected_site]
        title = f'Launch success for site {selected_site}'

    fig = px.scatter(
        df_plot, x='Payload Mass (kg)', y='class',
        color='Booster Version Category',
        title=title,
        labels={'class': 'Launch Outcome (0=Fail,1=Success)'}
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run(port=8051, debug=True)
