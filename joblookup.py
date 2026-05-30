import pandas as pd

df = pd.read_csv("jobs.csv")
print(df.columns)

print(df[['title','company']])

#for job in df.iterrows():
#    print(job[1])


'''
    print(f"Title: {job['title']}")
    print(f"Company: {job['company']}")
    print(f"Location: {job['location']}")
    print(f'Experience: {job["experience_range"]}')
'''


#print(job['description'])