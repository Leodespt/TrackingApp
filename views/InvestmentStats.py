# Dash library
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
from plotly.subplots import make_subplots

# Other imports
from app_init import app
import data_preparation as dataP
from data_preparation import usd_value

# Enables to retrive historical market data
import requests

# Formating of the thousand values in $
#import locale
#locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') 

# %% Display style of the tables and charts
MENU_STYLE = {
    'height': '112px',
    'width': '912px',
    'display': 'flex',
    'justify-content': 'space-evenly',
    'padding-top': '24px',
    'margin': '-80px auto 0 auto',
    'background-color': '#FFFFFF',
    'box-shadow': '0 4px 6px 0 rgba(0, 0, 0, 0.18)',
}

MENU_TITLE_STYLE = {
    'margin-bottom': '6px',
    'font-weight': 'bold',
    'color': '#079A82',
}

# %% Header layout
header = html.Div(
    children=[
        html.Div(style = {
  'backgroundColor': 'black', },
            children=[
                html.P(children="🧮", className="header-emoji"),
                html.H1(
                    children="Investment Statistiques", className="header-title"
                )],
            className="header")])


# %% Filter that enables the user to filter cryptos

filter_crypto = html.Div(
    children=[
        html.Div(children="Crypto", style = MENU_TITLE_STYLE),
        dcc.Dropdown(
            id="crypto-filter",
            clearable=False,
            className="dropdown",
            style={
                'backgroundColor': '#f9f9f9',
                'color': '#333333',
                'align-items': 'center',
                'justify-content': 'center',
                'width': '200px',
            },
        ),
    ]
)


################################################################################
# POPULATE THE CRYPTO-FILTER DROPDOWN OPTIONS
################################################################################
@app.callback(
    Output("crypto-filter", "options"),
    Output("crypto-filter", "value"),
    Input("pageContent", "children")  # You can adjust the input as needed
)
def populate_crypto_options(pageContent):

    crypto_list = dataP.unique_traded_crypto()
    crypto_list = [crypto for crypto in crypto_list if crypto not in ['BULL', 'ETHBULL']]

    # Sort the crypto list according to alphabetics
    crypto_list.sort()

    crypto_options = [
        {"label": crypto, "value": crypto}
        for crypto in crypto_list
    ]

    # Defines the default crypto value on BTC if BTC is in the list. 
    # Elsewise the first crypto in ht list is used.
    default_crypto = 'BTC' if 'BTC' in crypto_list else crypto_list[0] if len(crypto_list) > 0 else None

    return crypto_options, default_crypto

# %% Load crypto market data 
def load_price_data(interval, symbol):
    days = 500
    if interval == '1d':
        start_timestamp  = int ((datetime.today() - timedelta(days=days)).timestamp() * 1000)
    elif interval == '3d':
        start_timestamp  = int ((datetime.today() - timedelta(days=days*3)).timestamp() * 1000)
    elif interval == '1w':
        start_timestamp  = int ((datetime.today() - timedelta(days=days*7)).timestamp() * 1000)
    elif interval == '1M':
        start_timestamp  = int ((datetime.today() - timedelta(days=days*30)).timestamp() * 1000)

    try : 
        url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&startTime={start_timestamp}&endTime={int(datetime.today().timestamp() * 1000)}'
        response = requests.get(url)
        data = response.json()

        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

        # Convertir les timestamps en objets datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # convert numerical columns from str to float
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)

    except requests.exceptions.RequestException as e:

        df = pd.DataFrame()

    return df

# %% Regroup data into W, M or D for vertical crypto chart
def df_volume_formated(interval):
        if interval == '1w':
                p = 'W'
        if interval == '1M':
                p = 'M'
        if interval == '3d' or interval == '1d' :
                p = 'D'

        df = dataP.data()

        if df.empty :
            return df
        if df['qty_bought'].sum() == 0:
            return pd.DataFrame()
        else : 

            # Convert Date format so it is supported by graphs
            #df['Date'] = pd.to_datetime(df['Date'], format = '%Y-%m-%d').dt.strftime('%d/%m/%Y')

            # Group by 'Date', 'crypto', and 'action', and perform aggregations
            df = df.groupby(['Date', 'crypto', 'action']).sum(numeric_only=True).reset_index()

            # Convert 'Date' to datetime format
            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

            # Resample according to the desired frequency 'p' ('M' or 'W')
            df = df.set_index('Date').groupby(['crypto', 'action']).resample(p).sum(numeric_only=True)

            # Calculate the 'price' column as 'qty_spent' divided by 'qty_bought'
            df['price'] = df['qty_spent'] / df['qty_bought']

            # Filter rows where 'qty_bought' is not equal to 0
            df = df[df['qty_bought'] != 0]

            # Reset the index
            df = df.reset_index()
            return df


# %% Filter that enables a user to choose the interval of the graph (Daily, weekly, monthly)

filter_interval = html.Div(
    children=[
        html.Div(children="Interval", style = MENU_TITLE_STYLE),
        dcc.Dropdown(
            id="interval-filter",
            clearable=False,
            className="dropdown",
            value='1w',
            style={
                'backgroundColor': '#f9f9f9',
                'color': '#333333',
                'align-items': 'center',
                'justify-content': 'center',
                'width': '200px',
            },
        ),
    ]
)

################################################################################
# POPULATE THE INTERVAL DROPDOWN OPTIONS
################################################################################
@app.callback(
    Output("interval-filter", "options"),
    Input("pageContent", "children")  # You can adjust the input as needed
)
def populate_interval_options(pageContent):
    interval_options = [
        {"label": time, "value": time}
        for time in ['1d','3d','1w','1M'] # predefined interval
    ]
    return interval_options



# %% Callback of the price and avg acquisition price chart

################################################################################
# COMPUTATION OF AVG ACQUISITION PRICE CHART VALUES
################################################################################
@app.callback(Output(component_id='crypto-graph', component_property='figure'),
    [Input('crypto-filter', 'value'), 
     Input('interval-filter', 'value'),
     ])
def crypto_chart(selected_crypto, interval):
     
        df_volume = dataP.data()
        currency = 'EUR'#show_currency(current_user.username)
        usd_eur_rate = usd_value()

        if df_volume.empty or df_volume['qty_bought'].sum() == 0 or selected_crypto == None :
                # Handle the case where df_volume is empty
                # For example, you can display an error message or take other actions
                fig = go.Figure()
                fig.update_layout(
                    title={"text": "Price Chart - No Data ", "font": {"color": "gray"}},
                    plot_bgcolor="#111111",
                    paper_bgcolor="black",
                    height=600,
                )
                return fig
        
        else : 

            df_price = dataP.actual_summary(df_volume)[0]

            # If the selected crypto is not in the summary dataset
            # it means everything has been sold so there is no more average acquisition price
            if selected_crypto not in df_price.index:
                avg_price = 0

            else : 
                avg_price = round(df_price.loc[df_price.index == selected_crypto]['Price'].values[0],2) #/ dataP.usd_value()

            symbol = selected_crypto+'USDT'

            df = load_price_data(interval, symbol)

            if currency == 'EUR': 
                df['open'] = df['open'] * usd_eur_rate
                df['high'] = df['high'] * usd_eur_rate
                df['low'] = df['low'] * usd_eur_rate
                df['close'] = df['close']* usd_eur_rate
                avg_price = avg_price * usd_eur_rate
                currency_symbol = '€'
            else : 
                currency_symbol = '$'

            # If the crypto symbol is not supported by the Binance API
            if df.empty:
                fig = go.Figure()
                fig.update_layout(
                    title={"text": "Price Chart - Data Curretly Unavailable ", "font": {"color": "gray"}},
                    plot_bgcolor="#111111",
                    paper_bgcolor="black",
                    height=600,
                )
                return fig
            else : 

                fig = go.Figure(data=[go.Candlestick(x=df['timestamp'],
                                open=df['open'],
                                high=df['high'],
                                low=df['low'],
                                close=df['close'])])
                
                # Add a horizontal line at y = average acquisition price
                fig.add_shape(type='line', x0=df['timestamp'].iloc[0], y0=avg_price, x1=df['timestamp'].iloc[-1], y1=avg_price,
                        line=dict(color='#FFFFFF', width=2, dash='dot'))
                
                # Add the line value as an annotation
                fig.add_annotation(x=df['timestamp'].iloc[-1],
                                y=avg_price,
                                text=str(f"{avg_price:.2f}"+f' {currency_symbol}'),#locale.format_string('%.2f', avg_price, grouping=True)
                                showarrow=False,
                                font=dict(color="#FFFFFF",size=16),
                                yshift=10,
                                xshift = -50,
                                hovertext=str(f"{avg_price:.2f}"+f' {currency_symbol}'))#locale.format_string('%.2f', avg_price, grouping=True))

                fig.update_layout(
                        title={
                        "text": "Price Chart",
                        "font": {"color": "gray"},   
                        },
                        legend={
                        'font': {'color': 'gray'}
                        },
                        xaxis={
                        'tickfont': {'color': 'gray'},
                        'titlefont': {'color': 'gray'},
                        'gridcolor': 'gray'
                        },
                        yaxis={
                        'tickfont': {'color': 'gray'},
                        'titlefont': {'color': 'gray'},
                        'gridcolor': 'gray'
                        },
                        plot_bgcolor="#111111",
                        paper_bgcolor="black",
                        height=600,
                )

                return fig


# %% Callback of the buying timing chart (vertical chart)

################################################################################
# COMPUTATION OF VERTICAL CHART / OF THE BUYING TIMING CHART
################################################################################
@app.callback(Output(component_id='crypto-graph-vertical', component_property='figure'),
    [Input(component_id='crypto-filter', component_property='value'), 
     Input(component_id='interval-filter', component_property='value'),
     ])
def crypto_chart_vertical(selected_crypto,interval):

    df_volume = df_volume_formated(interval)
    currency = 'EUR'#show_currency(current_user.username)
    usd_eur_rate = usd_value()

    if df_volume.empty or df_volume['qty_bought'].sum() == 0 or selected_crypto == None:
        # Handle the case where df_volume is empty
        # For example, you can display an error message or take other actions
        fig = go.Figure()
        fig.update_layout(
            title={"text": "Volume Chart - No Data ", "font": {"color": "gray"}},
            plot_bgcolor="#111111",
            paper_bgcolor="black",
            height=600,
        )
        return fig
    
    else : 

        symbol = selected_crypto+'USDT' 
        df = load_price_data(interval, symbol)

        # If the crypto symbol is not supported by the Binance API
        if df.empty:
            fig = go.Figure()
            fig.update_layout(
                title={"text": "Price Chart - Data Curretly Unavailable ", "font": {"color": "gray"}},
                plot_bgcolor="#111111",
                paper_bgcolor="black",
                height=600,
            )
            return fig
        else : 

            # Limit historical transaction data to the historical candelstick data
            df_volume = df_volume[df_volume['Date'] >= df['timestamp'].min()]

            if currency == 'EUR':
                df_volume['qty_spent'] = df_volume['qty_spent'] * usd_eur_rate
                df_volume['price'] = df_volume['price'] * usd_eur_rate
                df['open'] = df['open'] * usd_eur_rate
                df['high'] = df['high'] * usd_eur_rate
                df['low'] = df['low'] * usd_eur_rate
                df['close'] = df['close']* usd_eur_rate
                currency_symbol = '€'
            else : 
                currency_symbol = '$'

            # Define a list of x-coordinates for the vertical lines
            buy_dates = df_volume.loc[(df_volume['crypto'] == selected_crypto) & (df_volume['action'] == 'achat'), 'Date'].tolist()
            buy_qty = df_volume.loc[(df_volume['crypto'] == selected_crypto) & (df_volume['action'] == 'achat'), 'qty_bought'].tolist()
            # More data on trace legends
            buy_price = df_volume.loc[(df_volume['crypto'] == selected_crypto) & (df_volume['action'] == 'achat'), 'price'].tolist()
            buy_amount = df_volume.loc[(df_volume['crypto'] == selected_crypto) & (df_volume['action'] == 'achat'), 'qty_spent'].tolist()


            sell_dates = df_volume.loc[(df_volume['crypto'] == selected_crypto) & (df_volume['action'] == 'vente'), 'Date'].tolist()
            sell_qty = df_volume.loc[(df_volume['crypto'] == selected_crypto) & (df_volume['action'] == 'vente'), 'qty_bought'].tolist()
            # More data on trace legends
            sell_price = df_volume.loc[(df_volume['crypto'] == selected_crypto) & (df_volume['action'] == 'vente'), 'price'].tolist()
            sell_amount = df_volume.loc[(df_volume['crypto'] == selected_crypto) & (df_volume['action'] == 'vente'), 'qty_spent'].tolist()

            # Fig creation
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # Add the candlestick chart to the first subplot
            fig.add_trace(go.Candlestick(x=df['timestamp'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'], name="Candelstick",xaxis='x2'),secondary_y=False)

            bar_widths = 2

            # Define annotations for both buy and sell bars
            buy_annotations = [f'Buy<br>Quantity: {qty}<br>Amount: {amount}<br>Price: {price}' for amount, qty, price in zip(buy_amount, buy_qty,buy_price)]
            sell_annotations = [f'Sell<br>Quantity: {qty}<br>Amount: {amount}<br>Price: {price}' for amount, qty, price in zip(sell_amount, sell_qty,sell_price)]

            sky_blue = 'rgba(135, 206, 235, 0.5)'
            # Add the volume bar chart to the second subplot
            fig.add_trace(go.Bar(x=buy_dates, y=buy_qty,marker=dict(color=sky_blue,line=dict(color=sky_blue,width=2)), 
                                 name="Buy", text=buy_annotations,width=bar_widths),secondary_y=True)


            pale_orange = 'rgba(255, 165, 0, 0.5)'
            # Add the volume bar chart to the second subplot
            fig.add_trace(go.Bar(x=sell_dates, y=sell_qty,marker=dict(color=pale_orange,line=dict(color=pale_orange,width=2)), 
                                 name="Sell", text=sell_annotations,width=bar_widths),secondary_y=True)

            # Customize the layout of the figure
            fig.update_layout(
                title={
                    "text": "Volume Chart",
                    "font": {"color": "gray"},   
                },
                legend={
                    'font': {'color': 'gray'}
                },
                xaxis={
                        'tickfont': {'color': 'gray'},
                        'titlefont': {'color': 'gray'},
                        'gridcolor': 'gray'
                },
                yaxis2=dict(
                    title='Volume',
                    tickfont=dict(color='gray'),
                    titlefont=dict(color='gray'),
                    gridcolor='gray'
                ),
                yaxis=dict(
                    title='Price',
                    tickfont=dict(color='gray'),
                    titlefont=dict(color='gray'),
                    gridcolor='gray'
                ),
                plot_bgcolor="#111111",
                paper_bgcolor="black",
                height=600,
                showlegend=False
            )

            fig.update_yaxes(rangemode='tozero')

            # Turn off gridlines for the second y-axis plot
            fig.layout.yaxis2.showgrid=False
            return fig


#  %% crypto price graph layout
avg_crypto_graph = dbc.Container([
    dcc.Graph(
        id='crypto-graph',
    ),
    html.P('Note : If the average acquisition price is 0.00 it highy suggests that all of this crypto has been sold.'),
    ],className='jumbotron')

#  %% crypto graph vertical layout
crypto_graph_vertical = dbc.Container([
    dcc.Graph(
        id='crypto-graph-vertical',
    ),
    html.P('Note : Blue lines highlight a buy, Orange ones a sell.'),
    ],className='jumbotron')


# %% Investment_stats page layout
layout = [dbc.Container([
                        header,
                        html.Div([filter_crypto,
                                filter_interval,
                        ],style = MENU_STYLE),
        ], style={"textAlign": "center"},className='jumbotron'),
        dbc.Container([avg_crypto_graph,
                       crypto_graph_vertical,
                       ])
        ] 