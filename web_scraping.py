import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://angel.co/companies"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

startups = []

for company_div in soup.find_all("div", class_="startup-card"):
    name = company_div.find("h3").text.strip() if company_div.find("h3") else None
    location = company_div.find("div", class_="location").text.strip() if company_div.find("div", class_="location") else None
    website = company_div.find("a", class_="website-link")["href"] if company_div.find("a", class_="website-link") else None

    startups.append({
        "Name": name,
        "Location": location,
        "Website": website
    })

df = pd.DataFrame(startups)
df.to_csv("angel_list_startups.csv", index=False)
print("Saved AngelList startups to angel_list_startups.csv")
