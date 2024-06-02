# Dash library
import dash_bootstrap_components as dbc
from dash import html, dash_table, dcc
from dash.dependencies import Input, Output

# Other imports
from app_init import app
import data_preparation as dataP
from data_preparation import usd_value

# Formating of the thousand values in $
import locale
from dash.dash_table.Format import Format, Symbol, Group, Scheme
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# %% Display style of the tables and charts

WRAPPER_STYLE = {
    'margin-right': 'auto',
    'margin-left': 'auto',
    'max-width': '1200px',
    'padding-right': 'auto',
    'padding-left': 'auto',
    'margin-top': '32px',
}

# %% Creation of the header of the page
# Including Title and global info of the wallet (Size and Total P&L)
header = html.Div(
                children=[
                        html.Div(style = {
                        'backgroundColor': '#111111'},
                        children=[
                                html.P(children="📈📉", className="header-emoji"),
                                html.H3(children="Realized P&L", className="header-title"),
                                html.Br(),
                                html.H4(html.Div(id='totalPL'),className="header-description",)
                                ],className="header")],className='jumbotron')

################################################################################
# RETRUN P&L VALUE OF THE PORTFOLIO
################################################################################
@app.callback(Output('totalPL', 'children'),
      [Input('pageContent', 'children')]) 
def TotalPL(pageContent):

    df = dataP.data()
    currency = 'EUR'#show_currency(current_user.username)
    usd_eur_rate = usd_value()

    if (df.empty or df['qty_bought'].sum() == 0):
            description = html.Div('No data to be displayed')
    else : 
            pl_sum = dataP.final_pl(dataP.actual_summary(df)[1])["P&L"].sum()
            
            if currency == 'EUR':
                    pl_sum = pl_sum * usd_eur_rate
                    symbol = "€"
            else : 
                    symbol = "$"

            
            pl_formatted = locale.format_string("%.2f", pl_sum, grouping=True)
            color = 'red' if pl_sum < 0 else 'green'

            description = html.Div(
                    f'{ "+" if pl_sum > 0 else ""}{pl_formatted} {symbol}',
                    style={'text-align': 'center', 'color': color},
                    className="header-description"
            )
    return description


# %% Chart part of the page
# Initialisation of the P&L table
chart = dbc.Row(
      dbc.Col(dash_table.DataTable(
        id= "PL-table",
        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['Date', 'Region']
        ],
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
        style_as_list_view=True,
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'center',
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
            }
        ]
    ), className='jumbotron'),
    style=WRAPPER_STYLE
)

"""
# Money values formating for EUR
money = Format(
                scheme= Scheme.fixed, 
                precision=2,
                group= Group.yes,
                groups=3,
                group_delimiter=',',
                decimal_delimiter='.',
                symbol= Symbol.yes, 
                symbol_suffix=u'€') 
"""

################################################################################
# COMPUTING OF THE P&L TABLE
################################################################################
@app.callback(Output('PL-table', 'data'),
              Output('PL-table', 'columns'),
              Input('pageContent', 'children'))
def update_table(pageContent):
    df = dataP.data()
    currency = 'EUR' #show_currency(current_user.username)
    usd_eur_rate = usd_value()
    money = dash_table.FormatTemplate.money(2)

    if df.empty or df['qty_bought'].sum() == 0:
        
        empty_row = {
              'crypto':'',
              'P&L':0
        }        
        data = [empty_row]

    else :

        # Link the TransactionData to the P&L page
        df = dataP.final_pl(dataP.actual_summary(df)[1])

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
            df['P&L'] = df['P&L']* usd_eur_rate

        
        data = df.to_dict('records')

    # Table column creation and formatting
    columns = [
        {'id': 'crypto', 'name': 'Crypto'},
        {'id': 'P&L', 'name': 'Realised Profits & Losses', 'type': 'numeric', 'format': money}]

    # Return the updated data and columns
    return data, columns


# %% Accepted/Realized P&L layout

layout = html.Div([dbc.Container([
header,
chart
], style={"textAlign": "center"})])