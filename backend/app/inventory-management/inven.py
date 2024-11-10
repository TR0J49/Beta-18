import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Load the dataset (Make sure to update the path to your CSV file)
inventory_data = pd.read_csv("inventory_data_updated.csv")

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the dashboard with an orange-white gradient background
app.layout = html.Div(
    style={'background': 'linear-gradient(to bottom, #FFA500, #FFFFFF)', 'font-family': 'Arial'},
    children=[
        html.H1("Hostel Mess Inventory Dashboard", style={'textAlign': 'center', 'color': '#333', 'padding': '10px'}),

        # Input section to record consumed quantity
        html.Div(
            [
                html.Label("Select Food Item:", style={'font-weight': 'bold', 'color': '#555'}),
                dcc.Dropdown(
                    id='food-item-dropdown',
                    options=[{'label': item, 'value': item} for item in inventory_data['Food Name'].unique()],
                    value=inventory_data['Food Name'].unique()[0],
                    style={'width': '60%', 'marginBottom': '10px'}
                ),
                html.Label("Quantity Used (kg):", style={'font-weight': 'bold', 'color': '#555'}),
                dcc.Input(
                    id='quantity-used-input', type='number', min=0, placeholder="Enter quantity in kg",
                    style={'width': '60%', 'marginBottom': '10px'}
                ),
                html.Button(
                    "Update Inventory", id='update-button', n_clicks=0,
                    style={'backgroundColor': '#333', 'color': 'white', 'padding': '10px 20px', 'border': 'none', 'cursor': 'pointer'}
                )
            ],
            style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'backgroundColor': '#fff',
                   'width': '80%', 'margin': '0 auto', 'marginBottom': '20px'}
        ),

        # Alert message section
        html.Div(id='alert-message', style={'display': 'none', 'backgroundColor': '#ffcccc', 'color': 'red', 'padding': '10px', 'border': '1px solid red', 'border-radius': '5px', 'textAlign': 'center'}),

        # Charts section with a responsive grid layout for multiple visualizations
        html.Div(
            [
                html.Div([dcc.Graph(id="usage-histogram-chart")], style={'flex': '1', 'padding': '10px', 'border': '2px solid #333', 'margin': '10px', 'border-radius': '8px'}),
                html.Div([dcc.Graph(id="usage-pie-chart")], style={'flex': '1', 'padding': '10px', 'border': '2px solid #333', 'margin': '10px', 'border-radius': '8px'}),
                html.Div([dcc.Graph(id="stacked-area-chart")], style={'flex': '1', 'padding': '10px', 'border': '2px solid #333', 'margin': '10px', 'border-radius': '8px'}),
                html.Div([dcc.Graph(id="food-amount-bar-chart")], style={'flex': '1', 'padding': '10px', 'border': '2px solid #333', 'margin': '10px', 'border-radius': '8px'}),
                html.Div([dcc.Graph(id="food-amount-donut-chart")], style={'flex': '1', 'padding': '10px', 'border': '2px solid #333', 'margin': '10px', 'border-radius': '8px'}),
            ],
            style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'}
        ),
    ]
)

# Callback to update the data and charts when quantity is consumed
@app.callback(
    [Output("usage-histogram-chart", "figure"),
     Output("usage-pie-chart", "figure"),
     Output("stacked-area-chart", "figure"),
     Output("food-amount-bar-chart", "figure"),
     Output("food-amount-donut-chart", "figure"),
     Output("alert-message", "style")],
    [Input("update-button", "n_clicks"), Input("food-item-dropdown", "value"), Input("quantity-used-input", "value")]
)
def update_charts(n_clicks, food_item, quantity_used):
    global inventory_data
    
    # Update the dataset if an item and quantity were specified
    if n_clicks > 0 and food_item and quantity_used is not None:
        inventory_data.loc[inventory_data['Food Name'] == food_item, 'Used'] += quantity_used
        inventory_data.loc[inventory_data['Food Name'] == food_item, 'Quantity'] -= quantity_used
        inventory_data['Quantity'] = inventory_data['Quantity'].clip(lower=0)  # Ensure quantity doesn't go negative

    # Check if any food item's quantity is below 5kg
    low_inventory_item = inventory_data[inventory_data['Quantity'] < 5]
    alert_style = {'display': 'none'}  # Hide the alert by default

    if not low_inventory_item.empty:
        alert_style = {'display': 'block'}
    
    # Histogram showing the frequency of each food item's usage
    histogram_chart = px.histogram(
        inventory_data, x="Food Name", y="Used", title="Usage Frequency by Food Item",
        labels={'Used': 'Quantity Used (kg)'}, template="seaborn"
    )
    histogram_chart.update_layout(
        title={'x': 0.5},
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
        paper_bgcolor='rgba(0,0,0,0)'   # Transparent paper background
    )

    # Pie chart for proportion of total used for each item
    pie_chart = px.pie(
        inventory_data, names="Food Name", values="Used", title="Usage Proportion by Food Item",
        template="seaborn"
    )
    pie_chart.update_layout(
        title={'x': 0.5},
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
        paper_bgcolor='rgba(0,0,0,0)'   # Transparent paper background
    )

    # Stacked area chart showing the remaining quantity over time for each food item
    area_chart = px.area(
        inventory_data, x="Food Name", y="Quantity", color="Food Name", title="Remaining Quantity Over Time",
        labels={"Quantity": "Quantity Remaining (kg)"}, template="seaborn"
    )
    area_chart.update_layout(
        title={'x': 0.5},
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
        paper_bgcolor='rgba(0,0,0,0)'   # Transparent paper background
    )

    # Bar chart showing total food amount used by each food item
    bar_chart = px.bar(
        inventory_data, x="Food Name", y="Food Amount", title="Food Amount by Item",
        labels={"Food Amount": "Total Food Amount (kg)"}, template="seaborn"
    )
    bar_chart.update_layout(
        title={'x': 0.5},
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
        paper_bgcolor='rgba(0,0,0,0)'   # Transparent paper background
    )

    # Donut chart for the total food amount breakdown by item
    donut_chart = px.pie(
        inventory_data, names="Food Name", values="Food Amount", title="Food Amount Breakdown by Item",
        hole=0.4, template="seaborn"
    )
    donut_chart.update_layout(
        title={'x': 0.5},
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
        paper_bgcolor='rgba(0,0,0,0)'   # Transparent paper background
    )

    # Return all figures and alert style
    return histogram_chart, pie_chart, area_chart, bar_chart, donut_chart, alert_style

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
