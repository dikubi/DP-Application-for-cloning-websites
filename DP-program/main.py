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
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def close_file(file):
    file.close()

def create_file():
    file_name = "index.html"
    file = open(file_name, "w", encoding="utf-8")
    return file

def split_path(url):
    """Oddělí cestu od názvu souboru a vrátí jen název souboru."""

    parse_url = urlparse(url)
    just_path = parse_url.path  #vrátí cestu k souboru, bez https atd.
    head_tail = os.path.split(just_path)  #rozdělí cestu na cestu a název souboru
    name =  head_tail[1]  #vrátí jen název souboru
    return name

def create_file_style(original_path):
    """Vytvoří prázdné soubory pro styly,
    original_path je adresa css/js stylu, která byla získána z vložené stránky,
    pomocí fce split_path je upravena a použita jako název pro soubor."""
    
    file_name = split_path(original_path)
    
    print("Vytvořen soubor s jménem: " + file_name)  #pro kontrolu, potom smazat
    file = open(file_name, "w", encoding="utf-8")
    return file

def save_to_file(file, input_to_file):
    file.write(input_to_file)

def scrape_style_files(file_with_urls_found):
    """Projde odkazy na css/js styly v .txt dokumentech a vytáhne z nich css/js kód.
    Poté zavolá create_file_style, která vytvoří .css / .js souboru pro každý soubor
    a uloží do něj získaný kód stylu."""

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
            continue

        file_style = create_file_style(line) #line je předáno pro vytvoření správného názvu souboru
        save_to_file(file_style, scraped_code)
        close_file(file_style)

def download_images():
    """Projde odkazy na obrázky v .txt a stáhne je."""

    file = open("images.txt", "r")
    for line in file:
        file_name = split_path(line)
        print("Downloading image: " + file_name)
        try:
            urllib.request.urlretrieve(line, file_name) #stáhne obrázek
        except urllib.error.HTTPError:
            print("Soubor: " + line + " je prázdný.")
            continue

def find_styles_images(base_url, path_url):
    """Najde v html stránky (soup) všechny odkazy na css a js styly a obrázky, 
    uloží je do listů a tyto listy pak uloží do souborů javascript_files.txt,
    css_files.txt, images.txt.
    Zaroveň upraví jejich src a href v soup a uloží do index.html"""

    js_files = []
    cs_files = []
    img_files = []

    html = driver.page_source
    soup = BeautifulSoup(html, "html5lib")
    
    for script in soup.find_all("script"):
        if script.attrs.get("src"):
            url = script.attrs.get("src")
            contains_scheme = url.startswith("http")
            contains_dot = url.startswith(".")
            if contains_dot == True:
                url = url[1:]
            if contains_scheme == True:
                js_files.append(url)
            else:
                try: #prochází úrovně adresy a pro každou uloží nalezený src 
                    js_files.append(base_url + "/" + 
                                    PurePosixPath(unquote(urlparse(path_url).path)).parts[-2] + "/" + 
                                    PurePosixPath(unquote(urlparse(path_url).path)).parts[-1] + url)
                    js_files.append(base_url + "/" + 
                                    PurePosixPath(unquote(urlparse(path_url).path)).parts[-2] + url)
                    js_files.append(base_url+url)
                except IndexError:
                    continue

            new_src = split_path(url)
            
            script['src'] = new_src #nahradí původní src jen názvem souboru
            html = str(soup) #uloží upravený kód do soup

    for item in soup.find_all("link"):
        if item.attrs.get("href"):
            url = item.attrs.get("href")
            contains_scheme = url.startswith("http")
            if (url.__contains__("css")):
                print("bude uloženo:  " + url) #pro kontrolu, potom smazat
                if contains_dot == True:
                    url = url[1:]
                if contains_scheme == True:
                    cs_files.append(url)
                else:    
                    try: #prochází úrovně adresy a pro každou uloží nalezený href 
                        cs_files.append(base_url + "/" + 
                                        PurePosixPath(unquote(urlparse(path_url).path)).parts[-2] + "/" + 
                                        PurePosixPath(unquote(urlparse(path_url).path)).parts[-1] + url)
                        cs_files.append(base_url + "/" + 
                                        PurePosixPath(unquote(urlparse(path_url).path)).parts[-2] + url)
                        cs_files.append(base_url + url)
                    except IndexError:
                        continue
            elif url.endswith(".png") == True or url.endswith(".jpg") == True:
                print("bude uloženo:  " + url) #pro kontrolu, potom smazat
                if contains_dot == True:
                    url = url[1:]
                if contains_scheme == True:
                    img_files.append(url)
                else:   
                    try: 
                        img_files.append(base_url + "/" + 
                                        PurePosixPath(unquote(urlparse(path_url).path)).parts[-2] + "/" + 
                                        PurePosixPath(unquote(urlparse(path_url).path)).parts[-1] + url)
                        img_files.append(base_url + "/" + 
                                        PurePosixPath(unquote(urlparse(path_url).path)).parts[-2] + url)
                        img_files.append(base_url + url)
                    except IndexError:
                        continue
            else:
                print("nebude uloženo:  " + url) #pro kontrolu, potom smazat

            new_src = split_path(url)

            item['href'] = new_src #nahradí původní href jen názvem souboru
            html = str(soup) #uloží upravený kód do soup

    for img in soup.find_all('img'): 
        url = img['src']
        contains_scheme = url.startswith("http")
        contains_dot = url.startswith(".")
        if contains_dot == True:
            url = url[1:]
        if contains_scheme == True:
            img_files.append(url)
        else:  
            try:  
                img_files.append(base_url + "/" +
                                PurePosixPath(unquote(urlparse(path_url).path)).parts[-2] + "/" + 
                                PurePosixPath(unquote(urlparse(path_url).path)).parts[-1] + url)
                img_files.append(base_url + "/" + 
                                PurePosixPath(unquote(urlparse(path_url).path)).parts[-2] + url)
                img_files.append(base_url + url)
            except IndexError:
                continue

        new_src = split_path(url)
            
        img['src'] = new_src #nahradí původní src jen názvem souboru
        html = str(soup) #uloží upravený kód do soup

    file_html_tree = create_file() 
    save_to_file(file_html_tree, soup.prettify()) #uloží získaný a upravený html kód do samostatného .html souboru
    close_file(file_html_tree)

    print(f"Celkem {len(js_files)} javascript souborů nalezeno") #pro kontrolu, potom smazat
    print(f"Celkem {len(cs_files)} CSS souborů nalezeno") #pro kontrolu, potom smazat
    
    #nalezené odkazy, které byly uloženy do listů, se uloží do .txt souborů
    with open("javascript_files.txt", "w") as f:
        for js_file in js_files:
            print(js_file, file=f)

    with open("css_files.txt", "w") as f:
        for css_file in cs_files:
            print(css_file, file=f)

    with open("images.txt", "w") as f:
        for img_file in img_files:
            print(img_file, file=f) 

def main():
    URL_input = input("Vložte URL: ")
    driver.get(URL_input) 
    time.sleep(5)

    #odstranění path a parametrů za doménou stránky
    parse_url = urlparse(URL_input)
    print(parse_url) #pro kontrolu, potom smazat
    base_url = parse_url.scheme + "://" + parse_url.netloc
    print("Base url: " + base_url) #pro kontrolu, potom smazat
    
    # doména stránky + path část
    path_url = parse_url.scheme + "://" + parse_url.netloc + parse_url.path
    print("URL with path: " + path_url) #pro kontrolu, potom smazat

    html = driver.page_source 
    soup = BeautifulSoup(html, "html5lib")

    original_html = open("index_original.html", "w", encoding="utf-8")
    original_html.write(soup.prettify())
    original_html.close

    find_styles_images(base_url, path_url)
    
    print("scraping css") #pro kontrolu, potom smazat
    scrape_style_files("css_files.txt")
    scrape_style_files("javascript_files.txt")

    download_images()


    

main()