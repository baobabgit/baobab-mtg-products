"""baobab-mtg-products — gestion métier des produits scellés Magic: The Gathering.

Cette librairie modélise le cycle de vie des produits scellés (enregistrement,
relations parent/enfant, ouverture, traçabilité) sans couplage HTTP, UI,
moteur de règles ni deckbuilding. La surface exportée par ce module est
volontairement documentée par version semver (**2.1** : création d'instance, code de production).

**API publique recommandée** — importer depuis ce package :

- Modèle et identifiants : ``ProductInstance``, ``ProductReference``, ``ProductReferenceId``,
  ``ProductType``, ``ProductStatus``, ``ProductionCode``, ``SerialNumber``, codes et ids.
- Consultation : ``GetSealedProductSnapshotService``, ``GetProductStructuralViewService``,
  ``GetProductBusinessTimelineService``, ``ProductStructuralView``, ``SealedProductSnapshot``.
- Commandes métier courantes : cas d'usage ouverture, rattachement, création d'instance, etc.
- Ports d'intégration : ``CollectionPort``, ``StatisticsPort``, ``ProductRepositoryPort``,
  ``ProductReferenceRepositoryPort``, ``ProductReferenceIdFactoryPort``,
  ``ProductBusinessHistoryQueryPort``.
- Exceptions racine et consultation : ``BaobabMtgProductsException``,
  ``ProductNotFoundForQueryError``, ``MissingReferencedParentProductError``.

Les sous-modules ``domain.*``, ``use_cases.*``, ``ports`` et ``services`` restent disponibles
pour des imports fins ou des extensions.
"""

from importlib.metadata import PackageNotFoundError, version

from baobab_mtg_products.domain.history import (
    InMemoryProductBusinessEventLedger,
    ProductBusinessEventKind,
    ProductBusinessEventRecord,
)
from baobab_mtg_products.domain.opening import (
    ExternalCardId,
    OpenSealedProductOutcome,
    OpeningCardScanPayload,
    ProductOpeningEvent,
    RevealedCardTrace,
)
from baobab_mtg_products.domain.products import (
    CommercialBarcode,
    InternalBarcode,
    InternalProductId,
    MtgSetCode,
    ProductInstance,
    ProductReference,
    ProductReferenceId,
    ProductRelationship,
    ProductRelationshipKind,
    ProductStatus,
    ProductType,
    ProductionCode,
    SerialNumber,
)
from baobab_mtg_products.domain.query import ProductStructuralView, SealedProductSnapshot
from baobab_mtg_products.exceptions import (
    BaobabMtgProductsException,
    DuplicateInternalBarcodeError,
    MissingReferencedParentProductError,
    ProductNotFoundForQueryError,
    ProductReferenceNotFoundForQueryError,
    ProductReferenceNotFoundForWorkflowError,
)
from baobab_mtg_products.ports import (
    CollectionPort,
    ProductBusinessHistoryQueryPort,
    ProductReferenceIdFactoryPort,
    ProductReferenceRepositoryPort,
    ProductRepositoryPort,
    StatisticsPort,
)
from baobab_mtg_products.services.query import (
    GetProductBusinessTimelineService,
    GetProductStructuralViewService,
    GetSealedProductSnapshotService,
)
from baobab_mtg_products.use_cases.opening import (
    OpenSealedProductUseCase,
    RecordOpeningCardScanUseCase,
    RegisterRevealedCardFromOpeningUseCase,
)
from baobab_mtg_products.use_cases.instance import (
    AssignProductionCodeToProductInstanceUseCase,
    CreateProductInstanceUseCase,
)
from baobab_mtg_products.use_cases.parent_child import (
    AttachChildProductToParentUseCase,
    DetachChildProductFromParentUseCase,
)

try:
    __version__: str = version("baobab-mtg-products")
except PackageNotFoundError:
    __version__ = "2.1.0"

__all__ = [
    "AssignProductionCodeToProductInstanceUseCase",
    "AttachChildProductToParentUseCase",
    "BaobabMtgProductsException",
    "CollectionPort",
    "CommercialBarcode",
    "CreateProductInstanceUseCase",
    "DetachChildProductFromParentUseCase",
    "DuplicateInternalBarcodeError",
    "ExternalCardId",
    "GetProductBusinessTimelineService",
    "GetProductStructuralViewService",
    "GetSealedProductSnapshotService",
    "InMemoryProductBusinessEventLedger",
    "InternalBarcode",
    "InternalProductId",
    "MissingReferencedParentProductError",
    "MtgSetCode",
    "OpenSealedProductOutcome",
    "OpenSealedProductUseCase",
    "OpeningCardScanPayload",
    "ProductBusinessEventKind",
    "ProductBusinessEventRecord",
    "ProductBusinessHistoryQueryPort",
    "ProductInstance",
    "ProductNotFoundForQueryError",
    "ProductOpeningEvent",
    "ProductReference",
    "ProductReferenceId",
    "ProductReferenceIdFactoryPort",
    "ProductReferenceNotFoundForQueryError",
    "ProductReferenceNotFoundForWorkflowError",
    "ProductReferenceRepositoryPort",
    "ProductRelationship",
    "ProductRelationshipKind",
    "ProductRepositoryPort",
    "ProductStatus",
    "ProductStructuralView",
    "ProductType",
    "ProductionCode",
    "SealedProductSnapshot",
    "RecordOpeningCardScanUseCase",
    "RegisterRevealedCardFromOpeningUseCase",
    "RevealedCardTrace",
    "SerialNumber",
    "StatisticsPort",
    "__version__",
]
