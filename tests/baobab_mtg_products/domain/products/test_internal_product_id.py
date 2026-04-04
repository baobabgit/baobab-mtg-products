"""Tests pour le value object :class:`InternalProductId`."""

import pytest

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.exceptions.product.invalid_product_identifier_error import (
    InvalidProductIdentifierError,
)


class TestInternalProductId:
    """Validation de l'identifiant interne unique."""

    def test_strips_and_accepts_valid_id(self) -> None:
        """Les espaces sont retirés ; la valeur conservée est stable."""
        pid = InternalProductId("  prod-001  ")
        assert pid.value == "prod-001"

    def test_rejects_empty_after_strip(self) -> None:
        """Une valeur vide après normalisation est interdite."""
        with pytest.raises(InvalidProductIdentifierError):
            InternalProductId("   ")

    def test_rejects_too_long_value(self) -> None:
        """La longueur maximale est appliquée."""
        with pytest.raises(InvalidProductIdentifierError):
            InternalProductId("x" * 257)
