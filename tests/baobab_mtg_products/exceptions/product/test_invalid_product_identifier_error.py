"""Tests pour :class:`~baobab_mtg_products.exceptions.product.InvalidProductIdentifierError`."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)
from baobab_mtg_products.exceptions.product.invalid_product_identifier_error import (
    InvalidProductIdentifierError,
)


class TestInvalidProductIdentifierError:
    """Hiérarchie et instanciation de l'exception."""

    def test_inherits_baobab_base(self) -> None:
        """L'exception étend la racine métier."""
        assert issubclass(InvalidProductIdentifierError, BaobabMtgProductsException)

    def test_stores_message(self) -> None:
        """Le message est conservé sur l'instance."""
        exc = InvalidProductIdentifierError("détail")
        assert exc.message == "détail"
