import os
import time
import json
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configuration
CONFIG = {
    "base_url": "https://codeforces.com/problemset/problem/",
    "output_dir": "./data/",
    "delay": 2,
    "driver_path": "C:\\Program Files (x86)\\chromedriver" 
}    

def fetch_page(url, use_selenium=True):
    """Fetch page content using requests or Selenium."""
    options = Options()
    options.add_argument("--headless")
    service = Service(CONFIG["driver_path"])
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(CONFIG["delay"])
    content = driver.page_source
    driver.quit()
    return BeautifulSoup(content, "html.parser")

def parse_problem(html):
    """Extract problem details from the HTML."""
    try:
        title = html.find("div", class_="title").text.strip()
        statement = html.find("div", class_="problem-statement").text.strip()
        tags = [tag.text.strip() for tag in html.find_all("span", class_="tag-box")]
        return {
            "title": title,
            "statement": statement,
            "tags": tags
        }
    except AttributeError as e:
        raise Exception("Failed to parse problem data") from e

def save_problem(data):
    """Save problem data to text and JSON files."""
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    title_slug = data["title"].replace(" ", "_").replace("/", "_")
    text_path = os.path.join(CONFIG["output_dir"], f"{title_slug}.txt")
    json_path = os.path.join(CONFIG["output_dir"], f"{title_slug}.json")

    with open(text_path, "w", encoding="utf-8") as f:
        f.write(data["statement"])

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def scrape_problem(problem_id):
    """Scrape a problem given its ID."""
    url = f"{CONFIG['base_url']}{problem_id}"
    print(f"Scraping: {url}")
    html = fetch_page(url)
    problem_data = parse_problem(html)
    save_problem(problem_data)
    print(f"Saved: {problem_data['title']}")

def scrape_editorial(problem_id):
    """Scrape editorial for a given problem ID."""
    url = f"{CONFIG['base_url']}{problem_id}/tutorial"
    print(f"Scraping editorial: {url}")
    html = fetch_page(url, use_selenium=True)
    try:
        editorial_content = html.find("div", class_="editorial-content").text.strip()
        os.makedirs(CONFIG["output_dir"], exist_ok=True)
        editorial_path = os.path.join(CONFIG["output_dir"], f"editorial_{problem_id}.txt")
        with open(editorial_path, "w", encoding="utf-8") as f:
            f.write(editorial_content)
        print(f"Saved editorial: {editorial_path}")
    except AttributeError:
        print(f"No editorial found for problem {problem_id}")

def main():
    """Main function to scrape problems and editorials."""
    # Example problem IDs to scrape
    problem_ids = ["1/A", "1/B", "2/A"]

    for problem_id in problem_ids:
        try:
            scrape_problem(problem_id)
            scrape_editorial(problem_id)
        except Exception as e:
            print(f"Error scraping {problem_id}: {e}")
        time.sleep(CONFIG["delay"])

if __name__ == "__main__":
    main()
