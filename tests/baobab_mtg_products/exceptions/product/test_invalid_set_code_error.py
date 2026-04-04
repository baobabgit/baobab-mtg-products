"""Tests pour :class:`~baobab_mtg_products.exceptions.product.InvalidSetCodeError`."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)
from baobab_mtg_products.exceptions.product.invalid_set_code_error import InvalidSetCodeError


class TestInvalidSetCodeError:
    """Hiérarchie de l'exception de code de set."""

    def test_inherits_baobab_base(self) -> None:
        """L'exception étend la racine métier."""
        assert issubclass(InvalidSetCodeError, BaobabMtgProductsException)
