# Instructions pour projet : Utilisez les bases de Python pour l'analyse de marché

Ce projet est un script Python conçu pour extraire des données du site web "Books to Scrape". Il navigue à travers différentes catégories de livres, extrait les informations voulues pour chaque livre, et enregistre ces données dans des fichiers CSV.

## Configuration de l'Environnement

Pour exécuter le script, suivez les étapes ci-dessous pour configurer l'environnement.

### Prérequis

- Un éditeur : VisualStudio code, Spider, pycharm ...
- Python 3.x
- pip (LE gestionnaire de paquets pour Python)

### Création et Activation de l'Environnement Virtuel

1. **Créer un environnement virtuel** :

Ouvrez un terminal et naviguez jusqu'au dossier de votre projet. Exécutez la commande suivante pour créer un environnement virtuel :

   ```bash
   python -m venv env
```

2. **Activer l'environnement virtuel** :

Utilisez la commande appropriée selon votre système d'exploitation.

**Sur Windows** :

   ```bash
   env\Scripts\activate
```
**Sur MacOS/Linux** :

   ```bash
   source env/bin/activate
```


3. **Installation des Dépendances** :

Avec l'environnement virtuel activé, installez les dépendances requises :

   ```bash
   pip install -r requirements.txt
```
Assurez-vous que le fichier requirements.txt est présent dans le dossier du projet !

4. **Lancement du Script** :

Après l'installation des bibliothèques, lancez le script avec :

   ```bash
   python main.py
```

Patienter le temps que la totalité des livres soit scraper, on voit ensuite un dossier "images" avec les images des couvertures, et un dossier "Books Categories" avec les fichiers CSV correspondant à chaque catégorie !
