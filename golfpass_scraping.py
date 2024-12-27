import requests
from bs4 import BeautifulSoup
import pandas as pd

# Load the CSV and extract business names
file_path = 'Copy of golfcoursesandgolfresorts_1.0.2 - golfcoursesandgolfresorts_1.0.2 (1).csv'
data = pd.read_csv(file_path)
biz_names = data['biz_name'].dropna().tolist()

# Base URL for search
base_url = "https://www.golfpass.com/search?q={}&global=enabled#search-courses"

# Function to scrape all links from a search page
def scrape_golfpass_links(biz_name):
    search_url = base_url.format(biz_name.replace(' ', '+').replace('&', '%26'))
    response = requests.get(search_url)
    if response.status_code != 200:
        print(f"Failed to fetch {search_url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    # Find all <div> elements with the desired class
    div_elements = soup.find_all('div', class_='CoursePromo-media rounded-xl')
    
    links = []
    for div_element in div_elements:
        link_element = div_element.find('a', href=True)
        if link_element:
            links.append(f"https://www.golfpass.com{link_element['href']}")
    return links

# Function to scrape course description from a course page
def scrape_course_details(course_url):
    response = requests.get(course_url)
    if response.status_code != 200:
        print(f"Failed to fetch course page: {course_url}")
        return None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract course description
    description_div = soup.find('div', class_='CourseAbout-description')
    description = description_div.get_text(strip=True) if description_div else None

    # Extract the Course Website link
    website_link = soup.find('a', class_='Link', string='Course Website')
    course_website = website_link['href'] if website_link else None

    return description, course_website

# Iterate over business names and scrape links and descriptions
results = []
for biz_name in biz_names:
    print(f"Scraping for: {biz_name}")
    links = scrape_golfpass_links(biz_name)  # Get all links for the business name

    if not links:
        # Add a row for business names with no links
        results.append({"biz_name": biz_name, "link": None, "description": None, "website": None})
    else:
        for link in links:  # Iterate through each link
            print(f"Scraping details for: {link}")
            description, website = scrape_course_details(link)  # Scrape details for each link
            results.append({"biz_name": biz_name, "link": link, "description": description, "website": website})

# Save results to a CSV
output_df = pd.DataFrame(results)
output_df.to_csv('golfpass_links.csv', index=False)
print("Scraping completed. Results saved to 'golfpass_links.csv'.")
