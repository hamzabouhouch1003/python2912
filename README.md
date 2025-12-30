# Library Project – Gestion de Bibliothèque avec Django

> Projet de formation Python avancé : application de gestion de bibliothèque (livres, auteurs, catégories, emprunts) basée sur l’architecture MVT.

---

## 1. Présentation du projet

Ce projet est une application web de gestion de bibliothèque (library) avec Django.  
Elle permet notamment :

- De gérer un catalogue de livres (books) (métadonnées complètes, stock, catégories, etc.).
- De gérer des auteurs (authors) et de lier leurs oeuvres à leurs noms.
- De suivre des emprunts (loans) de livres par les usagers (dates, statut, retards…).
- D’administrer tout cela via l’interface admin de Django, et plus tard via une interface publique.

Le projet suit les phases décrites dans un sujet de TP :

- Phase 1 : Modélisation (Author, Book, Loan, Category).
- Phase 2 : Configuration du projet Django.
- Phase 3 : Interface d’administration.
- Phase 4 : Routage (URLs).
- Phase 5+ : Vues, templates, formulaires, signaux, statistiques, etc.

Le projet suit la structuration en phases du sujet de TP (Phase 1 à 10), même si seules certaines phases sont entièrement implémentées.

## 2. Stack technique

- Langage : Python 3.13
- Framework web : Django (version compatible 3.13, par ex. Django 5.1+)
- Base de données : SQLite (par défaut, simple pour le développement)
- Front-end : Templates Django + Bootstrap minimal (CDN)
- Environnement : Virtualenv (`.venv`) activé par `python -m venv .venv` (Sous windows .venv\Scripts\Activate.ps1)

---

## 3. Installation et mise en place

### 3.1 Récupération du projet et environnement virtuel

1. Cloner le dépôt du projet.
2. Se placer dans le dossier du projet.
3. Créer un environnement virtuel Python (`.venv`) à la racine.
4. Activer cet environnement pour toutes les commandes Python et Django.
5. Installer les dépendances à partir du fichier `requirements.txt`.

### 3.2 Configuration générale

Le projet Django se trouve dans le dossier `core`, et l’application principale qui contient la logique métier se trouve dans le dossier `books`.

La configuration générale :

- Enregistre l’application `books` dans la liste des applications installées.
- Configure la langue de l’application en français (`fr-fr`) et le fuseau horaire sur `Europe/Paris`.
- Définit les chemins vers les fichiers statiques (`static`) et les fichiers médias (`media`), à partir de `BASE_DIR`, avec des dossiers créés à la racine du projet.

Un fichier optionnel `settings_local.py` a été ajouté à `core` pour surcharger certains paramètres localement (par exemple `DEBUG`) sans modifier le fichier `settings.py` principal.

### 3.3 Migrations et base de données

Les modèles de notre application sont migrés vers la base SQLite via les commandes intégrées à Django : 

- Génération des migrations à partir des modèles définis
- Application des migrations pour la créations des tables dans la BDD.

En développemet, il est possible de régénérer la base et les migrations (en supprimant les fichiers), si les modèles reçoivent des changements importants et qu'aucune des données n'est importante à conserver.

## 4. Structure du projet

Le projet est organisé selon la logique suivante :

- Core 
   Il contient la configuration globale du projet :
   - 'settings.py' : paramètres généraux, apps installées, base de données, langue, timezone, configuration statique/média...
   - 'urls.py' : routage racine du projet, inclusion des URLs de l'application 'books' et de l'admin.
   - 'wsgi.py' / 'asgi.py' : points d'entrée pour le déploiement.

- Books 
   C'est l'application principale ("Library" dans le sujet de TP). Elle contient :
   - 'models.py' : modèles Author, Book, Category, Loan.
   - 'admin.py' : configuration de l'interface administrateur pour ces modèles.
   - 'views.py' : vues basées sur des classes (ListView, DetailView) pour les listes et détails.
   - 'urls.py' : routage spécifique à l'application (book, author, loan)
   - 'forms.py' : formulaires Django pour les phases de formulaires (loan, recherche, contact)
   - 'templates/books/' : templates propres à l'appli

- Templates
   Dossier des templates globaux : 
   - 'base.html' : template de base avec navigation, header, etc.
   - sous-dossier 'books/' : templates de liste et de détail pour les book, author, et loan.

- Static
   Dossier contenant les fichiers statiques (CSS, JS, images partagées) référencé dans la configuration.

- Media 
   Dossier contenant les fichiers uploadés par l'application (images de couverture de livres, photos d'auteurs), utilisé par les champs 'ImageField'.

- DB.SQLite3
   Base de données pour notre environnement de développement.

- manage.py
   Outil contenant toutes les commandes Django (migrations, serveur de dév, shell, etc...)

## 5. Modélisation (Phase 1) 
   La modélisation de la librairie est concentrée dans l'app 'books' avec 4 modèles principaux.

### 5.1 Modèle Author
   Le modèle Author représente un auteur avec les informations suivantes :
      - Prénom et nom de famille, avec contrainte d'unicité sur la combinaison prénom + nom pour éviter les doublons.
      - Date de naissance, et si existante, date de décès
      - Nationalité
      - Biographie texte
      - Site web ou URL de référence
      - Photo de l'auteur via un champ d'upload d'image stockée dans un sous-dossier des médias.

      La méthode '__str__' retourne le nom complet de l'auteur. La relation inverse vers les livres est définie dans le modèle Book au travers d'un 'related_name' explicite.

### 5.2 Modèle Category
   Le modèle Category représente une catégorie littéraire :

   - Un nom unique pour identifier la catégorie
   - Une description texte
   - Une image représentative stockée via média

   Un 'ordering' par défaut est défini pour trier les catégories par leur nom dans l'interface et dans les requêtes.

### 5.3 Modèle Book
   Le modèle Book représente un livre du catalogue : 

   - Titre
   - Code ISBN (unique) au format ISBN-13
   - Année de publication avec validation entre 1450 et année courante.
   - Lien vers un auteur via une clé étrangère, avec une relation inverse nommée (par exemple 'books' côté auteur), et une politique de suppression emêchant la suppression d'un auteur si des livres lui sont encore associés.
   - Lien vers une catégorie via la clé étrangère (catégorie optionnelle)
   - Informations du stock : nombre total possédé, nombre disponibles.
   - Description texte de l'ouvrage
   - Langue de publication
   - Nombre de pages
   - Maison d'édition
   - Image de couverture (upload dans un sous-dossier dédié)
   - Date d'ajout au catalogue (automatique à la création)

   Des contraintes métier sont intégrées, par exemple une validation qui interdit d'avoir plus d'exemplaires disponibles que totaux. La méthode '__str__' retourne le titre du livre.

### 5.4 Modèle Loan
   Le modèle Loan représente un emprunt d'un livre par un usager : 

   - Lien vers un livre via un clé étrangère, avec une relation inverse nommée (pour récupérer les emprunts d'un livre)
   - Nom complet de l'emprunteur 
   - Numéro de carte de bibliothèque
   - Date et heure de l'emprunt
   - Date limite de retour (durée standard)
   - Date et heure de retour effectif (optionnelle tant que le livre n'est pas rendu)
   - Statut de l'emprunt, géré via un champ à vhoix (par exemple : en attente, en cours, retourné, en retard)
   - Commentaires éventuels du bibliothécaire 

   Le modèle expose également des propriétés et méthodes utilitaires (par exemple pour déterminer si un loan est overdue (en retard)).
   Les règles métier plus poussées (Limite de 5 loans, calcul automatique de la date limite de rendu, pénalités, gestion du stock via signaux) sont prévues dans les phases ultérieures.

## 6. Interface d’administration (Phase 3)

   L'interface d'administration Django, est configurée dans l'application 'books'.

### 6.1 Enregistrement des modèles

   Chaque modèle (Author, Book, Category, Loan) est enregistré dans l'admin avec une configuration dédiée.

   - Pour Author :
      - Affichage en liste du nom complet, de la nationalité, et de la date de naissance.
      - Filtres latéraux par nationalité
      - Recherche par prénom et nom

   - Pour Category : 
      - Affichage du nom et de la description
      - Recherche par nom 

   - Pour Book : 
      - Affichage en liste du titre, de l'auteur, de l'ISBN, de la catégorie, et des informations du stock.
      - Filtres par catégorie, auteur et année de publication.
      - Barre de recherche sur le titre, l'ISBN et les noms d'auteurs.
      - Champ de date d'ajout en lecture seule.
      - Organisation des champs par sections logiques (informations générales, publication, stock, médias, métadonnées).
      - Inline pour visauliser les emprunts liés à un livre directement depuis la page de détail du livre.

   - Pour Loan : 
      - Affichage en liste du livre, de la personne faisant l'emprunt, des dates de début et limite, et le statut (par exemple : overdue)

### 6.2 Accès à l’admin

   L'accès à l'interface admin se fait après la création d'un superuser, puis en lançant le serveur de dév et en se rendant sur l'URL '.../admin/'. 
   Depuis cette dernière, il est possible d'ajouter, modifier, et supprimer auteurs, livres, catégories et emprunts. De plus, on peut tester rapidement la cohérence de la modélisation.

## 7. Routage (Phase 4)
   Le routage est divisé entre le fichier d'URLs du projet (Core) et celui de l'application (books)

### 7.1 URLs du projet (core)
   Le fichier d'URLs du projet ('core/urls.py') : 
      - Définit l'URL d'accès à l'interface admin Django
      - Inclut toutes les URLs de l'application 'books' à la racine du site, avec un namespace pour éviter les conflits
      - en mode dév, sert également les fichiers médias via une config spécifique

      De fait, la partie publique de l'application est gérée par l'URLconf de l'appli 'books', tandis que l'admin reste accessible sur un chemin dédié.

### 7.2 URLs de l’application (books)
   Le fichier 'books/urls.py' déclare les routes principales de l'application : 
      - Une route racine ('/') qui affiche la liste des livres.
      - Une route de détail pour un livre, basée sur son identifiant.
      - Une route pour la liste des auteurs et une route de détail pour un auteur.
      - Une route pour la liste des loans.

      Ces URLs sont nommées et organisées dans le namespace 'books', ce qui permet de les référencer dans les templates (par exemple 'books:book_list', 'books:book_detail', etc...)

      Les URLs complémentaires (recherche de livres, filtrage par catégorie ou auteur, historique par user, pages statiques de type "A propos" ou "Contact") peuvent êtres ajoutées dans ce même fichier lors de phases suivantes du TP.