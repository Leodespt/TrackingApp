# Dash library
from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Other libraries
import plotly.express as px
import pandas as pd

# Other imports
from app import app
import data_preparation as dataP
from data_preparation import usd_value

# Set the locale for formatting
import locale
from dash.dash_table.Format import Format, Symbol, Group, Scheme
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Table column formatting
percentage = dash_table.FormatTemplate.percentage(2)

# %% Display style of the tables and charts

WRAPPER_STYLE = {
    'margin-right': 'auto',
    'margin-left': 'auto',
    'max-width': '1200px',
    'padding-right': 'auto',
    'padding-left': 'auto',
    'margin-top': '32px',
}

CARD_STYLE = {
    'margin-bottom': '24px',
    'box-shadow': '0 4px 6px 0 rgba(0, 0, 0, 0.18)',
}

CARD_STYLE_PIE = {
    'margin-bottom': '24px',
    'box-shadow': '0 4px 6px 0 rgba(0, 0, 0, 0.18)',
    'width': '500px'
}

# %% Header
# Header Layout
header = html.Div([
    html.Div(id='header'),
],className='jumbotron')

################################################################################
# UPDATE THE HEADER CONTENT WITH WALLET DATA
################################################################################
@app.callback(Output('header', 'children'), Input('pageContent', 'children'))
def update_header(pageContent):
    df = dataP.data()
    trx_summary = dataP.final_table(dataP.actual_summary(df)[0])
    asset_nb = len(trx_summary)
    currency = 'EUR'#show_currency(current_user.username)
    usd_eur_rate = usd_value()

    # If the database is empty
    if df.empty or df['qty_bought'].sum() == 0 or trx_summary.empty: 
        header_content = [
            html.Div(
                style={
                    'backgroundColor': '#111111',
                },
                children=[
                    html.P(children="📊", className="header-emoji"),
                    html.H1(children="My Wallet", className="header-title"),
                    html.Br(),
                    html.H4(html.Div('No crypto inside the wallet'), style={'color': 'white'})
                ],
                className="header",
            )
        ]
    # Else
    else : 
        total_table = dataP.total_table(trx_summary)

        wallet_value = float(total_table[0])
        wallet_pl = total_table[1]

        amount_invested = round((trx_summary)['Value'].sum(),2) - round((trx_summary)['P&L'].sum(),2)
        print(amount_invested)

        if currency == 'EUR':
            wallet_pl = wallet_pl * usd_eur_rate
            wallet_value = wallet_value * usd_eur_rate
            amount_invested = amount_invested * usd_eur_rate
            symbol = '€'
        else : 
            symbol = '$'

        # Format wallet_value and wallet_pl
        wallet_value = locale.format_string('%.2f', wallet_value, grouping=True)
        wallet_pl = locale.format_string('%.2f', wallet_pl, grouping=True)

        amount_invested = locale.format_string('%.2f', amount_invested, grouping=True)
        print(amount_invested)

        pl_pourcentage = locale.format_string('%.2f', total_table[2], grouping=True)

        header_content = [
            html.Div(
                style={
                    'backgroundColor': '#111111',
                },
                children=[
                    html.P(children="📊", className="header-emoji"),
                    html.H1(children="My Wallet", className="header-title"),
                    html.P(
                        f'{ f"You own {asset_nb} different assets." if asset_nb > 1 else "You own one asset." } ',
                        style={'text-align': 'center'},
                        className="header-description",
                    ),
                    html.P(
                        f'Wallet value : {wallet_value} {symbol}',
                        style={'text-align': 'center'},
                        className="header-description",
                    ),
                    html.P(
                        f'Amount invested : {amount_invested} {symbol}',
                        style={'text-align': 'center'},
                        className="header-description",
                    ),
                    html.P(
                        f'{ "+" if total_table[1] > 0 else ""}{wallet_pl} {symbol}',
                        style={
                            'text-align': 'center',
                            'color': 'red' if total_table[1] < 0 else 'green',
                        },
                        className="header-description",
                    ),
                    html.P(
                        f'{ "+" if total_table[2] > 0 else ""}{pl_pourcentage} %',
                        style={
                            'text-align': 'center',
                            'color': 'red' if total_table[2] < 0 else 'green',
                        },
                        className="header-description",
                    ),
                ],
                className="header",
            )
        ]
    return header_content


# %% Pie chart

################################################################################
# UPDATE THE PIE CHART CONTENT
################################################################################
@app.callback(Output('pie-chart', 'figure'), 
              Output('other-info-pie','children'),
            [Input('pageContent', 'children')])
def update_pie_chart(pageContent):
    
    df = dataP.data()
    currency = 'EUR'#show_currency(current_user.username)
    usd_eur_rate = usd_value()
    other_info = html.Br()
    asset_nb = html.P("You own no assets.", style={'max-width': '500px'})

    if df.empty or df['qty_bought'].sum() == 0: 
    # Create an empty pie chart figure
        #pie = px.pie(names=[], values=[])
        #pie.update_layout(
            #title={
                #"text": "Pie Chart - No Data",
            #})
        pie = {
            'data': [],
            'layout': {
                'title': 'Empty Pie Chart',
                'showlegend': False
            }
        }
        return pie, other_info
    else : 
        # Retrieve data for the pie chart
        trx_summary = dataP.final_table(dataP.actual_summary(df)[0])

        if currency == 'EUR':
            symbol = '€'
            trx_summary['Value'] = round(trx_summary['Value'] * usd_eur_rate,2)
        else : 
            symbol = '$'

        # Calculate the percentage of each element
        trx_summary['Percentage'] = trx_summary['Value'] / trx_summary['Value'].sum() * 100

        # Group elements representing less than 1,5% under "Other"
        threshold = 1.5  # Set the threshold percentage
        trx_summary['Name'] = trx_summary.apply(
            lambda row: row['Name'] if row['Percentage'] >= threshold else 'Other',
            axis=1)

        # Sort the data frame so that "Other" is the last row
        trx_summary = trx_summary.sort_values(by='Value', ascending=False)

        # Check if there is an "Other" section
        if 'Other' in trx_summary['Name'].values:
            other_info = html.P("Note : Assets with a wallet proportion lower then 1% are gathered in the 'Other' section.", style={'max-width': '500px'})

        explode = (0.02,) * len((trx_summary))

        # Define the formatting function
        def format_value(value):
            return locale.format_string('%.2f', value, grouping=True)
        
        trx_summary['Value_with_unit'] = trx_summary['Value'].apply(format_value).astype(str) + symbol

        pie = px.pie(
            trx_summary,
            values="Value",
            names='Name',
            height=500,
            width=500,
            custom_data=["Value_with_unit"]
        )
        pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='%{label} <br>Percent: %{percent} <br>Value: %{customdata[0]}' , # Include custom data in hoverinfo
            hole=.4,
            pull=explode,
        )
        pie.update_layout(
            title={
                "text": "Pie Chart",
                "font": {"color": "gray"},
            },
            legend={"font": {"color": "white"}},
            plot_bgcolor="white",
            paper_bgcolor="#111111"
        )
        return pie, other_info

# %% Data table 

################################################################################
# UPDATE THE INVESTMENT TABLE CONTENT
################################################################################
@app.callback(Output('investments-table', 'data'), 
              Output('investments-table-other', 'data'),
            Output('investments-table', 'columns'), 
            Output('investments-table-other', 'columns'), 
            Output('other-info', 'children'), 
            Input('pageContent', 'children'))
def update_table(pageContent):
    
    df = dataP.data()
    currency = 'EUR' #show_currency(current_user.username)
    usd_eur_rate = usd_value()
    other_info = html.Br()
    other_data = None
    money = dash_table.FormatTemplate.money(2)
    
    if df.empty or df['qty_bought'].sum() == 0:
        empty_row = {
            'Name': '',
            'Amount': 0.0,
            'Market Price': 0.0,
            'Value': 0.0,
            'Wallet %': 0.0,
            'Amount Invested':0.0,
            'P&L': 0.0,
            'P&L %': 0.0,
        }

        data = [empty_row]
    else : 
        # Your data
        trx_summary = dataP.final_table(dataP.actual_summary(df)[0])

        if currency == 'EUR':
            money = Format(
                    scheme= Scheme.fixed, 
                    precision=2,
                    group= Group.yes,
                    groups=3,
                    group_delimiter=',',
                    decimal_delimiter='.',
                    symbol= Symbol.yes, 
                    symbol_suffix=u'€') 
            trx_summary['Market Price'] = trx_summary['Market Price'] * usd_eur_rate
            trx_summary['Value'] = trx_summary['Value'] * usd_eur_rate
            trx_summary['P&L'] = trx_summary['P&L'] * usd_eur_rate
        
        trx_summary['Amount Invested'] = round((trx_summary)['Value'],2) - round((trx_summary)['P&L'],2)
        print(trx_summary['Amount Invested'])

        # Split the table into two parts based on "Wallet %"
        other_data = trx_summary[trx_summary['Wallet %']*100 < 1.5 ]
        data = trx_summary[trx_summary['Wallet %']*100 >= 1.5 ]

        if not other_data.empty:
            other_info = html.P("Assets with a wallet presence lower then 1,5 % : ")

        # Convert both parts to dictionaries
        other_data = other_data.to_dict('records')
        data = data.to_dict('records')


    # Table column creation and formatting
    columns = [
        dict(id='Name', name='Name'),
        dict(id='Amount', name='Amount', type='numeric'),
        dict(id='Market Price', name='Market Price', type='numeric', format=money),
        dict(id='Value', name='Value', type='numeric', format=money),
        dict(id='Wallet %', name='Wallet %', type='numeric', format=percentage),
        dict(id='Amount Invested', name='Amount Invested', type='numeric', format=money),
        dict(id='P&L', name='P&L', type='numeric', format=money),
        dict(id='P&L %', name='P&L %', type='numeric', format=percentage),
    ]

    other_columns = columns
  
    return  data, other_data, columns, other_columns, other_info



# %% Pie chart and table layout

# Chart part of the page
chart = dbc.Row([
    # Pie chart
    dbc.Col([
        dcc.Graph(
            id="pie-chart", 
            style=CARD_STYLE_PIE,#CARD_STYLE,
        ),
        html.Div(id = 'other-info-pie')],
        #html.P("Note : Assets with a wallet proportion lower then 1% are gathered in the 'Other' section.", style={'max-width': '500px'})],
        width=5.5,className='jumbotron' # Set the width of the column to take half of the row width
    ),
    # Investments table
    dbc.Col([
        dash_table.DataTable(
            id="investments-table",
            #style_cell_conditional=[
             #   {
              #      'if': {'column_id': c},
               #     'textAlign': 'left'
                #} for c in ['Date', 'Region']
            #],
            style_header={
                'backgroundColor': '#111111',
                'color': 'grey',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'color': '#F5F5F5',
                'backgroundColor': '#111111'
            },
            #style_as_list_view=True,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'whiteSpace': 'normal',
                'height' : 'auto',
                'minWidth': '110px', 'width': '110px', 'maxWidth': '110px',
            },
            style_data_conditional=[
                {
                    "if": {"column_id": "P&L", "filter_query": "{P&L} < 0"},
                    "color": "#FFA0A0"
                },
                {
                    "if": {"column_id": "P&L", "filter_query": "{P&L} >= 0"},
                    "color": "#C0FFC0"
                },
                {
                    "if": {"column_id": "P&L %", "filter_query": "{P&L %} < 0"},
                    "color": "#FFA0A0"
                },
                {
                    "if": {"column_id": "P&L %", "filter_query": "{P&L %} >= 0"},
                    "color": "#C0FFC0"
                }
            ]
        ),
        html.Div(id='other-info'),#html.P("Assets with a wallet presence lower then 1% : "),
        dash_table.DataTable(
                id="investments-table-other",
                #style_cell_conditional=[
                #    {
                #        'if': {'column_id': c},
                #        'textAlign': 'left'
                #    } for c in ['Date', 'Region']
                #],
                style_header = {'display': 'none'}, # Hide the header
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'color': '#F5F5F5',
                    'backgroundColor': '#111111',
                },
                #style_as_list_view=True,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'whiteSpace': 'normal',
                    'height' : 'auto',
                    'minWidth': '110px', 'width': '110px', 'maxWidth': '110px',
                },
                style_data_conditional=[
                    {
                        "if": {"column_id": "P&L", "filter_query": "{P&L} < 0"},
                        "color": "#FFA0A0"
                    },
                    {
                        "if": {"column_id": "P&L", "filter_query": "{P&L} >= 0"},
                        "color": "#C0FFC0"
                    },
                    {
                        "if": {"column_id": "P&L %", "filter_query": "{P&L %} < 0"},
                        "color": "#FFA0A0"
                    },
                    {
                        "if": {"column_id": "P&L %", "filter_query": "{P&L %} >= 0"},
                        "color": "#C0FFC0"
                    }
                ]
            ), 
            ], width=6,className='jumbotron'  # Set the width of the column to take half of the row width
   )
], style=WRAPPER_STYLE)

# %% Layout of the wallet page
#layout = html.Div([dbc.Container([
#header,
#chart
#], style={"textAlign": "center"})])

layout = html.Div([dbc.Container([
    header, 
    ], style={"textAlign": "center"}),
    dbc.Container([
    chart
    ], style={"textAlign": "center"}, fluid=True)
    ])

