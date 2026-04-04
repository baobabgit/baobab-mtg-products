# 07_query_services_and_public_api — Services de consultation et API interne de la librairie

## Objectif

Structurer une API interne claire pour consulter les produits, leur provenance, leurs relations et leur historique sans exposer un CRUD bas niveau confus.

## Branche de développement

`feature/query-services-public-api`

## Dépendances

- 01_product_reference_model
- 03_parent_child_relationships
- 05_history_and_event_log
- 06_integration_ports_collection_statistics

## Périmètre

- Créer des services de consultation métier orientés cas d’usage.
- Permettre la récupération d’un produit, de ses relations et de son historique.
- Nettoyer l’API publique Python exposée par le package.
- Ajouter des exemples d’usage dans la documentation.

## Hors périmètre

- API HTTP ou interface utilisateur.
- Recherche avancée multi-critères persistée.

## Livrables attendus

- Services de lecture métier.
- Exports publics cohérents dans le package.
- Documentation d’usage.

## Critères d'acceptation

- L’utilisateur de la librairie dispose d’entrées claires pour utiliser le domaine.
- Les exports publics sont cohérents, documentés et stables.

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
