"""Tests pour :class:`~baobab_mtg_products.exceptions.product.InvalidSerialNumberError`."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)
from baobab_mtg_products.exceptions.product.invalid_serial_number_error import (
    InvalidSerialNumberError,
)


class TestInvalidSerialNumberError:
    """Hiérarchie de l'exception numéro de série."""

    def test_inherits_baobab_base(self) -> None:
        """L'exception étend la racine métier."""
        assert issubclass(InvalidSerialNumberError, BaobabMtgProductsException)
