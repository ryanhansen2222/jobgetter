import gspread
import pandas as pd
from datetime import date
import numpy as np

DATA_PATH = '../data/'

class ApplicationTracker:

    def __init__(self):
        pass
    def load_sheet(self):
        gc = gspread.service_account(filename="../sheets_credentials.json")

        sheet = gc.open("Job Sheet Master").worksheet("analyzed_jobs")

        records = sheet.get_all_records()

        return pd.DataFrame(records)


    def save_remote_changes_locally(self):


        gc = gspread.service_account(filename="../sheets_credentials.json")
        sheet = gc.open("Job Sheet Master").worksheet("Tracking")
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
        df["full_title_id"] = df["company"] + " - " + df["title"]

        df.to_csv(
            f"{DATA_PATH}application_tracking.csv",
            index=False
        )

    def update_application_csv(self):
        existing = None
        try:
            existing = pd.read_csv(f"{DATA_PATH}application_tracking.csv")
        except:
            pass

        df = self.load_sheet()

        applied_df = df[
            df["Applied"]
            .str.lower()
            .eq("yes")
        ].copy()

        today = date.today().isoformat()
        applied_df["full_title_id"] = applied_df["company"] + " - " + applied_df["title"]
        applied_df["applied_date"] = today
        applied_df = applied_df[~applied_df["full_title_id"].isin(existing['full_title_id'])]

        #print(applied_df)
        full_df = pd.concat([existing, applied_df])

        full_df = full_df.drop_duplicates(subset='full_title_id')

        full_df.to_csv(
            f"{DATA_PATH}application_tracking.csv",
            index=False
        )

        print(f"Saved {len(applied_df)} applications")
        #print(full_df)
        return full_df

    def update_sheet(self, df):
        df = df[["company", "title", "match_score", "Applied", "applied_date", "url", "Status", "Follow up"]]
        gc = gspread.service_account(
            filename="../sheets_credentials.json"
        )
        df = df.replace({np.nan: "NAN"})
        df = df.drop_duplicates()


        sheet = gc.open("Job Sheet Master").worksheet("Tracking")
        sheet.clear()

        sheet.update(
            [df.columns.values.tolist()] +
            df.values.tolist()
        )

    def full_run(self):
        self.save_remote_changes_locally()
        full_df = self.update_application_csv()
        self.update_sheet(full_df)



if __name__ == "__main__":
    at = ApplicationTracker()
    at.full_run()