"""baobab-mtg-products — gestion métier des produits scellés Magic: The Gathering.

Cette librairie modélise le cycle de vie des produits scellés (enregistrement,
relations parent/enfant, ouverture, traçabilité) sans couplage HTTP, UI,
moteur de règles ni deckbuilding. La surface exportée par ce module est
volontairement documentée par version semver (**2.0** pour la séparation référence / instance).

**API publique recommandée** — importer depuis ce package :

- Modèle et identifiants : ``ProductInstance``, ``ProductReference``, ``ProductReferenceId``,
  ``ProductType``, ``ProductStatus``, codes et ids.
- Consultation : ``GetSealedProductSnapshotService``, ``GetProductStructuralViewService``,
  ``GetProductBusinessTimelineService``, ``ProductStructuralView``, ``SealedProductSnapshot``.
- Commandes métier courantes : cas d'usage ouverture, rattachement, etc.
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
    SerialNumber,
)
from baobab_mtg_products.domain.query import ProductStructuralView, SealedProductSnapshot
from baobab_mtg_products.exceptions import (
    BaobabMtgProductsException,
    MissingReferencedParentProductError,
    ProductNotFoundForQueryError,
    ProductReferenceNotFoundForQueryError,
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
from baobab_mtg_products.use_cases.parent_child import (
    AttachChildProductToParentUseCase,
    DetachChildProductFromParentUseCase,
)

try:
    __version__: str = version("baobab-mtg-products")
except PackageNotFoundError:
    __version__ = "2.0.0"

__all__ = [
    "AttachChildProductToParentUseCase",
    "BaobabMtgProductsException",
    "CollectionPort",
    "CommercialBarcode",
    "DetachChildProductFromParentUseCase",
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
    "ProductReferenceRepositoryPort",
    "ProductRelationship",
    "ProductRelationshipKind",
    "ProductRepositoryPort",
    "ProductStatus",
    "ProductStructuralView",
    "ProductType",
    "SealedProductSnapshot",
    "RecordOpeningCardScanUseCase",
    "RegisterRevealedCardFromOpeningUseCase",
    "RevealedCardTrace",
    "SerialNumber",
    "StatisticsPort",
    "__version__",
]
