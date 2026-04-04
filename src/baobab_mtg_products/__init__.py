"""baobab-mtg-products — gestion métier des produits scellés Magic: The Gathering.

Cette librairie modélise le cycle de vie des produits scellés (enregistrement,
relations parent/enfant, ouverture, traçabilité) sans couplage HTTP, UI,
moteur de règles ni deckbuilding.
"""

from importlib.metadata import PackageNotFoundError, version

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
    __version__ = "0.5.0"

__all__ = [
    "AttachChildProductToParentUseCase",
    "BaobabMtgProductsException",
    "CommercialBarcode",
    "DetachChildProductFromParentUseCase",
    "ExternalCardId",
    "InternalBarcode",
    "InternalProductId",
    "MtgSetCode",
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
