"""Tests pour AmbiguousBarcodeResolutionError."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)
from baobab_mtg_products.exceptions.registration.ambiguous_barcode_resolution_error import (
    AmbiguousBarcodeResolutionError,
)


class TestAmbiguousBarcodeResolutionError:
    """Hiérarchie d'exception."""

    def test_inherits_base(self) -> None:
        """Extension de l'exception racine métier."""
        assert issubclass(AmbiguousBarcodeResolutionError, BaobabMtgProductsException)
