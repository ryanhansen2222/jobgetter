from openai import OpenAI
api_key = None
client = OpenAI(api_key=api_key)


def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

resume = load_file("../resume.txt")
job = load_file("../job.txt")

prompt = f"""
Compare this resume against the job description.

Resume:
{resume}

Job Description:
{job}

Return:
1. Match score (0-100)
2. Strengths
3. Missing skills
4. Suggested resume improvements
"""

response = client.responses.create(
    model="gpt-5",
    input=prompt
)

print(response.output_text)