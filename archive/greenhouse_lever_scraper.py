import requests
import pandas as pd
from bs4 import BeautifulSoup

SEARCH_TERM = input("Job title: ").lower()

GREENHOUSE_COMPANIES = [
    "openai",
    "databricks",
    "anduril",
    "scaleai"
]

LEVER_COMPANIES = [
    "netlify",
    "figma",
    "robinhood"
]

jobs = []


def clean_html(text):
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)


def fetch_greenhouse(company):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"

    try:
        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            return

        data = response.json()

        for job in data["jobs"]:

            title = job["title"]

            if SEARCH_TERM not in title.lower():
                continue

            jobs.append({
                "source": "greenhouse",
                "company": company,
                "title": title,
                "location": job.get("location", {}).get("name", ""),
                "description": clean_html(job.get("content", "")),
                "url": job.get("absolute_url", "")
            })

    except Exception as e:
        print(f"Greenhouse error {company}: {e}")


def fetch_lever(company):
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"

    try:
        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            return

        postings = response.json()

        for job in postings:

            title = job["text"]

            if SEARCH_TERM not in title.lower():
                continue

            description = ""

            for field in [
                "description",
                "descriptionPlain",
                "lists"
            ]:
                if field in job:
                    description += str(job[field])

            jobs.append({
                "source": "lever",
                "company": company,
                "title": title,
                "location": job.get("categories", {}).get("location", ""),
                "description": clean_html(description),
                "url": job.get("hostedUrl", "")
            })

    except Exception as e:
        print(f"Lever error {company}: {e}")


print("Collecting Greenhouse jobs...")

for company in GREENHOUSE_COMPANIES:
    fetch_greenhouse(company)

print("Collecting Lever jobs...")

for company in LEVER_COMPANIES:
    fetch_lever(company)

df = pd.DataFrame(jobs)

filename = f"{SEARCH_TERM.replace(' ', '_')}_jobs.csv"

df.to_csv(filename, index=False)

print(f"Saved {len(df)} jobs to {filename}")