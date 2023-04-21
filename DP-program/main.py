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
import cssutils
import logging
import http.client #pro chytání exception
from selenium.common.exceptions import WebDriverException #pro chytání exception
import urllib.error
from selenium.webdriver.chrome.options import Options
from os import system, name

o = Options()
#o.add_argument("--headless")
o.add_argument('log-level=3') #potlačení výpisu webdriveru do konzole

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=o) 

def clear_cli(): 
    # pro windows 
    if name == 'nt': 
        _ = system('cls') 
    # pro mac a linux 
    else: 
        _ = system('clear')

def close_file(file):
    try:
        file.close()
    except AttributeError:
        print("Attribute Error.")

def create_file():
    file_name = "index.html"
    file = open(file_name, "w", encoding="utf-8")
    return file

def split_path(url):
    """
    Oddělí cestu od názvu souboru a vrátí jen název souboru.
    Pro soubory s cestou data:image/ se nic nemění, cesta musí takto zůstat,
    aby byly přístupné přímo.
    """
    if url.startswith("data:image"):
        return url
    else:
        parse_url = urlparse(url)
        just_path = parse_url.path  #vrátí cestu k souboru (pod/složky a název souboru), bez https atd.
        head_tail = os.path.split(just_path)  #rozdělí cestu na cestu a název souboru
        name =  head_tail[1]  #vrátí jen název souboru

        return name

def create_file_style(original_path):
    """
    Vytvoří prázdné soubory pro styly,
    original_path je adresa css/js stylu, která byla získána z vložené stránky,
    pomocí fce split_path je upravena a použita jako název pro soubor.
    """
    
    file_name = split_path(original_path)
    
    print("Vytváří se soubor s jménem: " + file_name)  #pro kontrolu, potom smazat
    
    try:
        file = open(file_name, "w", encoding="utf-8")
        return file
    except FileNotFoundError:
        print("Soubor: " + file_name + "nemohl být vytvořen.")


def save_to_file(file, input_to_file):
    try:
        file.write(input_to_file)
    except AttributeError:
        print("Soubor nemohl být zapsán.")

def parse_css(css_file, line):
    """
    Projde vytvořený .css soubor a pokud v něm jsou nějaké url odkazy,
    uloží je do listu found_urls_css a do found_url_css.txt pod absolutní cestou.
    
    :css_file: uložený css soubor
    :line: celá url k css, ze kterého extrahuji další url - nutné pro sestavení
    absolutní url z relativní, která je uvedena v daném uloženém css souboru.
    """

    found_urls_css = []
    print("Do parse vstupuje: " + css_file)
    
    cssutils.log.setLevel(logging.CRITICAL) #zabrání vypisování useless logů
    sheet = cssutils.parseFile(css_file) #parse uloženého css souboru
    urls = cssutils.getUrls(sheet) #nalezení parametrů url

    for url in urls:
        print("--nalezené url:  " + url)
        contains_space = " " in url
        contains_scheme = url.startswith("http")
        edited_url = url.lstrip("./") #odstraní všechny ./ vyskytující se zleva
        #print("--editované url: " + edited_url)
        if contains_space == True:
            print("--obsahuje mezery, neplatná url, přeskakuji")
            continue
        if url.startswith("data:image") == True:
            print("--to data image, přeskakuji")
            continue
        if contains_scheme == True:
            #print("---1 " + url)
            found_urls_css.append(url)
        else:
            try: 
                #print("---2 " + edited_url)
                parse_url = urlparse(line)
                just_path = parse_url.path  #vrátí cestu k souboru s názvem souboru (začíná /)
                head_tail = os.path.split(just_path)  #rozdělí cestu na cestu a název souboru
                way =  head_tail[0]  #vrátí jen cestu k souboru bez názvu souboru (ponechává / na začátku)
                
                head_tail_second = os.path.split(way) #cestu rozdělí na cestu a poslední složku (nenechává / nakonci)
                way_second = head_tail_second[0] #vrátí jen cestu bez poslední složky

                head_tail_third = os.path.split(way_second) #cestu rozdělí na cestu a poslední složku (nenechává / nakonci)
                way_third = head_tail_third[0] #vrátí jen cestu bez poslední složky (tzn. celkově odebrány dvě poslední složky)
                
                if url.startswith("//"): #url umístěno hned za "https:"
                    final_string = parse_url.scheme + ":" + url
                    found_urls_css.append(final_string)
                    print("--nalezen: " + final_string)
                elif url.startswith("/"): #je to v root složce
                    final_string = parse_url.scheme + "://" + parse_url.netloc + "/" + edited_url
                    found_urls_css.append(final_string)
                    print("--nalezen: " + final_string)
                elif url.startswith("./"): #zůstává se ve stejné složce         
                    final_string = parse_url.scheme + "://" + parse_url.netloc + way + "/" + edited_url
                    found_urls_css.append(final_string)
                    print("--nalezen: " + final_string)
                elif url.startswith("../../"): #jde se o dvě složky výše
                    final_string = parse_url.scheme + "://" + parse_url.netloc + way_third + "/" + edited_url
                    found_urls_css.append(final_string)
                    print("--nalezen: " + final_string) 
                elif url.startswith("../"): #jde se o jednu složku  výše   
                    final_string = parse_url.scheme + "://" + parse_url.netloc + way_second + "/" + edited_url
                    found_urls_css.append(final_string)
                    print("--nalezen: " + final_string)
                else: #neobsahuje ani . ani /, zůstává se ve stejné složce jako css soubor
                    final_string = parse_url.scheme + "://" + parse_url.netloc + way + "/" + edited_url
                    found_urls_css.append(final_string)
                    print("--nalezen: " + final_string)
            except IndexError:
                continue
    
    with open("found_url_css.txt", "a") as f:
        for found_url in found_urls_css:
            print(found_url, file=f)

    cssutils.replaceUrls(sheet, split_path) #nahradí všechny výskyty url výstupem fce split_path
    with open (css_file, "wb") as f: #otevře daný css soubor
        f.write(sheet.cssText) #zapíše do něj aktualizované css
        print("Zapsáno")

def scrape_style_files(file_with_urls_found):
    """
    Projde odkazy na css/js styly v .txt dokumentech a vytáhne z nich css/js kód.
    Poté zavolá create_file_style, která vytvoří .css / .js souboru pro každý soubor
    a uloží do něj získaný kód stylu.
    Poté pro každý vytvořený css soubor zavolá parse_css.
    """

    file = open(file_with_urls_found, "r") #otevírá se css_files.txt, pak javascript_files.txt
    for line in file:
        print("Uložený odkaz: " + line) #pro kontrolu, potom smazat
        try:
            driver.get(line) 
            time.sleep(1)
        except WebDriverException:
            print("Odkaz: " + line + " je nedostupný/chybný.")
            continue

        html = driver.page_source 
        soup = BeautifulSoup(html, "html5lib")

        pre = soup.find("pre") #nalezení tagu pre
        
        try:
            scraped_code = pre.text #získání obsahu tagu pre, pokud není prázdný
        except AttributeError:
            print("Soubor: " + line + " je prázdný.")
            continue

        file_style = create_file_style(line) #line je předáno pro vytvoření správného názvu souboru
        save_to_file(file_style, scraped_code)
        close_file(file_style)

        file_name = split_path(line)
        
        if file_name.endswith(".css"):
            print("---Volá se parse_css---")
            parse_css(file_name, line) #volá se fce pro získání urls z uloženého css souboru
        #elif line.endswith(".js"):
        #   zde se bude volat fce pro získání url z uloženého JS souboru


def download_files(txt_file):
    """
    Projde odkazy na soubory v daném .txt a stáhne je.
    Voláno pro obrázky a fonty.
    """

    file = open(txt_file, "r")
    for line in file:
        file_name = split_path(line)
        print("Stahuje se soubor: " + file_name)
        
        #socket.setdefaulttimeout(10)

        try:
            #--------------------------
            #nastavení user-agent v headeru
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(line, file_name)
            #--------------------------

            #varianta bez nastavení user-agent v headeru
            #urllib.request.urlretrieve(line, file_name) #stáhne obrázek/font  
        except urllib.error.URLError:
            #print("URL error: " + line)
            continue
        except urllib.error.HTTPError:
            print("Soubor: " + line + " je prázdný.")
            continue
        except http.client.InvalidURL:
            print("Soubor: " + line + " má neplatnou URL.")
            continue
        except ValueError:
            print("Soubor: " + line + " má neplatnou URL.")
            continue
        except TimeoutError:
            print("Čas vypršel, nepodařilo se stáhnout.")
            continue


def find_styles_images(path_url):
    """
    Najde v html stránky (soup) všechny odkazy na css a js styly a obrázky, 
    uloží je do listů a tyto listy pak uloží do souborů javascript_files.txt,
    css_files.txt, images.txt.
    Zaroveň upraví jejich src a href v soup a uloží do index.html.

    :path_url: scheme + netloc + path = input uživatele; to, z čeho beru index.html
    """

    js_files = []
    cs_files = []
    img_files = []

    html = driver.page_source
    soup = BeautifulSoup(html, "html5lib")
    
    for script in soup.find_all("script"):
        if script.attrs.get("src"):
            url = script.attrs.get("src")
            contains_space = " " in url
            contains_scheme = url.startswith("http")
            edited_url = url.lstrip("./") #odstraní všechny ./ vyskytující se zleva
            if contains_space == True:
                print("Soubor obsahuje mezery, neplatná url, přeskakuji")
                continue
            if contains_scheme == True:
                js_files.append(url)
            else:
                try: 
                    parse_url = urlparse(path_url)
                    just_path = parse_url.path  #vrátí jen cestu (začíná /)
                    head_tail = os.path.split(just_path)  #rozdělí cestu na cestu a poslední složku
                    remove_one_folder =  head_tail[0]  #vrátí jen cestu bez poslední složky (ponechává / na začátku) (tzn. celkově odebrána jedna složka)
                
                    head_tail_second = os.path.split(remove_one_folder) #cestu rozdělí na cestu a poslední složku (nenechává / nakonci)
                    remove_two_folders = head_tail_second[0] #vrátí jen cestu bez poslední složky (tzn. celkově odebrány dvě složky)

                    head_tail_third = os.path.split(remove_two_folders) #cestu rozdělí na cestu a poslední složku (nenechává / nakonci)
                    remove_three_folders = head_tail_third[0] #vrátí jen cestu bez poslední složky (tzn. celkově odebrány třisložky)

                    if url.startswith("//"): #url umístěno hned za "https:"
                        final_string = parse_url.scheme + ":" + url
                        js_files.append(final_string)
                    elif url.startswith("/"): #je to v root složce 
                        final_string = parse_url.scheme + "://" + parse_url.netloc + "/" + edited_url
                        js_files.append(final_string)
                    elif url.startswith("./"): #zůstává se ve stejné složce 
                        final_string = parse_url.scheme + "://" + parse_url.netloc + parse_url.path + "/" + edited_url
                        js_files.append(final_string)
                    elif url.startswith("../../"): #jde se o dvě složky výše
                        final_string = parse_url.scheme + "://" + parse_url.netloc + remove_three_folders + "/" + edited_url
                        js_files.append(final_string)
                    elif url.startswith("../"): #jde se o jednu složku  výše
                        final_string = parse_url.scheme + "://" + parse_url.netloc + remove_two_folders + "/" + edited_url
                        js_files.append(final_string)
                    else: #neobsahuje ani . ani /, zůstává se ve stejné složce 
                        final_string = parse_url.scheme + "://" + parse_url.netloc + parse_url.path + "/" + edited_url
                        js_files.append(final_string)        
                except IndexError:
                    continue

            new_src = split_path(url)
            
            script['src'] = new_src #nahradí původní src jen názvem souboru
            html = str(soup) #uloží upravený kód do soup

    for item in soup.find_all("link"):
        if item.attrs.get("href"):
            url = item.attrs.get("href")
            contains_space = " " in url
            contains_scheme = url.startswith("http")
            edited_url = url.lstrip("./") #odstraní všechny ./ vyskytující se zleva
            if (url.__contains__("css")):
                print("bude uloženo:  " + url) #pro kontrolu, potom smazat
                if contains_space == True:
                    print("Soubor obsahuje mezery, neplatná url, přeskakuji")
                    continue
                if contains_scheme == True:
                    cs_files.append(url)
                else:    
                    try: 
                        parse_url = urlparse(path_url)
                        just_path = parse_url.path  #vrátí jen cestu (začíná /)
                        head_tail = os.path.split(just_path)  #rozdělí cestu na cestu a poslední složku
                        remove_one_folder =  head_tail[0]  #vrátí jen cestu bez poslední složky (ponechává / na začátku) (tzn. celkově odebrána jedna složka)
                
                        head_tail_second = os.path.split(remove_one_folder) #cestu rozdělí na cestu a poslední složku (nenechává / nakonci)
                        remove_two_folders = head_tail_second[0] #vrátí jen cestu bez poslední složky (tzn. celkově odebrány dvě složky)

                        head_tail_third = os.path.split(remove_two_folders) #cestu rozdělí na cestu a poslední složku (nenechává / nakonci)
                        remove_three_folders = head_tail_third[0] #vrátí jen cestu bez poslední složky (tzn. celkově odebrány třisložky)
                
                        if url.startswith("//"): #url umístěno hned za "https:"
                            final_string = parse_url.scheme + ":" + url
                            cs_files.append(final_string)
                        elif url.startswith("/"): #je to v root složce 
                            final_string = parse_url.scheme + "://" + parse_url.netloc + "/" + edited_url
                            cs_files.append(final_string)
                        elif url.startswith("./"): #zůstává se ve stejné složce 
                            final_string = parse_url.scheme + "://" + parse_url.netloc + parse_url.path + "/" + edited_url
                            cs_files.append(final_string)
                        elif url.startswith("../../"): #jde se o dvě složky výše
                            final_string = parse_url.scheme + "://" + parse_url.netloc + remove_three_folders + "/" + edited_url
                            cs_files.append(final_string)
                        elif url.startswith("../"): #jde se o jednu složku  výše
                            final_string = parse_url.scheme + "://" + parse_url.netloc + remove_two_folders + "/" + edited_url
                            cs_files.append(final_string)
                        else: #neobsahuje ani . ani /, zůstává se ve stejné složce 
                            final_string = parse_url.scheme + "://" + parse_url.netloc + parse_url.path + "/" + edited_url
                            cs_files.append(final_string)  
                    except IndexError:
                        continue
            elif url.endswith(".png") == True or url.endswith(".jpg") == True or url.endswith(".ico") == True:
                print("bude uloženo:  " + url) #pro kontrolu, potom smazat
                if contains_space == True:
                    print("Soubor obsahuje mezery, neplatná url, přeskakuji")
                    continue
                if contains_scheme == True:
                    img_files.append(url)
                else:   
                    try: 
                        parse_url = urlparse(path_url)
                        just_path = parse_url.path  #vrátí jen cestu (začíná /)
                        head_tail = os.path.split(just_path)  #rozdělí cestu na cestu a poslední složku
                        remove_one_folder =  head_tail[0]  #vrátí jen cestu bez poslední složky (ponechává / na začátku) (tzn. celkově odebrána jedna složka)
                
                        head_tail_second = os.path.split(remove_one_folder) #cestu rozdělí na cestu a poslední složku (nenechává / nakonci)
                        remove_two_folders = head_tail_second[0] #vrátí jen cestu bez poslední složky (tzn. celkově odebrány dvě složky)

                        head_tail_third = os.path.split(remove_two_folders) #cestu rozdělí na cestu a poslední složku (nenechává / nakonci)
                        remove_three_folders = head_tail_third[0] #vrátí jen cestu bez poslední složky (tzn. celkově odebrány třisložky)
                
                        if url.startswith("//"): #url umístěno hned za "https:"
                            final_string = parse_url.scheme + ":" + url
                            img_files.append(final_string)
                        elif url.startswith("/"): #je to v root složce 
                            final_string = parse_url.scheme + "://" + parse_url.netloc + "/" + edited_url
                            img_files.append(final_string)
                        elif url.startswith("./"): #zůstává se ve stejné složce 
                            final_string = parse_url.scheme + "://" + parse_url.netloc + parse_url.path + "/" + edited_url
                            img_files.append(final_string)
                        elif url.startswith("../../"): #jde se o dvě složky výše
                            final_string = parse_url.scheme + "://" + parse_url.netloc + remove_three_folders + "/" + edited_url
                            img_files.append(final_string)
                        elif url.startswith("../"): #jde se o jednu složku  výše
                            final_string = parse_url.scheme + "://" + parse_url.netloc + remove_two_folders + "/" + edited_url
                            img_files.append(final_string)
                        else: #neobsahuje ani . ani /, zůstává se ve stejné složce 
                            final_string = parse_url.scheme + "://" + parse_url.netloc + parse_url.path + "/" + edited_url
                            img_files.append(final_string)  
                    except IndexError:
                        continue
            else:
                print("Nebude uloženo:  " + url) #pro kontrolu, potom smazat

            new_src = split_path(url)

            item['href'] = new_src #nahradí původní href jen názvem souboru
            html = str(soup) #uloží upravený kód do soup

    for img in soup.find_all('img'): 
        try:
            url = img['src']
        except KeyError:
            print("EXCEPTION: Img tag neobsahuje src")
            continue
        contains_space = " " in url
        contains_scheme = url.startswith("http")
        edited_url = url.lstrip("./") #odstraní všechny ./ vyskytující se zleva
        if contains_space == True:
            print("Soubor obsahuje mezery, neplatná url, přeskakuji")
            continue
        if contains_scheme == True:
            img_files.append(url)
        else:  
            try:                 
                parse_url = urlparse(path_url)
                just_path = parse_url.path  #vrátí jen cestu (začíná /)
                head_tail = os.path.split(just_path)  #rozdělí cestu na cestu a poslední složku
                remove_one_folder =  head_tail[0]  #vrátí jen cestu bez poslední složky (ponechává / na začátku) (tzn. celkově odebrána jedna složka)
                
                head_tail_second = os.path.split(remove_one_folder) #cestu rozdělí na cestu a poslední složku (nenechává / nakonci)
                remove_two_folders = head_tail_second[0] #vrátí jen cestu bez poslední složky (tzn. celkově odebrány dvě složky)

                head_tail_third = os.path.split(remove_two_folders) #cestu rozdělí na cestu a poslední složku (nenechává / nakonci)
                remove_three_folders = head_tail_third[0] #vrátí jen cestu bez poslední složky (tzn. celkově odebrány třisložky)
                
                if url.startswith("//"): #url umístěno hned za "https:"
                    final_string = parse_url.scheme + ":" + url
                    img_files.append(final_string)
                elif url.startswith("/"): #je to v root složce 
                    final_string = parse_url.scheme + "://" + parse_url.netloc + "/" + edited_url
                    img_files.append(final_string)
                elif url.startswith("./"): #zůstává se ve stejné složce 
                    final_string = parse_url.scheme + "://" + parse_url.netloc + parse_url.path + "/" + edited_url
                    img_files.append(final_string)
                elif url.startswith("../../"): #jde se o dvě složky výše
                    final_string = parse_url.scheme + "://" + parse_url.netloc + remove_three_folders + "/" + edited_url
                    img_files.append(final_string)
                elif url.startswith("../"): #jde se o jednu složku  výše
                    final_string = parse_url.scheme + "://" + parse_url.netloc + remove_two_folders + "/" + edited_url
                    img_files.append(final_string)
                else: #neobsahuje ani . ani /, zůstává se ve stejné složce 
                    final_string = parse_url.scheme + "://" + parse_url.netloc + parse_url.path + "/" + edited_url
                    img_files.append(final_string) 
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
    with open("javascript_files.txt", "a") as f:
        for js_file in js_files:
            print(js_file, file=f)

    with open("css_files.txt", "a") as f:
        for css_file in cs_files:
            print(css_file, file=f)

    with open("images.txt", "a") as f:
        for img_file in img_files:
            print(img_file, file=f) 

def add_cookie():
    name = input("Vložte cookie name: ")
    value = input("Vložte cookie value: ")

    driver.add_cookie({"name" : name, "value" : value}) # formát je: driver.add_cookie({"name" : "_pk_ref.50.6f9c", "value" : "%5B%22%22%2C%22%22%2C1680182860%2C%22https%3A%2F%2Fwww.mojeid.cz%2F%22%5D"})

    print("Vložit další cookies? y/n\n")
    possible_choice = ["y", "n"]
    choice = input(">> ")
    
    while not choice in possible_choice:
        print("Neznámý příkaz, zadejte znovu.")
        choice = input(">> ")
    if choice == "y":
        add_cookie()
    elif choice == "n":
        print("Cookies byly uloženy.")

def print_menu():
    clear_cli()
    print("     -- MENU --\n")
    print("Zvolte jednu z možností:\n")
    print("1) Klonovat stránku")
    print("2) Klonovat stránku s vložením cookies")
    print("3) Konec\n")

def quit_program():
    print("Ukončuji se.")
    time.sleep(2.0)
    quit()

def main():
    print_menu()
    choice = input(">> ")

    if choice == "1":
        clear_cli()
        print("1) Klonovat stránku")
        print("-" * 30 + "\n")
        URL_input = input("Vložte URL: ")
        if " " in URL_input:
            print("URL je neplatná, opakujte akci.")
            time.sleep(2.0)
            main()
        try:
            driver.get(URL_input)
        except WebDriverException:
            print("URL je nedostupná/chybná. Opakujte akci")
            time.sleep(3.0)
            main()
    elif choice == "2":
        clear_cli()
        print("1) Klonovat stránku s vložením cookies\n")
        print("-" * 30 + "\n")
        URL_input = input("Vložte URL: ")
        if " " in URL_input:
            print("URL je neplatná, opakujte akci.")
            time.sleep(2.0)
            main()
        try:
            driver.get(URL_input)
        except WebDriverException:
            print("URL je nedostupná/chybná. Opakujte akci")
            time.sleep(3.0)
            main()
        add_cookie()  
        driver.refresh() 
    elif choice == "3":
        quit_program()
    else:
        print("Neznámý příkaz, zadejte znovu.")    
        time.sleep(2.0)
        main()

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

    find_styles_images(path_url)
    
    print("scraping css") #pro kontrolu, potom smazat
    scrape_style_files("css_files.txt")
    scrape_style_files("javascript_files.txt")

    download_files("images.txt")
    
    try:
        download_files("found_url_css.txt")
    except FileNotFoundError:
        print("Nebyl nalezen soubor: found_url_css.text")

    print("Ukončeno")
    time.sleep(2)
    quit()


main()