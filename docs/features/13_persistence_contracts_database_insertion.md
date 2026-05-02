# 13_persistence_contracts_database_insertion — Contrats de persistance et insertion en base

## Objectif

Rendre explicite la capacité de la librairie à être branchée sur une base de données via des ports, sans imposer SQLite, PostgreSQL, SQLAlchemy, Django ORM ou MongoDB au cœur métier.

La librairie ne doit pas forcément fournir un adaptateur de production, mais elle doit définir des contrats suffisamment précis pour qu’une application puisse insérer et relire les références, instances, relations et traces métier.

## Branche de développement

`feature/persistence-contracts-database-insertion`

## Dépendances

- 09_product_reference_instance_split
- 10_physical_instance_creation_and_production_code
- 11_commercial_and_internal_scan_workflow_refactor
- 12_container_deconditioning_workflow
- 05_history_and_event_log
- 07_query_services_and_public_api

## Périmètre

- Définir ou adapter `ProductReferenceRepositoryPort`.
- Définir ou adapter `ProductInstanceRepositoryPort` ou un `ProductRepositoryPort` clairement séparé.
- Définir, si nécessaire, `ProductRelationshipRepositoryPort`.
- Définir les méthodes de recherche nécessaires : par identifiant interne, par référence, par code-barres commercial, par code de production, par parent.
- Garantir que les méthodes de recherche par code non unique retournent des séquences.
- Fournir des doubles mémoire conformes aux ports pour tests.
- Ajouter une note de schéma SQL indicatif dans la documentation.
- Ajouter des tests de contrat de port via implémentation mémoire.

## Hors périmètre

- Dépendance obligatoire à un moteur SQL.
- Migration Alembic, Django migration ou équivalent.
- API HTTP.
- Administration graphique de base de données.

## Règles métier et techniques

- Le cœur métier doit dépendre de protocols ou abstractions, pas d’un connecteur concret.
- `reference_id` est unique.
- `internal_id` est unique.
- `internal_barcode` est unique lorsqu’il existe.
- `commercial_barcode` est indexable, mais ne doit pas identifier une instance physique.
- `production_code` est indexable, mais jamais unique.
- Les recherches par `production_code` doivent retourner zéro, une ou plusieurs instances.
- Les relations parent/enfant doivent référencer des instances physiques.

## Exemple de schéma cible indicatif

```sql
CREATE TABLE mtg_product_references (
    reference_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    image_uri TEXT NULL,
    product_type TEXT NOT NULL,
    set_code TEXT NOT NULL,
    commercial_barcode TEXT NULL
);

CREATE TABLE mtg_product_instances (
    internal_id TEXT PRIMARY KEY,
    reference_id TEXT NOT NULL,
    status TEXT NOT NULL,
    production_code TEXT NULL,
    internal_barcode TEXT NULL UNIQUE,
    parent_id TEXT NULL
);
```

Aucune contrainte `UNIQUE` ne doit être posée sur `production_code`.

## Livrables attendus

- Ports de persistance clarifiés (docstrings `ProductReferenceRepositoryPort`, `ProductRepositoryPort`).
- Doubles mémoire de test : module **`tests/support/in_memory_product_repositories.py`** (`InMemoryProductReferenceRepository`, `InMemoryProductRepository`).
- Tests de contrat sous **`tests/baobab_mtg_products/ports/`** (référence, instance, scénarios insert→read, vue structurelle, absence de dépendance DB runtime dans **`pyproject.toml`**).
- Documentation SQL indicative (inchangée dans son principe : schéma non normatif).
- Aucun adaptateur SQL dans le package runtime ; l’application fournit l’implémentation concrète.

La configuration **`[tool.pytest.ini_options] pythonpath`** inclut la racine du dépôt (`.` ) pour importer **`tests.support`** sans variable d’environnement ad hoc.

## Critères d'acceptation

- Une application peut implémenter un adaptateur SQLite ou PostgreSQL sans modifier le cœur métier.
- Les ports distinguent clairement référence et instance.
- Les recherches par code non unique ne supposent jamais un résultat unique.
- Les tests prouvent que deux instances avec le même code de production peuvent être sauvegardées et relues.
- Le package reste sans dépendance runtime à une base de données.
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
