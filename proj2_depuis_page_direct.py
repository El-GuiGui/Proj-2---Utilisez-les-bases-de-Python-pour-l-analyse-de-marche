
#importation des librairies de request, beautifulsoup et csv
import requests
from bs4 import BeautifulSoup
import csv

# lien de la page du livre à scrapper
url = "http://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html"
reponse = requests.get(url)
page = reponse.content

# transforme la page html via BeautifulSoup (parse)
soup = BeautifulSoup(page, "html.parser")



# récupération de tous les éléments
elements = soup.find_all("div", class_="page_inner")

resultats = []

for element in elements:
    titre = element.find("div", class_="h1")
    description = element.find_all('p').gettext
    prix = element.find("p", class_="price_color")
    disponibilite = element.find("p", class_="instock availability")
    donnee = [titre.string, description.string, prix.string, disponibilite.string]
    resultats.append(donnee)







# création du fichier data.csv
en_tete = ["titre", "description", "prix", "disponibilite"]
with open("data.csv", "w", newline="", encoding='utf-8') as fichier_csv:
    writer = csv.writer(fichier_csv, delimiter=',')  # Utilisation de la virgule comme délimiteur
    writer.writerow(en_tete)

    for donnee in resultats:
        writer.writerow(donnee)




