import csv
from jobspy import scrape_jobs
import pandas as pd
import requests
from bs4 import BeautifulSoup


class JobScrape:

    def __init__(self):
        pass

    def get_titles(self):
        titles = pd.read_csv("job_titles.csv")
        #print(titles)
        return titles["Job Title"].tolist()

    def get_names(self):
        names = pd.read_csv("company_names.csv")
        #print(names)

        return names["Company Name"].tolist()

    def clean_html(self, text):
        if not text:
            return ""
        return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)

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

    def linkedin_wrapper(self):
        titles = self.get_titles()

        linkedin_jobs = self.scrape_linkedin(titles[0])

        for title in titles[1:]:
            linkedin_jobs = pd.concat([linkedin_jobs,self.scrape_linkedin(title)])
        return linkedin_jobs
    def indeed_wrapper(self):
        titles = self.get_titles()

        indeed_jobs = self.scrape_indeed(titles[0])

        for title in titles[1:]:
            indeed_jobs = pd.concat([indeed_jobs,self.scrape_indeed(title)])
        return indeed_jobs

    def scrape_indeed(self, title):

        jobs = scrape_jobs(
            site_name=["indeed"],  # "glass
            search_term=title,
            location=None,
            results_wanted=1000
        )

        #print(jobs[['title', 'company', 'location', 'date_posted', 'description']])
        #print(jobs["company"].nunique())

        return jobs


    def scrape_greenhouse(self):

        company_names = self.get_names()
        print(company_names)
        job_titles = self.get_titles()
        jobs = []

        for idx, company in enumerate(company_names):
            #print(idx, company)
            url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"

            try:
                response = requests.get(url, timeout=20)

                if response.status_code != 200:
                    #print('Error finding on greenhouse.io')
                    continue

                data = response.json()

                for job in data["jobs"]:
                    title = job["title"]
                    #print(title)

                    for SEARCH_TERM in job_titles:


                        if SEARCH_TERM.lower() not in title.lower():
                            #print(f'Not found {SEARCH_TERM} in {title}')
                            continue

                        jobs.append({
                            "source": "greenhouse",
                            "company": company,
                            "title": title,
                            "location": job.get("location", {}).get("name", ""),
                            "description": self.clean_html(job.get("content", "")),
                            "url": job.get("absolute_url", "")
                        })

            except Exception as e:
                print(f"Greenhouse error {company}: {e}")
        companies = [x["company"] for x in jobs]
        print(set(companies))
        return pd.DataFrame(jobs)

    def scrape_lever(self):

        company_names = self.get_names()
        #print(company_names)
        job_titles = self.get_titles()
        jobs = []
        for idx, company in enumerate(company_names):
            url = f"https://api.lever.co/v0/postings/{company.lower()}?mode=json"

            try:
                response = requests.get(url, timeout=20)

                if response.status_code != 200:
                    print(f'{idx} Not on lever: {response}')
                    continue

                postings = response.json()

                for job in postings:

                    title = job["text"]
                    # print(title)

                    for SEARCH_TERM in job_titles:

                        if SEARCH_TERM.lower() not in title.lower():
                            # print(f'Not found {SEARCH_TERM} in {title}')
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
                            "description": self.clean_html(description),
                            "url": job.get("hostedUrl", "")
                        })

            except Exception as e:
                print(f"Lever error {company}: {e}")
        return pd.DataFrame(jobs)

    def full_scrape(self):
        lever = self.scrape_lever()
        greenhouse = self.scrape_greenhouse()



        indeed = self.indeed_wrapper()
        linkedin = self.linkedin_wrapper()

        full_df = pd.concat([lever, greenhouse, indeed, linkedin], ignore_index=True)

        full_df.to_csv("full_job_data", index=False, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\")
        print(f"Successfully saved {len(full_df)} jobs to csv")



if __name__ == '__main__':
    js = JobScrape()
    js.full_scrape()
