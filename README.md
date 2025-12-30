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

### 3.1 Cloner le dépôt

```bash
git clone <URL_DU_REPO>
cd <nom_du_dossier>

