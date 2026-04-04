# 02_registration_and_scan_workflow — Workflow d’enregistrement et de scan des produits

## Objectif

Mettre en place les cas d’usage permettant d’enregistrer un produit scanné, de distinguer un produit connu d’un produit inconnu et de qualifier un produit minimalement.

## Branche de développement

`feature/registration-scan-workflow`

## Dépendances

- 00_project_bootstrap
- 01_product_reference_model

## Périmètre

- Créer les ports nécessaires à la résolution d’un code-barres et au stockage des produits.
- Implémenter les cas d’usage d’enregistrement par scan commercial ou interne.
- Gérer les cas `produit connu`, `produit inconnu`, `produit à qualifier`.
- Permettre l’association initiale à un set et l’enregistrement d’un numéro de série si disponible.
- Émettre ou historiser les événements d’enregistrement et de scan.

## Hors périmètre

- Rattachement parent/enfant complexe.
- Ouverture et cartes révélées.

## Livrables attendus

- Ports de dépôt et de résolution de scan.
- Services / use cases d’enregistrement.
- Exceptions de workflow de scan.
- Tests unitaires avec doubles de test.

## Critères d'acceptation

- Un scan permet de créer ou retrouver un produit.
- Les cas ambigus ou invalides lèvent des exceptions métier explicites.
- Les tests couvrent toutes les branches métier principales.

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
