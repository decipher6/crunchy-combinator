from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import csv
import requests
import json
from datetime import datetime
from hidethis import CB_API_KEY

# Crunchbase API key
API_KEY = CB_API_KEY
BASE_URL = 'https://api.crunchbase.com/v4/data/entities/organizations'

driver = webdriver.Chrome()

driver.get('https://www.ycombinator.com/companies')

# function to get data from crunchbase API
def get_crunchbase_data(company_permalink):
    url = f"{BASE_URL}/{company_permalink}"
    # Add API key to params
    params = {
        'user_key': API_KEY,
        'field_ids': 'created_at,entity_def_id,facebook,image_url,linkedin,short_description,stock_exchange_symbol,twitter,updated_at,website_url'
    }

    # Make API request
    response = requests.get(url, params=params)
    
    # Check if request was successful
    if response.status_code == 200:
        return response.json()
    # Handle rate limit exceeded
    elif response.status_code == 429:
        print(f"Rate limit exceeded for {company_permalink}. Waiting before retrying...")
        time.sleep(61)
        return get_crunchbase_data(company_permalink)
    # Handle other errors
    else:
        print(f"Error fetching data for {company_permalink}: {response.status_code}")
        return None

# function to clean date
def clean_date(date_string):
    """Convert date from '2008-07-31T11:41:35Z' to 'YYYY-MM-DD'."""
    if date_string and date_string != 'NA':
        try:
            parsed_date = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            return 'NA'
    return 'NA'

# function to process crunchbase data
def process_crunchbase_data(data):
    if not data or 'properties' not in data:
        return {
            'cb_created_at': 'NA',
            'cb_entity_def_id': 'NA',
            'cb_facebook': 'NA',
            'cb_image_url': 'NA',
            'cb_linkedin': 'NA',
            'cb_short_description': 'NA',
            'cb_stock_exchange_symbol': 'NA',
            'cb_twitter': 'NA',
            'cb_updated_at': 'NA',
            'cb_website_url': 'NA'
        }

    properties = data['properties']
    processed_data = {
        'cb_created_at': clean_date(properties.get('created_at', 'NA')),
        'cb_entity_def_id': properties.get('entity_def_id', -1),
        'cb_facebook': properties.get('facebook', {}).get('value', 'NA'),
        'cb_image_url': properties.get('image_url', 'NA'),
        'cb_linkedin': properties.get('linkedin', {}).get('value', 'NA'),
        'cb_short_description': properties.get('short_description', 'NA'),
        'cb_stock_exchange_symbol': properties.get('stock_exchange_symbol', 'NA'),
        'cb_twitter': properties.get('twitter', {}).get('value', 'NA'),
        'cb_updated_at': clean_date(properties.get('updated_at', 'NA')),
        'cb_website_url': properties.get('website_url', 'NA')
    }
    return processed_data

# function to enrich existing data
def enrich_dataset(input_file, output_file):
    with open(input_file, 'r') as infile:
        # Read the CSV file into a list of dictionaries
        reader = csv.DictReader(infile)
        original_fieldnames = reader.fieldnames
        cb_fieldnames = [
            'cb_created_at', 
            'cb_entity_def_id', 
            'cb_facebook', 
            'cb_image_url', 
            'cb_linkedin',
            'cb_short_description', 
            'cb_stock_exchange_symbol',
            'cb_twitter', 
            'cb_updated_at', 
            'cb_website_url'
        ]
        # Add the new fieldnames to the original fieldnames
        all_fieldnames = original_fieldnames + cb_fieldnames

        # Write the enriched data to a new CSV file
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
                # Set the rest of the fields to "NA" if no data
                for field in cb_fieldnames:
                    if field in ['cb_created_at', 'cb_updated_at', 'cb_entity_def_id']:  # these are string values
                        row[field] = "NA"

            enriched_data.append(row)
            time.sleep(0.2)  # Delay to respect rate limits

    # Write the enriched data to a new CSV file
    with open(output_file, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=all_fieldnames)
        writer.writeheader()
        writer.writerows(enriched_data)

# Scrape data from a single company element
def scrape_company(company_element):
    name = company_element.find("span", class_="_coName_86jzd_453").text.strip()
    location = company_element.find("span", class_="_coLocation_86jzd_469").text.strip()
    description = company_element.find("span", class_="_coDescription_86jzd_478").text.strip()
    
    cohort_element = company_element.find("a", href=lambda x: x and "batch" in x)
    cohort = cohort_element.text.strip() if cohort_element else ""
    
    tags = [tag.text.strip() for tag in company_element.find_all("span", class_="pill _pill_86jzd_33") 
            if tag.text.strip() != cohort]
    
    # Check for B2B tag and remove it from tags if present
    b2b = False

    # make a new column to store boolean value for b2b startups
    if "B2B" in tags:
        b2b = True
        tags.remove("B2B")  # Remove B2B tag

    return {
        "Name": name,
        "Location": location,
        "Description": description,
        "Cohort": cohort,
        "Tags": ", ".join(tags),
        "b2b": b2b
    }

# All company data
all_companies = []

# Scroll and scrape
while True:
    # Wait to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "_company_86jzd_338")))
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # All company elements
    company_elements = soup.find_all("a", class_="_company_86jzd_338")
    
    # Scrape data from each company element
    for company_element in company_elements:
        company_data = scrape_company(company_element)
        if company_data not in all_companies:
            all_companies.append(company_data)
    
    # How much to be scraped |--> MODIFIABLE <--|, but minimum is 20 companies
    if len(all_companies) >= 300:
        break
    
    # Scroll down to load more companies
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for new content to load

# Quit browser
driver.quit()

# Create DataFrame and save to CSV
df = pd.DataFrame(all_companies)
df.to_csv("startup_data.csv", index=False)

print(f"Scraped data for {len(all_companies)} companies and saved to startup_data.csv")

# Enrich dataset with Crunchbase data
input_file = "startup_data.csv"
output_file = "startup_data_enriched.csv"
enrich_dataset(input_file, output_file)
print("Enrichment complete. Check the output file.")