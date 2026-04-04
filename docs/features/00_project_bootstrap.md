# 00_project_bootstrap — Bootstrap du projet et socle qualité

## Objectif

Mettre en place le squelette de la librairie, la configuration de packaging, l’outillage qualité, la hiérarchie d’exceptions racine et la structure documentaire minimale.

## Branche de développement

`feature/project-bootstrap`

## Dépendances

- Aucune.

## Périmètre

- Créer l’arborescence `src/baobab_mtg_products/`, `tests/`, `docs/`.
- Configurer `pyproject.toml` pour le packaging, pytest, coverage, black, pylint, mypy, flake8 et bandit.
- Créer l’exception racine `BaobabMtgProductsException` et les sous-packages de base.
- Créer les fichiers `README.md`, `CHANGELOG.md`, `docs/dev_diary.md` et la configuration de couverture dans `docs/tests/coverage`.
- Préparer les points d’extension pour les domaines, ports et cas d’usage.

## Hors périmètre

- Implémentation métier détaillée des produits, relations, scans ou ouvertures.
- Intégration concrète à des systèmes externes.

## Livrables attendus

- Projet installable en editable et en wheel.
- Outillage qualité exécutable sans erreur sur le squelette.
- Base d’exceptions projet.
- Documentation initiale.

## Critères d'acceptation

- Le projet s’installe avec `pip install -e .[dev]`.
- Tous les outils qualité passent.
- Les tests du squelette passent.
- La structure respecte strictement les contraintes.

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
