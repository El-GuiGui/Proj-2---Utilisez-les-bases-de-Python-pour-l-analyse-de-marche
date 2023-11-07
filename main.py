#importation des librairies
import requests
from bs4 import BeautifulSoup
import csv


# lien de la page du livre à scrapper
url = "https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"
reponse = requests.get(url)
page = reponse.content
print(reponse)


titre = BeautifulSoup(reponse.text, features="html.parser").find("div", {"class": "col-sm-6 product_main"}).find('h1').text
description = BeautifulSoup(reponse.text, features="html.parser").find("article", {"class": "product_page"}).find("p", {"class": ""}).text
price = BeautifulSoup(reponse.text, features="html.parser").find("div", {"class": "col-sm-6 product_main"}).find("p", {"class": "price_color"}).text
disponibilite = BeautifulSoup(reponse.text, features="html.parser").find("div", {"class": "col-sm-6 product_main"}).find("p", {"class": "instock availability"}).text
table = BeautifulSoup(reponse.text, features="html.parser").find("table", {"class": "table table-striped"})

#recherche url
canonical_link = BeautifulSoup(reponse.text, features="html.parser").find('link', {'rel': 'canonical'})
product_page_url = canonical_link['href'] if canonical_link else url  


# Extraire les informations du tableau
tab = {}
rows = table.select('tr')
for row in rows:
    header = row.find('th').text if row.find('th') else None
    value = row.find('td').text if row.find('td') else None
    if header and value:
        tab[header] = value.strip()

# Création de la liste des données
donnee = [
    titre, 
    description, 
    price, 
    disponibilite, 
    tab.get("UPC", ""), 
    tab.get("Product Type", ""), 
    tab.get("Price (excl. tax)", ""), 
    tab.get("Price (incl. tax)", ""), 
    tab.get("Number of reviews", ""),
    product_page_url
]

resultats = [donnee]





#création du fichier data.csv
en_tete = ["titre", "description", "prix", "disponibilite", "upc", "product_type", "price_excl_tax", "price_incl_tax", "reviews","url"]
with open("data.csv", "w", newline="", encoding='utf-8') as fichier_csv:
    writer = csv.writer(fichier_csv, delimiter=',')  # Utilisation de la virgule comme délimiteur
    writer.writerow(en_tete)
    for donnee in resultats:
        writer.writerow(donnee)

