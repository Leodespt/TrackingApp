import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def import_data():      

    # Connect to Google Sheets
    scope = ['https://www.googleapis.com/auth/spreadsheets',#Enable Google Sheet API
            "https://www.googleapis.com/auth/drive"] #Enable Google Drive API


    #Cretentials
    credentials = ServiceAccountCredentials.from_json_keyfile_name("gs_credentials.json", scope)
    client = gspread.authorize(credentials)

    # Open the spreadsheet
    spreadsheet = client.spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1abr3MTAxaynCIeiDPEN-WzYt0ht6IeUWvHThTr4CxnI/edit#gid=0')

    wks = spreadsheet.worksheet('Transactions')

    data = wks.get_all_values()
    headers = data.pop(0)

    dataframe = pd.DataFrame(data, columns=headers)

    return dataframe