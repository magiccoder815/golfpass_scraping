import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException


# File paths
original_file_path = 'Copy of golfcoursesandgolfresorts_1.0.2 - golfcoursesandgolfresorts_1.0.2.csv'
updated_file_path = 'updated_golfcoursesandgolfresorts_final.csv'  # New file for updated data

# Check if file is accessible
def is_file_accessible(filepath, mode='r'):
    """Check if a file can be accessed in the specified mode."""
    try:
        with open(filepath, mode):
            pass
    except IOError:
        return False
    return True

# Ensure the original file is not open
if not is_file_accessible(original_file_path, 'r'):
    print(f"Error: The file '{original_file_path}' is currently open. Please close it and try again.")
    exit()

# Load the CSV and ensure required columns exist
data = pd.read_csv(original_file_path)

if 'description' not in data.columns:
    data['description'] = None
if 'website' not in data.columns:
    data['website'] = None

biz_names = data['biz_name'].dropna().tolist()

# Base URL for search
base_url = "https://www.golfpass.com/search?q={}&global=enabled#search-courses"

# Function to scrape link from the first matching div on the search page
def scrape_first_golfpass_link(biz_name):
    search_url = base_url.format(biz_name.replace(' ', '+').replace('&', '%26'))
    response = requests.get(search_url)
    if response.status_code != 200:
        print(f"Failed to fetch {search_url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    div_element = soup.find('div', class_='CoursePromo-media rounded-xl')
    if div_element:
        link_element = div_element.find('a', href=True)
        if link_element:
            return f"https://www.golfpass.com{link_element['href']}"
    return None

# Selenium setup for getting the redirected URL
def get_redirected_url(raw_url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(raw_url)
        time.sleep(10)
        print("raw: ", raw_url)
        # Get the final redirected URL
        final_url = driver.current_url
        print("redirected: ", final_url)

    except TimeoutException:
        print(f"Timeout occurred while getting redirected URL for: {raw_url}")
        final_url = None
    finally:
        driver.quit()  # Ensure the browser is closed

    return final_url

# Function to scrape course details
def scrape_course_details(course_url):
    response = requests.get(course_url)
    if response.status_code != 200:
        print(f"Failed to fetch course page: {course_url}")
        return None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    description_div = soup.find('div', class_='CourseAbout-description')
    description = description_div.get_text(strip=True) if description_div else None

    website_link = soup.find('a', class_='Link', string='Course Website')
    course_website = None
    if website_link:
        # Extract the original href
        raw_website_url = website_link['href']
        course_website = get_redirected_url(raw_website_url)

    return description, course_website

# Iterate over business names and update the DataFrame
for index, row in data.iterrows():
    biz_name = row['biz_name']
    print(f"Scraping for: {biz_name}")
    link = scrape_first_golfpass_link(biz_name)
    description, website = None, None
    if link:
        print(f"Scraping details for: {link}")
        description, website = scrape_course_details(link)

    # Update the DataFrame
    data.at[index, 'Description'] = description
    data.at[index, 'website'] = website

# Ensure the updated file is not open
if not is_file_accessible(updated_file_path, 'w'):
    print(f"Error: The file '{updated_file_path}' is currently open. Please close it and try again.")
    exit()

# Save the updated data to a new file
data.to_csv(updated_file_path, index=False)
print(f"Scraping completed. Updated data saved to '{updated_file_path}'.")
