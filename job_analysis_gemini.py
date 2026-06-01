#!/usr/bin/env python3

from google import genai
import pandas as pd
import json
import csv
import time
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime


# ── Core Analysis ──────────────────────────────────────────────────────────────
class AiAnalysis:
    def __init__(self):
        pass
    def load_data(self):
        job_data = pd.read_csv("full_jobs_cleaned.csv")
        return job_data

    def load_profile(self):
        # Load resume text
        resume = None
        with open("resume.txt", "r", encoding="utf-8") as f:
            resume = f.read()
            return resume

    def get_api_key(self):
        with open("config", "r", encoding="utf-8") as f:
            key = f.read().split('=')[1]
            return key

    def run_analysis(self, df, profile, limit = 500):
        count = 0
        for idx, job in df.iterrows():
            count+=1
            if count%50 == 0:
                print(f"Processed {count} / {limit} jobs")
            description = job['description']
            analysis = self.call_gemini(description, profile)
            match_score = analysis['match_score']
            missing_skills = ", ".join(analysis['missing_skills'])
            recommendation = analysis['recommendation']

            df.at[idx, "match_score"] = match_score
            df.at[idx, "missing_skills"] = missing_skills
            df.at[idx, "recommendation"] = recommendation


            if count == limit:
                break
        return df.head(limit)



    def call_gemini(self, description, profile):
        API_KEY = self.get_api_key()

        client = genai.Client(api_key=API_KEY)

        prompt = f"""You are a recruiting assistant. You will receive a job description and a candidate profile.
    Respond with a concise JSON object containing:
    - "match_score": [0-100]
    - "missing_skills": List of 0-5 job skills listed in the job description that are missing from the candidate profile
    - "recommendation": [1-5] where 5 is the highest recommendation and 1 is the lowest.
    
    Respond with JSON only. No markdown, no explanation.
    
    Analyze the following job description and candidate profile:
    
    Description: {description}
    
    Profile: {profile}"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text

        try:
            result = json.loads(text)
            print(result)
            return result
        except:
            return {"match_score": 0, "missing_skills": [], "recommendation": 1}



    def full_run(self):
        profile = self.load_profile()
        df = self.load_data()
        analyzed_df = self.run_analysis(df, profile)
        analyzed_df.to_csv("analyzed_jobs.csv", index=False, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\")






if __name__ == "__main__":
    analysis = AiAnalysis()
    analysis.full_run()
