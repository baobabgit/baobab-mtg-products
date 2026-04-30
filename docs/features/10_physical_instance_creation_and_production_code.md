# 10_physical_instance_creation_and_production_code — Création d’instances physiques et code de production non unique

## Objectif

Ajouter un workflow explicite de création d’instance physique permettant d’enregistrer plusieurs exemplaires d’une même référence, y compris lorsque ces exemplaires partagent le même code de production.

## Branche de développement

`feature/physical-instance-production-code`

## Dépendances

- 09_product_reference_instance_split
- 02_registration_and_scan_workflow
- 05_history_and_event_log

## Périmètre

- Créer `CreateProductInstanceUseCase`.
- Créer ou renommer le value object métier `ProductionCode` ou `ProductProductionCode`.
- Documenter la compatibilité ou la migration depuis `SerialNumber` si ce nom existe encore dans l’API publique.
- Permettre l’association d’un code de production optionnel et non unique.
- Permettre l’association optionnelle d’un code-barres interne unique.
- Ajouter, si nécessaire, `AssignProductionCodeToProductInstanceUseCase` pour une saisie différée.
- Ajouter les événements métier : instance créée, code de production associé.
- Adapter les ports de dépôt pour rechercher par `internal_id`, `reference_id`, `production_code` et `internal_barcode`.
- Ajouter les tests de non-unicité.

## Hors périmètre

- Résolution d’un code-barres commercial vers une référence.
- Déconditionnement de contenant.
- Ouverture de booster.
- Implémentation concrète SQL.

## Règles métier

- `production_code` est optionnel.
- `production_code` n’est jamais unique.
- Plusieurs instances du même type peuvent partager le même `production_code`.
- Plusieurs instances de la même référence peuvent partager le même `production_code`.
- `internal_barcode`, lorsqu’il existe, doit être unique.
- `internal_id` reste la seule identité forte obligatoire de l’instance physique.

## Livrables attendus

- `CreateProductInstanceUseCase`.
- `ProductionCode` ou documentation de migration depuis `SerialNumber`.
- Port de dépôt adapté aux recherches nécessaires.
- Événements métier dédiés.
- Tests unitaires et tests de workflow.
- Documentation d’exemple.

## Critères d'acceptation

- Deux displays issues de la même référence peuvent être créées comme deux instances distinctes.
- Deux instances peuvent avoir le même code de production.
- Une recherche par code de production retourne une collection ou séquence de résultats, jamais un unique produit supposé.
- Une tentative de duplication de code-barres interne est rejetée explicitement.
- Les événements de création et d’association du code de production sont traçables.
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
- couverture minimale attendue : `95%` ;
- journal de développement dans `docs/dev_diary.md` ;
- évolution du `README.md` et du `CHANGELOG.md` si nécessaire ;
- commits au format Conventional Commits ;
- travail sur une branche dédiée ;
- à la fin : si tests, qualité et contraintes sont OK, ouvrir une Pull Request puis la merger sur `main`.
