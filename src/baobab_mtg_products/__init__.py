"""baobab-mtg-products — gestion métier des produits scellés Magic: The Gathering.

Cette librairie modélise le cycle de vie des produits scellés (enregistrement,
relations parent/enfant, ouverture, traçabilité) sans couplage HTTP, UI,
moteur de règles ni deckbuilding.
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
    ProductRelationship,
    ProductRelationshipKind,
    ProductStatus,
    ProductType,
    SerialNumber,
)
from baobab_mtg_products.exceptions import BaobabMtgProductsException
from baobab_mtg_products.use_cases.history import ListProductBusinessHistoryUseCase
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
    __version__ = "0.7.0"

__all__ = [
    "AttachChildProductToParentUseCase",
    "BaobabMtgProductsException",
    "CommercialBarcode",
    "DetachChildProductFromParentUseCase",
    "ExternalCardId",
    "InMemoryProductBusinessEventLedger",
    "InternalBarcode",
    "InternalProductId",
    "ListProductBusinessHistoryUseCase",
    "MtgSetCode",
    "ProductBusinessEventKind",
    "ProductBusinessEventRecord",
    "OpenSealedProductOutcome",
    "OpenSealedProductUseCase",
    "OpeningCardScanPayload",
    "ProductInstance",
    "ProductOpeningEvent",
    "ProductRelationship",
    "ProductRelationshipKind",
    "ProductStatus",
    "ProductType",
    "RecordOpeningCardScanUseCase",
    "RegisterRevealedCardFromOpeningUseCase",
    "RevealedCardTrace",
    "SerialNumber",
    "__version__",
]
