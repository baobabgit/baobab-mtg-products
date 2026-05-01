"""Tests pour :class:`ProductionCode`."""

import pytest

from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.exceptions.product.invalid_production_code_error import (
    InvalidProductionCodeError,
)


class TestProductionCode:
    """Normalisation et garde-fous du code de lot (non unique)."""

    def test_strips_whitespace(self) -> None:
        """Les espaces en tête et queue sont retirés."""
        code = ProductionCode("  LOT-A1  ")
        assert code.value == "LOT-A1"

    def test_rejects_empty_after_strip(self) -> None:
        """Une valeur vide n'est pas un code de production valide."""
        with pytest.raises(InvalidProductionCodeError):
            ProductionCode("   ")

    def test_rejects_too_long(self) -> None:
        """La longueur maximale est appliquée."""
        with pytest.raises(InvalidProductionCodeError):
            ProductionCode("x" * 129)
