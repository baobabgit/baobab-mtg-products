"""Tests pour :class:`~baobab_mtg_products.exceptions.product.InvalidProductInstanceError`."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)
from baobab_mtg_products.exceptions.product.invalid_product_instance_error import (
    InvalidProductInstanceError,
)


class TestInvalidProductInstanceError:
    """Hiérarchie de l'exception d'instance produit."""

    def test_inherits_baobab_base(self) -> None:
        """L'exception étend la racine métier."""
        assert issubclass(InvalidProductInstanceError, BaobabMtgProductsException)
