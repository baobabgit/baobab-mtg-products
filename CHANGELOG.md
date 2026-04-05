# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format s’inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [1.0.0] - 2026-04-04

### Summary

Première version **stable** : périmètre fonctionnel couvert par les features 00–07, documentation consolidée (`README`, `docs/RELEASE.md`), métadonnées de packaging (PyPI classifiers `Production/Stable`, URLs dépôt), seuil de couverture relevé à **95 %**, et clarification de la stabilité de l’API exportée au niveau racine.

### Fixed

- `pyproject.toml` : le classifier `Development Status` était resté en **Pre-Alpha** alors que la version **1.0.0** est annoncée stable ; alignement sur **Production/Stable**.
- `ParentChildRelationshipRules.validate` : suppression de l’`assert` d’exhaustivité (signalé par **bandit** B101) au profit d’une branche `else` explicite et d’un test de garde-fou pour les kinds non reconnus.

### Added

- Dépendances optionnelles de développement `build` et `twine` (**≥ 6**) pour reproduire localement la construction d’artefacts et le contrôle `twine check` (métadonnées **Metadata-Version 2.4** produites par le build actuel).
- Workflow GitHub Actions `.github/workflows/ci.yml` (événements `push` et `pull_request`) : tests, couverture avec seuil configuré, `black`, `pylint`, `mypy`, `flake8`, `bandit`, `python -m build`, `python -m twine check dist/*`.

### Changed

- `ParentChildRelationshipRules.validate` : branchement `if` / `elif` / `elif` / `else` sur le kind, sans `assert` runtime (couverture à 100 % ; compatible **bandit**).
- `pyproject.toml` : `fail_under` couverture à **95 %** ; liens `Repository` / `Documentation` / `Issues` alignés sur le dépôt effectif.
- Documentation : seuil de couverture porté à 95 % dans `docs/001_specifications.md`, `docs/000_dev_constraints.md` et `docs/tests/coverage/README.md`.

## [0.8.0] - 2026-04-04

### Added

- Package `services.query` : `GetSealedProductSnapshotService`, `GetProductStructuralViewService`, `GetProductBusinessTimelineService` (consultation métier via `load()`).
- `domain.query.ProductStructuralView` : vue produit + parent résolu + enfants directs.
- Port `ProductRepositoryPort` : `list_direct_children_of_parent` pour alimenter les vues structurelles.
- Exceptions `ProductNotFoundForQueryError`, `MissingReferencedParentProductError` (réexportées depuis `baobab_mtg_products.exceptions`).

### Changed

- API publique du package racine : exports des services de consultation, de `ProductStructuralView`, des ports `ProductRepositoryPort`, `ProductBusinessHistoryQueryPort`, `CollectionPort`, `StatisticsPort`, et des exceptions de consultation ; retrait de `ListProductBusinessHistoryUseCase` des exports racine (toujours disponible sous `use_cases.history`).

## [0.7.0] - 2026-04-04

### Added

- Intégration collection / statistiques : package `domain.integration` (DTO `ProductProvenanceForCollection`, `ProductParentLinkForCollectionEvent`, `SealedProductOpenedStatisticsEvent`, `CardRevealedStatisticsEvent`, `OpeningCardScanStatisticsEvent`).
- Ports `CollectionPort` (`publish_product_provenance`, `publish_parent_child_link`) et `StatisticsPort` (trois méthodes typées par DTO).
- Exception `InvalidIntegrationPayloadError` (réexportée depuis `baobab_mtg_products.exceptions`).

### Changed

- `RegistrationFromScanRunner` accepte un port `CollectionPort` optionnel et publie la provenance après chaque scan abouti (produit existant ou nouvellement créé).
- `QualifyScannedProductUseCase`, `OpenSealedProductUseCase`, `AttachChildProductToParentUseCase`, `DetachChildProductFromParentUseCase` acceptent un `CollectionPort` optionnel ; `OpenSealedProductUseCase` accepte aussi un `StatisticsPort` optionnel ; `RegisterRevealedCardFromOpeningUseCase` et `RecordOpeningCardScanUseCase` acceptent un `StatisticsPort` optionnel.

## [0.6.0] - 2026-04-04

### Added

- Historique métier : `domain.history` avec modèle d’événements (`ProductBusinessEventKind`, `ProductBusinessEventRecord`, `ProductBusinessEventPayload`) et `InMemoryProductBusinessEventLedger` (append-only, cohérence minimale).
- Port `ProductBusinessHistoryQueryPort` et cas d’usage `ListProductBusinessHistoryUseCase`.
- Exception `ProductHistoryCoherenceError` (réexportée depuis `baobab_mtg_products.exceptions`).

## [0.5.0] - 2026-04-04

### Added

- Ouverture et traçabilité : `domain.opening` (`ProductOpeningEvent`, `OpenSealedProductOutcome`, `ExternalCardId`, `RevealedCardTrace`, `OpeningCardScanPayload`, `SealedProductOpeningRules`, `OpenedProductCardTraceRules`).
- Cas d’usage `OpenSealedProductUseCase`, `RegisterRevealedCardFromOpeningUseCase`, `RecordOpeningCardScanUseCase` (`use_cases.opening`).
- Port `RevealedCardTraceRepositoryPort` pour persister les provenances carte ↔ produit ouvert.
- Exceptions `ProductAlreadyOpenedError`, `ProductNotOpenableError`, `ProductNotReadyForOpeningError`, `ProductNotOpenedForCardTraceError`, `DuplicateRevealedCardTraceError`, `InvalidExternalCardIdError`, `InvalidOpeningCardScanPayloadError`, `InvalidRevealedCardSequenceError` (réexportées depuis `baobab_mtg_products.exceptions`).
- Port `ProductWorkflowEventRecorderPort` : `record_product_opened`, `record_card_revealed_from_opening`, `record_opening_card_scan`.

## [0.4.0] - 2026-04-04

### Added

- Relations parent / enfant : `ProductRelationshipKind`, `ProductRelationship`, `ParentChildRelationshipRules`, `ProductAncestorChain`.
- Cas d’usage `AttachChildProductToParentUseCase` et `DetachChildProductFromParentUseCase` (`use_cases.parent_child`).
- Exceptions `InvalidProductRelationshipLinkError`, `IncompatibleParentChildTypesError`, `ProductAlreadyHasParentError`, `CircularProductParentageError`, `IncompleteProductHierarchyError`, `ChildProductNotAttachedError`, `DetachParentMismatchError` (réexportées depuis `baobab_mtg_products.exceptions`).
- Port `ProductWorkflowEventRecorderPort` : `record_product_attached_to_parent`, `record_product_detached_from_parent`.

## [0.3.0] - 2026-04-04

### Added

- Workflow d’enregistrement par scan : ports `BarcodeResolutionPort`, `ProductRepositoryPort`, `InternalProductIdFactoryPort`, `ProductWorkflowEventRecorderPort`.
- Domaine `domain.registration` : `ResolvedFromScan`, `RegistrationScanOutcome`, `RegistrationScanResult`, `RegistrationDefaults` (set placeholder `QQ`).
- `RegistrationFromScanRunner`, `RegisterProductByCommercialScanUseCase`, `RegisterProductByInternalScanUseCase`, `QualifyScannedProductUseCase`.
- Exceptions `AmbiguousBarcodeResolutionError`, `ProductNotFoundForWorkflowError`, `InvalidQualificationStateError`.
- Méthode `ProductInstance.derived_with` pour évolutions immuables (qualification).

## [0.2.0] - 2026-04-04

### Added

- Modèle de référence produit : `ProductType`, `ProductStatus`, `ProductInstance`.
- Value objects : `InternalProductId`, `MtgSetCode`, `CommercialBarcode`, `InternalBarcode`, `SerialNumber`.
- Exceptions domaine produit sous `exceptions.product` (réexportées depuis `baobab_mtg_products.exceptions`).
- Exports publics racine pour les symboles ci-dessus.

### Changed

- `pylint` : plafonds `max-args` / `max-positional-arguments` relevés ; désactivation de `duplicate-code` pour les listes `__all__` répétées.

## [0.1.0] - 2026-04-04

### Added

- Squelette du package `baobab_mtg_products` (layout `src/`, `tests/`, `docs/`).
- Exception racine `BaobabMtgProductsException`.
- Points d’extension : `DomainEntity`, ports `CollectionPort` et `StatisticsPort`, base `UseCase`.
- Configuration centralisée dans `pyproject.toml` (packaging, pytest, coverage, black, pylint, mypy, flake8, bandit).
- Documentation initiale (`README.md`, `docs/dev_diary.md`, configuration de couverture sous `docs/tests/coverage/`).
