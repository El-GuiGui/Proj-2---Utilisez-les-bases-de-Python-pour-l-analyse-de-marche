
#importation des librairies de request, beautifulsoup et csv
import requests
from bs4 import BeautifulSoup
import csv

# lien de la page du livre à scrapper
url = "https://books.toscrape.com/catalogue/category/books_1/index.html"
reponse = requests.get(url)
page = reponse.content

# transforme la page html via BeautifulSoup (parse)
soup = BeautifulSoup(page, "html.parser")



# récupération de tous les éléments
elements = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

resultats = []

for element in elements:
    titre = element.find("h3", "a href=", "title=", class_="")
    prix = element.find("p", class_="price_color")
    donnee = [titre.string, prix.string]
    resultats.append(donnee)




# création du fichier data.csv
en_tete = ["titre", "prix",]
with open("data.csv", "w", newline="", encoding='utf-8') as fichier_csv:
    writer = csv.writer(fichier_csv, delimiter=',')  # Utilisation de la virgule comme délimiteur
    writer.writerow(en_tete)

    for donnee in resultats:
        writer.writerow(donnee)