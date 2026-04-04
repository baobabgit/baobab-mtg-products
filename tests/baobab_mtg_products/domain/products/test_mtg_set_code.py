"""Tests pour :class:`~baobab_mtg_products.domain.products.mtg_set_code.MtgSetCode`."""

import pytest

from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.exceptions.product.invalid_set_code_error import InvalidSetCodeError


class TestMtgSetCode:
    """Format et normalisation du code d'extension."""

    def test_normalizes_to_uppercase(self) -> None:
        """Le code est stocké en majuscules."""
        assert MtgSetCode("mh3").value == "MH3"

    def test_accepts_alphanumeric_length_bounds(self) -> None:
        """Longueur 2 à 10 alphanumériques acceptée."""
        assert MtgSetCode("FD").value == "FD"
        assert MtgSetCode("1234567890").value == "1234567890"

    def test_rejects_too_short(self) -> None:
        """Un seul caractère est rejeté."""
        with pytest.raises(InvalidSetCodeError):
            MtgSetCode("A")

    def test_rejects_invalid_characters(self) -> None:
        """Espaces ou ponctuation hors plage interdits."""
        with pytest.raises(InvalidSetCodeError):
            MtgSetCode("MH-3")

    def test_rejects_too_long(self) -> None:
        """Plus de dix caractères alphanumériques est rejeté."""
        with pytest.raises(InvalidSetCodeError):
            MtgSetCode("ABCDEFGHIJK")
