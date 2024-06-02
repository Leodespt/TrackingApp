# Dash Library
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# Other imports
from app_init import app
from views import AcceptedPL, Wallet, InvestmentStats, error

navBar = dbc.Navbar(id='navBar',
    children=[],
    sticky='top',
    color='primary',
    className='navbar navbar-expand-lg navbar-dark bg-primary',
)

layout = html.Div([
    #dcc.Store(id='session-store-currency', storage_type='session',data={'currency': 'EUR'}),
    dcc.Location(id='url', refresh=False),
    html.Div([
        navBar,
        html.Div(id='pageContent')
    ])
], id='table-wrapper')

################################################################################
# HANDLE PAGE ROUTING - IF USER NOT LOGGED IN, ALWAYS RETURN TO LOGIN SCREEN
################################################################################
@app.callback(Output('pageContent', 'children'),
              [Input('url', 'pathname')])
def displayPage(pathname):

        if pathname == '/':
            return Wallet.layout

        if pathname == '/AcceptedPL':
            return AcceptedPL.layout

        if pathname == '/InvestmentStats':
            return InvestmentStats.layout

        else:
            return error.layout


################################################################################
# ONLY SHOW NAVIGATION BAR WHEN A USER IS LOGGED IN
################################################################################
@app.callback(
    Output('navBar', 'children'),
    [Input('pageContent', 'children')])
def navBar(pageContent):

    navBarContents = [
        dbc.Col([
            dbc.Row([
            dbc.NavItem(dbc.NavLink('Wallet', href='/')),
            dbc.NavItem(dbc.NavLink('Accepted P&L', href='/AcceptedPL')),
            dbc.NavItem(dbc.NavLink('Investment Statistics', href='/InvestmentStats')),
        ])],width="auto"),

        # Select Currency

        dbc.Col([
            dbc.Row([
            dcc.Dropdown(
                id='user-currency',
                options=[
                    {'label': 'USD', 'value': 'USD'},
                    {'label': 'EUR', 'value': 'EUR'}
                ],
                value= 'EUR',  # Default option
                style={'width': '80px'},  # Align to the right
                clearable=False,
            ),
            dbc.NavItem(html.Div(id='selected-currency-global')),
        ])],style={'margin-left': 'auto'} ,width="auto"),
    ]
    return navBarContents

"""
# Callback to update session state when currency dropdown value changes
@app.callback(
    Output('session-store', 'data'),
    [Input('user-currency', 'value')]
)
def update_currency(selected_currency):
    if selected_currency:
        return {'currency': selected_currency}
    else:
        raise PreventUpdate
"""


