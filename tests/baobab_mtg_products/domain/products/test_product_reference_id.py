"""Tests pour :class:`ProductReferenceId`."""

import pytest

from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.exceptions.product.invalid_product_reference_id_error import (
    InvalidProductReferenceIdError,
)


class TestProductReferenceId:
    """Normalisation et contraintes de l'identifiant de référence."""

    def test_strips_and_keeps_value(self) -> None:
        """Les espaces de bord sont supprimés."""
        rid = ProductReferenceId("  ref-a  ")
        assert rid.value == "ref-a"

    def test_rejects_empty(self) -> None:
        """Une valeur vide ou uniquement des espaces est interdite."""
        with pytest.raises(InvalidProductReferenceIdError):
            ProductReferenceId("")
        with pytest.raises(InvalidProductReferenceIdError):
            ProductReferenceId("   ")

    def test_rejects_too_long(self) -> None:
        """La longueur maximale est appliquée."""
        with pytest.raises(InvalidProductReferenceIdError):
            ProductReferenceId("x" * 257)
