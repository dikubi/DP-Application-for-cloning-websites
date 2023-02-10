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
import urllib.request
import os
import re
from os.path import basename, splitext


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def close_file(file):
    file.close()

def create_file():
    #time_now = time.strftime("%Y%m%d-%H%M%S")
    #file_name = time_now + ".html"
    file_name = "index.html"
    file = open(file_name, "w", encoding="utf-8")
    return file

def create_file_style(original_path): #original_path je adresa css/js stylu, která byla získána z vložené stránky
    parse_url = urlparse(original_path)
    just_path = parse_url.path  #vrátí cestu k souboru, bez https atd.
    head_tail = os.path.split(just_path)  #rozdělí cestu na cestu a název souboru
    file_name =  head_tail[1]  #vrátí jen název souboru
    print("head je: " + file_name)  #pro kontrolu, potom smazat
    file = open(file_name, "w", encoding="utf-8")
    return file

def save_to_file(file, input_to_file):
    file.write(input_to_file)


def scrape_style_files(file_with_urls_found):
    """Projde odkazy na css/js styly v .txt dokumentech a vytáhne z nich css/js kód.
    Poté zavolá create_file_style, která vytvoří .css / .js souboru pro každý soubor."""

    file = open(file_with_urls_found, "r")
    for line in file:
        print("uložený odkaz: " + line) #pro kontrolu, potom smazat
        driver.get(line) 
        time.sleep(5)

        html = driver.page_source 
        soup = BeautifulSoup(html, "html5lib")

        pre = soup.find("pre")
        
        try:
            scraped_code = pre.text
        except AttributeError:
            print("Soubor: " + line + " je prázdný.")

        file_style = create_file_style(line) #line je předáno pro vytvoření správného názvu souboru
        save_to_file(file_style, scraped_code)
        close_file(file_style)

def download_images(soup):
    """Najde tagy img v html, získá jejich url adresu a lokálně je uloží pod jejich
    původním jménem."""

    images = soup.find_all('img')

    for item in images:
        print("scraping images: ")
        print(item['src'])
    
    with open("images.txt", "w") as f:
        for item in images:
            parse_url = urlparse(item['src'])
            just_path = parse_url.path  #vrátí cestu k souboru, bez https atd.
            head_tail = os.path.split(just_path)  #rozdělí cestu na cestu a název souboru
            file_name =  head_tail[1]  #vrátí jen název souboru
            print("head je: " + file_name)  #pro kontrolu, potom smazat
            print(item['src'], file=f) #uloží odkaz na obrázek do txt souboru
            print("Downloading image: " + file_name)
            urllib.request.urlretrieve(item['src'], file_name) #stáhne obrázek
    

def find_styles(base_url): #původně další param soup
    """Najde v html stránky (soup) všechny odkazy na css a js styly, uloží je do listů 
    a tyto listy pak uloží do souborů javascript_files.txt a css_files.txt."""

    js_files = []
    cs_files = []

    html = driver.page_source
    soup = BeautifulSoup(html, "html5lib")
    
    for script in soup.find_all("script"):
        if script.attrs.get("src"):
        # if the tag has the attribute 'src'
            url = script.attrs.get("src")
            contains_scheme = url.startswith("http")
            if contains_scheme == True:
                js_files.append(url)
            else:
                js_files.append(base_url+url)

            parse_url = urlparse(url)
            just_path = parse_url.path  #vrátí cestu k souboru, bez https atd.
            head_tail = os.path.split(just_path)  #rozdělí cestu na cestu a název souboru
            new_src =  head_tail[1]  #vrátí jen název souboru
            
            script['src'] = new_src
            html = str(soup)

    #file_html_tree = create_file() 
    #save_to_file(file_html_tree, soup.prettify()) #uloží získaný html kód do samostatného .html souboru
    #close_file(file_html_tree)
            #rewrite_src(url)

    for css in soup.find_all("link"):
        if css.attrs.get("href"):
        # if the link tag has the 'href' attribute
            url = css.attrs.get("href")
            contains_scheme = url.startswith("http")
            if (url.__contains__("css")):
                print("bude uloženo:  " + url) #pro kontrolu, potom smazat
                if contains_scheme == True:
                    cs_files.append(url)
                else:    
                    cs_files.append(base_url+url)
            else:
                print("nebude uloženo:  " + url) #pro kontrolu, potom smazat
            
            parse_url = urlparse(url)
            just_path = parse_url.path  #vrátí cestu k souboru, bez https atd.
            head_tail = os.path.split(just_path)  #rozdělí cestu na cestu a název souboru
            new_src =  head_tail[1]  #vrátí jen název souboru

            css['href'] = new_src
            html = str(soup)

    file_html_tree = create_file() 
    save_to_file(file_html_tree, soup.prettify()) #uloží získaný html kód do samostatného .html souboru
    close_file(file_html_tree)

    print(f"Total {len(js_files)} javascript files found") #pro kontrolu, potom smazat
    print(f"Total {len(cs_files)} CSS files found") #pro kontrolu, potom smazat
    
    #nalezené odkazy, které byly uloženy do listů, se uloží do .txt souborů
    with open("javascript_files.txt", "w") as f:
        for js_file in js_files:
            print(js_file, file=f)

    with open("css_files.txt", "w") as f:
        for css_file in cs_files:
            print(css_file, file=f)


def main():
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

    find_styles(base_url)

    print("scraping css") #pro kontrolu, potom smazat
    scrape_style_files("css_files.txt")
    scrape_style_files("javascript_files.txt")

    download_images(soup)

    
main()