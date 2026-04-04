# 06_integration_ports_collection_statistics — Ports d’intégration collection et statistiques

## Objectif

Préparer l’intégration propre avec la collection et les statistiques au moyen de ports et DTO métier, sans couplage direct aux autres briques.

## Branche de développement

`feature/integration-ports-collection-statistics`

## Dépendances

- 04_opening_and_card_traceability
- 05_history_and_event_log

## Périmètre

- Créer des interfaces/ports sortants vers la collection et les statistiques.
- Définir des objets d’échange minimaux pour provenance produit et événements d’ouverture.
- Faire déclencher les publications adéquates depuis les cas d’usage concernés.
- Isoler toute dépendance à des implémentations externes derrière des Protocols ou interfaces.

## Hors périmètre

- Implémentations concrètes des briques externes.
- Transport HTTP, messaging ou API.

## Livrables attendus

- Ports d’intégration stables.
- DTO ou messages métier.
- Tests unitaires avec mocks/fakes.

## Critères d'acceptation

- La librairie reste indépendante des autres briques tout en exposant ses besoins d’intégration.
- Les cas d’usage appellent les ports attendus dans les bons scénarios.

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
