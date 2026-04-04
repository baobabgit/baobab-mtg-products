# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format s’inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

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
