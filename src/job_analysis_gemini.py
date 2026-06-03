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
from datetime import date
import traceback
import asyncio

DATA_PATH = '../data/'

# ── Core Analysis ──────────────────────────────────────────────────────────────
class AiAnalysis:
    def __init__(self):
        pass
    def load_data(self):
        today = date.today().isoformat()
        filename = f"{DATA_PATH}full_jobs_cleaned_{today}.csv"
        job_data = pd.read_csv(filename)
        return job_data

    def load_profile(self):
        # Load resume text
        resume = None
        with open("../resume.txt", "r", encoding="utf-8") as f:
            resume = f.read()
            return resume

    def get_api_key(self):
        with open("../config", "r", encoding="utf-8") as f:
            key = f.read().split('=')[1]
            return key

    async def process_row(self, row, profile):
        print("start", row["title"], time.time())
        return await self.call_gemini_async(row["description"], profile)

    async def run_async_analysis(self, df, profile):
        tasks = [self.process_row(r,profile) for r in df.to_dict("records")]
        print(f"Processing {len(tasks)} jobs")
        results_as_list = await asyncio.gather(*tasks)
        results = pd.DataFrame(results_as_list)
        df = pd.concat([df, results], axis=1)
        return df

    def run_analysis(self, df, profile, limit = 50):
        count = 0
        for idx, job in df.iterrows():
            count+=1
            if count%50 == 0:
                print(f"Processed {count} / {limit} jobs")
            description = job['description']
            analysis = self.call_gemini(description, profile)

            try:
                match_score = analysis['match_score']
                missing_skills = ", ".join(analysis['missing_skills'])
                recommendation = analysis['recommendation']

                df.at[idx, "match_score"] = match_score
                df.at[idx, "missing_skills"] = missing_skills
                df.at[idx, "recommendation"] = recommendation
            except:
                df.at[idx, "match_score"] = 0
                df.at[idx, "missing_skills"] = ''
                df.at[idx, "recommendation"] = 1

            try:
                df.at[idx, "YOE"] = analysis['YOE']
            except:
                df.at[idx, "YOE"] = 0

            if count == limit:
                return df.head(limit)
        return df


    async def call_gemini_async(self, description, profile):


        API_KEY = self.get_api_key()

        client = genai.Client(api_key=API_KEY)

        prompt = f"""You are a recruiting assistant. You will receive a job description and a candidate profile.
            Respond with a concise JSON object containing:
            - "match_score": [0-100]
            - "missing_skills": List of 0-5 job requirements listed in the job description that are missing from the candidate profile. Be detail oriented.
            - "recommendation": [1-5] where 5 is the highest recommendation and 1 is the lowest.
            - "YOE": years of experience requirement. If there is a range, respond with the minimum of the range.

            Respond with JSON only. No markdown, no explanation.

            Analyze the following job description and candidate profile:

            Description: {description}

            Profile: {profile}"""

        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text

        try:
            result = json.loads(text)
            print(result)
            return result
        except Exception as e:
            print(e)
            traceback.print_exc()
            return {"match_score": 0, "missing_skills": [], "recommendation": 1, "YOE": 0}

    def call_gemini(self, description, profile):
        API_KEY = self.get_api_key()

        client = genai.Client(api_key=API_KEY)

        prompt = f"""You are a recruiting assistant. You will receive a job description and a candidate profile.
    Respond with a concise JSON object containing:
    - "match_score": [0-100]
    - "missing_skills": List of 0-5 job requirements listed in the job description that are missing from the candidate profile. Be detail oriented.
    - "recommendation": [1-5] where 5 is the highest recommendation and 1 is the lowest.
    - "YOE": years of experience requirement. If there is a range, respond with the minimum of the range.
    
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
        except Exception as e:
            print(e)
            traceback.print_exc()
            return {"match_score": 0, "missing_skills": [], "recommendation": 1, "YOE": 0}



    def full_run(self):
        profile = self.load_profile()
        df = self.load_data()
        analyzed_df = asyncio.run(self.run_async_analysis(df.head(100), profile))
        today = date.today().isoformat()
        filename = f"{DATA_PATH}analyzed_jobs_{today}.csv"
        analyzed_df.to_csv(filename, index=False, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\")






if __name__ == "__main__":
    analysis = AiAnalysis()
    analysis.full_run()
