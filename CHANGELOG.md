# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format s’inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]

## [2.4.0] - 2026-05-02

### Summary

Version **mineure** : **contrats de persistance** affinés sur les ports références / instances, **doubles mémoire** de test sous **`tests/support/`**, et documentation **sécurité / intégrité** pour les futurs adaptateurs SQL.

### Added

- Tests de contrat **persistance** (ports références / instances) avec doubles **`tests/support/in_memory_product_repositories.py`** ; scénarios insert→read mémoire et vue structurelle ; garde-fou **`pyproject.toml`** sans dépendance runtime SQL.

### Changed

- **`pyproject.toml`** : **`pythonpath`** pytest étendu avec **`.`** pour importer **`tests.support`** ; **`init-hook`** pylint pour résoudre les imports **`tests.support.*`** dans la CI locale.

### Documentation

- **Sécurité et intégrité des futurs adaptateurs de persistance** : `docs/002_product_reference_instance_persistence_guidance.md` (§ 8), `docs/features/13_persistence_contracts_database_insertion.md` ; rappel **`README`** — aucun adaptateur SQL dans le package runtime, obligations applicatives (requêtes paramétrées, unicité **`internal_barcode`**, pas de choix arbitraire sur doublons, EAN, SSRF / **`image_uri`**, échappement UI).

## [2.3.0] - 2026-05-02

### Summary

Version **mineure** : **déconditionnement de contenants** (display, bundle, kit prerelease, etc.) — distinct de l’**ouverture** d’un booster pour révélation de cartes.

### Added

- **`ProductStatus.DECONDITIONED`** ; **`ProductBusinessEventKind.CONTAINER_DECONDITIONED`** ; charge **`deconditioned_children_count`** sur **`ProductBusinessEventPayload`**.
- Port **`ProductWorkflowEventRecorderPort.record_container_deconditioned`** ; implémentation **`InMemoryProductBusinessEventLedger`**.
- Domaine **`domain.deconditioning`** : **`DeconditionableContainerPolicy`**, **`DeconditionChildSpecification`**, **`DeconditionContainerCommand`**, **`DeconditionContainerResult`**.
- Cas d’usage **`DeconditionContainerUseCase`** (création d’enfants via **`CreateProductInstanceUseCase`** + rattachement via **`AttachChildProductToParentUseCase`** ; pas d’événements d’ouverture / carte).
- Exceptions **`exceptions.deconditioning`** : **`ProductNotDeconditionableContainerError`**, **`ContainerAlreadyDeconditionedError`**, **`DeconditionContainerEmptyChildrenError`**, **`InvalidDeconditionChildSpecificationError`**.
- Réexports racine du package ; tests unitaires et de workflow (vue structurelle, timeline).

### Changed

- Les implémentations du port workflow dans les tests incluent **`record_container_deconditioned`** (spy / no-op).

## [2.2.0] - 2026-05-01

### Summary

Version **mineure** : refonte explicite des workflows **scan commercial** (EAN → référence, jamais clé d’unicité d’exemplaire) et **scan interne** (clé vers une instance ou issue **inconnue** sans matérialisation catalogue).

### Added

- **`CommercialReferenceResolutionResult`** et **`ResolveProductReferenceFromCommercialBarcodeUseCase`** : résolution EAN → référence sans créer d’instance.
- **`RegistrationScanOutcome.INTERNAL_BARCODE_UNKNOWN`** ; champ **`resolved_reference`** documenté sur **`RegistrationScanResult`**.

### Changed

- **`RegistrationFromScanRunner.register_via_internal`** : code interne inconnu → ``product is None`` et issue explicite ; plus de création implicite via ``resolve_internal``.
- **`register_via_commercial`** : renseigne systématiquement **`resolved_reference`** lorsque la référence catalogue est connue (réutilisée ou créée).

## [2.1.0] - 2026-05-01

### Summary

Version **mineure** : création explicite d’**instances physiques** à partir d’une référence catalogue, **code de production / lot optionnel et non unique**, code-barres interne **unique s’il est renseigné**, et journalisation dédiée.

### Added

- Value object **`ProductionCode`** (lot / fabrication non unique) et exceptions **`InvalidProductionCodeError`**, **`DuplicateInternalBarcodeError`**.
- Cas d’usage **`CreateProductInstanceUseCase`** et **`AssignProductionCodeToProductInstanceUseCase`**.
- Champ **`production_code`** sur **`ProductInstance`** ; méthodes de dépôt **`list_by_reference_id`** et **`list_by_production_code`** (tuple trié, jamais sémantique d’unicité).
- Événements métier **`INSTANCE_CREATED`** et **`PRODUCTION_CODE_ASSIGNED`** (port workflow + implémentation **`InMemoryProductBusinessEventLedger`**).

### Changed

- Distinction documentée entre **`SerialNumber`** (piste qualité unitaire optionnelle) et **`ProductionCode`** (lot partagé par plusieurs exemplaires).

## [2.0.0] - 2026-05-01

### Summary

Version **majeure** : introduction du modèle **`ProductReference`** (catalogue partagé) distinct des **`ProductInstance`** (exemplaires physiques), avec adaptation des workflows d’enregistrement, de qualification et des services de consultation.

### Added

- **`ProductReference`** et **`ProductReferenceId`** : nom, `image_uri`, type, set, code-barres commercial optionnel, indicateur `requires_qualification`.
- Ports **`ProductReferenceRepositoryPort`** et **`ProductReferenceIdFactoryPort`**.
- **`SealedProductSnapshot`** et issue métier **`RegistrationScanOutcome.NEW_INSTANCE_SHARED_REFERENCE`**.
- Exceptions **`InvalidProductReferenceIdError`**, **`InvalidProductReferenceError`**, **`ProductReferenceNotFoundForQueryError`**, **`ProductReferenceNotFoundForWorkflowError`** (module `missing_product_ref_workflow_error`).
- Champs optionnels **`display_name`** et **`image_uri`** sur **`ResolvedFromScan`** pour alimenter la référence catalogue.
- Champ **`product_reference_id`** sur **`ProductProvenanceForCollection`**.

### Changed

- **`ProductInstance`** : **`reference_id`** obligatoire ; suppression du code-barres commercial au niveau instance ; **`product_type`** et **`set_code`** documentés comme miroir dénormalisé de la référence.
- **`RegistrationFromScanRunner`** : injection du dépôt références et de la fabrique d’identifiants de référence ; un scan **commercial** réutilise une référence existante mais **crée toujours une nouvelle instance** physique lorsque la référence est trouvée.
- **`QualifyScannedProductUseCase`** : met à jour la référence catalogue et l’instance ; injection de **`ProductReferenceRepositoryPort`**.
- **`GetSealedProductSnapshotService`** et **`GetProductStructuralViewService`** : injection de **`ProductReferenceRepositoryPort`** ; la vue structurelle expose les références alignées sur le produit, le parent et les enfants.

### Removed

- **`ProductRepositoryPort.find_by_commercial_barcode`** (remplacé par la résolution côté **`ProductReferenceRepositoryPort`**).

## [1.0.1] - 2026-04-05

### Summary

Release de **correction** (packaging et readiness PyPI) : incrément SemVer **patch** après publication du tag GitHub **`v1.0.0`**, afin de livrer un numéro d’artefact et des métadonnées **cohérents** avec l’état actuel du dépôt **sans recycler** ni déplacer ce tag.

### Fixed

- Alignement des sources de vérité de version sur **1.0.1** : `pyproject.toml`, repli dans `baobab_mtg_products.__init__`, test `tests/baobab_mtg_products/test_init.py`.

### Notes

- Le classifier PyPI **`Development Status :: 5 - Production/Stable`** est conservé (librairie stable).
- L’extra **`[dev]`** inclut **`build`** et **`twine` (≥ 6)** ; la documentation et la CI s’appuient sur `pip install -e ".[dev]"` pour construire les artefacts et exécuter `twine check`.

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
