from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

driver = webdriver.Chrome()

driver.get('https://www.ycombinator.com/companies')

# scrape data from a single company element
def scrape_company(company_element):
    name = company_element.find('span', class_='_coName_86jzd_453').text.strip()
    description = company_element.find('span', class_='_coDescription_86jzd_478').text.strip()
    
    # cohort
    cohort_element = company_element.find('a', href=lambda x: x and 'batch' in x)
    cohort = cohort_element.text.strip() if cohort_element else ''
    
    # tags
    tags = [tag.text.strip() for tag in company_element.find_all('span', class_='pill _pill_86jzd_33')]
    
    return {
        'Name': name,
        'Description': description,
        'Cohort': cohort,
        'Tags': ', '.join(tags)
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
    
    # how much to be scarped |--> MODIFIABLE <--|
    if len(all_companies) >= 20:
        break
    
    # scroll down to load more companies
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # wait for new content to load

# quuit browser
driver.quit()

# create df and save to csv
df = pd.DataFrame(all_companies)
df.to_csv('startup_data.csv', index=False)

print(f"Scraped data for {len(all_companies)} companies and saved to startup_data.csv")