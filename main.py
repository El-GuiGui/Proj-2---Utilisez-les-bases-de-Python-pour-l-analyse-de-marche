# Import des bibliothèques nécessaires
import requests
from bs4 import BeautifulSoup
import csv
import os
import re
from urllib.parse import urljoin


# Fonction pour récupérer le contenu d'une page web
def extraction(url):
    # Envoi d'une requête HTTP et récupération de la réponse
    reponse = requests.get(url)
    # Définition de l'encodage de la réponse
    reponse.encoding = "utf-8"
    # Création d'un objet BeautifulSoup pour analyser le contenu HTML
    soup = BeautifulSoup(reponse.text, features="html.parser")
    return soup


# Fonction pour extraire les URLs des différentes catégories de livres
def extraire_urls_categories(url_base):
    # Analyse de la page principale pour trouver les catégories
    soup = extraction(url_base)
    categories = soup.find("div", class_="side_categories").find_all("a")
    urls_categories = {}
    for cat in categories:
        nom_categorie = cat.text.strip()
        # Exclure la catégorie "Books"
        if nom_categorie != "Books":
            urls_categories[nom_categorie] = urljoin(url_base, cat["href"])
    return urls_categories


# Fonction pour extraire les URLs des livres dans une catégorie donnée
def extraire_urls_livres(url_categorie):
    # Initialisation d'une liste pour stocker les URLs des livres
    urls_livres = []
    base_url = "https://books.toscrape.com/catalogue/"
    while True:
        # Récupération et analyse de la page de la catégorie
        soup = extraction(url_categorie)
        livres = soup.find_all("article", class_="product_pod")
        # Extraction des URLs de chaque livre dans la catégorie
        for livre in livres:
            lien = livre.find("h3").find("a")["href"]
            lien_complet = base_url + lien.replace("../", "")
            urls_livres.append(lien_complet)

        # Gestion de la pagination pour passer à la page suivante
        next_button = soup.find("li", class_="next")
        if next_button:
            next_page = next_button.find("a")["href"]
            url_categorie = urljoin(url_categorie, next_page)
        else:
            break

    return urls_livres


# Fonction pour transformer les données d'un livre extraites de la page web
def transformation_tdp(soup, url_livre):
    # Vérification et extraction des informations principales du livre
    product_main = soup.find("div", {"class": "col-sm-6 product_main"})
    if not product_main:
        return [None] * 10

    # Extraction et transformation des données de base (titre, description, prix)
    title = (
        transformation_texte(product_main.find("h1").text)
        if product_main.find("h1")
        else ""
    )
    description = (
        transformation_texte(
            soup.find("article", {"class": "product_page"})
            .find("p", {"class": ""})
            .text
        )
        if soup.find("article", {"class": "product_page"}).find("p", {"class": ""})
        else ""
    )
    price = (
        transformation_texte(product_main.find("p", {"class": "price_color"}).text)
        if product_main.find("p", {"class": "price_color"})
        else ""
    )

    # Extraction de la disponibilité et transformation
    disponibilite_origin = (
        product_main.find("p", {"class": "instock availability"}).text
        if product_main.find("p", {"class": "instock availability"})
        else ""
    )
    disponibilite = transformation_disponibilite(disponibilite_origin)

    # Extraction et nettoyage des données depuis le tableau
    tab = {}
    table = soup.find("table", {"class": "table table-striped"})
    if table:
        rows = table.select("tr")
        for row in rows:
            header = row.find("th").text if row.find("th") else None
            value = row.find("td").text if row.find("td") else None
            if header and value:
                cleaned_value = transformation_texte(value)
                tab[header] = cleaned_value

    # Récupération de l'URL canonique de la page du produit
    canonical_link = soup.find("link", {"rel": "canonical"})
    product_page_url = canonical_link["href"] if canonical_link else url_livre

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


# Fonction pour nettoyer les textes extraits
def transformation_texte(texte):
    # Suppression des espaces en début et fin et remplacement des espaces multiples
    texte = re.sub(r"^\s+|\s+$", "", texte)
    texte = re.sub(r"\s+", " ", texte)
    # Filtrage des caractères pour ne conserver que ceux autorisés
    texte = re.sub(r'[^\w\s£€$.,;:!\'"()?-]', "", texte)
    return texte


# Fonction pour transformer la disponibilité en un format numérique
def transformation_disponibilite(texte):
    texte = texte.strip()
    match = re.search(r"\d+", texte)
    return match.group() if match else "0"


# Fonction pour sauvegarder les données extraites dans un fichier CSV et télécharger les images
def sauvegarde(donnee, soup, en_tete, nom_categorie, folder_name="images"):
    # Création du dossier pour les fichiers CSV si nécessaire
    dossier_csv = "Books Categories"
    os.makedirs(dossier_csv, exist_ok=True)
    nom_fichier_csv = os.path.join(dossier_csv, f"{nom_categorie}.csv")

    # Sauvegarde des données extraites dans le fichier CSV
    mode = "a" if os.path.exists(nom_fichier_csv) else "w"
    with open(nom_fichier_csv, mode, newline="", encoding="utf-8") as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=",")
        if mode == "w":
            writer.writerow(en_tete)
        writer.writerow(donnee)

    # Téléchargement et sauvegarde de l'image du livre
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


# Fonction principale pour traiter et sauvegarder les données d'un livre
def traiter_et_sauvegarder(url_livre, nom_categorie):
    soup = extraction(url_livre)
    donnee = transformation_tdp(soup, url_livre)
    sauvegarde(donnee, soup, en_tete, nom_categorie, "images")


# Définition des en-têtes pour les fichiers CSV
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

# Exécution du script : extraction et traitement des catégories et des livres
url_base = "https://books.toscrape.com/index.html"
categories_urls = extraire_urls_categories(url_base)

# Parcours de chaque catégorie pour extraire et sauvegarder les informations des livres
for nom_categorie, url_categorie in categories_urls.items():
    urls_livres = extraire_urls_livres(url_categorie)
    for url_livre in urls_livres:
        traiter_et_sauvegarder(url_livre, nom_categorie)
