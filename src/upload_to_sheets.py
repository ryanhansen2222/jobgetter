import gspread
from datetime import date
import pandas as pd
import numpy as np

DATA_PATH = '../data/'

class SheetsManager:

    def __init__(self):
        pass

    def load_df(self):
        today = date.today().isoformat()
        filename = f"{DATA_PATH}analyzed_jobs_{today}.csv"
        df = pd.read_csv(filename)
        return df
    def full_run(self):
        df = self.load_df()
        self.update_sheet(df)


    def update_sheet(self, df):
        df = df.replace({np.nan: "NAN"})

        gc = gspread.service_account(
            filename="../sheets_credentials.json"
        )

        sheet = gc.open("Job Sheet Master").sheet1
        sheet.clear()

        sheet.update(
            [df.columns.values.tolist()] +
            df.values.tolist()
        )

if __name__ == '__main__':
    sm = SheetsManager()
    sm.full_run()