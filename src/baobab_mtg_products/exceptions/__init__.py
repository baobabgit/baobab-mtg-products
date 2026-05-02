"""Exceptions de la librairie baobab-mtg-products."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)
from baobab_mtg_products.exceptions.product import (
    DuplicateInternalBarcodeError,
    InvalidCommercialBarcodeError,
    InvalidInternalBarcodeError,
    InvalidProductIdentifierError,
    InvalidProductInstanceError,
    InvalidProductReferenceError,
    InvalidProductReferenceIdError,
    InvalidProductionCodeError,
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
from baobab_mtg_products.exceptions.query import (
    MissingReferencedParentProductError,
    ProductNotFoundForQueryError,
    ProductReferenceNotFoundForQueryError,
)
from baobab_mtg_products.exceptions.deconditioning import (
    ContainerAlreadyDeconditionedError,
    DeconditionContainerEmptyChildrenError,
    InvalidDeconditionChildSpecificationError,
    ProductNotDeconditionableContainerError,
)
from baobab_mtg_products.exceptions.registration import (
    AmbiguousBarcodeResolutionError,
    InvalidQualificationStateError,
    ProductNotFoundForWorkflowError,
    ProductReferenceNotFoundForWorkflowError,
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
    "ContainerAlreadyDeconditionedError",
    "DuplicateInternalBarcodeError",
    "DuplicateRevealedCardTraceError",
    "CircularProductParentageError",
    "DeconditionContainerEmptyChildrenError",
    "DetachParentMismatchError",
    "InvalidDeconditionChildSpecificationError",
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
    "InvalidProductReferenceError",
    "InvalidProductReferenceIdError",
    "InvalidProductionCodeError",
    "InvalidQualificationStateError",
    "InvalidSerialNumberError",
    "InvalidSetCodeError",
    "MissingReferencedParentProductError",
    "ProductAlreadyHasParentError",
    "ProductNotDeconditionableContainerError",
    "ProductAlreadyOpenedError",
    "ProductHistoryCoherenceError",
    "ProductNotFoundForQueryError",
    "ProductNotFoundForWorkflowError",
    "ProductReferenceNotFoundForQueryError",
    "ProductReferenceNotFoundForWorkflowError",
    "ProductNotOpenableError",
    "ProductNotOpenedForCardTraceError",
    "ProductNotReadyForOpeningError",
]
