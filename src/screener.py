from company_names_gemini import CompanyNames
from description_cleaning import DescriptionCleaning
from job_analysis_gemini import AiAnalysis
from jobscraper import JobScrape
from job_titles_gemini import JobTitles
from upload_to_sheets import SheetsManager
import time

DATA_PATH = '../data/'

if __name__ == '__main__':
    print('Running Job Agent for user profile...')
    time.sleep(1)

    print('Getting good job titles for profile...')
    jt = JobTitles()
    jt.full_run()
    print('Job title analysis complete')
    time.sleep(1)

    print('Finding good companies to work for...')
    cn = CompanyNames()
    cn.full_run()
    print('Company analysis complete')

    time.sleep(1)
    print('Finding Candidate Job matches using Companies and Job Titles...')
    js = JobScrape()
    js.full_scrape()
    print('Job listings found.')

    time.sleep(1)
    print('Filtering out mismatched listings...')
    dc = DescriptionCleaning()
    dc.full_run()
    print('Filter complete')
    time.sleep(1)


    print('Performing in depth grading for remaining listings')
    ai = AiAnalysis()
    ai.full_run()
    print('Deep grading complete')


    time.sleep(1)

    print('Loading results to google sheets')
    sm = SheetsManager()
    sm.full_run()
    print('Results Loaded')

    time.sleep(1)
    print('\n\n')
    print('********** Done **********')

