"""Tests pour :class:`~baobab_mtg_products.domain.products.internal_barcode.InternalBarcode`."""

import pytest

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.exceptions.product.invalid_internal_barcode_error import (
    InvalidInternalBarcodeError,
)


class TestInternalBarcode:
    """Règles sur le code-barres interne."""

    def test_accepts_alphanumeric_and_separators(self) -> None:
        """Caractères autorisés pour une piste interne."""
        code = InternalBarcode("WH-12.A:stock_1")
        assert code.value == "WH-12.A:stock_1"

    def test_rejects_empty(self) -> None:
        """Vide interdit."""
        with pytest.raises(InvalidInternalBarcodeError):
            InternalBarcode("  ")

    def test_rejects_forbidden_characters(self) -> None:
        """Espace interne ou symboles hors liste interdits."""
        with pytest.raises(InvalidInternalBarcodeError):
            InternalBarcode("bad value")

    def test_rejects_when_too_long(self) -> None:
        """La longueur maximale est appliquée."""
        with pytest.raises(InvalidInternalBarcodeError):
            InternalBarcode("a" * 65)
