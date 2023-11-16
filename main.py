# Importation des librairies nécessaires
import requests
from bs4 import BeautifulSoup
import csv
import os
import re
from urllib.parse import urljoin


# Fonction pour extraire les données de la page web
def extraction(url):
    reponse = requests.get(url)
    # Définir l'encodage
    reponse.encoding = "utf-8"
    soup = BeautifulSoup(reponse.text, features="html.parser")
    return soup


# Fonction pour extraire les URLs des livres d'une catégorie
def extraire_urls_livres(url_categorie):
    urls_livres = []
    # URL de base avec /catalogue/
    base_url = "https://books.toscrape.com/catalogue/"

    while True:
        soup = extraction(url_categorie)
        livres = soup.find_all("article", class_="product_pod")
        for livre in livres:
            lien = livre.find("h3").find("a")["href"]
            lien_complet = base_url + lien.replace(
                "../", ""
            )  # Construction manuelle de l'URL
            urls_livres.append(lien_complet)

        next_button = soup.find("li", class_="next")
        if next_button:
            next_page = next_button.find("a")["href"]
            url_categorie = urljoin(
                "https://books.toscrape.com/catalogue/category/books/travel_2/",
                next_page,
            )
        else:
            break

    return urls_livres


# Fonction pour transformer les données extraites
def transformation_tdp(soup, url_livre):
    product_main = soup.find("div", {"class": "col-sm-6 product_main"})
    if not product_main:
        # Retourner une liste de None si la page n'est pas correcte
        return [None] * 10
    # Extraction et transformation du titre, de la description, du prix
    title = transformation_texte(product_main.find("h1").text)

    description = transformation_texte(
        soup.find("article", {"class": "product_page"}).find("p", {"class": ""}).text
    )
    price = transformation_texte(
        soup.find("div", {"class": "col-sm-6 product_main"})
        .find("p", {"class": "price_color"})
        .text
    )

    # Extraction et transformation de la disponibilité
    disponibilite_origin = (
        soup.find("div", {"class": "col-sm-6 product_main"})
        .find("p", {"class": "instock availability"})
        .text
    )
    disponibilite = transformation_disponibilite(disponibilite_origin)

    # Traitement des données du tableau
    tab = {}
    rows = soup.find("table", {"class": "table table-striped"}).select("tr")
    for row in rows:
        header = row.find("th").text if row.find("th") else None
        value = row.find("td").text if row.find("td") else None
        if header and value:
            cleaned_value = transformation_texte(value)
            tab[header] = cleaned_value

    # Extraction de l'URL du produit
    canonical_link = soup.find("link", {"rel": "canonical"})
    product_page_url = canonical_link["href"] if canonical_link else url_livre

    # Regroupement de toutes les données dans une liste
    return [
        title,
        description,
        price,
        disponibilite,
        tab.get("UPC", ""),
        tab.get("Product Type", ""),
        tab.get("Price (excl. tax)", ""),
        tab.get("Price (incl. tax)", ""),
        tab.get("Number of reviews", ""),
        product_page_url,
    ]


# Fonction pour nettoyer et transformer les textes
def transformation_texte(texte):
    # Enlever les espaces en début et en fin
    texte = re.sub(r"^\s+|\s+$", "", texte)
    # Remplacer les espaces multiples
    texte = re.sub(r"\s+", " ", texte)
    # Conserver certains symboles
    texte = re.sub(r'[^\w\s£€$.,;:!\'"()?-]', "", texte)
    return texte


# Fonction pour transformer la disponibilité en un nombre simple
def transformation_disponibilite(texte):
    # Nettoyage de base du texte
    texte = texte.strip()
    # Extraire le nombre
    match = re.search(r"\d+", texte)
    return match.group() if match else texte


# Fonction pour sauvegarder les données et les images
def sauvegarde(donnee, soup, en_tete, nom_fichier_csv="data.csv", folder_name="images"):
    mode = "a" if os.path.exists(nom_fichier_csv) else "w"
    with open(nom_fichier_csv, mode, newline="", encoding="utf-8") as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=",")
        if mode == "w":
            writer.writerow(en_tete)
        writer.writerow(donnee)

    image_element = soup.find("img")
    if image_element and image_element.get("src"):
        image_url = image_element["src"]
        base_url = "https://books.toscrape.com"
        full_image_url = base_url + image_url.lstrip(".")
        image_filename = full_image_url.split("/")[-1]
        os.makedirs(folder_name, exist_ok=True)
        if full_image_url:
            response = requests.get(full_image_url, stream=True)
            if response.status_code == 200:
                image_path = os.path.join(folder_name, image_filename)
                with open(image_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)


def traiter_et_sauvegarder(url_livre):
    soup = extraction(url_livre)
    donnee = transformation_tdp(soup, url_livre)
    sauvegarde(donnee, soup, en_tete, "data.csv", "images")


# Traiter et sauvegarder les données d'un livre
en_tete = [
    "titre",
    "description",
    "prix",
    "disponibilite",
    "upc",
    "product_type",
    "price_excl_tax",
    "price_incl_tax",
    "reviews",
    "url",
]


# URL de la catégorie Travel
url_categorie = (
    "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
)

# Extraction des URLs des livres de la catégorie Travel
urls_livres = extraire_urls_livres(url_categorie)

for url_livre in urls_livres:
    traiter_et_sauvegarder(url_livre)
