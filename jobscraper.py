import csv
from jobspy import scrape_jobs
import pandas as pd


class JobScrape:

    def __init__(self):
        pass

    def get_titles(self):
        titles = pd.read_csv("job_titles.csv")
        print(titles)
        return titles

    def scrape_linkedin(self, title, location="USA"):
        """
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "google"],  # "glassdoor", "bayt", "naukri", "bdjobs"
            search_term="AI Engineer",
            google_search_term="AI Engineer jobs near New York City, NY since yesterday",
            location="New York City, NY",
            results_wanted=20,
            hours_old=72,
            country_indeed='USA',

            # linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
            # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
        )"""

        jobs = scrape_jobs(
            site_name=["linkedin"],  # "glass
            search_term=title,
            location=None,
            linkedin_fetch_description=True,
            results_wanted=100
        )
        print(f"Found {len(jobs)} jobs")
        #print(jobs.columns)
        print(jobs[['title','company','location', 'date_posted', 'description']])
        return jobs
        #jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)  # to_excel

    def scrape_indeed(self,title):
        jobs = scrape_jobs(
            site_name=["indeed"],  # "glass
            search_term=title,
            location=None,
            results_wanted=1000
        )

        print(jobs[['title', 'company', 'location', 'date_posted', 'description']])
        print(jobs["company"].nunique())

        return jobs


    def scrape_glassdoor(self):
        pass

    def scrape_lever(self):
        pass



if __name__ == '__main__':
    js = JobScrape()
    job_titles = js.get_titles()

    title1 = job_titles.iloc[0]['Job Title']
    print(title1)
    js.scrape_google(title1)
