# -*- coding: utf-8 -*-
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from opencc import OpenCC
import json
import re
import time


URL = "https://www.forecastock.tw/category/%E7%9B%A4%E5%8B%A2%E5%88%86%E6%9E%90"
FALLBACK_URL = "https://www.cnyes.com/search/all?keyword=%E7%BE%8E%E8%82%A1%E7%9B%A4%E5%BE%8C"
converter = OpenCC('s2t')

def get_driver():
    # Configure Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    # Return a new instance of Chrome WebDriver
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)


def wait_for_scroll_to_complete(driver, timeout=20):
    # wait for page to finisg scolling, check if page is stable 
    prev_scroll_position = driver.execute_script("return window.scrollY;")  # current scolling position 
    timeout_time = time.time() + timeout  # set max waiting time 

    while time.time() < timeout_time:
        time.sleep(0.5)  # check every 0.5 seconds 
        new_scroll_position = driver.execute_script("return window.scrollY;")
        
        if new_scroll_position == prev_scroll_position:
            break  # scolling complete
        prev_scroll_position = new_scroll_position

def crawl_forecastock_news_browser(driver, idx):
    try:
        driver.switch_to.window(driver.window_handles[idx])  # switch to corresponding pages
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.cardArticle__header'))
        )
        news_btns = driver.find_elements(By.CSS_SELECTOR, '.cardArticle__header')
        if idx < len(news_btns):
            button = news_btns[idx]
            print(f"Found button at index {idx}")
            print(f"Button text: {button.text}")

            # scolling window to ensure buttions are visible 
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});", button)
            print(f"Scrolled to button at index {idx}")

            # wait for scolling to complete 
            wait_for_scroll_to_complete(driver)
            # wait for button to click
            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable(button)
            )
            button.click()
            print(f"Index {idx} clicked.")
        else:
            print(f"Index {idx} out of range.")

    except Exception as e:
        print(f"Failed to crawl index {idx}: {e}")


def open_webpage(driver, url):
    driver.execute_script(f"window.open('{url}');")

def crawl_forecastock(news=10):
    driver = get_driver()  # create only one WebDriver

    # open mutiple pages
    driver.get(URL)

    threads = []
    for _ in range(news - 1):  # open news - 1 pages, multi-threading with thread
        t = Thread(target=open_webpage, args=(driver, URL))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    # wait for all pages to finish loading
    for idx in range(news):
        crawl_forecastock_news_browser(driver, idx)

    articles = {}
    for i in range(news):
        # switch to correspoding page
        driver.switch_to.window(driver.window_handles[i])
        try:
            # Ensure news titles are loaded
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.article'))
            )
            # get current url
            current_url = driver.current_url
            # get website title
            title = driver.title

            # Convert titles to Traditional Chinese
            articles[converter.convert(title)] =  current_url
            
        except:
            print("Failed to crawl, switching to next news site...")
    driver.quit()
    return articles




def crawl_cnyes(news = 10):
    driver = get_driver()
    driver.get(FALLBACK_URL)
    

    WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.jsx-1986041679'))
    )

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')


    base_url = "https://news.cnyes.com"
    articles = {
        tag.select_one('h3.jsx-1986041679').text.strip(): base_url + tag.get("href") if tag.get("href").startswith("/") else tag.get("href")
        for tag in soup.select('.jsx-1986041679.news')
    }


    
    driver.quit()
    
    if not articles:
        print("Failed to crawl cnyes site...")

    return articles 

    
website = {
    'forecastock': crawl_forecastock,
    'cnyes': crawl_cnyes
}
content_lambda = {
    'forecastock': lambda x: x.find_element(By.CSS_SELECTOR, '.article'),
    'cnyes': lambda x: x.find_element(By.ID, 'article-container') 
}
content_parse = {
    'forecastock': 'article',
    'cnyes': '#article-container'
}
title_regex = {
    'forecastock': "美股盤勢",
    'cnyes': "美股盤後"
}

def news(news_website='cnyes', news=5):
       

    print(f'Crawl website: {news_website}')
    articles = website[news_website](news)

    if articles:        
        # Set the keyword to search for, using regex pattern
        keyword = title_regex[news_website]
        pattern = re.compile(r'.*' + re.escape(keyword) + r'.*')
        
        # Search for titles containing specific characters and their links
        # results = {title: link for title, link in data.items() if pattern.match(title)}
        results = {title: link for title, link in articles.items() if pattern.match(title)}
        
        
        # Display search results
        if results:
            print(f"News and links containing '{keyword}' are as follows:")
            for title, link in results.items():
                print(f"Title: {title}\nLink: {link}\n")
        else:
            print(f"No news containing '{keyword}' found.")
        
        
        # Get the first result
        if results:
            
            news_content = ''
            
            for news_title, news_link in results.items():
                
                print(f"result:\nTitle: {news_title}\nLink: {news_link}\n")
            
                driver = get_driver()
                driver.get(news_link)
                
                
                WebDriverWait(driver, 1).until(
                    content_lambda[news_website] 
                    )
                
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                content = '\n'.join(
                    [
                    tag.text
                    for tag in soup.select(content_parse[news_website])
                    ]
                )
                news_content += 'News content:\n' + content + '\n'     
                           
                driver.quit()
                
                    
                
    
        else:
            print(f"No news containing '{keyword}' found.")
            
        print(news_content)
        
        
        from openai import OpenAI
        with open(f'openAI_API_key.txt', 'r', encoding='utf-8') as file:
            api_key = file.read()
            
        client = OpenAI(api_key = api_key)
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"Please provide a professional analysis summary of the U.S. stock market performance for the most recent trading day from the scraped data. The content must include the following three parts:\n\n1. S&P 500 index performance data and percentage change for yesterday, and an explanation of the main macroeconomic or market factors driving these changes.\n\n2. The strongest and weakest industry sectors (at least two each), their specific gains or losses, and the specific catalysts or trends causing these sector performance differences.\n\n3. Significant movements (significant rise or fall or major announcements) of 3-5 important individual stocks, including the percentage change in stock prices and an analysis of the reasons.\n\nPlease provide each paragraph in bullet-point format, use professional financial terminology, ensure data accuracy to two decimal places, and keep each paragraph summary within 300 words, with a total word count not exceeding 900 words.\n\nHere is the data content:\n{news_content}"
                }
            ]
        )
        
        print(f'\n\n\n\n\n#(#(#(#(#(#(#(#(#(#(#(#(#))))))))))))')
        summary_content = completion.choices[0].message.content
        print(summary_content)
        return summary_content
        
    else:
        print("Unable to retrieve news from either website.")
        
        
        