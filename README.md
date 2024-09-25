# Crunchy-Combinator: Startup Data Aggregator

# Project Overview

Crunchy-Combinator is a project designed to aggregate comprehensive startup data by scraping Y Combinator's website for startup names and then enriching this data using the Crunchbase API. The purpose is to gather additional valuable information about startups, such as stock exchange listings, social media links (LinkedIn, Twitter, Facebook), logos, and extended descriptions, all of which help users gain deeper insights into the companies.

## Why Y Combinator?

Y Combinator is one of the most prestigious startup accelerators in the world, supporting hundreds of promising companies through their growth stages. The website provides an accessible list of startups, making it a valuable starting point for collecting data on early-stage companies. Many of these startups play significant roles in innovation across industries, and their data is critical for investors, analysts, or those simply interested in startup culture.

## Why Crunchbase?

Crunchbase is a comprehensive startup database that provides detailed information on companies, founders, investors, and funding rounds. By enriching Y Combinator’s startup data with Crunchbase’s insights, the dataset becomes more actionable, providing users with additional layers of information for analysis.


# Data Gathered

From Y Combinator:
- Startup Name
- Location
- Initial Description
- Cohort (the batch the startup belongs to)
- Tags (indicating their field of operation)

From Crunchbase API:
- Stock Exchange Information (for publicly traded startups)
- Social Media Links (LinkedIn, Twitter, Facebook)
- Date of Creation
- Entity Defining Tag (i.e. Organization)
- Logo
- Extended Description
- Information Update Date
- Website URL

This dataset contains startup data gathered from the Y Combinator website and Crunchbase API. The purpose of this dataset is to provide a comprehensive and up-to-date list of Y Combinator startups, including their names, descriptions, locations, cohorts, and tags. The dataset also includes additional information from Crunchbase, such as the date the startup was founded, its socials and its website URL.

The dataset will provide value to users by providing a single source of truth for Y Combinator startup data. Currently, there is no publicly available dataset that provides this information in a single place. The dataset will be useful for researchers, investors, and entrepreneurs who want to analyze or learn more about Y Combinator startups.

Both Y Combinator and Crunchbase limit the amount of data they make publicly available. Crunchbase, in particular, charges for access to their detailed data. The combination of these datasets can create valuable insights that typically require paid access, which is why a comprehensive dataset is not freely available in the market. Even in this case, the premium API provides more data about the startups.

To run this dataset, follow these steps:

1. Clone the repository: `git clone https://github.com/decipher6/crunchy_combinator`
2. Install the requirements: `pip install -r requirements.txt`
3. Run the web scraper: `python main.py`. (You may change the number of companies to scrape, but minimum 40 will be scraped)
4. The dataset will be saved as a CSV file called `startup_data_enriched.csv`.
5. The pre-enriched `startup_data.csv` is also available.
