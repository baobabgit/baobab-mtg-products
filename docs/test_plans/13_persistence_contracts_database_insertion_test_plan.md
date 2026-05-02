# Plan de test — 13_persistence_contracts_database_insertion — Contrats de persistance et insertion en base

## Objectif de validation

Garantir que les **contrats de ports** (`Protocol`) pour références et instances sont **complets**, **typés** et **documentés** pour permettre à une application d’écrire un adaptateur SQL (SQLite, PostgreSQL, etc.) **sans modifier le domaine** ; que les recherches par **clés non uniques** (`production_code`, multi-instances par `reference_id`) retournent **toujours des séquences** (`tuple[...]`), jamais une sémantique « un seul résultat » implicite ; que les **unicités** (`reference_id`, `internal_id`, `internal_barcode`) et la **non-unicité** du code commercial au niveau instance sont reflétées dans les contrats et la doc SQL ; que des **doubles mémoire** conformes valident ces contrats ; que le package **reste sans dépendance runtime** à une base de données.

Les tests restent **déterministes**, **sans moteur SQL** ni réseau.

## Cadrage validé (feature 13)

1. **Nom du port instance** : ne **pas** renommer `ProductRepositoryPort` en `ProductInstanceRepositoryPort` dans cette feature. Le dépôt utilise déjà `ProductRepositoryPort` pour les **instances physiques**. Un renommage relève d’une **migration d’API séparée**.

2. **Code de lot vs numéro de série** : les tests et le port **`list_by_production_code`** s’alignent sur le modèle réel — value object **`ProductionCode`** (feature 10). **`SerialNumber`** reste un champ distinct (piste qualité unitaire) ; ne pas le substituer au code de production dans ces tests.

3. **Périmètre technique** : **aucune** dépendance runtime à un moteur SQL, ORM ou driver. La feature 13 reste limitée aux **ports**, **contrats**, **doubles mémoire**, **tests**, **documentation** (dont schéma SQL indicatif).

4. **Unicité du code-barres interne** : l’exception métier **`DuplicateInternalBarcodeError`** **existe** dans le projet (`CreateProductInstanceUseCase`, exports publics). Les tests de **feature 13** peuvent **référencer** ce comportement là où un flux métier valide l’unicité avant persistance. **Ne pas** introduire d’extension obligatoire du port (`save` qui lève cette exception) **sans décision d’architecture** : pour un **adaptateur SQL**, l’unicité peut être garantie par **contrainte `UNIQUE`** et gestion d’erreur côté application ; le contrat du port peut rester silencieux sur ce point tant que la doc l’indique.

5. **Emplacement de ce plan** : `docs/test_plans/13_persistence_contracts_database_insertion_test_plan.md`.

**Avis** : GO sur le plan de test, sous réserve du présent cadrage.

## Matrice des règles métier à couvrir

| Règle | Tests nominaux | Tests d'erreur | Tests de non-régression |
|-------|----------------|----------------|-------------------------|
| Cœur métier → `Protocol` uniquement | Assignation `adapter: ProductRepositoryPort = _MemoryImpl` ; idem ref port | — | Use cases inchangés si adaptateur conforme |
| `reference_id` unique (agrégat ref) | `save` + `find_by_id` round-trip ; deux refs distinctes coexistent | — | VO `ProductReferenceId` |
| `internal_id` unique (instance) | Round-trip ; deux instances distinctes | — | VO `InternalProductId` |
| `internal_barcode` unique si présent | Deux instances même `ProductionCode` OK ; deux `internal_barcode` identiques → selon couche : voir ci-dessous | Use cases existants : `DuplicateInternalBarcodeError` où déjà levée ; adaptateur : contrainte UNIQUE documentée | Pas d’obligation nouvelle sur le `Protocol` sans ADR |
| `commercial_barcode` indexable, pas clé instance | Recherche uniquement sur **`ProductReferenceRepositoryPort`** ; pas de `find_by_commercial` sur instance port | — | Scan commercial / feature 11 |
| `production_code` indexable, jamais unique | `list_by_production_code` avec VO **`ProductionCode`** → 0, 1 ou **N** résultats ; ordre stable | Jamais de signature `Optional[ProductInstance]` pour ce critère | `test_product_repository_port` existant |
| Relations parent/enfant = instances | `list_direct_children_of_parent` ; `parent_id` pointe vers `internal_id` existant | — | Attach / déconditionnement |
| Distinction ref / instance | Deux ports distincts ; **`ProductRepositoryPort`** = instances (nom inchangé en 13) | — | Consultation 07 |
| Traces métier | Contrat historique via **`ProductBusinessHistoryQueryPort`** / ledger mémoire (pas d’ORM dans le domaine) | — | Feature 05 |
| Pas de dépendance DB runtime | `pyproject.toml` sans driver/ORM dans `[project]` ; test `test_project_has_no_runtime_database_dependency` | — | CI |

## Tests unitaires à créer

- **Contrat `ProductReferenceRepositoryPort`** : étendre `tests/.../test_product_reference_repository_port.py` — `save`/`find_by_id`/`find_by_commercial_barcode` ; optional `list_all` **non** requis par la spec actuelle.
- **Contrat `ProductRepositoryPort`** : compléter / factoriser `_FakeRepo` partagé — toutes les méthodes obligatoires implémentées ; tests `find_by_internal_barcode` non trivial (deux instances, codes différents).
- **`list_by_production_code` — deux lignes même code** : sauvegarder deux instances avec le même **`ProductionCode`**, relire les deux, ordre stable documenté (ex. tri par `internal_id`).
- **`DuplicateInternalBarcodeError`** : non obligatoire sur le **seul** contrat port ; optionnel : référencer les tests existants (`CreateProductInstanceUseCase`) dans la doc feature 13 ; doubles mémoire peuvent choisir « dernier gagne » ou lever une erreur pour refléter une politique d’adaptateur — à documenter si un double strict est ajouté.
- **Documentation vs domaine** : test optionnel ou checklist que les champs persistés du schéma SQL indicatif couvrent au minimum les attributs des agrégats **ou** que la doc mentionne les colonnes additionnelles (`requires_qualification`, `serial_number`, copie dénormalisée `product_type`/`set_code` sur instance si l’adaptateur les mappe).

## Tests de workflow à créer

- **Parcours insert→read** : `test_insert_and_read_reference_and_multiple_instances_from_memory_repositories` dans `tests/baobab_mtg_products/ports/test_persistence_memory_workflows.py`.
- **Vue consultation** : `test_structural_view_with_in_memory_repositories_aligns_children_and_references` (même fichier) ; `GetProductStructuralViewService` + `InMemory*` depuis `tests/support/in_memory_product_repositories.py`.
- **Pas de test use case SQL** : les workflows métier existants restent sur ports injectés.

## Cas limites

- `list_by_production_code` avec valeur absente : le critère est un **`ProductionCode`** valide ; pas de chemin API avec `None`.
- Instance sans `internal_barcode` : `find_by_internal_barcode` ne la retrouve pas ; plusieurs instances sans barcode interne autorisées.
- `parent_id` pointant vers instance absente : comportement consultation (`MissingReferencedParentProductError`) vs persistance tolérante — documenter ce que l’adaptateur SQL doit garantir (FK optionnelle vs validation applicative).
- `find_by_commercial_barcode` retourne au plus une ref (V1) — pas de test « multi-résultats » sur ce port tant que le contrat reste `Optional`.

## Tests de non-régression

- Tous les tests existants qui mockent les ports (`registration`, `qualify`, `create instance`, parent-enfant, opening, query) après refactor des fakes.
- **`ProductRelationshipRepositoryPort`** : si **non** introduit, la doc feature 13 indique que la relation est portée par **`parent_id` + `ProductRepositoryPort`**.

## Risques de couverture

| Risque | Mitigation |
|--------|------------|
| Fakes incomplets dans la suite | Factoriser implémentations mémoire complètes |
| Schéma SQL indicatif désynchronisé du domaine | Revue doc + colonnes explicites pour `ProductionCode`, `SerialNumber`, etc. |
| Historique append-only en base | Hors périmètre migration ; préciser contrat dans `ProductBusinessHistoryQueryPort` |

## Données de test recommandées

| Élément | Exemples |
|---------|----------|
| `reference_id` | `ref-a`, `ref-b` |
| `internal_id` | `p-1`, `p-2` |
| `ProductionCode` partagé | `LOT-2026-A` sur deux instances |
| `SerialNumber` (distinct du lot) | `SN-WOTC-001` si test persistance champs optionnels |
| `InternalBarcode` distincts | `INT-001`, `INT-002` |
| `CommercialBarcode` | `087207027866` sur **référence** uniquement |
| Parent / enfants | `display-internal`, enfants `pb-01`… avec `parent_id` |

## Points ouverts (hors renommage port)

1. **`ProductRelationshipRepositoryPort`** : nécessaire si extraction hors `parent_id`, sinon absence documentée dans la doc 13.
2. **Champs instance hors snippet SQL minimal** : stratégie colonnes pour dénormalisation vs jointure ref.
3. **Comportement `save` doublon `internal_barcode`** au niveau port : documenter « responsabilité adaptateur / contrainte UNIQUE » tant qu’aucune levée d’exception n’est ajoutée au `Protocol`.
