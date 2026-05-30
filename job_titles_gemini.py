from google import genai
import json
import csv
class JobTitles:


    def __init__(self):
        # Set your API key
        #API_KEY = "YOUR_GEMINI_API_KEY"
        pass


    def load_resume(self):
        # Load resume text
        resume = None
        with open("resume.txt", "r", encoding="utf-8") as f:
            resume = f.read()
            return resume
        return resume

    def get_api_key(self):
        with open("config", "r", encoding="utf-8") as f:
            key = f.read().split('=')[1]
            return key

    def call_gemini(self, resume):
        API_KEY = self.get_api_key()

        client = genai.Client(api_key=API_KEY)

        prompt = f"""
        Analyze the following resume.
        
        Return 5-7 job titles that match the candidate's skills and experience. 
        The job titles need to be simple plaintext and not contain any special characters e.g.
        '(', ')', '/'. The response needs to be 
        ONLY valid JSON in the outlined format. Do not include
        leading text before the curly brace:
        
        {{
          "candidate_summary": "...",
          "recommended_job_titles": [
            {{
              "title": "...",
              "reason": "..."
            }}
          ]
        }}
        
        Resume:
        
        {resume}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response

    def parse_response(self, response):

        text = response.text
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()
        #rint(text)
        result = json.loads(text)
        return result

    def get_titles(self, parsed_response):
        job_titles = []
        for job in parsed_response["recommended_job_titles"]:
            job_titles.append(job['title'])
        return job_titles

    def print_response(self, parsed_response):

        print("\nCandidate Summary:")
        print(parsed_response["candidate_summary"])

        print("\nRecommended Job Titles:")
        job_titles = []
        for job in parsed_response["recommended_job_titles"]:
            print(f"- {job['title']}")
            #print(f"  Reason: {job['reason']}")
            job_titles.append(job['title'])
        return job_titles

    def save_to_csv(self, job_titles: list[str], filename: str = "job_titles.csv"):
        """Saves a list of job titles to a CSV file."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["Job Title"]) # Header row
                for title in job_titles:
                    csv_writer.writerow([title])
            print(f"\nJob titles successfully saved to {filename}")
        except IOError as e:
            print(f"Error saving job titles to CSV: {e}")

    def full_run(self):
        resume = self.load_resume()
        response = self.call_gemini(resume)
        parsed_response = self.parse_response(response)
        titles = self.get_titles(parsed_response)
        # rint(titles)
        self.save_to_csv(titles)

if __name__ == '__main__':
    jt = JobTitles()
    jt.full_run()