# 05_history_and_event_log — Historique métier et journalisation événementielle interne

## Objectif

Centraliser la traçabilité métier via un historique cohérent des événements produits.

## Branche de développement

`feature/history-event-log`

## Dépendances

- 02_registration_and_scan_workflow
- 03_parent_child_relationships
- 04_opening_and_card_traceability

## Périmètre

- Définir un modèle d’événement métier commun si nécessaire.
- Conserver les événements : enregistrement, scan, qualification, rattachement, ouverture, association de cartes.
- Ajouter des services de consultation simple de l’historique d’un produit.
- Garantir l’ordre logique et la cohérence minimale des événements.

## Hors périmètre

- Bus événementiel externe.
- Persistance distribuée ou audit avancé.

## Livrables attendus

- Modèle d’historique.
- Services de lecture de l’historique.
- Tests unitaires d’ordonnancement et cohérence.

## Critères d'acceptation

- Chaque action métier importante produit une trace consultable.
- L’historique d’un produit est récupérable de manière fiable.
- Les événements incohérents sont empêchés ou rejetés.

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
