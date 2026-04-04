# Journal de développement — baobab-mtg-products

Les entrées sont classées par **date et heure décroissantes** (les plus récentes en premier).

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
