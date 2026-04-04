# 08_release_readiness — Durcissement qualité, documentation et préparation release

## Objectif

Finaliser la librairie pour une première version stable en consolidant la documentation, la couverture, la qualité et la préparation de release.

## Branche de développement

`feature/release-readiness`

## Dépendances

- 00_project_bootstrap
- 01_product_reference_model
- 02_registration_and_scan_workflow
- 03_parent_child_relationships
- 04_opening_and_card_traceability
- 05_history_and_event_log
- 06_integration_ports_collection_statistics
- 07_query_services_and_public_api

## Périmètre

- Compléter le `README.md` avec installation, usage et exemples.
- Mettre à jour `CHANGELOG.md` et `docs/dev_diary.md`.
- Vérifier et compléter la couverture de tests pour atteindre le seuil global.
- Vérifier packaging, métadonnées, licences et version initiale.
- Nettoyer l’API publique et les docstrings finales.

## Hors périmètre

- Nouvelles fonctionnalités métier majeures hors cahier des charges.

## Livrables attendus

- Projet prêt pour une release technique.
- Documentation consolidée.
- Rapports qualité et couverture propres.

## Critères d'acceptation

- Tous les outils qualité passent.
- La couverture minimale est atteinte.
- Le package est installable et documenté.
- La release candidate est cohérente avec le cahier des charges.

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
