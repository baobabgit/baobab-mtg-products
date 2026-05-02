# Journal de développement — baobab-mtg-products

Les entrées sont classées par **date et heure décroissantes** (les plus récentes en premier).

## 2026-05-02 22:00:00 — docs sécurité feature 13_persistence_contracts_database_insertion

### Modifications

- **`docs/002_product_reference_instance_persistence_guidance.md`** : § 8 **Sécurité et intégrité des futurs adaptateurs de persistance** (schémas indicatifs, SQL paramétré, anti-injection, unicité **`internal_barcode`**, **`find_by_internal_barcode`**, EAN / **`commercial_barcode`**, migrations, **`image_uri`** / SSRF, UI) ; note après schéma § 6.
- **`docs/features/13_persistence_contracts_database_insertion.md`** : même thème synthétique + renvoi vers **`docs/002`** § 8.
- **`README.md`** : entrées documentation références / persistance et feature **13** précisées (pas d’adaptateur SQL dans la lib).
- **`CHANGELOG.md`** **[Unreleased]** : ligne documentation associée.

### Buts

- Lever les réserves sécurité « GO avec réserves » en traçant les obligations applicatives pour les futurs adaptateurs SQL.

### Impact

- Aucun changement du code métier ; réserves restantes : mise en œuvre concrète côté application (politique DB, migrations, garde-fous runtime).

## 2026-05-02 18:30:00 — feature 13_persistence_contracts_database_insertion (tests & doc)

### Modifications

- **`tests/support/in_memory_product_repositories.py`** (doubles conformes aux ports) ; tests **`test_product_reference_repository_port`**, **`test_product_repository_port`**, **`test_persistence_memory_workflows`** ; **`pyproject.toml`** `pythonpath` pytest **`["src", "."]`**.
- Docstrings ports **`ProductReferenceRepositoryPort`**, **`ProductRepositoryPort`** ; **`docs/002_product_reference_instance_persistence_guidance.md`**, **`docs/features/13_...`**, **`docs/test_plans/13_...`** ; **`CHANGELOG`** section **[Unreleased]**.

### Buts

- Verrouiller les contrats insert/relecture (référence vs instance, **`ProductionCode`** non unique, **`parent_id`**, absence de lookup EAN côté instance) sans dépendance runtime DB.

### Impact

- Surface publique packages inchangée ; **README** non modifié (comportement attendu inchangé pour le consommateur hors tests).

## 2026-05-02 14:00:00 — docs 12_container_deconditioning_workflow (writer)

### Modifications

- **`README.md`** : bloc d’imports minimal (**`DeconditionChildSpecification`**, **`DeconditionContainerCommand`**, **`DeconditionContainerUseCase`**) sous la section déconditionnement.

### Buts

- Documentation consommateur alignée sur la surface exportée racine : distinction déconditionnement / ouverture, commande et specs.

### Impact

- Aucun changement de code ni de **`CHANGELOG.md`**.

## 2026-05-02 12:00:00 — feature 12_container_deconditioning_workflow

### Modifications

- **`DeconditionContainerUseCase`**, commandes et specs dans **`domain.deconditioning`** ; politique **`DeconditionableContainerPolicy`** ; statut **`DECONDITIONED`** ; événement **`CONTAINER_DECONDITIONED`** + **`record_container_deconditioned`** sur le port workflow et le ledger mémoire.
- Exceptions dédiées sous **`exceptions/deconditioning/`** ; réexports **`__init__.py`** racine ; tests (use case, commande, policy, timeline, vue structurelle) ; fakes de tests enrichis.
- **`CHANGELOG` [2.3.0]**, **`README`**, **`docs/features/12_container_deconditioning_workflow.md`** (scénario display → 15 boosters), **`pyproject.toml`**.

### Buts

- Séparer **déconditionnement** (contenant → exemplaires enfants) et **ouverture** (booster → cartes), sans traçabilité carte sur le premier flux.

### Impact

- **Mineur** SemVer **2.3.0** : les implémentations de **`ProductWorkflowEventRecorderPort`** doivent fournir **`record_container_deconditioned`**.

## 2026-05-01 22:00:00 — correction QA feature 11 (scan commercial / interne)

### Modifications

- Restauration des tests workflow `test_registration_from_scan_runner_contract_negatives` ; correction **flake8 F841** ; test d’inventaire **2 displays × 15 boosters + bundle** enrichi (pas de réutilisation silencieuse d’instance sur EAN).
- Test **`RegisterProductByInternalScanUseCase`** : rejet du code interne invalide **avant** le runner ; documentation **README** + **`docs/features/11_commercial_and_internal_scan_workflow_refactor.md`**.

### Buts

- Lever les réserves QA (arbre propre, qualité verte, scénario métier verrouillé).

## 2026-05-01 20:30:00 — feature 11_commercial_and_internal_scan_workflow_refactor

### Modifications

- **`RegistrationScanOutcome.INTERNAL_BARCODE_UNKNOWN`**, **`RegistrationScanResult.resolved_reference`** ; refonte **`register_via_internal`** / **`register_via_commercial`** (runner).
- **`ResolveProductReferenceFromCommercialBarcodeUseCase`**, **`CommercialReferenceResolutionResult`** ; tests scénario deux displays, résolution EAN seule, exports racine.
- **`CHANGELOG` [2.2.0]**, **`README`**, **`pyproject.toml`**.

### Buts

- Distinguer clairement résolution catalogue (EAN) et identification d’exemplaire (code interne), sans traiter l’EAN comme identifiant physique unique.

### Impact

- **Mineur** SemVer **2.2.0** : tout code qui supposait une matérialisation après scan interne inconnu doit migrer (ex. **`CreateProductInstanceUseCase`** + code interne).

## 2026-05-01 18:00:00 — feature 10_physical_instance_creation_and_production_code

### Modifications

- **`ProductionCode`**, exceptions associées, **`CreateProductInstanceUseCase`**, **`AssignProductionCodeToProductInstanceUseCase`** ; **`ProductInstance.production_code`**.
- **`ProductRepositoryPort.list_by_reference_id`** / **`list_by_production_code`** ; événements **`INSTANCE_CREATED`**, **`PRODUCTION_CODE_ASSIGNED`** sur le port workflow et le ledger mémoire.
- Exports racine (**`ProductionCode`**, cas d’usage, **`DuplicateInternalBarcodeError`**, **`ProductReferenceNotFoundForWorkflowError`**), **`CHANGELOG` [2.1.0]**, **`README`**, tests unitaires et de workflow.

### Buts

- Permettre plusieurs exemplaires d’une même référence avec le même code de lot sans confondre avec l’identité forte (**`internal_id`**), tout en imposant l’unicité du code-barres interne lorsqu’il existe.

### Impact

- **Mineur** SemVer **2.1.0** : les adaptateurs de **`ProductRepositoryPort`** et de **`ProductWorkflowEventRecorderPort`** doivent implémenter les nouvelles signatures.

## 2026-05-01 12:00:00 — feature 09_product_reference_instance_split

### Modifications

- Ajout de **`ProductReference`**, **`ProductReferenceId`**, ports de persistance et de fabrique d’ids ; adaptation de **`ProductInstance`** (`reference_id`, suppression du code-barres commercial sur l’instance, clarification type/set dénormalisés).
- Refonte de **`RegistrationFromScanRunner`** (réutilisation de référence + nouvelle instance par scan commercial dupliqué), de **`QualifyScannedProductUseCase`** (mise à jour référence + instance), des services **`GetSealedProductSnapshotService`** et **`GetProductStructuralViewService`** (jointure avec références).
- Extension de **`ResolvedFromScan`**, **`ProductProvenanceForCollection`**, exports racine, **`CHANGELOG`** **2.0.0**, **`README`**, tests unitaires et de workflow.

### Buts

- Séparer explicitement catalogue commercial et exemplaire physique, permettre plusieurs instances pour un même code-barres sans ambiguïté sur l’identité unique (**`internal_id`**).

### Impact

- **Breaking** SemVer **2.0.0** : signatures des constructeurs de services / runner, **`ProductInstance`**, port dépôt instance ; consommateurs doivent brancher un **`ProductReferenceRepositoryPort`** et migrer les données.

## 2026-04-05 — fix release_go_1_0_1

### Contexte

- Un tag / release GitHub **`v1.0.0`** est déjà public : toute correction de **packaging** ou de **readiness PyPI** doit éviter une réutilisation ambiguë de ce tag ou un historique réécrit.
- La mission visait aussi à garantir la cohérence **documentation ↔ extra `[dev]`** et **classifier PyPI stable** ; sur `main`, **`build`** et **`twine` (≥ 6)** étaient déjà présents dans `[dev]`, et le classifier était déjà **Production/Stable** — pas de régression à corriger de ce côté.

### Modifications

- Branche `fix/release-go-1-0-1` : bump **1.0.0 → 1.0.1** dans `pyproject.toml`, repli `__version__` dans `baobab_mtg_products.__init__`, assertion du test `test_init.py` ; entrée **`CHANGELOG.md` [1.0.1]** ; `docs/RELEASE.md` (stratégie tags `v1.0.0` vs release patch suivante, commandes avec `pip install --upgrade pip`) ; `README.md` (rappel SemVer après `v1.0.0`).

### Impact readiness PyPI

- Le prochain artefact publié peut porter le numéro **1.0.1**, traçable et distinct du tag **`v1.0.0`**, ce qui clarifie la chaîne release pour les consommateurs PyPI et les clones Git.

### Pourquoi 1.0.1 plutôt que « recycler » v1.0.0

- **SemVer** et les bonnes pratiques Git interdisent de déplacer un tag déjà poussé ; un **patch** documente explicitement les corrections release sans nier la release **`v1.0.0`**.

## 2026-04-04 — fix release_go_pypi_ci

### Modifications

- Branche `fix/release-go-1-0-0` : classifier PyPI `Development Status` aligné sur **Production/Stable** (cohérence avec la **1.0.0**) ; extras `[dev]` enrichis avec **`build`** et **`twine`** ; workflow **`.github/workflows/ci.yml`** (push / PR, matrix Python 3.10–3.13) reprenant tests, couverture avec `fail_under`, black, pylint, mypy, flake8, bandit, `python -m build`, `twine check dist/*` ; `ParentChildRelationshipRules.validate` : retrait de l’`assert` (B101 bandit) au profit d’un `else` métier explicite + test ; `docs/RELEASE.md`, `README.md`, `docs/000_dev_constraints.md`, `CHANGELOG.md` mis à jour en conséquence.

### Buts

- Rendre le **GO release PyPI** **traçable** (CI publique), **reproductible** (outils de build dans `[dev]`) et **honnête** dans les métadonnées (stable annoncée = classifier stable).

### Impact

- Toute contribution mergée sur `main` est vérifiée automatiquement sur plusieurs versions Python ; les mainteneurs peuvent rejouer la même séquence en local ou s’y référer pour le tag et la publication sans écart avec la CI.

## 2026-04-04 — feature 08_release_readiness

### Modifications

- Branche `feature/release-readiness` : version **1.0.0** ; `README.md` restructuré (périmètre, installation runtime/dev, démarrage rapide, tableaux, liens) ; `docs/RELEASE.md` (checklist publication) ; `CHANGELOG.md` ; métadonnées `pyproject.toml` (classifier stable, URLs, description) ; seuil couverture **95 %** (aligné cahier des charges / contraintes dev) ; `ParentChildRelationshipRules` ajusté pour **100 %** branches ; stabilité API documentée dans le module racine ; validation `python -m build`.

### Buts

- Finaliser une release technique cohérente avec le cahier des charges, sans nouvelle fonctionnalité métier majeure.

### Impact

- Les consommateurs peuvent s’appuyer sur SemVer 1.x pour la surface exportée à la racine ; les contrôles qualité et la checklist release sont explicités.

## 2026-04-04 — feature 07_query_services_and_public_api

### Modifications

- Branche `feature/query-services-public-api` : package `services.query` (`GetSealedProductSnapshotService`, `GetProductStructuralViewService`, `GetProductBusinessTimelineService`) ; `domain.query.ProductStructuralView` ; extension `ProductRepositoryPort.list_direct_children_of_parent` ; exceptions `ProductNotFoundForQueryError`, `MissingReferencedParentProductError` ; réorganisation des exports du package racine (ports clés + consultation) ; tests miroirs et doubles de dépôt mis à jour ; version `0.8.0`.

### Buts

- Offrir des entrées de lecture métier explicites et une surface publique Python documentée, sans HTTP ni recherche multi-critères persistée.

### Impact

- Les adaptateurs de dépôt doivent implémenter `list_direct_children_of_parent` ; `ListProductBusinessHistoryUseCase` reste disponible sous `use_cases.history` mais n’est plus exporté à la racine.

## 2026-04-04 — feature 06_integration_ports_collection_statistics

### Modifications

- Branche `feature/integration-ports-collection-statistics` : package `domain.integration` (provenance produit, événement lien parent-enfant, messages statistiques ouverture / carte / scan) ; ports `CollectionPort` et `StatisticsPort` redéfinis sur ces DTO ; exception `InvalidIntegrationPayloadError` ; branchement optionnel dans `RegistrationFromScanRunner`, `QualifyScannedProductUseCase`, `OpenSealedProductUseCase`, `RegisterRevealedCardFromOpeningUseCase`, `RecordOpeningCardScanUseCase`, `AttachChildProductToParentUseCase`, `DetachChildProductFromParentUseCase` ; tests miroirs et fakes ; version `0.7.0`.

### Buts

- Exposer des contrats stables pour synchroniser la collection et comptabiliser les faits d’ouverture sans coupler la lib à des transports ou implémentations externes.

### Impact

- Les applications injectent des adaptateurs derrière les protocols ; sans port, le comportement reste inchangé pour le journal métier existant.

## 2026-04-04 — feature 05_history_and_event_log

### Modifications

- Branche `feature/history-event-log` : package `domain.history` (`ProductBusinessEventKind`, `ProductBusinessEventPayload`, `ProductBusinessEventRecord`, `InMemoryProductBusinessEventLedger`) ; port `ProductBusinessHistoryQueryPort` ; cas d’usage `ListProductBusinessHistoryUseCase` ; exception `ProductHistoryCoherenceError` ; le ledger implémente aussi `ProductWorkflowEventRecorderPort` avec contrôles de cohérence ; version `0.6.0`.

### Buts

- Centraliser les traces métier (scan, enregistrement, qualification, rattachement, ouverture, cartes) dans un journal ordonné, consultable par produit, avec rejets explicites des séquences incohérentes.

### Impact

- Les applications peuvent injecter le ledger comme implémentation unique du journal d’événements workflow ; pas de bus externe ni persistance distribuée dans la lib.

## 2026-04-04 — feature 04_opening_and_card_traceability

### Modifications

- Branche `feature/opening-card-traceability` : package `domain.opening` (`ProductOpeningEvent`, `OpenSealedProductOutcome`, `ExternalCardId`, `RevealedCardTrace`, `OpeningCardScanPayload`, règles d’éligibilité) ; port `RevealedCardTraceRepositoryPort` ; cas d’usage `OpenSealedProductUseCase`, `RegisterRevealedCardFromOpeningUseCase`, `RecordOpeningCardScanUseCase` ; exceptions sous `exceptions.opening` ; extension `ProductWorkflowEventRecorderPort` (ouverture, carte révélée, scan carte) ; tests miroirs ; version `0.5.0`.

### Buts

- Ouvrir une fois un scellé éligible (hors display, statuts `sealed` ou `qualified`), tracer les cartes révélées via identifiants externes et journaliser les scans pendant la session.

### Impact

- Les adaptateurs implémentent le dépôt de traces et les trois nouvelles méthodes du journal d’événements ; pas de modèle de possession globale des cartes.

## 2026-04-04 — feature 03_parent_child_relationships

### Modifications

- Branche `feature/parent-child-relationships` : package `domain.products.relationships` (`ProductRelationshipKind`, `ProductRelationship`, `ParentChildRelationshipRules`, `ProductAncestorChain`) ; cas d’usage `AttachChildProductToParentUseCase`, `DetachChildProductFromParentUseCase` ; exceptions sous `exceptions.relationship` ; extension du port `ProductWorkflowEventRecorderPort` (événements attach / detach) ; tests miroirs ; version `0.4.0`.

### Buts

- Modéliser les rattachements structurels (display → booster, bundle → sous-produits, lien générique), rejeter cycles / types incohérents / enfant déjà rattaché, permettre un booster sans parent et journaliser attach / detach.

### Impact

- Les adaptateurs d’événements doivent implémenter les deux nouvelles méthodes du port ; la hiérarchie reste portée par `ProductInstance.parent_id`.

## 2026-04-04 — feature 02_registration_and_scan_workflow

### Modifications

- Branche `feature/registration-scan-workflow` : ports dépôt / résolution barcode / fabrique d’ids / journal d’événements ; runner `RegistrationFromScanRunner` ; cas d’usage scan commercial, scan interne et qualification ; package `domain.registration` ; exceptions dédiées.
- `ProductInstance.derived_with` pour qualification sans mutation ; tests avec doubles mémoire ; version `0.3.0`.

### Buts

- Permettre de créer ou de retrouver un produit après scan, distinguer connu / nouveau qualifié / à qualifier, journaliser scan et enregistrement.

### Impact

- Les adaptateurs externes implémentent les ports ; la librairie reste sans HTTP ni persistance imposée.

## 2026-04-04 — feature 01_product_reference_model

### Modifications

- Branche `feature/product-reference-model` : package `domain.products` avec `ProductType`, `ProductStatus`, value objects d’identifiants / codes et `ProductInstance` (héritage de `DomainEntity`).
- Exceptions `InvalidProductIdentifierError`, `InvalidSetCodeError`, `InvalidCommercialBarcodeError`, `InvalidInternalBarcodeError`, `InvalidSerialNumberError`, `InvalidProductInstanceError` et tests miroirs.
- Version `0.2.0`, exports racine, ajustements pylint (`duplicate-code`, limites d’arguments), mise à jour de `README.md`, `CHANGELOG.md`.

### Buts

- Couvrir le périmètre minimal du cahier des charges pour la modélisation des types, statuts et instance produit avec validations à la construction.

### Impact

- Base typée pour les workflows scan / rattachement / ouverture sans les implémenter dans cette feature.

## 2026-04-04 — feature 00_project_bootstrap

### Modifications

- Création de la branche `feature/project-bootstrap` et du socle `src/baobab_mtg_products/` avec sous-packages `exceptions`, `domain`, `ports`, `use_cases`.
- Ajout de `pyproject.toml` (setuptools, pytest, coverage avec `data_file` et rapports sous `docs/tests/coverage/`, black, pylint, mypy strict, flake8 via `flake8-pyproject`, bandit).
- Implémentation de `BaobabMtgProductsException`, `DomainEntity`, `CollectionPort`, `StatisticsPort`, `UseCase` et tests miroirs associés.
- Rédaction de `README.md`, `CHANGELOG.md`, `LICENSE`, `docs/tests/coverage/README.md` et mise à jour de `.gitignore` pour les artefacts de couverture.
- Ajout du marqueur `py.typed` pour indiquer un package typé.

### Buts

- Satisfaire la feature `00_project_bootstrap` : projet installable, outillage qualité vert, couverture ≥ 90 %, structure conforme au cahier des charges.

### Impact

- Base prête pour les features métier (produits, scans, relations, ouverture) sans couplage API / front / rules engine / deckbuilder.
