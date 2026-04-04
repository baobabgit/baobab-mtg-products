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
    "CircularProductParentageError",
    "DetachParentMismatchError",
    "IncompleteProductHierarchyError",
    "IncompatibleParentChildTypesError",
    "InvalidProductRelationshipLinkError",
    "InvalidCommercialBarcodeError",
    "InvalidInternalBarcodeError",
    "InvalidProductIdentifierError",
    "InvalidProductInstanceError",
    "InvalidQualificationStateError",
    "InvalidSerialNumberError",
    "InvalidSetCodeError",
    "ProductAlreadyHasParentError",
    "ProductNotFoundForWorkflowError",
]
