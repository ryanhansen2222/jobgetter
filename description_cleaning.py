import pandas as pd
import csv

class DescriptionCleaning:

    def __init__(self):
        pass

    def load_data(self):
        job_data = pd.read_csv("full_job_data")
        return job_data

    def clean_df(self, job_data):
        job_data["description"] = job_data["description"].apply(self.extract_requirements)
        return job_data

    def extract_requirements(self, full_description):
        KEEP_HEADERS = [
            "Responsibilit",
            "Requirement",
            "Qualification",
            "Preferred",
            "What You'll",
            "Required Skills",
            "Must-have",
            "must have",
            "About you"
        ]
        text_lower = full_description.lower()

        cutoff = len(full_description)
        start_idx = 0

        for header in KEEP_HEADERS:
            lowercase_header = header.lower()
            pos = text_lower.find(lowercase_header)
            if pos != -1:
                if start_idx == 0:
                    start_idx = pos
                cutoff = pos + 2500#allocate 2500 characters for the requirements sections

                cutoff = min(cutoff, len(full_description))

        return full_description[start_idx:cutoff].strip()

    def save_to_csv(self, full_df, filename: str = "full_jobs_cleaned.csv"):
        """Saves a list of job titles to a CSV file."""
        try:
            full_df.to_csv(filename, index=False, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\")

            print(f"\nSaved cleaned data to {filename}")
        except IOError as e:
            print(f"Error saving cleaned data to CSV: {e}")

    def full_run(self):
        d = self.load_data()
        c = self.clean_df(d)
        self.save_to_csv(c)


if __name__ == '__main__':
    dc = DescriptionCleaning()
    dc.full_run()