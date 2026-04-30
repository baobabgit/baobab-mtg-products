"""Exceptions du workflow d'enregistrement et de scan."""

from baobab_mtg_products.exceptions.registration.ambiguous_barcode_resolution_error import (
    AmbiguousBarcodeResolutionError,
)
from baobab_mtg_products.exceptions.registration.invalid_qualification_state_error import (
    InvalidQualificationStateError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.exceptions.registration.missing_product_ref_workflow_error import (
    ProductReferenceNotFoundForWorkflowError,
)

__all__ = [
    "AmbiguousBarcodeResolutionError",
    "InvalidQualificationStateError",
    "ProductNotFoundForWorkflowError",
    "ProductReferenceNotFoundForWorkflowError",
]
