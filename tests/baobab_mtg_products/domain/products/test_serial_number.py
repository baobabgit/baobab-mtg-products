"""Tests pour :class:`~baobab_mtg_products.domain.products.serial_number.SerialNumber`."""

import pytest

from baobab_mtg_products.domain.products.serial_number import SerialNumber
from baobab_mtg_products.exceptions.product.invalid_serial_number_error import (
    InvalidSerialNumberError,
)


class TestSerialNumber:
    """Validation du numéro de série optionnel (objet valeur)."""

    def test_accepts_non_empty_serial(self) -> None:
        """Un numéro significatif est conservé tel quel après strip."""
        sn = SerialNumber("  SN-42  ")
        assert sn.value == "SN-42"

    def test_rejects_empty_after_strip(self) -> None:
        """Fournir l'objet avec une chaîne vide est incohérent."""
        with pytest.raises(InvalidSerialNumberError):
            SerialNumber("   ")

    def test_rejects_too_long(self) -> None:
        """La longueur maximale est bornée."""
        with pytest.raises(InvalidSerialNumberError):
            SerialNumber("x" * 129)
