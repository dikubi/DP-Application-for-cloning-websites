import sys
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import webbrowser
from selenium.webdriver.chrome.options import Options


driver = webdriver.Chrome(ChromeDriverManager().install())

def close_file(file):
    file.close()

def create_file():
    time_now = time.strftime("%Y%m%d-%H%M%S")
    file_name = time_now + ".html"
    file = open(file_name, "w", encoding="utf-8")
    return file

def save_to_file(file, input_to_file):
    file.write(input_to_file)

def get_html_tree():
    URL_input = input("Vložte URL: ")
    driver.get(URL_input) 
    time.sleep(5)

    html = driver.page_source 
    soup = BeautifulSoup(html, "html5lib")
    print(soup.prettify())
    file_html_tree = create_file()
    save_to_file(file_html_tree, soup.prettify())
    close_file(file_html_tree)

get_html_tree()