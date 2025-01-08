import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager

# Load the uploaded file
uploaded_file_path = 'updated_golfcoursesandgolfresorts_1_2.csv'
data = pd.read_csv(uploaded_file_path)

# Function to set up Selenium WebDriver
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--use-gl=swiftshader')
    chrome_options.add_argument('--enable-unsafe-swiftshader')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# Function to fetch redirected URL using Selenium
def get_redirected_url(raw_url):

    if raw_url.startswith("http://"):
        return raw_url
    
    driver = setup_driver()
    final_url = None

    try:
        print("raw: ", raw_url)
        driver.get(raw_url)
        time.sleep(10)
        final_url = driver.current_url
        print("redirected: ", final_url)

    except TimeoutException:
        print(f"Timeout occurred for URL: {raw_url}")
    finally:
        driver.quit()

    return final_url

redirected = get_redirected_url("https://www.golfpass.com/travel-advisor/xgo/12304")
print(redirected)

# # Chunk size for processing
# CHUNK_SIZE = 300
# output_directory = 'data_5463-10000/'

# # Ensure output directory exists
# if not os.path.exists(output_directory):
#     os.makedirs(output_directory)

# # Process the data in chunks
# for i in range(0, len(data), CHUNK_SIZE):
#     chunk = data.iloc[i:i+CHUNK_SIZE].copy()

#     print(f"Processing rows {i} to {i+len(chunk)-1}")

#     # Update website column with redirected URLs
#     for index, row in chunk.iterrows():
#         if pd.notna(row['website']):
#             redirected_url = get_redirected_url(row['website'])
#             chunk.at[index, 'website'] = redirected_url

#     # Save the processed chunk to a new file
#     chunk_file_path = os.path.join(output_directory, f'updated_chunk_{i//CHUNK_SIZE + 1}.csv')
#     chunk.to_csv(chunk_file_path, index=False)

#     print(f"Chunk {i//CHUNK_SIZE + 1} saved to {chunk_file_path}")

# print("Processing complete.")
