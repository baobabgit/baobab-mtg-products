"""Tests pour :class:`~baobab_mtg_products.exceptions.BaobabMtgProductsException`."""

import pytest

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class TestBaobabMtgProductsException:
    """Comportement nominal et limites de l'exception racine."""

    def test_is_exception_subclass(self) -> None:
        """L'exception racine hérite bien de :class:`Exception`."""
        assert issubclass(BaobabMtgProductsException, Exception)

    def test_stores_message(self) -> None:
        """Le message fourni est conservé sur l'instance."""
        message = "erreur métier"
        exc = BaobabMtgProductsException(message)
        assert exc.message == message
        assert str(exc) == message

    def test_can_be_raised_and_caught(self) -> None:
        """On peut lever et capturer l'exception racine."""
        with pytest.raises(BaobabMtgProductsException) as caught:
            raise BaobabMtgProductsException("boom")
        assert caught.value.message == "boom"
