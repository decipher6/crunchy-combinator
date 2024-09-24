from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import csv
import requests
import time
import json
from datetime import datetime
from hidethis import CB_API_KEY

API_KEY = CB_API_KEY
BASE_URL = 'https://api.crunchbase.com/v4/data/entities/organizations'

driver = webdriver.Chrome()

driver.get('https://www.ycombinator.com/companies')

def get_crunchbase_data(company_permalink):
    url = f"{BASE_URL}/{company_permalink}"
    params = {
        'user_key': API_KEY,
        'field_ids': 'created_at,entity_def_id,facebook,image_url,linkedin,short_description,stock_exchange_symbol,twitter,updated_at,website_url'
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print(f"Rate limit exceeded for {company_permalink}. Waiting before retrying...")
        time.sleep(61)
        return get_crunchbase_data(company_permalink)
    else:
        print(f"Error fetching data for {company_permalink}: {response.status_code}")
        return None

def process_crunchbase_data(data):
    if not data or 'properties' not in data:
        return None

    properties = data['properties']
    processed_data = {
        'cb_created_at': properties.get('created_at'),
        'cb_entity_def_id': properties.get('entity_def_id'),
        'cb_facebook': properties.get('facebook', {}).get('value'),
        'cb_image_url': properties.get('image_url'),
        'cb_linkedin': properties.get('linkedin', {}).get('value'),
        'cb_short_description': properties.get('short_description'),
        'cb_stock_exchange_symbol': properties.get('stock_exchange_symbol'),
        'cb_twitter': properties.get('twitter', {}).get('value'),
        'cb_updated_at': properties.get('updated_at'),
        'cb_website_url': properties.get('website_url')
    }
    return processed_data

def enrich_dataset(input_file, output_file):
    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)
        original_fieldnames = reader.fieldnames
        cb_fieldnames = [
            'cb_created_at', 'cb_entity_def_id', 'cb_facebook', 'cb_image_url', 'cb_linkedin',
            'cb_short_description', 'cb_stock_exchange_symbol',
            'cb_twitter', 'cb_updated_at', 'cb_website_url'
        ]
        all_fieldnames = original_fieldnames + cb_fieldnames

        enriched_data = []
        for row in reader:
            company_permalink = row['Name'].lower()
            print(f"Processing: {company_permalink}")

            cb_data = get_crunchbase_data(company_permalink)
            processed_data = process_crunchbase_data(cb_data)

            if processed_data:
                row.update(processed_data)
            else:
                print(f"No data found for {company_permalink}")
                for field in cb_fieldnames:
                    row[field] = ''

            enriched_data.append(row)
            time.sleep(0.2)  # Delay to respect rate limits

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=all_fieldnames)
        writer.writeheader()
        writer.writerows(enriched_data)

# scrape data from a single company element
def scrape_company(company_element):
    name = company_element.find('span', class_='_coName_86jzd_453').text.strip()
    location = company_element.find('span', class_='_coLocation_86jzd_469').text.strip()
    description = company_element.find('span', class_='_coDescription_86jzd_478').text.strip()
    
    cohort_element = company_element.find('a', href=lambda x: x and 'batch' in x)
    cohort = cohort_element.text.strip() if cohort_element else ''
    
    tags = [tag.text.strip() for tag in company_element.find_all('span', class_='pill _pill_86jzd_33') 
            if tag.text.strip() != cohort]
    
    # Check for B2B tag and remove it from tags if present
    b2b = False
    if 'B2B' in tags:
        b2b = True
        tags.remove('B2B')  # Remove B2B tag

    return {
        'Name': name,
        'Location': location,
        'Description': description,
        'Cohort': cohort,
        'Tags': ', '.join(tags),
        'b2b': b2b  # Add the boolean field here
    }

# all company data
all_companies = []

# Scroll and scrape
while True:
    # wait to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, '_company_86jzd_338')))
    
    # parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # all company elements
    company_elements = soup.find_all('a', class_='_company_86jzd_338')
    
    # scrape data from each company element
    for company_element in company_elements:
        company_data = scrape_company(company_element)
        if company_data not in all_companies:
            all_companies.append(company_data)
    
    # how much to be scraped |--> MODIFIABLE <--|, but minimum is 40 companies
    if len(all_companies) >= 20:
        break
    
    # scroll down to load more companies
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # wait for new content to load

# quit browser
driver.quit()

# create df and save to csv
df = pd.DataFrame(all_companies)
df.to_csv('startup_data.csv', index=False)

print(f"Scraped data for {len(all_companies)} companies and saved to startup_data.csv")

input_file = 'startup_data.csv'
output_file = 'startup_data_enriched.csv'
enrich_dataset(input_file, output_file)
print("Enrichment complete. Check the output file.")