"""Tests pour :class:`~baobab_mtg_products.exceptions.product.InvalidCommercialBarcodeError`."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)
from baobab_mtg_products.exceptions.product.invalid_commercial_barcode_error import (
    InvalidCommercialBarcodeError,
)


class TestInvalidCommercialBarcodeError:
    """Hiérarchie de l'exception code-barres commercial."""

    def test_inherits_baobab_base(self) -> None:
        """L'exception étend la racine métier."""
        assert issubclass(InvalidCommercialBarcodeError, BaobabMtgProductsException)
