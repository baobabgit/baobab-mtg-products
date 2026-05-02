"""Tests pour :class:`~baobab_mtg_products.domain.products.internal_barcode.InternalBarcode`."""

from unittest.mock import MagicMock

import pytest

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.exceptions.product.invalid_internal_barcode_error import (
    InvalidInternalBarcodeError,
)
from baobab_mtg_products.use_cases.registration.register_product_by_internal_scan_use_case import (
    RegisterProductByInternalScanUseCase,
)


class TestInternalBarcode:
    """Règles sur le code-barres interne."""

    def test_accepts_alphanumeric_and_separators(self) -> None:
        """Caractères autorisés pour une piste interne."""
        code = InternalBarcode("WH-12.A:stock_1")
        assert code.value == "WH-12.A:stock_1"

    def test_internal_barcode_accepts_valid_internal_code(self) -> None:
        """Plan 11 — valeur valide conservée telle quelle après validation."""
        self.test_accepts_alphanumeric_and_separators()

    def test_rejects_empty(self) -> None:
        """Vide interdit."""
        with pytest.raises(InvalidInternalBarcodeError):
            InternalBarcode("  ")

    def test_internal_barcode_rejects_empty_value(self) -> None:
        """Plan 11 — chaîne vide / blanche refusée."""
        self.test_rejects_empty()

    def test_internal_barcode_rejects_value_with_spaces(self) -> None:
        """Plan 11 — espaces dans la valeur interdits."""
        with pytest.raises(InvalidInternalBarcodeError):
            InternalBarcode("code avec espaces")

    def test_rejects_forbidden_characters(self) -> None:
        """Espace interne ou symboles hors liste interdits."""
        with pytest.raises(InvalidInternalBarcodeError):
            InternalBarcode("bad value")

    def test_internal_barcode_rejects_forbidden_characters(self) -> None:
        """Plan 11 — caractères hors liste autorisée."""
        self.test_rejects_forbidden_characters()

    def test_rejects_when_too_long(self) -> None:
        """La longueur maximale est appliquée."""
        with pytest.raises(InvalidInternalBarcodeError):
            InternalBarcode("a" * 65)

    def test_internal_barcode_rejects_value_too_long(self) -> None:
        """Plan 11 — dépassement de longueur max."""
        self.test_rejects_when_too_long()

    def test_internal_scan_invalid_barcode_is_rejected_before_use_case_call(self) -> None:
        """Workflow interne : échec à la construction du VO, pas d’appel au runner.

        :class:`RegisterProductByInternalScanUseCase` ne peut pas être instancié avec un
        code invalide : l’expression ``InternalBarcode(...)`` est évaluée avant le corps
        du constructeur.
        """
        runner = MagicMock()
        with pytest.raises(InvalidInternalBarcodeError):
            RegisterProductByInternalScanUseCase(InternalBarcode("espace interdit"), runner)
        runner.register_via_internal.assert_not_called()
