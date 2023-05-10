# Aplikace na klonování stránek

Aplikace byla vytvořena v rámci praktické části diplomové práce na téma Aplikace na klonování stránek pro bezpečnostní testování. 

## Požadavky

* Nejnovější verze prohlížeče Google Chrome,
* moduly a balíčky uvedené v souboru requirements.txt:

```
bs4
beautifulsoup4
selenium
html5lib
requests
urllib3
webdriver-manager
pathspec
cssutils
```

## Spuštění

Aplikace se spouští z příkazové řádky ze složky obsahující hlavní soubor příkazem:

```
main.py
```

Po spuštění se zobrazí menu s možnostmi klonovat stránku přímo a nebo s vložením cookies.

### Klonovat stránku

Pro klonování stránky zvolte možnost 1) a zadejte URL adresu stránky, kterou si přejete kopírovat. 
Například pro stránku https://www.vut.cz/login bude vstup jen:

```
https://www.vut.cz/login
```
### Klonovat stránku s vložením cookies

Pro klonování stránky s vložením cookies zvolte možnost 2), zadejte URL adresu požadované stránky stejně jako v možnosti 1) a poté zadejte hodnoty cookie name a cookie value.
Příklad pro vložení cookie "vut_ack" s hodnotou "l6vcr7kaXJWMixnieoFqgIofh4Iqmi":

```
Vložte cookie name: vut_ack
Vložte cookie value: l6vcr7kaXJWMixnieoFqgIofh4Iqmi
```

Lze vložit libovolné množství cookies.


