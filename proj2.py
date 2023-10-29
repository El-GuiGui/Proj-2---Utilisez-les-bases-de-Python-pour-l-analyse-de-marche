
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
elements = soup.find_all("li", class_="gem-c-document-list__item")

resultats = []

for element in elements:
    titre = element.find("a", class_="govuk-link")
    description = element.find("p", class_="gem-c-document-list__item-description")
    donnee = (titre.string, description.string)
    resultats.append(donnee)




# création du fichier data.csv
en_tete = ["titre", "description", "prix", "disponibilite"]
with open("data.csv", "w", newline="") as fichier_csv:
    writer = csv.writer(fichier_csv, delimiter=",")
    writer.writerow(en_tete)
    # zip permet d'itérer sur deux listes à la fois
    for donnee in resultats:
        writer.writerow(donnee)
