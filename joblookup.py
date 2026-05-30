import pandas as pd

df = pd.read_csv("jobs.csv")
print(df.columns)

job_num = int(input("Job number: "))

job = df.iloc[job_num]

print(f"Title: {job['title']}")
print(f"Company: {job['company']}")
print(f"Location: {job['location']}")
print(f'Experience: {job["experience_range"]}')
#print(job['description'])