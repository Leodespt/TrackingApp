# Dash library
from dash import html, dcc
import dash_bootstrap_components as dbc

# %% Error Page Layout
layout = dbc.Container([
    html.Br(),
    dbc.Container([
        dcc.Location(id='err404', refresh=True),
        dbc.Container(
            html.Img(
                src='/assets/dash-logo-stripe.svg',
                className='center'
            ),
        ),
        dbc.Container([
            dbc.Container(id='outputState', children='Error 404 - Page not found')
        ], className='form-group'),
    ], className='jumbotron')
])
