# 04_opening_and_card_traceability — Ouverture des produits et traçabilité des cartes

## Objectif

Implémenter l’ouverture d’un produit ouvrable, la traçabilité des cartes révélées et les événements associés.

## Branche de développement

`feature/opening-card-traceability`

## Dépendances

- 01_product_reference_model
- 03_parent_child_relationships

## Périmètre

- Créer `ProductOpeningEvent` et les objets associés à l’ouverture.
- Implémenter un cas d’usage pour marquer un produit comme ouvert.
- Permettre d’associer des cartes révélées à un produit ouvert via des identifiants externes ou abstractions adaptées.
- Tracer les scans de cartes réalisés lors de l’ouverture.
- Empêcher l’ouverture invalide d’un produit déjà ouvert ou non ouvrable.

## Hors périmètre

- Possession globale des cartes par l’usager.
- Analyse probabiliste détaillée.

## Livrables attendus

- Cas d’usage d’ouverture.
- Événements et historiques liés aux ouvertures.
- Tests unitaires couvrant état nominal et erreurs.

## Critères d'acceptation

- Un produit ouvrable peut être marqué ouvert une seule fois selon les règles définies.
- Les cartes révélées sont rattachées à la provenance produit.
- Tous les scénarios invalides sont couverts par tests et exceptions.

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
