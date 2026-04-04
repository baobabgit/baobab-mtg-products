"""Exceptions de la librairie baobab-mtg-products."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)
from baobab_mtg_products.exceptions.product import (
    InvalidCommercialBarcodeError,
    InvalidInternalBarcodeError,
    InvalidProductIdentifierError,
    InvalidProductInstanceError,
    InvalidSerialNumberError,
    InvalidSetCodeError,
)
from baobab_mtg_products.exceptions.history import (
    ProductHistoryCoherenceError,
)
from baobab_mtg_products.exceptions.integration import InvalidIntegrationPayloadError
from baobab_mtg_products.exceptions.opening import (
    DuplicateRevealedCardTraceError,
    InvalidExternalCardIdError,
    InvalidOpeningCardScanPayloadError,
    InvalidRevealedCardSequenceError,
    ProductAlreadyOpenedError,
    ProductNotOpenableError,
    ProductNotOpenedForCardTraceError,
    ProductNotReadyForOpeningError,
)
from baobab_mtg_products.exceptions.registration import (
    AmbiguousBarcodeResolutionError,
    InvalidQualificationStateError,
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.exceptions.relationship import (
    ChildProductNotAttachedError,
    CircularProductParentageError,
    DetachParentMismatchError,
    IncompleteProductHierarchyError,
    IncompatibleParentChildTypesError,
    InvalidProductRelationshipLinkError,
    ProductAlreadyHasParentError,
)

__all__ = [
    "AmbiguousBarcodeResolutionError",
    "BaobabMtgProductsException",
    "ChildProductNotAttachedError",
    "DuplicateRevealedCardTraceError",
    "CircularProductParentageError",
    "DetachParentMismatchError",
    "IncompleteProductHierarchyError",
    "InvalidIntegrationPayloadError",
    "IncompatibleParentChildTypesError",
    "InvalidProductRelationshipLinkError",
    "InvalidCommercialBarcodeError",
    "InvalidExternalCardIdError",
    "InvalidInternalBarcodeError",
    "InvalidOpeningCardScanPayloadError",
    "InvalidProductIdentifierError",
    "InvalidRevealedCardSequenceError",
    "InvalidProductInstanceError",
    "InvalidQualificationStateError",
    "InvalidSerialNumberError",
    "InvalidSetCodeError",
    "ProductAlreadyHasParentError",
    "ProductAlreadyOpenedError",
    "ProductHistoryCoherenceError",
    "ProductNotFoundForWorkflowError",
    "ProductNotOpenableError",
    "ProductNotOpenedForCardTraceError",
    "ProductNotReadyForOpeningError",
]
