import pandas as pd

import urllib.request, json

from load_google_drive import import_data

def data():
    df  = import_data()
    df = data_formating(df.copy())
    return df

# %% USD and EUR value extraction for conversion
def usd_value():

    url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=USD&tsyms=EUR"
    response = urllib.request.urlopen(url)
    USD_value = json.loads(response.read())

    return USD_value['USD']['EUR']

# %% Formating the data 
# Acording to the right currency and the right variable type
def data_formating(df):
    
    # Convert valiables into string to replace ',' by '.'
    df['fee'] = df['fee'].astype(str)
    df['qty_bought'] = df['qty_bought'].astype(str)
    df['qty_spent'] = df['qty_spent'].astype(str)
    df['price'] = df['price'].astype(str)
    
    # Replace ',' by '.'
    df['fee'] = [element.replace(',', '.') for element in df['fee']]
    df['qty_bought'] = [element.replace(',', '.') for element in df['qty_bought']]
    df['qty_spent'] = [element.replace(',', '.') for element in df['qty_spent']]
    df['price'] = [element.replace(',', '.') for element in df['price']]
    
    # Convert variables back to float
    df['fee'] = pd.to_numeric(df['fee'], errors='coerce') # some variables of this column are empty so they are not converted
    df['qty_bought'] = df['qty_bought'].astype(float)
    df['qty_spent'] = df['qty_spent'].astype(float)
    df['price'] = df['price'].astype(float)
    
    # Convert date variable into date type
    #df['Date'] = pd.to_datetime(df['Date'], format = '%Y-%m-%d').dt.strftime('%d/%m/%Y')
    #df.loc[:, 'Date'] = pd.to_datetime(df['date'], format='%Y-%m-%d').dt.strftime('%d/%m/%Y')

    # Convert USD amounts into EUR amounts
    USD_value = usd_value()
    
    df.loc[df['fiat'] == 'EUR', 'qty_spent'] = df.loc[df['fiat']=='EUR','qty_spent'] / USD_value
    df.loc[df['fiat'] == 'EUR', 'price'] = df.loc[df['fiat']=='EUR','price'] / USD_value

    df.loc[df['fiat'] == 'EUR', 'fiat'] ='USD'

    return df

# %% Returns the summary of the actual portfolio [0] as well as the summary of the realised P&L [1]
###
def actual_summary(df):

    #summary dicionnary creation
    summary = {}#{'BTC': [0,0,0]}
    realised_pl = {}#{'BTC' : 0}

    # We go through the dataframe df with all the transactions
    for index in range(len(df)):
        #Select the transaction associated to the index
        trx = df.iloc[index]

        # If the crypto is not already registered in the summary
        if trx['crypto'] not in summary.keys() :#and trx['action'] == 'achat':
            #we add it to the summary
            summary[trx['crypto']] = [trx['qty_bought'],trx['price'],trx['qty_spent']]
            realised_pl[trx['crypto']] = 0
        # Elsewise
        else : 
            # We extract all the informations of the crypto already in the summary
            qty, price, amount = summary[trx['crypto']]

            #If the transaction is a buy
            if trx['action'] == 'achat':

                #Computation of the new average buying price
                price = (price*qty + trx['price']*trx['qty_bought'])/(qty+trx['qty_bought'])
                #Computation of the new quantity of the crypto in the wallet
                qty = qty + trx['qty_bought']
                #Computation of the total amount invested
                amount = amount + trx['qty_spent']

                #New values are added to the summary
                summary[trx['crypto']] = [qty,price,round(amount,2)]    

            #If the transaction is a sell
            elif trx['action'] == 'vente' :#and trx['qty_bought'] <= qty:
                

                #Extraction of the already realised profites and losses
                profit_loss = realised_pl[trx['crypto']]

                #Add to it the profil/loss of the sell transaction
                profit_loss += (trx['price']- price)*trx['qty_bought']

                 #Computation of the new quantity of the crypto in the wallet
                qty = qty - trx['qty_bought'] 

                amount = qty * price

                #New values are added to the summary and the realised_pl dataframe
                realised_pl[trx['crypto']] = round(profit_loss,2)
                summary[trx['crypto']] = [qty,price,round(amount,2)]

    # Drop lines with no asset or no walue
    summary = {
    asset: values
    for asset, values in summary.items()
    if not (float(values[2]) < 0.01 or float(values[0]) <= 0)
    }

    #Convert the dictionnaries into dataframes
    summary = pd.DataFrame.from_dict(summary, orient ='index', columns=['Amount','Price','Value']) 
    realised_pl = pd.DataFrame.from_dict(realised_pl, orient ='index', columns=['P&L']) 

    #Delet all the elements with a NaN amount invested
    #This means they are not in the wallet anymore
    index_with_nan = summary.index[summary.isnull().any(axis=1)]
    summary.drop(labels = index_with_nan,axis = 0, inplace=True)

    summary['crypto'] = summary.index
    realised_pl['crypto'] = realised_pl.index

    # Returns, [0] : The summary of the actual portfolio, [1] : The summary of the realised P&L
    return summary, realised_pl


# %% Drop elements with no realise P&L 
# Returns the final P&L data
def final_pl(df):
    df = df.sort_values('P&L',ascending=False)
    index_with_nan = df.index[df['P&L'] == 0]
    df.drop(labels = index_with_nan,axis = 0, inplace=True)
    return df


# %% Extraction from transaction data, the symbole of each traded crypto
def unique_traded_crypto():
    distinct_crypto = data()['crypto'].unique()
    # Returns the list of traded crypto
    return  distinct_crypto


#%%  Crypto market price extraction
def market_price():
    crypto_symbols = unique_traded_crypto()
    crypto_symbols = [symbol for symbol in crypto_symbols if symbol not in ['BULL', 'ETHBULL']] # Specific to me

    
    # Creation of the crypto symbol string to implement into the API url
    crypto_string = ''
    i = 1
    for asset in crypto_symbols:
        crypto_string+=asset
        if i < len(crypto_symbols):
            crypto_string+=','
        i+=1

    # Extraction of crypto market values via API
    url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms="+crypto_string+"&tsyms=USD,EUR&api_key={91b714f904430f669a18cd914ee8e84c7fc1c4a4529517df029c41c2929b5f12}"
    response = urllib.request.urlopen(url)
    crypto_values = json.loads(response.read())

    # Insert BULL values into basic crypto market data
    #crypto_values.update(bull_data(df))

    market = crypto_values
    market_summary = {}

    # Get the EUR price of each crypto
    for asset in crypto_symbols:
            market_summary[asset] = [market[asset]['EUR'],market[asset]['USD']]

    market_summary = pd.DataFrame.from_dict(market_summary, orient ='index', columns=['EUR','USD']) 

    return market_summary   

# %% Output table for my_wallet page
def final_table(df):
    summary = {}#{'BTC' : [0,0,0,0]}
    columns = ['Name','Amount','Market Price','Value']

    market = market_price()

    # Insert the needed values to the summary table
    for asset in df['crypto']: 
        summary[asset] = [asset,round(df.loc[asset]['Amount'],4),round(market.loc[asset]['USD'],2),df.loc[asset]['Value']]

    # Formating the values for the layout
    # Creation of the "P&L" and "P&L %"" elements
    summary = pd.DataFrame.from_dict(summary, orient ='index', columns=columns) 
    summary['P&L'] = round((summary['Market Price']-df['Price'])*summary['Amount'],2)
    summary['P&L %'] = round(summary['P&L']/summary['Value'],4)
    summary['Value'] = summary['Value'] + summary['P&L']
    
    summary['Wallet %'] = round(summary['Value'] / summary['Value'].sum(),4)

    # Sort values according to importance in the portfolio
    summary = summary.sort_values('Value',ascending=False)

    # Return the wallet summary table
    return summary

# %% Total value, P&L and P&L % of the portfolio 
def total_table(df):

    initial_value = round((df)['Value'].sum(),2) - round((df)['P&L'].sum(),2)

    # Computes the P&L % of the portfolio
    pl_pourcentage = round((df)['P&L'].sum(),2) / initial_value * 100

    # Returns a list [Value of portfolio, P&L, P&L %]
    total = [round((df)['Value'].sum(),2), 
             round((df)['P&L'].sum(),2),
             round(pl_pourcentage,2)]

    return total


# %% Main
if __name__ == '__main__':
    df = data()
    print(df)

    dfSummary = actual_summary(df)[0]
    print(dfSummary)

    dffinal = final_table(dfSummary)
    print(dffinal)

    dttotal = total_table(dffinal)
    print(dttotal)
