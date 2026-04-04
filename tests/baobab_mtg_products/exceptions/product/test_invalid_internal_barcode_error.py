"""Tests pour :class:`~baobab_mtg_products.exceptions.product.InvalidInternalBarcodeError`."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)
from baobab_mtg_products.exceptions.product.invalid_internal_barcode_error import (
    InvalidInternalBarcodeError,
)


class TestInvalidInternalBarcodeError:
    """Hiérarchie de l'exception code-barres interne."""

    def test_inherits_baobab_base(self) -> None:
        """L'exception étend la racine métier."""
        assert issubclass(InvalidInternalBarcodeError, BaobabMtgProductsException)
