# Dash Library
import dash
import dash_bootstrap_components as dbc


app = dash.Dash(__name__, external_stylesheets=[dbc.icons.FONT_AWESOME,dbc.icons.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
