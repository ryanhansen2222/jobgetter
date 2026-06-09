import pandas as pd
import csv
from datetime import date
DATA_PATH = '../data/'

class DescriptionCleaning:

    def __init__(self):
        pass

    def load_data(self):
        today = date.today().isoformat()
        filename = f"{DATA_PATH}full_job_data_{today}.csv"
        job_data = pd.read_csv(filename)
        print(f'Loaded {len(job_data)} jobs')
        return job_data

    def clean_df(self, job_data):
        job_data["description"] = job_data["description"].apply(self.extract_requirements)
        ooc = self.drop_out_of_country(job_data)
        filtered = self.drop_senior_roles(ooc)
        no_applied = self.remove_applied(filtered)
        no_dupes = self.drop_duplicates(no_applied)
        return no_dupes

    def drop_out_of_country(self, df):
        df["location"] = df["location"].apply(self.check_out_of_country)
        df = df[df['location'] != 'outside of US'].copy()
        return df

    def drop_senior_roles(self, df):
        df["title"] = df["title"].apply(self.check_senior_role)
        df = df[df['title'] != 'drop'].copy()
        return df

    def remove_applied(self, df):
        applied_df = pd.read_csv(f"{DATA_PATH}application_tracking.csv")
        today = date.today().isoformat()
        df["full_title_id"] = df["company"] + " - " + df["title"]
        df = df[~df["full_title_id"].isin(applied_df["full_title_id"])]
        return df

    def drop_duplicates(self, df):
        df = df.drop_duplicates(subset='full_title_id')
        return df

    def check_senior_role(self, role_title_string):
        REMOVE_HEADERS = [
            "Staff",
            "Principal",
            "Manage",
            "director"
        ]
        try:
            for keyword in REMOVE_HEADERS:
                if keyword.lower() in role_title_string.lower():
                    return 'drop'

            return role_title_string
        except:
            return role_title_string
    def check_out_of_country(self, location_string):
        KEEP_HEADERS = [
            "US",
            "USA",
            "United States",
            "U.S.",
        ]
        STATE_ABBREVIATIONS = [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ]
        try:
            for state in STATE_ABBREVIATIONS:
                if state in location_string:
                    return location_string

            text_lower = location_string.lower()
            for header in KEEP_HEADERS:
                if header.lower() in text_lower:
                    return location_string

            return 'outside of US'
        except:
            return 'US'


    def extract_requirements(self, full_description):
        KEEP_HEADERS = [
            "Responsibilit",
            "Require",
            "Qualification",
            "Preferred",
            "What You",
            "Required Skills",
            "Must-have",
            "must have",
            "About you",
            "experience"
        ]
        text_lower = full_description.lower()

        cutoff = []
        start_idx = []

        for header in KEEP_HEADERS:
            lowercase_header = header.lower()
            pos = text_lower.find(lowercase_header)
            if pos != -1:
                start_idx.append(pos)
                cutoff.append(pos + 2500)

        first_idx = 0
        if len(start_idx) > 0:
            first_idx = min(start_idx)
        last_idx = len(full_description)
        if len(cutoff) > 0:
            last_idx = max(cutoff)
        last_idx = min(len(full_description), last_idx)

        return full_description[first_idx:last_idx].strip()

    def save_to_csv(self, full_df, filename: str = "full_jobs_cleaned.csv"):
        """Saves a list of job titles to a CSV file."""
        try:
            today = date.today().isoformat()
            filename = f"{DATA_PATH}full_jobs_cleaned_{today}.csv"
            full_df.to_csv(filename, index=False, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\")

            print(f"\nSaved {len(full_df)} cleaned jobs to {filename}")
        except IOError as e:
            print(f"Error saving cleaned data to CSV: {e}")

    def full_run(self):
        d = self.load_data()
        c = self.clean_df(d)
        self.save_to_csv(c)


if __name__ == '__main__':
    dc = DescriptionCleaning()
    dc.full_run()