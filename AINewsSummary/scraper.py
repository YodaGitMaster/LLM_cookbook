from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
import requests_random_user_agent
from bs4 import BeautifulSoup
import re
import sqlite3
from PIL import Image
import pytesseract

def setup_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    
    # Create the table
    c.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY,
            url TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

setup_db()

def add_url(new_url):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()

    c.execute('INSERT INTO urls (url) VALUES (?)', (new_url,))

    conn.commit()
    conn.close()

def remove_url(target_url):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()

    c.execute('DELETE FROM urls WHERE url = ?', (target_url,))

    conn.commit()
    conn.close()

def purge_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()

    c.execute('DELETE FROM urls')

    conn.commit()
    conn.close()

def get_all_urls():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()

    c.execute('SELECT url FROM urls')
    urls = c.fetchall()

    conn.close()

    # Extracting URLs from tuples and returning as a list of strings
    return [url[0] for url in urls]

def click_accept_all_button(driver):
    # Try to locate the button by its text content
    try:
        accept_all_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept All')]")
        accept_all_button.click()
        allow_all = driver.find_element(By.XPATH, "//button[contains(text(), 'Allow All')]")
        allow_all.click()
    except:
        pass


def load_webpage_with_random_user_agent(URL):
    """
    Loads a webpage with a random user-agent using Selenium.

    Args:
    - URL (str): The URL of the webpage to load.

    Returns:
    - webdriver.Chrome: An instance of the Chrome browser with the loaded webpage.
    """

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    # options.add_argument('--headless')
    options.add_argument('log-level=3')
    options.add_argument("--disable-popup-blocking")
    # Fetch a random user-agent from httpbin
    resp = requests.get('https://httpbin.org/user-agent')
    random_agent = resp.json()['user-agent']
    print(random_agent)
    options.add_argument(f"--user-agent={random_agent}")

    # Initialize and return the Chrome driver with the specified options
    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    time.sleep(3)
    
 
    try:
        print(URL)
        #element = driver.find_element(By.XPATH,"//*[@id=\"yDmH0d\"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button")
        element = driver.find_element_by_xpath('//input[@type="submit" and @value="Accept all" or  @aria-label="Accept all"]')
        time.sleep(1)
        element.click()
        time.sleep(2)
        click_accept_all_button(driver)
        title = driver.title
 
        if 'Google News - Business - Latest' in title:
            return driver
        
        print(title)
        add_url()
        body_element = driver.find_element(by=webdriver.common.by.By.TAG_NAME, value='article')
        if body_element != None:
            text = str(body_element.text).strip().rstrip()
            print(f"Body Content: {text}")
       

    except Exception as e:
        print("Article tag not found trying <p> ")

        paragraphs = driver.find_elements(By.TAG_NAME, 'p')
        article = ''
        for p in paragraphs:
            article+=str(p.text).strip().rstrip()
        
        print(article.strip().rstrip())
        print("-"*50)
        pass
        

    
    return driver
 
URL = 'https://news.google.com/search?q=stock'
driver = load_webpage_with_random_user_agent(URL)

time.sleep(3)
soup = BeautifulSoup(driver.page_source, 'html.parser')
hrefs =  [a['href'] for a in soup.find_all('a', class_='VDXfz') if a.has_attr('href')]

print(f"found: {+len(hrefs)} urls")

for url in hrefs:
    load_webpage_with_random_user_agent(f"https://news.google.com/articles/{str(url).replace('./articles/','')}")
    time.sleep(10)
    # add_url(url)

# Close the browser
# driver.quit()
#
#https://news.google.com/articles/CCAiCzhEYzJ1TktWZUxzmAEB?hl=en-US&gl=US&ceid=US%3Aen