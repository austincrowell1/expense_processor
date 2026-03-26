import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

class gsheets_client:
    def __init__(self,google_creds, sheets_scope):
        creds = ServiceAccountCredentials.from_json_keyfile_name(google_creds, sheets_scope)
        self.client = gspread.authorize(creds)

    def refresh_data(self, df, sheet_name):
        try:
            spreadsheet = self.client.open(sheet_name)
            sheet = spreadsheet.get_worksheet(0)
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"could not find spreadsheet {sheet_name}")
            return

        # google sheets doesn't like dataframe nulls/none/nan or many non-string datatypes
        df = df.fillna("")
        df = df.astype(str)

        # convert df to a list of lists (aka rows) to upload to google sheets
        data = [df.columns.values.tolist()] + df.values.tolist()

        # clear out old data from sheet and add new data
        sheet.clear()
        sheet.update(data)
