import sys
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import webbrowser
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def close_file(file):
    file.close()

def create_file():
    time_now = time.strftime("%Y%m%d-%H%M%S")
    file_name = time_now + ".html"
    file = open(file_name, "w", encoding="utf-8")
    return file

def save_to_file(file, input_to_file):
    file.write(input_to_file)


#def scrape_style_files():




def get_html_tree():
    URL_input = input("Vložte URL: ")
    driver.get(URL_input) 
    time.sleep(5)

    #odstranění path a parametrů za doménou stránky
    parse_url = urlparse(URL_input)
    print(parse_url) #pro kontrolu, potom smazat
    base_url = parse_url.scheme + "://" + parse_url.netloc
    print(base_url) #pro kontrolu, potom smazat

    html = driver.page_source 
    soup = BeautifulSoup(html, "html5lib")
    #print(soup.prettify())
    file_html_tree = create_file()
    save_to_file(file_html_tree, soup.prettify())
    close_file(file_html_tree)

    js_files = []
    cs_files = []

    for script in soup.find_all("script"):
        if script.attrs.get("src"):
        # if the tag has the attribute 'src'
            url = script.attrs.get("src")
            contains_scheme = url.startswith("http")
            if contains_scheme == True:
                js_files.append(url)
            else:
                js_files.append(base_url+url)
    
    for css in soup.find_all("link"):
        if css.attrs.get("href"):
        # if the link tag has the 'href' attribute
            url = css.attrs.get("href")
            contains_scheme = url.startswith("http")
            if contains_scheme == True:
                cs_files.append(url)
            else:    
                cs_files.append(base_url+url)

    print(f"Total {len(js_files)} javascript files found")
    print(f"Total {len(cs_files)} CSS files found")


    with open("javascript_files.txt", "w") as f:
        for js_file in js_files:
            print(js_file, file=f)

    with open("css_files.txt", "w") as f:
        for css_file in cs_files:
            print(css_file, file=f)




get_html_tree()