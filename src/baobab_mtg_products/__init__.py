"""baobab-mtg-products — gestion métier des produits scellés Magic: The Gathering.

Cette librairie modélise le cycle de vie des produits scellés (enregistrement,
relations parent/enfant, ouverture, traçabilité) sans couplage HTTP, UI,
moteur de règles ni deckbuilding. La surface exportée par ce module est
volontairement documentée par version semver (**2.4** : contrats de persistance et doubles mémoire).

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
from baobab_mtg_products.domain.deconditioning import (
    DeconditionableContainerPolicy,
    DeconditionChildSpecification,
    DeconditionContainerCommand,
    DeconditionContainerResult,
)
from baobab_mtg_products.domain.registration import (
    CommercialReferenceResolutionResult,
    RegistrationScanOutcome,
    RegistrationScanResult,
)
from baobab_mtg_products.exceptions import (
    BaobabMtgProductsException,
    ContainerAlreadyDeconditionedError,
    DeconditionContainerEmptyChildrenError,
    DuplicateInternalBarcodeError,
    InvalidDeconditionChildSpecificationError,
    MissingReferencedParentProductError,
    ProductNotDeconditionableContainerError,
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
from baobab_mtg_products.use_cases.deconditioning import DeconditionContainerUseCase
from baobab_mtg_products.use_cases.parent_child import (
    AttachChildProductToParentUseCase,
    DetachChildProductFromParentUseCase,
)
from baobab_mtg_products.use_cases.registration import (
    ResolveProductReferenceFromCommercialBarcodeUseCase,
)

try:
    __version__: str = version("baobab-mtg-products")
except PackageNotFoundError:
    __version__ = "2.4.0"

__all__ = [
    "AssignProductionCodeToProductInstanceUseCase",
    "AttachChildProductToParentUseCase",
    "BaobabMtgProductsException",
    "CollectionPort",
    "ContainerAlreadyDeconditionedError",
    "CommercialBarcode",
    "CommercialReferenceResolutionResult",
    "CreateProductInstanceUseCase",
    "DeconditionableContainerPolicy",
    "DeconditionChildSpecification",
    "DeconditionContainerCommand",
    "DeconditionContainerResult",
    "DeconditionContainerUseCase",
    "DeconditionContainerEmptyChildrenError",
    "DetachChildProductFromParentUseCase",
    "DuplicateInternalBarcodeError",
    "ExternalCardId",
    "GetProductBusinessTimelineService",
    "GetProductStructuralViewService",
    "GetSealedProductSnapshotService",
    "InMemoryProductBusinessEventLedger",
    "InternalBarcode",
    "InternalProductId",
    "InvalidDeconditionChildSpecificationError",
    "MissingReferencedParentProductError",
    "MtgSetCode",
    "OpenSealedProductOutcome",
    "OpenSealedProductUseCase",
    "OpeningCardScanPayload",
    "ProductBusinessEventKind",
    "ProductBusinessEventRecord",
    "ProductBusinessHistoryQueryPort",
    "ProductInstance",
    "ProductNotDeconditionableContainerError",
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
    "RegistrationScanOutcome",
    "RegistrationScanResult",
    "ResolveProductReferenceFromCommercialBarcodeUseCase",
    "SerialNumber",
    "StatisticsPort",
    "__version__",
]
