"""Exceptions liées au modèle produit."""

from baobab_mtg_products.exceptions.product.duplicate_internal_barcode_error import (
    DuplicateInternalBarcodeError,
)
from baobab_mtg_products.exceptions.product.invalid_commercial_barcode_error import (
    InvalidCommercialBarcodeError,
)
from baobab_mtg_products.exceptions.product.invalid_internal_barcode_error import (
    InvalidInternalBarcodeError,
)
from baobab_mtg_products.exceptions.product.invalid_product_identifier_error import (
    InvalidProductIdentifierError,
)
from baobab_mtg_products.exceptions.product.invalid_product_instance_error import (
    InvalidProductInstanceError,
)
from baobab_mtg_products.exceptions.product.invalid_product_reference_error import (
    InvalidProductReferenceError,
)
from baobab_mtg_products.exceptions.product.invalid_production_code_error import (
    InvalidProductionCodeError,
)
from baobab_mtg_products.exceptions.product.invalid_product_reference_id_error import (
    InvalidProductReferenceIdError,
)
from baobab_mtg_products.exceptions.product.invalid_serial_number_error import (
    InvalidSerialNumberError,
)
from baobab_mtg_products.exceptions.product.invalid_set_code_error import (
    InvalidSetCodeError,
)

__all__ = [
    "DuplicateInternalBarcodeError",
    "InvalidCommercialBarcodeError",
    "InvalidInternalBarcodeError",
    "InvalidProductIdentifierError",
    "InvalidProductInstanceError",
    "InvalidProductReferenceError",
    "InvalidProductionCodeError",
    "InvalidProductReferenceIdError",
    "InvalidSerialNumberError",
    "InvalidSetCodeError",
]
