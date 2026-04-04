"""Tests pour :class:`~baobab_mtg_products.domain.products.commercial_barcode.CommercialBarcode`."""

import pytest

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.exceptions.product.invalid_commercial_barcode_error import (
    InvalidCommercialBarcodeError,
)


class TestCommercialBarcode:
    """Règles sur le code-barres commercial numérique."""

    def test_accepts_typical_gtin_length(self) -> None:
        """Une chaîne de chiffres dans la plage est acceptée."""
        code = CommercialBarcode("3600540576748")
        assert code.value == "3600540576748"

    def test_strips_whitespace(self) -> None:
        """Les bords sont normalisés."""
        assert CommercialBarcode("  12345678  ").value == "12345678"

    def test_rejects_empty(self) -> None:
        """Vide interdit."""
        with pytest.raises(InvalidCommercialBarcodeError):
            CommercialBarcode("")

    def test_rejects_non_digit(self) -> None:
        """Seuls les chiffres sont autorisés."""
        with pytest.raises(InvalidCommercialBarcodeError):
            CommercialBarcode("3600540ABC748")

    def test_rejects_too_short(self) -> None:
        """Moins de quatre chiffres interdit."""
        with pytest.raises(InvalidCommercialBarcodeError):
            CommercialBarcode("123")
