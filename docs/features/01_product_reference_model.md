# 01_product_reference_model — Modèle métier de référence des produits scellés

## Objectif

Implémenter le cœur du modèle métier : types de produits, statuts, identifiants, métadonnées de provenance et représentation d’une instance de produit.

## Branche de développement

`feature/product-reference-model`

## Dépendances

- 00_project_bootstrap

## Périmètre

- Créer `ProductType` pour les catégories minimales du périmètre.
- Créer `ProductStatus` pour les états métier cohérents du cycle de vie.
- Créer `ProductInstance` avec identifiant interne unique, set, numéros, codes-barres et parent éventuel.
- Ajouter les validations métier de base à la construction des objets.
- Prévoir des value objects ou wrappers si nécessaire pour clarifier les identifiants et codes.

## Hors périmètre

- Workflow de scan et d’enregistrement.
- Gestion détaillée des relations structurelles multiples.
- Ouverture de produit et rattachement des cartes.

## Livrables attendus

- Objets métier stables et typés.
- Exceptions dédiées au domaine produit.
- Jeu de tests unitaires complet du modèle.

## Critères d'acceptation

- Les objets couvrent le périmètre minimal du cahier des charges.
- Les invariants métier sont protégés par validation et exceptions spécifiques.
- Les tests couvrent les cas nominaux et d’erreur.

## Contraintes de développement à respecter

La feature doit impérativement respecter les règles suivantes :

- développement Python orienté objet ;
- une classe par fichier ;
- arborescence source sous `src/baobab_mtg_products/` ;
- arborescence des tests miroir sous `tests/` ;
- docstrings sur toutes les API publiques ;
- annotations de type complètes ;
- exceptions métier spécifiques héritant d'une exception racine du projet ;
- configuration centralisée dans `pyproject.toml` ;
- qualité obligatoire : `black`, `pylint`, `mypy`, `flake8`, `bandit` ;
- couverture minimale attendue : `90%` ;
- journal de développement dans `docs/dev_diary.md` ;
- évolution du `README.md` et du `CHANGELOG.md` si nécessaire ;
- commits au format Conventional Commits ;
- travail sur une branche dédiée ;
- à la fin : si tests, qualité et contraintes sont OK, ouvrir une Pull Request puis la merger sur `main`.
